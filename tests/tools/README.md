# Testwerkzeuge

Brauchen nur **Python 3** und **Google Chrome** (kein Installieren von Paketen). Alle Tests laufen mit den
erfundenen Beispieldaten aus `tests/fixtures/`. Ergebnisse landen in `tests/tools/ergebnisse/`; dieser Ordner
steht in `.gitignore` und kommt **nie** ins Repo.

Alle Befehle im Projektordner ausführen.

## Alles auf einmal – nach jedem Teilschritt

```sh
python3 tests/tools/alle-tests.py            # alle Tests (ca. 5 Min.)
python3 tests/tools/alle-tests.py --ohne-sw  # ohne Service-Worker-Test (ca. 1 Min.)
```

Führt Daten-Test (Deutsch und Englisch), Texte-Test, Vereins-Test, Fenster-Test, Knopfreihen-Test und Service-Worker-Test aus und zeigt eine
Zusammenfassung. Die Bilder (`bilder.py`) kommen zusätzlich, wenn sich das Aussehen ändert.

## Daten-Test – „gleiche Eingaben, gleiche Daten“

```sh
python3 tests/tools/daten-test.py                  # aktueller Stand gegen main, Deutsch
python3 tests/tools/daten-test.py --sprache en     # beide Stände auf Englisch
python3 tests/tools/daten-test.py --gegen 7c48820
```

Lädt das Beispielspiel in den aktuellen Stand **und** in den Vergleichsstand und vergleicht:
Scores der Beispieldateien, Export-JSON jedes Reiters (Laden → Anzeigen → Speichern), CSV, Saison-Statistik,
CSV je Schiedsrichter-System, Kader-Import (JSON und TXT) und den `localStorage`.
Das Aussehen darf sich unterscheiden, die Daten nicht. Ergebnis „0 Unterschiede“ = bestanden.
Gewollte Abweichungen sind im Test ausdrücklich aufgeführt und werden als „gewollt“ angezeigt
(seit 2.1b: gespeicherte Rolle/Partner immer deutsch, z. B. „Einzel-Schiedsrichter“ statt „Solo Referee“).

**Test-Schnittstelle** – diese globalen Namen ruft der Test auf; sie bleiben bestehen (oder der Test wird mitgeändert):
`selectRefTab(i)`, `selectSummaryTab()`, `selectStatsTab()`, `switchSystem(s)`, `exportSingleReviewJSON()`,
`exportCSV()`, `downloadBlob(blob, name)`, `handleSeasonFilesUpload(e)`, `renderSeasonStatsDashboard(stats)`,
`handleKaderUpload(e)`, `computeRefScores(d)`, `saveCurrentRefData()`, `SYSTEM_CONFIGS`, `currentSystem`.

## Texte-Test – Sprachen vollständig?

```sh
python3 tests/tools/texte-test.py            # FR/IT fehlend = Hinweis
python3 tests/tools/texte-test.py --streng   # ab Etappe 2.9: FR/IT fehlend = Fehler
```

Prüft: jeder verwendete Schlüssel (`t('…')`, `data-i18n`) existiert; Englisch hat alle Texte mit gleichen
Platzhaltern und gleich langen Listen; gespeicherte Werte (`val`) sind in allen Sprachen gleich; jede Rolle hat
eine englische Bezeichnung; die Sprachwahl bleibt nach Neuladen; `?lang=fr` wird nicht gespeichert und zeigt
fehlende Texte auf Deutsch; versteckte Sprachen stehen nicht in der Auswahl.

## Vereins-Test – kein „EVZ“ fest im Code

```sh
python3 tests/tools/verein-test.py
```

Startet eine Kopie der App mit einem erfundenen Verein („HC Musterdorf“, eigenes Logo) statt der Werte in
`js/club.js` und prüft alle Ansichten auf Deutsch und Englisch, am Bildschirm und im Druck, dazu Meldungen und
Exporte: Nirgends darf „EVZ“, „EV Zug“ oder „Bossard“ erscheinen. Der Testverein muss im Titel, im Export
(`club`) und als Logo erscheinen, und das Logo muss offline im Cache liegen.

## Fenster-Test – eigene Fenster statt Browser-Popups

```sh
python3 tests/tools/fenster-test.py
```

Bedient die App mit echten Klicks und Tasten (Enter, Esc), auf Deutsch und Englisch: kein `alert`/`confirm`/`prompt`
mehr (im Code und zur Laufzeit); Sichern mit fehlenden Feldern zeigt eine Liste, ein Tipp springt zum Feld;
Zurücksetzen hat einen roten Knopf, „Abbrechen“ ist vorgewählt und Enter/Esc löschen nichts; Szene mit Spielzeit
(Enter fügt hinzu, Esc bricht ab); Hinweise bei Kader-Import und übersprungenen Statistik-Dateien.

## Knopfreihen-Test – Segmented Controls

```sh
python3 tests/tools/knopfreihen-test.py
```

Auf 834, 1194 und 1440 px, Deutsch und Englisch, Head Referee und Linesperson: jede Knopfreihe ist eine echte
Radiogruppe mit Namen (VoiceOver), jedes Segment mindestens 44 × 44 px, nichts abgeschnitten, keine waagrechte
Bildlaufleiste; Reihenfolge vom besten zum schlechtesten Wert (Trend mit „Erstbeobachtung“); Gesamteinschätzung
ohne Vorwahl mit Hinweis, nach der Wahl mit Definition; jede Option speichert den bisherigen Wert (echter Klick),
auch nach Neuladen; Pfeiltasten wechseln die Wahl.

## Service-Worker-Test – Updates, offline, langsames Netz

```sh
python3 tests/tools/sw-test.py                          # alle Szenarien (ca. 4 Min.)
python3 tests/tools/sw-test.py langsam-alles offline    # einzelne Szenarien
python3 tests/tools/sw-test.py --uebergang-von 67b77e9  # zusätzlich: Wechsel von einem alten Stand
```

Simuliert ein neues Release (`?v=` + 1), Offline, langsames Netz (+5 s, alles oder nur CSS/JS) und ein Release
ohne erhöhte Nummer (Badge muss dann „Update blockiert“ zeigen). Prüft bei jedem Start: Seite, CSS und alle JS-Dateien aus **einer** Version, App vollständig,
vom Service Worker geliefert, bei langsamem Netz Start nach ca. 3 s. Ergebnis „0 Fehler“ = bestanden.

## Bilder – Bildschirmfotos und Druck-PDF

```sh
python3 tests/tools/bilder.py                 # aktueller Stand
python3 tests/tools/bilder.py --gegen main    # zusätzlich main daneben
```

Fotografiert Head Referee, Linesperson, Gespann und Statistik in iPad hochkant (834 px), iPad quer (1194 px) und
MacBook (1440 px), je hell und dunkel, plus ein Druck-PDF. Danach
`tests/tools/ergebnisse/bilder/uebersicht.html` im Browser öffnen.

## Andere Chrome-Installation

Liegt Chrome nicht unter `/Applications/Google Chrome.app`, den Pfad mitgeben:
`CHROME="/Pfad/zu/chrome" python3 tests/tools/daten-test.py`
