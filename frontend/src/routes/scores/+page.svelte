<script lang="ts">
  import ScoreSelector from '$lib/components/ScoreSelector.svelte';
  import MeiViewer from '$lib/components/MeiViewer.svelte';

  // Folder path typed by the user
  let folder: string = '';

  // List of MEI files returned by backend
  let files: string[] = [];

  // Currently selected file
  let selectedFile: string | null = null;

  // Error messages
  let error: string = '';

  // Compute the MEI source URL for the viewer
  $: meiSrc = selectedFile
    ? `/api/scores/file?folder=${encodeURIComponent(folder)}&filename=${encodeURIComponent(selectedFile)}`
    : null;

  // Handler for when folder input changes
  async function handleFolderChange(f: string) {
    folder = f;
    files = [];
    selectedFile = null;
    error = '';

    if (!folder) return;

    try {
      const res = await fetch(`/api/scores?folder=${encodeURIComponent(folder)}`);
      if (!res.ok) throw new Error('Folder not found');
      files = await res.json();
      if (files.length > 0) selectedFile = files[0];
    } catch (e: any) {
      error = e.message;
      console.error(e);
    }
  }

  // Handler for when file is selected from dropdown
  function handleFileSelect(f: string) {
    selectedFile = f;
  }
</script>

<div class="flex flex-col gap-6 p-4">

  <!-- Folder + File Selector -->
  <div class="card bg-base-200 p-4 shadow-md">
    

    <ScoreSelector
      {folder}
      {files}
      selectedFile={selectedFile}
      onFolderChange={handleFolderChange}
      onFileSelect={handleFileSelect}
    />

    {#if error}
      <p class="text-error mt-2">{error}</p>
    {/if}
  </div>

  <!-- MEI Viewer -->
  {#if meiSrc}
    <div class="card bg-base-100 p-4 shadow-md">
      <MeiViewer src={meiSrc} />
    </div>
  {/if}

</div>

<style>
  /* Optional: make the row wrap on smaller screens */
  .card > :global(.flex) {
    flex-wrap: wrap;
  }
</style>
