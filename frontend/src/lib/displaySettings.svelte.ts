/**
 * Display preferences shared across visualization pages.
 *
 * Unlike the per-page state modules, these belong to no single page: a colour
 * scheme chosen on the circular ribbon should still apply after switching to
 * the comparison view, since it is a viewing preference and carries no
 * meaning about the data.
 */
export const display = $state({
	colorScheme: 'viridisScheme'
});
