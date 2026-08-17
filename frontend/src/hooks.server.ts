import type { Handle } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

/**
 * Forwards /db requests to the FastAPI backend.
 *
 * During development Vite's own proxy does this and the hook never sees such
 * a request. In a container there is no Vite, so the SvelteKit server has to
 * take over — otherwise the browser would have to address the backend
 * directly, which would mean exposing its port, configuring its URL into the
 * client bundle, and reintroducing cross-origin requests. Proxying keeps the
 * backend unreachable from outside and everything on one origin.
 */

const BACKEND = env.BACKEND_URL ?? 'http://127.0.0.1:8000';

// Hop-by-hop headers describe the single connection they arrived on and must
// not be passed along. `host` would name the frontend, not the backend.
const STRIP_REQUEST = new Set(['host', 'connection', 'keep-alive', 'upgrade']);

// undici decompresses the body transparently; forwarding the encoding headers
// unchanged would tell the browser to decompress it a second time.
const STRIP_RESPONSE = new Set(['content-encoding', 'content-length', 'transfer-encoding', 'connection']);

export const handle: Handle = async ({ event, resolve }) => {
	if (!event.url.pathname.startsWith('/db/')) {
		return resolve(event);
	}

	const target = new URL(event.url.pathname + event.url.search, BACKEND);

	const headers = new Headers();
	for (const [key, value] of event.request.headers) {
		if (!STRIP_REQUEST.has(key.toLowerCase())) headers.set(key, value);
	}

	const init: RequestInit = { method: event.request.method, headers };
	if (event.request.method !== 'GET' && event.request.method !== 'HEAD') {
		init.body = await event.request.arrayBuffer();
	}

	let upstream: Response;
	try {
		upstream = await fetch(target, init);
	} catch (error) {
		// The backend being unreachable is an infrastructure fault, not a bad
		// request; reporting it as such keeps it distinguishable in the client.
		console.error(`Proxy to ${target} failed:`, error);
		return new Response(JSON.stringify({ detail: 'Backend unreachable' }), {
			status: 502,
			headers: { 'content-type': 'application/json' }
		});
	}

	const responseHeaders = new Headers();
	for (const [key, value] of upstream.headers) {
		if (!STRIP_RESPONSE.has(key.toLowerCase())) responseHeaders.set(key, value);
	}

	return new Response(upstream.body, { status: upstream.status, headers: responseHeaders });
};
