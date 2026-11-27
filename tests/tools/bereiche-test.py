"""Bereiche-Test (Etappe 2.9b): Findet VoiceOver jede Karte als benannten Bereich?

Liest den Bedienungshilfen-Baum des Browsers (das, was ein Screenreader sieht) und prüft:
- jede Karte (Score, Profil, Bereit zum Sichern?, Gespann-Durchschnitt, Profil des Gespanns,
  Gespann-Beobachtungen, Bewertungen laden) ist ein Bereich (region) mit ihrem Titel als Namen
- auch auf dem iPad hochkant, wo die rechte Spalte per display: contents aufgelöst wird
- Deutsch und Englisch (Name folgt der Sprache)
Dazu Kontrast der Platzhalter: jedes Text- und Notizfeld mit Platzhalter (Bewertung, Gespann, Szene-Fenster, Fenster
„Spiel bearbeiten“, auch die nur bei Bedarf sichtbaren Felder „anderer Name“) hell und dunkel mind. 4.5:1 gegen den
tatsächlichen Hintergrund des Feldes, alle in derselben Farbe; kein Platzhalter bleibt ungeprüft.
Hinweis: Der Test läuft in Chrome; VoiceOver in Safari kann in Einzelheiten abweichen (von Hand prüfen).
Aufruf: python3 tests/tools/bereiche-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER, fuehre_aus, pruefliste  # noqa: E402

BREITEN = [(834, 1194, 'iPad hochkant'), (1080, 810, 'iPad quer 1080'), (1194, 834, 'iPad quer')]
# Ansicht -> erwartete Bereiche (i18n-Schlüssel des Titels)
ANSICHTEN = {
    'Bewertung': ('selectRefTab(0)', ['txt_weighted_for', 'radar_title', 'ready_title']),
    'Gespann': ('selectSummaryTab()', ['crew_title', 'crew_radar_title', 'sec_crew_obs']),
    'Statistik': ('selectStatsTab()', ['stats_load_title']),
}


def bereiche(b):
    """Alle Bereiche (role region) im Bedienungshilfen-Baum: [Name, …] (nur nicht ausgeblendete)."""
    b.befehl('Accessibility.enable')
    knoten = b.befehl('Accessibility.getFullAXTree')['nodes']
    return [n.get('name', {}).get('value', '') for n in knoten
            if not n.get('ignored') and n.get('role', {}).get('value') == 'region']


# Kontrast aller sichtbaren Platzhalter gegen den Hintergrund (durchscheinende Ebenen eingerechnet)
PLATZHALTER_JS = r"""(() => {
  const rgba = (c) => { const m = c.match(/[\d.]+/g).map(Number); return [m[0], m[1], m[2], m.length > 3 ? m[3] : 1]; };
  const lum = ([r, g, b]) => { const f = (v) => { v /= 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }; return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b); };
  const misch = (o, u) => [0, 1, 2].map((i) => o[i] * o[3] + u[i] * (1 - o[3]));
  const grund = (e) => { const ebenen = []; for (let x = e; x; x = x.parentElement) { const c = rgba(getComputedStyle(x).backgroundColor); if (c[3] > 0) { ebenen.push(c); if (c[3] >= 1) break; } }
    let farbe = [255, 255, 255]; if (ebenen.length && ebenen[ebenen.length - 1][3] >= 1) farbe = ebenen.pop().slice(0, 3);
    for (let i = ebenen.length - 1; i >= 0; i--) farbe = misch(ebenen[i], farbe); return farbe; };
  return [...document.querySelectorAll('input[placeholder], textarea[placeholder]')].filter((e) => e.placeholder && e.offsetParent !== null).map((e) => {
    const s = getComputedStyle(e, '::placeholder'), g = grund(e);
    const p = misch(rgba(s.color).map((v, i) => (i === 3 ? v * Number(s.opacity || 1) : v)), g);
    const [a, b] = [lum(p), lum(g)].sort((x, y) => y - x);
    return { id: e.id, farbe: s.color, kontrast: Math.round((a + 0.05) / (b + 0.05) * 100) / 100 };
  });
})()"""
ALLE_PLATZHALTER = "[...document.querySelectorAll('input[placeholder], textarea[placeholder]')].filter((e) => e.placeholder).map((e) => e.id)"


def platzhalter(b, basis, fehler):
    """Platzhalter-Kontrast hell und dunkel in allen Ansichten und Fenstern (Felder „anderer Name“ eingeblendet)."""
    for schema in ('light', 'dark'):
        b.fenster(1194, 834, farbschema=schema)
        daten_setzen(b, basis)
        b.oeffnen(basis + '/index.html')
        gemessen = {}
        def messen():
            for x in b.js(PLATZHALTER_JS):
                gemessen[x['id']] = x
        b.js("selectRefTab(0); document.getElementById('current_schiri_name_custom').hidden = false")
        messen()
        b.js('selectSummaryTab()'); messen(); b.js('selectRefTab(0)')
        b.js('oeffneSzene(1)'); messen(); b.taste('Escape')
        b.js("oeffneSpielDialog(); document.querySelectorAll('#sfRollen input').forEach((e) => { e.hidden = false; })")
        messen()
        ungeprueft = sorted(set(b.js(ALLE_PLATZHALTER)) - set(gemessen))
        if ungeprueft:
            fehler.append(f'{schema}: Platzhalter ungeprüft: {ungeprueft}')
        schwach = [(x['id'], x['kontrast']) for x in gemessen.values() if x['kontrast'] < 4.5]
        if schwach:
            fehler.append(f'{schema}: Platzhalter unter 4.5:1: {schwach}')
        farben = sorted({x['farbe'] for x in gemessen.values()})
        if len(farben) != 1:
            fehler.append(f'{schema}: Platzhalter in verschiedenen Farben: {farben}')
        b.taste('Escape')
    return len(gemessen)


def main():
    fehler = pruefliste()
    anzahl = 0
    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            for sprache in ('de', 'en'):
                for w, h, gname in BREITEN:
                    b.fenster(w, h)
                    daten_setzen(b, srv.basis, sprache=sprache)
                    b.oeffnen(srv.basis + '/index.html')
                    for aname, (aktion, schluessel) in ANSICHTEN.items():
                        b.js(aktion)
                        da = bereiche(b)
                        for k in schluessel:
                            titel = b.js(f"t({k!r})")
                            if not any(n.startswith(titel) for n in da):
                                fehler.append(f'{sprache} {gname} {aname}: Bereich „{titel}“ fehlt (gefunden: {da})')
                        # nur Bereiche der sichtbaren Ansicht (ausgeblendete Ansichten nicht im Baum)
                        fremd = [n for n in da if not any(n.startswith(b.js(f"t({k!r})")) for k in schluessel)]
                        if fremd:
                            fehler.append(f'{sprache} {gname} {aname}: Bereiche aus anderen Ansichten im Baum: {fremd}')
                    # Score-Karte nennt den Schiedsrichter
                    b.js('selectRefTab(0)')
                    rolle = b.js("rolle(SYSTEM_CONFIGS[currentSystem][0])")
                    if not any(rolle in n for n in bereiche(b)):
                        fehler.append(f'{sprache} {gname}: Score-Bereich nennt die Rolle „{rolle}“ nicht')
            anzahl = platzhalter(b, srv.basis, fehler)
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Bereiche-Test: {len(fehler)} Fehler (jede Karte ein benannter Bereich, 3 Breiten × 3 Ansichten × DE/EN; '
          f'Platzhalter-Kontrast: {anzahl} Felder hell und dunkel)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    fuehre_aus(main)   # nach Verbindungsabbruch zu Chrome einmal von vorne (werkzeug.py)
