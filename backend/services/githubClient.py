import base64
import requests
from github_auth import get_github_headers
from config import OWNER, REPO, BRANCH


def fetch_repo_text(path: str) -> str:
    """Fetch and base64-decode a single file's content from the repo."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
    r = requests.get(url, headers=get_github_headers(), timeout=10)
    r.raise_for_status()
    return base64.b64decode(r.json()["content"]).decode()


def fetch_repo_json(path: str):
    """Fetch a repo contents listing (directory or metadata JSON), decoded."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
    r = requests.get(url, headers=get_github_headers(), timeout=10)
    return r


def fetch_repo_tree():
    """Fetch the full recursive git tree for BRANCH."""
    url = f"https://api.github.com/repos/{OWNER}/{REPO}/git/trees/{BRANCH}?recursive=1"
    headers = get_github_headers()
    headers["Accept"] = "application/vnd.github+json"
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    return r.json()["tree"]
