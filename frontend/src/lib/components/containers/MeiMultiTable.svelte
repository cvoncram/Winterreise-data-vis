<script lang="ts">
	import type {PerformanceRow} from "$lib/types";
	import { onMount } from "svelte";
    import LineGraphCsv from "../partials/LineGraphCsv.svelte";
	type tableRow = {
        measure: string,
        values: number[];
    }
    let rows: tableRow[] = $state([]);

    let {performances, parameter, labels}: {
    performances: PerformanceRow[][], parameter: string, labels: string[]
    } = $props();

    function makeTable(performances: PerformanceRow[][]): tableRow[]{
        const key = parameter as "tempo" | "timbre" | "dynamics";
        return performances[0].map((d, i) => ({
            measure: d.measure,
            values: performances.map(r => r[i][key] as number)
        }));
    }

    onMount(() => {
        if(performances && parameter) {
            rows = makeTable(performances);
        }
    })

</script>

{#if performances.length > 0}
<div class="overflow-auto mt-4">
    <LineGraphCsv rows={rows} labels={labels} />
	<table class="table table-zebra w-full">
		<thead>
			<tr>
                <th>Measure</th>
            {#each labels as label}
				<th>{label}</th>
            {/each}
			</tr>
		</thead>
		<tbody>
			{#each rows as row}
			<tr>
				<td>{row.measure}</td>
                {#each row.values as value}
                <td>{value}</td>
                {/each}
			</tr>
			{/each}
		</tbody>
	</table>
</div>
{/if}