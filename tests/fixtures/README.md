# Beispieldateien

Alle Namen, Spiele und Texte sind **erfunden**. Hier nie echte Bewertungen ablegen.
Die Dateinamen sind absichtlich so gewählt, dass sie nicht unter `.gitignore` fallen.

| Datei | Zweck | Erwarteter Gesamtscore |
|---|---|---|
| `beispiel-kader.json` | Kader-Import (4 Namen) | – |
| `beispiel-v1.0.json` | Export Version 1.0 (ohne `spiel_id` und `exportiertAm`, Partner im Format „Nachname Vorname (Referee 2)“), Meier Luca R1 | 80 (Teile 80 / 79 / 80) |
| `beispiel-v1.0-ohne-evaluation.json` | Version 1.0 nur mit `scoreGesamt`, Brunner Jan R1 | 72 (aus der Datei) |
| `beispiel-v1.1.json` | Export Version 1.1, Meier Luca R2 | 94 (Teile 100 / 91 / 93) |
| `beispiel-v1.1-mit-na.json` | Version 1.1 mit N/A bei Kriterium 7, Keller Nina R1 | 59 (Teile 50 / 65 / 55) |
| `beispiel-spiel.json` | ganzes Spiel (Format von `localStorage`, Schlüssel `referee_multi_supervision_data`) | Frei Lea 94, Gast Beispiel 32 (N/A bei Kriterium 3), Brunner Jan – (keine Gesamteinschätzung) |

Saison-Statistik mit allen fünf Bewertungsdateien plus `beispiel-spiel.json`:
Meier Luca R1 80 / R2 94 (Δ +14), Keller Nina R1 59, Brunner Jan R1 72 und R2 –, Frei Lea R1 94, Gast Beispiel R1 32. Brunner Jan R2 erscheint nicht, weil die Gesamteinschätzung fehlt.
