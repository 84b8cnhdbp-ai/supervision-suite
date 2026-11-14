// Bewertungslogik – einzige Berechnung des Scores (computeRefScores)
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

// ZENTRALE BEWERTUNGSLOGIK (eine Quelle für Formular, Übersicht, Export, Statistik)
const COACH_SCORES = {
  coach_trend: { "Fortschritt erkennbar": 100, "Konstant stabil": 80, "Erstbeobachtung": 80, "Rückschritt / Instabil": 40 },
  coach_attitude: { "Vorbildlich / Professionell": 100, "Gut / Angemessen": 80, "Ausbaufähig": 45 },
  coach_feedback: { "Sehr offen & reflektiert": 100, "Konstruktiv": 80, "Defensiv / Rechtfertigend": 40 }
};
const WEIGHTS = { part2: 0.30, part3: 0.50, part4: 0.20 };

function computeRefScores(d) {
  d = d || {};
  const g = parseInt(d.overall_grade, 10);
  const part2 = isNaN(g) ? null : g;

  const radar = [];
  let sum = 0, count = 0;
  for (let i = 1; i <= 7; i++) {
    const v = parseInt(d[`perf_${i}`] ?? "80", 10);
    if (isNaN(v)) { radar.push(null); continue; }  // N/A
    sum += v; count++;
    radar.push(v / 33.33);
  }
  const part3 = count > 0 ? Math.round(sum / count) : null;

  const c = ['coach_trend', 'coach_attitude', 'coach_feedback'].map(k => COACH_SCORES[k][d[k]] ?? 80);
  const part4 = Math.round((c[0] + c[1] + c[2]) / 3);

  let total = null;
  if (part2 !== null && part3 !== null) {
    total = Math.round(part2 * WEIGHTS.part2 + part3 * WEIGHTS.part3 + part4 * WEIGHTS.part4);
  } else if (part2 === null && part3 !== null) {
    total = null; // Gesamteinschätzung fehlt -> kein Gesamtscore
  }
  return { part2, part3, part4, total, radar };
}
