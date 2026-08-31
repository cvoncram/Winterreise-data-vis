import type { MorphSegment, PolarFrame } from '$lib/utils/ribbonGeometry';

/**
 * State for the transition from the circular to the linear ribbon.
 */
export const morph = $state({
	active: false,
	segments: [] as MorphSegment[],
	/** Where the circular ribbon was on screen when the click happened. */
	from: null as PolarFrame | null,
	/** Bounding box of the target ribbon, reported once it has rendered. */
	to: null as DOMRect | null,
	t: 0
});

export function reset() {
	morph.active = false;
	morph.segments = [];
	morph.from = null;
	morph.to = null;
	morph.t = 0;
}
