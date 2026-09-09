<script lang="ts">
    import { onMount } from 'svelte';
    import ScoreSelector from '$lib/components/partials/ScoreSelector.svelte';
    import MeiViewer from '$lib/components/containers/MeiViewer.svelte';
    import type {SongInfo} from "$lib/types";
    import { scoresPageState as pageState } from "./pageState.svelte";

    let error = $state<string>('');
    let loading = $state(false);
    let empty = $state(true);
    let ready = $state(false);

    let scaleLabel = $derived(pageState.scale);
    let spacingPercentLabel = $derived(pageState.spacingPercent);
    let pageHeightLabel = $derived(pageState.pageHeight);

    let meiViewer = $state<ReturnType<typeof MeiViewer>>();
    let scoreRendered = $state(false);

    async function fetchSelectedFile(file: SongInfo) {
        loading = true;
        empty = false;
        scoreRendered = false;
        try {
            const res = await fetch(
            `/db/file?path=${encodeURIComponent(file.path)}`
            );

            if (!res.ok) throw new Error('Could not fetch MEI file');

            const data = await res.text();
            pageState.meiContent = data;

        } catch (e: any) {
            error = e.message;
            console.error(e);
            pageState.meiContent = null;
        } finally {
            loading = false;
            empty = false;
        }
    }

    function handleFileSelect(file: SongInfo) {
        pageState.selectedFile = file;
        fetchSelectedFile(file);
    }

    onMount(async () => {
        if (pageState.files.length > 0) return;
        try {
            const res = await fetch('/db/scores-folder');
            if (!res.ok) throw new Error('Could not fetch file list');
            const data = await res.json();

            pageState.files = data;

        } catch (e: any) {
            error = e.message;
            console.error(e);
        }
    });

</script>
<div class="flex">
    <div class="fixed top-0 left-0 h-full w-64 bg-base-200 p-4 flex flex-col justify-center items-center gap-4 z-10">

        <div class="card bg-base-200 p-4 gap-4 shadow-md justify-start">
            <ScoreSelector
            files={pageState.files}
            selectedFile={pageState.selectedFile}
            onFileSelect={handleFileSelect}
            />
            {#if error}
            <p class="text-error mt-2">{error}</p>
            {/if}
            {#if pageState.meiContent}
            <div class="bg-base-100 gap-4 p-4 rounded-lg shadow flex flex-col items-start overflow-visible">
                <span class="label-text mb-2 text-lg font-semibold">Change size and appearance</span>
                <label>Scale (percent):
                    <input type="range" min="10" max="80" value={pageState.scale} class="range range-s range-primary"
                    onchange={(e) => { pageState.scale = Number(e.currentTarget.value); meiViewer?.doLayout();}}
                    oninput={(e) => {scaleLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{scaleLabel}</span>
                </label>
                <label>Spacing (percent):
                    <input type="range" min="1" max="100" value={pageState.spacingPercent} class="range range-s range-primary"
                    onchange={(e) => { pageState.spacingPercent = Number(e.currentTarget.value); meiViewer?.doLayout();}}
                    oninput={(e) => {spacingPercentLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{spacingPercentLabel}</span>
                </label>
                <label>Minimum page height (pixels):
                    <input type="range" min="300" max="4000" value={pageState.pageHeight} class="range range-s range-primary"
                    onchange={(e) => { pageState.pageHeight = Number(e.currentTarget.value); meiViewer?.doLayout();}}
                    oninput={(e) => {pageHeightLabel = Number(e.currentTarget.value)}}/>
                    <span class="font-bold">{pageHeightLabel}</span>
                </label>
            </div>
            {/if}
        </div>

    </div>

    <div class="ml-64 w-full min-h-[80vh] p-4">

        {#if empty && !pageState.meiContent}
            <div class="flex items-center justify-center w-full h-screen">
                <p style="font-size: 20px">In the side bar on the left, you can choose any piece from the score to render in this page.<br><br>
                The additions made by Dietrich Fischer-Dieskau to his own copy of the score are in <em style="color: blueviolet">violet</em>;<br>
                additions by editors in later editions of the score are in <em style="color: brown">brown</em>.<br>
                Click on any of Fischer-Dieskau's additions to view further information about their meanings and possible interpretations.
                </p>
            </div>
        {:else if loading && !empty}
        <div class="flex items-center justify-center w-full h-[80vh]">
            <span class="loading loading-spinner loading-lg"></span>
        </div>
        {:else if pageState.meiContent}
        <div class="card bg-base-100 p-2 w-full relative">
            {#if !scoreRendered}
                <div class="absolute inset-0 z-10 flex items-center justify-center bg-base-100/70">
                    <span class="loading loading-spinner loading-lg"></span>
                </div>
            {/if}
            <MeiViewer bind:this={meiViewer} bind:rendered={scoreRendered} src={pageState.meiContent} bind:scale={pageState.scale} bind:spacingPercent={pageState.spacingPercent} bind:pageHeight={pageState.pageHeight}/>
        </div>
        {/if}

    </div>

</div>

<style>
    .card > :global(.flex) {
        flex-wrap: wrap;
    }
</style>
