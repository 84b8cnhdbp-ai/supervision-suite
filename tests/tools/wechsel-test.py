"""Wechsel-Test: Eine nicht exportierte Bewertung übersteht den Wechsel von einem alten auf den neuen Stand.

Geräte können auf verschiedenen alten Ständen sein und springen direkt auf den neuen. Darum zwei Wege, je mit eigenem
Browser-Profil (eine Adresse – wie auf dem iPad):
- stand-etappe-2 → neu  (Stand nach Etappe 2, ?v=33; ausgefüllt über die Oberfläche von Etappe 2)
- stand-etappe-1 → neu  (Stand vor Etappe 2, ?v=7; ausgefüllt über die alte Oberfläche)

Ablauf je Weg:
1. Alter Stand: Kader-Import (echte Dateiwahl), Spieldaten, zwei Schiedsrichter mit Gesamteinschätzung, Kriterien
   (eines N/A), Coaching, Szenen (Etappe 1: alte Zeitangabe „[2. Drittel 8:34]“ im Notizfeld; Etappe 2: über das
   Szene-Fenster), freie Notiz, Stärken, Rapport, Gespann-Notiz; Englisch und dunkel – alles über die Oberfläche des
   alten Stands, NICHT exportiert. Festgehalten: localStorage sowie Export-JSON und CSV des alten Stands (nur abgefangen).
2. Wechsel: dieselbe Adresse liefert jetzt den neuen Stand (Arbeitsordner). Neu laden wie beim echten Update.
3. Prüfen: neue Version vollständig (alle Dateien mit derselben ?v=, keine gemischten Versionen), localStorage bis zur
   ersten Eingabe unverändert, jedes Feld zeigt den alten Wert, Szenen als Chips, computeRefScores gleich,
   Export-JSON/CSV gleich wie im alten Stand (nur die bekannten gewollten Abweichungen des Daten-Tests gegenüber
   Etappe 1), Englisch und dunkel bleiben; Etappe 1: ältere Daten ohne Angabe zum System bleiben 4-Mann; danach offline
   neu laden: neue Version vollständig aus dem Cache, Daten da.
4. Rückweg (git revert + ?v= erhöhen): In der neuen Oberfläche bearbeiten und Darstellung „Auto“ wählen; dann liefert
   die Adresse den alten Code mit höherer ?v=. Der alte Stand startet ohne JS-Fehler und zeigt die bearbeitete
   Bewertung – auch mit gespeicherten Werten „auto“ und „fr“.
5. Wechsel ohne erhöhte ?v=: neuer Code mit der Nummer des aktiven Stands – der bisherige Stand bleibt vollständig
   aktiv, keine gemischten Versionen, Badge „Update blockiert“. Nur wenn sich CSS/JS gegenüber dem alten Stand
   unterscheiden (sonst gibt es nichts zu blockieren; der Service Worker lässt eine geänderte index.html allein zu).

Welcher Stand aktiv ist, erkennt der Test an einer Markierung, die er nur in seinen Kopien in index.html einfügt
(<meta name="wechsel-stand">) – so auch dann, wenn sich zwei Stände äusserlich nicht unterscheiden.
Ist der Arbeitsstand noch codegleich mit dem alten Stand (gleiche ?v=, z. B. direkt nach dem Anlegen eines Branches),
erhöht der Test die Nummer nur in seiner Kopie und meldet das. Anderer Code mit gleicher oder kleinerer ?v= ist ein Fehler.

Rückweg aus dem echten Notfall-Ablauf (siehe Arbeitsplan), nur für den Weg ab stand-etappe-2:
  python3 tests/tools/wechsel-test.py --von stand-etappe-2 --rueck /pfad/zum/ergebnis

Gegenprobe (von Hand, prüft den Test selbst):
  python3 tests/tools/wechsel-test.py --gegenprobe   (neuer Stand speichert unter anderem Schlüssel -> muss rot werden)
Aufruf: python3 tests/tools/wechsel-test.py [--von stand-etappe-1]   (ohne --von: beide Wege; Abbruchcode 1 bei Fehlern)
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
from werkzeug import REPO, FIXTURES, REFERENZ, Browser, git_stand  # noqa: E402

_spec = importlib.util.spec_from_file_location('daten_test', os.path.join(os.path.dirname(os.path.abspath(__file__)), 'daten-test.py'))
_daten = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_daten)
vergleiche, gewollt = _daten.vergleiche, _daten.gewollt

# Alte Stände, von denen Geräte auf den neuen Stand wechseln können: Tag -> Oberfläche zum Ausfüllen
ALTE_STAENDE = {'stand-etappe-2': 'etappe2', 'stand-etappe-1': 'etappe1'}

ZUSTAND = {'dir': None, 'online': True}


class AbbruchFehler(Exception):
    pass


class _Fertig(Exception):
    """Lauf regulär vor Schritt 5 beendet (kein geänderter Code, nichts zu blockieren)."""


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


def nummer(ordner):
    return int(re.search(r'\?v=(\d+)', open(os.path.join(ordner, 'index.html'), encoding='utf-8').read()).group(1))


def mit_nummer(ordner, nr):
    """Setzt in index.html alle ?v= auf `nr`."""
    p = os.path.join(ordner, 'index.html')
    s = open(p, encoding='utf-8').read()
    open(p, 'w', encoding='utf-8').write(re.sub(r'\?v=\d+', f'?v={nr}', s))


def markiere(ordner, name):
    """Markierung nur in der Test-Kopie: welcher Stand liefert gerade index.html aus."""
    p = os.path.join(ordner, 'index.html')
    s = open(p, encoding='utf-8').read()
    s, n = re.subn(r'<head>', f'<head>\n<meta name="wechsel-stand" content="{name}">', s, count=1)
    assert n == 1, f'<head> nicht gefunden in {p}'
    open(p, 'w', encoding='utf-8').write(s)


def code_gleich(a, b):
    """Gleicher App-Code (index.html ohne ?v=, CSS, JS, Service Worker, Manifest)?"""
    def dateien(o):
        r = {}
        for unter in ('css', 'js'):
            for f in sorted(os.listdir(os.path.join(o, unter))):
                r[f'{unter}/{f}'] = open(os.path.join(o, unter, f), 'rb').read()
        for f in ('sw.js', 'manifest.json'):
            r[f] = open(os.path.join(o, f), 'rb').read()
        r['index.html'] = re.sub(rb'\?v=\d+', b'?v=N', open(os.path.join(o, 'index.html'), 'rb').read())
        return r
    return dateien(a) == dateien(b)


def kopie(quelle):
    ziel = tempfile.mkdtemp(prefix='stand-')
    shutil.copytree(quelle, ziel, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', 'ergebnisse', '__pycache__'))
    return ziel


# Fängt Downloads ab (Export-JSON, CSV), ohne etwas zu verändern
FANGEN = """window.__dl = []; window.downloadBlob = async (blob, name) => window.__dl.push({ name, text: await blob.text() });"""

# Versionsstand der geladenen Seite: alle ?v= von CSS/JS und die Markierung des Stands, der index.html geliefert hat
STAND = """(() => { const v = [...document.querySelectorAll('link[rel=stylesheet][href*="?v="], script[src*="?v="]')]
  .map((e) => (e.getAttribute('href') || e.getAttribute('src')).match(/[?&]v=(\\d+)/)[1]);
  const m = document.querySelector('meta[name="wechsel-stand"]');
  return { nummern: [...new Set(v)], stand: m ? m.content : null,
           sw: !!(navigator.serviceWorker && navigator.serviceWorker.controller) }; })()"""


# ---------------------------------------------------------------- Ausfüllen im alten Stand

def ausfuellen_etappe1(b):
    """Alte Oberfläche (stand-etappe-1): Dropdowns, Knöpfe Sprache/Dark Mode. 4-Mann (alter Standard)."""
    dok = b.befehl('DOM.getDocument')['root']['nodeId']
    knoten = b.befehl('DOM.querySelector', nodeId=dok, selector='input[type=file][accept=".json,.txt"]')['nodeId']
    b.befehl('DOM.setFileInputFiles', nodeId=knoten, files=[os.path.join(FIXTURES, 'beispiel-kader.json')])
    time.sleep(0.5)

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
    return [(0, '4-Man_h1', 'Frei Lea'), (2, '4-Man_l1', 'Brunner Jan')]


def ausfuellen_etappe2(b):
    """Oberfläche von Etappe 2 (stand-etappe-2): Fenster „Spiel bearbeiten“, Knopfreihen, Szene-Fenster, Menü „Mehr“.
    Neues Spiel startet mit 2-Mann (Vereins-Einstellung) und ohne Liga."""
    dok = b.befehl('DOM.getDocument')['root']['nodeId']
    knoten = b.befehl('DOM.querySelector', nodeId=dok, selector='#kaderDatei')['nodeId']
    b.befehl('DOM.setFileInputFiles', nodeId=knoten, files=[os.path.join(FIXTURES, 'beispiel-kader.json')])
    time.sleep(0.5)

    def setze(id_, wert, ereignis='change'):
        b.js(f"(() => {{ const e = document.getElementById({id_!r}); e.value = {wert!r}; e.dispatchEvent(new Event({ereignis!r}, {{ bubbles: true }})); }})()")

    def tippe(id_, text):
        b.klick('#' + id_)
        b.tippen(text)

    def knopf(name, nr):
        """n-ter Knopf (ab 1) der Knopfreihe `name` – echter Klick."""
        b.klick(f'#{name} label:nth-of-type({nr})')

    def knopf_wert(name, wert):
        b.klick(f"label[for=\"{b.js(f'document.querySelector(\"input[name={name}][value={wert}]\").id')}\"]")

    # Kader neu: Fenster „Spiel bearbeiten“ ist bei neuem Spiel offen; Namen erst nach dem Import wählbar -> neu öffnen
    if b.js("document.getElementById('spielDialog').open"):
        b.klick('#sfAbbrechen')
    b.klick('#spielTitel')
    tippe('spiel_id', '90003')
    setze('spiel_liga', 'U16-Elit')
    tippe('spiel_gegner', 'Team Rot')
    setze('spiel_datum', '2026-11-07T17:30', 'input')
    tippe('spiel_ort', 'Beispielhalle')
    tippe('supervisor_name', 'Muster Peter')
    setze('sf_name_r1', 'Frei Lea')
    setze('sf_name_r2', 'Brunner Jan')
    b.klick('#sfFertig')

    def schiri(reiter, note, perf, coach, drittel, zeit, szene):
        b.klick(f'#tabsContainer [data-reiter="{reiter}"]')
        knopf('overall_grade', note)
        for i, nr in enumerate(perf, 1):
            knopf(f'perf_{i}', nr)
        for name, nr in zip(('coach_trend', 'coach_attitude', 'coach_feedback'), coach):
            knopf(name, nr)
        b.klick('.szene-knopf[data-szene="1"]')
        knopf('szene_drittel', drittel)
        tippe('szeneZeit', zeit)
        tippe('szeneNotiz', szene)
        b.klick('#szeneOk')
        tippe('note_frei_4', 'Freie Notiz ohne Zeit')
        tippe('top_strengths', '1. Beispiel Stärke')
        tippe('top_workon', '1. Beispiel Schwerpunkt')
        tippe('general_report', 'Erfundener Rapport.')

    schiri('r1', 2, [1, 2, 5, 3, 2, 1, 4], [1, 2, 1], 2, '0834', 'Erfundene Szene')
    schiri('r2', 3, [2, 2, 3, 2, 5, 2, 2], [4, 3, 3], 1, '0512', 'Andere Szene')
    b.klick('#tabsContainer [data-reiter="gespann"]')
    tippe('crew_notes', 'Erfundene Gespann-Notiz.')
    b.klick('#btnMehr')
    knopf_wert('sprache', 'en')
    knopf_wert('darstellung', 'dark')
    b.taste('Escape')
    b.klick('#tabsContainer [data-reiter="r1"]')
    return [(0, '2-Man_r1', 'Frei Lea'), (1, '2-Man_r2', 'Brunner Jan')]


AUSFUELLEN = {'etappe1': ausfuellen_etappe1, 'etappe2': ausfuellen_etappe2}


# ---------------------------------------------------------------- ein Weg: alter Stand -> neu

def lauf(von, fehler_gesamt, rueck_ordner=None, gegenprobe=False):
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    alt = git_stand(von)
    neu = kopie(REPO)
    if gegenprobe:   # neuer Stand liest/schreibt unter anderem Schlüssel: Test muss rot werden
        for f in os.listdir(os.path.join(neu, 'js')):
            p = os.path.join(neu, 'js', f)
            s = open(p, encoding='utf-8').read()
            open(p, 'w', encoding='utf-8').write(s.replace("'referee_multi_supervision_data'", "'referee_daten_neu'"))
    nr_alt, nr_neu = nummer(alt), nummer(neu)
    hinweis = ''
    if gegenprobe and nr_neu <= nr_alt:   # wie ein korrekt freigegebener Stand mit Fehler: Nummer erhöht, Datenprüfung muss anschlagen
        nr_neu = nr_alt + 1
        mit_nummer(neu, nr_neu)
    # Schritt 5 nur, wenn sich CSS/JS unterscheiden: Der Service Worker blockiert nur geänderte CSS-/JS-Dateien unter
    # derselben Adresse; eine geänderte index.html allein darf durch (Release-Regel). Bei gleichem Code nichts zu prüfen.
    blockier_test = not code_gleich(alt, REPO)
    if nr_neu <= nr_alt:
        if code_gleich(alt, neu) and not gegenprobe:
            nr_neu = nr_alt + 1   # noch keine Änderung seit dem alten Stand: Release nur in der Kopie nachstellen
            mit_nummer(neu, nr_neu)
            hinweis = (f' (Arbeitsstand codegleich mit {von}: ?v= nur in der Test-Kopie auf {nr_neu}; '
                       f'Schritt 5 „ohne Erhöhung blockiert“ entfällt, weil es nichts zu blockieren gibt)')
        else:
            pruefe(False, f'Neuer Code mit ?v={nr_neu}, nicht über {von} (?v={nr_alt}) – Update würde blockiert')
            shutil.rmtree(alt, ignore_errors=True)
            shutil.rmtree(neu, ignore_errors=True)
            fehler_gesamt += [f'[{von}] {f}' for f in fehler]
            return hinweis
    if rueck_ordner:   # Rückweg aus einem Ordner, z. B. dem Ergebnis des Notfall-Ablaufs (Arbeitsplan)
        rueck = kopie(rueck_ordner)
    else:
        rueck = git_stand(von)
        mit_nummer(rueck, nr_neu + 1)      # Rückweg: alter Code mit höherer Nummer (wie Notfall-Ablauf: revert + ?v= erhöhen)
    nr_rueck = nummer(rueck)
    blockiert = kopie(REPO)
    mit_nummer(blockiert, nr_rueck)        # neuer Code mit der Nummer des gerade aktiven (alten) Stands
    for ordner, name in ((alt, 'alt'), (neu, 'neu'), (rueck, 'rueck'), (blockiert, 'blockiert')):
        markiere(ordner, name)

    ZUSTAND['dir'] = alt
    ZUSTAND['online'] = True
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
      try:
        with Browser() as b:
            b.vor_laden('window.alert = () => {};')   # alte Oberfläche meldet den Kader-Import mit alert()
            b.fenster(1194, 834)

            # ---------- 1. Alten Stand ausfüllen ----------
            st = laden_bis(b, lambda s: s['sw'] and s['stand'] == 'alt')
            pruefe(st['stand'] == 'alt' and st['nummern'] == [str(nr_alt)], f'Alter Stand startet nicht ({st})')
            schiris = AUSFUELLEN[ALTE_STAENDE[von]](b)
            pruefe(b.js("JSON.parse(localStorage.getItem('referee_kader') || '[]').length") == 4, 'Alter Stand: Kader nicht importiert')
            pruefe(b.js("localStorage.getItem('referee_lang_preference')") == 'en' and b.js("localStorage.getItem('referee_theme_preference')") == 'dark',
                   'Alter Stand: Englisch/dunkel nicht gespeichert')
            vorher = speicher(b)
            daten_alt = json.loads(vorher['referee_multi_supervision_data'])
            erster = schiris[0][1]
            pruefe(all(daten_alt['referees'].get(k, {}).get('name') == n for _, k, n in schiris), 'Alter Stand: Bewertung nicht gespeichert')
            scores_alt = b.js("Object.fromEntries(Object.entries(gameData.referees).map(([k, d]) => { const s = computeRefScores(d); delete s.radar; return [k, s]; }))")
            export_alt = exporte(b, [i for i, _, _ in schiris])
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
            st = laden_bis(b, lambda s: s['stand'] == 'neu')
            pruefe(st['stand'] == 'neu' and st['nummern'] == [str(nr_neu)], f'Neuer Stand nicht vollständig aktiv ({st})')
            pruefe(speicher(b) == vorher, 'Neuer Stand: localStorage beim Start verändert ' +
                   str([k for k in set(vorher) | set(speicher(b)) if vorher.get(k) != speicher(b).get(k)]))
            sys_neu = b.js('currentSystem')
            pruefe(sys_neu == daten_alt['global']['system_typ'] and b.js("Object.keys(gameData.referees || {}).length") > 0,
                   f"Neuer Stand: System {sys_neu} statt {daten_alt['global']['system_typ']} oder keine Bewertungen gelesen")
            if sys_neu != daten_alt['global']['system_typ']:
                raise AbbruchFehler('Bewertung nach dem Wechsel nicht gefunden – weitere Prüfungen nicht möglich')
            pruefe(b.js('currentLang') == 'en', 'Neuer Stand: Englisch nicht übernommen')
            pruefe(b.js("document.documentElement.dataset.theme || ''") == 'dark', f"Neuer Stand: dunkel nicht übernommen ({b.js('document.documentElement.dataset.theme')})")
            # Felder zeigen die alten Werte
            for i, key, _ in schiris:
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
                pruefe(len(ist['chips']) == 1, f'{key}: Szene nicht als Chip angezeigt ({ist["chips"]})')
            b.js('selectSummaryTab()')
            pruefe(b.js("document.getElementById('crew_notes').value") == 'Erfundene Gespann-Notiz.', 'Gespann-Notiz fehlt')
            b.js(f'selectRefTab({schiris[0][0]})')
            pruefe(speicher(b) == vorher, 'Neuer Stand: Anzeigen der Reiter hat Daten verändert')
            scores_neu = b.js("Object.fromEntries(Object.entries(gameData.referees).map(([k, d]) => { const s = computeRefScores(d); delete s.radar; return [k, s]; }))")
            pruefe(scores_neu == scores_alt, f'Scores weichen ab: {scores_alt} / {scores_neu}')
            export_neu = exporte(b, [i for i, _, _ in schiris])
            unterschiede = []
            vergleiche('', export_alt, export_neu, unterschiede)
            echt = [u for u in unterschiede if not gewollt(*u) and not u[0].endswith('.exportiertAm')]   # Zeitpunkt des Exports
            pruefe(not echt, f'Export weicht ab: {echt[:4]}')
            if ALTE_STAENDE[von] == 'etappe1':
                # Ältere Daten ohne Angabe zum System (die alte Oberfläche speichert sie erst bei einer Spielangabe):
                # weiterhin 4-Mann, Bewertung sichtbar – trotz neuem Standard für neue Spiele
                b.js("""(() => { const d = JSON.parse(localStorage.getItem('referee_multi_supervision_data'));
                  delete d.global.system_typ; localStorage.setItem('referee_multi_supervision_data', JSON.stringify(d)); })()""")
                b.oeffnen(url, warten=1.2)
                b.js('selectRefTab(0)')
                pruefe(b.js('currentSystem') == '4-Man' and b.js('getEffectiveRefName()') == 'Frei Lea',
                       f"Alte Daten ohne System: {b.js('currentSystem')}, Name {b.js('getEffectiveRefName()')!r} (Bewertung verschwunden?)")
                b.js(f"localStorage.setItem('referee_multi_supervision_data', {json.dumps(vorher['referee_multi_supervision_data'])})")
                b.oeffnen(url, warten=1.2)
            # offline neu laden
            ZUSTAND['online'] = False
            b.oeffnen(url, warten=1.5)
            st = b.js(STAND)
            pruefe(st['stand'] == 'neu' and st['nummern'] == [str(nr_neu)] and b.js("getEffectiveRefName()") == 'Frei Lea',
                   f'Offline: neue Version nicht vollständig aus dem Cache ({st})')
            ZUSTAND['online'] = True
            neu_fehler = [f for f in b.fehler if 'Update nicht möglich' not in f and 'Failed to fetch' not in f and 'ERR_' not in f]
            pruefe(not neu_fehler, f'JS-Fehler im neuen Stand: {neu_fehler}')

            # ---------- 4. Rückweg ----------
            b.oeffnen(url, warten=1.2)
            b.js(f'selectRefTab({schiris[0][0]})')
            b.klick(f"label[for=\"{b.js("document.querySelector('input[name=overall_grade][value=\"100\"]').id")}\"]")
            b.klick('#top_strengths')
            b.tippen(' – neu bearbeitet')
            b.klick('#btnMehr')
            b.klick(f"label[for=\"{b.js("document.querySelector('input[name=darstellung][value=auto]').id")}\"]")
            b.taste('Escape')
            pruefe(b.js("localStorage.getItem('referee_theme_preference')") in (None, 'auto'), 'Darstellung „Auto“ nicht gewählt')
            nach_neu = json.loads(b.js("localStorage.getItem('referee_multi_supervision_data')"))
            h1 = nach_neu['referees'][erster]
            pruefe(h1['overall_grade'] == '100' and h1['top_strengths'].endswith('neu bearbeitet'), f'Neuer Stand: Bearbeitung nicht gespeichert ({h1["overall_grade"]})')
            b.fehler = []
            ZUSTAND['dir'] = rueck
            st = laden_bis(b, lambda s: s['stand'] == 'rueck' and s['nummern'] == [str(nr_rueck)])
            pruefe(st['stand'] == 'rueck' and st['nummern'] == [str(nr_rueck)], f'Rückweg: alter Code nicht vollständig aktiv ({st})')
            for bezeichnung, extra in (('nach „Auto“', None), ('mit gespeicherten Werten „auto“ und „fr“', {'referee_theme_preference': 'auto', 'referee_lang_preference': 'fr'})):
                if extra:   # Werte, die nur neuere Versionen kennen, direkt im Speicher – alten Stand neu starten
                    b.js(';'.join(f"localStorage.setItem({k!r}, {v!r})" for k, v in extra.items()))
                    b.fehler = []
                    b.oeffnen(url, warten=1.2)
                rf = [f for f in b.fehler if 'Update nicht möglich' not in f]
                pruefe(not rf, f'Rückweg {bezeichnung}: JS-Fehler {rf}')
                b.js(f'selectRefTab({schiris[0][0]})')
                ist = b.js("""({ name: document.getElementById('current_schiri_name').value,
                  note: (document.querySelector('input[name=overall_grade]:checked') || {}).value,
                  st: document.getElementById('top_strengths').value, n1: document.getElementById('note_1').value,
                  start: typeof gameData === 'object' && !!document.getElementById('tabsContainer').children.length })""")
                pruefe(ist['start'] and ist['name'] == 'Frei Lea' and ist['note'] == '100' and ist['st'] == h1['top_strengths'] and ist['n1'] == h1['note_1'],
                       f'Rückweg {bezeichnung}: Bewertung nicht angezeigt ({ist})')

            # ---------- 5. Wechsel ohne erhöhte Nummer (nur bei geändertem CSS/JS, siehe oben) ----------
            if not blockier_test:
                raise _Fertig()
            b.fehler = []
            ZUSTAND['dir'] = blockiert
            st = None
            for _ in range(4):
                b.oeffnen(url, warten=1.5)
                st = b.js(STAND)
            badge = b.js("document.getElementById('pwaBadge').innerText")
            pruefe(st['stand'] == 'rueck' and st['nummern'] == [str(nr_rueck)], f'Ohne Erhöhung: bisheriger Stand nicht unverändert aktiv ({st})')
            pruefe('blockiert' in badge, f'Ohne Erhöhung: Badge zeigt „{badge}“ statt „Update blockiert“')
      except _Fertig:
        pass
      except (AbbruchFehler, RuntimeError, ConnectionError) as e:   # als Fehler melden, nicht abstürzen
        fehler.append(f'Abbruch: {str(e).splitlines()[0][:200]}')
    finally:
        srv.shutdown()
        for d in (alt, neu, rueck, blockiert):
            shutil.rmtree(d, ignore_errors=True)
    fehler_gesamt += [f'[{von}] {f}' for f in fehler]
    return hinweis


def main():
    gegenprobe = '--gegenprobe' in sys.argv
    if '--von' in sys.argv:
        wege = [sys.argv[sys.argv.index('--von') + 1]]
    else:
        wege = list(ALTE_STAENDE)
    for von in wege:
        if von not in ALTE_STAENDE:
            print(f'Unbekannter alter Stand {von!r} (bekannt: {", ".join(ALTE_STAENDE)})')
            sys.exit(1)
    rueck_ordner = sys.argv[sys.argv.index('--rueck') + 1] if '--rueck' in sys.argv else None
    if rueck_ordner and len(wege) != 1:
        wege = [REFERENZ]   # Rückweg aus dem Notfall-Ablauf gehört zum aktuellen Referenzstand
    fehler, hinweise = [], []
    for von in wege:
        h = lauf(von, fehler, rueck_ordner, gegenprobe)
        if h:
            hinweise.append(h)
    for h in hinweise:
        print('Hinweis:', h.strip())
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Wechsel-Test: {len(fehler)} Fehler ({", ".join(w + " → neu" for w in wege)}: Daten, Felder, Scores, Export, '
          f'Einstellungen, offline; Rückweg mit „auto“/„fr“; ohne Erhöhung blockiert)' + (' [Gegenprobe]' if gegenprobe else ''))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
