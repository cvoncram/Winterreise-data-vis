from fastapi import APIRouter
from github_auth import get_installation_token
from services.meiParser import parse_mei_to_rows
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

    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    xml = base64.b64decode(r.json()["content"]).decode()

    rows = parse_mei_to_rows(xml)

    return {"data": rows}