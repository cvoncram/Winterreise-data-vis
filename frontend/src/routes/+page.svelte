<script lang="ts">

    import Timeline from '$lib/components/containers/Timeline.svelte';
    import {onMount} from 'svelte';
	import PerfMap from '$lib/components/containers/PerfMap.svelte';
	import type { PerformanceDetailed } from '$lib/types';

    let performances = $state<PerformanceDetailed[] | undefined>(undefined);
    let viewMap = $state(false);
    let mapLabel = $derived("View as map");
    let error = $state("");
    
    onMount(async () => {
        try {
            const results = await fetch(`/db/performances-detailed`);
            const data = await results.json();
            performances = data.map((p: any) => ({
                year: p.year,
                date: p.date,
                place: p.place,
                placeAddendum: p.place_addendum,
                coordinates: p.coordinates,
                pianist: p.pianist,
                recordingContext: p.recording_context,
                misc: p.misc
            }))

        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    })

    $effect(() => {
        if (viewMap == true) {
            mapLabel = "View as timeline"
        } else {
            mapLabel = "View as map"
        }
    })

</script>

<div class="relative flex flex-col items-center px-[10%] h-full overflow-hidden">
    <div 
    class="absolute inset-0 bg-cover bg-center opacity-50"
    style="background-image: url('/Winterreise_manuscript.jpg');">
    </div>


    <div class="relative bg-base-100 p-10 rounded-md shadow-xl opacity-85 w-full">
        <div class="w-2/3 opacity-85 p-10 text-center mx-auto">
            <h3 class="text-5xl mb-5"><i>Winterreise</i> and Dietrich Fischer-Dieskau</h3>
            <div class="text-l mb-5">Franz Schubert composed the song cycle <i>Winterreise</i> for voice and piano shortly before his death in 1827. 
                Famous German baritone Dietrich Fischer-Dieskau had great influence on its reception in the 20th century, performing it more than 130 times
                in an extraordinarily long period of time from 1943 to 1991.<br><br>
                This project aims to accomplish twofold: First, creating an <i>Interpretationsedition</i> based on Fischer-Dieskaus personal copy; incorporating 
                his interpretative markings and directives. Second, examining 26 recordings from 1948 to 1990 by Fischer-Dieskau and 12 different pianists more
                closely, extracting audio analysis data and comparing these recordings to each other on the grounds of tempo, dynamics, and timbre data. 
            </div>
        </div>


        <h3 class="text-3xl mb-5 text-center">Where and when the recordings originated
            <p class="float-right">{mapLabel}
                <input type="checkbox" class="toggle text-xl" onchange={() => {viewMap = !viewMap}} /> 
            </p>
        </h3>
        
        <div class="w-full h-125">
            {#if viewMap}
                <div class="w-full h-full">
                    <PerfMap {performances}/>
                </div>
            {:else}
                <div class="w-full h-full">
                    <Timeline {performances}/>
                </div>
            {/if}  
        </div>
    </div>
</div>
