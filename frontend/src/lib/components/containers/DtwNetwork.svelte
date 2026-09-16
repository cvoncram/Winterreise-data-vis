<script lang=ts>
    import * as d3 from "d3";
    import { untrack } from "svelte";
    import SvgDownloadButton from '$lib/components/partials/SvgDownloadButton.svelte';
    let svgContainer: HTMLDivElement | undefined = $state();

    let {nodes, links, linkWidth = $bindable(), nodeSize = $bindable(), onMoreInfo,
         nodeColours = [], legend = []}: {
        nodes: { id: number; label?: string; }[];
        links: { source: number; target: number; distance: number; cost: number; tau: number | null; }[];
        linkWidth: number;
        nodeSize: number;
        onMoreInfo?: (source: number, target: number) => void;
        /** One colour per node id; empty leaves every node in the default fill. */
        nodeColours?: string[];
        legend?: { label: string; colour: string }[];
    } = $props();

    const DEFAULT_FILL = "#EDEFC4";

    const maxDistance = $derived(Math.max(...links.map(d => d.distance)));

    let popup: HTMLDivElement;

    let width = $state(0);
    let height = $state(0);

    interface GraphNode extends d3.SimulationNodeDatum {
        id: number;
        label?: string;
    }

    interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
        distance: number;
        cost: number;
        tau: number | null;
    }

    function displayNodeInfo(node: GraphNode) {
        return node.label ?? "";
    }

    function displayLinkInfo(link: GraphLink) {
        return `${(link.source as GraphNode).label} <---> ${(link.target as GraphNode).label}`
            + `\n<b>DTW cost (absolute)</b>: ${link.cost.toFixed(1)}`
            + `\n<b>Kendall's τ</b>: ${link.tau !== null ? link.tau.toFixed(3) : "n/a"}`
            // The popup itself ignores the pointer so that it never swallows a
            // click meant for the graph; the button takes it back.
            + (onMoreInfo ? `\n<button data-more class="btn btn-xs btn-primary pointer-events-auto mt-1">More information</button>` : "");
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
        let simulation: d3.Simulation<GraphNode, GraphLink> | null = null;
        let linkSelection: d3.Selection<SVGLineElement, GraphLink, SVGGElement, unknown> | null = null;
        let nodeSelection: d3.Selection<SVGCircleElement, GraphNode, SVGGElement, unknown> | null = null;
        let svgSelection: d3.Selection<SVGSVGElement, undefined, null, undefined> | null = null;
        let legendSelection: d3.Selection<SVGGElement, undefined, null, undefined> | null = null;
        let zoom: d3.ZoomBehavior<SVGSVGElement, undefined> | null = null;

        /** Writes the measured box onto the existing SVG, without rebuilding it. */
        function applySize(w: number, h: number) {
            if (!svgSelection || w === 0 || h === 0) return;
            svgSelection
                .attr("width", w)
                .attr("height", h)
                .attr("viewBox", `${-w / 2} ${-h / 2} ${w} ${h}`);
            zoom?.extent([[0, 0], [w, h]]);
            // Pinned to the top left corner of whatever box the SVG now has.
            legendSelection?.attr("transform", `translate(${-w / 2 + 12}, ${-h / 2 + 16})`);
        }

        $effect(() => {
            const currentNodes = nodes.map(n => ({...n})) as GraphNode[];
            const currentLinks = links.map(l => ({...l})) as GraphLink[];

            if (currentNodes.length === 0) return;

            // Read once, untracked: the sliders and the colouring are applied by
            // the effects below, and depending on them here would rebuild the
            // whole simulation whenever one of them moves — which also threw
            // away the node colours.
            const currentNodeSize = untrack(() => nodeSize);
            const currentLinkWidth = untrack(() => linkWidth);
            const currentColours = untrack(() => nodeColours);

            simulation?.stop();
            container.innerHTML = '';

            simulation = d3.forceSimulation<GraphNode>(currentNodes)
                .force("link", d3.forceLink<GraphNode, GraphLink>(currentLinks).distance(d => (d.distance * 8) / maxDistance * 100))
                .force("charge", d3.forceManyBody())
                .force("x", d3.forceX())
                .force("y", d3.forceY());

            const svg = d3.create("svg")
                .attr("style", "max-width: 100%;");

            zoom = d3.zoom<SVGSVGElement, undefined>()
                .scaleExtent([.2, 8])
                .filter(event => {
                    if (event.type === 'wheel') return true;
                    return !(event.target as Element).closest("circle");
                })
                .on("zoom", (event: d3.D3ZoomEvent<SVGSVGElement, undefined>) => {
                    svg.select("g").attr("transform", event.transform.toString());
                    hidePopup();
                });
            svg.call(zoom);

            svgSelection = svg;
            applySize(untrack(() => width), untrack(() => height));

            const g = svg.append("g");

            linkSelection = g.append("g")
                .attr("stroke", "#668ba4")
                .attr("stroke-opacity", 0.9)
                .selectAll<SVGLineElement, GraphLink>("line")
                .data(currentLinks)
                .join("line")
                .attr("stroke-width", d => currentLinkWidth / d.distance)
                .on("click", (event, d) => {
                    event.stopPropagation();
                    showPopup(event, displayLinkInfo(d));
                    popup.querySelector("[data-more]")?.addEventListener("click", () => {
                        hidePopup();
                        onMoreInfo?.((d.source as GraphNode).id, (d.target as GraphNode).id);
                    });
                });

            nodeSelection = g.append("g")
                .attr("stroke", "#009E37")
                .attr("stroke-width", 1.5)
                .selectAll<SVGCircleElement, GraphNode>("circle")
                .data(currentNodes)
                .join("circle")
                .attr("r", currentNodeSize)
                .attr("fill", d => currentColours[d.id] ?? DEFAULT_FILL)
                .on("click", (event, d) => {
                    event.stopPropagation();
                    showPopup(event, displayNodeInfo(d));
                });

            simulation.on("tick", () => {
                linkSelection!
                    .attr("x1", d => (d.source as any).x)
                    .attr("y1", d => (d.source as any).y)
                    .attr("x2", d => (d.target as any).x)
                    .attr("y2", d => (d.target as any).y);
                nodeSelection!
                    .attr("cx", d => (d as any).x)
                    .attr("cy", d => (d as any).y);
            });

            nodeSelection.call(d3.drag<SVGCircleElement, GraphNode>()
                .on("start", (event) => {
                    if (!event.active) simulation?.alphaTarget(0.3).restart();
                    event.subject.fx = event.subject.x;
                    event.subject.fy = event.subject.y;
                })
                .on("drag", (event) => {
                    event.subject.fx = event.x;
                    event.subject.fy = event.y;
                })
                .on("end", (event) => {
                    if (!event.active) simulation?.alphaTarget(0);
                    event.subject.fx = null;
                    event.subject.fy = null;
                }));

            legendSelection = svg.append("g").attr("class", "legend");
            untrack(drawLegend);
            applySize(untrack(() => width), untrack(() => height));

            container.appendChild(svg.node()!);
        });

        /** Rebuilds the key; cheap enough that changing it need not rebuild the graph. */
        function drawLegend() {
            if (!legendSelection) return;
            legendSelection.selectAll("*").remove();
            legend.forEach((entry, i) => {
                const row = legendSelection!.append("g").attr("transform", `translate(0, ${i * 18})`);
                row.append("rect")
                    .attr("width", 12).attr("height", 12)
                    .attr("fill", entry.colour)
                    .attr("stroke", "currentColor").attr("stroke-opacity", 0.3);
                row.append("text")
                    .attr("x", 18).attr("y", 10)
                    .attr("font-size", 12).attr("fill", "currentColor")
                    .text(entry.label);
            });
        }

        $effect(() => {
            nodeSelection?.attr("fill", d => nodeColours[d.id] ?? DEFAULT_FILL);
            drawLegend();
        });

        $effect(() => {
            applySize(width, height);
        });

        $effect(() => {
            if (!linkSelection || !nodeSelection) return;
            linkSelection.attr("stroke-width", d => linkWidth / d.distance);
            nodeSelection.attr("r", nodeSize);
        });

        return () => {
            simulation?.stop();
            container.innerHTML = '';
        };
    }
</script>

<div {@attach attachGraph} bind:this={svgContainer} bind:clientWidth={width} bind:clientHeight={height} class="w-full h-screen border-2 border-primary rounded-xl"></div>
<div bind:this={popup} class="fixed bg-base-200 shadow-md rounded p-2 text-sm pointer-events-none hidden whitespace-pre-line"></div>
<div class="flex justify-end">
    <SvgDownloadButton container={svgContainer} filename="dtw-network" />
</div>