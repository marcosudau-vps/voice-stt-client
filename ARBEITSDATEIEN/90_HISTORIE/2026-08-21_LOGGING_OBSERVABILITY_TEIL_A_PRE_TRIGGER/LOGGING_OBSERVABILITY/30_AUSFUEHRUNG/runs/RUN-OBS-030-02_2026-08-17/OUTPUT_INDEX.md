# OUTPUT_INDEX – RUN-OBS-030-02_2026-08-17

Alle Pfade relativ zu
`voice-stt-client/workspaces/einheitliche-triggerarchitektur`.

## Run-Dokumente

| Datei | Inhalt |
|---|---|
| `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/RUN_LOG.md` | Ablauf, gelesene Grundlagen, Arbeitsschritte, während der Ausführung gefundene Befunde, eingehaltene Grenzen |
| `.../RUN-OBS-030-02_2026-08-17/RESULT.md` | Status, B-1/B-2/B-3, W-1…W-7, Teststand, geänderte Dateien, offene Punkte |
| `.../RUN-OBS-030-02_2026-08-17/RUN_REPORT.md` | Kompakter fachlicher Bericht, Entscheidung, Risiken und Grenzen |
| `.../RUN-OBS-030-02_2026-08-17/OUTPUT_INDEX.md` | diese Datei |

## Evidence

| Datei | Inhalt |
|---|---|
| `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-02_2026-08-17/GATE_FINDINGS.md` | B-1/B-2/B-3 mit Korrektur und Nachweis; W-1…W-7 je FIXED/DEFERRED/NOT A DEFECT mit Contract-Referenz |
| `.../RUN-02_2026-08-17/TEST_RESULTS.md` | Alle Befehle, Exitcodes und Zahlen; erneute Prüfung der vorbestehenden Fehlschläge |
| `.../RUN-02_2026-08-17/FAULT_INJECTION.md` | Laufzeitproben zu B-1/W-1/W-2/W-4/B-3 und Gegenüberstellung zur Probe des Gate-Reviews |
| `.../RUN-02_2026-08-17/PATH_BOUNDARIES.md` | P-8: Umsetzung, Testmatrix, begründete Anpassung eines RUN-01-Tests, Status von P-9/M-11 |
| `.../RUN-02_2026-08-17/CONTRACT_COVERAGE.md` | Korrigierte Contract-Abdeckung (ersetzt inhaltlich die RUN-01-Fassung) |
| `.../RUN-02_2026-08-17/DIFF_SUMMARY.md` | `git status`/`git diff --stat`/`git diff --check`, Scope-Abgleich |
| `.../RUN-02_2026-08-17/DECISION_REQUIRED.md` | **Offene Entscheidung** zur Auslegung von `ARCH §8.3` „nur verwerfen und zählen": Ausgangsproblem, Normzitat, Konflikt mit `ARCH §7.3`/`CONTRACTS §11.2`, beide Lesarten, Hinweis dass `dropped_failed` **nicht** Bestandteil des finalen Stands ist, Status offen |
| `.../RUN-02_2026-08-17/probe_obs030_gate_fixes.py` | Reproduzierbares Probeskript (Evidence, kein Produktcode) |

## Geänderter Produktcode

| Datei | Befund |
|---|---|
| `core/observability/worker.py` | B-1, W-1, W-2, W-4, W-7b, W-7c |
| `core/observability/storage/sqlite.py` | W-7a, W-4 |
| `core/observability/manager.py` | B-3, W-5 |
| `core/config.py` | B-3 (P-8) |

`core/observability/health.py` und `core/observability/ingress.py` sind nach
dem Cleanup **nicht** mehr Teil der Änderungen dieses Runs: der Zähler
`dropped_failed` wurde vollständig zurückgenommen. `health.py` steht wieder
auf dem RUN-01-Stand `+21/-2`, `ingress.py` ist unverändert gegenüber `HEAD`.

## Tests

| Datei | Umfang |
|---|---|
| `tests/test_obs030_worker_fault_injection.py` | 6 (neu) |
| `tests/test_obs030_path_boundaries.py` | 23 (neu) |
| `tests/test_obs030_gate_corrections.py` | 18 (neu) |
| `tests/test_obs030_config.py` | ein Pfadliteral angepasst (begründet in `PATH_BOUNDARIES.md`) |
| `tests/test_obs030_{worker,sqlite_store,manager,jsonl_sink,contracts,app_wiring}.py` | unverändert, grün |

## Fortgeschriebene Steuerungsdateien

| Datei | Änderung |
|---|---|
| `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md` | Stand nach dem Korrekturlauf, offene Punkte, nächster zulässiger Schritt |
| `ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md` | append-only Eintrag zu diesem Run |
| `.../30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` | wiederhergestellt (siehe `RUN_LOG.md` §6) und fortgeschrieben; „OBS-030 – Gate Review" bleibt `[ ]` |
| `.../00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` | **unverändert** — der im Korrekturlauf angehängte Abschnitt 11 (`DR-OBS-030-01`) wurde im Cleanup entfernt; die Datei ist byte-identisch zum Stand vor diesem Run |

## Historie, die unverändert bleibt

| Datei | Status |
|---|---|
| `40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/GATE_REVIEW.md` | unverändert (`OBS-030 GATE FAIL`) |
| `40_EVIDENCE/OBS-030/RUN-01_2026-08-17_CLAUDE/*` | unverändert; `CONTRACT_COVERAGE.md` und `TEST_RESULTS.md` haben einen **angehängten** Korrekturvermerk |
| `30_AUSFUEHRUNG/runs/RUN-OBS-030-01_2026-08-17_CLAUDE/*` | unverändert; `RESULT.md` hat einen **angehängten** Korrekturvermerk |
