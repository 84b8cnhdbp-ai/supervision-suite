// Kader und Spieldaten im localStorage
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

// Kader wird NICHT im Code gespeichert (Datenschutz). Import über «Kader importieren»,
// gespeichert nur lokal im Browser (localStorage).
const KADER_STORAGE_KEY = 'referee_kader';
let KADER = loadKader();

function loadKader() {
  try {
    const raw = localStorage.getItem(KADER_STORAGE_KEY);
    const list = raw ? JSON.parse(raw) : [];
    return Array.isArray(list) ? list : [];
  } catch (e) { return []; }
}

function parseKaderFile(text) {
  const inhalt = text.trim();
  let names = [];
  if (inhalt.startsWith('{') || inhalt.startsWith('[')) {
    const json = JSON.parse(inhalt);
    names = Array.isArray(json) ? json : (json.schiedsrichter || json.referees || json.kader || []);
  } else {
    names = inhalt.split(/\r?\n/);
  }
  return Array.from(new Set(names
    .map(n => String(n).normalize('NFC').trim())
    .filter(n => n.length > 0)))
    .sort((a, b) => a.localeCompare(b, 'de'));
}

async function handleKaderUpload(e) {
  const file = e.target.files[0];
  if (!file) return;
  try {
    const names = parseKaderFile(await file.text());
    if (!names.length) throw new Error('leer');
    KADER = names;
    localStorage.setItem(KADER_STORAGE_KEY, JSON.stringify(KADER));
    setupRefereeDropdown();
    if (activeTabType === 'ref') loadRefereeForm(activeRefIndex);
    alert(t('kader_imported', { n: KADER.length }));
  } catch (err) {
    alert(t('kader_error'));
  }
  e.target.value = '';
}

function getDefaultRefData() {
  return {
    overall_grade: "",
    review_round: "R1",
    perf_1: "80", perf_2: "80", perf_3: "80", perf_4: "80", perf_5: "80", perf_6: "80", perf_7: "80",
    coach_trend: "Konstant stabil",
    coach_attitude: "Gut / Angemessen",
    coach_feedback: "Konstruktiv"
  };
}

function saveGlobalState() {
  gameData.global = {
    system_typ: document.getElementById('system_typ').value,
    spiel_liga: document.getElementById('spiel_liga').value,
    spiel_paarung: document.getElementById('spiel_paarung').value,
    spiel_id: document.getElementById('spiel_id').value,
    spiel_datum: document.getElementById('spiel_datum').value,
    spiel_ort: document.getElementById('spiel_ort').value,
    supervisor_name: document.getElementById('supervisor_name').value,
    crew_notes: document.getElementById('crew_notes') ? document.getElementById('crew_notes').value : ""
  };
  saveToStorage();
}

function saveToStorage() {
  localStorage.setItem('referee_multi_supervision_data', JSON.stringify(gameData));
  const status = document.getElementById('saveStatus');
  if (status) {
    status.innerText = t('saved_status', { zeit: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'}) });
  }
}

function loadFullState() {
  const raw = localStorage.getItem('referee_multi_supervision_data');
  if (raw) {
    try {
      gameData = JSON.parse(raw);
      if (gameData.global) {
        if (gameData.global.system_typ) {
          currentSystem = gameData.global.system_typ;
          document.getElementById('system_typ').value = currentSystem;
        }
        document.getElementById('spiel_liga').value = gameData.global.spiel_liga || "National League";
        document.getElementById('spiel_paarung').value = gameData.global.spiel_paarung || "";
        document.getElementById('spiel_id').value = gameData.global.spiel_id || "";
        document.getElementById('spiel_datum').value = gameData.global.spiel_datum || "";
        document.getElementById('spiel_ort').value = gameData.global.spiel_ort || "";
        document.getElementById('supervisor_name').value = gameData.global.supervisor_name || "";
        if (document.getElementById('crew_notes')) {
          document.getElementById('crew_notes').value = gameData.global.crew_notes || "";
        }
      }
    } catch(e) {
      console.error(e);
    }
  }
}
