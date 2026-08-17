"""
OBS-040 — hot-path rules and the 5-second aggregate.

Frozen source: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.6. The hot-path
functions may only increment plain ``int`` attributes; the aggregate record is
produced by the **worker**, which READS those counters.

The proof §8.6 itself prescribes is a source-reading test: *"ein Test, der den
QUELLTEXT der genannten Funktionen liest und belegt, dass dort kein submit, kein
format, kein json und kein Attributzugriff auf den Ingress steht."* That test
lives here for the full list of nine functions, and is complemented by a
behavioural one: 1000 audio packets produce zero records.
"""

from __future__ import annotations

import inspect
import unittest

from core.audio_capture import AudioCapture
from core.config import AppConfig
from core.controller import STTController
from core.observability.ingress import ObservabilityIngress
from core.observability.worker import AGGREGATE_INTERVAL_S, LoggingWorker
from core.stt_session import STTSession
from tests.test_controller import (
    FakeAudioCapture,
    FakeInjectionQueue,
    FakeSessionCoordinator,
    FakeSTTSession,
)
from core.history import TranscriptHistoryManager

# ARCH §8.6, the complete hot-path list.
HOT_PATH = (
    ("core.audio_capture", "AudioCapture", "_audio_callback"),
    ("core.audio_capture", "AudioCapture", "_process_loop"),
    ("core.controller", "STTController", "_on_audio_packet_from_thread"),
    ("core.controller", "STTController", "_enqueue_audio_packet"),
    ("core.controller", "STTController", "_audio_sender"),
    ("core.stt_session", "STTSession", "send_audio"),
    ("core.stt_session", "STTSession", "_message_loop"),
    ("core.event_stream", "EventStreamTransport", "_run_live"),
    ("core.event_stream", "EventStreamTransport", "_receive_result"),
)

# What OBS-040 must not have introduced: any route from a hot-path function to
# the observation boundary.
#
# ``json``/``format`` are deliberately NOT in this list. §8.6 rules out "Format-
# und JSON-Aufwand" *for observation*; ``_run_live`` has serialised its own
# protocol ping with ``json.dumps`` since long before this work package, and
# ``_message_loop`` carries pre-existing ``logger`` lines that §12.7 explicitly
# keeps ("der bestehende DEBUG-Log bleibt und wird vom Handlerlevel gefiltert").
# Forbidding them here would fail on product code OBS-040 did not write and
# must not change.
FORBIDDEN_IN_HOT_PATH = (
    "submit(",
    "_observe",
    "observability",
    "ingress",
)


class _RecordingStore:
    def __init__(self) -> None:
        self.rows = []

    def open(self):
        from core.observability.storage.sqlite import OpenResult

        return OpenResult(True, False, "")

    def write_batch(self, records):
        self.rows.extend(records)
        return (len(records), 0)

    def clear(self):
        return 0

    def run_retention(self, **kwargs):
        return (0, 0)

    def probe_write(self):
        return True

    def measure_db_bytes(self):
        return None

    def close(self):
        return None


def build_ingress(**changes) -> ObservabilityIngress:
    values = {"instance_id": "client-instance-1", "queue_size": 4096, "level": "DEBUG"}
    values.update(changes)
    return ObservabilityIngress(**values)


class TestHotPathSourceIsClean(unittest.TestCase):
    def test_no_hot_path_function_touches_the_observation_boundary(self):
        for module_name, class_name, function_name in HOT_PATH:
            with self.subTest(function=f"{class_name}.{function_name}"):
                module = __import__(module_name, fromlist=[class_name])
                owner = getattr(module, class_name)
                self.assertTrue(
                    hasattr(owner, function_name),
                    f"{class_name}.{function_name} disappeared -- §8.6's list "
                    "must be kept in sync with the code",
                )
                source = inspect.getsource(getattr(owner, function_name))
                for forbidden in FORBIDDEN_IN_HOT_PATH:
                    self.assertNotIn(
                        forbidden,
                        source,
                        f"§8.6 violation: {class_name}.{function_name} contains "
                        f"{forbidden!r}",
                    )

    def test_the_counter_increments_are_actually_there(self):
        """The counterpart: §8.6 permits exactly this, and the aggregate is
        worthless if nobody increments."""
        source = inspect.getsource(AudioCapture._audio_callback)
        self.assertIn("self.chunks_captured += 1", source)
        self.assertIn("self.chunks_dropped_capture_queue += 1", source)
        self.assertIn("self.overflow_count += 1", source)
        send_source = inspect.getsource(STTSession.send_audio)
        self.assertIn("self.packets_sent += 1", send_source)
        self.assertIn("self.bytes_sent += len(packet)", send_source)


class TestNoPerPacketLogging(unittest.IsolatedAsyncioTestCase):
    async def test_a_thousand_audio_packets_produce_no_record(self):
        """*"bei 40-ms-Chunks sind das 25 Callbacks je Sekunde und Richtung.
        Eine Zeile je Chunk ergaebe ~90.000 Records je Stunde Diktat."*"""
        ingress = build_ingress()
        config = AppConfig()
        session = STTSession(config.server, config.session, observability=ingress)
        sent = []

        class FakeWebSocket:
            async def send(self, packet):
                sent.append(packet)

        session._ws = FakeWebSocket()
        session._ws_is_open = lambda: True
        session._streaming = True

        for _ in range(1000):
            await session.send_audio(b"\x00\x01" * 320, 16000, 1, 320)

        self.assertEqual(len(sent), 1000)
        self.assertEqual(ingress.drain(4096, 0.0), [])
        self.assertEqual(ingress.health.snapshot().enqueued, 0)
        # The counters, however, moved.
        self.assertEqual(session.packets_sent, 1000)
        self.assertGreater(session.bytes_sent, 0)

    async def test_a_thousand_enqueues_produce_no_record(self):
        ingress = build_ingress()
        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=FakeSTTSession(),
            audio=FakeAudioCapture(),
            history_manager=TranscriptHistoryManager(config.history),
            injection_queue=FakeInjectionQueue(),
            session_coordinator=FakeSessionCoordinator(),
            observability=ingress,
        )
        self.addAsyncCleanup(controller.shutdown)
        controller._loop = None
        controller.session.set_streaming(True)
        controller._dictation_state = type(controller._dictation_state)("active")
        ingress.drain(4096, 0.0)

        for index in range(1000):
            controller._enqueue_audio_packet(
                (b"\x00", 16000, 1, 320, controller.session.generation)
            )

        self.assertEqual(ingress.drain(4096, 0.0), [])
        # The queue holds 300; the rest is counted, not logged.
        self.assertGreater(controller.chunks_dropped_send_queue, 0)
        self.assertGreater(controller.max_send_queue_depth, 0)

    def test_a_thousand_capture_callbacks_produce_no_record(self):
        import numpy as np

        ingress = build_ingress()
        capture = AudioCapture(AppConfig().audio, observability=ingress)
        chunk = np.zeros((320, 1), dtype=np.int16)
        for _ in range(1000):
            capture._audio_callback(chunk, 320, None, None)

        self.assertEqual(ingress.drain(4096, 0.0), [])
        self.assertEqual(
            capture.chunks_captured + capture.chunks_dropped_capture_queue, 1000
        )
        self.assertGreater(capture.chunks_dropped_capture_queue, 0)


class TestWorkerProducesTheAggregate(unittest.TestCase):
    def test_the_worker_reads_the_registered_counters(self):
        ingress = build_ingress()
        store = _RecordingStore()
        worker = LoggingWorker(ingress, store, batch_size=10, flush_interval_s=0.01)
        ingress.register_aggregate_source(
            "client.audio.stream_stats",
            lambda: {"chunks_captured": 25, "packets_sent": 25},
            component="audio",
        )

        worker._emit_aggregates_if_due()

        [record] = store.rows
        self.assertEqual(record.type, "client.audio.stream_stats")
        self.assertEqual(record.channel, "performance")
        self.assertEqual(record.level, "DEBUG")
        self.assertEqual(record.component, "audio")
        self.assertEqual(record.producer_kind, "client")
        self.assertEqual(record.instance_id, "client-instance-1")
        # §1.5: is_internal is reserved for logging's OWN records.
        self.assertFalse(record.is_internal)
        self.assertEqual(dict(record.details)["chunks_captured"], 25)

    def test_the_interval_is_respected(self):
        ingress = build_ingress()
        store = _RecordingStore()
        worker = LoggingWorker(ingress, store)
        ingress.register_aggregate_source(
            "client.audio.stream_stats", lambda: {"chunks_captured": 1}
        )

        worker._emit_aggregates_if_due()
        worker._emit_aggregates_if_due()
        worker._emit_aggregates_if_due()

        self.assertEqual(len(store.rows), 1)
        self.assertGreaterEqual(AGGREGATE_INTERVAL_S, 5.0)

    def test_a_source_returning_none_produces_nothing(self):
        """*"alle 5 s WAEHREND AKTIVEN STREAMINGS"* -- an idle producer must
        not produce a record per interval for the rest of the process."""
        ingress = build_ingress()
        store = _RecordingStore()
        worker = LoggingWorker(ingress, store)
        ingress.register_aggregate_source(
            "client.audio.stream_stats", lambda: None
        )
        worker._emit_aggregates_if_due()
        self.assertEqual(store.rows, [])

    def test_a_throwing_source_is_counted_and_does_not_break_the_worker(self):
        ingress = build_ingress()
        store = _RecordingStore()
        worker = LoggingWorker(ingress, store)

        def exploding():
            raise RuntimeError("counter read exploded")

        ingress.register_aggregate_source("client.audio.stream_stats", exploding)
        worker._emit_aggregates_if_due()

        self.assertEqual(store.rows, [])
        self.assertEqual(ingress.health.snapshot().malformed, 1)

    def test_the_ingress_level_still_filters_the_debug_aggregate(self):
        """ARCH §8.7: *"Ingress-Level gilt fuer strukturierte Clientevents"*.
        A default ``level: INFO`` installation must not silently collect the
        frozen DEBUG aggregates."""
        ingress = build_ingress(level="INFO")
        store = _RecordingStore()
        worker = LoggingWorker(ingress, store)
        ingress.register_aggregate_source(
            "client.audio.stream_stats", lambda: {"chunks_captured": 5}
        )
        worker._emit_aggregates_if_due()
        self.assertEqual(store.rows, [])

    def test_no_registered_source_means_no_work(self):
        ingress = build_ingress()
        store = _RecordingStore()
        worker = LoggingWorker(ingress, store)
        worker._emit_aggregates_if_due()
        self.assertEqual(store.rows, [])


class TestControllerAggregateSource(unittest.IsolatedAsyncioTestCase):
    async def test_the_source_merges_capture_and_send_counters_while_streaming(self):
        ingress = build_ingress()
        config = AppConfig()
        config.history.persistent.enabled = False
        session = STTSession(config.server, config.session, observability=ingress)
        session.packets_sent = 7
        session.bytes_sent = 700
        session._streaming = True
        capture = AudioCapture(config.audio, observability=ingress)
        capture.chunks_captured = 9
        controller = STTController(
            config,
            session=session,
            audio=capture,
            history_manager=TranscriptHistoryManager(config.history),
            injection_queue=FakeInjectionQueue(),
            session_coordinator=FakeSessionCoordinator(),
            observability=ingress,
        )
        self.addAsyncCleanup(controller.shutdown)

        stats = controller._collect_audio_stats()

        self.assertEqual(stats["packets_sent"], 7)
        self.assertEqual(stats["bytes_sent"], 700)
        self.assertEqual(stats["chunks_captured"], 9)
        self.assertIn("chunks_dropped_send_queue", stats)
        self.assertIn("max_send_queue_depth", stats)

    async def test_the_source_returns_none_when_nothing_streams(self):
        ingress = build_ingress()
        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=FakeSTTSession(),
            audio=FakeAudioCapture(),
            history_manager=TranscriptHistoryManager(config.history),
            injection_queue=FakeInjectionQueue(),
            session_coordinator=FakeSessionCoordinator(),
            observability=ingress,
        )
        self.addAsyncCleanup(controller.shutdown)
        self.assertIsNone(controller._collect_audio_stats())

    async def test_the_source_survives_a_component_without_counters(self):
        """The controller may be built with any session/audio double; a missing
        ``capture_counters``/``send_counters`` must not break the read."""
        ingress = build_ingress()
        config = AppConfig()
        config.history.persistent.enabled = False
        session = FakeSTTSession()
        session.set_streaming(True)
        controller = STTController(
            config,
            session=session,
            audio=FakeAudioCapture(),
            history_manager=TranscriptHistoryManager(config.history),
            injection_queue=FakeInjectionQueue(),
            session_coordinator=FakeSessionCoordinator(),
            observability=ingress,
        )
        self.addAsyncCleanup(controller.shutdown)
        stats = controller._collect_audio_stats()
        self.assertIsInstance(stats, dict)
        self.assertIn("chunks_dropped_send_queue", stats)


if __name__ == "__main__":
    unittest.main()
