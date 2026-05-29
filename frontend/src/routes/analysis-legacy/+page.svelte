<script lang="ts" >

    import { onMount } from 'svelte';
    import PerformanceSelector from '$lib/components/partials/PerformanceSelector.svelte';
    import ScoreSelector from '$lib/components/partials/ScoreSelector.svelte';
    import type { CyclePerformance, PerformanceRow, SongInfo} from '$lib/types';
    import MeiRibbon from '$lib/components/unused/MeiRibbon.svelte';

    let recordings: CyclePerformance[] = [];
    let selectedRecording: string | null = null;

    let pieces: SongInfo[] = [];
    let selectedPiece: string | null = null;

    let tableRows: PerformanceRow[] = [];
    let error = '';

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

            tableRows = data[1]?.data ?? [];

        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }

</script>


<div class="flex">
    <aside class="w-64 h-screen sticky top-0 bg-base-200 p-4 flex flex-col gap-4 justify-center">
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
    </aside>    
    <main class="flex-1">
        <div class="h-[90vh] w-full p-6">
            <MeiRibbon rows={tableRows} />
        </div>
    </main> 

</div>

