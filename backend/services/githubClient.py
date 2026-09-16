import base64
import time
import requests
from github_auth import get_github_headers
from config import OWNER, REPO, BRANCH

# Files change only when someone pushes to the database repository, so holding
# them for a while costs little and saves a great deal: one cycle analysis for
# 26 recordings fetches 624 files one at a time, and that, not the
# computation, is what the waiting consists of. The whole corpus is about
# 37 MB of text, so even holding all of it is affordable.
_TTL_SECONDS = 600
_MAX_ENTRIES = 800
_cache: dict[str, tuple[float, str]] = {}


def clear_file_cache() -> None:
    """Drop the cached files, so the next read goes to GitHub again."""
    _cache.clear()


def fetch_repo_text(path: str) -> str:
    """Fetch and base64-decode a single file's content from the repo."""
    cached = _cache.get(path)
    if cached and time.time() - cached[0] < _TTL_SECONDS:
        return cached[1]

    url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{path}?ref={BRANCH}"
    r = requests.get(url, headers=get_github_headers(), timeout=10)
    r.raise_for_status()
    text = base64.b64decode(r.json()["content"]).decode()

    # Emptying the cache wholesale is cruder than evicting the oldest entry,
    # but the corpus fits well inside the limit, so the case is rare and not
    # worth a dependency on an ordered structure.
    if len(_cache) >= _MAX_ENTRIES:
        _cache.clear()
    _cache[path] = (time.time(), text)
    return text


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
