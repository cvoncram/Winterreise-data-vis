<script lang="ts">
	import type {CyclePerformance} from "$lib/types"
	
	let {recordings = [], selectedRecording = null, onSelect}: 
	{recordings: CyclePerformance[]; selectedRecording: CyclePerformance | null; onSelect: (recording: CyclePerformance) => void} = $props();
	
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg w-full shadow flex flex-col items-start overflow-visible">
			<label class="label w-full flex flex-col items-center">
				<span class="label-text mb-2 text-lg font-semibold">Select performance</span>
				<select
				class="select select-bordered w-full"
				value={selectedRecording?.path ?? ""}
				onchange={(e) => {
					const selected = recordings.find(r => `${r.path}` === e.currentTarget.value);
					if (selected) onSelect(selected);
				}}
				>
				<option value="" disabled selected={!selectedRecording}>Select a piece...</option>
				{#each recordings as rec}
					<option value="{rec.path}" selected={selectedRecording?.path === rec.path}>{rec.label}</option>
				{/each}
				</select>
			</label>
		</div>
	</div>
</div>