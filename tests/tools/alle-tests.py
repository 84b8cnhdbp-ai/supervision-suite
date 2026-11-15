"""Alle Tests nacheinander – nach jedem Teilschritt laufen lassen.

Aufruf: python3 tests/tools/alle-tests.py            (ca. 4 Min.)
        python3 tests/tools/alle-tests.py --ohne-sw  (ohne Service-Worker-Test, ca. 1 Min.)
Abbruchcode 1, wenn ein Test fehlschlägt.
"""
import os
import subprocess
import sys
import time

HIER = os.path.dirname(os.path.abspath(__file__))
TESTS = [
    ('Daten-Test Deutsch', ['daten-test.py']),
    ('Daten-Test Englisch', ['daten-test.py', '--sprache', 'en']),
    ('Texte-Test', ['texte-test.py']),
    ('Vereins-Test', ['verein-test.py']),
    ('Fenster-Test', ['fenster-test.py']),
    ('Knopfreihen-Test', ['knopfreihen-test.py']),
    ('Layout-Test', ['layout-test.py']),
    ('Score-Test', ['score-test.py']),
    ('Spiel-Test', ['spiel-test.py']),
    ('Szene-Test', ['szene-test.py']),
    ('Übersicht-Test', ['uebersicht-test.py']),
    ('Druck-Test', ['druck-test.py']),
    ('Service-Worker-Test', ['sw-test.py']),
]

ergebnisse = []
for name, befehl in TESTS:
    if name == 'Service-Worker-Test' and '--ohne-sw' in sys.argv:
        continue
    start = time.time()
    r = subprocess.run([sys.executable, os.path.join(HIER, befehl[0])] + befehl[1:], capture_output=True, text=True)
    zeilen = (r.stdout + r.stderr).strip().splitlines()
    ergebnisse.append((name, r.returncode == 0, zeilen[-1] if zeilen else '', time.time() - start))
    if r.returncode != 0:
        print(f'--- {name} ---')
        print('\n'.join(zeilen[-25:]))

print()
for name, ok, letzte, dauer in ergebnisse:
    print(f"{'ok    ' if ok else 'FEHLER'} {name:<22} {dauer:5.0f} s  {letzte}")
sys.exit(0 if all(ok for _, ok, _, _ in ergebnisse) else 1)
