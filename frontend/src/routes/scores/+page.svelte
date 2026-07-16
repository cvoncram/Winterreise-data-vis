<script lang="ts">
    import { onMount } from 'svelte';
    import ScoreSelector from '$lib/components/partials/ScoreSelector.svelte';
    import MeiViewer from '$lib/components/containers/MeiViewer.svelte';
    import type {SongInfo} from "$lib/types"; 

    let files = $state<SongInfo[]>([]);
    let selectedFile = $state<SongInfo | null>(null);
    let meiContent = $state<string | null>(null);
    let error = $state<string>('');

    let scale = $state(40);
    let spacingPercent = $state(25);
    let pageWidth = $state(1400);
    let pageHeight = $state(600);

    let scaleLabel = $derived(scale);
    let spacingPercentLabel = $derived(spacingPercent);
    let pageWidthLabel = $derived(pageWidth);
    let pageHeightLabel = $derived(pageHeight);

    let meiViewer = $state<ReturnType<typeof MeiViewer>>();

    async function fetchSelectedFile(file: SongInfo) {
        try {
            const res = await fetch(
            `/db/file?path=${encodeURIComponent(file.path)}`
            );
            
            if (!res.ok) throw new Error('Could not fetch MEI file');
            
            const data = await res.text();
            meiContent = data; 
            
        } catch (e: any) {
            error = e.message;
            console.error(e);
            meiContent = null;
        }
    }  
    
    function handleFileSelect(file: SongInfo) {
        selectedFile = file;
        fetchSelectedFile(file);
    }
    
    onMount(async () => {
        try {
            const res = await fetch('/db/scores-folder');
            if (!res.ok) throw new Error('Could not fetch file list');
            const data = await res.json();
            
            files = data;
            
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    });
    
</script>
<span class="label-text mb-2 text-lg font-semibold">Change appearance</span>
<div class="flex">
    <div class="fixed top-0 left-0 h-full w-64 bg-base-200 p-4 flex flex-col justify-center items-center gap-4 z-10">
        
        <div class="card bg-base-200 p-4 gap-4 shadow-md justify-start">
            <ScoreSelector
            {files}
            selectedFile={selectedFile}
            onFileSelect={handleFileSelect}
            />
            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
            {#if meiContent}
            <div class="bg-base-100 gap-4 p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                <span class="label-text mb-2 text-lg font-semibold">Change size and appearance</span>
                <label>Scale (percent):
                    <input type="range" min="10" max="80" value={scale} class="range range-s range-primary"
                    onchange={(e) => { scale = Number(e.currentTarget.value); meiViewer?.doLayout();}}
                    oninput={(e) => {scaleLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{scaleLabel}</span>
                </label>
                <label>Spacing (percent):
                    <input type="range" min="1" max="100" value={spacingPercent} class="range range-s range-primary"
                    onchange={(e) => { spacingPercent = Number(e.currentTarget.value); meiViewer?.doLayout();}}
                    oninput={(e) => {spacingPercentLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{spacingPercentLabel}</span>
                </label>
                <label>Page width (pixels):
                    <input type="range" min="400" max="1600" value={pageWidth} class="range range-s range-primary"
                    onchange={(e) => { pageWidth = Number(e.currentTarget.value); meiViewer?.doLayout();}}
                    oninput={(e) => {pageWidthLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{pageWidthLabel}</span>
                </label>
                <label>Minimum page height (pixels):
                    <input type="range" min="300" max="4000" value={pageHeight} class="range range-s range-primary"
                    onchange={(e) => { pageHeight = Number(e.currentTarget.value); meiViewer?.doLayout();}}
                    oninput={(e) => {pageHeightLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{pageHeightLabel}</span>
                </label>
            </div>
            {/if}
        </div>

    </div>

    <div class="ml-64 p-4">
        
        {#if meiContent}
        <div class="card bg-base-100 p-4 shadow-md">
            <MeiViewer bind:this={meiViewer} src={meiContent} bind:scale bind:spacingPercent bind:pageWidth bind:pageHeight/>
        </div>
        {/if}

    </div>
    
</div>

<style>
    .card > :global(.flex) {
        flex-wrap: wrap;
    }
</style>
