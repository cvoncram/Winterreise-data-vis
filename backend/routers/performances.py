# backend/routers/performances.py
from fastapi import APIRouter, HTTPException
from services.githubClient import fetch_repo_json, fetch_repo_text
from services.pathSafety import is_safe_folder_name
from datetime import datetime
import re
import json
import unicodedata
from config import PIECE_TITLES

router = APIRouter()

_MISSING = {"no value", "unknown", "unclear", "", " "}

# -------------------------------
# Helper functions
# -------------------------------

def _normalize(s: str) -> str:
    """
    Unicode NFC normalization.
    """
    return unicodedata.normalize("NFC", s)


def get_performances_json() -> list[dict]:
    """
    Fetch and parse performances.json from the repo.
    """
    content = fetch_repo_text("performances/performances.json")
    return json.loads(content)


def _disambiguate_performance(folder_name: str, candidates: list[dict]) -> tuple[dict, bool]:
    """
    Pick the performances.json row matching a recording folder, when multiple rows share the same year/pianist. 
    """
    if len(candidates) <= 1:
        return (candidates[0] if candidates else {}), False

    folder_name = _normalize(folder_name)
    city_candidates = [
        p for p in candidates
        if _normalize(p.get("City", "").replace(" ", "")) in folder_name
    ]
    remaining = city_candidates if city_candidates else candidates
    if len(remaining) == 1:
        return remaining[0], False

    suffix_match = re.search(r"_([A-Z])$", folder_name)
    if suffix_match:
        index = ord(suffix_match.group(1)) - ord("A")
        sorted_candidates = sorted(remaining, key=lambda p: p.get("Date - Standardized", ""))
        if 0 <= index < len(sorted_candidates):
            return sorted_candidates[index], True

    return remaining[0], True

def _date_nice(day, month, year):
    """Readable date, marking missing day or month."""
    date = ""
    if year not in _MISSING:
        date += str(year)
        if month not in _MISSING:
            date = month + " " + date
            if day not in _MISSING:
                date = str(day) + " " + date
            else:
                date += " " + "(day unclear)"
        else:
            date += " " + "(day and month unclear)"
    else:
        date = "unclear"
    return date

def _name_nice(name: str) -> str:
    """"Last, First" as "First Last"."""
    last, _, first = name.partition(",")
    return f"{first.strip()} {last.strip()}".strip()

def _disentangle_coordinates(coords: str) -> list[float]:
    """Latitude and longitude from "lat, lon"."""
    latitude, _, longitude = coords.partition(",")
    return (float(latitude.strip()), float(longitude.strip()))

# -------------------------------
# Endpoints
# -------------------------------

@router.get("/db/performances")
def list_performances():
    """
    Return a list of recording folders (recordings) in /performances, enriched with info from performances.json for labels.
    """
    r = fetch_repo_json("performances")
    r.raise_for_status()
    items = r.json()

    folders = [item["name"] for item in items if item["type"] == "dir"]

    performances_json = get_performances_json()

    enriched = []
    for folder_name in folders:

        normalized_folder_name = _normalize(folder_name)
        candidates = [
            p for p in performances_json
            if folder_name.startswith(str(int(p["Recording Year"])))
            and _normalize(p["Pianist"].split(",")[0]) in normalized_folder_name
        ]

        perf_meta, needs_date_qualifier = _disambiguate_performance(folder_name, candidates)

        year = int(perf_meta.get("Recording Year", 0)) if perf_meta else None
        pianist = perf_meta.get("Pianist", "").split(",")[0] if perf_meta else folder_name.split("_")[1]
        city = perf_meta.get("City", "") if perf_meta and "City" in perf_meta else ""

        label = f"{pianist} {year}" if year else folder_name
        if city:
            label += f", {city}"

        if needs_date_qualifier:
            date_str = perf_meta.get("Date - Standardized")
            if date_str:
                try:
                    label += datetime.strptime(date_str, "%Y-%m-%d").strftime(" (%b %-d)")
                except ValueError:
                    pass

        enriched.append({
            "path": folder_name,
            "label": label,
            # Metadata for colouring.
            "year": year,
            "pianist": pianist,
            "city": city,
            "recordingContext": perf_meta.get("Recording Context") if perf_meta else None
        })

    return sorted(enriched, key=lambda x: x["label"])

@router.get("/db/performance-files")
def list_performance_files(performance: str):
    """
    Return all MEI files inside a recording folder, with friendly labels and order. Filenames are assumed to follow: folder_name_number_audio_data.xml
    """
    if not is_safe_folder_name(performance):
        raise HTTPException(status_code=400, detail="Invalid performance path")

    r = fetch_repo_json(f"performances/{performance}")
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="Recording not found")
    r.raise_for_status()
    items = r.json()

    files = []
    for item in items:
        if item["type"] == "file" and item["name"].endswith(".xml"):
            filename = item["name"]

            match = re.search(r"_(\d+)_", filename)
            piece_num = int(match.group(1)) if match else 0

            title = PIECE_TITLES[piece_num - 1] if 1 <= piece_num <= len(PIECE_TITLES) else filename
            label = f"{piece_num}. {title}"

            files.append({
                "name": filename,
                "path": item["path"],
                "label": label,
                "order": piece_num
            })

    files_sorted = sorted(files, key=lambda f: f["order"])
    return files_sorted

@router.get("/db/performances-detailed")
def list_performances_detailed():
    """
    Returns the list of performances with metadata for presentation.
    """
    perfs = get_performances_json()
    performances = []
    for p in perfs:
        performances.append({
            "no_in_order": int(p["No"]),
            "pianist": _name_nice(p.get("Pianist")),
            "pianist_gnd": p.get("GND number"),
            "year": int(p["Recording Year"]),
            "date": _date_nice(p.get("Recording Date"), p.get("Recording Month"), year = int(p["Recording Year"])),
            "place": p.get("City"),
            "place_addendum": p.get("Exact place") if p.get("Exact place") not in _MISSING else "",
            "coordinates": _disentangle_coordinates(p.get("coordinates")),
            "recording_context": p.get("Recording Context"),
            "online_info": p.get("further information online"),
            "misc": p.get("misc") if p.get("misc") not in _MISSING else ""
        })
    return performances