<script lang="ts">
    import { onMount } from 'svelte';
    import PerformanceSelector from '$lib/components/partials/PerformanceSelector.svelte';
    import ScoreSelector from '$lib/components/partials/ScoreSelector.svelte';
    import MeiTable from '$lib/components/containers/MeiTable.svelte';
    import MeiCircularRibbon from '$lib/components/containers/MeiCircularRibbon.svelte';
    import type { PerformanceRow, PerformanceMetadata, SongInfo, CyclePerformance } from '$lib/types';

    let recordings = $state<CyclePerformance[]>([]);
    let selectedRecording = $state<CyclePerformance | null>(null);

    let pieces = $state<SongInfo[]>([]);
    let selectedPiece = $state<SongInfo | null>(null);

    let metadata = $state<PerformanceMetadata | null>(null);

    let tableRows = $state<PerformanceRow[]>([]);
    let error = $state('');
    let active = $state("visualization");

    let brushEnabled = $state(false);
    let selectedColorDropdown: string = $state("viridisScheme");
    let displayedRows = $state<PerformanceRow[]>([]);
    let chart: any = $state();

    onMount(async () => {
        try {
            const res = await fetch('/db/performances');
            if (!res.ok) throw new Error('Could not fetch recordings');
            recordings = await res.json();
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    });

    async function handleRecordingSelect(recording: CyclePerformance) {
        selectedRecording = recording;
        pieces = [];
        selectedPiece = null;
        tableRows = [];

        try {
            const res = await fetch(`/db/performance-files?performance=${encodeURIComponent(recording.path)}`);
            if (!res.ok) throw new Error('Could not fetch pieces for recording');
            pieces = await res.json();
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }

    async function handlePieceSelect(piece: SongInfo) {
        selectedPiece = piece;
        tableRows = [];
        displayedRows = [];  // reset here
        error = '';

        try {
            const res = await fetch(`/db/parsed-file?path=${encodeURIComponent(piece.path)}`);
            if (!res.ok) throw new Error('Could not fetch parsed MEI data');

            const data = await res.json();
            metadata = data[0]?.metadata ?? null;
            tableRows = data[1]?.data ?? [];
            displayedRows = [...tableRows]; 
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }
</script>

<div class="flex h-auto overflow-hidden">

    <aside class="w-64 shrink-0 bg-base-200 p-4 flex flex-col gap-4">
        {#if error}
            <p class="text-error">{error}</p>
        {/if}

        <div class="card w-full">
            <PerformanceSelector
                {recordings}
                selectedRecording={selectedRecording}
                onSelect={handleRecordingSelect}
            />
        </div>

        {#if selectedRecording && pieces.length > 0}
            <div class="card w-full">
                <ScoreSelector
                    files={pieces}
                    selectedFile={selectedPiece}
                    onFileSelect={handlePieceSelect}
                />
            </div>
        {/if}
        {#if selectedPiece}
            <div class="flex w-full justify-start">
                <div class="flex gap-6 w-full">
                    <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                        <button 
                            class={`btn btn-block ${
                                active === "visualization"
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (active = "visualization")}
                        >
                            Show visualization
                        </button>
                    
                        <button
                            class={`btn btn-block ${
                                active === "table"
                                    ? "btn-primary"
                                    : "bg-base-300"
                            }`}
                            onclick={() => (active = "table")}
                        >
                            Show data table
                        </button>
                    </div>
                </div>
            </div>
            <div class="bg-base-100 w-full p-4 rounded-lg shadow flex flex-col overflow-visible">
                <h2 class="card-title justify-center">Display options</h2>
                <label>
                    <h3 class="mt-2 text-l">Color scheme</h3>
                    <select
                        class="select select-bordered w-full"
                        bind:value={selectedColorDropdown}>
                        <option value="viridisScheme">Viridis (default)</option>
                        <option value="infernoScheme">Inferno</option>
                        <option value="cividisScheme">Cividis</option>
                        <option value="bluesScheme">Blue shades</option>
                        <option value="greensScheme">Green shades</option>
                        <option value="redsScheme">Red shades</option>
                    </select>
                </label>

                <button class={`btn btn-sm btn-block mt-4 ${brushEnabled? "bg-base-300" : "btn-primary"}`}
                    onclick={() => {
                        brushEnabled = false;
                        chart.clearSelection();
                    }}
                >Select single beat</button>

                <button class={`btn btn-sm btn-block ${brushEnabled ? "btn-primary" : "bg-base-300"}`}
                    onclick={() => {
                        brushEnabled = true;
                        chart.clearSelection();
                    }}
                >Draw selection of beats</button>
            </div>
        {/if}
        {#if displayedRows.length < tableRows.length}
            <button class="btn btn-block btn-sm mt-2 btn-info" onclick={() => {
                displayedRows = [...tableRows];
                chart.clearSelection();
            }}>
                Back to complete performance
            </button>
        {/if}        
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">
        <div class="flex-1 relative p-6 overflow-auto mb-12">
            {#if active === "visualization"}

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
                    bind:brushEnabled
                    bind:selectedColorDropdown
                    bind:displayedRows
                    metadata={metadata}
                />

            {:else if active === "table"}
                <MeiTable rows={tableRows} />
            {/if}
        </div>
    </main>
</div>