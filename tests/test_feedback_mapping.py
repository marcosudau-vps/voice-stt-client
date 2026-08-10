"""Tests for the YAML-configured server and local feedback mapping."""

import tempfile
import unittest
from pathlib import Path

from core.config import AppConfig, DEFAULT_CONFIG_PATH
from core.event_models import CanonicalEventType
from core.feedback_mapping import (
    AppActionId,
    FeedbackMappingConfig,
    LedVerb,
    SoundCueId,
    default_feedback_mappings,
)


class TestFeedbackMapping(unittest.TestCase):
    def test_project_yaml_maps_server_and_local_client_events(self):
        config = AppConfig.load(DEFAULT_CONFIG_PATH)
        server_rule = config.feedback_mappings.rule_for(
            CanonicalEventType.SERVER_RECORDING_STARTED
        )
        client_rule = config.feedback_mappings.rule_for(
            CanonicalEventType.CLIENT_INJECTION_FAILED
        )
        self.assertEqual(len(server_rule.led), 1)
        self.assertEqual(server_rule.led[0].verb, LedVerb.SET_STATE)
        self.assertEqual(server_rule.led[0].target, "listening")
        self.assertEqual(server_rule.sound.cue, SoundCueId.START)
        self.assertEqual(server_rule.app.action, AppActionId.INDICATOR_RECORDING)

        self.assertEqual(client_rule.led[0].verb, LedVerb.EMIT_EVENT)
        self.assertEqual(client_rule.led[0].target, "error_event")
        self.assertEqual(client_rule.sound.cue, SoundCueId.ERROR)
        self.assertEqual(client_rule.app.action, AppActionId.INDICATOR_ERROR)
        self.assertEqual(
            set(config.feedback_mappings.events),
            {event_type.value for event_type in CanonicalEventType},
        )

    def test_one_fact_can_both_announce_and_change_the_lasting_state(self):
        """A wake word flashes and then settles. That is two calls, in order."""
        config = AppConfig.load(DEFAULT_CONFIG_PATH)
        rule = config.feedback_mappings.rule_for(
            CanonicalEventType.SERVER_WAKE_WORD_DETECTED
        )
        self.assertEqual(
            [(call.verb, call.target) for call in rule.led],
            [
                (LedVerb.EMIT_EVENT, "wakeword_detected"),
                (LedVerb.SET_STATE, "waiting"),
            ],
        )

    def test_every_named_target_is_reported_once_for_the_startup_check(self):
        config = AppConfig.load(DEFAULT_CONFIG_PATH)
        targets = config.feedback_mappings.led_targets()
        self.assertEqual(len(targets), len(set(targets)))
        self.assertIn("listening", targets)
        self.assertIn("success_event", targets)
        # clear_state names a slot, not an effect, so it contributes nothing.
        self.assertNotIn("primary", targets)

    def test_default_catalog_contains_every_known_event(self):
        mapping = default_feedback_mappings()
        self.assertEqual(
            set(mapping.events),
            {event_type.value for event_type in CanonicalEventType},
        )
        self.assertEqual(mapping.led_targets(), ())

    def test_schema_version_one_is_refused_with_a_usable_message(self):
        """The old vocabulary is gone; guessing what it meant would be worse."""
        with self.assertRaises(ValueError) as caught:
            FeedbackMappingConfig.from_mapping(
                {"schema_version": 1, "events": {}}
            )
        message = str(caught.exception)
        self.assertIn("schema_version", message)
        self.assertIn("set_state", message)

    def test_invalid_event_and_output_ids_are_rejected(self):
        invalid = (
            {"events": {"server.invented": {}}},
            # no verb at all
            {"events": {"server.recording.started": {"led": {"effect": "recording"}}}},
            # two verbs in one call
            {
                "events": {
                    "server.recording.started": {
                        "led": {"set_state": "listening", "emit_event": "warn_event"}
                    }
                }
            },
            # a modifier the verb does not take
            {
                "events": {
                    "server.recording.started": {
                        "led": {"set_state": "listening", "duration_ms": 500}
                    }
                }
            },
            # an empty target
            {"events": {"server.recording.started": {"led": {"set_state": "  "}}}},
            # a slot that does not exist
            {
                "events": {
                    "server.recording.started": {
                        "led": {"set_state": "listening", "slot": "middle"}
                    }
                }
            },
            {"events": {"server.recording.started": {"led": {"clear_state": "middle"}}}},
            # config has to be a mapping
            {
                "events": {
                    "server.recording.started": {
                        "led": {"set_state": "listening", "config": "bright"}
                    }
                }
            },
            # out of range
            {
                "events": {
                    "server.recording.started": {
                        "led": {"emit_event": "warn_event", "duration_ms": 0}
                    }
                }
            },
            {"events": {"client.injection.failed": {"sound": {"cue": "run_program"}}}},
            {"events": {"client.hotkey.accepted": {"app": {"action": "python.exec"}}}},
            {
                "events": {
                    "client.hotkey.accepted": {"sound": {"cue": "start", "volume": 1.5}}
                }
            },
            {"events": {"client.hotkey.accepted": {"python": "do_something()"}}},
        )
        for raw in invalid:
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    FeedbackMappingConfig.from_mapping(raw)

    def test_the_catalogue_decides_what_a_parameter_means(self):
        """Structure is checked here; effect parameters are not, on purpose.

        A second copy of every effect's schema would go stale the first time a
        set is updated, and would reject configurations the engine accepts.
        """
        config = FeedbackMappingConfig.from_mapping(
            {
                "schema_version": 2,
                "events": {
                    "server.recording.started": {
                        "led": {
                            "set_state": "listening",
                            "config": {"speed": 1.8, "whatever": "the set says"},
                        }
                    }
                },
            }
        )
        call = config.rule_for(CanonicalEventType.SERVER_RECORDING_STARTED).led[0]
        self.assertEqual(call.config["speed"], 1.8)

    def test_mapping_save_and_load_roundtrip_uses_plain_yaml_ids(self):
        config = AppConfig.load(DEFAULT_CONFIG_PATH)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "config.yaml"
            config.save(path)
            text = path.read_text(encoding="utf-8")
            self.assertIn("server.recording.started", text)
            self.assertIn("indicator.recording", text)
            loaded = AppConfig.load(path)
        self.assertEqual(
            loaded.feedback_mappings.rule_for(
                CanonicalEventType.SERVER_RECORDING_STARTED
            ),
            config.feedback_mappings.rule_for(
                CanonicalEventType.SERVER_RECORDING_STARTED
            ),
        )

    def test_user_override_is_merged_atomically_and_invalid_ids_abort(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            user = root / "user.yaml"
            user.write_text(
                "feedback_mappings:\n"
                "  events:\n"
                "    client.injection.failed:\n"
                "      app: {action: indicator.warning}\n",
                encoding="utf-8",
            )
            config = AppConfig.load(user_path=user)
            rule = config.feedback_mappings.rule_for(
                CanonicalEventType.CLIENT_INJECTION_FAILED
            )
            self.assertEqual(rule.app.action, AppActionId.INDICATOR_WARNING)
            self.assertEqual(rule.led[0].target, "error_event")

            user.write_text(
                "feedback_mappings:\n"
                "  events:\n"
                "    client.injection.failed:\n"
                "      app: {action: python.exec}\n",
                encoding="utf-8",
            )
            with self.assertRaises(ValueError):
                AppConfig.load(user_path=user)


if __name__ == "__main__":
    unittest.main()
