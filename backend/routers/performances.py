# backend/routers/performances.py
from fastapi import APIRouter, HTTPException
from services.githubClient import fetch_repo_json, fetch_repo_text
from services.pathSafety import is_safe_folder_name
import re
import json
from config import PIECE_TITLES

router = APIRouter()

# -------------------------------
# Helper functions
# -------------------------------

def get_performances_json() -> list[dict]:
    """
    Fetch and parse performances.json from the repo
    """
    content = fetch_repo_text("performances/performances.json")
    return json.loads(content)

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
    # Try to find the matching metadata entry, disambiguating by city if present
        candidates = [
            p for p in performances_json
            if folder_name.startswith(str(int(p["Recording Year"]))) and p["Pianist"].split(",")[0] in folder_name
        ]

        perf_meta = {}
        if len(candidates) == 1:
            perf_meta = candidates[0]
        elif len(candidates) > 1:
            # Try to disambiguate using the city name in the folder
            perf_meta = next(
                (p for p in candidates if p.get("City", "").replace(" ", "") in folder_name),
                candidates[0]  # fallback to first if no city match
            )

        year = int(perf_meta.get("Recording Year", 0)) if perf_meta else None
        pianist = perf_meta.get("Pianist", "").split(",")[0] if perf_meta else folder_name.split("_")[1]
        city = perf_meta.get("City", "") if perf_meta and "City" in perf_meta else ""

        label = f"{pianist} {year}" if year else folder_name
        if city:
            label += f", {city}"

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