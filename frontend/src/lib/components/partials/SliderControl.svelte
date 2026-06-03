<script lang="ts">

	let {label, min = 0, max = 100, value = 50, onChange}: {label: string; min: number; max: number; value: number; onChange: (value: number) => void } = $props();

	const sliderId = 'slider-' + Math.random().toString(36).substring(2, 9);

	let localValue = $derived(value);

	function handleInput(event: Event) {
		const target = event.target as HTMLInputElement;
		localValue = +target.value;
	}

	function handleChange(event: Event) {
		const target = event.target as HTMLInputElement;
		onChange(+target.value);
	}
</script>

<div class="slider-control">
	<label for={sliderId}>{label}</label>
	<label for={sliderId}>{localValue}</label>

	<input
		id={sliderId}
		type="range"
		min={min}
		max={max}
		value={value}
		oninput={handleInput}
		onchange={handleChange}
	/>
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
