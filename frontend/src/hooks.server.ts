import type { Handle } from '@sveltejs/kit';
import { env } from '$env/dynamic/private';

/** Forwards /db requests to the FastAPI backend. */

const BACKEND = env.BACKEND_URL ?? 'http://127.0.0.1:8000';

// Request headers that are not forwarded.
const STRIP_REQUEST = new Set(['host', 'connection', 'keep-alive', 'upgrade']);

// Response headers that are not forwarded.
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
		// Backend unreachable.
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
