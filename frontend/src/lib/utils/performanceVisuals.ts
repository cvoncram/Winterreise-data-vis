import * as d3 from "d3";
import type { NormalizationReference, PerformanceRow } from "$lib/types";

export function applyColorScheme(scheme: string, value: number): string {
    if (scheme === "viridisScheme") return d3.interpolateViridis(value);
    if (scheme === "infernoScheme") return d3.interpolateInferno(value);
    if (scheme === "cividisScheme") return d3.interpolateCividis(value);
    if (scheme === "greensScheme") return d3.interpolateGreens(1 - value);
    if (scheme === "bluesScheme") return d3.interpolateBlues(1 - value);
    if (scheme === "redsScheme") return d3.interpolateReds(1 - value);
    return "";
}

/**
 * Total sounding duration of a beat sequence, in seconds.
 */
export function totalDuration(rows: PerformanceRow[]): number {
    return rows.reduce((sum, r) => sum + (r.tempo ? 60 / r.tempo : 0), 0);
}

/** Clamp a z-score to +/-`clamp` scale units, rescaled to [0,1]. */
export function zScoreToUnit(z: number, clamp = 2): number {
    const clamped = Math.max(-clamp, Math.min(clamp, z));
    return (clamped + clamp) / (2 * clamp);
}

/** Per-beat dynamics as [0,1]: deviation from the reference centre in scale units, clamped. */
export function computeDynamicsUnit(rows: PerformanceRow[], reference: NormalizationReference | null): number[] {
    const center = reference?.dynamics?.center;
    const scale = reference?.dynamics?.scale;
    if (center == null || !scale) return rows.map(() => 0.5);

    return rows.map(r => {
        if (r.dynamics == null) return 0.5;
        return zScoreToUnit((r.dynamics - center) / scale);
    });
}

/** Per-beat timbre as [0,1], from the log spectral centroid. */
export function computeTimbreUnit(rows: PerformanceRow[], reference: NormalizationReference | null): number[] {
    const logCenter = reference?.timbre?.logCenter;
    const scale = reference?.timbre?.scale;
    if (logCenter == null || !scale) return rows.map(() => 0.5);

    return rows.map(r => {
        if (r.timbre == null || r.timbre <= 0) return 0.5;
        return zScoreToUnit((Math.log(r.timbre) - logCenter) / scale);
    });
}
