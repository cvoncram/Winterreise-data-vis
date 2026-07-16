<script lang="ts">
    import { get } from "svelte/store";
    import { onMount } from "svelte";
    import MeiLinearRibbon from '$lib/components/containers/MeiLinearRibbon.svelte';
    import MultiplePerformancesSelector from '$lib/components/partials/MultiplePerformancesSelector.svelte';
    import ColorSchemeSelector from '$lib/components/partials/ColorSchemeSelector.svelte';
    import type { PerformanceRow, PerformanceMetadata, CyclePerformance } from '$lib/types';
    import { selectedMeasuresStore, selectedPieceStore, selectedPiecePath, startMeasure, startBeat, endMeasure, endBeat } from "$lib/stores/selection";
	import MeiViewer from "$lib/components/containers/MeiViewer.svelte";

    const nbInOrder = (() => {
        const piecePathSplit = get(selectedPiecePath).split("_");
        return Number(piecePathSplit[piecePathSplit.length - 3]) ?? 0
    });

    let error = $state('');
    let showScore = $state(false);
    let score = $state("");
    let selectSameMeasure = $state(false);
    let selectedRowTarget = $state<string | null>(null);

    let allPerformances = $state<CyclePerformance[]>([]);
    let selectedPerformances = $state<CyclePerformance[]>([]);

    let selectedColorDropdown: string = $state("viridisScheme");


    let lockedPath = $state<string | null>(null);

    function applySelection() {
        const fullPath = get(selectedPiecePath);
        const folderName = fullPath.split("/")[1];
        const matchingPerf = allPerformances.find(p => p.path === folderName);

        lockedPath = folderName; // set once, never changes

        selectedPerformances = [{
            path: folderName,
            label: matchingPerf?.label ?? folderName,
            metadata: get(selectedPieceStore),
            songPerformances: [{ song: null, rows: get(selectedMeasuresStore) }]
        }];
    }
    
    async function displayScore() {
        showScore = !showScore;
        if (showScore) {
            try {
                const scoreRes = await fetch(`/db/file-measures?piece=${nbInOrder()}&start=${get(startMeasure)}&end=${get(endMeasure)}`)
                score = await scoreRes.text();

            } catch (e:any) {
                error = e.message;
                console.error(e);
            }
        }
    }

    onMount(async () => {
        console.log($selectedPiecePath);
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
        applySelection();
    });

    async function fetchPerformanceData(paths: string[]) {
        error = '';

        try {
            const piece = nbInOrder();
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
            const existingMap = new Map(
                selectedPerformances.map(p => [p.path, p])
            );

            const existingPaths = new Set(selectedPerformances.map(p => p.path));
            const newPaths = newSelection
                .map(p => p.path)
                .filter(path => !existingPaths.has(path));

            const fetchedMap = new Map<string, { performance: string; data: PerformanceRow[]; metadata: PerformanceMetadata }>();

            if (newPaths.length > 0) {
                const results = await fetchPerformanceData(newPaths);
                results.forEach(r => fetchedMap.set(r.performance, r));
            }

            selectedPerformances = newSelection.map(p => {
                if (fetchedMap.has(p.path)) {
                    const r = fetchedMap.get(p.path)!;
                    return {
                        ...p,
                        metadata: r.metadata,
                        songPerformances: [{ song: null, rows: r.data }]
                    };
                }
                return existingMap.get(p.path) ?? p;
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
            <ColorSchemeSelector bind:selectedColorDropdown />
        </div>

        <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col overflow-visible">
            <MultiplePerformancesSelector
                performances={allPerformances}
                selectedPerformances={selectedPerformances}
                {lockedPath}
                onSelectionChange={handlePerformancesChange}
            />
        </div>

        <button class="btn btn-primary"
        onclick={() => {
            displayScore();
        }}>Display score measures</button>

        <div class="flex gap-6 w-full">
            <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                <h2 class="card-title justify-center mb-2 ">Display options</h2>
                <button 
                    class={`btn btn-block ${
                        selectSameMeasure === true
                            ? "btn-primary"
                            : "bg-base-300"
                    }`}
                    onclick={() => (selectSameMeasure = true)}
                >Same measure in each performance</button>
                <button
                    class={`btn btn-block ${
                        selectSameMeasure === false
                            ? "btn-primary"
                            : "bg-base-300"
                    }`}
                    onclick={() => (selectSameMeasure = false)}
                >Each performance individually</button>
            </div>
        </div>
    </aside>

    <main class="flex-1 flex gap-4 p-6 overflow-hidden">
        <div class="w-[50%] overflow-auto">
            {#each selectedPerformances as performance (performance.path)}
                <div class="relative w-full">{performance.label}</div>
                <MeiLinearRibbon
                    bind:selectedColorDropdown
                    displayedRows={performance.songPerformances[0]?.rows ?? []}
                    metadata={performance.metadata}
                    selectedRowAll={selectSameMeasure}
                    bind:selectedRowTarget
                />
            {/each}
        </div>

        <div class="w-[50%] overflow-auto">
            {#if showScore}
                <MeiViewer
                    pageHeight={500}
                    pageWidth={700}
                    scale={40}
                    spacingPercent={20}
                    src={score}
                />
            {/if}
        </div>
    </main>
</div>