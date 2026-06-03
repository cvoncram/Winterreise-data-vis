from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from routers import files, scores, performances, analysis

app = FastAPI()

app.include_router(files.router)
app.include_router(scores.router)
app.include_router(performances.router)
app.include_router(analysis.router)

BASE_DIR = Path(__file__).resolve().parent
FAVICON_PATH = BASE_DIR / "static" / "favicon.png"

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(FAVICON_PATH)