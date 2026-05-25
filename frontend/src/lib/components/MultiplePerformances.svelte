<script lang="ts">
    import MeiCircularRibbon from "./MeiCircularRibbon.svelte";
    import type { PerformanceMetadata, PerformanceRow } from "./MeiTable.svelte";

    let {performancesData, metadata}: {performancesData: PerformanceRow[][]; metadata: PerformanceMetadata[]} = $props();
    const evenNbPerfs = $derived(performancesData.length % 2 === 0);

</script>

{#if (evenNbPerfs)}

    {#each performancesData as data, i}

    <div class="w-[50%]">
        <MeiCircularRibbon rows={data} metadata={metadata[i]}/>
    </div>

    {/each}

{:else}
    <p>Hello</p>


{/if}


