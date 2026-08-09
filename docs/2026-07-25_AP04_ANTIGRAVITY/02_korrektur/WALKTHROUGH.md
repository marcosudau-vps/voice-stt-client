# AP04 Korrekturrunde 2 – Walkthrough

> **Datum:** 25. Juli 2026  
> **Projektpfad:** `P:\DockerProjekte\RealtimeSTT_client`

---

## 1. Zurücknahme des unberechtigten Abschlussstatus
- Sämtliche aktiven Dokumente ([task.md](file:///P:/DockerProjekte/RealtimeSTT_client/task.md), [docs/IMPLEMENTATION_ROADMAP.md](file:///P:/DockerProjekte/RealtimeSTT_client/docs/IMPLEMENTATION_ROADMAP.md), [ÜBERGABE.md](file:///P:/DockerProjekte/RealtimeSTT_client/ÜBERGABE.md), [docs/PROJEKTUEBERSICHT.md](file:///P:/DockerProjekte/RealtimeSTT_client/docs/PROJEKTUEBERSICHT.md), [docs/work-packages/AP04_CONTROLLER_INTEGRATION.md](file:///P:/DockerProjekte/RealtimeSTT_client/docs/work-packages/AP04_CONTROLLER_INTEGRATION.md)) wurden zu Beginn der Korrekturrunde 2 explizit auf `[IN ARBEIT – Korrekturrunde 2]` gesetzt.

---

## 2. Umgesetzte Mängelbehebungen aus PRUEFBERICHT_01_KORREKTUR

### A. Reale Run-Loop-Semantik (`STTController.run()`)
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py): `run()` verwendet eine `monitored_tasks` Schleife. Ein normales Ende von `_auto_start_when_ready()` beendet `run()` **nicht**, sondern wird aus den überwachten Tasks entfernt. `session_task` ist die primäre Treiber-Task. Normales Ende von `session.run()` beendet die Hauptschleife geordnet.
- Task-Erzeugung wurde in den `try:` Block verlegt; Teilstartfehler räumen erzeugte Tasks im `finally` auf.
- Test `test_auto_start_completion_does_not_terminate_run_loop` bestätigt, dass der Controller nach dem Auto-Start-Ende bei offener Session weiterläuft.

### B. Idempotenter konkurrierender Shutdown
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py): `shutdown()` koordiniert parallele Aufrufe über `self._shutdown_task`. Überlappende oder mehrfache Aufrufer teilen sich dieselbe laufende Coroutine.
- Test `test_concurrent_shutdown_calls_stop_components_exactly_once` sichert überlappende Aufrufe ab: Audio-, Session-, Queue- und History-Stoppzähler sind exakt 1.

### C. Atomare Finalidentitäts-Reservierung
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py): `(sessionId, segmentId)` wird DIREKT unter `self._lock` in `_processed_finals` reserviert, bevor der potenziell langsame/blockierende History-Aufruf beginnt.
- Test `test_atomic_reservation_race_prevents_duplicate_history_calls` verifiziert: Ein fehlschlagender/blockierender erster History-Aufruf lässt parallele Serverduplikate nicht erneut in den History- oder Queue-Pfad eintreten (genau 1 History-Aufruf).

### D. Asynchrone ehrliche Diktierbefehle & Audio-Rollback
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py): Diktierbefehle sind `async def start_dictation()`, `stop_dictation()`, `toggle_dictation()`. Sie awaiten `send_start()`/`send_stop()`. Bei einem Fehler in `send_start()` wird Audio-Capture gestoppt (Rollback) und ein Fehlerergebnis zurückgegeben.
- `_auto_start_when_ready()` prüft `dictation_requested`.
- In [app.py](file:///P:/DockerProjekte/RealtimeSTT_client/app.py): `RealtimeSTTClient` setzt initial `_dictation_requested = True` für das Headless-Verhalten.
- Tests in `TestSTTControllerSemanticAPIAsync` decken Erfolg, Fehler-Rollback, `transport_not_ready` und Abbrechen vor `READY` ab.

### E. History Evicted Entries Randfall
- In [core/controller.py](file:///P:/DockerProjekte/RealtimeSTT_client/core/controller.py): Wenn `add_entry_with_status()` `ALREADY_EXISTS` mit `entry=None` liefert (Eintrag aus Memory/DB-Retention limitiert), klassifiziert der Controller dies als `FinalProcessingStatus.DEDUPLICATED` mit `reason="duplicate_entry_evicted"` und veranlasst keinen Enqueue.
- Test `test_evicted_history_duplicate_classified_as_deduplicated` in `tests/test_controller.py` verifiziert das Verhalten.

### F. Vollständige Test-Isolation von Benutzerdaten
- In [app.py](file:///P:/DockerProjekte/RealtimeSTT_client/app.py): `RealtimeSTTClient` akzeptiert DI-Parameter (`session`, `audio`, `history_manager`, `injection_queue`, `reinsertion_service`, `backend`).
- In [tests/test_app.py](file:///P:/DockerProjekte/RealtimeSTT_client/tests/test_app.py): Alle Tests nutzen ein temporäres Verzeichnis / DB-Pfad. Es werden keine Benutzerdaten in `%LOCALAPPDATA%` berührt. `queue` und `reinsertion` teilen sich dieselbe injizierte `history`.

---

## 3. Verifikationsbefehle & Ergebnisse

1. **AP1 History Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_history -v` -> 30 Tests OK (0.927s)
2. **AP4 Controller Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_controller -v` -> 32 Tests OK (1.781s)
3. **Headless App Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_app -v` -> 9 Tests OK (0.225s)
4. **AP2 & AP3 Tests:**
   `.\venv\Scripts\python.exe -m unittest tests.test_text_injector tests.test_reinsertion -v` -> 67 Tests OK (2.125s)
5. **Vollständige Discover-Gesamtsuite:**
   `.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"` -> **138 Tests OK (4.691s)**
6. **Compile-Prüfung:**
   `.\venv\Scripts\python.exe -m py_compile ...` -> **Exit-Code 0**
7. **Dokumentensuchprüfung:**
   `Select-String` auf alte Stale-Phrasen -> **0 Treffer**
