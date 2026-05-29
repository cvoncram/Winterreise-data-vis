<script lang="ts">
	import type { CyclePerformance } from "$lib/types";

    let {performances, selectedPerformances = $bindable([])}: {performances: CyclePerformance[]; 
        selectedPerformances: CyclePerformance[]} = $props();

        let checked = $state<boolean[]>([]);

        $effect(() => {
        checked = new Array(performances.length).fill(false);
        });

        $effect(() => {
        selectedPerformances = performances.filter((_, i) => checked[i]);
        $inspect(selectedPerformances);
        });
</script>

<div class="flex w-full mt-2 justify-start">
	<div class="flex gap-6 max-w-4xl w-full">
		<div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
            <span class="label-text mb-2 text-lg font-semibold">Select performances</span>
            {#each performances as p, i}
                <label class="label">
                    <input type="checkbox" bind:checked={checked[i]} class="checkbox checkbox_{i}" />
                    {p.label}
                </label>
            {/each}

        </div>
    </div>
</div>
