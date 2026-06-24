<script lang="ts">
    import { tick } from "svelte";
    import * as d3 from "d3";
    import { goto } from "$app/navigation";
    import { selectedMeasuresStore, selectedPieceStore, startMeasure, startBeat, endMeasure, endBeat } from "$lib/stores/selection";

    import type {
        PerformanceRow,
        PerformanceMetadata
    } from "$lib/types";

    type ArcDatum = d3.PieArcDatum<PerformanceRow> & {
        thickness: number;
        color: string;
        index: number;
    };

    let { displayedRows = $bindable([]), metadata, brushEnabled=$bindable(false), selectedColorDropdown=$bindable("viridisScheme") }:
        { displayedRows? : PerformanceRow[]; metadata: PerformanceMetadata | null; brushEnabled?: boolean; selectedColorDropdown?: string } = $props();

    let svg: SVGSVGElement;

    let selectedRow = $state<PerformanceRow | null>(null);
    let selectedMeasures = $state<PerformanceRow[]>([]);
    let isDraggingSelection = $state(false);
    let dragStartIndex: number | null = null;
    let width = $state(0);
    let height = $state(0);

    function applyColorScheme(color: number) {
        if (selectedColorDropdown === "viridisScheme") return d3.interpolateViridis(color);
        if (selectedColorDropdown === "infernoScheme") return d3.interpolateInferno(color);
        if (selectedColorDropdown === "cividisScheme") return d3.interpolateCividis(color);
        if (selectedColorDropdown === "greensScheme") return d3.interpolateGreens(1 - color);
        if (selectedColorDropdown === "bluesScheme") return d3.interpolateBlues(1 - color);
        if (selectedColorDropdown === "redsScheme") return d3.interpolateReds(1 - color);
        return "";
    }

    function computeDynamics(data: PerformanceRow[]) {
        if (!metadata) return [];
        const f = 12 / metadata.dynamicStep;
        const map: Record<string, number> = { ppp:12, pp:24, p:36, mp:48, mf:60, f:72, ff:84, fff:96 };

        return data.map(r => {
            if (!r.dynamics) return 0;
            const m = r.dynamics.match(/^([a-z]+)([+-]\d+)?$/i);
            const base = map[m?.[1] ?? ""] ?? 0;
            const off = m?.[2] ? Number(m[2]) : 0;
            return (base + off * f) / 200;
        });
    }

    let visualData = $derived.by(() => {
        if (!displayedRows.length || !metadata) return [];

        const min = d3.min(displayedRows, d => d.timbre) ?? 0;
        const max = d3.max(displayedRows, d => d.timbre) ?? 0;
        const diff = max - min || 1;

        const dyn = computeDynamics(displayedRows);

        const pie = d3.pie<PerformanceRow>()
            .sort(null)
            .startAngle(-Math.PI / 2)
            .endAngle(Math.PI / 2)
            .value(d => 60 / (d.tempo ?? 60));

        return pie(displayedRows).map((d, i) => ({
            ...d,
            index: i,
            thickness: dyn[i] ?? 0,
            color: applyColorScheme(((d.data.timbre ?? 0) - min) / diff)
        } satisfies ArcDatum));
    });

    export function clearSelection() {
        selectedMeasures = [];
        dragStartIndex = null;
        isDraggingSelection = false;
        tick().then(updateChart);
    }

    function updateChart() {
        if (!svg || !metadata || !visualData.length) return;

        const r = Math.min(width, height)/1.05;

        const svgSel = d3.select(svg)
            .attr("width", width)
            .attr("height", height);

        const arcGen = d3.arc<ArcDatum>()
            .innerRadius(r * 0.5)
            .outerRadius(d => r * (0.5 + d.thickness))
            .padAngle(0.001)
            .cornerRadius(5);

        let g = svgSel.select<SVGGElement>("g.chart-root");
        if (g.empty()) g = svgSel.append("g").attr("class", "chart-root");

        g.attr("transform", `translate(${width/2}, ${height/1.05})`);

        const arcs = g.selectAll<SVGPathElement, ArcDatum>("path.arc")
            .data(visualData, d => d.data.measure);

        arcs.exit().remove();

        const enter = arcs.enter().append("path").attr("class", "arc");
        const merged = enter.merge(arcs);

        merged
            .attr("fill", d => d.color)
            .attr("d", arcGen)
            .classed("selected", d => selectedMeasures.length > 0 && selectedMeasures.some(s => s.measure === d.data.measure));

        enter
            .on("click", (_, d) => {
                if (!brushEnabled) selectedRow = d.data;
            })
            .on("pointerdown", (_, d) => {
                if (!brushEnabled) return;
                isDraggingSelection = true;
                dragStartIndex = d.index;
            })
            .on("pointermove", (_, d) => {
                if (!isDraggingSelection || dragStartIndex == null) return;

                const start = Math.min(dragStartIndex, d.index);
                const end = Math.max(dragStartIndex, d.index);

                const startId = visualData[start].data.measure;
                const endId = visualData[end].data.measure;

                const a = displayedRows.findIndex(r => r.measure === startId);
                const b = displayedRows.findIndex(r => r.measure === endId);

                const [min, max] = [Math.min(a,b), Math.max(a,b)];

                selectedMeasures = [...displayedRows.slice(min, max + 1)];
                tick().then(updateChart);
            
            })
            .on("pointerup", () => {
                isDraggingSelection = false;
                dragStartIndex = null;
            });
    }

    function attachContainer(node: HTMLDivElement) {
        const resizeObserver = new ResizeObserver(() => {
            width = node.clientWidth;
            height = node.clientHeight;
        });
        resizeObserver.observe(node);
        width = node.clientWidth;
        height = node.clientHeight;

        window.addEventListener("mouseup", () => isDraggingSelection = false);

        return () => resizeObserver.disconnect();
    }

    $effect(() => {
        if (visualData.length && width > 0 && height > 0) {
            tick().then(updateChart);
        }
    });
</script>

<!-- SVG CONTAINER -->

<div {@attach attachContainer} class="relative w-full h-[80vh]">

    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <svg 
        bind:this={svg}
        class="w-full h-full"
        role="application"
        aria-label="Interactive performance visualization"
        onkeydown={() => {}}
        onpointerup={() => {
            isDraggingSelection = false;
        }}
        onpointerleave={() => {
            isDraggingSelection = false;
        }}
    ></svg>

    <!-- SINGLE ROW INFO -->
    {#if selectedRow && !brushEnabled}
        <div class="absolute bottom-10 left-1/2 -translate-x-1/2 bg-base-200 p-4 rounded-xl shadow-xl">
            <div>
                <h3 class="card-title">Measure {selectedRow.measure}</h3>
                <p>Tempo (bpm): {selectedRow.tempo}<br>Dynamics: {selectedRow.dynamics}<br>Spectral centroid (Hz): {selectedRow.timbre}
                </p>
            </div>
        </div>
    {/if}

    <!-- BRUSH INFO -->
    {#if brushEnabled && selectedMeasures.length > 0}
        <div class="absolute bottom-10 left-1/2 -translate-x-1/2 bg-base-200 p-4 rounded-xl shadow-xl">
            <h3 class="card-title">Selected range</h3>
            <p>Marked beats: {selectedMeasures[0].measure} – {selectedMeasures[selectedMeasures.length - 1].measure}
            </p>
            <p>Total selected beats: {selectedMeasures.length}</p>
            <button
                class="btn btn-block btn-secondary mt-3"
                onclick={() => {displayedRows = [
                        ...selectedMeasures
                    ];
                    clearSelection();
                }}
            >Visualize only these beats</button>
            <button                 
                class="btn btn-block btn-secondary mt-3"
                onclick={() => {
                    selectedMeasuresStore.set(selectedMeasures);
                    const[startFirst, startSecond] = selectedMeasures[0].measure.split(".").map(Number);
                    startMeasure.set(startFirst);
                    startBeat.set(startSecond);
                    const[endFirst, endSecond] = selectedMeasures[selectedMeasures.length-1].measure.split(".").map(Number);
                    endMeasure.set(endFirst);
                    endBeat.set(endSecond);
                    if (metadata) {
                        selectedPieceStore.set(metadata)
                    };
                    goto("multi-parameter/multi-performance")
                }}>Compare with other performances</button>

            <button class="btn btn-block btn-warning" onclick={clearSelection}>Exit selection
            </button>
        </div>
    {/if}
</div>

<style>
    :global(path.arc:hover) {
        filter: brightness(1.4);
    }

    :global(path.arc) {
        opacity: 1;
        transition:
            opacity 0.15s ease,
            filter 0.15s ease;
    }

    :global(path.arc.selected) {
        opacity: 0.2;
    }
</style>