"""Optional, non-blocking and failure-tolerant sound feedback."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from PySide6.QtCore import QObject, QUrl
from PySide6.QtMultimedia import QSoundEffect

from core.config import FeedbackConfig

logger = logging.getLogger("ui.feedback")


class SoundFeedback(QObject):
    def __init__(self, config: FeedbackConfig, parent: Optional[QObject] = None):
        super().__init__(parent)
        self.config = config
        self._effect = QSoundEffect(self)

    def apply_config(self, config: FeedbackConfig) -> None:
        self.config = config

    def play(self, event: str) -> None:
        if not self.config.sounds_enabled:
            return
        path_value = {
            "start": self.config.start_sound,
            "stop": self.config.stop_sound,
            "cancel": self.config.cancel_sound,
        }.get(event)
        if not path_value:
            return
        path = Path(path_value).expanduser()
        if not path.is_file():
            logger.warning("Sound asset is unavailable: %s", path)
            return
        try:
            self._effect.stop()
            self._effect.setSource(QUrl.fromLocalFile(str(path.resolve())))
            self._effect.play()
        except Exception:
            logger.exception("Sound feedback failed for %s.", event)
