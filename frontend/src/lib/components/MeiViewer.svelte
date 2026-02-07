<script lang="ts">
    import { onMount } from 'svelte';
    import PageControls from './PageControls.svelte';
    import SliderControl from './SliderControl.svelte';
    
    export let src: string;
    
    let svg = '';
    let error = '';
    let currentPage = 1;
    let totalPages = 1;
    let scale = 40;
    let toolkitReady = false;
    let vrvToolkit: any;
    
    // Height of the tallest page at current layout
    let viewportHeight = 0;
    
    // Slider values
    let spacingPercent = 25;
    let pageWidth = 800;
    let pageHeight = 600;
    
    const baseLayoutOptions = {
        spacingSystem: 0,
        spacingStaff: 5,
        adjustPageHeight: true,
        scaleToPageSize: true,
        footer: 'none',
        breaks: 'smart',
        breaksSmartSb: 1.0,
        spacingLinear: 1.0
    };
    
    // Keep current page within bounds
    function clampCurrentPage() {
        totalPages = vrvToolkit.getPageCount();
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;
    }
    
    /**
    * Compute the tallest page by actually rendering each SVG
    * and measuring its real pixel height using getBoundingClientRect().
    * This avoids relying on non-existent toolkit methods.
    */
    function computeMaxViewportHeight() {
        const pages = vrvToolkit.getPageCount();
        let maxHeight = 0;
        
        // Create a hidden container to render SVGs offscreen
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
    
    async function initMEI() {
        try {
            const response = await fetch(src);
            const mei = await response.text();
            vrvToolkit.loadData(mei);
        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    }
    
    function doLayout() {
        vrvToolkit.setOptions({
            ...baseLayoutOptions,
            scale,
            spacingNonLinear: spacingPercent / 100,
            pageWidth,
            pageHeight
        });
        
        vrvToolkit.redoLayout();
        clampCurrentPage();
        computeMaxViewportHeight(); // <-- recalc tallest page each time layout changes
        renderPage();
    }
    
    function renderPage() {
        svg = vrvToolkit.renderToSVG(currentPage);
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
    
    // Whenever `src` changes, reload the MEI
    $: if (toolkitReady && src) {
        initMEI().then(() => {
            doLayout();
        });
    }
    
    
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
                max={1200}
                value={pageHeight}
                onChange={(v) => { pageHeight = v; doLayout(); }}
                />
            </div>
        </div>
    </div>
    
    <!-- MEI SVG -->
    <div class="mei-svg">
        {@html svg}
    </div>
    
    
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
        border: 1px dotted black;
    }
    
    .mei-svg :global(svg) {
        transform-origin: top center;
    }
    
    /* Controls wrapper */
    .controls-wrapper {
        width: 100%;
        display: flex;
        justify-content: center; /* center the row of label + sliders */
    }
    
    /* Row containing label and sliders */
    .controls-header-and-sliders {
        display: flex;
        align-items: center;
        gap: 1rem; /* space between label and sliders */
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
