"""Fenster-Test: eigene Fenster und Hinweise statt alert/confirm/prompt (Etappe 2.2).

Bedient die App mit echten Klicks und Tasten (Enter, Esc) und prüft:
- im Code und zur Laufzeit kein alert, confirm oder prompt mehr
- Sichern mit fehlenden Feldern: Fenster mit Liste; Tipp auf einen Eintrag springt zum Feld
- Zurücksetzen: Knopf rot, „Abbrechen“ vorgewählt; Enter und Esc löschen nichts; nur der rote Knopf löscht
- Szene mit Spielzeit: Eingabefeld vorbelegt; Enter fügt hinzu, Esc bricht ab
- Kader importiert: Hinweis; Kaderdatei unlesbar: Fenster
- Statistik mit unlesbarer Datei: Hinweis
Auf Deutsch und Englisch. Aufruf: python3 tests/tools/fenster-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

FENSTER = "document.querySelector('dialog.fenster[open]')"


def main():
    fehler = []

    def pruefe(bedingung, text):
        if not bedingung:
            fehler.append(text)

    # 1. Im Code keine Browser-Popups mehr
    for name in sorted(os.listdir(os.path.join(REPO, 'js'))):
        src = open(os.path.join(REPO, 'js', name), encoding='utf-8').read()
        for m in re.finditer(r'(?<![\w.])(alert|confirm|prompt)\s*\(', src):
            fehler.append(f'js/{name}: {m.group(1)}() im Code')

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            for sprache in ('de', 'en'):
                def start():
                    b.fenster(1194, 834)
                    daten_setzen(b, srv.basis, sprache=sprache)
                    b.oeffnen(srv.basis + '/index.html')
                    b.js("window.__popups = []; for (const f of ['alert', 'confirm', 'prompt']) window[f] = (m) => { __popups.push(f + ': ' + m); return null; };")
                    b.js("window.__downloads = []; window.downloadBlob = (blob, name) => __downloads.push(name);")
                L = sprache.upper() + ': '
                T = lambda k: b.js(f"t({k!r})")

                # 2. Sichern mit fehlenden Feldern (Linesperson 1: Gesamteinschätzung fehlt)
                start()
                b.js('selectRefTab(2)')
                b.klick('#btnSichern')   # „Sichern“ in der Werkzeugleiste
                pruefe(b.js(FENSTER + ' !== null'), L + 'Sichern ohne Gesamteinschätzung: kein Fenster')
                pruefe(b.js(f"{FENSTER}.querySelector('.fenster-titel').innerText") == T('export_missing_title'), L + 'Sichern: falscher Titel')
                eintraege = b.js(f"[...{FENSTER}.querySelectorAll('.fenster-eintrag')].map((e) => e.innerText.replace('›', '').trim())")
                pruefe(eintraege == [T('missing_grade')], L + f'Sichern: Liste {eintraege}, erwartet nur Gesamteinschätzung')
                b.klick('dialog.fenster[open] .fenster-eintrag')
                b.js('new Promise((r) => setTimeout(r, 600))')
                pruefe(b.js(FENSTER + ' === null'), L + 'Sichern: Fenster nach Tipp auf Eintrag nicht zu')
                pruefe(b.js("document.activeElement && document.activeElement.name") == 'overall_grade', L + 'Sichern: Fokus nicht in der Gesamteinschätzung')
                pruefe(b.js("document.getElementById('gradeBox').classList.contains('feld-hervorheben')"),
                       L + 'Sichern: Gesamteinschätzung nicht hervorgehoben')
                r = b.js("(() => { const r = document.getElementById('gradeBox').getBoundingClientRect(); return [r.top, r.bottom, innerHeight]; })()")
                pruefe(r[0] < r[2] and r[1] > 0, L + f'Sichern: Gesamteinschätzung nach Sprung nicht sichtbar {r}')
                pruefe(b.js('__downloads.length') == 0, L + 'Sichern: trotz fehlender Felder exportiert')

                # neues leeres 2-Mann-Spiel ohne Datum: Name, Datum und Note fehlen
                b.js("switchSystem('2-Man'); document.getElementById('spiel_datum').value = ''; handleGlobalDateTimeChange();")
                b.klick('#btnSichern')
                eintraege = b.js(f"[...{FENSTER}.querySelectorAll('.fenster-eintrag')].map((e) => e.innerText.replace('›', '').trim())")
                pruefe(eintraege == [T('missing_name'), T('missing_date'), T('missing_grade')], L + f'Sichern (leer): Liste {eintraege}')
                b.klick('dialog.fenster[open] .fenster-eintrag:nth-of-type(1)')
                b.js("document.querySelectorAll('dialog.fenster[open] .fenster-eintrag')[1]?.click()")
                b.js('new Promise((r) => setTimeout(r, 600))')
                pruefe(b.js("document.activeElement.id") == 'current_schiri_name', L + f"Sichern: Sprung zum Namen landet bei {b.js('document.activeElement.id')}")
                b.klick('#btnSichern')
                b.js(f"{FENSTER}.querySelectorAll('.fenster-eintrag')[1].click()")
                b.js('new Promise((r) => setTimeout(r, 600))')
                pruefe(b.js("document.activeElement.id") == 'spiel_datum', L + f"Sichern: Sprung zum Datum landet bei {b.js('document.activeElement.id')}")

                # 3. Zurücksetzen
                start()
                daten = lambda: b.js("localStorage.getItem('referee_multi_supervision_data') !== null")
                b.klick('#btnMehr'); b.klick('#menuReset')
                pruefe(b.js(FENSTER + ' !== null'), L + 'Zurücksetzen: kein Fenster')
                pruefe(b.js("document.activeElement.innerText") == T('dlg_cancel'), L + f"Zurücksetzen: vorgewählt ist „{b.js('document.activeElement.innerText')}“ statt Abbrechen")
                rot = b.js(f"getComputedStyle({FENSTER}.querySelector('.fenster-knopf-gefahr')).backgroundColor")
                pruefe(rot == 'rgb(180, 35, 24)', L + f'Zurücksetzen: Knopf nicht rot ({rot})')
                b.taste('Enter')
                pruefe(b.js(FENSTER + ' === null') and daten(), L + 'Zurücksetzen: Enter hat nicht nur abgebrochen')
                b.klick('#btnMehr'); b.klick('#menuReset'); b.taste('Escape')
                pruefe(b.js(FENSTER + ' === null') and daten(), L + 'Zurücksetzen: Esc hat nicht nur abgebrochen')
                b.klick('#btnMehr'); b.klick('#menuReset'); b.klick('dialog.fenster[open] .fenster-knopf:not(.fenster-knopf-gefahr)')
                pruefe(daten(), L + 'Zurücksetzen: Abbrechen-Knopf hat gelöscht')
                b.klick('#btnMehr'); b.klick('#menuReset'); b.klick('dialog.fenster[open] .fenster-knopf-gefahr')
                b.js('new Promise((r) => setTimeout(r, 800))')
                pruefe(not daten(), L + 'Zurücksetzen: roter Knopf hat nicht gelöscht')

                # 4. Szene mit Spielzeit
                start()
                b.klick("button.stamp-btn[onclick*=\"note_2\"]")
                pruefe(b.js(FENSTER + ' !== null'), L + 'Szene: kein Fenster')
                pruefe(b.js("document.activeElement.classList.contains('fenster-eingabe') && document.activeElement.value") == 'P1 00:00',
                       L + 'Szene: Eingabe nicht vorbelegt/fokussiert')
                b.js("document.activeElement.select()"); b.tippen('P2 08:34'); b.taste('Enter')
                pruefe(b.js("document.getElementById('note_2').value") == '[P2 08:34] ', L + f"Szene: Notiz ist {b.js('document.getElementById(\"note_2\").value')!r}")
                pruefe(b.js("JSON.parse(localStorage.getItem('referee_multi_supervision_data')).referees['4-Man_h1'].note_2") == '[P2 08:34] ',
                       L + 'Szene: nicht gespeichert')
                b.klick("button.stamp-btn[onclick*=\"note_2\"]"); b.taste('Escape')
                pruefe(b.js("document.getElementById('note_2').value") == '[P2 08:34] ', L + 'Szene: Esc hat trotzdem etwas hinzugefügt')

                # 5. Kader-Import
                b.js("""handleKaderUpload({ target: { files: [new File(['Meier Luca\\nKeller Nina\\n'], 'k.txt')], value: '' } })""")
                b.js('new Promise((r) => setTimeout(r, 300))')
                toast = b.js("[...document.querySelectorAll('.toast')].map((e) => e.innerText).join(' | ')")
                pruefe(T('kader_imported').replace('{n}', '2') in toast, L + f'Kader: Hinweis fehlt ({toast!r})')
                b.js("""handleKaderUpload({ target: { files: [new File(['{kaputt'], 'k.json')], value: '' } })""")
                b.js('new Promise((r) => setTimeout(r, 300))')
                pruefe(b.js(f"{FENSTER} && {FENSTER}.querySelector('.fenster-titel').innerText") == T('kader_error_title'), L + 'Kader unlesbar: kein Fenster')
                b.taste('Enter')
                pruefe(b.js(FENSTER + ' === null'), L + 'Kader unlesbar: Enter schliesst das Fenster nicht')

                # 6. Statistik mit einer unlesbaren Datei
                b.js("""(async () => { selectStatsTab(); await handleSeasonFilesUpload({ target: { value: '', files: [
                          new File([await (await fetch('/tests/fixtures/beispiel-v1.1.json')).text()], 'a.json'),
                          new File(['kein json'], 'kaputt.json')] } }); })()""")
                b.js('new Promise((r) => setTimeout(r, 300))')
                toast = b.js("[...document.querySelectorAll('.toast')].map((e) => e.innerText).join(' | ')")
                pruefe(T('stats_skipped').replace('{n}', '1') in toast, L + f'Statistik: Hinweis zu übersprungener Datei fehlt ({toast!r})')

                pruefe(b.js('__popups.length') == 0, L + f"Browser-Popups aufgerufen: {b.js('__popups')}")
            # erwartet: Warnung der App zur absichtlich kaputten Testdatei
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f and 'kaputt.json' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Fenster-Test: {len(fehler)} Fehler (DE und EN, echte Klicks und Tasten)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
