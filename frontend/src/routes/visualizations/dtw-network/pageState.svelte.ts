import type { SongInfo, CyclePerformance } from "$lib/types";
import type { DtwScope, DtwMetric, DtwAnalysisParams } from "$lib/api";

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
	/** Metadata the nodes are coloured by. */
	colourBy: "none" as "none" | "year" | "pianist" | "context",
	showLabels: false,
	/** Which of the two views of the same result is on screen. */
	active: "network" as "network" | "matrix",
	nodes: [] as { id: number; label?: string; lines?: string[] }[],
	links: [] as { source: number; target: number; distance: number; cost: number; tau: number | null }[],
	/** Normalized distance matrix including refused pairs (null). */
	matrix: [] as (number | null)[][],
	/** Kendall's tau per pair including refused pairs (null). */
	tauMatrix: [] as (number | null)[][],
	matrixLabels: [] as string[],
	warnings: [] as { pair: string[]; reasons: string[] }[],
	/** Settings and recordings of the displayed result. */
	generated: null as { params: DtwAnalysisParams; performances: CyclePerformance[] } | null
});
