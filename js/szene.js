// Szenen pro Kriterium (Etappe 2.7): Fenster „Szene“, Chips unter dem Kriterium, freier Text.
//
// Gespeichert wird wie bisher in der Notiz des Kriteriums (note_1 … note_7), eine Szene pro Zeile:
//   [P2 08:34] Text      (Drittel P1/P2/P3/OT, Restzeit auf der Matchuhr mm:ss)
//   [P2] Text            (ohne Zeit)
// Neue Szenen werden angehängt (Reihenfolge der Eingabe); geänderte bleiben an ihrer Stelle.
// Zeilen ohne […] sind freier Text. Die Anzeige sortiert nach Drittel und absteigender Restzeit.

const DRITTEL = ['P1', 'P2', 'P3', 'OT'];
let szeneLetzte = { spiel: null, drittel: 'P1' };   // zuletzt benutztes Drittel (pro Spiel)
let szeneAktiv = null;                                // { kriterium, zeile (Index oder null = neu) }

// ---------- Lesen und Sortieren ----------

// Drittel und Zeit aus einer Angabe lesen – auch aus alten Formen, Gross-/Kleinschreibung egal:
//   „P2 08:34“, „p2 8:34“, „2. Drittel 8:34“, „2.D 8:34“, „2d“, „OT 3:00“, „Verlängerung“.
// Ergebnis { drittel, sekunden } oder null (nicht lesbar).
function leseStempel(stempel) {
  const m = /^(?:p\s*([123])|([123])\s*\.?\s*d(?:rittel)?\.?|(ot|verl(?:ängerung)?\.?))\s*(?:(\d{1,2})[:.](\d{2}))?$/i.exec(String(stempel).trim());
  if (!m) return null;
  const drittel = m[3] ? 'OT' : 'P' + (m[1] || m[2]);
  if (m[4] === undefined) return { drittel, sekunden: null };
  const min = parseInt(m[4], 10), sek = parseInt(m[5], 10);
  if (sek >= 60 || min > 20 || (min === 20 && sek > 0)) return null;
  return { drittel, sekunden: min * 60 + sek };
}

// Eine Zeile der Notiz zerlegen. Ergebnis null = freier Text.
// stempel = die gespeicherte Angabe Zeichen für Zeichen (bleibt erhalten, solange Drittel/Zeit nicht geändert werden).
function leseSzene(zeile) {
  const m = /^\[([^\]]*)\]\s?(.*)$/.exec(zeile);
  if (!m) return null;
  const stempel = m[1];
  const gelesen = leseStempel(stempel);
  if (!gelesen) return { stempel, text: m[2], drittel: null, sekunden: null, lesbar: false };   // alte, unlesbare Angabe
  return { stempel, text: m[2], drittel: gelesen.drittel, sekunden: gelesen.sekunden, lesbar: true };
}

// Alle Szenen einer Notiz mit ihrer Zeilennummer, sortiert für die Anzeige (und den Druck):
// Drittel 1–3, OT; darin Restzeit absteigend (20:00 zuerst), ohne Zeit am Ende des Drittels;
// unlesbare alte Angaben ganz am Ende. Gleichstand: Reihenfolge der Eingabe.
function szenenSortiert(notiz) {
  const zeilen = (notiz || '').split('\n');
  const szenen = [];
  zeilen.forEach((z, i) => { const s = leseSzene(z); if (s) szenen.push({ ...s, zeile: i }); });
  const rang = (s) => (s.lesbar ? DRITTEL.indexOf(s.drittel) : 99);
  return szenen.sort((a, b) =>
    rang(a) - rang(b)
    || (a.lesbar && b.lesbar ? (b.sekunden === null ? -1 : b.sekunden) - (a.sekunden === null ? -1 : a.sekunden) : 0)
    || a.zeile - b.zeile);
}

function freierText(notiz) {
  return (notiz || '').split('\n').filter((z) => !leseSzene(z)).join('\n');
}

function zeitText(sekunden) {
  return `${String(Math.floor(sekunden / 60)).padStart(2, '0')}:${String(sekunden % 60).padStart(2, '0')}`;
}

function stempelText(s) {
  if (!s.lesbar) return s.stempel;
  return s.sekunden === null ? s.drittel : `${s.drittel} ${zeitText(s.sekunden)}`;
}

// Eingabe „834“, „8:34“, „08 34“ -> Sekunden; '' -> null; ungültig -> NaN
function leseZeit(eingabe) {
  const roh = String(eingabe || '').trim();
  if (!roh) return null;
  let m, s;
  if (/^\d{1,2}[:.\s]\d{1,2}$/.test(roh)) { [m, s] = roh.split(/[:.\s]/).map((x) => parseInt(x, 10)); }
  else if (/^\d{1,4}$/.test(roh)) { const z = roh.padStart(4, '0'); m = parseInt(z.slice(0, 2), 10); s = parseInt(z.slice(2), 10); }
  else return NaN;
  if (s >= 60 || m > 20 || (m === 20 && s > 0)) return NaN;
  return m * 60 + s;
}

// ---------- Notiz lesen/schreiben (verstecktes Feld note_i = gespeicherter Wert) ----------

function notizFeld(k) { return document.getElementById(`note_${k}`); }

function speichereNotiz(k, notiz) {
  notizFeld(k).value = notiz;
  saveCurrentRefData();
  zeigeSzenen(k);
}

// ---------- Anzeige: Chips und freier Text ----------

function zeigeSzenen(k) {
  const notiz = notizFeld(k).value;
  const liste = document.getElementById(`szenen_${k}`);
  liste.innerHTML = '';
  szenenSortiert(notiz).forEach((s) => {
    const li = document.createElement('li');
    const b = document.createElement('button');
    b.type = 'button';
    b.className = 'szene-chip';
    b.dataset.zeile = s.zeile;
    const zeit = document.createElement('span');
    zeit.className = 'szene-zeit';
    zeit.textContent = stempelText(s);
    const text = document.createElement('span');
    text.className = 'szene-text';
    text.textContent = s.text;
    b.append(zeit, text);
    b.setAttribute('aria-label', t('scene_chip_label', { stempel: stempelText(s), text: s.text || '–' }));
    b.addEventListener('click', () => oeffneSzene(k, s.zeile));
    li.appendChild(b);
    liste.appendChild(li);
  });
  const frei = document.getElementById(`note_frei_${k}`);
  if (document.activeElement !== frei) frei.value = freierText(notiz);
  frei.setAttribute('aria-label', t('scene_free_label', { kriterium: t('radar_labels')[k - 1] }));
}

function zeigeAlleSzenen() {
  for (let k = 1; k <= 7; k++) zeigeSzenen(k);
}

// Freier Text geändert: Notiz = Szenen (bisherige Reihenfolge) + freier Text
function freierTextGeaendert(k) {
  const szenenZeilen = notizFeld(k).value.split('\n').filter((z) => leseSzene(z));
  const frei = document.getElementById(`note_frei_${k}`).value;
  notizFeld(k).value = [...szenenZeilen, ...(frei ? [frei] : [])].join('\n');
  saveCurrentRefData();
}

// ---------- Fenster „Szene“ ----------

function spielSchluessel() {
  const g = (gameData && gameData.global) || {};
  return `${g.spiel_paarung || ''}|${g.spiel_datum || ''}`;
}

function vorgewaehltesDrittel() {
  return szeneLetzte.spiel === spielSchluessel() ? szeneLetzte.drittel : 'P1';   // anderes/neues Spiel: wieder 1.
}

function oeffneSzene(k, zeile = null) {
  const dlg = document.getElementById('szeneDialog');
  szeneAktiv = { kriterium: k, zeile };
  const vorhanden = zeile === null ? null : leseSzene(notizFeld(k).value.split('\n')[zeile]);
  document.getElementById('szeneDialogTitel').textContent = t('scene_title', { kriterium: t('radar_labels')[k - 1] });
  setzeSeg('szene_drittel', vorhanden && vorhanden.lesbar ? vorhanden.drittel : vorgewaehltesDrittel());
  document.getElementById('szeneZeit').value = vorhanden && vorhanden.sekunden !== null ? zeitText(vorhanden.sekunden) : '';
  document.getElementById('szeneNotiz').value = vorhanden ? vorhanden.text : '';
  document.getElementById('szeneFehler').hidden = true;
  document.getElementById('szeneLoeschen').hidden = zeile === null;
  document.getElementById('szeneOk').textContent = zeile === null ? t('stamp_add') : t('scene_save');
  // Bisherige Angabe in einem anderen Format: bleibt erhalten, solange Drittel und Zeit nicht gewählt werden
  szeneAktiv.vorhanden = vorhanden;
  szeneAktiv.gewaehlt = false;
  zeigeAltHinweisSzene();
  if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
  (zeile === null ? document.getElementById('szeneZeit') : document.getElementById('szeneNotiz')).focus();
}

function zeigeAltHinweisSzene() {
  const alt = document.getElementById('szeneAlt');
  const v = szeneAktiv && szeneAktiv.vorhanden;
  const anders = v && (!v.lesbar || v.stempel !== stempelText(v));   // nicht im neuen Format gespeichert
  alt.hidden = !anders;
  if (!anders) return;
  const schluessel = szeneAktiv.gewaehlt ? 'scene_old_replace' : (v.lesbar ? 'scene_old_read' : 'scene_old_keep');
  alt.textContent = t(schluessel, { stempel: v.stempel });
}

// Drittel angetippt oder Zeit eingegeben: alte Angabe wird beim Sichern ersetzt
function szeneGewaehlt() {
  if (!szeneAktiv || szeneAktiv.gewaehlt) return;
  szeneAktiv.gewaehlt = true;
  zeigeAltHinweisSzene();
}

function schliesseSzene() {
  const dlg = document.getElementById('szeneDialog');
  if (typeof dlg.close === 'function') dlg.close(); else dlg.removeAttribute('open');
  szeneAktiv = null;
}

function formatiereSzeneZeit() {
  const feld = document.getElementById('szeneZeit');
  const sek = leseZeit(feld.value);
  if (sek !== null && !isNaN(sek)) feld.value = zeitText(sek);
}

function szeneUebernehmen() {
  if (!szeneAktiv) return;
  const sek = leseZeit(document.getElementById('szeneZeit').value);
  const fehler = document.getElementById('szeneFehler');
  if (sek !== null && isNaN(sek)) {
    fehler.hidden = false;
    fehler.textContent = t('scene_time_invalid');
    document.getElementById('szeneZeit').focus();
    return;
  }
  const drittel = segWert('szene_drittel') || 'P1';
  // Zeilenumbrüche werden Leerzeichen: jede Szene bleibt genau eine Zeile
  const text = document.getElementById('szeneNotiz').value.replace(/\s*\r?\n\s*/g, ' ').trim();
  // Bestehende Szene, Drittel und Zeit nicht angetippt: bisherige Angabe Zeichen für Zeichen behalten
  const behalten = szeneAktiv.vorhanden && !szeneAktiv.gewaehlt;
  const stempel = behalten ? szeneAktiv.vorhanden.stempel : (sek === null ? drittel : `${drittel} ${zeitText(sek)}`);
  const zeile = `[${stempel}]${text ? ' ' + text : ''}`;
  const { kriterium: k, zeile: nr } = szeneAktiv;
  const zeilen = notizFeld(k).value ? notizFeld(k).value.split('\n') : [];
  if (nr === null) zeilen.push(zeile);   // neu: anhängen (Reihenfolge der Eingabe)
  else zeilen[nr] = zeile;               // geändert: bleibt an derselben Stelle
  if (!behalten) szeneLetzte = { spiel: spielSchluessel(), drittel };
  schliesseSzene();
  speichereNotiz(k, zeilen.join('\n'));
  zeigeToast(t(nr === null ? 'scene_added' : 'scene_changed', { stempel }), 'ok');
}

async function szeneLoeschen() {
  if (!szeneAktiv || szeneAktiv.zeile === null) return;
  const { kriterium: k, zeile: nr } = szeneAktiv;
  if (!(await bestaetigen({ titel: t('scene_delete_title'), text: t('scene_delete_text'), ja: t('scene_delete'), gefahr: true }))) return;
  const zeilen = notizFeld(k).value.split('\n');
  zeilen.splice(nr, 1);
  schliesseSzene();
  speichereNotiz(k, zeilen.join('\n'));
}

function initSzenen() {
  document.querySelectorAll('.szene-knopf').forEach((b) => b.addEventListener('click', () => oeffneSzene(parseInt(b.dataset.szene, 10))));
  document.querySelectorAll('.notiz-frei').forEach((f) => f.addEventListener('input', () => freierTextGeaendert(parseInt(f.dataset.notiz, 10))));
  document.getElementById('szeneAbbrechen').addEventListener('click', schliesseSzene);
  document.getElementById('szeneOk').addEventListener('click', szeneUebernehmen);
  document.getElementById('szeneLoeschen').addEventListener('click', szeneLoeschen);
  document.getElementById('szeneDialog').addEventListener('cancel', (e) => { e.preventDefault(); schliesseSzene(); });   // Esc
  const zeit = document.getElementById('szeneZeit');
  zeit.addEventListener('blur', formatiereSzeneZeit);
  zeit.addEventListener('keydown', (e) => { if (e.key === 'Enter') { e.preventDefault(); formatiereSzeneZeit(); szeneUebernehmen(); } });
  zeit.addEventListener('input', () => { document.getElementById('szeneFehler').hidden = true; szeneGewaehlt(); });
  // Drittel angetippt (auch das bereits gewählte) zählt als Wahl
  document.querySelector('[data-seg="szene_drittel"]').addEventListener('click', (e) => { if (e.target.closest('label')) szeneGewaehlt(); });
  document.querySelector('[data-seg="szene_drittel"]').addEventListener('keydown', (e) => { if (e.key.startsWith('Arrow') || e.key === ' ') szeneGewaehlt(); });
}
