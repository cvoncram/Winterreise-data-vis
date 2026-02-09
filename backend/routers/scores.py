from fastapi import APIRouter
from github_auth import get_installation_token
import requests
from main import OWNER, REPO, BRANCH

router = APIRouter()

@router.get("/scores-folder")
def get_scores_tree():
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

    # ---- Build nested folder structure starting from /scores ----
    root = {}

    prefix = "scores/"

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

        parts = relative_path.split("/")
        node = root

        for part in parts[:-1]:
            node = node.setdefault(part, {})

        if item["type"] == "blob":
            node[parts[-1]] = {
                "type": "file",
                "sha": item["sha"],
                "path": path,  # keep full path for fetching later
            }
        else:
            node.setdefault(parts[-1], {})

    return root