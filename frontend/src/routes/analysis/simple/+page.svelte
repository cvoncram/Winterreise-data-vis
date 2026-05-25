<script lang="ts">
	import { onMount } from "svelte";
    import * as d3 from "d3";
    import type { PerformanceRow, PerformanceMetadata } from "$lib/components/MeiTable.svelte";

    let data;
    let container: HTMLDivElement;
    let error;
    let svgNode: SVGSVGElement | null;
    let path = "performances/1967_Moore/1967_Moore_1_Audio_Data.xml";
    let tableRows = $state<PerformanceRow[]>([]);
    let width: number = 1500;

    onMount(async () => {
        try {
            const res = await fetch(`/db/parsed-file?path=${encodeURIComponent(path)}`);
            if (!res.ok) throw new Error('Error');
            data = await res.json();
            tableRows = data[1]?.data ?? [];
            svgNode = createSimpleGraph(tableRows, width);
            container.appendChild(svgNode!);
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    });

    function createSimpleGraph(tableRows: PerformanceRow[], width: number) {

        const height = 500;

        const data = tableRows.filter(r => r.timbre !== null);

        const x = d3.scalePoint<string>()
            .domain(data.map(r => r.measure))
            .range([0, width]);

        const y = d3.scaleLinear()
            .domain([0, Math.max(...data.map(r => r.timbre!))])
            .range([height, 0]);

        const line = d3.line<PerformanceRow>()
        .x(d => x(d.measure)!)
        .y(d => y(d.timbre!));

        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height);

        const margin = { top: 20, right: 20, bottom: 30, left: 40 };

        svg.append("g")
            .attr("transform", `translate(0, ${height})`)  // bottom
            .call(d3.axisBottom(x));

        svg.append("g")
            .attr("transform", `translate(${margin.left}, 0)`)  // left
            .call(d3.axisLeft(y));

        svg.append("path")
            .attr("fill", "none")
            .attr("stroke", "steelblue")
            .attr("stroke-width", 1.5)
            .attr("d", line(data));

        return svg.node();
    }

    
    

</script>


<div bind:this={container}>
    <svg></svg>
</div>

{#if tableRows.length > 0}
<div class="overflow-auto mt-4">
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
      {#each tableRows as row}
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