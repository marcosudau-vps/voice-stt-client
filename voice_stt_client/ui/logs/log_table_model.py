"""Typed, configurable table model for the diagnostics viewer."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, List, Optional, Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

DEFAULT_MAX_ROWS = 5000
ORIGIN_HISTORY = "history"
ORIGIN_LIVE = "live"


@dataclass(frozen=True)
class ColumnSpec:
    field: str
    label: str
    kind: str = "text"
    default_visible: bool = False


COLUMN_SPECS = (
    ColumnSpec("received_at", "Zeit", "datetime", True),
    ColumnSpec("producer_kind", "Quelle", "text", True),
    ColumnSpec("channel", "Channel", "text", True),
    ColumnSpec("level", "Level", "level", True),
    ColumnSpec("type", "Ereignistyp", "text", True),
    ColumnSpec("component", "Component", "text", True),
    ColumnSpec("message", "Meldung", "text", True),
    ColumnSpec("record_id", "Record-ID"),
    ColumnSpec("session_id", "Session-ID"),
    ColumnSpec("generation", "Generation", "number"),
    ColumnSpec("activation_id", "Activation-ID"),
    ColumnSpec("segment_id", "Segment-ID", "number"),
    ColumnSpec("transcription_id", "Transcription-ID"),
    ColumnSpec("command_id", "Command-ID"),
    ColumnSpec("event_id", "Event-ID"),
    ColumnSpec("correlation_id", "Korrelations-ID"),
    ColumnSpec("producer_id", "Producer-ID"),
    ColumnSpec("instance_id", "Instance-ID"),
    ColumnSpec("scope", "Scope"),
    ColumnSpec("server_cursor", "Server-Cursor", "number"),
    ColumnSpec("replayed", "Wiederholt", "boolean"),
    ColumnSpec("source_timestamp", "Quellzeit", "datetime"),
)
COLUMNS = tuple(spec.label for spec in COLUMN_SPECS)
COLUMN_INDEX = {spec.field: index for index, spec in enumerate(COLUMN_SPECS)}
DEFAULT_VISIBLE_FIELDS = tuple(spec.field for spec in COLUMN_SPECS if spec.default_visible)
TIME_FIELDS = frozenset({"received_at", "source_timestamp"})

_LEVEL_COLORS = {
    "WARNING": QColor("#5a4a12"),
    "ERROR": QColor("#5a1f1f"),
    "CRITICAL": QColor("#701010"),
}
_LIVE_TINT = QColor(30, 144, 255, 34)
_HISTORY_TINT = QColor(128, 128, 128, 18)
_LEVEL_ORDER = {"DEBUG": 10, "INFO": 20, "WARNING": 30, "ERROR": 40, "CRITICAL": 50}


class LogTableModel(QAbstractTableModel):
    """Holds bounded records and keeps them in the active typed sort."""

    def __init__(self, parent: Optional[Any] = None, *, max_rows: int = DEFAULT_MAX_ROWS) -> None:
        super().__init__(parent)
        self._records: List[Any] = []
        self._origins: dict[tuple[str, str], str] = {}
        self._max_rows = max(1, int(max_rows))
        self._sort_field = "received_at"
        self._sort_order = Qt.SortOrder.DescendingOrder

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._records)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(COLUMN_SPECS)

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):  # noqa: N802
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal and 0 <= section < len(COLUMN_SPECS):
                return COLUMN_SPECS[section].label
            if orientation == Qt.Orientation.Vertical:
                return section + 1
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid() or not 0 <= index.row() < len(self._records):
            return None
        record = self._records[index.row()]
        spec = COLUMN_SPECS[index.column()]
        value = getattr(record, spec.field, None)
        if role == Qt.ItemDataRole.DisplayRole:
            return _display(value, spec.kind)
        if role == Qt.ItemDataRole.UserRole:
            return record
        if role == Qt.ItemDataRole.UserRole + 1:
            return _sort_value(value, spec.kind)
        if role == Qt.ItemDataRole.BackgroundRole:
            severity = _LEVEL_COLORS.get(str(getattr(record, "level", "")))
            if severity is not None:
                return severity
            return _LIVE_TINT if self.origin_at(index.row()) == ORIGIN_LIVE else _HISTORY_TINT
        if role == Qt.ItemDataRole.ForegroundRole:
            if str(getattr(record, "level", "")) in _LEVEL_COLORS:
                return QColor("#ffffff")
        if role == Qt.ItemDataRole.ToolTipRole:
            origin = "Live" if self.origin_at(index.row()) == ORIGIN_LIVE else "Historie"
            message = getattr(record, "message", None) or getattr(record, "type", None) or ""
            return f"{origin} · {message}"
        return None

    @property
    def max_rows(self) -> int:
        return self._max_rows

    @property
    def sort_field(self) -> str:
        return self._sort_field

    @property
    def sort_order(self) -> Qt.SortOrder:
        return self._sort_order

    def record_at(self, row: int) -> Optional[Any]:
        return self._records[row] if 0 <= row < len(self._records) else None

    def records(self) -> tuple:
        return tuple(self._records)

    def origin_at(self, row: int) -> str:
        record = self.record_at(row)
        return self._origins.get(_identity(record), ORIGIN_HISTORY) if record is not None else ORIGIN_HISTORY

    def clear(self) -> None:
        self.beginResetModel()
        self._records = []
        self._origins = {}
        self.endResetModel()

    def set_records(self, records: Sequence[Any], *, origin: str = ORIGIN_HISTORY) -> None:
        fresh = list(records)[-self._max_rows:]
        self.beginResetModel()
        self._records = fresh
        self._origins = {_identity(record): origin for record in fresh}
        self._sort_in_place()
        self.endResetModel()

    def append_page(self, records: Sequence[Any], *, origin: str = ORIGIN_HISTORY) -> int:
        new_records = list(records)
        if not new_records:
            return 0
        merged = list(self._records)
        positions = {_identity(record): index for index, record in enumerate(merged)}
        for record in new_records:
            key = _identity(record)
            if key in positions:
                merged[positions[key]] = record
            else:
                positions[key] = len(merged)
                merged.append(record)
            self._origins[key] = origin
        merged = merged[-self._max_rows:]
        keep = {_identity(record) for record in merged}
        self.beginResetModel()
        self._records = merged
        self._origins = {key: value for key, value in self._origins.items() if key in keep}
        self._sort_in_place()
        self.endResetModel()
        return len(new_records)

    def set_sort(self, field: str, order: Qt.SortOrder) -> None:
        if field not in COLUMN_INDEX:
            field = "received_at"
        self.beginResetModel()
        self._sort_field = field
        self._sort_order = order
        self._sort_in_place()
        self.endResetModel()

    def sort(self, column: int, order: Qt.SortOrder = Qt.SortOrder.AscendingOrder) -> None:
        if 0 <= column < len(COLUMN_SPECS):
            self.set_sort(COLUMN_SPECS[column].field, order)

    def _sort_in_place(self) -> None:
        spec = COLUMN_SPECS[COLUMN_INDEX[self._sort_field]]
        reverse = self._sort_order == Qt.SortOrder.DescendingOrder
        self._records.sort(
            key=lambda record: (
                _sort_value(getattr(record, spec.field, None), spec.kind),
                str(getattr(record, "record_id", "")),
            ),
            reverse=reverse,
        )


def _identity(record: Any) -> tuple[str, str]:
    return (str(getattr(record, "provider_id", "")), str(getattr(record, "record_id", "")))


def _display(value: Any, kind: str) -> str:
    if value is None:
        return ""
    if kind == "datetime":
        text = str(value)
        if "T" in text:
            text = text.replace("T", ", ", 1)
        return text[:-1] if text.endswith("Z") else text
    if kind == "boolean":
        return "Ja" if bool(value) else "Nein"
    return str(value)


def _sort_value(value: Any, kind: str) -> Any:
    if kind == "number":
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("-inf")
    if kind == "boolean":
        return 1 if bool(value) else 0
    if kind == "level":
        return _LEVEL_ORDER.get(str(value), 0)
    if kind == "datetime":
        if not value:
            return float("-inf")
        try:
            return datetime.fromisoformat(str(value).replace("Z", "+00:00")).timestamp()
        except (TypeError, ValueError, OverflowError):
            return float("-inf")
    return _sqlite_nocase_key("" if value is None else str(value))


def _sqlite_nocase_key(value: str) -> str:
    # SQLite's built-in NOCASE collation folds ASCII A-Z only. Matching it
    # here keeps local insertion of live rows consistent with the provider's
    # paginated ORDER BY, including non-ASCII event/component names.
    return str(value).translate(str.maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"))


__all__ = [
    "LogTableModel", "COLUMN_SPECS", "COLUMNS", "COLUMN_INDEX",
    "DEFAULT_VISIBLE_FIELDS", "TIME_FIELDS", "ORIGIN_HISTORY", "ORIGIN_LIVE",
]
