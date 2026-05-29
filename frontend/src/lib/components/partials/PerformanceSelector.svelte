<script lang="ts">
	import type {CyclePerformance} from "$lib/types"
	
	let {recordings = [], selectedRecording = null, onSelect}: 
	{recordings: CyclePerformance[]; selectedRecording: CyclePerformance | null; onSelect: (recording: CyclePerformance) => void} = $props();
	
	// Auto-select first recording when list arrives
	$effect (() => {
		if (recordings.length > 0 && !selectedRecording) {
			selectedRecording = recordings[0];
			onSelect(selectedRecording);
		}
	});
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg w-full shadow flex flex-col items-start overflow-visible">
			<label class="label w-full flex flex-col items-center">
				<span class="label-text mb-2 text-lg font-semibold">Select performance</span>
				<select
				class="select select-bordered w-full"
				onchange={(e) => {
					const selected = recordings.find(r => `${r.path}` === e.currentTarget.value);
					if (selected) onSelect(selected);
				}}
				disabled={recordings.length === 0}
				>
				{#each recordings as rec}
					<option value="{rec.path}">{rec.label}</option>
				{/each}
				</select>
			</label>
		</div>
	</div>
</div>