# RESULT — RUN-OBS-020-01_2026-08-17_CLAUDE

## Status

`OBS-020 IMPLEMENTED – READY FOR REVIEW`

## Zusammenfassung

OBS-020 (Ingress, Backpressure, Health & Python-Logging-Handler) wurde auf
Basis des kanonischen OBS-010-Modells implementiert. Voraussetzung (OBS-010
`GATE PASS`) war laut `CURRENT_STATE.md` erfüllt.

Neu:

- `core/observability/health.py` — `LoggingHealthState` (7 Zustände),
  `LoggingHealthSnapshot` (frozen, alle Zähler inkl. `deduplicated`),
  `LoggingInternalHealth` (ein Lock für alle Zähler), rate-begrenzter
  Emergency-stderr-Kanal über den eigenen, nicht propagierenden Logger
  `observability.internal` (G-2/G-4).
- `core/observability/ingress.py` — additiv um `ObservabilityIngress`
  (`submit`/`observe_server_result`/`event`/`drain`, CONTRACTS §6),
  `NullIngress`, `NULL_INGRESS` ergänzt. Eine bounded `queue.Queue`
  (Default 8192) mit Wasserstandsregel bei 75 % (ARCH §7.1/§7.2, inkl.
  `not replayed` in der Prioritätsregel, FD-R1/N-04).
- `core/observability/adapters/python_logging.py` — `UnifiedLogHandler`
  mit Wiedereintrittssperre (G-1), Health-basierter `handleError` (G-3),
  No-Op `flush()`/`close()` (G-7), Filter gegen den eigenen internen Logger.
- `core/observability/__init__.py` — additive Re-Exports der neuen
  öffentlichen Namen.
- `core/logging_setup.py` — additiv: optionaler Parameter
  `observability=None`, optionaler dritter Handler. Einzige geänderte Zeile
  ist die Funktionssignatur; der gesamte bisherige Funktionskörper ist
  unverändert; alles Neue ist angehängt.

## Testergebnis

- Baseline vor Änderung (nach OBS-010): 640/640 grün.
- Neue OBS-020-Tests: 75/75 grün (66 Kernpaket + 9 End-zu-Ende-Redaction).
- Vollständige Suite nach OBS-020: **715/715 grün**
  (`python -m pytest -q` und `python -m unittest discover -s tests -p
  "test_*.py"`, beide `OK`).
- Kein bestehender Test wurde geändert.

## Abschlussprüfung

- `git diff --check` → Exit 0
- `git status --short` → nur `core/logging_setup.py` als geänderte
  Produktdatei; alles Übrige neue/untracked Dateien unter
  `core/observability/**`, `tests/test_obs020_*.py` und den
  Steuerungs-/Evidence-Bereichen
- `git diff --stat` → siehe DIFF_SUMMARY.md
- Scope-Prüfung gegen WP-OBS-020: erfüllt (siehe RUN_LOG.md Abschnitt 2)

## Gate-Hinweis (laut Work Package unverändert gültig)

Der Ende-zu-Ende-Nachweis `logger.info → SQLite` gehört zum Gate von
OBS-030 — in OBS-020 existiert der Store noch nicht. Dieser Run wurde gegen
einen aufzeichnenden Fake-Ingress (`RecordingIngress` in den Testdateien)
abgenommen. Grüne Tests gegen Fakes sind ausdrücklich **kein**
Fertigstellungsnachweis für den Store-Pfad — dieser folgt in OBS-030.

`PASS` erfordert laut Work Package einen separaten Review; dieser Run vergibt
das Gate nicht selbst.

## Nächster Schritt

OBS-020 Gate-Review (frische Session), danach OBS-030
(Worker, SQLite-Store, Retention & JSONL-Sink).
