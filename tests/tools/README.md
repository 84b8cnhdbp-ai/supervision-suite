# Testwerkzeuge

Brauchen nur **Python 3** und **Google Chrome** (kein Installieren von Paketen). Alle Tests laufen mit den
erfundenen Beispieldaten aus `tests/fixtures/`. Ergebnisse landen in `tests/tools/ergebnisse/`; dieser Ordner
steht in `.gitignore` und kommt **nie** ins Repo.

Alle Befehle im Projektordner ausführen.

**Referenz:** Alle Vergleiche mit dem alten Stand (Daten-, Übersicht-, Wechsel-Test, `bilder.py --gegen`) laufen
standardmässig gegen den Tag `stand-etappe-1` (Stand vor Etappe 2, `5e59592`), nicht gegen `main` – so bleiben sie
gültig, auch wenn `main` weiterläuft. Ein anderer Stand geht mit `--gegen …` bzw. `--von …`.

**Gegenproben** nie im Arbeitsordner, immer in einer temporären Kopie: `python3 tests/tools/gegenprobe.py` (siehe unten).

**Bewegung:** Alle Tests laufen mit „Bewegung reduzieren“ (`prefers-reduced-motion`), damit Bilder und Messungen nie
mitten in einer Animation entstehen. Nur der Animations-Test schaltet die Übergänge ein (`b.bewegung = True`).

## Alles auf einmal – nach jedem Teilschritt

```sh
python3 tests/tools/alle-tests.py            # alle Tests (ca. 5 Min.)
python3 tests/tools/alle-tests.py --ohne-sw  # ohne Service-Worker-Test (ca. 1 Min.)
```

Führt Daten-Test (Deutsch und Englisch), Texte- (streng), Kunstsprache-, Vereins-, Fenster-, Knopfreihen-, Layout-, Score-,
Spiel-, System-, Szene-, Übersicht-, Druck-, Bereiche-, Animations-, Wechsel-, Dateiwahl- und Service-Worker-Test aus und zeigt eine Zusammenfassung
mit der Schlussmeldung jedes Tests (aus stdout; Meldungen auf stderr werden zusätzlich angezeigt).
Die Bilder (`bilder.py`) kommen zusätzlich, wenn sich das Aussehen ändert.

## Daten-Test – „gleiche Eingaben, gleiche Daten“

```sh
python3 tests/tools/daten-test.py                  # aktueller Stand gegen stand-etappe-1, Deutsch
python3 tests/tools/daten-test.py --sprache en     # beide Stände auf Englisch
python3 tests/tools/daten-test.py --gegen main     # anderer Referenzstand
python3 tests/tools/daten-test.py --gegen 7c48820
```

Lädt das Beispielspiel in den aktuellen Stand **und** in den Vergleichsstand und vergleicht:
Scores der Beispieldateien, Export-JSON jedes Reiters (Laden → Anzeigen → Speichern), CSV, Saison-Statistik,
CSV je Schiedsrichter-System, Kader-Import (JSON und TXT) und den `localStorage`.
Das Aussehen darf sich unterscheiden, die Daten nicht. Ergebnis „0 Unterschiede“ = bestanden.
Gewollte Abweichungen sind im Test ausdrücklich aufgeführt und werden als „gewollt“ angezeigt
(seit 2.1b: gespeicherte Rolle/Partner immer deutsch, z. B. „Einzel-Schiedsrichter“ statt „Solo Referee“;
neues Spiel startet mit `standardSystem` aus `js/club.js` statt immer 4-Mann – geprüft im Teil „leerer Start“;
neues Spiel startet ohne Liga statt mit „National League“ – ebenfalls „leerer Start“). Der Teil „ohneLiga“ vergleicht
ohne Abweichung: ältere Daten ohne Angabe zur Liga zeigen in beiden Ständen „National League“.

**Test-Schnittstelle** – diese globalen Namen ruft der Test auf; sie bleiben bestehen (oder der Test wird mitgeändert):
`selectRefTab(i)`, `selectSummaryTab()`, `selectStatsTab()`, `switchSystem(s)`, `exportSingleReviewJSON()`,
`exportCSV()`, `downloadBlob(blob, name)`, `handleSeasonFilesUpload(e)`, `renderSeasonStatsDashboard(stats)`,
`handleKaderUpload(e)`, `computeRefScores(d)`, `saveCurrentRefData()`, `SYSTEM_CONFIGS`, `currentSystem`.

## Texte-Test – Sprachen vollständig?

```sh
python3 tests/tools/texte-test.py            # FR/IT fehlend = Hinweis
python3 tests/tools/texte-test.py --streng   # ab Etappe 2.9: FR/IT fehlend = Fehler (so in alle-tests.py)
```

Prüft: jeder verwendete Schlüssel (`t('…')`, `data-i18n`, `-placeholder`, `-aria-label`, `-group`) existiert; Englisch hat alle Texte mit gleichen
Platzhaltern und gleich langen Listen; gespeicherte Werte (`val`) sind in allen Sprachen gleich; jede Rolle hat
eine englische Bezeichnung; die Sprachwahl bleibt nach Neuladen; `?lang=fr` wird nicht gespeichert und zeigt
fehlende Texte auf Deutsch; versteckte Sprachen stehen nicht in der Auswahl.

## Kunstsprache-Test – jeder Text über `t()`?

```sh
python3 tests/tools/kunstsprache-test.py
```

Erzeugt im Browser eine Kunstsprache, in der jeder Text als ⟦Text⟧ erscheint (gespeicherte Werte bleiben), und sucht
in allen Ansichten, Fenstern, Menüs und im Druck Texte, Platzhalter, `aria-label`, `title` und `alt` ausserhalb von ⟦…⟧ –
also fest eingebaute Texte. Ausgenommen sind Daten (Namen, Spiel, Verein, Ligen) und Sprachnamen. Die Kunstsprache gibt es
nur im Test: nie in der Sprachwahl, nie gespeichert (wird geprüft).

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

Auf 768, 834, 1080, 1194 und 1440 px, Deutsch und Englisch, Head Referee und Linesperson: jede Knopfreihe ist eine echte
Radiogruppe mit Namen (VoiceOver), jedes Segment mindestens 44 × 44 px, nichts abgeschnitten, keine waagrechte
Bildlaufleiste; ab zwei Spalten (1080, 1194, 1440 px) bricht in der Formularspalte nichts um; Reihenfolge vom besten zum schlechtesten Wert (Trend mit „Erstbeobachtung“); Gesamteinschätzung
ohne Vorwahl mit Hinweis, nach der Wahl mit Definition; jede Option speichert den bisherigen Wert (echter Klick),
auch nach Neuladen; Pfeiltasten wechseln die Wahl.

## Layout-Test – Seitenleiste, Werkzeugleiste, Menü „Mehr“

```sh
python3 tests/tools/layout-test.py
```

Auf 768, 834, 1080, 1194 und 1440 px (DE/EN): feste Seitenleiste ab 1180 px, darunter Schublade „‹ Spiele“ (öffnen, Esc, daneben tippen, Eintrag, Drehen auf quer), Hinweis für zu alte Geräte; Werkzeugleiste sichtbar, keine waagrechte Bildlaufleiste,
Knöpfe mind. 44 px, Reiter vollständig sichtbar. Reiter-Kurzform bei 3/4-Mann („H1 · Frei“), Nachname = alles
ausser dem letzten Wort („Von Rotz Peter“ → „Von Rotz“), Reiter folgen Namensänderungen sofort, Pfeiltasten.
Seitenleiste (Spiel, Statistik, Fuss mit Version/Stand aus `?v=`, Kader, Offline-Status, Gespeichert-Zeit).
Menü „Mehr“ mit echten Klicks: Esc / daneben tippen schliesst, CSV, Kader, Sprache, Darstellung, Zurücksetzen
(rot, mit Abstand). Kader-Knopf beim Schiedsrichter-Feld nur ohne Kader. Druck ohne Seitenleiste/Werkzeugleiste.

## Score-Test – rechte Spalte

```sh
python3 tests/tools/score-test.py
```

Ab 1000 px zwei Spalten, die rechte bleibt beim Scrollen stehen; darunter kompakte Score-Leiste (stehend) mit
Bereit-Zeichen, Profil und Bereit am Formularende. Abstand oben = gemessene Höhe der Werkzeugleiste (Gegenprobe mit
höherer Werkzeugleiste). Angezeigte Werte = `computeRefScores` in allen Reitern, Ring passend, Statustexte und Schwellen,
kurze Begriffe bei der Gesamteinschätzung. Netzdiagramm mit 7 Punkten, N/A als hohler grauer Punkt mit „(N/A)“,
im Druck sichtbar. „Bereit zum Sichern?“: fehlende Punkte springen zum Feld, gleiche Liste wie das Fenster beim
Sichern, nicht im Druck.

## Spiel-Test – Fenster „Spiel bearbeiten“

```sh
python3 tests/tools/spiel-test.py
```

Mit echten Klicks und Tasten: Zugang über Titel und „Mehr“, Reihenfolge der Felder, Spielnummer mit
Zifferntastatur (ohne Einschränkung auf Ziffern); „Abbrechen“/Esc verwerfen (auch ein späteres Speichern übernimmt
nichts Verworfenes), „Fertig“ speichert; Begegnung „CLUB.kurz – Gegner“, alte Begegnung bleibt, solange sie nicht
geändert wird; Visum wie früher; Namen und Durchgang je Rolle; Systemwechsel mit Rückfrage („Abbrechen“ vorgewählt)
nur bei vorhandenen Bewertungen; Spielnummer als Hinweis getrennt von den Pflichtpunkten, Sichern bleibt möglich;
automatisch öffnen nur ohne Spiel; Grössen 768/834/1194 px, DE/EN.

## System-Test – Standard-System für neue Spiele

```sh
python3 tests/tools/system-test.py
```

Neues Spiel und „Spiel zurücksetzen“ (echte Klicks) starten mit `standardSystem` aus `js/club.js` (beim Verein 2-Mann),
das Startsystem steht sofort in den Spieldaten (eine Bewertung vor jeder Spielangabe bleibt nach dem Neuladen erhalten);
ein gespeichertes 4-Mann-Spiel bleibt 4-Mann; ältere Daten ohne Angabe zum System gelten als 4-Mann; mit
`standardSystem: '4-Man'` startet die App mit 4-Mann, ein ungültiger Wert fällt auf 4-Mann zurück.

## Liga-Test – neue Spiele ohne Liga

```sh
python3 tests/tools/liga-test.py
```

Neues Spiel und „Spiel zurücksetzen“ (echte Klicks) starten ohne Liga („Liga wählen …“ / „Choose league …“), die leere
Liga steht sofort in den Spieldaten; in „Bereit zum Sichern?“ unter „Hinweise“ „Liga fehlt – Sichern trotzdem möglich“
(kein Pflichtpunkt), der Tipp darauf öffnet „Spiel bearbeiten“ mit Fokus auf der Liga; im Fenster steht derselbe Hinweis
unter der Karte „Spiel“ und verschwindet mit der Wahl; „Liga wählen …“ ist gesperrt (steht da, ist aber nicht wählbar);
nach Wahl und „Fertig“ ist der Hinweis weg und die Liga gespeichert. Ältere Daten ohne Angabe zur Liga (ohne `spiel_liga`, ohne `global`) zeigen
„National League“ (Datenregel `LIGA_OHNE_ANGABE` in `js/config.js`). Export JSON und CSV mit leerer Liga gehen, die
exportierte Datei läuft durch die Saison-Statistik. Gegenproben: `liga-startwert`, `liga-sperre`, `liga-fenster-hinweis`.

## Dateiwahl-Test – Knöpfe mit Dateiauswahl

```sh
python3 tests/tools/dateiwahl-test.py
```

Jeder Knopf mit Dateiauswahl („Kader importieren“ im Menü und beim Schiedsrichter-Feld, „Dateien wählen“ in der
Statistik) mit echtem Klick: Die Auswahl öffnet sich (CDP `Page.setInterceptFileChooserDialog`), direkt im Klick, das
Dateifeld ist nicht `display: none`, die übergebene Datei wird importiert; alle Dateifelder abgedeckt; Gegenprobe mit
einem nicht angeschlossenen Knopf.

## Szene-Test – Szenen und Chips

```sh
python3 tests/tools/szene-test.py
```

Mit echten Klicks und Tasten: Spielzeit freiwillig, „834“ → 08:34, gültig bis 20:00 und Sekunden unter 60, ungültige
Zeit wird nicht gespeichert; Speicherformat genau `[P2 08:34] Text` bzw. `[P2] Text`, Zeilenumbrüche werden
Leerzeichen, neue Szenen am Ende der Notiz; Anzeige und Druck sortiert (Drittel, Restzeit absteigend, ohne Zeit am Ende
des Drittels, unlesbare alte Angaben ganz am Ende); Ändern an derselben Stelle, Löschen mit Rückfrage; freier Text
getrennt, Notiz ohne Bearbeitung unverändert; zuletzt benutztes Drittel, bei anderem Spiel wieder „1.“; Chips höchstens
zwei Zeilen; 768/834/1194 px, DE/EN.

## Übersicht-Test – Gespann-Übersicht und Saison-Statistik

```sh
python3 tests/tools/uebersicht-test.py
```

Gespann: eine Karte je Rolle als echter Knopf (Enter/Leertaste, VoiceOver-Name), Werte = `computeRefScores`,
Durchschnitt mit denselben Schwellen wie die Bewertung, Tipp öffnet den Reiter, leerer Zustand („Rollen besetzen“),
Druck. Statistik: Zahlen mit den Beispieldateien und **Zelle für Zelle gleich wie im alten Stand** (`stand-etappe-1`) (gleiche Dateien in den
alten Stand geladen), negative Entwicklung mit echtem „−“ und Pfeil, Abzeichen-Kontrast hell/dunkel, Tabelle passt ab
768 px, leerer Zustand („.json wählen“), Sprachwechsel, DE/EN.

## Druck-Test – Druck vollständig

```sh
python3 tests/tools/druck-test.py
```

Druckansicht A4: Jedes mehrzeilige Feld (Notizen, Stärken, Schwerpunkte, Rapport, Gespann-Notiz) erscheint mit langem
Text vollständig (Druckfassung, nichts abgeschnitten), leere Felder fallen weg; die Druckfassung ist am Bildschirm
ausgeblendet und `aria-hidden`; auch nach Reiterwechsel und Neuladen aktuell. Supervisor in der Titelzeile nur im Druck.
Statistik: Saison aus den Spieldaten (eine, mehrere, keine; ab August neue Saison), Druckdatum, Kennzahlen in einer Zeile,
Spaltentitel auf jeder Seite, keine geteilten Zeilen, „Bewertungen laden“ ausgeblendet, Fusszeile „Vertraulich“, DE/EN.

Supervisor in der Titelzeile auch nach Änderung unter „Spiel bearbeiten“ (echte Klicks).
Dass der Druck mitten im Hochzählen den fertigen Score zeigt, prüft der Animations-Test (nur dort laufen Übergänge).

## Bereiche-Test – Karten für VoiceOver

```sh
python3 tests/tools/bereiche-test.py
```

Liest den Bedienungshilfen-Baum (was ein Screenreader sieht): Jede Karte ist ein Bereich mit ihrem Titel als Namen –
Score (mit Rolle), Profil, Bereit zum Sichern?, Gespann-Durchschnitt, Profil des Gespanns, Gespann-Beobachtungen,
Bewertungen laden –, auch hochkant mit aufgelöster rechter Spalte; nur Bereiche der sichtbaren Ansicht; 834/1080/1194 px,
DE/EN. VoiceOver in Safari kann abweichen: auf dem iPad von Hand gegenprüfen.

## Animations-Test – Übergänge

```sh
python3 tests/tools/animation-test.py
```

Einziger Test mit Übergängen: Reiterwechsel blendet ein (150 ms), Score zählt nur beim Reiterwechsel hoch (400 ms,
Bewertung und Gespann, Endwert = berechneter Score); beim Bearbeiten und Sprachwechsel sofort. Druck mitten im
Hochzählen (Druckansicht und `beforeprint`): Zahl und Ring sofort fertig. Mit „Bewegung reduzieren“ bewegt sich nichts.

## Wechsel-Test – vom alten auf den neuen Stand, ohne Datenverlust

```sh
python3 tests/tools/wechsel-test.py                 # stand-etappe-1 → aktueller Stand
python3 tests/tools/wechsel-test.py --rueck ORDNER  # Rückweg aus einem Ordner (Ergebnis des Notfall-Ablaufs)
python3 tests/tools/wechsel-test.py --gegenprobe    # prüft den Test selbst: muss rot werden
```

Ein Browser-Profil, eine Adresse – wie auf dem iPad: Im alten Stand (`stand-etappe-1` = `main` vor dem Merge) wird über die alte Oberfläche eine Bewertung
ausgefüllt (Kader per echter Dateiwahl, Spieldaten, zwei Schiedsrichter, Notizen mit alten Zeitangaben, Englisch,
dunkel), **nicht** exportiert. Dann liefert dieselbe Adresse den neuen Stand: neue Version vollständig (keine
gemischten Versionen), Speicher beim Start unverändert, jedes Feld mit dem alten Wert, Scores sowie Export-JSON und CSV
gleich wie in der alten Oberfläche (gewollte Abweichungen wie im Daten-Test), Einstellungen bleiben, offline aus dem
Cache. Rückweg (alter Code mit höherer `?v=`, wie `git revert`): nach Bearbeiten und Darstellung „Auto“ startet die
alte Oberfläche ohne JS-Fehler und zeigt die Bewertung, auch mit gespeicherten Werten „auto“ und „fr“.
Neuer Code mit gleicher Nummer: alte Version bleibt aktiv, Badge „Update blockiert“.

## Gegenproben – fällt ein Test auf, wenn die App kaputt ist?

```sh
python3 tests/tools/gegenprobe.py           # alle (einige Minuten)
python3 tests/tools/gegenprobe.py --liste   # Katalog anzeigen
python3 tests/tools/gegenprobe.py system-vermerk
```

Jede Gegenprobe kopiert das ganze Repo in einen temporären Ordner, baut dort absichtlich einen Fehler ein und startet den
Test in der Kopie; er muss rot werden und die erwartete Meldung zeigen. Am Schluss wird geprüft, dass der Arbeitsordner
unverändert ist. Neue Gegenproben im Katalog `GEGENPROBEN` eintragen – nie Dateien im Repo dafür ändern.

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
python3 tests/tools/bilder.py --gegen         # zusätzlich der alte Stand (stand-etappe-1) daneben
python3 tests/tools/bilder.py --gegen main    # anderer Referenzstand
python3 tests/tools/bilder.py --gegen HEAD --pixel        # Pixelvergleich (z. B. vor/nach dem Aufräumen)
python3 tests/tools/bilder.py --gegen /pfad/kopie --pixel # Referenz aus einem Ordner (nicht committeter Stand)
```

Fotografiert Head Referee, Linesperson, Gespann und Statistik in iPad hochkant (768, 834 px), iPad quer (1080, 1194 px) und
MacBook (1440 px), je hell und dunkel, dazu Druckansichten und ein Druck-PDF – mit fester Uhrzeit und ohne Übergänge,
damit gleiche Stände pixelgleiche Bilder ergeben. `--pixel` listet jedes Bild, das sich auch nur in einem Pixel
unterscheidet (Abbruchcode 1). Achtung: Die Versionsnummer `?v=` steht in der Seitenleiste; für einen reinen
Pixelvergleich die Referenz mit derselben Nummer verwenden. Danach
`tests/tools/ergebnisse/bilder/uebersicht.html` im Browser öffnen.

## Andere Chrome-Installation

Liegt Chrome nicht unter `/Applications/Google Chrome.app`, den Pfad mitgeben:
`CHROME="/Pfad/zu/chrome" python3 tests/tools/daten-test.py`
