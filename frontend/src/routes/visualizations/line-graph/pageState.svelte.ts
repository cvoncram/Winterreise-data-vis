import type { SongInfo, CyclePerformance, Parameter, PerformanceRow, PerformanceMetadata } from "$lib/types";

export const lineGraphPageState = $state({
	allPerformances: [] as CyclePerformance[],
	selectedPerformances: [] as CyclePerformance[],
	pieces: [] as SongInfo[],
	selectedPiece: null as SongInfo | null,
	selectedParameter: "tempo" as Parameter,
	graphPerformances: [] as PerformanceRow[][],
	graphMetadata: [] as PerformanceMetadata[],
	showGraph: false
});
