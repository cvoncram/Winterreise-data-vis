<script lang="ts">
	import type { PerformanceRow, PerformanceMetadata } from "$lib/types";
    import * as d3 from "d3";

    let {performances, parameter, metadata}: {
        performances: PerformanceRow[][], parameter: string; metadata: PerformanceMetadata[]
    } = $props();

    type Point = { measure: string; value: number };

    // only temporary, until the backend returns dyn values
    function convertDynamics(data: string[], index: number) {
        if (!metadata) return [];
        let numVals: number[] = [];
        const mfVal = metadata[index].mfValue;
        const dynStep = metadata[index].dynamicStep;
        const map: Record<string, number> = { ppp:mfVal-(4*dynStep), pp:mfVal-(3*dynStep), p:mfVal-(2*dynStep), mp:mfVal-dynStep,
            mf:mfVal, f:mfVal+dynStep, ff:mfVal+(2*dynStep), fff:mfVal+(3*dynStep) };

        for (let i=0; i < data.length; i++) {
            if (data[i] == "extreme"){
                numVals[i] = 0;
            } else if (/^-?\d+(\.\d+)?$/.test(data[i].trim())) {
                numVals[i] = Math.abs(parseFloat(data[i]));
            } else {
                const m = data[i].match(/^([a-z]+)([+-]\d+)?$/i);
                const base = map[m?.[1] ?? ""] ?? 0;
                const off = m?.[2] ? Number(m[2]) : 0;
                numVals[i] = Math.abs(base + off);
            }
        }
        return numVals;
    }

    // Filters out null values while keeping each value paired with its
    // originating measure, so lines stay aligned to the shared x-axis even
    // when a performance has gaps.
    function extractSeries(performances: PerformanceRow[][], parameter: string): Point[][] {
        if (parameter === "tempo" || parameter === "timbre") {
            const key = parameter as "tempo" | "timbre";
            return performances.map(p =>
                p
                    .filter(r => r[key] !== null)
                    .map(r => ({ measure: r.measure, value: r[key] as number }))
            );
        }
        // dynamics
        return performances.map((p, i) => {
            const withDyn = p.filter(r => r.dynamics !== null);
            const values = convertDynamics(withDyn.map(r => r.dynamics), i);
            return withDyn.map((r, j) => ({ measure: r.measure, value: values[j] }));
        });
    }

    function createLineGraph(performances: PerformanceRow[][], parameter: string) {
        const margin = { top: 20, right: 20, bottom: 60, left: 80 };
        const width = 1400 - margin.left - margin.right;
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
        const maxVal = Math.max(...series.flat().map(d => d.value));

        const y = d3.scaleLinear()
            .domain([0, maxVal])
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
            g.append("path")
            .attr("d", line(points))
            .attr("fill", "none")
            .attr("stroke", color(String(i)));
        });

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

<div {@attach attachGraph} class="relative p-5 w-full"></div>
