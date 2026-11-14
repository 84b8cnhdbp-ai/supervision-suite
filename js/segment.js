// Knopfreihen (Segmented Controls) als echte Radiogruppen:
// <fieldset> mit normalen <input type="radio">, sichtbar als Segmente (<label>).
// Dadurch funktionieren Tastatur (Pfeiltasten, Tab) und VoiceOver („Taste 2 von 5“) wie bei jeder Radiogruppe.
// Reihenfolge immer vom besten zum schlechtesten Wert, von links nach rechts.
// Gespeichert wird weiterhin genau der bisherige Wert (val).

// Baut die Reihe in den Platzhalter <div data-seg="name">.
// optionen: [{ val, kurz, lang, farbe }] – kurz sichtbar, lang für Screenreader/Tooltip,
// farbe: CSS-Variable der gewählten Note (z. B. '--r-pp'); ohne farbe = neutral (weiss).
function baueSegmente(name, optionen, { standard = '', onChange } = {}) {
  const platz = document.querySelector(`[data-seg="${name}"]`);
  if (!platz) return;
  const bisher = segWert(name) || standard;
  platz.innerHTML = '';

  const fs = document.createElement('fieldset');
  fs.className = 'seg';
  fs.id = name;
  if (platz.dataset.segLabel) fs.setAttribute('aria-labelledby', platz.dataset.segLabel);
  if (platz.dataset.segBeschreibung) fs.setAttribute('aria-describedby', platz.dataset.segBeschreibung);

  optionen.forEach((o, i) => {
    const id = `${name}__${i}`;
    const input = document.createElement('input');
    input.type = 'radio';
    input.name = name;
    input.id = id;
    input.value = o.val;
    const label = document.createElement('label');
    label.htmlFor = id;
    label.className = 'seg-opt';
    if (o.farbe) {
      label.dataset.farbe = '1';
      label.style.setProperty('--farbe', `var(${o.farbe})`);
    }
    if (o.lang && o.lang !== o.kurz) {
      const sichtbar = document.createElement('span');
      sichtbar.setAttribute('aria-hidden', 'true');
      sichtbar.textContent = o.kurz;
      const vorlesen = document.createElement('span');
      vorlesen.className = 'sr-only';
      vorlesen.textContent = o.lang;
      label.append(sichtbar, vorlesen);
      label.title = o.lang;
    } else {
      label.textContent = o.kurz;
    }
    fs.append(input, label);
  });

  if (onChange) fs.addEventListener('change', () => onChange(segWert(name)));
  platz.appendChild(fs);
  setzeSeg(name, bisher);
}

// Gewählter Wert einer Reihe ('' wenn nichts gewählt).
function segWert(name) {
  const r = document.querySelector(`input[name="${name}"]:checked`);
  return r ? r.value : '';
}

// Wert setzen; unbekannte Werte = nichts gewählt (wie bisher bei einer Auswahlliste).
function setzeSeg(name, wert) {
  document.querySelectorAll(`input[name="${name}"]`).forEach((r) => { r.checked = r.value === wert; });
}

// Alle Knopfreihen der App (neu beschriftet bei Sprachwechsel; gewählte Werte bleiben).
function baueAlleKnopfreihen() {
  const farben = { '100': '--r-pp', '80': '--r-p', '50': '--r-m', '20': '--r-mm', 'NA': '--r-na' };

  baueSegmente('system_typ', t('system_options'), { standard: currentSystem, onChange: (v) => switchSystem(v) });
  baueSegmente('current_review_round', t('round_options'), { standard: 'R1', onChange: () => saveCurrentRefData() });

  baueSegmente('overall_grade', [
    { val: '100', kurz: t('grade_vg'), farbe: '--r-pp' },
    { val: '80', kurz: t('grade_good'), farbe: '--r-p' },
    { val: '50', kurz: t('grade_ni'), farbe: '--r-m' },
    { val: '20', kurz: t('grade_unsat'), farbe: '--r-mm' }
  ], { onChange: () => calcScores() });   // keine Vorwahl: bewusst wählen

  const noten = t('perf_options').map((o) => ({ ...o, farbe: farben[o.val] }));
  for (let i = 1; i <= 7; i++) baueSegmente(`perf_${i}`, noten, { standard: '80', onChange: () => calcScores() });

  baueSegmente('coach_trend', t('coach_trend_opts'), { standard: 'Konstant stabil', onChange: () => calcScores() });
  baueSegmente('coach_attitude', t('coach_att_opts'), { standard: 'Gut / Angemessen', onChange: () => calcScores() });
  baueSegmente('coach_feedback', t('coach_feed_opts'), { standard: 'Konstruktiv', onChange: () => calcScores() });

  // Menü „Mehr“: Sprache (sichtbare Sprachen, plus eine über ?lang= gewählte) und Darstellung
  baueSegmente('sprache', SPRACHEN.filter((s) => s.sichtbar || s.code === currentLang).map((s) => ({ val: s.code, kurz: s.name })),
    { standard: currentLang, onChange: (v) => { setLanguage(v); fokusAufWahl('sprache'); } });
  baueSegmente('darstellung', ['auto', 'light', 'dark'].map((p) => ({ val: p, kurz: t('theme_' + p) })),
    { standard: getThemePref(), onChange: (v) => setTheme(v) });
}

// Fokus auf die gewählte Option (z. B. nachdem die Reihe neu beschriftet wurde)
function fokusAufWahl(name) {
  const r = document.querySelector(`input[name="${name}"]:checked`);
  if (r) r.focus();
}

// Text unter der Gesamteinschätzung: Definition der gewählten Stufe oder Hinweis, bewusst zu wählen.
function zeigeStufenText() {
  const box = document.getElementById('gradeBox');
  const hinweis = document.getElementById('gradeHint');
  if (!box || !hinweis) return;
  const texte = { '100': 'desc_vg', '80': 'desc_good', '50': 'desc_ni', '20': 'desc_unsat' };
  const wert = segWert('overall_grade');
  box.classList.toggle('grade-missing', !wert);
  hinweis.classList.toggle('grade-hinweis-fehlt', !wert);
  hinweis.textContent = wert ? t(texte[wert]) : t('grade_choose');
}
