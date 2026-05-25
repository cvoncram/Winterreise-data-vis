# Data-Vis Project

This project is a web-based MEI viewer that fetches musical scores from a GitHub repository and displays them interactively. It consists of:

- **Backend**: FastAPI server that fetches MEI files from GitHub.  
- **Frontend**: SvelteKit app that renders the MEI files using Verovio.  

---

## Backend (FastAPI)

### Installing the backend

Python >= 3.12 required

Create and activate a virtual environment in /backend:

    python3 -m venv venv
    source venv/bin/activate    

Install requirements:

    pip install -r requirements.txt

### Running the backend

1. Configure your GitHub token and repository info in the backend code.
2. Activate the virtual environment (if you haven't done so already) and start the FastAPI server:

    `source venv/bin/activate
    uvicorn main:app --reload`

- Backend listens on `http://127.0.0.1:8000`.
- Endpoints:

| Endpoint | Description |
|----------|-------------|
| `/db/scores-folder` | Returns JSON list of MEI files in the scores folder. |
| `/db/performances` | Returns JSON list of folders inside /performances. |
| `/db/performance-files?performance=<performance-folder>` | Returns JSON list of MEI files inside a performance folder. | 
| `/db/file?path=<file-path>` | Returns JSON containing the MEI file content. |
| `/db/parsed-file?path=<file-path>` | Returns parsed MEI performance data as JSON objects (measure, tempo, dynamics, timbre) |

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

## Notes

- This setup is **temporary**: the GitHub repository from which files are retrieved is only a test database.

#### Used frameworks, libraries, and packages

##### Frontend
- MEI files are rendered with [Verovio](https://www.verovio.org/).  
- [Tailwind CSS](https://tailwindcss.com/) and [DaisyUI](https://daisyui.com/) for UI components.

##### Backend
- [FastAPI](https://fastapi.tiangolo.com/) handles http requests and returns responses to the frontend.