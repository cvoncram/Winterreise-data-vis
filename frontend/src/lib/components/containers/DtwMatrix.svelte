<script lang="ts">
    import DtwMatrixCsv from "../partials/DtwMatrixCsv.svelte";

    /**
     * The distance matrix as a triangle.
     *
     * Shows every pair exactly once — the other half is its mirror image and
     * the diagonal is zero by definition. Unlike the network it embeds
     * nothing, so no distance is approximated: this is the view to read a
     * single pair off, where the graph is the view to see the whole field.
     *
     * Drawn as plain SVG rather than through D3: there is no scale, layout or
     * simulation to compute here, only a grid of rectangles, and the markup is
     * easier to follow than an imperative redraw would be.
     */
    let { matrix, labels, onSelectPair }: {
        matrix: (number | null)[][];
        labels: string[];
        /** Indices into the same order the labels are in, so the caller can name the pair. */
        onSelectPair?: (a: number, b: number) => void;
    } = $props();

    /** Sequential single hue, light to dark — magnitude, not identity. */
    const RAMP = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"];

    const n = $derived(matrix.length);
    // Wide enough to read and to hit with a pointer, small enough that 26
    // recordings still fit on a screen.
    const cell = $derived(Math.max(28, Math.min(60, Math.round(1120 / Math.max(n, 1)))));
    const font = $derived(Math.min(18, Math.max(10, cell * 0.45)));
    const labelGap = 6;

    const extent = $derived.by(() => {
        let lo = Infinity, hi = -Infinity;
        for (let i = 0; i < n; i++)
            for (let j = 0; j < i; j++) {
                const v = matrix[i][j];
                if (v == null) continue;
                if (v < lo) lo = v;
                if (v > hi) hi = v;
            }
        return lo <= hi ? { lo, hi } : { lo: 0, hi: 1 };
    });

    function colour(value: number) {
        const t = (value - extent.lo) / (extent.hi - extent.lo || 1);
        return RAMP[Math.min(RAMP.length - 1, Math.max(0, Math.floor(t * RAMP.length)))];
    }

    const fmt = (v: number) => v.toFixed(3);

    let hovered = $state<{ a: string; b: string; value: number } | null>(null);

    // Room for the longest name, which sits at the end of the last row.
    const labelWidth = $derived(
        Math.max(160, ...labels.map(l => l.length * font * 0.55)) + labelGap
    );
    const width = $derived(n * cell + labelWidth + 16);
    const height = $derived(n * cell + 16);
</script>

{#if n > 1}
    <div class="flex flex-col gap-3 mt-4">
        <div class="flex items-center gap-4 flex-wrap">
            <DtwMatrixCsv {matrix} {labels} />
            <div class="flex items-center gap-2 text-sm opacity-70">
                <span class="font-mono">{fmt(extent.lo)}</span>
                <span class="flex h-3 w-40 rounded overflow-hidden" aria-hidden="true">
                    {#each RAMP as step}
                        <span class="flex-1" style="background:{step}"></span>
                    {/each}
                </span>
                <span class="font-mono">{fmt(extent.hi)}</span>
                <span>distance per beat</span>
            </div>
        </div>

        <div class="overflow-auto">
            <svg
                viewBox="0 0 {width} {height}"
                style="width:{width}px; max-width:100%; height:auto"
                role="img"
                aria-label="Triangular matrix of pairwise distances"
                onpointerleave={() => (hovered = null)}
            >
                {#each matrix as row, i}
                    {#each row.slice(0, i) as value, j}
                        <rect
                            x={8 + j * cell}
                            y={8 + i * cell}
                            width={cell}
                            height={cell}
                            fill={value == null ? "transparent" : colour(value)}
                            stroke="currentColor"
                            stroke-opacity={value == null ? 0.18 : 0.08}
                            stroke-width="0.7"
                            stroke-dasharray={value == null ? "2 2" : undefined}
                            role="button"
                            aria-disabled={value == null}
                            tabindex={value == null ? undefined : 0}
                            class={value == null ? "" : "cursor-pointer"}
                            aria-label={value == null
                                ? `${labels[j]} and ${labels[i]}: not comparable`
                                : `${labels[j]} and ${labels[i]}: ${fmt(value)} per beat`}
                            onpointerenter={() =>
                                (hovered = value == null
                                    ? null
                                    : { a: labels[j], b: labels[i], value })}
                            onclick={() => value != null && onSelectPair?.(j, i)}
                            onkeydown={(event) => {
                                if (value == null || (event.key !== "Enter" && event.key !== " ")) return;
                                event.preventDefault();
                                onSelectPair?.(j, i);
                            }}
                        />
                    {/each}
                    <text
                        x={8 + i * cell + labelGap}
                        y={8 + i * cell + cell - Math.max(4, cell * 0.28)}
                        font-size={font}
                        fill="currentColor"
                        fill-opacity="0.75"
                    >{labels[i]}</text>
                {/each}
            </svg>
        </div>

        <div class="text-sm min-h-6">
            {#if hovered}
                <span class="font-semibold">{hovered.a}</span>
                <span class="opacity-50"> / </span>
                <span class="font-semibold">{hovered.b}</span>
                <span class="font-mono ml-2">{fmt(hovered.value)}</span>
                <span class="opacity-70"> per beat</span>
            {:else}
                <span class="opacity-60">Point at a cell to read the pair, click it for the full comparison. Dashed cells were not comparable.</span>
            {/if}
        </div>
    </div>
{:else}
    <p class="opacity-60 mt-4">Select at least two performances to build a matrix.</p>
{/if}
