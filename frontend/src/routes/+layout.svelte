<script lang="ts">
    import "../app.css";
    let { children } = $props();
</script>

<svelte:head>
</svelte:head>

<div class="navbar bg-base-100 shadow-sm">
    <div class="page-title">
        <a href="/">MEI Visualisation tool</a>
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

    .page-title a:hover {
        color: #e2e8f0;
        background-color: rgba(25, 25, 207, 0.37);

    }
    
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
