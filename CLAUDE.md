# CLAUDE.md – Referee Supervision Suite

## Worum es geht
Offline-fähige Web-App (PWA) für die Supervision der EVZ-Nachwuchs-Schiedsrichter (U14–U16, JWL U16).
Der Supervisor bewertet pro Spiel jeden Schiedsrichter, exportiert die Bewertung als JSON-Datei und wertet am Saisonende R1 (Hinrunde) und R2 (Rückrunde) aus.
Gehostet auf GitHub Pages: https://84b8cnhdbp-ai.github.io/supervision-suite/
Genutzt auf MacBook und iPad (hoch und quer), selten auf dem Handy.

## Arbeitsweise mit Livio
- **Zuerst Fragen beantworten und Vorschläge machen. Erst nach Livios ausdrücklichem „Go“ Code ändern.**
- Pro Etappe aus `docs/ARBEITSPLAN.md` arbeiten, kleine Commits mit klarer Nachricht.
- Vor jedem Commit zeigen, was geändert wurde, und kurz sagen, wie man es testet.
- Nicht pushen, ausser Livio sagt es.
- Sprache in Code-Kommentaren, Texten der App und Antworten: Schweizer Hochdeutsch (kein ß, „ss“ verwenden).

## Datenschutz – nicht verhandelbar
- **Keine Personendaten im Repo.** Keine Namen von Schiedsrichtern, keine Bewertungen, keine Adressen, auch nicht in Tests, Beispielen oder Kommentaren. Für Beispiele erfundene Namen verwenden (z. B. „Meier Luca“).
- Der Kader wird über „Kader importieren“ geladen und nur im `localStorage` gespeichert (Schlüssel `referee_kader`).
- Bewertungen bleiben lokal (`localStorage` + exportierte Dateien). Keine Server, keine Analytics, keine externen Requests.
- `.gitignore` nicht aufweichen.

## Technik
- Reines HTML/CSS/JavaScript, **kein Build-Schritt, keine Frameworks, keine CDNs** (muss offline laufen).
- Dateien: `index.html`, `css/app.css`, `js/*.js`, `sw.js` (Service Worker), `manifest.json`, `icons/`, `logo-evz.svg`.
- Neue CSS-/JS-Dateien in `index.html` mit `?v=N` einbinden (gleiche Nummer wie die übrigen Links). Der Service Worker speichert automatisch alles, was `index.html` einbindet.
- Andere neue Dateien, die offline verfügbar sein müssen (Bilder, Icons), in `STATIC_ASSETS` in `sw.js` eintragen.
- Service Worker: `index.html` + ihre CSS/JS sind ein Paket. Ein neues Paket wird nur vollständig übernommen (Zeitlimit 3 s, sonst gespeichertes Paket); nie gemischte Versionen.

## Release-Regel
- Bei **jeder** Änderung an `css/` oder `js/` die Nummer `?v=` in `index.html` erhöhen, bei **allen** Links gleich (`?v=7` → `?v=8`). Sonst blockiert der Service Worker das Update (Hinweis im Badge oben: „Update blockiert – Version nicht erhöht“).
- Der pre-commit-Hook in `.githooks/` prüft das (Aktivierung siehe README).
- Nur `index.html` geändert: keine Erhöhung nötig.
- `CACHE_NAME` in `sw.js` nur ändern, wenn sich der Aufbau des Caches in `sw.js` ändert. Änderungen an `sw.js` selbst lädt der Browser automatisch.

## Fachliche Regeln (nicht ohne Rückfrage ändern)
- Score = Gesamteinschätzung × 30 % + Leistungs-Checkliste × 50 % + Coaching × 20 %.
- Gesamteinschätzung: Sehr gut 100, Gut 80, Verbesserungsbedürftig 50, Ungenügend 20. **Kein Standardwert** – ohne Wahl kein Gesamtscore und kein Export.
- Checkliste: 7 Kriterien, je ++ 100 / + 80 / – 50 / –– 20 / N/A. N/A wird überall (Formular, Gespann, CSV, Statistik) aus dem Durchschnitt ausgeschlossen.
- Coaching: Werte in `COACH_SCORES`. Die Speicherwerte sind deutsche Texte (z. B. „Konstant stabil“) und müssen für alte Dateien gültig bleiben.
- Die ganze Berechnung läuft über **eine** Funktion (`computeRefScores`). Keine zweite Berechnung bauen.
- Rollen je System (1-, 2-, 3-, 4-Mann) in `SYSTEM_CONFIGS`; Linesperson hat eigene Kriterien-Texte.

## Datenformat Export (JSON)
- Dateiname: `JJJJ-MM-TT_R1_Nachname Vorname.json`.
- Aktuelle Version `"version": "1.1"`. **Dateien der Version 1.0 müssen weiterhin importierbar sein** (Saison-Statistik, später „Bewertung öffnen“).
- Export nur, wenn Name, Spieldatum und Gesamteinschätzung gesetzt sind.

## Testen
- Lokal mit VS Code „Live Server“ (Go Live) oder `python3 -m http.server`.
- Nach Änderungen prüfen: Kader-Import, Bewertung ausfüllen, Export JSON und CSV, Gespann-Übersicht, Saison-Statistik mit Beispieldateien, Drucken, Dark Mode, iPad-Breite (834 px) und quer (1194 px).
- Testdaten nur mit erfundenen Namen, nie echte Bewertungen ins Repo legen.

## Design (ab Etappe 2)
Apple-Look nach Livios Entwurf: Systemschrift (`-apple-system`), grauer Grund `#F2F2F7`, weisse Karten mit 12 px Radius, Knopfreihen (Segmented Controls) statt Dropdowns, Mindesthöhe 44 px für alles Antippbare, ein Akzent `#0A58CA`, Bewertungsfarben ++ `#13662B`, + `#2E7D3A`, – `#B45309`, –– `#B42318`, N/A `#636366`. Keine Emojis als Icons. Dark Mode folgt dem System. Details in `docs/ARBEITSPLAN.md`.
