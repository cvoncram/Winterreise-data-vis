<script lang="ts">
    let { currentPage, totalPages, onPrev, onNext}: {currentPage: number; totalPages: number; onPrev: () => void; onNext: () => void} = $props(); 
</script>

<div class="page-controls">
    <button onclick={onPrev} disabled={currentPage === 1}>Prev Page</button>
    <span>Page {currentPage} / {totalPages}</span>
    <button onclick={onNext} disabled={currentPage === totalPages}>Next Page</button>
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
