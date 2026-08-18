"""System tray presentation and history actions for AP06."""

from __future__ import annotations

from typing import Callable, Iterable, Optional

from PySide6.QtCore import QObject, QTimer, Qt
from PySide6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from core.controller import AvailabilityState, ControllerStatusSnapshot
from core.event_models import CanonicalEventType
from core.feedback_reducer import FeedbackDecision
from core.history import HistoryEntry
from ui.presentation import (
    IndicatorColor,
    MappedAppPresentation,
    format_history_label,
    presentation_for_mapped_action,
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
        on_switch_led_sink: Optional[Callable[[], None]] = None,
        on_toggle_mute: Optional[Callable[[bool], None]] = None,
        on_reconnect_device: Optional[Callable[[], None]] = None,
        on_reconnect_server: Optional[Callable[[], None]] = None,
        on_show_logs: Optional[Callable[[], None]] = None,
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

        self.mute_action = QAction("Mikrofon stummschalten", self.menu)
        self.mute_action.setCheckable(True)
        if on_toggle_mute is not None:
            self.mute_action.toggled.connect(on_toggle_mute)
        self.menu.addAction(self.mute_action)

        self.history_menu = self.menu.addMenu("Verlauf")
        self.history_menu.aboutToShow.connect(self._request_history)
        self._set_history_placeholder("Verlauf wird geladen …")

        self.menu.addSeparator()
        self.reconnect_menu = self.menu.addMenu("Neu verbinden")
        self.reconnect_device_action = QAction("ReSpeaker", self.reconnect_menu)
        if on_reconnect_device is not None:
            self.reconnect_device_action.triggered.connect(on_reconnect_device)
        self.reconnect_menu.addAction(self.reconnect_device_action)
        self.reconnect_server_action = QAction("Server", self.reconnect_menu)
        if on_reconnect_server is not None:
            self.reconnect_server_action.triggered.connect(on_reconnect_server)
        self.reconnect_menu.addAction(self.reconnect_server_action)

        self.menu.addSeparator()
        # CONTRACTS §9.1: the log view is reachable "ueber das Tray-Menue und
        # ueber einen Knopf im Logging-Tab". Disabled rather than hidden when
        # there is no query service, so its absence is visible instead of
        # looking like a missing feature.
        self.logs_action = QAction("Logs anzeigen …", self.menu)
        self.logs_action.setEnabled(on_show_logs is not None)
        if on_show_logs is not None:
            self.logs_action.triggered.connect(on_show_logs)
        self.menu.addAction(self.logs_action)

        self.settings_action = QAction("Einstellungen …", self.menu)
        self.settings_action.setEnabled(on_settings is not None)
        if on_settings is not None:
            self.settings_action.triggered.connect(on_settings)
        self.menu.addAction(self.settings_action)

        # Only ever shown when the ring has been unreachable for a while and a
        # simulator is installed. Hidden rather than absent so the wiring is in
        # one place and the decision to reveal it stays with the application.
        self.led_sink_action = QAction("Auf LED-Simulation umschalten", self.menu)
        self.led_sink_action.setVisible(False)
        if on_switch_led_sink is not None:
            self.led_sink_action.triggered.connect(on_switch_led_sink)
        self.menu.addAction(self.led_sink_action)

        self.quit_action = QAction("Beenden", self.menu)
        self.quit_action.triggered.connect(on_quit)
        self.menu.addAction(self.quit_action)

        self.tray.setContextMenu(self.menu)
        self.tray.setIcon(create_status_icon(IndicatorColor.YELLOW))
        self.tray.setToolTip("RealtimeSTT – Startet")
        self._last_snapshot: Optional[ControllerStatusSnapshot] = None
        self._base_presentation = None
        self._feedback_override: Optional[MappedAppPresentation] = None
        self._event_stream_note: Optional[str] = None
        self._feedback_timer = QTimer(self)
        self._feedback_timer.setSingleShot(True)
        self._feedback_timer.timeout.connect(self._restore_base_presentation)

    def set_muted(self, muted: bool, *, on_device: bool = False) -> None:
        """Reflect the mute state without re-triggering the toggle."""
        blocked = self.mute_action.blockSignals(True)
        try:
            self.mute_action.setChecked(muted)
        finally:
            self.mute_action.blockSignals(blocked)
        if not muted:
            self.mute_action.setText("Mikrofon stummschalten")
        elif on_device:
            self.mute_action.setText("Stummschaltung aufheben")
        else:
            # Said plainly, because the mute LED on the device stays dark and
            # somebody looking at it would otherwise think nothing happened.
            self.mute_action.setText("Stummschaltung aufheben (nur Client)")

    def offer_led_simulation(self, offered: bool, label: str | None = None) -> None:
        """Reveal or hide the switch, and say so once when it appears."""
        if label is not None:
            self.led_sink_action.setText(label)
        was_visible = self.led_sink_action.isVisible()
        self.led_sink_action.setVisible(offered)
        if offered and not was_visible:
            self.notify(
                "ReSpeaker nicht erreichbar",
                "Im Tray-Menü lässt sich auf die LED-Simulation umschalten.",
            )

    def notify(self, title: str, message: str) -> None:
        """A balloon, if the system has them. Never a dialog: this is a tray app
        and a modal box over somebody's work is not a notification."""
        if self.tray.supportsMessages():
            self.tray.showMessage(title, message, self.tray.icon(), 8000)

    def show(self) -> None:
        self.tray.show()

    def hide(self) -> None:
        self.tray.hide()

    def update_snapshot(self, snapshot: ControllerStatusSnapshot) -> None:
        self._last_snapshot = snapshot
        self._base_presentation = presentation_for_snapshot(snapshot)
        if snapshot.availability_state is not AvailabilityState.READY:
            self._feedback_override = None
            self._feedback_timer.stop()
        presentation = self._feedback_override or self._base_presentation
        self.status_action.setText(presentation.status_text)
        self.toggle_action.setText(self._base_presentation.toggle_text)
        self.toggle_action.setEnabled(self._base_presentation.toggle_enabled)
        self._set_tooltip(presentation.status_text)
        self.tray.setIcon(
            create_status_icon(
                presentation.color,
                border_color=presentation.border_color,
            )
        )

    def update_feedback_decision(self, decision: FeedbackDecision) -> None:
        """Apply only configured in-app effects; transport state stays secondary."""
        if not decision.publish or decision.replay:
            return
        event_type = decision.event.event_type if decision.event is not None else None
        if event_type in {
            CanonicalEventType.CLIENT_EVENT_STREAM_CONNECTING,
            CanonicalEventType.CLIENT_EVENT_STREAM_REPLAYING,
            CanonicalEventType.CLIENT_EVENT_STREAM_DEGRADED,
            CanonicalEventType.CLIENT_EVENT_STREAM_LIVE,
        }:
            self._update_event_stream_note(event_type)
            if event_type is not CanonicalEventType.CLIENT_EVENT_STREAM_LIVE:
                return
        if decision.rule.app is None:
            return
        operating_mode = (
            self._last_snapshot.operating_mode
            if self._last_snapshot is not None
            else "hotkey"
        )
        presentation = presentation_for_mapped_action(
            decision.rule.app.action,
            operating_mode=operating_mode,
        )
        self._feedback_override = presentation
        self.status_action.setText(presentation.status_text)
        self._set_tooltip(presentation.status_text)
        self.tray.setIcon(
            create_status_icon(
                presentation.color,
                border_color=presentation.border_color,
            )
        )
        self._feedback_timer.stop()
        if presentation.duration_ms is not None:
            self._feedback_timer.start(presentation.duration_ms)

    def _update_event_stream_note(self, event_type: CanonicalEventType) -> None:
        self._event_stream_note = {
            CanonicalEventType.CLIENT_EVENT_STREAM_CONNECTING: (
                "Event-Feedback verbindet"
            ),
            CanonicalEventType.CLIENT_EVENT_STREAM_REPLAYING: (
                "Event-Feedback wird synchronisiert"
            ),
            CanonicalEventType.CLIENT_EVENT_STREAM_DEGRADED: (
                "Event-Feedback eingeschränkt; STT-Fallback aktiv"
            ),
            CanonicalEventType.CLIENT_EVENT_STREAM_LIVE: None,
        }[event_type]
        current_text = (
            self._feedback_override.status_text
            if self._feedback_override is not None
            else self._base_presentation.status_text
            if self._base_presentation is not None
            else self.status_action.text()
        )
        self._set_tooltip(current_text)

    def _restore_base_presentation(self) -> None:
        self._feedback_override = None
        if self._last_snapshot is not None:
            self.update_snapshot(self._last_snapshot)

    def _set_tooltip(self, status_text: str) -> None:
        if self._base_presentation is not None:
            tooltip = self._base_presentation.tooltip
            if status_text != self._base_presentation.status_text:
                tooltip = f"RealtimeSTT – {status_text}"
        else:
            tooltip = f"RealtimeSTT – {status_text}"
        if self._event_stream_note:
            tooltip = f"{tooltip}\n{self._event_stream_note}"
        self.tray.setToolTip(tooltip)

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
