<script lang="ts">
    import type { PerformanceDetailed } from "$lib/types";
    import * as d3 from 'd3';

    let {performances}: {performances: PerformanceDetailed[]| undefined} = $props();

    let width = $state(0);

    let popup: HTMLDivElement;

    function showPopup(event: MouseEvent, content: string) {
        popup.innerHTML = content;
        popup.classList.remove("hidden");

        const popupWidth = popup.offsetWidth;
        const popupHeight = popup.offsetHeight;

        popup.style.left = `${event.clientX - popupWidth - 12}px`;
        popup.style.top = `${event.clientY - popupHeight - 12}px`;
    }

    function lastName(fullName: string){
        return fullName.split(" ")[1];
    }

    function hidePopup() {
        popup.classList.add("hidden");
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

    function createTimeline(performances: PerformanceDetailed[], width: number) {

        const height = 500;
        const margin = 20;

        const yIndex = determineYIndex(performances);
        $inspect(yIndex);

        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .on("click", (event: MouseEvent, _) => {
                event.stopPropagation();
                hidePopup();
            });

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
                .on("click", (event: MouseEvent, d) => {
                    event.stopPropagation();
                    showPopup(event, `${d.pianist}, ${d.place} ${d.year}`)
                });

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
            .on("click", (event: MouseEvent, d) => {
                event.stopPropagation();
                showPopup(event, `${d.pianist}, ${d.place} ${d.year}`)
            })
            .text(d => (lastName(d.pianist) + " " + d.year));

        g.append("g")
            .attr("class", "x-axis")
            .attr("transform", `translate(0, ${(height - margin)})`)
            .call(d3.axisBottom(x).tickFormat(d3.format("d")));

        return svg.node();
    }

    function attachGraph(node: HTMLDivElement) {
        $effect(() => {
            if (!performances || performances.length === 0) return;
            node.innerHTML = '';
            const svg = createTimeline(performances, width);
            if (svg) node.appendChild(svg);
        });
        return () => { node.innerHTML = ''; };
    }

</script>

<div {@attach attachGraph} bind:clientWidth={width}></div>
<div bind:this={popup} class="fixed bg-base-200 shadow-md rounded p-2 text-sm pointer-events-none hidden whitespace-pre-line"></div>

<style>
    :global(rect) {
        cursor: pointer;
    }

    :global(svg text) {
        cursor: pointer;
    }
</style>
