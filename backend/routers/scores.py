from fastapi import APIRouter
from services.githubClient import fetch_repo_tree
from config import PIECE_TITLES
import re

router = APIRouter()

@router.get("/db/scores-folder")
def get_scores_tree():
    """Score directory as a tree sorted by song number."""
    tree_items = fetch_repo_tree()

    def format_filename(name: str) -> str:
        """Display name from a file name."""
        name = re.sub(r"\.[^/.]+$", "", name)   # remove extension
        name = re.sub(r"[-]", ". ", name)       # replace separators
        name = re.sub(r"[_]", " ", name)       # replace separators
        return name
    
    def extract_number(name: str) -> int:
        """Leading number of a name, 0 if none."""
        match = re.match(r"^\d+", name)
        return int(match.group()) if match else 0
    
    def sort_tree(node):
        """Nested folders and files, sorted by order."""
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
            order = extract_number(filename)
            title = (
                PIECE_TITLES[order - 1]
                if 1 <= order <= len(PIECE_TITLES)
                else None
            )
            label = f"{order}. {title}" if title else format_filename(filename)

            node[filename] = {
                "type": "file",
                "sha": item["sha"],
                "path": path,
                "label": label,
                "order": order,
            }
        else:
            node.setdefault(parts[-1], {})

    return sort_tree(root)


