<script lang="ts">
    import * as d3 from "d3";
    import type { PerformanceRow, PerformanceMetadata, NormalizationReference } from "$lib/types";
    import { applyColorScheme, computeDynamicsUnit, computeTimbreUnit } from "$lib/utils/performanceVisuals";
    import SvgDownloadButton from '$lib/components/partials/SvgDownloadButton.svelte';
    let svgContainer: HTMLDivElement | undefined = $state();

    let { displayedRows = $bindable([]), metadata, normalizationReference = null, selectedColorDropdown = $bindable("viridisScheme"), selectedRowAll = $bindable(false), selectedRowTarget = $bindable(null), maxDuration = 0, label = 'linear-ribbon' }:
        { displayedRows? : PerformanceRow[]; metadata: PerformanceMetadata | null; normalizationReference?: NormalizationReference | null; selectedColorDropdown?: string; selectedRowAll: boolean; selectedRowTarget: string | null;
          maxDuration?: number; label?: string } = $props();

    let selectedRow = $state<PerformanceRow | null>(null);

    const width = 1000;
    const height = 200;
    const marginTop = 20;
    const marginRight = 10;
    const marginBottom = 30;
    const marginLeft = 40;

    const LENGTH_MAX = 2.5;

    let visualData = $derived.by(() => {
        if (!metadata || !displayedRows.length) return [];

        const dyn = computeDynamicsUnit(displayedRows, normalizationReference);
        const timbreUnit = computeTimbreUnit(displayedRows, normalizationReference);

        let elapsed = 0;

        return displayedRows.map((d, i) => {
            const t0 = elapsed;
            elapsed += d.tempo ? 60 / d.tempo : 0;

            return {
                index: i,
                color: applyColorScheme(selectedColorDropdown, timbreUnit[i] ?? 0.5),
                length: 0.5 + (dyn[i] ?? 0.5) * 2,
                t0,
                t1: elapsed
            };
        });
    });

    let extent = $derived(
        maxDuration > 0 ? maxDuration : (visualData.at(-1)?.t1 ?? 0)
    );

    function attachGraph(container: HTMLDivElement) {
        $effect(() => {
            if (!visualData || visualData.length === 0) return;

            container.innerHTML = '';

            const x = d3.scaleLinear()
                .domain([0, extent])
                .range([marginLeft, width - marginRight]);

            const y = d3.scaleLinear()
                .domain([0, LENGTH_MAX])
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
                .attr("x", d => x(d.t0))
                .attr("width", d => x(d.t1) - x(d.t0))
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
                .attr("transform", `translate(0,${height - marginBottom})`)
                .call(d3.axisBottom(x).ticks(8).tickFormat(d => `${d}s`));

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
    <div {@attach attachGraph} bind:this={svgContainer} class="relative w-[75%]"></div>
    <div class="relative w-[25%] min-h-px">
        {#if selectedRow}
            <div><b>Selected measure:</b> {selectedRow?.measure}</div>
            <div><b>Tempo:</b> {selectedRow?.tempo} bpm</div>
            <div><b>Dynamics:</b> {selectedRow?.dynamics} dB</div>
            <div><b>Spectral centroid:</b> {selectedRow?.timbre} Hz</div>
        {/if}

        <div class="mt-2">
            <SvgDownloadButton container={svgContainer} filename={label} />
        </div>
    </div>
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