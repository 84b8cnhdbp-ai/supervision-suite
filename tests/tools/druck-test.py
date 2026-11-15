"""Druck-Test (Etappe 2.9a): Druck vollständig und druckfertig.

Prüft (Druckansicht A4, wie beim Drucken / PDF):
- jedes mehrzeilige Feld (Notizen der Kriterien, Stärken, Schwerpunkte, Rapport, Gespann-Notiz) erscheint mit langem Text
  (600 Zeichen, mit Zeilenumbrüchen) vollständig: Druckfassung = Feldinhalt, nichts abgeschnitten, Feld selbst
  ausgeblendet; leere Felder fallen weg (samt Beschriftung)
- Druckfassung am Bildschirm ausgeblendet und für VoiceOver unsichtbar (aria-hidden)
- auch nach Reiterwechsel / Laden aktuell (programmatisch gefüllt)
- Supervisor in der Titelzeile nur im Druck
- Statistik: Kopf mit Saison aus den Spieldaten (eine / mehrere / keine), Druckdatum, Kennzahlen, Tabelle mit
  Spaltentiteln auf jeder Seite, keine geteilten Zeilen, „Bewertungen laden“ ausgeblendet, Fusszeile „Vertraulich“;
  Deutsch und Englisch
Aufruf: python3 tests/tools/druck-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

FELDER = ['note_frei_1', 'note_frei_4', 'note_frei_7', 'top_strengths', 'top_workon', 'general_report']
LANG = ('Anfang ' + 'Ein sehr langer Satz mit vielen Wörtern für den Druck. ' * 10).strip() + '\nZweite Zeile\nDritte Zeile Ende'
LADEN = """(async (extra) => { selectStatsTab();
  const n = ['beispiel-v1.0.json','beispiel-v1.0-ohne-evaluation.json','beispiel-v1.1.json','beispiel-v1.1-mit-na.json','beispiel-spiel.json'];
  const f = await Promise.all(n.map(async (x) => new File([await (await fetch('/tests/fixtures/' + x)).text()], x)));
  extra.forEach((e, i) => f.push(new File([JSON.stringify(e)], 'extra' + i + '.json')));
  await handleSeasonFilesUpload({ target: { files: f, value: '' } }); })"""


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    def setze(b, id_, wert):
        b.js(f"(() => {{ const e = document.getElementById({id_!r}); e.value = {wert!r}; e.dispatchEvent(new Event('input', {{ bubbles: true }})); }})()")

    def druckfassung(b, id_):
        return b.js(f"""(() => {{ const f = document.getElementById({id_!r}); const d = f.nextElementSibling;
            const r = d.getBoundingClientRect(); const s = getComputedStyle(d);
            return {{ feld: getComputedStyle(f).display, druck: s.display, text: d.textContent, aria: d.getAttribute('aria-hidden'),
                      ueberlauf: d.scrollHeight - d.clientHeight, sichtbar: r.height > 10, klasse: d.className }}; }})()""")

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            # 1. Bildschirm: Druckfassung ausgeblendet und aria-hidden
            b.fenster(1194, 834)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            for id_ in FELDER:
                setze(b, id_, LANG)
            setze(b, 'general_report', '')
            for id_ in FELDER + ['crew_notes']:
                d = druckfassung(b, id_)
                pruefe(d['druck'] == 'none' and d['aria'] == 'true', f'Bildschirm: Druckfassung von {id_} sichtbar oder nicht aria-hidden ({d})')
            pruefe(b.js("getComputedStyle(document.getElementById('spielTitelSupervisor')).display") == 'none', 'Bildschirm: Supervisor in der Titelzeile sichtbar')

            # 2. Druck: voller Text, nichts abgeschnitten, Feld ausgeblendet; leere Felder fallen weg
            b.fenster(794, 1123, druck=True)
            for id_ in FELDER:
                if id_ == 'general_report':
                    continue
                d = druckfassung(b, id_)
                pruefe(d['feld'] == 'none', f'Druck: Feld {id_} nicht ausgeblendet')
                pruefe(d['druck'] == 'block' and d['sichtbar'], f'Druck: Druckfassung von {id_} nicht sichtbar')
                pruefe(d['text'] == LANG, f'Druck: Text von {id_} nicht vollständig')
                pruefe(d['ueberlauf'] <= 1, f'Druck: {id_} abgeschnitten ({d["ueberlauf"]} px)')
            leer = b.js("getComputedStyle(document.getElementById('general_report').closest('[data-druck-ganz]')).display")
            pruefe(leer == 'none', 'Druck: leerer Rapport samt Beschriftung nicht weggelassen')
            pruefe(druckfassung(b, 'note_frei_2')['druck'] == 'none', 'Druck: leere Kriterien-Notiz nicht weggelassen')
            sup = b.js("(() => { const e = document.getElementById('spielTitelSupervisor'); return [getComputedStyle(e).display, e.textContent]; })()")
            pruefe(sup[0] != 'none' and sup[1] == ' · ' + b.js("t('print_supervisor', { name: 'Muster Peter' })"), f'Druck: Supervisor in der Titelzeile fehlt ({sup})')

            # 3. nach Reiterwechsel / Laden aktuell
            b.fenster(1194, 834)
            b.js('selectRefTab(1); selectRefTab(0);')
            b.fenster(794, 1123, druck=True)
            pruefe(druckfassung(b, 'top_strengths')['text'] == LANG, 'Druck nach Reiterwechsel: Druckfassung nicht aktuell')
            b.oeffnen(srv.basis + '/index.html')
            pruefe(druckfassung(b, 'top_strengths')['text'] == LANG and druckfassung(b, 'note_frei_1')['text'] == LANG, 'Druck nach Neuladen: Druckfassung nicht aktuell')
            # Gespann-Notiz lang
            b.fenster(1194, 834)
            b.js('selectSummaryTab()')
            setze(b, 'crew_notes', LANG)
            b.fenster(794, 1123, druck=True)
            d = druckfassung(b, 'crew_notes')
            pruefe(d['text'] == LANG and d['ueberlauf'] <= 1 and d['sichtbar'], f'Druck Gespann-Notiz nicht vollständig ({d["druck"]}, {d["ueberlauf"]})')

            # 4. Statistik
            for sprache in ('de', 'en'):
                b.fenster(1194, 834)
                daten_setzen(b, srv.basis, sprache=sprache)
                b.oeffnen(srv.basis + '/index.html')
                b.js(LADEN + '([])')
                saison = b.js("document.getElementById('statSaison').textContent")
                pruefe(saison == b.js("t('stats_season', { saison: '2026/27' })"), f'{sprache}: Saison {saison!r}')
                b.fenster(794, 1123, druck=True)
                info = b.js("document.getElementById('statInfo').innerText")
                pruefe(saison in info and b.js("t('stats_printed', { datum: '' })").strip() in info, f'{sprache}: Kopf {info!r}')
                pruefe(b.js("getComputedStyle(document.querySelector('.stat-laden')).display") == 'none', f'{sprache}: „Bewertungen laden“ im Druck')
                fuss = b.js("(() => { const e = document.querySelector('#seasonStatsView .druck-fuss'); return [getComputedStyle(e).display, e.textContent]; })()")
                pruefe(fuss[0] != 'none' and fuss[1] == b.js("t('stats_print_footer')"), f'{sprache}: Fusszeile {fuss}')
                pruefe(fuss[1] in ('Vertraulich – nur für den internen Gebrauch', 'Confidential – for internal use only'), f'{sprache}: Fusszeilen-Text {fuss[1]!r}')
                tab = b.js("(() => { const t = document.querySelector('.stat-tabelle'); const box = document.querySelector('.stat-tabelle-box'); return [getComputedStyle(t.tHead).display, getComputedStyle(t.querySelector('tbody tr')).breakInside, getComputedStyle(box).overflow, t.getBoundingClientRect().width]; })()")
                pruefe(tab[0] == 'table-header-group' and tab[1] == 'avoid' and tab[2] == 'visible' and tab[3] > 600, f'{sprache}: Tabelle im Druck {tab}')
                pruefe(b.js("getComputedStyle(document.querySelector('.stat-kacheln')).gridTemplateColumns").count('px') == 3, f'{sprache}: Kennzahlen nicht in einer Zeile')
                pruefe(b.js("getComputedStyle(document.querySelector('.stat-abzeichen')).printColorAdjust") == 'exact', f'{sprache}: Abzeichen nicht farbig im Druck')
            # mehrere Saisons und ohne Datum
            for extra, soll in (([{'schiedsrichter': 'Alt Test', 'reviewRunde': 'R1', 'scoreGesamt': 70, 'datum': '2025-09-12'}], '2025/26 und 2026/27'),
                                ([{'schiedsrichter': 'Juli Test', 'reviewRunde': 'R1', 'scoreGesamt': 70, 'datum': '2026-07-31'}], '2025/26 und 2026/27'),
                                ([{'schiedsrichter': 'August Test', 'reviewRunde': 'R1', 'scoreGesamt': 70, 'datum': '2026-08-01'}], '2026/27')):
                b.fenster(1194, 834)
                daten_setzen(b, srv.basis)
                b.oeffnen(srv.basis + '/index.html')
                b.js(LADEN + f'({extra!r})')
                ist = b.js("document.getElementById('statSaison').textContent")
                pruefe(ist == f'Saison {soll}', f'Saison mit {extra[0]["datum"]}: {ist!r} statt „Saison {soll}“')
            b.js("""(async () => { selectStatsTab(); await handleSeasonFilesUpload({ target: { files: [new File([JSON.stringify({ schiedsrichter: 'Ohne Datum', reviewRunde: 'R1', scoreGesamt: 70 })], 'x.json')], value: '' } }); })()""")
            pruefe(b.js("document.getElementById('statSaison').textContent") == '', 'Saison trotz fehlendem Datum angezeigt')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Druck-Test: {len(fehler)} Fehler (Textfelder vollständig, leer weg, aria-hidden, Supervisor, Statistik mit Saison/Fusszeile, DE/EN)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
