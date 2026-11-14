// Saison-Statistik aus importierten JSON-Dateien
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

// MULTI-JSON STATISTIK LOGIK
async function handleSeasonFilesUpload(e) {
  const files = Array.from(e.target.files);
  if (!files.length) return;

  const stats = {};
  let skipped = 0;
  KADER.forEach(name => {
    stats[name] = { R1: null, R2: null };
  });

  for (const file of files) {
    try {
      const text = await file.text();
      const json = JSON.parse(text);
      
      if (json.schiedsrichter && json.reviewRunde) {
        const n = String(json.schiedsrichter).normalize('NFC').trim();
        if (!stats[n]) stats[n] = { R1: null, R2: null };
        const total = json.evaluation ? computeRefScores(json.evaluation).total : json.scoreGesamt;
        stats[n][json.reviewRunde] = { ...json, scoreGesamt: total ?? json.scoreGesamt };
      } else if (json.referees) {
        Object.values(json.referees).forEach(r => {
          if (r.name) {
            if (!stats[r.name]) stats[r.name] = { R1: null, R2: null };
            const rRunde = r.review_round || "R1";
            const total = computeRefScores(r).total;
            if (total !== null) stats[r.name][rRunde] = { scoreGesamt: total, datum: json.global?.spiel_datum || "" };
          }
        });
      }
    } catch (err) {
      skipped++;
      console.warn("Fehler beim Parsen von", file.name, err);
    }
  }

  renderSeasonStatsDashboard(stats);
  if (skipped) alert(`${skipped} Datei(en) konnten nicht gelesen werden und wurden übersprungen.`);
  e.target.value = '';
}

function renderSeasonStatsDashboard(stats) {
  const container = document.getElementById('seasonStatsContent');

  let totalR1 = 0, countR1 = 0;
  let totalR2 = 0, countR2 = 0;
  let totalCompleted = 0;

  let rowsHtml = "";

  const allNames = Array.from(new Set([...KADER, ...Object.keys(stats)])).sort((a, b) => a.localeCompare(b, 'de'));

  allNames.forEach(name => {
    const data = stats[name] || { R1: null, R2: null };
    const r1 = data.R1 ? data.R1.scoreGesamt : null;
    const r2 = data.R2 ? data.R2.scoreGesamt : null;

    if (r1 !== null) { totalR1 += r1; countR1++; }
    if (r2 !== null) { totalR2 += r2; countR2++; }

    let avgStr = "-";
    let deltaStr = `<span style="color: var(--text-muted);">-</span>`;

    if (r1 !== null && r2 !== null) {
      totalCompleted++;
      const avg = ((r1 + r2) / 2).toFixed(1);
      avgStr = `<strong>${avg}%</strong>`;
      const delta = r2 - r1;
      if (delta > 0) {
        deltaStr = `<span style="color: var(--green); font-weight: bold;">+${delta}% ↗</span>`;
      } else if (delta < 0) {
        deltaStr = `<span style="color: var(--red); font-weight: bold;">${delta}% ↘</span>`;
      } else {
        deltaStr = `<span style="color: var(--text-muted); font-weight: bold;">0% →</span>`;
      }
    } else if (r1 !== null) {
      avgStr = `${r1}%`;
    } else if (r2 !== null) {
      avgStr = `${r2}%`;
    }

    let statusBadge = `<span style="background: #FEE2E2; color: #991B1B; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;">0/2 Offen</span>`;
    if (r1 !== null && r2 !== null) {
      statusBadge = `<span style="background: #DCFCE7; color: #166534; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;">2/2 Fertig</span>`;
    } else if (r1 !== null || r2 !== null) {
      statusBadge = `<span style="background: #FEF9C3; color: #854D0E; padding: 2px 8px; border-radius: 10px; font-size: 11px; font-weight: bold;">1/2 In Arbeit</span>`;
    }

    rowsHtml += `
      <tr>
        <td style="font-weight: 600;">${escapeHtml(name)}</td>
        <td style="text-align: center;">${statusBadge}</td>
        <td style="text-align: center;">${r1 !== null ? r1 + '%' : '<span style="color: var(--text-muted);">-</span>'}</td>
        <td style="text-align: center;">${r2 !== null ? r2 + '%' : '<span style="color: var(--text-muted);">-</span>'}</td>
        <td style="text-align: center;">${deltaStr}</td>
        <td style="text-align: center;">${avgStr}</td>
      </tr>
    `;
  });

  const avgTeamR1 = countR1 > 0 ? (totalR1 / countR1).toFixed(1) + "%" : "-";
  const avgTeamR2 = countR2 > 0 ? (totalR2 / countR2).toFixed(1) + "%" : "-";

  container.innerHTML = `
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; margin-bottom: 20px;">
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 14px; border-radius: 8px; text-align: center;">
        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Abgeschlossen (2/2)</div>
        <div style="font-size: 22px; font-weight: 800; color: var(--navy); margin-top: 4px;">${totalCompleted} / ${allNames.length}</div>
      </div>
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 14px; border-radius: 8px; text-align: center;">
        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Ø Review 1 (Hinrunde)</div>
        <div style="font-size: 22px; font-weight: 800; color: var(--accent); margin-top: 4px;">${avgTeamR1}</div>
      </div>
      <div style="background: var(--bg-card); border: 1px solid var(--border); padding: 14px; border-radius: 8px; text-align: center;">
        <div style="font-size: 11px; font-weight: 700; color: var(--text-muted); text-transform: uppercase;">Ø Review 2 (Rückrunde)</div>
        <div style="font-size: 22px; font-weight: 800; color: var(--green); margin-top: 4px;">${avgTeamR2}</div>
      </div>
    </div>

    <table>
      <thead>
        <tr>
          <th>Schiedsrichter</th>
          <th style="text-align: center;">Status</th>
          <th style="text-align: center;">Review 1</th>
          <th style="text-align: center;">Review 2</th>
          <th style="text-align: center;">Entwicklung (Δ)</th>
          <th style="text-align: center;">Gesamtnote</th>
        </tr>
      </thead>
      <tbody>
        ${rowsHtml}
      </tbody>
    </table>
  `;
}
