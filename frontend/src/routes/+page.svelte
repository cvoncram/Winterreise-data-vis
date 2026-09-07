<script lang="ts">

    import Timeline from '$lib/components/containers/Timeline.svelte';
    import {onMount} from 'svelte';
	import PerfMap from '$lib/components/containers/PerfMap.svelte';
	import type { PerformanceDetailed } from '$lib/types';

    let performances = $state<PerformanceDetailed[] | undefined>(undefined);
    let viewMap = $state(false);
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
                onlineInfo: p.online_info,
                misc: p.misc
            }))

        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    })

</script>

<div class="relative flex flex-col items-center pl-[10%] pr-[10%] h-full overflow-hidden">
    <div 
    class="absolute inset-0 bg-cover bg-center opacity-50"
    style="background-image: url('/Winterreise_manuscript.jpg');">
    </div>


    <div class="relative bg-base-100 p-10 rounded-md shadow-xl opacity-85 w-full">
        <div class="opacity-85 text-left ml-[20%] mr-[20%]">
            <h3 class="text-5xl mb-5"><i>Winterreise</i> and Dietrich Fischer-Dieskau</h3>
            <div class="text-l mb-5">Franz Schubert composed the song cycle <i>Winterreise</i> for voice and piano shortly before his death in 1827. 
                Famous German baritone Dietrich Fischer-Dieskau had great influence on its reception in the 20th century, performing it more than 130 times
                in an extraordinarily long period of time from 1943 to 1991.<br><br>
                <h4 class="text-2xl mb-2">What this application aims to accomplish</h4>
                First, creating an <i>Interpretationsedition</i> based on Fischer-Dieskaus personal copy; incorporating his interpretative markings and directives. <a class="underline" href="/scores">Click here to view the annotated scores.</a><br> 
                Second, examining 26 recordings from 1948 to 1990 by Fischer-Dieskau and 12 different pianists closely, extracting audio analysis data and comparing these recordings to each other on the grounds of tempo, dynamics, and timbre data. <a class="underline" href="/visualizations">Click here to view the different analysis and visualization tools.</a>
            </div>
        </div>


        <h3 class="text-3xl mb-5 ml-20">Where and when these performances were recorded
            <p class="float-right"> 
                Timeline <input type="checkbox" class="toggle text-xl" onchange={() => {viewMap = !viewMap}} /> Map
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
