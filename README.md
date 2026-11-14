# Referee Supervision Suite

Offline-fähige Web-App (PWA) für die Supervision von Eishockey-Schiedsrichtern: Bewertung pro Schiedsrichter, Gespann-Übersicht, JSON-/CSV-Export, PDF-Druck und Saison-Statistik.

## Voraussetzungen
- **iPadOS / iOS 16.4 oder neuer** (Safari), auf dem Mac ein aktueller Safari, Chrome oder Edge.
  Nötig für die eigenen Fenster (`<dialog>`), die Spaltenlogik (Container Queries) und ab Etappe 4 den
  Excel-Import (`DecompressionStream`). Auf älteren Geräten erscheint oben ein Hinweis; die App bleibt bedienbar.

## Datenschutz
Im Code stehen keine Namen und keine Bewertungen.
- **Kader:** Über „Mehr“ (⋯) → „Kader importieren“ eine JSON-Datei (`{"schiedsrichter": ["Nachname Vorname", …]}` oder `[…]`) oder eine TXT-Datei (ein Name pro Zeile) laden. Die Liste wird nur lokal im Browser gespeichert.
- **Bewertungen:** werden nur lokal gespeichert und als Datei exportiert (`JJJJ-MM-TT_R1_Nachname Vorname.json`).

## Release
1. Änderungen machen und lokal testen (`python3 -m http.server`).
2. Wenn `css/` oder `js/` geändert wurden: in `index.html` die Nummer `?v=` bei **allen** CSS-/JS-Links um 1 erhöhen (z. B. Suchen/Ersetzen `?v=7` → `?v=8`).
3. Commit und Push auf `main` → GitHub Pages veröffentlicht automatisch.

Die App lädt beim Start Seite, CSS und JS als ein Paket. Ist das Netz innert 3 Sekunden nicht fertig, startet sie mit der gespeicherten Version und übernimmt die neue beim nächsten Start. Wurde `?v=` vergessen, bleibt die bisherige Version aktiv und oben erscheint „⚠ Update blockiert – Version nicht erhöht“.

### Prüfung vor jedem Commit (einmalig aktivieren)
Im Projektordner einmal ausführen:

```sh
git config core.hooksPath .githooks
```

Danach lehnt `git commit` ab, wenn `css/` oder `js/` geändert wurden, `?v=` aber nicht erhöht wurde, oder wenn die Links verschiedene Nummern haben. Im Notfall überspringen: `git commit --no-verify`.

### Entwickeln mit Live Server
Der Service Worker liefert CSS/JS mit gleicher Nummer aus seinem Speicher. Damit lokale Änderungen ohne neue Nummer sofort sichtbar sind: in den Entwicklertools unter **Application → Service Workers** die Option **„Bypass for network“** einschalten.
