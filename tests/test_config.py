"""
Unit tests for configuration validation and loading in core/config.py.
"""

import unittest
import tempfile
import math
from pathlib import Path

import yaml

from core.config import (
    AppConfig,
    HotkeyConfig,
    OverlayConfig,
    ServerConfig,
    normalize_hotkey_spec,
)


class TestConfigValidation(unittest.TestCase):

    def test_default_config_valid(self):
        cfg = AppConfig()
        cfg.validate()
        self.assertEqual(cfg.server.start_confirmation_timeout, 10.0)
        self.assertEqual(cfg.server.server_busy_min_delay, 10.0)
        self.assertEqual(cfg.hotkey.toggle_key, "Ctrl+Shift+Space")
        self.assertEqual(cfg.hotkey.reinsert_last_key, "Ctrl+Alt+Space")

    def test_invalid_reconnect_min_delay(self):
        cfg = ServerConfig(reconnect_min_delay=0)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_invalid_reconnect_max_delay(self):
        cfg = ServerConfig(reconnect_min_delay=5.0, reconnect_max_delay=2.0)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_invalid_server_busy_min_delay(self):
        cfg = ServerConfig(server_busy_min_delay=40.0, reconnect_max_delay=30.0)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_invalid_reconnect_jitter(self):
        cfg = ServerConfig(reconnect_jitter=1.0)
        with self.assertRaises(ValueError):
            cfg.validate()

        cfg2 = ServerConfig(reconnect_jitter=-0.1)
        with self.assertRaises(ValueError):
            cfg2.validate()

    def test_invalid_ping_timeout_count(self):
        for value in (0, 1.5, True, "3"):
            with self.subTest(value=value):
                cfg = ServerConfig(ping_timeout_count=value)
                with self.assertRaises(ValueError):
                    cfg.validate()

    def test_invalid_start_confirmation_timeout(self):
        cfg = ServerConfig(start_confirmation_timeout=0)
        with self.assertRaises(ValueError):
            cfg.validate()

    def test_non_numeric_and_non_finite_values_are_rejected_cleanly(self):
        for field_name, value in (
            ("ping_interval", "10"),
            ("reconnect_min_delay", None),
            ("reconnect_max_delay", math.inf),
            ("server_busy_min_delay", math.nan),
            ("start_confirmation_timeout", True),
        ):
            with self.subTest(field=field_name, value=value):
                cfg = ServerConfig(**{field_name: value})
                with self.assertRaises(ValueError):
                    cfg.validate()

    def test_handshake_timeouts_must_be_positive(self):
        for field_name in ("hello_timeout", "ready_timeout"):
            with self.subTest(field=field_name):
                cfg = ServerConfig(**{field_name: 0})
                with self.assertRaises(ValueError):
                    cfg.validate()

    def test_load_yaml_with_ap05_keys(self):
        yaml_content = """
server:
  url: wss://test.server/ws
  reconnect_min_delay: 1.0
  reconnect_max_delay: 20.0
  server_busy_min_delay: 5.0
  start_confirmation_timeout: 15.0
"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
            f.write(yaml_content)
            temp_path = Path(f.name)

        try:
            cfg = AppConfig.load(temp_path)
            self.assertEqual(cfg.server.url, "wss://test.server/ws")
            self.assertEqual(cfg.server.reconnect_min_delay, 1.0)
            self.assertEqual(cfg.server.reconnect_max_delay, 20.0)
            self.assertEqual(cfg.server.server_busy_min_delay, 5.0)
            self.assertEqual(cfg.server.start_confirmation_timeout, 15.0)
        finally:
            if temp_path.exists():
                temp_path.unlink()

    def test_hotkey_normalization_accepts_legacy_and_canonical_format(self):
        self.assertEqual(
            normalize_hotkey_spec("<ctrl>+<shift>+space"),
            "Ctrl+Shift+Space",
        )
        self.assertEqual(
            normalize_hotkey_spec("shift+ctrl+F12"),
            "Ctrl+Shift+F12",
        )

    def test_hotkey_normalization_rejects_ambiguous_or_unsupported_specs(self):
        for value in (
            "",
            "Space",
            "Ctrl+Shift",
            "Ctrl+Ctrl+Space",
            "Ctrl+Space+V",
            "Ctrl+Mouse1",
        ):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    normalize_hotkey_spec(value)

    def test_hotkey_config_rejects_invalid_modes_types_and_duplicates(self):
        invalid_configs = (
            HotkeyConfig(enabled=1),
            HotkeyConfig(mode="push_to_talk"),
            HotkeyConfig(auto_start="yes"),
            HotkeyConfig(toggle_key="Ctrl+Space", reinsert_last_key="Ctrl+Space"),
        )
        for config in invalid_configs:
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    config.validate()

    def test_legacy_hotkey_key_overrides_toggle_key(self):
        config = HotkeyConfig(key="<ctrl>+<shift>+space")
        config.validate()
        self.assertEqual(config.effective_toggle_key, "<ctrl>+<shift>+space")

    def test_overlay_config_validation(self):
        OverlayConfig().validate()
        invalid_configs = (
            OverlayConfig(enabled=1),
            OverlayConfig(position="center"),
            OverlayConfig(width=0),
            OverlayConfig(max_height=True),
            OverlayConfig(opacity=1.1),
            OverlayConfig(fade_after=-0.1),
            OverlayConfig(font_size=0),
            OverlayConfig(margin=-1),
        )
        for config in invalid_configs:
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    config.validate()

    def test_load_yaml_with_ap06_hotkeys(self):
        yaml_content = """
hotkey:
  enabled: true
  mode: toggle
  toggle_key: Ctrl+Shift+Space
  reinsert_last_key: Ctrl+Alt+Space
  auto_start: false
overlay:
  enabled: true
  position: bottom_center
  width: 500
  max_height: 90
  opacity: 0.8
  fade_after: 1.5
  font_size: 13
  margin: 40
"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
            f.write(yaml_content)
            temp_path = Path(f.name)
        try:
            cfg = AppConfig.load(temp_path)
            self.assertEqual(cfg.hotkey.toggle_key, "Ctrl+Shift+Space")
            self.assertEqual(cfg.hotkey.reinsert_last_key, "Ctrl+Alt+Space")
            self.assertEqual(cfg.overlay.width, 500)
        finally:
            temp_path.unlink(missing_ok=True)

    def test_non_mapping_yaml_root_falls_back_to_valid_defaults(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".yaml") as f:
            f.write("- not\\n- a\\n- mapping\\n")
            temp_path = Path(f.name)
        try:
            cfg = AppConfig.load(temp_path)
            self.assertEqual(cfg.hotkey.toggle_key, "Ctrl+Shift+Space")
            cfg.validate()
        finally:
            temp_path.unlink(missing_ok=True)

    def test_save_migrates_legacy_hotkey_without_parallel_key(self):
        cfg = AppConfig()
        cfg.hotkey.key = "<ctrl>+<shift>+space"
        with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as f:
            temp_path = Path(f.name)
        try:
            cfg.save(temp_path)
            saved = yaml.safe_load(temp_path.read_text(encoding="utf-8"))
            self.assertEqual(
                saved["hotkey"]["toggle_key"],
                "Ctrl+Shift+Space",
            )
            self.assertNotIn("key", saved["hotkey"])
        finally:
            temp_path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
