"""Szene-Test (Etappe 2.7): Fenster „Szene“, Chips, freier Text – mit echten Klicks und Tasten.

Prüft:
- Hinzufügen: Spielzeit freiwillig; „834“ → 08:34; gültig bis 20:00, Sekunden unter 60; ungültige Zeit wird nicht
  gespeichert; ohne Zeit „[P2] Text“; Zeilenumbrüche in der Notiz werden Leerzeichen (jede Szene eine Zeile)
- Speicherformat genau „[P2 08:34] Text“, neue Szenen am Ende der Notiz (Reihenfolge der Eingabe)
- Anzeige sortiert: Drittel 1–3, OT; Restzeit absteigend; ohne Zeit am Ende des Drittels; unlesbare alte Angaben ganz
  am Ende in bisheriger Reihenfolge; Druck gleich sortiert
- Ändern über den Chip: Zeile bleibt an derselben Stelle; alte Angabe wird ersetzt; Löschen mit Rückfrage
- freier Text getrennt; ohne Bearbeitung bleibt die Notiz Zeichen für Zeichen gleich
- zuletzt benutztes Drittel vorgewählt, bei anderem Spiel wieder „1.“
- Abbrechen/Esc ändern nichts; lange Notiz höchstens zwei Zeilen im Chip, voller Text im Fenster
- 768 / 834 / 1194 px, Ziele mind. 44 px, Deutsch und Englisch
Aufruf: python3 tests/tools/szene-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

GESPEICHERT = "JSON.parse(localStorage.getItem('referee_multi_supervision_data')).referees['4-Man_h1']"
OFFEN = "document.getElementById('szeneDialog').open"
GEMISCHT = ('[P1 05:12] Erfundene Szene\\nfreier Text dazwischen\\n[2. Drittel 8:34] alt eins\\n[P2] ohne Zeit\\n'
            '[P2 15:40] mittel\\n[P1 18:02] früh\\n[OT 03:00] Verlängerung\\n[alt zwei] zweite alte\\n[P2 20:00] Beginn')


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            def start(w=1194, h=834, sprache='de'):
                b.fenster(w, h)
                daten_setzen(b, srv.basis, sprache=sprache)
                b.oeffnen(srv.basis + '/index.html')

            notiz = lambda k: b.js(f"document.getElementById('note_{k}').value")
            gespeichert = lambda k: b.js(GESPEICHERT).get(f'note_{k}')
            chips = lambda k: b.js(f"[...document.querySelectorAll('#szenen_{k} .szene-chip')].map((c) => c.querySelector('.szene-zeit').textContent + '|' + c.querySelector('.szene-text').textContent)")

            def szene(k, zeit='', text='', drittel=None, enter=True):
                b.klick(f".szene-knopf[data-szene='{k}']")
                if drittel is not None:
                    b.klick(f"label[for='szene_drittel__{drittel}']")
                    b.js("document.getElementById('szeneZeit').focus()")
                if zeit:
                    b.tippen(zeit)
                if text:
                    b.js(f"(() => {{ const n = document.getElementById('szeneNotiz'); n.value = {text!r}; }})()")
                if enter:
                    b.js("document.getElementById('szeneZeit').focus()")
                    b.taste('Enter')

            # 1. Unverändert laden: alte Notiz als Chip, Notiz bleibt gleich
            start()
            pruefe(chips(1) == ['P1 05:12|Erfundene Szene'], f'alte Notiz als Chip: {chips(1)}')
            pruefe(b.js("document.getElementById('note_frei_1').value") == '', 'freier Text nicht leer')
            b.js('selectRefTab(1); selectRefTab(0);')
            pruefe(gespeichert(1) == '[P1 05:12] Erfundene Szene', 'Notiz durch Laden/Speichern verändert')

            # 2. Hinzufügen und Speicherformat
            szene(2, '834', 'Zeile eins\nZeile zwei')
            pruefe(not b.js(OFFEN), 'Hinzufügen schliesst das Fenster nicht')
            pruefe(gespeichert(2) == '[P1 08:34] Zeile eins Zeile zwei', f'Speicherformat/Zeilenumbruch: {gespeichert(2)!r}')
            szene(2, '', 'ohne Zeit', drittel=1)
            pruefe(gespeichert(2).split('\n')[-1] == '[P2] ohne Zeit', f'ohne Zeit: {gespeichert(2)!r}')
            szene(2, '1802', 'früher im ersten', drittel=0)
            pruefe(gespeichert(2).split('\n') == ['[P1 08:34] Zeile eins Zeile zwei', '[P2] ohne Zeit', '[P1 18:02] früher im ersten'],
                   f'Reihenfolge der Eingabe nicht gespeichert: {gespeichert(2)!r}')
            pruefe(chips(2) == ['P1 18:02|früher im ersten', 'P1 08:34|Zeile eins Zeile zwei', 'P2|ohne Zeit'], f'Anzeige sortiert: {chips(2)}')

            # 3. Zeiten prüfen
            for eingabe, soll in (('8:34', '08:34'), ('2000', '20:00'), ('5', '00:05'), ('0959', '09:59')):
                b.klick(".szene-knopf[data-szene='3']"); b.tippen(eingabe); b.js("document.getElementById('szeneNotiz').focus()")
                ist = b.js("document.getElementById('szeneZeit').value")
                pruefe(ist == soll, f'Zeit „{eingabe}“ wird „{ist}“ statt „{soll}“')
                b.taste('Escape')
            for eingabe in ('2001', '1260', '2100', 'abc', '99:99'):
                vorher = notiz(3)
                b.klick(".szene-knopf[data-szene='3']"); b.tippen(eingabe); b.taste('Enter')
                pruefe(b.js(OFFEN) and not b.js("document.getElementById('szeneFehler').hidden") and b.js('document.activeElement.id') == 'szeneZeit',
                       f'ungültige Zeit „{eingabe}“ nicht abgefangen')
                b.taste('Escape')
                pruefe(notiz(3) == vorher, f'ungültige Zeit „{eingabe}“ trotzdem gespeichert')
            # Abbrechen-Knopf
            b.klick(".szene-knopf[data-szene='3']"); b.tippen('1000'); b.klick('#szeneAbbrechen')
            pruefe(notiz(3) == '' and not b.js(OFFEN), 'Abbrechen hat gespeichert / Fenster offen')

            # 4. Sortierung mit gemischter Notiz, Druck gleich
            b.js(f"(() => {{ document.getElementById('note_4').value = '{GEMISCHT}'; saveCurrentRefData(); zeigeSzenen(4); }})()")
            erwartet = ['P1 18:02|früh', 'P1 05:12|Erfundene Szene', 'P2 20:00|Beginn', 'P2 15:40|mittel', 'P2|ohne Zeit',
                        'OT 03:00|Verlängerung', '2. Drittel 8:34|alt eins', 'alt zwei|zweite alte']
            pruefe(chips(4) == erwartet, f'Sortierung: {chips(4)}')
            pruefe(b.js("document.getElementById('note_frei_4').value") == 'freier Text dazwischen', 'freier Text nicht getrennt')
            # freien Text bearbeiten: Szenen (bisherige Reihenfolge) + freier Text
            b.js("(() => { const f = document.getElementById('note_frei_4'); f.value = 'neuer freier Text'; f.dispatchEvent(new Event('input')); })()")
            zeilen = gespeichert(4).split('\n')
            pruefe(zeilen[:8] == [z for z in GEMISCHT.split('\\n') if z.startswith('[')] and zeilen[8:] == ['neuer freier Text'],
                   f'Notiz nach Bearbeiten des freien Texts: {zeilen}')

            # 5. Ändern an derselben Stelle, alte Angabe ersetzen, Löschen
            b.js(f"(() => {{ document.getElementById('note_4').value = '{GEMISCHT}'; saveCurrentRefData(); zeigeSzenen(4); }})()")
            b.klick("#szenen_4 .szene-chip[data-zeile='4']")   # [P2 15:40] mittel
            pruefe(b.js(OFFEN) and b.js("document.getElementById('szeneZeit').value") == '15:40' and b.js("segWert('szene_drittel')") == 'P2'
                   and b.js("document.getElementById('szeneNotiz').value") == 'mittel', 'Ändern: Fenster nicht vorbelegt')
            b.js("document.getElementById('szeneNotiz').value = 'geändert'")
            b.klick('#szeneOk')
            zeilen = gespeichert(4).split('\n')
            pruefe(zeilen[4] == '[P2 15:40] geändert' and len(zeilen) == 9, f'Ändern: Zeile nicht an derselben Stelle: {zeilen}')
            b.klick("#szenen_4 .szene-chip[data-zeile='2']")   # alte Angabe
            pruefe(not b.js("document.getElementById('szeneAlt').hidden"), 'alte Angabe: Hinweis fehlt')
            b.klick("label[for='szene_drittel__1']"); b.js("document.getElementById('szeneZeit').focus()"); b.tippen('834'); b.klick('#szeneOk')
            pruefe(gespeichert(4).split('\n')[2] == '[P2 08:34] alt eins', f"alte Angabe nicht ersetzt: {gespeichert(4).split(chr(10))[2]!r}")
            b.klick("#szenen_4 .szene-chip[data-zeile='5']")   # [P1 18:02] früh
            b.klick('#szeneLoeschen')
            pruefe(b.js("document.activeElement.textContent") == b.js("t('dlg_cancel')"), 'Löschen: „Abbrechen“ nicht vorgewählt')
            b.taste('Enter')
            pruefe(len(gespeichert(4).split('\n')) == 9, 'Löschen: Enter hat gelöscht')
            b.klick('#szeneLoeschen'); b.klick('dialog.fenster[open] .fenster-knopf-gefahr')
            zeilen = gespeichert(4).split('\n')
            pruefe(len(zeilen) == 8 and '[P1 18:02] früh' not in zeilen and zeilen[4] == '[P2 15:40] geändert', f'Löschen: {zeilen}')

            # 6. Zuletzt benutztes Drittel; anderes Spiel -> wieder 1.
            szene(5, '0500', 'drittes', drittel=2)
            b.klick(".szene-knopf[data-szene='6']")
            pruefe(b.js("segWert('szene_drittel')") == 'P3', 'zuletzt benutztes Drittel nicht vorgewählt')
            b.taste('Escape')
            b.klick('#spielTitel')
            b.js("(() => { const g = document.getElementById('spiel_gegner'); g.value = 'Anderes Team'; g.dispatchEvent(new Event('input')); })()")
            b.klick('#sfFertig')
            b.klick(".szene-knopf[data-szene='6']")
            pruefe(b.js("segWert('szene_drittel')") == 'P1', 'anderes Spiel: Drittel nicht wieder „1.“')
            b.taste('Escape')

            # 7. Lange Notiz: höchstens zwei Zeilen im Chip, voller Text im Fenster
            lang = 'Sehr lange Notiz ' * 20
            szene(7, '1200', lang.strip())
            h = b.js("(() => { const t = document.querySelector('#szenen_7 .szene-text'); const z = parseFloat(getComputedStyle(t).lineHeight); return [t.clientHeight, z, t.scrollHeight]; })()")
            pruefe(h[0] <= 2 * h[1] + 1 and h[2] > h[0], f'Chip nicht auf zwei Zeilen begrenzt ({h})')
            b.klick('#szenen_7 .szene-chip')
            pruefe(b.js("document.getElementById('szeneNotiz').value") == lang.strip(), 'voller Text nicht im Fenster')
            b.taste('Escape')

            # 8. Druck: gleich sortiert, voller Text, kein Knopf
            b.js(f"(() => {{ document.getElementById('note_4').value = '{GEMISCHT}'; saveCurrentRefData(); }})()")
            b.fenster(794, 1123, druck=True)
            b.oeffnen(srv.basis + '/index.html')
            pruefe(chips(4) == erwartet, f'Druck: Reihenfolge {chips(4)}')
            pruefe(b.js("getComputedStyle(document.querySelector('.szene-knopf')).display") == 'none', 'Druck: Knopf „Szene“ sichtbar')
            pruefe(b.js("getComputedStyle(document.querySelector('#szenen_7 .szene-text')).overflow") == 'visible', 'Druck: lange Notiz abgeschnitten')

            # 9. Grössen und Englisch
            for w, h, sprache in ((768, 1024, 'en'), (834, 1194, 'de'), (1194, 834, 'en')):
                start(w, h, sprache)
                szene(1, '1500', 'kurz')
                klein = b.js("[...document.querySelectorAll('.szene-chip, .szene-knopf')].filter((e) => e.offsetParent && e.getBoundingClientRect().height < 43.5).length")
                pruefe(klein == 0, f'{w}px: {klein} zu kleine Chips/Knöpfe')
                pruefe(b.js('document.documentElement.scrollWidth') <= w, f'{w}px: waagrechte Bildlaufleiste')
                b.klick(".szene-knopf[data-szene='1']")
                r = b.js("(() => { const d = document.getElementById('szeneDialog').getBoundingClientRect(); return [d.left >= 0, d.right <= innerWidth, d.bottom <= innerHeight]; })()")
                pruefe(all(r), f'{w}px: Szene-Fenster passt nicht ({r})')
                if sprache == 'en':
                    pruefe(b.js("document.getElementById('szeneZeitHinweis').textContent") == 'Time remaining on game clock', f'{w}px: Hinweis Restzeit nicht englisch')
                else:
                    pruefe(b.js("document.getElementById('szeneZeitHinweis').textContent") == 'Restzeit auf der Matchuhr', f'{w}px: Hinweis Restzeit fehlt')
                b.taste('Escape')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Szene-Test: {len(fehler)} Fehler (Hinzufügen, Zeiten, Format, Sortierung, Ändern/Löschen, freier Text, Drittel, Chips, Druck, Grössen, DE/EN)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
