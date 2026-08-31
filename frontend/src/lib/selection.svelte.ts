import type { PerformanceRow, PerformanceMetadata, NormalizationReference } from '$lib/types';

export const selection = $state({
	/**
	 * Set when "Compare with other performances" is clicked, cleared once the
	 * target page has consumed it.
	 */
	pending: false,
	measures: [] as PerformanceRow[],
	metadata: { sampleRate: 0, mfValue: 0, dynamicStep: 0 } as PerformanceMetadata,
	normalizationReference: null as NormalizationReference | null,
	piecePath: '',
	startMeasure: 0,
	startBeat: 0,
	endMeasure: 0,
	endBeat: 0
});