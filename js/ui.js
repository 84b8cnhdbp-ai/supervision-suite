// Zustand, Reiter, Formular, Score-Anzeige, Gespann-Übersicht, Radar
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

let currentSystem = "4-Man";
let activeTabType = "ref"; 
let activeRefIndex = 0;
let gameData = {
  global: {},
  referees: {}
};

function initApp() {
  loadLanguagePreference();
  loadTheme();
  loadFullState();
  setupRefereeDropdown();
  applyTranslations();
  renderTabs();
  initLayout();
  if (activeTabType === "summary") {
    renderSummaryView();
  } else if (activeTabType === "stats") {
    selectStatsTab();
  } else {
    loadRefereeForm(activeRefIndex);
  }
  initSpiel();
  initSzenen();
  initStatistik();
  document.getElementById('crew_notes').addEventListener('input', saveGlobalState);   // Gespann-Notiz
}

function setupRefereeDropdown() {
  const sel = document.getElementById('current_schiri_name');
  sel.innerHTML = '';
  const leer = document.createElement('option');
  leer.value = '';
  leer.textContent = KADER.length ? t('kader_choose') : t('kader_first');
  sel.appendChild(leer);
  // Ohne Kader: Knopf „Kader importieren“ beim Schiedsrichter-Feld (gleich wie im Menü „Mehr“)
  const knopf = document.getElementById('btnKaderForm');
  if (knopf) knopf.hidden = KADER.length > 0;
  if (typeof aktualisiereSeitenleiste === 'function') aktualisiereSeitenleiste();
  KADER.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    sel.appendChild(opt);
  });
  const optOther = document.createElement('option');
  optOther.value = "_CUSTOM_";
  optOther.textContent = t('kader_other');
  sel.appendChild(optOther);
}

function handleRefSelectChange() {
  const sel = document.getElementById('current_schiri_name');
  const customInput = document.getElementById('current_schiri_name_custom');
  if (sel.value === "_CUSTOM_") {
    customInput.style.display = "block";
    customInput.focus();
  } else {
    customInput.style.display = "none";
    customInput.value = "";
  }
  saveCurrentRefData();
  updatePartnerField();
}

// Darstellung wählen: 'auto' (folgt dem System), 'light', 'dark' (Grundfunktionen in js/theme.js)
function setTheme(wahl) {
  if (wahl === 'auto') localStorage.removeItem(THEME_KEY);
  else localStorage.setItem(THEME_KEY, wahl);
  applyTheme();
  setzeSeg('darstellung', getThemePref());
  redrawCharts();
}

// Netzdiagramme neu zeichnen (Farben kommen aus den CSS-Variablen)
function redrawCharts() {
  if (activeTabType === "summary") renderSummaryView();
  else if (activeTabType === "ref") calcScores(false);
}

function loadTheme() {
  // Wechselt das System zwischen hell und dunkel, Diagramme nachziehen
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
    if (getThemePref() === 'auto') redrawCharts();
  });
}

function switchSystem(newSys) {
  currentSystem = newSys;
  activeTabType = "ref";
  activeRefIndex = 0;
  saveGlobalState();
  renderTabs();
  loadRefereeForm(activeRefIndex);
}

// Reiter in der Werkzeugleiste (Tabs mit Pfeiltasten; Beschriftung siehe js/layout.js)
function renderTabs() {
  const box = document.getElementById('tabsContainer');
  box.innerHTML = "";
  const refs = SYSTEM_CONFIGS[currentSystem];
  const eintraege = refs.map((ref, index) => ({
    text: reiterText(ref), schluessel: ref.id, steuert: 'singleRefView', klasse: '',
    aktiv: activeTabType === "ref" && index === activeRefIndex, klick: () => selectRefTab(index)
  }));
  if (refs.length > 1) {
    eintraege.push({ text: { sichtbar: t('txt_tab_crew'), voll: t('txt_tab_crew') }, schluessel: 'gespann', steuert: 'summaryView',
      klasse: ' tab-summary', aktiv: activeTabType === "summary", klick: () => selectSummaryTab() });
  }
  const einerAktiv = eintraege.some((e) => e.aktiv);
  eintraege.forEach((e, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'tab-btn' + e.klasse + (e.aktiv ? ' active' : '');
    btn.setAttribute('role', 'tab');
    btn.setAttribute('aria-selected', String(e.aktiv));
    btn.setAttribute('aria-controls', e.steuert);
    btn.dataset.reiter = e.schluessel;
    btn.tabIndex = e.aktiv || (!einerAktiv && i === 0) ? 0 : -1;
    btn.title = e.text.voll;
    btn.textContent = e.text.sichtbar;
    btn.onclick = e.klick;
    btn.addEventListener('keydown', reiterTaste);
    box.appendChild(btn);
  });
  aktualisiereSeitenleiste();
}

function selectRefTab(index) {
  if (activeTabType === "ref") saveCurrentRefData();
  activeTabType = "ref";
  activeRefIndex = index;
  document.getElementById('singleRefView').style.display = "";   // Anzeige bestimmt das CSS (z. B. zwei Spalten)
  document.getElementById('summaryView').style.display = "none";
  document.getElementById('seasonStatsView').style.display = "none";
  renderTabs();
  loadRefereeForm(activeRefIndex);
}

function selectSummaryTab() {
  if (activeTabType === "ref") saveCurrentRefData();
  activeTabType = "summary";
  document.getElementById('singleRefView').style.display = "none";
  document.getElementById('summaryView').style.display = "";   // Anzeige bestimmt das CSS (z. B. zwei Spalten)
  document.getElementById('seasonStatsView').style.display = "none";
  renderTabs();
  renderSummaryView();
}

function selectStatsTab() {
  if (activeTabType === "ref") saveCurrentRefData();
  activeTabType = "stats";
  document.getElementById('singleRefView').style.display = "none";
  document.getElementById('summaryView').style.display = "none";
  document.getElementById('seasonStatsView').style.display = "";   // Anzeige bestimmt das CSS (z. B. zwei Spalten)
  renderTabs();
}

function adjustLabelsForRole(refConfig) {
  // Kriterien-Texte je Rolle (Linesperson hat eigene Texte)
  const kriterien = t(refConfig.type === 'lines' ? 'crit_lines' : 'crit_head');
  kriterien.forEach((k, i) => {
    document.getElementById(`lbl_perf_${i + 1}`).innerHTML =
      `<strong>${escapeHtml(k.t)}</strong><br><small style="color:var(--text-muted);">${escapeHtml(k.s)}</small>`;
  });
}

function getEffectiveRefName() {
  const sel = document.getElementById('current_schiri_name');
  const custom = document.getElementById('current_schiri_name_custom');
  if (sel.value === "_CUSTOM_") {
    return custom.value.trim();
  }
  return sel.value;
}

// AUTOMATISCHE GESPASS-PARTNER-BERECHNUNG
function updatePartnerField() {
  const currentRefConfig = SYSTEM_CONFIGS[currentSystem][activeRefIndex];
  if (!currentRefConfig) return;

  // Anzeige in der gewählten Sprache; gespeichert wird partnerText(true) (immer deutsch)
  document.getElementById('current_schiri_partner').value = partnerText(false);
}

// Partner des aktiven Reiters als Text. deutsch=true: Wert zum Speichern (sprachunabhängig).
function partnerText(deutsch) {
  const partners = [];
  SYSTEM_CONFIGS[currentSystem].forEach((ref, idx) => {
    if (idx !== activeRefIndex) {
      const pData = gameData.referees[`${currentSystem}_${ref.id}`];
      if (pData && pData.name && pData.name.trim()) {
        partners.push(`${pData.name} (${deutsch ? ref.role_de : rolle(ref)})`);
      }
    }
  });
  if (partners.length > 0) return partners.join(", ");
  return deutsch ? I18N.de.partner_none : t('partner_none');
}

// AUTOMATISCHES SPIEGELN VON ORT & DATUM
function updateDerivedLocationAndDate() {
  const arena = document.getElementById('spiel_ort').value.trim();
  const dtVal = document.getElementById('spiel_datum').value;

  let formattedDate = "";
  if (dtVal) {
    const d = new Date(dtVal);
    if (!isNaN(d.getTime())) {
      const day = String(d.getDate()).padStart(2, '0');
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const year = d.getFullYear();
      formattedDate = `${day}.${month}.${year}`;
    }
  }

  const targetField = document.getElementById('visum_ort_datum');
  if (arena && formattedDate) {
    targetField.value = `${arena}, ${formattedDate}`;
  } else if (formattedDate) {
    targetField.value = formattedDate;
  } else {
    targetField.value = arena;
  }
}

function handleGlobalDateTimeChange() {
  saveGlobalState();
  updateDerivedLocationAndDate();
}

function handleGlobalArenaChange() {
  saveGlobalState();
  updateDerivedLocationAndDate();
}

function handleGlobalSupervisorChange() {
  saveGlobalState();
  document.getElementById('visum_name').value = document.getElementById('supervisor_name').value;
}

function loadRefereeForm(index) {
  const refConfig = SYSTEM_CONFIGS[currentSystem][index];
  const roleName = rolle(refConfig);
  document.getElementById('activeRefLabel').innerText = roleName;
  adjustLabelsForRole(refConfig);

  const refKey = `${currentSystem}_${refConfig.id}`;
  const data = gameData.referees[refKey] || getDefaultRefData();

  const sel = document.getElementById('current_schiri_name');
  const custom = document.getElementById('current_schiri_name_custom');
  if (data.name && KADER.includes(data.name)) {
    sel.value = data.name;
    custom.style.display = "none";
    custom.value = "";
  } else if (data.name) {
    sel.value = "_CUSTOM_";
    custom.style.display = "block";
    custom.value = data.name;
  } else {
    sel.value = "";
    custom.style.display = "none";
    custom.value = "";
  }

  setzeSeg('current_review_round', data.review_round || "R1");

  const radios = document.querySelectorAll('input[name="overall_grade"]');
  radios.forEach(r => {
    r.checked = (r.value === (data.overall_grade || ""));
  });

  for (let i = 1; i <= 7; i++) {
    setzeSeg(`perf_${i}`, data[`perf_${i}`] || "80");
    document.getElementById(`note_${i}`).value = data[`note_${i}`] || "";
  }
  zeigeAlleSzenen();   // Chips und freier Text aus der gespeicherten Notiz (js/szene.js)

  if (data.coach_trend) setzeSeg('coach_trend', data.coach_trend);
  if (data.coach_attitude) setzeSeg('coach_attitude', data.coach_attitude);
  if (data.coach_feedback) setzeSeg('coach_feedback', data.coach_feedback);

  document.getElementById('top_strengths').value = data.top_strengths || "";
  document.getElementById('top_workon').value = data.top_workon || "";
  document.getElementById('general_report').value = data.general_report || "";
  
  // Ort/Datum und Visum spiegeln
  if (data.visum_ort_datum) {
    document.getElementById('visum_ort_datum').value = data.visum_ort_datum;
  } else {
    updateDerivedLocationAndDate();
  }

  document.getElementById('visum_name').value = data.visum_name || document.getElementById('supervisor_name').value || "";

  updatePartnerField();
  calcScores(false);
}

function saveCurrentRefData() {
  const refConfig = SYSTEM_CONFIGS[currentSystem][activeRefIndex];
  if (!refConfig) return;
  const refKey = `${currentSystem}_${refConfig.id}`;
  const selectedGrade = document.querySelector('input[name="overall_grade"]:checked');

  const data = {
    role: refConfig.role_de,              // gespeicherte Werte immer deutsch
    name: getEffectiveRefName(),
    review_round: segWert('current_review_round'),
    partner: partnerText(true),
    overall_grade: selectedGrade ? selectedGrade.value : "",
    coach_trend: segWert('coach_trend'),
    coach_attitude: segWert('coach_attitude'),
    coach_feedback: segWert('coach_feedback'),
    top_strengths: document.getElementById('top_strengths').value,
    top_workon: document.getElementById('top_workon').value,
    general_report: document.getElementById('general_report').value,
    visum_ort_datum: document.getElementById('visum_ort_datum').value,
    visum_name: document.getElementById('visum_name').value
  };

  for (let i = 1; i <= 7; i++) {
    data[`perf_${i}`] = segWert(`perf_${i}`);
    data[`note_${i}`] = document.getElementById(`note_${i}`).value;
  }

  gameData.referees[refKey] = data;
  saveToStorage();
  aktualisiereReiter();   // Name im Reiter („H1 · Meier“) sofort nachführen
}

function readFormData() {
  const selectedGrade = document.querySelector('input[name="overall_grade"]:checked');
  const d = {
    overall_grade: selectedGrade ? selectedGrade.value : "",
    coach_trend: segWert('coach_trend'),
    coach_attitude: segWert('coach_attitude'),
    coach_feedback: segWert('coach_feedback')
  };
  for (let i = 1; i <= 7; i++) d[`perf_${i}`] = segWert(`perf_${i}`);
  return d;
}

// Status zum Gesamtscore: Text, Ringfarbe, Schriftfarbe (Schwellen wie bisher)
function scoreStatus(total) {
  if (total === null) return { text: 'status_missing', farbe: '--r-none', schrift: '--secondary' };
  if (total > 80) return { text: 'status_exc', farbe: '--r-pp', schrift: '--t-good' };
  if (total >= 75) return { text: 'status_good', farbe: '--r-p', schrift: '--t-good2' };
  if (total >= 60) return { text: 'status_sat', farbe: '--r-solid', schrift: '--t-solid' };
  if (total >= 45) return { text: 'status_ni', farbe: '--r-m', schrift: '--t-warn' };
  return { text: 'status_unsat', farbe: '--r-mm', schrift: '--t-bad' };
}

// „Bereit zum Sichern?“: erledigte Punkte mit Haken, fehlende antippbar (springt zum Feld)
function zeigeBereit() {
  const liste = document.getElementById('bereitListe');
  if (!liste || activeTabType !== 'ref') return;
  const punkte = pruefeSicherbar({ name: getEffectiveRefName(), overall_grade: segWert('overall_grade') });
  liste.innerHTML = '';
  punkte.forEach((p) => {
    const li = document.createElement('li');
    const zeichen = document.createElement('span');
    zeichen.className = 'bereit-zeichen ' + (p.ok ? 'ok' : 'fehlt');
    zeichen.setAttribute('aria-hidden', 'true');
    zeichen.textContent = p.ok ? '✓' : '!';
    if (p.ok) {
      li.className = 'bereit-ok';
      li.append(zeichen, document.createTextNode(p.text));
      const sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = ' – ' + t('ready_done');
      li.appendChild(sr);
    } else {
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'bereit-fehlt';
      b.dataset.punkt = p.schluessel;
      b.append(zeichen, document.createTextNode(p.text));
      const sr = document.createElement('span'); sr.className = 'sr-only'; sr.textContent = ' – ' + t('ready_missing');
      b.appendChild(sr);
      b.addEventListener('click', p.aktion);
      li.appendChild(b);
    }
    liste.appendChild(li);
  });
  // Hinweise (kein Pflichtpunkt, Sichern bleibt möglich), getrennt unter „Hinweise“
  const hinweise = spielHinweise().filter((h) => !h.ok);
  if (hinweise.length) {
    const kopf = document.createElement('li');
    kopf.className = 'bereit-gruppe';
    kopf.textContent = t('ready_hints');
    liste.appendChild(kopf);
    hinweise.forEach((h) => {
      const li = document.createElement('li');
      const b = document.createElement('button');
      b.type = 'button';
      b.className = 'bereit-hinweis';
      b.dataset.punkt = h.schluessel;
      const zeichen = document.createElement('span');
      zeichen.className = 'bereit-zeichen hinweis';
      zeichen.setAttribute('aria-hidden', 'true');
      zeichen.textContent = 'i';
      b.append(zeichen, document.createTextNode(h.text));
      b.addEventListener('click', h.aktion);
      li.appendChild(b);
      liste.appendChild(li);
    });
  }
  const fehlen = punkte.filter((p) => !p.ok).length;
  const chip = document.getElementById('bereitChip');
  if (chip) {
    chip.textContent = fehlen ? t('ready_chip_open', { n: fehlen })
      : (hinweise.length ? t('ready_chip_hint', { n: hinweise.length }) : t('ready_chip_ok'));
    chip.classList.toggle('bereit-chip-ok', !fehlen);
    chip.classList.toggle('bereit-chip-hinweis', !fehlen && hinweise.length > 0);
    chip.disabled = !fehlen && !hinweise.length;
    chip.setAttribute('aria-label', fehlen ? t('ready_no', { n: fehlen }) : t('ready_yes') + (hinweise.length ? ' ' + hinweise[0].text : ''));
  }
  if (typeof aktualisiereSpielTitel === 'function' && document.getElementById('spielTitelName')) aktualisiereSpielTitel();
  const status = document.getElementById('bereitStatus');
  status.textContent = fehlen ? t('ready_no', { n: fehlen }) : t('ready_yes');
  status.classList.toggle('bereit-ja', !fehlen);
}

function calcScores(shouldSave = true) {
  const sc = computeRefScores(readFormData());
  const fmt = v => v === null ? "–" : v + "%";

  document.getElementById('scoreVal').innerText = fmt(sc.total);
  document.getElementById('subScorePart2').innerText = fmt(sc.part2);
  document.getElementById('subScorePart3').innerText = fmt(sc.part3);
  document.getElementById('subScorePart4').innerText = fmt(sc.part4);

  zeigeStufenText();   // Definition der gewählten Stufe bzw. Hinweis (oranger Rahmen)

  // Status und Ring (Schwellen unverändert, siehe scoreStatus)
  const status = scoreStatus(sc.total);
  const statusText = document.getElementById('scoreStatusText');
  statusText.innerText = t(status.text);
  statusText.style.color = `var(${status.schrift})`;
  const ring = document.getElementById('scoreRing');
  const umfang = 2 * Math.PI * 64;
  ring.setAttribute('stroke-dasharray', `${(sc.total === null ? 0 : umfang * sc.total / 100).toFixed(1)} ${umfang.toFixed(1)}`);
  ring.style.stroke = `var(${status.farbe})`;
  zeigeBereit();

  drawRadar('radarChart', sc.radar);
  if (shouldSave) saveCurrentRefData();
}

// Kleiner Ring (SVG) mit Score in der Statusfarbe
function ringHtml(total, klein) {
  const umfang = 2 * Math.PI * 64;
  const st = scoreStatus(total);
  const strich = total === null ? 0 : umfang * total / 100;
  return `<span class="score-ring${klein ? ' klein' : ''}" aria-hidden="true"><svg viewBox="0 0 150 150">
    <circle class="ring-grund" cx="75" cy="75" r="64"></circle>
    <circle class="ring-wert" cx="75" cy="75" r="64" stroke-dasharray="${strich.toFixed(1)} ${umfang.toFixed(1)}" transform="rotate(-90 75 75)" style="stroke: var(${st.farbe})"></circle>
  </svg><span class="score-zahl">${total === null ? '–' : total + '%'}</span></span>`;
}

// Gespann-Übersicht: Durchschnitt (gleiche Schwellen wie bei der Bewertung), Profil, eine Karte je Rolle
function renderSummaryView() {
  const refs = SYSTEM_CONFIGS[currentSystem];
  const container = document.getElementById('summaryCardsContainer');
  container.innerHTML = "";

  let totalCrewScore = 0, scoredRefs = 0, mitName = 0;
  const avgScores7 = [0, 0, 0, 0, 0, 0, 0];
  const radarCounts = [0, 0, 0, 0, 0, 0, 0];
  const fmt = v => v === null ? "–" : v + "%";

  refs.forEach((ref, idx) => {
    const d = gameData.referees[`${currentSystem}_${ref.id}`] || getDefaultRefData();
    const sc = computeRefScores(d);
    sc.radar.forEach((v, i) => { if (v !== null) { avgScores7[i] += v; radarCounts[i]++; } });
    const refScore = sc.total;
    if (refScore !== null) { totalCrewScore += refScore; scoredRefs++; }
    if (d.name) mitName++;
    const st = scoreStatus(refScore);

    // Echter Knopf: Tipp, Enter oder Leertaste öffnet den Reiter dieser Rolle
    const karte = document.createElement('button');
    karte.type = 'button';
    karte.className = 'gespann-karte';
    karte.dataset.index = idx;
    karte.innerHTML = `
      <span class="gk-kopf"><span class="gk-rolle">${escapeHtml(rolle(ref))}</span>
        <span class="gk-name${d.name ? '' : ' gk-leer'}">${escapeHtml(d.name || t('crew_no_name'))}</span></span>
      <span class="gk-zeile">${ringHtml(refScore, true)}
        <span class="gk-status" style="color: var(${refScore === null ? '--t-warn' : st.schrift})">${escapeHtml(refScore === null ? t('crew_grade_missing') : t(st.text))}</span></span>
      <span class="gk-teile">
        <span><span class="gk-teil-name">${escapeHtml(t('sub_part2'))}</span> ${fmt(sc.part2)}</span>
        <span><span class="gk-teil-name">${escapeHtml(t('sub_part3'))}</span> ${fmt(sc.part3)}</span>
        <span><span class="gk-teil-name">${escapeHtml(t('sub_part4'))}</span> ${fmt(sc.part4)}</span>
      </span>`;
    karte.setAttribute('aria-label', t('crew_card_label', {
      rolle: rolle(ref), name: d.name || t('crew_no_name'), score: fmt(refScore),
      status: refScore === null ? t('crew_grade_missing') : t(st.text)
    }));
    karte.addEventListener('click', () => { selectRefTab(idx); window.scrollTo({ top: 0 }); });
    container.appendChild(karte);
  });

  const crewAvg = scoredRefs > 0 ? Math.round(totalCrewScore / scoredRefs) : null;
  document.getElementById('crewScoreVal').innerText = fmt(crewAvg);
  const st = scoreStatus(crewAvg);
  const ring = document.getElementById('crewRing');
  const umfang = 2 * Math.PI * 64;
  ring.setAttribute('stroke-dasharray', `${(crewAvg === null ? 0 : umfang * crewAvg / 100).toFixed(1)} ${umfang.toFixed(1)}`);
  ring.style.stroke = `var(${st.farbe})`;
  const status = document.getElementById('crewStatus');
  status.textContent = crewAvg === null ? t('crew_none') : t(st.text);
  status.style.color = `var(${crewAvg === null ? '--secondary' : st.schrift})`;
  document.getElementById('crewSub').textContent = t('crew_sub', { n: scoredRefs, von: refs.length });
  // Leerer Zustand: noch niemand besetzt
  const leer = document.getElementById('crewLeer');
  leer.hidden = mitName > 0;
  leer.textContent = t('crew_empty');

  const crewRadar = avgScores7.map((sum, i) => radarCounts[i] ? sum / radarCounts[i] : null);
  drawRadar('crewRadarChart', crewRadar);
}

// Netzdiagramm als SVG. scores: Werte 0–3 (Note / 33.33) oder null (N/A = hohler grauer Punkt).
// Farben über CSS-Klassen (hell/dunkel/Druck).
function drawRadar(svgId, scores) {
  const svg = document.getElementById(svgId);
  if (!svg) return;
  const labels = t('radar_labels');
  const n = labels.length;
  const cx = 150, cy = 116, R = 72;
  const punkt = (i, f) => {
    const a = (Math.PI * 2 / n) * i - Math.PI / 2;
    return [cx + Math.cos(a) * R * f, cy + Math.sin(a) * R * f];
  };
  const xy = (p) => p.map((v) => v.toFixed(1)).join(',');
  const istNA = (v) => v === null || v === undefined;
  const anteil = (v) => (istNA(v) ? 0.1 : Math.max(0.1, Math.min(1, v / 3)));
  let html = '';
  for (let stufe = 1; stufe <= 3; stufe++) {
    html += `<polygon class="netz-gitter" points="${labels.map((_, i) => xy(punkt(i, stufe / 3))).join(' ')}"/>`;
  }
  labels.forEach((_, i) => {
    const [x, y] = punkt(i, 1);
    html += `<line class="netz-achse" x1="${cx}" y1="${cy}" x2="${x.toFixed(1)}" y2="${y.toFixed(1)}"/>`;
  });
  html += `<polygon class="netz-flaeche" points="${labels.map((_, i) => xy(punkt(i, anteil(scores[i])))).join(' ')}"/>`;
  labels.forEach((label, i) => {
    const [x, y] = punkt(i, anteil(scores[i]));
    html += `<circle class="${istNA(scores[i]) ? 'netz-na' : 'netz-punkt'}" cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${istNA(scores[i]) ? 4 : 3.5}"/>`;
    const [lx, ly] = punkt(i, 1.22);
    const anker = Math.abs(lx - cx) < 8 ? 'middle' : (lx > cx ? 'start' : 'end');
    html += `<text class="netz-label${istNA(scores[i]) ? ' netz-label-na' : ''}" x="${lx.toFixed(1)}" y="${(ly + 4).toFixed(1)}" text-anchor="${anker}">${escapeHtml(label)}${istNA(scores[i]) ? ' (N/A)' : ''}</text>`;
  });
  svg.innerHTML = html;
  svg.setAttribute('aria-label', t('radar_title') + ': ' + labels.map((l, i) =>
    `${l} ${istNA(scores[i]) ? 'N/A' : Math.round(scores[i] * 33.33) + ' %'}`).join(', '));
}

async function resetAll() {
  // „Abbrechen“ ist vorgewählt: Enter löscht nichts
  if (await bestaetigen({ titel: t('reset_title'), text: t('reset_confirm'), ja: t('reset_button'), gefahr: true })) {
    localStorage.removeItem('referee_multi_supervision_data');
    location.reload();
  }
}
