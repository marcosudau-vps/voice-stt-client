# AP04 Korrekturrunde 1 – Walkthrough

> **Datum:** 25. Juli 2026  
> **Projektpfad:** `P:\DockerProjekte\RealtimeSTT_client`

---

## 1. Zurücknahme des unberechtigten Abschlussstatus
- Sämtliche aktiven Dokumente ([task.md](file:///P:/DockerProjekte/RealtimeSTT_client/task.md), [docs/IMPLEMENTATION_ROADMAP.md](file:///P:/DockerProjekte/RealtimeSTT_client/docs/IMPLEMENTATION_ROADMAP.md), [ÜBERGABE.md](file:///P:/DockerProjekte/RealtimeSTT_client/ÜBERGABE.md), [docs/PROJEKTUEBERSICHT.md](file:///P:/DockerProjekte/RealtimeSTT_client/docs/PROJEKTUEBERSICHT.md), [docs/work-packages/AP04_CONTROLLER_INTEGRATION.md](file:///P:/DockerProjekte/RealtimeSTT_client/docs/work-packages/AP04_CONTROLLER_INTEGRATION.md)) wurden zu Beginn der Korrekturrunde explizit auf `[IN ARBEIT – Korrekturrunde 1]` gesetzt.

---

## 2. Behebung der Mängel aus PRUEFBERICHT_00_INITIAL

### A. Thread-Leakage & Test-Hänger behoben (M-01)
- `tests/test_controller.py`: `test_shutdown_raises_queue_stop_timeout_with_fake` verwendet `FakeInjectionQueue` mit `timeout_on_stop = True`. Es wird kein echter OS-Worker-Thread mehr gestartet.
- `tests/test_app.py`: `TestRunLoopBinding` nutzt `FakeInjectionQueue` und verifiziert das geordnete Herunterfahren in `finally`, ohne un-gestoppte realen Worker-Threads zu hinterlassen.
- In allen Testklassen (`BaseControllerTestCase`, `TestAudioThreadBridge`) wurde ein Teardown-Check auf `TextInjectionQueueWorker` hinzugefügt.

### B. E-02 / E-03 History-Ergebnis-API (M-02)
- In [core/history.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/history.py):
  - `HistoryAddStatus` Enum (`NEW`, `ALREADY_EXISTS`, `UNAVAILABLE`) und `HistoryAddResult` dataclass hinzugefügt.
  - `add_entry_with_status()` implementiert. `add_entry()` verwendet diese Methode rückwärtskompatibel.
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py):
  - In `process_raw_final_event` wird `add_entry_with_status` ausgewertet.
  - Pre-existing DB-Einträge (`HistoryAddStatus.ALREADY_EXISTS`) lösen keinen automatischen Enqueue in die Injektions-Queue aus, sondern werden als Duplikat/Konflikt gemeldet.

### C. Reentrant Lock Safety (M-03)
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py):
  - `_emit_final_result` wird aus dem `with self._lock:` Block herausgelöst und ausschließlich außerhalb interner Locks aufgerufen.
  - Test `test_callback_querying_controller_status_does_not_deadlock` bestätigt deadlocksfreies Arbeiten bei Abfragen von `get_status()` / `is_closing` im Callback.

### D. Idempotenter Shutdown (M-04)
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py):
  - `shutdown()` verwendet `self._shutdown_completed` und `self._shutdown_error`.
  - Wiederholte und konkurrierende Shutdown-Aufrufe stoppen jede Komponente (`audio`, `session`, `queue`, `history`) exakt 1-mal.

### E. Semantische Controller-API (M-05)
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py):
  - UI-neutrale Methoden `get_status()`, `start_dictation()`, `stop_dictation()`, `toggle_dictation()` hinzugefügt.
  - `dictation_requested` wird unabhängig vom Transportzustand gehalten.
  - `CommandResult` und `ControllerStatus` Datenklassen bereitgestellt.

### F. Deterministischer Run-Loop (M-06)
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py):
  - Task-Cleanup (`cancel()` & `await`) im `finally`-Block von `run()`.
- In [app.py](file:///P:/DockerProjekte/RealtimeSTT_client/app.py):
  - SIGINT signal handler bricht Tasks im Event Loop geordnet ab, ohne durch `sys.exit(0)` den Shutdown im `finally` abzuschneiden.

---

## 3. Verifikationsbefehle & Ergebnisse

1. **AP1 History Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_history -v` -> 30 Tests OK (0.919s)
2. **AP4 Controller Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_controller -v` -> 27 Tests OK (1.287s)
3. **Headless App Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_app -v` -> 7 Tests OK (0.038s)
4. **AP2 & AP3 Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_text_injector tests.test_reinsertion -v` -> 67 Tests OK (1.811s)
5. **Vollständige Gesamtsuite:**
   `.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"` -> 131 Tests OK (4.104s)
6. **Compile-Prüfung:**
   `.\venv\Scripts\python.exe -m py_compile ...` -> Exit code 0
