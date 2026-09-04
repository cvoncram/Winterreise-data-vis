<script lang="ts">
	import type {PerformanceRow} from "$lib/types";
	import CsvSimple from "../partials/CsvSimple.svelte";
	let {rows = []}: {rows: PerformanceRow[]} = $props();
	
	let downloadable = $derived(rows);
</script>

{#if rows.length > 0}
<div class="overflow-auto mt-4">
	<CsvSimple table={downloadable}/>
	<table class="table table-zebra w-full">
		<thead>
			<tr>
				<th>Measure</th>
				<th>Tempo</th>
				<th>Dynamics</th>
				<th>Spectral Centroid</th>
			</tr>
		</thead>
		<tbody>
			{#each rows as row}
			<tr>
				<td>{row.measure}</td>
				<td>{row.tempo ?? "-"}</td>
				<td>{row.dynamics ?? "-"}</td>
				<td>{row.timbre ?? "-"}</td>
			</tr>
			{/each}
		</tbody>
	</table>
</div>
{/if}