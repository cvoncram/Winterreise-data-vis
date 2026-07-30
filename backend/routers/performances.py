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

# -------------------------------
# Helper functions
# -------------------------------

def _normalize(s: str) -> str:
    """
    Normalize to NFC so accented characters compare equal regardless of
    whether they arrived precomposed (e.g. macOS-typed text) or decomposed
    (e.g. filenames created on HFS+/APFS) — both render identically but are
    different byte/codepoint sequences otherwise.
    """
    return unicodedata.normalize("NFC", s)


def get_performances_json() -> list[dict]:
    """
    Fetch and parse performances.json from the repo
    """
    content = fetch_repo_text("performances/performances.json")
    return json.loads(content)


def _disambiguate_performance(folder_name: str, candidates: list[dict]) -> tuple[dict, bool]:
    """
    Pick the performances.json row matching a recording folder, when
    multiple rows share the same year/pianist. Narrows by city first; if
    that's still ambiguous (same pianist, year, *and* city — e.g. two
    recitals in the same city within one year), folders are named with a
    trailing _A/_B/... suffix, earliest recording first, resolved here by
    sorting the remaining candidates on "Date - Standardized".

    Returns (matched_row, needs_date_qualifier) — the second value is True
    when other candidates share the same pianist/year/city, so the caller
    should distinguish the label further (e.g. by date).
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

# -------------------------------
# Endpoint 1: List all recordings
# -------------------------------

@router.get("/db/performances")
def list_performances():
    """
    Return a list of recording folders (recordings) in /performances,
    enriched with info from performances.json for friendly labels.
    """
    r = fetch_repo_json("performances")
    r.raise_for_status()
    items = r.json()

    # Only include directories (recordings)
    folders = [item["name"] for item in items if item["type"] == "dir"]

    # Fetch performances.json metadata
    performances_json = get_performances_json()

    enriched = []
    for folder_name in folders:
        # Try to find the matching metadata entry, disambiguating by city
        # (and, if needed, recording date) if present
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
            "label": label
        })

    return sorted(enriched, key=lambda x: x["label"])

# -------------------------------
# Endpoint 2: List pieces inside a recording
# -------------------------------

@router.get("/db/performance-files")
def list_performance_files(performance: str):
    """
    Return all MEI files inside a recording folder, with friendly labels and order.
    Filenames are assumed to follow: folder_name_number_audio_data.xml
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

            # Extract the piece number from the filename
            match = re.search(r"_(\d+)_", filename)
            piece_num = int(match.group(1)) if match else 0

            # Create a nice label
            title = PIECE_TITLES[piece_num - 1] if 1 <= piece_num <= len(PIECE_TITLES) else filename
            label = f"{piece_num}. {title}"

            files.append({
                "name": filename,
                "path": item["path"],
                "label": label,
                "order": piece_num
            })

    # Sort by piece number
    files_sorted = sorted(files, key=lambda f: f["order"])
    return files_sorted