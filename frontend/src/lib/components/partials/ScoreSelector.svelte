<script lang="ts">
	import type {SongInfo} from "$lib/types"
	
	let { files, selectedFile, onFileSelect}:
		{files: SongInfo[]; selectedFile: SongInfo | null; onFileSelect: (file: SongInfo) => void} = $props();
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible w-full min-w-0">
			<label class="label w-full flex flex-col items-center">
				<span class="label-text mb-2 text-lg font-semibold">Select piece</span>
				<select
				class="select select-bordered w-full min-w-0"
				onchange={(e) => {
					const selected = files.find(f => f.path === e.currentTarget.value);
					if (selected) onFileSelect(selected);
				}}>
				<option value="" disabled selected={!selectedFile}>Select a piece...</option>
				{#each files as file}
					<option value={file.path} selected={selectedFile?.path === file.path}>{file.label}</option>
				{/each}
				</select>
			</label>
		</div>
	</div>
</div>