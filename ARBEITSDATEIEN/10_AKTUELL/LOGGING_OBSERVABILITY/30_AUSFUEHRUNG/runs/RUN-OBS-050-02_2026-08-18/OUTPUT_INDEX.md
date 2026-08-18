# OUTPUT_INDEX – RUN-OBS-050-02_2026-08-18

## Run-Unterlagen

| Datei | Inhalt |
|---|---|
| `RUN_LOG.md` | Reproduktion beider Befunde, Ursachen, Korrekturen, Umfang, W-1/W-2, Verifikation |
| `RESULT.md` | Ergebnis, B-1 und B-2 je mit Ursache/Korrektur/Nachweis, Teststand |
| `RUN_REPORT.md` | Pflichtform inkl. Entscheidungen K-1..K-4 und Gate-Empfehlung |
| `OUTPUT_INDEX.md` | diese Übersicht |

## Evidence (`40_EVIDENCE/OBS-050/RUN-02_2026-08-18/`)

| Datei | Inhalt |
|---|---|
| `FIX_SUMMARY.md` | Ursache und Korrektur je Befund, Einordnung der unveränderten Gate-Probe, Datei- und Scope-Abgleich |
| `TEST_RESULTS.md` | neue und richtiggestellte Tests, alle Kommandos mit Exitcodes, Vorbestandsnachweis |
| `UI_ACCEPTANCE.md` | W-2: A-11..A-13 richtiggestellt, A-34..A-42 neu, Ordnungsregel in einem Satz |
| `probe_obs050_ordering_fix.py` | acht richtungsbewusste Laufzeitprüfungen gegen den echten Stack, exit 0 |

## Unverändert erhaltene Vorunterlagen

| Pfad | Inhalt |
|---|---|
| `40_EVIDENCE/OBS-050/RUN-01_2026-08-17/` | vollständige RUN-01-Evidence, nicht angefasst |
| `40_EVIDENCE/OBS-050/GATE-REVIEW-01_2026-08-18_CLAUDE/` | Gate-FAIL samt beider Probeskripte, nicht angefasst |
| `30_AUSFUEHRUNG/runs/RUN-OBS-050-01_2026-08-17/` | RUN-01-Unterlagen, nicht angefasst |

## Geänderter Code

```text
ui/logs/log_page.py              Produkt, 456 -> 526 Zeilen
tests/test_obs050_ui.py          +9 Regressionstests, eine Erwartung korrigiert
tests/test_obs050_contracts.py   Trichter-Test angepasst, ein Strukturtest neu
```

Keine weitere Produktdatei berührt.

## Steuerung

| Datei | Änderung |
|---|---|
| `00_STEUERUNG/CURRENT_STATE.md` | Gate-FAIL und Korrekturlauf eingetragen, nächster Schritt |
| `00_STEUERUNG/LOG_VERLAUF.md` | ein Meilensteineintrag (append-only) |
| `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` | Abschnitt „Aktuell"; **kein** Haken gesetzt oder entfernt |
