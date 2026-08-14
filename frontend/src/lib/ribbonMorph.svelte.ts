import type { MorphSegment, PolarFrame } from '$lib/utils/ribbonGeometry';

/**
 * State for the transition from the circular to the linear ribbon.
 *
 * Lives at module scope for the same reason `selection` does: navigating
 * destroys the source component before the target exists, so the segments and
 * their starting geometry have to outlive both. The overlay that draws them is
 * mounted in the root layout, which survives navigation.
 */
export const morph = $state({
	/** True from the click until the transition finishes or is abandoned. */
	active: false,
	segments: [] as MorphSegment[],
	/** Where the circular ribbon was on screen when the click happened. */
	from: null as PolarFrame | null,
	/** Bounding box of the target ribbon, reported once it has rendered. */
	to: null as DOMRect | null,
	/** 0 = circular, 1 = linear. */
	t: 0
});

export function reset() {
	morph.active = false;
	morph.segments = [];
	morph.from = null;
	morph.to = null;
	morph.t = 0;
}
