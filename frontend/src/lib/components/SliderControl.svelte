<script lang="ts">
    export let label: string;
    export let min = 0;
    export let max = 100;
    export let value = 50;
    export let onChange: (value: number) => void;
    
    const sliderId = 'slider-' + Math.random().toString(36).substring(2, 9);
    
    function handleInput(event: Event) {
        const target = event.target as HTMLInputElement;
        onChange(+target.value);
    }
</script>

<div class="slider-control">
    <label for={sliderId}>{label}</label>
    <label for={sliderId}>{value}</label>
    <input id={sliderId} type="range" min={min} max={max} value={value} on:input={handleInput} />
</div>

<style>
    .slider-control {
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        gap: 0.5rem;
        margin-bottom: 0.5rem;
    }
    input[type="range"] {
        flex: 0;
    }
</style>
