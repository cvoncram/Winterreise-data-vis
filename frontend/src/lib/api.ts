import type { CyclePerformance, NormalizationReference, SongInfo } from "$lib/types";

export async function fetchAllPerformances(): Promise<CyclePerformance[]> {
	const res = await fetch('/db/performances');
	if (!res.ok) throw new Error('Could not fetch file list');
	const perfList = await res.json();
	return perfList.map((p: any) => ({
		path: p.path,
		label: p.label,
		year: p.year ?? null,
		pianist: p.pianist ?? null,
		city: p.city ?? null,
		recordingContext: p.recordingContext ?? null,
		songPerformances: [],
		metadata: { sampleRate: 0, mfValue: 0, dynamicStep: 0 }
	}));
}

export async function fetchPieces(): Promise<SongInfo[]> {
	const res = await fetch('/db/scores-folder');
	if (!res.ok) throw new Error('could not fetch pieces list');
	const piecesList = await res.json();
	return piecesList.map((p: any) => ({
		label: p.label,
		nbInOrder: p.order,
		path: p.path
	}));
}

export async function fetchNormalizationReference(
	performance: string,
	piece: number
): Promise<NormalizationReference> {
	const search = new URLSearchParams({ performance, piece: String(piece) });
	const res = await fetch(`/db/stats/normalization-reference?${search.toString()}`);
	if (!res.ok) throw new Error('Could not fetch normalization reference');
	return res.json();
}

export type DtwScope = 'piece' | 'cycle' | 'halfCycle' | 'measures';

export type DtwMetric = 'euclidean' | 'mahalanobis';

export interface DtwAnalysisParams {
	parameters: string[];
	metric?: DtwMetric;
	weights?: number[];
	paths: string[];
	scope: DtwScope;
	piece?: number;
	half?: 1 | 2;
	start?: number;
	startBeat?: number;
	end?: number;
	endBeat?: number;
}

export interface DtwAnalysisResult {
	parameters: string[];
	metric?: DtwMetric;
	weights?: number[] | null;
	piece: number | null;
	n: number;
	matrix: (number | null)[][];
	normalizedMatrix: (number | null)[][];
	/** Kendall's tau-b per pair, averaged across the selected parameters. */
	correlationMatrix: (number | null)[][];
	warnings: { i: number; j: number; performances: string[]; reasons: string[] }[];
	scope: DtwScope;
}

/** One piece of a pair comparison; the fields after `reason` are absent when it could not be compared. */
export interface PairPieceRow {
	piece: number;
	title: string;
	usable: boolean;
	reason: string | null;
	beats?: [number, number];
	pairs?: number;
	distance?: number;
	normalizedDistance?: number;
	/** Keyed by parameter name, plus "combined". */
	tau?: Record<string, number | null>;
	/** What this piece yields without any real correspondence — read tau against it. */
	floor?: Record<string, number | null>;
	path?: { offDiagonalShare: number; maxOffset: number; longestRun: number };
}

/** One stretch where the two recordings pull apart; positive means the first reads higher. */
export interface PairDifference {
	piece: number;
	title: string;
	parameter: string;
	value: number;
	from: string | null;
	to: string | null;
	/** Mean untransformed measurement over the same stretch, per recording. */
	first: number | null;
	second: number | null;
}

export interface PairAnalysisResult {
	performances: string[];
	parameters: string[];
	scope: DtwScope;
	pieces: PairPieceRow[];
	differences: PairDifference[];
	total: {
		distance: number;
		normalizedDistance: number | null;
		tau: number | null;
		floor: number | null;
		beats: number;
		piecesCompared: number;
	};
	onlyFirst: number[];
	onlySecond: number[];
}

function analysisQuery(params: DtwAnalysisParams): URLSearchParams {
	const search = new URLSearchParams();
	params.parameters.forEach((p) => search.append('parameters', p));
	if (params.metric) search.set('metric', params.metric);
	if (params.weights) params.weights.forEach((w) => search.append('weights', String(w)));
	search.set('scope', params.scope);
	if (params.piece !== undefined) search.set('piece', String(params.piece));
	if (params.half !== undefined) search.set('half', String(params.half));
	if (params.start !== undefined) search.set('start', String(params.start));
	if (params.startBeat !== undefined) search.set('start_beat', String(params.startBeat));
	if (params.end !== undefined) search.set('end', String(params.end));
	if (params.endBeat !== undefined) search.set('end_beat', String(params.endBeat));
	params.paths.forEach((p) => search.append('paths', p));
	return search;
}

/** How far the analysis has got; `stage` says what it is busy with. */
export interface AnalysisProgress {
	stage: 'fetching' | 'comparing';
	done: number;
	total: number;
}

/**
 * The analysis over a stream, so that the caller can follow its progress.
 *
 * A whole cycle means several hundred files fetched one by one and hundreds
 * of pairs compared; without this the browser sits on an unexplained wait of
 * minutes. The plain runDtwAnalysis stays for callers that do not care.
 */
export function runDtwAnalysisStreamed(
	params: DtwAnalysisParams,
	onProgress: (progress: AnalysisProgress) => void
): Promise<DtwAnalysisResult> {
	return new Promise((resolve, reject) => {
		const source = new EventSource(`/db/analysis/stream?${analysisQuery(params).toString()}`);

		source.onmessage = (event) => {
			const update = JSON.parse(event.data);
			if (update.error) {
				source.close();
				reject(new Error(update.error));
			} else if (update.result) {
				source.close();
				resolve(update.result);
			} else {
				onProgress(update);
			}
		};

		// EventSource reconnects by itself, which would silently start the whole
		// analysis again; closing it first turns a lost connection into a plain
		// failure.
		source.onerror = () => {
			source.close();
			reject(new Error('The connection to the analysis was lost'));
		};
	});
}

export async function runDtwAnalysis(params: DtwAnalysisParams): Promise<DtwAnalysisResult> {
	const res = await fetch(`/db/analysis?${analysisQuery(params).toString()}`);
	if (!res.ok) throw new Error('Invalid request: Could not fetch the requested data');
	return res.json();
}

/** The same comparison as one link of the network, taken apart piece by piece. */
export async function fetchPairAnalysis(params: DtwAnalysisParams): Promise<PairAnalysisResult> {
	const res = await fetch(`/db/analysis/pair?${analysisQuery(params).toString()}`);
	if (!res.ok) throw new Error('Could not fetch the details of this comparison');
	return res.json();
}