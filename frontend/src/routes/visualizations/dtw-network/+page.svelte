<script lang=ts>
    import DtwNetwork from "$lib/components/containers/DtwNetwork.svelte";
    import DtwMatrix from "$lib/components/containers/DtwMatrix.svelte";
    import ScoreSelector from "$lib/components/partials/ScoreSelector.svelte";
    import MultiplePerformancesSelector from "$lib/components/partials/MultiplePerformancesSelector.svelte";
    import ParameterMultiSelector from "$lib/components/partials/ParameterMultiSelector.svelte";
    import MetricSelector from "$lib/components/partials/MetricSelector.svelte";
    import MeasureRangeInput from "$lib/components/partials/MeasureRangeInput.svelte";
    import type { SongInfo, CyclePerformance } from "$lib/types";
    import { fetchAllPerformances, fetchPieces, runDtwAnalysis } from "$lib/api";
    import {onMount} from "svelte";
    import { dtwNetworkPageState as pageState } from "./pageState.svelte";

    let linkWidthLabel = $derived(pageState.linkWidth);
    let nodeSizeLabel = $derived(pageState.nodeSize);

    let error: string = $state("");
    let loading = $state(false);
    let graphFinished = $state(false);

    /**
     * Weights in the order of the selected parameters, normalized to sum to one. Returns undefined where weighting cannot take effect.
     */
    function currentWeights(): number[] | undefined {
        const params = pageState.selectedParameters;
        if (params.length < 2 || pageState.selectedMetric !== "euclidean") return undefined;

        const raw = params.map(p => pageState.parameterWeights[p] ?? 0);
        const total = raw.reduce((sum, w) => sum + w, 0);
        if (total === 0) return params.map(() => 1 / params.length);
        return raw.map(w => w / total);
    }

    async function selectPiece(piece: SongInfo) {
        pageState.selectedPiece = piece;
    }

    function handlePerformancesChange(newSelection: CyclePerformance[]) {
        pageState.selectedPerformances = newSelection;
    }

    async function generateNetwork() {
        if (!pageState.analysisScope || pageState.selectedPerformances.length === 0 || pageState.selectedParameters.length === 0) return;
        if ((pageState.analysisScope === "piece" || pageState.analysisScope === "measures") && !pageState.selectedPiece) return;

        loading = true;
        try {
            const result = await runDtwAnalysis({
                parameters: pageState.selectedParameters,
                metric: pageState.selectedMetric,
                weights: currentWeights(),
                paths: pageState.selectedPerformances.map(p => p.path),
                scope: pageState.analysisScope,
                piece: pageState.selectedPiece?.nbInOrder,
                half: pageState.analysisScope === "halfCycle" ? (pageState.ersteAbtheilung ? 1 : 2) : undefined,
                start: pageState.analysisScope === "measures" ? pageState.measureStart : undefined,
                startBeat: pageState.analysisScope === "measures" ? pageState.measureStartBeat : undefined,
                end: pageState.analysisScope === "measures" ? pageState.measureEnd : undefined,
                endBeat: pageState.analysisScope === "measures" ? pageState.measureEndBeat : undefined,
            });

            const newNodes = pageState.selectedPerformances.map((performance, i) => ({
                id: i,
                label: performance.label
            }));

            const newLinks: { source: number; target: number; distance: number; }[] = [];
            for (let i = 0; i < result.n; i++) {
                for (let j = i + 1; j < result.n; j++) {
                    const distance = result.normalizedMatrix[i][j];
                    if (distance === null) continue;
                    newLinks.push({ source: i, target: j, distance });
                }
            }
            pageState.nodes = newNodes;
            pageState.links = newLinks;
            // The matrix keeps the refused pairs as nulls, which the links
            // cannot carry — the triangle shows them as gaps.
            pageState.matrix = result.normalizedMatrix;
            pageState.matrixLabels = newNodes.map(node => node.label ?? String(node.id));
            pageState.warnings = (result.warnings ?? []).map(w => ({
                pair: w.performances.map(p =>
                    pageState.allPerformances.find(a => a.path === p)?.label ?? p
                ),
                reasons: w.reasons
            }));

        } catch (e: any) {
            error = e.message;
            console.error(e);
        } finally {
            loading = false;
            graphFinished = true;
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
    <aside class="w-64 shrink-0 bg-base-200 p-4 flex flex-col gap-4 min-h-screen">
        {#if pageState.analysisScope == ""}
            <div class="card w-full bg-base-200 p-4 shadow-md gap-2 justify-start">
                <h2 class="card-title">Choose scope of analysis</h2>
                <button class="btn btn-primary" onclick={() => {pageState.analysisScope = "cycle"}}>Whole cycle</button>
                <button class="btn btn-primary" onclick={() => {pageState.analysisScope = "halfCycle"}}>Half cycle ("Abtheilung")</button>
                <button class="btn btn-primary" onclick={() => {pageState.analysisScope = "piece"}}>Single piece</button>
                <button class="btn btn-primary" onclick={() => {pageState.analysisScope = "measures"}}>Selected measures</button>
            </div>
            {:else}
            
            <button onclick={() => {pageState.analysisScope = ""}} class="btn btn-primary"> <p class="text-4xl">&lArr;</p> Change scope of analysis</button>
            
            {#if graphFinished}
            <div class="card w-full bg-base-200 p-4 shadow-md gap-2 justify-start">
                <button
                    class={`btn btn-block ${pageState.active === "network" ? "btn-primary" : "bg-base-300"}`}
                    onclick={() => (pageState.active = "network")}
                >Show network</button>
                <button
                    class={`btn btn-block ${pageState.active === "matrix" ? "btn-primary" : "bg-base-300"}`}
                    onclick={() => (pageState.active = "matrix")}
                >Show matrix</button>
            </div>
            {/if}

            <!-- Only the network is drawn from these; the matrix ignores them. -->
            {#if graphFinished && pageState.active === "network"}
            <div class="card w-full bg-base-200 p-4 shadow-md justify-start">
                <label>Node size
                    <input type="range" min="1" max="20" value={pageState.nodeSize} class="range range-s range-primary"
                    onchange={(e) => { pageState.nodeSize = Number(e.currentTarget.value)}}
                    oninput={(e) => {nodeSizeLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{nodeSizeLabel}</span>
                </label>
                <label>Link width
                    <input type="range" min="2" max="50" value={pageState.linkWidth} class="range range-s range-primary"
                    onchange={(e) => { pageState.linkWidth = Number(e.currentTarget.value)}}
                    oninput={(e) => {linkWidthLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{linkWidthLabel}</span>
                </label>
            </div>
            {/if}

            {#if pageState.analysisScope == "piece"}

                <div class="card w-full bg-base-200 p-4 shadow-md justify-start">
                    <ScoreSelector files={pageState.pieces} selectedFile={pageState.selectedPiece} onFileSelect={selectPiece} />
                    <ParameterMultiSelector bind:selectedParameters={pageState.selectedParameters} bind:weights={pageState.parameterWeights} metric={pageState.selectedMetric} />
                    <MetricSelector bind:selectedMetric={pageState.selectedMetric} />
                    <MultiplePerformancesSelector performances={pageState.allPerformances} selectedPerformances={pageState.selectedPerformances} onSelectionChange={handlePerformancesChange}/>
                </div>

            {:else if pageState.analysisScope == "cycle"}
                <ParameterMultiSelector bind:selectedParameters={pageState.selectedParameters} bind:weights={pageState.parameterWeights} metric={pageState.selectedMetric} />
                <MetricSelector bind:selectedMetric={pageState.selectedMetric} />
                <MultiplePerformancesSelector performances={pageState.allPerformances} selectedPerformances={pageState.selectedPerformances} onSelectionChange={handlePerformancesChange}/>

            {:else if pageState.analysisScope == "halfCycle"}
                <div class="flex gap-6 w-full">
                    <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                        <h2 class="card-title justify-center mb-2 ">Choose part of cycle</h2>
                        <button
                            class={`btn btn-block ${
                                pageState.ersteAbtheilung === true
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (pageState.ersteAbtheilung = true)}
                        >Erste Abtheilung (1-12)</button>
                        <button
                            class={`btn btn-block ${
                                pageState.ersteAbtheilung === false
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (pageState.ersteAbtheilung = false)}
                        >Zweite Abtheilung (13-24)</button>
                    </div>
                </div>
                <ParameterMultiSelector bind:selectedParameters={pageState.selectedParameters} bind:weights={pageState.parameterWeights} metric={pageState.selectedMetric} />
                <MetricSelector bind:selectedMetric={pageState.selectedMetric} />
                <MultiplePerformancesSelector performances={pageState.allPerformances} selectedPerformances={pageState.selectedPerformances} onSelectionChange={handlePerformancesChange}/>

            {:else if pageState.analysisScope == "measures"}
                <ScoreSelector files={pageState.pieces} selectedFile={pageState.selectedPiece} onFileSelect={selectPiece} />
                <MeasureRangeInput bind:start={pageState.measureStart} bind:startBeat={pageState.measureStartBeat} bind:end={pageState.measureEnd} bind:endBeat={pageState.measureEndBeat} />
                <ParameterMultiSelector bind:selectedParameters={pageState.selectedParameters} bind:weights={pageState.parameterWeights} metric={pageState.selectedMetric} />
                <MetricSelector bind:selectedMetric={pageState.selectedMetric} />
                <MultiplePerformancesSelector performances={pageState.allPerformances} selectedPerformances={pageState.selectedPerformances} onSelectionChange={handlePerformancesChange}/>
            {/if}

            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
            <button class="btn btn-primary" onclick={generateNetwork} type="submit" disabled={loading}>
                {#if loading}<span class="loading loading-spinner loading-sm"></span>{/if}
                Generate Network
            </button>


        {/if}
    </aside>

    <main class="flex-1 flex flex-col p-2 overflow-auto">
        {#if pageState.warnings.length > 0}
            <div class="alert alert-warning mb-4 flex-col items-start">
                <span class="font-semibold">
                    {pageState.warnings.length}
                    {pageState.warnings.length === 1 ? 'Paar wurde' : 'Paare wurden'}
                    nicht verglichen — die Aufnahmen decken sich nicht.
                </span>
                <ul class="text-sm list-disc pl-5">
                    {#each pageState.warnings as warning}
                        <li>
                            <span class="font-medium">{warning.pair.join(' / ')}:</span>
                            {warning.reasons.join('; ')}
                        </li>
                    {/each}
                </ul>
            </div>
        {/if}

        <div class="w-full h-full">
            {#if loading}
                <div class="flex items-center justify-center w-full h-[80vh]">
                    <span class="loading loading-spinner loading-lg"></span>
                </div>
            {:else if pageState.active === "matrix"}
                <DtwMatrix matrix={pageState.matrix} labels={pageState.matrixLabels} />
            {:else}
                <DtwNetwork links={pageState.links} nodes={pageState.nodes} bind:linkWidth={pageState.linkWidth} bind:nodeSize={pageState.nodeSize} />
            {/if}
        </div>
    </main>

</div>
