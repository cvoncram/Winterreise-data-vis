/**
 * Hands a rendered visualization to the browser as an SVG file.
 */
export function downloadSvg(svg: SVGSVGElement, filename: string) {
	const clone = svg.cloneNode(true) as SVGSVGElement;
	clone.setAttribute('xmlns', 'http://www.w3.org/2000/svg');
	clone.setAttribute('xmlns:xlink', 'http://www.w3.org/1999/xlink');
	clone.setAttribute('font-family', getComputedStyle(svg).fontFamily);

	// Elements laid out by flexbox have no width of their own in the file.
	if (!clone.getAttribute('width')) {
		const { width, height } = svg.getBoundingClientRect();
		clone.setAttribute('width', String(Math.round(width)));
		clone.setAttribute('height', String(Math.round(height)));
	}

	const blob = new Blob([new XMLSerializer().serializeToString(clone)], {
		type: 'image/svg+xml;charset=utf-8'
	});
	const url = URL.createObjectURL(blob);

	const a = document.createElement('a');
	a.href = url;
	a.download = filename.endsWith('.svg') ? filename : `${filename}.svg`;
	document.body.appendChild(a);
	a.click();
	a.remove();

	// Revoked on the next tick: revoking while the click is still being
	// handled aborts the download in some browsers.
	setTimeout(() => URL.revokeObjectURL(url), 0);
}
