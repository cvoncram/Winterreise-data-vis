<script lang=ts>
    import * as d3 from "d3";
    import {onMount} from "svelte";

    let {nodes, links, linkWidth = $bindable(), linkLength = $bindable()}: {
        nodes: { id: number }[];
        links: {
            source: number;
            target: number;
            distance: number;
        }[];
        linkWidth: number;
        linkLength: number;
    } = $props();
    
    let linkSelection = $state<d3.Selection< SVGLineElement, typeof links[number], SVGGElement, unknown >>();
    let simulation = $state<d3.Simulation<GraphNode, GraphLink>>();

    let container: HTMLDivElement;
    
    
    const width = 1600;
    const height = 680;
    
    interface GraphNode extends d3.SimulationNodeDatum {
        id: number;
    }
    
    interface GraphLink extends d3.SimulationLinkDatum<GraphNode> {
        distance: number;
    }

    $effect(() => {
        if (linkSelection) {
            linkSelection.attr(
            "stroke-width",
            d => linkWidth / d.distance
            );
        }
    });

    $effect(() => {
        if (!simulation) return;
        simulation.force(
        "link",
        d3.forceLink<GraphNode, GraphLink>(links)
        .distance(d => d.distance * linkLength)
        );
        simulation.alpha(1).restart();
    });

    onMount(() => {
        const node = createDtwNetwork(linkWidth, linkLength);
        if (node) container.appendChild(node);
    });

    function createDtwNetwork(linkWidth: number, linkLength: number){
        simulation = d3.forceSimulation<GraphNode>(nodes)
            .force("link", d3.forceLink<GraphNode, GraphLink>(links).distance(d => d.distance * linkLength))
            .force("charge", d3.forceManyBody())
            .force("x", d3.forceX())
            .force("y", d3.forceY());
            
            const svg = d3.create("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [-width / 2, -height / 2, width, height])
            .attr("style", "max-width: 100%; height: auto;");
            
            linkSelection = svg.append("g")
            .attr("stroke", "#668ba4")
            .attr("stroke-opacity", 0.8)
            .selectAll<SVGLineElement, typeof links[number]>("line")
            .data(links)
            .join("line")
            .attr("stroke-width", d => linkWidth / d.distance);
            
            const node = svg.append("g")
            .attr("stroke", "#fff")
            .attr("stroke-width", 1.5)
            .selectAll("circle")
            .data(nodes)
            .join("circle")
            .attr("r", 5);
            
            node.append("title")
            .text(d => d.id);
            simulation.on("tick", () => {
                if (linkSelection) linkSelection
                .attr("x1", d => (d.source as any).x)
                .attr("y1", d => (d.source as any).y)
                .attr("x2", d => (d.target as any).x)
                .attr("y2", d => (d.target as any).y);
                node
                .attr("cx", d => (d as any).x)
                .attr("cy", d => (d as any).y);
            });
            
            return svg.node();
            
        }
        
    </script>

    <div bind:this={container} class="w-full h-full"></div>