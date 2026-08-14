import type { PerformanceRow, PerformanceMetadata, NormalizationReference, SongInfo, CyclePerformance } from "$lib/types";

export const multiParameterPageState = $state({
	recordings: [] as CyclePerformance[],
	selectedRecording: null as CyclePerformance | null,
	pieces: [] as SongInfo[],
	selectedPiece: null as SongInfo | null,
	metadata: null as PerformanceMetadata | null,
	normalizationReference: null as NormalizationReference | null,
	tableRows: [] as PerformanceRow[],
	active: "visualization",
	brushEnabled: false,
	displayedRows: [] as PerformanceRow[]
});
