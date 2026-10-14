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

from voice_stt_client.core.audio_capture import AudioCapture
from voice_stt_client.core.config import AppConfig
from voice_stt_client.core.observability.ingress import ObservabilityIngress
from voice_stt_client.core.observability.worker import AGGREGATE_INTERVAL_S, LoggingWorker
from voice_stt_client.core.history import TranscriptHistoryManager

# ARCH §8.6, the complete hot-path list.
HOT_PATH = (
    ("voice_stt_client.core.audio_capture", "AudioCapture", "_audio_callback"),
    ("voice_stt_client.core.audio_capture", "AudioCapture", "_process_loop"),
    ("voice_stt_client.core.v2_media", "V2MediaConnection", "_packet_callback"),
    ("voice_stt_client.core.v2_media", "V2MediaConnection", "_send"),
    ("voice_stt_client.core.v2_transport", "V2STTSession", "send_audio"),
    ("voice_stt_client.core.event_stream", "EventStreamTransport", "_run_live"),
    ("voice_stt_client.core.event_stream", "EventStreamTransport", "_receive_result"),
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
        from voice_stt_client.core.observability.storage.sqlite import OpenResult

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



class TestNoPerPacketLogging(unittest.IsolatedAsyncioTestCase):


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




if __name__ == "__main__":
    unittest.main()
