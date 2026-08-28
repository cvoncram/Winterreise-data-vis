<script lang="ts">
    import { onDestroy } from "svelte";
    import { beforeNavigate } from "$app/navigation";
    import { gsap } from "gsap";
    import { morph, reset } from "$lib/ribbonMorph.svelte";
    import { segmentPath } from "$lib/utils/ribbonGeometry";

    const DURATION = 0.8;

    const tween = { t: 0 };
    let animation: ReturnType<typeof gsap.to> | null = null;

    function prefersReducedMotion() {
        return typeof window !== "undefined"
            && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    }

    function finish() {
        animation?.kill();
        animation = null;
        tween.t = 0;
        reset();
    }

    $effect(() => {
        if (!morph.active || !morph.from || !morph.to || animation) return;

        if (prefersReducedMotion()) {
            finish();
            return;
        }

        tween.t = 0;
        animation = gsap.to(tween, {
            t: 1,
            duration: DURATION,
            ease: "power2.inOut",
            onUpdate: () => { morph.t = tween.t; },
            onComplete: finish
        });
    });

    beforeNavigate(() => {
        if (morph.active && animation) finish();
    });

    onDestroy(() => animation?.kill());

    let paths = $derived(
        morph.active && morph.from && morph.to
            ? morph.segments.map(seg => ({
                d: segmentPath(seg, morph.t, morph.from!, morph.to!),
                color: seg.color
            }))
            : []
    );
</script>

{#if paths.length > 0}
    <svg class="ribbon-morph" aria-hidden="true">
        {#each paths as p, i (i)}
            <path d={p.d} fill={p.color} />
        {/each}
    </svg>
{/if}

<style>
    .ribbon-morph {
        position: fixed;
        inset: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 40;
    }
</style>
