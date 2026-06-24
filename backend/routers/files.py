from fastapi import APIRouter, Query
from github_auth import get_installation_token
from services.meiParser import parse_mei_to_rows, parse_mei_metadata, parse_measures_to_rows
import requests
import base64
from config import OWNER, REPO, BRANCH

router = APIRouter()

@router.get("/db/file")
def get_file(path: str):
    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"

    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    content = base64.b64decode(r.json()["content"]).decode()
    return {"content": content}

@router.get("/db/parsed-file")
def parse_mei(path: str):
    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
    print(url)
    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    xml = base64.b64decode(r.json()["content"]).decode()

    rows = parse_mei_to_rows(xml)
    metadata = parse_mei_metadata(xml)

    return [{"metadata": metadata}, {"data": rows}]


@router.get("/db/parsed-measures")
def parse_files(
        piece: int,
        start: int,
        start_beat: int,
        end: int,
        end_beat: int,
        paths: list[str] = Query(...)
    ):
    token = get_installation_token()
    headers = {"Authorization": f"token {token}"}

    measures = []
    for path in paths:
        folder_name = path
        file_path = f"performances/{path}/{folder_name}_{piece}_Audio_Data.xml"
        url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{file_path}?ref={BRANCH}"
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        xml = base64.b64decode(r.json()["content"]).decode()
        measures.append({
            "performance": path,
            "data": parse_measures_to_rows(xml, start, start_beat, end, end_beat),
            "metadata": parse_mei_metadata(xml)
        })
    return measures