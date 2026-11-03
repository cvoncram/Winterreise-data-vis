import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routers import files, scores, performances, analysis, stats

app = FastAPI()

# Allowed origins (the Vite dev server by default).
_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins.split(",") if o.strip()],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.get("/health", include_in_schema=False)
def health():
    """Liveness probe."""
    return {"status": "ok"}

app.include_router(files.router)
app.include_router(scores.router)
app.include_router(performances.router)
app.include_router(analysis.router)
app.include_router(stats.router)

BASE_DIR = Path(__file__).resolve().parent
FAVICON_PATH = BASE_DIR / "static" / "favicon.png"

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(FAVICON_PATH)