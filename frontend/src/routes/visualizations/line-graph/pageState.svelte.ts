import type { SongInfo, CyclePerformance, Parameter, PerformanceRow } from "$lib/types";

export const lineGraphPageState = $state({
	allPerformances: [] as CyclePerformance[],
	selectedPerformances: [] as CyclePerformance[],
	pieces: [] as SongInfo[],
	selectedPiece: null as SongInfo | null,
	selectedParameter: "tempo" as Parameter,
	graphPerformances: [] as PerformanceRow[][],
	labels: [] as string[],
	showGraph: false,
	active: "graph"
});
