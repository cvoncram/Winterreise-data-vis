import type { SongInfo } from "$lib/types";

export const scoresPageState = $state({
	files: [] as SongInfo[],
	selectedFile: null as SongInfo | null,
	meiContent: null as string | null,
	scale: 50,
	spacingPercent: 25,
	pageWidth: 1400,
	pageHeight: 1000
});
