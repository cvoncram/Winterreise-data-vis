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

/** Clamp a z-score to +/-`clamp` scale units, rescaled to [0,1]. */
export function zScoreToUnit(z: number, clamp = 2): number {
    const clamped = Math.max(-clamp, Math.min(clamp, z));
    return (clamped + clamp) / (2 * clamp);
}

/**
 * Per-beat dynamics expressed as a [0,1] unit value: how far this beat's raw
 * dB value sits from the reference recording/piece's own median, divided by
 * the corpus-wide scale figure and clamped.
 */
export function computeDynamicsUnit(rows: PerformanceRow[], reference: NormalizationReference | null): number[] {
    const median = reference?.dynamics?.median;
    const scale = reference?.dynamics?.scale;
    if (median == null || !scale) return rows.map(() => 0.5);

    return rows.map(r => {
        const raw = parseFloat(r.dynamics);
        if (isNaN(raw)) return 0.5;
        return zScoreToUnit((raw - median) / scale);
    });
}

/**
 * Per-beat timbre expressed as a [0,1] unit value, same idea as
 * computeDynamicsUnit but on log-transformed spectral centroid.
 */
export function computeTimbreUnit(rows: PerformanceRow[], reference: NormalizationReference | null): number[] {
    const logMedian = reference?.timbre?.logMedian;
    const scale = reference?.timbre?.scale;
    if (logMedian == null || !scale) return rows.map(() => 0.5);

    return rows.map(r => {
        if (r.timbre == null || r.timbre <= 0) return 0.5;
        return zScoreToUnit((Math.log(r.timbre) - logMedian) / scale);
    });
}
