"""Kunstsprache-Test (Etappe 2.9b): Läuft jeder sichtbare Text über t()?

Der Test erzeugt im Browser eine Kunstsprache „xx“: jeder deutsche Text wird zu ⟦Text⟧ (gespeicherte Werte `val`
bleiben unverändert). Danach sucht er in allen Ansichten, Fenstern und Menüs Texte, Platzhalter, aria-label, title und
alt, die nicht in ⟦…⟧ stehen – das sind fest eingebaute Texte, die an t() vorbeigehen.
Ausgenommen sind Daten (Namen aus Kader und Spiel, Vereinsangaben, Ligen, Zahlen).

Die Kunstsprache gibt es nur hier im Test: Sie steht nie in SPRACHEN (also nie in der Sprachwahl) und wird nie
gespeichert. Der Test prüft beides.
Aufruf: python3 tests/tools/kunstsprache-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

# Kunstsprache anlegen und einschalten, ohne die Sprachwahl zu speichern
EIN = r"""(() => {
  const um = (w, k) => typeof w === 'string' ? '⟦' + w + '⟧'
    : Array.isArray(w) ? w.map((x) => um(x))
    : (w && typeof w === 'object') ? Object.fromEntries(Object.entries(w).map(([kk, v]) => [kk, kk === 'val' ? v : um(v, kk)]))
    : w;
  I18N.xx = Object.fromEntries(Object.entries(I18N.de).map(([k, v]) => [k, um(v)]));
  SYSTEM_CONFIGS && Object.values(SYSTEM_CONFIGS).flat().forEach((r) => { r.role_xx = '⟦' + r.role_de + '⟧'; });
  const orig = Storage.prototype.setItem;
  Storage.prototype.setItem = function (k, v) { if (k === LANG_KEY) return; return orig.call(this, k, v); };
  try { setLanguage('xx'); } finally { Storage.prototype.setItem = orig; }
  return currentLang;
})()"""

# Alle Texte und Attribute einsammeln (auch in ausgeblendeten Teilen)
SAMMELN = r"""(() => {
  const pfad = (e) => { const t = []; while (e && e.nodeType === 1 && t.length < 4) { t.unshift(e.id ? '#' + e.id : e.tagName.toLowerCase() + (e.className && typeof e.className === 'string' ? '.' + e.className.split(' ')[0] : '')); if (e.id) break; e = e.parentElement; } return t.join(' > '); };
  const aus = [];
  const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  let n;
  while ((n = w.nextNode())) {
    const p = n.parentElement;
    if (!p || p.closest('script, style, #sprache')) continue;   // Sprachnamen stehen in ihrer eigenen Sprache
    const s = n.textContent.trim();
    if (s) aus.push([pfad(p), s]);
  }
  document.querySelectorAll('[placeholder], [aria-label], [title], img[alt], optgroup[label]').forEach((e) => {
    ['placeholder', 'aria-label', 'title', 'alt', 'label'].forEach((a) => {
      if (a === 'label' && e.tagName !== 'OPTGROUP') return;
      const v = (e.getAttribute(a) || '').trim();
      if (v) aus.push([pfad(e) + ' @' + a, v]);
    });
  });
  aus.push(['<title>', document.title]);
  return aus;
})()"""

# Daten, die keine Oberflächentexte sind
DATEN = r"""(() => {
  const s = new Set();
  const sammle = (x) => { if (typeof x === 'string') s.add(x.trim()); else if (x && typeof x === 'object') Object.values(x).forEach(sammle); };
  sammle(gameData); sammle(KADER); sammle(CLUB);
  if (typeof letzteStatistik !== 'undefined') sammle(letzteStatistik);
  document.querySelectorAll('#spiel_liga option').forEach((o) => s.add(o.textContent.trim()));
  document.querySelectorAll('textarea, input').forEach((e) => s.add((e.value || '').trim()));
  // Teile davon: Nachnamen (Reiter „H1 · Meier“), Szenen-Texte und Zeilen aus Notizen
  [...s].forEach((x) => x.split(/[\n\[\]]| · /).forEach((y) => s.add(y.trim())));
  const namen = [...KADER, ...Object.values(gameData.referees || {}).map((r) => r && r.name || '')];
  namen.forEach((n) => n.split(' ').forEach((y) => s.add(y.trim())));
  return [...s].filter((x) => x.length > 1).sort((a, b) => b.length - a.length);
})()"""


def offen(text, daten):
    """Rest nach Entfernen von ⟦…⟧ und Daten: enthält er noch Wörter, ist er ein fester Text."""
    rest = re.sub(r'⟦[^⟦⟧]*⟧', ' ', text)
    rest = re.sub(r'⟦[^⟦⟧]*⟧', ' ', rest)   # verschachtelt (Text mit eingesetztem Text)
    for d in daten:
        if d in rest:
            rest = rest.replace(d, ' ')
    rest = re.sub(r'\b(R1|R2|NA|N/A|PDF|CSV|JSON|mm:ss)\b', ' ', rest)   # Kürzel und Formate, in allen Sprachen gleich
    return re.findall(r'[A-Za-zÄÖÜäöüéèàç]{2,}', rest)


def main():
    fehler = []
    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            b.fenster(1194, 834)
            daten_setzen(b, srv.basis, sprache='en')
            b.oeffnen(srv.basis + '/index.html')
            if b.js(EIN) != 'xx':
                fehler.append('Kunstsprache liess sich nicht einschalten')
            funde = {}

            def pruefe(zustand):
                daten = b.js(DATEN)
                for ort, text in b.js(SAMMELN):
                    woerter = offen(text, daten)
                    if woerter:
                        funde.setdefault((ort, text), zustand)

            # Ansichten und Fenster nacheinander
            pruefe('Bewertung Head')
            b.js('selectRefTab(2)'); pruefe('Bewertung Linesperson')
            b.js('selectRefTab(0)')
            b.klick('#btnMehr'); pruefe('Menü Mehr'); b.taste('Escape')
            b.js('oeffneSpielDialog()'); pruefe('Spiel bearbeiten'); b.js('spielAbbrechen()')
            b.klick('.szene-knopf[data-szene="1"]'); pruefe('Szene neu'); b.taste('Escape')
            b.js('selectSummaryTab()'); pruefe('Gespann')
            b.js("""(async () => { selectStatsTab();
              const n = ['beispiel-v1.0.json','beispiel-v1.1.json','beispiel-v1.1-mit-na.json','beispiel-spiel.json'];
              const f = await Promise.all(n.map(async (x) => new File([await (await fetch('/tests/fixtures/' + x)).text()], x)));
              await handleSeasonFilesUpload({ target: { files: f, value: '' } }); })()""")
            pruefe('Statistik')
            b.js('selectRefTab(0)')
            b.js("mehrAktion(resetAll)"); pruefe('Fenster Zurücksetzen'); b.taste('Escape')
            b.fenster(834, 1194); pruefe('iPad hochkant')
            b.fenster(794, 1123, druck=True); pruefe('Druck')

            for (ort, text), zustand in sorted(funde.items(), key=lambda x: x[1]):
                fehler.append(f'{zustand}: {ort}: „{text[:90]}“')

            # Kunstsprache nie in der Sprachwahl, nie gespeichert
            b.fenster(1194, 834)
            b.klick('#btnMehr')
            wahl = b.js("[...document.querySelectorAll('input[name=sprache]')].map((o) => o.value)")
            if 'xx' in wahl or b.js("SPRACHEN.some((s) => s.code === 'xx')"):
                fehler.append(f'Kunstsprache erscheint in der Sprachwahl ({wahl})')
            if b.js("localStorage.getItem('referee_lang_preference')") != 'en':
                fehler.append('Kunstsprache wurde gespeichert')
            b.oeffnen(srv.basis + '/index.html')
            if b.js('currentLang') != 'en':
                fehler.append(f"Nach Neuladen nicht wieder Englisch ({b.js('currentLang')})")
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Kunstsprache-Test: {len(fehler)} Fehler (alle Ansichten, Fenster, Menü, Druck; nie in der Sprachwahl, nie gespeichert)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
