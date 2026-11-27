"""Alle Tests nacheinander – nach jedem Teilschritt laufen lassen.

Aufruf: python3 tests/tools/alle-tests.py            (ca. 4 Min.)
        python3 tests/tools/alle-tests.py --ohne-sw  (ohne Service-Worker-Test, ca. 1 Min.)
Abbruchcode 1, wenn ein Test fehlschlägt.
Bricht die Verbindung zu Chrome ab, wiederholt ein Test einmal von vorne (werkzeug.fuehre_aus, im sw-test das Szenario) –
nur ohne vorherige Fehler; die Anzahl steht als Hinweis bei der Schlussmeldung und am Ende insgesamt.
"""
import os
import subprocess
import sys
import re
import time

HIER = os.path.dirname(os.path.abspath(__file__))
TESTS = [
    ('Daten-Test Deutsch', ['daten-test.py']),
    ('Daten-Test Englisch', ['daten-test.py', '--sprache', 'en']),
    ('Texte-Test', ['texte-test.py', '--streng']),
    ('Kunstsprache-Test', ['kunstsprache-test.py']),
    ('Vereins-Test', ['verein-test.py']),
    ('Fenster-Test', ['fenster-test.py']),
    ('Dateiwahl-Test', ['dateiwahl-test.py']),
    ('Knopfreihen-Test', ['knopfreihen-test.py']),
    ('Layout-Test', ['layout-test.py']),
    ('Score-Test', ['score-test.py']),
    ('Spiel-Test', ['spiel-test.py']),
    ('System-Test', ['system-test.py']),
    ('Liga-Test', ['liga-test.py']),
    ('Szene-Test', ['szene-test.py']),
    ('Übersicht-Test', ['uebersicht-test.py']),
    ('Druck-Test', ['druck-test.py']),
    ('Bereiche-Test', ['bereiche-test.py']),
    ('Animations-Test', ['animation-test.py']),
    ('Wechsel-Test', ['wechsel-test.py']),
    ('Service-Worker-Test', ['sw-test.py']),
]

ergebnisse = []
for name, befehl in TESTS:
    if name == 'Service-Worker-Test' and '--ohne-sw' in sys.argv:
        continue
    start = time.time()
    r = subprocess.run([sys.executable, os.path.join(HIER, befehl[0])] + befehl[1:], capture_output=True, text=True)
    zeilen = (r.stdout + r.stderr).strip().splitlines()
    # Schlussmeldung = letzte Zeile auf stdout ohne den Hinweis zu Wiederholungen (stderr kann z. B. Meldungen des
    # Test-Servers enthalten). Wiederholungen nach Verbindungsabbruch (werkzeug.fuehre_aus, sw-test) als Hinweis anhängen.
    zeilen_out = r.stdout.strip().splitlines()
    m = [re.match(r'Hinweis: (\d+) Wiederholung nach Verbindungsabbruch$', z) for z in zeilen_out]
    wiederholungen = sum(int(x.group(1)) for x in m if x)
    schluss = [z for z, x in zip(zeilen_out, m) if not x]
    letzte = schluss[-1] if schluss else '(keine Schlussmeldung – Test abgebrochen?)'
    if wiederholungen:
        letzte += f'  [Hinweis: {wiederholungen} Wiederholung nach Verbindungsabbruch]'
    if r.stderr.strip():
        letzte += f'  [+{len(r.stderr.strip().splitlines())} Zeilen stderr]'
    ok = r.returncode == 0 and bool(schluss)
    ergebnisse.append((name, ok, letzte, time.time() - start, wiederholungen))
    if not ok or r.stderr.strip() or wiederholungen:
        print(f'--- {name} ---')
        print('\n'.join(zeilen[-25:]))

print()
for name, ok, letzte, dauer, _ in ergebnisse:
    print(f"{'ok    ' if ok else 'FEHLER'} {name:<22} {dauer:5.0f} s  {letzte}")
summe = sum(w for *_, w in ergebnisse)
print(f'\nWiederholungen nach Verbindungsabbruch insgesamt: {summe}' + (' (siehe Hinweise oben)' if summe else ''))
sys.exit(0 if all(ok for _, ok, *_ in ergebnisse) else 1)
