from typing import List, Literal, Optional
import numpy as np
import requests
from fastapi import APIRouter, HTTPException, Query
from services.meiParser import parse_rows, parse_mei_metadata
from services.dtwCalc import combined_dtw_matrix, normalize_series
from services.statsCalc import get_normalization_reference
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
    paths: list[str] = Query(...),
    parameters: List[str] = Query(...),
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[List[float]] = Query(None),
    scope: Literal["piece", "cycle", "halfCycle", "measures"] = "piece",
    piece: Optional[int] = None,
    half: Optional[int] = None,
    start: Optional[int] = None,
    start_beat: Optional[int] = None,
    end: Optional[int] = None,
    end_beat: Optional[int] = None,
):
    if not parameters:
        raise HTTPException(status_code=400, detail="parameters is required")
    if weights is not None and len(weights) != len(parameters):
        raise HTTPException(status_code=400, detail="weights must be the same length as parameters")
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

    # Rows are kept per piece rather than concatenated: the alignment runs
    # separately for each piece, so that it cannot run across the boundary
    # between two songs.
    performances = []
    for path in paths:
        rows_by_piece = {}
        for p in pieces:
            try:
                if scope == "measures":
                    rows, _ = _rows_for_performance(path, p, start, start_beat, end, end_beat)
                else:
                    rows, _ = _rows_for_performance(path, p)
            except requests.exceptions.HTTPError as e:
                if skip_missing and e.response is not None and e.response.status_code == 404:
                    continue
                raise
            rows_by_piece[p] = rows
        performances.append(rows_by_piece)

    def _is_usable(r, kind: str) -> bool:
        value = r.get(kind)
        if value is None:
            return False
        if kind == "dynamics":
            try:
                float(value)
            except ValueError:
                return False
        return True

    sequences = []
    for path, rows_by_piece in zip(paths, performances):
        reference_by_kind = get_normalization_reference(path, piece, scope)
        by_piece = {}
        for p, rows in rows_by_piece.items():
            selected_rows = [
                r for r in rows if all(_is_usable(r, kind) for kind in parameters)
            ]
            dims = [
                normalize_series(
                    [r[kind] for r in selected_rows], kind, reference_by_kind[kind]
                )
                for kind in parameters
            ]
            by_piece[p] = (
                np.stack(dims, axis=1) if dims else np.empty((0, len(parameters)))
            )
        sequences.append(by_piece)

    result = combined_dtw_matrix(sequences, metric, weights)

    # Warnings carry positional indices; name the recordings so the message is
    # readable without the caller having to map them back.
    for warning in result["warnings"]:
        warning["performances"] = [paths[warning["i"]], paths[warning["j"]]]

    result["parameters"] = parameters
    result["metric"] = metric
    result["weights"] = weights
    result["piece"] = piece
    result["scope"] = scope
    return result
