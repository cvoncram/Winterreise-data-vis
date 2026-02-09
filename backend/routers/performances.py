import json
from github_auth import get_installation_token
import requests
import base64
from fastapi import APIRouter
from main import OWNER, REPO, BRANCH

router = APIRouter()

@router.get("/performances-folder")
def get_tree():
    token = get_installation_token()

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
    }
    print(url)

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    tree_items = r.json()["tree"]

    # ---- Build nested folder structure ----
    root = {}

    prefix = "performances/"

    for item in tree_items:
        path = item["path"]

        # Only include files/folders under /scores
        if not path.startswith(prefix):
            continue

        # Remove the 'scores/' prefix
        relative_path = path[len(prefix):]

        # Skip if path is empty (this can happen if there’s a folder named 'scores')
        if not relative_path:
            continue

        parts = path.split("/")
        node = root

        for part in parts[:-1]:
            node = node.setdefault(part, {})

        if item["type"] == "blob":
            node[parts[-1]] = {
                "type": "file",
                "sha": item["sha"],
                "path": path,
            }
        else:
            node.setdefault(parts[-1], {})

    return root

@router.get("/performances-list")
def get_performance_list():
    token = get_installation_token()
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/performances/performances.json"

    headers = {"Authorization": f"token {token}"}

    r = requests.get(url, headers=headers)
    r.raise_for_status()

    content_str = base64.b64decode(r.json()["content"]).decode()
    content_json = json.loads(content_str)
    return content_json