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
from scipy.spatial.distance import cdist

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
BAND_TOLERANCE = 3

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
        median = reference.get("median")
        scale = reference.get("scale")
        transformed = list(values)
    else:
        median = reference.get("logMedian")
        scale = reference.get("scale")
        transformed = [math.log(v) for v in values if v > 0]

    if median is None or not scale:
        return np.array(transformed, dtype=np.float64)

    return np.array([(v - median) / scale for v in transformed], dtype=np.float64)


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


def _inverse_covariance(by_piece: list) -> Optional[np.ndarray]:
    """
    Inverse covariance for the Mahalanobis metric, estimated from all
    selected performances and pieces pooled.

    Estimated from the unweighted data, since weighting provably cancels out
    under this metric: whitening normalizes every direction to unit variance
    anyway, so a preceding axis-wise scaling can have no effect.
    """
    parts = [seq for pieces in by_piece for seq in pieces.values() if len(seq)]
    if not parts:
        return None
    pooled = np.concatenate(parts, axis=0)
    cov = np.atleast_2d(np.cov(pooled, rowvar=False))
    cov = cov + np.eye(cov.shape[0]) * _COV_RIDGE
    return np.linalg.inv(cov)


def _piece_distance(a: np.ndarray, b: np.ndarray, metric: str, w, VI) -> float:
    """DTW distance for one piece, with the path confined to a narrow band."""
    if metric == "mahalanobis" and VI is not None:
        cost = cdist(a, b, metric="mahalanobis", VI=VI)
    else:
        cost = cdist(a, b, metric="minkowski", p=2, w=w)

    window = abs(len(a) - len(b)) + BAND_TOLERANCE
    alignment = dtw(
        cost,
        step_pattern=STEP_PATTERN,
        distance_only=True,
        window_type="sakoechiba",
        window_args={"window_size": window},
    )
    return float(alignment.distance)


def combined_dtw_matrix(
    sequences_by_piece: list,  # per performance: {piece number: (T, d) array}
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[list] = None,
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
    """
    n = len(sequences_by_piece)
    n_dims = 1
    for pieces in sequences_by_piece:
        for seq in pieces.values():
            if seq.ndim == 2:
                n_dims = seq.shape[1]
                break

    w = _cdist_weights(weights, n_dims)
    VI = _inverse_covariance(sequences_by_piece) if metric == "mahalanobis" else None

    matrix: list = [[0.0] * n for _ in range(n)]
    normalized: list = [[0.0] * n for _ in range(n)]
    warnings: list = []

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
                warnings.append({"i": i, "j": j, "reasons": reasons})
                continue

            total = 0.0
            beats = 0
            for p in shared:
                total += _piece_distance(a_pieces[p], b_pieces[p], metric, w, VI)
                beats += max(len(a_pieces[p]), len(b_pieces[p]))

            matrix[i][j] = matrix[j][i] = total
            # Per beat compared. The alignment stays within a few beats of the
            # diagonal, so the number of summed terms is essentially the beat
            # count; dividing by it gives a figure that stays comparable
            # between pieces and scopes, which the raw sum does not.
            normalized[i][j] = normalized[j][i] = total / beats if beats else None

    return {"n": n, "matrix": matrix, "normalizedMatrix": normalized, "warnings": warnings}
