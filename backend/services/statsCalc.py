"""
Access to the normalization statistics held in the database repository.

The figures themselves are produced by `stats/build_stats.py` there, run by a
GitHub Action on every push that touches performance data. This module only
reads the results, so no computation, caching of raw values or incremental
invalidation happens here any more.

Centering uses each recording's median (per piece for piece/measures scope,
per recording overall for cycle/halfCycle scope); scaling uses a corpus-wide
scaled median absolute deviation. Tempo is not centred per recording — a
recording being generally faster is interpretive information, not a recording
artefact — and therefore has a single corpus-wide reference.
"""

import json
import time
from typing import Optional

import requests

from services.githubClient import fetch_repo_text

CORPUS_PATH = "stats/corpus.json"
RECORDING_PATH = "stats/recordings/{name}.json"

# The statistics change only when the Action runs, so a short-lived process
# cache is enough to keep a single visualization from issuing one GitHub
# request per selected performance.
_TTL_SECONDS = 300
_cache: dict[str, tuple[float, Optional[dict]]] = {}


def _fetch_json(path: str) -> Optional[dict]:
    """
    Read one statistics file, or None if it is not available.

    A missing file is a legitimate state — the Action may never have run, or a
    recording may have been added since the last run — so it is reported as
    absence rather than raised, letting callers degrade gracefully.
    """
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
    """Drop the process cache, so the next read hits the repository again."""
    _cache.clear()


def get_corpus_stats() -> dict:
    return _fetch_json(CORPUS_PATH) or {}


def get_recording_stats(performance: str) -> dict:
    return _fetch_json(RECORDING_PATH.format(name=performance)) or {}


def get_report() -> dict:
    """Data-quality report written alongside the statistics."""
    return _fetch_json("stats/report.json") or {}


def get_normalization_reference(performance: str, piece: Optional[str], scope: str) -> dict:
    """
    Centering and scaling figures needed to normalize one performance's beat
    data for the given scope.

    `available` reports whether every figure could be resolved. A caller that
    proceeds without it still gets a usable result, but one computed on
    untransformed values — which is not otherwise distinguishable from a
    regular result.
    """
    corpus = get_corpus_stats()
    recording = get_recording_stats(performance)

    if scope in ("piece", "measures"):
        entry = recording.get("pieces", {}).get(str(piece), {})
        dynamics_median = entry.get("dynamicsMedian")
        # Already log-transformed by the pipeline — do not take the log again.
        timbre_log_median = entry.get("timbreLogMedian")
        dynamics_scale = corpus.get("dynamics", {}).get("madVsPiece")
        timbre_scale = corpus.get("timbre", {}).get("madVsPiece")
    else:  # cycle / halfCycle
        overall = recording.get("overall", {})
        dynamics_median = overall.get("dynamicsMedian")
        timbre_log_median = overall.get("timbreLogMedian")
        dynamics_scale = corpus.get("dynamics", {}).get("madVsPerformance")
        timbre_scale = corpus.get("timbre", {}).get("madVsPerformance")

    tempo_log_median = corpus.get("tempo", {}).get("logMedian")
    tempo_scale = corpus.get("tempo", {}).get("mad")

    reference = {
        # "scale" rather than "std": the divisor is a scaled median absolute
        # deviation, not a standard deviation.
        "dynamics": {"median": dynamics_median, "scale": dynamics_scale},
        "timbre": {"logMedian": timbre_log_median, "scale": timbre_scale},
        "tempo": {"logMedian": tempo_log_median, "scale": tempo_scale},
    }
    reference["available"] = all(
        v is not None
        for param in ("dynamics", "timbre", "tempo")
        for v in reference[param].values()
    )
    return reference
