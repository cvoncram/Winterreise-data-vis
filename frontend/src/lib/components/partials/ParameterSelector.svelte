<script lang="ts">
	import type { Parameter } from "$lib/types";

	let { selectedParameter, onParameterSelect }: { 
	selectedParameter: Parameter; 
	onParameterSelect: (parameter: Parameter) => void 
	} = $props();

	const parameters: Parameter[] = ["tempo", "dynamics", "timbre"];
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col w-full items-start overflow-visible">
			<label class="label w-full flex flex-col items-center">
				<span class="label-text mb-2 text-lg font-semibold">Select parameter</span>
				<select
				class="select select-bordered w-full"
				bind:value={selectedParameter}
				onchange={(e) => onParameterSelect(e.currentTarget.value as Parameter)}
				>
				{#each parameters as p}
					<option value={p}>{p}</option>
				{/each}
				</select>
			</label>
		</div>
	</div>
</div>