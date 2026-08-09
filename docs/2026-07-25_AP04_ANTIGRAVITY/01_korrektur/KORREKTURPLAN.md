# AP04 – Korrekturplan (Korrekturrunde 1)

> **Status:** in Umsetzung  
> **Datum:** 25. Juli 2026  
> **Projektpfad:** `P:\DockerProjekte\RealtimeSTT_client`  
> **Bezugs-Prüfbericht:** `docs/2026-07-25_AP04_ANTIGRAVITY/PRUEFBERICHT_00_INITIAL.md`

---

## 1. Übersicht der zu behebenden Mängel

| ID | Befund aus PRUEFBERICHT_00_INITIAL | Geplante Massnahme |
|---|---|---|
| M-01 | Tests hängen (`test_shutdown_raises_queue_stop_timeout`, `tests.test_app` Run-Loop) wegen leistender Worker-Threads | Fakes/Mocks für Worker und Komponenten in Tests nutzen. Keine echten Worker unkontrolliert abklemmen. Teardown-Checks sicherstellen. |
| M-02 | Pre-existing History-Einträge (z.B. aus SQLite DB) werden fälschlicherweise erneut enqueued | Extension in `TranscriptHistoryManager`: `add_entry_with_status()` liefert `HistoryAddResult(entry, status)`. Nur `NEW` wird automatisch enqueued. `ALREADY_EXISTS` meldet Duplikat/Konflikt ohne Enqueue. |
| M-03 | Reentrant Deadlock beim Aufruf von `is_closing` / Controller-Status aus `on_final_result` Callbacks | Callbacks niemals unter gehaltenem `self._lock` ausführen. Callbacks vor Aufruf aus dem Lock extrahieren. |
| M-04 | `shutdown()` führt doppelte Stopps aus (`DOUBLE_SHUTDOWN_COUNTS 2 2 2`) | Exakte 1-Mal-Stopp-Garantie in `shutdown()`. Atomic Flag & Result-Caching für wiederholte/konkurrierende Shutdowns. |
| M-05 | Semantische Controller-API fehlt (`start_dictation`, `stop_dictation`, `toggle_dictation`, `get_status`) | UI-neutrale Methoden & Status-Ergebnisklassen (`ControllerStatus`, `CommandResult`) implementieren. `dictation_requested` getrennt verwalten. |
| M-06 | Run-Loop `run()` ist nicht deterministisch/robust und cancelt Background-Tasks nicht sauber im `finally` | Task-Cleanup (`cancel()` & `await`) im `finally`. Normales Ende von `session.run()` cancelt Rest-Tasks. Loop `_loop` immer zurücksetzen. |
| M-07 | Fehlende Testabdeckungen (parallele Doppel-Finals, Pre-existing DB Duplikate, Thread-Cleanup, App-Fake-Lifecycle) | Gezielte deterministische Tests in `tests/test_controller.py` und `tests/test_history.py` hinzufügen. |
| M-08 | Voreiliger Abschlussstatus in Projektdokumenten | Dokumente auf `[IN ARBEIT]` zurückgesetzt. Erst nach voller grüner Suite aktualisieren. |

---

## 2. Technische Umsetzung im Detail

### A. `core/history.py` (E-02 / E-03)
- Hinzufügen von `HistoryAddStatus` (`NEW`, `ALREADY_EXISTS`, `UNAVAILABLE`).
- Hinzufügen von `HistoryAddResult(entry: Optional[HistoryEntry], status: HistoryAddStatus)`.
- Implementieren von `add_entry_with_status(session_id, segment_id, text, timestamp=None) -> HistoryAddResult`.
- Bestehendes `add_entry(...)` ruft intern `add_entry_with_status` auf und gibt `result.entry` zurück (100% rückwärtskompatibel).

### B. `core/controller.py`
1. **Deduplizierung & Pre-existing Entry Check:**
   - In `process_raw_final_event`:
     - Erst controller-lokalen `_processed_finals` Index prüfen.
     - Dann `self.history.add_entry_with_status(...)` aufrufen.
     - Wenn `status == HistoryAddStatus.ALREADY_EXISTS`: Identischen Text -> `DEDUPLICATED` (`is_conflict=False`), abweichenden Text -> `DEDUPLICATED` (`is_conflict=True`). Keinen zweiten Enqueue auslösen!
     - Nur wenn `status == HistoryAddStatus.NEW`: Injektions-Queue Enqueue ausführen.
2. **Lock-Safety & Callbacks:**
   - Alle Event-Callbacks (`_emit_final_result`, `_handle_transport_change`, etc.) werden AUSSERHALB von `self._lock` aufgerufen.
3. **Shutdown-Idempotenz & 1-Mal-Stop-Garantie:**
   - Thread-sicheres atomic Guarding: `_shutdown_completed`, `_shutdown_error`.
   - Jede Komponente (`audio`, `session`, `queue`, `history`) wird exakt einmal gestoppt.
4. **Semantische Diktier-API & Status:**
   - `get_status() -> ControllerStatus`
   - `start_dictation() -> CommandResult`
   - `stop_dictation() -> CommandResult`
   - `toggle_dictation() -> CommandResult`
5. **Run-Loop Task-Cleanup in `run()`:**
   - Alle erzeugten Tasks (`session_task`, `audio_sender_task`, `auto_start_task`) im `finally`-Block sauber canceln und awaiten.
   - Normales Beenden von `session_task` bricht die Hilfstasks ab und beendet `run()` geordnet.

### C. `app.py`
- SIGINT-Handler scheduling über event loop clean task cancellation statt direktem `sys.exit(0)`.

### D. `tests/test_controller.py` & `tests/test_app.py`
- Reale `TextInjectionQueue` Worker Threads in Lifecycle-/Run-Loop-Tests durch kontrollierte Fake-Queues / Backends ersetzen.
- Echte Worker threads in Teardown kontrolliert verifizieren (`threading.enumerate()`).
- Deadlock-Test (Callback fragt `is_closing` / `get_status()` ab).
- Barrier-Test (2 parallele Doppel-Finals).
- Pre-existing DB Duplikat-Test.

---

## 3. Verifikationsplan

1. `.\venv\Scripts\python.exe -m unittest tests.test_history -v`
2. `.\venv\Scripts\python.exe -m unittest tests.test_controller -v`
3. `.\venv\Scripts\python.exe -m unittest tests.test_app -v`
4. `.\venv\Scripts\python.exe -m unittest tests.test_text_injector tests.test_reinsertion`
5. `.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"`
6. `py_compile` auf all Python target files.
