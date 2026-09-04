import calendar
import os
import time
from pathlib import Path

import jwt
import requests

BASE_DIR = Path(__file__).resolve().parent

# Identifiers of the GitHub App, not secret in themselves. Overridable so the
# application can be pointed at a different installation without editing code.
APP_ID = os.getenv("GITHUB_APP_ID", "2827092")
INSTALLATION_ID = os.getenv("GITHUB_INSTALLATION_ID", "108972344")

DEFAULT_KEY_PATH = BASE_DIR / "winterreise-database-test.2026-02-09.private-key.pem"


def _load_private_key() -> str:
    """
    The App's signing key — the one secret the system holds.

    Read from a file whose location is configurable, so that a container can
    have it mounted at run time and never carry it inside the image. Reading
    it from an environment variable is supported as well, but the file is
    preferable: environment variables are visible to anything that can inspect
    the process, and they turn up in logs and crash reports.
    """
    key = os.getenv("GITHUB_PRIVATE_KEY")
    if key:
        # A PEM passed through the environment almost always arrives with its
        # line breaks escaped.
        return key.replace("\\n", "\n")

    path = Path(os.getenv("GITHUB_PRIVATE_KEY_PATH", DEFAULT_KEY_PATH))
    if not path.is_file():
        raise RuntimeError(
            f"No GitHub private key found at {path}. Either place the .pem "
            f"there, point GITHUB_PRIVATE_KEY_PATH at it, or pass its contents "
            f"in GITHUB_PRIVATE_KEY."
        )
    return path.read_text()


# Loaded once at import: without it nothing can be fetched, so failing here is
# preferable to failing on the first request.
PRIVATE_KEY = _load_private_key()

_cached_token = None
_cached_token_expires_at = 0


# GitHub rejects an App JWT whose lifetime exceeds ten minutes, measured as
# `exp` minus `iat` — not as `exp` minus the current time. Backdating `iat` to
# absorb clock skew therefore eats into the same allowance, and the two
# together must stay under the limit. Nine minutes leaves room to spare; the
# token is only ever used for the exchange immediately below, so a longer life
# would buy nothing anyway.
_JWT_BACKDATE = 60
_JWT_LIFETIME = 9 * 60


def generate_jwt():
    issued_at = int(time.time()) - _JWT_BACKDATE
    payload = {
        "iat": issued_at,
        "exp": issued_at + _JWT_LIFETIME,
        "iss": APP_ID,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")


def get_installation_token():
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
        # GitHub explains authentication failures precisely — "'Expiration
        # time' claim ('exp') is too far in the future", "A JSON web token
        # could not be decoded" — and raise_for_status() discards that,
        # leaving only a bare 401 to guess from.
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
    return {"Authorization": f"token {get_installation_token()}"}
