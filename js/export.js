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

// Was zum Sichern fehlt – dieselbe Prüfung für „Bereit zum Sichern?“ und das Fenster beim Sichern.
// d: Daten des Schiedsrichters (name, overall_grade); Spieldatum aus den Spieldaten.
function pruefeSicherbar(d) {
  return [
    { schluessel: 'name', text: t('missing_name'), ok: !!d.name, aktion: () => {
      const sel = document.getElementById('current_schiri_name');
      const custom = document.getElementById('current_schiri_name_custom');
      springeZuFeld(sel.value === '_CUSTOM_' ? custom : sel);
    } },
    { schluessel: 'datum', text: t('missing_date'), ok: !!(gameData.global && gameData.global.spiel_datum),
      aktion: () => springeZuFeld(document.getElementById('spiel_datum')) },
    { schluessel: 'note', text: t('missing_grade'), ok: computeRefScores(d).part2 !== null, aktion: () => {
      const erste = document.querySelector('input[name="overall_grade"]');
      springeZuFeld(erste, document.getElementById('gradeBox'));
    } }
  ];
}

function exportSingleReviewJSON() {
  saveCurrentRefData();
  const refConfig = SYSTEM_CONFIGS[currentSystem][activeRefIndex];
  const refKey = `${currentSystem}_${refConfig.id}`;
  const refData = gameData.referees[refKey] || {};
  const sc = computeRefScores(refData);

  // Fehlt etwas, Fenster mit Liste; ein Tipp auf einen Eintrag springt zum Feld
  const missing = pruefeSicherbar(refData).filter((p) => !p.ok);
  if (missing.length) {
    zeigeFenster({
      titel: t('export_missing_title'), text: t('export_missing_hint'), liste: missing,
      knoepfe: [{ text: t('dlg_ok'), wert: true, art: 'primaer', fokus: true }]
    });
    return;
  }

  const name = refData.name;
  const round = refData.review_round || "R1";
  const dateStr = gameData.global.spiel_datum.split("T")[0];

  const payload = {
    version: "1.1",
    club: CLUB.exportName,
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
  // CSV ist ein Bericht: Spaltentitel und Rollen in der gewählten Sprache, Werte deutsch
  const rows = [
    [t('csv_game_id'), gameData.global.spiel_id || ""],
    [t('csv_league'), gameData.global.spiel_liga || ""],
    [t('csv_matchup'), gameData.global.spiel_paarung || ""],
    [t('csv_date'), gameData.global.spiel_datum || ""],
    [t('csv_arena'), gameData.global.spiel_ort || ""],
    [t('csv_supervisor'), gameData.global.supervisor_name || ""],
    [t('csv_system'), currentSystem],
    [t('csv_crew_notes'), (gameData.global.crew_notes || "").replace(/\n/g, ' ')],
    [],
    t('csv_headers')
  ];

  const refs = SYSTEM_CONFIGS[currentSystem];
  refs.forEach(ref => {
    const d = gameData.referees[`${currentSystem}_${ref.id}`] || {};
    const roleText = rolle(ref);
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
