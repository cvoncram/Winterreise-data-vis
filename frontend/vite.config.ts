import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
    plugins: [sveltekit(), tailwindcss()],
    optimizeDeps: {},
    server: {
        proxy: {
            '/api': {
                target: 'http://127.0.0.1:8000',
                changeOrigin: true
            }
        }
    }
});
