"""Bereiche-Test (Etappe 2.9b): Findet VoiceOver jede Karte als benannten Bereich?

Liest den Bedienungshilfen-Baum des Browsers (das, was ein Screenreader sieht) und prüft:
- jede Karte (Score, Profil, Bereit zum Sichern?, Gespann-Durchschnitt, Profil des Gespanns,
  Gespann-Beobachtungen, Bewertungen laden) ist ein Bereich (region) mit ihrem Titel als Namen
- auch auf dem iPad hochkant, wo die rechte Spalte per display: contents aufgelöst wird
- Deutsch und Englisch (Name folgt der Sprache)
Hinweis: Der Test läuft in Chrome; VoiceOver in Safari kann in Einzelheiten abweichen (von Hand prüfen).
Aufruf: python3 tests/tools/bereiche-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, Browser, server, daten_setzen, LEER  # noqa: E402

BREITEN = [(834, 1194, 'iPad hochkant'), (1080, 810, 'iPad quer 1080'), (1194, 834, 'iPad quer')]
# Ansicht -> erwartete Bereiche (i18n-Schlüssel des Titels)
ANSICHTEN = {
    'Bewertung': ('selectRefTab(0)', ['txt_weighted_for', 'radar_title', 'ready_title']),
    'Gespann': ('selectSummaryTab()', ['crew_title', 'crew_radar_title', 'sec_crew_obs']),
    'Statistik': ('selectStatsTab()', ['stats_load_title']),
}


def bereiche(b):
    """Alle Bereiche (role region) im Bedienungshilfen-Baum: [Name, …] (nur nicht ausgeblendete)."""
    b.befehl('Accessibility.enable')
    knoten = b.befehl('Accessibility.getFullAXTree')['nodes']
    return [n.get('name', {}).get('value', '') for n in knoten
            if not n.get('ignored') and n.get('role', {}).get('value') == 'region']


def main():
    fehler = []
    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            for sprache in ('de', 'en'):
                for w, h, gname in BREITEN:
                    b.fenster(w, h)
                    daten_setzen(b, srv.basis, sprache=sprache)
                    b.oeffnen(srv.basis + '/index.html')
                    for aname, (aktion, schluessel) in ANSICHTEN.items():
                        b.js(aktion)
                        da = bereiche(b)
                        for k in schluessel:
                            titel = b.js(f"t({k!r})")
                            if not any(n.startswith(titel) for n in da):
                                fehler.append(f'{sprache} {gname} {aname}: Bereich „{titel}“ fehlt (gefunden: {da})')
                        # nur Bereiche der sichtbaren Ansicht (ausgeblendete Ansichten nicht im Baum)
                        fremd = [n for n in da if not any(n.startswith(b.js(f"t({k!r})")) for k in schluessel)]
                        if fremd:
                            fehler.append(f'{sprache} {gname} {aname}: Bereiche aus anderen Ansichten im Baum: {fremd}')
                    # Score-Karte nennt den Schiedsrichter
                    b.js('selectRefTab(0)')
                    rolle = b.js("rolle(SYSTEM_CONFIGS[currentSystem][0])")
                    if not any(rolle in n for n in bereiche(b)):
                        fehler.append(f'{sprache} {gname}: Score-Bereich nennt die Rolle „{rolle}“ nicht')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Bereiche-Test: {len(fehler)} Fehler (jede Karte ein benannter Bereich, 3 Breiten × 3 Ansichten × DE/EN)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
