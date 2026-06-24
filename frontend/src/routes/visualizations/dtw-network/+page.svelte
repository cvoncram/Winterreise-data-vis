<script lang=ts>
    import DtwNetwork from "$lib/components/containers/DtwNetwork.svelte";
    import ScoreSelector from "$lib/components/partials/ScoreSelector.svelte";
    import MultiplePerformancesSelector from "$lib/components/partials/MultiplePerformancesSelector.svelte";
    import ParameterSelector from "$lib/components/partials/ParameterSelector.svelte";
    import type { SongInfo, CyclePerformance, Parameter } from "$lib/types";
    import {onMount} from "svelte";

    let linkWidth = $state(200);
    let nodeSize = $state(10);
    let linkWidthLabel = $derived(linkWidth);
    let nodeSizeLabel = $derived(nodeSize);

    let allPerformances = $state<CyclePerformance[]>([]);
    let selectedPerformances = $state<CyclePerformance[]>([]);
    let pieces = $state<SongInfo[]>([]);
    let selectedPiece = $state<SongInfo | null>(null);
    let selectedParameter = $state<Parameter>("tempo");
    let error: string = $state("");

    let nodes = $state<{ id: number; label?: string; }[]>([]);
    let links = $state<{ source: number; target: number; distance: number; }[]>([]);
    
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

    async function generateNetwork() {
        if (!selectedPiece|| !nodes || selectedPerformances.length === 0) return;
        try {
            const piece = selectedPiece.nbInOrder;
            const folders = selectedPerformances.map(p => `paths=${p.path}`).join("&");
            const res = await fetch(`/db/analysis?parameter=${selectedParameter}&piece=${piece}&${folders}`);
            if (!res.ok) throw new Error ("Invalid request: Could not fetch the requested data");
            const { matrix, n } = await res.json();

            const newNodes = selectedPerformances.map((performance, i) => ({
                id: i,
                label: performance.label
            }));

            const newLinks: { source: number; target: number; distance: number; }[] = [];
            for (let i = 0; i < n; i++) {
                for (let j = i + 1; j < n; j++) {
                    newLinks.push({
                        source: i,
                        target: j,
                        distance: matrix[i][j]
                    });
                }
            }
            nodes = newNodes;
            links = newLinks;

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
            <MultiplePerformancesSelector performances={allPerformances} selectedPerformances={selectedPerformances}/>
            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
            <button class="btn btn-primary" onclick={generateNetwork} type="submit">Generate Network</button>
        </div>
        <div class="card bg-base-200 p-4 shadow-md justify-start">
            <label>Node size
                <input type="range" min="1" max="20" value={nodeSize} class="range range-s range-primary"
                onchange={(e) => { nodeSize = Number(e.currentTarget.value)}}
                oninput={(e) => {nodeSizeLabel = Number(e.currentTarget.value)}}/>
                <span class="font-bold">{nodeSizeLabel}</span>
            </label>
            <label>Link width
                <input type="range" min="10" max="400" value={linkWidth} class="range range-s range-primary"
                onchange={(e) => { linkWidth = Number(e.currentTarget.value)}}
                oninput={(e) => {linkWidthLabel = Number(e.currentTarget.value)}}/>
                <span class="font-bold">{linkWidthLabel}</span>
            </label>
        </div>
    </aside>
    
    <main class="flex-1 flex flex-col p-10 overflow-hidden">
        <div style="background-color: rgba(254, 255, 223, .2);" class="rounded-xl">
            <DtwNetwork links={links} nodes={nodes} bind:linkWidth={linkWidth} bind:nodeSize={nodeSize} />   
        </div>
    </main>
    
</div>