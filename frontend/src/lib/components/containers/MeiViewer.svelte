<script lang="ts">
    import { onMount } from 'svelte';
    import PageControls from '../partials/PageControls.svelte';
    
    let {src, scale = $bindable(40), spacingPercent = $bindable(25), pageWidth = $bindable(1400), pageHeight = $bindable(600)}:
        {src: string; scale: number; spacingPercent: number; pageWidth: number; pageHeight: number } = $props();

    let meiDocument: Document;
    
    let svg = $state('');
    let error = $state('');
    let currentPage = $state(1);
    let totalPages = $state(1);
    let toolkitReady = $state(false);
    let vrvToolkit: any;

    let meiIdMap = new Map<string, Element>();
    
    let viewportHeight = $state(0);
    
    const baseLayoutOptions = {
        spacingSystem: 0,
        spacingStaff: 5,
        adjustPageHeight: true,
        scaleToPageSize: true,
        footer: 'none',
        breaks: 'smart',
        breaksSmartSb: 1.0,
        spacingLinear: 1.0,
    };

    const capitalize = (s: string) =>
        s ? s[0].toUpperCase() + s.slice(1) : "";
    
    function buildMeiIdMap(meiDoc: Document) {

        meiIdMap.clear();

        const all = meiDoc.getElementsByTagName("*");

        let count = 0;

        for (const el of Array.from(all)) {
            const id = el.getAttribute("xml:id");
            if (id) {
                meiIdMap.set(id, el);
                count++;
            }
        }
    }
    
    function clampCurrentPage() {
        totalPages = vrvToolkit.getPageCount();
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;
    }
    
    function computeMaxViewportHeight() {
        const pages = vrvToolkit.getPageCount();
        let maxHeight = 0;
        
        const container = document.createElement('div');
        container.style.position = 'absolute';
        container.style.visibility = 'hidden';
        container.style.height = 'auto';
        container.style.width = 'auto';
        document.body.appendChild(container);
        
        for (let i = 1; i <= pages; i++) {
            container.innerHTML = vrvToolkit.renderToSVG(i);
            const svgEl = container.querySelector('svg');
            if (svgEl) {
                const h = svgEl.getBoundingClientRect().height;
                if (h > maxHeight) maxHeight = h;
            }
        }
        
        document.body.removeChild(container);
        viewportHeight = maxHeight;
    }
    
    function initMEI() {
        try {
            if (!src) return;
            
            meiDocument = new DOMParser().parseFromString(src, "text/xml");

            buildMeiIdMap(meiDocument);
            
            vrvToolkit.loadData(src);
            
        } catch (e: any) {
            error = e.message;
            console.error('MEI load error:', e);
        }

    }

    export function doLayout() {
        vrvToolkit.setOptions({
            ...baseLayoutOptions,
            scale,
            spacingNonLinear: spacingPercent / 100,
            pageWidth,
            pageHeight,
            svgAdditionalAttribute: ["add@source", "unclear@reason", "dir@type", "dir@label"]
        });
        
        vrvToolkit.redoLayout();
        clampCurrentPage();
        computeMaxViewportHeight(); 
        renderPage();
    }
    
    function renderPage() {
        svg = vrvToolkit.renderToSVG(currentPage);
    }

    // one function for all clicks (notes, annots, adds)
    let clickContent = $state("");
    let clickType = $state("");
    let clickElement: HTMLDialogElement;

    function handleClick(event: Event) {
        if (!meiDocument) return;

        const target = event.target as Element;

        // Determine what type of MEI SVG element was clicked
        const noteEl = target.closest("g.note") as HTMLElement;
        const annotEl = target.closest("g.annot.score") as HTMLElement;
        const addEl = target.closest("g.add") as HTMLElement;

        if (noteEl) {
            clickType = "Note";

            const meiNote = meiIdMap.get(noteEl.id) || null;
            if (!meiNote) return;

            const pitch = meiNote.getAttribute("pname");
            const octave = meiNote.getAttribute("oct");

            // Walk up DOM tree to find containing <measure>
            let parent = meiNote.parentElement;
            let measure = null;

            while (parent && parent.tagName.toLowerCase() !== "measure") {
                parent = parent.parentElement;
            }

            if (parent) {
                measure = parent.getAttribute("n");
            }

            clickContent = "Note: " + pitch + octave + "\nMeasure: " + measure;
            clickElement?.showModal();

        } else if (annotEl) {
            clickType = "Annotation";

            const meiAnnot = meiIdMap.get(annotEl.id) || null;
            if (!meiAnnot) return;

            // Annotation content is taken directly from MEI text node
            clickContent = meiAnnot.textContent || "";
            clickElement?.showModal();

        } else if (addEl) {
            clickType = "Addition by Fischer-Dieskau";

            const meiAdd = meiIdMap.get(addEl.id) || null;
            if (!meiAdd) return;

            // First meaningful child (ignoring handShift markup elements)
            const child = Array.from(meiAdd.children)
                .find(el => el.localName !== "handShift" && el.localName !== "annot") || null;

            const firstDirChild = Array.from(meiAdd.children)
                .filter(el => el.localName === "dir")[0];

            // Classify type of musical addition based on first meaningful child
            let addClass = "";

            if (child?.localName == "dir") {
                addClass = "directive for interpretation";

            } else if (child?.localName == "hairpin") {
                if (child?.getAttribute("form") == "cres") {
                    addClass = "crescendo hairpin";
                } else if (child?.getAttribute("form") == "dim") {
                    addClass = "diminuendo hairpin";
                }

            } else if (child?.localName == "tempo") {
                addClass = "instruction for tempo";

            } else if (child?.localName == "dynam") {
                addClass = "instruction for dynamics";

            } else if (child?.localName == "trill" || child?.localName == "mordent") {
                addClass = "Trill/vibrato";

            } else if (child?.localName == "slur") {
                addClass = "slur";

            } else if (child?.localName == "fermata") {
                addClass = "fermata";
            }

            const handShift = meiAdd.querySelector("handShift");
            let addHandShift = "";

            if (handShift) {
                addHandShift = handShift.getAttribute("medium") || "";
            }

            const annot = meiAdd.querySelector("annot");
            let annotTag = "";

            if (annot) {
                annotTag = annot.textContent;
            }

            const addType = addClass;
            const medium = addHandShift.replace(/-/g, " ");
            const type = (firstDirChild?.getAttribute("type"))?.replace(/-/g, " ");
            const label = (firstDirChild?.getAttribute("label"))?.replace(/-/g, " ");

            // Some MEI additions may contain editorial uncertainty annotations
            const unclearReason = addEl.querySelector("tspan.unclear")?.getAttribute("data-reason");

            // Build modal content from available metadata fields
            clickContent = [
                capitalize(addType) + (unclearReason ? `, unclear (${unclearReason})` : ""),
                type ? `Type: ${type}` : "",
                label ? `Label: ${label}` : "",
                handShift ? `Medium: ${medium}` : "",
                annot ? `Additional information: ${annotTag}` : ""
            ]
                .filter(Boolean)
                .join("\n");

            clickElement?.showModal();

        } else {
            return;
        }
    }
    
    onMount(async () => {
        try {
            const createVerovioModule = (await import('verovio/wasm')).default;
            const { VerovioToolkit } = await import('verovio/esm');
            const VerovioModule = await createVerovioModule();
            vrvToolkit = new VerovioToolkit(VerovioModule);
            
            await initMEI();
            doLayout();
            
            toolkitReady = true;
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
        
    });
    
    $effect (() => {
        if (toolkitReady && src) {
            initMEI();
            doLayout();
        }
    });

    function attachMeiContainer(node: HTMLDivElement) {
        node.addEventListener("click", handleClick);
        return () => node.removeEventListener("click", handleClick);
    }
    
</script>

<!-- MeiViewer.svelte -->
<div class="viewer-container" style="--pageWidth: {pageWidth}px; --viewport-height: {viewportHeight}px">
    {#if error}
        <p class="text-error">{error}</p>
    {/if}
    <div class="mei-svg" {@attach attachMeiContainer}>
        {@html svg}
    </div>

    <dialog bind:this={clickElement} class="modal">
        <div class="modal-box">
            <form method="dialog">
                <button class="btn btn-sm btn-circle btn-ghost absolute right-2 top-2">✕</button>
            </form>
            <h3 class="text-lg font-bold">{clickType}</h3>
            <p style="white-space: pre-line;">{clickContent}</p>
        </div>
        <form method="dialog" class="modal-backdrop">
            <button>close</button>
        </form>
    </dialog>
    
    <!-- Page controls -->
    <div class="page-controls">
        <PageControls
        {currentPage}
        {totalPages}
        onPrev={() => { currentPage--; renderPage(); }}
        onNext={() => { currentPage++; renderPage(); }}
        />
    </div>
    
</div>

<style>
    .viewer-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.5rem;
        padding: 1rem;
        width: var(--pageWidth);
        min-width: 1000px;
        margin: 0 auto;
        border: 2px solid var(--color-primary);
        border-radius: 8px;
    }
    
    .mei-svg {
        width: 100%;
        height: var(--viewport-height);
        overflow: hidden;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        
    }
    
    .mei-svg :global(svg) {
        transform-origin: top center;
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: rgba(254, 255, 223, .5);
    }
    
    .mei-svg :global(g.note path),
    .mei-svg :global(g.note use) {
        transition: fill 0.15s ease, stroke 0.15s ease;
    }
    
    .mei-svg :global(g.note:hover path),
    .mei-svg :global(g.note:hover use) {
        fill: red;
        stroke: red;
    }
    
    .mei-svg :global(g.supplied) {
        color: yellowgreen;
        stroke: yellowgreen;
        fill: yellowgreen;
        
    }
    
    .mei-svg :global(g.supplied:hover) {
        color: brown;
        stroke: brown;
        fill: brown;
        
    }
    
    .mei-svg :global(g[data-source="#dwdfdc9075d0e-7aaa-4a82-bfa0-06eb81584587"]) {
        color: blueviolet;
        stroke: blueviolet;
        fill: blueviolet;
        cursor: pointer  
    }
    
    .mei-svg :global(g[data-source="#dwdfdc9075d0e-7aaa-4a82-bfa0-06eb81584587"]:hover) {
        color: orange;
        stroke: orange;
        fill: orange;
    }

    .modal-box {
        line-height: 3vh;
    }
    
    /* Page controls */
    .page-controls {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
</style>