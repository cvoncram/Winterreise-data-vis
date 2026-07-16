import time
import calendar
from pathlib import Path
import jwt
import requests

APP_ID = "2827092"
INSTALLATION_ID = "108972344"

BASE_DIR = Path(__file__).resolve().parent
PRIVATE_KEY_PATH = BASE_DIR / "winterreise-database-test.2026-02-09.private-key.pem"

with open(PRIVATE_KEY_PATH, "r") as f:
    PRIVATE_KEY = f.read()

_cached_token = None
_cached_token_expires_at = 0


def generate_jwt():
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
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
    response.raise_for_status()
    data = response.json()

    _cached_token = data["token"]
    _cached_token_expires_at = calendar.timegm(
        time.strptime(data["expires_at"], "%Y-%m-%dT%H:%M:%SZ")
    )

    return _cached_token


def get_github_headers() -> dict:
    return {"Authorization": f"token {get_installation_token()}"}
