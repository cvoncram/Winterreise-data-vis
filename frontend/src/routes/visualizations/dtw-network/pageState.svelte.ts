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
	measureStart: 1,
	measureStartBeat: 1,
	measureEnd: 1,
	measureEndBeat: 1,
	nodes: [] as { id: number; label?: string }[],
	links: [] as { source: number; target: number; distance: number }[]
});
