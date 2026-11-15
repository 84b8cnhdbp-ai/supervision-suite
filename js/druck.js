// Druck (Etappe 2.9a): mehrzeilige Felder erscheinen im Druck vollständig.
//
// Ein Textfeld kann im Druck nicht mitwachsen und schneidet lange Texte ab. Darum hat jedes mehrzeilige Feld
// eine Druckfassung als normalen Text direkt danach. Sie ist am Bildschirm ausgeblendet und für VoiceOver
// unsichtbar (aria-hidden), damit nichts doppelt vorgelesen wird. Leere Felder fallen im Druck weg
// (bei [data-druck-ganz] samt Beschriftung).

const DRUCK_FELDER = 'textarea.notiz-frei, #top_strengths, #top_workon, #general_report, #crew_notes';

function aktualisiereDruckText(feld) {
  const text = feld.nextElementSibling;
  if (!text || !text.classList.contains('druck-text')) return;
  text.textContent = feld.value;
  const leer = !feld.value.trim();
  text.classList.toggle('leer', leer);
  const ganz = feld.closest('[data-druck-ganz]');
  if (ganz) ganz.classList.toggle('druck-leer', leer);
}

function aktualisiereDruckTexte() {
  document.querySelectorAll(DRUCK_FELDER).forEach(aktualisiereDruckText);
}

function initDruck() {
  document.querySelectorAll(DRUCK_FELDER).forEach((feld) => {
    if (feld.nextElementSibling && feld.nextElementSibling.classList.contains('druck-text')) return;
    const text = document.createElement('div');
    text.className = 'druck-text';
    text.setAttribute('aria-hidden', 'true');
    feld.after(text);
  });
  document.addEventListener('input', (e) => { if (e.target.matches && e.target.matches(DRUCK_FELDER)) aktualisiereDruckText(e.target); });
  window.addEventListener('beforeprint', aktualisiereDruckTexte);   // Sicherheitsnetz vor dem Drucken
  aktualisiereDruckTexte();
}

// Saisons aus Datumsangaben (ab August neue Saison), z. B. „2025/26 und 2026/27“; ohne lesbares Datum ''
function saisonsText(daten) {
  const saisons = new Set();
  daten.forEach((d) => {
    const m = /^(\d{4})-(\d{2})/.exec(String(d || ''));
    if (!m) return;
    const jahr = parseInt(m[1], 10), monat = parseInt(m[2], 10);
    if (monat < 1 || monat > 12) return;
    const start = monat >= 8 ? jahr : jahr - 1;
    saisons.add(`${start}/${String((start + 1) % 100).padStart(2, '0')}`);
  });
  const liste = [...saisons].sort();
  if (!liste.length) return '';
  try { return new Intl.ListFormat(currentLang, { type: 'conjunction' }).format(liste); }
  catch (e) { return liste.join(', '); }
}
