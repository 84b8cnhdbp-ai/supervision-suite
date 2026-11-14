// Texte und Sprachwahl
// Sichtbar: DE, EN. Vorbereitet, aber versteckt: FR, IT (nur zum Testen über ?lang=fr bzw. ?lang=it).
// Fehlt ein Text in einer Sprache, wird der deutsche verwendet (t()).
// Gespeicherte Werte (Coaching-Texte, R1/R2, Liga, Rollen …) bleiben in jeder Sprache deutsch.

const I18N = {
  de: {
    app_title: "Referee Supervision Hub",
    app_subtitle: "Digitales Coaching-, Evaluations- & Analyse-Tool für Schiedsrichter-Supervisoren",
    lbl_system: "Schiedsrichter-System",
    lbl_league: "Liga / Stufe",
    lbl_game: "Begegnung (Heim vs. Gast)",
    lbl_game_id: "Spiel-Nr. / ID",
    lbl_datetime: "Datum & Zeit",
    lbl_arena: "Spielort / Arena",
    lbl_supervisor: "Supervisor / Coach",
    txt_score: "Score",
    txt_weighted_for: "Gewichteter Score",
    sub_part2: "Teil 2: Gesamt (30%)",
    sub_part3: "Teil 3: Matrix (50%)",
    sub_part4: "Teil 4: Coach (20%)",
    sec1_title: "Angaben zur Person & Funktion",
    lbl_ref_name: "Schiedsrichter ({kurz} Kader)",
    ph_game: "z. B. {verein} vs. Gastteam",
    ph_arena: "z. B. {halle}",
    stats_title: "{kurz} Schiedsrichter-Supervision — Gesamtstatistik",
    lbl_partner: "Gespann-Partner (Automatisch)",
    sec2_title: "Gesamteinschätzung (Standard)",
    th_choice: "Wahl",
    th_grade: "Stufe",
    th_definition: "Definition & Kriterien",
    grade_vg: "Sehr Gut",
    grade_good: "Gut / Zufriedenstellend",
    grade_ni: "Verbesserungsbedürftig",
    grade_unsat: "Ungenügend",
    desc_vg: "Mutige, korrekte Schlüsselentscheide unter hohem Druck (z. B. doppelte Unterzahl, Torannullierung). Kein Phantom-Pfiff, perfekte Ruhe, erstklassige Spielkontrolle.",
    desc_good: "Ordentlich geleitetes Spiel, Frustrationsniveau tief gehalten, gutes Gespür für Spielfluss. Hält sich bei Bedarf im Hintergrund und ist vor dem Spielzug an der Torlinie.",
    desc_ni: "Wenig Zugriff aufs Spiel, Über- oder Unterinterpretation von Regeln, macht Routine-Situationen unnötig hektisch oder unkonsequent.",
    desc_unsat: "Kontrollverlust, gravierende Regelfehlentscheide, erhebliche Sicherheits- oder Eislaufdefizite.",
    sec3_title: "Leistungs-Checkliste & Rollen-Kriterien",
    th_matrix_area: "Bereich & Leitfragen",
    th_matrix_rating: "Bewertung",
    th_matrix_notes: "Szenen, Timestamps & Notizen",
    sec4_title: "Coaching, Trend & Mindset",
    lbl_trend: "Leistungsentwicklung / Trend (6.7%)",
    lbl_attitude: "Einstellung On-/Off-Ice (6.7%)",
    lbl_feedback_mind: "Feedback-Bereitschaft (6.6%)",
    sec5_title: "Abschluss-Rapport & Action Plan",
    lbl_strengths: "Top 2–3 Stärken (Keep Doing)",
    lbl_workon: "Top 2–3 Entwicklungsschwerpunkte (Work On)",
    lbl_report: "Ausführlicher Rapport / Besondere Vorkommnisse",
    lbl_location_date: "Ort, Datum (Übernommen aus Metadaten)",
    lbl_signature: "Visum Supervisor",
    sec_summary_title: "Gespann-Übersicht & Team-Performance",
    txt_team: "Team",
    txt_crew_avg: "Gespann-Durchschnittsnote",
    txt_crew_sub: "Mittelwert aus allen bewerteten Schiedsrichtern dieses Spiels",
    sec_crew_obs: "Gemeinsame Gespann-Beobachtungen",
    lbl_crew_notes: "Zusammenarbeit, Teamwork & Spielcharakter",
    btn_reset: "Gesamtes Spiel zurücksetzen",
    txt_tab_crew: "Gespann-Übersicht",
    txt_tab_stats: "Saison-Statistik",
    radar_labels: ["Eislaufen", "Position", "Präsenz", "Antizipation", "Deeskalation", "Teamwork", "Regeln"],
    perf_options: [
      { val: "100", text: "++ (Überdurchschnittlich)" },
      { val: "80", text: "+ (Erfüllt / Gut)" },
      { val: "50", text: "- (Mängel erkennbar)" },
      { val: "20", text: "-- (Ungenügend)" },
      { val: "NA", text: "N/A (Nicht bewertbar)" }
    ],
    coach_trend_opts: [
      { val: "Konstant stabil", text: "Konstant stabil (Gut / 80%)" },
      { val: "Fortschritt erkennbar", text: "Fortschritt erkennbar (Top / 100%)" },
      { val: "Erstbeobachtung", text: "Erstbeobachtung (Neutral / 80%)" },
      { val: "Rückschritt / Instabil", text: "Rückschritt / Instabil (40%)" }
    ],
    coach_att_opts: [
      { val: "Gut / Angemessen", text: "Gut / Angemessen (80%)" },
      { val: "Vorbildlich / Professionell", text: "Vorbildlich / Professionell (100%)" },
      { val: "Ausbaufähig", text: "Ausbaufähig (45%)" }
    ],
    coach_feed_opts: [
      { val: "Konstruktiv", text: "Konstruktiv (80%)" },
      { val: "Sehr offen & reflektiert", text: "Sehr offen & reflektiert (100%)" },
      { val: "Defensiv / Rechtfertigend", text: "Defensiv / Rechtfertigend (40%)" }
    ],
    status_exc: "Leistung: Überdurchschnittlich / Sehr Gut",
    status_good: "Leistung: Gut / Erfüllt",
    status_sat: "Leistung: Zufriedenstellend / Solide",
    status_ni: "Leistung: Verbesserungsbedürftig",
    status_unsat: "Leistung: Ungenügend",
    status_missing: "Gesamteinschätzung (Teil 2) fehlt noch",
    lang_label: "Sprache",
    theme_label: "Darstellung",
    theme_auto: "Auto",
    theme_light: "Hell",
    theme_dark: "Dunkel",
    kader_count: "Kader: {n} (aktualisieren)",
    kader_import: "Kader importieren",
    kader_choose: "-- Schiedsrichter wählen --",
    kader_first: "-- Zuerst Kader importieren --",
    kader_other: "✎ Anderer / Externer Schiedsrichter...",
    kader_imported: "Kader importiert: {n} Schiedsrichter",
    kader_error: "Kaderdatei konnte nicht gelesen werden. Erwartet: JSON ({\"schiedsrichter\": [...]} oder [...]) oder ein Name pro Zeile.",
    system_info: "{system} ({n} Schiedsrichter)",
    partner_none: "Noch keine Partner in den anderen Reitern erfasst",
    stamp_prompt: "Drittel & Spielminute eingeben (z. B. 'P2 08:34'):",
    reset_confirm: "Möchten Sie das gesamte Spiel und alle Schiedsrichter-Reiter zurücksetzen?",
    saved_status: "Auto-Gespeichert ({zeit})",
    export_missing: "Review kann nicht gespeichert werden. Es fehlt:",
    missing_name: "Name Schiedsrichter",
    missing_date: "Spieldatum",
    missing_grade: "Gesamteinschätzung (Teil 2)",
    csv_game_id: "Spiel-ID",
    csv_league: "Liga",
    csv_matchup: "Begegnung",
    csv_date: "Datum",
    csv_arena: "Ort",
    csv_supervisor: "Supervisor",
    csv_system: "System",
    csv_crew_notes: "Gespann-Notizen",
    summary_no_name: "Kein Name",
    summary_grade: "Note",
    dlg_ok: "OK",
    dlg_cancel: "Abbrechen",
    reset_title: "Spiel zurücksetzen?",
    reset_button: "Zurücksetzen",
    export_missing_title: "Review kann nicht gesichert werden",
    export_missing_hint: "Es fehlt noch – antippen, um zum Feld zu springen:",
    stamp_title: "Szene mit Spielzeit",
    stamp_add: "Hinzufügen",
    kader_error_title: "Kaderdatei nicht lesbar",
    stats_skipped: "{n} Datei(en) konnten nicht gelesen werden und wurden übersprungen.",
    badge_ready: "● Offline bereit",
    badge_update: "⟳ Neue Version – tippen zum Laden",
    badge_blocked: "⚠ Update blockiert – Version nicht erhöht",
    badge_blocked_detail: "Auf dem Server gibt es geänderte Dateien mit gleicher Versionsnummer (?v=). Die bisherige Version bleibt aktiv. Betroffen: {dateien}",
    toast_blocked: "Update blockiert: Die Versionsnummer wurde nicht erhöht. Die bisherige Version bleibt aktiv.",
    csv_headers: ["Rolle", "Name", "Review", "Gesamtscore", "Gesamteinschätzung", "Eislaufen", "Position", "Präsenz", "Antizipation", "Deeskalation", "Teamwork", "Regeln", "Trend", "Einstellung", "Feedback", "Top Stärken", "Entwicklung", "Rapport"],
    crit_head: [{"t": "1. Eislaufen & Physis", "s": "Agilität, Mobilität, Rückwärtslaufen, Fitness"}, {"t": "2. Positionsspiel & Sichtachsen", "s": "Torlinie vor Spielzug, Net-Front-Position, Blickfeld"}, {"t": "3. Pfiff, Zeichengebung & Präsenz", "s": "Prägnanz, klare Signale, aufrechte Körpersprache"}, {"t": "4. Antizipation & Spielaufmerksamkeit", "s": "Spielzüge lesen, Off-Puck Play, Gefahren"}, {"t": "5. Deeskalation & Post-Whistle Management", "s": "Torraumabsicherung, Rudelbildungen unterbinden"}, {"t": "6. Teamwork & Kommunikation", "s": "Gespann-Abstimmung, Dialog mit Captains/Coaches"}, {"t": "7. Strafmassstab & Regelanwendung", "s": "Konstanz über 60 Min., Offizielles Regelbuch & Weisungen"}],
    crit_lines: [{"t": "1. Eislaufen & Physis", "s": "Agilität, Mobilität, Rückwärtslaufen, Fitness"}, {"t": "2. Positionsspiel & Linienkontrolle", "s": "Blaue Linie bei knappen Offsides, Icing-Beurteilung"}, {"t": "3. Pfiff, Bully-Präsenz & Signale", "s": "Korrektes Anspiel, Bully-Conduct, Zeichen Icing/Abseits"}, {"t": "4. Antizipation & Spielaufmerksamkeit", "s": "Spielzüge lesen, Off-Puck Play, Gefahren"}, {"t": "5. Deeskalation & Scrum-Intervention", "s": "Schnelles Trennen von Spielern, Torraumabsicherung"}, {"t": "6. Teamwork & Kommunikation", "s": "Gespann-Abstimmung, Dialog mit Captains/Coaches"}, {"t": "7. Regelanwendung (Abseits / Icing / Handpass)", "s": "Präzision bei Linienentscheiden & Puckkontakt"}],
  },
  en: {
    app_title: "Referee Supervision Hub",
    app_subtitle: "Digital Coaching, Evaluation & Analytics Suite for Officiating Supervisors",
    lbl_system: "Officiating System",
    lbl_league: "League / Level",
    lbl_game: "Game Matchup (Home vs. Away)",
    lbl_game_id: "Game ID / No.",
    lbl_datetime: "Date & Time",
    lbl_arena: "Location / Arena",
    lbl_supervisor: "Supervisor / Coach",
    txt_score: "Score",
    txt_weighted_for: "Weighted Score for",
    sub_part2: "Part 2: Overall (30%)",
    sub_part3: "Part 3: Matrix (50%)",
    sub_part4: "Part 4: Coach (20%)",
    sec1_title: "Official's Information & Assignment",
    lbl_ref_name: "Referee ({kurz} Roster)",
    ph_game: "e.g. {verein} vs. Visitors",
    ph_arena: "e.g. {halle}",
    stats_title: "{kurz} Referee Supervision — Overall Statistics",
    lbl_partner: "Crew Partner(s) (Auto)",
    sec2_title: "Overall Performance Rating (Standard)",
    th_choice: "Select",
    th_grade: "Grade",
    th_definition: "Definition & Evaluation Criteria",
    grade_vg: "Excellent",
    grade_good: "Good / Satisfactory",
    grade_ni: "Needs Improvement",
    grade_unsat: "Unsatisfactory",
    desc_vg: "Makes courageous, correct key decisions under high pressure. No phantom calls, complete composure, excellent game control.",
    desc_good: "Solidly officiated game, kept frustration low, good feel for game flow. Stays out of the way when appropriate and arrives at goal line ahead of play.",
    desc_ni: "Lack of game feel/control, inconsistent standard, over- or under-interprets rulebook, makes routine situations difficult.",
    desc_unsat: "Loss of control, critical rule misapplications, substantial safety or skating mobility deficits.",
    sec3_title: "Performance Matrix & Role Competencies",
    th_matrix_area: "Area & Key Competency",
    th_matrix_rating: "Rating",
    th_matrix_notes: "Plays, Timestamps & Notes",
    sec4_title: "Coaching, Trend & Mindset",
    lbl_trend: "Performance Trend (6.7%)",
    lbl_attitude: "On-/Off-Ice Attitude (6.7%)",
    lbl_feedback_mind: "Feedback Receptiveness (6.6%)",
    sec5_title: "Debrief Rapport & Action Plan",
    lbl_strengths: "Top 2–3 Strengths (Keep Doing)",
    lbl_workon: "Top 2–3 Action Items (Work On)",
    lbl_report: "Detailed Game Rapport / Key Incidents",
    lbl_location_date: "Location, Date (Inherited)",
    lbl_signature: "Supervisor Signature",
    sec_summary_title: "Crew Summary & Collective Performance",
    txt_team: "Crew",
    txt_crew_avg: "Crew Average Rating",
    txt_crew_sub: "Mean score across all evaluated officials in this game",
    sec_crew_obs: "Collective Crew Observations",
    lbl_crew_notes: "Teamwork, Communication & Game Management",
    btn_reset: "Reset Entire Game",
    txt_tab_crew: "Crew Overview",
    txt_tab_stats: "Season Stats",
    radar_labels: ["Skating", "Position", "Presence", "Anticipation", "De-escalation", "Teamwork", "Rules"],
    perf_options: [
      { val: "100", text: "++ (Above Average)" },
      { val: "80", text: "+ (Proficient / Good)" },
      { val: "50", text: "- (Deficits Identified)" },
      { val: "20", text: "-- (Unsatisfactory)" },
      { val: "NA", text: "N/A (Not Evaluated)" }
    ],
    coach_trend_opts: [
      { val: "Konstant stabil", text: "Consistent / Stable (Good / 80%)" },
      { val: "Fortschritt erkennbar", text: "Noticeable Progress (Top / 100%)" },
      { val: "Erstbeobachtung", text: "First Observation (Neutral / 80%)" },
      { val: "Rückschritt / Instabil", text: "Regression / Inconsistent (40%)" }
    ],
    coach_att_opts: [
      { val: "Gut / Angemessen", text: "Good / Professional (80%)" },
      { val: "Vorbildlich / Professionell", text: "Exemplary / Role Model (100%)" },
      { val: "Ausbaufähig", text: "Needs Development (45%)" }
    ],
    coach_feed_opts: [
      { val: "Konstruktiv", text: "Constructive (80%)" },
      { val: "Sehr offen & reflektiert", text: "Highly Receptive & Reflective (100%)" },
      { val: "Defensiv / Rechtfertigend", text: "Defensive / Resistant (40%)" }
    ],
    status_exc: "Performance: Above Average / Excellent",
    status_good: "Performance: Good / Proficient",
    status_sat: "Performance: Satisfactory / Solid",
    status_ni: "Performance: Needs Improvement",
    status_unsat: "Performance: Unsatisfactory",
    status_missing: "Overall assessment (Part 2) missing",
    lang_label: "Language",
    theme_label: "Appearance",
    theme_auto: "Auto",
    theme_light: "Light",
    theme_dark: "Dark",
    kader_count: "Roster: {n} (update)",
    kader_import: "Import roster",
    kader_choose: "-- Select official --",
    kader_first: "-- Import roster first --",
    kader_other: "✎ Other / external official...",
    kader_imported: "Roster imported: {n} officials",
    kader_error: "Could not read roster file. Expected JSON ({\"schiedsrichter\": [...]} or [...]) or one name per line.",
    system_info: "{system} ({n} Officials)",
    partner_none: "No partners entered in the other tabs yet",
    stamp_prompt: "Enter Period & Game Clock (e.g. 'P2 08:34'):",
    reset_confirm: "Reset the entire game evaluation and all officiating tabs?",
    saved_status: "Auto-Saved ({zeit})",
    export_missing: "Cannot save review. Missing:",
    missing_name: "Official's name",
    missing_date: "Game date",
    missing_grade: "Overall assessment (Part 2)",
    csv_game_id: "Game-ID",
    csv_league: "League",
    csv_matchup: "Matchup",
    csv_date: "Date",
    csv_arena: "Arena",
    csv_supervisor: "Supervisor",
    csv_system: "System",
    csv_crew_notes: "Crew Notes",
    summary_no_name: "Unnamed Official",
    summary_grade: "Grade",
    dlg_ok: "OK",
    dlg_cancel: "Cancel",
    reset_title: "Reset game?",
    reset_button: "Reset",
    export_missing_title: "Review cannot be saved",
    export_missing_hint: "Still missing – tap to go to the field:",
    stamp_title: "Scene with game clock",
    stamp_add: "Add",
    kader_error_title: "Roster file not readable",
    stats_skipped: "{n} file(s) could not be read and were skipped.",
    badge_ready: "● Offline ready",
    badge_update: "⟳ New version – tap to reload",
    badge_blocked: "⚠ Update blocked – version not increased",
    badge_blocked_detail: "The server has changed files with the same version number (?v=). The current version stays active. Affected: {dateien}",
    toast_blocked: "Update blocked: the version number was not increased. The current version stays active.",
    csv_headers: ["Role", "Name", "Review", "Total Score", "Overall Grade", "Skating", "Positioning", "Presence", "Anticipation", "De-escalation", "Teamwork", "Rules", "Trend", "Attitude", "Feedback", "Top Strengths", "Work On", "Rapport"],
    crit_head: [{"t": "1. Skating & Physical Stamina", "s": "Speed, agility, backwards mobility over 60 min"}, {"t": "2. Positioning & Sightlines", "s": "Goal line ahead of play, net-front position, sightlines"}, {"t": "3. Whistle, Signals & Body Language", "s": "Sharp whistle, authoritative signals, upright posture"}, {"t": "4. Anticipation & Game Awareness", "s": "Reading plays, anticipating contact, awareness"}, {"t": "5. De-escalation & Post-Whistle Control", "s": "Protecting goalies, stopping scrums immediately"}, {"t": "6. Teamwork & Communication", "s": "Crew coordination, respectful bench dialogue"}, {"t": "7. Penalty Standard & Rulebook Adherence", "s": "60-min consistency, adherence to official rulebook"}],
    crit_lines: [{"t": "1. Skating & Physical Stamina", "s": "Mobility, agility, backwards acceleration"}, {"t": "2. Positioning & Line Judgment", "s": "Blue line tight offsides, icing assessment"}, {"t": "3. Whistle, Face-Offs & Signals", "s": "Puck drop technique, face-off conduct, signals"}, {"t": "4. Anticipation & Play Reading", "s": "Reading dump-ins, deflections, off-puck fouls"}, {"t": "5. Scrum Management & Intervention", "s": "Fast separation of players, net-front safety"}, {"t": "6. Teamwork & Communication", "s": "Partner eye contact, communication with benches"}, {"t": "7. Rule Application (Offside / Icing / Handpass)", "s": "Precision on lines & high-stick puck touches"}],
  },
  // Vorbereitet, Übersetzung folgt in Etappe 2.9 (bis dahin deutsche Texte)
  fr: {},
  it: {}
};

const SPRACHEN = [
  { code: 'de', name: 'Deutsch', sichtbar: true },
  { code: 'en', name: 'English', sichtbar: true },
  { code: 'fr', name: 'Français', sichtbar: false },
  { code: 'it', name: 'Italiano', sichtbar: false }
];
const LANG_KEY = 'referee_lang_preference';
let currentLang = "de";

// Text in der aktuellen Sprache, sonst deutsch. Platzhalter {name} werden aus `werte` ersetzt;
// {verein}, {kurz} und {halle} kommen aus der Vereins-Einstellung (js/club.js).
function t(key, werte) {
  let text = I18N[currentLang] && I18N[currentLang][key] !== undefined ? I18N[currentLang][key] : I18N.de[key];
  if (text === undefined) return key;
  if (typeof text === 'string' && text.includes('{')) {
    const alle = { verein: CLUB.name, kurz: CLUB.kurz, halle: CLUB.halle, ...(werte || {}) };
    text = text.replace(/\{(\w+)\}/g, (m, k) => (alle[k] !== undefined ? alle[k] : m));
  }
  return text;
}

// Rollenbezeichnung zur Anzeige (gespeichert wird immer role_de)
function rolle(ref) {
  return ref['role_' + currentLang] || ref.role_de;
}

// Sprache: ?lang=xx gilt nur für diesen Aufruf (auch versteckte Sprachen), sonst gespeicherte Wahl, sonst Deutsch.
function loadLanguagePreference() {
  const ausAdresse = new URLSearchParams(location.search).get('lang');
  if (ausAdresse && I18N[ausAdresse]) {
    currentLang = ausAdresse;
  } else {
    const gespeichert = localStorage.getItem(LANG_KEY);
    currentLang = SPRACHEN.some((s) => s.code === gespeichert && s.sichtbar) ? gespeichert : 'de';
  }
  document.documentElement.lang = currentLang;
}

function renderLanguageSelect() {
  const sel = document.getElementById('langSelect');
  if (!sel) return;
  sel.innerHTML = '';
  SPRACHEN.filter((s) => s.sichtbar || s.code === currentLang).forEach((s) => {
    const o = document.createElement('option');
    o.value = s.code;
    o.textContent = s.name;
    o.selected = s.code === currentLang;
    sel.appendChild(o);
  });
  sel.setAttribute('aria-label', t('lang_label'));
}

function setLanguage(code) {
  if (!I18N[code]) return;
  if (activeTabType === 'ref') saveCurrentRefData();
  currentLang = code;
  localStorage.setItem(LANG_KEY, code);
  document.documentElement.lang = code;
  renderLanguageSelect();
  setupRefereeDropdown();
  applyTranslations();
  updateThemeButton();
  renderTabs();
  if (activeTabType === 'ref') loadRefereeForm(activeRefIndex);
  else if (activeTabType === 'summary') renderSummaryView();
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.innerText = t(el.getAttribute('data-i18n'));
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.getAttribute('data-i18n-placeholder'));
  });
  applyClub();
  if (typeof zeigeBadge === 'function') zeigeBadge();   // Badge-Text je nach Status (js/app.js)
  // Listen (Notenstufen, Coaching) mit Rückfall auf Deutsch
  const dict = {
    perf_options: t('perf_options'), coach_trend_opts: t('coach_trend_opts'),
    coach_att_opts: t('coach_att_opts'), coach_feed_opts: t('coach_feed_opts')
  };

  for (let i = 1; i <= 7; i++) {
    const select = document.getElementById(`perf_${i}`);
    const curVal = select.value || "80";
    select.innerHTML = "";
    dict.perf_options.forEach(opt => {
      const o = document.createElement('option');
      o.value = opt.val;
      o.innerText = opt.text;
      if (opt.val === curVal) o.selected = true;
      select.appendChild(o);
    });
  }

  const tSel = document.getElementById('coach_trend');
  const curT = tSel.value || "Konstant stabil";
  tSel.innerHTML = "";
  dict.coach_trend_opts.forEach(opt => {
    const o = document.createElement('option');
    o.value = opt.val;
    o.innerText = opt.text;
    if (curT.includes(opt.val)) o.selected = true;
    tSel.appendChild(o);
  });

  const aSel = document.getElementById('coach_attitude');
  const curA = aSel.value || "Gut / Angemessen";
  aSel.innerHTML = "";
  dict.coach_att_opts.forEach(opt => {
    const o = document.createElement('option');
    o.value = opt.val;
    o.innerText = opt.text;
    if (curA.includes(opt.val)) o.selected = true;
    aSel.appendChild(o);
  });

  const fSel = document.getElementById('coach_feedback');
  const curF = fSel.value || "Konstruktiv";
  fSel.innerHTML = "";
  dict.coach_feed_opts.forEach(opt => {
    const o = document.createElement('option');
    o.value = opt.val;
    o.innerText = opt.text;
    if (curF.includes(opt.val)) o.selected = true;
    fSel.appendChild(o);
  });
}
