<script lang="ts">
  type FileItem = {
    path: string;
    label: string;
    order?: number;
  };

  export let recordings: FileItem[] = [];
  export let selectedRecording: string | null = null;
  export let onSelect: (recording: string) => void;

  // Auto-select first recording when list arrives
  $: if (recordings.length > 0 && !selectedRecording) {
    selectedRecording = recordings[0].path;
    onSelect(selectedRecording);
  }
</script>

<div class="flex w-full mt-4 justify-start">
  <div class="flex gap-6 max-w-4xl w-full">
    <div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
      <label class="label w-full flex flex-col items-center">
        <span class="label-text mb-2 text-lg font-semibold">Select performance</span>
        <select
          class="select select-bordered w-full"
          bind:value={selectedRecording}
          on:change={(e) => onSelect(e.currentTarget.value)}
          disabled={recordings.length === 0}
        >
          {#each recordings as rec}
            <option value={rec.path}>{rec.label}</option>
          {/each}
        </select>
      </label>
    </div>
  </div>
</div>