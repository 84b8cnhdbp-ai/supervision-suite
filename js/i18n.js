// Texte DE/EN und Sprachwahl
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

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
    lbl_ref_name: "Schiedsrichter (EVZ Kader)",
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
    txt_tab_crew: "★ Gespann-Übersicht",
    txt_tab_stats: "📊 EVZ Saison-Statistik",
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
    status_missing: "Gesamteinschätzung (Teil 2) fehlt noch"
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
    lbl_ref_name: "Referee (EVZ Roster)",
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
    txt_tab_crew: "★ Crew Overview",
    txt_tab_stats: "📊 EVZ Season Stats",
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
    status_missing: "Overall assessment (Part 2) missing"
  }
};

let currentLang = "de";

function toggleLang() {
  currentLang = currentLang === "de" ? "en" : "de";
  document.getElementById('langToggle').innerText = currentLang === "de" ? "🌐 EN" : "🌐 DE";
  localStorage.setItem('referee_lang_preference', currentLang);
  applyTranslations();
  renderTabs();
  if (activeTabType === "ref") loadRefereeForm(activeRefIndex);
}

function loadLanguagePreference() {
  const pref = localStorage.getItem('referee_lang_preference');
  if (pref === "en" || pref === "de") currentLang = pref;
  document.getElementById('langToggle').innerText = currentLang === "de" ? "🌐 EN" : "🌐 DE";
}

function applyTranslations() {
  const dict = I18N[currentLang];
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) el.innerText = dict[key];
  });

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
