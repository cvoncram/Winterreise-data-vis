import type { CyclePerformance, NormalizationReference, SongInfo } from "$lib/types";

export async function fetchAllPerformances(): Promise<CyclePerformance[]> {
	const res = await fetch('/db/performances');
	if (!res.ok) throw new Error('Could not fetch file list');
	const perfList = await res.json();
	return perfList.map((p: any) => ({
		path: p.path,
		label: p.label,
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
	parameter?: string;
	parameters?: string[];
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
	parameter?: string;
	parameters?: string[];
	metric?: DtwMetric;
	weights?: number[] | null;
	piece: number | null;
	n: number;
	matrix: number[][];
	scope: DtwScope;
}

export async function runDtwAnalysis(params: DtwAnalysisParams): Promise<DtwAnalysisResult> {
	const search = new URLSearchParams();
	if (params.parameters?.length) {
		params.parameters.forEach((p) => search.append('parameters', p));
		if (params.metric) search.set('metric', params.metric);
		if (params.weights) params.weights.forEach((w) => search.append('weights', String(w)));
	} else if (params.parameter) {
		search.set('parameter', params.parameter);
	}
	search.set('scope', params.scope);
	if (params.piece !== undefined) search.set('piece', String(params.piece));
	if (params.half !== undefined) search.set('half', String(params.half));
	if (params.start !== undefined) search.set('start', String(params.start));
	if (params.startBeat !== undefined) search.set('start_beat', String(params.startBeat));
	if (params.end !== undefined) search.set('end', String(params.end));
	if (params.endBeat !== undefined) search.set('end_beat', String(params.endBeat));
	params.paths.forEach((p) => search.append('paths', p));

	const res = await fetch(`/db/analysis?${search.toString()}`);
	if (!res.ok) throw new Error('Invalid request: Could not fetch the requested data');
	return res.json();
}
