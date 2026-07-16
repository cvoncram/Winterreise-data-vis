<script lang=ts>
    import DtwNetwork from "$lib/components/containers/DtwNetwork.svelte";
    import ScoreSelector from "$lib/components/partials/ScoreSelector.svelte";
    import MultiplePerformancesSelector from "$lib/components/partials/MultiplePerformancesSelector.svelte";
    import ParameterSelector from "$lib/components/partials/ParameterSelector.svelte";
    import MeasureRangeInput from "$lib/components/partials/MeasureRangeInput.svelte";
    import type { SongInfo, CyclePerformance, Parameter } from "$lib/types";
    import { fetchAllPerformances, fetchPieces, runDtwAnalysis, type DtwScope } from "$lib/api";
    import {onMount} from "svelte";

    let linkWidth = $state(200);
    let nodeSize = $state(10);
    let linkWidthLabel = $derived(linkWidth);
    let nodeSizeLabel = $derived(nodeSize);

    let analysisScope = $state<DtwScope | "">("");
    let ersteAbtheilung = $state(true);

    let allPerformances = $state<CyclePerformance[]>([]);
    let selectedPerformances = $state<CyclePerformance[]>([]);
    let pieces = $state<SongInfo[]>([]);
    let selectedPiece = $state<SongInfo | null>(null);
    let selectedParameter = $state<Parameter>("tempo");
    let error: string = $state("");

    let measureStart = $state(1);
    let measureStartBeat = $state(1);
    let measureEnd = $state(1);
    let measureEndBeat = $state(1);

    let nodes = $state<{ id: number; label?: string; }[]>([]);
    let links = $state<{ source: number; target: number; distance: number; }[]>([]);

    async function selectPiece(piece: SongInfo) {
        selectedPiece = piece;
    }

    function handlePerformancesChange(newSelection: CyclePerformance[]) {
        selectedPerformances = newSelection;
    }

    async function selectParameter (parameter: Parameter) {
        selectedParameter = parameter;
    }

    async function generateNetwork() {
        if (!analysisScope || selectedPerformances.length === 0) return;
        if ((analysisScope === "piece" || analysisScope === "measures") && !selectedPiece) return;

        try {
            const result = await runDtwAnalysis({
                parameter: selectedParameter,
                paths: selectedPerformances.map(p => p.path),
                scope: analysisScope,
                piece: selectedPiece?.nbInOrder,
                half: analysisScope === "halfCycle" ? (ersteAbtheilung ? 1 : 2) : undefined,
                start: analysisScope === "measures" ? measureStart : undefined,
                startBeat: analysisScope === "measures" ? measureStartBeat : undefined,
                end: analysisScope === "measures" ? measureEnd : undefined,
                endBeat: analysisScope === "measures" ? measureEndBeat : undefined,
            });

            const newNodes = selectedPerformances.map((performance, i) => ({
                id: i,
                label: performance.label
            }));

            const newLinks: { source: number; target: number; distance: number; }[] = [];
            for (let i = 0; i < result.n; i++) {
                for (let j = i + 1; j < result.n; j++) {
                    newLinks.push({
                        source: i,
                        target: j,
                        distance: result.matrix[i][j]
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
            pieces = await fetchPieces();
            allPerformances = await fetchAllPerformances();
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    })

</script>

<div class="flex h-auto overflow-hidden">
    <aside class="w-64 shrink-0 bg-base-200 p-4 items-center flex flex-col justify-center gap-4 min-h-screen">
        {#if analysisScope == ""}
            <div class="card bg-base-200 p-4 shadow-md gap-2 justify-start">
                <h2 class="card-title">Choose scope of analysis</h2>
                <button class="btn btn-primary" onclick={() => {analysisScope = "cycle"}}>Whole cycle</button>
                <button class="btn btn-primary" onclick={() => {analysisScope = "halfCycle"}}>Half cycle ("Abtheilung")</button>
                <button class="btn btn-primary" onclick={() => {analysisScope = "piece"}}>Single piece</button>
                <button class="btn btn-primary" onclick={() => {analysisScope = "measures"}}>Selected measures</button>
            </div>
        {:else}

            <button onclick={() => {analysisScope = ""}} class="btn btn-primary"> <p class="text-4xl">&lArr;</p> Change scope of analysis</button>

            {#if analysisScope == "piece"}

                <div class="card bg-base-200 p-4 shadow-md justify-start">
                    <ScoreSelector files={pieces} selectedFile={selectedPiece} onFileSelect={selectPiece} />
                    <ParameterSelector selectedParameter={selectedParameter} onParameterSelect={selectParameter}/>
                    <MultiplePerformancesSelector performances={allPerformances} selectedPerformances={selectedPerformances} onSelectionChange={handlePerformancesChange}/>
                </div>

            {:else if analysisScope == "cycle"}
                <ParameterSelector selectedParameter={selectedParameter} onParameterSelect={selectParameter}/>
                <MultiplePerformancesSelector performances={allPerformances} selectedPerformances={selectedPerformances} onSelectionChange={handlePerformancesChange}/>

            {:else if analysisScope == "halfCycle"}
                <div class="flex gap-6 w-full">
                    <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                        <h2 class="card-title justify-center mb-2 ">Choose part of cycle</h2>
                        <button
                            class={`btn btn-block ${
                                ersteAbtheilung === true
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (ersteAbtheilung = true)}
                        >Erste Abtheilung (1-12)</button>
                        <button
                            class={`btn btn-block ${
                                ersteAbtheilung === false
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (ersteAbtheilung = false)}
                        >Zweite Abtheilung (13-24)</button>
                    </div>
                </div>
                <ParameterSelector selectedParameter={selectedParameter} onParameterSelect={selectParameter}/>
                <MultiplePerformancesSelector performances={allPerformances} selectedPerformances={selectedPerformances} onSelectionChange={handlePerformancesChange}/>

            {:else if analysisScope == "measures"}
                <ScoreSelector files={pieces} selectedFile={selectedPiece} onFileSelect={selectPiece} />
                <MeasureRangeInput bind:start={measureStart} bind:startBeat={measureStartBeat} bind:end={measureEnd} bind:endBeat={measureEndBeat} />
                <ParameterSelector selectedParameter={selectedParameter} onParameterSelect={selectParameter}/>
                <MultiplePerformancesSelector performances={allPerformances} selectedPerformances={selectedPerformances} onSelectionChange={handlePerformancesChange}/>
            {/if}

            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
            <button class="btn btn-primary" onclick={generateNetwork} type="submit">Generate Network</button>

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

        {/if}
    </aside>

    <main class="flex-1 flex flex-col p-10 overflow-hidden">
        <div style="background-color: rgba(254, 255, 223, .2);" class="rounded-xl">
            <DtwNetwork links={links} nodes={nodes} bind:linkWidth={linkWidth} bind:nodeSize={nodeSize} />
        </div>
    </main>

</div>
