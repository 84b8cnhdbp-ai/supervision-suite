// Rollen je Schiedsrichter-System; Versionsnummer der App

// Version der App (sichtbar unten in der Seitenleiste). Der „Stand“ daneben kommt automatisch aus ?v= in index.html.
const APP_VERSION = "2.0";
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

// Datenregel: Gespeicherte Spiele ohne Angabe zum System (ältere Stände) sind 4-Mann-Spiele.
// Nicht ändern – sonst verschwinden deren Bewertungen. Der Standard für NEUE Spiele steht in js/club.js (standardSystem).
const SYSTEM_OHNE_ANGABE = "4-Man";

// System für ein neues Spiel: Vereins-Einstellung, falls gültig
function startSystem() {
  return CLUB.standardSystem && SYSTEM_CONFIGS[CLUB.standardSystem] ? CLUB.standardSystem : SYSTEM_OHNE_ANGABE;
}

const SYSTEM_CONFIGS = {
  "4-Man": [
    { id: "h1", role_de: "Head Referee 1", role_en: "Head Referee 1", role_fr: "Head Referee 1", role_it: "Head Referee 1", type: "head" },
    { id: "h2", role_de: "Head Referee 2", role_en: "Head Referee 2", role_fr: "Head Referee 2", role_it: "Head Referee 2", type: "head" },
    { id: "l1", role_de: "Linesperson 1", role_en: "Linesperson 1", role_fr: "Linesperson 1", role_it: "Linesperson 1", type: "lines" },
    { id: "l2", role_de: "Linesperson 2", role_en: "Linesperson 2", role_fr: "Linesperson 2", role_it: "Linesperson 2", type: "lines" }
  ],
  "3-Man": [
    { id: "h1", role_de: "Head Referee 1", role_en: "Head Referee 1", role_fr: "Head Referee 1", role_it: "Head Referee 1", type: "head" },
    { id: "l1", role_de: "Linesperson 1", role_en: "Linesperson 1", role_fr: "Linesperson 1", role_it: "Linesperson 1", type: "lines" },
    { id: "l2", role_de: "Linesperson 2", role_en: "Linesperson 2", role_fr: "Linesperson 2", role_it: "Linesperson 2", type: "lines" }
  ],
  "2-Man": [
    { id: "r1", role_de: "Referee 1", role_en: "Referee 1", role_fr: "Referee 1", role_it: "Referee 1", type: "dual" },
    { id: "r2", role_de: "Referee 2", role_en: "Referee 2", role_fr: "Referee 2", role_it: "Referee 2", type: "dual" }
  ],
  "1-Man": [
    { id: "r1", role_de: "Einzel-Schiedsrichter", role_en: "Solo Referee", role_fr: "Arbitre unique", role_it: "Arbitro unico", type: "solo" }
  ]
};
