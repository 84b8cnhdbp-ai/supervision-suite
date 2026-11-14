"""Layout-Test (Etappe 2.4a): Seitenleiste, Werkzeugleiste mit Reitern, Menü „Mehr“.

Prüft mit echten Klicks und Tasten:
- 834 / 1194 / 1440 px, DE/EN: Seitenleiste und Werkzeugleiste sichtbar (unter 1000 px Leiste oben), keine
  waagrechte Bildlaufleiste, alle Knöpfe mind. 44 px, Reiter vollständig sichtbar
- Reiter: Kurzform bei 3/4-Mann („H1 · Frei“), Rolle bei 1/2-Mann; Nachname = alles ausser dem letzten Wort
  („Von Rotz Peter“ → „Von Rotz“), ein Wort = ganzes Wort; Pfeiltasten wechseln den Reiter
- Seitenleiste: Spiel, Saison-Statistik (wechselt Ansicht), Fuss mit „Daten bleiben …“, Version und Stand aus ?v=,
  Kader-Anzahl, Offline-Status, Gespeichert-Zeit; Punkte ohne Funktion nicht vorhanden
- Menü „Mehr“: öffnen/schliessen (Esc, daneben tippen), Fokus; CSV, Kader, Sprache, Darstellung, Zurücksetzen
  (rot, mit Abstand)
- Kader-Knopf beim Schiedsrichter-Feld nur ohne Kader
- Druck: Seitenleiste, Werkzeugleiste und Menü nicht sichtbar, Druckkopf sichtbar
Aufruf: python3 tests/tools/layout-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

GEROEST = r"""(() => {
  const f = [];
  const vw = document.documentElement.clientWidth;
  if (document.documentElement.scrollWidth > vw + 1) f.push(`waagrechte Bildlaufleiste (${document.documentElement.scrollWidth} > ${vw})`);
  const sl = document.getElementById('seitenleiste').getBoundingClientRect();
  const wl = document.querySelector('.werkzeugleiste').getBoundingClientRect();
  if (sl.width < 50 || sl.height < 40) f.push('Seitenleiste nicht sichtbar');
  if (wl.height < 44) f.push('Werkzeugleiste nicht sichtbar');
  if (vw >= 1000 && !(sl.right <= wl.left + 1)) f.push('Seitenleiste nicht links neben dem Inhalt');
  if (vw < 1000 && !(sl.bottom <= wl.top + 1)) f.push('Seitenleiste (schmal) nicht oben');
  document.querySelectorAll('.seitenleiste button, .werkzeugleiste button').forEach((b) => {
    if (b.closest('[hidden]')) return;
    const r = b.getBoundingClientRect();
    if (r.height < 43.5 || r.width < 43.5) f.push(`Knopf „${(b.innerText || b.getAttribute('aria-label') || '').trim()}“ nur ${Math.round(r.width)}×${Math.round(r.height)} px`);
    if (r.right > vw + 1) f.push(`Knopf „${b.innerText.trim()}“ ragt rechts hinaus`);
  });
  const leiste = document.getElementById('tabsContainer');
  if (leiste.scrollWidth > leiste.clientWidth + 1) f.push(`Reiter passen nicht (${leiste.scrollWidth} > ${leiste.clientWidth})`);
  return f;
})()"""

REITER = "[...document.querySelectorAll('#tabsContainer [role=tab]')].map((b) => b.textContent)"


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            # 1. Gerüst in allen Breiten und Sprachen, Bildschirm
            for w, h in ((834, 1194), (1194, 834), (1440, 900)):
                for sprache in ('de', 'en'):
                    b.fenster(w, h)
                    daten_setzen(b, srv.basis, sprache=sprache)
                    b.oeffnen(srv.basis + '/index.html')
                    for f in b.js(GEROEST):
                        fehler.append(f'{w}px {sprache}: {f}')

            b.fenster(1194, 834)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')

            # 2. Reiter-Beschriftung
            pruefe(b.js(REITER) == ['H1 · Frei', 'H2 · Gast', 'L1 · Brunner', 'L2', 'Gespann'], f'Reiter 4-Mann: {b.js(REITER)}')
            pruefe(b.js("nachname('Von Rotz Peter')") == 'Von Rotz', 'Nachname „Von Rotz Peter“')
            pruefe(b.js("nachname('Muster')") == 'Muster', 'Nachname aus einem Wort')
            pruefe(b.js("nachname('  Meier   Luca ')") == 'Meier', 'Nachname mit Leerzeichen')
            # Name im Formular ändern -> Reiter folgt sofort
            b.js("selectRefTab(3); const s = document.getElementById('current_schiri_name'); s.value = '_CUSTOM_'; handleRefSelectChange();"
                 "const c = document.getElementById('current_schiri_name_custom'); c.value = 'Von Rotz Peter'; c.dispatchEvent(new Event('input'));")
            pruefe(b.js(REITER)[3] == 'L2 · Von Rotz', f'Reiter nach Namenseingabe: {b.js(REITER)[3]!r}')
            pruefe('Linesperson 2' in b.js("document.querySelector('#tabsContainer [data-reiter=l2]').title"), 'Reiter ohne vollen Namen als Tooltip')
            b.klick("label[for='system_typ__1']")   # 2-Mann
            pruefe(b.js(REITER) == ['Referee 1', 'Referee 2', 'Gespann'], f'Reiter 2-Mann: {b.js(REITER)}')
            b.klick("label[for='system_typ__0']")   # 1-Mann
            pruefe(b.js(REITER) == ['Einzel-Schiedsrichter'], f'Reiter 1-Mann: {b.js(REITER)}')
            b.klick("label[for='system_typ__3']")   # zurück zu 4-Mann

            # 3. Reiter mit Tastatur
            b.js("document.querySelector('#tabsContainer [aria-selected=true]').focus()")
            vorher = b.js("document.activeElement.dataset.reiter")
            b.taste('ArrowRight')
            nachher = b.js("document.activeElement.dataset.reiter")
            pruefe(nachher != vorher and b.js("document.activeElement.getAttribute('aria-selected')") == 'true',
                   f'Pfeil rechts in den Reitern: {vorher} -> {nachher}')
            pruefe(b.js("[...document.querySelectorAll('#tabsContainer [role=tab]')].filter((t) => t.tabIndex === 0).length") == 1,
                   'Reiter: nicht genau ein Reiter per Tab erreichbar')

            # 4. Seitenleiste
            pruefe('Team Blau vs. Team Rot' in b.js("document.getElementById('navSpiel').innerText"), 'Seitenleiste: Spiel fehlt')
            pruefe(b.js("document.getElementById('navSpiel').getAttribute('aria-current')") == 'page', 'Seitenleiste: Spiel nicht als aktuell markiert')
            b.klick('#navStats')
            pruefe(b.js("getComputedStyle(document.getElementById('seasonStatsView')).display") != 'none', 'Saison-Statistik öffnet nicht')
            pruefe(b.js("document.getElementById('navStats').getAttribute('aria-current')") == 'page', 'Statistik nicht als aktuell markiert')
            b.klick('#navSpiel')
            pruefe(b.js("getComputedStyle(document.getElementById('singleRefView')).display") != 'none', 'Klick auf Spiel führt nicht zur Bewertung')
            fuss = b.js("document.querySelector('.sl-fuss').innerText")
            stand = b.js("document.querySelector('script[src*=\"js/app.js\"]').getAttribute('src').match(/v=(\\d+)/)[1]")
            pruefe(b.js("t('footer_local')") in fuss, 'Fuss: „Daten bleiben auf diesem Gerät“ fehlt')
            pruefe(f"Version {b.js('APP_VERSION')} · Stand {stand}" in fuss, f'Fuss: Version/Stand falsch ({fuss!r})')
            pruefe('Kader: 4' in fuss, 'Fuss: Kader-Anzahl fehlt')
            pruefe(b.js("document.getElementById('pwaBadge').offsetParent !== null"), 'Fuss: Offline-Status nicht sichtbar')
            b.js("saveGlobalState()")
            pruefe(re.search(r'Gespeichert \d\d:\d\d', b.js("document.getElementById('saveStatus').innerText") or ''), 'Fuss: Gespeichert-Zeit fehlt')
            for wort in ('Geplant', 'Erledigt', 'Berichte'):
                pruefe(wort not in b.js("document.getElementById('seitenleiste').innerText"), f'Seitenleiste zeigt „{wort}“ (noch ohne Funktion)')

            # 5. Menü „Mehr“
            b.klick('#btnMehr')
            pruefe(b.js("!document.getElementById('mehrMenu').hidden"), 'Mehr: öffnet nicht')
            pruefe(b.js("document.getElementById('btnMehr').getAttribute('aria-expanded')") == 'true', 'Mehr: aria-expanded nicht true')
            pruefe(b.js("document.getElementById('mehrMenu').contains(document.activeElement)"), 'Mehr: Fokus nicht im Menü')
            eintraege = b.js("[...document.querySelectorAll('#mehrMenu .menu-eintrag')].map((e) => e.innerText.trim())")
            pruefe(eintraege == [b.js("t('menu_csv')"), b.js("t('kader_import')"), b.js("t('menu_reset')")], f'Mehr: Einträge {eintraege}')
            rot = b.js("getComputedStyle(document.getElementById('menuReset')).color")
            pruefe(rot == 'rgb(180, 35, 24)', f'Mehr: Zurücksetzen nicht rot ({rot})')
            abstand = b.js("document.getElementById('menuReset').getBoundingClientRect().top - document.querySelector('.menu-gruppe:last-of-type').getBoundingClientRect().bottom")
            pruefe(abstand >= 12 and b.js("!!document.querySelector('#mehrMenu .menu-trenner')"), f'Mehr: Zurücksetzen ohne Abstand/Trennlinie ({abstand:.0f} px)')
            b.taste('Escape')
            pruefe(b.js("document.getElementById('mehrMenu').hidden") and b.js("document.activeElement.id") == 'btnMehr', 'Mehr: Esc schliesst nicht / Fokus nicht zurück')
            b.klick('#btnMehr'); b.klick('#navSpiel')
            pruefe(b.js("document.getElementById('mehrMenu').hidden"), 'Mehr: Tippen daneben schliesst nicht')
            # CSV
            b.js("window.__dl = []; window.downloadBlob = (blob, name) => __dl.push(name);")
            b.klick('#btnMehr'); b.klick("#mehrMenu .menu-eintrag:nth-of-type(1)")
            pruefe(b.js('__dl.length') == 1 and b.js('__dl[0]').endswith('.csv'), 'Mehr: CSV-Export lädt keine CSV herunter')
            # Kader: Dateiauswahl wird geöffnet
            b.js("window.__dateiwahl = 0; HTMLInputElement.prototype.click = function () { if (this.type === 'file') __dateiwahl++; };")
            b.klick('#btnMehr'); b.klick("#mehrMenu .menu-eintrag:nth-of-type(2)")
            pruefe(b.js('__dateiwahl') == 1, 'Mehr: Kader importieren öffnet keine Dateiauswahl')
            # Sprache
            b.klick('#btnMehr'); b.klick("label[for='sprache__1']")
            pruefe(b.js('currentLang') == 'en' and b.js("localStorage.getItem('referee_lang_preference')") == 'en', 'Mehr: Sprache wechselt nicht auf Englisch')
            pruefe(b.js(REITER)[-1] == 'Crew', 'Mehr: Reiter nach Sprachwechsel nicht englisch')
            pruefe(b.js("document.activeElement && document.activeElement.name") == 'sprache', 'Mehr: Fokus nach Sprachwechsel verloren')
            b.klick("label[for='sprache__0']")
            # Darstellung
            b.klick("label[for='darstellung__2']")
            pruefe(b.js("document.documentElement.getAttribute('data-theme')") == 'dark', 'Mehr: Darstellung „Dunkel“ wirkt nicht')
            b.klick("label[for='darstellung__0']")
            pruefe(b.js("document.documentElement.getAttribute('data-theme')") is None and b.js("localStorage.getItem('referee_theme_preference')") is None,
                   'Mehr: Darstellung „Auto“ wirkt nicht')
            # Zurücksetzen öffnet das Fenster aus 2.2
            b.klick('#menuReset')
            pruefe(b.js("!!document.querySelector('dialog.fenster[open] .fenster-knopf-gefahr')"), 'Mehr: Zurücksetzen öffnet kein Fenster')
            b.taste('Escape')

            # 6. Kader-Knopf beim Schiedsrichter-Feld nur ohne Kader
            pruefe(b.js("document.getElementById('btnKaderForm').hidden"), 'Kader-Knopf sichtbar, obwohl Kader geladen')
            b.js("localStorage.removeItem('referee_kader')")
            b.oeffnen(srv.basis + '/index.html')
            pruefe(b.js("!document.getElementById('btnKaderForm').hidden && document.getElementById('btnKaderForm').offsetHeight >= 44"),
                   'Kader-Knopf fehlt, obwohl kein Kader geladen')
            b.js("window.__dateiwahl = 0; HTMLInputElement.prototype.click = function () { if (this.type === 'file') __dateiwahl++; };")
            b.klick('#btnKaderForm')
            pruefe(b.js('__dateiwahl') == 1, 'Kader-Knopf öffnet keine Dateiauswahl')

            # 7. Druck
            b.fenster(794, 1123, druck=True)
            daten_setzen(b, srv.basis)
            b.oeffnen(srv.basis + '/index.html')
            for sel in ('#seitenleiste', '.werkzeugleiste', '#mehrMenu'):
                pruefe(b.js(f"getComputedStyle(document.querySelector('{sel}')).display") == 'none', f'Druck: {sel} wird gedruckt')
            pruefe(b.js("getComputedStyle(document.querySelector('.druck-kopf')).display") != 'none', 'Druck: Druckkopf fehlt')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Layout-Test: {len(fehler)} Fehler (Gerüst 3 Breiten × DE/EN, Reiter, Seitenleiste, Menü „Mehr“, Kader-Knopf, Druck)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
