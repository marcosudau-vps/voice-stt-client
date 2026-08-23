"""
Shared fixtures for the OBS-050 apply-chain tests.

Not named ``test_*`` on purpose: this module holds no test cases, and neither
``pytest`` nor ``unittest discover`` should collect it.

The session double's ``reconfigure`` raises. That is the measurement device
for ``LOGGING_CONTRACTS_FREEZE_V1.md`` §10.4's hard rule — *"Nachweis:
apply_runtime_config mit einer Fake-Session, deren reconfigure bei Aufruf
durchfaellt"*: if a pure observability change ever set ``session_changed``,
the apply would reach ``reconfigure`` and fail visibly instead of quietly
reconnecting.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import Any, Optional

from core.config import AppConfig
from core.controller import STTController
from core.history import TranscriptHistoryManager
from core.stt_session import ClientState, SessionState, TransportState


class RecordingIngress:
    """An ``Ingress`` double that records what ``apply_config`` received."""

    def __init__(self, *, raises: bool = False) -> None:
        self.applied: list[Any] = []
        self.events: list[tuple] = []
        self._raises = raises

    def event(self, type, **kwargs):  # noqa: A002
        self.events.append((type, kwargs))

    def submit(self, record):
        return False

    def observe_server_result(self, context, result):
        return None

    def apply_config(self, config):
        self.applied.append(config)
        if self._raises:
            raise RuntimeError("apply_config exploded")


class IngressWithoutApplyConfig(RecordingIngress):
    """A pre-OBS-050 double: everything except ``apply_config``."""

    apply_config = None

    def __getattribute__(self, name):
        if name == "apply_config":
            raise AttributeError(name)
        return super().__getattribute__(name)


class FakeAudio:
    def __init__(self) -> None:
        self.on_audio_packet = None
        self.running = False

    def start(self, *args, **kwargs):
        self.running = True

    def stop(self, *args, **kwargs):
        self.running = False

    @property
    def is_running(self) -> bool:
        return self.running


class FakeSession:
    def __init__(self) -> None:
        self.generation = 1
        self.reconfigure_calls = 0
        self.state = ClientState(
            transport=TransportState.READY,
            ready_ok=True,
            server_status=SessionState.IDLE,
            generation=1,
            session_id="fake-session",
        )

    @property
    def is_ready(self) -> bool:
        return True

    @property
    def is_streaming(self) -> bool:
        return False

    async def reconfigure(self, session_config, server_config):
        self.reconfigure_calls += 1
        raise RuntimeError("reconfigure must not be reached by a logging change")

    async def stop(self) -> None:
        return None

    async def invalidate_connection(self, reason: str = "") -> None:
        return None


class FakeCoordinator:
    def __init__(self) -> None:
        self.on_event = None
        self.on_context_change = None
        self.on_observation = None
        self.config_updates = []

    async def update_config(self, server_config, event_config) -> None:
        self.config_updates.append((server_config, event_config))

    async def shutdown(self) -> None:
        return None


def build_controller(
    *,
    apply_config_raises: bool = False,
    apply_config_missing: bool = False,
    cleanup: Optional[list] = None,
):
    """A controller wired to doubles, with a temporary history database."""
    directory = tempfile.mkdtemp()
    config = AppConfig()
    config.history.persistent.db_path = os.path.join(directory, "history.db")
    history = TranscriptHistoryManager(config.history, db_path=config.history.persistent.db_path)

    ingress: Any
    if apply_config_missing:
        ingress = IngressWithoutApplyConfig()
    else:
        ingress = RecordingIngress(raises=apply_config_raises)

    session = FakeSession()
    controller = STTController(
        config,
        session=session,
        audio=FakeAudio(),
        history_manager=history,
        session_coordinator=FakeCoordinator(),
        observability=ingress,
    )
    if cleanup is not None:
        cleanup.append(lambda: shutil.rmtree(directory, ignore_errors=True))
    return controller, session
