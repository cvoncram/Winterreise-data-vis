<script lang="ts">
    import { onMount, tick } from "svelte";
    import * as d3 from "d3";
    import type { PerformanceRow, PerformanceMetadata } from "$lib/components/MeiTable.svelte";

    let svg: SVGSVGElement;
    let container: HTMLDivElement;

    let width = $state(0);
    let height = $state(0);

    let { rows, metadata }: {
        rows: PerformanceRow[],
        metadata: PerformanceMetadata | null
    } = $props();
    let selectedRow = $state<PerformanceRow | null>(null);

    let isDraggingSelection = $state(false);
    let selectedMeasures = $state<PerformanceRow[]>([]);

    let resizeObserver: ResizeObserver;

    let brushEnabled = $state(false);

    let dragStartIndex: number | null = null;

    onMount(() => {
        resizeObserver = new ResizeObserver(() => {
            updateSize();
        });

        resizeObserver.observe(container);

        updateSize();
        
        window.addEventListener("mouseup", () => {
            isDraggingSelection = false;
        });

        return () => resizeObserver.disconnect();
    });

    function updateSize() {
        width = container.clientWidth;
        height = container.clientHeight;
    }

    let selectedColorDropdown = $state("viridisScheme");    

    // calculate colors for timbre/spectral centroid    
    function applyColorScheme (color: number) {
        if (selectedColorDropdown == "viridisScheme") {
            return d3.interpolateViridis(color);
        } else if (selectedColorDropdown == "infernoScheme") {
            return d3.interpolateInferno(color);
        } else if (selectedColorDropdown == "cividisScheme") {
            return d3.interpolateCividis(color);
        } else if (selectedColorDropdown == "greensScheme") {
            return d3.interpolateGreens(1 - color);
        } else if (selectedColorDropdown == "bluesScheme") {
            return d3.interpolateBlues(1 - color);
        } else if (selectedColorDropdown == "redsScheme") {
            return d3.interpolateReds(1 - color);
        } else {
            return "";
        }
    }
  
    let colors = $state<string[]>([""]);
    
    function fillColorArray (minTimbre: number, diff: number){
        for (let i=0; i < rows.length; i++) {
            const timbre = rows[i].timbre;
            if (timbre && minTimbre != null && timbre > 0) {
                colors[i] = applyColorScheme((timbre - minTimbre) / diff);
            } else if (timbre != null && timbre == 0) {
                colors[i] = applyColorScheme(0);
            }
        }
    }
    
    function updateColors() {
        if(!minTimbre) return;
        fillColorArray(minTimbre, diff);
        
        d3.select(svg)
        .selectAll<SVGPathElement, any>("path.arc")
        .attr("fill", (d, i) => colors[i]);
    }

    function clearSelection() {
        selectedMeasures = [];
        dragStartIndex = null;
        isDraggingSelection = false;

        d3.selectAll("path.arc")
            .classed("selected", false);
    }
    
    
    
    $effect(() => {
        if (rows.length && width > 0 && height > 0) {
        tick().then(render)}
    });

    let minTimbre: number | null;
    let maxTimbre: number;
    let diff: number;

    
    
    function render() {
        if(!svg || !container || !metadata ) return;
        
        minTimbre = d3.min(rows, d => d.timbre) ?? 0;
        maxTimbre = d3.max(rows, d => d.timbre) ?? 0;    
        diff = maxTimbre - minTimbre;
        
        const svgSel = d3.select(svg)
        .attr("width", width)
        .attr("height", height);
        
        svgSel.selectAll("*").remove();
        
        const radius = Math.min(width, height)/ 0.95;
        
        // calculate thickness of each arch from dynamics values
        let dynamics: number[] = [];
        const dynamicsFactor = 12 / metadata.dynamicStep;
        const dynamicsMap: Record<string, number> = {
            "ppp": 12,
            "pp": 24,
            "p": 36,
            "mp": 48,
            "mf": 60,
            "f": 72,
            "ff": 84,
            "fff": 96
        };
        for (let i = 0; i < rows.length; i++) {
            if (rows[i].dynamics == null){
                dynamics[i] = 0;
                continue;
            };
            const match = rows[i].dynamics?.match(/^([a-z]+)([+-]\d+)?$/i);
            const letters = match?.[1] ?? "";
            const number = match?.[2] ? Number(match[2]) : 0;
            const base = dynamicsMap[letters] ?? 0;
            const offset = number;
            dynamics[i] = (base + (offset * dynamicsFactor)) / 250;
        }
        
        const arcGen = d3.arc<any>()
            .innerRadius(radius * 0.5)
            .outerRadius(d => radius * (0.5 + d.thickness))
            .padAngle(0.001)
            .cornerRadius(5);
            
        const pie = d3.pie<PerformanceRow>()
            .sort(null)
            .startAngle(-Math.PI / 2)
            .endAngle(Math.PI / 2)
            .value(d => (60 / (d.tempo ?? 60)));
                
        const arcs = pie(rows).map((d, i) => ({
            ...d,
            thickness: dynamics[i] ?? 0,
            index: i
        }));
                
        const g = svgSel.append("g")
            .attr("transform", `translate(${width / 2}, ${height/1.05})`);
                        


        fillColorArray(minTimbre, diff);

        g.selectAll("path")
            .data(arcs)
            .enter()
            .append("path")
            .attr("class", "arc")
            .attr("d", arcGen)
            .attr("fill", (d, i) => colors[i])
            .on("click", (event, d) => {
                selectedRow = d.data;
            })
            .on("pointerdown", (event, d) => {
                if (brushEnabled) {
                    isDraggingSelection = true;
                    selectedMeasures = [];
                    dragStartIndex = d.index;
                }
            }).on("pointermove", (event, d) => {
                if (!isDraggingSelection || dragStartIndex == null) return;

                const start = Math.min(dragStartIndex, d.index);
                const end = Math.max(dragStartIndex, d.index);

                const selected = rows.slice(start, end + 1);

                selectedMeasures = selected;

                d3.selectAll("path.arc")
                    .classed("selected", (_, i) => i >= start && i <= end);
            })
            .on("pointerup", () => {
                isDraggingSelection = false;
                dragStartIndex = null;
            });

    }

</script>


<div bind:this={container} class="relative w-full h-[80vh]">

    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <svg
        bind:this={svg}
        class="w-full h-full"
        role="application"
        aria-label="Interactive performance visualization"
        onkeydown={() => {}}
        onpointerdown={() => {
            isDraggingSelection = true;
            selectedMeasures = [];
        }}
        onpointerup={() => {
            isDraggingSelection = false;
        }}
        onpointerleave={() => {
            isDraggingSelection = false;
        }}
    ></svg>

    {#if selectedRow && !brushEnabled}
    <div class="absolute bottom-10 left-1/2 -translate-x-1/2 bg-base-200 p-4 rounded-xl shadow-xl">
        <div>
            <h3 class="card-title">Measure {selectedRow.measure}</h3>
            <p> Tempo (bpm): {selectedRow.tempo}<br>
                Dynamics: {selectedRow.dynamics}<br>
                Spectral centroid (Hz): {selectedRow.timbre}
            </p>
        </div>
    </div>
    {/if}
    {#if brushEnabled && selectedMeasures && selectedMeasures.length > 0}
    <div class="absolute bottom-10 left-1/2 -translate-x-1/2 bg-base-200 p-4 rounded-xl shadow-xl">
        <h3 class="card-title">Selected range</h3>

        <p>
            Marked beats:
            {selectedMeasures[0].measure}
            –
            {selectedMeasures[selectedMeasures.length - 1].measure}
        </p>

        <p>
            Total selected beats:
            {selectedMeasures.length}
        </p>


        <button class="btn btn-block btn-warning mt-3" onclick={clearSelection}>
            Exit selection
        </button>
    </div>
    {/if}
    <div class="absolute top-4 left-4 bg-base-200 p-4 rounded-xl shadow-xl max-w-[10vw]">
        <label>
            <span class="card-title">Choose color scheme:</span>
            <select 
                class="select select-bordered w-full" 
                bind:value={selectedColorDropdown} 
                onchange={() => updateColors()}
            >
                <option value="viridisScheme">Viridis</option>
                <option value="infernoScheme">Inferno</option>
                <option value="cividisScheme">Cividis</option>
                <option value="bluesScheme">Blue shades</option>
                <option value="greensScheme">Green shades</option>
                <option value="redsScheme">Red shades</option>         
            </select>
        </label>
        <button class={`btn btn-sm btn-block mt-4 ${brushEnabled? "bg-base-300" : "btn-primary"}`} onclick={() => {
            brushEnabled = false;
            clearSelection();
            render();  
        }}>Select single beat</button>
        <button class={`btn btn-sm btn-block mt-4 ${brushEnabled? "btn-primary" : "bg-base-300"}`} onclick={() => {
            brushEnabled = true;
            clearSelection();
            render();  
        }}>Select multiple beats</button>

    </div>
    
</div>

<div class="relative bg-base-200 max-w-[55vw] p-4 left-1/2 -translate-x-1/2 rounded-xl shadow-xl">
    <h3 class="card-title">How to read this visualization</h3>
    <p>This graph visualizes three different parameters of performance data. Each slab represents one marked beat.</p>
    <ol class="list-decimal pl-6">
        <li>The <u>tempo</u> of the beat determines the size of the slab's <b>angle</b>, i.e. a "thicker" slab 
            denotes a longer/slower performed beat.</li>
        <li>The <u>dynamics</u> value of the beat decides the <b>length</b> of a slab; a longer slab 
            is louder than a shorter slab.</li>
        <li>The <b>color</b> of a slab represents the detected <u>spectral centroid</u> of the beat. 
            A lighter color denotes a higher value, i.e. a "brighter" perceived sound.</li>
    </ol>
    <h3 class="card-title mt-2">Additional options</h3>
    <p>If you find a different color scheme than the default <i>Viridis</i> scheme more helpful, 
        you may choose among several options in the upper left corner. Clicking on a slab shows information 
        about the according beat in the upper right corner.</p>
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