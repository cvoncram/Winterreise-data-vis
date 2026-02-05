<script lang="ts">
    export let currentPage: number;
    export let totalPages: number;
    export let onPrev: () => void;
    export let onNext: () => void;
</script>

<div class="page-controls">
    <button on:click={onPrev} disabled={currentPage === 1}>Prev Page</button>
    <span>Page {currentPage} / {totalPages}</span>
    <button on:click={onNext} disabled={currentPage === totalPages}>Next Page</button>
</div>

<style>
    .page-controls {
        display: flex;
        gap: 0.5rem;
        align-items: center;
    }
    button {
        padding: 0.3rem 0.8rem;
        font-size: 1rem;
        border-radius: 0.3rem;
        border: 1px solid #ccc;
        cursor: pointer;
        background: #f7f7f7;
    }
    button:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
