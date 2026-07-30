import json
import math
import re
import statistics
from pathlib import Path
from typing import Optional

from services.githubClient import fetch_repo_tree, fetch_repo_text
from services.meiParser import parse_rows, parse_mei_metadata
from services.dtwCalc import convert_dynamics

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_FILE = CACHE_DIR / "performance_stats.json"

PIECE_FILE_RE = re.compile(r"^performances/([^/]+)/.*_(\d+)_Audio_Data\.xml$")

# Fields added for the normalization pipeline. A cached piece missing any of
# these (even with a matching fileSha) is treated as needing recompute, so
# the schema backfills itself on the next call — no separate migration.
NEW_PIECE_FIELDS = (
    "tempoMedian",
    "tempoValues",
    "dynamicsMedianSigned",
    "dynamicsResidualVsPiece",
    "dynamicsResidualVsPerformance",
    "timbreResidualVsPiece",
    "timbreResidualVsPerformance",
)

EMPTY_SUM_STATS = {"count": 0, "sum": 0.0, "sumSq": 0.0}


def load_stats() -> dict:
    if not CACHE_FILE.exists():
        return {"performances": {}, "corpus": {}}
    with open(CACHE_FILE, "r") as f:
        data = json.load(f)
    data.setdefault("performances", {})
    data.setdefault("corpus", {})
    return data


def save_stats(data: dict) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _median(values: list) -> Optional[float]:
    if not values:
        return None
    return statistics.median(values)


def _population_std(values: list) -> Optional[float]:
    if not values:
        return None
    return statistics.pstdev(values)


def _sum_stats(values: list) -> dict:
    return {"count": len(values), "sum": sum(values), "sumSq": sum(v * v for v in values)}


def _std_from_sum_stats(stats_list: list[dict]) -> Optional[float]:
    total_count = sum(s["count"] for s in stats_list)
    if total_count == 0:
        return None
    total_sum = sum(s["sum"] for s in stats_list)
    total_sumSq = sum(s["sumSq"] for s in stats_list)
    mean = total_sum / total_count
    variance = max(total_sumSq / total_count - mean * mean, 0.0)
    return math.sqrt(variance)


def _fetch_piece_values(path: str) -> Optional[dict]:
    xml = fetch_repo_text(path)
    rows = parse_rows(xml)
    metadata = parse_mei_metadata(xml)
    if metadata is None:
        # Missing calibration block (older-pipeline file) — leave this
        # piece unprocessed for now rather than crashing the whole
        # recompute; it'll be retried on future calls until the data (or
        # its fileSha) changes.
        return None

    # Existing abs-valued, categorical-aware conversion — used only for the
    # pre-existing display median (statsCalc's original feature).
    dynamics_values_abs = convert_dynamics(
        [r["dynamics"] for r in rows if r["dynamics"] is not None], metadata
    )
    # Raw signed dynamics value (the `n` attribute is numeric for normal
    # beats, but can still be "extreme" or "" for edge-case markings — those
    # are skipped here, same as they fall through to 0.0 in convert_dynamics).
    dynamics_values_signed = []
    for r in rows:
        if r["dynamics"] is None:
            continue
        try:
            dynamics_values_signed.append(float(r["dynamics"]))
        except ValueError:
            continue
    timbre_values = [r["timbre"] for r in rows if r["timbre"] is not None]
    tempo_values = [r["tempo"] for r in rows if r["tempo"] is not None]

    return {
        "dynamicsValuesAbs": dynamics_values_abs,
        "dynamicsValuesSigned": dynamics_values_signed,
        "timbreValues": timbre_values,
        "tempoValues": tempo_values,
    }


def recompute_stats() -> dict:
    stats = load_stats()
    performances = stats["performances"]

    tree = fetch_repo_tree()

    current_by_performance: dict = {}
    for item in tree:
        if item.get("type") != "blob":
            continue
        match = PIECE_FILE_RE.match(item["path"])
        if not match:
            continue
        performance_name, piece_num = match.group(1), match.group(2)
        current_by_performance.setdefault(performance_name, []).append(
            (piece_num, item["path"], item["sha"])
        )

    total_pieces = 0
    recomputed = []
    touched_performances = set()

    # Pass 1: detect changed/new/not-yet-migrated pieces, no fetching yet.
    for performance_name, piece_entries in current_by_performance.items():
        perf_entry = performances.setdefault(performance_name, {"pieces": {}, "overall": {}})
        for piece_num, _path, sha in piece_entries:
            total_pieces += 1
            existing_piece = perf_entry["pieces"].get(piece_num)
            needs_recompute = (
                existing_piece is None
                or existing_piece.get("fileSha") != sha
                or any(field not in existing_piece for field in NEW_PIECE_FIELDS)
            )
            if needs_recompute:
                touched_performances.add(performance_name)
                recomputed.append({"performance": performance_name, "piece": piece_num})

    # Pass 2: for touched performances, fetch every one of their pieces once
    # to recompute per-piece stats, then performance-level overall stats.
    skipped = []
    for performance_name in touched_performances:
        perf_entry = performances[performance_name]
        fetched: dict[str, dict] = {}
        all_dynamics_abs = []
        all_dynamics_signed = []
        all_timbre = []

        for piece_num, path, sha in current_by_performance[performance_name]:
            values = _fetch_piece_values(path)
            if values is None:
                skipped.append({"performance": performance_name, "piece": piece_num})
                continue
            fetched[piece_num] = values
            perf_entry["pieces"][piece_num] = {
                "fileSha": sha,
                "dynamicsMedian": _median(values["dynamicsValuesAbs"]),
                "dynamicsMedianSigned": _median(values["dynamicsValuesSigned"]),
                "timbreMedian": _median(values["timbreValues"]),
                "tempoMedian": _median(values["tempoValues"]),
                "tempoValues": values["tempoValues"],
            }
            all_dynamics_abs.extend(values["dynamicsValuesAbs"])
            all_dynamics_signed.extend(values["dynamicsValuesSigned"])
            all_timbre.extend(values["timbreValues"])

        overall_dynamics_median_signed = _median(all_dynamics_signed)
        overall_timbre_median = _median(all_timbre)
        log_overall_timbre_median = (
            math.log(overall_timbre_median) if overall_timbre_median else None
        )

        perf_entry["overall"] = {
            "dynamicsMedian": _median(all_dynamics_abs),
            "dynamicsMedianSigned": overall_dynamics_median_signed,
            "timbreMedian": overall_timbre_median,
        }

        # Residual sums, now that both piece- and performance-level medians
        # are known (used to derive corpus-wide spread further down).
        for piece_num, values in fetched.items():
            piece_entry = perf_entry["pieces"][piece_num]
            piece_dyn_median = piece_entry["dynamicsMedianSigned"]
            piece_timbre_median = piece_entry["timbreMedian"]
            log_piece_timbre_median = (
                math.log(piece_timbre_median) if piece_timbre_median else None
            )

            dyn_signed = values["dynamicsValuesSigned"]
            log_timbre_vals = [math.log(v) for v in values["timbreValues"] if v > 0]

            piece_entry["dynamicsResidualVsPiece"] = (
                _sum_stats([v - piece_dyn_median for v in dyn_signed])
                if piece_dyn_median is not None else dict(EMPTY_SUM_STATS)
            )
            piece_entry["dynamicsResidualVsPerformance"] = (
                _sum_stats([v - overall_dynamics_median_signed for v in dyn_signed])
                if overall_dynamics_median_signed is not None else dict(EMPTY_SUM_STATS)
            )
            piece_entry["timbreResidualVsPiece"] = (
                _sum_stats([v - log_piece_timbre_median for v in log_timbre_vals])
                if log_piece_timbre_median is not None else dict(EMPTY_SUM_STATS)
            )
            piece_entry["timbreResidualVsPerformance"] = (
                _sum_stats([v - log_overall_timbre_median for v in log_timbre_vals])
                if log_overall_timbre_median is not None else dict(EMPTY_SUM_STATS)
            )

    # Corpus-wide aggregation: cheap, combines already-cached per-piece data
    # (touched this call + previously cached), no extra network calls.
    all_tempo_values = []
    dyn_vs_piece_stats = []
    dyn_vs_perf_stats = []
    timbre_vs_piece_stats = []
    timbre_vs_perf_stats = []

    for perf_entry in performances.values():
        for piece_entry in perf_entry["pieces"].values():
            all_tempo_values.extend(piece_entry.get("tempoValues", []))
            dyn_vs_piece_stats.append(piece_entry.get("dynamicsResidualVsPiece", EMPTY_SUM_STATS))
            dyn_vs_perf_stats.append(piece_entry.get("dynamicsResidualVsPerformance", EMPTY_SUM_STATS))
            timbre_vs_piece_stats.append(piece_entry.get("timbreResidualVsPiece", EMPTY_SUM_STATS))
            timbre_vs_perf_stats.append(piece_entry.get("timbreResidualVsPerformance", EMPTY_SUM_STATS))

    log_tempo_values = [math.log(v) for v in all_tempo_values if v > 0]
    corpus_tempo_log_median = _median(log_tempo_values)
    corpus_tempo_log_std = (
        _population_std([v - corpus_tempo_log_median for v in log_tempo_values])
        if corpus_tempo_log_median is not None else None
    )

    stats["corpus"] = {
        "tempo": {
            "logMedian": corpus_tempo_log_median,
            "logStd": corpus_tempo_log_std,
        },
        "dynamics": {
            "stdVsPiece": _std_from_sum_stats(dyn_vs_piece_stats),
            "stdVsPerformance": _std_from_sum_stats(dyn_vs_perf_stats),
        },
        "timbre": {
            "stdVsPiece": _std_from_sum_stats(timbre_vs_piece_stats),
            "stdVsPerformance": _std_from_sum_stats(timbre_vs_perf_stats),
        },
    }

    save_stats(stats)

    return {
        "totalPieces": total_pieces,
        "recomputedPieces": len(recomputed),
        "recomputedPerformances": sorted(touched_performances),
        "details": recomputed,
        "skippedPieces": len(skipped),
        "skippedDetails": skipped,
    }


def get_stats_summary() -> dict:
    stats = load_stats()
    result = {}
    for performance_name, perf_entry in stats.get("performances", {}).items():
        result[performance_name] = {
            "overall": {
                "dynamicsMedian": perf_entry.get("overall", {}).get("dynamicsMedian"),
                "timbreMedian": perf_entry.get("overall", {}).get("timbreMedian"),
            },
            "pieces": {
                piece_num: {
                    "dynamicsMedian": piece.get("dynamicsMedian"),
                    "timbreMedian": piece.get("timbreMedian"),
                }
                for piece_num, piece in perf_entry.get("pieces", {}).items()
            },
        }
    return result


def get_corpus_stats() -> dict:
    return load_stats().get("corpus", {})


def get_normalization_reference(performance: str, piece: Optional[str], scope: str) -> dict:
    """
    Medians/std needed to normalize one performance's beat data for the
    given DTW scope. Centering reference for dynamics/timbre is per-piece
    for piece/measures scope, per-performance-overall for cycle/halfCycle
    scope; tempo always centers on the one corpus-wide value.
    """
    stats = load_stats()
    perf_entry = stats.get("performances", {}).get(performance, {})
    corpus = stats.get("corpus", {})

    if scope in ("piece", "measures"):
        piece_entry = perf_entry.get("pieces", {}).get(str(piece), {})
        dynamics_median = piece_entry.get("dynamicsMedianSigned")
        timbre_median = piece_entry.get("timbreMedian")
        dynamics_std = corpus.get("dynamics", {}).get("stdVsPiece")
        timbre_std = corpus.get("timbre", {}).get("stdVsPiece")
    else:  # cycle / halfCycle
        overall = perf_entry.get("overall", {})
        dynamics_median = overall.get("dynamicsMedianSigned")
        timbre_median = overall.get("timbreMedian")
        dynamics_std = corpus.get("dynamics", {}).get("stdVsPerformance")
        timbre_std = corpus.get("timbre", {}).get("stdVsPerformance")

    return {
        "dynamics": {"median": dynamics_median, "std": dynamics_std},
        "timbre": {
            "logMedian": math.log(timbre_median) if timbre_median else None,
            "std": timbre_std,
        },
        "tempo": {
            "logMedian": corpus.get("tempo", {}).get("logMedian"),
            "std": corpus.get("tempo", {}).get("logStd"),
        },
    }
