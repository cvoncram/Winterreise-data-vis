<script lang="ts">
	import { onMount } from "svelte";
    import type { SongInfo, CyclePerformance, Parameter, PerformanceRow, PerformanceMetadata } from "$lib/types";
    import MultiplePerformancesSelector from "$lib/components/partials/MultiplePerformancesSelector.svelte";
	import ScoreSelector from "$lib/components/partials/ScoreSelector.svelte";
	import ParameterSelector from "$lib/components/partials/ParameterSelector.svelte";
	import LineGraph from "$lib/components/containers/LineGraph.svelte";
    
    let allPerformances = $state<CyclePerformance[]>([]);
    let selectedPerformances = $state<CyclePerformance[]>([]);
    let pieces = $state<SongInfo[]>([]);
    let selectedPiece = $state<SongInfo | null>(null);
    let selectedParameter = $state<Parameter>("dynamics");
    let error: string = $state("");

    let graphPerformances = $state<PerformanceRow[][]>([]);
    let graphMetadata = $state<PerformanceMetadata[]>([]);
    let showGraph = $state(false);
    
    async function selectPiece(piece: SongInfo) {
        selectedPiece = piece;
        selectedPerformances = allPerformances.map(perf => ({
            ...perf,
            songPerformances: [{ song: piece, rows: [] }]
        }));
    }

    async function selectParameter (parameter: Parameter) {
        selectedParameter = parameter;
    }

    async function generateGraph() {
        if (!selectedPiece || selectedPerformances.length === 0) return;
        try {
            const results = await Promise.all(
            selectedPerformances.map(async (perf) => {
                const folder = perf.path;
                const fileNumber = selectedPiece!.nbInOrder;
                const fileName = `${folder}/${folder.split('/').pop()}_${fileNumber}_Audio_Data.xml`;
                return fetch(`/db/parsed-file?path=performances/${encodeURIComponent(fileName)}`)
                .then(res => {
                    if (!res.ok) throw new Error(`Could not fetch ${perf.label}`);
                    return res.json();
                });
            })
            );
            graphPerformances = results.map(r => r[1].data);
            graphMetadata = results.map(r => r[0].metadata);
            showGraph = true;
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }

    onMount(async () => {
        try {
            const perfRes = await fetch('/db/performances');
            if (!perfRes.ok) throw new Error('Could not fetch file list');
            const perfList = await perfRes.json();

            const piecesRes = await fetch("/db/scores-folder");
            if (!piecesRes.ok) throw new Error("could not fetch pieces list");
            const piecesList = await piecesRes.json();

            pieces = piecesList.map((p: any) => ({
                label: p.label,
                nbInOrder: p.order,
                path: p.path
            }));

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
    })

    

</script>

<div class="flex h-auto overflow-hidden">
    <aside class="w-64 shrink-0 bg-base-200 p-4 items-center flex flex-col justify-center gap-4">
        
        <div class="card bg-base-200 p-4 shadow-md justify-start">
            <ScoreSelector files={pieces} selectedFile={selectedPiece} onFileSelect={selectPiece} />
            <ParameterSelector selectedParameter={selectedParameter} onParameterSelect={selectParameter}/>
            <MultiplePerformancesSelector performances={allPerformances} bind:selectedPerformances={selectedPerformances}/>
            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
            <button class="btn btn-primary" onclick={generateGraph} type="submit">Generate Graph</button>
        </div>
    </aside>

    <main class="flex-1 flex flex-col p-10 overflow-hidden">
        <div style="background-color: rgba(254, 255, 223, .2);" class="border-2 border-[#668ba4] rounded-xl bg-base-200">
            {#if showGraph}
            <LineGraph performances={graphPerformances} parameter={selectedParameter} metadata={graphMetadata} />
            {:else}
            <div style="background-color: rgba(254, 255, 223, .2)" class="flex items-center justify-center w-full h-[80vh] rounded-lg">
                <p class="text-base-content opacity-50">Select a piece, parameter and performances, then click Generate Graph</p>
            </div>
            {/if}
        </div>
    </main>

</div>