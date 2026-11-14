// Export JSON (Einzel-Review) und CSV (Spiel)
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

// EXPORT: Einzelnes Review sichern
function safeFilePart(str) {
  return String(str).normalize('NFC').replace(/[\\/:*?"<>|]/g, '').replace(/\s+/g, ' ').trim();
}

function downloadBlob(blob, filename) {
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  setTimeout(() => URL.revokeObjectURL(link.href), 1000);
}

function exportSingleReviewJSON() {
  saveCurrentRefData();
  const isEn = currentLang === 'en';
  const refConfig = SYSTEM_CONFIGS[currentSystem][activeRefIndex];
  const refKey = `${currentSystem}_${refConfig.id}`;
  const refData = gameData.referees[refKey] || {};
  const sc = computeRefScores(refData);

  const missing = [];
  if (!refData.name) missing.push(isEn ? "Official's name" : "Name Schiedsrichter");
  if (!gameData.global.spiel_datum) missing.push(isEn ? "Game date" : "Spieldatum");
  if (sc.part2 === null) missing.push(isEn ? "Overall assessment (Part 2)" : "Gesamteinschätzung (Teil 2)");
  if (missing.length) {
    alert((isEn ? "Cannot save review. Missing:\n• " : "Review kann nicht gespeichert werden. Es fehlt:\n• ") + missing.join("\n• "));
    return;
  }

  const name = refData.name;
  const round = refData.review_round || "R1";
  const dateStr = gameData.global.spiel_datum.split("T")[0];

  const payload = {
    version: "1.1",
    club: "EV Zug",
    schiedsrichter: name,
    reviewRunde: round,
    datum: dateStr,
    spiel_id: gameData.global.spiel_id || "",
    spiel_liga: gameData.global.spiel_liga || "",
    spiel_paarung: gameData.global.spiel_paarung || "",
    spiel_ort: gameData.global.spiel_ort || "",
    system: currentSystem,
    scoreGesamt: sc.total,
    subScores: {
      teil2_overall: sc.part2,
      teil3_matrix: sc.part3,
      teil4_coach: sc.part4
    },
    evaluation: refData,
    supervisor: gameData.global.supervisor_name || "",
    exportiertAm: new Date().toISOString()
  };

  const filename = `${dateStr}_${round}_${safeFilePart(name)}.json`;
  downloadBlob(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }), filename);
}

function exportCSV() {
  if (activeTabType === "ref") saveCurrentRefData();
  const isEn = currentLang === 'en';
  const rows = [
    [isEn ? "Game-ID" : "Spiel-ID", gameData.global.spiel_id || ""],
    [isEn ? "League" : "Liga", gameData.global.spiel_liga || ""],
    [isEn ? "Matchup" : "Begegnung", gameData.global.spiel_paarung || ""],
    [isEn ? "Date" : "Datum", gameData.global.spiel_datum || ""],
    [isEn ? "Arena" : "Ort", gameData.global.spiel_ort || ""],
    [isEn ? "Supervisor" : "Supervisor", gameData.global.supervisor_name || ""],
    [isEn ? "System" : "System", currentSystem],
    [isEn ? "Crew Notes" : "Gespann-Notizen", (gameData.global.crew_notes || "").replace(/\n/g, ' ')],
    [],
    isEn
      ? ["Role", "Name", "Review", "Total Score", "Overall Grade", "Skating", "Positioning", "Presence", "Anticipation", "De-escalation", "Teamwork", "Rules", "Trend", "Attitude", "Feedback", "Top Strengths", "Work On", "Rapport"]
      : ["Rolle", "Name", "Review", "Gesamtscore", "Gesamteinschätzung", "Eislaufen", "Position", "Präsenz", "Antizipation", "Deeskalation", "Teamwork", "Regeln", "Trend", "Einstellung", "Feedback", "Top Stärken", "Entwicklung", "Rapport"]
  ];

  const refs = SYSTEM_CONFIGS[currentSystem];
  refs.forEach(ref => {
    const d = gameData.referees[`${currentSystem}_${ref.id}`] || {};
    const roleText = isEn ? ref.role_en : ref.role_de;
    rows.push([
      roleText,
      d.name || "",
      d.review_round || "R1",
      computeRefScores(d).total ?? "",
      d.overall_grade || "",
      d.perf_1 || "80",
      d.perf_2 || "80",
      d.perf_3 || "80",
      d.perf_4 || "80",
      d.perf_5 || "80",
      d.perf_6 || "80",
      d.perf_7 || "80",
      d.coach_trend || "",
      d.coach_attitude || "",
      d.coach_feedback || "",
      (d.top_strengths || "").replace(/\n/g, ' '),
      (d.top_workon || "").replace(/\n/g, ' '),
      (d.general_report || "").replace(/\n/g, ' ')
    ]);
  });

  const csvContent = rows.map(e => e.map(cell => '"' + (cell ?? "").toString().replace(/"/g, '""') + '"').join(";")).join("\r\n");
  const fname = `${(gameData.global.spiel_datum || '').split('T')[0] || 'Spiel'}_Supervision_${safeFilePart(gameData.global.spiel_paarung || 'Game').replace(/\s+/g, '_')}.csv`;
  downloadBlob(new Blob(["\uFEFF" + csvContent], { type: "text/csv;charset=utf-8" }), fname);
}
