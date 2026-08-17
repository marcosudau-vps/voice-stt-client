"""
Client observation entry-point contract and concrete ingress (OBS-010/OBS-020).

Signature source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §6. OBS-010 froze the
``Ingress`` protocol; OBS-020 adds the concrete, thread-safe
``ObservabilityIngress`` plus the behaviorally-equivalent ``NullIngress``
no-op and its module constant ``NULL_INGRESS``.

``submit`` is the non-blocking, non-throwing boundary every producer thread
crosses (ARCH §5, §6.3): order is Health ``FAILED``? -> enabled/level? ->
watermark rule (ARCH §7.1/§7.2) -> ``put_nowait``.
"""

from __future__ import annotations

import queue
from typing import Any, List, Mapping, Optional, Protocol

from .health import LoggingInternalHealth
from .models import CanonicalLogRecord, RecordPriority, level_rank
from .normalizer import from_client_event, from_server_result


class Ingress(Protocol):
    """The structured client observation API. Exactly one call per call site."""

    def event(
        self,
        type: str,
        *,
        channel: str,
        level: str = "INFO",
        component: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        session_id: Optional[str] = None,
        generation: Optional[int] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[int] = None,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        transcription_id: Optional[str] = None,
    ) -> None: ...


DEFAULT_QUEUE_SIZE = 8192
WATERMARK_RATIO = 0.75


class ObservabilityIngress:
    """Thread-safe ingress boundary in front of **one** bounded ``queue.Queue``
    (ARCH §7.1). ``submit`` never blocks and never raises."""

    def __init__(
        self,
        *,
        instance_id: str,
        enabled: bool = True,
        level: str = "INFO",
        queue_size: int = DEFAULT_QUEUE_SIZE,
        watermark_ratio: float = WATERMARK_RATIO,
        store_raw_payload: bool = True,
        store_transcription_content: bool = False,
        user_profile: Any = None,
        health: Optional[LoggingInternalHealth] = None,
    ) -> None:
        self._instance_id = instance_id
        self._enabled = enabled
        self._level = level if isinstance(level, str) and level else "INFO"
        self._queue: "queue.Queue[CanonicalLogRecord]" = queue.Queue(maxsize=max(1, queue_size))
        self._watermark = max(0, int(max(1, queue_size) * watermark_ratio))
        self._store_raw_payload = store_raw_payload
        self._store_transcription_content = store_transcription_content
        self._user_profile = user_profile
        self.health = health if health is not None else LoggingInternalHealth()

    # -- read-only config, used by the future normalizer callable
    # (core/logging_setup.py) so nothing besides ``ingress``/``level`` needs
    # to be invented on the future ``observability`` composition root.

    @property
    def instance_id(self) -> str:
        return self._instance_id

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def level(self) -> str:
        return self._level

    @property
    def store_transcription_content(self) -> bool:
        return self._store_transcription_content

    @property
    def user_profile(self) -> Any:
        return self._user_profile

    def qsize(self) -> int:
        return self._queue.qsize()

    def submit(self, record: Any) -> bool:
        """Thread-safe. Never blocks, never raises.

        ``False`` = not accepted (disabled, filtered, dropped).
        """
        if not isinstance(record, CanonicalLogRecord):
            return False
        if self.health.is_failed():
            return False
        if not self._enabled:
            return False
        if level_rank(record.level) < level_rank(self._level):
            return False
        if self._queue.qsize() >= self._watermark and record.priority is not RecordPriority.HIGH:
            self.health.record_dropped_watermark()
            return False
        try:
            self._queue.put_nowait(record)
        except queue.Full:
            self.health.record_dropped_queue_full()
            return False
        self.health.record_enqueued()
        return True

    def observe_server_result(self, context: Any, result: Any) -> None:
        """The fan-out entry point of the future ``ServerLiveAdapter`` (OBS-040)."""
        if not self._enabled:
            return
        try:
            record = from_server_result(
                context,
                result,
                client_instance_id=self._instance_id,
                store_raw_payload=self._store_raw_payload,
                store_transcription_content=self._store_transcription_content,
                user_profile=self._user_profile,
            )
        except Exception:  # noqa: BLE001 - the ingress boundary never raises
            self.health.record_malformed()
            return
        if record is None:
            return
        self.submit(record)

    def event(
        self,
        type: str,
        *,
        channel: str,
        level: str = "INFO",
        component: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        session_id: Optional[str] = None,
        generation: Optional[int] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[int] = None,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        transcription_id: Optional[str] = None,
    ) -> None:
        """The structured client observation API. Exactly one call per call site."""
        if not self._enabled:
            return
        try:
            record = from_client_event(
                type,
                channel=channel,
                level=level,
                component=component,
                message=message,
                details=details,
                instance_id=self._instance_id,
                store_transcription_content=self._store_transcription_content,
                user_profile=self._user_profile,
                session_id=session_id,
                generation=generation,
                activation_id=activation_id,
                segment_id=segment_id,
                command_id=command_id,
                correlation_id=correlation_id,
                transcription_id=transcription_id,
            )
        except Exception:  # noqa: BLE001 - the ingress boundary never raises
            self.health.record_malformed()
            return
        if record is None:
            return
        self.submit(record)

    def drain(self, max_items: int, timeout: float) -> List[CanonicalLogRecord]:
        """Only for the future worker (OBS-030)."""
        items: List[CanonicalLogRecord] = []
        if max_items <= 0:
            return items
        try:
            items.append(self._queue.get(timeout=max(0.0, timeout)))
        except queue.Empty:
            return items
        while len(items) < max_items:
            try:
                items.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return items


class NullIngress(ObservabilityIngress):
    """Behaviorally equivalent no-op (CONTRACTS §6)."""

    def __init__(self) -> None:
        super().__init__(instance_id="null", enabled=False, level="INFO", queue_size=1)

    def submit(self, record: Any) -> bool:  # noqa: D401
        return False

    def observe_server_result(self, context: Any, result: Any) -> None:
        return None

    def event(
        self,
        type: str,
        *,
        channel: str,
        level: str = "INFO",
        component: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        session_id: Optional[str] = None,
        generation: Optional[int] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[int] = None,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        transcription_id: Optional[str] = None,
    ) -> None:
        return None

    def drain(self, max_items: int, timeout: float) -> List[CanonicalLogRecord]:
        return []


NULL_INGRESS = NullIngress()