/**
 * Shared geometry for the circular and linear ribbons, and the mapping
 * between them used by the morph transition.
 */

/** Linear ribbon viewBox and margins. */
export const LINEAR = {
	width: 1000,
	height: 200,
	marginTop: 20,
	marginRight: 10,
	marginBottom: 30,
	marginLeft: 40,
	lengthMax: 2.5
} as const;

export type Point = { x: number; y: number };

/** Where the circular ribbon sits on screen, in page coordinates. */
export type PolarFrame = { cx: number; cy: number; radius: number };

/**
 * One beat, as captured from the circular ribbon. Angles follow d3.arc:
 * zero points up, increasing clockwise, spanning −π/2 … +π/2.
 */
export type MorphSegment = {
	startAngle: number;
	endAngle: number;
	thickness: number;
	color: string;
};

/**
 * Position along the axis, in [0,1].
 */
export function angleToUnit(angle: number): number {
	return (angle + Math.PI / 2) / Math.PI;
}

/** Point on the semicircle. `h` is the [0,1] height above the inner radius. */
export function polarPoint(angle: number, h: number, frame: PolarFrame): Point {
	const radius = frame.radius * (0.5 + h * 0.5);
	return {
		x: frame.cx + radius * Math.sin(angle),
		y: frame.cy - radius * Math.cos(angle)
	};
}

/**
 * Corresponding point on the linear ribbon, in page coordinates.
 */
export function linearPoint(u: number, h: number, rect: DOMRect): Point {
	const sx = rect.width / LINEAR.width;
	const sy = rect.height / LINEAR.height;

	const plotWidth = LINEAR.width - LINEAR.marginLeft - LINEAR.marginRight;
	const vx = LINEAR.marginLeft + u * plotWidth;

	const length = 0.5 + h * 2;
	const plotHeight = LINEAR.height - LINEAR.marginTop - LINEAR.marginBottom;
	const vy = LINEAR.height - LINEAR.marginBottom - (length / LINEAR.lengthMax) * plotHeight;

	return { x: rect.left + vx * sx, y: rect.top + vy * sy };
}

/** Baseline of the linear ribbon — where a bar of zero length would sit. */
export function linearBaseline(u: number, rect: DOMRect): Point {
	const sx = rect.width / LINEAR.width;
	const sy = rect.height / LINEAR.height;
	const plotWidth = LINEAR.width - LINEAR.marginLeft - LINEAR.marginRight;
	const vx = LINEAR.marginLeft + u * plotWidth;
	const vy = LINEAR.height - LINEAR.marginBottom;
	return { x: rect.left + vx * sx, y: rect.top + vy * sy };
}

export function lerp(a: Point, b: Point, t: number): Point {
	return { x: a.x + (b.x - a.x) * t, y: a.y + (b.y - a.y) * t };
}

/**
 * SVG path for one segment at interpolation position `t`, where 0 is the circular and 1 the linear layout.
 */
export function segmentPath(
	seg: MorphSegment,
	t: number,
	frame: PolarFrame,
	rect: DOMRect
): string {
	const u0 = angleToUnit(seg.startAngle);
	const u1 = angleToUnit(seg.endAngle);

	const corners: Point[] = [
		// inner edge, start → end
		lerp(polarPoint(seg.startAngle, 0, frame), linearBaseline(u0, rect), t),
		lerp(polarPoint(seg.endAngle, 0, frame), linearBaseline(u1, rect), t),
		// outer edge, end → start
		lerp(polarPoint(seg.endAngle, seg.thickness, frame), linearPoint(u1, seg.thickness, rect), t),
		lerp(polarPoint(seg.startAngle, seg.thickness, frame), linearPoint(u0, seg.thickness, rect), t)
	];

	return `M${corners.map((p) => `${p.x.toFixed(2)},${p.y.toFixed(2)}`).join('L')}Z`;
}
