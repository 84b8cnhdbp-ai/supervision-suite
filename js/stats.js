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
  if (skipped) zeigeToast(t('stats_skipped', { n: skipped }), 'fehler', 5000);
  e.target.value = '';
}

// Prozentwert wie bisher („80%“, Durchschnitt „87.0%“); fehlend = „–“
const statProzent = (v) => (v === null || v === undefined ? '<span class="stat-leer">–</span>' : `${v}%`);

// Saison-Statistik (Zahlen wie bisher; Aussehen Etappe 2.8). Sortieren usw. folgt in Etappe 7.
let letzteStatistik = null;   // für Sprachwechsel

function renderSeasonStatsDashboard(stats) {
  letzteStatistik = stats;
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

    let avgStr = '<span class="stat-leer">–</span>';
    let deltaStr = '<span class="stat-leer">–</span>';
    if (r1 !== null && r2 !== null) {
      totalCompleted++;
      avgStr = `<strong>${((r1 + r2) / 2).toFixed(1)}%</strong>`;
      const delta = r2 - r1;
      // Richtung mit Pfeil (nicht nur Farbe); negative Werte mit echtem Minuszeichen
      if (delta > 0) deltaStr = `<span class="stat-plus">+${delta}% <span aria-hidden="true">↑</span></span><span class="sr-only"> ${t('stats_up')}</span>`;
      else if (delta < 0) deltaStr = `<span class="stat-minus">−${Math.abs(delta)}% <span aria-hidden="true">↓</span></span><span class="sr-only"> ${t('stats_down')}</span>`;
      else deltaStr = `<span class="stat-gleich">0% <span aria-hidden="true">→</span></span><span class="sr-only"> ${t('stats_same')}</span>`;
    } else if (r1 !== null) {
      avgStr = `${r1}%`;
    } else if (r2 !== null) {
      avgStr = `${r2}%`;
    }

    const status = r1 !== null && r2 !== null ? ['fertig', t('stats_status_done')]
      : (r1 !== null || r2 !== null ? ['arbeit', t('stats_status_progress')] : ['offen', t('stats_status_open')]);

    rowsHtml += `
      <tr>
        <th scope="row">${escapeHtml(name)}</th>
        <td class="stat-mitte"><span class="stat-abzeichen stat-${status[0]}">${escapeHtml(status[1])}</span></td>
        <td class="stat-zahl">${statProzent(r1)}</td>
        <td class="stat-zahl">${statProzent(r2)}</td>
        <td class="stat-zahl">${deltaStr}</td>
        <td class="stat-zahl">${avgStr}</td>
      </tr>`;
  });

  const avgTeamR1 = countR1 > 0 ? (totalR1 / countR1).toFixed(1) + "%" : "–";
  const avgTeamR2 = countR2 > 0 ? (totalR2 / countR2).toFixed(1) + "%" : "–";

  container.innerHTML = `
    <div class="stat-kacheln">
      <div class="karte stat-kachel"><span class="stat-kachel-titel">${escapeHtml(t('stats_done'))}</span><strong id="statFertig">${totalCompleted} / ${allNames.length}</strong></div>
      <div class="karte stat-kachel"><span class="stat-kachel-titel">${escapeHtml(t('stats_avg_r1'))}</span><strong id="statR1" class="stat-r1">${avgTeamR1}</strong></div>
      <div class="karte stat-kachel"><span class="stat-kachel-titel">${escapeHtml(t('stats_avg_r2'))}</span><strong id="statR2" class="stat-r2">${avgTeamR2}</strong></div>
    </div>
    <div class="stat-tabelle-box">
      <table class="stat-tabelle">
        <thead>
          <tr>
            <th scope="col">${escapeHtml(t('stats_col_name'))}</th>
            <th scope="col" class="stat-mitte">${escapeHtml(t('stats_col_status'))}</th>
            <th scope="col" class="stat-zahl">${escapeHtml(t('stats_col_r1'))}</th>
            <th scope="col" class="stat-zahl">${escapeHtml(t('stats_col_r2'))}</th>
            <th scope="col" class="stat-zahl">${escapeHtml(t('stats_col_delta'))}</th>
            <th scope="col" class="stat-zahl">${escapeHtml(t('stats_col_total'))}</th>
          </tr>
        </thead>
        <tbody>${rowsHtml}</tbody>
      </table>
    </div>`;
}

function initStatistik() {
  const datei = document.getElementById('multiJsonInput');
  document.getElementById('btnStatsLaden').addEventListener('click', () => datei.click());
  datei.addEventListener('change', handleSeasonFilesUpload);
}
