"""
Distance computation between performances.

Both halves of the calculation come from established libraries rather than
from this file: scipy builds the matrix of local distances between every pair
of beats, dtw-python accumulates it into the optimal alignment. What remains
here is the normalization of the raw measurements, the assembly of the
pairwise distance matrix, and the guards described below.

Two constraints shape this module, and both follow from what the alignment is
for here. The recordings are of the same score, so beat i of one corresponds
to beat i of the other; the alignment exists only to absorb the last few
measurement errors that survive manual checking, not to discover a
correspondence. Anything beyond a few beats of drift is a defect in the data,
and the calculation is meant to surface it rather than to paper over it.
"""

import math
from typing import Literal, Optional

import numpy as np
from dtw import dtw, stepPattern
from scipy.ndimage import uniform_filter1d
from scipy.spatial.distance import cdist
from scipy.stats import kendalltau

# symmetric1 charges every step once, which — because a detour can never cost
# less than the diagonal it replaces — leaves the alignment close to the
# diagonal unless the data force it away. That is the wanted behaviour here:
# the comparison is positional by design, and warping is the exception.
#
# symmetric2, which weights the diagonal twice, was measured against it. It
# stretches freely and reached distances 13.8% lower by wandering up to 64
# beats off the diagonal between two recordings of a 273-beat song — an
# alignment with no musical meaning. Its advantage is that the total step
# weight is always N+M, so the distance normalizes cleanly; that is recovered
# here by dividing by the beat count instead.
STEP_PATTERN = stepPattern.symmetric1

# How far a piece's beat counts may differ between two recordings before the
# comparison is refused. Careful manual checking keeps real differences at
# zero to two beats; anything larger means a missing or mistapped passage,
# and a distance computed across it would be meaningless.
MAX_LENGTH_DIFF = 3

# How far the alignment may leave the diagonal, over and above whatever the
# length difference already forces. Keeps a local mismatch from being
# "resolved" by a long excursion into an unrelated part of the piece.
#
# One band serves both figures: the rank correlation is measured along the
# same path the distance is summed from. Pairing the beats by any other rule
# would describe an alignment the distance does not use, and if the path is
# not trusted for the correlation there is little reason to trust it for the
# distance either. The freedom it grants — a beat may take the best partner
# within two, which absorbs an imprecisely placed marker — is therefore
# accepted for both, together with its cost: the correlation of two unrelated
# recordings does not sit at zero but around 0.1, occasionally near 0.3.
BAND_TOLERANCE = 2

# Guards the covariance against singularity, e.g. when two parameters are
# nearly collinear in the selected excerpt.
_COV_RIDGE = 1e-8


def normalize_series(values: list, kind: Literal["tempo", "dynamics", "timbre"], reference: dict) -> np.ndarray:
    """
    Center + scale raw beat values onto a comparable scale, per the
    normalization design: dynamics is already dB-like (no transform,
    signed), tempo/timbre are log-transformed first. `reference` is the
    per-parameter dict shape returned by
    statsCalc.get_normalization_reference()[kind].
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
    """
    Weights in the form scipy expects, rescaled to sum to the number of
    dimensions.

    scipy applies `w` to the *squared* difference, computing
    sqrt(sum w_k (a_k - b_k)^2), so the weights are passed through as given
    rather than square-rooted first — a distinction that is easy to get
    wrong, since pre-scaling the vectors themselves would require sqrt(w).

    The rescaling keeps the total weight constant at `n_dims`, which is what
    equal weights of one would give. Without it, moving a slider would change
    the overall magnitude of every distance as well as the emphasis between
    parameters, and it would be impossible to tell the two effects apart.
    """
    if weights is None:
        return None
    total = float(sum(weights))
    if total <= 0:
        return None
    return np.array(weights, dtype=np.float64) * (n_dims / total)


def _inverse_covariance(by_piece: list, corpus: Optional[list] = None) -> Optional[np.ndarray]:
    """
    Inverse covariance for the Mahalanobis metric.

    The corpus-wide figure is used when the statistics carry one, and the
    selection is fallen back on only when they do not. The difference is not
    cosmetic: estimated from a handful of selected recordings, the
    correlation between dynamics and timbre has been seen to range from -0.17
    to +0.60, which makes the metric mean something different with every
    selection and the distances incomparable between runs.

    Either way it is estimated from the unweighted data, since weighting
    provably cancels out under this metric: whitening normalizes every
    direction to unit variance anyway, so a preceding axis-wise scaling can
    have no effect.
    """
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
    """
    One piece aligned once: the DTW distance, and Kendall's tau-b per
    parameter along that same path.

    The beats are paired exactly as the path pairs them, repeated partners
    included. Tau depends on ranks only, so the normalization does not affect
    it — only which beats the path pairs.

    The path is returned alongside: its two index arrays say which beats were
    paired, and their difference how far the path sits from the diagonal —
    which is what a displaced marker looks like from here.
    """
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


# Fractions of a piece by which one series is rotated to see what tau a
# pairing of the same data yields when it means nothing. Several of them,
# because which rotation scores highest depends on the song: a strophic one
# peaks where a repeat lands on its original (Frühlingstraum reaches 0.78 at
# half its length, but -0.38 at a quarter), a through-composed one where the
# shift is small enough for the curve to still resemble itself.
FLOOR_SHIFTS = (0.12, 0.25, 1 / 3, 0.5)


def _piece_floor(a: np.ndarray, b: np.ndarray, metric: str, w, VI) -> list:
    """
    The tau this song produces without any real correspondence: the same two
    series, one of them rotated.

    This is not a constant of the method but a property of the music. Every
    tau has to be read against it, and taus of different songs cannot be
    compared without it.

    The highest of the rotations is reported, not their average: the question
    is what a meaningless pairing can reach, not what it reaches on average.
    """
    per_shift = []
    for fraction in FLOOR_SHIFTS:
        shifted = np.roll(b, max(1, int(len(b) * fraction)), axis=0)
        _, taus, _, _ = _piece_alignment(a, shifted, _local_cost(a, shifted, metric, w, VI))
        per_shift.append(taus)
    return [float(x) for x in np.nanmax(np.array(per_shift, dtype=np.float64), axis=0)]


def _longest_offset_run(offsets: np.ndarray) -> int:
    """Longest stretch of path steps that share one non-zero offset."""
    longest = run = 0
    for k in range(1, len(offsets)):
        run = run + 1 if offsets[k] == offsets[k - 1] and offsets[k] != 0 else 0
        longest = max(longest, run + 1 if run else 0)
    return int(longest)


def combined_dtw_matrix(
    sequences_by_piece: list,  # per performance: {piece number: (T, d) array}
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[list] = None,
    covariance: Optional[list] = None,
) -> dict:
    """
    Pairwise DTW distances over a set of normalized performance sequences.

    Each piece is aligned against its own counterpart and the results are
    summed, rather than concatenating the whole scope into one long sequence
    and aligning that. Concatenation would let the path cross the boundary
    between two songs — matching the close of one against the opening of the
    next — and would let a length difference early in the cycle displace
    everything after it. Aligning piece by piece enforces the correspondence
    that actually exists, and is cheaper besides, the cost of an alignment
    growing with the square of the sequence length.

    A pair whose pieces do not match up is reported as incomparable rather
    than given a number: `matrix` carries null in its place, and `warnings`
    says which recordings, which piece, and why.

    `correlationMatrix` holds Kendall's tau-b for the same pairs, measured
    along the very path the distance comes from and averaged across the
    parameters with the same weights as the distance. Across
    pieces it is the mean of each piece's tau weighted by its beat pairs, not
    the tau of all beats pooled: pooled beats would correlate by the tempo
    and loudness differences between the songs alone.
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
    """
    The same computation as combined_dtw_matrix, handed out pair by pair.

    A whole cycle takes long enough that a caller has to be able to say how
    far it has got; yielding after every pair is what lets it. The last item
    carries the finished result under "result".
    """
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
                # None rather than infinity: JSON has no representation for
                # infinity, and a very large number would quietly distort the
                # graph instead of being recognisable as an absent value.
                matrix[i][j] = matrix[j][i] = None
                normalized[i][j] = normalized[j][i] = None
                correlation[i][j] = correlation[j][i] = None
                warnings.append({"i": i, "j": j, "reasons": reasons})
                compared += 1
                yield {"stage": "comparing", "done": compared, "total": total_pairs}
                continue

            total = 0.0
            beats = 0
            # Per parameter: each piece's tau times its pairs, and the pairs.
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
            # Per beat compared. The alignment stays within a few beats of the
            # diagonal, so the number of summed terms is essentially the beat
            # count; dividing by it gives a figure that stays comparable
            # between pieces and scopes, which the raw sum does not.
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


# Over how many beats a difference has to hold before it is reported. A single
# beat says nothing — tempo jitters from beat to beat, and one mistapped
# marker produces a spike in both directions at once. Eight beats cover
# roughly two to three measures.
DIFFERENCE_WINDOW = 8

# At most this many places per parameter — enough for a table that can be
# scanned and exported, still far from a complete account of where two
# recordings differ.
DIFFERENCES_PER_PARAMETER = 10


def _largest_differences(
    a, b, ia, ib, parameters: list, measures: Optional[list], piece: int,
    raw_first: Optional[dict] = None, raw_second: Optional[dict] = None,
) -> list:
    """
    Where the two recordings pull apart the most, along the path that paired
    them, in units of the normalization's scale.

    Reported as stretches rather than beats, and never overlapping: a wide
    difference would otherwise fill the list with its own neighbouring beats.

    The mean raw measurement of each recording over the same stretch is
    carried along. Scale units say how unusual a difference is, and that is
    what makes the places comparable, but only beats per minute and decibels
    say what it sounds like.
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
                # Signed: positive means the first recording reads higher.
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
    """
    The strongest stretches, kept apart per parameter rather than ranked in
    one list. Three scale units of timbre do not mean what three units of
    tempo mean, and a single ranking would let whichever parameter varies
    most fill the whole list — in practice timbre, which is also the one most
    affected by the recording chain.
    """
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
    What the network's link stands for, taken apart piece by piece: the
    distance, tau along the same path, the floor that piece produces anyway,
    and how far the path had to leave the diagonal.

    The floor belongs beside every tau. Over a whole cycle it also explains
    why one summary figure is not enough: the cycle mixes songs whose floor
    is near zero with songs that reach 0.85 by repetition alone.
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
        pairs, offsets = len(ia), ib - ia
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
            # A marker that is missing rather than merely imprecise shows up
            # as a long stretch at one and the same offset.
            "path": {
                "offDiagonalShare": float(np.mean(offsets != 0)),
                "maxOffset": int(np.abs(offsets).max()),
                "longestRun": _longest_offset_run(offsets),
            },
        })

    usable = [r for r in rows if r["usable"]]
    beats = sum(max(r["beats"]) for r in usable)
    distance = sum(r["distance"] for r in usable)

    def _weighted(key: str) -> Optional[float]:
        """Across pieces: each piece's figure weighted by the pairs it rests on."""
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
