<script lang="ts">
    import { onMount } from 'svelte';
    import ScoreSelector from '$lib/components/ScoreSelector.svelte';
    import MeiViewer from '$lib/components/MeiViewer.svelte';
    
    type FileItem = {
        path: string;
        label: string;
        order?: number;
    };

    type AddData = {
        id: string;
        medium: string | null;
        type: string | null;
        label: string | null;
        unclearReason: string | null;
        x: number;
        y: number;

    }

    type NoteData = {
        id: string;
        pitch: string | null;
        octave: string | null;
        measure: string | null;
        x: number;
        y: number;
    };

    let files = $state<FileItem[]>([]);
    let notePopup = $state<NoteData | null>(null);
    let addPopup = $state<AddData | null>(null);
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

    function handleAddClick(data: AddData) {
        addPopup = data;
    }
    
    function handleNoteClick(data: NoteData) {
        notePopup = data;
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
            <MeiViewer src={meiContent} onNoteClick={handleNoteClick} onAddClick={handleAddClick}/>
        </div>
        {/if}
        
        {#if notePopup}
        <div
        class="popup"
        style="left: {notePopup.x}px; top: {notePopup.y}px;"
        >
        <strong>Note:</strong> {notePopup.pitch}{notePopup.octave}<br>
        <strong>Measure:</strong> {notePopup.measure}
        </div>
        {/if}

        {#if addPopup}
        <div
        class="popup"
        style="left: {addPopup.x}px; top: {addPopup.y}px;"
        >
        <strong style="text-decoration: underline;">Addition by Fischer-Dieskau</strong><br>
        <strong>Medium:</strong> {addPopup.medium}<br>
        <strong>Label:</strong> {addPopup.label}<br>
        <strong>Type:</strong> {addPopup.type}<br>
            {#if addPopup.unclearReason != null}
        <p>Unclear, {addPopup.unclearReason}</p>
            {/if}
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
