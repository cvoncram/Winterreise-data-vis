<script lang="ts">
	import type { PerformanceRow } from "$lib/types";
    import * as d3 from "d3";
    import SvgDownloadButton from '$lib/components/partials/SvgDownloadButton.svelte';
    let svgContainer: HTMLDivElement | undefined = $state();

    let {performances, parameter, labels}: {
        performances: PerformanceRow[][], parameter: string, labels: string[]
    } = $props();

    let width = $state(0);

    const color = d3.scaleOrdinal(d3.schemeCategory10);
    const usedColors = $derived(labels.map((_, i) => color(String(i))));

    type Point = { measure: string; value: number };

    function extractSeries(performances: PerformanceRow[][], parameter: string): Point[][] {
        if (parameter === "tempo" || parameter === "timbre") {
            const key = parameter as "tempo" | "timbre";
            return performances.map(p =>
                p
                    .filter(r => r[key] !== null)
                    .map(r => ({ measure: r.measure, value: r[key] as number }))
            );
        }

        return performances.map(p =>
            p
                .filter(r => r.dynamics !== null)
                .map(r => ({ measure: r.measure, value: parseFloat(r.dynamics) }))
                .filter(d => !Number.isNaN(d.value))
        );
    }

    function createLineGraph(performances: PerformanceRow[][], parameter: string, width: number) {
        const margin = 20;
        const height = 800;
        const refMeasures = performances[0].map(r => r.measure);

        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height + 2*margin)
            .attr("transform", `translate(${margin}, ${-margin})`);


        const g = svg.append("g")
            .attr("transform", `translate(${margin}, ${margin})`);


        function xLabeling (interval: number) {
            let values = [];
            for (let i = 0; i < refMeasures.length; i += interval) {
                values.push(refMeasures[i]);
            }
            return values;
        };

        const x = d3.scalePoint<string>()
            .domain(refMeasures)
            .range([0, width]);

        const series = extractSeries(performances, parameter);

        const [lo, hi] = d3.extent(series.flat(), d => d.value) as [number, number];

        const y = d3.scaleLinear()
            .domain([lo, hi]).nice()
            .range([height, 0]);

        g.append("g")
            .attr("transform", `translate(0, ${height})`)
            .call(d3.axisBottom(x).tickValues(xLabeling(20)));

        g.append("g")
            .call(d3.axisLeft(y));

        series.forEach((points, i) => {
            const line = d3.line<Point>()
                .x(d => x(d.measure)!)
                .y(d => y(d.value));

            g.append("path")
                .attr("d", line(points))
                .attr("fill", "none")
                .attr("stroke", color(String(i)));
        });

        return svg.node();
    }

    function attachGraph(node: HTMLDivElement) {
        $effect(() => {
            if (performances.length === 0 || performances[0].length === 0) return;
            node.innerHTML = '';
            const svg = createLineGraph(performances, parameter, width);
            if (svg) node.appendChild(svg);
        });

        return () => { node.innerHTML = ''; };
    }

</script>



<div {@attach attachGraph} bind:this={svgContainer} bind:clientWidth={width} class="m-5"></div>

<div>
    <p>Key:</p>
    {#each labels as label, i}
        <p style="color: {usedColors[i]}">{label}</p>
    {/each}
</div>

<div class="flex justify-end">
    <SvgDownloadButton container={svgContainer} filename="line-graph" />
</div>