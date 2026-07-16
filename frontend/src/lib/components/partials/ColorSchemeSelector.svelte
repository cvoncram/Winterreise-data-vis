<script lang="ts">
	let { selectedColorDropdown = $bindable("viridisScheme") }: { selectedColorDropdown?: string } = $props();
</script>

<label>
	<h3 class="mt-2 text-l">Color scheme</h3>
	<select class="select select-bordered w-full" bind:value={selectedColorDropdown}>
		<option value="viridisScheme">Viridis (default)</option>
		<option value="infernoScheme">Inferno</option>
		<option value="cividisScheme">Cividis</option>
		<option value="bluesScheme">Blue shades</option>
		<option value="greensScheme">Green shades</option>
		<option value="redsScheme">Red shades</option>
	</select>
</label>
