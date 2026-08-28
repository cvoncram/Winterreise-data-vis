<script lang="ts">
	import type { PerformanceRow } from "$lib/types";
    import * as d3 from "d3";

    let {performances, parameter, labels}: {
        performances: PerformanceRow[][], parameter: string, labels: string[]
    } = $props();


    let usedColors: string[] = $state([]);

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

    function createLineGraph(performances: PerformanceRow[][], parameter: string) {
        const margin = { top: 20, right: 20, bottom: 60, left: 80 };
        const width = 1300 - margin.left - margin.right;
        const height = 800 - margin.top - margin.bottom;
        const refMeasures = performances[0].map(r => r.measure);

        const svg = d3.create("svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom);


        const g = svg.append("g")
            .attr("transform", `translate(${margin.left}, ${margin.top})`);


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

        const color = d3.scaleOrdinal(d3.schemeCategory10);

        series.forEach((points, i) => {
            const line = d3.line<Point>()
                .x(d => x(d.measure)!)
                .y(d => y(d.value));

            const strokeColor = color(String(i))
            g.append("path")
                .attr("d", line(points))
                .attr("fill", "none")
                .attr("stroke", strokeColor);
            usedColors.push(strokeColor);             

        });

        $inspect(usedColors.toString)

        return svg.node();
    }

    function attachGraph(node: HTMLDivElement) {
        $effect(() => {
            if (performances.length === 0) return;
            node.innerHTML = '';
            const svg = createLineGraph(performances, parameter);
            if (svg) node.appendChild(svg);
        });

        return () => { node.innerHTML = ''; };
    }

</script>


<div class="flex flex-row p-5">
    <div {@attach attachGraph} class="basis-2/3"></div>

    <div class="basis-1/3 align-middle">
        <p>Key:</p>
        {#each labels as label, i}
            <p style="color: {usedColors[i]}">{label}</p>
        {/each}
    </div>
</div>