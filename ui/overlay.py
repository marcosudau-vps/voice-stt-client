"""Passive, focus-safe transcript and feedback overlay."""

from __future__ import annotations

from typing import Optional

from PySide6.QtCore import QEasingCurve, QPropertyAnimation, QTimer, Qt
from PySide6.QtGui import QGuiApplication
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.config import OverlayConfig
from ui.presentation import FeedbackPresentation, IndicatorColor


class TranscriptOverlay(QWidget):
    def __init__(
        self,
        config: OverlayConfig,
        parent: Optional[QWidget] = None,
    ) -> None:
        flags = (
            Qt.WindowType.Tool
            | Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
            | Qt.WindowType.WindowTransparentForInput
        )
        super().__init__(parent, flags)
        self.config = config
        self.setObjectName("transcriptOverlay")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        self.label = QLabel(self)
        self.label.setObjectName("transcriptLabel")
        self.label.setWordWrap(True)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        font = self.label.font()
        font.setPointSize(config.font_size)
        if config.font_family:
            font.setFamily(config.font_family)
        self.label.setFont(font)
        layout.addWidget(self.label)

        self.setFixedWidth(config.width)
        self.setMaximumHeight(config.max_height)
        self._base_opacity = float(config.opacity)
        self.setWindowOpacity(self._base_opacity)

        self._fade_timer = QTimer(self)
        self._fade_timer.setSingleShot(True)
        self._fade_timer.timeout.connect(self._begin_fade)
        self._alert_timer = QTimer(self)
        self._alert_timer.setSingleShot(True)
        self._alert_timer.timeout.connect(self.hide)
        self._fade_animation = QPropertyAnimation(self, b"windowOpacity", self)
        self._fade_animation.setDuration(250)
        self._fade_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._fade_animation.finished.connect(self._finish_fade)
        self._set_background(config.background_color)

    def _set_background(self, color: str) -> None:
        self.label.setStyleSheet(
            "QLabel {"
            f"background-color: {color};"
            f"color: {self.config.text_color};"
            "border-radius: 10px;"
            "padding: 10px 14px;"
            "}"
        )

    def show_transcript(self, text: str, is_final: bool) -> None:
        if not self.config.enabled or not text:
            return
        self._alert_timer.stop()
        self._fade_timer.stop()
        self._fade_animation.stop()
        self.setWindowOpacity(self._base_opacity)
        self._set_background(self.config.background_color)
        self.label.setText(text)
        self.adjustSize()
        if self.height() > self.config.max_height:
            self.resize(self.config.width, self.config.max_height)
        self.reposition()
        self.show()
        if is_final:
            delay_ms = max(0, int(self.config.fade_after * 1000))
            self._fade_timer.start(delay_ms)

    def show_feedback(self, feedback: FeedbackPresentation) -> None:
        if not self.config.enabled:
            return
        self._fade_timer.stop()
        self._fade_animation.stop()
        self.setWindowOpacity(self._base_opacity)
        self._set_background(feedback.color.value)
        self.label.setText(feedback.text)
        self.adjustSize()
        self.reposition()
        self.show()
        self._alert_timer.start(max(100, feedback.duration_ms))

    def show_hotkey_error(self) -> None:
        self.show_feedback(
            FeedbackPresentation(
                color=IndicatorColor.RED,
                text="Globale Hotkeys konnten nicht registriert werden",
                duration_ms=1800,
            )
        )

    def apply_config(self, config: OverlayConfig) -> None:
        self.config = config
        self.setFixedWidth(config.width)
        self.setMaximumHeight(config.max_height)
        self._base_opacity = float(config.opacity)
        self.setWindowOpacity(self._base_opacity)
        font = self.label.font()
        font.setPointSize(config.font_size)
        if config.font_family:
            font.setFamily(config.font_family)
        self.label.setFont(font)
        if not config.enabled:
            self.hide()

    def toggle_visibility(self) -> None:
        if self.isVisible():
            self.hide()
        elif self.config.enabled:
            self.reposition()
            self.show()

    def _begin_fade(self) -> None:
        if not self.isVisible():
            return
        self._fade_animation.stop()
        self._fade_animation.setStartValue(self.windowOpacity())
        self._fade_animation.setEndValue(0.0)
        self._fade_animation.start()

    def _finish_fade(self) -> None:
        if self.windowOpacity() <= 0.01:
            self.hide()
            self.setWindowOpacity(self._base_opacity)

    def reposition(self) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None:
            return
        geometry = screen.availableGeometry()
        margin = self.config.margin
        x_center = geometry.x() + (geometry.width() - self.width()) // 2
        y_center = geometry.y() + (geometry.height() - self.height()) // 2

        positions = {
            "bottom_center": (
                x_center,
                geometry.bottom() - self.height() - margin + 1,
            ),
            "top_right": (
                geometry.right() - self.width() - margin + 1,
                geometry.top() + margin,
            ),
            "top_left": (geometry.left() + margin, geometry.top() + margin),
            "bottom_right": (
                geometry.right() - self.width() - margin + 1,
                geometry.bottom() - self.height() - margin + 1,
            ),
            "bottom_left": (
                geometry.left() + margin,
                geometry.bottom() - self.height() - margin + 1,
            ),
        }
        x, y = positions.get(self.config.position, (x_center, y_center))
        self.move(x, y)
