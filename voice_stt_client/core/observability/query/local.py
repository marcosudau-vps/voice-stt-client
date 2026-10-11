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
* **Every filter and sort-cursor value travels as a placeholder.** §5.7: *"Parameterbindung
  ausschliesslich ueber Platzhalter. Kein String-Format, keine
  Interpolation."* The only text ever formatted into SQL is the column list
  and a placeholder count.
* **The connection is closed on every path.** The antipattern list in §13
  names the leaking ``with self._get_connection()`` of
  ``TranscriptHistoryManager`` explicitly.
"""

from __future__ import annotations

import json
import base64
import sqlite3
from pathlib import Path
from typing import Any, List, Mapping, Optional, Sequence, Tuple

from .base import (
    LogRecordView,
    ProviderState,
    ProviderStatus,
    QueryFilter,
    QueryFacets,
    QueryPage,
)

PROVIDER_ID = "local"
DISPLAY_NAME = "Lokale Diagnosehistorie"
DEFAULT_LIMIT = 200
MAX_LIMIT = 1000
CURSOR_PREFIX = "id:"
SORT_CURSOR_PREFIX = "sort:"

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

# UI field name -> (SQLite expression, value kind).  Expressions are static
# and whitelisted here; user input never becomes SQL syntax.
_SORT_FIELDS = {
    "received_at": ("COALESCE(received_at, '') COLLATE NOCASE", "text"),
    "source_timestamp": ("COALESCE(source_timestamp, '') COLLATE NOCASE", "text"),
    "producer_kind": ("COALESCE(producer_kind, '') COLLATE NOCASE", "text"),
    "producer_id": ("COALESCE(producer_id, '') COLLATE NOCASE", "text"),
    "instance_id": ("COALESCE(instance_id, '') COLLATE NOCASE", "text"),
    "scope": ("COALESCE(scope, '') COLLATE NOCASE", "text"),
    "channel": ("COALESCE(channel, '') COLLATE NOCASE", "text"),
    "level": (
        "CASE level WHEN 'DEBUG' THEN 10 WHEN 'INFO' THEN 20 "
        "WHEN 'WARNING' THEN 30 WHEN 'ERROR' THEN 40 "
        "WHEN 'CRITICAL' THEN 50 ELSE 0 END",
        "number",
    ),
    "type": ("COALESCE(type, '') COLLATE NOCASE", "text"),
    "component": ("COALESCE(component, '') COLLATE NOCASE", "text"),
    "session_id": ("COALESCE(session_id, '') COLLATE NOCASE", "text"),
    "generation": ("COALESCE(generation, -9223372036854775808)", "number"),
    "activation_id": ("COALESCE(activation_id, '') COLLATE NOCASE", "text"),
    "segment_id": ("COALESCE(segment_id, -9223372036854775808)", "number"),
    "transcription_id": ("COALESCE(transcription_id, '') COLLATE NOCASE", "text"),
    "command_id": ("COALESCE(command_id, '') COLLATE NOCASE", "text"),
    "event_id": ("COALESCE(event_id, '') COLLATE NOCASE", "text"),
    "correlation_id": ("COALESCE(correlation_id, '') COLLATE NOCASE", "text"),
    "server_cursor": ("COALESCE(server_cursor, -9223372036854775808)", "number"),
    "replayed": ("COALESCE(replayed, 0)", "number"),
    "message": ("COALESCE(message, '') COLLATE NOCASE", "text"),
    "record_id": ("COALESCE(record_id, '') COLLATE NOCASE", "text"),
}


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


def _encode_sort_cursor(field: str, descending: bool, value: Any, row_id: int) -> str:
    payload = json.dumps(
        [str(field), bool(descending), value, int(row_id)],
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("utf-8")
    token = base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
    return f"{SORT_CURSOR_PREFIX}{token}"


def _decode_sort_cursor(cursor: str, field: str, descending: bool) -> Tuple[Any, int]:
    text = str(cursor)
    if not text.startswith(SORT_CURSOR_PREFIX):
        raise ValueError("not a sorted local cursor")
    token = text[len(SORT_CURSOR_PREFIX):]
    token += "=" * (-len(token) % 4)
    value = json.loads(base64.urlsafe_b64decode(token.encode("ascii")).decode("utf-8"))
    if (
        not isinstance(value, list)
        or len(value) != 4
        or value[0] != field
        or bool(value[1]) is not bool(descending)
    ):
        raise ValueError("cursor does not match the active sort")
    return value[2], int(value[3])


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
        # ``complete=False`` means *"the provider cut something off"* (§8).
        # Only the ``MAX_LIMIT`` clamp does that. A caller asking for ``0`` or
        # a negative limit gets the default page size, which cuts nothing —
        # reporting that page as incomplete told the status line about a
        # truncation that never happened (OBS-050 gate observation N-4).
        truncated_limit = self._requested_limit(limit) > MAX_LIMIT

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
        after_sort_value: Any = None
        after_sort_id: Optional[int] = None
        if cursor is not None and str(cursor) != "":
            try:
                if filter.sort_by:
                    if filter.sort_by not in _SORT_FIELDS:
                        raise ValueError("unknown sort field")
                    after_sort_value, after_sort_id = _decode_sort_cursor(
                        cursor,
                        filter.sort_by,
                        bool(filter.sort_descending),
                    )
                else:
                    after_id = decode_cursor(cursor)
            except (TypeError, ValueError):
                return self._empty_page(ProviderState.ERROR, "ungueltiger Cursor")

        try:
            sql, parameters = self._build_list_query(
                filter,
                after_id=after_id,
                after_sort_value=after_sort_value,
                after_sort_id=after_sort_id,
                limit=effective_limit,
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
            tail_sql, tail_parameters = self._build_tail_cursor_query(filter)
            tail_row = connection.execute(tail_sql, tail_parameters).fetchone()
        except sqlite3.Error as exc:
            return self._empty_page(*self._classify(exc))
        except Exception as exc:  # noqa: BLE001 - the provider never raises
            return self._empty_page(ProviderState.ERROR, self._short(exc))
        finally:
            self._close(connection)

        has_more = len(rows) > effective_limit
        page_rows = rows[:effective_limit]
        records = tuple(
            self._to_view(
                row,
                sort_field=filter.sort_by,
                sort_descending=bool(filter.sort_descending),
            )
            for row in page_rows
        )
        next_cursor = records[-1].cursor if (has_more and records) else None
        tail_cursor = (
            encode_cursor(int(tail_row[0]))
            if tail_row is not None and tail_row[0] is not None
            else None
        )
        self._status = ProviderStatus(
            self._provider_id, self._display_name, ProviderState.AVAILABLE, ""
        )
        return QueryPage(
            provider_id=self._provider_id,
            records=records,
            next_cursor=next_cursor,
            complete=not truncated_limit,
            status=self._status,
            tail_cursor=tail_cursor,
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

    def facets(self, filter: QueryFilter) -> QueryFacets:  # noqa: A002
        """Return available values while excluding each facet itself.

        Four bounded ``SELECT DISTINCT`` statements avoid loading records or
        raw payloads.  They share one short-lived query-only connection.
        """
        if self._db_path is None or not self._db_path.exists():
            return QueryFacets()
        connection: Optional[sqlite3.Connection] = None
        values = {}
        try:
            connection = self._connect()
            for field, excluded in (
                ("producer_kind", {"producer_kinds"}),
                ("channel", {"channels"}),
                ("level", {"levels"}),
                ("type", {"types", "type_prefix"}),
            ):
                clauses, parameters = self._build_filter_clauses(
                    filter, exclude=excluded
                )
                clauses.append(f"{field} IS NOT NULL")
                where = f" WHERE {' AND '.join(clauses)}"
                rows = connection.execute(
                    f"SELECT DISTINCT {field} FROM logs{where}",
                    tuple(parameters),
                ).fetchall()
                values[field] = tuple(
                    sorted(
                        (str(row[0]) for row in rows if str(row[0]) != ""),
                        key=str.casefold,
                    )
                )
        except Exception:  # noqa: BLE001 - provider boundary never raises
            return QueryFacets()
        finally:
            self._close(connection)
        return QueryFacets(
            producer_kinds=values.get("producer_kind", ()),
            channels=values.get("channel", ()),
            levels=values.get("level", ()),
            types=values.get("type", ()),
        )

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
        after_sort_value: Any,
        after_sort_id: Optional[int],
        limit: int,
    ) -> Tuple[str, Tuple[Any, ...]]:
        clauses, parameters = self._build_filter_clauses(filter)

        if filter.sort_by:
            if filter.sort_by not in _SORT_FIELDS:
                raise ValueError(f"unsupported sort field: {filter.sort_by}")
            expression, _kind = _SORT_FIELDS[filter.sort_by]
            descending = bool(filter.sort_descending)
            operator = "<" if descending else ">"
            if after_sort_id is not None:
                clauses.append(
                    f"({expression} {operator} ? OR "
                    f"({expression} = ? AND id {operator} ?))"
                )
                parameters.extend((after_sort_value, after_sort_value, after_sort_id))
            order = "DESC" if descending else "ASC"
            order_clause = f"{expression} {order}, id {order}"
        else:
            descending = bool(filter.newest_first)
            if after_id is not None:
                clauses.append("id < ?" if descending else "id > ?")
                parameters.append(int(after_id))
            order = "DESC" if descending else "ASC"
            order_clause = f"id {order}"

        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        sql = (
            f"SELECT {', '.join(_LIST_COLUMNS)} FROM logs{where} "
            f"ORDER BY {order_clause} LIMIT ?"
        )
        parameters.append(int(limit) + 1)
        return sql, tuple(parameters)

    def _build_filter_clauses(
        self,
        filter: QueryFilter,  # noqa: A002
        *,
        exclude: Optional[set[str]] = None,
    ) -> Tuple[List[str], List[Any]]:
        excluded = exclude or set()
        clauses: List[str] = []
        parameters: List[Any] = []

        for attribute, column in (
            ("producer_kinds", "producer_kind"),
            ("producer_ids", "producer_id"),
            ("instance_ids", "instance_id"),
            ("channels", "channel"),
            ("levels", "level"),
            ("types", "type"),
            ("components", "component"),
            ("scopes", "scope"),
        ):
            if attribute in excluded:
                continue
            values = _clean_values(getattr(filter, attribute))
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

        if filter.type_prefix and "type_prefix" not in excluded:
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
        return clauses, parameters

    def _build_tail_cursor_query(
        self, filter: QueryFilter  # noqa: A002
    ) -> Tuple[str, Tuple[Any, ...]]:
        clauses, parameters = self._build_filter_clauses(filter)
        where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
        return f"SELECT MAX(id) FROM logs{where}", tuple(parameters)

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

    def _to_view(
        self,
        row: Sequence[Any],
        *,
        sort_field: Optional[str] = None,
        sort_descending: bool = False,
    ) -> LogRecordView:
        (
            row_id, record_id, received_at, source_timestamp,
            producer_kind, producer_id, instance_id, scope,
            channel, level, type_, component,
            session_id, generation, activation_id, segment_id,
            transcription_id, command_id, event_id, correlation_id,
            server_cursor, replayed, message, details_json,
        ) = row
        cursor = encode_cursor(row_id)
        if sort_field:
            cursor = _encode_sort_cursor(
                sort_field,
                sort_descending,
                self._sort_value(row, sort_field),
                row_id,
            )
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
            cursor=cursor,
        )

    @staticmethod
    def _sort_value(row: Sequence[Any], field: str) -> Any:
        index = _LIST_COLUMNS.index(field)
        value = row[index]
        if field == "level":
            return {"DEBUG": 10, "INFO": 20, "WARNING": 30,
                    "ERROR": 40, "CRITICAL": 50}.get(str(value), 0)
        if _SORT_FIELDS[field][1] == "number":
            return -9223372036854775808 if value is None else int(value)
        return "" if value is None else str(value)

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
