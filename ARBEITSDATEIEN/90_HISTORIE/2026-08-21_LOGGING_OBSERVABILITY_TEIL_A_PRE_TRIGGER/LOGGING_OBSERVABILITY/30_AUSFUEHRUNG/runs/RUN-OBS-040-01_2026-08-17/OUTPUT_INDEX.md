# OUTPUT_INDEX – RUN-OBS-040-01_2026-08-17

## Run-Dokumente

| Datei | Inhalt |
|---|---|
| `RUN_LOG.md` | Pflichtlektüre, Voraussetzungsprüfung, Baseline, Umsetzungsreihenfolge, die fünf realen Befunde B-1 bis B-5, die neun Entscheidungen, Abschlussprüfung |
| `RESULT.md` | Ergebnis, N-07, Teststand, Diff, offene Punkte, Gate-Empfehlung |
| `OUTPUT_INDEX.md` | diese Datei |

## Evidence

Ordner: `40_EVIDENCE/OBS-040/RUN-01_2026-08-17/`

| Datei | Inhalt |
|---|---|
| `TEST_RESULTS.md` | Baseline und Endstand mit beiden Runnern, Aufteilung der 115 neuen Tests, Zuordnung zu den zehn im Auftrag verlangten Testgegenständen, Git-Pflichtprüfungen, bekannte Einschränkungen |
| `DIFF_SUMMARY.md` | `git diff --stat`, alle 16 geänderten Dateien mit Änderungsart, die zwei neuen Produktmodule, Nachweis „kein bestehender Test geändert", `session_coordinator.py` im Detail, kein Cross-Workstream-Diff |
| `CONTRACT_COVERAGE.md` | Deckung gegen alle drei normativen Dokumente, Zeile für Zeile mit Nachweis; offene Punkte anderer Pakete; was der Run ausdrücklich **nicht** behauptet |
| `OBSERVATION_HOOK_MATRIX.md` | vollständige §12-Matrix (42 Typen), §12.7-Prüfungen, §12.6-Reihenfolge, die sechs benannten Abweichungen A-1 bis A-6 |
| `SERVER_EVENT_MAPPING.md` | Weg eines Serverereignisses, §3.2-Feldabbildung am echten Ergebnis, Controlframes, hello-Whitelist, replayed/Priorität/Dedupe, Cursorunberührtheit |
| `probe_obs040_end_to_end.py` | ausführbares Diagnoseskript, sieben Prüfungen P-1 bis P-7 gegen echten Manager, echten SQLite-Store, echten Protokollprozessor, echten Cursorstore; exit 0 |

## Neue Produktdateien

| Datei | Zeilen |
|---|---|
| `core/observability/adapters/server_live.py` | 89 |
| `core/observability/adapters/client_events.py` | 102 |

## Geänderte Produktdateien

`app.py`, `core/audio_capture.py`, `core/controller.py`, `core/event_stream.py`,
`core/observability/__init__.py`,
`core/observability/adapters/python_logging.py`,
`core/observability/ingress.py`, `core/observability/worker.py`,
`core/session_coordinator.py`, `core/stt_session.py`, `core/text_injector.py`,
`ui/application.py`, `ui/core_bridge.py`, `ui/hotkeys.py`,
`ui/led_feedback.py`, `ui/settings_dialog.py`

## Neue Testdateien

| Datei | Tests | Gegenstand |
|---|---|---|
| `tests/test_obs040_server_live_adapter.py` | 22 | Serverabbildung, replayed, Dedupe, Controlframes, Adapter-Fehlerisolation |
| `tests/test_obs040_fanout_hook.py` | 18 | Fan-out, **N-07**, verbotene Hookstellen, `state_changed`, `protocol_error` |
| `tests/test_obs040_client_hooks.py` | 35 | §12.1–§12.5, Korrelationsfelder, §12.7 |
| `tests/test_obs040_hot_path.py` | 14 | §8.6-Quelltextnachweis, kein per-Packet-Logging, Worker-Aggregat |
| `tests/test_obs040_failure_isolation.py` | 10 | Logging-Ausfall ohne Runtime-Ausfall |
| `tests/test_obs040_contracts.py` | 16 | Modulstruktur, Layering, eingefrorener Zählersatz, Verdrahtung, Hookdeckung |

## Aktualisierte Steuerungsdateien

| Datei | Änderung |
|---|---|
| `00_STEUERUNG/CURRENT_STATE.md` | OBS-040-Abschnitt ergänzt, „Nächster Schritt" fortgeschrieben |
| `00_STEUERUNG/LOG_VERLAUF.md` | ein Meilensteineintrag angefügt (append-only) |
| `30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` | OBS-040-Implementierung abgehakt, `Aktuell` fortgeschrieben |

## Nicht verändert

- `00_NORMATIV/**` (alle drei Freeze-Dokumente byte-identisch)
- jede bestehende Testdatei
- Server-Workspace und LED-Workspace
- kein Commit, Push, Merge, Rebase, Tag oder PR
