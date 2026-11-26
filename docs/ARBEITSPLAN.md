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

## Etappe 2 – Neues Design (Apple-Look) – abgeschlossen
**Abgeschlossen am 26.11.2026:** `main` per Fast-Forward auf `c254cc8` (von `5e59592`, 44 Commits), gepusht; GitHub Pages liefert den neuen Stand aus. Details unten in der Checkliste.

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

Spieldaten:
- **Fenster „Spiel bearbeiten“**: öffnet sich beim Tippen auf den Spieltitel oder über „Spiel bearbeiten“ in der Werkzeugleiste. Bei einem neuen Spiel öffnet es sich automatisch.
  - Reihenfolge: **Spielnummer** (ganz oben, Zifferntastatur, vom Matchblatt) · Stufe · Gegner · Datum & Zeit · Halle · System (1/2/3/4-Mann als Knopfreihe) · Schiedsrichter je Rolle mit Durchgang (– / R1 / R2) · Supervisor.
  - Spielnummer ist **kein Pflichtfeld**: fehlt sie, steht in „Bereit zum Sichern?“ ein oranger Hinweis „Spielnummer fehlt“, Sichern bleibt möglich. Sie wird als `spiel_id` exportiert.
  - Felder, die der Supervisor von Hand geändert hat, bekommen eine kleine blaue Markierung („von dir geändert“). Hinweiszeile oben: „Übernommen aus Einteilung vom …“, sobald Etappe 4 da ist.
- Die Spieldaten verschwinden damit aus dem grossen grauen Bereich oben; auf der Bewertungsseite steht nur noch der Titel (Stufe · Datum, Zeit · Halle · System + Begegnung).
- Entwurf: Ansicht „Spiel bearbeiten“ im Design-Entwurf.

Stil:
- Schrift `-apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Helvetica Neue', sans-serif`.
- Hell: Grund `#F2F2F7`, Karten `#FFFFFF`, Text `#1C1C1E`, Sekundär `#636366`, Linien `#D8D8DE`, Segment-Grund `#E6E6EB`.
- Dunkel: Grund `#000000`, Karten `#1C1C1E`, Text `#F5F5F7`, Sekundär `#A1A1A6`, Linien `#38383A`, Akzent `#4C9AFF`.
- Akzent `#0A58CA`; Bewertung ++ `#13662B`, + `#2E7D3A`, – `#B45309`, –– `#B42318`, N/A `#636366`.
- Radius Karten 12 px, Knöpfe 7–10 px; Abschnittstitel klein, grau, in Grossbuchstaben.
- Schlichte Linien-Icons (inline SVG), keine Emojis. Kontrast mind. 4.5:1.
- Dark Mode automatisch über `prefers-color-scheme`, Umschalter bleibt (Auto / Hell / Dunkel).

Sprachen und Verein (seit 2.1b):
- Sprachwahl als Liste: DE und EN sichtbar, FR und IT vorbereitet, aber versteckt (nur über `?lang=fr` / `?lang=it` zum Testen). Fehlt ein Text, wird der deutsche angezeigt. Die Wahl bleibt nach dem Neuladen. Ab 2.4 im Menü „Mehr“.
- Jeder neue Text über `t()`, auf DE und EN. Bestehende rein deutsche Texte im HTML werden im jeweiligen Teilschritt umgestellt; Ende 2.9 läuft jeder Text über `t()`.
- **2.9:** FR und IT übersetzen, wenn die Texte fertig sind; sie bleiben versteckt (Freigabe in Etappe 9). Ab dann `texte-test.py --streng`.
- **2.9:** `manifest.json`-Farben (`theme_color`, `background_color`) an das neue Design anpassen, hell und dunkel.
- Gespeicherte Werte (Coaching-Texte, R1/R2, Liga, Rollen, Partner) bleiben in jeder Sprache deutsch, damit Dateien austauschbar sind. Die CSV ist ein Bericht: Spaltentitel in der gewählten Sprache.
- Verein zentral in `js/club.js` (Name, Kürzel, Logo, Beispiel-Halle, Wert für `club` im Export), ohne Knopf in der App. Kein „EVZ“ / „EV Zug“ fest im Code.

Tests nach jedem Teilschritt: `python3 tests/tools/alle-tests.py` (Daten DE/EN, Texte, Verein, Service Worker), bei sichtbaren Änderungen zusätzlich `bilder.py --gegen` (Referenz: Tag `stand-etappe-1`).

**Fertig, wenn:** Alle Funktionen von vorher gehen; auf iPad hoch/quer und MacBook gut bedienbar; Dark Mode sauber; Drucken nicht schlechter als vorher; alle Texte über `t()` auf DE und EN.

### Stand (seit 26.11.2026 auf `main`, `c254cc8`)
Fertig und getestet (`alle-tests.py` grün, Bilder gegen den alten Stand angesehen):

| Teilschritt | Commit |
|---|---|
| Testwerkzeuge unter `tests/tools/` | `96a2d2d`, `ec4c792` |
| 2.1 Fundament: Farben, Schrift, Dark Mode nach System | `bc3a7d9` |
| 2.1b Sprachwahl DE/EN, FR/IT vorbereitet | `bcdc64e` |
| Verein zentral (`js/club.js`) | `4fe619b` |
| 2.2 Eigene Fenster und Hinweise | `90b0227` |
| 2.3 Knopfreihen | `35a4485` |
| 2.4a Gerüst: Seitenleiste, Werkzeugleiste, Menü „Mehr“ | `0cf7fb9` |
| 2.4b Zwei Spalten: Score-Karte, Netzdiagramm, „Bereit zum Sichern?“ | `6bb0178` |
| 2.5 iPad hochkant: Schublade, kompakte Score-Leiste | `4763a29` |
| 2.6 Fenster „Spiel bearbeiten“ | `bfb6c47` |
| Auswahltext „Name wählen …“ | `1cf66d5` |
| 2.7 Szene-Fenster mit Chips | `544aa3d` |
| 2.7 Korrektur: alte Zeitangaben bleiben beim Ändern erhalten (tolerantes Lesen, Angabe bleibt ohne Wahl von Drittel/Zeit) | `d44da1c` |
| 2.8 Gespann-Übersicht und Saison-Statistik im neuen Stil (Zahlen gleich wie `main`) | `ec41896` |
| 2.9a Druck und Inhalt: Textfelder vollständig im Druck (leere weg), Supervisor in der Titelzeile, Statistik mit Saison, Druckdatum und Fusszeile „Vertraulich“ | `ad6c75b` |
| Tests: Schlussmeldung immer sichtbar, Supervisor-Wechsel im Druck-Test, Bewegung reduzieren als Standard | `2037709` |
| 2.9b Feinschliff (1): alle Texte über `t()`, keine Inline-Styles/-Handler, Kunstsprache-Test, Pixelvergleich | `2c8f9de` |
| 2.9b (2): FR und IT übersetzt (versteckt, nur `?lang=`), Texte-Test streng | `e18357a` |
| 2.9b (3): Karten als benannte Bereiche (VoiceOver), Manifest-Farben | `7b42687` |
| 2.9b (4): Übergänge (Einblenden 150 ms, Score zählt beim Reiterwechsel 400 ms, Bewegung reduzieren, Druck fertig) | `b6c0300` |
| 2.9b (5): CSS-Reste entfernt (Bilder pixelgleich), Test-Anleitung | `df74ba4` |
| Französischer Reiter „Équipe“ | `e789c53` |
| Wechsel-Test: `main` → neuer Stand ohne Datenverlust, Rückweg, ohne Erhöhung blockiert | `a02c701` |
| Korrektur nach Test auf dem Mac: rechte Spalte scrollt bis zum unteren Ende mit; Dateiauswahl in Safari (Dateiwahl-Test) | `dea17a9` |
| Neue Spiele mit 2-Mann (`standardSystem` in `js/club.js`); gespeicherte Spiele behalten ihr System, ohne Angabe 4-Mann (System-Test) | `a03ae27` |
| Tag `stand-etappe-1` auf `5e59592` (gepusht); alle Vergleichstests gegen den Tag statt gegen `main`; Gegenproben nur noch in temporären Kopien (`gegenprobe.py`); Notfall-Ablauf geprobt | `6d2c67b` |
| Neue Spiele ohne Liga („Liga wählen …“, Hinweis „Liga fehlt“ mit Sprung zur Liga); ältere Daten ohne Angabe zeigen „National League“ (Datenregel `LIGA_OHNE_ANGABE` in `js/config.js`); Liga-Test, Gegenprobe `liga-startwert` | `fca21f5` |
| Liga: Hinweis auch im Fenster „Spiel bearbeiten“, „Liga wählen …“ gesperrt (nicht wieder wählbar); Gegenproben `liga-sperre`, `liga-fenster-hinweis`; ganzer Gegenproben-Katalog 12/12, Bilder gegen den Tag angesehen, gegen den Stand davor pixelgleich (ausser Nummer `?v=`) | `8779149` |
| Liga: Hinweis direkt unter dem Feld (Karte „Spiel“), „Liga wählen …“ grau ohne Wahl; Gegenproben `liga-grau`, `liga-hinweis-unter-karte` | `d1467b5` |
| Platzhalter überall in `--secondary` (bisher Browser-Standard, dunkel nur 4.09:1), hell mind. 5.6:1, dunkel mind. 6.61:1; Kontrastprüfung im Bereiche-Test, Gegenprobe `platzhalter-kontrast`; ganzer Katalog 15/15 | `670f2d7` |

Doku dazwischen: `b0355ac`, `32e57fc`, `651499c`, `caa3cbd`, `59bb44a`, `3407e00`, `ab11ea5`. Der Branch wird nach jedem Teilschritt auf GitHub gepusht (Sicherung).

**Erledigt:** Test auf dem iPad bestanden (26.11.2026), Wechsel auf `main` am 26.11.2026 (`c254cc8`), Prüfung danach bestanden. Etappe 2 ist abgeschlossen; als Nächstes Etappe 3 – nur nach Livios Go.

**2.9b Feinschliff (erledigt):**
- `manifest.json`-Farben (`theme_color`, `background_color`) ans neue Design anpassen, hell und dunkel.
- VoiceOver: jede Karte ein benannter Bereich, auch wo die rechte Spalte hochkant per `display: contents` aufgelöst wird; Test über den Bedienungshilfen-Baum.
- Restliche rein deutsche Texte auf `t()`, geprüft mit einer Kunstsprache ⟦…⟧ (nur im Test, nie in der Sprachwahl, nie gespeichert); restliche Inline-Styles und -Handler entfernen.
- FR und IT übersetzen; bleiben versteckt, nur über `?lang=fr` / `?lang=it`, ohne Speichern; `texte-test.py --streng` in `alle-tests.py`.
- CSS-Reste: eine Regel nur entfernen, wenn ihre Klasse weder im HTML noch in einer JS-Datei vorkommt (viele Klassen entstehen erst im JavaScript); Bilder vor/nach dem Aufräumen pixelgleich.
- Übergänge: Reiterwechsel weich (150 ms), Score zählt nur beim Reiterwechsel hoch (400 ms), `prefers-reduced-motion` respektieren. Der Druck zeigt immer den fertigen Score, auch mitten im Hochzählen.
- Alle Tests laufen mit `prefers-reduced-motion`; nur der Animations-Test schaltet die Übergänge ein.

**Wechsel auf `main` (Checkliste):**
1. ~~Wechsel-Test als eigener Commit~~ (erledigt, `a02c701`, läuft in `alle-tests.py`).
2. ~~**Vor dem Merge: Test auf dem iPad über den lokalen Server** (Mac und iPad im selben WLAN, `python3 -m http.server`, Adresse des Macs im Safari): Bedienung und Layout hoch und quer, Szene mit Zifferntastatur, „Spiel bearbeiten“, Druck über „Teilen“. Probleme sollen vor dem Merge auffallen.~~
   ~~**Dateiknöpfe:** alle drei („Kader importieren“ im Menü „Mehr“, „Kader importieren“ beim Schiedsrichter-Feld – erscheint nur ohne Kader –, „Dateien wählen“ in der Statistik) mit Dateien aus der App **Dateien** testen (erfundene Beispieldateien aus `tests/fixtures/`, z. B. per AirDrop aufs iPad).~~
   (erledigt am 26.11.2026 mit Stand `1669d38`: hoch und quer, hell und dunkel, neues Spiel mit 2-Mann und „Liga wählen …“, Platzhalter, Szene mit Zifferntastatur, die drei Dateiknöpfe mit der App „Dateien“, Sichern und CSV, Druck über „Teilen“ – keine Auffälligkeiten)
3. ~~**VoiceOver kurz auf dem iPad:** Reiter, eine Knopfreihe, Score-Leiste, Karten.~~ (erledigt am 26.11.2026, keine Auffälligkeiten)
4. ~~**Handtest Bewertung über Nacht:** Am Vorabend in der App eine Bewertung offen lassen (nicht exportieren), nach dem Merge öffnen und prüfen, dass alles da ist. Wichtig: Auf dem iPad haben die Home-Bildschirm-App und Safari **getrennte Speicher** – den Test in der App machen, die in der Halle wirklich benutzt wird.~~
   (ersetzt durch den Test auf dem MacBook direkt nach dem Merge, 26.11.2026: Stand 33, gespeicherte Bewertung unverändert da, Export vollständig, App startet offline. Bewertungen vorher auf dem MacBook gesichert.)
5. ~~Nur unter der Woche, nicht vor einem Einsatz in der Halle.~~ (Donnerstag, 26.11.2026)
6. ~~Alten Stand markieren: Tag `stand-etappe-1` auf `5e59592`, Tag pushen.~~ (erledigt; alle Vergleichstests nutzen den Tag)
7. ~~`main` per Fast-Forward auf `etappe-2` – nur nach Livios Go – und pushen.~~ (erledigt am 26.11.2026 nach Livios Go: `5e59592..c254cc8`; vorher geprüft: `etappe-2` sauber und gleich wie `origin/etappe-2`, `main` und Tag auf `5e59592`, `alle-tests.py` 20/20)
8. ~~Danach `alle-tests.py` komplett und `bilder.py --gegen`, auf GitHub Pages prüfen (Update-Badge, offline).~~ (erledigt am 26.11.2026: `alle-tests.py` 20/20; GitHub Pages nach ca. 20 s mit `?v=33`, `index.html` und `sw.js` bytegleich mit `main`, alle 25 eingebundenen bzw. offline gespeicherten Dateien und das Vereinslogo erreichbar; auf dem MacBook Stand 33 und offline geprüft, siehe Punkt 4. `bilder.py --gegen` nach dem Merge nicht nochmals: Code identisch mit dem vorher geprüften Stand.)
9. Zurück, falls nötig: **Notfall-Ablauf** (unten) – seit Etappe 3 mit Ziel `stand-etappe-2`; nur auf Livios ausdrückliches Wort.

**Notfall-Ablauf: zurück auf den alten Stand** – Ziel ist der zuletzt ausgelieferte Stand, seit 26.11.2026 der Tag `stand-etappe-2` (`f5c1070`). Nur nach dem Fast-Forward-Merge einer neuen Etappe; `main` muss linear auf `stand-etappe-2` aufbauen. Nur auf Livios ausdrückliches Wort.

```sh
git switch main && git pull --ff-only
ALT=$(grep -oE '\?v=[0-9]+' index.html | head -1 | cut -d= -f2); NEU=$((ALT + 1)); echo "?v=$ALT -> ?v=$NEU"
git revert --no-commit stand-etappe-2..HEAD      # alter Stand wiederhergestellt, Verlauf bleibt erhalten
sed -i '' -E "s/\?v=[0-9]+\"/?v=$NEU\"/g" index.html   # Nummer über den aktuellen Wert (nie zurück auf ?v=33)
git add index.html
git diff --cached --stat stand-etappe-2          # Kontrolle: nur index.html (?v=) weicht vom alten Stand ab
git commit -m "Notfall: zurück auf stand-etappe-2 (?v=$NEU)"   # Hook prüft die Nummer
git push origin main
```

- Der Revert stellt den Code des alten Stands wieder her (neue Dateien der neuen Etappe fallen weg), ohne Verlauf zu löschen oder etwas zu überschreiben; kein `reset`, kein Force-Push.
- Die Nummer muss höher sein als die aktuelle, sonst lehnt der Hook ab und der Service Worker würde die alte Version nicht laden.
- Die gespeicherten Bewertungen bleiben: Der Wechsel-Test prüft den Rückweg (alte Oberfläche liest die Daten der neuen, auch „Auto“ und „fr“) – mit genau diesem Stand: `wechsel-test.py --von stand-etappe-2 --rueck ORDNER`. Wichtig für Etappe 3: Ein neues Datenmodell muss für diesen Rückweg lesbar bleiben (siehe Etappe 3).
- **Mit Ziel `stand-etappe-2` noch nicht geprobt** – vor dem Merge von Etappe 3 in einer Wegwerf-Kopie proben (wie am 15.11.2026).
- **Geprobt am 15.11.2026 (Ziel damals `stand-etappe-1`)** in einer Wegwerf-Kopie (lokales Repo als „GitHub“, Merge simuliert): `?v=29 → 30`, Hook lehnt mit `?v=7` ab und akzeptiert `?v=30`, Push geht, Ergebnis weicht vom Tag nur in `?v=` ab und ist dateigleich mit dem Rückweg des Wechsel-Tests; Wechsel-Test mit diesem Ergebnis als Rückweg: 0 Fehler.
- Später wieder vorwärts: `git revert` des Notfall-Commits und `?v=` nochmals erhöhen.

**Hinweis Datensicherung:** Safari kann gespeicherte Daten einer Website löschen, wenn sie etwa 7 Tage nicht geöffnet wurde. Das Export-JSON bleibt die eigentliche Sicherung – jede Bewertung nach dem Spiel sichern.

**Offener Entscheid:** Kriterien ohne Vorbelegung starten (siehe „Offene Entscheide“) – Livio entscheidet nach der Rückmeldung seines Vorgesetzten.

---

## Etappe 3 – Spielliste und Bewertungen wieder öffnen
- Mehrere Spiele gleichzeitig speichern (statt nur eines). Neues Spiel anlegen, Spiel duplizieren, Spiel archivieren.
- Bestehende JSON-Dateien (Version 1.0 und 1.1) wieder ins Formular laden und korrigieren.
- Datenmodell in `localStorage` mit Versionsnummer; bestehende Daten beim ersten Start automatisch übernehmen.
- „Zurücksetzen“ betrifft nur noch das aktuelle Spiel und fragt mit eigenem Fenster nach.

**Fertig, wenn:** Zwei Spiele parallel bearbeitbar; alte Exportdateien öffnen sich korrekt; nach dem Update ist das laufende Spiel noch da.

---

## Etappe 4 – Einteilung importieren und Änderungen abgleichen
**Ziel:** Spiele, Zeiten, Hallen und eingeteilte Schiedsrichter nicht mehr von Hand eintippen. Bei jeder neuen Einteilung zeigt die App, was sich geändert hat und was das für die Supervisionsplanung bedeutet.

### Quelle
- **Jetzt:** Livios Excel-Einteilung (`.xlsx`), z. B. `Einsatzplan_Supervision_Stand_06-11-2026.xlsx`.
  - Zeile 1 Titel, Zeile 2 Untertitel, **Zeile 3 Kopfzeile**. Spalten **über den Namen in der Kopfzeile** finden, nicht über die Position (ältere Dateien haben weniger Spalten, z. B. ohne „Status“ und „Bemerkung“).
  - Spalten: `Date` (TT.MM.JJJJ) · `Time` (HH:MM) · `Home Team` = **Stufe** (z. B. „U14 Elit“, „JWLU16“, „U9 I“) · `Away Team` = **Gegner** · `Arena` · `Ref 1` · `Ref 2` · optional `Supervision für` · `Status` (Erledigt / Verpasst / Geplant) · `Bemerkung`.
  - `Supervision für` hat das Format „Meier L. (R1), Keller N. (R2)“ oder „L. Meier (R1)“; auch „J. Brunner (1/1)“ aus älteren Dateien kommt vor → Rundenangabe tolerant lesen, unklare Werte nachfragen.
  - EVZ ist immer stillschweigend das Heimteam.
  - Zellen können Text oder Zahl sein (Datum als Excel-Seriennummer) → beides lesen.
- **Später:** CSV vom Schiedsrichterobmann (angefragt). Der Import soll darum aus **austauschbaren Lesern** bestehen (xlsx, csv, evtl. später pdf), die alle dasselbe interne Format liefern.
- **PDF-Export** („GAME SCHEDULE“, Spalten Date · Time · Home Team · Away Team · Arena · Type · Status · Ref 1–4): nur falls nötig und nach Rückfrage – bräuchte pdf.js lokal mitgeliefert. Besonderheiten: „Missing“ = unbesetzte Stelle, lange Gegnernamen über zwei Zeilen umbrochen.

### Technik
- `.xlsx` **ohne Fremdbibliothek** lesen: ZIP mit `DecompressionStream('deflate-raw')` entpacken, `xl/worksheets/sheet1.xml` (+ `sharedStrings.xml`, falls vorhanden; Livios Dateien nutzen Inline-Strings `<is><t>`) per `DOMParser` auslesen. Auf iPad (Safari ab 16.4) testen.
- Namen aus der Einteilung („L. Meier“, „Meier L.“) dem Kader zuordnen: Nachname + Anfangsbuchstabe des Vornamens. Es gibt Namensgleichheiten (gleicher Nachname, anderer Vorname, z. B. Frei L. / Frei M.; im echten Kader mehrere solche Paare) → nur bei eindeutigem Treffer automatisch, sonst nachfragen und die Antwort merken.
- Einteilung wie der Kader **nur lokal** speichern. Nie ins Repo.

### Spiel wiedererkennen (ohne Spielnummer)
Jedes Spiel bekommt beim ersten Import eine interne ID. Beim nächsten Import, in dieser Reihenfolge:
1. Datum + Zeit + Stufe + Gegner gleich → gleiches Spiel.
2. Datum + Stufe + Gegner gleich, Zeit anders → gleiches Spiel, Hinweis „Zeit geändert“.
3. Stufe + Gegner gleich, Datum anders, altes Spiel fehlt → **Rückfrage „verschoben?“**; Antwort merken.
4. Sonst: neues Spiel; ein nicht mehr vorhandenes Spiel wird als „abgesagt?“ markiert, **nicht gelöscht**.
- Ist eine offizielle Spielnummer (vom Matchblatt) erfasst, ist sie das feste Merkmal.
- Gleiche Halle + Zeit kommt bei U9/U12 doppelt vor (I/II) → Stufe inkl. „I/II“ und Gegner gehören immer zum Schlüssel.

### Abgleich-Fenster „Einteilung aktualisiert“ (siehe Entwurf)
- Oben: **Betrifft deine Supervision** – Schiri-Wechsel, Verschiebungen oder Absagen bei Spielen, an denen eine Supervision geplant ist.
  - Bei Wegfall: **Ersatzvorschläge** – andere Spiele, an denen dieser Schiri eingeteilt ist, mit gleichem Durchgang (R1/R2), noch in der Zukunft.
  - Ersatzvorschläge filtern nach Livios Regeln (einstellbar): keine U9/U12, ausgeschlossene Schiris, max. 2× pro Schiri.
- Darunter: **weitere Änderungen** (Zeit, Halle, neue Spiele, besetzte Stellen „offen → Name“).
- Nichts wird übernommen, bevor Livio „Übernehmen“ tippt. Offene Rückfragen müssen beantwortet sein.
- **Nie verändert:** begonnene/gesicherte Bewertungen und Felder, die Livio von Hand geändert hat (ausser er bestätigt es).

### Supervisionsplan in der App
- Spiele mit geplanter Supervision erscheinen in der Seitenleiste unter „Geplant“, mit R1/R2 je Schiri vorbelegt. Beim Öffnen sind Begegnung, Stufe, Datum, Zeit, Halle, System und Schiris schon ausgefüllt.
- Übersicht pro Schiri: wie oft gesehen, wie oft noch geplant, ob noch möglich.

### Tests
- Beispieldateien mit **erfundenen Namen** unter `tests/fixtures/`: `beispiel-einteilung-alt.xlsx`, `beispiel-einteilung-neu.xlsx` (mit Zeitänderung, Schiri-Wechsel bei geplanter Supervision, Verschiebung, neuem Spiel, besetzter offener Stelle) und eine ältere Variante ohne „Status“/„Bemerkung“. Erwartete Ergebnisse im Fixture-README.
- Mehrfach importieren ohne Änderung → „keine Änderungen“.

**Fertig, wenn:** Livios Excel-Einteilung sich importieren lässt; ein zweiter Stand alle Änderungen korrekt anzeigt; Bewertungen und eigene Korrekturen unangetastet bleiben; auf iPad und MacBook getestet.

---

## Etappe 5 – R1 → R2
- Beim Erfassen von R2 die R1-Datei des gleichen Schiris laden (über „Bewertung öffnen“ oder die importierten Saisondateien).
- R1-Entwicklungsschwerpunkte erscheinen als Checkliste („umgesetzt / teilweise / nicht umgesetzt“) mit Notiz.
- Vergleich R1 ↔ R2 pro Kriterium (Pfeile ↑ ↓ →).

---

## Etappe 6 – Neue Felder
- **Sicherheit & Ausrüstung:** Schalter „Auffälligkeit festgestellt“ + Textfeld; roter Rahmen; im Bericht und in der Statistik hervorgehoben.
- **Empfehlung (nur R2 oder Saisonende):** Aufstieg empfohlen / Stufe halten / gezielte Förderung.
- **Kurzbeschreibung pro Note und Kriterium:** Beim Antippen einer Note erscheint, was sie bei diesem Kriterium bedeutet (einheitlicher Massstab). Texte in einer eigenen Datei (`js/rubric.js`), damit Livio sie selbst anpassen kann.
- Exportformat auf Version 1.2 erweitern; 1.0/1.1 bleiben lesbar.

---

## Etappe 7 – Berichte
- **Einzelbericht A4** (Drucken / PDF): Kopf mit Logo und Spieldaten, Score, Netzdiagramm, Kriterien mit Szenen, Stärken, Schwerpunkte, Sicherheit, Unterschriftsfeld. Eigenes Druck-CSS.
- **Saisonbericht für den EVZ** (Drucken / PDF): wer wie oft gesehen wurde, Durchschnitt R1/R2, Entwicklung, häufigste Schwerpunkte im Team, Sicherheitsvorfälle, Empfehlungen.
- Statistik-Ansicht: Kennzahlen oben, sortierbare Tabelle, Verlauf R1 → R2.

---

## Etappe 8 – Datenschutz in der App
- Info-Seite „Datenschutz“: was gespeichert wird, wo, wie lange.
- Einstellbare Aufbewahrungsfrist (z. B. Saisonende + 1 Jahr) mit Erinnerung, alte Spiele zu löschen.
- „Alle lokalen Daten löschen“ mit Bestätigung.

---

## Etappe 9 – Für andere Vereine (nicht umsetzen, nur vormerken)
- **Verein in der App einstellbar** (Name, Kürzel, Logo …). Die Grundlage aus Etappe 2 ist vorhanden (`js/club.js`, kein „EVZ“ fest im Code, Vereins-Test).
- **FR und IT freigeben.** Vorher die Fachbegriffe von Schiedsrichtern aus der Romandie bzw. dem Tessin prüfen lassen.
- **Eventuell eigene Kriterien, Notenstufen und Gewichtung** – erst nach Rückmeldung anderer Vereine bzw. des SIHF.
- **Lizenz** und **Datenschutz-Seite** für die Weitergabe.
- **Sichtbare Versionsnummer** und **Änderungsliste** in der App.
- **Einteilungs-Import** für eine Quelle, die alle Vereine haben (abklären, welche).
- **System passend zur Liga vorschlagen:** Unter „Spiel bearbeiten“ schlägt die App das System zur gewählten Liga vor – 4-Mann für National League und Swiss League, sonst 2-Mann. Die Zuordnung ist pro Verein einstellbar (wie `standardSystem` in `js/club.js`) und wird vor der Freigabe mit dem SIHF abgeglichen. Bei vorhandenen Bewertungen gilt die bestehende Rückfrage zum Systemwechsel.

---

## Offene Entscheide
- **Kriterien ohne Vorbelegung starten**, fehlende in „Bereit zum Sichern?“ anzeigen – ändert eine fachliche Regel (heute „+“ vorbelegt). **Livio entscheidet erst nach der Rückmeldung seines Vorgesetzten** (Stand 26.11.2026); bis dahin nichts umsetzen.

---

## Laufend
- Bei jeder Änderung an `css/` oder `js/` die Nummer `?v=` in `index.html` erhöhen (Hook prüft es).
- Nach jeder Änderung `python3 tests/tools/alle-tests.py` laufen lassen.
- Versionsnummer in der Fusszeile nachführen.
- README aktuell halten.
