from fastapi import APIRouter, HTTPException, Query, Response
from services.meiParser import parse_rows, parse_mei_metadata, return_relevant_measures
from services.pathSafety import is_safe_repo_path, is_safe_folder_name
from services.githubClient import fetch_repo_text
from config import TITLES

router = APIRouter()

@router.get("/db/file")
def get_file(path: str):
    """MEI file as raw text."""
    if not is_safe_repo_path(path):
        raise HTTPException(status_code=400, detail="Invalid path")

    content = fetch_repo_text(path)
    return Response(content=content, media_type="application/xml")

@router.get("/db/file-measures")
def get_file_measures(piece: int, start: int = Query(ge=0), end: int = Query(ge=0)):
    """Score of one song, cut to a measure range; measure 0 is the pickup."""

    if not 1 <= piece <= len(TITLES):
        raise HTTPException(status_code=404, detail="Piece not found")

    content = fetch_repo_text(TITLES[piece-1])
    score = return_relevant_measures(content, start, end)

    return Response(content=score, media_type="application/xml")

@router.get("/db/parsed-file")
def parse_mei(path: str):
    """Performance file as calibration metadata and per-beat rows."""
    if not is_safe_repo_path(path):
        raise HTTPException(status_code=400, detail="Invalid path")

    xml = fetch_repo_text(path)

    rows = parse_rows(xml)
    metadata = parse_mei_metadata(xml)

    return [{"metadata": metadata}, {"data": rows}]


@router.get("/db/parsed-measures")
def parse_files(
        piece: int,
        start: int = Query(ge=0),
        start_beat: int = Query(ge=1),
        end: int = Query(ge=0),
        end_beat: int = Query(ge=1),
        paths: list[str] = Query(...)
    ):
    """Per-beat rows of a measure range, for several performances of one song."""
    if not 1 <= piece <= len(TITLES):
        raise HTTPException(status_code=404, detail="Piece not found")

    for path in paths:
        if not is_safe_folder_name(path):
            raise HTTPException(status_code=400, detail="Invalid performance path")

    measures = []
    for path in paths:
        xml = fetch_repo_text(f"performances/{path}/{path}_{piece}_Audio_Data.xml")
        measures.append({
            "performance": path,
            "data": parse_rows(xml, start, start_beat, end, end_beat),
            "metadata": parse_mei_metadata(xml)
        })
    return measures