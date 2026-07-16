<script lang="ts">
	let {
		start = $bindable(1),
		startBeat = $bindable(1),
		end = $bindable(1),
		endBeat = $bindable(1)
	}: { start?: number; startBeat?: number; end?: number; endBeat?: number } = $props();
</script>

<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible w-full">
	<span class="label-text mb-2 text-lg font-semibold">Measure range</span>
	<label class="label w-full justify-between">Start measure
		<input type="number" min="1" class="input input-bordered w-24" bind:value={start} />
	</label>
	<label class="label w-full justify-between">Start beat
		<input type="number" min="1" class="input input-bordered w-24" bind:value={startBeat} />
	</label>
	<label class="label w-full justify-between">End measure
		<input type="number" min="1" class="input input-bordered w-24" bind:value={end} />
	</label>
	<label class="label w-full justify-between">End beat
		<input type="number" min="1" class="input input-bordered w-24" bind:value={endBeat} />
	</label>
</div>
