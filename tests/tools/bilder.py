"""Bilder: Bildschirmfotos aller Ansichten (iPad hochkant, iPad quer, MacBook; hell und dunkel) und Druck-PDF.

Aufruf:   python3 tests/tools/bilder.py                 (nur aktueller Stand)
          python3 tests/tools/bilder.py --gegen         (zusätzlich alter Stand, Tag stand-etappe-1, nebeneinander)
          python3 tests/tools/bilder.py --gegen main    (anderer Referenzstand)
          python3 tests/tools/bilder.py --gegen HEAD --pixel   (dazu Pixelvergleich: listet jedes Bild, das sich
                                                         auch nur in einem Pixel unterscheidet; Abbruchcode 1)
          Statt eines Git-Stands geht auch ein Ordner mit einer Kopie der App (--gegen /pfad/zur/kopie).
Ergebnis: tests/tools/ergebnisse/bilder/uebersicht.html im Browser öffnen (nicht im Repo).

Die App läuft mit dem erfundenen Beispielspiel aus tests/fixtures/.
"""
import html
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, ERGEBNISSE, REFERENZ, Browser, server, git_stand, daten_setzen, LEER  # noqa: E402

GROESSEN = [('ipad-hoch-768', 768, 1024), ('ipad-hoch', 834, 1194), ('ipad-quer-1080', 1080, 810), ('ipad-quer', 1194, 834), ('macbook', 1440, 900)]
SCHEMEN = ['light', 'dark']
ANSICHTEN = [
    ('head-referee', 'selectRefTab(0)'),
    ('linesperson', 'selectRefTab(2)'),
    ('gespann', 'selectSummaryTab()'),
    ('statistik', """(async () => { selectStatsTab();
        const n = ['beispiel-v1.0.json','beispiel-v1.0-ohne-evaluation.json','beispiel-v1.1.json','beispiel-v1.1-mit-na.json','beispiel-spiel.json'];
        const files = await Promise.all(n.map(async (x) => new File([await (await fetch('/tests/fixtures/' + x)).text()], x)));
        window.alert = () => {};
        await handleSeasonFilesUpload({ target: { files, value: '' } }); })()"""),
]

# Feste Uhrzeit, damit „Gesichert 10:00“ und „gedruckt am …“ in allen Bildern gleich sind (Pixelvergleich);
# dazu ohne Übergänge
FESTE_ZEIT = """(() => { const T = new Date(2026, 10, 15, 10, 0, 0).getTime(); const D = Date;
  class F extends D { constructor(...a) { super(...(a.length ? a : [T])); } static now() { return T; } }
  window.Date = F;
  // Übergänge aus (auch in älteren Ständen ohne Rücksicht auf „Bewegung reduzieren“): Bilder nie mitten in einer Animation
  document.addEventListener('DOMContentLoaded', () => { const s = document.createElement('style');
    s.textContent = '*, *::before, *::after { transition: none !important; animation: none !important; }';
    document.head.appendChild(s); }); })()"""


def fotografieren(wurzel, ziel):
    os.makedirs(ziel, exist_ok=True)
    srv = server(wurzel, {'/__leer': LEER})
    fehler = []
    try:
        with Browser() as b:
            b.vor_laden(FESTE_ZEIT)
            for gname, w, h in GROESSEN:
                for schema in SCHEMEN:
                    for aname, aktion in ANSICHTEN:
                        b.fenster(w, h, schema)
                        # Theme: alter Stand kennt nur 'light'/'dark' als Einstellung, neuer Stand folgt dem System.
                        daten_setzen(b, srv.basis, spiel=True, theme='dark' if schema == 'dark' else None)
                        b.oeffnen(srv.basis + '/index.html')
                        b.js(aktion)
                        b.js('new Promise((r) => setTimeout(r, 300))')
                        b.bild(os.path.join(ziel, f'{aname}_{gname}_{schema}.png'))
            # Druck: als PDF und als Bild der Druckansicht (A4-Breite); auch bei Darstellung "Dunkel" muss er hell sein
            for schema in SCHEMEN:
                b.fenster(794, 1123, schema, druck=True)
                daten_setzen(b, srv.basis, spiel=True, theme='dark' if schema == 'dark' else None)
                b.oeffnen(srv.basis + '/index.html')
                b.bild(os.path.join(ziel, f'druck_a4_{schema}.png'))
            # Druck der Gespann-Übersicht
            b.fenster(794, 1123, 'light', druck=True)
            daten_setzen(b, srv.basis, spiel=True)
            b.oeffnen(srv.basis + '/index.html')
            b.js('selectSummaryTab()')
            b.bild(os.path.join(ziel, 'druck_gespann.png'))
            # Druck der Saison-Statistik
            b.fenster(794, 1123, 'light', druck=True)
            daten_setzen(b, srv.basis, spiel=True)
            b.oeffnen(srv.basis + '/index.html')
            b.js(dict(ANSICHTEN)['statistik'])
            b.js('new Promise((r) => setTimeout(r, 300))')
            b.bild(os.path.join(ziel, 'druck_statistik.png'))
            b.fenster(794, 1123, 'light', druck=True)
            daten_setzen(b, srv.basis, spiel=True)
            b.oeffnen(srv.basis + '/index.html')
            b.pdf(os.path.join(ziel, 'druck_head-referee.pdf'))
            fehler = [f for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    return fehler


def uebersicht(ordner, staende):
    zeilen = ['<!doctype html><meta charset="utf-8"><title>Bilder</title>',
              '<style>body{font:14px -apple-system,sans-serif;margin:20px;background:#eee}h2{margin-top:40px}'
              '.reihe{display:flex;gap:16px;align-items:flex-start}figure{margin:0;background:#fff;padding:8px;border-radius:8px}'
              'figcaption{font-weight:600;margin-bottom:6px}img{max-width:560px;border:1px solid #ccc;display:block}</style>',
              '<h1>Bildschirmfotos</h1><p>Druck-PDF: ' +
              ' · '.join(f'<a href="{s}/druck_head-referee.pdf">{html.escape(s)}</a>' for s in staende) + '</p>']
    for name, titel in (('druck_gespann', 'Gespann-Übersicht'), ('druck_statistik', 'Saison-Statistik')):
        zeilen.append(f'<h2>Druckansicht {titel}</h2><div class="reihe">')
        for s in staende:
            zeilen.append(f'<figure><figcaption>{html.escape(s)}</figcaption><a href="{s}/{name}.png"><img src="{s}/{name}.png" loading="lazy"></a></figure>')
        zeilen.append('</div>')
    for schema in SCHEMEN:
        datei = f'druck_a4_{schema}.png'
        zeilen.append(f'<h2>Druckansicht A4 · Darstellung {"dunkel" if schema == "dark" else "hell"}</h2><div class="reihe">')
        for s in staende:
            zeilen.append(f'<figure><figcaption>{html.escape(s)}</figcaption><a href="{s}/{datei}"><img src="{s}/{datei}" loading="lazy"></a></figure>')
        zeilen.append('</div>')
    for aname, _ in ANSICHTEN:
        for gname, w, h in GROESSEN:
            for schema in SCHEMEN:
                datei = f'{aname}_{gname}_{schema}.png'
                zeilen.append(f'<h2>{aname} · {gname} ({w}×{h}) · {"dunkel" if schema == "dark" else "hell"}</h2><div class="reihe">')
                for s in staende:
                    zeilen.append(f'<figure><figcaption>{html.escape(s)}</figcaption><a href="{s}/{datei}"><img src="{s}/{datei}" loading="lazy"></a></figure>')
                zeilen.append('</div>')
    with open(os.path.join(ordner, 'uebersicht.html'), 'w', encoding='utf-8') as f:
        f.write('\n'.join(zeilen))


PIXEL_JS = """(async (a, b) => {
  const lade = (u) => new Promise((ok, f) => { const i = new Image(); i.onload = () => ok(i); i.onerror = f; i.src = u; });
  const [x, y] = await Promise.all([lade(a), lade(b)]);
  if (x.width !== y.width || x.height !== y.height) return [-1, x.width + '×' + x.height + ' / ' + y.width + '×' + y.height];
  const daten = (i) => { const c = document.createElement('canvas'); c.width = i.width; c.height = i.height;
    const k = c.getContext('2d'); k.drawImage(i, 0, 0); return k.getImageData(0, 0, i.width, i.height).data; };
  const p = daten(x), q = daten(y);
  let n = 0;
  for (let j = 0; j < p.length; j += 4) if (p[j] !== q[j] || p[j + 1] !== q[j + 1] || p[j + 2] !== q[j + 2]) n++;
  return [n, ''];
})"""


def pixelvergleich(ordner):
    """Vergleicht jedes PNG von „referenz“ und „aktuell“. Gibt [(datei, abweichende Pixel, Hinweis)] zurück."""
    abweichend = []
    dateien = sorted(f for f in os.listdir(os.path.join(ordner, 'aktuell')) if f.endswith('.png'))
    srv = server(ordner)
    try:
        with Browser() as b:
            b.oeffnen(srv.basis + '/uebersicht.html', warten=0)
            for d in dateien:
                a, r = os.path.join(ordner, 'aktuell', d), os.path.join(ordner, 'referenz', d)
                if not os.path.exists(r):
                    abweichend.append((d, -1, 'fehlt in der Referenz'))
                    continue
                if open(a, 'rb').read() == open(r, 'rb').read():
                    continue
                n, hinweis = b.js(PIXEL_JS + f"('/referenz/{d}', '/aktuell/{d}')")
                if n:
                    abweichend.append((d, n, hinweis))
    finally:
        srv.shutdown()
    return abweichend, len(dateien)


def main():
    ordner = os.path.join(ERGEBNISSE, 'bilder')
    shutil.rmtree(ordner, ignore_errors=True)
    staende = []
    if '--gegen' in sys.argv:
        i = sys.argv.index('--gegen') + 1
        ref = sys.argv[i] if i < len(sys.argv) and not sys.argv[i].startswith('--') else REFERENZ
        if os.path.isdir(ref):   # Ordner (z. B. Kopie eines nicht committeten Stands) statt Git-Stand
            fotografieren(os.path.abspath(ref), os.path.join(ordner, 'referenz'))
        else:
            d = git_stand(ref)
            try:
                fotografieren(d, os.path.join(ordner, 'referenz'))
            finally:
                shutil.rmtree(d, ignore_errors=True)
        staende.append('referenz')
    fehler = fotografieren(REPO, os.path.join(ordner, 'aktuell'))
    staende.append('aktuell')
    uebersicht(ordner, staende)
    for f in fehler:
        print('JS-Fehler/Warnung:', f)
    n = len(GROESSEN) * len(SCHEMEN) * len(ANSICHTEN)
    print(f'{n} Bilder + 2 Druckansichten je Stand + Druck-PDF → {os.path.join(ordner, "uebersicht.html")}')
    if '--pixel' in sys.argv and 'referenz' in staende:
        abweichend, gesamt = pixelvergleich(ordner)
        for d, n, hinweis in abweichend:
            print(f'Abweichung: {d}: ' + (hinweis if n < 0 else f'{n} Pixel'))
        print(f'Pixelvergleich: {gesamt - len(abweichend)} von {gesamt} Bildern pixelgleich')
        sys.exit(1 if abweichend else 0)


if __name__ == '__main__':
    main()
