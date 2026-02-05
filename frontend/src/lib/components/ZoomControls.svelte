<script lang="ts">
    export let onZoomIn: () => void;
    export let onZoomOut: () => void;
</script>

<div class="zoom-controls">
    <button on:click={onZoomOut}>- Zoom</button>
    <button on:click={onZoomIn}>+ Zoom</button>
</div>

<style>
    .zoom-controls {
        display: flex;
        gap: 0.5rem;
        align-items: center;
        margin-bottom: 0.5rem;
    }
    button {
        padding: 0.25rem 0.6rem;
        font-weight: bold;
        cursor: pointer;
    }
</style>
