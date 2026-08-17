"""
Canonical logging/observability record model (OBS-010).

Frozen by OBS-000; signature source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §1.
This module is the single data contract between producers, normalizer,
worker, storage, sinks and query providers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from types import MappingProxyType
from typing import Any, Mapping, Optional


class ProducerKind(str, Enum):
    """Closed value set: ``producer_kind``. No other value is valid."""

    CLIENT = "client"
    SERVER = "server"
    LED = "led"
    OTHER = "other"


class Channel(str, Enum):
    """The four canonical channels. Open at runtime: the normalizer passes
    unknown channel values through unchanged (CONTRACTS §2.1)."""

    SYSTEM = "system"
    AUDIT = "audit"
    TRANSCRIPTION = "transcription"
    PERFORMANCE = "performance"


class Level(str, Enum):
    """Closed value set: ``level``. The only closed enum-like field, because
    filtering and prioritisation rely on it."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Scope(str, Enum):
    """Closed value set: ``scope``. Never derivable from ``session_id`` alone;
    see CONTRACTS §1.3 for the complete and binding derivation rule."""

    SESSION = "session"
    INSTANCE = "instance"
    GLOBAL = "global"


class RecordPriority(str, Enum):
    HIGH = "high"
    LOW = "low"


# Original rank for severity/level comparison (CONTRACTS §2.1).
_LEVEL_RANK: dict[str, int] = {
    "DEBUG": 0,
    "INFO": 1,
    "WARNING": 2,
    "ERROR": 3,
    "CRITICAL": 4,
}


def level_rank(level: str) -> int:
    """Rank of a level string; unknown values default to INFO (CONTRACTS §2.1)."""
    return _LEVEL_RANK.get(level, _LEVEL_RANK["INFO"])


def _freeze(value: Any) -> Any:
    """Freeze rich structures into immutable ones (pattern ``event_models._freeze``).

    An already canonical ``MappingProxyType`` is returned by identity (no copy):
    the ingress receives the server payload as an already frozen reference and
    must not copy it (LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.2).
    """
    if isinstance(value, MappingProxyType):
        return value
    if isinstance(value, Mapping):
        return MappingProxyType({str(key): _freeze(item) for key, item in value.items()})
    if isinstance(value, tuple):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, list):
        return tuple(_freeze(item) for item in value)
    if isinstance(value, (set, frozenset)):
        return frozenset(_freeze(item) for item in value)
    return value


def _required_string(value: Any, name: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _optional_string(value: Any, name: str) -> None:
    if value is not None and (not isinstance(value, str) or not value.strip()):
        raise ValueError(f"{name} must be null or a non-empty string")


def _optional_int(value: Any, name: str) -> None:
    if value is not None:
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise ValueError(f"{name} must be null or an integer >= 0")


@dataclass(frozen=True)
class CanonicalLogRecord:
    """The canonical log record (LOGGING_CONTRACTS_FREEZE_V1.md §1.4).

    Field names, nullability, defaults and the ``priority`` property are
    contract. ``details`` and ``raw`` are frozen on construction.
    """

    record_id: str
    received_at: str
    producer_kind: str
    producer_id: str
    instance_id: str
    scope: str
    channel: str
    level: str
    replayed: bool = False
    source_timestamp: Optional[str] = None
    type: Optional[str] = None
    component: Optional[str] = None
    session_id: Optional[str] = None
    generation: Optional[int] = None
    activation_id: Optional[str] = None
    segment_id: Optional[int] = None
    transcription_id: Optional[str] = None
    command_id: Optional[str] = None
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    server_cursor: Optional[int] = None
    message: Optional[str] = None
    details: Mapping[str, Any] = field(default_factory=dict)
    raw: Optional[Mapping[str, Any]] = None
    is_internal: bool = False  # logging-eigene Records (Prioritaet)

    def __post_init__(self) -> None:
        for name in ("record_id", "received_at", "producer_kind", "producer_id",
                     "instance_id", "scope", "channel", "level"):
            _required_string(getattr(self, name), name)
        try:
            ProducerKind(self.producer_kind)
        except ValueError as exc:
            raise ValueError("producer_kind must be one of "
                             f"{[kind.value for kind in ProducerKind]}") from exc
        try:
            Scope(self.scope)
        except ValueError as exc:
            raise ValueError("scope must be one of "
                             f"{[kind.value for kind in Scope]}") from exc
        try:
            Level(self.level)
        except ValueError as exc:
            raise ValueError("level must be one of "
                             f"{[kind.value for kind in Level]}") from exc
        if not isinstance(self.replayed, bool):
            raise ValueError("replayed must be a boolean")
        if not isinstance(self.is_internal, bool):
            raise ValueError("is_internal must be a boolean")
        for name in ("source_timestamp", "type", "component", "session_id",
                     "activation_id", "transcription_id", "command_id",
                     "event_id", "correlation_id", "message"):
            _optional_string(getattr(self, name), name)
        for name in ("generation", "segment_id", "server_cursor"):
            _optional_int(getattr(self, name), name)
        if not isinstance(self.details, Mapping):
            raise ValueError("details must be a mapping")
        if self.raw is not None and not isinstance(self.raw, Mapping):
            raise ValueError("raw must be null or a mapping")
        object.__setattr__(self, "details", _freeze(self.details))
        if self.raw is not None:
            object.__setattr__(self, "raw", _freeze(self.raw))

    @property
    def priority(self) -> RecordPriority:
        """Priority derivation, frozen in CONTRACTS §1.5.

        `HIGH` if internal, or (not replayed and (level >= WARNING or
        channel == audit or type is not None)); otherwise `LOW`.
        """
        if self.is_internal:
            return RecordPriority.HIGH
        if self.replayed:
            return RecordPriority.LOW
        if (
            level_rank(self.level) >= level_rank(Level.WARNING.value)
            or self.channel == Channel.AUDIT.value
            or self.type is not None
        ):
            return RecordPriority.HIGH
        return RecordPriority.LOW