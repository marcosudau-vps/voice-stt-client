"""
``LogQueryController`` — the Qt-side boundary in front of the query layer
(OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.2::

    Qt-Mainthread  --filter_changed(QueryFilter), entprellt 300 ms-->
    LogQueryController (QObject, lebt im Qt-Thread)
        submit -> ThreadPoolExecutor(max_workers=1)
        Query-Worker-Thread: LogQueryService -> LocalLogProvider
        Ergebnis per Signal (QueuedConnection) -> Qt-Mainthread

Two rules of that picture are the reason this class exists at all:

* **The query never runs on ``CoreBridge``.** §9.2: *"CoreBridge gehoert dem
  Core-asyncio-Loop; eine SQLite-Leseabfrage haette dort nichts zu suchen --
  sie wuerde den Loop blockieren, auf dem Audio und WebSocket liegen."* Hence
  an executor of this view's own.
* **``max_workers=1``.** One reader thread keeps the result order equal to
  the request order and bounds the number of short-lived SQLite connections
  at one, which is what makes a "cheap or faulty UI query" a local problem
  (ARCH §8.3, row *"UI-Abfrage teuer/fehlerhaft"*).

Every result carries the ``request_id`` it was asked for. A filter change
while a page is in flight is normal, and the answer to the previous filter
must not be painted into the new one.
"""

from __future__ import annotations

from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import fields, is_dataclass
from typing import Any, Mapping, Optional

from PySide6.QtCore import QObject, Signal

from core.observability.query.base import QueryFilter

DEFAULT_PAGE_SIZE = 200
LIVE_PAGE_SIZE = 500


class LogQueryController(QObject):
    """Runs queries off the Qt thread and hands results back as signals."""

    page_ready = Signal(int, object)
    """``(request_id, QueryPage)`` — always delivered on the Qt thread."""

    raw_ready = Signal(int, str, object)
    """``(request_id, record_id, Mapping | None)``."""

    facets_ready = Signal(int, object)
    """``(request_id, QueryFacets)``."""

    json_ready = Signal(int, object)
    """``(request_id, list[dict])`` with raw loaded only for selected rows."""

    def __init__(self, service: Any, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._service = service
        self._executor = ThreadPoolExecutor(
            max_workers=1, thread_name_prefix="RealtimeSTT-LogQuery"
        )
        self._serial = 0
        self._closed = False

    @property
    def service(self) -> Any:
        return self._service

    def provider_statuses(self) -> tuple:
        """§8.1: ``status()`` answers without I/O, so the Qt thread may ask
        directly instead of paying a round trip through the executor."""
        try:
            return tuple(self._service.providers())
        except Exception:  # noqa: BLE001 - a status line never raises
            return ()

    def next_request_id(self) -> int:
        self._serial += 1
        return self._serial

    def request_page(
        self,
        provider_id: str,
        filter: QueryFilter,  # noqa: A002 - frozen parameter name (§8)
        *,
        cursor: Optional[str] = None,
        limit: int = DEFAULT_PAGE_SIZE,
        request_id: Optional[int] = None,
    ) -> int:
        """Queue one page query and return its ``request_id``.

        ``request_id`` may be reserved by the caller through
        :meth:`next_request_id` **before** the query is issued. That is not a
        convenience: a query that finishes before ``submit`` returns has its
        completion callback run synchronously on the calling thread, so the
        answer can arrive while the caller is still on the line that started
        it. A caller that stores the returned id would then discard its own
        fresh answer as stale.

        Returns ``0`` when the controller is already closed — the caller's
        timer may still fire once while the window is going away, and a
        rejected request is the honest answer to that.
        """
        if self._closed:
            return 0
        query_id = self.next_request_id() if request_id is None else int(request_id)
        self._submit(
            lambda: self._service.query(provider_id, filter, cursor, limit),
            lambda page: self.page_ready.emit(query_id, page),
        )
        return query_id

    def request_raw(
        self,
        provider_id: str,
        record_id: str,
        *,
        request_id: Optional[int] = None,
    ) -> int:
        """Queue the detail-view ``raw`` load (§5.7: loaded separately, only
        for the selected record). Same id reservation as
        :meth:`request_page`."""
        if self._closed:
            return 0
        query_id = self.next_request_id() if request_id is None else int(request_id)
        self._submit(
            lambda: self._service.fetch_raw(provider_id, record_id),
            lambda raw: self.raw_ready.emit(query_id, str(record_id), raw),
        )
        return query_id

    def request_facets(
        self,
        provider_id: str,
        filter: QueryFilter,  # noqa: A002
        *,
        request_id: Optional[int] = None,
    ) -> int:
        if self._closed or not hasattr(self._service, "facets"):
            return 0
        query_id = self.next_request_id() if request_id is None else int(request_id)
        self._submit(
            lambda: self._service.facets(provider_id, filter),
            lambda facets: self.facets_ready.emit(query_id, facets),
        )
        return query_id

    def request_json_records(
        self,
        records: object,
        *,
        request_id: Optional[int] = None,
    ) -> int:
        """Load raw only for the selected records and build canonical JSON."""
        if self._closed:
            return 0
        selected = tuple(records or ())
        if not selected:
            return 0
        query_id = self.next_request_id() if request_id is None else int(request_id)

        def build() -> list[dict[str, Any]]:
            result = []
            for record in selected:
                value = _record_mapping(record)
                provider_id = str(value.get("provider_id", ""))
                record_id = str(value.get("record_id", ""))
                value["raw"] = self._service.fetch_raw(provider_id, record_id)
                result.append(value)
            return result

        self._submit(build, lambda value: self.json_ready.emit(query_id, value))
        return query_id

    def _submit(self, work, publish) -> None:
        def run() -> Any:
            return work()

        def done(future: Future) -> None:
            # Runs on the executor thread. The provider contract says it never
            # raises, and the service repeats that guarantee; this last guard
            # is for the case where it nevertheless did, because an exception
            # swallowed by a Future would otherwise be invisible AND leave the
            # view waiting forever.
            try:
                result = future.result()
            except Exception:  # noqa: BLE001 - O-05 boundary
                return
            if self._closed:
                return
            try:
                publish(result)
            except RuntimeError:
                # The receiving QObject was deleted between the query and its
                # answer (window closed). Nothing to deliver to.
                return

        try:
            self._executor.submit(run).add_done_callback(done)
        except RuntimeError:
            # Executor already shut down — same situation as ``_closed``.
            return

    def shutdown(self, wait: bool = True) -> None:
        """Stop accepting queries and wait for the one that may be running.

        Waiting is not politeness, it is correctness: a query still in flight
        finishes by emitting a signal from the executor thread, and by then
        this ``QObject`` and its window may already be gone — in PySide6 that
        is an access violation, not an exception. The wait is bounded by a
        single short-lived SQLite read (§5.4) and happens only at teardown,
        never on a producing path, so O-03 is untouched.

        Safe to call more than once.
        """
        if self._closed:
            return
        self._closed = True
        try:
            self._executor.shutdown(wait=wait)
        except Exception:  # noqa: BLE001 - teardown never raises
            pass


__all__ = ["LogQueryController", "DEFAULT_PAGE_SIZE", "LIVE_PAGE_SIZE"]


def _record_mapping(record: Any) -> dict[str, Any]:
    if is_dataclass(record):
        return {
            item.name: _plain(getattr(record, item.name))
            for item in fields(record)
            if item.name != "cursor"
        }
    if isinstance(record, Mapping):
        return {str(key): _plain(value) for key, value in record.items()}
    return {
        key: _plain(value)
        for key, value in vars(record).items()
        if not key.startswith("_") and key != "cursor"
    }


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_plain(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(_plain(item) for item in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)
