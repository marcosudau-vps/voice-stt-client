# AP04 – Implementation Plan: Controller Integration

> **Status:** Initial Plan  
> **Date:** 2026-07-25  
> **Scope:** AP04 Controller Integration  

---

## 1. Goal & Architecture Overview

The objective of AP04 is to introduce a UI-neutral, central controller component (`core/controller.py`) that manages the lifecycle and event wiring of:
- `STTSession` (WebSocket communications and protocol handling)
- `AudioCapture` (Microphone recording and chunking)
- `TranscriptHistoryManager` (AP1 transcript history and deduplication)
- `TextInjectionQueue` (AP2 Win32 clipboard/SendInput injection worker)
- `TranscriptReinsertionService` (AP3 re-injection service)

The controller orchestrates the end-to-end flow for incoming raw server events:
```text
raw "final" event
  → identity validation (sessionId, segmentId, non-empty text)
  → logical atomic deduplication per (sessionId, segmentId)
  → HistoryEntry resolution / creation in TranscriptHistoryManager
  → automatic enqueue into TextInjectionQueue
  → serialized paste execution via worker thread
  → single InjectionAttempt recorded on the same HistoryEntry
```

---

## 2. Key Design Decisions & Guarantees (E-01 to E-04)

- **E-01 (History-before-enqueue):** Every raw final transcript must be resolved/created as a stable `HistoryEntry` in `TranscriptHistoryManager` prior to any automatic enqueue. If history is unavailable or disabled, no automatic paste is attempted.
- **E-02 (History Error Handling):** The controller explicitly distinguishes between "entry created/resolved", "duplicate", and "history unavailable".
- **E-03 (Authoritative Final Identity):** `on_event` with raw `type == "final"` is the sole authoritative trigger for automatic history insertion and text injection. `realtime`, `on_text`, and timeline `final_transcript` events will NOT create history entries or trigger automatic enqueue. Deduplication is strictly `(sessionId, segmentId)` based. Identical and contradictory duplicates do not trigger a second automatic queue job.
- **E-04 (Hotkey Isolation):** No hotkeys, PySide6, or key-combination schemas are implemented in AP04; all controller interactions are programmatic and UI-neutral.

---

## 3. Affected Components & Interfaces

1. **`core/controller.py` (New File)**
   - Defines `STTController`, `FinalProcessingStatus`, and `FinalProcessingResult`.
   - Manages lifecycle (`start_queue()`, `run()`, `shutdown()`).
   - Implements raw event router (`handle_server_event`) and deduplicating final processor (`process_raw_final_event`).
   - Forwards reinsertion requests to `TranscriptReinsertionService`.

2. **`app.py` (Modified)**
   - Re-wires `RealtimeSTTClient` to extend/use `STTController` directly as its core engine.
   - Retains all 7 audio-bridge regression mechanisms and console formatting.

3. **`tests/test_controller.py` (New File)**
   - Comprehensive test suite covering lifecycle, deduplication, error branches, reinsertion, and component isolation.

4. **`tests/test_app.py` (Maintained)**
   - All existing 7 tests must pass without modification or regression.

---

## 4. Test Strategy & Baseline Verification

- **Baseline:** Ran `.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"` on 2026-07-25 -> **103 tests OK** (2.69s).
- **Target Test Suite (`tests/test_controller.py`):**
  - Component wiring & lifecycle (start order, idempotent shutdown, stop timeout handling).
  - Identity validation & deduplication (identical vs. conflicting duplicates, session scoping, invalid fields).
  - Exclusion of non-final events (`realtime`, timeline, `on_text`).
  - Error Pfade (history unavailable, queue stopped/rejecting, enqueue exceptions).
  - Reinsertion integration without duplicate `HistoryEntry` creation.
- **Verification Commands:**
  - `.\venv\Scripts\python.exe -m unittest tests.test_controller -v`
  - `.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"`
  - `py_compile` checks for `app.py`, `core/*.py`, and `tests/*.py`.

---

## 5. Execution Steps

1. Create `core/controller.py` with `STTController` implementation.
2. Update `app.py` to use `STTController`.
3. Create `tests/test_controller.py` with extensive unit and integration tests.
4. Execute unit test suite and verify all baseline + new tests pass.
5. Create `WALKTHROUGH.md` documenting execution and verification details.
6. Synchronize project documentation (`docs/work-packages/AP04_CONTROLLER_INTEGRATION.md`, `task.md`, `docs/IMPLEMENTATION_ROADMAP.md`, `ÜBERGABE.md`, `docs/PROJEKTUEBERSICHT.md`).
7. Write `ABSCHLUSSBERICHT.md` and report outcome.
