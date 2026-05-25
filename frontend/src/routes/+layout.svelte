<script lang="ts">
	import "../app.css";
	import { page } from "$app/state";
	import Footer from "$lib/components/Footer.svelte";

	let { children } = $props();

	const baseTitle = "MEI Visualization";
	const title = $derived(
		page.data.title ? `${page.data.title} | ${baseTitle}` : baseTitle
	);
</script>

<svelte:head>
	<title>{title}</title>
</svelte:head>

<div class="navbar bg-base-200 shadow-sm z-50">
    <div id="home" class="page-title ml-10">
        <a href="/" id="home" title="home">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                class="w-15 h-15"
            >
                <g transform="translate(-379.76917,-329.19561)">
                    <path
                        id="path387-7"
                        style="fill-opacity:1"
                        d="m 384.76917,329.1956 v 1 h -1 v 1 h -1 v 1 h -1 -1 v -1 h -1 v 1 1 1 1 1 1 1 1 1 1 1 1 1 1 1 h 1 v -1 
                            h 1 1 1 1 1 v 1 h 1 v 1 h -1 v 1 h -1 v -1 h -1 v -1 h -1 v 1 h -1 v 1 h 1 v 1 h 1 1 1 1 v -1 h 1 v -1 -1 
                            -1 h 1 1 1 1 1 v 1 h 1 1 v -1 h 1 1 1 1 1 v -1 h -1 -1 -1 -1 v -1 -1 h 1 1 1 1 v -1 h -1 -1 -1 -1 v -1 -1 
                            h 1 v 1 h 1 v -1 h 1 1 v -1 h -1 v -1 -1 h 1 v -1 h -1 v -1 h -1 v -1 h 1 1 v -1 h -1 -1 -1 -1 v -1 h -1 v
                            1 h -1 -1 -1 -1 -1 -1 v -1 h -1 v -1 h -1 v -1 h -1 z m 0,2 h 1 1 v 1 h -1 -1 z m -4,2 h 1 1 1 v 1 h 1 v 
                            1 h -1 -1 -1 -1 v -1 z m 5,0 h 1 v 1 h -1 z m 2,0 h 1 1 1 1 1 1 1 v 1 1 h -1 -1 -1 -1 -1 -1 -1 v -1 z m 8,1
                            h 1 v 1 h -1 z m -15,2 h 1 1 1 v 1 h -1 v 1 h -1 -1 v -1 z m 6,0 h 1 1 1 1 1 1 1 1 v 1 1 h -1 -1 -1 -1 -1 
                            -1 -1 v -1 h -1 z m 9,0 h 1 1 v 1 1 h -1 -1 v -1 z m -11,1 h 1 v 1 h -1 z m -4,2 h 1 v 1 1 h -1 v -1 z m 2,0 
                            h 1 1 v 1 h 1 1 v 1 h -1 -1 v -1 h -1 v 1 h -1 v -1 z m 6,0 h 1 1 1 1 1 1 v 1 1 h -1 -1 -1 -1 -1 v -1 h -1 z m 
                            -8,3 h 1 1 v 1 1 h -1 -1 v -1 z m 3,0 h 1 v 1 h -1 z m 2,0 h 1 v 1 h -1 z m 3,0 h 1 1 1 1 v 1 h -1 v 1 h -1 -1 
                            -1 -1 v -1 h 1 z" />
                </g>
            </svg>
        </a>
    </div>
    <div class="nav-items">
        <a class="btn btn-success" href="/documentation">Documentation</a>
        <a class="btn btn-success" href="/analysis">Analysis</a>
        <a class="btn btn-success" href="/scores">Scores</a>
        <a class="btn btn-success" href="/visualizations">Visualizations</a>
    </div>
</div>

<main>
    {@render children()}
</main>

<Footer />

<style global()>
    
    .navbar {
        display: grid;
        grid-template-columns: 1fr auto 1fr;
        align-items: center;
        border-bottom: 1px solid #e2e8f0;
        padding: 0 1rem;
    }
    
    .page-title {
        justify-self: start;
    }
    :global(svg path#path387-7) {
        fill: oklch(51% 0.096 186.391);
    }
    :global(svg:hover path#path387-7) {
        fill: var(--color-base-200);
    }
    div#home:hover{
        background-color: oklch(51% 0.096 186.391);
    }


    /* maybe later
    .page-title a:hover {
        color: #e2e8f0;
        background-color: rgb(129 161 193);
        padding: 5px;
        border-radius: 5px;

    }
    */
    
    .nav-items {
        justify-self: center;
        display: flex;
        gap: 0.5rem;
    }

    .nav-items > * {
        width: 110px;
    }
    
    /** (maybe for later, to have an element at the right of the navbar)
    .right-items {
        justify-self: end;
    }
    **/
    
</style>
