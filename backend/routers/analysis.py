from typing import Literal, Optional
import requests
from fastapi import APIRouter, HTTPException, Query
from services.meiParser import parse_rows, parse_mei_metadata
from services.dtwCalc import calculate_dtw_matrix
from services.pathSafety import is_safe_folder_name
from services.githubClient import fetch_repo_text
from config import TITLES

router = APIRouter()


def _rows_for_performance(
    path: str,
    piece: int,
    start: Optional[int] = None,
    start_beat: Optional[int] = None,
    end: Optional[int] = None,
    end_beat: Optional[int] = None,
):
    """Fetch and parse one piece's performance file for one recording."""
    xml = fetch_repo_text(f"performances/{path}/{path}_{piece}_Audio_Data.xml")
    return parse_rows(xml, start, start_beat, end, end_beat), parse_mei_metadata(xml)


@router.get("/db/analysis")
def calculate_dtw(
    parameter: str,
    paths: list[str] = Query(...),
    scope: Literal["piece", "cycle", "halfCycle", "measures"] = "piece",
    piece: Optional[int] = None,
    half: Optional[int] = None,
    start: Optional[int] = None,
    start_beat: Optional[int] = None,
    end: Optional[int] = None,
    end_beat: Optional[int] = None,
):
    for path in paths:
        if not is_safe_folder_name(path):
            raise HTTPException(status_code=400, detail="Invalid performance path")

    if scope in ("piece", "measures") and piece is None:
        raise HTTPException(status_code=400, detail="piece is required for this scope")
    if scope == "halfCycle" and half not in (1, 2):
        raise HTTPException(status_code=400, detail="half must be 1 or 2 for scope=halfCycle")
    if scope == "measures" and None in (start, start_beat, end, end_beat):
        raise HTTPException(
            status_code=400,
            detail="start/start_beat/end/end_beat are required for scope=measures",
        )

    if scope in ("piece", "measures"):
        pieces = [piece]
    elif scope == "halfCycle":
        pieces = list(range(1, 13)) if half == 1 else list(range(13, len(TITLES) + 1))
    else:  # cycle
        pieces = list(range(1, len(TITLES) + 1))

    # cycle/halfCycle span many pieces per performance, and not every
    # recording covers every piece of the cycle — missing pieces are
    # skipped rather than failing the whole request.
    skip_missing = scope in ("cycle", "halfCycle")

    performances = []
    for path in paths:
        all_rows = []
        metadata = None
        for p in pieces:
            try:
                if scope == "measures":
                    rows, piece_metadata = _rows_for_performance(path, p, start, start_beat, end, end_beat)
                else:
                    rows, piece_metadata = _rows_for_performance(path, p)
            except requests.exceptions.HTTPError as e:
                if skip_missing and e.response is not None and e.response.status_code == 404:
                    continue
                raise
            all_rows.extend(rows)
            if metadata is None:
                metadata = piece_metadata
        performances.append({"data": all_rows, "metadata": metadata})

    result = calculate_dtw_matrix(parameter, piece, performances)
    result["scope"] = scope
    return result
