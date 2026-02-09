import time
import jwt
import requests

APP_ID = "2827092"
INSTALLATION_ID = "108972344"

with open("winterreise-database-test.2026-02-09.private-key.pem", "r") as f:
    PRIVATE_KEY = f.read()


def generate_jwt():
    payload = {
        "iat": int(time.time()) - 60,
        "exp": int(time.time()) + (10 * 60),
        "iss": APP_ID,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm="RS256")


def get_installation_token():
    jwt_token = generate_jwt()

    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github+json",
    }

    url = f"https://api.github.com/app/installations/{INSTALLATION_ID}/access_tokens"

    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]
