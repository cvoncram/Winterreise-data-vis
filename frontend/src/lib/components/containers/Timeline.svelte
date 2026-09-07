<script lang="ts">
    import type { PerformanceDetailed } from "$lib/types";
    import * as d3 from 'd3';

    let {performances}: {performances: PerformanceDetailed[]| undefined} = $props();

    let width = $state(0);
    let clickContentDate = $state("");
    let clickContentPlace = $state("");
    let clickContentPlaceAdd = $state("");
    let clickContentPianist = $state("");
    let clickContentYear = $state(0);
    let clickContentRecContext = $state("");
    let clickContentMisc = $state("");
    let clickContentInfo = $state("");
    let clickContentNoInOrder = $state(0);

    let clickElement: HTMLDialogElement;

    function lastName(fullName: string){
        return fullName.split(" ")[1];
    }

    function determineYIndex(performances: PerformanceDetailed[]): number[] {
        let yIndices = [0];

        for (let i = 1; i < performances.length; i++) {
            if (performances[i].year === performances[i-1].year) {
                yIndices[i] = yIndices[i-1] + 1;
            } else {
                yIndices[i] = 0
            }  
        }
        return yIndices;
    }

    function handleClick(event: Event){
        const target = event.target as Element;

        const rectEl = target.closest("rect") as SVGElement;
        const textEl = target.closest("text.label-text") as SVGElement;
        if ((!rectEl && !textEl) || !performances) return;

        let element: SVGElement = (rectEl)? rectEl : textEl;
        const id = parseInt(element.getAttribute("perf-id") ?? "NaN");

        clickContentNoInOrder = id + 1;
        clickContentPlaceAdd = (performances[id].placeAddendum != "")? ", " + performances[id].placeAddendum : " (exact place unknown)";
        clickContentDate = performances[id].date;
        clickContentPlace = `${performances[id].place}${clickContentPlaceAdd}`;
        clickContentPianist = performances[id].pianist;
        clickContentYear = performances[id].year;
        clickContentMisc = performances[id].misc;
        clickContentRecContext = performances[id].recordingContext;
        clickContentInfo = performances[id].onlineInfo;
        clickElement?.showModal();
        
    }
    

    function createTimeline(performances: PerformanceDetailed[], width: number) {

        const height = 500;
        const margin = 20;
        const yIndex = determineYIndex(performances);

        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height);

        const g = svg.append("g")
            .attr("transform", `translate(${margin}, ${margin}, ${margin}, ${margin})`);

        const x = d3.scaleLinear([1945, 2000], [margin, width - margin]);
        const boxWidth = width/30;
        const color = d3.scaleOrdinal(d3.schemeCategory10);

        const rectXs = performances.map(d => (x(d.year) - boxWidth/2));
        const barHeight = (() => {
            if (width < 1500){
            return boxWidth * 3
            } else if (width >= 1500 && width < 2300) {
                return boxWidth * 2
            } else {
                return boxWidth;
            }
        })();
        const gap = 2;
        const rectY = height - barHeight - margin;
        const yShift = yIndex.map(v => v * (barHeight + gap));

        g.append("g")
            .attr("class", "bars")
            .selectAll("rect")
            .data(performances)
            .join("rect")
                .attr("fill", (d, i) => color(String(i)))
                .attr("x", (d, i) => rectXs[i])
                .attr("y", (d, i) => rectY - yShift[i])
                .attr("height", barHeight)
                .attr("width", boxWidth)
                .attr("perf-id", (d, i) => i);

        svg.selectAll("text")
            .data(performances)
            .join("text")
            .attr('transform', (d, i) => {
                return 'translate( '+(rectXs[i] + boxWidth / 2) +' , '+(rectY - (yShift[i]) + barHeight / 2)+'),'+ 'rotate(90)';})
            .attr("x", 0)
            .attr("y", 0)
            .attr("text-anchor", "middle")
            .attr("dominant-baseline", "middle")
            .attr("fill", "white")
            .attr("class", "label-text")
            .attr("perf-id", (d, i) => i)
            .text(d => (lastName(d.pianist) + " " + d.year));

        g.append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0, ${(height - margin)})`)
            .call(d3.axisBottom(x).tickFormat(d3.format("d")));

        return svg.node();
    }

    function attachGraph(node: HTMLDivElement) {
        node.addEventListener("click", handleClick);
        $effect(() => {
            if (!performances || performances.length === 0) return;
            node.innerHTML = '';
            const svg = createTimeline(performances, width);
            if (svg) node.appendChild(svg);
        });
        return () => {
            node.innerHTML = '';
            node.removeEventListener("click", handleClick)
        };
    }

</script>

<div {@attach attachGraph} bind:clientWidth={width}></div>

<dialog bind:this={clickElement} class="modal">
    <div class="modal-box">
        <form method="dialog">
            <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
        </form>
        <h3 class="text-lg font-bold">{clickContentNoInOrder}. {lastName(clickContentPianist)} {clickContentYear}</h3>
        <p>Date: {clickContentDate}</p>
        <p>Pianist: {clickContentPianist}</p>
        <p>Place: {clickContentPlace}</p>
        <p>Recording Context: {clickContentRecContext}</p>
        {#if (clickContentInfo != "no value")}<p><a style="color: blue; text-decoration: underline;" href={clickContentInfo}>Click here for further information</a> (you will be redirected to an external site)</p>{/if}
        {#if (clickContentMisc != "")}<p>{clickContentMisc}</p>{/if}
        
    </div>
    <form method="dialog" class="modal-backdrop">
        <button>close</button>
    </form>
</dialog>

<style>
    :global(rect) {
        cursor: pointer;
    }

    :global(svg text) {
        cursor: pointer;
    }

    .modal-box {
        line-height: 3vh;
    }
</style>
