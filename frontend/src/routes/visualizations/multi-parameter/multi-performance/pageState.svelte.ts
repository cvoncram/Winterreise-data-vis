import type { CyclePerformance } from "$lib/types";

export const multiPerformancePageState = $state({
	allPerformances: [] as CyclePerformance[],
	selectedPerformances: [] as CyclePerformance[],
	selectSameMeasure: false,
	selectedRowTarget: null as string | null,
	lockedPath: null as string | null,
	showScore: false,
	score: ""
});
