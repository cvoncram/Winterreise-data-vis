<script lang="ts">
    import { onMount } from 'svelte';
    import ScoreSelector from '$lib/components/ScoreSelector.svelte';
    import MeiViewer from '$lib/components/MeiViewer.svelte';
    
    type FileItem = {
        path: string;
        label: string;
        order?: number;
    };

    type NoteData = {
        id: string;
        pitch: string | null;
        octave: string | null;
        measure: string | null;
        x: number;
        y: number;
    };

    let files = $state<FileItem[]>([]);
    let popup = $state<NoteData | null>(null);
    let selectedFile = $state<string | null>(null);
    let meiContent = $state<string | null>(null);
    let error = $state<string>('');
    
    async function fetchSelectedFile(file: string) {
        try {
            const res = await fetch(
            `/db/file?path=${encodeURIComponent(file)}`
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
    
    function handleFileSelect(file: string) {
        selectedFile = file;
        fetchSelectedFile(file);
    }
    
    function handleNoteClick(data: NoteData) {
        popup = data;
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
            {selectedFile}
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
            <MeiViewer src={meiContent} onNoteClick={handleNoteClick}/>
        </div>
        {/if}
        
        {#if popup}
        <div
        class="popup"
        style="left: {popup.x}px; top: {popup.y}px;"
        >
        <strong>Note:</strong> {popup.pitch}{popup.octave}<br>
        <strong>Measure:</strong> {popup.measure}
        </div>
        {/if}

    </div>
    
</div>

<style>
    .card > :global(.flex) {
        flex-wrap: wrap;
    }
    
    .popup {
        position: fixed;
        background: white;
        border: 1px solid black;
        padding: 0.5rem;
        font-size: 0.9rem;
        pointer-events: none;
    }
</style>
