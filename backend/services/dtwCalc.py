from dtaidistance import dtw
import numpy as np
from typing import Literal

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
            seq = convert_dynamics([r["dynamics"] for r in rows], perf["metadata"])
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
        else:
            import re
            m = re.match(r"^([a-z]+)([+-]\d+)?$", d, re.IGNORECASE)
            base = map.get(m.group(1), 0.0) if m else 0.0
            off = float(m.group(2)) if m and m.group(2) else 0.0
            result.append(abs(base + off))
    return result