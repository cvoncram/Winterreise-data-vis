<script lang=ts>
    import SliderControl from "$lib/components/partials/SliderControl.svelte";
    import DtwNetwork from "$lib/components/containers/DtwNetwork.svelte";

    let linkWidth = $state(200);
    let linkLength = $state(5);
    
    
    const testNodes = [{id:0}, {id:1}, {id:2}, {id:3}, {id:4}, {id:5}, {id:6}, {id:7}, {id:8}, {id:9}];
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
    
    <div class="flex">
        <div class="fixed top-0 left-0 h-full w-64 bg-base-200 p-4 flex flex-col justify-center items-center gap-4 z-10">
            
            <div class="card bg-base-200 p-4 shadow-md justify-start">
                <SliderControl
                label="Link width"
                min={10}
                max={400}
                value={linkWidth}
                onChange={(w) => { linkWidth = w}}
                />
                <SliderControl
                label="Link length"
                min={1}
                max={20}
                value={linkLength}
                onChange={(w) => { linkLength = w}}
                />
            </div>
        </div>
        
        <div class="ml-64 mt-15 p-4">
            <DtwNetwork links={testLinks} nodes={testNodes} bind:linkWidth={linkWidth} bind:linkLength={linkLength} />   
        </div>
        
    </div>