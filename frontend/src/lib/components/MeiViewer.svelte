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
    
    function clampCurrentPage() {
        totalPages = vrvToolkit.getPageCount();
        if (currentPage > totalPages) currentPage = totalPages;
        if (currentPage < 1) currentPage = 1;
    }
    
    async function initMEI() {
        const response = await fetch(src);
        const mei = await response.text();
        vrvToolkit.loadData(mei);
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
        renderPage();
    }
    
    function renderPage() { svg = vrvToolkit.renderToSVG(currentPage); }
    
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
</script>

{#if !toolkitReady && !error}
<p>Loading MEI score…</p>
{/if}
<h3 class="tools-header">Display options</h3>

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

<div class="mei-svg">{@html svg}</div>

<div class="page-controls">
    <PageControls
    {currentPage}
    {totalPages}
    onPrev={() => { currentPage--; renderPage(); }}
    onNext={() => { currentPage++; renderPage(); }}
    />
</div>

<style>
    .tools-header {
        background-color: rgba(0, 255, 98, 0.103);
        display: flex;
        align-content: center;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
    }

    .controls {
        display: grid;
        grid-template-columns: auto auto auto auto;
        gap: 2%;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        padding: 1%;
        
    }

    .page-controls {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-bottom: 1rem;
        background-color: rgba(0, 255, 98, 0.103);
        
    }

    .mei-svg {
        width: 100%;
        overflow-x: auto;
        display: flex;
        justify-content: center;
    }
    .mei-svg :global(svg) { transform-origin: top center; }
</style>
