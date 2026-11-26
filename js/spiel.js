// Fenster „Spiel bearbeiten“ und Titel des Spiels (Etappe 2.6)
//
// Die Felder (spiel_id, spiel_liga, spiel_datum, spiel_ort, supervisor_name, System) behalten ihre IDs, damit
// saveGlobalState() unverändert bleibt. Gespeichert wird erst mit „Fertig“; „Abbrechen“ / Esc füllen die Felder
// wieder aus den gespeicherten Daten (so kann nichts Verworfenes später mitgespeichert werden).

let sfDaten = {};          // Arbeitskopie Schiedsrichter: { '4-Man_h1': { name, round } }
let sfAltePaarung = null;  // bisherige Begegnung im alten Format (nicht „KURZ – Gegner“)

const spielPraefix = () => `${CLUB.kurz} – `;

function systemKurz(sys) {
  const o = t('system_options').find((x) => x.val === sys);
  return o ? o.kurz : sys;
}

// ---------- Titel über der Bewertung ----------

function aktualisiereSpielTitel() {
  const g = (gameData && gameData.global) || {};
  const info = [g.spiel_liga, datumZeitText(g.spiel_datum), g.spiel_ort, systemKurz(currentSystem),
    g.spiel_id ? t('game_nr', { nr: g.spiel_id }) : ''].filter(Boolean).join(' · ');
  const zeile = document.getElementById('spielTitelInfo');
  zeile.textContent = info;
  if (g.supervisor_name) {   // Supervisor nur im Druck
    const sup = document.createElement('span');
    sup.className = 'nur-druck';
    sup.id = 'spielTitelSupervisor';
    sup.textContent = ' · ' + t('print_supervisor', { name: g.supervisor_name });
    zeile.appendChild(sup);
  }
  document.getElementById('spielTitelName').textContent = g.spiel_paarung || t('nav_no_game');
  document.getElementById('spielKopf').hidden = activeTabType === 'stats';
}

// ---------- Hinweise (kein Pflichtpunkt: Sichern bleibt möglich) ----------

function spielHinweise() {
  const nr = (gameData.global && gameData.global.spiel_id || '').trim();
  return [
    { schluessel: 'spielnr', text: t('hint_game_nr'), ok: !!nr, aktion: () => oeffneSpielDialog('spiel_id') },
    { schluessel: 'liga', text: t('hint_league'), ok: !!ligaAusDaten(gameData.global), aktion: () => oeffneSpielDialog('spiel_liga') }
  ];
}

// ---------- Fenster füllen ----------

function fuelleSpielDialog() {
  const g = (gameData && gameData.global) || {};
  document.getElementById('spiel_id').value = g.spiel_id || '';
  document.getElementById('spiel_liga').value = ligaAusDaten(g);
  document.getElementById('spiel_datum').value = g.spiel_datum || '';
  document.getElementById('spiel_ort').value = g.spiel_ort || '';
  document.getElementById('supervisor_name').value = g.supervisor_name || '';
  const paarung = g.spiel_paarung || '';
  document.getElementById('spiel_paarung').value = paarung;
  document.getElementById('sfPraefix').textContent = spielPraefix();
  if (!paarung || paarung.startsWith(spielPraefix())) {
    sfAltePaarung = null;
    document.getElementById('spiel_gegner').value = paarung.slice(spielPraefix().length);
  } else {
    sfAltePaarung = paarung;   // altes Format: unverändert anzeigen und speichern, solange nicht geändert
    document.getElementById('spiel_gegner').value = paarung;
  }
  setzeSeg('system_typ', currentSystem);
  sfDaten = {};
  Object.keys(SYSTEM_CONFIGS).forEach((sys) => SYSTEM_CONFIGS[sys].forEach((ref) => {
    const d = gameData.referees[`${sys}_${ref.id}`];
    sfDaten[`${sys}_${ref.id}`] = { name: (d && d.name) || '', round: (d && d.review_round) || 'R1' };
  }));
  baueSfRollen(currentSystem);
  aktualisiereSfHinweise();
}

function aktualisiereSfHinweise() {
  document.getElementById('sfNrHinweis').hidden = !!document.getElementById('spiel_id').value.trim();
  const gegner = document.getElementById('spiel_gegner').value;
  const alt = sfAltePaarung !== null && gegner === sfAltePaarung;
  document.getElementById('sfPraefix').hidden = alt;
  const hinweis = document.getElementById('sfAltHinweis');
  hinweis.hidden = !alt;
  if (alt) hinweis.textContent = t('opponent_old');
}

// Schiedsrichter je Rolle (Name aus dem Kader oder anderer Name, Durchgang R1/R2)
function baueSfRollen(sys) {
  const box = document.getElementById('sfRollen');
  box.innerHTML = '';
  SYSTEM_CONFIGS[sys].forEach((ref) => {
    const key = `${sys}_${ref.id}`;
    const daten = sfDaten[key];
    const zeile = document.createElement('div');
    zeile.className = 'sf-rolle';
    const titel = document.createElement('span');
    titel.className = 'sf-rolle-name';
    titel.id = `sf_lbl_${ref.id}`;
    titel.textContent = rolle(ref);
    const wahl = document.createElement('select');
    wahl.id = `sf_name_${ref.id}`;
    wahl.setAttribute('aria-labelledby', titel.id);
    const option = (wert, text) => { const o = document.createElement('option'); o.value = wert; o.textContent = text; wahl.appendChild(o); };
    option('', KADER.length ? t('kader_choose') : t('kader_first'));
    KADER.forEach((n) => option(n, n));
    option('_CUSTOM_', t('kader_other'));
    const eigen = document.createElement('input');
    eigen.type = 'text';
    eigen.id = `sf_custom_${ref.id}`;
    eigen.setAttribute('aria-labelledby', titel.id);
    eigen.placeholder = t('ph_other_name');
    const imKader = daten.name && KADER.includes(daten.name);
    wahl.value = imKader ? daten.name : (daten.name ? '_CUSTOM_' : '');
    eigen.value = imKader ? '' : daten.name;
    eigen.hidden = wahl.value !== '_CUSTOM_';
    wahl.addEventListener('change', () => {
      eigen.hidden = wahl.value !== '_CUSTOM_';
      daten.name = wahl.value === '_CUSTOM_' ? eigen.value.trim() : wahl.value;
      if (!eigen.hidden) eigen.focus();
    });
    eigen.addEventListener('input', () => { daten.name = eigen.value.trim(); });
    const runde = document.createElement('div');
    runde.dataset.seg = `sf_round_${ref.id}`;
    runde.dataset.segLabel = titel.id;
    zeile.append(titel, wahl, eigen, runde);
    box.appendChild(zeile);
    baueSegmente(`sf_round_${ref.id}`, t('round_options'), { standard: daten.round, onChange: (v) => { daten.round = v; } });
  });
}

// ---------- Öffnen, Abbrechen, Fertig ----------

function oeffneSpielDialog(fokusId) {
  const dlg = document.getElementById('spielDialog');
  if (dlg.open) return;
  if (typeof toggleMehr === 'function' && !document.getElementById('mehrMenu').hidden) toggleMehr(false);
  fuelleSpielDialog();
  if (typeof dlg.showModal === 'function') dlg.showModal(); else dlg.setAttribute('open', '');
  const ziel = document.getElementById(fokusId || 'spiel_id');
  if (ziel) { ziel.focus(); ziel.scrollIntoView({ block: 'center' }); }
}

function schliesseSpielDialog() {
  const dlg = document.getElementById('spielDialog');
  if (typeof dlg.close === 'function') dlg.close(); else dlg.removeAttribute('open');
}

function spielAbbrechen() {
  fuelleSpielDialog();   // Felder wieder wie gespeichert
  schliesseSpielDialog();
}

function hatBewertungen(sys) {
  return Object.keys(gameData.referees).some((k) => k.startsWith(sys + '_') &&
    gameData.referees[k] && (gameData.referees[k].name || gameData.referees[k].overall_grade));
}

async function spielFertig() {
  const g = gameData.global || {};
  const neuesSystem = segWert('system_typ') || currentSystem;
  if (neuesSystem !== currentSystem && hatBewertungen(currentSystem)) {
    const ok = await bestaetigen({
      titel: t('system_switch_title'),
      text: t('system_switch_text', { alt: systemKurz(currentSystem), neu: systemKurz(neuesSystem) }),
      ja: t('system_switch_yes')
    });
    if (!ok) return;   // zurück ins Fenster
  }

  // 1. Schiedsrichter je Rolle (nur geänderte; neue Einträge mit Standardwerten)
  Object.entries(sfDaten).forEach(([key, w]) => {
    const d = gameData.referees[key];
    const bisherName = (d && d.name) || '', bisherRunde = (d && d.review_round) || 'R1';
    if (w.name === bisherName && w.round === bisherRunde) return;
    const [sys, id] = key.split('_');
    const ref = SYSTEM_CONFIGS[sys].find((r) => r.id === id);
    gameData.referees[key] = { ...(d || { ...getDefaultRefData(), role: ref.role_de }), name: w.name, review_round: w.round };
  });

  // 2. Begegnung: „KURZ – Gegner“; altes Format bleibt, solange nicht geändert
  const gegner = document.getElementById('spiel_gegner').value.trim();
  document.getElementById('spiel_paarung').value =
    sfAltePaarung !== null && document.getElementById('spiel_gegner').value === sfAltePaarung ? sfAltePaarung
      : (gegner ? spielPraefix() + gegner : '');

  // 3. Spieldaten speichern – mit denselben Funktionen wie früher beim Tippen
  const geaendert = (feld, schluessel) => document.getElementById(feld).value !== (g[schluessel] || '');
  const datumNeu = geaendert('spiel_datum', 'spiel_datum');
  const ortNeu = geaendert('spiel_ort', 'spiel_ort');
  const supervisorNeu = geaendert('supervisor_name', 'supervisor_name');
  schliesseSpielDialog();
  if (neuesSystem !== currentSystem) switchSystem(neuesSystem);   // speichert die Spieldaten mit
  else {
    saveGlobalState();
    if (activeTabType === 'ref') loadRefereeForm(activeRefIndex);
    else if (activeTabType === 'summary') renderSummaryView();
  }
  if (datumNeu) handleGlobalDateTimeChange();
  if (ortNeu) handleGlobalArenaChange();
  if (supervisorNeu) handleGlobalSupervisorChange();
  if (activeTabType === 'ref' && (datumNeu || ortNeu || supervisorNeu)) saveCurrentRefData();   // Visum mitspeichern
  renderTabs();
  aktualisiereSpielTitel();
  zeigeBereit();
}

function initSpiel() {
  const dlg = document.getElementById('spielDialog');
  document.getElementById('sfAbbrechen').addEventListener('click', spielAbbrechen);
  document.getElementById('sfFertig').addEventListener('click', spielFertig);
  dlg.addEventListener('cancel', (e) => { e.preventDefault(); spielAbbrechen(); });   // Esc = Abbrechen
  document.getElementById('spielTitel').addEventListener('click', () => oeffneSpielDialog());
  document.getElementById('spiel_id').addEventListener('input', aktualisiereSfHinweise);
  document.getElementById('spiel_gegner').addEventListener('input', aktualisiereSfHinweise);
  aktualisiereSpielTitel();
  // Noch kein Spiel erfasst (kein Gegner und kein Datum): Fenster automatisch öffnen
  const g = gameData.global || {};
  if (!g.spiel_paarung && !g.spiel_datum) oeffneSpielDialog();
}
