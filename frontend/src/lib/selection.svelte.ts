import type { PerformanceRow, PerformanceMetadata, NormalizationReference } from '$lib/types';

export const selection = $state({
	/**
	 * Set when "Compare with other performances" is clicked, cleared once the
	 * target page has consumed it.
	 *
	 * The target cannot infer from the data alone whether a fresh selection
	 * was made: picking a different range within the same piece of the same
	 * recording leaves every other field unchanged, and is indistinguishable
	 * from merely navigating back. Recording the intent explicitly avoids
	 * that ambiguity.
	 */
	pending: false,
	measures: [] as PerformanceRow[],
	metadata: { sampleRate: 0, mfValue: 0, dynamicStep: 0 } as PerformanceMetadata,
	/**
	 * Carried over so the target page can colour its ribbon on first render.
	 * Fetching it there instead would leave the bars neutrally coloured until
	 * the response arrives, and they would then visibly change.
	 */
	normalizationReference: null as NormalizationReference | null,
	piecePath: '',
	startMeasure: 0,
	startBeat: 0,
	endMeasure: 0,
	endBeat: 0
});