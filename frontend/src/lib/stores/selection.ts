import { writable } from 'svelte/store';
import type { PerformanceRow, PerformanceMetadata } from '$lib/types';

export const selectedMeasuresStore = writable<PerformanceRow[]>([]);
export const selectedPieceStore = writable<PerformanceMetadata>();
export const selectedPiecePath = writable("");
export const startMeasure = writable(0);
export const startBeat = writable(0);
export const endMeasure = writable(0);
export const endBeat = writable(0);
