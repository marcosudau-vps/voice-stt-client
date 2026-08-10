from __future__ import annotations

import os
from pathlib import Path
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QApplication

from core.config import FeedbackConfig
from core.feedback_mapping import SoundCueId, SoundEffect
from ui.feedback import SoundFeedback


class FakeSoundEffect(QObject):
    statusChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.volume = None
        self.source = None
        self.play_count = 0
        self.stop_count = 0

    def stop(self) -> None:
        self.stop_count += 1

    def setVolume(self, volume: float) -> None:
        self.volume = volume

    def setSource(self, source) -> None:
        self.source = source

    def play(self) -> None:
        self.play_count += 1

    def status(self):
        return QSoundEffect.Status.Ready


class FailingSoundEffect(FakeSoundEffect):
    def play(self) -> None:
        raise RuntimeError("simulated sound backend failure")


class SoundFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.application = QApplication.instance() or QApplication([])

    def test_disabled_feedback_does_not_touch_backend(self) -> None:
        backend = FakeSoundEffect()
        adapter = SoundFeedback(
            FeedbackConfig(sounds_enabled=False, start_sound="unused.wav"),
            effect_factory=lambda parent: backend,
        )

        self.assertFalse(adapter.play(SoundEffect(SoundCueId.START)))
        self.assertEqual(backend.play_count, 0)

    def test_mapped_cue_uses_configured_asset_and_volume(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset = Path(directory) / "complete.wav"
            asset.touch()
            backend = FakeSoundEffect()
            adapter = SoundFeedback(
                FeedbackConfig(
                    sounds_enabled=True,
                    complete_sound=str(asset),
                ),
                effect_factory=lambda parent: backend,
            )

            self.assertTrue(
                adapter.play(SoundEffect(SoundCueId.COMPLETE, volume=0.35))
            )
            self.assertEqual(backend.volume, 0.35)
            self.assertEqual(backend.play_count, 1)
            self.assertTrue(backend.source.isLocalFile())

    def test_missing_asset_failure_is_reported_only_once(self) -> None:
        backend = FakeSoundEffect()
        adapter = SoundFeedback(
            FeedbackConfig(
                sounds_enabled=True,
                warning_sound="definitely-missing.wav",
            ),
            effect_factory=lambda parent: backend,
        )
        failures: list[str] = []
        adapter.failure.connect(failures.append)

        self.assertFalse(adapter.play(SoundEffect(SoundCueId.WARNING)))
        self.assertFalse(adapter.play(SoundEffect(SoundCueId.WARNING)))

        self.assertEqual(len(failures), 1)
        self.assertEqual(backend.play_count, 0)

    def test_backend_exception_is_nonfatal_and_limited(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset = Path(directory) / "error.wav"
            asset.touch()
            adapter = SoundFeedback(
                FeedbackConfig(
                    sounds_enabled=True,
                    error_sound=str(asset),
                ),
                effect_factory=FailingSoundEffect,
            )
            failures: list[str] = []
            adapter.failure.connect(failures.append)

            self.assertFalse(adapter.play(SoundEffect(SoundCueId.ERROR)))
            self.assertFalse(adapter.play(SoundEffect(SoundCueId.ERROR)))
            self.assertEqual(len(failures), 1)


if __name__ == "__main__":
    unittest.main()
