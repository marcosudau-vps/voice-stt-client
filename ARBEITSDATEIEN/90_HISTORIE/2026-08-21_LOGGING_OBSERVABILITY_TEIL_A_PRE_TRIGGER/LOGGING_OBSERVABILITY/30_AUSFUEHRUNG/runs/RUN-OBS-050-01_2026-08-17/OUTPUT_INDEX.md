# OUTPUT_INDEX – RUN-OBS-050-01_2026-08-17

## Run-Unterlagen

| Datei | Inhalt |
|---|---|
| `RUN_LOG.md` | Ablauf, Pflichtlektüre, Befunde F-1..F-4, Entscheidungen E-1..E-10, Prüfungen |
| `RESULT.md` | Ergebnis und Begründung, Teststand, Grenzen |
| `RUN_REPORT.md` | Pflichtform nach Themen-`AGENTS.md` inkl. Gate-Empfehlung |
| `OUTPUT_INDEX.md` | diese Übersicht |

## Evidence (`40_EVIDENCE/OBS-050/RUN-01_2026-08-17/`)

| Datei | Inhalt |
|---|---|
| `TEST_RESULTS.md` | Kommandos, Exitcodes, Zahlen, Baselinevergleich, Einschränkungen |
| `DIFF_SUMMARY.md` | jede neue und jede geänderte Datei mit Begründung; Befunde |
| `CONTRACT_COVERAGE.md` | Vorgabe → Umsetzung → Nachweis, je normativer Fundstelle |
| `QUERY_CASES.md` | Abfragefälle Q-01..Q-62 mit dem jeweiligen Test |
| `UI_ACCEPTANCE.md` | Abnahmepunkte A-01..A-33, Non-Scope, manuelle Restpunkte |
| `probe_obs050_end_to_end.py` | Ende-zu-Ende-Diagnoseskript, 12 Prüfungen, exit 0 |

## Produktcode

Neu:

```text
core/observability/query/local.py        LocalLogProvider
core/observability/query/service.py      LogQueryService
core/logging_settings_metadata.py        Metadaten des sechsten Tabs
ui/logs/__init__.py                      Paket
ui/logs/log_window.py                    LogWindow
ui/logs/log_page.py                      LogPage
ui/logs/log_table_model.py               LogTableModel
ui/logs/log_filter_bar.py                LogFilterBar
ui/logs/log_detail_view.py               LogDetailView
ui/logs/log_query_controller.py          LogQueryController
```

Geändert (additiv):

```text
.gitignore                    Befund F-1: !ui/logs/
app.py                        Manager an run_gui (N-4)
core/controller.py            apply_config in der Apply-Kette (§10.4)
core/logging_setup.py         Handler an die Kompositionswurzel melden (§8.7)
core/observability/ingress.py apply_config + Config-Listener
core/observability/manager.py query_service, health_snapshot, Runtime-Apply
core/observability/worker.py  request_settings + Anwendung auf dem Workerthread
ui/application.py             Manager, LogWindow, Löschaktion
ui/settings_dialog.py         sechster Tab, zwei Schaltflächen, optional_path
ui/tray.py                    Menüeintrag "Logs anzeigen …"
```

## Tests

```text
tests/test_obs050_local_provider.py   42 Tests
tests/test_obs050_query_service.py    10 Tests
tests/test_obs050_settings.py         37 Tests
tests/test_obs050_ui.py               60 Tests
tests/test_obs050_contracts.py        21 Tests
tests/obs050_apply_support.py         Hilfsmodul ohne Testfälle
```

## Steuerung

| Datei | Änderung |
|---|---|
| `00_STEUERUNG/CURRENT_STATE.md` | OBS-050-Eintrag, nächster Schritt |
| `00_STEUERUNG/LOG_VERLAUF.md` | ein Meilensteineintrag (append-only) |
| `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` | Implementierungshaken, Abschnitt „Aktuell" |
