import type { SongInfo, CyclePerformance } from "$lib/types";
import type { DtwScope, DtwMetric } from "$lib/api";

export const dtwNetworkPageState = $state({
	linkWidth: 10,
	nodeSize: 10,
	analysisScope: "" as DtwScope | "",
	ersteAbtheilung: true,
	allPerformances: [] as CyclePerformance[],
	selectedPerformances: [] as CyclePerformance[],
	pieces: [] as SongInfo[],
	selectedPiece: null as SongInfo | null,
	selectedParameters: ["tempo"] as string[],
	selectedMetric: "euclidean" as DtwMetric,
	parameterWeights: { tempo: 1, dynamics: 1, timbre: 1 } as Record<string, number>,
	measureStart: 1,
	measureStartBeat: 1,
	measureEnd: 1,
	measureEndBeat: 1,
	/** Which of the two views of the same result is on screen. */
	active: "network" as "network" | "matrix",
	nodes: [] as { id: number; label?: string }[],
	links: [] as { source: number; target: number; distance: number }[],
	/**
	 * The distance matrix as the backend returned it, kept beside the links
	 * because those carry only the pairs that could be compared — the matrix
	 * keeps the nulls, and the triangle has to show them as gaps.
	 */
	matrix: [] as (number | null)[][],
	matrixLabels: [] as string[],
	warnings: [] as { pair: string[]; reasons: string[] }[]
});
