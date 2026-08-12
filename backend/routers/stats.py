from fastapi import APIRouter, HTTPException

from services.pathSafety import is_safe_folder_name
from services.statsCalc import (
    clear_cache,
    get_corpus_stats,
    get_normalization_reference,
    get_recording_stats,
    get_report,
)

router = APIRouter()


@router.get("/db/stats/corpus")
def get_corpus():
    return get_corpus_stats()


@router.get("/db/stats/performances")
def get_performance_stats(performance: str):
    """
    Medians for one recording. Scoped to a single recording rather than the
    whole corpus, since each one is a separate file in the database repo.
    """
    if not is_safe_folder_name(performance):
        raise HTTPException(status_code=400, detail="Invalid performance path")
    stats = get_recording_stats(performance)
    if not stats:
        raise HTTPException(status_code=404, detail="No statistics for this recording")
    return stats


@router.get("/db/stats/report")
def get_stats_report():
    """Data-quality report from the last statistics build."""
    return get_report()


@router.get("/db/stats/normalization-reference")
def get_normalization_reference_route(performance: str, piece: int):
    if not is_safe_folder_name(performance):
        raise HTTPException(status_code=400, detail="Invalid performance path")
    return get_normalization_reference(performance, piece, scope="piece")


@router.post("/db/stats/refresh")
def refresh():
    """
    Drop the process cache so the next read picks up a freshly built set of
    statistics without waiting for the cache to expire. The statistics
    themselves are built in the database repository, not here.
    """
    clear_cache()
    return {"cleared": True}
