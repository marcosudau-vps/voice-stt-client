"""
Path boundaries for store and sink — gate finding B-3 (RUN-OBS-030-02).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §4.3 P-8: *"Store und Sinks
liegen unterhalb von %LOCALAPPDATA%\\RealtimeSTT Client\\ und erben damit die
Benutzer-ACL. Es wird KEIN eigenes Verzeichnis mit abweichenden Rechten
angelegt und KEIN Pfad ausserhalb des Benutzerprofils akzeptiert. Ein
konfigurierter absoluter Pfad wird gegen das Benutzerprofil geprueft."*
Also R-7 and §5.1 (``logging.observability.db_path`` addresses exactly the
store built in OBS-030).

The check runs against the **resolved** path, so ``..``, an absolute path
elsewhere, a relative path, a drive-relative path and a UNC path are all
rejected alike.
"""

from __future__ import annotations

import os
import tempfile
import unittest
from pathlib import Path

from core.config import (
    DEFAULT_LOCAL_APP_DIR,
    LoggingObservabilityConfig,
    is_inside_user_profile,
)
from core.observability.manager import DEFAULT_DB_PATH, ObservabilityManager


def _profile_root() -> Path:
    value = os.environ.get("USERPROFILE") or os.environ.get("HOME")
    return Path(value) if value else Path.home()


def _outside_root() -> Path:
    """A directory that is definitely outside the user profile on any
    platform: the profile's own anchor plus a name the profile never has."""
    return Path(_profile_root().anchor) / "obs030-outside-user-profile"


class TestIsInsideUserProfile(unittest.TestCase):
    def test_positive_default_store_location_is_inside(self):
        self.assertTrue(is_inside_user_profile(DEFAULT_LOCAL_APP_DIR))
        self.assertTrue(is_inside_user_profile(DEFAULT_LOCAL_APP_DIR / "observability.sqlite3"))

    def test_positive_temp_dir_used_by_the_test_suite_is_inside(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Not a contract statement, a precondition check: the OBS-030
            # tests store their databases here, so they must stay valid.
            self.assertTrue(is_inside_user_profile(Path(tmp) / "obs.sqlite3"))

    def test_negative_path_outside_the_profile(self):
        self.assertFalse(is_inside_user_profile(_outside_root() / "observability.sqlite3"))

    def test_negative_dotdot_escape_is_resolved_before_the_check(self):
        escape = DEFAULT_LOCAL_APP_DIR / ".." / ".." / ".." / ".." / "obs030-escaped.sqlite3"
        self.assertFalse(is_inside_user_profile(escape))

    def test_positive_dotdot_that_stays_inside_is_accepted(self):
        inside = DEFAULT_LOCAL_APP_DIR / "logs" / ".." / "observability.sqlite3"
        self.assertTrue(is_inside_user_profile(inside))

    def test_case_insensitive_on_windows(self):
        if os.name != "nt":
            self.skipTest("case-insensitive path comparison is a Windows case")
        self.assertTrue(is_inside_user_profile(str(DEFAULT_LOCAL_APP_DIR).upper()))

    def test_forward_slashes_are_normalised_on_windows(self):
        if os.name != "nt":
            self.skipTest("separator normalisation is a Windows case")
        self.assertTrue(is_inside_user_profile(str(DEFAULT_LOCAL_APP_DIR).replace("\\", "/")))


class TestConfigValidationRejectsForeignPaths(unittest.TestCase):
    def _validate(self, **overrides) -> None:
        LoggingObservabilityConfig(**overrides).validate()

    def test_positive_db_path_inside_the_profile_is_accepted(self):
        self._validate(db_path=str(DEFAULT_LOCAL_APP_DIR / "observability.sqlite3"))

    def test_positive_file_sink_dir_inside_the_profile_is_accepted(self):
        self._validate(file_sink_dir=str(DEFAULT_LOCAL_APP_DIR / "logs" / "observability"))

    def test_positive_tilde_expands_into_the_profile(self):
        self._validate(db_path="~/obs030-home.sqlite3")

    def test_positive_none_means_default_location(self):
        self._validate(db_path=None, file_sink_dir=None)

    def test_negative_absolute_db_path_outside_the_profile(self):
        with self.assertRaises(ValueError):
            self._validate(db_path=str(_outside_root() / "observability.sqlite3"))

    def test_negative_absolute_file_sink_dir_outside_the_profile(self):
        with self.assertRaises(ValueError):
            self._validate(file_sink_dir=str(_outside_root() / "sink"))

    def test_negative_programdata_is_the_gate_review_example(self):
        if os.name != "nt":
            self.skipTest("Windows-specific path case")
        system_drive = os.environ.get("SystemDrive", "C:")
        with self.assertRaises(ValueError):
            self._validate(
                db_path=f"{system_drive}\\ProgramData\\somewhere-else\\observability.sqlite3"
            )

    def test_negative_dotdot_escape_is_rejected(self):
        escape = str(DEFAULT_LOCAL_APP_DIR / ".." / ".." / ".." / ".." / "obs030-escaped.sqlite3")
        with self.assertRaises(ValueError):
            self._validate(db_path=escape)

    def test_negative_relative_path_is_rejected(self):
        with self.assertRaises(ValueError):
            self._validate(db_path="observability.sqlite3")

    def test_negative_empty_string_is_rejected(self):
        with self.assertRaises(ValueError):
            self._validate(db_path="   ")

    def test_negative_drive_relative_windows_path_is_rejected(self):
        if os.name != "nt":
            self.skipTest("drive-relative paths are a Windows case")
        with self.assertRaises(ValueError):
            self._validate(db_path="C:observability.sqlite3")

    def test_negative_unc_path_is_rejected(self):
        if os.name != "nt":
            self.skipTest("UNC paths are a Windows case")
        with self.assertRaises(ValueError):
            self._validate(db_path="\\\\server\\share\\observability.sqlite3")

    def test_negative_windows_temp_of_another_user_is_rejected(self):
        if os.name != "nt":
            self.skipTest("Windows-specific path case")
        system_drive = os.environ.get("SystemDrive", "C:")
        with self.assertRaises(ValueError):
            self._validate(
                file_sink_dir=f"{system_drive}\\Users\\obs030-someone-else\\AppData\\Local\\sink"
            )


class TestManagerRefusesForeignPaths(unittest.TestCase):
    """Defense in depth: ``app.py::main()`` builds the manager straight from
    ``AppConfig.load()`` and never calls ``AppConfig.validate()``, so the
    manager must not rely on validation having happened."""

    def test_db_path_outside_the_profile_falls_back_to_the_default_location(self):
        config = LoggingObservabilityConfig(store_enabled=True, file_sink_enabled=False)
        # Bypass validate() on purpose: this is the unvalidated runtime path.
        object.__setattr__(config, "db_path", str(_outside_root() / "observability.sqlite3"))
        manager = ObservabilityManager(config)
        try:
            store_path = manager._worker._store.path
            self.assertFalse(is_inside_user_profile(_outside_root()))
            self.assertEqual(Path(store_path), Path(DEFAULT_DB_PATH))
        finally:
            manager.stop(0.5)

    def test_file_sink_dir_outside_the_profile_falls_back_to_the_default_location(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = LoggingObservabilityConfig(store_enabled=False, file_sink_enabled=True)
            object.__setattr__(config, "file_sink_dir", str(_outside_root() / "sink"))
            manager = ObservabilityManager(config, log_dir=tmp)
            try:
                sink_dir = Path(manager._worker._sink._directory)
                self.assertEqual(sink_dir, Path(tmp) / "observability")
            finally:
                manager.stop(0.5)

    def test_accepted_path_inside_the_profile_is_used_unchanged(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "obs.sqlite3"
            config = LoggingObservabilityConfig(db_path=str(db_path))
            config.validate()  # must not raise
            manager = ObservabilityManager(config, log_dir=tmp)
            try:
                self.assertEqual(Path(manager._worker._store.path), db_path)
            finally:
                manager.stop(0.5)


if __name__ == "__main__":
    unittest.main()
