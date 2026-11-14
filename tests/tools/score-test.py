"""Score-Test (Etappe 2.4b): rechte Spalte mit Score-Karte, Netzdiagramm und „Bereit zum Sichern?“.

Prüft:
- iPad quer (1194) und MacBook (1440): zwei Spalten, rechte Spalte bleibt beim Scrollen stehen und ist ganz sichtbar;
  iPad hochkant (834): eine Spalte, Score oben
- angezeigte Werte = computeRefScores (Gesamt und drei Teilwerte) in allen Reitern; Ring passend zum Score
- Statustexte und Schwellen (> 80, ≥ 75, ≥ 60, ≥ 45, darunter, ohne Gesamteinschätzung)
- kurze Begriffe bei der Gesamteinschätzung, lange als Vorlese-/Tooltip-Text
- Netzdiagramm: 7 Punkte, N/A als hohler grauer Punkt mit „(N/A)“, im Druck sichtbar
- „Bereit zum Sichern?“: fehlende Punkte antippbar, Sprung zum Feld; nach Ergänzung „Alles da“; nicht im Druck
Aufruf: python3 tests/tools/score-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

RECHTECK = "(sel) => { const r = document.querySelector(sel).getBoundingClientRect(); return { l: r.left, r: r.right, t: r.top, b: r.bottom }; }"


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            # 1. Spalten und Stehenbleiben
            for w, h in ((834, 1194), (1194, 834), (1440, 900)):
                b.fenster(w, h)
                daten_setzen(b, srv.basis)
                b.oeffnen(srv.basis + '/index.html')
                aside = b.js(f"({RECHTECK})('.score-spalte')")
                form = b.js(f"({RECHTECK})('#singleRefView .formular-spalte')")
                if w >= 1000:
                    pruefe(aside['l'] >= form['r'], f'{w}px: rechte Spalte nicht rechts vom Formular')
                    leiste = b.js(f"({RECHTECK})('.werkzeugleiste')")['b']
                    for y in (800, 1500, 2200, 2600):
                        b.js(f'window.scrollTo(0, {y})')
                        b.js('new Promise((r) => setTimeout(r, 100))')
                        a = b.js(f"({RECHTECK})('.score-spalte')")
                        if b.js(f"({RECHTECK})('#singleRefView .formular-spalte')")['b'] < h:
                            continue   # Formular zu Ende: die Spalte rollt mit dem Formularende mit (normal)
                        pruefe(leiste - 1 <= a['t'] <= leiste + 30 and a['b'] <= h + 1,
                               f'{w}px: rechte Spalte bleibt beim Scrollen ({y}) nicht sichtbar stehen (oben {a["t"]:.0f}, unten {a["b"]:.0f})')
                else:
                    pruefe(aside['b'] <= form['t'] + 1, f'{w}px: Score nicht über dem Formular')

            b.fenster(1194, 834)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')

            # 2. Werte = computeRefScores, Ring
            for tab in range(4):
                b.js(f'selectRefTab({tab})')
                sc = b.js('(() => { const s = computeRefScores(readFormData()); delete s.radar; return s; })()')
                fmt = lambda v: '–' if v is None else f'{v}%'
                ist = b.js("['scoreVal', 'subScorePart2', 'subScorePart3', 'subScorePart4'].map((id) => document.getElementById(id).textContent)")
                pruefe(ist == [fmt(sc['total']), fmt(sc['part2']), fmt(sc['part3']), fmt(sc['part4'])], f'Reiter {tab}: angezeigt {ist}, gerechnet {sc}')
                strich = float(b.js("document.getElementById('scoreRing').getAttribute('stroke-dasharray').split(' ')[0]"))
                soll = 0 if sc['total'] is None else 2 * 3.14159265 * 64 * sc['total'] / 100
                pruefe(abs(strich - soll) < 0.5, f'Reiter {tab}: Ring {strich:.1f} statt {soll:.1f}')
                status = b.js("document.getElementById('scoreStatusText').textContent")
                pruefe(status == b.js(f"t(scoreStatus({'null' if sc['total'] is None else sc['total']}).text)"), f'Reiter {tab}: Status „{status}“')

            # 3. Schwellen
            erwartet = {81: 'status_exc', 80: 'status_good', 75: 'status_good', 74: 'status_sat', 60: 'status_sat',
                        59: 'status_ni', 45: 'status_ni', 44: 'status_unsat', None: 'status_missing'}
            for wert, schluessel in erwartet.items():
                ist = b.js(f"scoreStatus({'null' if wert is None else wert}).text")
                pruefe(ist == schluessel, f'Schwelle {wert}: {ist} statt {schluessel}')
            pruefe(b.js("t('status_exc')") == 'Überdurchschnittlich', 'kurzer Statustext fehlt')

            # 4. Kurze Begriffe Gesamteinschätzung
            kurz = b.js("[...document.querySelectorAll('#overall_grade .seg-opt')].map((l) => (l.querySelector('[aria-hidden]') || l).textContent)")
            pruefe(kurz == ['Sehr gut', 'Gut', 'Verbesserungsbedürftig', 'Ungenügend'], f'Gesamteinschätzung kurz: {kurz}')
            lang = b.js("document.querySelector('label[for=overall_grade__1] .sr-only').textContent")
            pruefe(lang == b.js("t('grade_good')"), f'Gesamteinschätzung lang (VoiceOver): {lang}')

            # 5. Netzdiagramm mit N/A
            b.js("selectRefTab(0); setzeSeg('perf_3', 'NA'); calcScores();")
            pruefe(b.js("document.querySelectorAll('#radarChart .netz-punkt, #radarChart .netz-na').length") == 7, 'Netz: nicht 7 Punkte')
            pruefe(b.js("document.querySelectorAll('#radarChart .netz-na').length") == 1, 'Netz: N/A nicht als eigener Punkt')
            na = b.js("(() => { const c = getComputedStyle(document.querySelector('#radarChart .netz-na')); return [c.fill, c.stroke]; })()")
            karte = b.js("getComputedStyle(document.querySelector('.netz-karte')).backgroundColor")
            pruefe(na[0] == karte and na[1] != na[0], f'Netz: N/A nicht hohl/grau ({na}, Karte {karte})')
            pruefe('(N/A)' in b.js("document.getElementById('radarChart').textContent"), 'Netz: Beschriftung ohne „(N/A)“')
            pruefe('N/A' in b.js("document.getElementById('radarChart').getAttribute('aria-label')"), 'Netz: Vorlesetext ohne N/A')

            # 6. Bereit zum Sichern?
            b.js('selectRefTab(2)')   # Linesperson 1: Gesamteinschätzung fehlt
            fehlt = b.js("[...document.querySelectorAll('#bereitListe .bereit-fehlt')].map((x) => x.dataset.punkt)")
            pruefe(fehlt == ['note'], f'Bereit: fehlend {fehlt} statt [note]')
            pruefe(b.js("document.querySelectorAll('#bereitListe .bereit-ok').length") == 2, 'Bereit: Name/Datum nicht als erledigt')
            b.klick("#bereitListe .bereit-fehlt[data-punkt=note]")
            b.js('new Promise((r) => setTimeout(r, 600))')
            pruefe(b.js("document.activeElement.name") == 'overall_grade' and b.js("document.getElementById('gradeBox').classList.contains('feld-hervorheben')"),
                   'Bereit: Tipp auf Gesamteinschätzung springt nicht zum Feld')
            b.klick("label[for='overall_grade__1']")
            pruefe(b.js("document.querySelectorAll('#bereitListe .bereit-fehlt').length") == 0 and b.js("document.getElementById('bereitStatus').classList.contains('bereit-ja')"),
                   'Bereit: nach Wahl nicht „Alles da“')
            # leerer 2-Mann-Reiter ohne Datum: Name und Datum fehlen
            b.js("switchSystem('2-Man'); document.getElementById('spiel_datum').value = ''; handleGlobalDateTimeChange();")
            fehlt = b.js("[...document.querySelectorAll('#bereitListe .bereit-fehlt')].map((x) => x.dataset.punkt)")
            pruefe(fehlt == ['name', 'datum', 'note'], f'Bereit (leer): fehlend {fehlt}')
            b.klick("#bereitListe .bereit-fehlt[data-punkt=name]")
            b.js('new Promise((r) => setTimeout(r, 600))')
            pruefe(b.js('document.activeElement.id') == 'current_schiri_name', f"Bereit: Sprung zum Namen landet bei {b.js('document.activeElement.id')}")
            b.klick("#bereitListe .bereit-fehlt[data-punkt=datum]")
            b.js('new Promise((r) => setTimeout(r, 600))')
            pruefe(b.js('document.activeElement.id') == 'spiel_datum', f"Bereit: Sprung zum Datum landet bei {b.js('document.activeElement.id')}")
            # gleiche Prüfung wie das Fenster beim Sichern
            b.klick('#btnSichern')
            im_fenster = b.js("[...document.querySelectorAll('dialog.fenster[open] .fenster-eintrag')].map((e) => e.textContent.replace('›', '').trim())")
            in_liste = b.js("[...document.querySelectorAll('#bereitListe .bereit-fehlt')].map((e) => e.childNodes[1].textContent)")
            pruefe(im_fenster == in_liste, f'Fenster beim Sichern ({im_fenster}) ≠ Bereit-Liste ({in_liste})')
            b.taste('Escape')

            # 7. Druck: Netzdiagramm sichtbar, Bereit-Liste nicht
            b.fenster(794, 1123, druck=True)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            netz = b.js("(() => { const s = document.getElementById('radarChart'); const r = s.getBoundingClientRect(); return [getComputedStyle(s).display, r.width, s.querySelectorAll('polygon').length]; })()")
            pruefe(netz[0] != 'none' and netz[1] > 100 and netz[2] >= 4, f'Druck: Netzdiagramm nicht sichtbar ({netz})')
            pruefe(b.js("getComputedStyle(document.querySelector('.bereit-karte')).display") == 'none', 'Druck: „Bereit zum Sichern?“ wird gedruckt')
            pruefe(b.js("getComputedStyle(document.querySelector('.score-karte')).display") != 'none', 'Druck: Score-Karte fehlt')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Score-Test: {len(fehler)} Fehler (Spalten/Stehenbleiben, Werte, Schwellen, Netz mit N/A, Bereit zum Sichern, Druck)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
