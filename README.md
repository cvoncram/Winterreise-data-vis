# Winterreise Performance Visualization

*[English](#english) · [Deutsch](#deutsch)*

---

## English

A research tool for comparing recorded performances of Schubert's *Winterreise*.
It reads an annotated score together with per-beat measurements taken from 26
recordings, and makes the differences between interpretations visible and
measurable.

Three quantities are measured for every beat of every recording: **tempo** in
beats per minute, **dynamics** as a sound level in decibels, and **timbre** as
the spectral centroid in hertz. Because level and frequency response depend on
how a recording was made, the values are normalized before any comparison —
centred on the median of the recording and scaled by a corpus-wide robust
measure of spread — so that what is compared is musical shaping rather than
recording technique.

### What it does

| | |
|---|---|
| **Score viewer** | Engraves the score in the browser and highlights Dietrich Fischer-Dieskau's handwritten entries in his working copies. Individual elements can be clicked to trace them back to the source encoding. |
| **Line graph** | One parameter, one piece, any number of recordings, drawn as curves over a shared axis. |
| **Multi-parameter view** | A single performance as a ribbon encoding all three parameters at once: segment width from tempo, extent from dynamics, colour from timbre. A passage can be selected and carried over to a comparison view, where several recordings are shown side by side. |
| **Similarity network** | Computes distances between recordings using dynamic time warping and lays the result out as a graph, so that groupings become visible at a glance. Works on a single passage, one piece, half the cycle, or all of it. |

The data live in a separate private GitHub repository, which the application
only ever reads. There is no database and no local copy of the material.

### Requirements

- **Docker**, for the containerised installation — nothing else
- or **Python 3.12** and **Node 20.19+ / 22+** for the local one
- in either case, the GitHub App's private key (`.pem`), which is not part of
  this repository

Instructions are for Linux and macOS.

### Installation with Docker

Put the private key into `backend/`, then:

```bash
docker compose up --build
```

The application is then at **http://localhost:3000**.

```bash
docker compose down          # stop
docker compose logs -f       # follow the logs
```

If your key has a different file name, or port 3000 is taken, copy
`.env.example` to `.env` and adjust it there.

Only the frontend is published. Requests to `/db/…` are forwarded to the
backend by the SvelteKit server itself, so both halves share an origin and the
backend stays unreachable from outside. Its port is published to the loopback
interface alone, so that the interactive API documentation at
http://127.0.0.1:8000/docs remains available while working on the application.

The key is never part of an image: it is excluded from the build context and
mounted at run time as a Docker secret.

### Installation without Docker

Two processes, so two terminals.

**Backend**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Listens on `http://127.0.0.1:8000`. The private key is expected beside
`github_auth.py`; `GITHUB_PRIVATE_KEY_PATH` points it elsewhere.

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173`. Vite forwards `/db/…` to the backend, which
therefore has to be running.

### Layout

```
backend/     FastAPI server — GitHub access, MEI parsing, statistics, distances
frontend/    SvelteKit application — pages, components, visualizations
```

Each has a README of its own describing its structure.

---

## Deutsch

Ein Forschungswerkzeug zum Vergleich eingespielter Aufführungen von Schuberts
*Winterreise*. Es liest einen annotierten Notentext zusammen mit
schlagweise erhobenen Messwerten aus 26 Aufnahmen und macht die Unterschiede
zwischen Interpretationen sichtbar und messbar.

Für jeden Schlag jeder Aufnahme liegen drei Größen vor: das **Tempo** in
Schlägen pro Minute, die **Dynamik** als Pegel in Dezibel und die
**Klangfarbe** als spektraler Schwerpunkt in Hertz. Da Pegel und Frequenzgang
davon abhängen, wie eine Aufnahme entstanden ist, werden die Werte vor jedem
Vergleich normalisiert — zentriert auf den Median der Aufnahme und skaliert
mit einem korpusweiten robusten Streuungsmaß —, sodass verglichen wird, was
gestaltet wurde, und nicht, wie aufgenommen wurde.

### Funktionen

| | |
|---|---|
| **Partiturbetrachter** | Setzt den Notentext im Browser und hebt die handschriftlichen Eintragungen Dietrich Fischer-Dieskaus in seinen Arbeitsexemplaren farblich hervor. Einzelne Elemente lassen sich anklicken und auf ihre Kodierung zurückverfolgen. |
| **Liniendiagramm** | Ein Parameter, ein Lied, beliebig viele Aufnahmen, als Kurven über einer gemeinsamen Achse. |
| **Mehrparameter-Darstellung** | Eine Aufführung als Band, das alle drei Parameter zugleich kodiert: Segmentbreite aus dem Tempo, Ausdehnung aus der Dynamik, Farbe aus der Klangfarbe. Ein Ausschnitt lässt sich auswählen und in eine Vergleichsansicht übernehmen, in der mehrere Aufnahmen untereinander stehen. |
| **Ähnlichkeitsnetzwerk** | Berechnet Distanzen zwischen Aufnahmen mittels Dynamic Time Warping und ordnet das Ergebnis als Graph an, sodass Gruppierungen auf einen Blick erkennbar werden. Wahlweise für einen Ausschnitt, ein Lied, eine Zyklushälfte oder den ganzen Zyklus. |

Die Daten liegen in einem eigenen, privaten GitHub-Repositorium, auf das die
Anwendung ausschließlich lesend zugreift. Es gibt weder eine Datenbank noch
eine lokale Kopie des Materials.

### Voraussetzungen

- **Docker** für die Installation in Containern — sonst nichts
- oder **Python 3.12** und **Node 20.19+ / 22+** für die lokale Installation
- in beiden Fällen der private Schlüssel der GitHub App (`.pem`), der nicht
  Bestandteil dieses Repositoriums ist

Die Anleitungen gelten für Linux und macOS.

### Installation mit Docker

Den privaten Schlüssel nach `backend/` legen, dann:

```bash
docker compose up --build
```

Die Anwendung ist anschließend unter **http://localhost:3000** erreichbar.

```bash
docker compose down          # anhalten
docker compose logs -f       # Protokoll mitlesen
```

Heißt der Schlüssel anders oder ist Port 3000 belegt, genügt es,
`.env.example` nach `.env` zu kopieren und dort anzupassen.

Veröffentlicht wird allein das Frontend. Anfragen an `/db/…` leitet der
SvelteKit-Server selbst ans Backend weiter, sodass beide Hälften denselben
Ursprung teilen und das Backend von außen unerreichbar bleibt. Sein Port ist
nur auf der Loopback-Schnittstelle veröffentlicht, damit die interaktive
Schnittstellenbeschreibung unter http://127.0.0.1:8000/docs während der Arbeit
an der Anwendung erreichbar bleibt.

Der Schlüssel gelangt nie in ein Abbild: Er ist vom Build-Kontext
ausgeschlossen und wird zur Laufzeit als Docker-Secret eingehängt.

### Installation ohne Docker

Zwei Prozesse, also zwei Terminals.

**Backend**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Hört auf `http://127.0.0.1:8000`. Der private Schlüssel wird neben
`github_auth.py` erwartet; `GITHUB_PRIVATE_KEY_PATH` verweist auf einen
anderen Ort.

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Läuft auf `http://localhost:5173`. Vite leitet `/db/…` an das Backend weiter,
das folglich laufen muss.

### Aufbau

```
backend/     FastAPI-Server — GitHub-Zugriff, MEI-Parser, Statistik, Distanzen
frontend/    SvelteKit-Anwendung — Seiten, Komponenten, Visualisierungen
```

Beide besitzen eine eigene README, die ihre Struktur beschreibt.
