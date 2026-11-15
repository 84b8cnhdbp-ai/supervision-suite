// Verein – zentral eingestellt. Ändern vorerst nur in dieser Datei (kein Knopf in der App).
// Kein Vereinsname fest im Code: HTML, Texte (Platzhalter {verein}, {kurz}, {halle}) und Export
// lesen diese Werte. Wird auch vom Service Worker geladen (Logo offline verfügbar).
// Achtung: Weil der Service Worker diese Datei lädt, hier keine Browser-Befehle (document, window)
// ausserhalb von Funktionen.
const CLUB = {
  name: 'EV Zug',             // voller Name (Fenstertitel, Texte)
  kurz: 'EVZ',                // Kürzel (z. B. „EVZ Kader“, später „EVZ – Gegner“)
  logo: 'logo-evz.svg',       // Logo-Datei im Projektordner
  halle: 'Bossard Arena',     // Beispiel im Feld „Spielort“
  exportName: 'EV Zug',       // Wert für "club" im Export-JSON
  standardSystem: '2-Man'     // System für neue Spiele und nach „Spiel zurücksetzen“ ('1-Man', '2-Man', '3-Man', '4-Man')
};

// Logo und Fenstertitel setzen (nur im Browser, nicht im Service Worker)
function applyClub() {
  document.querySelectorAll('[data-club-logo]').forEach((logo) => {
    logo.onerror = () => { logo.style.display = 'none'; };   // Logo-Datei fehlt: nichts anzeigen
    logo.src = CLUB.logo;
    logo.alt = t('logo_alt');
  });
  document.title = t('app_title') + ' - ' + CLUB.name;
}
