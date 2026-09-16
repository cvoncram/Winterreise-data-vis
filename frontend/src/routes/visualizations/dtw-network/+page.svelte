<script lang=ts>
    import * as d3 from "d3";
    import DtwNetwork from "$lib/components/containers/DtwNetwork.svelte";
    import DtwMatrix from "$lib/components/containers/DtwMatrix.svelte";
    import ScoreSelector from "$lib/components/partials/ScoreSelector.svelte";
    import MultiplePerformancesSelector from "$lib/components/partials/MultiplePerformancesSelector.svelte";
    import ParameterMultiSelector from "$lib/components/partials/ParameterMultiSelector.svelte";
    import MetricSelector from "$lib/components/partials/MetricSelector.svelte";
    import MeasureRangeInput from "$lib/components/partials/MeasureRangeInput.svelte";
    import CsvTable from "$lib/components/partials/CsvTable.svelte";
    import type { SongInfo, CyclePerformance } from "$lib/types";
    import { fetchAllPerformances, fetchPairAnalysis, fetchPieces, runDtwAnalysisStreamed } from "$lib/api";
    import type { AnalysisProgress, DtwAnalysisParams, DtwScope, PairAnalysisResult } from "$lib/api";
    import {onMount} from "svelte";
    import { dtwNetworkPageState as pageState } from "./pageState.svelte";

    let linkWidthLabel = $derived(pageState.linkWidth);
    let nodeSizeLabel = $derived(pageState.nodeSize);

    let error: string = $state("");
    let loading = $state(false);
    let graphFinished = $state(false);

    let progress: AnalysisProgress | null = $state(null);
    let progressStarted = 0;

    const stageLabel: Record<string, string> = {
        fetching: "Loading performance data",
        comparing: "Comparing recordings"
    };

    /**
     * Seconds left in the current step, from how long its steps have taken so
     * far. Fetching and comparing run at very different speeds, so the estimate
     * restarts when the step does.
     */
    let remainingSeconds = $derived.by(() => {
        if (!progress || progress.done < 3) return null;
        const elapsed = (Date.now() - progressStarted) / 1000;
        return Math.round((elapsed / progress.done) * (progress.total - progress.done));
    });

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

    /** The one description of the current selection, so that network and detail view cannot diverge. */
    function analysisParams(paths: string[]): DtwAnalysisParams {
        return {
            parameters: pageState.selectedParameters,
            metric: pageState.selectedMetric,
            weights: currentWeights(),
            paths,
            scope: pageState.analysisScope as DtwScope,
            piece: pageState.selectedPiece?.nbInOrder,
            half: pageState.analysisScope === "halfCycle" ? (pageState.ersteAbtheilung ? 1 : 2) : undefined,
            start: pageState.analysisScope === "measures" ? pageState.measureStart : undefined,
            startBeat: pageState.analysisScope === "measures" ? pageState.measureStartBeat : undefined,
            end: pageState.analysisScope === "measures" ? pageState.measureEnd : undefined,
            endBeat: pageState.analysisScope === "measures" ? pageState.measureEndBeat : undefined,
        };
    }

    /** Recordings without the metadata in question keep this. */
    const UNKNOWN_COLOUR = "#9ca3af";

    /**
     * Node colours and their key. Year gets a sequential scale because it is
     * an order, pianist and context a categorical one because they are not.
     */
    let nodeStyling = $derived.by(() => {
        const performances = pageState.selectedPerformances;
        const none = { colours: [] as string[], legend: [] as { label: string; colour: string }[] };
        if (pageState.colourBy === "none" || performances.length === 0) return none;

        if (pageState.colourBy === "year") {
            const years = performances.map(p => p.year ?? null);
            const known = years.filter((y): y is number => y != null);
            if (known.length === 0) return none;

            const [low, high] = [Math.min(...known), Math.max(...known)];
            const scale = d3.scaleSequential(d3.interpolateViridis).domain([low, high]);
            const ticks = low === high ? [low] : d3.ticks(low, high, 4);
            return {
                colours: years.map(y => (y == null ? UNKNOWN_COLOUR : scale(y))),
                legend: ticks.map(t => ({ label: String(t), colour: scale(t) }))
            };
        }

        const values = performances.map(p =>
            (pageState.colourBy === "pianist" ? p.pianist : p.recordingContext) ?? "unknown"
        );
        const distinct = [...new Set(values)].sort();
        const scale = d3.scaleOrdinal(d3.schemeTableau10).domain(distinct);
        return {
            colours: values.map(v => (v === "unknown" ? UNKNOWN_COLOUR : scale(v))),
            legend: distinct.map(v => ({ label: v, colour: v === "unknown" ? UNKNOWN_COLOUR : scale(v) }))
        };
    });

    let pairDialog: HTMLDialogElement;
    let pair: PairAnalysisResult | null = $state(null);
    let pairLabels: string[] = $state([]);
    let pairLoading = $state(false);
    let pairError = $state("");
    let sortByMargin = $state(true);

    const fmt = (v: number | null | undefined, digits = 3) => v == null ? "—" : v.toFixed(digits);

    /** What a higher value means, per parameter. */
    const direction: Record<string, string> = {
        tempo: "faster",
        dynamics: "louder",
        timbre: "brighter"
    };

    /** Pieces in the order the reader needs them: the least telling comparisons first. */
    let pairRows = $derived.by(() => {
        const rows = [...(pair?.pieces ?? [])];
        if (!sortByMargin) return rows;
        const margin = (r: typeof rows[number]) =>
            r.usable && r.tau?.combined != null && r.floor?.combined != null
                ? r.tau.combined - r.floor.combined : Number.POSITIVE_INFINITY;
        return rows.sort((a, b) => margin(a) - margin(b));
    });

    /** The unit each parameter is measured in before normalization. */
    const units: Record<string, { unit: string; digits: number }> = {
        tempo: { unit: "bpm", digits: 1 },
        dynamics: { unit: "dBFS", digits: 1 },
        timbre: { unit: "Hz", digits: 0 }
    };

    const unitOf = (parameter: string) => units[parameter]?.unit ?? "";

    /** Both recordings' mean measurement over the stretch, in their own unit. */
    function absolute(difference: { parameter: string; first: number | null; second: number | null }) {
        const digits = units[difference.parameter]?.digits ?? 2;
        if (difference.first == null || difference.second == null) return "—";
        return `${difference.first.toFixed(digits)} vs ${difference.second.toFixed(digits)} ${unitOf(difference.parameter)}`.trim();
    }

    /** Which recording reads higher, spelled out so that the exported file needs no key. */
    const higherIn = (difference: { value: number; parameter: string }) =>
        `${pairLabels[difference.value > 0 ? 0 : 1]} ${direction[difference.parameter] ?? "higher"}`;

    const margin = (row: { tau?: Record<string, number | null>; floor?: Record<string, number | null> }) =>
        row.tau?.combined != null && row.floor?.combined != null ? row.tau.combined - row.floor.combined : null;

    const differenceHeaders = ["Piece", "Title", "Parameter", "From", "To", "Higher",
                               "Difference (scale units)", "First (mean)", "Second (mean)", "Unit"];
    let differenceCsv = $derived.by(() => (pair?.differences ?? []).map(d =>
        [d.piece, d.title, d.parameter, d.from, d.to, higherIn(d), d.value, d.first, d.second, unitOf(d.parameter)]
    ));

    const pieceHeaders = ["Piece", "Title", "Tau", "Floor", "Tau minus floor", "Cost per beat",
                          "Off diagonal share", "Longest run", "Beats (first)", "Beats (second)", "Not compared"];
    let pieceCsv = $derived(pairRows.map(r =>
        [r.piece, r.title, r.tau?.combined ?? null, r.floor?.combined ?? null, margin(r),
         r.normalizedDistance ?? null, r.path?.offDiagonalShare ?? null, r.path?.longestRun ?? null,
         r.beats?.[0] ?? null, r.beats?.[1] ?? null, r.reason]
    ));

    const parameterHeaders = ["Parameter", "Tau", "Floor", "Difference"];
    let parameterCsv = $derived.by(() => {
        const row = pair?.pieces[0];
        if (!row) return [];
        return [...(pair?.parameters ?? []), "combined"].map(parameter => {
            const tau = row.tau?.[parameter] ?? null;
            const floor = row.floor?.[parameter] ?? null;
            return [parameter, tau, floor, tau != null && floor != null ? tau - floor : null];
        });
    });

    async function showPairDetails(source: number, target: number) {
        const performances = [source, target].map(i => pageState.selectedPerformances[i]);
        if (performances.some(p => !p)) return;

        pair = null;
        pairError = "";
        pairLabels = performances.map(p => p.label);
        pairLoading = true;
        pairDialog?.showModal();
        try {
            pair = await fetchPairAnalysis(analysisParams(performances.map(p => p.path)));
        } catch (e: any) {
            pairError = e.message;
            console.error(e);
        } finally {
            pairLoading = false;
        }
    }

    async function selectPiece(piece: SongInfo) {
        pageState.selectedPiece = piece;
    }

    function handlePerformancesChange(newSelection: CyclePerformance[]) {
        pageState.selectedPerformances = newSelection;
    }

    async function generateNetwork() {
        // Say why nothing happens, rather than returning in silence.
        if (!pageState.analysisScope) return;
        if (pageState.selectedPerformances.length === 0) {
            error = "Select at least one recording.";
            return;
        }
        if (pageState.selectedParameters.length === 0) {
            error = "Select at least one parameter.";
            return;
        }
        if ((pageState.analysisScope === "piece" || pageState.analysisScope === "measures") && !pageState.selectedPiece) {
            error = "Select a piece.";
            return;
        }

        error = "";
        loading = true;
        progress = null;
        progressStarted = Date.now();
        try {
            const result = await runDtwAnalysisStreamed(
                analysisParams(pageState.selectedPerformances.map(p => p.path)),
                update => {
                    // Each step has its own pace, so the estimate starts afresh with it.
                    if (progress?.stage !== update.stage) progressStarted = Date.now();
                    progress = update;
                }
            );

            const newNodes = pageState.selectedPerformances.map((performance, i) => ({
                id: i,
                label: performance.label
            }));

            const newLinks: { source: number; target: number; distance: number; cost: number; tau: number | null }[] = [];
            for (let i = 0; i < result.n; i++) {
                for (let j = i + 1; j < result.n; j++) {
                    const distance = result.normalizedMatrix[i][j];
                    if (distance === null) continue;
                    newLinks.push({ source: i, target: j, distance, cost: result.matrix[i][j] as number, tau: result.correlationMatrix[i][j] });
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
            progress = null;
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
                <label class="mt-2">Colour nodes by
                    <select class="select select-sm select-bordered w-full"
                        value={pageState.colourBy}
                        onchange={(e) => (pageState.colourBy = e.currentTarget.value as typeof pageState.colourBy)}>
                        <option value="none">nothing</option>
                        <option value="year">recording year</option>
                        <option value="pianist">pianist</option>
                        <option value="context">recording context</option>
                    </select>
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
                <div class="flex flex-col items-center justify-center w-full h-[80vh] gap-3">
                    {#if progress}
                        <progress class="progress progress-primary w-2/3" value={progress.done} max={progress.total}></progress>
                        <p class="text-sm">
                            {stageLabel[progress.stage] ?? progress.stage}: {progress.done} / {progress.total}
                            {#if remainingSeconds !== null}· about {remainingSeconds} s left in this step{/if}
                        </p>
                    {:else}
                        <progress class="progress progress-primary w-2/3"></progress>
                        <p class="text-sm">Starting…</p>
                    {/if}
                </div>
            {:else if pageState.active === "matrix"}
                <DtwMatrix matrix={pageState.matrix} labels={pageState.matrixLabels} onSelectPair={showPairDetails} />
            {:else}
                <DtwNetwork links={pageState.links} nodes={pageState.nodes} bind:linkWidth={pageState.linkWidth} bind:nodeSize={pageState.nodeSize} onMoreInfo={showPairDetails} nodeColours={nodeStyling.colours} legend={nodeStyling.legend} />
            {/if}
        </div>
    </main>

    <dialog bind:this={pairDialog} class="modal">
        <div class="modal-box max-w-4xl">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
            </form>
            <h3 class="text-lg font-bold">{pairLabels.join(" ⟷ ")}</h3>

            {#if pairLoading}
                <span class="loading loading-spinner loading-md mt-4"></span>
            {:else if pairError}
                <p class="text-error mt-4">{pairError}</p>
            {:else if pair}
                <p class="text-sm mt-2">
                    <span class="font-semibold">DTW cost</span> {fmt(pair.total.distance, 1)}
                    ({fmt(pair.total.normalizedDistance)} per beat) ·
                    <span class="font-semibold">Kendall's τ</span> {fmt(pair.total.tau)}
                    (floor {fmt(pair.total.floor)}) ·
                    {pair.total.beats} beats in {pair.total.piecesCompared}
                    {pair.total.piecesCompared === 1 ? "piece" : "pieces"}
                </p>
                <p class="text-xs opacity-70 mt-1">
                    The floor is what this music would yield without any real correspondence: the same
                    two series, one of them rotated. Only the distance between τ and the floor
                    carries information, and it cannot be compared between pieces.
                </p>

                {#if pair.differences.length > 0}
                    <div class="flex items-center justify-between mt-4 gap-4">
                        <h4 class="font-semibold">Largest differences</h4>
                        <CsvTable headers={differenceHeaders} rows={differenceCsv} filename="pair-differences" />
                    </div>
                    <p class="text-xs opacity-70">
                        Stretches of about eight beats, measured along the same path, in units of the
                        normalization's scale, at most ten per parameter. The parameters are listed separately because their scale
                        units do not mean the same thing. "Measured" gives both recordings' mean
                        over the same stretch in their own unit, in the order of the heading above.
                    </p>
                    <div class="overflow-x-auto max-h-80">
                        <table class="table table-sm table-pin-rows mt-1">
                            <thead>
                                <tr>
                                    <th>Piece</th>
                                    <th>Parameter</th>
                                    <th>Measures</th>
                                    <th>Higher</th>
                                    <th class="text-right">Difference</th>
                                    <th class="text-right">Measured</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each pair.differences as difference}
                                    <tr>
                                        <td>{difference.piece}. {difference.title}</td>
                                        <td>{difference.parameter}</td>
                                        <td>{difference.from ? `${difference.from}–${difference.to}` : "—"}</td>
                                        <td>{higherIn(difference)}</td>
                                        <td class="text-right">{Math.abs(difference.value).toFixed(2)}</td>
                                        <td class="text-right whitespace-nowrap">{absolute(difference)}</td>
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                {/if}

                {#if pair.pieces.length === 1 && pair.pieces[0].usable}
                    <!-- A single piece: the parameters are the interesting breakdown. -->
                    <div class="flex items-center justify-between mt-4 gap-4">
                        <h4 class="font-semibold">Correlation per parameter</h4>
                        <CsvTable headers={parameterHeaders} rows={parameterCsv} filename="pair-parameters" />
                    </div>
                    <table class="table table-sm mt-1">
                        <thead>
                            <tr><th>Parameter</th><th class="text-right">τ</th><th class="text-right">Floor</th><th class="text-right">Difference</th></tr>
                        </thead>
                        <tbody>
                            {#each [...pair.parameters, "combined"] as parameter}
                                {@const tau = pair.pieces[0].tau?.[parameter]}
                                {@const floor = pair.pieces[0].floor?.[parameter]}
                                <tr class={parameter === "combined" ? "font-semibold" : ""}>
                                    <td>{parameter}</td>
                                    <td class="text-right">{fmt(tau)}</td>
                                    <td class="text-right">{fmt(floor)}</td>
                                    <td class="text-right">{tau != null && floor != null ? fmt(tau - floor) : "—"}</td>
                                </tr>
                            {/each}
                        </tbody>
                    </table>
                    <p class="text-sm mt-2">
                        Beats: {pair.pieces[0].beats?.join(" vs ")} ·
                        path off the diagonal for {((pair.pieces[0].path?.offDiagonalShare ?? 0) * 100).toFixed(0)}%
                        of its steps, at most {pair.pieces[0].path?.maxOffset} beats,
                        longest unbroken stretch {pair.pieces[0].path?.longestRun} steps
                    </p>
                {:else}
                    <!-- A whole cycle: one figure hides which songs carry it. -->
                    <div class="flex items-center justify-between mt-4 gap-4">
                        <h4 class="font-semibold">Correlation per piece</h4>
                        <div class="flex gap-2">
                            <button class="btn btn-sm" onclick={() => (sortByMargin = !sortByMargin)}>
                                {sortByMargin ? "Sort by piece" : "Sort by τ − floor"}
                            </button>
                            <CsvTable headers={pieceHeaders} rows={pieceCsv} filename="pair-pieces" />
                        </div>
                    </div>
                    <div class="overflow-x-auto max-h-96">
                        <table class="table table-sm table-pin-rows mt-1">
                            <thead>
                                <tr>
                                    <th>Piece</th>
                                    <th class="text-right">τ</th>
                                    <th class="text-right">Floor</th>
                                    <th class="text-right">τ − floor</th>
                                    <th class="text-right">Cost per beat</th>
                                    <th class="text-right">Off diagonal</th>
                                </tr>
                            </thead>
                            <tbody>
                                {#each pairRows as row}
                                    {@const tau = row.tau?.combined}
                                    {@const floor = row.floor?.combined}
                                    <tr>
                                        <td>{row.piece}. {row.title}</td>
                                        {#if row.usable}
                                            <td class="text-right">{fmt(tau)}</td>
                                            <td class="text-right">{fmt(floor)}</td>
                                            <td class="text-right {tau != null && floor != null && tau - floor < 0.1 ? 'text-warning' : ''}">
                                                {tau != null && floor != null ? fmt(tau - floor) : "—"}
                                            </td>
                                            <td class="text-right">{fmt(row.normalizedDistance)}</td>
                                            <td class="text-right">{((row.path?.offDiagonalShare ?? 0) * 100).toFixed(0)}%</td>
                                        {:else}
                                            <td class="text-warning" colspan="5">not compared — {row.reason}</td>
                                        {/if}
                                    </tr>
                                {/each}
                            </tbody>
                        </table>
                    </div>
                    {#if pair.onlyFirst.length || pair.onlySecond.length}
                        <p class="text-sm text-warning mt-2">
                            Only in one of the two recordings:
                            {[...pair.onlyFirst, ...pair.onlySecond].join(", ")}
                        </p>
                    {/if}
                {/if}
            {/if}
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>

</div>
