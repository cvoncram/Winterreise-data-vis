<script lang="ts">
    import { get } from "svelte/store";
    import { onMount } from "svelte";
    import MeiLinearRibbon from '$lib/components/containers/MeiLinearRibbon.svelte';
    import MultiplePerformancesSelector from '$lib/components/partials/MultiplePerformancesSelector.svelte';
    import type { PerformanceRow, PerformanceMetadata, CyclePerformance } from '$lib/types';
    import { selectedMeasuresStore, selectedPieceStore, selectedPiecePath, startMeasure, startBeat, endMeasure, endBeat } from "$lib/stores/selection";

    let error = $state('');
    let active = $state("visualization");

    let allPerformances = $state<CyclePerformance[]>([]);
    let selectedPerformances = $state<CyclePerformance[]>([]);

    let selectedColorDropdown: string = $state("viridisScheme");

    function applySelection() {
        const fullPath = get(selectedPiecePath);
        const folderName = fullPath.split("/")[1];

        selectedPerformances = [{
            path: folderName,
            label: "",
            metadata: get(selectedPieceStore),
            songPerformances: [{ song: null, rows: get(selectedMeasuresStore) }]
        }];

        for (let i=0; i < selectedPerformances.length; i++) {
            for (let index = 0; index < allPerformances.length; index++) {
                if (selectedPerformances[i].path === allPerformances[index].path){
                    selectedPerformances[i].label = allPerformances[index].label;
                }
            }
        };
    }

    onMount(async () => {
        applySelection();

        try {
            const perfRes = await fetch('/db/performances');
            if (!perfRes.ok) throw new Error('Could not fetch file list');
            const perfList = await perfRes.json();
            allPerformances = perfList.map((p: any) => ({
                path: p.path,
                label: p.label,
                songPerformances: [],
                metadata: { sampleRate: 0, mfValue: 0, dynamicStep: 0 }
            }));
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    });

    async function fetchPerformanceData(paths: string[]) {
        error = '';

        try {
            const piece = 1; // adjust if this should come from a store too
            const sM = get(startMeasure);
            const sB = get(startBeat);
            const eM = get(endMeasure);
            const eB = get(endBeat);

            const params = new URLSearchParams();
            params.set("piece", String(piece));
            params.set("start", String(sM));
            params.set("start_beat", String(sB));
            params.set("end", String(eM));
            params.set("end_beat", String(eB));
            paths.forEach(p => params.append("paths", p));

            const res = await fetch(`/db/parsed-measures?${params.toString()}`);
            if (!res.ok) throw new Error('Could not fetch parsed MEI data');

            const results: { performance: string; data: PerformanceRow[]; metadata: PerformanceMetadata }[] = await res.json();

            return results;
        } catch (e: any) {
            error = e.message;
            console.error(e);
            return [];
        }
    }

    async function handlePerformancesChange(newSelection: CyclePerformance[]) {

        try {
            const existingPaths = new Set(selectedPerformances.map(p => p.path));

            const newPaths = newSelection
                .map(p => p.path)
                .filter(path => !existingPaths.has(path));

            if (newPaths.length === 0) {
                selectedPerformances = newSelection;
                return;
            }

            const results = await fetchPerformanceData(newPaths);

            const fetchedMap = new Map(results.map(r => [r.performance, r]));

            selectedPerformances = newSelection.map(p => {
                if (fetchedMap.has(p.path)) {
                    const r = fetchedMap.get(p.path)!;
                    return {
                        ...p,
                        metadata: r.metadata,
                        songPerformances: [{ song: null, rows: r.data }]
                    };
                }
                return p;
            });

        } catch (e) {
            console.error("ERROR in handlePerformancesChange:", e);
        }
    }
    
</script>

<div class="flex h-auto overflow-hidden">
    <aside class="w-64 shrink-0 bg-base-200 p-4 flex flex-col gap-4">
        {#if error}
            <p class="text-error">{error}</p>
        {/if}

        <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col overflow-visible">
            <h2 class="card-title justify-center">Display options</h2>
            <label>
                <h3 class="mt-2 text-l">Color scheme</h3>
                <select class="select select-bordered w-full" bind:value={selectedColorDropdown}>
                    <option value="viridisScheme">Viridis (default)</option>
                    <option value="infernoScheme">Inferno</option>
                    <option value="cividisScheme">Cividis</option>
                    <option value="bluesScheme">Blue shades</option>
                    <option value="greensScheme">Green shades</option>
                    <option value="redsScheme">Red shades</option>
                </select>
            </label>
        </div>
        <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col overflow-visible">
            <MultiplePerformancesSelector
                performances={allPerformances}
                selectedPerformances={selectedPerformances}
                lockedPath={selectedPerformances[0]?.path}
                onSelectionChange={handlePerformancesChange}
            />
        </div>
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">
        <div class="flex-1 relative p-6 overflow-auto mb-12">
            {#if active === "visualization"}
                {#each selectedPerformances as performance}
                    <div class="relative w-full">{performance.label}</div>
                    <MeiLinearRibbon
                        bind:selectedColorDropdown
                        displayedRows={performance.songPerformances[0]?.rows ?? []}
                        metadata={performance.metadata}
                    />
                {/each}
            {/if}
        </div>
    </main>
</div>