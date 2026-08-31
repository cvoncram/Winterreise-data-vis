<script lang="ts">
	let {
		selectedParameters = $bindable(["tempo"]),
		weights = $bindable({ tempo: 1, dynamics: 1, timbre: 1 }),
		metric = "euclidean"
	}: {
		selectedParameters?: string[];
		weights?: Record<string, number>;
		metric?: string;
	} = $props();

	const options: { value: string; label: string }[] = [
		{ value: "tempo", label: "Tempo" },
		{ value: "dynamics", label: "Dynamics" },
		{ value: "timbre", label: "Timbre" }
	];

	/**
	 * Weighting only has an effect on several parameters compared with the euclidean metric.
	 */
	const weightsApply = $derived(selectedParameters.length > 1 && metric === "euclidean");

	/** 
	 * Share each parameter actually contributes, for display.
	 */
	const shares = $derived.by(() => {
		const total = selectedParameters.reduce((sum, p) => sum + (weights[p] ?? 0), 0);
		const equal = 1 / Math.max(selectedParameters.length, 1);
		return Object.fromEntries(
			selectedParameters.map(p => [p, total > 0 ? (weights[p] ?? 0) / total : equal])
		) as Record<string, number>;
	});

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

				{#if weightsApply && selectedParameters.includes(opt.value)}
					<div class="w-full pl-6 pr-1 -mt-1 mb-2">
						<input
							type="range"
							min="0"
							max="100"
							bind:value={weights[opt.value]}
							class="range range-xs range-primary"
							aria-label={`Weight for ${opt.label}`}
						/>
						<div class="text-xs opacity-60 text-right">
							{(shares[opt.value] * 100).toFixed(0)} %
						</div>
					</div>
				{/if}
			{/each}

			{#if weightsApply}
				<p class="text-xs opacity-60 mt-1">
					Weights are relative; the percentages show each parameter's actual share.
				</p>
			{/if}
		</div>
	</div>
</div>
