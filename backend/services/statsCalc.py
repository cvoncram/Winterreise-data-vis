"""
Access to the normalization statistics held in the database repository.

The figures themselves are produced by `stats/build_stats.py` there, run by a
GitHub Action on every push that touches performance data. This module only
reads the results, so no computation, caching of raw values or incremental
invalidation happens here any more.

Both the centre and the scale follow the scope, since the two questions are
different ones: within a single piece, only variation inside that piece is at
stake, whereas across the cycle the differences between loud and quiet pieces
belong to the comparison. Scales are scaled median absolute deviations, always
pooled across all recordings so that one unit means the same everywhere.

Dynamics and timbre are centred on the recording's own median, a generally
louder or brighter recording being a matter of recording technique. Tempo is
not: a recording being generally faster is interpretive information, so its
centre comes from the corpus and is the same for every recording — which also
means it cancels out of any comparison between two of them, leaving the scale
as the only figure that affects a distance.
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
    regular result. A piece missing from the corpus statistics therefore ends
    up reported as unavailable rather than silently falling back to the
    cycle-wide figures, which are on a different scale and would understate
    every distance.
    """
    corpus = get_corpus_stats()
    recording = get_recording_stats(performance)

    if scope in ("piece", "measures"):
        medians = recording.get("pieces", {}).get(str(piece), {})
        scales = corpus.get("pieces", {}).get(str(piece), {})
    else:  # cycle / halfCycle — a half is close enough to the whole for the
        # cycle-wide figures to apply, and has no reference of its own.
        medians = recording.get("overall", {})
        scales = corpus.get("cycle", {})

    reference = {
        # "scale" rather than "std": the divisor is a scaled median absolute
        # deviation, not a standard deviation.
        "dynamics": {
            "median": medians.get("dynamicsMedian"),
            "scale": scales.get("dynamics", {}).get("mad"),
        },
        "timbre": {
            # Already log-transformed by the pipeline — do not log it again.
            "logMedian": medians.get("timbreLogMedian"),
            "scale": scales.get("timbre", {}).get("mad"),
        },
        # Tempo takes its centre from the corpus as well, there being no
        # recording-specific tempo median to apply.
        "tempo": {
            "logMedian": scales.get("tempo", {}).get("logMedian"),
            "scale": scales.get("tempo", {}).get("mad"),
        },
    }
    reference["available"] = all(
        v is not None
        for param in ("dynamics", "timbre", "tempo")
        for v in reference[param].values()
    )
    return reference
