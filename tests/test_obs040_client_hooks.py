"""
OBS-040 — the V1 client observation hooks of ``LOGGING_CONTRACTS_FREEZE_V1.md``
§12, and their correlation fields.

Frozen sources: §12.1 (lifecycle/transport, channel ``system``), §12.2
(intentional actions, channel ``audit``), §12.3 (transcript, channel
``transcription``), §12.4 (numbers, channel ``performance``), §12.5 (feedback
and output, channel ``system``), §12.6 (implementation order by ascending
risk), §12.7 (what is deliberately NOT instrumented), §2.2 (channel
definitions), §1.1 (which field carries which id);
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.6 (hot-path rules), O-01/O-05
(a logging failure never reaches the client function).
"""

from __future__ import annotations

import asyncio
import logging
import unittest
from unittest.mock import patch

from voice_stt_client.core.config import AppConfig
from voice_stt_client.core.observability.adapters.client_events import ClientEventEmitter
from voice_stt_client.core.observability.ingress import NULL_INGRESS, ObservabilityIngress
from voice_stt_client.core.history import TranscriptHistoryManager


def build_ingress(**changes) -> ObservabilityIngress:
    values = {"instance_id": "client-instance-1", "queue_size": 4096, "level": "DEBUG"}
    values.update(changes)
    return ObservabilityIngress(**values)


def records_of(ingress: ObservabilityIngress, type_: str) -> list:
    return [record for record in ingress.drain(4096, 0.0) if record.type == type_]


def _sources(ingress: ObservabilityIngress) -> list:
    """The registered aggregate sources, as ``(type, component, callable)``."""
    with ingress._aggregate_lock:
        return [
            (type_, component, source)
            for type_, (component, source) in ingress._aggregate_sources.items()
        ]


def all_records(ingress: ObservabilityIngress) -> dict:
    grouped: dict = {}
    for record in ingress.drain(4096, 0.0):
        grouped.setdefault(record.type, []).append(record)
    return grouped


# ---------------------------------------------------------------------------
# The emitter itself: the boundary every hook goes through.
# ---------------------------------------------------------------------------


class TestClientEventEmitter(unittest.TestCase):
    def test_a_throwing_ingress_never_reaches_the_call_site(self):
        """O-05: *"Logging-Ausfall beeinflusst die eigentliche Clientfunktion
        nicht."* The emitter is the single guard that makes that true for ANY
        ingress implementation, not just the concrete one."""

        class Exploding:
            def event(self, *args, **kwargs):
                raise RuntimeError("ingress exploded")

        emitter = ClientEventEmitter(Exploding(), component="unit")
        # No assertRaises: nothing may escape.
        self.assertIsNone(emitter.system("client.test"))

    def test_cancellation_still_propagates(self):
        class Cancelling:
            def event(self, *args, **kwargs):
                raise asyncio.CancelledError()

        emitter = ClientEventEmitter(Cancelling())
        with self.assertRaises(asyncio.CancelledError):
            emitter.audit("client.test")

    def test_the_component_default_is_applied_and_overridable(self):
        ingress = build_ingress()
        emitter = ClientEventEmitter(ingress, component="default-component")
        emitter.system("client.a")
        emitter.system("client.b", component="explicit")
        records = {record.type: record for record in ingress.drain(10, 0.0)}
        self.assertEqual(records["client.a"].component, "default-component")
        self.assertEqual(records["client.b"].component, "explicit")

    def test_each_wrapper_sets_its_own_channel(self):
        ingress = build_ingress()
        emitter = ClientEventEmitter(ingress)
        emitter.system("client.s")
        emitter.audit("client.a")
        emitter.transcription("client.t")
        emitter.performance("client.p")
        channels = {
            record.type: record.channel for record in ingress.drain(10, 0.0)
        }
        self.assertEqual(
            channels,
            {
                "client.s": "system",
                "client.a": "audit",
                "client.t": "transcription",
                "client.p": "performance",
            },
        )

    def test_null_ingress_produces_nothing_and_raises_nothing(self):
        emitter = ClientEventEmitter(NULL_INGRESS)
        emitter.audit("client.hotkey.pressed")
        self.assertEqual(NULL_INGRESS.drain(10, 0.0), [])


# ---------------------------------------------------------------------------
# §12.1 / §12.2: core/stt_session.py
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# §12.1 - §12.5: core/controller.py
# ---------------------------------------------------------------------------




# ---------------------------------------------------------------------------
# §12.2 / §12.4: core/audio_capture.py and its counters
# ---------------------------------------------------------------------------


class TestAudioCaptureHooks(unittest.TestCase):
    def test_stream_stopped_reports_the_final_counters(self):
        from voice_stt_client.core.audio_capture import AudioCapture

        ingress = build_ingress()
        config = AppConfig()
        capture = AudioCapture(config.audio, observability=ingress)
        capture.chunks_captured = 42
        capture.chunks_dropped_capture_queue = 3
        capture.overflow_count = 1
        capture._running = True
        capture.stop()

        [record] = records_of(ingress, "client.audio.stream_stopped")
        details = dict(record.details)
        self.assertEqual(details["chunks_captured"], 42)
        self.assertEqual(details["chunks_dropped_capture_queue"], 3)
        self.assertEqual(details["overflow_count"], 1)
        self.assertEqual(record.channel, "audit")

    def test_capture_counters_snapshot_is_a_plain_int_mapping(self):
        from voice_stt_client.core.audio_capture import AudioCapture

        capture = AudioCapture(AppConfig().audio)
        counters = capture.capture_counters()
        self.assertTrue(all(isinstance(value, int) for value in counters.values()))
        self.assertIn("chunks_captured", counters)


# ---------------------------------------------------------------------------
# §12.4: core/text_injector.py -- client.queue.state
# ---------------------------------------------------------------------------


class TestInjectionQueueStateHook(unittest.TestCase):
    def test_queue_state_is_aggregated_and_rate_limited(self):
        from voice_stt_client.core.text_injector import TextInjectionQueue

        ingress = build_ingress()
        config = AppConfig()
        config.history.persistent.enabled = False
        history = TranscriptHistoryManager(config.history)
        queue = TextInjectionQueue(config, history, None, observability=ingress)

        queue._observe_queue_state("after_job")
        # Immediately again: the rate limit suppresses it.
        queue._observe_queue_state("after_job")
        # A state change is forced through regardless.
        queue._observe_queue_state("worker_stopped", force=True)

        records = records_of(ingress, "client.queue.state")
        self.assertEqual(len(records), 2)
        self.assertEqual(
            [dict(record.details)["phase"] for record in records],
            ["after_job", "worker_stopped"],
        )
        for record in records:
            self.assertEqual(record.channel, "performance")
            self.assertEqual(record.level, "DEBUG")
            details = dict(record.details)
            self.assertIn("queue_size", details)
            self.assertIn("jobs_processed", details)
            # Aggregated numbers only -- never a job or a text.
            self.assertNotIn("text", details)
            self.assertNotIn("entry_id", details)


# ---------------------------------------------------------------------------
# §12.7: what must stay uninstrumented
# ---------------------------------------------------------------------------


class TestDeliberatelyNotInstrumented(unittest.TestCase):

    def test_pure_modules_import_no_observability(self):
        """§12.7: *"Module ohne Logging (event_models, event_protocol,
        event_normalizer, feedback_reducer, feedback_mapping,
        settings_metadata, actions, version): bewusst rein, nicht aendern."*"""
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[1] / "voice_stt_client" / "core"
        for name in (
            "event_models",
            "event_protocol",
            "event_normalizer",
            "feedback_reducer",
            "feedback_mapping",
            "settings_metadata",
            "actions",
            "version",
        ):
            with self.subTest(module=name):
                source = (root / f"{name}.py").read_text(encoding="utf-8")
                self.assertNotIn("observability", source)



if __name__ == "__main__":
    unittest.main()
