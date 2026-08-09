# AP04 – Korrekturplan (Korrekturrunde 3 – Letzte Runde)

> **Status:** in Umsetzung  
> **Datum:** 25. Juli 2026  
> **Projektpfad:** `P:\DockerProjekte\RealtimeSTT_client`  
> **Bezugs-Prüfbericht:** `docs/2026-07-25_AP04_ANTIGRAVITY/PRUEFBERICHT_02_KORREKTUR.md`

---

## 1. Mängelanalyse & Behebungsstrategie

| Mangel ID | Befund aus PRUEFBERICHT_02_KORREKTUR | Geplante Massnahme |
|---|---|---|
| **M3-01** | Teilweise Task-Erzeugung in `run()` wird bei Fehler des 3. Tasks nicht aufgeräumt. | Schrittweise Aufnahme jeder erzeugten Task in `tasks: List[asyncio.Task]`. Bei Exception in Task-Erzeugung sofort alle erzeugten Tasks canceln und awaiten. |
| **M3-02** | Fehler bei `start_queue()` lässt `_loop` gesetzt. | `self._loop = asyncio.get_running_loop()` und `start_queue()` in das geschützte `try/finally` in `run()` verlegen. `finally` setzt `self._loop = None` garantiert. |
| **M3-03** | Shutdown-Task ist bei Cancellation eines Waiters ungeschützt (`_shutdown_task` wird gecancelt). | `await asyncio.shield(shutdown_task)` in `shutdown()` nutzen. Bricht ein Aufrufer ab, läuft das Cleanup im Hintergrund geschützt weiter. Spätere Aufrufer können dasselbe Cleanup abwarten. |
| **M3-04** | `app.py` SIGINT Handler cancelt pauschal alle tasks auf `_loop` inkl. `_shutdown_task`. | SIGINT-Handler bricht selektiv die Haupt-Run-Task ab oder ruft `client.shutdown()` auf, statt `asyncio.all_tasks()` pauschal zu canceln. |
| **M3-05** | Auto-Start-Fehler wird nach Audio-Rollback verschluckt; `run()` läuft stumm weiter. | `_auto_start_when_ready()` löst nach Audio-Rollback Exception erneut aus. `run()` erkennt Exception und löst geordneten Abbruch aus. |
| **M3-06** | Aufnahmeübergänge nicht serialisiert (Race zwischen Start, Stop, Toggle & Auto-Start). | Gemeinsamen `asyncio.Lock` (`_transition_lock`) für `start_dictation()`, `stop_dictation()`, `toggle_dictation()` und `_auto_start_when_ready()` einführen. Interne `*_locked()` Methoden nutzen. |
| **M3-07** | Fehlende deterministische Testabdeckungen für die neuen Fehlerpfade. | Gezielte Event-gesteuerte Tests in `tests/test_controller.py` ergänzen (Teilstart-Cleanup, Shutdown-Shield-Cancellation, Async-Lock-Race). |
| **M3-08** | Nicht saubere Typimporte in `app.py` (`sys`, `Path` ungenutzt, fehlende Typimporte). | `app.py` Imports bereinigen: `sys`, `Path` entfernen, Typimporte aus `typing` & Core-Modulen ergänzen. |
| **M3-09** | Kanonische Dokumentation nicht durchgehend bereinigt. | Dokumente konsolidieren & exakten `Select-String`-Check ausführen. |
| **M3-10** | History Race Test nutzt `time.sleep()` und `:memory:` SQLite Fehler-Lograuschen. | Test in `test_controller.py` auf `threading.Event` / `Barrier` umstellen und `config.history.persistent.enabled = False` setzen. |

---

## 2. Detaillierte Moduländerungen

### `core/controller.py`
1. **Transition Lock (`asyncio.Lock`):**
   - `_transition_lock: Optional[asyncio.Lock]`
   - `_get_transition_lock() -> asyncio.Lock`
   - `async def start_dictation()`, `async def stop_dictation()`, `async def toggle_dictation()`, `async def _auto_start_when_ready()` nutzen `async with self._get_transition_lock():`.
   - Interne Methoden `_start_dictation_locked()`, `_stop_dictation_locked()`.

2. **Full Exception-Safe `run()` Lifecycle:**
   - `self._loop = asyncio.get_running_loop()`
   - `tasks: List[asyncio.Task] = []`
   - `try`: `start_queue()`, dann einzeln `create_task()` und direkt `tasks.append(...)`.
   - Bei Task-Erzeugungs-Fehler: sofort `cancel()` & `gather()` auf `tasks`, dann `shutdown()`.
   - `monitored_tasks` Schleife. Wenn `auto_start_task` mit Exception endet -> Exception re-raisen, `run()` beenden.
   - `finally`: `self._loop = None` garantiert.

3. **Cancellation-Shielded `shutdown()`:**
   - `await asyncio.shield(shutdown_task)`

### `app.py`
- Import-Bereinigung (`sys` & `Path` entfernen, saubere Annotationstyp-Imports).
- SIGINT-Handler ruft gezielt `run_task.cancel()` / `client.shutdown()` auf.

### `tests/test_controller.py` & `tests/test_app.py`
- Ergänzung aller verlangten Tests für Teilstart-Cleanup, Shutdown-Shield, Async-Transition Races, Auto-Start Exception propagation.
- Bereinigung von `time.sleep()` und `:memory:` SQLite Fehlerlogs.
