"""
``LocalLogProvider`` — the read-only query provider over the local SQLite
store (OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §5.4 (own short-lived
reader connections, ``PRAGMA query_only = ON`` and **never** ``mode=ro``),
§5.7 (keyset pagination, ``raw_json`` not in the list query, placeholders
only), §8 (the provider contract: ``status()`` without I/O, ``query()``
never raises, opaque cursor) and ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` O-14
(*"Der Query-Layer ist ausschliesslich lesend"*) plus §5.2 (``query`` knows
``models`` + ``storage``, never ``ingress``/``worker``/``manager``).

Three properties of this module are load-bearing and easy to lose:

* **It never creates the database file.** ``sqlite3.connect`` would create an
  empty one, and a store file conjured up by the *reader* would be a write by
  the query layer in everything but name (O-14). A missing file is a provider
  *state* (``UNAVAILABLE``), not an error.
* **Every filter value travels as a placeholder.** §5.7: *"Parameterbindung
  ausschliesslich ueber Platzhalter. Kein String-Format, keine
  Interpolation."* The only text ever formatted into SQL is the column list
  and a placeholder count.
* **The connection is closed on every path.** The antipattern list in §13
  names the leaking ``with self._get_connection()`` of
  ``TranscriptHistoryManager`` explicitly.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence, Tuple

from .base import (
    LogRecordView,
    ProviderState,
    ProviderStatus,
    QueryFilter,
    QueryPage,
)

PROVIDER_ID = "local"
DISPLAY_NAME = "Lokale Diagnosehistorie"
DEFAULT_LIMIT = 200
MAX_LIMIT = 1000
CURSOR_PREFIX = "id:"

# CONTRACTS §5.7: exactly these columns, ``raw_json`` deliberately absent —
# *"raw_json wird in der LISTENabfrage NICHT geladen"*.
_LIST_COLUMNS: Tuple[str, ...] = (
    "id",
    "record_id",
    "received_at",
    "source_timestamp",
    "producer_kind",
    "producer_id",
    "instance_id",
    "scope",
    "channel",
    "level",
    "type",
    "component",
    "session_id",
    "generation",
    "activation_id",
    "segment_id",
    "transcription_id",
    "command_id",
    "event_id",
    "correlation_id",
    "server_cursor",
    "replayed",
    "message",
    "details_json",
)

_LIKE_ESCAPE = "\\"


def encode_cursor(row_id: int) -> str:
    """The opaque pagination key of one record (§8.1: *"cursor als opaker
    String"*). The local provider encodes ``logs.id``; a later server
    provider encodes ``afterCursor``. Callers must never parse it."""
    return f"{CURSOR_PREFIX}{int(row_id)}"


def decode_cursor(cursor: str) -> int:
    """Inverse of :func:`encode_cursor`. Raises ``ValueError`` for anything
    this provider did not produce — the caller turns that into an ``ERROR``
    page rather than silently restarting at the first row, which would show a
    different result set than the caller asked for."""
    text = str(cursor)
    if not text.startswith(CURSOR_PREFIX):
        raise ValueError(f"not a local cursor: {cursor!r}")
    return int(text[len(CURSOR_PREFIX):])


def _like_pattern(text: str) -> str:
    """``%text%`` with the LIKE wildcards inside ``text`` neutralised.

    Without this a user typing ``%`` into the free-text box would match every
    row, and ``_`` would match any single character — a filter that quietly
    means something else than what was typed.
    """
    escaped = (
        str(text)
        .replace(_LIKE_ESCAPE, _LIKE_ESCAPE + _LIKE_ESCAPE)
        .replace("%", _LIKE_ESCAPE + "%")
        .replace("_", _LIKE_ESCAPE + "_")
    )
    return f"%{escaped}%"


def _prefix_pattern(text: str) -> str:
    escaped = (
        str(text)
        .replace(_LIKE_ESCAPE, _LIKE_ESCAPE + _LIKE_ESCAPE)
        .replace("%", _LIKE_ESCAPE + "%")
        .replace("_", _LIKE_ESCAPE + "_")
    )
    return f"{escaped}%"


def _clean_values(values: Any) -> Tuple[Any, ...]:
    """Drop empty/None entries from a tuple filter. An empty tuple means
    *"no restriction"* (§8), so a tuple that only held blanks must behave
    exactly like an unset filter instead of matching nothing."""
    if not values:
        return ()
    return tuple(value for value in values if value is not None and str(value) != "")


def _loads_mapping(text: Any) -> Mapping[str, Any]:
    if not text:
        return {}
    try:
        value = json.loads(text)
    except Exception:  # noqa: BLE001 - a corrupt row must not break the page
        return {}
    return value if isinstance(value, dict) else {}


class LocalLogProvider:
    """Reads the local ``observability.sqlite3`` and nothing else.

    ``db_path`` of ``None`` means *"this installation has no local store"*
    (``store_enabled: false``); the provider then reports ``UNAVAILABLE`` and
    answers every query with an empty page instead of pretending there is
    nothing to see.
    """

    def __init__(
        self,
        db_path: Optional[Path],
        *,
        provider_id: str = PROVIDER_ID,
        display_name: str = DISPLAY_NAME,
        timeout: float = 5.0,
    ) -> None:
        self._db_path = Path(db_path) if db_path is not None else None
        self._provider_id = provider_id
        self._display_name = display_name
        self._timeout = max(0.1, float(timeout))
        if self._db_path is None:
            self._status = ProviderStatus(
                provider_id, display_name, ProviderState.UNAVAILABLE,
                "lokale Diagnosehistorie ist deaktiviert",
            )
        else:
            self._status = ProviderStatus(
                provider_id, display_name, ProviderState.AVAILABLE, ""
            )

    # -- LogProvider ------------------------------------------------------

    @property
    def provider_id(self) -> str:
        return self._provider_id

    @property
    def db_path(self) -> Optional[Path]:
        return self._db_path

    def status(self) -> ProviderStatus:
        """§8: *"Muss OHNE Netz- oder DB-Zugriff antworten koennen
        (gecacht). Die UI ruft es bei jedem Filterwechsel."* The cached value
        is refreshed as a side effect of every ``query``/``fetch_raw``."""
        return self._status

    def query(
        self,
        filter: QueryFilter,  # noqa: A002 - frozen parameter name (§8)
        cursor: Optional[str] = None,
        limit: int = DEFAULT_LIMIT,
    ) -> QueryPage:
        """Blocking, called on a worker thread, **never raises** (§8.1: *"Ein
        Providerfehler ist ein Anzeigezustand, kein Programmfehler"*)."""
        effective_limit = self._effective_limit(limit)
        truncated_limit = effective_limit != self._requested_limit(limit)

        if self._db_path is None:
            return self._empty_page(
                ProviderState.UNAVAILABLE, "lokale Diagnosehistorie ist deaktiviert"
            )
        if not self._db_path.exists():
            # Not an error: the worker creates the file on first write. Opening
            # it here would CREATE it — a write by the query layer (O-14).
            return self._empty_page(
                ProviderState.UNAVAILABLE, "noch keine lokale Diagnosehistorie vorhanden"
            )

        after_id: Optional[int] = None
        if cursor is not None and str(cursor) != "":
            try:
                after_id = decode_cursor(cursor)
            except (TypeError, ValueError):
                return self._empty_page(ProviderState.ERROR, "ungueltiger Cursor")

        try:
            sql, parameters = self._build_list_query(
                filter, after_id=after_id, limit=effective_limit
            )
        except Exception as exc:  # noqa: BLE001 - a bad filter is a display state
            return self._empty_page(ProviderState.ERROR, self._short(exc))

        connection: Optional[sqlite3.Connection] = None
        try:
            connection = self._connect()
            # One row more than asked for: its existence — and only its
            # existence — answers "is there a next page?" without a COUNT
            # (§8.1: *"kein count()"*).
            rows = connection.execute(sql, parameters).fetchall()
        except sqlite3.Error as exc:
            return self._empty_page(*self._classify(exc))
        except Exception as exc:  # noqa: BLE001 - the provider never raises
            return self._empty_page(ProviderState.ERROR, self._short(exc))
        finally:
            self._close(connection)

        has_more = len(rows) > effective_limit
        page_rows = rows[:effective_limit]
        records = tuple(self._to_view(row) for row in page_rows)
        next_cursor = records[-1].cursor if (has_more and records) else None
        self._status = ProviderStatus(
            self._provider_id, self._display_name, ProviderState.AVAILABLE, ""
        )
        return QueryPage(
            provider_id=self._provider_id,
            records=records,
            next_cursor=next_cursor,
            complete=not truncated_limit,
            status=self._status,
        )

    def fetch_raw(self, record_id: str) -> Optional[Mapping[str, Any]]:
        """§5.7: the detail view loads ``raw`` separately, by ``record_id``.
        Never raises; ``None`` means "no raw payload stored, or unreadable"."""
        if self._db_path is None or not self._db_path.exists():
            return None
        connection: Optional[sqlite3.Connection] = None
        try:
            connection = self._connect()
            row = connection.execute(
                "SELECT raw_json FROM logs WHERE record_id = ?", (str(record_id),)
            ).fetchone()
        except Exception:  # noqa: BLE001 - the provider never raises
            return None
        finally:
            self._close(connection)
        if row is None or row[0] is None:
            return None
        value = _loads_mapping(row[0])
        return value or None

    # -- connection -------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        """A fresh, short-lived reader connection (§5.4).

        ``PRAGMA query_only = ON`` rather than ``mode=ro``: a read-only URI
        connection to a WAL database is not generally possible — the opening
        process needs write access to the ``-shm`` file (W-13). Side benefit
        named in §5.4: a faulty query can never write.
        """
        connection = sqlite3.connect(str(self._db_path), timeout=self._timeout)
        try:
            connection.execute("PRAGMA busy_timeout = 5000")
            connection.execute("PRAGMA query_only = ON")
        except Exception:
            self._close(connection)
            raise
        return connection

    @staticmethod
    def _close(connection: Optional[sqlite3.Connection]) -> None:
        if connection is None:
            return
        try:
            connection.close()
        except Exception:  # noqa: BLE001
            pass

    # -- SQL construction (§5.7) ------------------------------------------

    def _build_list_query(
        self,
        filter: QueryFilter,  # noqa: A002
        *,
        after_id: Optional[int],
        limit: int,
    ) -> Tuple[str, Tuple[Any, ...]]:
        clauses: List[str] = []
        parameters: List[Any] = []

        for column, values in (
            ("producer_kind", _clean_values(filter.producer_kinds)),
            ("producer_id", _clean_values(filter.producer_ids)),
            ("instance_id", _clean_values(filter.instance_ids)),
            ("channel", _clean_values(filter.channels)),
            ("level", _clean_values(filter.levels)),
            ("type", _clean_values(filter.types)),
            ("component", _clean_values(filter.components)),
            ("scope", _clean_values(filter.scopes)),
        ):
            if values:
                placeholders = ",".join("?" for _ in values)
                clauses.append(f"{column} IN ({placeholders})")
                parameters.extend(values)

        for column, value in (
            ("session_id", filter.session_id),
            ("activation_id", filter.activation_id),
            ("command_id", filter.command_id),
            ("correlation_id", filter.correlation_id),
            ("transcription_id", filter.transcription_id),
            ("event_id", filter.event_id),
        ):
            if value is not None and str(value) != "":
                clauses.append(f"{column} = ?")
                parameters.append(str(value))

        for column, value in (
            ("generation", filter.generation),
            ("segment_id", filter.segment_id),
        ):
            if value is not None:
                clauses.append(f"{column} = ?")
                parameters.append(int(value))

        if filter.type_prefix:
            clauses.append("type LIKE ? ESCAPE ?")
            parameters.extend((_prefix_pattern(filter.type_prefix), _LIKE_ESCAPE))

        if filter.since:
            clauses.append("received_at >= ?")
            parameters.append(str(filter.since))
        if filter.until:
            # exclusive (§8), so a day boundary belongs to exactly one page
            clauses.append("received_at < ?")
            parameters.append(str(filter.until))

        if filter.text:
            pattern = _like_pattern(filter.text)
            clauses.append(
                "(message LIKE ? ESCAPE ? OR type LIKE ? ESCAPE ? "
                "OR component LIKE ? ESCAPE ?)"
            )
            parameters.extend(
                (pattern, _LIKE_ESCAPE, pattern, _LIKE_ESCAPE, pattern, _LIKE_ESCAPE)
            )

        if not filter.include_replayed:
            clauses.append("replayed = 0")

        descending = bool(filter.newest_first)
        if after_id is not None:
            # Keyset, not OFFSET (§5.7): the page sequence stays stable while
            # the worker keeps writing.
            clauses.append("id < ?" if descending else "id > ?")
            parameters.append(int(after_id))

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        order = "DESC" if descending else "ASC"
        sql = (
            f"SELECT {', '.join(_LIST_COLUMNS)} FROM logs{where} "
            f"ORDER BY id {order} LIMIT ?"
        )
        parameters.append(int(limit) + 1)
        return sql, tuple(parameters)

    # -- helpers ----------------------------------------------------------

    @staticmethod
    def _requested_limit(limit: Any) -> int:
        try:
            value = int(limit)
        except (TypeError, ValueError):
            return DEFAULT_LIMIT
        return value

    def _effective_limit(self, limit: Any) -> int:
        value = self._requested_limit(limit)
        if value <= 0:
            return DEFAULT_LIMIT
        return min(value, MAX_LIMIT)

    def _to_view(self, row: Sequence[Any]) -> LogRecordView:
        (
            row_id, record_id, received_at, source_timestamp,
            producer_kind, producer_id, instance_id, scope,
            channel, level, type_, component,
            session_id, generation, activation_id, segment_id,
            transcription_id, command_id, event_id, correlation_id,
            server_cursor, replayed, message, details_json,
        ) = row
        return LogRecordView(
            provider_id=self._provider_id,
            record_id=record_id,
            received_at=received_at,
            source_timestamp=source_timestamp,
            producer_kind=producer_kind,
            producer_id=producer_id,
            instance_id=instance_id,
            scope=scope,
            channel=channel,
            level=level,
            type=type_,
            component=component,
            session_id=session_id,
            generation=generation,
            activation_id=activation_id,
            segment_id=segment_id,
            transcription_id=transcription_id,
            command_id=command_id,
            event_id=event_id,
            correlation_id=correlation_id,
            server_cursor=server_cursor,
            replayed=bool(replayed),
            message=message,
            details=_loads_mapping(details_json),
            raw=None,  # §5.7: never in the list query
            cursor=encode_cursor(row_id),
        )

    def _classify(self, exc: sqlite3.Error) -> Tuple[ProviderState, str]:
        """A store the worker has not populated yet is *unavailable*, not
        broken. Everything else is an error the status line must show."""
        text = str(exc)
        if "no such table" in text.lower():
            return (
                ProviderState.UNAVAILABLE,
                "noch keine lokale Diagnosehistorie vorhanden",
            )
        return ProviderState.ERROR, self._short(exc)

    @staticmethod
    def _short(exc: BaseException) -> str:
        """Short and redacted enough for the status line (§8: *"detail: kurz,
        redigiert"*): the exception type plus at most 120 characters."""
        return f"{type(exc).__name__}: {str(exc)[:120]}"

    def _empty_page(self, state: ProviderState, detail: str) -> QueryPage:
        self._status = ProviderStatus(
            self._provider_id, self._display_name, state, detail
        )
        return QueryPage(
            provider_id=self._provider_id,
            records=(),
            next_cursor=None,
            complete=state is ProviderState.AVAILABLE,
            status=self._status,
        )


__all__ = [
    "LocalLogProvider",
    "PROVIDER_ID",
    "DEFAULT_LIMIT",
    "MAX_LIMIT",
    "encode_cursor",
    "decode_cursor",
]
