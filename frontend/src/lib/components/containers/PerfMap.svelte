<script lang="ts">
    import { Map, TileLayer, Marker, Popup } from 'sveaflet';
    import type { PerformanceDetailed } from '$lib/types';

    type MyMarker = {coordinates: number[], info: string};

    let markers = $state<MyMarker[]>([]);

    let {performances}: {performances: PerformanceDetailed[]| undefined} = $props();

    /**
     * Adds markers to the map. In case of duplicates, info string is appended.
     */
    function createMarkers(performances: PerformanceDetailed[]): MyMarker[] {
        const uniqueCoords: string[] = [];
        const testMarkers: MyMarker[] = [];

        for (let i = 0; i < performances.length; i++) {
            const p = performances[i];
            const info = `Date: ${p.date}\nPianist: ${p.pianist}\nPlace: ${p.place}`
                + (p.placeAddendum ? `, ${p.placeAddendum}` : "");
            const key = p.coordinates.join(",");
            const pos = uniqueCoords.indexOf(key);

            if (pos !== -1) {
                testMarkers[pos].info += `\n---\n${info}`;
            } else {
                uniqueCoords.push(key);
                testMarkers.push({ coordinates: p.coordinates, info });
            }
        }

        return testMarkers;
    }

    $effect(() => {
        if(performances){
            markers = createMarkers(performances);
        }
    })

</script>                    
                    
                    
<Map
    options={{
        center: [41.6, -46.8],
        zoom: 3
    }}
>
    <TileLayer url={'https://tile.openstreetmap.org/{z}/{x}/{y}.png'} />
    {#each markers as m}
        <Marker latLng={[m.coordinates[0], m.coordinates[1]]}>
            <Popup options={{
                content: m.info,
            }} />
        </Marker>
    {/each}

</Map>

<style>
        :global(.leaflet-popup-content) {
        white-space: pre-line;
    }
</style>