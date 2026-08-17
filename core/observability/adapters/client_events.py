"""
``ClientEventEmitter`` — the structured client observation call-site boundary
(OBS-040).

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §5.1 (this module and its
class name are part of the frozen module structure), §5.2 (adapters know
``ingress`` + ``normalizer``, never the other way round),
``LOGGING_CONTRACTS_FREEZE_V1.md`` §6 (the ``event`` signature) and §12 (the
binding hook list).

Why a wrapper at all, when ``ObservabilityIngress.event`` already never
raises: the *injected* object is typed as an ``Ingress`` and a product call
site must stay correct for **any** implementation of it, including a test
double or a future adapter. O-01/O-05 require that a logging failure never
reach the client function, so exactly one ``try/except Exception`` sits
between every hook and the ingress. ``BaseException`` is never caught here
(ARCH §7.3): ``asyncio.CancelledError`` has to keep travelling.

The emitter carries **no** state beyond the ingress and the component name.
It queries no runtime state, holds no reference to session, controller or
coordinator (FD-R8), and never returns a value a caller could branch on.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional


class ClientEventEmitter:
    """One structured-observation boundary per call site owner.

    ``component`` is the default ``component`` field for every event this
    emitter produces; an individual call may override it.
    """

    __slots__ = ("_ingress", "_component")

    def __init__(self, ingress: Any, *, component: Optional[str] = None) -> None:
        self._ingress = ingress
        self._component = component

    @property
    def ingress(self) -> Any:
        return self._ingress

    def emit(
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
        """Emit one structured client observation. Never raises, never blocks,
        returns nothing (O-01: no return value may steer a client path)."""
        try:
            self._ingress.event(
                type,
                channel=channel,
                level=level,
                component=component if component is not None else self._component,
                message=message,
                details=details,
                session_id=session_id,
                generation=generation,
                activation_id=activation_id,
                segment_id=segment_id,
                command_id=command_id,
                correlation_id=correlation_id,
                transcription_id=transcription_id,
            )
        except Exception:  # noqa: BLE001 - O-05: the logging domain stops here
            pass

    # -- convenience wrappers, one per channel (CONTRACTS §2.2) -----------
    #
    # They exist so a call site names the channel by intent rather than by
    # string, and so the four channels stay the closed set §2.2 describes.

    def system(self, type: str, **kwargs: Any) -> None:
        self.emit(type, channel="system", **kwargs)

    def audit(self, type: str, **kwargs: Any) -> None:
        self.emit(type, channel="audit", **kwargs)

    def transcription(self, type: str, **kwargs: Any) -> None:
        self.emit(type, channel="transcription", **kwargs)

    def performance(self, type: str, **kwargs: Any) -> None:
        self.emit(type, channel="performance", **kwargs)


__all__ = ["ClientEventEmitter"]
