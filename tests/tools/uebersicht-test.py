"""Übersicht-Test (Etappe 2.8): Gespann-Übersicht und Saison-Statistik im neuen Stil.

Prüft:
- Gespann: eine Karte je Rolle als echter Knopf (Tastatur Enter/Leertaste, VoiceOver-Name); Werte = computeRefScores;
  Durchschnitt und Status mit denselben Schwellen wie bei der Bewertung; Tipp öffnet den Reiter; leerer Zustand sagt,
  dass man die Rollen besetzt; Druck mit Karten und Profil
- Statistik: Zahlen wie bisher mit den Beispieldateien (Meier Luca 80 % → 94 %, +14 %, 87.0 %; Ø R1 67.4 %, Ø R2 94.0 %;
  1 / 5 abgeschlossen); negative Entwicklung mit echtem Minuszeichen „−“ und Pfeil; Abzeichen mit Kontrast ≥ 4.5:1
  hell und dunkel; leerer Zustand sagt, was zu tun ist; Tabelle passt ab 768 px; Deutsch und Englisch
Aufruf: python3 tests/tools/uebersicht-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import shutil
from werkzeug import REPO, Browser, server, daten_setzen, LEER, git_stand  # noqa: E402

LADEN = """(async (extra) => { selectStatsTab();
  const n = ['beispiel-v1.0.json','beispiel-v1.0-ohne-evaluation.json','beispiel-v1.1.json','beispiel-v1.1-mit-na.json','beispiel-spiel.json'];
  const f = await Promise.all(n.map(async (x) => new File([await (await fetch('/tests/fixtures/' + x)).text()], x)));
  extra.forEach((e, i) => f.push(new File([JSON.stringify(e)], 'extra' + i + '.json')));
  await handleSeasonFilesUpload({ target: { files: f, value: '' } }); })"""
EXTRA = [  # erfundene Zusatzfälle: Verschlechterung und gleichbleibend (nur scoreGesamt)
    {'version': '1.0', 'schiedsrichter': 'Minus Test', 'reviewRunde': 'R1', 'scoreGesamt': 70},
    {'version': '1.0', 'schiedsrichter': 'Minus Test', 'reviewRunde': 'R2', 'scoreGesamt': 64},
    {'version': '1.0', 'schiedsrichter': 'Gleich Test', 'reviewRunde': 'R1', 'scoreGesamt': 75},
    {'version': '1.0', 'schiedsrichter': 'Gleich Test', 'reviewRunde': 'R2', 'scoreGesamt': 75},
]
ZEILEN = "[...document.querySelectorAll('.stat-tabelle tbody tr')].map((r) => [...r.children].map((c) => c.textContent.replace(/\\s+/g, ' ').trim()))"


def kontrast(a, b):
    def lum(rgb):
        r, g, bl = (int(x) / 255 for x in re.findall(r'\d+', rgb)[:3])
        f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(bl)
    la, lb = sorted((lum(a), lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            def start(w=1194, h=834, sprache='de', schema='light'):
                b.fenster(w, h, schema)
                daten_setzen(b, srv.basis, sprache=sprache)
                b.oeffnen(srv.basis + '/index.html')

            # ---------- Gespann ----------
            start()
            b.js('selectSummaryTab()')
            karten = b.js("[...document.querySelectorAll('#summaryCardsContainer .gespann-karte')].map((k) => [k.tagName, k.type, k.getAttribute('aria-label')])")
            pruefe(len(karten) == 4 and all(k[0] == 'BUTTON' and k[1] == 'button' for k in karten), f'Gespann-Karten keine echten Knöpfe: {karten}')
            pruefe(karten and 'Head Referee 1' in karten[0][2] and 'Frei Lea' in karten[0][2] and '94%' in karten[0][2], f'VoiceOver-Name: {karten[:1]}')
            for i, ref in enumerate(['h1', 'h2', 'l1', 'l2']):
                sc = b.js(f"(() => {{ const d = gameData.referees['4-Man_{ref}'] || getDefaultRefData(); const s = computeRefScores(d); return [s.total, s.part2, s.part3, s.part4]; }})()")
                fmt = lambda v: '–' if v is None else f'{v}%'
                text = b.js(f"document.querySelectorAll('.gespann-karte')[{i}].textContent.replace(/\\s+/g, ' ')")
                for wert in sc:
                    pruefe(fmt(wert) in text, f'Karte {ref}: Wert {fmt(wert)} fehlt ({text.strip()[:120]})')
            pruefe(b.js("document.getElementById('crewScoreVal').textContent") == '63%', f"Gespann-Durchschnitt {b.js('document.getElementById(\"crewScoreVal\").textContent')} statt 63%")
            pruefe(b.js("document.getElementById('crewStatus').textContent") == b.js("t(scoreStatus(63).text)"), 'Gespann-Status nicht mit gleichen Schwellen')
            pruefe(b.js("document.getElementById('crewRing').style.stroke") == 'var(--r-solid)', 'Gespann-Ring nicht in der Statusfarbe')
            pruefe('2' in b.js("document.getElementById('crewSub').textContent") and '4' in b.js("document.getElementById('crewSub').textContent"), 'Gespann: „2 von 4“ fehlt')
            pruefe(b.js("document.getElementById('crewLeer').hidden"), 'Gespann: Leer-Hinweis trotz besetzter Rollen')
            # Tastatur: Enter und Leertaste öffnen den Reiter
            b.js("document.querySelectorAll('.gespann-karte')[1].focus()"); b.taste('Enter')
            pruefe(b.js('activeTabType') == 'ref' and b.js('activeRefIndex') == 1, 'Enter auf Gespann-Karte öffnet Reiter H2 nicht')
            b.js('selectSummaryTab()'); b.js("document.querySelectorAll('.gespann-karte')[2].focus()"); b.taste(' ')
            pruefe(b.js('activeTabType') == 'ref' and b.js('activeRefIndex') == 2, 'Leertaste auf Gespann-Karte öffnet Reiter L1 nicht')
            b.js('selectSummaryTab()'); b.klick('.gespann-karte:nth-child(4)')
            pruefe(b.js('activeRefIndex') == 3, 'Tipp auf Gespann-Karte öffnet Reiter L2 nicht')
            # leerer Zustand: 2-Mann ohne Namen
            b.js("switchSystem('2-Man'); selectSummaryTab()")
            pruefe(not b.js("document.getElementById('crewLeer').hidden") and b.js("document.getElementById('crewLeer').textContent") == b.js("t('crew_empty')"),
                   'Gespann: Leer-Hinweis „Rollen besetzen“ fehlt')
            pruefe(b.js("document.getElementById('crewStatus').textContent") == b.js("t('crew_none')"), 'Gespann leer: Status falsch')
            b.js("switchSystem('4-Man')")
            # Druck der Gespann-Übersicht: Karten, Profil und Notiz sichtbar, nicht schlechter als bisher
            b.fenster(794, 1123, druck=True)
            b.js('selectSummaryTab()')
            sichtbar = b.js("['#summaryCardsContainer', '#crewRadarChart', '#crew_notes', '#crewScoreVal'].map((s) => { const e = document.querySelector(s); const r = e.getBoundingClientRect(); return getComputedStyle(e).display !== 'none' && r.width > 20 && r.height > 10; })")
            pruefe(all(sichtbar), f'Druck Gespann: nicht alles sichtbar {sichtbar}')
            pruefe(b.js("document.querySelectorAll('#summaryCardsContainer .gespann-karte').length") == 4, 'Druck Gespann: nicht 4 Karten')

            # ---------- Statistik ----------
            for sprache in ('de', 'en'):
                start(1194, 834, sprache)
                b.js('selectStatsTab()')
                pruefe(b.js("document.getElementById('seasonStatsContent').textContent.trim()") == b.js("t('stats_empty')"), f'{sprache}: Leer-Hinweis fehlt')
                pruefe('.json' in b.js("t('stats_empty')"), f'{sprache}: Leer-Hinweis sagt nicht, dass man die .json-Dateien wählt')
                b.js("window.__wahl = 0; HTMLInputElement.prototype.click = function () { if (this.type === 'file') __wahl++; };")
                b.klick('#btnStatsLaden')
                pruefe(b.js('__wahl') == 1, f'{sprache}: „Dateien wählen“ öffnet keine Dateiauswahl')
                b.js(LADEN + f"({EXTRA!r})".replace('None', 'null'))
                zeilen = b.js(ZEILEN)
                tabelle = {z[0]: z[2:] for z in zeilen}
                pruefe(tabelle.get('Meier Luca') == ['80%', '94%', '+14% ↑ ' + b.js("t('stats_up')"), '87.0%'], f"{sprache}: Meier Luca {tabelle.get('Meier Luca')}")
                pruefe(tabelle.get('Brunner Jan') == ['72%', '–', '–', '72%'], f"{sprache}: Brunner Jan {tabelle.get('Brunner Jan')}")
                pruefe(tabelle.get('Frei Lea', [''])[0] == '94%' and tabelle.get('Gast Beispiel', [''])[0] == '32%' and tabelle.get('Keller Nina', [''])[0] == '59%',
                       f'{sprache}: Frei/Gast/Keller falsch')
                pruefe(tabelle.get('Minus Test', ['', '', ''])[2] == '−6% ↓ ' + b.js("t('stats_down')"), f"{sprache}: Verschlechterung {tabelle.get('Minus Test')} (echtes Minus „−“ erwartet)")
                pruefe(tabelle.get('Gleich Test', ['', '', ''])[2] == '0% → ' + b.js("t('stats_same')"), f"{sprache}: gleichbleibend {tabelle.get('Gleich Test')}")
                kacheln = b.js("['statFertig', 'statR1', 'statR2'].map((id) => document.getElementById(id).textContent)")
                pruefe(kacheln == ['3 / 7', '68.9%', '77.7%'], f'{sprache}: Kennzahlen {kacheln}')   # mit den 2 Zusatzfällen: (80+72+94+32+59+70+75)/7, (94+64+75)/3
                status = {z[0]: z[1] for z in zeilen}
                pruefe(status.get('Meier Luca') == b.js("t('stats_status_done')") and status.get('Keller Nina') == b.js("t('stats_status_progress')"),
                       f'{sprache}: Status-Abzeichen {status}')
                kopf = b.js("[...document.querySelectorAll('.stat-tabelle thead th')].map((t) => t.textContent)")
                pruefe(kopf[0] == b.js("t('stats_col_name')") and kopf[4] == b.js("t('stats_col_delta')"), f'{sprache}: Spaltentitel {kopf}')
            # Zahlen genau wie bisher (nur Beispieldateien, ohne Zusatzfälle)
            start()
            b.js(LADEN + '([])')
            pruefe(b.js("['statFertig', 'statR1', 'statR2'].map((id) => document.getElementById(id).textContent)") == ['1 / 5', '67.4%', '94.0%'],
                   f"Kennzahlen mit Beispieldateien: {b.js(chr(91) + repr('statFertig') + ', ' + repr('statR1') + ', ' + repr('statR2') + '].map((id) => document.getElementById(id).textContent)')}")
            # Sprachwechsel beschriftet die geladene Statistik neu
            b.js("setLanguage('en')")
            pruefe(b.js("document.querySelector('.stat-fertig').textContent") == '2/2 done', 'Sprachwechsel: Statistik nicht neu beschriftet')
            b.js("setLanguage('de')")

            # Kontrast der Abzeichen und Entwicklung, hell und dunkel; Tabelle passt ab 768 px
            for w, h, schema in ((768, 1024, 'light'), (768, 1024, 'dark'), (834, 1194, 'dark'), (1440, 900, 'light')):
                start(w, h, 'de', schema)
                b.js(LADEN + f"({EXTRA!r})".replace('None', 'null'))
                for sel in ('.stat-offen', '.stat-arbeit', '.stat-fertig'):
                    if not b.js(f"!!document.querySelector('{sel}')"):
                        if sel != '.stat-offen':
                            fehler.append(f'{w}px {schema}: {sel} fehlt')
                        continue
                    f, g = b.js(f"(() => {{ const e = getComputedStyle(document.querySelector('{sel}')); return [e.color, e.backgroundColor]; }})()")
                    pruefe(kontrast(f, g) >= 4.5, f'{w}px {schema}: Kontrast {sel} {kontrast(f, g):.2f}')
                karte = b.js("getComputedStyle(document.querySelector('.karte')).backgroundColor")
                for sel in ('.stat-plus', '.stat-minus'):
                    f = b.js(f"getComputedStyle(document.querySelector('{sel}')).color")
                    pruefe(kontrast(f, karte) >= 4.5, f'{w}px {schema}: Kontrast {sel} {kontrast(f, karte):.2f}')
                box = b.js("(() => { const b = document.querySelector('.stat-tabelle-box'); return [b.scrollWidth, b.clientWidth, document.documentElement.scrollWidth]; })()")
                pruefe(box[0] <= box[1] + 1 and box[2] <= w, f'{w}px {schema}: Tabelle passt nicht ({box})')
                klein = b.js("[...document.querySelectorAll('#seasonStatsView button')].filter((e) => e.getBoundingClientRect().height < 43.5).length")
                pruefe(klein == 0, f'{w}px: zu kleiner Knopf in der Statistik')
            # Zahlen genau wie auf main: gleiche Dateien in den alten Stand laden und Zelle für Zelle vergleichen
            def zahlen(zeilen):   # nur Zahlen (Pfeile, Minuszeichen-Form, Status-Text egal)
                zahl = lambda c: (lambda x: '' if x == '-' else x)(re.sub(r'[^0-9.+\u2212-]', '', c).replace('\u2212', '-'))   # „-“/„–“ = kein Wert
                return {z[0]: [zahl(c) for c in z[2:]] for z in zeilen}
            neu_zahlen = None
            start()
            b.js(LADEN + f"({EXTRA!r})".replace('None', 'null'))
            neu_zahlen = zahlen(b.js(ZEILEN))
            alt_dir = git_stand('main')
            alt_srv = server(alt_dir, {'/__leer': LEER})
            try:
                b.fenster(1194, 834)
                daten_setzen(b, alt_srv.basis)
                b.oeffnen(alt_srv.basis + '/index.html')
                b.js("window.alert = () => {};")
                b.js(LADEN + f"({EXTRA!r})".replace('None', 'null'))
                alt_zahlen = zahlen(b.js("[...document.querySelectorAll('#seasonStatsContent tbody tr')].map((r) => [...r.children].map((c) => c.textContent.replace(/\\s+/g, ' ').trim()))"))
                alt_kacheln = b.js("[...document.querySelectorAll('#seasonStatsContent > div:first-child > div > div:last-child')].map((d) => d.textContent.trim())")
            finally:
                alt_srv.shutdown()
                shutil.rmtree(alt_dir, ignore_errors=True)
            pruefe(neu_zahlen == alt_zahlen, f'Statistik-Zahlen anders als main:\n  neu {neu_zahlen}\n  alt {alt_zahlen}')
            b.fenster(1194, 834)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            b.js(LADEN + f"({EXTRA!r})".replace('None', 'null'))
            neu_kacheln = b.js("['statFertig', 'statR1', 'statR2'].map((id) => document.getElementById(id).textContent)")
            pruefe([k.replace('–', '-') for k in neu_kacheln] == alt_kacheln, f'Kennzahlen anders als main: {neu_kacheln} / {alt_kacheln}')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Übersicht-Test: {len(fehler)} Fehler (Gespann: Knöpfe, Werte, Schwellen, Tastatur, leer, Druck; Statistik: Zahlen, Minus/Pfeile, Kontrast, Breite, DE/EN)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
