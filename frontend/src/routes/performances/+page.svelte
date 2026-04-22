<script lang="ts">
    import { onMount } from 'svelte';
    import PerformanceSelector from '$lib/components/PerformanceSelector.svelte';
    import ScoreSelector from '$lib/components/ScoreSelector.svelte';
    import MeiTable from '$lib/components/MeiTable.svelte';
    import MeiRibbon from '$lib/components/MeiRibbon.svelte';
    import type { PerformanceRow } from '$lib/components/MeiTable.svelte';

    type FileItem = { path: string; label: string; order?: number };

    let recordings: FileItem[] = [];
    let selectedRecording: string | null = null;

    let pieces: FileItem[] = [];
    let selectedPiece: string | null = null;

    let tableRows: PerformanceRow[] = [];
    let error = '';
    let active = "table";

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

    async function handleRecordingSelect(path: string) {
        selectedRecording = path;
        pieces = [];
        selectedPiece = null;
        tableRows = [];

        try {
            const res = await fetch(`/db/performance-files?performance=${encodeURIComponent(path)}`);
            if (!res.ok) throw new Error('Could not fetch pieces for recording');
            pieces = await res.json();
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }

    async function handlePieceSelect(path: string) {
        selectedPiece = path;
        tableRows = [];
        error = '';

        try {
            const res = await fetch(`/db/parsed-file?path=${encodeURIComponent(path)}`);
            if (!res.ok) throw new Error('Could not fetch parsed MEI data');

            const data = await res.json();

            tableRows = data.data;

        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }
</script>

<div class="flex">
    <div>
        <div class="fixed top-0 left-0 h-full w-64 bg-base-200 p-4 flex flex-col justify-center items-center gap-4 z-10">
            {#if error}
            <p class="text-error">{error}</p>
            {/if}
            <div class="card bg-base-200 p-4 shadow-md justify-start">        
                <PerformanceSelector
                {recordings}
                selectedRecording={selectedRecording}
                onSelect={handleRecordingSelect}
                />
            </div>       
            
            {#if selectedRecording && pieces.length > 0}
            <div class="card bg-base-200 p-4 shadow-md justify-start">        
                <ScoreSelector
                files={pieces}
                selectedFile={selectedPiece}
                onFileSelect={handlePieceSelect}
                />
            </div>
            {/if}
        </div>
    </div>

    
    <div class="p-6">
        {#if active === "table"}
        <div class="ml-64 p-4">
            <MeiTable rows={tableRows} />
        </div>

        {:else if active === "visualization"}
        <div class="ml-64 p-4">
        <MeiRibbon rows={tableRows} />
        </div>
        {/if}
    </div>

    <!-- Dock (bottom navigation) -->
    <div class="dock dock-xs" style="border-top: 1px solid #e2e8f0; background-color: rgb(216 222 233);">
    <button
        class:dock-active={active === "table"}
        on:click={() => (active = "table")}
    >Table</button>

    <button
        class:dock-active={active === "visualization"}
        on:click={() => (active = "visualization")}
    >Visualization</button>
    </div>

</div>