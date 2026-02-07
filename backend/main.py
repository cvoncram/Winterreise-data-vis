# backend/main.py
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow Svelte dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILES = 40


@app.get("/api/scores")
async def list_scores(folder: str = Query(...)):
    folder_path = Path(folder)

    if not folder_path.exists() or not folder_path.is_dir():
        raise HTTPException(status_code=400, detail="Folder not found")

    files = [f.name for f in folder_path.glob("*.mei")]
    return files[:MAX_FILES]


@app.get("/api/scores/file")
async def get_score_file(folder: str, filename: str):
    file_path = Path(folder) / filename

    if file_path.exists() and file_path.suffix == ".mei":
        return FileResponse(file_path, media_type="application/xml")

    raise HTTPException(status_code=404, detail="File not found")
