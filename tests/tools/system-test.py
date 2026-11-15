"""System-Test: Standard-System für neue Spiele aus der Vereins-Einstellung (js/club.js, standardSystem).

Prüft (echte Klicks, wo die App bedient wird):
- leerer Start: System = standardSystem (beim Verein '2-Man'), Knopfreihe und Reiter passend, Startsystem sofort in
  den Spieldaten; eine Bewertung, die vor jeder Spielangabe gesichert wird, bleibt nach dem Neuladen im selben System
- „Spiel zurücksetzen“ (Menü „Mehr“, roter Knopf) bei einem 4-Mann-Spiel: danach standardSystem
- ein gespeichertes 4-Mann-Spiel bleibt nach dem Neuladen 4-Mann
- gespeicherte Daten ohne Angabe zum System (ältere Stände): 4-Mann, Bewertung sichtbar
- Vereins-Einstellung standardSystem: '4-Man' -> leerer Start und Zurücksetzen mit 4-Mann; ungültiger Wert -> 4-Mann
Aufruf: python3 tests/tools/system-test.py   (Abbruchcode 1 bei Fehlern)
"""
import json
import os
import re
import shutil
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

SPEICHER = "JSON.parse(localStorage.getItem('referee_multi_supervision_data') || 'null')"
ZUSTAND = """({ system: currentSystem, seg: segWert('system_typ'), reiter: [...document.querySelectorAll('#tabsContainer [data-reiter]')].filter((e) => SYSTEM_CONFIGS[currentSystem].some((r) => r.id === e.dataset.reiter)).length,   // ohne „Gespann“
  imSpeicher: gameData.global && gameData.global.system_typ })"""


def kopie_mit_verein(wert):
    """Kopie der App mit anderem standardSystem in js/club.js."""
    ziel = tempfile.mkdtemp(prefix='system-')
    shutil.copytree(REPO, ziel, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', 'ergebnisse', '__pycache__'))
    p = os.path.join(ziel, 'js', 'club.js')
    s = open(p, encoding='utf-8').read()
    s, n = re.subn(r"standardSystem:\s*'[^']*'", f"standardSystem: '{wert}'", s)
    assert n == 1, 'standardSystem nicht in js/club.js'
    open(p, 'w', encoding='utf-8').write(s)
    return ziel


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    standard = re.search(r"standardSystem:\s*'([^']+)'", open(os.path.join(REPO, 'js', 'club.js'), encoding='utf-8').read()).group(1)
    anzahl = {'1-Man': 1, '2-Man': 2, '3-Man': 3, '4-Man': 4}

    def leerer_start(b, basis, soll, wo):
        daten_setzen(b, basis, spiel=False)
        b.oeffnen(basis + '/index.html')
        b.taste('Escape')   # „Spiel bearbeiten“ öffnet sich bei neuem Spiel automatisch
        z = b.js(ZUSTAND)
        pruefe(z == {'system': soll, 'seg': soll, 'reiter': anzahl[soll], 'imSpeicher': soll}, f'{wo}: leerer Start {z}, erwartet {soll}')
        return z

    def zuruecksetzen(b, basis, soll, wo):
        daten_setzen(b, basis)   # Beispielspiel mit 4-Mann
        b.oeffnen(basis + '/index.html')
        pruefe(b.js('currentSystem') == '4-Man', f'{wo}: Beispielspiel nicht 4-Mann')
        b.klick('#btnMehr')
        b.klick('#menuReset')
        b.klick('.fenster-knopf-gefahr')   # roter Knopf „Zurücksetzen“ (lädt neu)
        b.js('new Promise((r) => setTimeout(r, 800))')
        b.taste('Escape')
        z = b.js(ZUSTAND)
        pruefe(z['system'] == soll and z['seg'] == soll and z['reiter'] == anzahl[soll], f'{wo}: nach „Spiel zurücksetzen“ {z}, erwartet {soll}')

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            b.fenster(1194, 834)
            pruefe(standard == '2-Man', f'Vereins-Einstellung standardSystem ist {standard!r}, erwartet „2-Man“')

            # 1. Leerer Start; Bewertung vor jeder Spielangabe sichern, neu laden
            leerer_start(b, srv.basis, standard, 'Verein')
            b.js("selectRefTab(0)")
            b.js("(() => { const s = document.getElementById('current_schiri_name'); s.value = 'Meier Luca'; s.dispatchEvent(new Event('change')); })()")
            b.klick(f"label[for=\"{b.js('''document.querySelector('input[name=overall_grade][value=\"80\"]').id''')}\"]")
            gesp = b.js(SPEICHER)
            pruefe(gesp and gesp['global'].get('system_typ') == standard and f'{standard}_r1' in gesp['referees'],
                   f'Erste Bewertung ohne System gespeichert: {gesp and gesp["global"]}')
            b.oeffnen(srv.basis + '/index.html')
            pruefe(b.js('currentSystem') == standard and b.js('getEffectiveRefName()') == 'Meier Luca',
                   f'Nach Neuladen: System {b.js("currentSystem")}, Name {b.js("getEffectiveRefName()")!r}')

            # 2. Spiel zurücksetzen (echte Klicks)
            zuruecksetzen(b, srv.basis, standard, 'Verein')

            # 3. Gespeichertes 4-Mann-Spiel bleibt 4-Mann
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            b.oeffnen(srv.basis + '/index.html')
            pruefe(b.js('currentSystem') == '4-Man' and b.js("segWert('system_typ')") == '4-Man', 'Gespeichertes 4-Mann-Spiel nicht 4-Mann')
            pruefe(b.js(SPEICHER)['global']['system_typ'] == '4-Man', 'Gespeichertes System überschrieben')

            # 4. Ältere Daten ohne Angabe zum System: 4-Mann, Bewertung sichtbar
            for art, entfernen in (('ohne system_typ', "delete d.global.system_typ;"), ('ohne global', "delete d.global;")):
                daten_setzen(b, srv.basis)
                b.js(f"(() => {{ const d = {SPEICHER}; {entfernen} localStorage.setItem('referee_multi_supervision_data', JSON.stringify(d)); }})()")
                b.oeffnen(srv.basis + '/index.html')
                b.js('selectRefTab(0)')
                pruefe(b.js('currentSystem') == '4-Man' and b.js('getEffectiveRefName()') == 'Frei Lea',
                       f'Ältere Daten {art}: System {b.js("currentSystem")}, Name {b.js("getEffectiveRefName()")!r}')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()

    # 5. Andere Vereins-Einstellung: 4-Mann; ungültiger Wert fällt auf 4-Mann zurück
    for wert, soll in (('4-Man', '4-Man'), ('5-Man', '4-Man')):
        ordner = kopie_mit_verein(wert)
        srv = server(ordner, {'/__leer': LEER})
        try:
            with Browser() as b:
                b.fenster(1194, 834)
                leerer_start(b, srv.basis, soll, f'standardSystem {wert!r}')
                if wert == '4-Man':
                    zuruecksetzen(b, srv.basis, soll, f'standardSystem {wert!r}')
                fehler += [f'JS-Fehler ({wert}): {f}' for f in b.fehler if 'Update nicht möglich' not in f]
        finally:
            srv.shutdown()
            shutil.rmtree(ordner, ignore_errors=True)

    for f in fehler:
        print('FEHLER: ', f)
    print(f'System-Test: {len(fehler)} Fehler (leerer Start {standard}, Zurücksetzen, gespeichert bleibt, ältere Daten 4-Mann, '
          f'Verein mit 4-Mann und ungültigem Wert)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
