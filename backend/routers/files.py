from fastapi import APIRouter
from github_auth import get_installation_token
import requests
import base64
from config import OWNER, REPO, BRANCH

router = APIRouter()

@router.get("/file")
def get_file(path: str):
    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"

    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    content = base64.b64decode(r.json()["content"]).decode()
    return {"content": content}