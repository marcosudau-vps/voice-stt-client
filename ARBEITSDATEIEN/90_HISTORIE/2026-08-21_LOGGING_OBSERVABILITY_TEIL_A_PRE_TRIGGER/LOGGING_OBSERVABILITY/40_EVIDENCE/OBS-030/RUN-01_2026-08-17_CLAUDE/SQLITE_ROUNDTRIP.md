# SQLITE_ROUNDTRIP – OBS-030 RUN-01 (Claude)

## DDL (CONTRACTS §5.2)

`tests/test_obs030_sqlite_store.py::TestBootstrapAndDDL` bestätigt an einer
frisch angelegten Datei:

- `PRAGMA user_version` = `1` nach dem ersten `open()`.
- Tabellen `logs` und `schema_meta` existieren; `schema_meta` enthält genau
  `created_at`, `created_by_version`, `last_migrated_at`.
- Alle sechs Indizes existieren:
  `ux_logs_producer_event` (partieller UNIQUE-Index),
  `ix_logs_session_id`, `ix_logs_received_at`, `ix_logs_channel_level`,
  `ix_logs_activation`, `ix_logs_correlation`.
- `PRAGMA journal_mode` = `wal`.
- `-wal`/`-shm`-Geschwister entstehen im selben Verzeichnis wie die
  Hauptdatei (P-9).

## Struktureller/raw-Daten-Round-Trip (CONTRACTS §4.1/§5.2)

`TestWriteBatchRoundTrip` schreibt einen `CanonicalLogRecord` mit allen 24
Feldern (inkl. `details` mit verschachtelten Listen/Dicts und `raw`) und
liest die Zeile über eine unabhängige `sqlite3`-Verbindung zurück:

- Alle Skalarfelder (inkl. `replayed` als `0`/`1`) stimmen exakt.
- `details`/`raw` sind gültiges JSON in `details_json`/`raw_json`.
- **Frozen-Container-Test**: Ein `CanonicalLogRecord` friert `details`
  beim Bau immer zu `MappingProxyType`/`tuple` ein
  (`models.py::_freeze`). Der Store serialisiert das korrekt zu
  JSON-Objekten/-Arrays — **kein** `default=str`-Kollaps auf Container-Ebene
  (das würde, wie in `CONTRACTS §4.1` als Sicherheitsbefund benannt, die
  schlüsselbasierte Redaction unwirksam machen, weil keine Schlüssel mehr
  existierten). Verifiziert:
  `test_structured_details_with_frozen_containers_round_trip`.
- Leere `details`/`None`-`raw` werden als SQL-`NULL` gespeichert, nicht als
  `"{}"`-String (`test_empty_details_and_none_raw_store_as_null`).

## Dedupe/Identity (CONTRACTS §5.5)

`TestDedupe`:

- Zwei Schreibvorgänge mit identischem `(producer_id, event_id)` ergeben
  **eine** Zeile; der zweite Aufruf liefert `(0, 1)` (`eingefügt,
  dedupliziert`); die **erste** gespeicherte Fassung gewinnt
  (`replayed` bleibt `0`, auch wenn die zweite, verworfene Fassung
  `replayed=True` trug — exakt die in `CONTRACTS §5.5` geforderte Garantie
  "Die ERSTE gespeicherte Fassung gewinnt").
- Records ohne `event_id` (Client/LED) kollidieren nie untereinander.
- Der Dedupe-Schlüssel ist an `producer_id` gebunden: derselbe `event_id`
  unter zwei verschiedenen `producer_id`s ergibt zwei Zeilen (Vorbereitung
  auf einen künftigen zweiten Produzenten, `ARCH §10.3`).

`ON CONFLICT`-Hinweis: SQLite verlangt bei einem **partiellen** Unique-Index
als Arbiter, dass die `ON CONFLICT`-Klausel dieselbe `WHERE`-Bedingung trägt
wie der Index selbst (`ON CONFLICT (producer_id, event_id) WHERE event_id IS
NOT NULL DO NOTHING`) — ohne dieses `WHERE` bricht SQLite mit „ON CONFLICT
clause does not match any PRIMARY KEY or UNIQUE constraint" ab. In diesem Run
zunächst genau so aufgetreten und in `storage/sqlite.py::_INSERT_SQL`
korrigiert; durch `test_same_producer_event_id_twice_is_one_row_and_counted`
und `test_records_without_event_id_never_collide` dauerhaft abgesichert.

## Migration (CONTRACTS §5.5 „MIGRATION")

`TestMigrationAndVersioning`:

- `user_version = 99` (höher als unterstützt) → `open()` liefert
  `degraded=True`; Store bleibt les-/schreibbar für Lesezugriffe, aber
  `write_batch` liefert `(0, 0)` ohne zu schreiben; der vorher vorhandene
  Sentinel-Datensatz bleibt unverändert erhalten — **nichts gelöscht, nichts
  downgegradet**.
- Ein absichtlich fehlschlagender Migrationsschritt (monkeypatchte
  `_MIGRATIONS`) löst ein `ROLLBACK` aus; `open()` liefert `ok=False`; ein
  danach mit den echten Migrationen neu erstellter Store funktioniert
  einwandfrei — die Datei wurde durch den fehlgeschlagenen Versuch nicht
  dauerhaft beschädigt.
- Ein nicht anlegbares Zielverzeichnis liefert `ok=False` statt einer
  Exception.

## Nebenläufigkeit / Lock-nahe Fälle

- **N-05**: `open()` in einem Thread, `write_batch()` aus einem fremden
  Thread → `sqlite3.ProgrammingError` (`check_same_thread` bleibt auf dem
  Standard, `CONTRACTS §5.4`).
- **Nebenläufiger Leser**: Eine zweite, unabhängige `sqlite3`-Verbindung mit
  `PRAGMA query_only = ON` hält eine offene `SELECT`-Transaktion mitten im
  Scan; `write_batch()` auf der Schreiberverbindung bleibt währenddessen
  erfolgreich und schnell (< 2 s Testschwelle) — WAL entkoppelt Leser und
  Schreiber wie in `CONTRACTS §5.4` gefordert.

## Retention (CONTRACTS §5.6)

- Altersbasiert: Nur Zeilen älter als der Cutoff werden gelöscht; jüngere
  bleiben unangetastet.
- Anzahlbasiert: Bei `max_entries=4` unter 10 Zeilen werden genau die 6
  ältesten gelöscht, die 4 jüngsten bleiben.
- Blockweise: Mit `RETENTION_BLOCK_SIZE` künstlich auf `3` gesenkt, löscht
  ein einzelner `run_retention()`-Aufruf dennoch alle 10 fälligen Zeilen
  (mehrere 3er-Blöcke innerhalb des Zeitbudgets).
- **Kein** `VACUUM`/`auto_vacuum`/`incremental_vacuum` irgendwo im
  Produktionscode (`test_retention_never_calls_vacuum`, FD-D8).

## Neustart/Persistenz

`TestRestartPersistence` und `test_obs030_manager.py::TestRestartAcrossManagers`:
Daten überleben `close()` + Neuöffnen sowohl auf Store- als auch auf
Manager-Ebene (zwei komplette `ObservabilityManager`-Läufe nacheinander,
zweiter Lauf sieht die Zeile des ersten).

## `clear()` (FD-S4)

`TestClear`: `DELETE FROM logs` liefert die korrekte Zeilenanzahl zurück;
`PRAGMA wal_checkpoint(TRUNCATE)` läuft danach (best-effort, Fehler dort
werden verschluckt, da der eigentliche Löschvorgang bereits committet ist).
Auf Manager-/Worker-Ebene läuft `clear()` nachweislich auf dem
Worker-Thread (derselbe, der die Verbindung besitzt), nicht auf dem
aufrufenden Thread (`test_request_clear_runs_on_worker_thread_and_returns_count`).
