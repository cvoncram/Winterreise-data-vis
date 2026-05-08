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
            return d3.interpolateGreens(color);
        } else if (selectedColorDropdown == "bluesScheme") {
            return d3.interpolateBlues(color);
        } else if (selectedColorDropdown == "redsScheme") {
            return d3.interpolateReds(color);
        } else {
            return "";
        }
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
    <div class="absolute bottom-8 left-1/2 -translate-x-1/2 bg-base-200 p-4 rounded">
        <div>Measure.beat: {selectedRow.measure}<br>
            Tempo (bpm): {selectedRow.tempo}<br>
            Dynamics: {selectedRow.dynamics}<br>
            Spectral centroid (Hz): {selectedRow.timbre}
        </div>
    </div>
    {/if}
    <div class="absolute bottom-40 left-1/2 -translate-x-1/2 bg-base-200 p-4 rounded">
        <label>
            <span>Choose color scheme:</span>
            <select 
                class="select select-bordered w-full" 
                bind:value={selectedColorDropdown} 
                on:change={(e) => updateColors()}
            >
                <option value="viridisScheme">Viridis</option>
                <option value="infernoScheme">Inferno</option>
                <option value="cividisScheme">Cividis</option>
                <option value="bluesScheme">Blue shades</option>
                <option value="greensScheme">Green shades</option>
                <option value="redsScheme">Red shades</option>         
            </select>
        </label>
    </div>

</div>

<style>
    :global(path.arc:hover) {
    filter: brightness(1.4);
    }   
</style>