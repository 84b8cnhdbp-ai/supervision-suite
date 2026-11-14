// Gerüst: Seitenleiste, Werkzeugleiste (Reiter) und Menü „Mehr“ (Etappe 2.4a)

// ---------- Reiter ----------

// Nachname aus „Nachname Vorname“: alles ausser dem letzten Wort („Von Rotz Peter“ → „Von Rotz“);
// bei nur einem Wort das ganze Wort.
function nachname(name) {
  const woerter = String(name || '').trim().split(/\s+/).filter(Boolean);
  if (woerter.length <= 1) return woerter[0] || '';
  return woerter.slice(0, -1).join(' ');
}

// Beschriftung eines Reiters: bei 3- und 4-Mann Kurzform („H1 · Meier“), sonst Rolle („Referee 1 · Meier“).
function reiterText(ref) {
  const d = gameData.referees[`${currentSystem}_${ref.id}`];
  const nn = d && d.name ? nachname(d.name) : '';
  const basis = SYSTEM_CONFIGS[currentSystem].length >= 3 ? ref.id.toUpperCase() : rolle(ref);
  return { sichtbar: nn ? `${basis} · ${nn}` : basis, voll: d && d.name ? `${rolle(ref)} · ${d.name}` : rolle(ref) };
}

// Beschriftung der bestehenden Reiter nachführen (z. B. nach Namensänderung), ohne neu aufzubauen
function aktualisiereReiter() {
  SYSTEM_CONFIGS[currentSystem].forEach((ref) => {
    const btn = document.querySelector(`#tabsContainer [data-reiter="${ref.id}"]`);
    if (!btn) return;
    const text = reiterText(ref);
    btn.textContent = text.sichtbar;
    btn.title = text.voll;
  });
}

// Pfeiltasten, Pos1 und Ende in der Reiterleiste (wie bei Tabs üblich: Wechsel sofort)
function reiterTaste(e) {
  const reiter = [...document.querySelectorAll('#tabsContainer [role="tab"]')];
  const i = reiter.indexOf(e.currentTarget);
  let ziel = null;
  if (e.key === 'ArrowRight') ziel = reiter[(i + 1) % reiter.length];
  else if (e.key === 'ArrowLeft') ziel = reiter[(i - 1 + reiter.length) % reiter.length];
  else if (e.key === 'Home') ziel = reiter[0];
  else if (e.key === 'End') ziel = reiter[reiter.length - 1];
  if (!ziel) return;
  e.preventDefault();
  const schluessel = ziel.dataset.reiter;
  ziel.click();   // baut die Reiter neu auf
  const neu = document.querySelector(`#tabsContainer [data-reiter="${schluessel}"]`);
  if (neu) neu.focus();
}

// ---------- Seitenleiste ----------

function appStand() {
  const s = document.querySelector('script[src*="js/app.js"]');
  const m = s && s.getAttribute('src').match(/[?&]v=(\d+)/);
  return m ? m[1] : '?';
}

function saisonText(heute = new Date()) {
  const jahr = heute.getMonth() >= 7 ? heute.getFullYear() : heute.getFullYear() - 1;   // Saison ab August
  return t('season', { s: `${jahr}/${String((jahr + 1) % 100).padStart(2, '0')}` });
}

function datumZeitText(wert) {
  if (!wert) return '';
  const d = new Date(wert);
  if (isNaN(d)) return '';
  const zwei = (n) => String(n).padStart(2, '0');
  return `${zwei(d.getDate())}.${zwei(d.getMonth() + 1)}.${d.getFullYear()}, ${zwei(d.getHours())}:${zwei(d.getMinutes())}`;
}

function aktualisiereSeitenleiste() {
  const g = (gameData && gameData.global) || {};
  const setze = (id, text) => { const el = document.getElementById(id); if (el) el.textContent = text; };
  setze('navSpielTitel', g.spiel_paarung || t('nav_no_game'));
  setze('navSpielInfo', [g.spiel_liga, datumZeitText(g.spiel_datum), g.spiel_ort].filter(Boolean).join(' · '));
  setze('saisonText', saisonText());
  setze('versionText', t('footer_version', { version: APP_VERSION, stand: appStand() }));
  setze('kaderText', t('footer_kader', { n: KADER.length }));
  setze('druckVerein', CLUB.name);
  const statistik = activeTabType === 'stats';
  const spiel = document.getElementById('navSpiel');
  const stats = document.getElementById('navStats');
  if (spiel) { spiel.classList.toggle('aktiv', !statistik); statistik ? spiel.removeAttribute('aria-current') : spiel.setAttribute('aria-current', 'page'); }
  if (stats) { stats.classList.toggle('aktiv', statistik); statistik ? stats.setAttribute('aria-current', 'page') : stats.removeAttribute('aria-current'); }
}

// Klick auf das Spiel in der Seitenleiste: zurück zur Bewertung
function zeigeBewertung() {
  if (activeTabType === 'stats') selectRefTab(activeRefIndex);
  window.scrollTo({ top: 0 });
}

// ---------- Menü „Mehr“ ----------

function toggleMehr(offen) {
  const menu = document.getElementById('mehrMenu');
  const knopf = document.getElementById('btnMehr');
  const auf = offen === undefined ? menu.hidden : offen;
  menu.hidden = !auf;
  knopf.setAttribute('aria-expanded', String(auf));
  if (auf) {
    menu.querySelector('.menu-eintrag').focus();
    document.addEventListener('pointerdown', mehrAussen, true);
    document.addEventListener('keydown', mehrTaste, true);
    menu.addEventListener('focusout', mehrFokusWeg);
  } else {
    document.removeEventListener('pointerdown', mehrAussen, true);
    document.removeEventListener('keydown', mehrTaste, true);
    menu.removeEventListener('focusout', mehrFokusWeg);
  }
}

function mehrAussen(e) {
  if (!document.getElementById('mehrMenu').contains(e.target) && !document.getElementById('btnMehr').contains(e.target)) toggleMehr(false);
}

function mehrTaste(e) {
  if (e.key === 'Escape') {
    e.preventDefault();
    toggleMehr(false);
    document.getElementById('btnMehr').focus();
  }
}

// Fokus verlässt das Menü (z. B. mit Tab): schliessen
function mehrFokusWeg(e) {
  const menu = document.getElementById('mehrMenu');
  if (e.relatedTarget && !menu.contains(e.relatedTarget) && e.relatedTarget.id !== 'btnMehr') toggleMehr(false);
}

// Menüeintrag: Menü schliessen, dann Aktion (im selben Klick, damit z. B. die Dateiauswahl erlaubt ist)
function mehrAktion(aktion) {
  toggleMehr(false);
  aktion();
}

// Kader-Datei wählen (Menü „Mehr“ und Knopf beim Schiedsrichter-Feld, solange kein Kader geladen ist)
function kaderWaehlen() {
  document.getElementById('kaderDatei').click();
}

// ---------- Schublade (Seitenleiste unter 1180 px) ----------

const SCHUBLADE_MQ = window.matchMedia('(max-width: 1179px)');

function schubladeOffen() {
  return document.querySelector('.app').classList.contains('schublade-offen');
}

function oeffneSchublade() {
  document.querySelector('.app').classList.add('schublade-offen');
  document.getElementById('schubladeHintergrund').hidden = false;
  document.querySelector('.haupt').inert = true;   // Rest der Seite gesperrt
  document.getElementById('btnSpiele').setAttribute('aria-expanded', 'true');
  document.addEventListener('keydown', schubladeTaste, true);
  const ziel = document.querySelector('#seitenleiste .sl-eintrag.aktiv') || document.getElementById('navSpiel');
  ziel.focus();
}

function schliesseSchublade(fokusZurueck = true) {
  if (!schubladeOffen()) return;
  document.querySelector('.app').classList.remove('schublade-offen');
  document.getElementById('schubladeHintergrund').hidden = true;
  document.querySelector('.haupt').inert = false;
  document.getElementById('btnSpiele').setAttribute('aria-expanded', 'false');
  document.removeEventListener('keydown', schubladeTaste, true);
  if (fokusZurueck) document.getElementById('btnSpiele').focus();
}

function schubladeTaste(e) {
  if (e.key === 'Escape') { e.preventDefault(); schliesseSchublade(); }
}

// ---------- Höhen messen: Werkzeugleiste und kompakte Score-Leiste ----------
// Als CSS-Variablen, damit stehende Elemente und Sprünge zu Feldern den richtigen Abstand haben
// (ändert sich beim Drehen, bei Sprachwechsel oder anderer Textgrösse).

function messeHoehen() {
  const wurzel = document.documentElement.style;
  const leiste = document.querySelector('.werkzeugleiste');
  if (leiste) wurzel.setProperty('--wl-hoehe', Math.ceil(leiste.getBoundingClientRect().height) + 'px');
  const karte = document.querySelector('.score-karte');
  const kompakt = window.matchMedia('(max-width: 999px)').matches;
  wurzel.setProperty('--scoreleiste-hoehe', karte && kompakt ? Math.ceil(karte.getBoundingClientRect().height) + 'px' : '0px');
}

// ---------- Hinweis für zu alte Geräte (App bleibt bedienbar) ----------

function geraetZuAlt() {
  return typeof HTMLDialogElement !== 'function'
    || !(window.CSS && CSS.supports('container-type: inline-size'))
    || !('DecompressionStream' in window);   // ab iPadOS / iOS 16.4
}

function zeigeAltHinweis() {
  let hinweis = document.getElementById('altHinweis');
  if (!geraetZuAlt()) { if (hinweis) hinweis.remove(); return; }
  if (!hinweis) {
    hinweis = document.createElement('div');
    hinweis.id = 'altHinweis';
    hinweis.className = 'alt-hinweis no-print';
    hinweis.setAttribute('role', 'status');
    document.body.prepend(hinweis);
  }
  hinweis.textContent = t('old_device');
}

// ---------- Einrichten (einmal beim Start) ----------

function initLayout() {
  document.getElementById('btnSpiele').addEventListener('click', () => (schubladeOffen() ? schliesseSchublade() : oeffneSchublade()));
  document.getElementById('schubladeHintergrund').addEventListener('click', () => schliesseSchublade());
  // Eintrag in der Schublade gewählt: Schublade zu
  document.querySelectorAll('#seitenleiste .sl-eintrag').forEach((e) => e.addEventListener('click', () => schliesseSchublade(false)));
  // auf quer gedreht (ab 1180 px): Schublade schliessen, feste Seitenleiste erscheint
  SCHUBLADE_MQ.addEventListener('change', (e) => { if (!e.matches) schliesseSchublade(false); messeHoehen(); });
  document.getElementById('bereitChip').addEventListener('click', () => {
    const erster = pruefeSicherbar({ name: getEffectiveRefName(), overall_grade: segWert('overall_grade') }).find((p) => !p.ok);
    if (erster) erster.aktion();
  });
  if (window.ResizeObserver) {
    const ro = new ResizeObserver(messeHoehen);
    // ganzer Rahmen (border-box): auch Höhenänderungen durch Innenabstand oder Zeilenumbruch zählen
    ro.observe(document.querySelector('.werkzeugleiste'), { box: 'border-box' });
    ro.observe(document.querySelector('.score-karte'), { box: 'border-box' });
  }
  window.addEventListener('resize', messeHoehen);
  messeHoehen();
  zeigeAltHinweis();
}
