"""
OBS-040 — ServerLiveAdapter and the server-event normalisation it feeds.

Frozen sources: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §3.2 (field mapping for
EVENT and CONTROL results), §5.5 (dedupe key and "die ERSTE gespeicherte
Fassung gewinnt"), §6 (``observe_server_result``), §7.3 (two error levels),
§12.4 (``logging.record_rejected``); ``LOGGING_ARCHITEKTUR_FREEZE_V1.md``
§7.2 (priority incl. ``not replayed``), §8.2 (``raw`` is not copied in the
producer), §8.3 (Normalizer exception -> malformed + one substitute record).

Everything here uses the REAL ``EventProtocolProcessor`` and the REAL
``ObservabilityIngress``. A double for either would define the very semantics
under test.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import MappingProxyType

from core.event_cursor_store import EventCursorStore
from core.event_models import EventOrigin
from core.event_protocol import (
    EventProtocolProcessor,
    EventResultKind,
    EventStreamAccess,
)
from core.observability.adapters.server_live import ServerLiveAdapter
from core.observability.ingress import ObservabilityIngress
from core.observability.models import RecordPriority
from core.session_coordinator import SessionContext

ENDPOINT = "wss://stt.voice.marcosudau.com/ws/logs"


def access(**changes) -> EventStreamAccess:
    values = {
        "endpoint": ENDPOINT,
        "session_id": "session-1",
        "access_token": "session-secret-token",
        "server_instance_id": "server-1",
        "oldest_cursor": 0,
        "latest_cursor": 20,
        "channels": ("transcription",),
    }
    values.update(changes)
    return EventStreamAccess(**values)


def hello_frame(**changes) -> dict:
    values = {
        "type": "log.hello",
        "schemaVersion": 1,
        "logProtocolVersion": 2,
        "deliveryMode": "sqlite_first",
        "replayAvailable": True,
        "serverInstanceId": "server-1",
        "oldestCursor": 0,
        "latestCursor": 20,
        "retentionCursor": 0,
        # R-6: hello demonstrably carries the session log token.
        "logAccess": {
            "available": True,
            "accessToken": "another-session-secret",
            "serverInstanceId": "server-1",
            "oldestCursor": 0,
            "latestCursor": 20,
        },
        "sessionConfig": {"warnings": ["w1"], "fallbacks": [], "ignoredFields": []},
    }
    values.update(changes)
    return values


def subscribed_frame(after_cursor: int = 0, **changes) -> dict:
    values = {
        "type": "log.subscribed",
        "channels": ["transcription"],
        "sessionId": "session-1",
        "afterCursor": after_cursor,
        "authorizationScope": "session",
        "allChannels": False,
        "allSessions": False,
    }
    values.update(changes)
    return values


def envelope(cursor: int, event_id: str, **changes) -> dict:
    values = {
        "schemaVersion": 1,
        "eventId": event_id,
        "cursor": cursor,
        "timestamp": "2026-08-09T12:00:00Z",
        "channel": "transcription",
        "event": "transcription.completed",
        "severity": "info",
        "serverInstanceId": "server-1",
        "sessionId": "session-1",
        "segmentId": 7,
        "transcriptionId": "session-1:3:7",
        "data": {"reason": "done", "activationId": "act-9"},
        # §3.2: the server puts the human-readable message under the German,
        # undocumented top-level key "meldung"; the envelope does not know it
        # and therefore pushes it into ``EventEnvelope.extra``.
        "meldung": "Transkription abgeschlossen",
    }
    values.update(changes)
    return values


def event_frame(cursor: int, event_id: str, *, replay: bool, **changes) -> dict:
    return {
        "type": "log.event",
        "event": envelope(cursor, event_id, **changes),
        "replay": replay,
    }


def replay_completed_frame(cursor: int = 0, count: int = 0) -> dict:
    return {"type": "log.replay_completed", "cursor": cursor, "count": count}


def gap_frame(from_cursor: int, to_cursor: int) -> dict:
    return {
        "type": "log.gap",
        "lostFromCursor": from_cursor,
        "lostToCursor": to_cursor,
        "reason": "retention",
        "oldestCursor": from_cursor,
        "latestCursor": 20,
    }


def build_ingress(**changes) -> ObservabilityIngress:
    values = {"instance_id": "client-instance-1", "queue_size": 512}
    values.update(changes)
    return ObservabilityIngress(**values)


def enter_replay(processor: EventProtocolProcessor, after_cursor: int = 0) -> None:
    processor.begin_subscription()
    processor.process_mapping(hello_frame())
    processor.process_mapping(subscribed_frame(after_cursor))


def context(**changes) -> SessionContext:
    values = {"generation": 3, "session_id": "session-1"}
    values.update(changes)
    return SessionContext(**values)


class TestServerEventNormalisation(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = EventProtocolProcessor(access())
        enter_replay(self.processor)
        self.processor.process_mapping(replay_completed_frame())
        self.ingress = build_ingress()
        self.adapter = ServerLiveAdapter(self.ingress)

    def observe(self, frame: dict, ctx: SessionContext = None):
        result = self.processor.process_mapping(frame)
        self.adapter.observe(ctx if ctx is not None else context(), result)
        return result

    def test_live_event_maps_every_frozen_field(self):
        self.observe(event_frame(5, "evt-5", replay=False))
        [record] = self.ingress.drain(10, 0.0)

        self.assertEqual(record.producer_kind, "server")
        self.assertEqual(record.producer_id, "voice-stt-server")
        # CONTRACTS §1.1: instance_id of a server record is the SERVER's.
        self.assertEqual(record.instance_id, "server-1")
        self.assertEqual(record.scope, "session")
        self.assertEqual(record.channel, "transcription")
        self.assertEqual(record.level, "INFO")
        self.assertEqual(record.type, "transcription.completed")
        # §1.1: component is the namespace prefix of type, never the transport.
        self.assertEqual(record.component, "transcription")
        self.assertEqual(record.session_id, "session-1")
        # §1.1: generation is taken from the SessionContext, not the envelope.
        self.assertEqual(record.generation, 3)
        self.assertEqual(record.activation_id, "act-9")
        self.assertEqual(record.segment_id, 7)
        self.assertEqual(record.transcription_id, "session-1:3:7")
        self.assertEqual(record.event_id, "evt-5")
        self.assertEqual(record.server_cursor, 5)
        # §3.2 / Befund C-2: message comes from extra["meldung"] and nowhere else.
        self.assertEqual(record.message, "Transkription abgeschlossen")
        self.assertFalse(record.replayed)

    def test_segment_id_is_stored_as_integer_even_though_the_server_db_uses_text(self):
        self.observe(event_frame(6, "evt-6", replay=False, segmentId=11))
        [record] = self.ingress.drain(10, 0.0)
        self.assertIsInstance(record.segment_id, int)
        self.assertEqual(record.segment_id, 11)

    def test_unknown_severity_falls_back_to_info_and_keeps_the_original(self):
        self.observe(event_frame(7, "evt-7", replay=False, severity="notice"))
        [record] = self.ingress.drain(10, 0.0)
        self.assertEqual(record.level, "INFO")
        self.assertEqual(dict(record.details)["source_severity"], "notice")

    def test_warning_severity_is_mapped_and_ranks_as_high(self):
        self.observe(event_frame(8, "evt-8", replay=False, severity="warning"))
        [record] = self.ingress.drain(10, 0.0)
        self.assertEqual(record.level, "WARNING")
        self.assertIs(record.priority, RecordPriority.HIGH)

    def test_raw_is_the_frozen_reference_and_is_not_copied(self):
        """ARCH §8.2: the producer takes over the frozen reference, it neither
        copies nor serialises it. Identity is the check that proves it."""
        result = self.observe(event_frame(9, "evt-9", replay=False))
        [record] = self.ingress.drain(10, 0.0)
        self.assertIsInstance(record.raw, MappingProxyType)
        self.assertIs(record.raw, result.payload)

    def test_store_raw_payload_false_stores_no_raw(self):
        ingress = build_ingress(store_raw_payload=False)
        adapter = ServerLiveAdapter(ingress)
        result = self.processor.process_mapping(event_frame(10, "evt-10", replay=False))
        adapter.observe(context(), result)
        [record] = ingress.drain(10, 0.0)
        self.assertIsNone(record.raw)

    def test_performance_channel_never_carries_raw(self):
        """FD-D2: one rule -- raw is stored unless channel == performance."""
        processor = EventProtocolProcessor(
            access(channels=("performance",))
        )
        processor.begin_subscription()
        processor.process_mapping(hello_frame())
        processor.process_mapping(
            subscribed_frame(0, channels=["performance"])
        )
        processor.process_mapping(replay_completed_frame())
        adapter = ServerLiveAdapter(self.ingress)
        result = processor.process_mapping(
            event_frame(4, "evt-perf", replay=False, channel="performance")
        )
        adapter.observe(context(), result)
        [record] = self.ingress.drain(10, 0.0)
        self.assertEqual(record.channel, "performance")
        self.assertIsNone(record.raw)


class TestReplayedAndPriority(unittest.TestCase):
    def test_replayed_event_is_marked_and_ranks_as_low(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        ingress = build_ingress()
        adapter = ServerLiveAdapter(ingress)

        result = processor.process_mapping(event_frame(3, "evt-3", replay=True))
        self.assertIs(result.origin, EventOrigin.REPLAY)
        adapter.observe(context(), result)
        [record] = ingress.drain(10, 0.0)

        self.assertTrue(record.replayed)
        # FD-R1 / ARCH §7.2: replayed records are LOW even with a type set.
        self.assertIs(record.priority, RecordPriority.LOW)

    def test_live_event_of_the_same_shape_ranks_as_high(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        processor.process_mapping(replay_completed_frame())
        ingress = build_ingress()
        adapter = ServerLiveAdapter(ingress)

        result = processor.process_mapping(event_frame(4, "evt-4", replay=False))
        adapter.observe(context(), result)
        [record] = ingress.drain(10, 0.0)

        self.assertFalse(record.replayed)
        self.assertIs(record.priority, RecordPriority.HIGH)

    def test_replayed_low_records_are_dropped_above_the_watermark(self):
        """The point of FD-R1: the replay flood protection actually engages."""
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        ingress = build_ingress(queue_size=8)
        adapter = ServerLiveAdapter(ingress)

        for index in range(20):
            result = processor.process_mapping(
                event_frame(index + 1, f"evt-r{index}", replay=True)
            )
            adapter.observe(context(), result)

        snapshot = ingress.health.snapshot()
        self.assertGreater(snapshot.dropped_watermark, 0)
        self.assertLessEqual(snapshot.enqueued, 8)


class TestEventIdentityAndDedupe(unittest.TestCase):
    def test_duplicate_is_observed_but_produces_no_second_stored_row(self):
        """FD-W9 / WP-OBS-040: *"Ein Duplikat erzeugt KEINEN Record mit
        replayed=True. Es wird beobachtet, normalisiert und an den Store
        uebergeben; der Store fuegt KEINE zweite Zeile ein."*

        The store half is OBS-030's dedupe index; what OBS-040 owns is that the
        duplicate is *observed at all* -- it never reaches ``on_event``.
        """
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        processor.process_mapping(replay_completed_frame())
        ingress = build_ingress()
        adapter = ServerLiveAdapter(ingress)

        first = processor.process_mapping(event_frame(5, "evt-5", replay=False))
        processor.confirm_event(first)
        adapter.observe(context(), first)
        duplicate = processor.process_mapping(event_frame(5, "evt-5", replay=False))
        self.assertTrue(duplicate.duplicate)
        adapter.observe(context(), duplicate)

        records = ingress.drain(10, 0.0)
        self.assertEqual(len(records), 2)
        original, marked = records
        self.assertEqual(original.event_id, "evt-5")
        self.assertFalse(original.replayed)
        # §3.2: a duplicate is mapped through the CONTROL path -- producer
        # client, component eventstream, and NEVER a server event_id, so the
        # dedupe index cannot collapse it with the original row.
        self.assertEqual(marked.producer_kind, "client")
        self.assertEqual(marked.component, "eventstream")
        self.assertIsNone(marked.event_id)
        self.assertFalse(marked.replayed)

    def test_event_id_is_stable_across_live_and_replay_of_the_same_event(self):
        processor = EventProtocolProcessor(access())
        enter_replay(processor)
        ingress = build_ingress()
        adapter = ServerLiveAdapter(ingress)

        replayed = processor.process_mapping(event_frame(6, "evt-6", replay=True))
        adapter.observe(context(), replayed)
        processor.confirm_event(replayed)
        processor.process_mapping(replay_completed_frame(6, 1))
        live = processor.process_mapping(event_frame(7, "evt-7", replay=False))
        adapter.observe(context(), live)

        records = ingress.drain(10, 0.0)
        self.assertEqual([item.event_id for item in records], ["evt-6", "evt-7"])
        self.assertEqual([item.server_cursor for item in records], [6, 7])
        # §5.5 GRENZE 3: cursors are only comparable within one instance_id.
        self.assertEqual({item.instance_id for item in records}, {"server-1"})


class TestControlFrames(unittest.TestCase):
    def setUp(self) -> None:
        self.processor = EventProtocolProcessor(access())
        self.ingress = build_ingress()
        self.adapter = ServerLiveAdapter(self.ingress)

    def test_hello_is_whitelisted_and_never_stores_raw(self):
        """R-6 / FD-D5: hello is diagnostically valuable AND carries
        ``logAccess.accessToken``. Whitelist, never raw."""
        self.processor.begin_subscription()
        result = self.processor.process_mapping(hello_frame())
        self.adapter.observe(context(), result)
        [record] = self.ingress.drain(10, 0.0)

        self.assertEqual(record.type, "client.eventstream.hello")
        self.assertEqual(record.producer_kind, "client")
        self.assertEqual(record.component, "eventstream")
        self.assertIsNone(record.raw)
        details = dict(record.details)
        self.assertIn("sessionConfig", details)
        log_access = dict(details["logAccess"])
        self.assertNotIn("accessToken", log_access)
        self.assertNotIn("another-session-secret", repr(details))

    def test_gap_keeps_the_lost_cursor_range_visible(self):
        """§3.2: log.gap(reason=retention) is definitive server-side data loss
        and is stored as its own record so the hole stays VISIBLE."""
        enter_replay(self.processor)
        result = self.processor.process_mapping(gap_frame(11, 14))
        self.adapter.observe(context(), result)
        records = self.ingress.drain(10, 0.0)
        gap = [item for item in records if item.type == "client.eventstream.gap"]
        self.assertEqual(len(gap), 1)
        details = dict(gap[0].details)
        self.assertEqual(details["lostFromCursor"], 11)
        self.assertEqual(details["lostToCursor"], 14)
        self.assertEqual(gap[0].level, "WARNING")

    def test_control_frames_take_the_client_instance_id(self):
        self.processor.begin_subscription()
        result = self.processor.process_mapping(hello_frame())
        self.adapter.observe(context(), result)
        [record] = self.ingress.drain(10, 0.0)
        self.assertEqual(record.instance_id, "client-instance-1")

    def test_control_frame_without_session_is_scope_instance(self):
        self.processor.begin_subscription()
        result = self.processor.process_mapping(hello_frame())
        self.adapter.observe(SessionContext(generation=1), result)
        [record] = self.ingress.drain(10, 0.0)
        self.assertEqual(record.scope, "instance")


class TestAdapterFailureIsolation(unittest.TestCase):
    class BrokenIngress(ObservabilityIngress):
        def __init__(self) -> None:
            super().__init__(instance_id="broken", queue_size=8)
            self.calls = 0

        def observe_server_result(self, ctx, result):
            self.calls += 1
            raise RuntimeError("normalizer exploded")

    def test_adapter_catches_and_reports_and_never_raises(self):
        """ARCH §7.3 level 1: the adapter catches itself and reports to
        LoggingInternalHealth -- that is where the visibility comes from."""
        ingress = self.BrokenIngress()
        adapter = ServerLiveAdapter(ingress)

        # No assertRaises: the whole point is that nothing escapes.
        adapter.observe(context(), object())

        self.assertEqual(ingress.calls, 1)
        snapshot = ingress.health.snapshot()
        self.assertEqual(snapshot.malformed, 1)
        # Health stays OK -- ARCH §8.3, row "Normalizer-Ausnahme".
        self.assertEqual(snapshot.state.value, "ok")

    def test_adapter_emits_exactly_one_record_rejected_without_original_data(self):
        """N-1 / ARCH §8.3 / CONTRACTS §12.4: one substitute record with
        component and exception type, WITHOUT the original data."""
        ingress = self.BrokenIngress()
        adapter = ServerLiveAdapter(ingress)
        adapter.observe(context(), object())

        [record] = ingress.drain(10, 0.0)
        self.assertEqual(record.type, "logging.record_rejected")
        self.assertEqual(record.channel, "performance")
        self.assertTrue(record.is_internal)
        self.assertIs(record.priority, RecordPriority.HIGH)
        details = dict(record.details)
        self.assertEqual(details["exception"], "RuntimeError")
        self.assertIn("server_live", details["component"])
        self.assertIsNone(record.message)
        self.assertIsNone(record.raw)

    def test_cancellation_is_never_swallowed(self):
        """ARCH §7.3: BaseException is caught NOWHERE. asyncio.CancelledError
        carries the cancellation of the event-stream task."""

        class CancellingIngress(ObservabilityIngress):
            def __init__(self) -> None:
                super().__init__(instance_id="cancel", queue_size=4)

            def observe_server_result(self, ctx, result):
                raise __import__("asyncio").CancelledError()

        adapter = ServerLiveAdapter(CancellingIngress())
        with self.assertRaises(BaseException) as caught:
            adapter.observe(context(), object())
        self.assertIsInstance(caught.exception, BaseException)
        self.assertNotIsInstance(caught.exception, Exception)

    def test_a_broken_result_object_produces_no_record_and_no_exception(self):
        """§3 *"Der Normalizer wirft nie. Im Zweifel liefert er None."*

        A result object that explodes on attribute access therefore yields
        neither a record nor a raised exception — and no substitute record,
        because nothing was rejected that could be reported. The counted case
        is the one below, where the normalizer contract itself is broken.
        """
        ingress = build_ingress()
        adapter = ServerLiveAdapter(ingress)

        class ExplodingResult:
            @property
            def kind(self):
                raise ValueError("kind explodes")

        adapter.observe(context(), ExplodingResult())

        self.assertEqual(ingress.drain(10, 0.0), [])
        self.assertEqual(ingress.health.snapshot().malformed, 0)

    def test_ingress_guard_reports_a_throwing_normalizer(self):
        """The ingress' own ``except`` is the second line of defence for a
        normalizer that breaks its "never raises" contract. Reachable only by
        replacing the normalizer, which is exactly what makes it worth a test:
        the guard must count ``malformed`` and emit one substitute record."""
        import core.observability.ingress as ingress_module

        ingress = build_ingress()
        adapter = ServerLiveAdapter(ingress)
        original = ingress_module.from_server_result

        def exploding(*args, **kwargs):
            raise RuntimeError("normalizer contract broken")

        ingress_module.from_server_result = exploding
        try:
            adapter.observe(context(), object())
        finally:
            ingress_module.from_server_result = original

        self.assertEqual(ingress.health.snapshot().malformed, 1)
        [record] = ingress.drain(10, 0.0)
        self.assertEqual(record.type, "logging.record_rejected")
        self.assertIn("normalizer.server", dict(record.details)["component"])
        self.assertEqual(dict(record.details)["exception"], "RuntimeError")


class TestCursorSemanticsAreUntouched(unittest.TestCase):
    def test_observation_neither_commits_nor_advances_the_cursor(self):
        """The adapter is passive: with the REAL cursor store on a temporary
        file, observing an event must not create or change the file."""
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cursor.json"
            store = EventCursorStore(path)
            processor = EventProtocolProcessor(access(), cursor_store=store)
            enter_replay(processor)
            processor.process_mapping(replay_completed_frame())
            ingress = build_ingress()
            adapter = ServerLiveAdapter(ingress)

            result = processor.process_mapping(event_frame(5, "evt-5", replay=False))
            adapter.observe(context(), result)

            self.assertFalse(path.exists())
            self.assertEqual(processor.resume_cursor, 0)

            processor.confirm_event(result)
            self.assertTrue(path.exists())
            self.assertEqual(processor.resume_cursor, 5)
            self.assertEqual(result.kind, EventResultKind.EVENT)


if __name__ == "__main__":
    unittest.main()
