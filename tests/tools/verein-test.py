"""Vereins-Test: Startet die App mit einem erfundenen Verein (js/club.js ersetzt) und prüft, dass nirgends
mehr „EVZ“ oder „EV Zug“ erscheint – in keiner Ansicht, keiner Sprache, nicht im Druck, nicht in Meldungen
und nicht in Exporten. Prüft auch, dass der erfundene Verein wirklich angezeigt und exportiert wird und dass
sein Logo offline im Cache liegt.

Aufruf: python3 tests/tools/verein-test.py      Abbruchcode 1 bei Fehlern.
"""
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

TESTVEREIN = {'name': 'HC Musterdorf', 'kurz': 'HCM', 'logo': 'logo-test.svg',
              'halle': 'Musterhalle', 'exportName': 'HC Musterdorf'}
VERBOTEN = re.compile(r'evz|ev\s*zug|bossard', re.I)
LOGO = b'<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48"><circle cx="24" cy="24" r="22" fill="#888"/></svg>'

ANSICHTEN = {
    'head-referee': 'selectRefTab(0)',
    'linesperson': 'selectRefTab(2)',
    'gespann': 'selectSummaryTab()',
    'statistik': """(async () => { selectStatsTab();
        const n = ['beispiel-v1.0.json','beispiel-v1.1.json','beispiel-v1.1-mit-na.json','beispiel-spiel.json'];
        const files = await Promise.all(n.map(async (x) => new File([await (await fetch('/tests/fixtures/' + x)).text()], x)));
        await handleSeasonFilesUpload({ target: { files, value: '' } }); })()""",
}

# Alles Sichtbare und Vorlesbare einsammeln: Text, Titel, Optionen, Platzhalter, Beschriftungen, Meldungen
SAMMELN = r"""(() => {
  const teile = [document.title, document.body.innerText];
  document.querySelectorAll('*').forEach((el) => {
    for (const a of ['placeholder', 'alt', 'title', 'aria-label']) if (el.getAttribute(a)) teile.push(el.getAttribute(a));
  });
  document.querySelectorAll('option, optgroup').forEach((o) => teile.push(o.label || o.textContent));
  return teile.join('\n');
})()"""


def testkopie():
    ziel = tempfile.mkdtemp(prefix='verein-')
    for name in ('index.html', 'sw.js', 'manifest.json'):
        shutil.copy(os.path.join(REPO, name), ziel)
    for ordner in ('css', 'js', 'icons'):
        shutil.copytree(os.path.join(REPO, ordner), os.path.join(ziel, ordner))
    with open(os.path.join(ziel, TESTVEREIN['logo']), 'wb') as f:
        f.write(LOGO)
    p = os.path.join(ziel, 'js', 'club.js')
    s = open(p, encoding='utf-8').read()
    for k, v in TESTVEREIN.items():
        s, n = re.subn(rf"(\b{k}:\s*)'[^']*'", rf"\g<1>'{v}'", s, count=1)
        assert n == 1, f'club.js: Feld {k} nicht gefunden'
    open(p, 'w', encoding='utf-8').write(s)
    return ziel


def main():
    fehler = []
    wurzel = testkopie()
    srv = server(wurzel, {'/__leer': LEER})
    try:
        with Browser() as b:
            for sprache in ('de', 'en'):
                for druck in (False, True):
                    for ansicht, aktion in ANSICHTEN.items():
                        b.fenster(1194, 834, druck=druck)
                        daten_setzen(b, srv.basis, sprache=sprache)
                        b.oeffnen(srv.basis + '/index.html')
                        b.js("window.__meldungen = []; window.alert = (m) => __meldungen.push(m); "
                             "window.confirm = (m) => (__meldungen.push(m), false); window.prompt = (m) => (__meldungen.push(m), null);")
                        b.js(aktion)
                        text = b.js(SAMMELN)
                        ort = f'{ansicht}/{sprache}' + ('/Druck' if druck else '')
                        for m in sorted(set(VERBOTEN.findall(text))):
                            zeile = next(z for z in text.splitlines() if m in z)
                            fehler.append(f'{ort}: "{m}" gefunden in: {zeile.strip()[:100]}')
                        if not druck and ansicht == 'head-referee':
                            if TESTVEREIN['name'] not in b.js('document.title'):
                                fehler.append(f'{ort}: Fenstertitel ohne Testverein: {b.js("document.title")}')
                            if TESTVEREIN['kurz'] not in text:
                                fehler.append(f'{ort}: Kürzel des Testvereins nirgends sichtbar')
                            logo = b.js("(() => { const i = document.getElementById('clubLogo'); return i && i.complete && i.naturalWidth > 0 ? i.getAttribute('src') : null; })()")
                            if logo != TESTVEREIN['logo']:
                                fehler.append(f'{ort}: Logo des Testvereins nicht geladen ({logo})')
                            # Meldungen und Exporte
                            b.js("""window.__downloads = [];
                                    window.downloadBlob = async (blob, name) => __downloads.push(name + '\\n' + await blob.text());
                                    exportSingleReviewJSON(); exportCSV(); addTimestamp('note_1'); resetAll();
                                    selectRefTab(2); exportSingleReviewJSON();""")
                            b.js('new Promise((r) => setTimeout(r, 200))')
                            export = '\n'.join(b.js('__downloads') + b.js('__meldungen'))
                            for m in sorted(set(VERBOTEN.findall(export))):
                                fehler.append(f'{ort}: "{m}" in Export oder Meldung')
                            if f'"club": "{TESTVEREIN["exportName"]}"' not in export:
                                fehler.append(f'{ort}: Export enthält nicht "club": "{TESTVEREIN["exportName"]}"')
            # Logo offline verfügbar (Service Worker lädt js/club.js)
            for _ in range(50):
                if b.js("caches.keys().then((k) => k.length)"):
                    break
                b.js('new Promise((r) => setTimeout(r, 200))')
            b.js('new Promise((r) => setTimeout(r, 1000))')
            if not b.js(f"caches.match('/{TESTVEREIN['logo']}').then((r) => !!r)"):
                fehler.append('Logo des Testvereins liegt nicht im Offline-Cache')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
        shutil.rmtree(wurzel, ignore_errors=True)
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Vereins-Test mit „{TESTVEREIN["name"]}“: {len(fehler)} Fehler '
          f'({len(ANSICHTEN)} Ansichten × 2 Sprachen × Bildschirm/Druck, dazu Meldungen, Exporte, Offline-Logo)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
