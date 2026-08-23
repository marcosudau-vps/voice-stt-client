# RUN_LOG – OBS-030 RUN-01 (Claude)

Datum: 2026-08-17
Session-Root: `P:\GithubRepos\marcosudau-vps`
Schreibbarer Projektbereich: `voice-stt-client\workspaces\einheitliche-triggerarchitektur`
Auftrag: `ARBEITSDATEIEN\10_AKTUELL\LOGGING_OBSERVABILITY\30_AUSFUEHRUNG\Prompts\OBS-030_IMPLEMENTIERUNGSAUFTRAG.md`

## Voraussetzung geprüft

`CURRENT_STATE.md`: OBS-020 GATE PASS (2026-08-17, unabhängiger Review) — erfüllt.

## Gelesene Pflichtunterlagen

- README.md, AGENTS.md, CURRENT_STATE.md, MASTERPLAN.md, ARBEITSPROZESS.md
- `00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md` (vollständig)
- `00_NORMATIV/LOGGING_ARCHITEKTUR_FREEZE_V1.md` (vollständig)
- `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` (FD-R3..R6, OBS-030-Abschnitte)
- `20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-030_QUEUE_WORKER_SQLITE_RETENTION.md`
- `WP-OBS-040...md`, `WP-OBS-050...md` (zur Abgrenzung des Scopes)
- bestehender Code: `core/observability/**` (Stand nach OBS-010/OBS-020),
  `core/config.py`, `core/logging_setup.py`, `app.py`, `ui/application.py`
- Referenzmuster: `core/history.py` (SQLite-Anti-Pattern-Liste beachtet),
  `core/event_cursor_store.py` (atomares Schreiben), `ui/led_feedback.py`
  (bounded queue / daemon thread / timeout join)

## Baseline vor Änderungen

```
$ python -m pytest -q
1 failed, 714 passed, 337 subtests passed in 39.46s
```

Der eine Fehlschlag (`test_ap06_followup.py::...test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
`ModuleNotFoundError: No module named 'lefx.interfaces'`) ist identisch zum in
`CURRENT_STATE.md` dokumentierten vorbestehenden Umgebungsbefund und liegt
außerhalb dieses Diffs.

## Scope-Entscheidung: Config-Anbindung (dokumentiert, siehe Auftrag Zeile 67)

WP-OBS-030 verlangt explizit "ObservabilityManager als Kompositionswurzel;
Lebensdauer in `app.py::main()`" sowie (AR-5) die Startreihenfolge
`AppConfig.load() -> Manager bauen und starten -> setup_logging(...)`. Damit
der Manager in `app.py::main()` echte Konfigurationswerte (Queue-Größe,
Batch-Größe, DB-Pfad, Retention, ...) erhält, muss `AppConfig` einen
`logging.observability`-Unterabschnitt kennen (`CONTRACTS §10.1`).

Diese minimale Schnittstelle (Dataclass `LoggingObservabilityConfig` +
Feld `LoggingConfig.observability` + Default-Werte) ist für die in diesem WP
selbst verlangte `app.py`-Verdrahtung zwingend erforderlich und wird hiermit
ausdrücklich dokumentiert (Auftrag: "keine spätere Work-Package-
Implementierung vorziehen, außer eine minimale Schnittstelle ist für
Testbarkeit zwingend erforderlich").

**Korrektur während der Ausführung:** Der ursprüngliche Plan sah vor, die
`_from_dict`-Sonderbehandlung für `logging.observability` (Nachweis **N-12**,
wörtlich WP-OBS-050 zugeordnet) NICHT vorzuziehen und stattdessen auf den
generischen `_build`-Pfad zu vertrauen, in der Annahme, dass ohne
Einstellungs-UI niemand `logging.observability.*` in eine `config.yaml`
schreibt. Das erwies sich als falsch: `AppConfig.save()` serialisiert JEDE
Dataclass vollständig, also auch das neue `observability`-Feld, sodass jeder
bestehende Save→Load-Roundtrip-Test (`test_history.py`,
`test_text_injector.py`, `test_feedback_mapping.py`,
`test_ap06_followup.py::TestSettingsDialog`) beim erneuten `AppConfig.load()`
sofort auf denselben stillen Fehler lief: `LoggingConfig.observability` wurde
zu einem rohen `dict` statt einer `LoggingObservabilityConfig`-Instanz, und
`AppConfig.validate()` stürzte mit `AttributeError: 'dict' object has no
attribute 'validate'` ab — eine echte Regression, kein Randfall. Die
`_from_dict`-Sonderbehandlung (analog `history`) wurde deshalb doch in
diesem Run ergänzt, als direkte Voraussetzung dafür, dass das neue Feld
selbst nicht die bestehende Suite bricht — nicht als Vorgriff auf OBS-050s
volle Settings-Integration. Die eigentliche Nachweis-Verantwortung (N-12,
Settings-UI-Integration) bleibt bei OBS-050.

Bewusst weiterhin NICHT vorgezogen (bleibt OBS-050-Scope):
- Settings-Tab, `apply_runtime_config`-Anbindung in `core/controller.py`,
  „Diagnosehistorie löschen"/„Logs anzeigen"-Schaltflächen (UI).
- Verdrahtung von `observability` in `core/controller.py`/`ui/core_bridge.py`
  (Fan-out-Hook, Client-Observation-Hooks) — OBS-040.

## Implementierungsschritte

Siehe `DIFF_SUMMARY.md` in `40_EVIDENCE/OBS-030/RUN-01_2026-08-17_CLAUDE/`
für die vollständige Dateiliste.

## Abschluss

Siehe `RESULT.md`.
