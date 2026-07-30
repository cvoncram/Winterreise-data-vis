from fastapi import APIRouter
from services.statsCalc import (
    recompute_stats,
    get_stats_summary,
    get_corpus_stats,
    get_normalization_reference,
)

router = APIRouter()


@router.post("/db/stats/recompute")
def recompute():
    return recompute_stats()


@router.get("/db/stats/performances")
def get_performance_stats():
    return get_stats_summary()


@router.get("/db/stats/corpus")
def get_corpus():
    return get_corpus_stats()


@router.get("/db/stats/normalization-reference")
def get_normalization_reference_route(performance: str, piece: int):
    return get_normalization_reference(performance, piece, scope="piece")
