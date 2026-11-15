// Übergänge (Etappe 2.9b)
//
// - Reiterwechsel: die Ansicht blendet weich ein (150 ms, CSS-Klasse .einblenden).
// - Der Score zählt nur beim Reiterwechsel hoch (400 ms), beim Bearbeiten springt er sofort auf den neuen Wert.
// - Bei „Bewegung reduzieren“ (prefers-reduced-motion) nichts davon.
// - Im Druck immer der fertige Wert, auch wenn mitten im Hochzählen gedruckt wird.

const ZAEHL_DAUER = 400;
const zaehler = new Map();    // Element -> laufende Animation (requestAnimationFrame)
let reiterWechsel = false;    // true nur während eines Reiterwechsels (mitReiterWechsel)

const ruhigeBewegung = () => window.matchMedia('(prefers-reduced-motion: reduce)').matches;
const imDruck = () => window.matchMedia('print').matches;

// Arbeit eines Reiterwechsels ausführen: nur darin zählt der Score hoch
function mitReiterWechsel(arbeit) {
  reiterWechsel = true;
  try { arbeit(); } finally { reiterWechsel = false; }
}

// Ansicht weich einblenden (bei jedem Reiterwechsel, auch zwischen zwei Schiedsrichtern)
function blendeEin(ansicht) {
  if (!ansicht || ruhigeBewegung()) return;
  ansicht.classList.remove('einblenden');
  void ansicht.offsetWidth;   // Animation neu starten
  ansicht.classList.add('einblenden');
}

// Score-Zahl anzeigen: beim Reiterwechsel von 0 hochzählen, sonst sofort
function zeigeScoreZahl(el, wert) {
  const text = wert === null ? '–' : wert + '%';
  el.dataset.ziel = text;
  stoppeZaehler(el);
  if (!reiterWechsel || wert === null || wert === 0 || ruhigeBewegung() || imDruck()) {
    el.innerText = text;
    return;
  }
  const start = performance.now();
  const schritt = (jetzt) => {
    const anteil = Math.min(1, (jetzt - start) / ZAEHL_DAUER);
    if (anteil >= 1 || imDruck()) { el.innerText = text; zaehler.delete(el); return; }
    el.innerText = Math.round(wert * (1 - Math.pow(1 - anteil, 3))) + '%';   // sanft auslaufend
    zaehler.set(el, requestAnimationFrame(schritt));
  };
  el.innerText = '0%';
  zaehler.set(el, requestAnimationFrame(schritt));
}

function stoppeZaehler(el) {
  if (zaehler.has(el)) { cancelAnimationFrame(zaehler.get(el)); zaehler.delete(el); }
}

// Alle laufenden Zähler sofort auf den fertigen Wert setzen (vor dem Drucken)
function zaehlerFertig() {
  zaehler.forEach((id, el) => { cancelAnimationFrame(id); el.innerText = el.dataset.ziel; });
  zaehler.clear();
}

function initBewegung() {
  window.addEventListener('beforeprint', zaehlerFertig);
  const druck = window.matchMedia('print');
  if (druck.addEventListener) druck.addEventListener('change', (e) => { if (e.matches) zaehlerFertig(); });
}
