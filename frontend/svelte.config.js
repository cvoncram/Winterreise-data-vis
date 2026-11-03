import adapter from '@sveltejs/adapter-node';

/** @type {import('@sveltejs/kit').Config} */
const config = {
	kit: {
		// Node server for the container.
		adapter: adapter()
	}
};

export default config;
