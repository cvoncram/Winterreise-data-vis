<script lang="ts">
    import { onMount } from "svelte";
    import MeiLinearRibbon from '$lib/components/containers/MeiLinearRibbon.svelte';
    import MultiplePerformancesSelector from '$lib/components/partials/MultiplePerformancesSelector.svelte';
    import ColorSchemeSelector from '$lib/components/partials/ColorSchemeSelector.svelte';
    import type { PerformanceRow, PerformanceMetadata, NormalizationReference, CyclePerformance } from '$lib/types';
    import { selection } from "$lib/selection.svelte";
    import { display } from "$lib/displaySettings.svelte";
	import MeiViewer from "$lib/components/containers/MeiViewer.svelte";
    import { tick } from "svelte";
    import { fetchNormalizationReference } from "$lib/api";
    import { totalDuration } from "$lib/utils/performanceVisuals";
    import { morph } from "$lib/ribbonMorph.svelte";
    import { multiPerformancePageState as pageState } from "./pageState.svelte";

    let ribbonList: HTMLDivElement | undefined = $state();

    /** Reports the first ribbon's position to the morph overlay. */
    $effect(() => {
        if (!morph.active || morph.to || !ribbonList) return;
        void pageState.selectedPerformances.length;

        tick().then(() => {
            const svg = ribbonList?.querySelector("svg");
            if (svg) morph.to = svg.getBoundingClientRect();
        });
    });

    let maxDuration = $derived(
        Math.max(0, ...pageState.selectedPerformances.map(
            p => totalDuration(p.songPerformances[0]?.rows ?? [])
        ))
    );

    /** Song number, taken from the file name of the handed-over passage. */
    const nbInOrder = (() => {
        const piecePathSplit = selection.piecePath.split("_");
        return Number(piecePathSplit[piecePathSplit.length - 3]) ?? 0
    });

    let error = $state('');
    let loading = $state(false);

    /** Sets the passage from the semicircular ribbon as the locked first performance; fetches its normalization reference if missing. */
    function applySelection() {
        const fullPath = selection.piecePath;
        const folderName = fullPath.split("/")[1];
        const matchingPerf = pageState.allPerformances.find(p => p.path === folderName);

        pageState.lockedPath = folderName;

        pageState.selectedPerformances = [{
            path: folderName,
            label: matchingPerf?.label ?? folderName,
            metadata: selection.metadata,
            normalizationReference: selection.normalizationReference ?? undefined,
            songPerformances: [{ song: null, rows: selection.measures }]
        }];

        if (selection.normalizationReference) return;

        fetchNormalizationReference(folderName, nbInOrder())
            .then(normalizationReference => {
                pageState.selectedPerformances = pageState.selectedPerformances.map(p =>
                    p.path === folderName ? { ...p, normalizationReference } : p
                );
            })
            .catch(e => console.error(e));
    }

    /** Shows or hides the score of the selected measures. */
    async function displayScore() {
        pageState.showScore = !pageState.showScore;
        if (pageState.showScore) {
            try {
                const scoreRes = await fetch(`/db/file-measures?piece=${nbInOrder()}&start=${selection.startMeasure}&end=${selection.endMeasure}`)
                pageState.score = await scoreRes.text();

            } catch (e:any) {
                error = e.message;
                console.error(e);
            }
        }
    }

    // Performance list, then the passage handed over from the ribbon page.
    onMount(async () => {
        try {
            if (pageState.allPerformances.length === 0) {
                const perfRes = await fetch('/db/performances');
                if (!perfRes.ok) throw new Error('Could not fetch file list');
                const perfList = await perfRes.json();
                pageState.allPerformances = perfList.map((p: any) => ({
                    path: p.path,
                    label: p.label,
                    songPerformances: [],
                    metadata: { sampleRate: 0, mfValue: 0, dynamicStep: 0 }
                }));
            }
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }

        if (selection.pending) {
            selection.pending = false;
            applySelection();
        }
    });

    /** Beats, metadata and normalization reference of the selected passage, per performance. */
    async function fetchPerformanceData(paths: string[]) {
        error = '';

        try {
            const piece = nbInOrder();
            const sM = selection.startMeasure;
            const sB = selection.startBeat;
            const eM = selection.endMeasure;
            const eB = selection.endBeat;

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

            return await Promise.all(results.map(async r => {
                let normalizationReference: NormalizationReference | undefined;
                try {
                    normalizationReference = await fetchNormalizationReference(r.performance, piece);
                } catch (e) {
                    console.error(e);
                }
                return { ...r, normalizationReference };
            }));
        } catch (e: any) {
            error = e.message;
            console.error(e);
            return [];
        }
    }

    /** Loads newly added performances, keeps loaded ones, the locked performance first. */
    async function handlePerformancesChange(newSelection: CyclePerformance[]) {
        const existingPaths = new Set(pageState.selectedPerformances.map(p => p.path));
        const newPaths = newSelection
            .map(p => p.path)
            .filter(path => !existingPaths.has(path));

        if (newPaths.length > 0) loading = true;
        try {
            const existingMap = new Map(
                pageState.selectedPerformances.map(p => [p.path, p])
            );

            const fetchedMap = new Map<string, { performance: string; data: PerformanceRow[]; metadata: PerformanceMetadata; normalizationReference?: NormalizationReference }>();

            if (newPaths.length > 0) {
                const results = await fetchPerformanceData(newPaths);
                results.forEach(r => fetchedMap.set(r.performance, r));
            }

            const resolved = newSelection.map(p => {
                if (fetchedMap.has(p.path)) {
                    const r = fetchedMap.get(p.path)!;
                    return {
                        ...p,
                        metadata: r.metadata,
                        normalizationReference: r.normalizationReference,
                        songPerformances: [{ song: null, rows: r.data }]
                    };
                }
                return existingMap.get(p.path) ?? p;
            });
            
            pageState.selectedPerformances = [
                ...resolved.filter(p => p.path === pageState.lockedPath),
                ...resolved.filter(p => p.path !== pageState.lockedPath)
            ];

        } catch (e) {
            console.error("ERROR in handlePerformancesChange:", e);
        } finally {
            loading = false;
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
            <ColorSchemeSelector bind:selectedColorDropdown={display.colorScheme} />

        </div>
        <MultiplePerformancesSelector
            performances={pageState.allPerformances}
            selectedPerformances={pageState.selectedPerformances}
            lockedPath={pageState.lockedPath}
            onSelectionChange={handlePerformancesChange}
        />

        <button class="btn btn-primary"
        onclick={() => {
            displayScore();
        }}>Display score measures</button>

        <div class="flex gap-6 w-full">
            <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                <h2 class="card-title justify-center mb-2 ">Display options</h2>
                <button
                    class={`btn btn-block ${
                        pageState.selectSameMeasure === true
                            ? "btn-primary"
                            : "bg-base-300"
                    }`}
                    onclick={() => (pageState.selectSameMeasure = true)}
                >Same measure in each performance</button>
                <button
                    class={`btn btn-block ${
                        pageState.selectSameMeasure === false
                            ? "btn-primary"
                            : "bg-base-300"
                    }`}
                    onclick={() => (pageState.selectSameMeasure = false)}
                >Each performance individually</button>
            </div>
        </div>
    </aside>

    <main class="flex-1 flex gap-4 p-6 overflow-hidden min-h-screen">
        <!-- Morph overlay in place of the first ribbon. -->
        <div class="w-[50%] overflow-auto" bind:this={ribbonList}
             style:opacity={morph.active ? 0 : 1}>
            {#each pageState.selectedPerformances as performance (performance.path)}
                <div class="relative w-full">{performance.label}</div>
                <MeiLinearRibbon
                    bind:selectedColorDropdown={display.colorScheme}
                    displayedRows={performance.songPerformances[0]?.rows ?? []}
                    metadata={performance.metadata}
                    normalizationReference={performance.normalizationReference}
                    selectedRowAll={pageState.selectSameMeasure}
                    bind:selectedRowTarget={pageState.selectedRowTarget}
                    {maxDuration}
                    label={performance.label}
                />
            {/each}
            {#if loading}
                <div class="flex items-center justify-center w-full py-10">
                    <span class="loading loading-spinner loading-lg"></span>
                </div>
            {/if}
        </div>

        <div class="w-[50%] overflow-auto">
            {#if pageState.showScore}
                <MeiViewer
                    pageHeight={500}
                    scale={40}
                    spacingPercent={20}
                    src={pageState.score}
                />
            {/if}
        </div>
    </main>
</div>
