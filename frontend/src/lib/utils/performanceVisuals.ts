import * as d3 from "d3";
import type { PerformanceRow, PerformanceMetadata } from "$lib/types";

export function applyColorScheme(scheme: string, value: number): string {
    if (scheme === "viridisScheme") return d3.interpolateViridis(value);
    if (scheme === "infernoScheme") return d3.interpolateInferno(value);
    if (scheme === "cividisScheme") return d3.interpolateCividis(value);
    if (scheme === "greensScheme") return d3.interpolateGreens(1 - value);
    if (scheme === "bluesScheme") return d3.interpolateBlues(1 - value);
    if (scheme === "redsScheme") return d3.interpolateReds(1 - value);
    return "";
}

export function computeDynamics(data: PerformanceRow[], metadata: PerformanceMetadata | null): number[] {
    if (!metadata) return [];
    const f = 12 / metadata.dynamicStep;
    const map: Record<string, number> = { ppp: 12, pp: 24, p: 36, mp: 48, mf: 60, f: 72, ff: 84, fff: 96 };

    return data.map(r => {
        const numeric = parseFloat(r.dynamics);
        if (!isNaN(numeric) && /^-?\d+(\.\d+)?$/.test(r.dynamics.trim())) {
            return 0.3 + (((Math.abs(numeric) - Math.abs(metadata.mfValue)) / (-metadata.dynamicStep)) * 0.06);
        }
        const m = r.dynamics.match(/^([a-z]+)([+-]\d+)?$/i);
        const base = map[m?.[1] ?? ""] ?? 0;
        const off = m?.[2] ? Number(m[2]) : 0;
        return (base + off * f) / 200;
    });
}
