<script lang="ts">
  export let files: string[] = [];
  export let selectedFile: string | null = null;
  export let onFileSelect: (file: string) => void;

  // Auto-select first file when files arrive
  $: if (files.length > 0 && !selectedFile) {
    selectedFile = files[0];
    onFileSelect(selectedFile);
  }
</script>

<div class="flex justify-center w-full mt-4">
  <div class="flex gap-6 max-w-4xl w-full flex-wrap">

    <div class="flex-1 bg-base-100 p-4 rounded-lg shadow flex flex-col justify-center items-center overflow-visible">
      <label class="label w-full flex flex-col items-center">
        <span class="label-text mb-2 text-lg font-semibold">Select MEI file</span>
        <select
          class="select select-bordered w-full"
          bind:value={selectedFile}
          on:change={(e) => onFileSelect((e.target as HTMLSelectElement).value)}
          disabled={files.length === 0}
        >
          {#each files as file}
            <option value={file}>{file}</option>
          {/each}
        </select>
      </label>
    </div>

  </div>
</div>
