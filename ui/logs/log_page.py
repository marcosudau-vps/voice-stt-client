"""
``LogPage`` — filter bar, table, detail view and the two modes (OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.2/§9.3 and
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §11.2 (``FD-S1``).

**Live mode has no ring buffer.** §9.2::

    QTimer (250 ms) im LogPage stellt eine TAILENDE ABFRAGE ueber dieselbe
    Provider-Schnittstelle:  WHERE id > :last  ORDER BY id  LIMIT 500
    KEIN Signal je Record

So live and history are the *same* query path with different parameters:
history asks ``newest_first=True`` and pages backwards with ``next_cursor``,
live asks ``newest_first=False`` and pages forwards from the last row it has
seen. That is one abstraction, not two — and when the worker is dead the live
view simply stops gaining rows, *"was der Wahrheit entspricht"* (FD-S1).

**No mixed mode** (§9.3): it would have to deduplicate live records against
the loaded page and re-sort on every filter change — the most expensive part
of a log view, and explicitly out of V1.

**Ordering invariant (OBS-050 gate findings B-1/B-2).** The table is always
monotone in ``logs.id``, and it shows every page in exactly the direction its
query walked:

* **Historie** descends. The frozen ``QueryFilter`` default is
  ``newest_first=True``, the page is displayed as the provider returned it,
  and a further page — which by definition holds *older* rows — is appended
  **below**. "Unten" therefore means "älter", which is what makes the frozen
  *"automatisches Nachladen am Listenende"* (§9.3) land on the right end of
  the list.
* **Live** ascends. The tail query is ``WHERE id > :last ORDER BY id``
  (§9.2), so new rows belong at the bottom, where ``scrollToBottom`` and the
  "auto-scroll turns off when you scroll up" rule expect them. The one and
  only reversal in this module turns the descending **seed** page of the live
  mode into that ascending direction, so the tails extend it instead of
  contradicting it.

The earlier code reversed *every* history page and appended it below, which
made the visible time axis jump backwards at each page boundary (B-1).

**A response is interpreted by what was asked, never by the current cursor
state.** Every query is issued through :meth:`_issue`, which reserves the
request id and records the request *kind* in the same step;
:meth:`_on_page_ready` dispatches on that kind. Deriving it from
``_live_cursor is not None`` was B-2: after a live start on an empty result
set the cursor is ``None``, so the first ascending tail was processed as if
it were a descending page — reversed, and with the cursor taken from its
*oldest* row, which made the next tail return the same records again.

The status line polls (``QTimer`` 1 s, CONTRACTS §11.2: *"Kein Signal je
Fehler -- sonst wiederholt sich das Frequenzproblem"*), following the
existing LED-availability poll as its model.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Any, Callable, Optional

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from core.observability.query.base import QueryFilter
from ui.logs.log_detail_view import LogDetailView
from ui.logs.log_filter_bar import LogFilterBar
from ui.logs.log_query_controller import (
    DEFAULT_PAGE_SIZE,
    LIVE_PAGE_SIZE,
    LogQueryController,
)
from ui.logs.log_table_model import LogTableModel

LIVE_INTERVAL_MS = 250
HEALTH_INTERVAL_MS = 1000
AUTO_LOAD_MARGIN = 4

MODE_HISTORY = "history"
MODE_LIVE = "live"

# What a pending query asked for. The answer is interpreted by this value —
# never by a piece of state that may have moved in the meantime (B-2).
REQUEST_HISTORY_FIRST = "history_first"
REQUEST_HISTORY_MORE = "history_more"
REQUEST_LIVE_SEED = "live_seed"
REQUEST_LIVE_TAIL = "live_tail"


class LogPage(QWidget):
    """One provider, one filter, one mode."""

    status_changed = Signal(str)

    def __init__(
        self,
        controller: LogQueryController,
        *,
        health_provider: Optional[Callable[[], Any]] = None,
        parent: Optional[QWidget] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._health_provider = health_provider
        self._page_size = max(1, int(page_size))
        self._mode = MODE_HISTORY
        self._filter = QueryFilter()
        self._provider_id = ""
        self._next_cursor: Optional[str] = None
        self._live_cursor: Optional[str] = None
        self._active_request = 0
        self._active_kind: Optional[str] = None
        self._raw_request = 0
        self._loading = False
        self._last_page_status: Optional[Any] = None

        root = QVBoxLayout(self)

        self.filter_bar = LogFilterBar(self)
        root.addWidget(self.filter_bar)

        controls = QHBoxLayout()
        self.provider_box = QComboBox(self)
        controls.addWidget(QLabel("Quelle"))
        controls.addWidget(self.provider_box)
        self.mode_box = QComboBox(self)
        self.mode_box.addItem("Historie", MODE_HISTORY)
        self.mode_box.addItem("Live", MODE_LIVE)
        controls.addWidget(QLabel("Modus"))
        controls.addWidget(self.mode_box)
        self.autoscroll_box = QCheckBox("Automatisch scrollen", self)
        self.autoscroll_box.setChecked(True)
        controls.addWidget(self.autoscroll_box)
        self.reload_button = QPushButton("Neu laden", self)
        controls.addWidget(self.reload_button)
        self.more_button = QPushButton("Weitere laden", self)
        controls.addWidget(self.more_button)
        controls.addStretch(1)
        root.addLayout(controls)

        self.splitter = QSplitter(Qt.Orientation.Vertical, self)
        self.table = QTableView(self.splitter)
        self.model = LogTableModel(self.table)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.table.verticalHeader().setVisible(False)
        self.detail = LogDetailView(self.splitter)
        self.splitter.addWidget(self.table)
        self.splitter.addWidget(self.detail)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        root.addWidget(self.splitter, 1)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        root.addWidget(self.status_label)

        self._live_timer = QTimer(self)
        self._live_timer.setInterval(LIVE_INTERVAL_MS)
        self._live_timer.timeout.connect(self._tail)
        self._health_timer = QTimer(self)
        self._health_timer.setInterval(HEALTH_INTERVAL_MS)
        self._health_timer.timeout.connect(self.refresh_status)

        self.filter_bar.filter_changed.connect(self._on_filter_changed)
        self.mode_box.currentIndexChanged.connect(self._on_mode_changed)
        self.provider_box.currentIndexChanged.connect(self._on_provider_changed)
        self.reload_button.clicked.connect(self.reload)
        self.more_button.clicked.connect(self.load_more)
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.table.verticalScrollBar().valueChanged.connect(self._on_scrolled)
        controller.page_ready.connect(self._on_page_ready)
        controller.raw_ready.connect(self._on_raw_ready)

        self.refresh_providers()

    # -- lifecycle ---------------------------------------------------------

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def start(self) -> None:
        """Called when the window becomes visible. Nothing polls while the
        window is hidden — §9.1's second reason for not making this a
        settings tab was exactly a view that keeps querying unseen."""
        self._health_timer.start()
        self.refresh_status()
        self.reload()

    def stop(self) -> None:
        self._live_timer.stop()
        self._health_timer.stop()

    # -- providers ---------------------------------------------------------

    def refresh_providers(self) -> None:
        statuses = self._controller.provider_statuses()
        previous = self._provider_id
        blocked = self.provider_box.blockSignals(True)
        try:
            self.provider_box.clear()
            for status in statuses:
                self.provider_box.addItem(status.display_name, status.provider_id)
            index = self.provider_box.findData(previous) if previous else -1
            self.provider_box.setCurrentIndex(index if index >= 0 else 0)
        finally:
            self.provider_box.blockSignals(blocked)
        self._provider_id = str(self.provider_box.currentData() or "")

    def _on_provider_changed(self, *unused: object) -> None:
        del unused
        self._provider_id = str(self.provider_box.currentData() or "")
        self.reload()

    # -- filter and mode ---------------------------------------------------

    def _on_filter_changed(self, new_filter: object) -> None:
        if isinstance(new_filter, QueryFilter):
            self._filter = new_filter
        self.reload()

    def _on_mode_changed(self, *unused: object) -> None:
        del unused
        self._mode = str(self.mode_box.currentData() or MODE_HISTORY)
        self.reload()

    def set_mode(self, mode: str) -> None:
        index = self.mode_box.findData(mode)
        if index >= 0:
            self.mode_box.setCurrentIndex(index)

    # -- queries -----------------------------------------------------------

    def reload(self) -> None:
        """Discard the current page and ask again from the top.

        The live timer is stopped first: an in-flight tail belongs to the old
        filter, and its ``request_id`` would no longer be the active one
        anyway.
        """
        self._live_timer.stop()
        self.model.clear()
        self.detail.clear()
        self._next_cursor = None
        self._live_cursor = None
        self._active_kind = None
        if not self._provider_id:
            self.refresh_status()
            return
        # Both modes start from the newest end: history because that is the
        # page it shows, live because it needs a starting point for the tail.
        self._issue(
            REQUEST_LIVE_SEED if self._mode == MODE_LIVE else REQUEST_HISTORY_FIRST,
            newest_first=True,
            cursor=None,
            limit=self._page_size,
        )

    def load_more(self) -> None:
        """Next page of the history mode (§9.3: *"'Weitere laden' und
        automatisches Nachladen am Listenende"*)."""
        if self._mode != MODE_HISTORY or self._loading or not self._next_cursor:
            return
        if not self._provider_id:
            return
        self._issue(
            REQUEST_HISTORY_MORE,
            newest_first=True,
            cursor=self._next_cursor,
            limit=self._page_size,
        )

    def _tail(self) -> None:
        """The 250 ms tailing query (§9.2). One request at a time: a slow
        answer must not queue up a backlog of timer ticks."""
        if self._mode != MODE_LIVE or self._loading or not self._provider_id:
            return
        self._issue(
            REQUEST_LIVE_TAIL,
            newest_first=False,
            cursor=self._live_cursor,
            limit=LIVE_PAGE_SIZE,
        )

    def _issue(
        self,
        kind: str,
        *,
        newest_first: bool,
        cursor: Optional[str],
        limit: int,
    ) -> None:
        """Reserve the request id **and** record what was asked, in one step.

        The pairing is the whole point (B-2): an answer must be interpretable
        from its own request, not from state that may have moved on. Reserving
        the id before the query is issued is equally deliberate — a query that
        finishes before ``request_page`` returns publishes synchronously, and
        this page would otherwise discard its own fresh answer as stale.
        """
        self._active_request = self._controller.next_request_id()
        self._active_kind = kind
        self._loading = True
        self._controller.request_page(
            self._provider_id,
            replace(self._filter, newest_first=newest_first),
            cursor=cursor,
            limit=limit,
            request_id=self._active_request,
        )

    def _on_page_ready(self, request_id: int, page: object) -> None:
        """Render one answer according to the request that produced it.

        ``kind`` is consumed here, so a repeated delivery of the same answer
        is a no-op rather than a second append.
        """
        if request_id != self._active_request or self._active_kind is None:
            # Answer to a filter, mode or provider that is no longer current.
            return
        kind = self._active_kind
        self._active_kind = None
        self._loading = False
        records = tuple(getattr(page, "records", ()) or ())
        self._last_page_status = getattr(page, "status", None)

        if kind == REQUEST_LIVE_SEED:
            # The only reversal in this module: the seed arrives descending
            # and is turned into the ascending direction the tails extend.
            ordered = tuple(reversed(records))
            self.model.set_records(ordered)
            self._live_cursor = ordered[-1].cursor if ordered else None
            self._live_timer.start()
            if self.autoscroll_box.isChecked():
                self.table.scrollToBottom()
        elif kind == REQUEST_LIVE_TAIL:
            # Already ascending (``ORDER BY id``); the newest row is the last.
            appended = self.model.append_page(records)
            if records:
                self._live_cursor = records[-1].cursor
            if appended and self.autoscroll_box.isChecked():
                self.table.scrollToBottom()
        else:
            # Historie: shown exactly as the provider returned it, newest at
            # the top. A further page holds older rows and therefore belongs
            # below — which is what makes "Nachladen am Listenende" load the
            # next page instead of breaking the order (B-1).
            if kind == REQUEST_HISTORY_FIRST:
                self.model.set_records(records)
            else:
                self.model.append_page(records)
            self._next_cursor = getattr(page, "next_cursor", None)
            self.more_button.setEnabled(bool(self._next_cursor))
        self.refresh_status()

    # -- selection and detail ---------------------------------------------

    def _on_selection_changed(self, *unused: object) -> None:
        del unused
        record = self._selected_record()
        if record is None:
            self.detail.clear()
            return
        self.detail.show_record(record)
        # §9.3: raw is loaded on selection, never with the list.
        self._raw_request = self._controller.next_request_id()
        self._controller.request_raw(
            str(getattr(record, "provider_id", self._provider_id)),
            str(record.record_id),
            request_id=self._raw_request,
        )

    def _on_raw_ready(self, request_id: int, record_id: str, raw: object) -> None:
        if request_id != self._raw_request:
            return
        self.detail.set_raw(record_id, raw if isinstance(raw, dict) or raw is None else dict(raw))

    def _selected_record(self) -> Optional[Any]:
        indexes = self.table.selectionModel().selectedRows()
        if not indexes:
            return None
        return self.model.record_at(indexes[0].row())

    # -- context actions (§9.3) -------------------------------------------

    def _show_context_menu(self, position) -> None:
        record = self.model.record_at(self.table.indexAt(position).row())
        if record is None:
            return
        menu = QMenu(self.table)
        if record.session_id:
            action = menu.addAction("Nur diese Session")
            action.triggered.connect(
                lambda _checked=False, value=record.session_id: (
                    self.filter_bar.apply_context(session_id=value)
                )
            )
        if record.activation_id:
            # FD-C2 / ARCH §3.4: the unreliability is named in the action itself.
            action = menu.addAction("Nur diese Activation (unzuverlässig)")
            action.triggered.connect(
                lambda _checked=False, value=record.activation_id: (
                    self.filter_bar.apply_context(activation_id=value)
                )
            )
        if record.segment_id is not None:
            action = menu.addAction("Nur dieses Segment")
            action.triggered.connect(
                lambda _checked=False, value=record.segment_id: (
                    self.filter_bar.apply_context(segment_id=value)
                )
            )
        if record.type:
            action = menu.addAction("Nur diesen Eventtyp")
            action.triggered.connect(
                lambda _checked=False, value=record.type: (
                    self.filter_bar.apply_context(type_value=value)
                )
            )
        if record.correlation_id:
            action = menu.addAction("Nur diese Korrelation")
            action.triggered.connect(
                lambda _checked=False, value=record.correlation_id: (
                    self.filter_bar.apply_context(correlation_id=value)
                )
            )
        if menu.isEmpty():
            return
        menu.exec(self.table.viewport().mapToGlobal(position))

    # -- auto-scroll and auto-load ----------------------------------------

    def _on_scrolled(self, value: int) -> None:
        bar = self.table.verticalScrollBar()
        if self._mode == MODE_LIVE:
            # §9.3: auto-scroll "schaltet sich beim Hochscrollen ab".
            if value < bar.maximum():
                self.autoscroll_box.setChecked(False)
            return
        if value >= bar.maximum() - AUTO_LOAD_MARGIN:
            # §9.3: automatisches Nachladen am Listenende.
            self.load_more()

    # -- status line (CONTRACTS §11.2) ------------------------------------

    def refresh_status(self) -> None:
        parts = []
        status = self._last_page_status
        if status is not None:
            state = getattr(getattr(status, "state", None), "value", "")
            detail = getattr(status, "detail", "")
            parts.append(f"Provider: {state}" + (f" – {detail}" if detail else ""))
        parts.append(f"{self.model.rowCount()} Zeilen")
        # The two modes read in opposite directions, each following its own
        # query (see the ordering invariant in the module docstring). Saying
        # which one is active costs one word and removes the only thing about
        # this table that somebody could otherwise misread.
        parts.append(
            "neueste unten" if self._mode == MODE_LIVE else "neueste oben"
        )
        if self._mode == MODE_HISTORY and self._next_cursor:
            parts.append("ältere Seiten verfügbar")
        snapshot = self._health_snapshot()
        if snapshot is not None:
            parts.append(_health_text(snapshot))
        text = " · ".join(part for part in parts if part)
        self.status_label.setText(text)
        self.status_changed.emit(text)

    def _health_snapshot(self) -> Optional[Any]:
        if self._health_provider is None:
            return None
        try:
            return self._health_provider()
        except Exception:  # noqa: BLE001 - a status line never raises (§8.4)
            return None


def _health_text(snapshot: Any) -> str:
    """The health half of the status line. ARCH §8.4: a logging-internal
    fatal error is silent everywhere else — *"Wer das LogWindow geoeffnet
    hat, sieht sofort, dass die Daten unvollstaendig sind."*"""
    state = getattr(getattr(snapshot, "state", None), "value", "?")
    dropped = (
        int(getattr(snapshot, "dropped_watermark", 0) or 0)
        + int(getattr(snapshot, "dropped_queue_full", 0) or 0)
        + int(getattr(snapshot, "dropped_shutdown", 0) or 0)
    )
    text = (
        f"Logging: {state} · geschrieben {getattr(snapshot, 'written', 0)}"
        f" · dedupliziert {getattr(snapshot, 'deduplicated', 0)}"
        f" · verworfen {dropped}"
        f" · Queue {getattr(snapshot, 'queue_depth', 0)}"
    )
    detail = getattr(snapshot, "detail", "")
    return f"{text} – {detail}" if detail else text


__all__ = ["LogPage", "MODE_HISTORY", "MODE_LIVE", "LIVE_INTERVAL_MS"]
