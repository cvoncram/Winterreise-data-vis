<script lang="ts">
    import type { CyclePerformance } from "$lib/types";

    let {
        performances,
        selectedPerformances = $bindable(),
        lockedPath = null,
        onSelectionChange
    }: {
        performances: CyclePerformance[];
        selectedPerformances: CyclePerformance[];
        lockedPath?: string | null;
        onSelectionChange?: (selection: CyclePerformance[]) => void;
    } = $props();

    let checked = $state<boolean[]>([]);

    function initChecked() {
        const selectedPaths = new Set(
            selectedPerformances.map(p => p.path)
        );

        checked = performances.map(
            p => selectedPaths.has(p.path)
        );
   }

   $effect(() => {
        if (performances.length > 0 && lockedPath && checked.length === 0) {
            initChecked();
        }
    });

    function handleToggle(i: number) {
        if (performances[i].path === lockedPath) return;
        checked[i] = !checked[i];
        const newSelection = performances.filter((_, idx) => checked[idx]);
        selectedPerformances = newSelection;
        onSelectionChange?.(newSelection);
    }
</script>

<div class="flex w-full mt-2 justify-start">
    <div class="flex gap-6 max-w-4xl w-full">
        <div class="bg-base-100 p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
            <span class="label-text mb-2 text-lg font-semibold">Select performances</span>
            {#each performances as p, i}
                <label class="label">
                    <input
                        type="checkbox"
                        checked={checked[i]}
                        disabled={p.path === lockedPath}
                        onchange={() => handleToggle(i)}
                    />
                    {p.label}
                </label>
            {/each}
        </div>
    </div>
</div>