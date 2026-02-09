# MEI Score Viewer – Backend (FastAPI)

This FastAPI backend serves MEI files directly from a GitHub repository.  
It acts as a lightweight proxy between the frontend and GitHub.

---

## Tech Stack

- FastAPI
- Requests
- GitHub App authentication
- Python 3.10+

---

## Requirements

- Python 3.10+
- GitHub App credentials

---

## Installation

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Running the Server

```bash
uvicorn main:app --reload
```

Server runs on:

```
http://127.0.0.1:8000
```

---

## GitHub Configuration

The backend authenticates using a GitHub App installation token.

You must configure:

- `OWNER`
- `REPO`
- `BRANCH`
- GitHub App private key
- App ID
- Installation ID

These are used to generate an installation token for accessing the repository.

---

## API Endpoints

### List MEI files

```
GET /db/scores-folder
```

Returns a JSON object of files in the `scores/` folder of the repo.

---

### Get MEI file content

```
GET /db/file?path=scores/<filename>.mei
```

Returns:

```json
{
  "content": "<MEI XML here>"
}
```

The backend decodes the base64 content returned by GitHub.

---

## How it works

1. Frontend calls `/db/scores-folder`
2. Backend queries GitHub API for contents of `/scores`
3. Frontend selects a file and calls `/db/file`
4. Backend fetches file from GitHub and returns decoded MEI XML

---

## Important Files

| File | Purpose |
|-----|---------|
| `main.py` | FastAPI app and routes |
| `auth.py` | GitHub App token generation |
| `requirements.txt` | Dependencies |

---

## Common Pitfalls

### 422 Unprocessable Entity
You passed `filename=` instead of `path=`.

### GitHub 401/403
Installation token failed — check GitHub App credentials.

### Works in backend but not frontend
This is almost always a Vite proxy issue.

---

## Testing endpoints directly

In browser or curl:

```
http://127.0.0.1:8000/db/scores-folder
http://127.0.0.1:8000/db/file?path=scores/1-Gute_Nacht.mei
```
