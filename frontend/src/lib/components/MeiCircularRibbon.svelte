<script lang="ts">
    import { onMount, tick } from "svelte";
    import * as d3 from "d3";
    import type { PerformanceRow, PerformanceMetadata } from "$lib/components/MeiTable.svelte";

    let svg: SVGSVGElement;
    let container: HTMLDivElement;

    let width = 0;
    let height = 0;

    export let rows: PerformanceRow[] = [];
    export let metadata: PerformanceMetadata | null = null;
    let selectedRow: PerformanceRow | null = null;

    let resizeObserver: ResizeObserver;

    let brushEnabled = false;

    onMount(() => {
        resizeObserver = new ResizeObserver(() => {
            updateSize();
        });

        resizeObserver.observe(container);

        updateSize();       

        return () => resizeObserver.disconnect();
    });

    function updateSize() {
        width = container.clientWidth;
        height = container.clientHeight;
    }

    let selectedColorDropdown = "viridisScheme";    

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


    function brushed(event: any) {
        const selection = event.selection;
        if (!selection) return;

        const [[x0, y0], [x1, y1]] = selection;

        d3.select(svg)
            .selectAll<SVGPathElement, any>("path.arc")
            .classed("selected", function() {
                const bbox = this.getBBox();

                return (
                    bbox.x < x1 &&
                    bbox.x + bbox.width > x0 &&
                    bbox.y < y1 &&
                    bbox.y + bbox.height > y0
                );
            });
    }

    
    let colors: string[] = [""];
    
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
    
    
    
    $: if (rows.length && width > 0 && height > 0) {
        tick().then(render);
        
    }

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
        
        const radius = Math.min(width, height)/ 1.1;
        
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
            .innerRadius(radius * 0.6)
            .outerRadius(d => radius * (0.6 + d.thickness))
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
        }));
                
        const g = svgSel.append("g")
            .attr("transform", `translate(${width / 2}, ${height/1})`);
                
        if (brushEnabled) {
            const brush = d3.brush()
                .on("brush end", brushed);

            svgSel.append("g")
                .attr("class", "brush")
                .call(d3.brush().on("brush", brushed));
        }

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
            });

    }

</script>


<div bind:this={container} class="relative w-full h-full">

    <svg bind:this={svg} class="w-full h-full"></svg>

    {#if selectedRow}
    <div class="absolute top-4 right-4 bg-base-200 p-4 rounded-xl shadow-xl">
        <div>
            <h3 class="card-title">Measure {selectedRow.measure}</h3>
            <p> Tempo (bpm): {selectedRow.tempo}<br>
                Dynamics: {selectedRow.dynamics}<br>
                Spectral centroid (Hz): {selectedRow.timbre}
            </p>
        </div>
    </div>
    {/if}
    <div class="absolute top-4 left-4 bg-base-200 p-4 rounded-xl shadow-xl">
        <label>
            <span class="card-title">Choose color scheme:</span>
            <select 
                class="select select-bordered w-full" 
                bind:value={selectedColorDropdown} 
                on:change={() => updateColors()}
            >
                <option value="viridisScheme">Viridis</option>
                <option value="infernoScheme">Inferno</option>
                <option value="cividisScheme">Cividis</option>
                <option value="bluesScheme">Blue shades</option>
                <option value="greensScheme">Green shades</option>
                <option value="redsScheme">Red shades</option>         
            </select>
        </label>
        <button class="btn btn-sm btn-secondary btn-block mt-4" on:click={() => {
            brushEnabled = !brushEnabled; 
            render();  
        }}>{brushEnabled ? "Disable selection" : "Enable selection"}
        </button>

    </div>
    <div class="absolute bottom-2 bg-base-200 max-w-[25vw] p-4 left-1/2 -translate-x-1/2 rounded-xl shadow-xl">
        <h3 class="card-title">About this visualization</h3>
        <p>This graph visualizes three different parameters of performance data. Each slab represents one marked beat.</p>
        <ol class="list-decimal pl-6">
            <li>The <u>tempo</u> of the beat determines the size of the slab's <b>angle</b>, i.e. a "thicker" slab 
                denotes a longer/slower performed beat.</li>
            <li>The <u>dynamics</u> value of the measure decides how <b>long</b> a slab is; a longer slab 
                is louder than a shorter slab.</li>
            <li>The <b>color</b> of a slab represents the detected <u>spectral centroid</u> of the beat. 
                A lighter color denotes a higher value, i.e. a "brighter" perceived sound.</li>
        </ol>
        <p>If you find a different color scheme than the default <i>Viridis</i> scheme more helpful, 
            you may choose among several options in the upper left corner. Clicking on a slab shows information 
            about the according beat in the upper right corner.</p>
    </div>

</div>

<style>
    :global(path.arc:hover) {
    filter: brightness(1.4);
    }

    :global(path.arc.selected) {
    stroke: white;
    stroke-width: 2;
    } 
</style>