<script lang="ts">
	let { selectedMetric = $bindable("euclidean") }: { selectedMetric?: "euclidean" | "mahalanobis" } = $props();
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col w-full items-start overflow-visible">
			<label class="label w-full flex flex-col items-center">
				<span class="label-text mb-2 text-lg font-semibold">Distance metric</span>
				<select class="select select-bordered w-full" bind:value={selectedMetric}>
					<option value="euclidean">Euclidean (equal weighting)</option>
					<option value="mahalanobis">Mahalanobis (accounts for correlation)</option>
				</select>
			</label>
		</div>
	</div>
</div>
