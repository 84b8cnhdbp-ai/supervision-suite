"""Texte-Test: Hat jede Sprache alle Texte? Funktioniert die Sprachwahl?

Prüft (Fehler = Abbruchcode 1):
- jeder Schlüssel, den Code und HTML verwenden (t('…'), data-i18n), existiert auf Deutsch
- Englisch hat alle deutschen Schlüssel, gleiche Platzhalter ({n} …) und gleich lange Listen
- in Listen mit gespeicherten Werten (val) sind die Werte in allen Sprachen gleich (deutsch)
- jede Rolle in SYSTEM_CONFIGS hat eine englische Bezeichnung
- Sprachwahl: Englisch bleibt nach Neuladen; ?lang=fr wird nicht gespeichert und zeigt
  fehlende Texte auf Deutsch; versteckte Sprachen stehen nicht in der Auswahl
FR und IT: fehlende Texte werden nur gemeldet. Mit --streng (ab Etappe 2.9) sind sie Fehler.

Aufruf: python3 tests/tools/texte-test.py [--streng]
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

STRENG = '--streng' in sys.argv


def verwendete_schluessel():
    """Alle Schlüssel aus t('…')-Aufrufen im JS und data-i18n im HTML."""
    keys = set()
    for name in os.listdir(os.path.join(REPO, 'js')):
        if not name.endswith('.js'):
            continue
        src = open(os.path.join(REPO, 'js', name), encoding='utf-8').read()
        for m in re.finditer(r"\bt\(([^()]*)\)", src):
            arg = m.group(1)
            # erstes Argument; auch Ternär-Ausdrücke wie t(x ? 'a' : 'b')
            erstes = arg.split(',')[0] if not arg.strip().startswith('{') else ''
            # bei Bedingungen (a ? 'x' : 'y') nur die Ergebnisse, nicht den Vergleichswert
            muster = r"[?:]\s*'([a-z0-9_]+)'" if '?' in erstes else r"'([a-z0-9_]+)'"
            for lit in re.findall(muster, erstes):
                if not re.search(rf"'{re.escape(lit)}'\s*\+", erstes):   # 'theme_' + x: nur als Anfang zählen (unten)
                    keys.add(lit)
            # dynamisch zusammengesetzte Schlüssel: t('theme_' + …)
            for prefix in re.findall(r"'([a-z0-9_]+_)'\s*\+", erstes):
                keys.add(prefix + '*')
    html = open(os.path.join(REPO, 'index.html'), encoding='utf-8').read()
    keys |= set(re.findall(r'data-i18n="([a-z0-9_]+)"', html))
    return keys


def main():
    fehler, hinweise = [], []
    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            b.fenster(1194, 834)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            d = b.js("""({
              sprachen: SPRACHEN,
              texte: I18N,
              rollen: Object.values(SYSTEM_CONFIGS).flat().map((r) => ({ id: r.id, de: r.role_de, en: r.role_en }))
            })""")

            de = d['texte']['de']
            # 1. verwendete Schlüssel existieren
            for k in sorted(verwendete_schluessel()):
                if k.endswith('*'):
                    if not any(x.startswith(k[:-1]) for x in de):
                        fehler.append(f'Kein Text beginnt mit "{k[:-1]}"')
                elif k not in de:
                    fehler.append(f'Schlüssel "{k}" wird verwendet, fehlt aber auf Deutsch')

            # 2./3. Vollständigkeit je Sprache
            for s in d['sprachen']:
                code = s['code']
                if code == 'de':
                    continue
                txt = d['texte'].get(code, {})
                fehlend = [k for k in de if k not in txt]
                pflicht = s['sichtbar'] or STRENG
                if fehlend:
                    meldung = f'{code.upper()}: {len(fehlend)} von {len(de)} Texten fehlen' + (
                        f" (z. B. {', '.join(fehlend[:5])})" if fehlend else '')
                    (fehler if pflicht else hinweise).append(meldung)
                for k, v in txt.items():
                    if k not in de:
                        hinweise.append(f'{code.upper()}: Schlüssel "{k}" gibt es auf Deutsch nicht (überflüssig?)')
                        continue
                    if isinstance(de[k], str) != isinstance(v, str):
                        fehler.append(f'{code.upper()} "{k}": anderer Typ als Deutsch')
                    elif isinstance(v, str):
                        if set(re.findall(r'\{\w+\}', v)) != set(re.findall(r'\{\w+\}', de[k])):
                            fehler.append(f'{code.upper()} "{k}": andere Platzhalter als Deutsch')
                    elif isinstance(v, list):
                        if len(v) != len(de[k]):
                            fehler.append(f'{code.upper()} "{k}": {len(v)} statt {len(de[k])} Einträge')
                        elif v and isinstance(v[0], dict) and 'val' in v[0]:
                            if [x['val'] for x in v] != [x['val'] for x in de[k]]:
                                fehler.append(f'{code.upper()} "{k}": gespeicherte Werte (val) weichen vom Deutschen ab')

            # 4. Rollen
            for r in d['rollen']:
                if not r['en']:
                    fehler.append(f"Rolle {r['id']} ({r['de']}): englische Bezeichnung fehlt")

            # 5. Verhalten der Sprachwahl
            sichtbar = [s['code'] for s in d['sprachen'] if s['sichtbar']]
            auswahl = b.js("[...document.querySelectorAll('input[name=sprache]')].map((o) => o.value)")
            if auswahl != sichtbar:
                fehler.append(f'Sprachauswahl zeigt {auswahl}, erwartet {sichtbar}')
            b.js("setLanguage('en')")
            b.oeffnen(srv.basis + '/index.html')
            if b.js('currentLang') != 'en' or b.js('document.documentElement.lang') != 'en':
                fehler.append('Englisch bleibt nach dem Neuladen nicht erhalten')
            tab_en = b.js("document.querySelector('.tab-summary').innerText")
            b.oeffnen(srv.basis + '/index.html?lang=fr')
            if b.js('currentLang') != 'fr':
                fehler.append('?lang=fr schaltet nicht auf Französisch')
            if b.js("localStorage.getItem('referee_lang_preference')") != 'en':
                fehler.append('?lang=fr hat die gespeicherte Sprache überschrieben')
            tab_fr = b.js("document.querySelector('.tab-summary').innerText")
            erwartet_fr = d['texte']['fr'].get('txt_tab_crew') or de['txt_tab_crew']
            if tab_fr != erwartet_fr:
                fehler.append(f'?lang=fr: Reiter zeigt "{tab_fr}", erwartet "{erwartet_fr}" (Rückfall auf Deutsch)')
            if b.js("[...document.querySelectorAll('input[name=sprache]')].map((o) => o.value)") != sichtbar + ['fr']:
                fehler.append('?lang=fr: Auswahl sollte die sichtbaren Sprachen plus FR (aktuell) zeigen')
            b.oeffnen(srv.basis + '/index.html')
            if b.js('currentLang') != 'en':
                fehler.append('Nach ?lang=fr ist ohne Parameter nicht wieder Englisch aktiv')
            if tab_en == de['txt_tab_crew']:
                hinweise.append('Englischer Reiter-Text gleich wie Deutsch (gewollt?)')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()

    for h in hinweise:
        print('Hinweis:', h)
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Texte-Test: {len(fehler)} Fehler, {len(hinweise)} Hinweise' + (' (streng)' if STRENG else ''))
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
