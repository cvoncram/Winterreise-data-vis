<script lang="ts">
  import { onMount } from 'svelte';
  import ScoreSelector from '$lib/components/ScoreSelector.svelte';
  import MeiViewer from '$lib/components/MeiViewer.svelte';

  type FileItem = {
    path: string;
    label: string;
    order?: number;
  };
  
  let files: FileItem[] = [];
  let selectedFile: string | null = null;
  let meiContent: string | null = null;
  let error: string = '';
  
  async function fetchSelectedFile(file: string) {
    try {
      // IMPORTANT: backend expects `path`, not `filename`
      const res = await fetch(
      `/db/file?path=${encodeURIComponent(file)}`
      );
      
      if (!res.ok) throw new Error('Could not fetch MEI file');
      
      const data = await res.json();
      meiContent = data.content;  // this is the MEI string
      
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
  
  onMount(async () => {
    try {
      const res = await fetch('/db/scores-folder');
      if (!res.ok) throw new Error('Could not fetch file list');
      const data = await res.json();
      
      files = data; // <-- convert object keys to array

    } catch (e: any) {
      error = e.message;
      console.error(e);
    }
  });
  
</script>

<div class="flex flex-col gap-6 p-4">
  
  <div class="card bg-base-200 p-4 shadow-md">
    <ScoreSelector
    {files}
    {selectedFile}
    onFileSelect={handleFileSelect}
    />
    {#if error}
    <p class="text-error mt-2">{error}</p>
    {/if}
  </div>
  
  {#if meiContent}
  <div class="card bg-base-100 p-4 shadow-md">
    <MeiViewer src={meiContent} />
  </div>
  {/if}
  
</div>

<style>
  .card > :global(.flex) {
    flex-wrap: wrap;
  }
</style>
