<script lang="ts">
    import { onDestroy } from "svelte";
    import { beforeNavigate } from "$app/navigation";
    import { gsap } from "gsap";
    import { morph, reset } from "$lib/ribbonMorph.svelte";
    import { segmentPath } from "$lib/utils/ribbonGeometry";

    /**
     * Draws a copy of the circular ribbon's segments over the whole viewport
     * and stretches them into the linear layout.
     *
     * Mounted in the root layout so that it survives the navigation between
     * the two pages — the source component is destroyed long before the
     * target has rendered, so neither could host this itself.
     */

    const DURATION = 0.8;

    // GSAP tweens plain object properties, so the animated value lives here
    // and is mirrored into reactive state on each frame.
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

    // Starts once the target page has reported where its ribbon ended up.
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

    // Leaving mid-transition would strand the overlay on screen.
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
        z-index: 40; /* below the navbar (z-50), above page content */
    }
</style>
