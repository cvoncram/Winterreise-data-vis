<script lang=ts>
    import * as d3 from "d3";

    let {nodes, links, linkWidth = $bindable(), nodeSize = $bindable()}: {
        nodes: { id: number; label?: string; }[];
        links: { source: number; target: number; distance: number; }[];
        linkWidth: number;
        nodeSize: number;
    } = $props();

    const maxDistance = $derived(Math.max(...links.map(d => d.distance)));

    let popup: HTMLDivElement;

    const width = 1600;
    const height = 680;

    interface GraphNode extends d3.SimulationNodeDatum {
        id: number;
        label?: string;
    }

    interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
        distance: number;
    }

    function displayNodeInfo(node: GraphNode) {
        return node.label ?? "";
    }

    function displayLinkInfo(link: GraphLink) {
        return `${(link.source as GraphNode).label}, ${(link.target as GraphNode).label}, relative similarity: ${(100 - (link.distance / maxDistance * 100)).toFixed(2)}%`;
    }

    function showPopup(event: MouseEvent, content: string) {
        popup.innerHTML = content;
        popup.classList.remove("hidden");
        popup.style.left = `${event.clientX + 12}px`;
        popup.style.top = `${event.clientY + 12}px`;
    }

    function hidePopup() {
        popup.classList.add("hidden");
    }

    function attachGraph(container: HTMLDivElement) {
        const simulation = d3.forceSimulation<GraphNode>(nodes)
            .force("link", d3.forceLink<GraphNode, GraphLink>(links).distance(d => (d.distance * 8) / maxDistance * 100))
            .force("charge", d3.forceManyBody())
            .force("x", d3.forceX())
            .force("y", d3.forceY());

        const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [-width / 2, -height / 2, width, height])
            .attr("style", "max-width: 100%; height: auto;");

        svg.on("click", () => hidePopup());

        svg.call(d3.zoom<SVGSVGElement, undefined>()
            .extent([[0, 0], [width, height]])
            .scaleExtent([1, 8])
            .on("zoom", (event: d3.D3ZoomEvent<SVGSVGElement, undefined>) => {
                svg.attr("transform", event.transform.toString());
                hidePopup();
            }));

        const linkSelection = svg.append("g")
            .attr("stroke", "#668ba4")
            .attr("stroke-opacity", 0.8)
            .selectAll<SVGLineElement, GraphLink>("line")
            .data(links as GraphLink[])
            .join("line")
            .attr("stroke-width", d => linkWidth / d.distance)
            .on("click", (event, d) => {
                event.stopPropagation();
                showPopup(event, displayLinkInfo(d));
            });

        const nodeSelection = svg.append("g")
            .attr("stroke", "yellow")
            .attr("fill", "green")
            .attr("stroke-width", 1.5)
            .selectAll<SVGCircleElement, GraphNode>("circle")
            .data(nodes as GraphNode[])
            .join("circle")
            .attr("r", nodeSize)
            .on("click", (event, d) => {
                event.stopPropagation();
                showPopup(event, displayNodeInfo(d));
            });

        simulation.on("tick", () => {
            linkSelection
                .attr("x1", d => (d.source as any).x)
                .attr("y1", d => (d.source as any).y)
                .attr("x2", d => (d.target as any).x)
                .attr("y2", d => (d.target as any).y);
            nodeSelection
                .attr("cx", d => (d as any).x)
                .attr("cy", d => (d as any).y);
        });

        const svgNode = svg.node()!;
        container.appendChild(svgNode);

        $effect(() => {
            linkSelection.attr("stroke-width", d => linkWidth / d.distance);
            nodeSelection.attr("r", nodeSize);
        });

        return () => {
            simulation.stop();
            container.innerHTML = '';
        };
    }
</script>

<div {@attach attachGraph} class="w-full h-full overflow-auto"></div>
<div bind:this={popup} class="fixed bg-base-200 shadow-md rounded p-2 text-sm pointer-events-none hidden"></div>