<script lang="ts">
    import * as d3 from "d3";
    import type { PerformanceRow, PerformanceMetadata } from "$lib/types";

    let { displayedRows = $bindable([]), metadata, selectedColorDropdown = $bindable("viridisScheme"), selectedRowAll = $bindable(false), selectedRowTarget = $bindable(null) }:
        { displayedRows? : PerformanceRow[]; metadata: PerformanceMetadata | null; selectedColorDropdown?: string; selectedRowAll: boolean; selectedRowTarget: string | null } = $props();

    let selectedRow = $state<PerformanceRow | null>(null);

    const width = 1000;
    const height = 200;
    const marginTop = 20;
    const marginRight = 10;
    const marginBottom = 30;
    const marginLeft = 40;

    function applyColorScheme(color: number) {
        if (selectedColorDropdown === "viridisScheme") return d3.interpolateViridis(color);
        if (selectedColorDropdown === "infernoScheme") return d3.interpolateInferno(color);
        if (selectedColorDropdown === "cividisScheme") return d3.interpolateCividis(color);
        if (selectedColorDropdown === "greensScheme") return d3.interpolateGreens(1 - color);
        if (selectedColorDropdown === "bluesScheme") return d3.interpolateBlues(1 - color);
        if (selectedColorDropdown === "redsScheme") return d3.interpolateReds(1 - color);
        return "";
    }

    function computeDynamics(data: PerformanceRow[], metadata: PerformanceMetadata) {
        if (!metadata) return [];
        const f = 12 / metadata.dynamicStep;
        const map: Record<string, number> = { ppp:12, pp:24, p:36, mp:48, mf:60, f:72, ff:84, fff:96 };

        return data.map(r => {
            const numeric = parseFloat(r.dynamics);
            if (!isNaN(numeric) && /^-?\d+(\.\d+)?$/.test(r.dynamics.trim())) {
                return 0.3 + (((Math.abs(numeric) - Math.abs(metadata.mfValue)) / (-metadata.dynamicStep)) * 0.06);
            }
            const m = r.dynamics.match(/^([a-z]+)([+-]\d+)?$/i);
            const base = map[m?.[1] ?? ""] ?? 0;
            const off = m?.[2] ? Number(m[2]) : 0;
            return (base + off * f) / 200;
        });
    }

    let visualData = $derived.by(() => {
        if (!metadata || !displayedRows.length) return [];

        const timbreMin = d3.min(displayedRows, d => d.timbre) ?? 0;
        const timbreMax = d3.max(displayedRows, d => d.timbre) ?? 0;
        const diff = timbreMax - timbreMin || 1;

        const dyn = computeDynamics(displayedRows, metadata);
        const dynMax = d3.max(dyn) ?? 0;

        const tempoSum = d3.sum(displayedRows, d => d.tempo) ?? 0;

        let currentX = 0;

        return displayedRows.map((d, i) => {
            const barWidth = ((1 / d.tempo) / d3.sum(displayedRows, d => 1 / d.tempo)) * width;
            const x0: number = currentX;
            const x1: number = x0 + barWidth;
            currentX = x1;

            return {
                index: i,
                color: applyColorScheme(((d.timbre ?? 0) - timbreMin) / diff),
                length: 0.5 + (dyn[i] / dynMax * 2),
                width: d.tempo / tempoSum,
                x0,
                x1
            };
        });
    });

    function attachGraph(container: HTMLDivElement) {
        $effect(() => {
            if (!visualData || visualData.length === 0) return;

            container.innerHTML = '';

            const x = d3.scaleLinear()
                .domain([
                    d3.min(visualData, d => d.x0) ?? 0,
                    d3.max(visualData, d => d.x1) ?? 0
                ])
                .range([marginLeft, width - marginRight]);

            const y = d3.scaleLinear()
                .domain([0, d3.max(visualData, d => d.length ?? 0) ?? 0]).nice()
                .range([height - marginBottom, marginTop]);

            const svg = d3.create("svg")
                .attr("viewBox", [0, 0, width, height])
                .attr("width", width)
                .attr("height", height)
                .attr("style", "max-width: 100%; height: auto;")
                .on("click", () => {
                    selectedRow = null;
                    selectedRowTarget = null;
                });

            svg.append("g")
                .selectAll("rect")
                .data(visualData)
                .join("rect")
                .attr("x", d => x(d.x0))
                .attr("width", d => x(d.x1) - x(d.x0))
                .attr("y", d => y(d.length))
                .attr("height", d => y(0) - y(d.length))
                .attr("fill", d => d.color)
                .attr("rx", 4)
                .on("click", (event: MouseEvent, d) => {
                    event.stopPropagation();
                    if (selectedRowAll) {
                        selectedRowTarget = displayedRows[d.index].measure;
                    } else {
                        selectedRow = displayedRows[d.index];
                    };

                });

            svg.append("g")
                .attr("class", "x-axis")
                .attr("transform", `translate(0,${height - marginBottom})`);

            container.appendChild(svg.node()!);
        });
    }

    $effect(() => {
        if (selectedRowAll) {
            selectedRow = selectedRowTarget
                ? (displayedRows.find(r => r.measure === selectedRowTarget) ?? null)
                : null;
        }
    });



</script>

<div class="flex gap-2 overflow-hidden">
    <div {@attach attachGraph} class="relative w-[75%]"></div>
    {#if selectedRow}
    <div class="relative w-[25%]">
        <div><b>Selected measure:</b> {selectedRow?.measure}</div>
        <div><b>Tempo:</b> {selectedRow?.tempo} bpm</div>
        <div><b>Dynamics:</b> {selectedRow?.dynamics}</div>
        <div><b>Spectral centroid:</b> {selectedRow?.timbre} Hz</div>
    </div>
    {/if}
</div>

<style>
    :global(g rect:hover) {
        filter: brightness(1.4);
    }

    :global(g rect) {
        opacity: 1;
        transition:
            opacity 0.15s ease,
            filter 0.15s ease;
    }

    :global(g rect.selected) {
        opacity: 0.2;
    }

</style>