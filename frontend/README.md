# Frontend — SvelteKit

*[English](#english) · [Deutsch](#deutsch)*

Installation and start-up are described in the [project README](../README.md).

---

## English

```
frontend/
├── src/
│   ├── routes/          the pages; the directory structure is the URL structure
│   ├── lib/             everything reusable
│   ├── hooks.server.ts  forwards /db to the backend (production only)
│   ├── app.html         the HTML shell
│   ├── app.css          Tailwind entry point
│   └── types/           type declarations for libraries that ship none
├── static/              served unprocessed: favicon, screenshots, images
├── svelte.config.js     adapter (Node, for the container)
├── vite.config.ts       plugins and the dev-time proxy for /db
└── Dockerfile
```

### `src/routes/` — the pages

SvelteKit routes by file system: a directory containing `+page.svelte` becomes
a page at the corresponding path. The leading plus sign marks files with
special meaning to the framework.

| Path | Page |
|---|---|
| `/` | landing page |
| `/scores` | score viewer |
| `/visualizations` | overview of the three visualizations |
| `/visualizations/line-graph` | one parameter as curves |
| `/visualizations/multi-parameter` | one performance as a semicircular ribbon |
| `/visualizations/multi-parameter/multi-performance` | several performances as linear ribbons |
| `/visualizations/dtw-network` | similarity network |
| `/documentation` | the accompanying explanations |

`+layout.svelte` at the top level defines the frame common to every page —
navigation bar, footer, and the overlay for the ribbon transition. It is not
recreated when moving between pages, which is what lets that transition
outlive the change of page.

Alongside them, each visualization directory holds a `pageState.svelte.ts`. A
page's component is destroyed on leaving and created afresh on returning,
which would discard fetched data and computed results; declaring the state at
module level instead lets it survive navigation. The `.svelte.ts` extension is
required for runes to work outside a component.

### `src/lib/` — the reusable parts

| Path | Contents |
|---|---|
| `components/containers/` | the displays proper: `MeiViewer` (engraving via Verovio), `MeiCircularRibbon` and `MeiLinearRibbon` (the two ribbon forms), `RibbonMorph` (the transition between them), `LineGraph`, `DtwNetwork`, `MeiTable`. They take data through properties only and cannot fetch anything themselves, which makes them independent of where the data came from. |
| `components/partials/` | the smaller, form-like pieces the control panels are built from — selectors for score, recordings, parameters, metric and range of measures — plus `Logo`, `Footer`, `PageControls` and `IntroGallery`. |
| `components/unused/` | two components no longer in use, kept for reference. |
| `layouts/` | `LandingPage`, the shared shape of the landing and overview pages. |
| `utils/performanceVisuals.ts` | the conversions both ribbons share: from a measured value and a reference figure to a number in the unit interval, and the choice of colour scale. |
| `utils/ribbonGeometry.ts` | the geometry common to both ribbon forms and the mapping between them that the transition interpolates. |
| `api.ts` | every call to the backend, one function per endpoint, returning typed results. |
| `types.ts` | the type definitions for everything crossing a component boundary or a network call. |
| `selection.svelte.ts` | the passage handed from the circular ribbon to the comparison page. Both pages are separate components that never exist at the same time, so this cannot be passed as a property. |
| `displaySettings.svelte.ts` | display preferences belonging to no single page — currently the colour scheme, which should survive a change of page. |
| `ribbonMorph.svelte.ts` | the state of the transition between the two ribbon forms. |

### The two paths to the backend

In development Vite forwards `/db/…` to `http://127.0.0.1:8000`; the
configuration is in `vite.config.ts`. In a container there is no Vite, and
`hooks.server.ts` takes over the same job. Either way both halves share an
origin, so no API address has to be configured into the client bundle and no
cross-origin request arises.

---

## Deutsch

```
frontend/
├── src/
│   ├── routes/          die Seiten; die Verzeichnisstruktur ist die Adressstruktur
│   ├── lib/             alles Wiederverwendbare
│   ├── hooks.server.ts  leitet /db ans Backend weiter (nur im Produktionsbetrieb)
│   ├── app.html         das HTML-Gerüst
│   ├── app.css          Einstiegspunkt für Tailwind
│   └── types/           Typdeklarationen für Bibliotheken, die keine mitbringen
├── static/              unverarbeitet ausgeliefert: Symbole, Bildschirmfotos, Bilder
├── svelte.config.js     Adapter (Node, für den Container)
├── vite.config.ts       Plugins und der Proxy für /db im Entwicklungsbetrieb
└── Dockerfile
```

### `src/routes/` — die Seiten

SvelteKit leitet die Adressen aus dem Dateisystem ab: Ein Verzeichnis mit einer
Datei `+page.svelte` wird zur Seite unter dem entsprechenden Pfad. Das
vorangestellte Pluszeichen kennzeichnet Dateien mit besonderer Bedeutung für
das Framework.

| Pfad | Seite |
|---|---|
| `/` | Startseite |
| `/scores` | Partiturbetrachter |
| `/visualizations` | Übersicht über die drei Visualisierungen |
| `/visualizations/line-graph` | ein Parameter als Kurven |
| `/visualizations/multi-parameter` | eine Aufführung als halbkreisförmiges Band |
| `/visualizations/multi-parameter/multi-performance` | mehrere Aufführungen als lineare Bänder |
| `/visualizations/dtw-network` | Ähnlichkeitsnetzwerk |
| `/documentation` | die begleitenden Erläuterungen |

`+layout.svelte` auf oberster Ebene definiert den Rahmen, der allen Seiten
gemeinsam ist — Navigationsleiste, Seitenfuß und die Überlagerung für den
Übergang zwischen den Bandformen. Er wird beim Wechsel zwischen Seiten nicht
neu erzeugt, was diesen Übergang den Seitenwechsel überdauern lässt.

Daneben enthält jedes Visualisierungsverzeichnis eine `pageState.svelte.ts`.
Die Komponente einer Seite wird beim Verlassen zerstört und beim Zurückkehren
neu erzeugt, was abgerufene Daten und berechnete Ergebnisse verwerfen würde;
auf Modulebene deklarierter Zustand überlebt die Navigation dagegen. Die
Endung `.svelte.ts` ist nötig, damit Runen außerhalb einer Komponente wirken.

### `src/lib/` — die wiederverwendbaren Teile

| Pfad | Inhalt |
|---|---|
| `components/containers/` | die eigentlichen Darstellungen: `MeiViewer` (Notensatz mittels Verovio), `MeiCircularRibbon` und `MeiLinearRibbon` (die beiden Bandformen), `RibbonMorph` (der Übergang zwischen ihnen), `LineGraph`, `DtwNetwork`, `MeiTable`. Sie nehmen Daten ausschließlich über Eigenschaften entgegen und können selbst keine Abrufe auslösen, was sie unabhängig davon macht, woher die Daten stammen. |
| `components/partials/` | die kleineren, formularartigen Bausteine, aus denen die Auswahlbereiche zusammengesetzt sind — Auswahl von Partitur, Aufnahmen, Parametern, Distanzmaß und Taktbereich — sowie `Logo`, `Footer`, `PageControls` und `IntroGallery`. |
| `components/unused/` | zwei nicht mehr verwendete Komponenten, zur Ansicht aufbewahrt. |
| `layouts/` | `LandingPage`, die gemeinsame Gestalt von Start- und Übersichtsseiten. |
| `utils/performanceVisuals.ts` | die von beiden Bändern gemeinsam genutzten Umrechnungen: von einem Messwert und einer Bezugsgröße zu einem Wert im Einheitsintervall, samt Auswahl der Farbskala. |
| `utils/ribbonGeometry.ts` | die beiden Bandformen gemeinsame Geometrie und die Abbildung zwischen ihnen, die der Übergang interpoliert. |
| `api.ts` | sämtliche Aufrufe an das Backend, je eine Funktion pro Endpunkt, mit typisierter Rückgabe. |
| `types.ts` | die Typdefinitionen für alles, was eine Komponentengrenze oder einen Netzwerkaufruf überschreitet. |
| `selection.svelte.ts` | der Ausschnitt, den die Kreisdarstellung an die Vergleichsseite übergibt. Beide Seiten sind getrennte Komponenten, die nie gleichzeitig existieren, sodass diese Angabe nicht als Eigenschaft weitergereicht werden kann. |
| `displaySettings.svelte.ts` | Darstellungsvorlieben, die zu keiner einzelnen Seite gehören — gegenwärtig das Farbschema, das einen Seitenwechsel überdauern soll. |
| `ribbonMorph.svelte.ts` | der Zustand des Übergangs zwischen den beiden Bandformen. |

### Die zwei Wege zum Backend

Im Entwicklungsbetrieb leitet Vite `/db/…` an `http://127.0.0.1:8000` weiter;
die Konfiguration steht in `vite.config.ts`. Im Container gibt es kein Vite,
dort übernimmt `hooks.server.ts` dieselbe Aufgabe. In beiden Fällen teilen
sich die beiden Hälften einen Ursprung, sodass keine API-Adresse ins
Client-Bündel muss und keine ursprungsübergreifende Anfrage entsteht.
