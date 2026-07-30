import math
import re
from dtaidistance import dtw
import numpy as np
from typing import Literal, Optional

def calculate_dtw_matrix(
    parameter: Literal["tempo", "dynamics", "timbre"],
    piece: int,
    performances: list
) -> dict:
    
    sequences = []
    for perf in performances:
        rows = perf["data"]
        if parameter == "tempo":
            seq = [r["tempo"] for r in rows if r["tempo"] is not None]
        elif parameter == "timbre":
            seq = [r["timbre"] for r in rows if r["timbre"] is not None]
        elif parameter == "dynamics":
            seq = [r["dynamics"] for r in rows if r["dynamics"] is not None]
        sequences.append(np.array(seq, dtype=np.float64))
    
    matrix = dtw.distance_matrix_fast(sequences)
    
    n = len(sequences)
    result = []
    for i in range(n):
        row = []
        for j in range(n):
            if i == j:
                row.append(0.0)
            elif j > i:
                row.append(float(matrix[i][j]))
            else:
                row.append(float(matrix[j][i]))
        result.append(row)
    
    return {
        "parameter": parameter,
        "piece": piece,
        "n": n,
        "matrix": result
    }


def convert_dynamics(dynamics: list[str], metadata: dict) -> list[float]:
    mf_val = metadata["mfValue"]
    dyn_step = metadata["dynamicStep"]
    map = {
        "ppp": mf_val - (4 * dyn_step), "pp": mf_val - (3 * dyn_step),
        "p": mf_val - (2 * dyn_step), "mp": mf_val - dyn_step,
        "mf": mf_val, "f": mf_val + dyn_step,
        "ff": mf_val + (2 * dyn_step), "fff": mf_val + (3 * dyn_step)
    }
    result = []
    for d in dynamics:
        if d == "extreme":
            result.append(0.0)
            continue

        if re.match(r"^-?\d+(\.\d+)?$", d.strip()):
            result.append(abs(float(d)))
            continue

        m = re.match(r"^([a-z]+)([+-]\d+)?$", d, re.IGNORECASE)
        base = map.get(m.group(1), 0.0) if m else 0.0
        off = float(m.group(2)) if m and m.group(2) else 0.0
        result.append(abs(base + off))
    return result


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
        std = reference.get("std")
        transformed = [float(v) for v in values]
    else:
        median = reference.get("logMedian")
        std = reference.get("std")
        transformed = [math.log(float(v)) for v in values if float(v) > 0]

    if median is None or not std:
        return np.array(transformed, dtype=np.float64)

    return np.array([(v - median) / std for v in transformed], dtype=np.float64)


def _pairwise_cost_matrix(
    a: np.ndarray, b: np.ndarray, metric: Literal["euclidean", "mahalanobis"], VI: Optional[np.ndarray]
) -> np.ndarray:
    diff = a[:, None, :] - b[None, :, :]  # (n, m, d)
    if metric == "mahalanobis" and VI is not None:
        left = np.einsum("nmd,de->nme", diff, VI)
        return np.sqrt(np.einsum("nme,nme->nm", left, diff))
    return np.sqrt(np.einsum("nmd,nmd->nm", diff, diff))


def _dtw_from_cost_matrix(cost: np.ndarray) -> float:
    n, m = cost.shape
    if n == 0 or m == 0:
        return float("inf")
    D = np.full((n + 1, m + 1), np.inf)
    D[0, 0] = 0.0
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            D[i, j] = cost[i - 1, j - 1] + min(D[i - 1, j], D[i, j - 1], D[i - 1, j - 1])
    return float(D[n, m])


def combined_dtw_matrix(
    sequences: list,  # list of (T_i, D) arrays, one per performance
    metric: Literal["euclidean", "mahalanobis"] = "euclidean",
    weights: Optional[list] = None,
) -> dict:
    n_dims = sequences[0].shape[1] if sequences and sequences[0].ndim == 2 else 1
    if weights is None:
        weights = [1.0 / n_dims] * n_dims

    scale = np.sqrt(np.array(weights, dtype=np.float64))
    weighted_sequences = [seq * scale for seq in sequences]

    VI = None
    if metric == "mahalanobis":
        pooled = np.concatenate(weighted_sequences, axis=0)
        cov = np.atleast_2d(np.cov(pooled, rowvar=False))
        cov += np.eye(cov.shape[0]) * 1e-8  # regularize against singular covariance
        VI = np.linalg.inv(cov)

    n = len(weighted_sequences)
    matrix = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            cost = _pairwise_cost_matrix(weighted_sequences[i], weighted_sequences[j], metric, VI)
            d = _dtw_from_cost_matrix(cost)
            matrix[i][j] = d
            matrix[j][i] = d

    return {"n": n, "matrix": matrix}