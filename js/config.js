// Rollen je Schiedsrichter-System
// (aus index.html ausgelagert, Etappe 1 – Code unverändert)

const SYSTEM_CONFIGS = {
  "4-Man": [
    { id: "h1", role_de: "Head Referee 1", role_en: "Head Referee 1", type: "head" },
    { id: "h2", role_de: "Head Referee 2", role_en: "Head Referee 2", type: "head" },
    { id: "l1", role_de: "Linesperson 1", role_en: "Linesperson 1", type: "lines" },
    { id: "l2", role_de: "Linesperson 2", role_en: "Linesperson 2", type: "lines" }
  ],
  "3-Man": [
    { id: "h1", role_de: "Head Referee 1", role_en: "Head Referee 1", type: "head" },
    { id: "l1", role_de: "Linesperson 1", role_en: "Linesperson 1", type: "lines" },
    { id: "l2", role_de: "Linesperson 2", role_en: "Linesperson 2", type: "lines" }
  ],
  "2-Man": [
    { id: "r1", role_de: "Referee 1", role_en: "Referee 1", type: "dual" },
    { id: "r2", role_de: "Referee 2", role_en: "Referee 2", type: "dual" }
  ],
  "1-Man": [
    { id: "r1", role_de: "Einzel-Schiedsrichter", role_en: "Solo Referee", type: "solo" }
  ]
};
