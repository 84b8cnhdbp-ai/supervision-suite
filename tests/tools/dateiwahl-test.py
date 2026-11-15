"""Dateiwahl-Test: Öffnet jeder Knopf mit Dateiauswahl sie wirklich – und wirkt der Import?

Für jeden Knopf, der eine Dateiauswahl öffnet („Kader importieren“ im Menü „Mehr“, „Kader importieren“ beim
Schiedsrichter-Feld, „Dateien wählen“ in der Statistik):
- echter Mausklick; über CDP (Page.setInterceptFileChooserDialog) wird geprüft, dass sich die Dateiauswahl öffnet
- die Auswahl wird direkt im Klick ausgelöst (nicht nach einem await oder Zeitgeber) – sonst öffnen Browser,
  besonders Safari auf dem iPad, sie nicht
- das Dateifeld ist nicht display: none (Safari öffnet bei ausgeblendeten Feldern teils nichts)
- eine Datei wird übergeben, der Import wirkt (Kader im Speicher bzw. Statistik geladen)
- vollständig: jedes Dateifeld der App hat einen geprüften Knopf
Gegenprobe: ein nicht angeschlossener Knopf (Kopie ohne Ereignisse) muss als Fehler auffallen.
Aufruf: python3 tests/tools/dateiwahl-test.py   (Abbruchcode 1 bei Fehlern)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from werkzeug import REPO, FIXTURES, Browser, server, daten_setzen, LEER  # noqa: E402

# Merkt sich für jedes programmatische click() auf ein Dateifeld, in welchem Ereignis es geschah
BEOBACHTEN = """(() => { window.__dateiKlicks = [];
  const orig = HTMLInputElement.prototype.click;
  HTMLInputElement.prototype.click = function () {
    if (this.type === 'file') window.__dateiKlicks.push({ id: this.id, ereignis: window.event ? window.event.type : null,
      display: getComputedStyle(this).display });
    return orig.call(this);
  }; })()"""

# Knopf -> (Vorbereitung, Dateien, Prüfung des Imports)
KNOEPFE = [
    ('Menü „Mehr“ › Kader importieren', '#menuKader', "localStorage.removeItem('referee_kader'); KADER = []; setupRefereeDropdown(); toggleMehr(true);",
     ['beispiel-kader.json'], "JSON.parse(localStorage.getItem('referee_kader') || '[]').length === 4 && KADER.length === 4"),
    ('Kader importieren beim Schiedsrichter-Feld', '#btnKaderForm', "localStorage.removeItem('referee_kader'); KADER = []; setupRefereeDropdown();",
     ['beispiel-kader.json'], "KADER.length === 4 && document.getElementById('btnKaderForm').hidden"),
    ('Statistik › Dateien wählen', '#btnStatsLaden', "selectStatsTab();",
     ['beispiel-v1.1.json', 'beispiel-v1.0.json'], "!!letzteStatistik && document.querySelectorAll('.stat-tabelle tbody tr').length >= 1"),
]


def main():
    fehler = []

    def pruefe(ok, text):
        if not ok:
            fehler.append(text)

    srv = server(REPO, {'/__leer': LEER})
    try:
        with Browser() as b:
            def knopf_pruefen(name, sel, vorbereiten, dateien, wirkung, w=1194, h=834, melden=True):
                """Gibt True zurück, wenn sich die Auswahl öffnet und der Import wirkt."""
                funde = []
                b.fenster(w, h)
                daten_setzen(b, srv.basis)
                b.oeffnen(srv.basis + '/index.html')
                b.js(BEOBACHTEN)
                b.js(vorbereiten)
                b.befehl('Page.setInterceptFileChooserDialog', enabled=True)
                b.dateiwahl.clear()
                b.klick(sel)
                b.js('new Promise((r) => setTimeout(r, 300))')
                if not b.dateiwahl:
                    funde.append(f'{name} ({w} px): Dateiauswahl öffnet sich nicht')
                else:
                    klicks = b.js('window.__dateiKlicks')
                    if not klicks or klicks[-1]['ereignis'] != 'click':
                        funde.append(f'{name}: Auswahl nicht direkt im Klick ausgelöst ({klicks})')
                    elif klicks[-1]['display'] == 'none':
                        funde.append(f'{name}: Dateifeld ist display: none (Safari öffnet die Auswahl teils nicht)')
                    b.befehl('DOM.setFileInputFiles', backendNodeId=b.dateiwahl[-1]['backendNodeId'],
                             files=[os.path.join(FIXTURES, d) for d in dateien])
                    time.sleep(0.6)
                    if not b.js(wirkung):
                        funde.append(f'{name}: Import wirkt nicht')
                b.befehl('Page.setInterceptFileChooserDialog', enabled=False)
                if melden:
                    fehler.extend(funde)
                return not funde

            for name, sel, vorb, dateien, wirkung in KNOEPFE:
                for w, h in ((1194, 834), (834, 1194), (1440, 900)):
                    knopf_pruefen(name, sel, vorb, dateien, wirkung, w, h)

            # Vollständigkeit: jedes Dateifeld hat einen geprüften Knopf
            b.fenster(1194, 834)
            b.oeffnen(srv.basis + '/index.html')
            felder = b.js("[...document.querySelectorAll('input[type=file]')].map((e) => e.id)")
            pruefe(sorted(felder) == ['kaderDatei', 'multiJsonInput'], f'Unbekannte Dateifelder: {felder} – Knopf im Test ergänzen')

            # Gegenprobe: nicht angeschlossener Knopf (Kopie ohne Ereignisse) muss auffallen
            gegen = knopf_pruefen('Gegenprobe', '#menuKader',
                                  "toggleMehr(true); const k = document.getElementById('menuKader'); k.replaceWith(k.cloneNode(true));",
                                  ['beispiel-kader.json'], 'KADER.length === 4', melden=False)
            pruefe(not gegen, 'Gegenprobe: nicht angeschlossener Knopf fällt nicht auf')
            fehler += [f'JS-Fehler: {f}' for f in b.fehler if 'Update nicht möglich' not in f]
    finally:
        srv.shutdown()
    for f in fehler:
        print('FEHLER: ', f)
    print(f'Dateiwahl-Test: {len(fehler)} Fehler (3 Knöpfe × 3 Grössen, echte Klicks, Auswahl öffnet sich im Klick, Import wirkt; Gegenprobe)')
    sys.exit(1 if fehler else 0)


if __name__ == '__main__':
    main()
