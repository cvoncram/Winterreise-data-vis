<script lang="ts">
    import { onMount } from "svelte";
    import * as d3 from "d3";
    import type { PerformanceRow } from "$lib/components/MeiTable.svelte";

    export let rows: PerformanceRow[] = [];

    let container: HTMLDivElement;

    const width = 1400;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 40, left: 20 };

    function draw() {
        if (!rows || rows.length === 0) return;

        d3.select(container).selectAll("*").remove();

        const svg = d3
            .select(container)
            .append("svg")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g");

        // ---- DATA ----
        const data = rows.map((d, i) => ({
            index: i,
            measure: d.measure,
            tempo: d.tempo ?? 60,
            dynamics: d.dynamics ?? "mf",
            timbre: d.timbre ?? 0
        }));

        // ---- SCALES ----
        let xScale = d3
            .scaleLinear()
            .domain([0, data.length - 1])
            .range([margin.left, width - margin.right]);

        const yCenter = height / 2;

        const colorScale = d3
            .scaleSequential(d3.interpolateViridis)
            .domain(d3.extent(data, d => d.timbre) as [number, number]);

        const dynScale: Record<string, number> = {
            "pp": 3,
            "p": 6,
            "mp": 10,
            "mf": 16,
            "f": 24,
            "ff": 32
        };

        const tempoExtent = d3.extent(data, d => d.tempo) as [number, number];

        const tempoScale = d3
            .scaleLinear()
            .domain(tempoExtent)
            .range([0.6, 1.6]);

        // ---- ZOOM ----
        const zoom = d3.zoom<SVGSVGElement, unknown>()
            .scaleExtent([1, 12])
            .on("zoom", (event) => {
                const transform = event.transform;

                xScale = transform.rescaleX(
                    d3.scaleLinear()
                        .domain([0, data.length - 1])
                        .range([margin.left, width - margin.right])
                );

                render();
            });

        svg.call(zoom as any);

        // ---- RENDER ----
        function render() {
            g.selectAll("*").remove();

            // ---- GRADIENT FILL (important change) ----
            const gradient = svg.append("defs")
                .append("linearGradient")
                .attr("id", "timbre-fill")
                .attr("gradientUnits", "userSpaceOnUse")
                .attr("x1", 0)
                .attr("x2", width);

            data.forEach((d, i) => {
                gradient.append("stop")
                    .attr("offset", `${(i / data.length) * 100}%`)
                    .attr("stop-color", colorScale(d.timbre))
                    .attr("stop-opacity", 0.9);
            });

            // ---- AREA (FILLED RIBBON) ----
            const area = d3.area<typeof data[0]>()
                .x((d, i) => xScale(i))
                .y0(d => {
                    const base = dynScale[d.dynamics] || 10;
                    const amp = tempoScale(d.tempo);
                    return yCenter - base * amp;
                })
                .y1(d => {
                    const base = dynScale[d.dynamics] || 10;
                    const amp = tempoScale(d.tempo);
                    return yCenter + base * amp;
                })
                .curve(d3.curveCatmullRom.alpha(0.8));

            // ---- FILLED RIBBON ----
            g.append("path")
                .datum(data)
                .attr("d", area as any)
                .attr("fill", "url(#timbre-fill)")
                .attr("stroke", "none");

            // ---- X AXIS (MEASURE LABELS) ----
            const xAxisScale = d3
                .scalePoint<string>()
                .domain(data.map(d => d.measure))
                .range([margin.left, width - margin.right]);

            const xAxis = d3.axisBottom(xAxisScale)
                .tickValues(
                    data
                        .filter((_, i) => i % Math.floor(data.length / 10) === 0)
                        .map(d => d.measure)
                );

            g.append("g")
                .attr("transform", `translate(0, ${height - margin.bottom})`)
                .call(xAxis)
                .selectAll("text")
                .attr("transform", "rotate(-45)")
                .style("text-anchor", "end");

            // ---- CENTER LINE (optional) ----
            g.append("line")
                .attr("x1", margin.left)
                .attr("x2", width - margin.right)
                .attr("y1", yCenter)
                .attr("y2", yCenter)
                .attr("stroke", "#999")
                .attr("opacity", 0.15);
        }

        render();
    }

    onMount(draw);

    $: if (rows) draw();
</script>

<div bind:this={container}></div>