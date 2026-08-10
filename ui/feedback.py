"""Optional, non-blocking and failure-tolerant mapped sound feedback."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable, Optional

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect

from core.config import FeedbackConfig
from core.feedback_mapping import SoundCueId, SoundEffect as MappedSoundEffect

logger = logging.getLogger("ui.feedback")


class SoundFeedback(QObject):
    failure = Signal(str)

    def __init__(
        self,
        config: FeedbackConfig,
        parent: Optional[QObject] = None,
        *,
        effect_factory: Optional[Callable[[QObject], QSoundEffect]] = None,
    ):
        super().__init__(parent)
        self.config = config
        self._effect = (effect_factory or QSoundEffect)(self)
        self._reported_failures: set[str] = set()
        self._current_cue: Optional[SoundCueId] = None
        status_changed = getattr(self._effect, "statusChanged", None)
        if status_changed is not None:
            status_changed.connect(self._check_status)

    def apply_config(self, config: FeedbackConfig) -> None:
        self.config = config
        self._reported_failures.clear()

    def play(self, effect: Optional[MappedSoundEffect]) -> bool:
        if not self.config.sounds_enabled or effect is None:
            return False
        path_value = self._path_for_cue(effect.cue)
        if not path_value:
            return False
        path = Path(path_value).expanduser()
        if not path.is_file():
            self._report_failure(
                f"missing:{effect.cue.value}:{path}",
                "Sound asset is unavailable: %s",
                path,
            )
            return False
        try:
            self._current_cue = effect.cue
            self._effect.stop()
            self._effect.setVolume(float(effect.volume))
            self._effect.setSource(QUrl.fromLocalFile(str(path.resolve())))
            self._effect.play()
            return True
        except Exception:
            self._report_failure(
                f"backend:{effect.cue.value}",
                "Sound feedback failed for %s.",
                effect.cue.value,
                exception=True,
            )
            return False

    def _path_for_cue(self, cue: SoundCueId) -> Optional[str]:
        return {
            SoundCueId.WAKE_WORD: self.config.wake_word_sound,
            SoundCueId.START: self.config.start_sound,
            SoundCueId.STOP: self.config.stop_sound,
            SoundCueId.COMPLETE: self.config.complete_sound,
            SoundCueId.CANCEL: self.config.cancel_sound,
            SoundCueId.WARNING: self.config.warning_sound,
            SoundCueId.ERROR: self.config.error_sound,
        }[cue]

    def _check_status(self) -> None:
        if self._current_cue is None:
            return
        try:
            is_error = self._effect.status() == QSoundEffect.Status.Error
        except Exception:
            is_error = True
        if is_error:
            self._report_failure(
                f"load:{self._current_cue.value}",
                "Sound backend could not load cue %s.",
                self._current_cue.value,
            )

    def _report_failure(
        self,
        key: str,
        message: str,
        *args: object,
        exception: bool = False,
    ) -> None:
        if key in self._reported_failures:
            return
        if len(self._reported_failures) >= 64:
            self._reported_failures.pop()
        self._reported_failures.add(key)
        if exception:
            logger.exception(message, *args)
        else:
            logger.warning(message, *args)
        self.failure.emit(key)
