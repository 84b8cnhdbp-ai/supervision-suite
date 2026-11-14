"""Knopfreihen-Test (Etappe 2.3): Segmented Controls als echte Radiogruppen.

Prüft auf iPad hochkant (834), iPad quer (1194) und MacBook (1440), Deutsch und Englisch, Head Referee und
Linesperson:
- jede Reihe ist ein <fieldset> mit Namen (für VoiceOver), aus echten Radioknöpfen mit je einer Beschriftung
- jedes Segment mindestens 44 × 44 px, nichts abgeschnitten, keine waagrechte Bildlaufleiste
- Reihenfolge vom besten zum schlechtesten Wert; beim Trend alle 4 Optionen inkl. „Erstbeobachtung“
- Gesamteinschätzung ohne Vorwahl: oranger Rahmen und Hinweis; nach der Wahl die Definition der Stufe
- jede Option ergibt den bisherigen Speicherwert (echter Klick → localStorage), auch nach Neuladen gewählt
- Tastatur: Pfeiltasten wechseln die Wahl und speichern
Aufruf: python3 tests/tools/knopfreihen-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

GROESSEN = [(834, 1194), (1194, 834), (1440, 900)]

PRUEFE_REIHEN = r"""((auswahl) => {
  const fehler = [];
  const vw = document.documentElement.clientWidth;
  if (document.documentElement.scrollWidth > vw + 1) fehler.push(`waagrechte Bildlaufleiste (${document.documentElement.scrollWidth} > ${vw})`);
  document.querySelectorAll(auswahl).forEach((fs) => {
    const name = fs.id;
    const ref = fs.getAttribute('aria-labelledby');
    const titel = ref && document.getElementById(ref) ? document.getElementById(ref).textContent.trim() : '';
    if (!titel) fehler.push(`${name}: Gruppe ohne Namen (aria-labelledby)`);
    const radios = [...fs.querySelectorAll('input')];
    if (radios.length < 2 || radios.some((r) => r.type !== 'radio' || r.name !== name)) fehler.push(`${name}: keine echte Radiogruppe`);
    const fr = fs.getBoundingClientRect();
    if (fr.right > vw + 1 || fr.left < -1) fehler.push(`${name}: Reihe ragt aus dem Bild (${Math.round(fr.left)}–${Math.round(fr.right)} bei ${vw})`);
    radios.forEach((r) => {
      const l = r.labels && r.labels[0];
      if (!r.labels || r.labels.length !== 1 || !l.textContent.trim()) { fehler.push(`${name}=${r.value}: ohne Beschriftung`); return; }
      const b = l.getBoundingClientRect();
      if (b.height < 43.5 || b.width < 43.5) fehler.push(`${name}=${r.value}: nur ${Math.round(b.width)}×${Math.round(b.height)} px`);
      if (l.scrollWidth > l.clientWidth + 1 || l.scrollHeight > l.clientHeight + 1) fehler.push(`${name}=${r.value}: Text abgeschnitten`);
      // Umbruch mitten im Wort: mehr Zeilen als Wörter (z. B. „1-Man / n“)
      const sichtbar = [...l.childNodes].find((n) => n.nodeType === 3 || !n.classList.contains('sr-only'));
      if (sichtbar) {
        const range = document.createRange(); range.selectNodeContents(sichtbar);
        const zeilen = new Set([...range.getClientRects()].map((q) => Math.round(q.top))).size;
        const woerter = sichtbar.textContent.trim().split(/\s+/).length;
        if (zeilen > woerter) fehler.push(`${name}=${r.value}: „${sichtbar.textContent.trim()}“ bricht mitten im Wort um`);
      }
      if (b.right > fr.right + 1) fehler.push(`${name}=${r.value}: ragt aus der Reihe`);
    });
  });
  return fehler;
})"""
FORMULAR = "'.app-container fieldset.seg'"

# iPad quer / MacBook: In der Formularspalte bricht nichts um und nichts ragt hinaus
# (Knopf-Beschriftungen, Feldbezeichnungen, Abschnittstitel; Fliesstext wie Definitionen darf umbrechen).
EINZEILIG = r"""(() => {
  const f = [];
  const spalte = document.querySelector('#singleRefView .formular-spalte');
  if (spalte.scrollWidth > spalte.clientWidth + 1) f.push(`Formularspalte zu breit (${spalte.scrollWidth} > ${spalte.clientWidth})`);
  const zeilen = (el) => {
    const teile = [...el.childNodes].filter((n) => n.nodeType === 3 ? n.textContent.trim() : !n.classList.contains('sr-only'));
    // Zeilen = Gruppen von Rechtecken, die sich in der Höhe überlappen (Kreis-Nummer + Text = eine Zeile)
    const rects = [];
    teile.forEach((n) => { const r = document.createRange(); r.selectNodeContents(n); rects.push(...[...r.getClientRects()].filter((q) => q.width > 0)); });
    rects.sort((a, b) => a.top - b.top);
    let anzahl = 0, unten = -Infinity;
    rects.forEach((q) => { if (q.top >= unten - 1) { anzahl++; unten = q.bottom; } else unten = Math.max(unten, q.bottom); });
    return anzahl;
  };
  spalte.querySelectorAll('.seg-opt, .feld-label, label, .section-title, .seg-legende').forEach((el) => {
    if (!el.offsetParent || !el.textContent.trim()) return;
    if (zeilen(el) > 1) f.push(`„${el.textContent.trim().slice(0, 40)}“ bricht um`);
  });
  spalte.querySelectorAll('input, select, textarea, fieldset.seg').forEach((el) => {
    if (!el.offsetParent) return;
    const r = el.getBoundingClientRect(), s = spalte.getBoundingClientRect();
    if (r.right > s.right + 1) f.push(`${el.id || el.name || el.tagName} ragt aus der Formularspalte`);
  });
  return f;
})()"""
MENU = "'#mehrMenu fieldset.seg'"


def main():
    fehler = []
    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            # 1. Grössen, Namen, Abschneiden – alle Breiten, Sprachen, Rollen
            for w, h in GROESSEN:
                for sprache in ('de', 'en'):
                    b.fenster(w, h)
                    daten_setzen(b, srv.basis, sprache=sprache)
                    b.oeffnen(srv.basis + '/index.html')
                    for tab, rolle in ((0, 'Head'), (2, 'Linesperson')):
                        b.js(f'selectRefTab({tab})')
                        for f in b.js(PRUEFE_REIHEN + f'({FORMULAR})'):
                            fehler.append(f'{w}px {sprache} {rolle}: {f}')
                        if w >= 1194:
                            for f in b.js(EINZEILIG):
                                fehler.append(f'{w}px {sprache} {rolle}: {f}')
                    anzahl = b.js(f"document.querySelectorAll({FORMULAR}).length")
                    if anzahl != 13:
                        fehler.append(f'{w}px {sprache}: {anzahl} Knopfreihen im Formular statt 13')
                    # Menü „Mehr“: Sprache und Darstellung
                    b.klick('#btnMehr')
                    for f in b.js(PRUEFE_REIHEN + f'({MENU})'):
                        fehler.append(f'{w}px {sprache} Menü: {f}')
                    if b.js(f"document.querySelectorAll({MENU}).length") != 2:
                        fehler.append(f'{w}px {sprache}: Menü ohne die 2 Knopfreihen Sprache/Darstellung')
                    b.taste('Escape')

            b.fenster(1194, 834)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            werte = lambda n: b.js(f"[...document.querySelectorAll('input[name={n}]')].map((r) => r.value)")

            # 2. Reihenfolge vom besten zum schlechtesten Wert
            if werte('overall_grade') != ['100', '80', '50', '20']:
                fehler.append(f"Gesamteinschätzung: Reihenfolge {werte('overall_grade')}")
            for i in range(1, 8):
                if werte(f'perf_{i}') != ['100', '80', '50', '20', 'NA']:
                    fehler.append(f"Kriterium {i}: Reihenfolge {werte(f'perf_{i}')}")
            for k in ('coach_trend', 'coach_attitude', 'coach_feedback'):
                punkte = b.js(f"[...document.querySelectorAll('input[name={k}]')].map((r) => COACH_SCORES['{k}'][r.value])")
                alle = b.js(f"Object.keys(COACH_SCORES['{k}']).sort()")
                if sorted(werte(k)) != alle:
                    fehler.append(f'{k}: Optionen {werte(k)} statt {alle}')
                if any(p is None for p in punkte) or punkte != sorted(punkte, reverse=True):
                    fehler.append(f'{k}: nicht vom besten zum schlechtesten ({punkte})')
            if 'Erstbeobachtung' not in werte('coach_trend'):
                fehler.append('Trend: „Erstbeobachtung“ fehlt')

            # 3. Gesamteinschätzung: ohne Vorwahl Hinweis, nach Wahl Definition
            b.js('selectRefTab(2)')   # Linesperson 1: keine Gesamteinschätzung im Beispiel
            if b.js("segWert('overall_grade')") != '':
                fehler.append('Gesamteinschätzung: ist vorgewählt')
            if not b.js("document.getElementById('gradeBox').classList.contains('grade-missing')"):
                fehler.append('Gesamteinschätzung: kein oranger Rahmen ohne Wahl')
            if b.js("document.getElementById('gradeHint').textContent") != b.js("t('grade_choose')"):
                fehler.append('Gesamteinschätzung: Hinweis „bewusst wählen“ fehlt')
            b.klick("label[for='overall_grade__1']")
            if b.js("document.getElementById('gradeHint').textContent") != b.js("t('desc_good')"):
                fehler.append('Gesamteinschätzung: nach Wahl „Gut“ steht nicht dessen Definition')
            if b.js("document.getElementById('gradeBox').classList.contains('grade-missing')"):
                fehler.append('Gesamteinschätzung: oranger Rahmen trotz Wahl')

            # 4. Jede Option -> bisheriger Speicherwert (echter Klick)
            b.js('selectRefTab(0)')
            gespeichert = lambda: b.js("JSON.parse(localStorage.getItem('referee_multi_supervision_data')).referees['4-Man_h1']")
            felder = {'overall_grade': 'overall_grade', 'current_review_round': 'review_round',
                      'coach_trend': 'coach_trend', 'coach_attitude': 'coach_attitude', 'coach_feedback': 'coach_feedback'}
            felder.update({f'perf_{i}': f'perf_{i}' for i in range(1, 8)})
            letzte = {}
            for name, schluessel in felder.items():
                for nr, wert in enumerate(werte(name)):
                    b.klick(f"label[for='{name}__{nr}']")
                    ist = gespeichert().get(schluessel)
                    if ist != wert:
                        fehler.append(f'{name}: Klick auf Option {nr + 1} speichert {ist!r} statt {wert!r}')
                    letzte[name] = wert
            # nach Neuladen bleibt die Wahl sichtbar
            b.oeffnen(srv.basis + '/index.html')
            for name, wert in letzte.items():
                if b.js(f"segWert('{name}')") != wert:
                    fehler.append(f"{name}: nach Neuladen gewählt {b.js(f'segWert({name!r})')!r} statt {wert!r}")
            # System
            b.klick("label[for='system_typ__1']")
            if b.js('currentSystem') != '2-Man' or b.js("JSON.parse(localStorage.getItem('referee_multi_supervision_data')).global.system_typ") != '2-Man':
                fehler.append('System: Klick auf „2-Mann“ wechselt/speichert nicht')
            b.klick("label[for='system_typ__3']")

            # 5. Tastatur: Pfeiltasten in einer Reihe
            b.js("setzeSeg('perf_3', '80'); saveCurrentRefData(); document.querySelector('input[name=perf_3]:checked').focus()")
            b.taste('ArrowRight')
            if b.js("segWert('perf_3')") != '50' or gespeichert().get('perf_3') != '50':
                fehler.append(f"Tastatur: Pfeil rechts ergibt {b.js(chr(115) + 'egWert(' + repr('perf_3') + ')')!r} statt '50'")
            b.taste('ArrowLeft')
            if b.js("segWert('perf_3')") != '80':
                fehler.append('Tastatur: Pfeil links geht nicht zurück')
            if b.js("document.activeElement.name") != 'perf_3':
                fehler.append('Tastatur: Fokus hat die Reihe verlassen')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Knopfreihen-Test: {len(fehler)} Fehler (3 Breiten × DE/EN × Head/Linesperson, Reihenfolge, Speicherwerte, Tastatur)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
