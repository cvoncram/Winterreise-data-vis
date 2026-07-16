# backend/routers/performances.py
from fastapi import APIRouter, HTTPException
from github_auth import get_installation_token
from services.pathSafety import is_safe_folder_name
import requests
import re
import json
import base64
from config import OWNER, REPO, BRANCH

router = APIRouter()

# -------------------------------
# Helper functions
# -------------------------------

def format_filename(name: str) -> str:
    """
    Convert raw filename to a user-friendly label.
    - Remove extension
    - Replace underscores with spaces
    - Replace hyphens with dots
    """
    name = re.sub(r"\.[^/.]+$", "", name)  # remove extension
    name = re.sub(r"[-]", ". ", name)
    name = re.sub(r"[_]", " ", name)
    return name

def extract_number(name: str) -> int:
    """
    Extract leading number from filename for sorting
    """
    match = re.match(r"^\d+", name)
    return int(match.group()) if match else 0

def get_performances_json() -> list[dict]:
    """
    Fetch and parse performances.json from the repo
    """
    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/performances/performances.json?ref={BRANCH}"
    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    content_b64 = r.json()["content"]
    content = base64.b64decode(content_b64).decode()
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
    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/performances?ref={BRANCH}"
    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers, timeout=10)
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

    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/performances/{performance}?ref={BRANCH}"
    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers, timeout=10)
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
            piece_titles = [
                "Gute Nacht",
                "Die Wetterfahne",
                "Gefror'ne Tränen",
                "Erstarrung",
                "Der Lindenbaum",
                "Wasserflut",
                "Auf dem Flusse",
                "Rückblick",
                "Irrlicht",
                "Rast",
                "Frühlingstraum",
                "Einsamkeit",
                "Die Post",
                "Der greise Kopf",
                "Die Krähe",
                "Letzte Hoffnung",
                "Im Dorfe",
                "Der stürmische Morgen",
                "Täuschung",
                "Der Wegweiser",
                "Das Wirtshaus",
                "Mut",
                "Die Nebensonnen",
                "Der Leiermann"
                ]

            # Create a nice label
            label = f"{piece_num}. {piece_titles[piece_num - 1]}"

            files.append({
                "name": filename,
                "path": item["path"],
                "label": label,
                "order": piece_num
            })

    # Sort by piece number
    files_sorted = sorted(files, key=lambda f: f["order"])
    return files_sorted