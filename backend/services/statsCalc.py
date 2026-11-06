"""
Read access to the normalization statistics in the database repository
(built there by stats/build_stats.py).
"""

import json
import time
from typing import Literal, Optional

import requests

from services.githubClient import fetch_repo_text

CORPUS_PATH = "stats/corpus.json"
RECORDING_PATH = "stats/recordings/{name}.json"

# Lifetime of cached statistics files, in seconds.
_TTL_SECONDS = 300
_cache: dict[str, tuple[float, Optional[dict]]] = {}


def _fetch_json(path: str) -> Optional[dict]:
    """One statistics file, or None if it is not available."""
    now = time.time()
    cached = _cache.get(path)
    if cached and now - cached[0] < _TTL_SECONDS:
        return cached[1]

    try:
        data = json.loads(fetch_repo_text(path))
    except (requests.exceptions.HTTPError, json.JSONDecodeError):
        data = None

    _cache[path] = (now, data)
    return data


def clear_cache() -> None:
    """Empty the statistics cache."""
    _cache.clear()


def get_corpus_stats() -> dict:
    return _fetch_json(CORPUS_PATH) or {}


def get_recording_stats(performance: str) -> dict:
    return _fetch_json(RECORDING_PATH.format(name=performance)) or {}


def get_report() -> dict:
    """Data-quality report written alongside the statistics."""
    return _fetch_json("stats/report.json") or {}


# Keys per method: dynamics centre, timbre centre, tempo centre, scale.
_METHOD_KEYS = {
    "mean": ("dynamicsMean", "timbreLogMean", "logMean", "sd"),
    "median": ("dynamicsMedian", "timbreLogMedian", "logMedian", "mad"),
}


def get_covariance(
    piece: Optional[str], scope: str, parameters: list, method: Literal["mean", "median"] = "mean"
) -> Optional[list]:
    """
    Corpus covariance of the selected parameters on the normalized scale of
    the chosen method, or None if the statistics do not contain it.
    """
    corpus = get_corpus_stats()
    block = (
        corpus.get("pieces", {}).get(str(piece), {})
        if scope in ("piece", "measures")
        else corpus.get("cycle", {})
    )

    covariance = block.get("covariance")
    if not covariance:
        return None

    order = covariance.get("order", [])
    if any(parameter not in order for parameter in parameters):
        return None
    index = [order.index(parameter) for parameter in parameters]

    scale_key = _METHOD_KEYS[method][3]
    scales = [block.get(parameter, {}).get(scale_key) for parameter in parameters]
    if any(not scale for scale in scales):
        return None

    matrix = covariance["matrix"]
    return [
        [matrix[index[a]][index[b]] / (scales[a] * scales[b]) for b in range(len(parameters))]
        for a in range(len(parameters))
    ]


def get_normalization_reference(
    performance: str, piece: Optional[str], scope: str, method: Literal["mean", "median"] = "mean"
) -> dict:
    """
    Centres and scales for normalizing one performance in the given scope.
    `method`: mean/SD (default) or median/MAD. `available`: all figures found.
    """
    corpus = get_corpus_stats()
    recording = get_recording_stats(performance)

    if scope in ("piece", "measures"):
        centres = recording.get("pieces", {}).get(str(piece), {})
        scales = corpus.get("pieces", {}).get(str(piece), {})
    else:  # cycle / halfCycle
        centres = recording.get("overall", {})
        scales = corpus.get("cycle", {})

    dynamics_key, timbre_key, tempo_key, scale_key = _METHOD_KEYS[method]

    reference = {
        "dynamics": {
            "center": centres.get(dynamics_key),
            "scale": scales.get("dynamics", {}).get(scale_key),
        },
        "timbre": {
            # Already log-transformed.
            "logCenter": centres.get(timbre_key),
            "scale": scales.get("timbre", {}).get(scale_key),
        },
        # Corpus-wide centre.
        "tempo": {
            "logCenter": scales.get("tempo", {}).get(tempo_key),
            "scale": scales.get("tempo", {}).get(scale_key),
        },
    }
    reference["available"] = all(
        v is not None
        for param in ("dynamics", "timbre", "tempo")
        for v in reference[param].values()
    )
    reference["method"] = method
    return reference
