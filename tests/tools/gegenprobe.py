"""Gegenproben: Fällt ein Test auf, wenn die App kaputt ist? – immer in einer temporären Kopie, nie im Arbeitsordner.

Jede Gegenprobe kopiert das ganze Repo (mit .git, ohne Ergebnisse) in einen temporären Ordner, baut dort absichtlich
einen Fehler ein und startet den Test in der Kopie. Der Test MUSS dann rot werden (Abbruchcode 1) und die erwartete
Meldung zeigen. Der Arbeitsordner bleibt unberührt (wird am Ende geprüft).

Aufruf:   python3 tests/tools/gegenprobe.py               (alle)
          python3 tests/tools/gegenprobe.py system-vermerk animation-druck
          python3 tests/tools/gegenprobe.py --liste
Neue Gegenprobe: unten in GEGENPROBEN eintragen (Datei, alter Text, neuer Text – der alte Text muss vorkommen).
Abbruchcode 1, wenn eine Gegenprobe nicht anschlägt oder veraltet ist.
"""
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HIER, '..', '..'))

# name: (Test, [(Datei, alter Text, neuer Text)], erwartete Meldung, Beschreibung)
GEGENPROBEN = {
    'kunstsprache-feste-texte': ('kunstsprache-test.py', [
        ('index.html', '<p class="sf-hinweis sf-hinweis-info" id="sfAltHinweis" hidden></p>',
         '<p class="sf-hinweis sf-hinweis-info" id="sfAltHinweis" hidden></p><p>Szene</p>'),
        ('index.html', 'id="spiel_ort" data-i18n-placeholder="ph_arena" placeholder=""', 'id="spiel_ort" placeholder="Halle eingeben"'),
        ('js/stats.js', 'function initStatistik() {',
         "function initStatistik() {\n  document.getElementById('seasonStatsView').insertAdjacentHTML('beforeend', '<span>Durchschnitt</span>');"),
    ], 'Halle eingeben', 'feste Texte in HTML, Platzhalter und JavaScript'),
    'druck-supervisor': ('druck-test.py', [
        ('tests/tools/druck-test.py', "            b.klick('#sfFertig')\n            b.fenster(794, 1123, druck=True)\n            sup =",
         "            b.js('aktualisiereSpielTitel = () => {}'); b.klick('#sfFertig')\n            b.fenster(794, 1123, druck=True)\n            sup ="),
    ], 'Supervisor nicht aktualisiert', 'Titelzeile nach „Spiel bearbeiten“ nicht nachgeführt'),
    'animation-druck': ('animation-test.py', [
        ('js/bewegung.js', '    if (anteil >= 1 || imDruck()) {', '    if (anteil >= 1) {'),
        ('js/bewegung.js', "  window.addEventListener('beforeprint', zaehlerFertig);", ''),
        ('js/bewegung.js', "  if (druck.addEventListener) druck.addEventListener('change', (e) => { if (e.matches) zaehlerFertig(); });", ''),
    ], 'Druck zeigt', 'Druck mitten im Hochzählen ohne Absicherung'),
    'animation-bearbeiten': ('animation-test.py', [
        ('js/bewegung.js', '  if (!reiterWechsel || wert === null', '  if (wert === null'),
    ], 'Bearbeiten: Score springt nicht sofort', 'Score zählt auch beim Bearbeiten hoch'),
    'system-vermerk': ('system-test.py', [
        ('js/storage.js', '  if (!raw) gameData.global = { ...(gameData.global || {}), system_typ: currentSystem };\n', ''),
    ], 'Nach Neuladen', 'neues Spiel ohne sofort vermerktes System (Bewertung verschwindet)'),
    'wechsel-altdaten': ('wechsel-test.py', [
        ('js/storage.js', '  currentSystem = raw ? SYSTEM_OHNE_ANGABE : startSystem();', '  currentSystem = startSystem();'),
    ], 'Alte Daten ohne System', 'alte Daten ohne Systemangabe nicht mehr 4-Mann'),
    'wechsel-speicherschluessel': ('wechsel-test.py', [
        ('js/storage.js', "'referee_multi_supervision_data'", "'referee_daten_neu'"),
    ], 'Bewertung', 'neuer Stand liest unter anderem Speicherschlüssel'),
    'score-spalte-alte-regel': ('score-test.py', [
        ('js/layout.js', "  wurzel.setProperty('--spalte-oben', Math.floor(Math.min(normal, window.innerHeight - hoehe - 12)) + 'px');",
         "  wurzel.setProperty('--spalte-oben', normal + 'px');"),
    ], 'nicht richtig', 'rechte Spalte bleibt immer oben stehen (unteres Ende unerreichbar)'),
    'dateiwahl-display-none': ('dateiwahl-test.py', [
        ('index.html', 'id="kaderDatei" class="datei-feld"', 'id="kaderDatei" class="datei-feld" hidden'),
    ], 'display: none', 'Dateifeld wieder display: none'),
}


def fingerabdruck(ordner):
    """Prüfsumme aller Dateien im Arbeitsordner (ohne Ergebnisse) – muss vorher und nachher gleich sein."""
    h = hashlib.sha256()
    for wurzel, ordnerliste, dateien in os.walk(ordner):
        ordnerliste[:] = sorted(d for d in ordnerliste if d not in ('ergebnisse', '__pycache__', '.git'))
        for d in sorted(dateien):
            p = os.path.join(wurzel, d)
            h.update(p.encode())
            h.update(open(p, 'rb').read())
    return h.hexdigest()


def gegenprobe(name):
    test, aenderungen, erwartet, _ = GEGENPROBEN[name]
    kopie = tempfile.mkdtemp(prefix='gegenprobe-')
    try:
        shutil.copytree(REPO, kopie, dirs_exist_ok=True, ignore=shutil.ignore_patterns('ergebnisse', '__pycache__'))
        for datei, alt, neu in aenderungen:
            p = os.path.join(kopie, datei)
            s = open(p, encoding='utf-8').read()
            if alt not in s:
                return False, f'veraltet: Text in {datei} nicht gefunden – Gegenprobe anpassen'
            open(p, 'w', encoding='utf-8').write(s.replace(alt, neu))
        r = subprocess.run([sys.executable, os.path.join(kopie, 'tests', 'tools', test)], capture_output=True, text=True, cwd=kopie)
        letzte = (r.stdout.strip().splitlines() or [''])[-1]
        if r.returncode != 1:
            return False, f'schlägt NICHT an (Abbruchcode {r.returncode}): {letzte[:90]}'
        if erwartet not in r.stdout:
            return False, f'rot, aber ohne die erwartete Meldung „{erwartet}“: {letzte[:90]}'
        anzahl = sum(1 for z in r.stdout.splitlines() if z.startswith('FEHLER'))
        return True, f'schlägt an ({anzahl} Fehler, u. a. „{erwartet}“)'
    finally:
        shutil.rmtree(kopie, ignore_errors=True)


def main():
    if '--liste' in sys.argv:
        for n, (t, _, _, beschr) in GEGENPROBEN.items():
            print(f'{n:<28} {t:<20} {beschr}')
        return
    namen = [a for a in sys.argv[1:] if not a.startswith('--')] or list(GEGENPROBEN)
    vorher = fingerabdruck(REPO)
    ergebnisse = []
    for n in namen:
        ok, text = gegenprobe(n)
        ergebnisse.append(ok)
        print(f"{'ok    ' if ok else 'FEHLER'} {n:<28} {text}")
    unberuehrt = fingerabdruck(REPO) == vorher
    print(f'Arbeitsordner unverändert: {"ja" if unberuehrt else "NEIN"}')
    print(f'Gegenproben: {sum(ergebnisse)} von {len(ergebnisse)} schlagen an')
    sys.exit(0 if all(ergebnisse) and unberuehrt else 1)


if __name__ == '__main__':
    main()
