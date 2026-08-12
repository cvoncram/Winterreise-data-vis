import type { PerformanceRow, PerformanceMetadata } from '$lib/types';

export const selection = $state({
	measures: [] as PerformanceRow[],
	metadata: { sampleRate: 0, mfValue: 0, dynamicStep: 0 } as PerformanceMetadata,
	piecePath: '',
	startMeasure: 0,
	startBeat: 0,
	endMeasure: 0,
	endBeat: 0
});