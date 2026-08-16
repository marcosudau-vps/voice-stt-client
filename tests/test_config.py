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
    EventStreamConfig,
    FeedbackConfig,
    HotkeyConfig,
    LedConfig,
    OverlayConfig,
    ServerConfig,
    normalize_hotkey_spec,
)
from core.event_models import CanonicalEventType


class TestConfigValidation(unittest.TestCase):

    def test_default_config_valid(self):
        cfg = AppConfig()
        cfg.validate()
        self.assertEqual(cfg.server.start_confirmation_timeout, 10.0)
        self.assertEqual(cfg.server.server_busy_min_delay, 10.0)
        self.assertEqual(cfg.hotkey.toggle_key, "Ctrl+Shift+Space")
        self.assertEqual(cfg.hotkey.reinsert_last_key, "Ctrl+Alt+Space")
        self.assertTrue(cfg.event_stream.enabled)
        self.assertTrue(cfg.event_stream.cursor_persistence_enabled)

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

    def test_event_stream_limits_and_safe_url_building(self):
        self.assertEqual(
            EventStreamConfig.build_url(
                "wss://stt.voice.marcosudau.com/ws/transcribe?mode=hotkey",
                "/ws/logs",
            ),
            "wss://stt.voice.marcosudau.com/ws/logs",
        )
        invalid_configs = (
            EventStreamConfig(connect_timeout=0),
            EventStreamConfig(reconnect_min_delay=5, reconnect_max_delay=2),
            EventStreamConfig(reconnect_jitter=1),
            EventStreamConfig(max_message_size=100),
            EventStreamConfig(queue_maxsize=0),
            EventStreamConfig(cursor_persistence_enabled="yes"),
            EventStreamConfig(cursor_path="relative/cursor.json"),
        )
        for config in invalid_configs:
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    config.validate()
        for base, path in (
            ("https://example.test/ws", "/ws/logs"),
            ("wss://user:secret@example.test/ws", "/ws/logs"),
            ("wss://example.test/ws", "wss://evil.test/ws/logs"),
            ("wss://example.test/ws", "//evil.test/ws/logs"),
            ("wss://example.test/ws", "/ws/logs?token=secret"),
        ):
            with self.subTest(base=base, path=path):
                with self.assertRaises(ValueError):
                    EventStreamConfig.build_url(base, path)

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

    def test_feedback_supports_every_declared_sound_cue_asset(self):
        config = FeedbackConfig(
            sounds_enabled=True,
            wake_word_sound="wake.wav",
            start_sound="start.wav",
            stop_sound="stop.wav",
            complete_sound="complete.wav",
            cancel_sound="cancel.wav",
            warning_sound="warning.wav",
            error_sound="error.wav",
            timeout_tick_sound="timeout.wav",
        )
        config.validate()

        self.assertEqual(config.complete_sound, "complete.wav")
        with self.assertRaises(ValueError):
            FeedbackConfig(error_sound=42).validate()

    def test_shipped_debug_feedback_assets_and_mapping_are_complete(self):
        project_root = Path(__file__).resolve().parent.parent
        config = AppConfig.load(project_root / "config.yaml")
        self.assertTrue(config.feedback.sounds_enabled)
        self.assertEqual(config.led.brightness, 192)
        paths = (
            config.feedback.wake_word_sound,
            config.feedback.start_sound,
            config.feedback.stop_sound,
            config.feedback.complete_sound,
            config.feedback.cancel_sound,
            config.feedback.warning_sound,
            config.feedback.error_sound,
            config.feedback.timeout_tick_sound,
        )
        self.assertEqual(len(set(paths)), 8)
        for path in paths:
            with self.subTest(path=path):
                self.assertIsNotNone(path)
                self.assertTrue((project_root / path).is_file())

        degraded = config.feedback_mappings.rule_for(
            CanonicalEventType.CLIENT_EVENT_STREAM_DEGRADED
        )
        self.assertIsNone(degraded.app)
        countdown = config.feedback_mappings.rule_for(
            CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING
        )
        self.assertEqual(countdown.led[0].target, "countdown_ring")

    def test_led_config_validates_output_and_worker_limits(self):
        LedConfig().validate()
        invalid = (
            LedConfig(enabled=1),
            LedConfig(sink="hologram"),
            LedConfig(fps=0.0),
            LedConfig(fps=500.0),
            LedConfig(vendor_id=-1),
            LedConfig(product_id=0x10000),
            LedConfig(brightness=256),
            LedConfig(usb_timeout_ms=10),
            LedConfig(shutdown_timeout=20.0),
            LedConfig(simulation_offer_after_s=-1),
            LedConfig(effect_paths="C:/effects"),
            LedConfig(effect_paths=[""]),
            LedConfig(effect_paths=[3]),
        )
        for config in invalid:
            with self.subTest(config=config):
                with self.assertRaises(ValueError):
                    config.validate()

    def test_brightness_keeps_its_scale_and_is_offered_as_a_fraction(self):
        """LEFX wants 0.0..1.0; the file keeps 0..255 so saved values still mean
        what they meant."""
        self.assertAlmostEqual(LedConfig(brightness=255).brightness_fraction, 1.0)
        self.assertAlmostEqual(LedConfig(brightness=0).brightness_fraction, 0.0)
        self.assertAlmostEqual(
            LedConfig(brightness=64).brightness_fraction, 64 / 255
        )

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


class TestAP6ConfigMigration(unittest.TestCase):
    """The migration rule of the specification, verbatim.

    ```text
    mode = hotkey     ->  manual = true,  wake_word = false
    mode = wake_word  ->  manual = false, wake_word = true
    ```

    An implicit migration to ``true / true`` is explicitly forbidden.
    """

    def test_legacy_hotkey_mode_migrates_to_manual_only(self):
        from core.config import SessionConfig, OperatingMode
        cfg = SessionConfig(mode=OperatingMode.HOTKEY.value)
        cfg.validate()
        self.assertTrue(cfg.effective_manual_trigger_enabled)
        self.assertFalse(cfg.effective_wake_word_trigger_enabled)
        params = cfg.query_parameters()
        self.assertEqual(params["manualTriggerEnabled"], "true")
        self.assertEqual(params["wakeWordTriggerEnabled"], "false")

    def test_legacy_wake_word_mode_migrates_to_wake_word_only(self):
        from core.config import SessionConfig, OperatingMode
        cfg = SessionConfig(mode=OperatingMode.WAKE_WORD.value)
        cfg.validate()
        self.assertFalse(
            cfg.effective_manual_trigger_enabled,
            "wake_word must not implicitly enable the manual trigger",
        )
        self.assertTrue(cfg.effective_wake_word_trigger_enabled)
        params = cfg.query_parameters()
        self.assertEqual(params["manualTriggerEnabled"], "false")
        self.assertEqual(params["wakeWordTriggerEnabled"], "true")

    def test_no_legacy_mode_ever_migrates_to_both_triggers(self):
        from core.config import SessionConfig, OperatingMode
        for mode in OperatingMode:
            with self.subTest(mode=mode.value):
                cfg = SessionConfig(mode=mode.value)
                cfg.validate()
                enabled = (
                    cfg.effective_manual_trigger_enabled,
                    cfg.effective_wake_word_trigger_enabled,
                )
                self.assertNotEqual(
                    enabled, (True, True), "implicit true/true is forbidden"
                )
                self.assertIn(True, enabled, "a mode must map to one trigger")

    def test_explicit_flags_override_the_legacy_mode(self):
        from core.config import SessionConfig, OperatingMode
        cfg = SessionConfig(
            mode=OperatingMode.WAKE_WORD.value,
            manual_trigger_enabled=True,
            wake_word_trigger_enabled=True,
        )
        cfg.validate()
        params = cfg.query_parameters()
        self.assertEqual(params["manualTriggerEnabled"], "true")
        self.assertEqual(params["wakeWordTriggerEnabled"], "true")
        self.assertFalse(cfg.migrated_from_legacy_mode)

    def test_a_single_explicit_flag_still_reads_the_other_from_the_mode(self):
        from core.config import SessionConfig, OperatingMode
        cfg = SessionConfig(
            mode=OperatingMode.WAKE_WORD.value, manual_trigger_enabled=True
        )
        cfg.validate()
        self.assertTrue(cfg.effective_manual_trigger_enabled)
        self.assertTrue(cfg.effective_wake_word_trigger_enabled)

    def test_a_missing_mode_field_keeps_the_hotkey_default(self):
        from core.config import SessionConfig
        cfg = SessionConfig()
        cfg.validate()
        self.assertTrue(cfg.effective_manual_trigger_enabled)
        self.assertFalse(cfg.effective_wake_word_trigger_enabled)

    def test_an_invalid_legacy_mode_value_is_rejected(self):
        from core.config import SessionConfig
        cfg = SessionConfig(mode="dictation")
        with self.assertRaises(ValueError) as ctx:
            cfg.validate()
        self.assertIn("session.mode", str(ctx.exception))

    def test_disabling_all_triggers_raises_validation_error(self):
        from core.config import SessionConfig
        cfg = SessionConfig(
            manual_trigger_enabled=False, wake_word_trigger_enabled=False
        )
        with self.assertRaises(ValueError) as ctx:
            cfg.validate()
        self.assertIn("At least one trigger source", str(ctx.exception))

    def test_disabling_all_triggers_is_rejected_for_every_legacy_mode(self):
        from core.config import SessionConfig, OperatingMode
        for mode in OperatingMode:
            with self.subTest(mode=mode.value):
                cfg = SessionConfig(
                    mode=mode.value,
                    manual_trigger_enabled=False,
                    wake_word_trigger_enabled=False,
                )
                with self.assertRaises(ValueError):
                    cfg.validate()

    def test_a_non_boolean_trigger_flag_is_rejected(self):
        from core.config import SessionConfig
        for field in ("manual_trigger_enabled", "wake_word_trigger_enabled"):
            with self.subTest(field=field):
                cfg = SessionConfig(**{field: "yes"})
                with self.assertRaises(ValueError) as ctx:
                    cfg.validate()
                self.assertIn(field, str(ctx.exception))

    def test_wake_word_details_are_only_sent_when_the_wake_word_is_on(self):
        from core.config import SessionConfig, OperatingMode
        hotkey = SessionConfig(mode=OperatingMode.HOTKEY.value)
        hotkey.validate()
        params = hotkey.query_parameters()
        self.assertEqual(params["wakeWordEnabled"], "false")
        self.assertNotIn("wakeWords", params)

        wake = SessionConfig(mode=OperatingMode.WAKE_WORD.value)
        wake.validate()
        params = wake.query_parameters()
        self.assertEqual(params["wakeWordEnabled"], "true")
        self.assertEqual(params["wakeWords"], "hey_jarvis")

    def test_activation_timings_reach_the_query_when_configured(self):
        from core.config import SessionConfig
        cfg = SessionConfig(
            initial_speech_timeout=12.0,
            followup_timeout=2.5,
            extension_seconds=4.0,
        )
        cfg.validate()
        params = cfg.query_parameters()
        self.assertEqual(params["initialSpeechTimeout"], "12.0")
        self.assertEqual(params["followupTimeout"], "2.5")
        self.assertEqual(params["extensionSeconds"], "4.0")


if __name__ == "__main__":
    unittest.main()
