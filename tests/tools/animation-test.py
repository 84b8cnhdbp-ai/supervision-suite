"""Animations-Test (Etappe 2.9b): Übergänge – der einzige Test mit eingeschalteten Übergängen.

Alle anderen Tests laufen mit „Bewegung reduzieren“ (werkzeug.Browser), damit Bilder und Messungen nie mitten in
einer Animation entstehen. Dieser Test setzt b.bewegung = True und prüft:
- Reiterwechsel: die Ansicht blendet ein (Deckkraft, 150 ms), auch zwischen zwei Schiedsrichtern
- Score zählt beim Reiterwechsel hoch (400 ms, Zwischenwerte steigend, Endwert = berechneter Score) – Bewertung und Gespann
- beim Bearbeiten (Stufe ändern) und beim Sprachwechsel springt der Score sofort, ohne Hochzählen
- Druck mitten im Hochzählen: Score-Zahl und Ring zeigen sofort den fertigen Wert (Druckansicht und beforeprint)
- mit „Bewegung reduzieren“: kein Einblenden, kein Hochzählen, keine CSS-Übergänge
Aufruf: python3 tests/tools/animation-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

# Score-Zahl über 600 ms abtasten (alle 30 ms) – im Browser, damit die Zeitpunkte genau sind
ABTASTEN = """(async (id, aktion) => {
  const el = document.getElementById(id); const werte = [];
  eval(aktion);
  const start = performance.now();
  while (performance.now() - start < 600) { werte.push([Math.round(performance.now() - start), el.innerText]); await new Promise((r) => setTimeout(r, 30)); }
  return werte; })"""
ZIEL_REF = "(() => { const sc = computeRefScores(gameData.referees[currentSystem + '_' + SYSTEM_CONFIGS[currentSystem][activeRefIndex].id]); return sc.total === null ? '–' : sc.total + '%'; })()"
ANIMATION = """((id) => document.getElementById(id).getAnimations().map((a) => [a.animationName, a.effect.getTiming().duration]))"""


def zahl(text):
    return int(text.rstrip('%')) if text and text.rstrip('%').isdigit() else None


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    def zaehlt_hoch(werte, ziel, name):
        zahlen = [zahl(w) for _, w in werte]
        pruefe(werte[-1][1] == ziel, f'{name}: Endwert {werte[-1][1]} statt {ziel}')
        zwischen = [z for z in zahlen if z is not None and z != zahl(ziel)]
        pruefe(len(zwischen) >= 3, f'{name}: zählt nicht hoch ({[w for _, w in werte[:8]]})')
        pruefe(all(a <= b for a, b in zip([z for z in zahlen if z is not None], [z for z in zahlen if z is not None][1:])),
               f'{name}: Zwischenwerte nicht steigend')
        fertig = next((ms for ms, w in werte if w == ziel), 9999)
        pruefe(300 <= fertig <= 520, f'{name}: fertig nach {fertig} ms (erwartet etwa 400 ms)')

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            b.bewegung = True
            b.fenster(1194, 834)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            pruefe(not b.js("matchMedia('(prefers-reduced-motion: reduce)').matches"), 'Übergänge im Test nicht eingeschaltet')

            # 1. Reiterwechsel: Einblenden 150 ms und Hochzählen 400 ms
            werte = b.js(ABTASTEN + "('scoreVal', 'selectRefTab(1)')")
            zaehlt_hoch(werte, b.js(ZIEL_REF), 'Reiter H2')
            b.js('selectRefTab(0)')
            anim = b.js(ANIMATION + "('singleRefView')")
            pruefe(['einblenden', 150] in anim, f'Einblenden beim Reiterwechsel fehlt oder nicht 150 ms ({anim})')
            werte = b.js(ABTASTEN + "('crewScoreVal', 'selectSummaryTab()')")
            zaehlt_hoch(werte, b.js("document.getElementById('crewScoreVal').dataset.ziel"), 'Gespann')
            pruefe(werte[-1][1] == b.js("(() => { const r = SYSTEM_CONFIGS[currentSystem].map((x) => computeRefScores(gameData.referees[currentSystem + '_' + x.id] || getDefaultRefData()).total).filter((v) => v !== null); return Math.round(r.reduce((a, b) => a + b, 0) / r.length) + '%'; })()"),
                   'Gespann: Endwert weicht vom Durchschnitt ab')
            b.js('selectRefTab(0)')
            time.sleep(0.6)

            # 2. Bearbeiten und Sprachwechsel: sofort, ohne Hochzählen
            werte = b.js(ABTASTEN + "('scoreVal', \"document.querySelector('input[name=overall_grade][value=\\\"Gut\\\"], input[name=overall_grade]:not(:checked)').click()\")")
            pruefe(werte[0][1] == werte[-1][1] == b.js(ZIEL_REF), f'Bearbeiten: Score springt nicht sofort ({[w for _, w in werte[:5]]})')
            werte = b.js(ABTASTEN + "('scoreVal', \"setLanguage('en')\")")
            pruefe(werte[0][1] == werte[-1][1], f'Sprachwechsel: Score zählt hoch ({[w for _, w in werte[:5]]})')
            b.js("setLanguage('de')")

            # 3. Druck mitten im Hochzählen: sofort der fertige Wert (Zahl und Ring)
            for weg in ('Druckansicht', 'beforeprint'):
                b.fenster(1194, 834)
                b.js('selectRefTab(2)')
                time.sleep(0.6)
                ziel_ring = None
                b.js('selectRefTab(0)')
                time.sleep(0.08)
                mitten = b.js("document.getElementById('scoreVal').innerText")
                if weg == 'Druckansicht':
                    # Umschalten per Emulation meldet der Browser beim nächsten Bildaufbau (wie der Druck vor dem Erfassen)
                    b.fenster(794, 1123, druck=True)
                    b.js('new Promise((r) => requestAnimationFrame(() => requestAnimationFrame(r)))')
                else:   # echter Druck: beforeprint kommt vor dem Erfassen, ohne Wartezeit
                    b.js("window.dispatchEvent(new Event('beforeprint'))")
                ist = b.js("document.getElementById('scoreVal').innerText")
                ziel = b.js(ZIEL_REF)
                pruefe(mitten != ziel, f'{weg}: Probe ungültig, Hochzählen war schon fertig ({mitten})')
                pruefe(ist == ziel, f'{weg}: Druck zeigt {ist} statt dem fertigen Score {ziel}')
                if weg == 'Druckansicht':
                    ring = b.js("(() => { const r = document.getElementById('scoreRing'); return [getComputedStyle(r).strokeDasharray, r.getAttribute('stroke-dasharray')]; })()")
                    ziel_ring = ring[1].replace(' ', 'px, ') + 'px'
                    pruefe(ring[0] == ziel_ring, f'Druck: Ring nicht fertig ({ring})')
                    pruefe(b.js(ANIMATION + "('singleRefView')") == [], 'Druck: Einblenden läuft im Druck')
                time.sleep(0.5)
                pruefe(b.js("document.getElementById('scoreVal').innerText") == ziel, f'{weg}: Score nach dem Druck verändert')

            # 4. Bewegung reduzieren: nichts bewegt sich
            b.bewegung = False
            b.fenster(1194, 834)
            werte = b.js(ABTASTEN + "('scoreVal', 'selectRefTab(1)')")
            pruefe(werte[0][1] == werte[-1][1] == b.js(ZIEL_REF), f'Bewegung reduzieren: Score zählt hoch ({[w for _, w in werte[:5]]})')
            pruefe(b.js(ANIMATION + "('singleRefView')") == [], 'Bewegung reduzieren: Ansicht blendet ein')
            pruefe(b.js("getComputedStyle(document.getElementById('scoreRing')).transitionDuration") == '0s', 'Bewegung reduzieren: Ring mit Übergang')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Animations-Test: {len(fehler)} Fehler (Einblenden 150 ms, Hochzählen 400 ms nur beim Reiterwechsel, Druck fertig, Bewegung reduzieren)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
