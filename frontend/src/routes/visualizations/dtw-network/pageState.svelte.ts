import type { SongInfo, CyclePerformance } from "$lib/types";
import type { DtwScope, DtwMetric } from "$lib/api";

export const dtwNetworkPageState = $state({
	linkWidth: 200,
	nodeSize: 10,
	analysisScope: "" as DtwScope | "",
	ersteAbtheilung: true,
	allPerformances: [] as CyclePerformance[],
	selectedPerformances: [] as CyclePerformance[],
	pieces: [] as SongInfo[],
	selectedPiece: null as SongInfo | null,
	selectedParameters: ["tempo"] as string[],
	selectedMetric: "euclidean" as DtwMetric,
	/**
	 * Relative weights per parameter, keyed by name so the mapping does not
	 * depend on selection order. Normalized to sum to one before sending;
	 * only meaningful with several parameters and the euclidean metric.
	 */
	parameterWeights: { tempo: 1, dynamics: 1, timbre: 1 } as Record<string, number>,
	measureStart: 1,
	measureStartBeat: 1,
	measureEnd: 1,
	measureEndBeat: 1,
	nodes: [] as { id: number; label?: string }[],
	links: [] as { source: number; target: number; distance: number }[],
	/**
	 * Pairs the backend refused to compare, with the reason. Kept in page
	 * state rather than shown transiently: a missing edge is easy to overlook,
	 * and the reason usually points at a defect in the data worth following up.
	 */
	warnings: [] as { pair: string[]; reasons: string[] }[]
});
