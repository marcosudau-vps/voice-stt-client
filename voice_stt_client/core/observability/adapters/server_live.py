"""
``ServerLiveAdapter`` — the passive consumer of the server event fan-out
(OBS-040).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5.1 (module and class
name), §5.2 (import direction), §7.1 (hook location and form), §7.3 (two
levels of error handling), §8.2 (``raw`` is neither copied nor serialised
here), ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.2 (the field mapping this
delegates to), §6 (``observe_server_result`` is the fan-out entry point),
§7.4 (the forbidden hook locations this one deliberately avoids).

Why the adapter and not ``observability.observe_server_result`` directly:
``ARCH §7.3`` fixes **two** error levels and assigns the first one to this
class — *"ServerLiveAdapter.observe() faengt SELBST und meldet an
LoggingInternalHealth. Dort entsteht die Sichtbarkeit."* The empty
``except Exception`` inside ``DualSessionCoordinator._notify_observer`` is
explicitly only the *last* line of defence. Without this class the visible,
counted level would not exist at all.

The adapter is **passive** in the strict sense of O-01/O-02: ``observe``
returns ``None``, so no return value can reach the cursor-commit decision in
``EventStreamTransport._dispatch``, and it swallows every ``Exception`` so a
throwing observer can never make the dispatch call ``reject_event(result)``.
``BaseException`` is not caught (``asyncio.CancelledError`` carries the
cancellation of the event-stream task).
"""

from __future__ import annotations

from typing import Any

from ..health import LoggingInternalHealth


class ServerLiveAdapter:
    """Installed as ``DualSessionCoordinator.on_observation``.

    Callable with the frozen hook signature
    ``(SessionContext, EventProtocolResult) -> None`` (ARCH §7.1).
    """

    __slots__ = ("_ingress",)

    def __init__(self, ingress: Any) -> None:
        self._ingress = ingress

    @property
    def ingress(self) -> Any:
        return self._ingress

    def observe(self, context: Any, result: Any) -> None:
        """Hand one successfully validated protocol result to the ingress.

        Everything the record needs is already present: ``result`` carries
        envelope, frozen raw payload, cursor, replay origin and the duplicate
        flag; ``context`` carries ``generation``/``session_id``. Nothing is
        read from ``context.log_access`` — the session log token is never
        looked at (ARCH §10.1).
        """
        try:
            self._ingress.observe_server_result(context, result)
        except Exception as exc:  # noqa: BLE001 - ARCH §7.3, level 1
            self._report(exc)

    # The coordinator stores a plain callable; being callable keeps the frozen
    # hook type ``Callable[[SessionContext, EventProtocolResult], None]`` exact.
    __call__ = observe

    def _report(self, exc: BaseException) -> None:
        """ARCH §8.3, row *"Normalizer-Ausnahme"*: the record is dropped,
        ``malformed++``, Health stays ``OK``, and **one** substitute record
        ``logging.record_rejected`` carries component and exception type —
        never the original data."""
        health = getattr(self._ingress, "health", None)
        if isinstance(health, LoggingInternalHealth):
            try:
                health.record_malformed()
            except Exception:  # noqa: BLE001
                pass
        reject = getattr(self._ingress, "emit_record_rejected", None)
        if reject is None:
            return
        try:
            reject("observability.adapters.server_live", exc)
        except Exception:  # noqa: BLE001 - the error path itself never raises
            pass


__all__ = ["ServerLiveAdapter"]
