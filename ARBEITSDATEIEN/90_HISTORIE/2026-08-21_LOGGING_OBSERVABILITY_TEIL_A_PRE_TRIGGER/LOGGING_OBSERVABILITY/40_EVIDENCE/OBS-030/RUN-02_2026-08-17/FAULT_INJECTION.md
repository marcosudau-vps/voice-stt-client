# FAULT_INJECTION – OBS-030 RUN-02

Unabhängige Laufzeitproben zu B-1, W-1, W-2, W-4 und B-3. Das Skript ist
Gegenstück zu den Proben des Gate-Reviews und liegt reproduzierbar neben
dieser Datei:

```text
$ python ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-02_2026-08-17/probe_obs030_gate_fixes.py
```

CWD: Client-Workspace. Interpreter: Python 3.12.10 (global).
Das Skript ist Evidence, kein Produktcode; nichts importiert es.

> **Cleanup-Vermerk.** Die Ausgabe unten stammt aus dem Lauf **nach** der
> Rücknahme von `dropped_failed` (Prompt `OBS-030_FIX_RUN_II.md`). Die Zeile
> `dropped_failed : 5` der ersten Fassung ist entfallen; an ihrer Stelle
> steht die Beobachtung, dass abgewiesene Submits die Queue nicht erreichen.
> Die Frage, ob sie zusätzlich zu zählen sind, ist offen —
> `DECISION_REQUIRED.md`.

## Vollständige Ausgabe (2026-08-17)

```text
[observability] worker_loop_failed: boom
[observability] worker_loop_failed: boom
[observability] worker_drain_failed: boom
[observability] shutdown_flush_incomplete: 1 records dropped at shutdown
[observability] store_write_failed: store broken
[observability] retention_pressure: db_bytes=1024 exceeds max_db_bytes=512
== B-1a  single unexpected worker exception ==
  worker alive after boom : True
  worker_errors           : 1
  health.state            : ok
  submit() after boom     : True
  rows written after boom : 1
== B-1b  permanently failing worker loop ==
  queued before boom      : True
  worker alive            : False
  health.state            : failed_worker
  health.is_failed()      : True
  worker_errors           : 6
  live observability thrds: []
  submit() after death    : [False, False, False, False, False]
  queue depth unchanged   : True
  dropped_shutdown        : 1
== W-1  broken store must not silence the sink ==
  store rows              : 0
  sink lines written      : 20
  health.state            : degraded_store
== W-2  logging.retention_pressure as a canonical record ==
  pressure records        : 1 (edge-triggered)
    type=logging.retention_pressure channel=performance level=WARNING is_internal=True details={'db_bytes': 1024, 'max_db_bytes': 512}
== W-4  empty test write after the store pause ==
  probe_write() unopened  : False
  probe_write() open      : True
  probe_write() closed    : False
== B-3  P-8 path boundaries ==
  REJECTED db_path = C:\ProgramData\somewhere-else\observability.sqlite3
  REJECTED db_path = C:\Users\marco\AppData\Local\RealtimeSTT Client\..\..\..\..\escaped.sqlite3
  REJECTED db_path = observability.sqlite3
  REJECTED file_sink_dir = C:\ProgramData\sink
  ACCEPTED db_path = C:\Users\marco\AppData\Local\RealtimeSTT Client\observability.sqlite3
  ACCEPTED file_sink_dir = C:\Users\marco\AppData\Local\RealtimeSTT Client\logs\observability
  DEFAULT_LOCAL_APP_DIR   = C:\Users\marco\AppData\Local\RealtimeSTT Client
```

## Gegenüberstellung zum Gate-Review

Das Gate-Review hielt für dieselbe Injektion (`Ingress.drain` wirft) fest:

```text
after  boom: worker alive = False
             health.state = ok
             worker_errors = 0
             live observability threads = []
submit() after worker death returns: [True, True, True, True, True]
health.is_failed() -> False
rows written after death: 1
queue depth (records stranded): 5
```

Jetzt:

| Beobachtung | Gate-Review (FAIL) | RUN-02 |
|---|---|---|
| Einzelne Ausnahme beendet den Worker | ja (still) | **nein** — `worker_errors = 1`, Schleife läuft weiter, nachfolgende Records werden geschrieben |
| `worker_errors` nach dauerhaftem Fehler | `0` | `6` (5 Schleifendurchläufe + 1 Fehlschlag beim Shutdown-Drain) |
| `health.state` nach Worker-Tod | `ok` | `failed_worker` |
| `health.is_failed()` | `False` | `True` |
| `submit()` nach Worker-Tod | `[True × 5]` | `[False × 5]` |
| Abgewiesene Records erreichen die Queue | ja (5 gestrandet) | nein — Füllstand unverändert; ob diese Ablehnungen zusätzlich zu zählen sind, ist die **offene** Frage aus `DECISION_REQUIRED.md` |
| Bereits eingereihter Record | strandet (queue depth 5) | `dropped_shutdown = 1` |
| Neustartversuch | – | keiner (`live observability thrds: []`) |
| stderr | ungefilterter `threading`-Traceback | ausschließlich `[observability] <code>: <detail>`, ratenbegrenzt (G-2/G-4) |
| Sink bei defektem Store (20 Records) | `sink lines written: 0` | `sink lines written: 20` |
| `logging.retention_pressure` | nur stderr | zusätzlich kanonischer Record (`performance`, `WARNING`, `is_internal`) |
| `db_path` außerhalb `%LOCALAPPDATA%` | akzeptiert | abgelehnt |

## Automatisierte Entsprechung

Dieselben Sachverhalte sind als dauerhafte Tests abgesichert, damit die
Korrektur nicht wieder verloren geht:

```text
tests/test_obs030_worker_fault_injection.py   6 Tests   (B-1, W-7c)
tests/test_obs030_gate_corrections.py        18 Tests   (W-1, W-2, W-4, W-5, W-7a/b)
tests/test_obs030_path_boundaries.py         23 Tests   (B-3)
```

## Grenze dieser Probe

`probe_write()` prüft mit `BEGIN IMMEDIATE` + `COMMIT`. Das erkennt eine
gesperrte, nur lesbare, geschlossene oder nicht geöffnete Datenbank
zuverlässig. Ein reiner `disk full`-Zustand kann von einer leeren
Transaktion nicht in jedem Fall erzwungen werden — für ihn greift jedoch der
eigene Pfad aus `ARCH §8.3` (`_looks_like_disk_full` → `FAILED_STORE`,
Retention ausgesetzt), der von diesem Lauf unverändert bleibt.
