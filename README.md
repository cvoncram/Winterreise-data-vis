# Winterreise Performance Visualization

*[English](#english) · [Deutsch](#deutsch)*

---

## English

A web application for comparing 26 recordings (1948–1990) of Schubert's
*Winterreise* by Dietrich Fischer-Dieskau. It shows the annotated score and
visualizes three per-beat measurements of every recording: **tempo** (bpm),
**dynamics** (dBFS) and **timbre** (spectral centroid, Hz).

### Private key

Contact me at cvoncram@gmail.com to request a private key (.pem) in order to access the database (https://github.com/cvoncram/Winterreise-database), which is necessary for using the application.

### Features

| | |
|---|---|
| **Landing page** | Timeline and map of where and when the recordings were made. |
| **Score viewer** | Engraves the MEI score in the browser (Verovio) and highlights Fischer-Dieskau's handwritten entries; clicking an element shows its encoded information. |
| **Line graph** | One parameter, one song, several recordings as curves; also as a table with CSV export. |
| **Multi-parameter view** | One recording of one song as a semicircular ribbon (width: duration, length: dynamics, colour: timbre). A selected passage can be compared across recordings as linear ribbons, next to the score. |
| **Similarity network** | Pairwise DTW distance and Kendall's τ between recordings, for a measure range, a song, half the cycle or the whole cycle; shown as a network or a matrix, with a detail view for every pair. |

### How it works

- The data (MEI scores and per-beat measurements) live in the GitHub
  repository `cvoncram/Winterreise-database`. The backend reads it through a
  GitHub App; there is no local copy and no database.
- A script in that repository computes the normalization statistics on every
  change and stores them as JSON next to the data.
- The backend (FastAPI) fetches and parses the files, normalizes the series and
  computes the distances. The frontend (SvelteKit) renders the score and the
  visualizations.
- The frontend forwards all requests to `/db/…` to the backend.

### Requirements

- **Docker**, or **Python 3.12** and **Node 20.19+ / 22+**
- the GitHub App's private key (`.pem`), which is not part of this repository

### Installation with Docker

Put the private key into `backend/`, then:

```bash
docker compose up --build    # build and start
docker compose down          # stop
docker compose logs -f       # follow the logs
```

The application runs at **http://localhost:3000**; the API documentation at
http://127.0.0.1:8000/docs.

For a key with a different file name or a different port, copy `.env.example`
to `.env` and adjust it.

### Installation without Docker

**Backend** (first terminal)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Runs at `http://127.0.0.1:8000`. The key is expected next to `github_auth.py`
or at `GITHUB_PRIVATE_KEY_PATH`.

**Frontend** (second terminal)

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`.

### Layout

```
backend/     FastAPI server: GitHub access, MEI parsing, statistics, DTW
frontend/    SvelteKit application: pages, components, visualizations
```

See the READMEs in both directories for their structure.

Note: This documentation was generated with the help of Generative AI.

---

## Deutsch

Eine Webanwendung zum Vergleich von 26 Aufnahmen (1948–1990) von Schuberts
*Winterreise* mit Dietrich Fischer-Dieskau. Sie zeigt den annotierten
Notentext und visualisiert drei schlagweise Messgrößen jeder Aufnahme:
**Tempo** (bpm), **Dynamik** (dBFS) und **Klangfarbe** (spektraler
Schwerpunkt, Hz).

### Privater Schlüssel

Wenden Sie sich an mich unter cvoncram@gmail.com, um einen privaten Schlüssel (.pem) zu erhalten, der benötigt wird, um lesend auf die Datenbank (https://github.com/cvoncram/Winterreise-database) zuzugreifen. 

### Funktionen

| | |
|---|---|
| **Startseite** | Zeitleiste und Karte der Aufnahmeorte und -daten. |
| **Partiturbetrachter** | Setzt die MEI-Partitur im Browser (Verovio) und hebt Fischer-Dieskaus handschriftliche Eintragungen hervor; ein Klick auf ein Element zeigt die kodierten Informationen. |
| **Liniendiagramm** | Ein Parameter, ein Lied, mehrere Aufnahmen als Kurven; auch als Tabelle mit CSV-Export. |
| **Mehrparameter-Darstellung** | Eine Aufnahme eines Liedes als halbkreisförmiges Band (Breite: Dauer, Länge: Dynamik, Farbe: Klangfarbe). Ein ausgewählter Abschnitt lässt sich als lineare Bänder mit anderen Aufnahmen vergleichen, neben dem Notentext. |
| **Ähnlichkeitsnetzwerk** | Paarweise DTW-Distanz und Kendalls τ zwischen Aufnahmen, für einen Taktbereich, ein Lied, eine Zyklushälfte oder den ganzen Zyklus; als Netzwerk oder Matrix, mit Detailansicht für jedes Paar. |

### Funktionsweise

- Die Daten (MEI-Partituren und schlagweise Messwerte) liegen im
  GitHub-Repositorium `cvoncram/Winterreise-database`. Das Backend liest es
  über eine GitHub App; es gibt weder eine lokale Kopie noch eine Datenbank.
- Ein Skript in diesem Repositorium berechnet bei jeder Änderung die
  Normalisierungsgrößen und legt sie als JSON neben den Daten ab.
- Das Backend (FastAPI) lädt und parst die Dateien, normalisiert die
  Messreihen und berechnet die Distanzen. Das Frontend (SvelteKit) setzt den
  Notentext und zeichnet die Visualisierungen.
- Das Frontend leitet alle Anfragen an `/db/…` an das Backend weiter.

### Voraussetzungen

- **Docker** oder **Python 3.12** und **Node 20.19+ / 22+**
- der private Schlüssel der GitHub App (`.pem`), der nicht Teil dieses
  Repositoriums ist

### Installation mit Docker

Den privaten Schlüssel nach `backend/` legen, dann:

```bash
docker compose up --build    # bauen und starten
docker compose down          # anhalten
docker compose logs -f       # Protokoll mitlesen
```

Die Anwendung läuft unter **http://localhost:3000**, die API-Dokumentation
unter http://127.0.0.1:8000/docs.

Für einen anders benannten Schlüssel oder einen anderen Port `.env.example`
nach `.env` kopieren und anpassen.

### Installation ohne Docker

**Backend** (erstes Terminal)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Läuft unter `http://127.0.0.1:8000`. Der Schlüssel wird neben
`github_auth.py` oder unter `GITHUB_PRIVATE_KEY_PATH` erwartet.

**Frontend** (zweites Terminal)

```bash
cd frontend
npm install
npm run dev
```

Läuft unter `http://localhost:5173`.

### Aufbau

```
backend/     FastAPI-Server: GitHub-Zugriff, MEI-Parser, Statistik, DTW
frontend/    SvelteKit-Anwendung: Seiten, Komponenten, Visualisierungen
```

Die READMEs in beiden Verzeichnissen beschreiben deren Struktur.

Anmerkung: Diese Dokumentation wurde mithilfe von generativer KI erstellt.

