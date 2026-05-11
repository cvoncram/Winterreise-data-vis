<script lang="ts">
    import { onMount } from 'svelte';
    import PageControls from './PageControls.svelte';
    import SliderControl from './SliderControl.svelte';
    
    let {src}: {src: string} = $props();

    let meiDocument: Document;
    let meiContainer: HTMLDivElement;
    
    let svg = $state('');
    let error = $state('');
    let currentPage = $state(1);
    let totalPages = $state(1);
    let toolkitReady = $state(false);
    let vrvToolkit: any;

    let meiIdMap = new Map<string, Element>();
    
    let viewportHeight = $state(0);
    
    let scale = $state(40);
    let spacingPercent = $state(25);
    let pageWidth = $state(1400);
    let pageHeight = $state(600);
    
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

    function doLayout() {
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

        meiContainer?.addEventListener("click", handleClick);
        
    });
    
    $effect (() => {
        if (toolkitReady && src) {
            initMEI();
            doLayout();
        }
    });
    
</script>

<!-- MeiViewer.svelte -->
<div class="viewer-container" style="--pageWidth: {pageWidth}px; --viewport-height: {viewportHeight}px">
    
    <!-- Controls with left-aligned label -->
    <div class="controls-wrapper">
        <div class="controls-header-and-sliders">
            <h2 class="tools-header">Display options</h2>
            <div class="controls">
                <SliderControl
                label="Scale (percent)"
                min={10}
                max={80}
                value={scale}
                onChange={(v) => { scale = v; doLayout(); }}
                />
                <SliderControl
                label="Note spacing (percent)"
                min={1}
                max={100}
                value={spacingPercent}
                onChange={(v) => { spacingPercent = v; doLayout(); }}
                />
                <SliderControl
                label="Page width (pixels)"
                min={400}
                max={1600}
                value={pageWidth}
                onChange={(v) => { pageWidth = v; doLayout(); }}
                />
                <SliderControl
                label="Maximum page height (pixels)"
                min={300}
                max={4000}
                value={pageHeight}
                onChange={(v) => { pageHeight = v; doLayout(); }}
                />
            </div>
        </div>
    </div>
    
    <div class="mei-svg" bind:this={meiContainer}>
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
        border: 2px solid black;
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
        background-color: whitesmoke;
        border-radius: 0.5rem;
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
    
    
    /* Controls wrapper */
    .controls-wrapper {
        width: 100%;
        display: flex;
        justify-content: center;
    }
    
    /* Row containing label and sliders */
    .controls-header-and-sliders {
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    /* Label on the left, vertical alignment center */
    .tools-header {
        white-space: nowrap;
    }
    
    /* Sliders container */
    .controls {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 2%;
    }
    
    /* Page controls */
    .page-controls {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
</style>