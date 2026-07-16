from fastapi import APIRouter, HTTPException, Query, Response
from github_auth import get_installation_token
from services.meiParser import parse_mei_to_rows, parse_mei_metadata, parse_measures_to_rows, return_relevant_measures
from services.pathSafety import is_safe_repo_path, is_safe_folder_name
import requests
import base64
from config import OWNER, REPO, BRANCH, TITLES

router = APIRouter()

@router.get("/db/file")
def get_file(path: str):
    if not is_safe_repo_path(path):
        raise HTTPException(status_code=400, detail="Invalid path")

    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"

    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    content = base64.b64decode(r.json()["content"]).decode()
    return Response(content=content, media_type="application/xml")

@router.get("/db/file-measures")
def get_file_measures(piece: int, start: int = Query(ge=1), end: int = Query(ge=1)):

    if not 1 <= piece <= len(TITLES):
        raise HTTPException(status_code=404, detail="Piece not found")

    path = TITLES[piece-1]

    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"

    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    content = base64.b64decode(r.json()["content"]).decode()

    score = return_relevant_measures(content, start, end)

    return Response(content=score, media_type="application/xml")

@router.get("/db/parsed-file")
def parse_mei(path: str):
    if not is_safe_repo_path(path):
        raise HTTPException(status_code=400, detail="Invalid path")

    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()

    xml = base64.b64decode(r.json()["content"]).decode()

    rows = parse_mei_to_rows(xml)
    metadata = parse_mei_metadata(xml)

    return [{"metadata": metadata}, {"data": rows}]


@router.get("/db/parsed-measures")
def parse_files(
        piece: int,
        start: int = Query(ge=1),
        start_beat: int = Query(ge=1),
        end: int = Query(ge=1),
        end_beat: int = Query(ge=1),
        paths: list[str] = Query(...)
    ):
    if not 1 <= piece <= len(TITLES):
        raise HTTPException(status_code=404, detail="Piece not found")

    for path in paths:
        if not is_safe_folder_name(path):
            raise HTTPException(status_code=400, detail="Invalid performance path")

    token = get_installation_token()
    headers = {"Authorization": f"token {token}"}

    measures = []
    for path in paths:
        folder_name = path
        file_path = f"performances/{path}/{folder_name}_{piece}_Audio_Data.xml"
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{file_path}?ref={BRANCH}"
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
        xml = base64.b64decode(r.json()["content"]).decode()
        measures.append({
            "performance": path,
            "data": parse_measures_to_rows(xml, start, start_beat, end, end_beat),
            "metadata": parse_mei_metadata(xml)
        })
    return measures