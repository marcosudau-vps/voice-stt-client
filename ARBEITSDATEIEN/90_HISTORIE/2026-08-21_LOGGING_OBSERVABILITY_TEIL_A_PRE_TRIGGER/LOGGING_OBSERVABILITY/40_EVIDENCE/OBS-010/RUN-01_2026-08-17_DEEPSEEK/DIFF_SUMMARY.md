# DIFF_SUMMARY – OBS-010 RUN-01 (DeepSeek)

## Diff-Typ

Nur **neue Dateien**. Keine bestehende Datei im Produktbaum wurde geändert
(WP-OBS-010: „Dieses Paket legt ausschließlich neue Dateien an.").

- `git diff --stat` (tracked) → leer
- `git diff --check` → Exit 0, keine Whitespace-/Konfliktmarker
- `git status --short` → nur `??` (neue/untracked), keine ` M`/` D`

## Produktbaum: neue Dateien (18)

| Datei | Zweck |
|---|---|
| `core/observability/__init__.py` | Paket-Re-Exports (additiv; Endstand laut ARCH §5.1 folgt in OBS-020/030) |
| `core/observability/models.py` | `CanonicalLogRecord` (frozen), `ProducerKind`, `Channel`, `Level`, `Scope`, `RecordPriority`, `level_rank`, `_freeze`; `details`/`raw` beim Bau eingefroren; `priority`-Property §1.5; Feld-/Typ-Validierung |
| `core/observability/redaction.py` | `unfreeze`, `redact_mapping`, `redact_text`, `shorten_user_paths`, `SENSITIVE_KEYS`, `TRANSCRIPT_KEYS` (R-3/8/9/10/11/12, FD-C11/C12) |
| `core/observability/normalizer.py` | `from_log_record`, `from_server_result`, `from_client_event`, `LOGGER_CHANNEL_MAP`, `_normalize_level` (INFO-Rückfall + `source_severity`), Control-/Event-Mapping §3.2, R-6-Whitelist |
| `core/observability/ingress.py` | `Ingress`-Protocol (Signatur der strukturierten Client-Observation-API §6); OBS-020 implementiert |
| `core/observability/storage/__init__.py` | Paketmarker |
| `core/observability/storage/base.py` | `LogStore`-Protokoll (`write_batch`, `clear`) — nur Signaturen |
| `core/observability/sinks/__init__.py` | Paketmarker |
| `core/observability/sinks/base.py` | `Sink`-Protokoll (`write_batch`, `close`) — nur Signaturen |
| `core/observability/query/__init__.py` | Paketmarker |
| `core/observability/query/base.py` | `ProviderState`, `ProviderStatus`, `QueryFilter`, `LogRecordView`, `QueryPage`, `LogProvider` (CONTRACTS §8) |
| `tests/test_obs010_models.py` | Modell-/Enum-/Prioritäts-/Validierungs-/Freeze-Tests |
| `tests/test_obs010_redaction.py` | N-01, R-3/R-8/R-9/R-10/R-11/R-12, N-02, Bounds, Mutation-Guards |
| `tests/test_obs010_normalizer_python.py` | §3.1: Channel-/Producer-/Component-/Details-/Correlations-/Zeit-/Negativ-Tests |
| `tests/test_obs010_normalizer_server.py` | §3.2: EVENT-/CONTROL-Mapping, hello-Whitelist, Duplicate, Negativ (None, wirft nie) |
| `tests/test_obs010_normalizer_client.py` | §6-API: Felder, Scope, Redaction, Negativ (Level/Details/Segment) |
| `tests/test_obs010_query_contracts.py` | §8: Filter-/View-/Page-/Status-/Protocol-Tests |
| `tests/test_obs010_contracts.py` | Isolation (PySide6/QtCore/sqlite3), Zyklenfreiheit, Ingress-Signatur, Runtime-Import-Grenze, Mutation-Guards |

## Änderungen unter ARBEITSDATEIEN (nicht Produktcode)

- `30_AUSFUEHRUNG/RUN-OBS-010-01_2026-08-17_DEEPSEEK/` (RUN_LOG.md, RESULT.md,
  RUN_REPORT.md, OUTPUT_INDEX.md)
- `40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK/` (TEST_RESULTS.md,
  DIFF_SUMMARY.md, CONTRACT_COVERAGE.md, Diagnose-Skript)
- `00_STEUERUNG/CURRENT_STATE.md` (aktualisiert)
- `00_STEUERUNG/LOG_VERLAUF.md` (append-only ergänzt)

## Cross-Workstream-Check

Es wurde **kein** Produktcode außerhalb `core/observability/**` und
**kein** Test außer `tests/test_obs010_*.py` angefasst. Server-/LED-Repo:
unberührt (nur gelesen, keine Schreibzugriffe).

## Extern vorinstallierte, NICHT von diesem Run erzeugte untracked Dateien

`30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md`, `LOGGING_V1_PROMPT_PIPELINE_V2/`,
`Prompts/{00_LOGGING_V1_PROMPT_SEQUENZ, OBS-010..060_GATE_REVIEW,
OBS-020..060_IMPLEMENTIERUNGSAUFTRAG}.md` — externes Setup vom 2026-08-17
02:00:02. Nicht angefasst.