"""Wechsel-Test (vor dem Merge): Eine nicht exportierte Bewertung übersteht den Wechsel von main auf den neuen Stand.

Ablauf (ein Browser-Profil, eine Adresse – wie auf dem iPad):
1. Alter Stand (Standard: main, ?v=7): Kader-Import (echte Dateiwahl), Spieldaten, zwei Schiedsrichter mit
   Gesamteinschätzung, Kriterien (eines N/A), Coaching, Notizen mit alten Zeitangaben „[2. Drittel 8:34]“, Stärken,
   Rapport, Gespann-Notiz; Englisch und dunkel – alles über die alte Oberfläche, NICHT exportiert.
   Festgehalten: localStorage sowie Export-JSON und CSV der alten Oberfläche (nur abgefangen, nichts geändert).
2. Wechsel: dieselbe Adresse liefert jetzt den neuen Stand (Arbeitsordner). Neu laden wie beim echten Update.
3. Prüfen: neue Version vollständig (alle Dateien mit derselben ?v=, keine gemischten Versionen), localStorage bis zur
   ersten Eingabe unverändert, jedes Feld zeigt den alten Wert, alte Zeitangaben bleiben, computeRefScores gleich,
   Export-JSON/CSV gleich wie in der alten Oberfläche (nur die bekannten gewollten Abweichungen des Daten-Tests),
   Englisch und dunkel bleiben; danach offline neu laden: neue Version vollständig aus dem Cache, Daten da.
4. Rückweg (git revert + ?v= erhöhen): In der neuen Oberfläche bearbeiten und Darstellung „Auto“ wählen (gibt es nur
   neu); dann liefert die Adresse den alten Code mit höherer ?v=. Die alte Oberfläche startet ohne JS-Fehler und zeigt
   die bearbeitete Bewertung – auch mit gespeicherten Werten, die nur die neue Version kennt („auto“, „fr“).
5. Wechsel ohne erhöhte ?v=: neuer Code mit alter Nummer – die alte Version bleibt vollständig aktiv, keine gemischten
   Versionen, Badge „Update blockiert“.

Gegenprobe (von Hand, prüft den Test selbst):
  python3 tests/tools/wechsel-test.py --gegenprobe   (neuer Stand speichert unter anderem Schlüssel -> muss rot werden)
Aufruf: python3 tests/tools/wechsel-test.py [--von main]   (Abbruchcode 1 bei Fehlern)
"""
import http.server
import importlib.util
import json
import os
import re
import shutil
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, FIXTURES, Browser, git_stand  # noqa: E402

_spec = importlib.util.spec_from_file_location('daten_test', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'daten-test.py'))
_daten = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_daten)
vergleiche, gewollt = _daten.vergleiche, _daten.gewollt

ZUSTAND = {'dir': None, 'online': True}


def starte_server():
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(s, *a, **k):
            super().__init__(*a, directory=ZUSTAND['dir'], **k)

        def translate_path(s, path):
            p = path.split('?')[0]
            if p.startswith('/tests/fixtures/'):
                return os.path.join(FIXTURES, p[len('/tests/fixtures/'):])
            return super().translate_path(path)

        def do_GET(s):
            if not ZUSTAND['online']:     # offline: Verbindung ohne Antwort schliessen
                s.close_connection = True
                return
            super().do_GET()

        def end_headers(s):
            s.send_header('Cache-Control', 'no-store')
            super().end_headers()

        def log_message(s, *a):
            pass

        def handle(s):
            try:
                super().handle()
            except (BrokenPipeError, ConnectionResetError):
                pass

    class Srv(http.server.ThreadingHTTPServer):
        request_queue_size = 64
    srv = Srv(('127.0.0.1', 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    srv.basis = f'http://127.0.0.1:{srv.server_address[1]}'
    return srv


def mit_nummer(ordner, nummer):
    """Setzt in index.html alle ?v= auf `nummer`."""
    p = os.path.join(ordner, 'index.html')
    s = open(p, encoding='utf-8').read()
    open(p, 'w', encoding='utf-8').write(re.sub(r'\?v=\d+', f'?v={nummer}', s))


def kopie(quelle):
    ziel = tempfile.mkdtemp(prefix='stand-')
    shutil.copytree(quelle, ziel, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', 'ergebnisse', '__pycache__'))
    return ziel


# Fängt Downloads ab (Export-JSON, CSV), ohne etwas zu verändern
FANGEN = """window.__dl = []; window.downloadBlob = async (blob, name) => window.__dl.push({ name, text: await blob.text() });"""

# Versionsstand der geladenen Seite: alle ?v= von CSS/JS und ob es der neue Code ist
STAND = """(() => { const v = [...document.querySelectorAll('link[rel=stylesheet][href*="?v="], script[src*="?v="]')]
  .map((e) => (e.getAttribute('href') || e.getAttribute('src')).match(/[?&]v=(\\d+)/)[1]);
  return { nummern: [...new Set(v)], neu: typeof initBewegung === 'function', alt: !!document.getElementById('langToggle'),
           sw: !!(navigator.serviceWorker && navigator.serviceWorker.controller) }; })()"""


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    von = sys.argv[sys.argv.index('--von') + 1] if '--von' in sys.argv else 'main'
    alt = git_stand(von)
    neu = kopie(REPO)
    if '--gegenprobe' in sys.argv:   # neuer Stand liest/schreibt unter anderem Schlüssel: Test muss rot werden
        for f in os.listdir(os.path.join(neu, 'js')):
            p = os.path.join(neu, 'js', f)
            s = open(p, encoding='utf-8').read()
            open(p, 'w', encoding='utf-8').write(s.replace("'referee_multi_supervision_data'", "'referee_daten_neu'"))
    nr_alt = int(re.search(r'\?v=(\d+)', open(os.path.join(alt, 'index.html'), encoding='utf-8').read()).group(1))
    nr_neu = int(re.search(r'\?v=(\d+)', open(os.path.join(neu, 'index.html'), encoding='utf-8').read()).group(1))
    rueck = git_stand(von)
    mit_nummer(rueck, nr_neu + 1)          # Rückweg: alter Code mit höherer Nummer (wie git revert + ?v= erhöhen)
    blockiert = kopie(REPO)
    mit_nummer(blockiert, nr_neu + 1)      # neuer Code mit der Nummer des gerade aktiven (alten) Stands

    ZUSTAND['dir'] = alt
    srv = starte_server()
    url = srv.basis + '/index.html'

    def laden_bis(b, bedingung, versuche=6):
        """Neu laden, bis die gewünschte Version aktiv ist (wie mehrmaliges Öffnen auf dem iPad)."""
        st = None
        for _ in range(versuche):
            b.oeffnen(url, warten=1.2)
            st = b.js(STAND)
            if bedingung(st):
                return st
        return st

    def speicher(b):
        return b.js("Object.fromEntries(Object.keys(localStorage).sort().map((k) => [k, localStorage.getItem(k)]))")

    def exporte(b, reiter):
        b.js(FANGEN)
        for i in reiter:
            b.js(f'selectRefTab({i})')
            b.js('exportSingleReviewJSON()')
        b.js('exportCSV()')
        b.js('new Promise((r) => setTimeout(r, 200))')
        dl = b.js('window.__dl')
        return [{'name': d['name'], 'inhalt': json.loads(d['text']) if d['name'].endswith('.json') else d['text']} for d in dl]

    try:
        with Browser() as b:
            b.vor_laden('window.alert = () => {};')   # alte Oberfläche meldet den Kader-Import mit alert()
            b.fenster(1194, 834)

            # ---------- 1. Alte Oberfläche ausfüllen ----------
            st = laden_bis(b, lambda s: s['sw'] and s['alt'])
            pruefe(st['alt'] and st['nummern'] == [str(nr_alt)], f'Alter Stand startet nicht ({st})')
            # Kader über die echte Dateiwahl
            dok = b.befehl('DOM.getDocument')['root']['nodeId']
            knoten = b.befehl('DOM.querySelector', nodeId=dok, selector='input[type=file][accept=".json,.txt"]')['nodeId']
            b.befehl('DOM.setFileInputFiles', nodeId=knoten, files=[os.path.join(FIXTURES, 'beispiel-kader.json')])
            time.sleep(0.5)
            pruefe(b.js("JSON.parse(localStorage.getItem('referee_kader') || '[]').length") == 4, 'Alter Stand: Kader nicht importiert')

            def waehle(id_, wert=None, index=None):
                b.js(f"""(() => {{ const s = document.getElementById({id_!r});
                  {f's.value = {wert!r};' if wert is not None else f's.selectedIndex = {index};'}
                  s.dispatchEvent(new Event('change', {{ bubbles: true }})); }})()""")

            def tippe(id_, text):
                b.klick('#' + id_)
                b.tippen(text)

            waehle('spiel_liga', 'U16-Elit')
            tippe('spiel_paarung', 'Team Blau vs. Team Rot')
            tippe('spiel_id', '90003')
            b.js("(() => { const e = document.getElementById('spiel_datum'); e.value = '2026-11-07T17:30'; e.dispatchEvent(new Event('input', { bubbles: true })); })()")
            tippe('spiel_ort', 'Beispielhalle')
            tippe('supervisor_name', 'Muster Peter')

            def schiri(reiter, name, note, perf, coach, szene):
                b.klick(f'#tabsContainer .tab-btn:nth-child({reiter + 1})')
                waehle('current_schiri_name', name)
                b.klick(f'input[name=overall_grade][value="{note}"]')
                for i, idx in enumerate(perf, 1):
                    waehle(f'perf_{i}', index=idx)
                for id_, idx in zip(('coach_trend', 'coach_attitude', 'coach_feedback'), coach):
                    waehle(id_, index=idx)
                tippe('note_1', szene)
                tippe('note_4', 'Freie Notiz ohne Zeit')
                tippe('top_strengths', '1. Beispiel Stärke')
                tippe('top_workon', '1. Beispiel Schwerpunkt')
                tippe('general_report', 'Erfundener Rapport.')

            schiri(0, 'Frei Lea', '80', [0, 1, 4, 2, 1, 0, 3], [0, 1, 0], '[2. Drittel 8:34] Erfundene Szene')
            schiri(2, 'Brunner Jan', '50', [1, 1, 2, 1, 4, 1, 1], [3, 2, 2], '[P1 05:12] Andere Szene')
            b.klick('#tabsContainer .tab-summary')
            tippe('crew_notes', 'Erfundene Gespann-Notiz.')
            b.klick('#langToggle')
            b.klick('#themeToggle')
            b.klick('#tabsContainer .tab-btn:nth-child(1)')
            pruefe(b.js("localStorage.getItem('referee_lang_preference')") == 'en' and b.js("localStorage.getItem('referee_theme_preference')") == 'dark',
                   'Alter Stand: Englisch/dunkel nicht gespeichert')
            vorher = speicher(b)
            daten_alt = json.loads(vorher['referee_multi_supervision_data'])
            pruefe(daten_alt['referees'].get('4-Man_h1', {}).get('name') == 'Frei Lea', 'Alter Stand: Bewertung nicht gespeichert')
            scores_alt = b.js("Object.fromEntries(Object.entries(gameData.referees).map(([k, d]) => { const s = computeRefScores(d); delete s.radar; return [k, s]; }))")
            export_alt = exporte(b, [0, 2])
            # Die alte Oberfläche führt den Gespann-Partner erst beim Anzeigen eines Reiters nach (altes Verhalten).
            # Sonst darf das Durchgehen der Reiter nichts ändern; danach gilt dieser Stand als „vorher“.
            d = []
            vergleiche('', json.loads(vorher['referee_multi_supervision_data']), json.loads(speicher(b)['referee_multi_supervision_data']), d)
            pruefe(all(p.endswith('.partner') for p, _, _ in d), f'Alter Stand: Reiter anzeigen ändert mehr als den Partner: {d[:4]}')
            vorher = speicher(b)
            daten_alt = json.loads(vorher['referee_multi_supervision_data'])
            alt_fehler = [f for f in b.fehler if 'Update nicht möglich' not in f]
            pruefe(not alt_fehler, f'JS-Fehler im alten Stand: {alt_fehler}')

            # ---------- 2./3. Wechsel auf den neuen Stand ----------
            b.fehler = []
            ZUSTAND['dir'] = neu
            st = laden_bis(b, lambda s: s['neu'])
            pruefe(st['neu'] and st['nummern'] == [str(nr_neu)], f'Neuer Stand nicht vollständig aktiv ({st})')
            pruefe(speicher(b) == vorher, 'Neuer Stand: localStorage beim Start verändert ' +
                   str([k for k in set(vorher) | set(speicher(b)) if vorher.get(k) != speicher(b).get(k)]))
            pruefe(b.js('currentLang') == 'en', 'Neuer Stand: Englisch nicht übernommen')
            pruefe(b.js("document.documentElement.dataset.theme || ''") == 'dark', f"Neuer Stand: dunkel nicht übernommen ({b.js('document.documentElement.dataset.theme')})")
            # Felder zeigen die alten Werte
            for i, key in ((0, '4-Man_h1'), (2, '4-Man_l1')):
                d = daten_alt['referees'][key]
                b.js(f'selectRefTab({i})')
                ist = b.js("""({ name: getEffectiveRefName(), note: (document.querySelector('input[name=overall_grade]:checked') || {}).value || '',
                  perf: [1,2,3,4,5,6,7].map((k) => segWert('perf_' + k)), trend: segWert('coach_trend'), att: segWert('coach_attitude'), feed: segWert('coach_feedback'),
                  notes: [1,2,3,4,5,6,7].map((k) => document.getElementById('note_' + k).value),
                  st: document.getElementById('top_strengths').value, wo: document.getElementById('top_workon').value, rap: document.getElementById('general_report').value,
                  chips: [...document.querySelectorAll('#szenen_1 .szene-chip')].map((c) => c.innerText.replace(/\\s+/g, ' ').trim()) })""")
                soll_perf = [d.get(f'perf_{k}') for k in range(1, 8)]
                pruefe(ist['name'] == d['name'] and ist['note'] == d.get('overall_grade'), f'{key}: Name/Note {ist["name"]}/{ist["note"]}')
                pruefe(ist['perf'] == soll_perf, f'{key}: Kriterien {ist["perf"]} statt {soll_perf}')
                pruefe([ist['trend'], ist['att'], ist['feed']] == [d.get('coach_trend'), d.get('coach_attitude'), d.get('coach_feedback')], f'{key}: Coaching')
                pruefe(ist['notes'] == [d.get(f'note_{k}', '') for k in range(1, 8)], f'{key}: Notizen verändert ({ist["notes"][:1]})')
                pruefe([ist['st'], ist['wo'], ist['rap']] == [d.get('top_strengths'), d.get('top_workon'), d.get('general_report')], f'{key}: Rapport-Felder')
                pruefe(len(ist['chips']) == 1, f'{key}: alte Szene nicht als Chip angezeigt ({ist["chips"]})')
            b.js('selectSummaryTab()')
            pruefe(b.js("document.getElementById('crew_notes').value") == 'Erfundene Gespann-Notiz.', 'Gespann-Notiz fehlt')
            b.js('selectRefTab(0)')
            pruefe(speicher(b) == vorher, 'Neuer Stand: Anzeigen der Reiter hat Daten verändert')
            scores_neu = b.js("Object.fromEntries(Object.entries(gameData.referees).map(([k, d]) => { const s = computeRefScores(d); delete s.radar; return [k, s]; }))")
            pruefe(scores_neu == scores_alt, f'Scores weichen ab: {scores_alt} / {scores_neu}')
            export_neu = exporte(b, [0, 2])
            unterschiede = []
            vergleiche('', export_alt, export_neu, unterschiede)
            echt = [u for u in unterschiede if not gewollt(*u) and not u[0].endswith('.exportiertAm')]   # Zeitpunkt des Exports
            pruefe(not echt, f'Export weicht ab: {echt[:4]}')
            # offline neu laden
            ZUSTAND['online'] = False
            b.oeffnen(url, warten=1.5)
            st = b.js(STAND)
            pruefe(st['neu'] and st['nummern'] == [str(nr_neu)] and b.js("getEffectiveRefName()") == 'Frei Lea', f'Offline: neue Version nicht vollständig aus dem Cache ({st})')
            ZUSTAND['online'] = True
            neu_fehler = [f for f in b.fehler if 'Update nicht möglich' not in f and 'Failed to fetch' not in f and 'ERR_' not in f]
            pruefe(not neu_fehler, f'JS-Fehler im neuen Stand: {neu_fehler}')

            # ---------- 4. Rückweg ----------
            b.oeffnen(url, warten=1.2)
            b.klick(f"label[for=\"{b.js("document.querySelector('input[name=overall_grade][value=\"100\"]').id")}\"]")
            b.klick('#top_strengths')
            b.tippen(' – neu bearbeitet')
            b.klick('#btnMehr')
            b.klick(f"label[for=\"{b.js("document.querySelector('input[name=darstellung][value=auto]').id")}\"]")
            b.taste('Escape')
            pruefe(b.js("localStorage.getItem('referee_theme_preference')") in (None, 'auto'), 'Darstellung „Auto“ nicht gewählt')
            nach_neu = json.loads(b.js("localStorage.getItem('referee_multi_supervision_data')"))
            h1 = nach_neu['referees']['4-Man_h1']
            pruefe(h1['overall_grade'] == '100' and h1['top_strengths'].endswith('neu bearbeitet'), f'Neuer Stand: Bearbeitung nicht gespeichert ({h1["overall_grade"]})')
            b.fehler = []
            ZUSTAND['dir'] = rueck
            st = laden_bis(b, lambda s: s['alt'] and s['nummern'] == [str(nr_neu + 1)])
            pruefe(st['alt'] and st['nummern'] == [str(nr_neu + 1)], f'Rückweg: alter Code nicht vollständig aktiv ({st})')
            for bezeichnung, extra in (('nach „Auto“', None), ('mit gespeicherten Werten „auto“ und „fr“', {'referee_theme_preference': 'auto', 'referee_lang_preference': 'fr'})):
                if extra:   # Werte, die nur die neue Version kennt, direkt im Speicher – alte Oberfläche neu starten
                    b.js(';'.join(f"localStorage.setItem({k!r}, {v!r})" for k, v in extra.items()))
                    b.fehler = []
                    b.oeffnen(url, warten=1.2)
                rf = [f for f in b.fehler if 'Update nicht möglich' not in f]
                pruefe(not rf, f'Rückweg {bezeichnung}: JS-Fehler {rf}')
                b.js('selectRefTab(0)')
                ist = b.js("""({ name: document.getElementById('current_schiri_name').value,
                  note: (document.querySelector('input[name=overall_grade]:checked') || {}).value,
                  st: document.getElementById('top_strengths').value, n1: document.getElementById('note_1').value,
                  start: typeof gameData === 'object' && !!document.getElementById('tabsContainer').children.length })""")
                pruefe(ist['start'] and ist['name'] == 'Frei Lea' and ist['note'] == '100' and ist['st'] == h1['top_strengths'] and ist['n1'] == h1['note_1'],
                       f'Rückweg {bezeichnung}: Bewertung nicht angezeigt ({ist})')

            # ---------- 5. Wechsel ohne erhöhte Nummer ----------
            b.fehler = []
            ZUSTAND['dir'] = blockiert
            st = None
            for _ in range(4):
                b.oeffnen(url, warten=1.5)
                st = b.js(STAND)
            badge = b.js("document.getElementById('pwaBadge').innerText")
            pruefe(st['alt'] and not st['neu'] and st['nummern'] == [str(nr_neu + 1)], f'Ohne Erhöhung: alte Version nicht unverändert aktiv ({st})')
            pruefe('blockiert' in badge, f'Ohne Erhöhung: Badge zeigt „{badge}“ statt „Update blockiert“')
    finally:
        srv.shutdown()
        for d in (alt, neu, rueck, blockiert):
            shutil.rmtree(d, ignore_errors=True)
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Wechsel-Test: {len(fehler)} Fehler ({von} → neu: Daten, Felder, Scores, Export, Einstellungen, offline; '
          f'Rückweg mit „auto“/„fr“; ohne Erhöhung blockiert)' + (' [Gegenprobe]' if '--gegenprobe' in sys.argv else ''))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
