"""
``LogDetailView`` — record detail, ``details`` tree and ``raw`` JSON
(OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.3: *"Detail: QSplitter
unterhalb der Tabelle; ``details`` als Baum, ``raw`` als eingerücktes JSON,
**bei Auswahl nachgeladen**"* and §5.7 (``raw_json`` is never part of the
list query — it arrives through ``fetch_raw`` for the selected record only).

The header shows the fields §9.3 keeps out of the seven columns
(session/generation/activation/segment/transcription/command/event/
correlation/cursor/replayed), because they are filter and correlation keys,
not something to scan a table for.
"""

from __future__ import annotations

import json
from typing import Any, Mapping, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QLabel,
    QPlainTextEdit,
    QTabWidget,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

RAW_PLACEHOLDER = "Kein raw-Payload gespeichert."
RAW_LOADING = "raw wird geladen …"
NO_SELECTION = "Kein Record ausgewählt."


class LogDetailView(QWidget):
    """Shows one ``LogRecordView`` plus its lazily loaded ``raw`` payload."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.header = QLabel(NO_SELECTION)
        self.header.setWordWrap(True)
        # Copyable: a record_id or correlation_id in the header is exactly
        # what someone pastes into the filter bar next.
        self.header.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
        )
        layout.addWidget(self.header)

        self.tabs = QTabWidget(self)
        self.details_tree = QTreeWidget(self)
        self.details_tree.setColumnCount(2)
        self.details_tree.setHeaderLabels(("Feld", "Wert"))
        self.tabs.addTab(self.details_tree, "details")

        self.raw_view = QPlainTextEdit(self)
        self.raw_view.setReadOnly(True)
        self.raw_view.setPlainText(NO_SELECTION)
        self.tabs.addTab(self.raw_view, "raw")
        layout.addWidget(self.tabs)

        self._record: Optional[Any] = None

    @property
    def record(self) -> Optional[Any]:
        return self._record

    def clear(self) -> None:
        self._record = None
        self.header.setText(NO_SELECTION)
        self.details_tree.clear()
        self.raw_view.setPlainText(NO_SELECTION)

    def show_record(self, record: Any) -> None:
        """Render one record. ``raw`` stays a placeholder until
        :meth:`set_raw` delivers it — the list query never carries it."""
        self._record = record
        if record is None:
            self.clear()
            return
        self.header.setText(self._header_text(record))
        self.details_tree.clear()
        details = getattr(record, "details", None) or {}
        _fill_tree(self.details_tree.invisibleRootItem(), details)
        self.details_tree.expandToDepth(1)
        self.raw_view.setPlainText(RAW_LOADING)

    def set_raw(self, record_id: str, raw: Optional[Mapping[str, Any]]) -> None:
        """Install a loaded ``raw`` payload, but only if it still belongs to
        the selected record — the load is asynchronous and the selection may
        have moved on."""
        current = self._record
        if current is None or str(getattr(current, "record_id", "")) != str(record_id):
            return
        if not raw:
            self.raw_view.setPlainText(RAW_PLACEHOLDER)
            return
        self.raw_view.setPlainText(_pretty_json(raw))

    @staticmethod
    def _header_text(record: Any) -> str:
        def value(name: str) -> str:
            item = getattr(record, name, None)
            return "—" if item is None or item == "" else str(item)

        return (
            f"{value('received_at')} · {value('level')} · {value('channel')} · "
            f"{value('producer_kind')}/{value('producer_id')}\n"
            f"type={value('type')} component={value('component')} "
            f"record_id={value('record_id')}\n"
            f"session={value('session_id')} generation={value('generation')} "
            f"activation={value('activation_id')} segment={value('segment_id')}\n"
            f"transcription={value('transcription_id')} command={value('command_id')} "
            f"event={value('event_id')} correlation={value('correlation_id')}\n"
            f"instance={value('instance_id')} scope={value('scope')} "
            f"server_cursor={value('server_cursor')} replayed={value('replayed')}\n"
            f"source_timestamp={value('source_timestamp')}\n"
            f"{value('message')}"
        )


def _pretty_json(value: Any) -> str:
    try:
        return json.dumps(_plain(value), indent=2, ensure_ascii=False, sort_keys=False)
    except Exception:  # noqa: BLE001 - a detail view never raises over content
        return str(value)


def _plain(value: Any) -> Any:
    """Frozen containers (``MappingProxyType``, tuple, frozenset) travel with
    the record; ``json.dumps`` knows none of them."""
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return sorted(str(item) for item in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _fill_tree(parent: QTreeWidgetItem, value: Any, *, depth: int = 0) -> None:
    """Render a mapping as a two-column tree.

    The depth guard mirrors R-12's reason rather than its exact number: a
    pathologically deep ``details`` must not be able to hang the Qt thread in
    a view.
    """
    if depth > 16:
        parent.addChild(QTreeWidgetItem(["…", "(zu tief verschachtelt)"]))
        return
    if isinstance(value, Mapping):
        for key, item in value.items():
            if isinstance(item, (Mapping, list, tuple, set, frozenset)):
                node = QTreeWidgetItem([str(key), ""])
                parent.addChild(node)
                _fill_tree(node, item, depth=depth + 1)
            else:
                parent.addChild(QTreeWidgetItem([str(key), _scalar(item)]))
        return
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            if isinstance(item, (Mapping, list, tuple, set, frozenset)):
                node = QTreeWidgetItem([f"[{index}]", ""])
                parent.addChild(node)
                _fill_tree(node, item, depth=depth + 1)
            else:
                parent.addChild(QTreeWidgetItem([f"[{index}]", _scalar(item)]))
        return
    if isinstance(value, (set, frozenset)):
        for index, item in enumerate(sorted(str(entry) for entry in value)):
            parent.addChild(QTreeWidgetItem([f"[{index}]", item]))
        return
    parent.addChild(QTreeWidgetItem(["", _scalar(value)]))


def _scalar(value: Any) -> str:
    return "null" if value is None else str(value)


__all__ = ["LogDetailView", "RAW_PLACEHOLDER", "NO_SELECTION"]
