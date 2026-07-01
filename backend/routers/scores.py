from fastapi import APIRouter
from github_auth import get_installation_token
import requests
from config import OWNER, REPO, BRANCH
import re

router = APIRouter()

@router.get("/db/scores-folder")
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


    def format_filename(name: str) -> str:
        name = re.sub(r"\.[^/.]+$", "", name)   # remove extension
        name = re.sub(r"[-]", ". ", name)       # replace separators
        name = re.sub(r"[_]", " ", name)       # replace separators
        return name
    
    def extract_number(name: str) -> int:
        match = re.match(r"^\d+", name)
        return int(match.group()) if match else 0
    
    def sort_tree(node):
        if isinstance(node, dict):
            items = []

            for key, value in node.items():
                if isinstance(value, dict) and value.get("type") == "file":
                    items.append(value)
                else:
                    items.append({
                        "type": "folder",
                        "name": key,
                        "children": sort_tree(value)
                    })

            return sorted(items, key=lambda x: x.get("order", 0))

        return node
    
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
            filename = parts[-1]

            node[filename] = {
                "type": "file",
                "sha": item["sha"],
                "path": path,
                "label": format_filename(filename),
                "order": extract_number(filename),
            }
        else:
            node.setdefault(parts[-1], {})

    return sort_tree(root)


