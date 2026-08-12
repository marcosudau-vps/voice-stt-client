from __future__ import annotations

import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, Signal
from PySide6.QtMultimedia import QSoundEffect
from PySide6.QtWidgets import QApplication

from core.config import FeedbackConfig
from core.feedback_mapping import SoundCueId, SoundEffect
MappedSoundEffect = SoundEffect
from ui.feedback import SoundFeedback, application_resource_root, resolve_sound_asset


class FakeSoundEffect(QObject):
    statusChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self.volume = None
        self.source_value = None
        self.play_count = 0
        self.stop_count = 0

    def stop(self) -> None:
        self.stop_count += 1

    def setVolume(self, volume: float) -> None:
        self.volume = volume

    def setSource(self, source) -> None:
        self.source_value = source

    def source(self):
        return self.source_value

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
            self.assertTrue(backend.source_value.isLocalFile())

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

    def test_relative_asset_is_resolved_against_application_resource_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            asset = root / "assets" / "cue.wav"
            asset.parent.mkdir(parents=True)
            asset.touch()
            backend = FakeSoundEffect()
            adapter = SoundFeedback(
                FeedbackConfig(sounds_enabled=True, start_sound="assets/cue.wav"),
                effect_factory=lambda parent: backend,
                resource_root=root,
            )

            self.assertTrue(adapter.play(SoundEffect(SoundCueId.START)))
            self.assertEqual(
                backend.source_value.toLocalFile(),
                str(asset.resolve()).replace("\\", "/"),
            )

    def test_different_cues_use_independent_players(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "start.wav").touch()
            (root / "stop.wav").touch()
            players: list[FakeSoundEffect] = []

            def factory(parent):
                player = FakeSoundEffect(parent)
                players.append(player)
                return player

            adapter = SoundFeedback(
                FeedbackConfig(
                    sounds_enabled=True,
                    start_sound="start.wav",
                    stop_sound="stop.wav",
                ),
                effect_factory=factory,
                resource_root=root,
            )

            self.assertTrue(adapter.play(SoundEffect(SoundCueId.START)))
            self.assertTrue(adapter.play(SoundEffect(SoundCueId.STOP)))
            self.assertEqual(len(players), 2)
            self.assertEqual([player.play_count for player in players], [1, 1])
            self.assertEqual([player.stop_count for player in players], [0, 0])

    def test_apply_config_releases_preloaded_players(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset = Path(directory) / "start.wav"
            asset.touch()
            backend = FakeSoundEffect()
            adapter = SoundFeedback(
                FeedbackConfig(sounds_enabled=True, start_sound=str(asset)),
                effect_factory=lambda parent: backend,
            )
            self.assertTrue(adapter.play(SoundEffect(SoundCueId.START)))

            adapter.apply_config(FeedbackConfig(sounds_enabled=False))

            self.assertEqual(backend.stop_count, 1)
            self.assertEqual(adapter._effects, {})

    def test_timeout_tick_can_be_stopped_explicitly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            asset = Path(directory) / "tick.wav"
            asset.touch()
            backend = FakeSoundEffect()
            adapter = SoundFeedback(
                FeedbackConfig(sounds_enabled=True, timeout_tick_sound=str(asset)),
                effect_factory=lambda parent: backend,
            )

            self.assertTrue(
                adapter.play(SoundEffect(SoundCueId.TIMEOUT_TICK, action="play"))
            )
            self.assertTrue(
                adapter.play(SoundEffect(SoundCueId.TIMEOUT_TICK, action="stop"))
            )
            self.assertEqual(backend.stop_count, 1)

    def test_resolver_preserves_absolute_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            absolute = Path(directory) / "cue.wav"
            self.assertEqual(
                resolve_sound_asset(absolute.as_posix(), resource_root=Path("ignored")),
                absolute,
            )

    def test_resolver_expands_a_user_relative_path(self) -> None:
        expected = Path("~/cue.wav").expanduser()
        self.assertEqual(
            resolve_sound_asset("~/cue.wav", resource_root=Path("ignored")),
            expected,
        )

    def test_frozen_application_uses_pyinstaller_resource_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            frozen_root = Path(directory)
            with mock.patch.object(sys, "_MEIPASS", str(frozen_root), create=True):
                self.assertEqual(application_resource_root(), frozen_root)


if __name__ == "__main__":
    unittest.main()


class TestSoundCueCatalogueIsComplete(unittest.TestCase):
    """Every cue a rule may name has to resolve to a configured asset slot.

    ``_path_for_cue`` is a dict lookup, so a cue without an entry does not
    degrade -- it raises KeyError in the middle of feedback. Parametrised over
    the enum so that adding a cue and forgetting the slot fails here rather
    than in front of somebody dictating.
    """

    def test_every_cue_has_a_configuration_slot(self) -> None:
        feedback = SoundFeedback(FeedbackConfig(sounds_enabled=True))
        self.addCleanup(feedback.deleteLater)
        for cue in SoundCueId:
            with self.subTest(cue=cue):
                # No assertion on the value: a slot may legitimately be unset.
                # What must hold is that asking does not blow up.
                feedback._path_for_cue(cue)

    def test_an_unset_slot_is_silence_rather_than_a_failure(self) -> None:
        feedback = SoundFeedback(FeedbackConfig(sounds_enabled=True))
        self.addCleanup(feedback.deleteLater)
        reported: list[str] = []
        feedback.failure.connect(reported.append)
        for cue in SoundCueId:
            if feedback._path_for_cue(cue):
                continue
            self.assertFalse(feedback.play(MappedSoundEffect(cue, 1.0)))
        self.assertEqual(reported, [])
