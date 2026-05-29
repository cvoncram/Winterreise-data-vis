<script lang="ts">
	import { onMount } from "svelte";
	import type { PerformanceRow, PerformanceMetadata } from "$lib/types";
    import * as d3 from "d3";

    let {performances, parameter, metadata}: {performances: PerformanceRow[][], parameter: string; metadata: PerformanceMetadata[]} = $props();
    let colors: string[] = $state(["red", "green", "yellow", "blue", "purple", "orange"]);
    let container: HTMLDivElement;

    $effect(() => {
        if (performances.length === 0) return;
        container.innerHTML = ''; // clear previous graph
        const node = createLineGraph(performances, parameter, colors);
        if (node) container.appendChild(node);
    });

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
            } else {
                const m = data[i].match(/^([a-z]+)([+-]\d+)?$/i);
                const base = map[m?.[1] ?? ""] ?? 0;
                const off = m?.[2] ? Number(m[2]) : 0;
                numVals[i] = Math.abs(base + off);
            }
        }
        return numVals;
    }

    export function createLineGraph(performances: PerformanceRow[][], parameter: string, colors: string[]) {
        const width = 1400;
        const height = 800;
        const refMeasures = performances[0].map(r => r.measure);

        const x = d3.scalePoint<string>()
            .domain(refMeasures)
            .range([0, width]);

        function xLabeling (interval: number) {
            let values = [];
            for (let i = 0; i < refMeasures.length; i += interval) {
                values.push(refMeasures[i]);
            }
            return values;
        };

        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("transform", "translate(0, -50)")

        const margin = { top: 20, right: 20, bottom: 40, left: 40 };

        svg.append("g")
            .attr("transform", `translate(${margin.left + 40}, ${height - 20})`)
            .call(d3.axisBottom(x).tickValues(xLabeling(refMeasures.length/20)));

        let graphData: number[][] = [[]];

        if (parameter == "tempo") {
            graphData = performances.map(p => p.map(r => r.tempo).filter(t => t !== null));
        } else if (parameter == "dynamics") {
            const dynData = performances.map(p => p.map(r => r.dynamics).filter(t => t !== null));
            graphData = dynData.map((d, i) => convertDynamics(d, i));
        } else if (parameter == "timbre") {
            graphData = performances.map(p => p.map(r => r.timbre).filter(t => t !== null));
        }

        const maxVal = Math.max(...graphData.flat());

        const y = d3.scaleLinear()
            .domain([0, maxVal])
            .range([height, 0]);

        performances.forEach((p, i) => {
        const line = d3.line<number>()
            .x((_, j) => x(refMeasures[j])!)
            .y(d => y(d));
        svg.append("path")
            .attr("d", line(graphData[i]))
            .attr("fill", "none")
            .attr("stroke", colors[i]);
        });

        svg.append("g")
            .attr("transform", `translate(${margin.left + 40}, -20)`)
            .call(d3.axisLeft(y));

        return svg.node();
    }  

</script>

<div bind:this={container} class="relative w-full h-[80vh]">

</div>