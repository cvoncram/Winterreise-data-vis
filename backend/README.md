# Backend — FastAPI

*[English](#english) · [Deutsch](#deutsch)*

Installation and start-up are described in the [project README](../README.md).

---

## English

```
backend/
├── main.py              application instance, CORS, router registration, /health
├── config.py            work-bound constants: repository, namespaces, piece titles
├── github_auth.py       authentication as a GitHub App
├── requirements.txt     pinned dependencies
├── Dockerfile
├── routers/             HTTP layer
└── services/            domain logic, no knowledge of HTTP
```

### The division between routers and services

A router contains only what has to do with the HTTP protocol: declaring path
and method, accepting and checking parameters, translating failures into status
codes, assembling the response. Everything else lives in `services/`, in
modules that know nothing of HTTP and can therefore be called with constructed
inputs and checked in isolation — which matters most for the numerically
demanding parts, where correctness is hardest to establish by inspection.

### `routers/`

| File | Endpoints |
|---|---|
| `files.py` | `/db/file`, `/db/file-measures`, `/db/parsed-file`, `/db/parsed-measures` — MEI as raw text or already parsed, optionally cut to a range of measures |
| `scores.py` | `/db/scores-folder` — the score directory as a sorted tree |
| `performances.py` | `/db/performances`, `/db/performance-files` — recordings and the pieces each contains |
| `analysis.py` | `/db/analysis` — the distance matrix, the most parameter-rich endpoint |
| `stats.py` | `/db/stats/…` — normalization figures, data-quality report, cache refresh |

### `services/`

| File | Purpose |
|---|---|
| `githubClient.py` | Every outgoing call to GitHub, in three functions: file contents, directory listing, full file tree. Base URLs, headers, base64 decoding and timeouts are thus stated exactly once. |
| `pathSafety.py` | Two checks ensuring that a path supplied by the client cannot leave the permitted area. Small but security-critical: the backend is unauthenticated access to a private repository, and this restriction is what confines it. |
| `meiParser.py` | Turns MEI documents into the row structure the application works with, extracts the calibration block, and cuts scores to a range of measures. |
| `statsCalc.py` | Reads the normalization figures held in the database repository, keeps them briefly in memory, and selects those the requested scope calls for. Nothing is computed here — that happens in a GitHub Action in the database repository. |
| `dtwCalc.py` | Normalization of individual series and the pairwise distances. The alignment itself comes from `scipy` and `dtw-python`; what remains here is the assembly of the matrix and the guards against comparing recordings that do not line up. |

### Other directories

`static/` holds the favicon, the one file served unprocessed. `venv/` and
`__pycache__/` are working directories and belong to neither the repository nor
the container image.

### The private key

The GitHub App's signing key is the one secret the system holds. It is expected
beside `github_auth.py`, is excluded from version control by `.gitignore` and
from the image by `.dockerignore`, and is mounted at run time under Docker.
`GITHUB_PRIVATE_KEY_PATH` points it elsewhere.

---

## Deutsch

```
backend/
├── main.py              Anwendungsinstanz, CORS, Registrierung der Router, /health
├── config.py            werkgebundene Konstanten: Repositorium, Namensräume, Liedtitel
├── github_auth.py       Authentifizierung als GitHub App
├── requirements.txt     festgelegte Abhängigkeiten
├── Dockerfile
├── routers/             HTTP-Schicht
└── services/            Fachlogik, ohne Kenntnis von HTTP
```

### Die Trennung von Routern und Services

Ein Router enthält ausschließlich das, was mit dem HTTP-Protokoll zu tun hat:
die Deklaration von Pfad und Methode, die Entgegennahme und Prüfung der
Parameter, die Übersetzung von Fehlzuständen in Statuscodes und die
Zusammenstellung der Antwort. Alles Übrige liegt in `services/`, in Modulen
ohne jede Kenntnis von HTTP, die sich folglich mit konstruierten Eingaben
aufrufen und isoliert prüfen lassen — was vor allem bei den numerisch
anspruchsvollen Teilen zählt, deren Korrektheit sich am schwersten durch
bloßes Lesen feststellen lässt.

### `routers/`

| Datei | Endpunkte |
|---|---|
| `files.py` | `/db/file`, `/db/file-measures`, `/db/parsed-file`, `/db/parsed-measures` — MEI als Rohtext oder bereits geparst, wahlweise auf einen Taktbereich beschnitten |
| `scores.py` | `/db/scores-folder` — das Partiturverzeichnis als sortierter Baum |
| `performances.py` | `/db/performances`, `/db/performance-files` — Aufnahmen und die darin enthaltenen Lieder |
| `analysis.py` | `/db/analysis` — die Distanzmatrix, der parameterreichste Endpunkt |
| `stats.py` | `/db/stats/…` — Normalisierungsgrößen, Datenqualitätsbericht, Leeren des Zwischenspeichers |

### `services/`

| Datei | Zweck |
|---|---|
| `githubClient.py` | Sämtliche ausgehenden Aufrufe an GitHub, in drei Funktionen: Dateiinhalt, Verzeichnisliste, vollständiger Dateibaum. Basis-URLs, Kopfzeilen, Base64-Dekodierung und Zeitlimits sind damit genau einmal formuliert. |
| `pathSafety.py` | Zwei Prüfungen, die sicherstellen, dass ein vom Client übergebener Pfad den zulässigen Bereich nicht verlässt. Klein, aber sicherheitskritisch: Das Backend ist ein unauthentifizierter Zugang zu einem privaten Repositorium, und diese Beschränkung ist es, die ihn eingrenzt. |
| `meiParser.py` | Überführt MEI-Dokumente in die Zeilenstruktur der Anwendung, entnimmt den Kalibrierungsblock und beschneidet Partituren auf einen Taktbereich. |
| `statsCalc.py` | Liest die im Datenbank-Repositorium hinterlegten Normalisierungsgrößen, hält sie kurz im Arbeitsspeicher vor und wählt daraus diejenigen aus, die der angefragte Geltungsbereich verlangt. Berechnet wird hier nichts — das geschieht in einer GitHub-Action im Datenbank-Repositorium. |
| `dtwCalc.py` | Normalisierung einzelner Messreihen und die paarweisen Distanzen. Die Ausrichtung selbst stammt aus `scipy` und `dtw-python`; hier verbleiben der Aufbau der Matrix und die Absicherung gegen Vergleiche zwischen Aufnahmen, die sich nicht decken. |

### Weitere Verzeichnisse

In `static/` liegt das Adressleistensymbol, die einzige unverarbeitet
ausgelieferte Datei. `venv/` und `__pycache__/` sind Arbeitsverzeichnisse und
gehören weder ins Repositorium noch ins Container-Abbild.

### Der private Schlüssel

Der Signierschlüssel der GitHub App ist das einzige Geheimnis des Systems. Er
wird neben `github_auth.py` erwartet, ist über `.gitignore` von der
Versionskontrolle und über `.dockerignore` vom Abbild ausgeschlossen und wird
unter Docker zur Laufzeit eingehängt. `GITHUB_PRIVATE_KEY_PATH` verweist auf
einen anderen Ort.
