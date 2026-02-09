# MEI Score Viewer – Frontend (SvelteKit)

This is the SvelteKit frontend for displaying MEI music scores using Verovio.  
It communicates with the FastAPI backend, which serves MEI files from a GitHub repository.

---

## Tech Stack

- SvelteKit
- TypeScript
- Vite
- Verovio (MEI rendering)
- DaisyUI / Tailwind (UI)

---

## Requirements

- Node 18+
- npm

---

## Installation

```bash
npm install
```

---

## Development Server

```bash
npm run dev
```

The app runs on:

```
http://localhost:5173
```

---

## Proxy Configuration (important)

The frontend talks to the backend via `/db/*` routes.

`vite.config.ts`:

```ts
server: {
  proxy: {
    '/db': {
      target: 'http://127.0.0.1:8000',
      changeOrigin: true
    }
  }
}
```

This means:

Frontend request:

```
/db/scores-folder
```

→ is transparently forwarded to:

```
http://127.0.0.1:8000/db/scores-folder
```

---

## How it works

1. On page load, the app fetches:

   ```
   /db/scores-folder
   ```

   to populate the dropdown with available MEI files.

2. When a file is selected, the frontend fetches:

   ```
   /db/file?path=scores/<filename>.mei
   ```

3. The returned MEI content is passed directly to Verovio inside `MeiViewer.svelte`.

---

## Important Files

| File | Purpose |
|-----|---------|
| `+page.svelte` | Fetches file list and selected MEI content |
| `ScoreSelector.svelte` | Dropdown UI |
| `MeiViewer.svelte` | Verovio integration and rendering |
| `src/app.html` | Must contain correct favicon path |
| `vite.config.ts` | Proxy to backend |

---

## Common Pitfalls

### Dropdown empty
Check that `/db/scores-folder` returns JSON in the browser console.

### `fetch` SSR error
All fetches must be inside `onMount`.

### Favicon dynamic import error
`static/favicon.ico` must exist and `app.html` must use:

```html
<link rel="icon" href="%sveltekit.assets%/favicon.ico" />
```

---

## Production Build

```bash
npm run build
npm run preview
```
