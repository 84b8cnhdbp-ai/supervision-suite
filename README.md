# Referee Supervision Suite

Offline-fähige Web-App (PWA) für die Supervision von Eishockey-Schiedsrichtern: Bewertung pro Schiedsrichter, Gespann-Übersicht, JSON-/CSV-Export, PDF-Druck und Saison-Statistik.

## Datenschutz
Im Code stehen keine Namen und keine Bewertungen.
- **Kader:** Über «📋 Kader importieren» eine JSON-Datei (`{"schiedsrichter": ["Nachname Vorname", …]}` oder `[…]`) oder eine TXT-Datei (ein Name pro Zeile) laden. Die Liste wird nur lokal im Browser gespeichert.
- **Bewertungen:** werden nur lokal gespeichert und als Datei exportiert (`JJJJ-MM-TT_R1_Nachname Vorname.json`).

## Release
1. Änderungen machen und lokal testen (`python3 -m http.server`).
2. In `sw.js` die `CACHE_NAME`-Version erhöhen.
3. Commit und Push auf `main` → GitHub Pages veröffentlicht automatisch.
