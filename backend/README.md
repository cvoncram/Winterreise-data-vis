# Backend — FastAPI

*[English](#english) · [Deutsch](#deutsch)*

Installation and start-up are described in the [project README](../README.md).

---

## English

```
backend/
├── main.py              app instance, CORS, routers, /health
├── config.py            repository, MEI namespaces, song titles
├── github_auth.py       authentication as a GitHub App
├── requirements.txt     pinned dependencies
├── Dockerfile
├── routers/             endpoints (HTTP layer)
├── services/            data access and computations
└── static/              favicon
```

### `routers/`

| File | Endpoints |
|---|---|
| `files.py` | `/db/file`, `/db/file-measures`, `/db/parsed-file`, `/db/parsed-measures`: MEI as text or parsed rows, optionally cut to a measure range |
| `scores.py` | `/db/scores-folder`: the score directory as a sorted tree |
| `performances.py` | `/db/performances` (recordings with year, pianist, city, context), `/db/performance-files` (songs per recording), `/db/performances-detailed` (metadata for timeline and map) |
| `analysis.py` | `/db/analysis` (distance and τ matrices), `/db/analysis/stream` (the same as server-sent events with progress), `/db/analysis/pair` (detail view of one pair) |
| `stats.py` | `/db/stats/corpus`, `/db/stats/performances`, `/db/stats/report`, `/db/stats/normalization-reference`, `/db/stats/refresh` (clears the caches) |

### `services/`

| File | Purpose |
|---|---|
| `githubClient.py` | All requests to the GitHub API: file contents, directory listings, file tree; caches files for ten minutes. |
| `pathSafety.py` | Checks that paths from the client stay inside the permitted directories. |
| `meiParser.py` | Turns performance MEI files into per-beat rows, reads the calibration block, cuts scores to a measure range. |
| `statsCalc.py` | Reads the precomputed statistics from the database repository (cached for five minutes) and returns centres, scales and the covariance for a given scope and method. |
| `dtwCalc.py` | Normalization, DTW distances, Kendall's τ along the alignment path, τ floor, largest differences per pair. |

### Analysis

1. For each selected recording, the beats of every song in the scope are
   loaded; a beat is used only if every selected parameter has a value.
2. Each series is normalized: `(value − centre) / scale`, tempo and timbre on a
   log scale. Default method: mean/SD; alternatively median/MAD
   (`normalization=median`). Centres for dynamics and timbre are per recording,
   for tempo corpus-wide; scales are corpus-wide, per song or for the cycle
   depending on the scope.
3. Every song is aligned separately with DTW (`dtw-python`, step pattern
   `symmetric1`, Sakoe-Chiba band `|n − m| + 2`); local costs are Euclidean
   (optionally weighted) or Mahalanobis (corpus covariance) via `scipy`.
4. A pair is refused if a song is missing in one recording, has no usable
   beats, or the beat counts differ by more than 3.
5. Results per pair: summed cost, cost per beat (sum divided by
   Σ max(n, m)), and Kendall's τ-b along the same path, averaged over songs
   and parameters.

### Private key

Expected next to `github_auth.py` or at `GITHUB_PRIVATE_KEY_PATH`. Excluded
by `.gitignore` and `.dockerignore`; under Docker it is mounted as a secret.

Note: This documentation was generated with the help of Generative AI.

---

## Deutsch

```
backend/
├── main.py              Anwendungsinstanz, CORS, Router, /health
├── config.py            Repositorium, MEI-Namensräume, Liedtitel
├── github_auth.py       Authentifizierung als GitHub App
├── requirements.txt     festgelegte Abhängigkeiten
├── Dockerfile
├── routers/             Endpunkte (HTTP-Schicht)
├── services/            Datenzugriff und Berechnungen
└── static/              Favicon
```

### `routers/`

| Datei | Endpunkte |
|---|---|
| `files.py` | `/db/file`, `/db/file-measures`, `/db/parsed-file`, `/db/parsed-measures`: MEI als Text oder geparste Zeilen, wahlweise auf einen Taktbereich beschnitten |
| `scores.py` | `/db/scores-folder`: das Partiturverzeichnis als sortierter Baum |
| `performances.py` | `/db/performances` (Aufnahmen mit Jahr, Pianist, Ort, Kontext), `/db/performance-files` (Lieder je Aufnahme), `/db/performances-detailed` (Metadaten für Zeitleiste und Karte) |
| `analysis.py` | `/db/analysis` (Distanz- und τ-Matrix), `/db/analysis/stream` (dasselbe als Server-Sent Events mit Fortschritt), `/db/analysis/pair` (Detailansicht eines Paares) |
| `stats.py` | `/db/stats/corpus`, `/db/stats/performances`, `/db/stats/report`, `/db/stats/normalization-reference`, `/db/stats/refresh` (leert die Zwischenspeicher) |

### `services/`

| Datei | Zweck |
|---|---|
| `githubClient.py` | Alle Anfragen an die GitHub-API: Dateiinhalte, Verzeichnislisten, Dateibaum; hält Dateien zehn Minuten im Zwischenspeicher. |
| `pathSafety.py` | Prüft, dass Pfade vom Client in den zulässigen Verzeichnissen bleiben. |
| `meiParser.py` | Überführt Performance-MEI-Dateien in schlagweise Zeilen, liest den Kalibrierungsblock, beschneidet Partituren auf einen Taktbereich. |
| `statsCalc.py` | Liest die vorberechneten Statistiken aus dem Datenbank-Repositorium (fünf Minuten zwischengespeichert) und liefert Zentren, Skalen und Kovarianz für Geltungsbereich und Methode. |
| `dtwCalc.py` | Normalisierung, DTW-Distanzen, Kendalls τ entlang des Ausrichtungspfads, τ-Untergrenze, größte Unterschiede je Paar. |

### Analyse

1. Für jede ausgewählte Aufnahme werden die Schläge aller Lieder im
   Geltungsbereich geladen; ein Schlag zählt nur, wenn jeder ausgewählte
   Parameter einen Wert hat.
2. Jede Messreihe wird normalisiert: `(Wert − Zentrum) / Skala`, Tempo und
   Klangfarbe logarithmiert. Standard: Mittelwert/Standardabweichung; alternativ
   Median/MAD (`normalization=median`). Zentren für Dynamik und Klangfarbe je
   Aufnahme, für Tempo korpusweit; Skalen korpusweit, je nach Geltungsbereich
   pro Lied oder für den Zyklus.
3. Jedes Lied wird einzeln mit DTW ausgerichtet (`dtw-python`, Schrittmuster
   `symmetric1`, Sakoe-Chiba-Band `|n − m| + 2`); lokale Kosten euklidisch
   (wahlweise gewichtet) oder Mahalanobis (Korpus-Kovarianz) über `scipy`.
4. Ein Paar wird abgelehnt, wenn ein Lied in einer Aufnahme fehlt, keine
   verwertbaren Schläge hat oder die Schlagzahlen um mehr als 3 abweichen.
5. Ergebnisse je Paar: summierte Kosten, Kosten pro Schlag (Summe geteilt durch
   Σ max(n, m)) und Kendalls τ-b entlang desselben Pfads, gemittelt über
   Lieder und Parameter.

### Privater Schlüssel

Wird neben `github_auth.py` oder unter `GITHUB_PRIVATE_KEY_PATH` erwartet.
Über `.gitignore` und `.dockerignore` ausgeschlossen; unter Docker als Secret
eingehängt.

Anmerkung: Diese Dokumentation wurde mithilfe von generativer KI erstellt.

