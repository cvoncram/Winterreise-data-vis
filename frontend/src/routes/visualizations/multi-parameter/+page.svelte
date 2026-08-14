<script lang="ts">
    import { onMount } from 'svelte';
    import PerformanceSelector from '$lib/components/partials/PerformanceSelector.svelte';
    import ScoreSelector from '$lib/components/partials/ScoreSelector.svelte';
    import MeiTable from '$lib/components/containers/MeiTable.svelte';
    import MeiCircularRibbon from '$lib/components/containers/MeiCircularRibbon.svelte';
    import ColorSchemeSelector from '$lib/components/partials/ColorSchemeSelector.svelte';
    import type { SongInfo, CyclePerformance } from '$lib/types';
    import { selection } from "$lib/selection.svelte";
    import { display } from "$lib/displaySettings.svelte";
    import { fetchNormalizationReference } from "$lib/api";
    import { multiParameterPageState as pageState } from "./pageState.svelte";

    let error = $state('');
    let loading = $state(false);

    let chart: any = $state();

    onMount(async () => {
        if (pageState.recordings.length > 0) return;
        try {
            const res = await fetch('/db/performances');
            if (!res.ok) throw new Error('Could not fetch recordings');
            pageState.recordings = await res.json();
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    });

    async function handleRecordingSelect(recording: CyclePerformance) {
        pageState.selectedRecording = recording;
        pageState.pieces = [];
        pageState.selectedPiece = null;
        pageState.tableRows = [];

        try {
            const res = await fetch(`/db/performance-files?performance=${encodeURIComponent(recording.path)}`);
            if (!res.ok) throw new Error('Could not fetch pieces for recording');
            const piecesList = await res.json();
            pageState.pieces = piecesList.map((p: any) => ({
                label: p.label,
                nbInOrder: p.order,
                path: p.path
            }));
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }

    async function handlePieceSelect(piece: SongInfo) {
        pageState.selectedPiece = piece;
        pageState.tableRows = [];
        pageState.displayedRows = [];  // reset here
        pageState.normalizationReference = null;
        error = '';
        loading = true;

        try {
            const res = await fetch(`/db/parsed-file?path=${encodeURIComponent(piece.path)}`);
            if (!res.ok) throw new Error('Could not fetch parsed MEI data');

            const data = await res.json();
            pageState.metadata = data[0]?.metadata ?? null;
            pageState.tableRows = data[1]?.data ?? [];
            pageState.displayedRows = [...pageState.tableRows];

            if (pageState.selectedRecording) {
                pageState.normalizationReference = await fetchNormalizationReference(pageState.selectedRecording.path, piece.nbInOrder);
            }
        } catch (e: any) {
            error = e.message;
            console.error(e);
        } finally {
            loading = false;
        }
        selection.piecePath = piece.path;

    }
</script>

<div class="flex h-auto overflow-hidden">

    <aside class="w-64 shrink-0 bg-base-200 p-4 flex flex-col gap-4">
        {#if error}
            <p class="text-error">{error}</p>
        {/if}

        <div class="card w-full">
            <PerformanceSelector
                recordings={pageState.recordings}
                selectedRecording={pageState.selectedRecording}
                onSelect={handleRecordingSelect}
            />
        </div>

        {#if pageState.selectedRecording && pageState.pieces.length > 0}
            <div class="card w-full">
                <ScoreSelector
                    files={pageState.pieces}
                    selectedFile={pageState.selectedPiece}
                    onFileSelect={handlePieceSelect}
                />
            </div>
        {/if}
        {#if pageState.selectedPiece}
            <div class="flex w-full justify-start">
                <div class="flex gap-6 w-full">
                    <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                        <button
                            class={`btn btn-block ${
                                pageState.active === "visualization"
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (pageState.active = "visualization")}
                        >
                            Show visualization
                        </button>

                        <button
                            class={`btn btn-block ${
                                pageState.active === "table"
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (pageState.active = "table")}
                        >
                            Show data table
                        </button>
                    </div>
                </div>
            </div>
            <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col overflow-visible">
                <h2 class="card-title justify-center">Display options</h2>
                <ColorSchemeSelector bind:selectedColorDropdown={display.colorScheme} />

                <button class={`btn btn-sm btn-block mt-4 ${pageState.brushEnabled ? "bg-base-300" : "btn-primary"}`}
                    onclick={() => {
                        pageState.brushEnabled = false;
                        chart.clearSelection();
                    }}
                >Select single beat</button>

                <button class={`btn btn-sm btn-block ${pageState.brushEnabled ? "btn-primary" : "bg-base-300"}`}
                    onclick={() => {
                        pageState.brushEnabled = true;
                        chart.clearSelection();
                    }}
                >Draw selection of beats</button>
            </div>
        {/if}
        {#if pageState.displayedRows.length < pageState.tableRows.length}
            <button class="btn btn-block btn-sm mt-2 btn-info" onclick={() => {
                pageState.displayedRows = [...pageState.tableRows];
                chart.clearSelection();
            }}>
                Back to complete performance
            </button>
        {/if}
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">
        <div class="flex-1 relative p-6 overflow-auto mb-12">
            {#if loading}
                <div class="flex items-center justify-center w-full h-[80vh]">
                    <span class="loading loading-spinner loading-lg"></span>
                </div>
            {:else if pageState.active === "visualization"}

                <!-- INFORMATION -->
                <div class="relative bg-base-200 max-w-[70vw] p-4 left-1/2 -translate-x-1/2 rounded-xl shadow-s grid grid-cols-2 gap-4">
                    <div>
                        <h3 class="card-title">How to read this visualization</h3>
                        <p>This graph visualizes three different parameters of performance data. Each slab represents one marked beat.</p>
                        <ol class="list-decimal pl-6">
                            <li>The <u>tempo</u> of the beat determines the size of the slab's <b>angle</b>, i.e. a "thicker" slab denotes a longer/slower performed beat.</li>
                            <li>The <u>dynamics</u> value of the beat decides the <b>length</b> of a slab; a longer slab is louder than a shorter slab.</li>
                            <li>The <b>color</b> of a slab represents the detected <u>spectral centroid</u> of the beat. A lighter color denotes a higher value, i.e. a
                                "brighter" perceived sound.</li>
                        </ol>
                    </div>
                    <div>
                        <h3 class="card-title">How to use this tool</h3>
                        <p>If you find a different color scheme than the default <i>Viridis</i> scheme more helpful, you may choose among several options in the upper
                            left corner.</p>
                        <p>Clicking on a slab shows information about the according beat.</p>
                        <p>You can select multiple beats by means of drag and drop.</p>
                    </div>
                </div>

                <MeiCircularRibbon
                    bind:this = {chart}
                    bind:brushEnabled={pageState.brushEnabled}
                    bind:selectedColorDropdown={display.colorScheme}
                    bind:displayedRows={pageState.displayedRows}
                    metadata={pageState.metadata}
                    normalizationReference={pageState.normalizationReference}
                />

            {:else if pageState.active === "table"}
                <MeiTable rows={pageState.tableRows} />
            {/if}
        </div>
    </main>
</div>
