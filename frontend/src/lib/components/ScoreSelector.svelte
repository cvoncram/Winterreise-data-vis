<script lang="ts">
  export let folder: string = '';
  export let files: string[] = [];
  export let selectedFile: string | null = null;

  export let onFolderChange: (folder: string) => void;
  export let onFileSelect: (file: string) => void;
</script>

<div class="flex justify-center w-full mt-2">
  <label class="label w-full flex flex-col items-center"> tbd
  <!-- Row wrapper -->
  <div class="flex gap-3 max-w-4xl w-full">
    
    <!-- Folder box -->
    <div class="flex-1 bg-base-100 p-2 rounded-lg shadow flex flex-col justify-center items-center">
      <label class="label w-full flex flex-col items-center">
        <span class="label-text mb-2 text-lg font-semibold">Select folder</span>
        <input
          type="text"
          class="input input-bordered w-full"
          placeholder="/home/user/Desktop/Scores"
          bind:value={folder}
          on:input={() => onFolderChange(folder)}
        />
      </label>
    </div>

    <!-- File selector box -->
    <div class="flex-1 bg-base-100 p-2 rounded-lg shadow flex flex-col justify-center items-center">
      <label class="label w-full flex flex-col items-center">
        <span class="label-text mb-2 text-lg font-semibold">Select MEI file</span>
        <select
          class="select select-bordered w-full"
          bind:value={selectedFile}
          on:change={(e) => onFileSelect((e.target as HTMLSelectElement).value)}
          disabled={folder === '' || files.length === 0}
        >
          {#each files as file}
            <option value={file}>{file}</option>
          {/each}
        </select>
      </label>
    </div>

  </div>
  </label>
</div>
