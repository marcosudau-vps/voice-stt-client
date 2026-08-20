"""Productive desktop viewer for local observability records (OBS-050)."""

from __future__ import annotations

import csv
import json
from dataclasses import fields, is_dataclass, replace
from pathlib import Path
from typing import Any, Callable, Mapping, Optional

from PySide6.QtCore import QItemSelectionModel, QSettings, Qt, QTimer, Signal
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMenu,
    QPushButton,
    QSplitter,
    QStyle,
    QTableView,
    QToolBar,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from core.observability.query.base import QueryFacets, QueryFilter
from ui.logs.log_detail_view import LogDetailView
from ui.logs.log_filter_bar import LogFilterBar
from ui.logs.log_query_controller import DEFAULT_PAGE_SIZE, LIVE_PAGE_SIZE, LogQueryController
from ui.logs.log_table_model import (
    COLUMN_INDEX,
    COLUMN_SPECS,
    DEFAULT_VISIBLE_FIELDS,
    ORIGIN_HISTORY,
    ORIGIN_LIVE,
    TIME_FIELDS,
    LogTableModel,
)

LIVE_INTERVAL_MS = 250
HEALTH_INTERVAL_MS = 1000
AUTO_LOAD_MARGIN = 4

MODE_HISTORY = "history"
MODE_LIVE = "live"
MODE_MIXED = "mixed"

REQUEST_HISTORY_FIRST = "history_first"
REQUEST_HISTORY_MORE = "history_more"
REQUEST_LIVE_SEED = "live_seed"
REQUEST_LIVE_TAIL = "live_tail"
REQUEST_MIXED_SEED = "mixed_seed"

HEADER_STATE_KEY = "log_view/header_state"
VISIBLE_COLUMNS_KEY = "log_view/visible_columns"
SORT_FIELD_KEY = "log_view/sort_field"
SORT_DESC_KEY = "log_view/sort_descending"
SPLITTER_STATE_KEY = "log_view/lower_splitter_state"


class LogPage(QWidget):
    """History, live and combined diagnostics in one sortable table."""

    status_changed = Signal(str)

    def __init__(
        self,
        controller: LogQueryController,
        *,
        health_provider: Optional[Callable[[], Any]] = None,
        parent: Optional[QWidget] = None,
        page_size: int = DEFAULT_PAGE_SIZE,
        settings: Optional[QSettings] = None,
    ) -> None:
        super().__init__(parent)
        self._controller = controller
        self._health_provider = health_provider
        self._page_size = max(1, int(page_size))
        self._settings = settings if settings is not None else QSettings()
        self._mode = MODE_HISTORY
        self._filter = QueryFilter()
        self._provider_id = ""
        self._next_cursor: Optional[str] = None
        self._live_cursor: Optional[str] = None
        self._active_request = 0
        self._active_kind: Optional[str] = None
        self._facets_request = 0
        self._raw_request = 0
        self._json_request = 0
        self._loading = False
        self._last_page_status: Optional[Any] = None
        self._restoring_state = True

        root = QVBoxLayout(self)
        root.setContentsMargins(6, 6, 6, 6)
        root.setSpacing(5)

        self.table = QTableView(self)
        self.model = LogTableModel(self.table)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(False)
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionsMovable(True)
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.setSortIndicatorShown(True)
        self.table.setSortingEnabled(True)
        root.addWidget(self.table, 1)

        self.toolbar = QToolBar("Diagnoseansicht", self)
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        root.addWidget(self.toolbar)
        self._build_toolbar()

        self.filter_bar = LogFilterBar(self)
        # The coordinator itself has no visible surface. Its two groups are
        # separate splitter panes and therefore independently resizable.
        self.filter_bar.hide()
        self.filter_bar.filter_group.setMinimumWidth(330)
        self.filter_bar.filter_group.setMaximumWidth(460)
        self.filter_bar.context_group.setMinimumWidth(230)
        self.filter_bar.context_group.setMaximumWidth(330)
        self.lower_splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self.lower_splitter.addWidget(self.filter_bar.filter_group)
        self.lower_splitter.addWidget(self.filter_bar.context_group)
        self.actions_group = self._build_actions_group()
        self.actions_group.setMinimumWidth(185)
        self.actions_group.setMaximumWidth(240)
        self.lower_splitter.addWidget(self.actions_group)
        self.detail = LogDetailView(self.lower_splitter)
        self.detail.setMinimumWidth(220)
        self.lower_splitter.addWidget(self.detail)
        self.lower_splitter.setChildrenCollapsible(False)
        self.lower_splitter.setStretchFactor(0, 0)
        self.lower_splitter.setStretchFactor(1, 0)
        self.lower_splitter.setStretchFactor(2, 0)
        self.lower_splitter.setStretchFactor(3, 1)
        self.lower_splitter.setSizes([370, 250, 190, 620])
        self.lower_splitter.setMinimumHeight(235)
        root.addWidget(self.lower_splitter)

        self.status_label = QLabel("")
        self.status_label.setWordWrap(True)
        root.addWidget(self.status_label)

        self._live_timer = QTimer(self)
        self._live_timer.setInterval(LIVE_INTERVAL_MS)
        self._live_timer.timeout.connect(self._tail)
        self._health_timer = QTimer(self)
        self._health_timer.setInterval(HEALTH_INTERVAL_MS)
        self._health_timer.timeout.connect(self.refresh_status)

        self._restore_view_state()
        self._restoring_state = False
        self._connect_signals()
        self.refresh_providers()

    def _build_toolbar(self) -> None:
        self.provider_container = QWidget(self.toolbar)
        provider_layout = QHBoxLayout(self.provider_container)
        provider_layout.setContentsMargins(0, 0, 4, 0)
        provider_layout.addWidget(QLabel("Datenquelle"))
        self.provider_box = QComboBox(self.provider_container)
        self.provider_box.setToolTip("Datenprovider der Diagnoseansicht.")
        provider_layout.addWidget(self.provider_box)
        self.provider_action = self.toolbar.addWidget(self.provider_container)

        self.toolbar.addSeparator()
        self.toolbar.addWidget(QLabel("Ansicht"))
        self.mode_box = QComboBox(self.toolbar)
        self.mode_box.addItem("Historie", MODE_HISTORY)
        self.mode_box.addItem("Live", MODE_LIVE)
        self.mode_box.addItem("Live + Historie", MODE_MIXED)
        self.mode_box.setToolTip("Wechselt zwischen Historie, Live-Tailing und kombinierter Ansicht.")
        self.toolbar.addWidget(self.mode_box)

        self.autoscroll_box = QToolButton(self.toolbar)
        self.autoscroll_box.setText("Auto-Scroll")
        self.autoscroll_box.setCheckable(True)
        self.autoscroll_box.setChecked(True)
        self.autoscroll_box.setToolTip(
            "Folgt neuen Einträgen nur bei Sortierung nach einer Zeitspalte; bei anderer Sortierung bleibt die Option ohne Scrollwirkung aktiv."
        )
        self.toolbar.addWidget(self.autoscroll_box)

        self.reload_button = QToolButton(self.toolbar)
        self.reload_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_BrowserReload))
        self.reload_button.setToolTip("Aktualisieren")
        self.toolbar.addWidget(self.reload_button)

        self.more_button = QToolButton(self.toolbar)
        self.more_button.setText("Ältere Einträge laden")
        self.more_button.setToolTip("Lädt die nächste Seite der gefilterten Historie.")
        self.toolbar.addWidget(self.more_button)

        self.toolbar.addSeparator()
        self.previous_button = QToolButton(self.toolbar)
        self.previous_button.setText("↑")
        self.previous_button.setToolTip("Vorheriger Eintrag")
        self.toolbar.addWidget(self.previous_button)
        self.next_button = QToolButton(self.toolbar)
        self.next_button.setText("↓")
        self.next_button.setToolTip("Nächster Eintrag")
        self.toolbar.addWidget(self.next_button)

    def _build_actions_group(self) -> QGroupBox:
        group = QGroupBox("Aktionen", self)
        layout = QVBoxLayout(group)
        layout.setContentsMargins(8, 8, 8, 8)
        self.copy_button = QPushButton("Auswahl kopieren", group)
        self.copy_button.setToolTip("Kopiert die markierte Zellfläche als TSV.")
        self.copy_json_button = QPushButton("Als JSON kopieren", group)
        self.copy_json_button.setToolTip("Kopiert jeden ausgewählten vollständigen Record genau einmal.")
        self.export_csv_button = QPushButton("Geladene Ansicht als CSV …", group)
        self.export_json_button = QPushButton("Geladene Ansicht als JSON …", group)
        self.export_json_button.setToolTip("Exportiert die geladenen Records ohne Raw-Massenabfrage.")
        for button in (
            self.copy_button, self.copy_json_button,
            self.export_csv_button, self.export_json_button,
        ):
            layout.addWidget(button)
        layout.addStretch(1)
        return group

    def _connect_signals(self) -> None:
        self.filter_bar.filter_changed.connect(self._on_filter_changed)
        self.mode_box.currentIndexChanged.connect(self._on_mode_changed)
        self.provider_box.currentIndexChanged.connect(self._on_provider_changed)
        self.reload_button.clicked.connect(self.reload)
        self.more_button.clicked.connect(self.load_more)
        self.previous_button.clicked.connect(lambda: self._move_current(-1))
        self.next_button.clicked.connect(lambda: self._move_current(1))
        self.copy_button.clicked.connect(self.copy_selection_tsv)
        self.copy_json_button.clicked.connect(self.copy_selected_json)
        self.export_csv_button.clicked.connect(lambda: self._export_loaded("csv"))
        self.export_json_button.clicked.connect(lambda: self._export_loaded("json"))
        self.table.customContextMenuRequested.connect(self._show_context_menu)
        self.table.horizontalHeader().customContextMenuRequested.connect(self._show_header_menu)
        self.table.horizontalHeader().sortIndicatorChanged.connect(self._on_sort_changed)
        self.table.horizontalHeader().sectionMoved.connect(lambda *args: self.save_view_state())
        self.table.horizontalHeader().sectionResized.connect(lambda *args: self.save_view_state())
        self.table.selectionModel().currentChanged.connect(self._on_current_changed)
        self.table.verticalScrollBar().valueChanged.connect(self._on_scrolled)
        self.lower_splitter.splitterMoved.connect(lambda *args: self.save_view_state())
        self._controller.page_ready.connect(self._on_page_ready)
        self._controller.raw_ready.connect(self._on_raw_ready)
        self._controller.facets_ready.connect(self._on_facets_ready)
        self._controller.json_ready.connect(self._on_json_ready)
        self._copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.table)
        self._copy_shortcut.activated.connect(self.copy_selection_tsv)

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def provider_id(self) -> str:
        return self._provider_id

    def start(self) -> None:
        self._health_timer.start()
        self.refresh_status()
        self.reload()

    def stop(self) -> None:
        self._live_timer.stop()
        self._health_timer.stop()

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
        self.provider_action.setVisible(self.provider_box.count() >= 2)

    def _on_provider_changed(self, *unused: object) -> None:
        del unused
        self._provider_id = str(self.provider_box.currentData() or "")
        self.reload()

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

    def reload(self) -> None:
        self._live_timer.stop()
        self.model.clear()
        self.detail.clear()
        self._raw_request = self._controller.next_request_id()
        self._next_cursor = None
        self._live_cursor = None
        self._active_kind = None
        self._update_more_action()
        if not self._provider_id:
            self.refresh_status()
            return
        self._request_facets()
        if self._mode == MODE_LIVE:
            self._issue(REQUEST_LIVE_SEED, tail_query=True, cursor=None, limit=self._page_size)
        elif self._mode == MODE_MIXED:
            self._issue(REQUEST_MIXED_SEED, tail_query=False, cursor=None, limit=self._page_size)
        else:
            self._issue(REQUEST_HISTORY_FIRST, tail_query=False, cursor=None, limit=self._page_size)

    def _request_facets(self) -> None:
        request_id = self._controller.next_request_id()
        accepted = self._controller.request_facets(
            self._provider_id, self._filter, request_id=request_id
        )
        self._facets_request = request_id if accepted else 0

    def load_more(self) -> None:
        if self._mode not in (MODE_HISTORY, MODE_MIXED) or self._loading or not self._next_cursor:
            return
        self._issue(REQUEST_HISTORY_MORE, tail_query=False, cursor=self._next_cursor, limit=self._page_size)

    def _tail(self) -> None:
        if self._mode not in (MODE_LIVE, MODE_MIXED) or self._loading or not self._provider_id:
            return
        self._issue(REQUEST_LIVE_TAIL, tail_query=True, cursor=self._live_cursor, limit=LIVE_PAGE_SIZE)

    def _issue(self, kind: str, *, tail_query: bool, cursor: Optional[str], limit: int) -> None:
        self._active_request = self._controller.next_request_id()
        self._active_kind = kind
        self._loading = True
        query_filter = replace(
            self._filter,
            newest_first=not tail_query,
            sort_by=None if tail_query else self.model.sort_field,
            sort_descending=None if tail_query else (
                self.model.sort_order == Qt.SortOrder.DescendingOrder
            ),
        )
        self._controller.request_page(
            self._provider_id, query_filter, cursor=cursor, limit=limit,
            request_id=self._active_request,
        )

    def _on_page_ready(self, request_id: int, page: object) -> None:
        if request_id != self._active_request or self._active_kind is None:
            return
        kind = self._active_kind
        self._active_kind = None
        self._loading = False
        records = tuple(getattr(page, "records", ()) or ())
        self._last_page_status = getattr(page, "status", None)

        if kind == REQUEST_LIVE_SEED:
            self.model.set_records(records, origin=ORIGIN_LIVE)
            self._live_cursor = getattr(page, "tail_cursor", None) or _latest_storage_cursor(records)
            self._live_timer.start()
            self._follow_latest()
        elif kind == REQUEST_MIXED_SEED:
            self.model.set_records(records, origin=ORIGIN_HISTORY)
            self._next_cursor = getattr(page, "next_cursor", None)
            self._live_cursor = getattr(page, "tail_cursor", None) or _latest_storage_cursor(records)
            self._live_timer.start()
            self._follow_latest()
        elif kind == REQUEST_LIVE_TAIL:
            appended = self.model.append_page(records, origin=ORIGIN_LIVE)
            if records:
                self._live_cursor = records[-1].cursor
            if appended:
                self._follow_latest()
        else:
            if kind == REQUEST_HISTORY_FIRST:
                self.model.set_records(records, origin=ORIGIN_HISTORY)
            else:
                self.model.append_page(records, origin=ORIGIN_HISTORY)
            self._next_cursor = getattr(page, "next_cursor", None)
        self._update_more_action()
        self.refresh_status()

    def _on_facets_ready(self, request_id: int, facets: object) -> None:
        if request_id == self._facets_request and isinstance(facets, QueryFacets):
            self.filter_bar.apply_facets(facets)

    def _on_current_changed(self, current, previous) -> None:
        del previous
        record = self.model.record_at(current.row()) if current.isValid() else None
        self._raw_request = self._controller.next_request_id()
        if record is None:
            self.detail.clear()
            return
        self.detail.show_record(record)
        self._controller.request_raw(
            str(getattr(record, "provider_id", self._provider_id)),
            str(record.record_id), request_id=self._raw_request,
        )

    def _on_raw_ready(self, request_id: int, record_id: str, raw: object) -> None:
        if request_id != self._raw_request:
            return
        self.detail.set_raw(record_id, raw if isinstance(raw, dict) or raw is None else dict(raw))

    def _selected_records(self) -> tuple[Any, ...]:
        rows = sorted({index.row() for index in self.table.selectionModel().selectedIndexes()})
        return tuple(record for row in rows if (record := self.model.record_at(row)) is not None)

    def copy_selection_tsv(self) -> None:
        indexes = self.table.selectionModel().selectedIndexes()
        if not indexes:
            return
        rows = range(min(i.row() for i in indexes), max(i.row() for i in indexes) + 1)
        selected_columns = sorted(
            {i.column() for i in indexes if not self.table.isColumnHidden(i.column())},
            key=self.table.horizontalHeader().visualIndex,
        )
        if not selected_columns:
            return
        lines = []
        for row in rows:
            values = [str(self.model.data(self.model.index(row, column)) or "") for column in selected_columns]
            lines.append("\t".join(value.replace("\t", " ").replace("\r", " ").replace("\n", " ") for value in values))
        QApplication.clipboard().setText("\n".join(lines))

    def copy_selected_json(self) -> None:
        records = self._selected_records()
        if not records:
            return
        request_id = self._controller.next_request_id()
        accepted = self._controller.request_json_records(records, request_id=request_id)
        self._json_request = request_id if accepted else 0

    def _on_json_ready(self, request_id: int, records: object) -> None:
        if request_id != self._json_request:
            return
        data = list(records or ())
        payload: object = data[0] if len(data) == 1 else data
        QApplication.clipboard().setText(json.dumps(payload, indent=2, ensure_ascii=False))

    def _show_context_menu(self, position) -> None:
        index = self.table.indexAt(position)
        if index.isValid() and not self.table.selectionModel().isSelected(index):
            self.table.setCurrentIndex(index)
            self.table.selectionModel().select(
                index, QItemSelectionModel.SelectionFlag.ClearAndSelect
            )
        record = self.model.record_at(index.row()) if index.isValid() else None
        menu = QMenu(self.table)
        copy_action = menu.addAction("Auswahl kopieren (TSV)")
        copy_action.setEnabled(bool(self.table.selectionModel().selectedIndexes()))
        copy_action.triggered.connect(self.copy_selection_tsv)
        json_action = menu.addAction("Als JSON kopieren")
        json_action.setEnabled(bool(self._selected_records()))
        json_action.triggered.connect(self.copy_selected_json)
        if record is not None:
            menu.addSeparator()
            self._add_context_actions(menu, record)
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _add_context_actions(self, menu: QMenu, record: Any) -> None:
        for label, key, value in (
            ("Nur diese Session", "session_id", record.session_id),
            ("Nur diese Activation (diagnostisch)", "activation_id", record.activation_id),
            ("Nur dieses Segment", "segment_id", record.segment_id),
            ("Nur diesen Ereignistyp", "type_value", record.type),
            ("Nur diese Korrelation", "correlation_id", record.correlation_id),
            ("Nur dieses Command", "command_id", record.command_id),
            ("Nur dieses Event", "event_id", record.event_id),
        ):
            if value is None or value == "":
                continue
            action = menu.addAction(label)
            action.triggered.connect(
                lambda _checked=False, k=key, v=value: self.filter_bar.apply_context(**{k: v})
            )

    def _show_header_menu(self, position) -> None:
        menu = QMenu(self.table.horizontalHeader())
        visible_count = sum(not self.table.isColumnHidden(i) for i in range(self.model.columnCount()))
        for column, spec in enumerate(COLUMN_SPECS):
            action = QAction(spec.label, menu)
            action.setCheckable(True)
            action.setChecked(not self.table.isColumnHidden(column))
            action.setEnabled(action.isChecked() or visible_count > 0)
            action.toggled.connect(lambda checked, c=column: self._set_column_visible(c, checked))
            menu.addAction(action)
        menu.exec(self.table.horizontalHeader().mapToGlobal(position))

    def _set_column_visible(self, column: int, visible: bool) -> None:
        currently_visible = sum(not self.table.isColumnHidden(i) for i in range(self.model.columnCount()))
        if not visible and not self.table.isColumnHidden(column) and currently_visible <= 1:
            return
        self.table.setColumnHidden(column, not visible)
        self.save_view_state()

    def _on_sort_changed(self, column: int, order: Qt.SortOrder) -> None:
        if self._restoring_state or not 0 <= column < len(COLUMN_SPECS):
            return
        self.model.set_sort(COLUMN_SPECS[column].field, order)
        self.save_view_state()
        self.reload()

    def _follow_latest(self) -> None:
        if not self.autoscroll_box.isChecked() or self.model.sort_field not in TIME_FIELDS:
            return
        if self.model.sort_order == Qt.SortOrder.AscendingOrder:
            self.table.scrollToBottom()
        else:
            self.table.scrollToTop()

    def _on_scrolled(self, value: int) -> None:
        if self._mode in (MODE_HISTORY, MODE_MIXED):
            bar = self.table.verticalScrollBar()
            if value >= bar.maximum() - AUTO_LOAD_MARGIN:
                self.load_more()

    def _move_current(self, delta: int) -> None:
        if self.model.rowCount() == 0:
            return
        current = self.table.currentIndex()
        row = current.row() if current.isValid() else 0
        column = current.column() if current.isValid() else self.table.horizontalHeader().logicalIndex(0)
        row = max(0, min(self.model.rowCount() - 1, row + delta))
        self.table.setCurrentIndex(self.model.index(row, column))
        self.table.scrollTo(self.model.index(row, column))

    def _update_more_action(self) -> None:
        relevant = self._mode in (MODE_HISTORY, MODE_MIXED)
        self.more_button.setVisible(relevant)
        self.more_button.setEnabled(relevant and bool(self._next_cursor) and not self._loading)

    def _visible_columns_in_visual_order(self) -> list[int]:
        header = self.table.horizontalHeader()
        return sorted(
            (i for i in range(self.model.columnCount()) if not self.table.isColumnHidden(i)),
            key=header.visualIndex,
        )

    def _export_loaded(self, kind: str) -> None:
        if not self.model.records():
            return
        suffix = "csv" if kind == "csv" else "json"
        path, _selected = QFileDialog.getSaveFileName(
            self, "Geladene Diagnoseansicht exportieren", f"diagnose.{suffix}",
            "CSV-Datei (*.csv)" if kind == "csv" else "JSON-Datei (*.json)",
        )
        if not path:
            return
        try:
            if kind == "csv":
                columns = self._visible_columns_in_visual_order()
                with Path(path).open("w", encoding="utf-8-sig", newline="") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(COLUMN_SPECS[column].label for column in columns)
                    for row in range(self.model.rowCount()):
                        writer.writerow(self.model.data(self.model.index(row, column)) or "" for column in columns)
            else:
                payload = [_record_mapping(record) for record in self.model.records()]
                Path(path).write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            self.status_label.setText(f"{len(self.model.records())} geladene Records exportiert: {path}")
        except (OSError, ValueError) as exc:
            self.status_label.setText(f"Export fehlgeschlagen: {type(exc).__name__}: {exc}")

    def _restore_view_state(self) -> None:
        field = str(self._settings.value(SORT_FIELD_KEY, "received_at") or "received_at")
        if field not in COLUMN_INDEX:
            field = "received_at"
        descending = _settings_bool(self._settings.value(SORT_DESC_KEY, True), True)
        order = Qt.SortOrder.DescendingOrder if descending else Qt.SortOrder.AscendingOrder
        self.model.set_sort(field, order)

        restored = False
        state = self._settings.value(HEADER_STATE_KEY)
        if state:
            try:
                restored = bool(self.table.horizontalHeader().restoreState(state))
            except Exception:  # noqa: BLE001 - invalid settings fall back
                restored = False
        visible = self._settings.value(VISIBLE_COLUMNS_KEY, list(DEFAULT_VISIBLE_FIELDS))
        if isinstance(visible, str):
            visible = [visible]
        visible_set = {str(value) for value in (visible or ()) if str(value) in COLUMN_INDEX}
        if not visible_set:
            visible_set = set(DEFAULT_VISIBLE_FIELDS)
            restored = False
        for index, spec in enumerate(COLUMN_SPECS):
            self.table.setColumnHidden(index, spec.field not in visible_set)
        if not restored:
            for index, spec in enumerate(COLUMN_SPECS):
                self.table.setColumnWidth(index, 150 if spec.field not in ("message", "type") else 260)

        sort_column = COLUMN_INDEX[field]
        self.table.horizontalHeader().setSortIndicator(sort_column, order)
        splitter_state = self._settings.value(SPLITTER_STATE_KEY)
        if splitter_state:
            try:
                self.lower_splitter.restoreState(splitter_state)
            except Exception:  # noqa: BLE001
                pass

    def save_view_state(self) -> None:
        if self._restoring_state:
            return
        try:
            self._settings.setValue(HEADER_STATE_KEY, self.table.horizontalHeader().saveState())
            self._settings.setValue(
                VISIBLE_COLUMNS_KEY,
                [spec.field for index, spec in enumerate(COLUMN_SPECS) if not self.table.isColumnHidden(index)],
            )
            self._settings.setValue(SORT_FIELD_KEY, self.model.sort_field)
            self._settings.setValue(
                SORT_DESC_KEY, self.model.sort_order == Qt.SortOrder.DescendingOrder
            )
            self._settings.setValue(SPLITTER_STATE_KEY, self.lower_splitter.saveState())
        except Exception:  # noqa: BLE001 - a broken settings store never breaks the viewer
            pass

    def refresh_status(self) -> None:
        parts = []
        status = self._last_page_status
        if status is not None:
            state = getattr(getattr(status, "state", None), "value", "")
            detail = getattr(status, "detail", "")
            parts.append(f"Provider: {state}" + (f" – {detail}" if detail else ""))
        parts.append(f"{self.model.rowCount()} geladene Zeilen")
        direction = "↓" if self.model.sort_order == Qt.SortOrder.DescendingOrder else "↑"
        parts.append(f"Sortierung: {COLUMN_SPECS[COLUMN_INDEX[self.model.sort_field]].label} {direction}")
        if self._mode in (MODE_HISTORY, MODE_MIXED) and self._next_cursor:
            parts.append("weitere Historie verfügbar")
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
        except Exception:  # noqa: BLE001
            return None


def _latest_storage_cursor(records: tuple[Any, ...]) -> Optional[str]:
    candidates = []
    for record in records:
        cursor = str(getattr(record, "cursor", ""))
        if cursor.startswith("id:"):
            try:
                candidates.append((int(cursor[3:]), cursor))
            except ValueError:
                pass
    return max(candidates)[1] if candidates else None


def _record_mapping(record: Any) -> dict[str, Any]:
    if is_dataclass(record):
        return {
            item.name: _plain(getattr(record, item.name))
            for item in fields(record)
            if item.name != "cursor"
        }
    return {key: _plain(value) for key, value in vars(record).items() if not key.startswith("_")}


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


def _settings_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return default


def _health_text(snapshot: Any) -> str:
    state = getattr(getattr(snapshot, "state", None), "value", "?")
    dropped = (
        int(getattr(snapshot, "dropped_watermark", 0) or 0)
        + int(getattr(snapshot, "dropped_queue_full", 0) or 0)
        + int(getattr(snapshot, "dropped_shutdown", 0) or 0)
    )
    text = (
        f"Logging: {state} · geschrieben {getattr(snapshot, 'written', 0)}"
        f" · dedupliziert {getattr(snapshot, 'deduplicated', 0)}"
        f" · verworfen {dropped} · Queue {getattr(snapshot, 'queue_depth', 0)}"
    )
    detail = getattr(snapshot, "detail", "")
    return f"{text} – {detail}" if detail else text


__all__ = [
    "LogPage", "MODE_HISTORY", "MODE_LIVE", "MODE_MIXED", "LIVE_INTERVAL_MS",
]
