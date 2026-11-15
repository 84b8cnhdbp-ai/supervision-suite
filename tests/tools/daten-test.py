"""Daten-Test: Die App muss mit denselben Eingaben dieselben Daten erzeugen wie ein Referenzstand.

Vergleicht Export-JSON (pro Reiter), CSV, Saison-Statistik, Kader-Import, Systemwechsel und
localStorage zwischen dem aktuellen Arbeitsstand und einem Git-Stand (Standard: Tag stand-etappe-1).
Das Aussehen darf sich ändern – die Daten nicht.

Aufruf:   python3 tests/tools/daten-test.py                  (gegen stand-etappe-1, Deutsch)
          python3 tests/tools/daten-test.py --sprache en     (beide Stände auf Englisch)
          python3 tests/tools/daten-test.py --gegen 7c48820
Ergebnis: tests/tools/ergebnisse/daten-<stand>.json (nicht im Repo), Abbruchcode 1 bei Unterschieden.

Die Test-Schnittstelle (globale Funktionen, die der Test aufruft) steht in tests/tools/README.md.
"""
import json
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, ERGEBNISSE, REFERENZ, Browser, server, git_stand, daten_setzen, LEER  # noqa: E402

TEST_JS = r"""
(async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const downloads = [];
  window.downloadBlob = async (blob, name) => downloads.push({ name, type: blob.type, text: await blob.text() });
  window.alert = () => {}; window.confirm = () => false; window.prompt = () => null;
  let stats = null;
  const render = window.renderSeasonStatsDashboard;
  window.renderSeasonStatsDashboard = (s) => { stats = JSON.parse(JSON.stringify(s)); return render(s); };
  const fixture = async (n) => new File([await (await fetch('/tests/fixtures/' + n)).text()], n, { type: 'application/json' });
  const r = {};

  // 1. Scores der Beispieldateien (einzige Berechnung: computeRefScores)
  r.scores = {};
  for (const n of ['beispiel-v1.0.json', 'beispiel-v1.1.json', 'beispiel-v1.1-mit-na.json']) {
    const j = await (await fetch('/tests/fixtures/' + n)).json();
    const s = computeRefScores(j.evaluation); delete s.radar; r.scores[n] = s;
  }

  // 2. Export pro Reiter (liest dabei das Formular: Laden -> Anzeigen -> Speichern muss verlustfrei sein)
  const anzahl = SYSTEM_CONFIGS[currentSystem].length;
  for (let i = 0; i < anzahl; i++) { selectRefTab(i); await sleep(30); exportSingleReviewJSON(); }
  exportCSV();
  selectSummaryTab(); await sleep(30);
  r.nachReitern = localStorage.getItem('referee_multi_supervision_data');

  // 3. Saison-Statistik mit allen Beispieldateien
  selectStatsTab();
  const dateien = await Promise.all(['beispiel-v1.0.json', 'beispiel-v1.0-ohne-evaluation.json', 'beispiel-v1.1.json',
    'beispiel-v1.1-mit-na.json', 'beispiel-spiel.json'].map(fixture));
  await handleSeasonFilesUpload({ target: { files: dateien, value: '' } });
  r.statistik = stats && Object.fromEntries(Object.entries(stats).map(([n, v]) =>
    [n, { R1: v.R1 && v.R1.scoreGesamt, R2: v.R2 && v.R2.scoreGesamt }]));

  // 4. Systemwechsel (leere Reiter) und CSV je System
  for (const sys of ['2-Man', '1-Man', '3-Man', '4-Man']) { switchSystem(sys); await sleep(30); exportCSV(); }

  // 5. Kader-Import JSON und TXT
  await handleKaderUpload({ target: { files: [await fixture('beispiel-kader.json')], value: '' } });
  r.kaderJson = localStorage.getItem('referee_kader');
  await handleKaderUpload({ target: { files: [new File(['Meier Luca\nTest Anna\n'], 'k.txt')], value: '' } });
  r.kaderTxt = localStorage.getItem('referee_kader');

  // 6. Gespeicherte Rolle beim 1-Mann-System (einzige Rolle mit eigener englischer Bezeichnung)
  switchSystem('1-Man'); await sleep(30); saveCurrentRefData();
  r.rolle1Mann = JSON.parse(localStorage.getItem('referee_multi_supervision_data')).referees['1-Man_r1'].role;
  switchSystem('4-Man'); await sleep(30);

  await sleep(200);
  r.downloads = downloads.map((d) => {
    if (d.name.endsWith('.json')) { const j = JSON.parse(d.text); j.exportiertAm = '(maskiert)'; return { ...d, text: j }; }
    return d;
  });
  r.ende = localStorage.getItem('referee_multi_supervision_data');
  return r;
})()
"""


# Gewollte Abweichungen gegenüber dem Referenzstand:
# - Etappe 2.1b: gespeicherte Rollen und Partner-Texte sind neu in jeder Sprache deutsch.
# - Startsystem: Ein NEUES Spiel (leerer Start, „Spiel zurücksetzen“) beginnt neu mit dem System aus der
#   Vereins-Einstellung (js/club.js, standardSystem), bisher immer 4-Mann. Gespeicherte Spiele behalten ihr System,
#   Spiele ohne Angabe gelten weiter als 4-Mann – das prüfen die übrigen Teile dieses Tests (Beispielspiel) und der
#   System- und der Wechsel-Test.
# Alles andere muss gleich bleiben.
EN_ZU_DE = {'Solo Referee': 'Einzel-Schiedsrichter'}
STANDARD_SYSTEM = re.search(r"standardSystem:\s*'([^']+)'", open(os.path.join(REPO, 'js', 'club.js'), encoding='utf-8').read()).group(1)


def gewollt(pfad, alt, neu):
    if pfad == '.leerStart.system':
        return alt == '4-Man' and neu == STANDARD_SYSTEM
    if pfad == '.leerStart.reiter':
        return neu == {'1-Man': 1, '2-Man': 2, '3-Man': 3, '4-Man': 4}[STANDARD_SYSTEM]
    if not isinstance(alt, str) or not (pfad.endswith('.role') or pfad.endswith('.partner') or pfad == '.rolle1Mann'):
        return False
    for en, de in EN_ZU_DE.items():
        alt = alt.replace(en, de)
    return alt == neu


def lauf(wurzel, sprache):
    srv = server(wurzel, {'/__leer': LEER})
    try:
        with Browser() as b:
            b.fehler = []
            b.fenster(1194, 834)
            daten_setzen(b, srv.basis, spiel=True, sprache=sprache)
            b.oeffnen(srv.basis + '/index.html')
            r = b.js(TEST_JS)
            # Leerer Start (neues Spiel ohne gespeicherte Daten): Startsystem und Anzahl Reiter
            daten_setzen(b, srv.basis, spiel=False, sprache=sprache)
            b.oeffnen(srv.basis + '/index.html')
            r['leerStart'] = b.js("({ system: currentSystem, reiter: SYSTEM_CONFIGS[currentSystem].length })")
            r['jsFehler'] = [f for f in b.fehler if 'Update nicht möglich' not in f]
            # gespeicherte Spielstände als Objekte vergleichen (genauere Fundstellen)
            for k in ('nachReitern', 'ende'):
                r[k] = json.loads(r[k]) if r.get(k) else r.get(k)
            return r
    finally:
        srv.shutdown()


def vergleiche(pfad, a, b, aus):
    if type(a) != type(b) or not isinstance(a, (dict, list)):
        if a != b:
            aus.append((pfad, a, b))
        return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            vergleiche(f'{pfad}.{k}', a.get(k, '<fehlt>'), b.get(k, '<fehlt>'), aus)
    else:
        if len(a) != len(b):
            aus.append((pfad + '.Anzahl', len(a), len(b)))
        for i, (x, y) in enumerate(zip(a, b)):
            vergleiche(f'{pfad}[{i}]', x, y, aus)


def main():
    ref = sys.argv[sys.argv.index('--gegen') + 1] if '--gegen' in sys.argv else REFERENZ
    sprache = sys.argv[sys.argv.index('--sprache') + 1] if '--sprache' in sys.argv else 'de'
    os.makedirs(ERGEBNISSE, exist_ok=True)
    alt_dir = git_stand(ref)
    try:
        alt = lauf(alt_dir, sprache)
    finally:
        shutil.rmtree(alt_dir, ignore_errors=True)
    neu = lauf(REPO, sprache)
    for name, r in ((f'referenz-{ref.replace("/", "_")}-{sprache}', alt), (f'aktuell-{sprache}', neu)):
        with open(os.path.join(ERGEBNISSE, f'daten-{name}.json'), 'w', encoding='utf-8') as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
    if neu['jsFehler']:
        print('JS-Fehler im aktuellen Stand:'); [print('  ', f) for f in neu['jsFehler']]
    alt.pop('jsFehler', None); neu.pop('jsFehler', None)
    alle = []
    vergleiche('', alt, neu, alle)
    gewollte = [u for u in alle if gewollt(*u)]
    unterschiede = [u for u in alle if not gewollt(*u)]
    for p, x, y in gewollte:
        print('gewollt    ', p, ':', repr(x)[:80], '->', repr(y)[:80])
    for p, x, y in unterschiede[:30]:
        print('UNTERSCHIED', p, '\n   Referenz:', str(x)[:200], '\n   aktuell :', str(y)[:200])
    print(f"Daten-Test gegen {ref} ({sprache}): {len(neu['downloads'])} Downloads, {len(neu['statistik'] or {})} Schiris in der Statistik, "
          f"{len(unterschiede)} Unterschiede" + (f", {len(gewollte)} gewollte Abweichungen" if gewollte else ''))
    sys.exit(1 if unterschiede else 0)


if __name__ == '__main__':
    main()
