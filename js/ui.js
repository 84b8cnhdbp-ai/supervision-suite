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
  sel.innerHTML = '<option value="">-- Schiedsrichter wählen --</option>';
  if (!KADER.length) {
    sel.innerHTML = '<option value="">-- Zuerst Kader importieren (📋) --</option>';
  }
  const info = document.getElementById('kaderInfo');
  if (info) info.innerText = KADER.length
    ? (currentLang === 'en' ? `Roster: ${KADER.length} (update)` : `Kader: ${KADER.length} (aktualisieren)`)
    : (currentLang === 'en' ? 'Import roster' : 'Kader importieren');
  KADER.forEach(name => {
    const opt = document.createElement('option');
    opt.value = name;
    opt.textContent = name;
    sel.appendChild(opt);
  });
  const optOther = document.createElement('option');
  optOther.value = "_CUSTOM_";
  optOther.textContent = "✎ Anderer / Externer Schiedsrichter...";
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

function toggleTheme() {
  document.body.classList.toggle('dark-mode');
  const isDark = document.body.classList.contains('dark-mode');
  document.getElementById('themeToggle').innerText = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
  localStorage.setItem('referee_theme_preference', isDark ? 'dark' : 'light');
  calcScores(false);
  if (activeTabType === "summary") renderSummaryView();
}

function loadTheme() {
  const pref = localStorage.getItem('referee_theme_preference');
  if (pref === 'dark') {
    document.body.classList.add('dark-mode');
    document.getElementById('themeToggle').innerText = "☀️ Light Mode";
  }
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
  const dict = I18N[currentLang];

  refs.forEach((ref, index) => {
    const roleText = currentLang === "en" ? ref.role_en : ref.role_de;
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
    sumBtn.innerHTML = `<span>${dict.txt_tab_crew}</span>`;
    sumBtn.onclick = () => selectSummaryTab();
    tabsContainer.appendChild(sumBtn);
  }

  const statBtn = document.createElement('button');
  statBtn.type = 'button';
  statBtn.className = 'tab-btn tab-stats' + (activeTabType === "stats" ? ' active' : '');
  statBtn.innerHTML = `<span>${dict.txt_tab_stats}</span>`;
  statBtn.onclick = () => selectStatsTab();
  tabsContainer.appendChild(statBtn);

  document.getElementById('currentSystemInfo').innerText = `${currentSystem} (${refs.length} ${currentLang === 'en' ? 'Officials' : 'Schiedsrichter'})`;
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
  const isLines = refConfig.type === 'lines';
  const isEn = currentLang === 'en';

  if (isLines) {
    document.getElementById('lbl_perf_1').innerHTML = isEn
      ? `<strong>1. Skating & Physical Stamina</strong><br><small style="color:var(--text-muted);">Mobility, agility, backwards acceleration</small>`
      : `<strong>1. Eislaufen & Physis</strong><br><small style="color:var(--text-muted);">Agilität, Mobilität, Rückwärtslaufen, Fitness</small>`;
    document.getElementById('lbl_perf_2').innerHTML = isEn 
      ? `<strong>2. Positioning & Line Judgment</strong><br><small style="color:var(--text-muted);">Blue line tight offsides, icing assessment</small>`
      : `<strong>2. Positionsspiel & Linienkontrolle</strong><br><small style="color:var(--text-muted);">Blaue Linie bei knappen Offsides, Icing-Beurteilung</small>`;
    document.getElementById('lbl_perf_3').innerHTML = isEn
      ? `<strong>3. Whistle, Face-Offs & Signals</strong><br><small style="color:var(--text-muted);">Puck drop technique, face-off conduct, signals</small>`
      : `<strong>3. Pfiff, Bully-Präsenz & Signale</strong><br><small style="color:var(--text-muted);">Korrektes Anspiel, Bully-Conduct, Zeichen Icing/Abseits</small>`;
    document.getElementById('lbl_perf_4').innerHTML = isEn
      ? `<strong>4. Anticipation & Play Reading</strong><br><small style="color:var(--text-muted);">Reading dump-ins, deflections, off-puck fouls</small>`
      : `<strong>4. Antizipation & Spielaufmerksamkeit</strong><br><small style="color:var(--text-muted);">Spielzüge lesen, Off-Puck Play, Gefahren</small>`;
    document.getElementById('lbl_perf_5').innerHTML = isEn
      ? `<strong>5. Scrum Management & Intervention</strong><br><small style="color:var(--text-muted);">Fast separation of players, net-front safety</small>`
      : `<strong>5. Deeskalation & Scrum-Intervention</strong><br><small style="color:var(--text-muted);">Schnelles Trennen von Spielern, Torraumabsicherung</small>`;
    document.getElementById('lbl_perf_6').innerHTML = isEn
      ? `<strong>6. Teamwork & Communication</strong><br><small style="color:var(--text-muted);">Partner eye contact, communication with benches</small>`
      : `<strong>6. Teamwork & Kommunikation</strong><br><small style="color:var(--text-muted);">Gespann-Abstimmung, Dialog mit Captains/Coaches</small>`;
    document.getElementById('lbl_perf_7').innerHTML = isEn
      ? `<strong>7. Rule Application (Offside / Icing / Handpass)</strong><br><small style="color:var(--text-muted);">Precision on lines & high-stick puck touches</small>`
      : `<strong>7. Regelanwendung (Abseits / Icing / Handpass)</strong><br><small style="color:var(--text-muted);">Präzision bei Linienentscheiden & Puckkontakt</small>`;
  } else {
    document.getElementById('lbl_perf_1').innerHTML = isEn
      ? `<strong>1. Skating & Physical Stamina</strong><br><small style="color:var(--text-muted);">Speed, agility, backwards mobility over 60 min</small>`
      : `<strong>1. Eislaufen & Physis</strong><br><small style="color:var(--text-muted);">Agilität, Mobilität, Rückwärtslaufen, Fitness</small>`;
    document.getElementById('lbl_perf_2').innerHTML = isEn
      ? `<strong>2. Positioning & Sightlines</strong><br><small style="color:var(--text-muted);">Goal line ahead of play, net-front position, sightlines</small>`
      : `<strong>2. Positionsspiel & Sichtachsen</strong><br><small style="color:var(--text-muted);">Torlinie vor Spielzug, Net-Front-Position, Blickfeld</small>`;
    document.getElementById('lbl_perf_3').innerHTML = isEn
      ? `<strong>3. Whistle, Signals & Body Language</strong><br><small style="color:var(--text-muted);">Sharp whistle, authoritative signals, upright posture</small>`
      : `<strong>3. Pfiff, Zeichengebung & Präsenz</strong><br><small style="color:var(--text-muted);">Prägnanz, klare Signale, aufrechte Körpersprache</small>`;
    document.getElementById('lbl_perf_4').innerHTML = isEn
      ? `<strong>4. Anticipation & Game Awareness</strong><br><small style="color:var(--text-muted);">Reading plays, anticipating contact, awareness</small>`
      : `<strong>4. Antizipation & Spielaufmerksamkeit</strong><br><small style="color:var(--text-muted);">Spielzüge lesen, Off-Puck Play, Gefahren</small>`;
    document.getElementById('lbl_perf_5').innerHTML = isEn
      ? `<strong>5. De-escalation & Post-Whistle Control</strong><br><small style="color:var(--text-muted);">Protecting goalies, stopping scrums immediately</small>`
      : `<strong>5. Deeskalation & Post-Whistle Management</strong><br><small style="color:var(--text-muted);">Torraumabsicherung, Rudelbildungen unterbinden</small>`;
    document.getElementById('lbl_perf_6').innerHTML = isEn
      ? `<strong>6. Teamwork & Communication</strong><br><small style="color:var(--text-muted);">Crew coordination, respectful bench dialogue</small>`
      : `<strong>6. Teamwork & Kommunikation</strong><br><small style="color:var(--text-muted);">Gespann-Abstimmung, Dialog mit Captains/Coaches</small>`;
    document.getElementById('lbl_perf_7').innerHTML = isEn
      ? `<strong>7. Penalty Standard & Rulebook Adherence</strong><br><small style="color:var(--text-muted);">60-min consistency, adherence to official rulebook</small>`
      : `<strong>7. Strafmassstab & Regelanwendung</strong><br><small style="color:var(--text-muted);">Konstanz über 60 Min., Offizielles Regelbuch & Weisungen</small>`;
  }
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

  const partners = [];
  const refs = SYSTEM_CONFIGS[currentSystem];

  refs.forEach((ref, idx) => {
    if (idx !== activeRefIndex) {
      const partnerKey = `${currentSystem}_${ref.id}`;
      const pData = gameData.referees[partnerKey];
      if (pData && pData.name && pData.name.trim()) {
        const roleText = currentLang === 'en' ? ref.role_en : ref.role_de;
        partners.push(`${pData.name} (${roleText})`);
      }
    }
  });

  const partnerField = document.getElementById('current_schiri_partner');
  if (partners.length > 0) {
    partnerField.value = partners.join(", ");
  } else {
    partnerField.value = "Noch keine Partner in den anderen Reitern erfasst";
  }
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
  const roleName = currentLang === 'en' ? refConfig.role_en : refConfig.role_de;
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

  document.getElementById('current_review_round').value = data.review_round || "R1";

  const radios = document.querySelectorAll('input[name="overall_grade"]');
  radios.forEach(r => {
    r.checked = (r.value === (data.overall_grade || ""));
  });

  for (let i = 1; i <= 7; i++) {
    document.getElementById(`perf_${i}`).value = data[`perf_${i}`] || "80";
    document.getElementById(`note_${i}`).value = data[`note_${i}`] || "";
  }

  if (data.coach_trend) document.getElementById('coach_trend').value = data.coach_trend;
  if (data.coach_attitude) document.getElementById('coach_attitude').value = data.coach_attitude;
  if (data.coach_feedback) document.getElementById('coach_feedback').value = data.coach_feedback;

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
    role: currentLang === 'en' ? refConfig.role_en : refConfig.role_de,
    name: getEffectiveRefName(),
    review_round: document.getElementById('current_review_round').value,
    partner: document.getElementById('current_schiri_partner').value,
    overall_grade: selectedGrade ? selectedGrade.value : "",
    coach_trend: document.getElementById('coach_trend').value,
    coach_attitude: document.getElementById('coach_attitude').value,
    coach_feedback: document.getElementById('coach_feedback').value,
    top_strengths: document.getElementById('top_strengths').value,
    top_workon: document.getElementById('top_workon').value,
    general_report: document.getElementById('general_report').value,
    visum_ort_datum: document.getElementById('visum_ort_datum').value,
    visum_name: document.getElementById('visum_name').value
  };

  for (let i = 1; i <= 7; i++) {
    data[`perf_${i}`] = document.getElementById(`perf_${i}`).value;
    data[`note_${i}`] = document.getElementById(`note_${i}`).value;
  }

  gameData.referees[refKey] = data;
  saveToStorage();
}

function addTimestamp(targetId) {
  const field = document.getElementById(targetId);
  const promptMsg = currentLang === 'en' 
    ? "Enter Period & Game Clock (e.g. 'P2 08:34'):"
    : "Drittel & Spielminute eingeben (z. B. 'P2 08:34'):";
  const stamp = prompt(promptMsg, "P1 00:00");
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
    coach_trend: document.getElementById('coach_trend').value,
    coach_attitude: document.getElementById('coach_attitude').value,
    coach_feedback: document.getElementById('coach_feedback').value
  };
  for (let i = 1; i <= 7; i++) d[`perf_${i}`] = document.getElementById(`perf_${i}`).value;
  return d;
}

function calcScores(shouldSave = true) {
  const dict = I18N[currentLang];
  const sc = computeRefScores(readFormData());
  const fmt = v => v === null ? "–" : v + "%";

  document.getElementById('scoreVal').innerText = fmt(sc.total);
  document.getElementById('subScorePart2').innerText = fmt(sc.part2);
  document.getElementById('subScorePart3').innerText = fmt(sc.part3);
  document.getElementById('subScorePart4').innerText = fmt(sc.part4);

  const gradeTable = document.querySelector('input[name="overall_grade"]').closest('table');
  if (gradeTable) gradeTable.classList.toggle('grade-missing', sc.part2 === null);

  const statusText = document.getElementById('scoreStatusText');
  const ampelDot = document.getElementById('ampelDot');
  const setAmpel = (text, color, rgba) => {
    statusText.innerText = text;
    ampelDot.style.backgroundColor = color;
    ampelDot.style.boxShadow = `0 0 0 3px ${rgba}`;
  };
  const t = sc.total;
  if (t === null) setAmpel(dict.status_missing, "#94A3B8", "rgba(148, 163, 184, 0.3)");
  else if (t > 80) setAmpel(dict.status_exc, "#15803D", "rgba(21, 128, 61, 0.3)");
  else if (t >= 75) setAmpel(dict.status_good, "#4ADE80", "rgba(74, 222, 128, 0.3)");
  else if (t >= 60) setAmpel(dict.status_sat, "#EAB308", "rgba(234, 179, 8, 0.3)");
  else if (t >= 45) setAmpel(dict.status_ni, "var(--orange)", "rgba(234, 88, 12, 0.25)");
  else setAmpel(dict.status_unsat, "var(--red)", "rgba(220, 38, 38, 0.25)");

  drawRadar('radarChart', sc.radar, '#2563EB');
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
    const roleText = currentLang === 'en' ? ref.role_en : ref.role_de;
    
    const sc = computeRefScores(d);
    sc.radar.forEach((v, i) => { if (v !== null) { avgScores7[i] += v; radarCounts[i]++; } });
    const p2 = sc.part2, p3 = sc.part3, p4 = sc.part4, refScore = sc.total;
    if (refScore !== null) { totalCrewScore += refScore; scoredRefs++; }

    const card = document.createElement('div');
    card.className = "summary-card";
    card.innerHTML = `
      <h3>${escapeHtml(roleText)}</h3>
      <div class="name">${d.name ? escapeHtml(d.name) : (currentLang === 'en' ? "<i>Unnamed Official</i>" : "<i>Kein Name</i>")}</div>
      <div class="score">${fmt(refScore)}</div>
      <div style="font-size: 11px; color: var(--text-muted);">${currentLang === 'en' ? 'Grade' : 'Note'}: ${fmt(p2)} | Matrix: ${fmt(p3)} | Coach: ${fmt(p4)}</div>
    `;
    container.appendChild(card);
  });

  const crewAvg = scoredRefs > 0 ? Math.round(totalCrewScore / scoredRefs) : null;
  document.getElementById('crewScoreVal').innerText = fmt(crewAvg);

  const crewRadar = avgScores7.map((sum, i) => radarCounts[i] ? sum / radarCounts[i] : null);
  drawRadar('crewRadarChart', crewRadar, '#4F46E5');
}

function drawRadar(canvasId, scores, polyColor = '#2563EB') {
  const canvas = document.getElementById(canvasId);
  if (!canvas || !canvas.getContext) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;
  const cx = w / 2;
  const cy = h / 2;
  const radius = Math.min(cx, cy) - 16;
  const labels = I18N[currentLang].radar_labels;
  const total = labels.length;

  const isDark = document.body.classList.contains('dark-mode');
  const gridStroke = isDark ? "#3A506B" : "#CBD5E1";
  const axisStroke = isDark ? "#2A3B53" : "#E2E8F0";

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
  ctx.fillStyle = polyColor === '#4F46E5' ? "rgba(79, 70, 229, 0.28)" : "rgba(37, 99, 235, 0.25)";
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
  ctx.fill();
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
      ctx.strokeStyle = "#94A3B8"; ctx.lineWidth = 1.5; ctx.stroke();
    } else {
      ctx.fillStyle = isDark ? "#FFFFFF" : "#0B2545";
      ctx.fill();
    }
  }
}

function resetAll() {
  const confirmMsg = currentLang === 'en'
    ? "Reset the entire game evaluation and all officiating tabs?"
    : "Möchten Sie das gesamte Spiel und alle Schiedsrichter-Reiter zurücksetzen?";
  if (confirm(confirmMsg)) {
    localStorage.removeItem('referee_multi_supervision_data');
    location.reload();
  }
}
