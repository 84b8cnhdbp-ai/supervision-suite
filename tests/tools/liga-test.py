"""Liga-Test: Neue Spiele starten ohne Liga; ältere Daten ohne Angabe zeigen „National League“ (Datenregel).

Prüft (echte Klicks, wo die App bedient wird):
- leerer Start: „Liga wählen …“ (DE) / „Choose league …“ (EN) gewählt, Liga leer sofort in den Spieldaten vermerkt
- „Bereit zum Sichern?“: unter „Hinweise“ „Liga fehlt – Sichern trotzdem möglich“ (kein Pflichtpunkt); Tipp darauf
  öffnet „Spiel bearbeiten“ mit Fokus auf der Liga; Liga wählen + „Fertig“ -> Hinweis weg, gespeichert, nach Neuladen da
- Fenster „Spiel bearbeiten“: unter der Karte „Spiel“ derselbe Hinweis (DE/EN), weg sobald eine Liga gewählt ist
- „Liga wählen …“ gesperrt: steht da, solange keine Liga gewählt ist, ist aber nicht wählbar (einziger leerer Eintrag,
  disabled). Pfeiltasten verändern eine geschlossene Auswahl im Test-Chrome nicht – darum Prüfung über die Einträge
- „Spiel zurücksetzen“ (Menü „Mehr“, roter Knopf) bei einem Spiel mit Liga: danach ohne Liga
- ältere Daten ohne Angabe zur Liga (ohne spiel_liga, ohne global): „National League“, kein Hinweis; „Fertig“ speichert sie
- Export mit leerer Liga: JSON (spiel_liga "") und CSV (Zeile Liga leer) gehen; die exportierte Datei läuft durch die
  Saison-Statistik
Aufruf: python3 tests/tools/liga-test.py   (Abbruchcode 1 bei Fehlern)
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

SPEICHER = "JSON.parse(localStorage.getItem('referee_multi_supervision_data') || 'null')"
OFFEN = "document.getElementById('spielDialog').open"
WAHL = "(() => { const s = document.getElementById('spiel_liga'); return { wert: s.value, text: s.options[s.selectedIndex] && s.options[s.selectedIndex].textContent }; })()"
HINWEISE = "[...document.querySelectorAll('#bereitListe .bereit-hinweis')].map((x) => [x.dataset.punkt, x.textContent])"
FENSTER_HINWEIS = "(() => { const h = document.getElementById('sfLigaHinweis'); return h && !h.hidden && h.offsetParent !== null ? h.textContent : null; })()"
# alle Einträge mit leerem Wert: [gesperrt?, Text] – erwartet genau einer, gesperrt
LEERE_EINTRAEGE = "[...document.getElementById('spiel_liga').options].filter((o) => o.value === '').map((o) => [o.disabled, o.textContent])"
PFLICHT = "[...document.querySelectorAll('#bereitListe .bereit-fehlt')].map((x) => x.dataset.punkt)"


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            b.fenster(1194, 834)

            def gespeichert():   # Spieldaten im Speicher (leer, wenn nichts gespeichert – Test läuft weiter)
                return (b.js(SPEICHER) or {}).get('global') or {}

            def hinweis_liga():
                return [h for h in b.js(HINWEISE) if h[0] == 'liga']

            # 1. Leerer Start (DE und EN): ohne Liga, Hinweis
            for sprache, wahl, hinweis in (('de', 'Liga wählen …', 'Liga fehlt – Sichern trotzdem möglich'),
                                           ('en', 'Choose league …', 'League missing – saving still possible')):
                daten_setzen(b, srv.basis, spiel=False, sprache=sprache)
                b.oeffnen(srv.basis + '/index.html')
                pruefe(b.js(OFFEN), f'{sprache}: „Spiel bearbeiten“ öffnet sich bei neuem Spiel nicht')
                pruefe(b.js(WAHL) == {'wert': '', 'text': wahl}, f'{sprache}: neues Spiel Liga {b.js(WAHL)}, erwartet leer mit „{wahl}“')
                pruefe(b.js(LEERE_EINTRAEGE) == [[True, wahl]], f'{sprache}: „{wahl}“ nicht gesperrt: {b.js(LEERE_EINTRAEGE)}')
                pruefe(b.js(FENSTER_HINWEIS) == hinweis, f'{sprache}: Hinweis im Fenster {b.js(FENSTER_HINWEIS)!r}, erwartet „{hinweis}“')
                b.taste('Escape')
                pruefe(b.js("gameData.global.spiel_liga") == '', f'{sprache}: leere Liga nicht in den Spieldaten vermerkt: {b.js("gameData.global.spiel_liga")!r}')
                pruefe(hinweis_liga() and hinweis_liga()[0][1].endswith(hinweis), f'{sprache}: Hinweis Liga fehlt: {b.js(HINWEISE)}')
                pruefe('liga' not in b.js(PFLICHT), f'{sprache}: Liga als Pflichtpunkt gezählt')
                pruefe(b.js("[...document.querySelectorAll('#bereitListe li')].findIndex((li) => li.classList.contains('bereit-gruppe'))")
                       < b.js("[...document.querySelectorAll('#bereitListe li')].findIndex((li) => li.querySelector('[data-punkt=liga]'))"),
                       f'{sprache}: Liga-Hinweis nicht unter „Hinweise“')

            # 2. Sprung zum Feld, Liga wählen, Fertig, Neuladen
            daten_setzen(b, srv.basis, spiel=False)
            b.oeffnen(srv.basis + '/index.html')
            b.taste('Escape')
            if hinweis_liga():
                b.klick('#bereitListe [data-punkt=liga]')
            pruefe(b.js(OFFEN) and b.js('document.activeElement.id') == 'spiel_liga', 'Tipp auf „Liga fehlt“ öffnet nicht die Liga im Fenster')
            b.js("(() => { const s = document.getElementById('spiel_liga'); s.value = 'U14-Elit'; s.dispatchEvent(new Event('change')); })()")
            pruefe(b.js(FENSTER_HINWEIS) is None, 'Hinweis im Fenster bleibt nach der Wahl')
            pruefe(b.js(LEERE_EINTRAEGE) == [[True, 'Liga wählen …']], f'Nach der Wahl „Liga wählen …“ wieder wählbar: {b.js(LEERE_EINTRAEGE)}')
            b.klick('#sfFertig')
            pruefe(not hinweis_liga(), 'Hinweis Liga bleibt nach der Wahl')
            pruefe(gespeichert().get('spiel_liga') == 'U14-Elit', f'Gewählte Liga nicht gespeichert: {gespeichert()}')
            b.oeffnen(srv.basis + '/index.html')
            pruefe(b.js(WAHL)['wert'] == 'U14-Elit', f'Nach Neuladen Liga {b.js(WAHL)}')

            # 3. Spiel zurücksetzen (echte Klicks): Beispielspiel mit Liga -> danach ohne Liga
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            pruefe(b.js(WAHL)['wert'] == 'U16-Elit', f'Beispielspiel Liga {b.js(WAHL)}')
            b.klick('#btnMehr'); b.klick('#menuReset'); b.klick('.fenster-knopf-gefahr')
            b.js('new Promise((r) => setTimeout(r, 800))')
            pruefe(b.js(WAHL) == {'wert': '', 'text': 'Liga wählen …'}, f'Nach „Spiel zurücksetzen“ Liga {b.js(WAHL)}')
            b.taste('Escape')
            pruefe(hinweis_liga(), 'Nach „Spiel zurücksetzen“ kein Hinweis Liga')

            # 4. Ältere Daten ohne Angabe zur Liga: „National League“ (Datenregel), kein Hinweis
            for art, entfernen in (('ohne spiel_liga', "delete d.global.spiel_liga;"), ('ohne global', "delete d.global;")):
                daten_setzen(b, srv.basis)
                b.js(f"(() => {{ const d = {SPEICHER}; {entfernen} localStorage.setItem('referee_multi_supervision_data', JSON.stringify(d)); }})()")
                b.oeffnen(srv.basis + '/index.html')
                b.js('selectRefTab(0)')
                pruefe(b.js(WAHL)['wert'] == 'National League', f'Ältere Daten {art}: Liga {b.js(WAHL)}, erwartet „National League“')
                pruefe(not hinweis_liga(), f'Ältere Daten {art}: Hinweis Liga fehlt angezeigt')
                b.klick('#spielTitel')
                pruefe(b.js(WAHL)['wert'] == 'National League', f'Ältere Daten {art}: Fenster zeigt Liga {b.js(WAHL)}')
                pruefe(b.js(FENSTER_HINWEIS) is None, f'Ältere Daten {art}: Hinweis im Fenster angezeigt')
                b.klick('#sfFertig')
                pruefe(gespeichert().get('spiel_liga') == 'National League', f'Ältere Daten {art}: „Fertig“ speichert {gespeichert().get("spiel_liga")!r}')

            # 5. Export mit leerer Liga: JSON und CSV, danach Saison-Statistik mit der exportierten Datei
            daten_setzen(b, srv.basis)
            b.js(f"(() => {{ const d = {SPEICHER}; d.global.spiel_liga = ''; localStorage.setItem('referee_multi_supervision_data', JSON.stringify(d)); }})()")
            b.oeffnen(srv.basis + '/index.html')
            b.js("window.__dl = []; window.downloadBlob = async (blob, name) => __dl.push({ name, text: await blob.text() });")
            b.js('selectRefTab(0)')
            pruefe(b.js(WAHL)['wert'] == '' and hinweis_liga(), f'Gespeicherte leere Liga: {b.js(WAHL)}, Hinweise {b.js(HINWEISE)}')
            b.klick('#btnSichern')
            b.js('exportCSV()')
            b.js('new Promise((r) => setTimeout(r, 300))')
            dl = b.js('__dl')
            js = [d for d in dl if d['name'].endswith('.json')]
            csv = [d for d in dl if d['name'].endswith('.csv')]
            pruefe(len(js) == 1 and json.loads(js[0]['text']).get('spiel_liga') == '', f'Export JSON mit leerer Liga: {[d["name"] for d in dl]}')
            pruefe(len(csv) == 1 and any(z.split(';')[0].strip('"') == 'Liga' and z.split(';')[1].strip('"') == '' for z in csv[0]['text'].splitlines()),
                   f'Export CSV ohne leere Zeile Liga: {csv and csv[0]["text"][:200]}')
            if js:
                score = b.js(f"""(async () => {{
                  let stats = null; const render = window.renderSeasonStatsDashboard;
                  window.renderSeasonStatsDashboard = (s) => {{ stats = s; return render(s); }};
                  selectStatsTab();
                  await handleSeasonFilesUpload({{ target: {{ files: [new File([{json.dumps(js[0]['text'])}], {json.dumps(js[0]['name'])})], value: '' }} }});
                  const name = {json.dumps(json.loads(js[0]['text'])['schiedsrichter'])};
                  return stats && stats[name] && stats[name].R1 ? stats[name].R1.scoreGesamt : null;
                }})()""")
                pruefe(isinstance(score, (int, float)) and not b.js("[...document.querySelectorAll('.toast')].some((e) => e.classList.contains('toast-fehler'))"),
                       f'Saison-Statistik mit leerer Liga: Score {score!r} oder Datei übersprungen')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()

    for f in fehler:
        print('FEHLER: ', f)
    print(f'Liga-Test: {len(fehler)} Fehler (neues Spiel ohne Liga DE/EN, Hinweis und Sprung, Hinweis im Fenster, Sperre, Zurücksetzen, '
          f'ältere Daten „National League“, Export und Statistik mit leerer Liga)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
