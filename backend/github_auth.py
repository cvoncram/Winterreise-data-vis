import calendar
import os
import time
from pathlib import Path

import jwt
import requests

BASE_DIR = Path(__file__).resolve().parent

# GitHub App identifiers, overridable via environment.
APP_ID = os.getenv("GITHUB_APP_ID", "2827092")
INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID", "108972344")

DEFAULT_KEY_PATH = BASE_DIR / "winterreise-database-test.2026-02-09.private-key.pem"


def _load_private_key() -> str:
    """
    Private key of the GitHub App, from GITHUB_PRIVATE_KEY or from the file
    at GITHUB_PRIVATE_KEY_PATH (default: next to this module).
    """
    key = os.getenv("GITHUB_PRIVATE_KEY")
    if key:
        # Unescape line breaks.
        return key.replace("\\n", "\n")

    path = Path(os.getenv("GITHUB_PRIVATE_KEY_PATH", DEFAULT_KEY_PATH))
    if not path.is_file():
        raise RuntimeError(
            f"No GitHub private key found at {path}. Either place the .pem "
            f"there, point GITHUB_PRIVATE_KEY_PATH at it, or pass its contents "
            f"in GITHUB_PRIVATE_KEY."
        )
    return path.read_text()


# Loaded at import.
PRIVATE_KEY = _load_private_key()

_cached_token = None
_cached_token_expires_at = 0


# JWT timing in seconds; exp - iat must not exceed ten minutes.
_JWT_BACKDATE = 60
_JWT_LIFETIME = 9 * 60


def generate_jwt():
    """Signed JWT of the GitHub App."""
    issued_at = int(time.time()) - _JWT_BACKDATE
    payload = {
        "iat": issued_at,
        "exp": issued_at + _JWT_LIFETIME,
        "iss": APP_ID,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")


def get_installation_token():
    """Installation access token, cached until shortly before expiry."""
    global _cached_token, _cached_token_expires_at

    if _cached_token and time.time() < _cached_token_expires_at - 60:
        return _cached_token

    jwt_token = generate_jwt()

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }

    url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"

    response = requests.post(url, headers=headers, timeout=10)
    if not response.ok:
        # Error including GitHub's message.
        try:
            detail = response.json().get("message", response.text)
        except ValueError:
            detail = response.text
        raise requests.exceptions.HTTPError(
            f"GitHub refused the App token ({response.status_code}): {detail}",
            response=response,
        )
    data = response.json()

    _cached_token = data["token"]
    _cached_token_expires_at = calendar.timegm(
        time.strptime(data["expires_at"], "%Y-%m-%dT%H:%M:%SZ")
    )

    return _cached_token


def get_github_headers() -> dict:
    """Authorization header for GitHub API requests."""
    return {"Authorization": f"token {get_installation_token()}"}
