<script lang="ts">
	import "../app.css";
	import { page } from "$app/state";

	let { children } = $props();

	const baseTitle = "MEI Visualization";
	const title = $derived(
		page.data.title ? `${page.data.title} | ${baseTitle}` : baseTitle
	);
</script>

<svelte:head>
	<title>{title}</title>
</svelte:head>

<div class="navbar bg-base-100 shadow-sm">
    <div class="page-title">
        <a class="btn btn-primary" href="/">MEI Visualisation tool</a>
    </div>
    <div class="nav-items">
        <a class="btn btn-accent" href="/scores">Scores</a>
        <a class="btn btn-accent" href="/performances">Performances</a>
        <a class="btn btn-accent" href="/analysis">Analysis</a>
    </div>
</div>

<main>
    {@render children()}
</main>

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
