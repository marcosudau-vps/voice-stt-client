# Implementation Plan – AP05 Fehlerverhalten und stille Selbstheilung

Implementation plan for **AP05 Fehlerverhalten und stille Selbstheilung** according to `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md` and `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md`.

## User Review Required

> [!IMPORTANT]
> - **Dictation Cancellation on Transport Loss**: Dictations are bound strictly to a single WebSocket session generation. A dropped connection permanently terminates the active dictation and purges pending audio. After reconnection, the client reaches `ready + idle` without resuming dictation or replaying audio.
> - **Immediate Rejection of User Start when Not Ready**: Calling `start_dictation()` when transport is not `READY` immediately returns `success=false` and emits an `action_blocked` event. The request is never queued for auto-execution upon reconnection.
> - **10-Second Start Confirmation Timeout**: `send_start()` waits up to 10 seconds for a server status confirmation (`listening`, `wakeword_wait`, or subsequent active states). If unconfirmed within 10s, dictation fails (`dictation_start_failed`), audio is stopped/purged, and the WS session is closed to avoid ambiguous server states.
> - **Backoff Reset on First Pong**: Connection backoff resets only after receiving the first valid `pong` of the current session, not on `ready` alone.

## Proposed Changes

### Configuration Layer (`core/config.py`, `config.yaml`)

#### [MODIFY] [config.py](file:///p:/DockerProjekte/RealtimeSTT_client/core/config.py)
#### [MODIFY] [config.yaml](file:///p:/DockerProjekte/RealtimeSTT_client/config.yaml)

- Add `start_confirmation_timeout: float = 10.0` and `server_busy_min_delay: float = 10.0` to `ServerConfig`.
- Add range and consistency validation for all `ServerConfig` parameters (`reconnect_min_delay > 0`, `reconnect_max_delay >= reconnect_min_delay`, `reconnect_jitter >= 0 and < 1.0`, `ping_timeout_count >= 1`, `start_confirmation_timeout > 0`, `server_busy_min_delay > 0`).

---

### Transport Layer & Session Management (`core/stt_session.py`)

#### [MODIFY] [stt_session.py](file:///p:/DockerProjekte/RealtimeSTT_client/core/stt_session.py)

- **Session Generation Tracking**: Introduce an internal `_generation: int` counter incremented on each connection attempt. Tag state and events with generation.
- **Ping/Pong Hardening**:
  - Maintain single outstanding ping per connection.
  - Set `ping_started_at` at send time without overwriting prior to evaluation.
  - Increment `consecutive_misses` if ping unanswered by end of interval (no old RTT masking).
  - Reset `consecutive_misses = 0` and compute RTT on matching pong.
  - Trigger connection close/invalidation on `consecutive_misses >= ping_timeout_count` (3).
  - Clear ping state on new generation.
- **Backoff & Reconnect Rules**:
  - Bound exponential backoff delay **inclusive of jitter** to `reconnect_max_delay` (30.0s).
  - Close code 1013 (`server_busy`) uses `server_busy_min_delay` (10.0s).
  - Reset `_backoff_attempt = 0` **only after receiving first valid pong** of current session.
  - Ensure backoff sleep is cancelled immediately during `stop()` / shutdown.

---

### Controller & Dictation Lifecycle (`core/controller.py`)

#### [MODIFY] [controller.py](file:///p:/DockerProjekte/RealtimeSTT_client/core/controller.py)

- **State Snapshots & Event Signals**:
  - Enums/Data Structures: `AvailabilityState` (`starting`, `connecting`, `ready`, `network_unavailable`, `server_busy`, `server_unavailable`, `protocol_error`, `shutting_down`, `stopped`), `DictationState` (`idle`, `starting`, `active`), `TransientEventType` (`action_blocked`, `dictation_start_failed`, `dictation_interrupted`).
  - Dataclass `ControllerStatusSnapshot` for UI-neutral status polling.
  - Callbacks `on_feedback_event` / `on_snapshot_change`.
- **Start Confirmation & Timeout**:
  - `start_dictation()`:
    - If transport not `READY`, reject immediately (`success=false`), emit `action_blocked`, stay `idle`.
    - If `READY` and `idle`: enter `starting`, send `start`, start 10s timer.
    - Confirm on server status `listening`, `wakeword_wait`, or active states (`wakeword_detected`, `voice`, `silence`, `recording`, `transcribing`).
    - On confirmation: enter `active`, enable audio transmission.
    - On 10s timeout: emit `dictation_start_failed`, purge audio, reset to `idle`, close WS session.
- **Transport Disconnect & Dictation Termination**:
  - When connection is lost during `starting` or `active`: emit `dictation_interrupted` exactly once, stop audio capture, purge audio queue, reset dictation to `idle`.
  - Reconnect proceeds in background without auto-resuming dictation.
- **Headless One-Shot Initial Start**:
  - Headless auto-start only occurs once on initial application launch (if configured). After any disconnect/session loss, auto-start never re-triggers.

---

### Headless Application Entry Point (`app.py`)

#### [MODIFY] [app.py](file:///p:/DockerProjekte/RealtimeSTT_client/app.py)

- Only release audio packets to WebSocket when dictation state is `active` and generation matches current session.
- Discard packets from old session generations after disconnect or stop.
- Log UI-neutral feedback events and availability state changes.

---

### Automated Unit Tests (`tests/`)

#### [NEW] [test_stt_session.py](file:///p:/DockerProjekte/RealtimeSTT_client/tests/test_stt_session.py)
#### [NEW] [test_config.py](file:///p:/DockerProjekte/RealtimeSTT_client/tests/test_config.py)
#### [MODIFY] [test_controller.py](file:///p:/DockerProjekte/RealtimeSTT_client/tests/test_controller.py)
#### [MODIFY] [test_app.py](file:///p:/DockerProjekte/RealtimeSTT_client/tests/test_app.py)

- **`test_config.py`**: Test `ServerConfig` validation, `config.yaml` loading, default values, and range checks.
- **`test_stt_session.py`**: Test ping/pong miss calculation without RTT masking, single outstanding ping, backoff capping with jitter, backoff reset on first pong, 1013 server_busy min delay, generation isolation, and shutdown backoff interruption.
- **`test_controller.py`**: Test user start rejection when not ready (`action_blocked`), 10s start confirmation timeout (`dictation_start_failed`), server status confirmation transitions (`listening`/`wakeword_wait` -> `active`), dictation termination on disconnect (`dictation_interrupted`), audio queue purging, no auto-resume after reconnect, and headless initial start limits.
- **`test_app.py`**: Test audio gating by dictation state & session generation.

## Verification Plan

### Automated Tests
Run unit tests with Python 3.12 virtual environment:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_config
.\venv\Scripts\python.exe -m unittest tests.test_stt_session
.\venv\Scripts\python.exe -m unittest tests.test_controller
.\venv\Scripts\python.exe -m unittest tests.test_app
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
.\venv\Scripts\python.exe -m py_compile app.py core\stt_session.py core\controller.py core\audio_capture.py core\config.py
```

Target: All existing 152 tests plus all new AP05 tests pass cleanly (100% green).

### Manual Verification
Validate syntax and configuration defaults. (Live server test optional after automated approval).
