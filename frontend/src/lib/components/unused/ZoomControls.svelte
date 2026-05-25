<!-- deprecated, only sliderControl is used -->

<script lang="ts">
    let {onZoomIn, onZoomOut}: {onZoomIn: () => void; onZoomOut: () => void;} = $props();
</script>

<div class="zoom-controls">
    <button onclick={onZoomOut}>- Zoom</button>
    <button onclick={onZoomIn}>+ Zoom</button>
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
