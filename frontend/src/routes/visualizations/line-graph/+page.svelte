<script lang="ts">
	import { onMount } from "svelte";
    import type { SongInfo, Parameter } from "$lib/types";
    import MultiplePerformancesSelector from "$lib/components/partials/MultiplePerformancesSelector.svelte";
	import ScoreSelector from "$lib/components/partials/ScoreSelector.svelte";
	import ParameterSelector from "$lib/components/partials/ParameterSelector.svelte";
	import LineGraph from "$lib/components/containers/LineGraph.svelte";
    import { fetchAllPerformances, fetchPieces } from "$lib/api";
    import { lineGraphPageState as pageState } from "./pageState.svelte";

    let error: string = $state("");
    let loading = $state(false);

    async function selectPiece(piece: SongInfo) {
        pageState.selectedPiece = piece;
        pageState.selectedPerformances = pageState.allPerformances.map(perf => ({
            ...perf,
            songPerformances: [{ song: piece, rows: [] }]
        }));
    }

    async function selectParameter (parameter: Parameter) {
        pageState.selectedParameter = parameter;
    }

    async function generateGraph() {
        if (!pageState.selectedPiece || pageState.selectedPerformances.length === 0) return;
        loading = true;
        try {
            const results = await Promise.all(
            pageState.selectedPerformances.map(async (perf) => {
                const folder = perf.path;
                const fileNumber = pageState.selectedPiece!.nbInOrder;
                const fileName = `${folder}/${folder.split('/').pop()}_${fileNumber}_Audio_Data.xml`;
                return fetch(`/db/parsed-file?path=performances/${encodeURIComponent(fileName)}`)
                .then(res => {
                    if (!res.ok) throw new Error(`Could not fetch ${perf.label}`);
                    return res.json();
                });
            })
            );
            pageState.graphPerformances = results.map(r => r[1].data);
            pageState.graphMetadata = results.map(r => r[0].metadata);
            pageState.showGraph = true;
        } catch (e: any) {
            error = e.message;
            console.error(e);
        } finally {
            loading = false;
        }
    }

    onMount(async () => {
        if (pageState.pieces.length > 0 && pageState.allPerformances.length > 0) return;
        try {
            pageState.pieces = await fetchPieces();
            pageState.allPerformances = await fetchAllPerformances();
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    })
</script>

<div class="flex h-auto overflow-hidden">
    <aside class="w-64 shrink-0 bg-base-200 p-4 items-center flex flex-col justify-center gap-4">

        <div class="card bg-base-200 p-4 shadow-md justify-start">
            <ScoreSelector files={pageState.pieces} selectedFile={pageState.selectedPiece} onFileSelect={selectPiece} />
            <ParameterSelector selectedParameter={pageState.selectedParameter} onParameterSelect={selectParameter}/>
            <MultiplePerformancesSelector performances={pageState.allPerformances} bind:selectedPerformances={pageState.selectedPerformances}/>
            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
            <button class="btn btn-primary" onclick={generateGraph} type="submit">Generate Graph</button>
        </div>
    </aside>

    <main class="flex-1 flex flex-col p-10 overflow-hidden">
        <div style="background-color: rgba(254, 255, 223, .2);" class="border-2 border-[#668ba4] rounded-xl bg-base-200">
            {#if loading}
            <div class="flex items-center justify-center w-full h-[80vh] rounded-lg">
                <span class="loading loading-spinner loading-lg"></span>
            </div>
            {:else if pageState.showGraph}
            <LineGraph performances={pageState.graphPerformances} parameter={pageState.selectedParameter} metadata={pageState.graphMetadata} />
            {:else}
            <div style="background-color: rgba(254, 255, 223, .2)" class="flex items-center justify-center w-full h-[80vh] rounded-lg">
                <p class="text-base-content opacity-50">Select a piece, parameter and performances, then click Generate Graph</p>
            </div>
            {/if}
        </div>
    </main>

</div>
