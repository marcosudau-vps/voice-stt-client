"""Optional, non-blocking and failure-tolerant mapped sound feedback."""

from __future__ import annotations

import logging
from pathlib import Path
import sys
from typing import Callable, Optional

from PySide6.QtCore import QObject, QUrl, Signal
from PySide6.QtMultimedia import QSoundEffect

from core.config import FeedbackConfig
from core.feedback_mapping import SoundCueId, SoundEffect as MappedSoundEffect

logger = logging.getLogger("ui.feedback")


def application_resource_root() -> Path:
    """Return the stable root for source and PyInstaller data files."""
    frozen_root = getattr(sys, "_MEIPASS", None)
    if frozen_root:
        return Path(frozen_root)
    return Path(__file__).resolve().parent.parent


def resolve_sound_asset(path_value: str, *, resource_root: Path | None = None) -> Path:
    """Resolve an external absolute path or one bundled application asset."""
    path = Path(path_value).expanduser()
    if path.is_absolute():
        return path
    return (resource_root or application_resource_root()) / path


class SoundFeedback(QObject):
    failure = Signal(str)

    def __init__(
        self,
        config: FeedbackConfig,
        parent: Optional[QObject] = None,
        *,
        effect_factory: Optional[Callable[[QObject], QSoundEffect]] = None,
        resource_root: Path | None = None,
    ):
        super().__init__(parent)
        self.config = config
        self._effect_factory = effect_factory or QSoundEffect
        self._resource_root = resource_root
        self._effects: dict[SoundCueId, QSoundEffect] = {}
        self._reported_failures: set[str] = set()

    def apply_config(self, config: FeedbackConfig) -> None:
        for effect in self._effects.values():
            try:
                effect.stop()
                effect.deleteLater()
            except Exception:
                logger.debug("Could not release old sound effect.", exc_info=True)
        self._effects.clear()
        self.config = config
        self._reported_failures.clear()

    def play(self, effect: Optional[MappedSoundEffect]) -> bool:
        if not self.config.sounds_enabled or effect is None:
            return False
        if effect.action == "stop":
            player = self._effects.get(effect.cue)
            if player is None:
                return False
            player.stop()
            return True
        if effect.cue is not SoundCueId.TIMEOUT_TICK:
            timeout_player = self._effects.get(SoundCueId.TIMEOUT_TICK)
            if timeout_player is not None:
                timeout_player.stop()
        path_value = self._path_for_cue(effect.cue)
        if not path_value:
            return False
        path = resolve_sound_asset(path_value, resource_root=self._resource_root)
        if not path.is_file():
            self._report_failure(
                f"missing:{effect.cue.value}:{path}",
                "Sound asset is unavailable: %s",
                path,
            )
            return False
        try:
            player = self._effect_for_cue(effect.cue)
            source = QUrl.fromLocalFile(str(path.resolve()))
            if player.source() != source:
                player.setSource(source)
            player.setVolume(float(effect.volume))
            player.play()
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
            SoundCueId.TIMEOUT_TICK: self.config.timeout_tick_sound,
        }[cue]

    def _effect_for_cue(self, cue: SoundCueId) -> QSoundEffect:
        existing = self._effects.get(cue)
        if existing is not None:
            return existing
        effect = self._effect_factory(self)
        status_changed = getattr(effect, "statusChanged", None)
        if status_changed is not None:
            status_changed.connect(
                lambda *_, selected=cue, player=effect: self._check_status(
                    selected, player
                )
            )
        self._effects[cue] = effect
        return effect

    def _check_status(self, cue: SoundCueId, effect: QSoundEffect) -> None:
        try:
            is_error = effect.status() == QSoundEffect.Status.Error
        except Exception:
            is_error = True
        if is_error:
            self._report_failure(
                f"load:{cue.value}",
                "Sound backend could not load cue %s.",
                cue.value,
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


__all__ = ["SoundFeedback", "application_resource_root", "resolve_sound_asset"]
