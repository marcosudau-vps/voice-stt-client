# DIFF_SUMMARY – OBS-030 RUN-02 (Korrekturlauf)

Branch: `feat/einheitliche-triggerarchitektur`
Kein Commit, kein Push, kein Merge, kein Rebase, kein Tag, kein PR.
Der Diff ist kumulativ gegenüber `HEAD` und enthält damit RUN-01 **und**
diesen Korrekturlauf.

## `git status --short` (Produkt und Tests)

```text
 M app.py
 M core/config.py
 M core/observability/__init__.py
 M core/observability/health.py
?? core/observability/manager.py
?? core/observability/sinks/jsonl_file.py
?? core/observability/storage/sqlite.py
?? core/observability/worker.py
?? tests/test_obs030_app_wiring.py
?? tests/test_obs030_config.py
?? tests/test_obs030_contracts.py
?? tests/test_obs030_gate_corrections.py
?? tests/test_obs030_jsonl_sink.py
?? tests/test_obs030_manager.py
?? tests/test_obs030_path_boundaries.py
?? tests/test_obs030_sqlite_store.py
?? tests/test_obs030_worker.py
?? tests/test_obs030_worker_fault_injection.py
```

## `git diff --stat` (verfolgte Bestandsdateien)

```text
 app.py                         |  27 ++++--
 core/config.py                 | 182 ++++++++++++++++++++++++++++++++++++++++-
 core/observability/__init__.py |   8 ++
 core/observability/health.py   |  21 ++++-
 4 files changed, 230 insertions(+), 8 deletions(-)
```

Das ist **dieselbe Menge geänderter Bestandsdateien wie in RUN-01**, die der
Gate-Review eigenständig verifiziert hat. `core/observability/health.py` steht
nach dem Cleanup wieder bei `+21/-2`, also exakt auf dem vom Gate-Review
festgehaltenen Stand; `core/observability/ingress.py` ist wieder unverändert.

```text
$ git diff --check
(leer, Exit 0)
```

## Was RUN-02 gegenüber RUN-01 geändert hat

### Im Cleanup zurückgenommen (Prompt `OBS-030_FIX_RUN_II.md`)

| Datei | zwischenzeitlich in RUN-02 | Stand jetzt |
|---|---|---|
| `core/observability/ingress.py` | +5/-0 — `submit()` erhöhte `health.record_dropped_failed()` vor dem `False` im `health.is_failed()`-Zweig | **unverändert gegenüber `HEAD`**; die Datei ist wieder aus dem Diff heraus |
| `core/observability/health.py` | zusätzlich `dropped_failed` (Snapshot-Feld mit Default) und `record_dropped_failed()` | beides entfernt; wieder auf dem RUN-01-Stand `+21/-2` |
| `00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` | +56 — Abschnitt 11 mit `DR-OBS-030-01` | **byte-identisch zum Stand vor RUN-OBS-030-02** (`git diff` leer, kein `git status`-Eintrag) |

Grund der Rücknahme: `dropped_failed` war eine echte Erweiterung von
`ARCH §7.3` und `CONTRACTS §11.2` ohne Autorisierung, und der Nachtrag
veränderte die normative Grundlage, gegen die anschließend geprüft werden
soll. Die Auslegungsfrage bleibt offen und ausschließlich in
`DECISION_REQUIRED.md` dokumentiert.

### Bereits in RUN-01 geänderte, in RUN-02 erweiterte Bestandsdateien

| Datei | RUN-01 | RUN-02 zusätzlich |
|---|---|---|
| `core/config.py` | +101 | P-8: `user_profile_roots()`, `is_inside_user_profile()`, `_validate_user_profile_path()`, zwei Aufrufe in `LoggingObservabilityConfig.validate()`. |
| `core/observability/health.py` | +21/-2 | **keine** (nach dem Cleanup) |
| `app.py`, `core/observability/__init__.py` | unverändert gegenüber RUN-01 | keine Änderung in RUN-02 |

### Neue (noch nicht verfolgte) Produktdateien mit Änderungen in RUN-02

| Datei | Änderung |
|---|---|
| `core/observability/worker.py` | B-1 (guarded `run()`, `_record_loop_failure`, `_finish`, `FAILED_WORKER`, `_prepare_record`), W-1 (`_write_sink` unabhängig), W-2 (`_report_retention_pressure`), W-4 (`_probe_store`), W-7b (`_records_since_retention += inserted`), W-7c (`stop()` zählt Reste) |
| `core/observability/storage/sqlite.py` | W-7a (PRAGMA-Reihenfolge nach §5.2), W-4 (`probe_write()`) |
| `core/observability/manager.py` | B-3 (`_resolve_profile_path`), W-5 (`DISABLED`), `_NullStore.probe_write()` |

### Neue Testdateien

`tests/test_obs030_worker_fault_injection.py`,
`tests/test_obs030_path_boundaries.py`,
`tests/test_obs030_gate_corrections.py` (zusammen 47 Tests).

### Genau eine geänderte Testdatei aus RUN-01

`tests/test_obs030_config.py`: der Literalwert `file_sink_dir="C:/tmp/obs-sink"`
wurde durch einen Pfad im Benutzerprofil ersetzt (Konstante
`SINK_DIR_INSIDE_PROFILE`). Vollständige Begründung in `PATH_BOUNDARIES.md`,
Abschnitt „Angepasster Bestandstest". Der entfallene Fall lebt als Negativtest
weiter. Es wurde **kein** Test außerhalb von `tests/test_obs030_*.py`
geändert.

## Scope-Abgleich

**Unverändert (stichprobenhaft und per `git status` bestätigt):**
`core/observability/ingress.py` (nach dem Cleanup wieder),
`ui/**`, `core/controller.py`, `core/session_coordinator.py`,
`core/event_stream.py`, `core/stt_session.py`, `core/logging_setup.py`,
`core/led_controller.py`, `core/observability/normalizer.py`,
`core/observability/redaction.py`, `core/observability/models.py`,
`core/observability/adapters/python_logging.py`,
`core/observability/query/**`, `core/observability/sinks/base.py`,
`core/observability/storage/base.py`.

**Kein Cross-Workstream-Diff:** Weder `voice-stt-server` noch
`led_controller_respeaker-v3` wurden angefasst (eigene Verzeichnisse
außerhalb dieses Git-Repositories; dieser Workspace ist die Repowurzel).

**Kein OBS-040/OBS-050:** kein `adapters/server_live.py`, kein
`query/local.py`, kein `query/service.py`, kein `ui/logs/**`, kein
Settings-Eintrag, kein Fan-out-Hook in `core/session_coordinator.py`.

## Dokumentationsdiff (außerhalb von Produkt und Tests)

```text
 M ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md
 M ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md            (append-only)
 ?? .../30_AUSFUEHRUNG/runs/RUN-OBS-030-02_2026-08-17/
 ?? .../40_EVIDENCE/OBS-030/RUN-02_2026-08-17/
 M  .../40_EVIDENCE/OBS-030/RUN-01_.../CONTRACT_COVERAGE.md   (Korrekturvermerk angehängt)
 M  .../40_EVIDENCE/OBS-030/RUN-01_.../TEST_RESULTS.md        (Korrekturvermerk angehängt)
 M  .../30_AUSFUEHRUNG/runs/RUN-OBS-030-01_.../RESULT.md      (Korrekturvermerk angehängt)
 .../30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md                  (wiederhergestellt, siehe RUN_LOG)
```

`00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` erscheint nach dem Cleanup
**nicht mehr** im Diff: der Nachtrag `DR-OBS-030-01` wurde entfernt, die Datei
ist byte-identisch zum Stand vor `RUN-OBS-030-02`. **Kein normatives Dokument
wird durch diesen Run verändert.**

Die Gate-Review-Evidence
(`40_EVIDENCE/OBS-030/GATE-REVIEW-01_2026-08-17_CLAUDE/`) ist **unverändert**.
Die drei RUN-01-Dateien sind inhaltlich unverändert und ausschließlich am
Ende um einen gekennzeichneten Korrekturvermerk ergänzt; sie bleiben laut
Cleanup-Auftrag Gegenstand des unabhängigen Gate-Reviews.
