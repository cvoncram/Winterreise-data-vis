<script lang="ts">
	let { selectedParameters = $bindable(["tempo"]) }: { selectedParameters?: string[] } = $props();

	const options: { value: string; label: string }[] = [
		{ value: "tempo", label: "Tempo" },
		{ value: "dynamics", label: "Dynamics" },
		{ value: "timbre", label: "Timbre" }
	];

	function toggle(value: string) {
		if (selectedParameters.includes(value)) {
			if (selectedParameters.length === 1) return; // keep at least one selected
			selectedParameters = selectedParameters.filter(p => p !== value);
		} else {
			selectedParameters = [...selectedParameters, value];
		}
	}
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible w-full">
			<span class="label-text mb-2 text-lg font-semibold">Select parameters</span>
			{#each options as opt}
				<label class="label">
					<input
						type="checkbox"
						checked={selectedParameters.includes(opt.value)}
						onchange={() => toggle(opt.value)}
					/>
					{opt.label}
				</label>
			{/each}
		</div>
	</div>
</div>
