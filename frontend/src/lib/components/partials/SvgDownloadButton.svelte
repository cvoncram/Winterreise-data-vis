<script lang="ts">
	import { downloadSvg } from '$lib/utils/downloadSvg';

	let { container, filename = 'visualization', label = 'Download SVG' }: {
		container?: HTMLElement;
		filename?: string;
		label?: string;
	} = $props();

	function save() {
		const svg = container?.querySelector('svg');
		if (svg) downloadSvg(svg as SVGSVGElement, filename);
	}
</script>

<button class="btn btn-sm btn-ghost" onclick={save} disabled={!container}>
	{label}
</button>
