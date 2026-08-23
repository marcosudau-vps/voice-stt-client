"""
``LogDetailView`` — record detail, ``details`` tree and ``raw`` JSON
(OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.3: *"Detail: QSplitter
unterhalb der Tabelle; ``details`` als Baum, ``raw`` als eingerücktes JSON,
**bei Auswahl nachgeladen**"* and §5.7 (``raw_json`` is never part of the
list query — it arrives through ``fetch_raw`` for the selected record only).

All standard record fields and structured details live inside the Details
tab. Raw is loaded separately for the current record and never left over
from a previous selection.
"""

from __future__ import annotations

import json
from typing import Any, Mapping, Optional

from PySide6.QtWidgets import (
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

_RECORD_FIELDS = (
    ("received_at", "Zeit"), ("source_timestamp", "Quellzeit"),
    ("level", "Level"), ("channel", "Channel"),
    ("producer_kind", "Quelle"), ("producer_id", "Producer-ID"),
    ("type", "Ereignistyp"), ("component", "Component"),
    ("message", "Meldung"), ("record_id", "Record-ID"),
    ("session_id", "Session-ID"), ("generation", "Generation"),
    ("activation_id", "Activation-ID"), ("segment_id", "Segment-ID"),
    ("transcription_id", "Transcription-ID"), ("command_id", "Command-ID"),
    ("event_id", "Event-ID"), ("correlation_id", "Korrelations-ID"),
    ("instance_id", "Instance-ID"), ("scope", "Scope"),
    ("server_cursor", "Server-Cursor"), ("replayed", "Wiederholt"),
)


class LogDetailView(QWidget):
    """Shows one ``LogRecordView`` plus its lazily loaded ``raw`` payload."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget(self)
        self.details_tree = QTreeWidget(self)
        self.details_tree.setColumnCount(2)
        self.details_tree.setHeaderLabels(("Feld", "Wert"))
        self.tabs.addTab(self.details_tree, "Details")

        self.raw_view = QPlainTextEdit(self)
        self.raw_view.setReadOnly(True)
        self.raw_view.setPlainText(NO_SELECTION)
        self.tabs.addTab(self.raw_view, "Raw")
        layout.addWidget(self.tabs)

        self._record: Optional[Any] = None
        self.clear()

    @property
    def record(self) -> Optional[Any]:
        return self._record

    def clear(self) -> None:
        self._record = None
        self.details_tree.clear()
        self.details_tree.addTopLevelItem(QTreeWidgetItem([NO_SELECTION, ""]))
        self.raw_view.setPlainText(NO_SELECTION)

    def show_record(self, record: Any) -> None:
        """Render one record. ``raw`` stays a placeholder until
        :meth:`set_raw` delivers it — the list query never carries it."""
        self._record = record
        if record is None:
            self.clear()
            return
        self.details_tree.clear()
        record_node = QTreeWidgetItem(["Record", ""])
        self.details_tree.addTopLevelItem(record_node)
        for name, label in _RECORD_FIELDS:
            record_node.addChild(
                QTreeWidgetItem([label, _scalar(getattr(record, name, None))])
            )
        details = getattr(record, "details", None) or {}
        details_node = QTreeWidgetItem(["Details", ""])
        self.details_tree.addTopLevelItem(details_node)
        _fill_tree(details_node, details)
        self.details_tree.expandToDepth(2)
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
