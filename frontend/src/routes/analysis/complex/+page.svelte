<script lang=ts>
    import SliderControl from "$lib/components/partials/SliderControl.svelte";
    import DtwNetwork from "$lib/components/containers/DtwNetwork.svelte";

    let linkWidth = $state(200);
    let nodeSize = $state(10);
    
    
    const testNodes = [{id:0, label: "arsch"}, {id:1, label: "penis"}, {id:2, label:"schwanz"}, {id:3, label:"pöter"}, {id:4, label:"fotzenfritz"}, {id:5}, {id:6}, {id:7}, {id:8}, {id:9}];
    const testLinks = [
    { source: 0, target: 1, distance: 57.7 },
    { source: 0, target: 2, distance: 49.2 },
    { source: 0, target: 3, distance: 162.4 },
    { source: 0, target: 4, distance: 79.8 },
    { source: 0, target: 5, distance: 82.7 },
    { source: 0, target: 6, distance: 92.0 },
    { source: 0, target: 7, distance: 176.2 },
    { source: 0, target: 8, distance: 84.7 },
    { source: 0, target: 9, distance: 166.0 },
    { source: 1, target: 2, distance: 18.4 },
    { source: 1, target: 3, distance: 132.0 },
    { source: 1, target: 4, distance: 97.7 },
    { source: 1, target: 5, distance: 113.0 },
    { source: 1, target: 6, distance: 159.6 },
    { source: 1, target: 7, distance: 160.1 },
    { source: 1, target: 8, distance: 121.4 },
    { source: 1, target: 9, distance: 143.8 },
    { source: 2, target: 3, distance: 129.6 },
    { source: 2, target: 4, distance: 86.9 },
    { source: 2, target: 5, distance: 173.9 },
    { source: 2, target: 6, distance: 107.1 },
    { source: 2, target: 7, distance: 162.8 },
    { source: 2, target: 8, distance: 90.3 },
    { source: 2, target: 9, distance: 157.4 },
    { source: 3, target: 4, distance: 32.4 },
    { source: 3, target: 5, distance: 24.5 },
    { source: 3, target: 6, distance: 28.9 },
    { source: 3, target: 7, distance: 151.7 },
    { source: 3, target: 8, distance: 91.5 },
    { source: 3, target: 9, distance: 108.6 },
    { source: 4, target: 5, distance: 31.6 },
    { source: 4, target: 6, distance: 25.3 },
    { source: 4, target: 7, distance: 81.0 },
    { source: 4, target: 8, distance: 153.9 },
    { source: 4, target: 9, distance: 124.6 },
    { source: 5, target: 6, distance: 44.3 },
    { source: 5, target: 7, distance: 155.0 },
    { source: 5, target: 8, distance: 94.5 },
    { source: 5, target: 9, distance: 107.2 },
    { source: 6, target: 7, distance: 132.9 },
    { source: 6, target: 8, distance: 169.7 },
    { source: 6, target: 9, distance: 149.7 },
    { source: 7, target: 8, distance: 21.3 },
    { source: 7, target: 9, distance: 21.3 },
    { source: 8, target: 9, distance: 45.2 }
    ];
        
</script>
    
<div class="flex h-auto overflow-hidden">
    <aside class="w-64 shrink-0 bg-base-200 p-4 items-center flex flex-col justify-center gap-4">
        
        <div class="card bg-base-200 p-4 shadow-md justify-start">
            <SliderControl
            label="Link width"
            min={10}
            max={400}
            value={linkWidth}
            onChange={(w) => { linkWidth = w}}
            />
            <SliderControl
            label="Node size"
            min={1}
            max={20}
            value={nodeSize}
            onChange={(w) => { nodeSize = w}}
            />
        </div>
    </aside>
    
    <main class="flex-1 flex flex-col p-10 overflow-hidden">
        <div style="background-color: rgba(254, 255, 223, .2);" class="border-2 border-[#668ba4] rounded-xl bg-base-200">
            <DtwNetwork links={testLinks} nodes={testNodes} bind:linkWidth={linkWidth} bind:nodeSize={nodeSize} />   
        </div>
    </main>
    
</div>