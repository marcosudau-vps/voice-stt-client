"""
``LogTableModel`` — the seven-column model behind the log table (OBS-050).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.3:

* **seven columns**: Zeit (``received_at``), Quelle (``producer_kind``),
  Channel, Level, Typ, Component, Meldung. Session/Activation/Segment are
  filter criteria and detail fields, **not** columns.
* ``QAbstractTableModel`` + ``QTableView`` — *"Erste Einfuehrung dieses
  Musters im Repository ... Deshalb bewusst klein halten."* The repository's
  existing ``QTableWidget`` pattern rebuilds every item on every refresh,
  which is exactly what 200.000 rows must not do.
* **Farben**: only a row colour by ``level`` (WARNING/ERROR/CRITICAL).

The row count is bounded (``max_rows``). Live tailing appends forever
otherwise, and O-04 (*"Jede Queue und jeder Puffer ist begrenzt"*) is not
suspended just because the buffer happens to live in a table model. Trimming
drops the oldest rows, which in both modes are the ones furthest from what
the reader is looking at.
"""

from __future__ import annotations

from typing import Any, List, Optional, Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtGui import QColor

COLUMNS = ("Zeit", "Quelle", "Channel", "Level", "Typ", "Component", "Meldung")
DEFAULT_MAX_ROWS = 5000

# §9.3: "nur Zeilenfarbe nach level (WARNING/ERROR/CRITICAL)".
_LEVEL_COLORS = {
    "WARNING": QColor("#5a4a12"),
    "ERROR": QColor("#5a1f1f"),
    "CRITICAL": QColor("#701010"),
}


class LogTableModel(QAbstractTableModel):
    """Holds ``LogRecordView`` objects; renders seven columns of them."""

    def __init__(self, parent: Optional[Any] = None, *, max_rows: int = DEFAULT_MAX_ROWS) -> None:
        super().__init__(parent)
        self._records: List[Any] = []
        self._max_rows = max(1, int(max_rows))

    # -- QAbstractTableModel ---------------------------------------------

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(self._records)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:  # noqa: N802
        return 0 if parent.isValid() else len(COLUMNS)

    def headerData(  # noqa: N802
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        if role != Qt.ItemDataRole.DisplayRole:
            return None
        if orientation == Qt.Orientation.Horizontal and 0 <= section < len(COLUMNS):
            return COLUMNS[section]
        return None

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        row, column = index.row(), index.column()
        if not 0 <= row < len(self._records):
            return None
        record = self._records[row]
        if role == Qt.ItemDataRole.DisplayRole:
            return self._cell(record, column)
        if role == Qt.ItemDataRole.BackgroundRole:
            return _LEVEL_COLORS.get(getattr(record, "level", ""))
        if role == Qt.ItemDataRole.UserRole:
            return record
        if role == Qt.ItemDataRole.ToolTipRole:
            return getattr(record, "message", None) or getattr(record, "type", None)
        return None

    @staticmethod
    def _cell(record: Any, column: int) -> Any:
        if column == 0:
            return getattr(record, "received_at", "")
        if column == 1:
            return getattr(record, "producer_kind", "")
        if column == 2:
            return getattr(record, "channel", "")
        if column == 3:
            return getattr(record, "level", "")
        if column == 4:
            return getattr(record, "type", None) or ""
        if column == 5:
            return getattr(record, "component", None) or ""
        if column == 6:
            return getattr(record, "message", None) or ""
        return ""

    # -- content ----------------------------------------------------------

    @property
    def max_rows(self) -> int:
        return self._max_rows

    def record_at(self, row: int) -> Optional[Any]:
        if 0 <= row < len(self._records):
            return self._records[row]
        return None

    def records(self) -> tuple:
        return tuple(self._records)

    def clear(self) -> None:
        self.beginResetModel()
        self._records = []
        self.endResetModel()

    def set_records(self, records: Sequence[Any]) -> None:
        self.beginResetModel()
        self._records = list(records)[-self._max_rows:]
        self.endResetModel()

    def append_page(self, records: Sequence[Any]) -> int:
        """Append one page in the order the provider delivered it.

        Returns the number of rows actually appended. Trimming happens after
        the insert, as its own model reset, so the two operations never
        overlap in a single ``beginInsertRows`` block — a view that reads row
        indices between them would otherwise see indices that no longer mean
        what they meant.
        """
        new_records = list(records)
        if not new_records:
            return 0
        first = len(self._records)
        self.beginInsertRows(QModelIndex(), first, first + len(new_records) - 1)
        self._records.extend(new_records)
        self.endInsertRows()
        self._trim()
        return len(new_records)

    def _trim(self) -> None:
        excess = len(self._records) - self._max_rows
        if excess <= 0:
            return
        self.beginRemoveRows(QModelIndex(), 0, excess - 1)
        del self._records[:excess]
        self.endRemoveRows()


__all__ = ["LogTableModel", "COLUMNS", "DEFAULT_MAX_ROWS"]
