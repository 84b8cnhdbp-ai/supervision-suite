"""Spiel-Test (Etappe 2.6): Fenster „Spiel bearbeiten“ und Titel – mit echten Klicks und Tasten.

Prüft:
- Zugang über den Titel und „Mehr“ → „Spiel bearbeiten“; Reihenfolge der Felder; Spielnummer mit Zifferntastatur,
  aber ohne Einschränkung auf Ziffern
- „Abbrechen“ und Esc verwerfen alles (auch ein späteres Speichern übernimmt nichts Verworfenes); „Fertig“ speichert
- Begegnung = „CLUB.kurz – Gegner“; alte Begegnung bleibt unverändert, solange sie nicht geändert wird
- Visum (Ort, Datum, Supervisor) wird wie früher nachgeführt
- Namen und Durchgang je Rolle landen in Daten, Reitern und Formular
- Systemwechsel: Rückfrage nur, wenn im bisherigen System Bewertungen stehen; „Abbrechen“ vorgewählt; Daten bleiben
- Spielnummer fehlt = Hinweis (getrennt von den Pflichtpunkten), Sichern bleibt möglich; Sprung öffnet das Fenster
- automatisch öffnen nur ohne Spiel (kein Gegner und kein Datum)
- Fenster passt auf 768 / 834 / 1194 px, Knöpfe mind. 44 px; Deutsch und Englisch
Aufruf: python3 tests/tools/spiel-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER, fuehre_aus, pruefliste  # noqa: E402

GESPEICHERT = "JSON.parse(localStorage.getItem('referee_multi_supervision_data'))"
OFFEN = "document.getElementById('spielDialog').open"


def main():
    fehler = pruefliste()

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            def start(w=1194, h=834, sprache='de', spiel=True):
                b.fenster(w, h)
                daten_setzen(b, srv.basis, spiel=spiel, sprache=sprache)
                b.oeffnen(srv.basis + '/index.html')
                b.js("window.__dl = []; window.downloadBlob = (blob, name) => __dl.push(name);")

            def setze(id_, wert):
                b.js(f"(() => {{ const e = document.getElementById({id_!r}); e.value = {wert!r}; e.dispatchEvent(new Event('input')); e.dispatchEvent(new Event('change')); }})()")

            # 1. Zugang, Reihenfolge, Spielnummer
            start()
            pruefe(not b.js(OFFEN), 'Fenster öffnet sich, obwohl ein Spiel erfasst ist')
            b.klick('#spielTitel')
            pruefe(b.js(OFFEN), 'Titel antippen öffnet das Fenster nicht')
            reihe = b.js("[...document.querySelectorAll('#spielDialog .sf-label, #spielDialog .feld-label, #spielDialog .sf-rolle-name')].map((e) => e.textContent.trim())")
            erwartet = ['Spielnummer', 'Liga / Stufe', 'Gegner', 'Datum & Zeit', 'Spielort / Arena', 'Schiedsrichter-System',
                        'Head Referee 1', 'Head Referee 2', 'Linesperson 1', 'Linesperson 2', 'Supervisor / Coach']
            pruefe(reihe == erwartet, f'Reihenfolge der Felder: {reihe}')
            pruefe(b.js("document.activeElement.id") == 'spiel_id', 'Fokus beim Öffnen nicht auf der Spielnummer')
            pruefe(b.js("document.getElementById('spiel_id').inputMode") == 'numeric', 'Spielnummer ohne Zifferntastatur')
            pruefe(not b.js("document.getElementById('spiel_id').pattern") and b.js("document.getElementById('spiel_id').type") == 'text',
                   'Spielnummer auf Ziffern eingeschränkt')
            b.taste('Escape')
            b.klick('#btnMehr'); b.klick('#menuSpiel')
            pruefe(b.js(OFFEN), '„Mehr“ → „Spiel bearbeiten“ öffnet das Fenster nicht')
            b.taste('Escape')

            # 2. Abbrechen / Esc verwerfen
            vorher = b.js(GESPEICHERT)
            for art in ('Abbrechen', 'Escape'):
                b.klick('#spielTitel')
                setze('spiel_id', '11111'); setze('spiel_gegner', 'Verworfen'); setze('spiel_ort', 'Woanders'); setze('supervisor_name', 'Niemand')
                b.js("(() => { const s = document.getElementById('sf_name_l2'); s.value = 'Meier Luca'; s.dispatchEvent(new Event('change')); })()")
                b.klick("label[for='system_typ__1']")
                if art == 'Abbrechen':
                    b.klick('#sfAbbrechen')
                else:
                    b.taste('Escape')
                pruefe(not b.js(OFFEN), f'{art}: Fenster bleibt offen')
                pruefe(b.js(GESPEICHERT) == vorher, f'{art}: Änderungen wurden gespeichert')
                pruefe(b.js('currentSystem') == '4-Man', f'{art}: System gewechselt')
                b.js("saveGlobalState()")   # z. B. durch Gespann-Notiz: darf nichts Verworfenes mitnehmen
                pruefe(b.js(GESPEICHERT)['global'] == vorher['global'], f'{art}: späteres Speichern übernimmt Verworfenes')

            # 3. Fertig: alte Begegnung bleibt, Spieldaten und Visum
            b.klick('#spielTitel'); b.klick('#sfFertig')
            pruefe(b.js(GESPEICHERT)['global']['spiel_paarung'] == 'Team Blau vs. Team Rot', 'alte Begegnung wurde ohne Änderung umgeschrieben')
            b.klick('#spielTitel')
            setze('spiel_gegner', 'Gastteam'); setze('spiel_id', 'A-123'); setze('spiel_ort', 'Neue Halle')
            setze('spiel_datum', '2026-12-05T18:00'); setze('supervisor_name', 'Beispiel Anna')
            b.js("document.getElementById('spiel_liga').value = 'U14-Elit'")
            b.klick('#sfFertig')
            g = b.js(GESPEICHERT)['global']
            kurz = b.js('CLUB.kurz')
            pruefe(g['spiel_paarung'] == f'{kurz} – Gastteam', f"Begegnung: {g['spiel_paarung']!r}")
            pruefe((g['spiel_id'], g['spiel_ort'], g['spiel_datum'], g['supervisor_name'], g['spiel_liga']) ==
                   ('A-123', 'Neue Halle', '2026-12-05T18:00', 'Beispiel Anna', 'U14-Elit'), f'Spieldaten: {g}')
            ref = b.js(GESPEICHERT)['referees']['4-Man_h1']
            pruefe(ref['visum_ort_datum'] == 'Neue Halle, 05.12.2026' and ref['visum_name'] == 'Beispiel Anna', f"Visum: {ref['visum_ort_datum']!r} / {ref['visum_name']!r}")
            titel = b.js("document.getElementById('spielTitelName').textContent + ' | ' + document.getElementById('spielTitelInfo').textContent")
            pruefe(f'{kurz} – Gastteam' in titel and 'Nr. A-123' in titel and 'U14-Elit' in titel, f'Titel: {titel}')
            pruefe(f'{kurz} – Gastteam' in b.js("document.getElementById('navSpiel').innerText"), 'Seitenleiste nicht nachgeführt')
            b.klick('#spielTitel')
            pruefe(b.js("document.getElementById('spiel_gegner').value") == 'Gastteam' and b.js("!document.getElementById('sfPraefix').hidden"),
                   'Gegner beim erneuten Öffnen nicht ohne Kürzel')
            b.taste('Escape')

            # 4. Namen und Durchgang je Rolle
            b.klick('#spielTitel')
            b.js("(() => { const s = document.getElementById('sf_name_l2'); s.value = 'Keller Nina'; s.dispatchEvent(new Event('change')); })()")
            b.klick("label[for='sf_round_l2__1']")   # R2
            b.js("(() => { const s = document.getElementById('sf_name_h2'); s.value = '_CUSTOM_'; s.dispatchEvent(new Event('change')); })()")
            setze('sf_custom_h2', 'Neu Gast')
            b.klick('#sfFertig')
            r = b.js(GESPEICHERT)['referees']
            pruefe(r['4-Man_l2']['name'] == 'Keller Nina' and r['4-Man_l2']['review_round'] == 'R2', f"L2: {r.get('4-Man_l2')}")
            pruefe(r['4-Man_l2'].get('perf_1') == '80' and r['4-Man_l2'].get('role') == 'Linesperson 2', 'L2: neuer Eintrag ohne Standardwerte/Rolle')
            pruefe(r['4-Man_h2']['name'] == 'Neu Gast' and r['4-Man_h2']['overall_grade'] == '20', 'H2: Name nicht übernommen oder Bewertung verloren')
            reiter = b.js("[...document.querySelectorAll('#tabsContainer [role=tab]')].map((t) => t.textContent)")
            pruefe(reiter[1] == 'H2 · Neu' and reiter[3] == 'L2 · Keller', f'Reiter: {reiter}')
            b.js('selectRefTab(3)')
            pruefe(b.js("getEffectiveRefName()") == 'Keller Nina' and b.js("segWert('current_review_round')") == 'R2', 'Formular L2 zeigt Name/Durchgang nicht')

            # 5. Systemwechsel mit Rückfrage
            b.klick('#spielTitel'); b.klick("label[for='system_typ__1']")
            pruefe(b.js("document.querySelectorAll('#sfRollen .sf-rolle').length") == 2, 'Systemwahl zeigt nicht sofort die 2 Rollen')
            b.klick('#sfFertig')
            text = b.js("document.querySelector('dialog.fenster[open] .fenster-text') && document.querySelector('dialog.fenster[open] .fenster-text').textContent")
            pruefe(text and '4-Mann' in text and '2-Mann' in text, f'Rückfrage fehlt oder ohne Systeme: {text!r}')
            pruefe(b.js("document.activeElement.textContent") == 'Abbrechen', 'Rückfrage: „Abbrechen“ nicht vorgewählt')
            b.taste('Enter')
            pruefe(b.js(OFFEN) and b.js('currentSystem') == '4-Man', 'Rückfrage Abbrechen: Fenster zu oder System gewechselt')
            b.klick('#sfFertig'); b.klick('dialog.fenster[open] .fenster-knopf-primaer')
            pruefe(not b.js(OFFEN) and b.js('currentSystem') == '2-Man', 'Rückfrage Wechseln: System nicht gewechselt')
            pruefe(b.js(GESPEICHERT)['referees']['4-Man_h1']['name'] == 'Frei Lea', 'Bewertungen des 4-Mann-Systems verloren')
            b.klick('#spielTitel'); b.klick("label[for='system_typ__2']"); b.klick('#sfFertig')   # 2-Mann leer -> 3-Mann ohne Rückfrage
            pruefe(b.js('currentSystem') == '3-Man' and not b.js("!!document.querySelector('dialog.fenster[open]')"), 'Wechsel ohne Bewertungen fragt nach')
            b.js("switchSystem('4-Man')")

            # 6. Spielnummer als Hinweis, getrennt von den Pflichtpunkten
            start(834, 1194)
            b.klick('#spielTitel'); setze('spiel_id', ''); b.klick('#sfFertig')
            pruefe(b.js("document.querySelectorAll('#bereitListe .bereit-fehlt').length") == 0, 'Spielnummer als Pflichtpunkt gezählt')
            pruefe(b.js("[...document.querySelectorAll('#bereitListe .bereit-hinweis')].map((x) => x.dataset.punkt)") == ['spielnr'], 'Hinweis Spielnummer fehlt')
            pruefe(b.js("document.getElementById('bereitChip').textContent") == b.js("t('ready_chip_hint', { n: 1 })"), 'Bereit-Zeichen ohne „· 1 Hinweis“')
            b.klick('#btnSichern')
            pruefe(b.js('__dl.length') == 1 and not b.js("!!document.querySelector('dialog.fenster[open]')"), 'Sichern ohne Spielnummer nicht möglich')
            b.klick('#bereitChip')
            pruefe(b.js(OFFEN) and b.js('document.activeElement.id') == 'spiel_id', 'Bereit-Zeichen (Hinweis) öffnet nicht die Spielnummer')
            b.taste('Escape')
            # Datum fehlt: Pflicht, Sprung öffnet das Fenster bei „Datum & Zeit“
            b.klick('#spielTitel'); setze('spiel_datum', ''); b.klick('#sfFertig')
            pruefe(b.js("[...document.querySelectorAll('#bereitListe .bereit-fehlt')].map((x) => x.dataset.punkt)") == ['datum'], 'Datum fehlt nicht als Pflicht')
            b.klick('#bereitChip')
            pruefe(b.js(OFFEN) and b.js('document.activeElement.id') == 'spiel_datum', 'Sprung zum Datum öffnet nicht das Fenster')
            b.taste('Escape')

            # 7. Automatisch öffnen nur ohne Spiel
            start(834, 1194, spiel=False)
            pruefe(b.js(OFFEN), 'Ohne Spiel öffnet sich das Fenster nicht automatisch')
            # neues Spiel: System aus der Vereins-Einstellung, im Fenster vorgewählt (ausdrücklich, nicht still 4-Mann)
            pruefe(b.js('currentSystem') == b.js('CLUB.standardSystem') == b.js("segWert('system_typ')"),
                   f"Neues Spiel: System {b.js('currentSystem')} statt {b.js('CLUB.standardSystem')}")
            setze('spiel_gegner', 'Gastteam'); b.klick('#sfFertig')
            b.oeffnen(srv.basis + '/index.html')
            pruefe(not b.js(OFFEN), 'Fenster öffnet sich trotz erfasstem Gegner')

            # 8. Grössen und Englisch
            for w, h, sprache in ((768, 1024, 'en'), (834, 1194, 'de'), (1194, 834, 'en')):
                start(w, h, sprache)
                b.klick('#spielTitel')
                r = b.js("(() => { const d = document.getElementById('spielDialog').getBoundingClientRect(); const i = document.querySelector('.sf-inhalt'); return [d.left, d.right, d.top, d.bottom, innerWidth, innerHeight, i.scrollWidth - i.clientWidth]; })()")
                pruefe(r[0] >= 0 and r[1] <= r[4] and r[2] >= 0 and r[3] <= r[5] and r[6] <= 1, f'{w}px: Fenster passt nicht ({r})')
                klein = b.js("[...document.querySelectorAll('#spielDialog button, #spielDialog select')].filter((e) => e.offsetParent && e.getBoundingClientRect().height < 43.5).map((e) => e.id || e.textContent.trim())")
                pruefe(not klein, f'{w}px: zu kleine Ziele im Fenster: {klein}')
                if sprache == 'en':
                    pruefe(b.js("document.getElementById('spielDialogTitel').textContent") == 'Edit game' and b.js("document.getElementById('sfFertig').textContent") == 'Done',
                           f'{w}px: Fenster nicht englisch')
                b.taste('Escape')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Spiel-Test: {len(fehler)} Fehler (Zugang, Reihenfolge, Abbrechen/Fertig, Begegnung, Rollen, Systemwechsel, Hinweis, automatisch öffnen, Grössen, DE/EN)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    fuehre_aus(main)   # nach Verbindungsabbruch zu Chrome einmal von vorne (werkzeug.py)
