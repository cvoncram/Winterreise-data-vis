# Frontend — SvelteKit

*[English](#english) · [Deutsch](#deutsch)*

Installation and start-up are described in the [project README](../README.md).

---

## English

```
frontend/
├── src/
│   ├── routes/          pages; the directory structure is the URL structure
│   ├── lib/             components, API client, types, shared state, utilities
│   ├── hooks.server.ts  forwards /db to the backend (production)
│   ├── app.html         HTML shell
│   ├── app.css          Tailwind/DaisyUI entry point
│   └── types/           type declarations for untyped libraries
├── static/              favicon, images, screenshots
├── svelte.config.js     Node adapter
├── vite.config.ts       plugins and the /db proxy (development)
└── Dockerfile
```

### `src/routes/`

| Path | Page |
|---|---|
| `/` | landing page: timeline and map of the recordings |
| `/scores` | score viewer |
| `/visualizations` | overview of the visualizations |
| `/visualizations/line-graph` | one parameter as curves or table |
| `/visualizations/multi-parameter` | one performance as a semicircular ribbon |
| `/visualizations/multi-parameter/multi-performance` | a passage from several performances as linear ribbons, with the score |
| `/visualizations/dtw-network` | similarity network and matrix, pair detail view |
| `/documentation` | user documentation |

`+layout.svelte` holds the navigation bar, footer and the overlay for the
ribbon transition. Each visualization has a `pageState.svelte.ts` with its
module-level state, which persists across page changes.

### `src/lib/`

| Path | Contents |
|---|---|
| `components/containers/` | the displays: `MeiViewer`, `MeiCircularRibbon`, `MeiLinearRibbon`, `RibbonMorph`, `LineGraph`, `DtwNetwork`, `DtwMatrix`, `MeiTable`, `MeiMultiTable`, `Timeline`, `PerfMap` |
| `components/partials/` | controls (score, recording, parameter, metric, measure range, colour scheme), CSV and SVG export (`CsvTable`, `DtwMatrixCsv`, `LineGraphCsv`, `SvgDownloadButton`), `Logo`, `Footer`, `PageControls`, `IntroGallery` |
| `components/unused/` | components no longer in use |
| `layouts/` | `LandingPage`, shared layout of overview pages |
| `utils/` | `performanceVisuals.ts` (normalized values → [0, 1], colour schemes), `ribbonGeometry.ts` (ribbon geometry and morph mapping), `downloadSvg.ts` |
| `api.ts` | one function per backend endpoint, typed results; DTW analysis also as a stream with progress |
| `types.ts` | shared type definitions |
| `selection.svelte.ts` | passage handed from the semicircular ribbon to the comparison page |
| `displaySettings.svelte.ts` | colour scheme shared across pages |
| `ribbonMorph.svelte.ts` | state of the ribbon transition |

### Backend connection

Development: Vite forwards `/db/…` to `http://127.0.0.1:8000`
(`vite.config.ts`). Production: `hooks.server.ts` forwards `/db/…` to
`BACKEND_URL`.

Note: This documentation was generated with the help of Generative AI.

---

## Deutsch

```
frontend/
├── src/
│   ├── routes/          Seiten; die Verzeichnisstruktur ist die Adressstruktur
│   ├── lib/             Komponenten, API-Client, Typen, geteilter Zustand, Hilfsfunktionen
│   ├── hooks.server.ts  leitet /db an das Backend weiter (Produktion)
│   ├── app.html         HTML-Gerüst
│   ├── app.css          Einstiegspunkt für Tailwind/DaisyUI
│   └── types/           Typdeklarationen für Bibliotheken ohne Typen
├── static/              Favicon, Bilder, Bildschirmfotos
├── svelte.config.js     Node-Adapter
├── vite.config.ts       Plugins und der /db-Proxy (Entwicklung)
└── Dockerfile
```

### `src/routes/`

| Pfad | Seite |
|---|---|
| `/` | Startseite: Zeitleiste und Karte der Aufnahmen |
| `/scores` | Partiturbetrachter |
| `/visualizations` | Übersicht über die Visualisierungen |
| `/visualizations/line-graph` | ein Parameter als Kurven oder Tabelle |
| `/visualizations/multi-parameter` | eine Aufführung als halbkreisförmiges Band |
| `/visualizations/multi-parameter/multi-performance` | ein Abschnitt aus mehreren Aufführungen als lineare Bänder, mit Notentext |
| `/visualizations/dtw-network` | Ähnlichkeitsnetzwerk und Matrix, Detailansicht je Paar |
| `/documentation` | Benutzerdokumentation |

`+layout.svelte` enthält Navigationsleiste, Seitenfuß und die Überlagerung für
den Übergang zwischen den Bandformen. Jede Visualisierung hat eine
`pageState.svelte.ts` mit ihrem Zustand auf Modulebene, der Seitenwechsel
überdauert.

### `src/lib/`

| Pfad | Inhalt |
|---|---|
| `components/containers/` | die Darstellungen: `MeiViewer`, `MeiCircularRibbon`, `MeiLinearRibbon`, `RibbonMorph`, `LineGraph`, `DtwNetwork`, `DtwMatrix`, `MeiTable`, `MeiMultiTable`, `Timeline`, `PerfMap` |
| `components/partials/` | Bedienelemente (Partitur, Aufnahme, Parameter, Distanzmaß, Taktbereich, Farbschema), CSV- und SVG-Export (`CsvTable`, `DtwMatrixCsv`, `LineGraphCsv`, `SvgDownloadButton`), `Logo`, `Footer`, `PageControls`, `IntroGallery` |
| `components/unused/` | nicht mehr verwendete Komponenten |
| `layouts/` | `LandingPage`, gemeinsames Layout der Übersichtsseiten |
| `utils/` | `performanceVisuals.ts` (normalisierte Werte → [0, 1], Farbschemata), `ribbonGeometry.ts` (Bandgeometrie und Übergangsabbildung), `downloadSvg.ts` |
| `api.ts` | eine Funktion je Backend-Endpunkt, typisierte Rückgabe; DTW-Analyse auch als Stream mit Fortschritt |
| `types.ts` | gemeinsame Typdefinitionen |
| `selection.svelte.ts` | der Abschnitt, den das halbkreisförmige Band an die Vergleichsseite übergibt |
| `displaySettings.svelte.ts` | seitenübergreifendes Farbschema |
| `ribbonMorph.svelte.ts` | Zustand des Übergangs zwischen den Bandformen |

### Verbindung zum Backend

Entwicklung: Vite leitet `/db/…` an `http://127.0.0.1:8000` weiter
(`vite.config.ts`). Produktion: `hooks.server.ts` leitet `/db/…` an
`BACKEND_URL` weiter.

Anmerkung: Diese Dokumentation wurde mithilfe von generativer KI erstellt.
