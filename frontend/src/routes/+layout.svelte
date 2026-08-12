<script lang="ts">
	import "../app.css";
	import { page } from "$app/state";
	import Footer from "$lib/components/partials/Footer.svelte";
	import Logo from "$lib/components/partials/Logo.svelte";

	let { children } = $props();

    export const ssr = false;

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
            <Logo />
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

<style>

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
