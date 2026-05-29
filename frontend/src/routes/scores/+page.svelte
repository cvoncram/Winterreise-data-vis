<script lang="ts">
    import { onMount } from 'svelte';
    import ScoreSelector from '$lib/components/partials/ScoreSelector.svelte';
    import MeiViewer from '$lib/components/containers/MeiViewer.svelte';
    import type {SongInfo} from "$lib/types"   

    let files = $state<SongInfo[]>([]);
    let selectedFile = $state<SongInfo | null>(null);
    let meiContent = $state<string | null>(null);
    let error = $state<string>('');
    
    async function fetchSelectedFile(file: SongInfo) {
        try {
            const res = await fetch(
            `/db/file?path=${encodeURIComponent(file.path)}`
            );
            
            if (!res.ok) throw new Error('Could not fetch MEI file');
            
            const data = await res.json();
            meiContent = data.content; 
            
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

<div class="flex">
    <div class="fixed top-0 left-0 h-full w-64 bg-base-200 p-4 flex flex-col justify-center items-center gap-4 z-10">
        
        <div class="card bg-base-200 p-4 shadow-md justify-start">
            <ScoreSelector
            {files}
            selectedFile={selectedFile}
            onFileSelect={handleFileSelect}
            />
            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
        </div>

    </div>

    <div class="ml-64 p-4">
        
        {#if meiContent}
        <div class="card bg-base-100 p-4 shadow-md">
            <MeiViewer src={meiContent}/>
        </div>
        {/if}

    </div>
    
</div>

<style>
    .card > :global(.flex) {
        flex-wrap: wrap;
    }
</style>
