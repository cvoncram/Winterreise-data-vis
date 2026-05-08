<script lang="ts">
    import { onMount } from 'svelte';
    import PerformanceSelector from '$lib/components/PerformanceSelector.svelte';
    import ScoreSelector from '$lib/components/ScoreSelector.svelte';
    import MeiTable from '$lib/components/MeiTable.svelte';
    import MeiCircularRibbon from '$lib/components/MeiCircularRibbon.svelte';
    import type { PerformanceRow, PerformanceMetadata } from '$lib/components/MeiTable.svelte';

    type FileItem = { path: string; label: string; order?: number };

    let recordings: FileItem[] = [];
    let selectedRecording: string | null = null;

    let pieces: FileItem[] = [];
    let selectedPiece: string | null = null;

    let metadata: PerformanceMetadata | null = null;

    let tableRows: PerformanceRow[] = [];
    let error = '';
    let active = "visualization";

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

            metadata = data[0]?.metadata ?? null;
            tableRows = data[1]?.data ?? [];

        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }
</script>

<div class="flex h-screen overflow-hidden">

    <aside class="w-64 shrink-0 bg-base-200 p-4 flex flex-col gap-4 justify-center">
        {#if error}
            <p class="text-error">{error}</p>
        {/if}

        <div class="card bg-base-200 p-4 shadow-md">
            <PerformanceSelector
                {recordings}
                selectedRecording={selectedRecording}
                onSelect={handleRecordingSelect}
            />
        </div>

        {#if selectedRecording && pieces.length > 0}
            <div class="card bg-base-200 p-4 shadow-md">
                <ScoreSelector
                    files={pieces}
                    selectedFile={selectedPiece}
                    onFileSelect={handlePieceSelect}
                />
            </div>
        {/if}
    </aside>

    <main class="flex-1 flex flex-col overflow-hidden">

        <div class="flex-1 relative p-6 overflow-auto mb-12">
            {#if active === "table"}
                <MeiTable rows={tableRows} />
            {:else if active === "visualization"}
                <MeiCircularRibbon
                    rows={tableRows}
                    metadata={metadata}
                />
            {/if}
        </div>

        <div
            class="dock dock-xs shrink-0"
            style="border-top: 1px solid #e2e8f0; background-color: rgb(216 222 233);"
        >
            <button
                class:dock-active={active === "visualization"}
                on:click={() => (active = "visualization")}
            >
                Visualization
            </button>

            <button
                class:dock-active={active === "table"}
                on:click={() => (active = "table")}
            >
                Table
            </button>
        </div>

    </main>

</div>