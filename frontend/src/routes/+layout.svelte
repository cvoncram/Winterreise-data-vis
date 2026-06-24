<script lang="ts">
	import "../app.css";
	import { page } from "$app/state";
	import Footer from "$lib/components/partials/Footer.svelte";

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
        <a class="btn btn-primary" href="/documentation">Documentation</a>
        <a class="btn btn-primary" href="/scores">Scores</a>
        <a class="btn btn-primary" href="/visualizations">Visualizations</a>
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
        fill:  #668ba4;
    }
    :global(svg:hover path#path387-7) {
        fill: var(--color-base-200);
    }
    div#home:hover{
        background-color:  #668ba4;
    }
   
    .nav-items {
        justify-self: center;
        display: flex;
        gap: 0.5rem;
    }

    .nav-items > * {
        width: 110px;
    }
       
</style>
