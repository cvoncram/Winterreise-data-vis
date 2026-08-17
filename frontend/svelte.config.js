import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		// adapter-node rather than adapter-auto: the application is deployed as
		// a container and needs a plain Node server it can start itself, which
		// adapter-auto only produces on platforms it recognises.
		adapter: adapter()
	}
};

export default config;
