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
  renderLanguageSelect();
  loadTheme();
  loadFullState();
  setupRefereeDropdown();
  applyTranslations();
  renderTabs();
  if (activeTabType === "summary") {
    renderSummaryView();
  } else if (activeTabType === "stats") {
    selectStatsTab();
  } else {
    loadRefereeForm(activeRefIndex);
  }
}

function setupRefereeDropdown() {
  const sel = document.getElementById('current_schiri_name');
  sel.innerHTML = '';
  const leer = document.createElement('option');
  leer.value = '';
  leer.textContent = KADER.length ? t('kader_choose') : t('kader_first');
  sel.appendChild(leer);
  const info = document.getElementById('kaderInfo');
  if (info) info.innerText = KADER.length ? t('kader_count', { n: KADER.length }) : t('kader_import');
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

// Darstellung umschalten: Auto -> Hell -> Dunkel -> Auto (Grundfunktionen in js/theme.js)
function toggleTheme() {
  const naechste = { auto: 'light', light: 'dark', dark: 'auto' }[getThemePref()];
  if (naechste === 'auto') localStorage.removeItem(THEME_KEY);
  else localStorage.setItem(THEME_KEY, naechste);
  applyTheme();
  updateThemeButton();
  redrawCharts();
}

function updateThemeButton() {
  const btn = document.getElementById('themeToggle');
  if (btn) btn.innerText = t('theme_label') + ': ' + t('theme_' + getThemePref());
}

// Netzdiagramme neu zeichnen (Farben kommen aus den CSS-Variablen)
function redrawCharts() {
  if (activeTabType === "summary") renderSummaryView();
  else if (activeTabType === "ref") calcScores(false);
}

function loadTheme() {
  updateThemeButton();
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

// TABS RENDERN (OHNE BADGE-DOPPELUNG)
function renderTabs() {
  const tabsContainer = document.getElementById('tabsContainer');
  tabsContainer.innerHTML = "";
  const refs = SYSTEM_CONFIGS[currentSystem];
  refs.forEach((ref, index) => {
    const roleText = escapeHtml(rolle(ref));
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'tab-btn' + (activeTabType === "ref" && index === activeRefIndex ? ' active' : '');
    btn.innerHTML = `<span>${roleText}</span>`;
    btn.onclick = () => selectRefTab(index);
    tabsContainer.appendChild(btn);
  });

  if (refs.length > 1) {
    const sumBtn = document.createElement('button');
    sumBtn.type = 'button';
    sumBtn.className = 'tab-btn tab-summary' + (activeTabType === "summary" ? ' active' : '');
    sumBtn.innerHTML = `<span>${escapeHtml(t('txt_tab_crew'))}</span>`;
    sumBtn.onclick = () => selectSummaryTab();
    tabsContainer.appendChild(sumBtn);
  }

  const statBtn = document.createElement('button');
  statBtn.type = 'button';
  statBtn.className = 'tab-btn tab-stats' + (activeTabType === "stats" ? ' active' : '');
  statBtn.innerHTML = `<span>${escapeHtml(t('txt_tab_stats'))}</span>`;
  statBtn.onclick = () => selectStatsTab();
  tabsContainer.appendChild(statBtn);

  document.getElementById('currentSystemInfo').innerText = t('system_info', { system: currentSystem, n: refs.length });
}

function selectRefTab(index) {
  if (activeTabType === "ref") saveCurrentRefData();
  activeTabType = "ref";
  activeRefIndex = index;
  document.getElementById('singleRefView').style.display = "block";
  document.getElementById('summaryView').style.display = "none";
  document.getElementById('seasonStatsView').style.display = "none";
  renderTabs();
  loadRefereeForm(activeRefIndex);
}

function selectSummaryTab() {
  if (activeTabType === "ref") saveCurrentRefData();
  activeTabType = "summary";
  document.getElementById('singleRefView').style.display = "none";
  document.getElementById('summaryView').style.display = "block";
  document.getElementById('seasonStatsView').style.display = "none";
  renderTabs();
  renderSummaryView();
}

function selectStatsTab() {
  if (activeTabType === "ref") saveCurrentRefData();
  activeTabType = "stats";
  document.getElementById('singleRefView').style.display = "none";
  document.getElementById('summaryView').style.display = "none";
  document.getElementById('seasonStatsView').style.display = "block";
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
}

async function addTimestamp(targetId) {
  const field = document.getElementById(targetId);
  const stamp = await eingeben({ titel: t('stamp_title'), text: t('stamp_prompt'), wert: "P1 00:00", ok: t('stamp_add') });
  if (stamp) {
    field.value += (field.value.trim() ? "\n" : "") + "[" + stamp + "] ";
    field.focus();
    saveCurrentRefData();
  }
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

function calcScores(shouldSave = true) {
  const dict = { status_missing: t('status_missing'), status_exc: t('status_exc'), status_good: t('status_good'),
    status_sat: t('status_sat'), status_ni: t('status_ni'), status_unsat: t('status_unsat') };
  const sc = computeRefScores(readFormData());
  const fmt = v => v === null ? "–" : v + "%";

  document.getElementById('scoreVal').innerText = fmt(sc.total);
  document.getElementById('subScorePart2').innerText = fmt(sc.part2);
  document.getElementById('subScorePart3').innerText = fmt(sc.part3);
  document.getElementById('subScorePart4').innerText = fmt(sc.part4);

  zeigeStufenText();   // Definition der gewählten Stufe bzw. Hinweis (oranger Rahmen)

  const statusText = document.getElementById('scoreStatusText');
  const ampelDot = document.getElementById('ampelDot');
  const setAmpel = (text, farbe) => {
    statusText.innerText = text;
    ampelDot.style.backgroundColor = `var(${farbe})`;
    ampelDot.style.boxShadow = `0 0 0 3px var(--accent-soft)`;
  };
  // Schwellen unverändert; Farben = Bewertungsfarben aus css/app.css
  const total = sc.total;
  if (total === null) setAmpel(dict.status_missing, '--r-none');
  else if (total > 80) setAmpel(dict.status_exc, '--r-pp');
  else if (total >= 75) setAmpel(dict.status_good, '--r-p');
  else if (total >= 60) setAmpel(dict.status_sat, '--r-solid');
  else if (total >= 45) setAmpel(dict.status_ni, '--r-m');
  else setAmpel(dict.status_unsat, '--r-mm');

  drawRadar('radarChart', sc.radar);
  if (shouldSave) saveCurrentRefData();
}

function renderSummaryView() {
  const refs = SYSTEM_CONFIGS[currentSystem];
  const container = document.getElementById('summaryCardsContainer');
  container.innerHTML = "";

  let totalCrewScore = 0, scoredRefs = 0;
  const avgScores7 = [0, 0, 0, 0, 0, 0, 0];
  const radarCounts = [0, 0, 0, 0, 0, 0, 0];
  const fmt = v => v === null ? "–" : v + "%";

  refs.forEach((ref, idx) => {
    const d = gameData.referees[`${currentSystem}_${ref.id}`] || getDefaultRefData();
    const roleText = rolle(ref);

    const sc = computeRefScores(d);
    sc.radar.forEach((v, i) => { if (v !== null) { avgScores7[i] += v; radarCounts[i]++; } });
    const p2 = sc.part2, p3 = sc.part3, p4 = sc.part4, refScore = sc.total;
    if (refScore !== null) { totalCrewScore += refScore; scoredRefs++; }

    const card = document.createElement('div');
    card.className = "summary-card";
    card.innerHTML = `
      <h3>${escapeHtml(roleText)}</h3>
      <div class="name">${d.name ? escapeHtml(d.name) : `<i>${escapeHtml(t('summary_no_name'))}</i>`}</div>
      <div class="score">${fmt(refScore)}</div>
      <div style="font-size: 11px; color: var(--text-muted);">${escapeHtml(t('summary_grade'))}: ${fmt(p2)} | Matrix: ${fmt(p3)} | Coach: ${fmt(p4)}</div>
    `;
    container.appendChild(card);
  });

  const crewAvg = scoredRefs > 0 ? Math.round(totalCrewScore / scoredRefs) : null;
  document.getElementById('crewScoreVal').innerText = fmt(crewAvg);

  const crewRadar = avgScores7.map((sum, i) => radarCounts[i] ? sum / radarCounts[i] : null);
  drawRadar('crewRadarChart', crewRadar);
}

function drawRadar(canvasId, scores) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const radius = Math.min(cx, cy) - 16;
  const labels = t('radar_labels');
  const total = labels.length;

  // Farben aus den CSS-Variablen (hell/dunkel)
  const css = getComputedStyle(document.documentElement);
  const farbe = (name) => css.getPropertyValue(name).trim();
  const gridStroke = farbe('--radar-grid');
  const axisStroke = farbe('--radar-axis');
  const polyColor = farbe('--accent');

  ctx.clearRect(0, 0, w, h);

  for (let level = 1; level <= 3; level++) {
    ctx.beginPath();
    ctx.strokeStyle = gridStroke;
    ctx.lineWidth = 1;
    const r = (radius / 3) * level;
    for (let i = 0; i < total; i++) {
      const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
      const x = cx + Math.cos(angle) * r;
      const y = cy + Math.sin(angle) * r;
      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.closePath();
    ctx.stroke();
  }

  for (let i = 0; i < total; i++) {
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
    ctx.beginPath();
    ctx.strokeStyle = axisStroke;
    ctx.moveTo(cx, cy);
    ctx.lineTo(cx + Math.cos(angle) * radius, cy + Math.sin(angle) * radius);
    ctx.stroke();
  }

  ctx.beginPath();
  ctx.fillStyle = polyColor;
  ctx.strokeStyle = polyColor;
  ctx.lineWidth = 2;

  for (let i = 0; i < total; i++) {
    const val = (scores[i] === null || scores[i] === undefined) ? 0.3 : scores[i];
    const r = (radius / 3) * Math.max(0.3, val);
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.closePath();
  ctx.globalAlpha = 0.25;
  ctx.fill();
  ctx.globalAlpha = 1;
  ctx.stroke();

  for (let i = 0; i < total; i++) {
    const isNA = scores[i] === null || scores[i] === undefined;
    const val = isNA ? 0.3 : scores[i];
    const r = (radius / 3) * Math.max(0.3, val);
    const angle = (Math.PI * 2 / total) * i - Math.PI / 2;
    const x = cx + Math.cos(angle) * r;
    const y = cy + Math.sin(angle) * r;
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, Math.PI * 2);
    if (isNA) {
      ctx.strokeStyle = farbe('--radar-na'); ctx.lineWidth = 1.5; ctx.stroke();
    } else {
      ctx.fillStyle = farbe('--radar-point');
      ctx.fill();
    }
  }
}

async function resetAll() {
  // „Abbrechen“ ist vorgewählt: Enter löscht nichts
  if (await bestaetigen({ titel: t('reset_title'), text: t('reset_confirm'), ja: t('reset_button'), gefahr: true })) {
    localStorage.removeItem('referee_multi_supervision_data');
    location.reload();
  }
}
