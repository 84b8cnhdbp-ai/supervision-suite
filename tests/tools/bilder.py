"""Bilder: Bildschirmfotos aller Ansichten (iPad hochkant, iPad quer, MacBook; hell und dunkel) und Druck-PDF.

Aufruf:   python3 tests/tools/bilder.py                 (nur aktueller Stand)
          python3 tests/tools/bilder.py --gegen main    (zusätzlich Referenzstand, nebeneinander)
Ergebnis: tests/tools/ergebnisse/bilder/uebersicht.html im Browser öffnen (nicht im Repo).

Die App läuft mit dem erfundenen Beispielspiel aus tests/fixtures/.
"""
import html
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, ERGEBNISSE, Browser, server, git_stand, daten_setzen, LEER  # noqa: E402

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


def fotografieren(wurzel, ziel):
    os.makedirs(ziel, exist_ok=True)
    srv = server(wurzel, {'/__leer': LEER})
    fehler = []
    try:
        with Browser() as b:
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


def main():
    ordner = os.path.join(ERGEBNISSE, 'bilder')
    shutil.rmtree(ordner, ignore_errors=True)
    staende = []
    if '--gegen' in sys.argv:
        ref = sys.argv[sys.argv.index('--gegen') + 1]
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


if __name__ == '__main__':
    main()
