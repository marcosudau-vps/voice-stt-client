"""
Query contracts (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §8. These are the only
abstractions the UI knows; no provider may be reached through storage or
transport details (O-10, O-14).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Optional, Protocol, Tuple


class ProviderState(str, Enum):
    AVAILABLE = "available"
    AUTH_REQUIRED = "auth_required"  # von V1 nie erzeugt, aber gueltig
    UNAVAILABLE = "unavailable"
    ERROR = "error"


@dataclass(frozen=True)
class ProviderStatus:
    provider_id: str
    display_name: str
    state: ProviderState
    detail: str = ""  # kurz, redigiert, fuer die Statuszeile
    # ProviderCapabilities: in V1 NICHT vorhanden (YAGNI), additiv
    # nachruestbar, weil dies eine frozen dataclass mit Defaults ist.


@dataclass(frozen=True)
class QueryFilter:
    """Rein deklarativ. Kein Provider darf sie veraendern."""

    producer_kinds: Tuple[str, ...] = ()
    producer_ids: Tuple[str, ...] = ()
    instance_ids: Tuple[str, ...] = ()
    channels: Tuple[str, ...] = ()
    levels: Tuple[str, ...] = ()
    types: Tuple[str, ...] = ()
    type_prefix: Optional[str] = None
    components: Tuple[str, ...] = ()
    scopes: Tuple[str, ...] = ()

    session_id: Optional[str] = None
    generation: Optional[int] = None
    activation_id: Optional[str] = None
    segment_id: Optional[int] = None
    command_id: Optional[str] = None
    correlation_id: Optional[str] = None
    transcription_id: Optional[str] = None
    event_id: Optional[str] = None

    since: Optional[str] = None  # ISO-8601 UTC, inklusive
    until: Optional[str] = None  # ISO-8601 UTC, exklusive
    text: Optional[str] = None  # Freitext ueber message/type/component

    include_replayed: bool = True
    newest_first: bool = True
    # ``None`` preserves the original storage-sequence ordering.  The log UI
    # sets one of the whitelisted record fields so a paginated history is
    # sorted by SQLite rather than merely reordering the currently loaded
    # page.  ``newest_first`` remains the direction of the storage-sequence
    # tail used by live mode.
    sort_by: Optional[str] = None
    sort_descending: Optional[bool] = None


@dataclass(frozen=True)
class QueryFacets:
    """Values which still have at least one hit under the other filters.

    Counts are intentionally not exposed: the UI only needs availability,
    while keeping the query small and free from an expensive global count.
    """

    producer_kinds: Tuple[str, ...] = ()
    channels: Tuple[str, ...] = ()
    levels: Tuple[str, ...] = ()
    types: Tuple[str, ...] = ()


@dataclass(frozen=True)
class LogRecordView:
    """Was die UI sieht. Bewusst NICHT das Speichermodell."""

    provider_id: str
    record_id: str
    received_at: str
    source_timestamp: Optional[str]
    producer_kind: str
    producer_id: str
    instance_id: str
    scope: str
    channel: str
    level: str
    type: Optional[str]
    component: Optional[str]
    session_id: Optional[str]
    generation: Optional[int]
    activation_id: Optional[str]
    segment_id: Optional[int]
    transcription_id: Optional[str]
    command_id: Optional[str]
    event_id: Optional[str]
    correlation_id: Optional[str]
    server_cursor: Optional[int]
    replayed: bool
    message: Optional[str]
    details: Mapping[str, Any] = field(default_factory=dict)
    raw: Optional[Mapping[str, Any]] = None
    cursor: str = ""  # OPAKER Paginierungsschluessel DIESES Records


@dataclass(frozen=True)
class QueryPage:
    provider_id: str
    records: Tuple[LogRecordView, ...]
    next_cursor: Optional[str]  # None = keine weitere Seite
    complete: bool  # False, wenn der Provider abgeschnitten hat
    status: ProviderStatus
    # High-water mark of the filtered storage sequence.  Mixed mode uses it
    # to start tailing after the history snapshot without depending on the
    # active (possibly non-time) table sort.
    tail_cursor: Optional[str] = None


class LogProvider(Protocol):
    """Read-only provider boundary used by the diagnostics UI."""

    @property
    def provider_id(self) -> str: ...

    def status(self) -> ProviderStatus:
        """Muss OHNE Netz- oder DB-Zugriff antworten koennen (gecacht)."""
        ...

    def query(
        self,
        filter: QueryFilter,
        cursor: Optional[str] = None,
        limit: int = 200,
    ) -> QueryPage:
        """Blockierend, auf einem Worker-Thread gerufen. Wirft NIE; Fehler
        kommen als ``QueryPage`` mit ``status.state == ERROR`` und leeren
        records zurueck."""
        ...

    def fetch_raw(self, record_id: str) -> Optional[Mapping[str, Any]]: ...

    def facets(self, filter: QueryFilter) -> QueryFacets: ...
