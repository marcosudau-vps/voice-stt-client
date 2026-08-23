---
id: OBS-030
title: Worker, SQLite-Store, Retention & JSONL-Sink
status: DRAFT
authority: planning
workstream: OBS
phase: A
depends_on: OBS-010, OBS-020
freeze_reference: 00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md
last_updated: 2026-08-15
---

# OBS-030 – Worker, SQLite-Store, Retention & JSONL-Sink

> **Titelkorrektur aus OBS-000.** Die Queue liegt im Ingress und damit in
> OBS-020. Der frühere Titel „Queue, Worker, SQLite & Retention" hätte dazu
> verleitet, sie zweimal zu bauen. Der Dateiname bleibt aus Pfadgründen
> unverändert.

## Ziel

Lokale Persistenz vollständig außerhalb kritischer Runtimepfade. Das Paket wird
vor Beginn gegen `00_NORMATIV/LOGGING_CONTRACTS_FREEZE_V1.md §5` auf `READY`
gesetzt; alle Architekturentscheidungen sind bereits geschlossen.

## Scope

- [ ] `LoggingWorker` (Thread) mit Batching und Flush
- [ ] `ObservabilityManager` als Kompositionswurzel; Lebensdauer in
      `app.py::main()` mit `try/finally`, `stop(2.0)` **nach** `bridge.stop(10.0)`
- [ ] `SQLiteLogStore` + Schema/Migration/Indizes nach `CONTRACTS §5.2`
- [ ] Replay-Dedupe über den partiellen UNIQUE-Index; `write_batch` liefert
      `(eingefügt, dedupliziert)`
- [ ] Retention/Cleanup nach `CONTRACTS §5.6`
- [ ] `LogStore.clear()` für „Diagnosehistorie löschen" (`FD-S4`)
- [ ] `JsonlSink` (nur JSONL, `FD-D4`), **nach** dem SQLite-Commit
- [ ] Shutdown/Flush und Failure Isolation

## Verbindliche Korrekturen aus OBS-000

```text
D-2   Leser oeffnen KEIN mode=ro (auf WAL nicht allgemein moeglich).
      Stattdessen PRAGMA query_only = ON.
D-4   Die SQLite-Verbindung wird IM WORKER-THREAD erzeugt, nicht in start().
      Sonst sqlite3.ProgrammingError beim ersten Batch.
      check_same_thread bleibt auf dem Standard.
      -> Nachweis N-05.
      KEIN auto_vacuum, KEIN incremental_vacuum, KEIN VACUUM (FD-D8).
      Retention nach ANZAHL ebenfalls blockweise und gegen NULL gesichert.
      max_db_bytes ist ein reines Warnsignal.
AR-5  Startreihenfolge: AppConfig.load() -> Manager bauen und starten ->
      setup_logging(..., observability=manager).
AR-6  Managerlebensdauer in app.py::main(), NICHT in
      DesktopApplication.shutdown() -- vier Startabbruchpfade kommen dort
      nie hin, und der Headless-Pfad ruft shutdown nie.
FD-R5 Zaehler `deduplicated` ist Pflicht.
```

## Non-Scope

- Keine Queue (liegt in OBS-020), kein Adapter, keine UI, keine Settings.
- Kein Text-Sink.
- Keine stillen Änderungen außerhalb dieses Work Packages.
- Keine Änderung normativer Contracts ohne `DECISION REQUIRED`.
- Keine fachliche Runtime-Autorität für Logging.
- Keine Git-History-Aktion ohne ausdrückliche Freigabe.

## Pflichtprüfungen

- [ ] Positive Tests
- [ ] Negative Tests
- [ ] Failure-/Edge-Tests passend zum Paket
- [ ] relevante Produktionspfade
- [ ] **Ende-zu-Ende-Nachweis `logger.info → SQLite`** — er gehört zu **diesem**
      Gate, nicht zu OBS-020
- [ ] N-05: Verbindung aus einem Fremdthread benutzt → erwarteter Fehler
- [ ] Derselbe Serverrecord zweimal geschrieben → genau **eine** Zeile,
      `deduplicated` steigt, kein Fehler
- [ ] `user_version` = 99 → Nur-Lesen, `DEGRADED_STORE`, **nichts gelöscht**
- [ ] Migration schlägt fehl → Rollback, **Datei unverändert**, Anwendung läuft
- [ ] Nebenläufiger Leser mit offener Abfrage → `write_batch` bleibt erfolgreich
- [ ] Store dauerhaft defekt → Worker läuft weiter, `FAILED_STORE`, Anwendung
      unbeeinflusst
- [ ] Nach `stop()` ist kein Thread mehr aktiv (`threading.enumerate()`);
      **kein Test hinterlässt einen laufenden Worker** (die Suite läuft mit
      `unittest` **und** `pytest`)
- [ ] `git diff --check`
- [ ] kein unbeabsichtigter Cross-Workstream-Diff

## Evidence

Evidence wird unter einem paketbezogenen Evidence-Ordner abgelegt und enthält mindestens Commands, Exitcodes, Ergebnisse und bekannte Einschränkungen.

## Gate

`PASS` nur nach separatem Review. Ein Coding-Agent darf nicht allein aufgrund eigener grüner Tests das Gate vergeben.
