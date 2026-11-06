"""
Distance and rank correlation between performances, aligned with DTW.
"""

import math
from typing import Literal, Optional

import numpy as np
from dtw import dtw, stepPattern
from scipy.ndimage import uniform_filter1d
from scipy.spatial.distance import cdist
from scipy.stats import kendalltau

# Step pattern of the alignment.
STEP_PATTERN = stepPattern.symmetric1

# Largest beat-count difference per piece before a comparison is refused.
MAX_LENGTH_DIFF = 3

# Sakoe-Chiba band width beyond the length difference.
BAND_TOLERANCE = 2

# Ridge added to the covariance diagonal.
_COV_RIDGE = 1e-8


def normalize_series(values: list, kind: Literal["tempo", "dynamics", "timbre"], reference: dict) -> np.ndarray:
    """
    Centred and scaled beat values; tempo and timbre are log-transformed first.
    `reference` is one entry of statsCalc.get_normalization_reference().
    """
    if kind == "dynamics":
        center = reference.get("center")
        scale = reference.get("scale")
        transformed = list(values)
    else:
        center = reference.get("logCenter")
        scale = reference.get("scale")
        transformed = [math.log(v) for v in values if v > 0]

    if center is None or not scale:
        return np.array(transformed, dtype=np.float64)

    return np.array([(v - center) / scale for v in transformed], dtype=np.float64)


def _cdist_weights(weights: Optional[list], n_dims: int) -> Optional[np.ndarray]:
    """Parameter weights rescaled to sum to the number of dimensions."""
    if weights is None:
        return None
    total = float(sum(weights))
    if total <= 0:
        return None
    return np.array(weights, dtype=np.float64) * (n_dims / total)


def _inverse_covariance(by_piece: list, corpus: Optional[list] = None) -> Optional[np.ndarray]:
    """Inverse covariance for the Mahalanobis metric: corpus-wide if given, else from the selection."""
    if corpus is not None:
        cov = np.atleast_2d(np.array(corpus, dtype=np.float64))
    else:
        parts = [seq for pieces in by_piece for seq in pieces.values() if len(seq)]
        if not parts:
            return None
        pooled = np.concatenate(parts, axis=0)
        cov = np.atleast_2d(np.cov(pooled, rowvar=False))

    cov = cov + np.eye(cov.shape[0]) * _COV_RIDGE
    return np.linalg.inv(cov)


def _local_cost(a: np.ndarray, b: np.ndarray, metric: str, w, VI) -> np.ndarray:
    """Distances between every beat of one piece and every beat of the other."""
    if metric == "mahalanobis" and VI is not None:
        return cdist(a, b, metric="mahalanobis", VI=VI)
    return cdist(a, b, metric="minkowski", p=2, w=w)


def _piece_alignment(a: np.ndarray, b: np.ndarray, cost: np.ndarray) -> tuple[float, list, int]:
    """DTW distance of one piece, Kendall's tau-b per parameter along the path, and the path indices."""
    n, m = cost.shape
    window = abs(n - m) + BAND_TOLERANCE
    alignment = dtw(
        cost,
        step_pattern=STEP_PATTERN,
        window_type="sakoechiba",
        window_args={"window_size": window},
    )
    ia, ib = alignment.index1, alignment.index2
    taus = [float(kendalltau(a[ia, d], b[ib, d]).statistic) for d in range(a.shape[1])]
    return float(alignment.distance), taus, ia, ib


# Rotations (fractions of the piece length) used for the tau floor.
FLOOR_SHIFTS = (0.12, 0.25, 1 / 3, 0.5)


def _piece_floor(a: np.ndarray, b: np.ndarray, metric: str, w, VI) -> list:
    """Highest tau per parameter over the rotations of one series."""
    per_shift = []
    for fraction in FLOOR_SHIFTS:
        shifted = np.roll(b, max(1, int(len(b) * fraction)), axis=0)
        _, taus, _, _ = _piece_alignment(a, shifted, _local_cost(a, shifted, metric, w, VI))
        per_shift.append(taus)
    return [float(x) for x in np.nanmax(np.array(per_shift, dtype=np.float64), axis=0)]


def combined_dtw_matrix(
    sequences_by_piece: list,  # per performance: {piece number: (T, d) array}
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[list] = None,
    covariance: Optional[list] = None,
) -> dict:
    """
    Pairwise distance and tau matrices, each piece aligned separately and summed.
    Incomparable pairs are null and listed in `warnings`.
    """
    for update in combined_dtw_matrix_iter(sequences_by_piece, metric, weights, covariance):
        if "result" in update:
            return update["result"]
    return {}


def combined_dtw_matrix_iter(
    sequences_by_piece: list,
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[list] = None,
    covariance: Optional[list] = None,
):
    """combined_dtw_matrix as progress updates; the last item carries the result."""
    n = len(sequences_by_piece)
    n_dims = 1
    for pieces in sequences_by_piece:
        for seq in pieces.values():
            if seq.ndim == 2:
                n_dims = seq.shape[1]
                break

    w = _cdist_weights(weights, n_dims)
    VI = _inverse_covariance(sequences_by_piece, covariance) if metric == "mahalanobis" else None
    tau_weights = w if w is not None else np.ones(n_dims)

    matrix: list = [[0.0] * n for _ in range(n)]
    normalized: list = [[0.0] * n for _ in range(n)]
    correlation: list = [[1.0] * n for _ in range(n)]
    warnings: list = []

    total_pairs = n * (n - 1) // 2
    compared = 0

    for i in range(n):
        for j in range(i + 1, n):
            a_pieces, b_pieces = sequences_by_piece[i], sequences_by_piece[j]

            reasons = []
            only_a = sorted(set(a_pieces) - set(b_pieces))
            only_b = sorted(set(b_pieces) - set(a_pieces))
            if only_a or only_b:
                reasons.append(
                    "pieces missing from one recording: "
                    + ", ".join(str(p) for p in sorted(only_a + only_b))
                )

            shared = sorted(set(a_pieces) & set(b_pieces))
            for p in shared:
                diff = abs(len(a_pieces[p]) - len(b_pieces[p]))
                if not len(a_pieces[p]) or not len(b_pieces[p]):
                    reasons.append(f"piece {p}: no usable beats")
                elif diff > MAX_LENGTH_DIFF:
                    reasons.append(
                        f"piece {p}: beat counts differ by {diff} "
                        f"({len(a_pieces[p])} vs {len(b_pieces[p])}), "
                        f"tolerance is {MAX_LENGTH_DIFF}"
                    )
            if not shared:
                reasons.append("no pieces in common")

            if reasons:
                # Refused pair.
                matrix[i][j] = matrix[j][i] = None
                normalized[i][j] = normalized[j][i] = None
                correlation[i][j] = correlation[j][i] = None
                warnings.append({"i": i, "j": j, "reasons": reasons})
                compared += 1
                yield {"stage": "comparing", "done": compared, "total": total_pairs}
                continue

            total = 0.0
            beats = 0
            # Per parameter: sum of tau times pairs, and the pairs.
            tau_sums = np.zeros(n_dims)
            tau_pairs = np.zeros(n_dims)
            for p in shared:
                cost = _local_cost(a_pieces[p], b_pieces[p], metric, w, VI)
                distance, taus, ia, _ = _piece_alignment(a_pieces[p], b_pieces[p], cost)
                pairs = len(ia)
                total += distance
                beats += max(len(a_pieces[p]), len(b_pieces[p]))
                for d, tau in enumerate(taus):
                    # NaN where a parameter does not vary within the piece.
                    if math.isfinite(tau):
                        tau_sums[d] += tau * pairs
                        tau_pairs[d] += pairs

            valid = tau_pairs > 0
            correlation[i][j] = correlation[j][i] = (
                float(np.sum(tau_weights[valid] * tau_sums[valid] / tau_pairs[valid]) / np.sum(tau_weights[valid]))
                if np.sum(tau_weights[valid]) > 0
                else None
            )

            matrix[i][j] = matrix[j][i] = total
            # Distance per beat.
            normalized[i][j] = normalized[j][i] = total / beats if beats else None

            compared += 1
            yield {"stage": "comparing", "done": compared, "total": total_pairs}

    yield {
        "result": {
            "n": n,
            "matrix": matrix,
            "normalizedMatrix": normalized,
            "correlationMatrix": correlation,
            "warnings": warnings,
        }
    }


# Number of beats a difference is averaged over.
DIFFERENCE_WINDOW = 8

# Maximum number of reported differences per parameter.
DIFFERENCES_PER_PARAMETER = 10


def _largest_differences(
    a, b, ia, ib, parameters: list, measures: Optional[list], piece: int,
    raw_first: Optional[dict] = None, raw_second: Optional[dict] = None,
) -> list:
    """
    Non-overlapping stretches with the largest smoothed difference per parameter,
    in scale units, with the mean raw values of both recordings.
    """
    if len(ia) < DIFFERENCE_WINDOW:
        return []

    found = []
    for d, parameter in enumerate(parameters):
        smoothed = uniform_filter1d(a[ia, d] - b[ib, d], DIFFERENCE_WINDOW, mode="nearest")
        chosen: list = []
        for k in np.argsort(-np.abs(smoothed)):
            if any(abs(int(k) - c) < DIFFERENCE_WINDOW for c in chosen):
                continue
            chosen.append(int(k))
            low = max(0, int(k) - DIFFERENCE_WINDOW // 2)
            high = min(len(ia) - 1, int(k) + DIFFERENCE_WINDOW // 2)
            def _mean_raw(raw, index):
                """Mean of the untransformed measurements over the stretch."""
                if not raw or parameter not in raw:
                    return None
                values = np.asarray(raw[parameter], dtype=np.float64)[index[low:high + 1]]
                return float(np.mean(values)) if len(values) else None

            found.append({
                "piece": piece,
                "parameter": parameter,
                # Positive: the first recording is higher.
                "value": float(smoothed[k]),
                "from": measures[ia[low]] if measures else None,
                "to": measures[ia[high]] if measures else None,
                "first": _mean_raw(raw_first, ia),
                "second": _mean_raw(raw_second, ib),
            })
            if len(chosen) >= DIFFERENCES_PER_PARAMETER:
                break
    return found


def _top_differences(found: list, parameters: list) -> list:
    """The strongest stretches, ranked separately per parameter."""
    out = []
    for parameter in parameters:
        rows = [r for r in found if r["parameter"] == parameter]
        out.extend(sorted(rows, key=lambda r: -abs(r["value"]))[:DIFFERENCES_PER_PARAMETER])
    return out


def pair_analysis(
    a_by_piece: dict,
    b_by_piece: dict,
    parameters: list,
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[list] = None,
    measures_by_piece: Optional[dict] = None,
    raw_by_piece: Optional[list] = None,
    covariance: Optional[list] = None,
) -> dict:
    """
    Per-piece breakdown of one pair: distance, tau, tau floor and
    largest differences, plus totals.
    """
    n_dims = len(parameters)
    w = _cdist_weights(weights, n_dims)
    VI = _inverse_covariance([a_by_piece, b_by_piece], covariance) if metric == "mahalanobis" else None
    tau_weights = np.asarray(w if w is not None else np.ones(n_dims), dtype=np.float64)

    def _by_parameter(values: list) -> dict:
        """Per-parameter figures plus their weighted combination, nulls where absent."""
        v = np.array(values, dtype=np.float64)
        ok = np.isfinite(v)
        combined = (
            float(np.sum(tau_weights[ok] * v[ok]) / np.sum(tau_weights[ok]))
            if ok.any() and np.sum(tau_weights[ok]) > 0
            else None
        )
        out = {"combined": combined}
        out.update({k: (float(x) if math.isfinite(x) else None) for k, x in zip(parameters, values)})
        return out

    rows = []
    differences: list = []
    for p in sorted(set(a_by_piece) & set(b_by_piece)):
        a, b = a_by_piece[p], b_by_piece[p]
        if not len(a) or not len(b):
            rows.append({"piece": p, "usable": False, "reason": "no usable beats"})
            continue
        if abs(len(a) - len(b)) > MAX_LENGTH_DIFF:
            rows.append({
                "piece": p,
                "usable": False,
                "reason": f"beat counts differ by {abs(len(a) - len(b))} ({len(a)} vs {len(b)})",
            })
            continue

        distance, taus, ia, ib = _piece_alignment(a, b, _local_cost(a, b, metric, w, VI))
        pairs = len(ia)
        differences.extend(
            _largest_differences(
                a, b, ia, ib, parameters, (measures_by_piece or {}).get(p), p,
                raw_first=(raw_by_piece[0] or {}).get(p) if raw_by_piece else None,
                raw_second=(raw_by_piece[1] or {}).get(p) if raw_by_piece else None,
            )
        )
        rows.append({
            "piece": p,
            "usable": True,
            "reason": None,
            "beats": [int(len(a)), int(len(b))],
            "pairs": int(pairs),
            "distance": distance,
            "normalizedDistance": distance / max(len(a), len(b)),
            "tau": _by_parameter(taus),
            "floor": _by_parameter(_piece_floor(a, b, metric, w, VI)),
        })

    usable = [r for r in rows if r["usable"]]
    beats = sum(max(r["beats"]) for r in usable)
    distance = sum(r["distance"] for r in usable)

    def _weighted(key: str) -> Optional[float]:
        """Mean over pieces, weighted by beat pairs."""
        parts = [(r[key]["combined"], r["pairs"]) for r in usable if r[key]["combined"] is not None]
        if not parts:
            return None
        return float(sum(v * n for v, n in parts) / sum(n for _, n in parts))

    return {
        "pieces": rows,
        "differences": _top_differences(differences, parameters),
        "total": {
            "distance": distance,
            "normalizedDistance": distance / beats if beats else None,
            "tau": _weighted("tau"),
            "floor": _weighted("floor"),
            "beats": beats,
            "piecesCompared": len(usable),
        },
        "onlyFirst": sorted(set(a_by_piece) - set(b_by_piece)),
        "onlySecond": sorted(set(b_by_piece) - set(a_by_piece)),
    }
