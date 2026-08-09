"""System tray presentation and history actions for AP06."""

from __future__ import annotations

from typing import Callable, Iterable, Optional

from PySide6.QtCore import QObject, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from core.controller import ControllerStatusSnapshot
from core.history import HistoryEntry
from ui.presentation import (
    IndicatorColor,
    format_history_label,
    presentation_for_snapshot,
)


def create_status_icon(
    color: IndicatorColor | str,
    size: int = 32,
    *,
    border_color: Optional[str] = None,
) -> QIcon:
    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    if border_color is None:
        painter.setPen(QPen(QColor("#20242a"), 1))
    else:
        painter.setPen(QPen(QColor(border_color), max(2, size // 10)))
    painter.setBrush(QColor(color.value if isinstance(color, IndicatorColor) else color))
    margin = max(2, size // 8)
    painter.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
    painter.end()
    return QIcon(pixmap)


class TrayController(QObject):
    def __init__(
        self,
        *,
        on_toggle: Callable[[], None],
        on_reinsert_last: Callable[[], None],
        on_reinsert_entry: Callable[[str], None],
        on_request_history: Callable[[], None],
        on_quit: Callable[[], None],
        on_settings: Optional[Callable[[], None]] = None,
        parent: Optional[QObject] = None,
    ) -> None:
        super().__init__(parent)
        self._on_request_history = on_request_history
        self._on_reinsert_entry = on_reinsert_entry
        self.tray = QSystemTrayIcon(self)
        self.menu = QMenu()

        self.status_action = QAction("Startet", self.menu)
        self.status_action.setEnabled(False)
        self.menu.addAction(self.status_action)
        self.menu.addSeparator()

        self.toggle_action = QAction("Diktat starten", self.menu)
        self.toggle_action.triggered.connect(on_toggle)
        self.menu.addAction(self.toggle_action)

        self.reinsert_last_action = QAction(
            "Letztes Transkript erneut einfügen", self.menu
        )
        self.reinsert_last_action.triggered.connect(on_reinsert_last)
        self.menu.addAction(self.reinsert_last_action)

        self.history_menu = self.menu.addMenu("Verlauf")
        self.history_menu.aboutToShow.connect(self._request_history)
        self._set_history_placeholder("Verlauf wird geladen …")

        self.menu.addSeparator()
        self.settings_action = QAction("Einstellungen …", self.menu)
        self.settings_action.setEnabled(on_settings is not None)
        if on_settings is not None:
            self.settings_action.triggered.connect(on_settings)
        self.menu.addAction(self.settings_action)

        self.quit_action = QAction("Beenden", self.menu)
        self.quit_action.triggered.connect(on_quit)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)
        self.tray.setIcon(create_status_icon(IndicatorColor.YELLOW))
        self.tray.setToolTip("RealtimeSTT – Startet")

    def show(self) -> None:
        self.tray.show()

    def hide(self) -> None:
        self.tray.hide()

    def update_snapshot(self, snapshot: ControllerStatusSnapshot) -> None:
        presentation = presentation_for_snapshot(snapshot)
        self.status_action.setText(presentation.status_text)
        self.toggle_action.setText(presentation.toggle_text)
        self.toggle_action.setEnabled(presentation.toggle_enabled)
        self.tray.setToolTip(presentation.tooltip)
        self.tray.setIcon(
            create_status_icon(
                presentation.color,
                border_color=presentation.border_color,
            )
        )

    def _request_history(self) -> None:
        self._set_history_placeholder("Verlauf wird geladen …")
        self._on_request_history()

    def _set_history_placeholder(self, text: str) -> None:
        self.history_menu.clear()
        action = QAction(text, self.history_menu)
        action.setEnabled(False)
        self.history_menu.addAction(action)

    def set_history_entries(self, entries: Iterable[HistoryEntry]) -> None:
        entry_list = list(entries)
        self.history_menu.clear()
        if not entry_list:
            self._set_history_placeholder("Noch keine Transkripte")
            return

        for entry in entry_list:
            action = QAction(format_history_label(entry), self.history_menu)
            action.setData(entry.id)
            action.triggered.connect(
                lambda checked=False, entry_id=entry.id: self._on_reinsert_entry(
                    entry_id
                )
            )
            self.history_menu.addAction(action)
