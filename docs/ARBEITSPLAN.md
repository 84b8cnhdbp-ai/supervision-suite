# Arbeitsplan – Referee Supervision Suite 2.0

So benutzt du ihn mit Claude Code: Gib jeweils **eine Etappe** als Auftrag, z. B.
„Lies CLAUDE.md und docs/ARBEITSPLAN.md. Mach einen Vorschlag für Etappe 1, noch nicht umsetzen.“
Nach dem Vorschlag gibst du das Go. Erst wenn die Etappe getestet und committet ist, kommt die nächste.

---

## Etappe 1 – Code aufräumen (ohne sichtbare Änderung)
**Ziel:** Die 2000 Zeilen in `index.html` aufteilen, damit das neue Design sauber umsetzbar ist.
- CSS nach `css/app.css`, JavaScript nach `js/` (`i18n.js`, `config.js`, `scoring.js`, `storage.js`, `ui.js`, `export.js`, `stats.js`, `app.js`), als normale `<script>`-Dateien ohne Build. Code nur verschieben, nicht umschreiben; Inline-Handler (`onclick` …) bleiben.
- Alle neuen Dateien im Service Worker cachen; Versionsnummer `?v=` in den CSS-/JS-Links von `index.html` (Release-Regel neu, siehe CLAUDE.md), pre-commit-Hook prüft sie.
- Service Worker: Seite + CSS/JS als ein Paket mit `cache: 'no-cache'` laden; nur vollständig übernehmen (Zeitlimit 3 s, sonst gespeichertes Paket), nie gemischte Versionen; Hinweis im Badge, wenn ein Update wegen nicht erhöhter Nummer blockiert ist.
- Beispieldateien mit erfundenen Namen unter `tests/fixtures/` (Version 1.0 und 1.1, ganzes Spiel, Kader).

**Fertig, wenn:** Die App sieht exakt gleich aus und verhält sich gleich; alle Tests aus CLAUDE.md laufen; online ist eine neue Version sofort sichtbar; Offline-Start funktioniert vollständig.

---

## Etappe 2 – Neues Design (Apple-Look)
**Ziel:** Professionelle, ruhige Oberfläche für MacBook und iPad.

Aufbau:
- **MacBook / iPad quer:** Seitenleiste links (Spiele: Heute / Geplant / Erledigt; darunter Schiedsrichter, Saison-Statistik, Berichte; unten „Daten bleiben auf diesem Gerät“ + Version). Rechts oben eine Werkzeugleiste mit Reitern (Referee 1 · Name | Referee 2 · Name | Gespann) und den Aktionen Sichern, Drucken, Mehr. Inhalt zweispaltig: links Formular, rechts Score-Karte (Kreis-Score, Status, drei Teilwerte), Netzdiagramm und „Bereit zum Sichern?“-Checkliste.
- **iPad hochkant:** Seitenleiste eingeklappt („‹ Spiele“), kompakte Score-Leiste oben, die beim Scrollen stehen bleibt; Formular einspaltig.

Bedienelemente:
- Gesamteinschätzung, alle 7 Kriterien, Coaching (3 Felder) und Drittel als **Segmented Controls** (Knopfreihe). Gewählte Note farbig mit weisser Schrift.
- Gesamteinschätzung ohne Wahl: orange Rahmen + Hinweis „Bitte bewusst wählen …“.
- „Szene“-Knopf pro Kriterium öffnet ein eigenes Fenster (Drittel 1/2/3/OT, Spielzeit mm:ss, Notiz). Szenen erscheinen als Chips unter dem Kriterium (Format bleibt `[P2 08:34] Text` in den Notizen, damit alte Dateien passen).
- `alert`, `confirm`, `prompt` durch eigene Fenster und Hinweise (Toasts) ersetzen.
- Inline-Styles (im HTML und in den HTML-Vorlagen im JS) durch Klassen ersetzen; Inline-Handler (`onclick` …) durch `addEventListener` ersetzen.
- Weiche Übergänge beim Reiterwechsel, Score zählt animiert; `prefers-reduced-motion` respektieren.

Stil:
- Schrift `-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif`.
- Hell: Grund `#F2F2F7`, Karten `#FFFFFF`, Text `#1C1C1E`, Sekundär `#636366`, Linien `#D8D8DE`, Segment-Grund `#E6E6EB`.
- Dunkel: Grund `#000000`, Karten `#1C1C1E`, Text `#F5F5F7`, Sekundär `#A1A1A6`, Linien `#38383A`, Akzent `#4C9AFF`.
- Akzent `#0A58CA`; Bewertung ++ `#13662B`, + `#2E7D3A`, – `#B45309`, –– `#B42318`, N/A `#636366`.
- Radius Karten 12 px, Knöpfe 7–10 px; Abschnittstitel klein, grau, in Grossbuchstaben.
- Schlichte Linien-Icons (inline SVG), keine Emojis. Kontrast mind. 4.5:1.
- Dark Mode automatisch über `prefers-color-scheme`, Umschalter bleibt (Auto / Hell / Dunkel).

**Fertig, wenn:** Alle Funktionen von vorher gehen; auf iPad hoch/quer und MacBook gut bedienbar; Dark Mode sauber; Drucken nicht schlechter als vorher.

---

## Etappe 3 – Spielliste und Bewertungen wieder öffnen
- Mehrere Spiele gleichzeitig speichern (statt nur eines). Neues Spiel anlegen, Spiel duplizieren, Spiel archivieren.
- Bestehende JSON-Dateien (Version 1.0 und 1.1) wieder ins Formular laden und korrigieren.
- Datenmodell in `localStorage` mit Versionsnummer; bestehende Daten beim ersten Start automatisch übernehmen.
- „Zurücksetzen“ betrifft nur noch das aktuelle Spiel und fragt mit eigenem Fenster nach.

**Fertig, wenn:** Zwei Spiele parallel bearbeitbar; alte Exportdateien öffnen sich korrekt; nach dem Update ist das laufende Spiel noch da.

---

## Etappe 4 – R1 → R2
- Beim Erfassen von R2 die R1-Datei des gleichen Schiris laden (über „Bewertung öffnen“ oder die importierten Saisondateien).
- R1-Entwicklungsschwerpunkte erscheinen als Checkliste („umgesetzt / teilweise / nicht umgesetzt“) mit Notiz.
- Vergleich R1 ↔ R2 pro Kriterium (Pfeile ↑ ↓ →).

---

## Etappe 5 – Neue Felder
- **Sicherheit & Ausrüstung:** Schalter „Auffälligkeit festgestellt“ + Textfeld; roter Rahmen; im Bericht und in der Statistik hervorgehoben.
- **Empfehlung (nur R2 oder Saisonende):** Aufstieg empfohlen / Stufe halten / gezielte Förderung.
- **Kurzbeschreibung pro Note und Kriterium:** Beim Antippen einer Note erscheint, was sie bei diesem Kriterium bedeutet (einheitlicher Massstab). Texte in einer eigenen Datei (`js/rubric.js`), damit Livio sie selbst anpassen kann.
- Exportformat auf Version 1.2 erweitern; 1.0/1.1 bleiben lesbar.

---

## Etappe 6 – Berichte
- **Einzelbericht A4** (Drucken / PDF): Kopf mit Logo und Spieldaten, Score, Netzdiagramm, Kriterien mit Szenen, Stärken, Schwerpunkte, Sicherheit, Unterschriftsfeld. Eigenes Druck-CSS.
- **Saisonbericht für den EVZ** (Drucken / PDF): wer wie oft gesehen wurde, Durchschnitt R1/R2, Entwicklung, häufigste Schwerpunkte im Team, Sicherheitsvorfälle, Empfehlungen.
- Statistik-Ansicht: Kennzahlen oben, sortierbare Tabelle, Verlauf R1 → R2.

---

## Etappe 7 – Datenschutz in der App
- Info-Seite „Datenschutz“: was gespeichert wird, wo, wie lange.
- Einstellbare Aufbewahrungsfrist (z. B. Saisonende + 1 Jahr) mit Erinnerung, alte Spiele zu löschen.
- „Alle lokalen Daten löschen“ mit Bestätigung.

---

## Laufend
- Bei jeder Änderung an `css/` oder `js/` die Nummer `?v=` in `index.html` erhöhen (Hook prüft es).
- Versionsnummer in der Fusszeile nachführen.
- README aktuell halten.
