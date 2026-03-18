# Data-Vis Project

This project is a web-based MEI viewer that fetches musical scores from a GitHub repository and displays them interactively. It consists of:

- **Backend**: FastAPI server that fetches MEI files from GitHub.  
- **Frontend**: SvelteKit app that renders the MEI files using Verovio.  

---

## Backend (FastAPI)

### Requirements

Python >= 3.12

Minimal required packages:

    fastapi==0.128.3
    uvicorn==0.40.0
    pydantic==2.12.5
    pydantic_core==2.41.5
    starlette==0.52.1
    requests==2.32.5
    PyJWT==2.11.0
    anyio==4.12.1
    cryptography==46.0.5

Create and activate a virtual environment in /backend:

    python3 -m venv venv
    source venv/bin/activate    

Install requirements:

    pip install -r requirements.txt

### Running the Backend

1. Configure your GitHub token and repository info in the backend code.
2. Activate the virtual environment (if you haven't done so already) and start the FastAPI server:

    source venv/bin/activate
    uvicorn main:app --reload

- Backend listens on `http://127.0.0.1:8000`.
- Endpoints:

| Endpoint | Description |
|----------|-------------|
| `/db/scores-folder` | Returns JSON list of MEI files in GitHub folder. |
| `/db/file?path=<file-path>` | Returns JSON containing the MEI file content. |

---

## Frontend (SvelteKit)

### Requirements

- Node.js >= 20  
- npm >= 9 (or yarn/pnpm)

All dependencies are listed in `package.json`. Install with:

    npm install

### Running the Frontend

    npm run dev

- Opens the app on `http://localhost:5173`.
- Frontend communicates with backend via `/db` routes.

### Proxy Configuration

In `vite.config.js`, ensure the following to forward `/db` requests to the backend:

    server: {
      proxy: {
        '/db': {
          target: 'http://127.0.0.1:8000',
          changeOrigin: true
        }
      }
    }

This ensures that requests like `/db/scores-folder` and `/db/file` are routed to FastAPI, while the frontend serves the UI.

---

## Using the App

1. Open the frontend in your browser.  
2. The MEI viewer loads a dropdown menu of scores from GitHub.  
3. Select a file from the dropdown to display it in the viewer.  
4. Use the sliders and page controls to adjust layout and navigate the score.

---

## Notes

- This setup is **temporary**: the frontend requests GitHub files through the backend. In production, the backend could fetch directly without exposing folder paths.  
- MEI files are rendered with [Verovio](https://www.verovio.org/).  
- The frontend uses [Tailwind CSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/) for UI components.

