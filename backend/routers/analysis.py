import json
from typing import List, Literal, Optional
import numpy as np
import requests
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from services.meiParser import parse_rows, parse_mei_metadata
from services.dtwCalc import combined_dtw_matrix_iter, normalize_series, pair_analysis
from services.statsCalc import get_covariance, get_normalization_reference
from services.pathSafety import is_safe_folder_name
from services.githubClient import fetch_repo_text
from config import PIECE_TITLES, TITLES

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


def _validate_request(paths, parameters, weights, scope, piece, half, start, start_beat, end, end_beat):
    """Everything both analysis endpoints need to agree on before fetching anything."""
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


def _sequences(
    paths, parameters, scope, piece, half, start, start_beat, end, end_beat, normalization
) -> tuple:
    """Sequences and measure labels, for callers that do not follow progress."""
    for update in _sequences_iter(
        paths, parameters, scope, piece, half, start, start_beat, end, end_beat, normalization
    ):
        if "sequences" in update:
            return update["sequences"], update["measures"], update["raw"]
    return [], [], []


def _sequences_iter(
    paths, parameters, scope, piece, half, start, start_beat, end, end_beat, normalization
):
    """
    One normalized sequence per recording and piece, ready to be aligned,
    and the measure label of every beat that went into it.

    Kept as a helper because the network and the detail view of a single pair
    have to see exactly the same data; a difference between them would show
    up as two numbers for the same comparison. The labels are what lets the
    detail view name a place in the score instead of a beat number.

    Handed out as progress updates, because every file is a separate request
    to GitHub: a whole cycle for 26 recordings means several hundred of them,
    and that, not the computation, is what the waiting consists of. The last
    item carries the finished sequences and labels.
    """
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
    fetched = 0
    total_files = len(paths) * len(pieces)
    for path in paths:
        rows_by_piece = {}
        for p in pieces:
            fetched += 1
            yield {"stage": "fetching", "done": fetched, "total": total_files}
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
        # The parser already rejects what cannot be measured — non-numeric
        # dynamics readings and infinities alike. Tempo and timbre are
        # log-transformed, so a zero has to go as well: normalize_series would
        # otherwise drop it from that one parameter only, and the parameters
        # would no longer line up beat by beat.
        value = r.get(kind)
        return value is not None and (kind == "dynamics" or value > 0)

    sequences = []
    measures = []
    raw = []
    for path, rows_by_piece in zip(paths, performances):
        reference_by_kind = get_normalization_reference(path, piece, scope, normalization)
        by_piece = {}
        measures_by_piece = {}
        raw_by_piece = {}
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
            measures_by_piece[p] = [r["measure"] for r in selected_rows]
            # Kept untransformed as well, so that a difference can be given in
            # beats per minute and decibels and not only in scale units.
            raw_by_piece[p] = {
                kind: [r[kind] for r in selected_rows] for kind in parameters
            }
        sequences.append(by_piece)
        measures.append(measures_by_piece)
        raw.append(raw_by_piece)

    yield {"sequences": sequences, "measures": measures, "raw": raw}


def _analysis_events(
    paths, parameters, metric, weights, normalization, scope, piece, half, start, start_beat, end, end_beat
):
    """
    The network analysis as a sequence of progress updates, the last of which
    carries the finished result. Both the plain endpoint and the streaming
    one go through it, so that they cannot drift apart.
    """
    sequences = []
    for update in _sequences_iter(
        paths, parameters, scope, piece, half, start, start_beat, end, end_beat, normalization
    ):
        if "sequences" in update:
            sequences = update["sequences"]
        else:
            yield update

    # Mahalanobis without this would measure against the spread of whatever
    # was selected, so the same pair would come out differently in another run.
    covariance = get_covariance(piece, scope, parameters, normalization) if metric == "mahalanobis" else None

    for update in combined_dtw_matrix_iter(sequences, metric, weights, covariance):
        if "result" not in update:
            yield update
            continue

        result = update["result"]
        # Warnings carry positional indices; name the recordings so the
        # message is readable without the caller having to map them back.
        for warning in result["warnings"]:
            warning["performances"] = [paths[warning["i"]], paths[warning["j"]]]

        result["parameters"] = parameters
        result["metric"] = metric
        result["weights"] = weights
        result["normalization"] = normalization
        result["piece"] = piece
        result["scope"] = scope
        if metric == "mahalanobis":
            result["covarianceSource"] = "corpus" if covariance else "selection"
        yield {"result": result}


@router.get("/db/analysis")
def calculate_dtw(
    paths: list[str] = Query(...),
    parameters: List[str] = Query(...),
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[List[float]] = Query(None),
    normalization: Literal["mean", "median"] = "mean",
    scope: Literal["piece", "cycle", "halfCycle", "measures"] = "piece",
    piece: Optional[int] = None,
    half: Optional[int] = None,
    start: Optional[int] = None,
    start_beat: Optional[int] = None,
    end: Optional[int] = None,
    end_beat: Optional[int] = None,
):
    _validate_request(paths, parameters, weights, scope, piece, half, start, start_beat, end, end_beat)
    for update in _analysis_events(
        paths, parameters, metric, weights, normalization, scope, piece, half, start, start_beat, end, end_beat
    ):
        if "result" in update:
            return update["result"]
    raise HTTPException(status_code=500, detail="the analysis produced no result")


@router.get("/db/analysis/stream")
def stream_dtw(
    paths: list[str] = Query(...),
    parameters: List[str] = Query(...),
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[List[float]] = Query(None),
    normalization: Literal["mean", "median"] = "mean",
    scope: Literal["piece", "cycle", "halfCycle", "measures"] = "piece",
    piece: Optional[int] = None,
    half: Optional[int] = None,
    start: Optional[int] = None,
    start_beat: Optional[int] = None,
    end: Optional[int] = None,
    end_beat: Optional[int] = None,
):
    """
    The same analysis as /db/analysis, sent as server-sent events so that the
    browser can show how far it has got. Every event is one JSON object:
    either a progress update, the result, or an error.
    """
    _validate_request(paths, parameters, weights, scope, piece, half, start, start_beat, end, end_beat)

    def events():
        try:
            for update in _analysis_events(
                paths, parameters, metric, weights, normalization, scope, piece, half,
                start, start_beat, end, end_beat
            ):
                yield f"data: {json.dumps(update)}\n\n"
        except Exception as error:
            # Once the response has begun there is no status code left to set,
            # so a failure has to travel as an event of its own; otherwise the
            # browser would only see the stream close and could not say why.
            yield f"data: {json.dumps({'error': str(error)})}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/db/analysis/pair")
def analyse_pair(
    paths: list[str] = Query(...),
    parameters: List[str] = Query(...),
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[List[float]] = Query(None),
    normalization: Literal["mean", "median"] = "mean",
    scope: Literal["piece", "cycle", "halfCycle", "measures"] = "piece",
    piece: Optional[int] = None,
    half: Optional[int] = None,
    start: Optional[int] = None,
    start_beat: Optional[int] = None,
    end: Optional[int] = None,
    end_beat: Optional[int] = None,
):
    """
    One link of the network taken apart: the same comparison the matrix
    shows, but piece by piece and with the floor each piece produces anyway.
    """
    if len(paths) != 2:
        raise HTTPException(status_code=400, detail="exactly two paths are required")
    _validate_request(paths, parameters, weights, scope, piece, half, start, start_beat, end, end_beat)

    sequences, measures, raw = _sequences(
        paths, parameters, scope, piece, half, start, start_beat, end, end_beat, normalization
    )
    covariance = get_covariance(piece, scope, parameters, normalization) if metric == "mahalanobis" else None
    result = pair_analysis(
        sequences[0], sequences[1], parameters, metric, weights,
        measures_by_piece=measures[0], raw_by_piece=raw, covariance=covariance,
    )
    if metric == "mahalanobis":
        result["covarianceSource"] = "corpus" if covariance else "selection"

    for row in result["pieces"] + result["differences"]:
        row["title"] = PIECE_TITLES[row["piece"] - 1]
    result["performances"] = paths
    result["parameters"] = parameters
    result["metric"] = metric
    result["weights"] = weights
    result["normalization"] = normalization
    result["scope"] = scope
    return result
