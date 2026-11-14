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
  exportName: 'EV Zug'        // Wert für "club" im Export-JSON
};

// Logo und Fenstertitel setzen (nur im Browser, nicht im Service Worker)
function applyClub() {
  document.querySelectorAll('[data-club-logo]').forEach((logo) => {
    logo.src = CLUB.logo;
    logo.alt = CLUB.kurz + ' Logo';
  });
  document.title = t('app_title') + ' - ' + CLUB.name;
}
