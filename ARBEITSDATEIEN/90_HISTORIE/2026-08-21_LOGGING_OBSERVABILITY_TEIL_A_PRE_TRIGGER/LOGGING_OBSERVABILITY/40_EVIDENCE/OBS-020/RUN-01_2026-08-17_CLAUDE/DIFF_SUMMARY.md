# DIFF_SUMMARY – OBS-020 RUN-01 (Claude)

## Diff-Typ

Genau **eine** bestehende Produktdatei geändert (`core/logging_setup.py`,
additiv laut WP-OBS-020), alles Übrige sind neue Dateien.

- `git diff --check` → Exit 0, keine Whitespace-/Konfliktmarker (nur ein
  harmloser CRLF-Hinweis für `LOG_VERLAUF.md`, kein Fehler)
- `git diff --stat` (tracked) → `core/logging_setup.py` (+23/-1),
  `CURRENT_STATE.md`, `LOG_VERLAUF.md`
- `git status --short` → eine ` M`-Zeile für `core/logging_setup.py`
  (Produktcode), zwei ` M`-Zeilen für Steuerungsdateien, alles Übrige `??`

## `core/logging_setup.py` — vollständiger Diff

```diff
--- a/core/logging_setup.py
+++ b/core/logging_setup.py
@@ -58,7 +58,7 @@ class ReadableFormatter(logging.Formatter):
         super().__init__(fmt=self.FORMAT, datefmt=self.DATE_FMT)


-def setup_logging(config: LoggingConfig) -> None:
+def setup_logging(config: LoggingConfig, *, observability=None) -> None:
     """
     Configure the root logger and per-channel loggers.

@@ -117,3 +117,24 @@ def setup_logging(config: LoggingConfig) -> None:
         log_dir,
         config.json_format,
     )
+
+    # --- OBS-020: optional third handler, additive only. Without
+    # ``observability`` this function behaves exactly as before
+    # (WP-OBS-020 Sollzustand / LOGGING_CONTRACTS_FREEZE_V1.md §6).
+    if observability is not None:
+        from core.observability.adapters.python_logging import UnifiedLogHandler
+        from core.observability.normalizer import from_log_record
+
+        ingress = observability.ingress
+
+        def _normalize(record, _ingress=ingress):
+            return from_log_record(
+                record,
+                instance_id=_ingress.instance_id,
+                store_transcription_content=_ingress.store_transcription_content,
+                user_profile=_ingress.user_profile,
+            )
+
+        observability_handler = UnifiedLogHandler(ingress, _normalize)
+        observability_handler.setLevel(observability.level)
+        root_logger.addHandler(observability_handler)
```

**Genau eine bestehende Zeile geändert** — die Funktionssignatur, mit exakt
dem Sollzustand-Codeblock des Work Packages (`def setup_logging(config, *,
observability=None) -> None:`). Diese Änderung ist unvermeidlich, um den
neuen optionalen Parameter überhaupt anzubieten, und ist als solche im
Sollzustand des Work Packages selbst vorgegeben. Der komplette bisherige
Funktionskörper (Zeilen 62–119) ist byte-identisch erhalten; alles Neue ist
am Funktionsende angehängt. Keine bestehende Zeile im Funktionskörper wurde
verschoben, umformuliert oder gelöscht.

## Produktbaum: neue Dateien (4)

| Datei | Zweck |
|---|---|
| `core/observability/health.py` | `LoggingHealthState`, `LoggingHealthSnapshot`, `LoggingInternalHealth` (ein Lock für alle Zähler inkl. `deduplicated`), `observability.internal`-Logger (G-2), `_RateLimiter`/`emergency()` (G-4) |
| `core/observability/adapters/__init__.py` | Paketmarker |
| `core/observability/adapters/python_logging.py` | `UnifiedLogHandler` (G-1 Wiedereintrittssperre, G-3 `handleError`, G-7 No-Op `flush`/`close`, interner-Logger-Filter) |
| — | (`core/observability/ingress.py` und `core/observability/__init__.py` waren bereits als untracked Dateien aus OBS-010 vorhanden und wurden additiv erweitert, siehe unten) |

## Produktbaum: additiv erweiterte, bereits untracked Dateien aus OBS-010 (2)

| Datei | Ergänzung |
|---|---|
| `core/observability/ingress.py` | `ObservabilityIngress`, `NullIngress`, `NULL_INGRESS` ergänzt; das bestehende `Ingress`-Protocol unverändert erhalten |
| `core/observability/__init__.py` | Re-Exports für `ObservabilityIngress`, `NullIngress`, `NULL_INGRESS`, `LoggingHealthState`, `LoggingHealthSnapshot`, `LoggingInternalHealth`, `UnifiedLogHandler` ergänzt; bestehende Re-Exports unverändert |

Diese beiden Dateien sind noch nicht committet (OBS-010 ist selbst noch
nicht committet, siehe `CURRENT_STATE.md`), erscheinen deshalb weiterhin als
`??` in `git status` und nicht als ` M` — inhaltlich handelt es sich aber um
additive Erweiterungen bereits vorhandener Dateien, nicht um Neuanlagen.

## Neue Testdateien (6)

| Datei | Zweck |
|---|---|
| `tests/test_obs020_health.py` | Health-Zustände/-Snapshot/Zähler, Rate-Limiter (G-4), `sys.stderr`-Abwehr, `observability.internal` |
| `tests/test_obs020_ingress.py` | `ObservabilityIngress.submit`-Reihenfolge, Wasserstand/N-04, Queue-voll, `NullIngress`, Nebenläufigkeit, Zeitbasislinie |
| `tests/test_obs020_python_logging_handler.py` | `UnifiedLogHandler`: Positiv/Negativ/Failure, G-1 Rekursionssperre, G-7 No-Ops, interner Filter |
| `tests/test_obs020_logging_setup_integration.py` | `setup_logging(observability=...)`: Rückwärtskompatibilität, `client.log`-Gleichheit, dritter Handler, doppelter Aufruf |
| `tests/test_obs020_contracts.py` | Isolation, azyklische Importe, Signaturen, `observability.internal` |
| `tests/test_obs020_redaction_end_to_end.py` | End-zu-Ende-Nachweis der OBS-010-Redaction durch die neue Pipeline |

## Änderungen unter ARBEITSDATEIEN (nicht Produktcode)

- `30_AUSFUEHRUNG/Runs/RUN-OBS-020-01_2026-08-17_CLAUDE/` (RUN_LOG.md,
  RESULT.md)
- `40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE/` (TEST_RESULTS.md,
  DIFF_SUMMARY.md, CONTRACT_COVERAGE.md, REDACTION_CASES.md,
  Diagnoseskript)
- `00_STEUERUNG/CURRENT_STATE.md` (aktualisiert)
- `00_STEUERUNG/LOG_VERLAUF.md` (append-only ergänzt)

## Cross-Workstream-Check

Es wurde **kein** Produktcode außerhalb `core/observability/**` und
`core/logging_setup.py` und **kein** Test außer `tests/test_obs020_*.py`
angefasst. Server-/LED-Repo: nicht berührt (kein Lese- oder Schreibzugriff
in diesem Run nötig — WP-OBS-020 verweist auf keinen Contract-Abgleich, der
das erfordert hätte).

## Bereits aus OBS-010 vorhandene, unveränderte untracked Dateien

`core/observability/models.py`, `redaction.py`, `normalizer.py`,
`query/**`, `storage/**`, `sinks/**` sowie `tests/test_obs010_*.py` — alle
unverändert, nur zur Kontextangabe genannt (Verifikation: kein `git diff`
gegen diese Dateien möglich, da nie committet; ihr Inhalt wurde vor Beginn
gelesen und nach Abschluss erneut auf Unverändertheit geprüft — identisch
zum Stand vor diesem Run).

## Extern vorinstallierte, NICHT von diesem Run erzeugte untracked Dateien

`30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md`,
`30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/`,
`30_AUSFUEHRUNG/OBS-010_DEEPSEEK_IMPLEMENTIERUNGSAUFTRAG.md`,
`30_AUSFUEHRUNG/Prompts/{00_LOGGING_V1_PROMPT_SEQUENZ,
OBS-010..060_GATE_REVIEW, OBS-010..060_IMPLEMENTIERUNGSAUFTRAG}.md` sowie
`30_AUSFUEHRUNG/RUN-OBS-010-01_2026-08-17_DEEPSEEK/` und
`40_EVIDENCE/OBS-010/` — Materialien aus früheren Sessions bzw. externem
Setup. Nicht angefasst.
