# Testwerkzeuge

Brauchen nur **Python 3** und **Google Chrome** (kein Installieren von Paketen). Alle Tests laufen mit den
erfundenen Beispieldaten aus `tests/fixtures/`. Ergebnisse landen in `tests/tools/ergebnisse/`; dieser Ordner
steht in `.gitignore` und kommt **nie** ins Repo.

Alle Befehle im Projektordner ausführen.

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

## Service-Worker-Test – Updates, offline, langsames Netz

```sh
python3 tests/tools/sw-test.py                          # alle Szenarien (ca. 2 Min.)
python3 tests/tools/sw-test.py langsam-alles offline    # einzelne Szenarien
python3 tests/tools/sw-test.py --uebergang-von 67b77e9  # zusätzlich: Wechsel von einem alten Stand
```

Simuliert ein neues Release (`?v=` + 1), Offline, langsames Netz (+5 s, alles oder nur CSS/JS) und ein Release
ohne erhöhte Nummer. Prüft bei jedem Start: Seite, CSS und alle JS-Dateien aus **einer** Version, App vollständig,
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
