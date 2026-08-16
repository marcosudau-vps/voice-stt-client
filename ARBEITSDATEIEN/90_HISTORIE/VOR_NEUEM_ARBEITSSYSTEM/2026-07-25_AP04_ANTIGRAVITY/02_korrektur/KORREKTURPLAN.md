# AP04 – Korrekturplan (Korrekturrunde 2)

> **Status:** in Umsetzung  
> **Datum:** 25. Juli 2026  
> **Projektpfad:** `P:\DockerProjekte\RealtimeSTT_client`  
> **Bezugs-Prüfbericht:** `docs/2026-07-25_AP04_ANTIGRAVITY/PRUEFBERICHT_01_KORREKTUR.md`

---

## 1. Mängelanalyse & Behebungsstrategie

| Mangel ID | Befund aus PRUEFBERICHT_01_KORREKTUR | Geplante Massnahme |
| --- | --- | --- |
| **M2-01** | `STTController.run()` beendet sich ~200ms nach Autostart, weil `_auto_start_when_ready()` als `FIRST_COMPLETED` gilt. | In `run()`: Wenn `_auto_start_when_ready()` normal endet, wird es aus der überwachten Taskmenge entfernt. `run()` läuft weiter, solange `session_task` aktiv ist. |
| **M2-02** | Konkurrierende `shutdown()`-Aufrufe führen Stopps doppelt aus (`CONCURRENT_SHUTDOWN_COUNTS 2 2 2`). | Thread-/Loop-sicheres Future/Event-Locking für `shutdown()`. Alle Aufrufer teilen sich dieselbe laufende Shutdown-Coroutine. Zähler bleiben exakt 1. |
| **M2-03** | `(sessionId, segmentId)` wird nicht atomar vor dem History-Aufruf reserviert; Race-Condition bei fehlschlagendem/blockierendem ersten History-Aufruf. | `_processed_finals[key] = clean_text` wird DIREKT unter `self._lock` reserviert, bevor `add_entry_with_status` aufgerufen wird. |
| **M2-04** | Diktierbefehle sind synchron / fire-and-forget; melden `success=True` vor asynchronem Fehler; Audio wird bei Fehler nicht zurückgerollt. | Diktierbefehle als coroutines (`async def start_dictation()`, `stop_dictation()`, `toggle_dictation()`) umstellen. Awaiten `send_start`/`send_stop`. Bei `send_start`-Fehler: Audio stoppen & Fehler-Resultat liefern. `_auto_start_when_ready` prüft `dictation_requested`. Headless `RealtimeSTTClient` setzt initialen Diktierwunsch. |
| **M2-05** | History-Randfall (`ALREADY_EXISTS` mit `entry=None`) wird fälschlicherweise als `history_unavailable` klassifiziert. | In `process_raw_final_event`: Wenn `status == ALREADY_EXISTS` und `entry is None`, als `FinalProcessingStatus.DEDUPLICATED` mit `reason="duplicate_entry_evicted"` behandeln. Kein Enqueue. |
| **M2-06** | `tests/test_app.py` greift auf echte Benutzerdaten (`%LOCALAPPDATA%`) zu und ist nicht isoliert. | `RealtimeSTTClient` Konstruktor um DI-Parameter (`session`, `audio`, `history_manager`, `injection_queue`, `reinsertion_service`, `backend`) erweitern. `tests/test_app.py` isolieren. |
| **M2-07** | Dokumentationswidersprüche bezüglich Testzahlen und Paketstatus. | Dokumente auf `[IN ARBEIT]` halten und am Ende mit `rg` auf alte Vor-AP4 Phrasen prüfen. |

---

## 2. Detaillierte Moduländerungen

### `core/controller.py`
1. **Diktierbefehle (`async def`):**
   - `async def start_dictation() -> CommandResult`
   - `async def stop_dictation() -> CommandResult`
   - `async def toggle_dictation() -> CommandResult`
   - Bei `start_dictation`: `self._dictation_requested = True`. Wenn `session.is_ready`: `audio.start()`, `await session.send_start()`. Wenn Exception: `audio.stop()`, return `CommandResult(success=False, status="error", message=str(e))`.
   - Bei `stop_dictation`: `self._dictation_requested = False`. `audio.stop()`. Wenn `session.is_ready`: `await session.send_stop()`.
   - `_auto_start_when_ready()` wartet in Loop, prüft `if not self.dictation_requested: continue`, `if session.is_ready and not session.is_streaming: audio.start(); await session.send_start()`.

2. **Konkurrierender Shutdown:**
   - Erzeugen einer gemeinsamen Task `self._shutdown_task: Optional[asyncio.Task] = None` unter Lock.
   - Wenn ein Aufruf `shutdown()` betritt und bereits ein `_shutdown_task` läuft, wird `await _shutdown_task` ausgeführt.

3. **Atomare Reservierung & History Evicted Handling:**
   - In `process_raw_final_event()`:
     - Unter `with self._lock:`: Wenn `key in self._processed_finals` -> sofort Duplikat zurückgeben. Sonst `self._processed_finals[key] = clean_text` **sofort reservieren**!
     - Nach Lock-Freigabe `self.history.add_entry_with_status(...)` aufrufen.
     - Wenn `ALREADY_EXISTS` & `entry is None` -> `DEDUPLICATED` (`reason="duplicate_entry_evicted"`).
     - Wenn `NEW` -> `self.queue.enqueue(entry)`.

4. **Run-Loop Semantik (`run()`):**
   - Main Loop wartet primär auf `session_task`.
   - `_auto_start_when_ready` wird bei normalem Abschluss aus der überwachten Liste entfernt und beendet `run()` nicht.

### `app.py`
- `RealtimeSTTClient.__init__` akzeptiert DI-Parameter (`session`, `audio`, `history_manager`, `injection_queue`, `reinsertion_service`, `backend`).
- Setzt `self._dictation_requested = True` initial im Headless-Betrieb.

---

## 3. Verifikationsplan

1. `.\venv\Scripts\python.exe -m unittest tests.test_history -v`
2. `.\venv\Scripts\python.exe -m unittest tests.test_controller -v`
3. `.\venv\Scripts\python.exe -m unittest tests.test_app -v`
4. `.\venv\Scripts\python.exe -m unittest tests.test_text_injector tests.test_reinsertion`
5. `.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"`
6. `py_compile` Befehl
7. `rg` Suchprüfung auf verbliebene alte Phrasen.
