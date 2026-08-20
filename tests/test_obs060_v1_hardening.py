"""
OBS-060 — V1 hardening: the regression tests for the findings this work
package closed, plus the anchors the mutation checks need.

Frozen sources: ``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §6.3 (non-blocking
invariant and its proof), §7.1/§7.2 (watermark and priority), §8.3 (failure
states, store suspension and the empty test write), §8.7 (one level value);
``LOGGING_CONTRACTS_FREEZE_V1.md`` §3 (*"Der Normalizer wirft nie. Im Zweifel
liefert er ``None``, und der Aufrufer zaehlt ``malformed``"*), §5.4/§5.5
(reader connections, dedupe key), §5.7 (keyset pagination), §8 (provider
contract), §11.2 (health, *"Recovery — Automatisch und still"*).

The three findings of this run:

* **B-1** ``FAILED_STORE`` was terminal. The suspension is set together with
  the health state, and from that moment ``Ingress.submit`` rejects every
  record — so no batch reached the worker, so the empty test write §8.3
  prescribes never ran and the automatic recovery §11.2 promises never
  happened.
* **B-2** ``ObservabilityIngress.event`` dropped a ``None`` from the client
  normalizer without counting it, although §3 puts that counting duty on the
  caller in so many words.
* **N-2 (OBS-030 gate)** the two startup guards in ``LoggingWorker.run``
  consumed part of the consecutive-failure budget that §8.3 gives the loop.
"""

from __future__ import annotations

import logging
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path

from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.manager import ObservabilityManager
from core.observability.models import CanonicalLogRecord, RecordPriority
from core.observability.query.base import ProviderState, QueryFilter
from core.observability.query.local import DEFAULT_LIMIT, MAX_LIMIT, LocalLogProvider
from core.observability.storage.sqlite import OpenResult, SQLiteLogStore
from core.observability.worker import LoggingWorker

import core.observability.worker as worker_module


def make_record(**overrides) -> CanonicalLogRecord:
    values = dict(
        record_id="rec-" + str(len(overrides)),
        received_at="2026-08-18T10:00:00.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="inst-1",
        scope="instance",
        channel="system",
        level="INFO",
        type="client.app.started",
    )
    values.update(overrides)
    return CanonicalLogRecord(**values)


def wait_until(predicate, timeout=10.0, interval=0.02) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


class _FlakyStore:
    """A store whose ``write_batch`` fails until ``fail`` is cleared."""

    def __init__(self, inner) -> None:
        self._inner = inner
        self.fail = True
        self.write_calls = 0
        self.probe_calls = 0

    def open(self) -> OpenResult:
        return self._inner.open()

    def write_batch(self, records):
        self.write_calls += 1
        if self.fail:
            raise sqlite3.OperationalError("injected write failure")
        return self._inner.write_batch(records)

    def probe_write(self) -> bool:
        self.probe_calls += 1
        return not self.fail

    def run_retention(self, **_kwargs):
        return (0, 0)

    def measure_db_bytes(self):
        return self._inner.measure_db_bytes()

    def clear(self) -> int:
        return self._inner.clear()

    def close(self) -> None:
        self._inner.close()


class TestStoreRecoveryIsReachable(unittest.TestCase):
    """B-1. ARCH §8.3 suspends the store for 60 s and then checks it *"mit
    einem leeren Testschreibvorgang"*; CONTRACTS §11.2 calls that recovery
    *"Automatisch und still"*."""

    def setUp(self) -> None:
        self._original_pause = worker_module.STORE_PAUSE_S
        worker_module.STORE_PAUSE_S = 0.3
        self._directory = tempfile.mkdtemp()

    def tearDown(self) -> None:
        worker_module.STORE_PAUSE_S = self._original_pause

    def _build(self):
        db = Path(self._directory) / "observability.sqlite3"
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=1024)
        store = _FlakyStore(SQLiteLogStore(db))
        worker = LoggingWorker(ingress, store, batch_size=1, flush_interval_s=0.02)
        return db, ingress, store, worker

    def test_a_suspended_store_recovers_without_a_new_batch(self):
        db, ingress, store, worker = self._build()
        worker.start()
        try:
            for index in range(12):
                ingress.event("client.app.started", channel="system", message=str(index))
            self.assertTrue(
                wait_until(lambda: ingress.health.state is LoggingHealthState.FAILED_STORE),
                "the store never reached FAILED_STORE",
            )
            # From here on the ingress rejects everything, so nothing can be
            # queued and no batch can carry the recovery.
            self.assertFalse(ingress.submit(make_record()))
            self.assertEqual(ingress.qsize(), 0)

            store.fail = False
            self.assertTrue(
                wait_until(lambda: ingress.health.state is LoggingHealthState.OK),
                "the store never recovered on its own",
            )
            self.assertGreaterEqual(store.probe_calls, 1)
        finally:
            worker.stop(2.0)

    def test_the_recovery_costs_a_probe_and_not_a_batch(self):
        _db, ingress, store, worker = self._build()
        worker.start()
        try:
            for index in range(12):
                ingress.event("client.app.started", channel="system", message=str(index))
            wait_until(lambda: ingress.health.state is LoggingHealthState.FAILED_STORE)
            writes_at_failure = store.write_calls
            store.fail = False
            wait_until(lambda: ingress.health.state is LoggingHealthState.OK)
            # The probe re-enabled the store. The only writes after that point
            # are the recovery record itself, never a retried batch.
            self.assertGreaterEqual(store.probe_calls, 1)
            self.assertLessEqual(store.write_calls - writes_at_failure, 1)
        finally:
            worker.stop(2.0)

    def test_a_still_broken_store_stays_suspended_and_is_probed_again(self):
        _db, ingress, store, worker = self._build()
        worker.start()
        try:
            for index in range(12):
                ingress.event("client.app.started", channel="system", message=str(index))
            wait_until(lambda: ingress.health.state is LoggingHealthState.FAILED_STORE)
            self.assertTrue(wait_until(lambda: store.probe_calls >= 2, timeout=5.0),
                            "the suspension was never re-checked")
            self.assertIs(ingress.health.state, LoggingHealthState.FAILED_STORE)
        finally:
            worker.stop(2.0)

    def test_exactly_one_recovery_record_documents_the_return(self):
        db, ingress, store, worker = self._build()
        worker.start()
        try:
            for index in range(12):
                ingress.event("client.app.started", channel="system", message=str(index))
            wait_until(lambda: ingress.health.state is LoggingHealthState.FAILED_STORE)
            store.fail = False
            wait_until(lambda: ingress.health.state is LoggingHealthState.OK)
            time.sleep(0.3)
        finally:
            worker.stop(2.0)
        connection = sqlite3.connect(str(db))
        try:
            count = connection.execute(
                "SELECT COUNT(*) FROM logs WHERE type = 'logging.recovered'"
            ).fetchone()[0]
        finally:
            connection.close()
        self.assertEqual(count, 1)


class TestNormalizerNoneIsCounted(unittest.TestCase):
    """B-2. CONTRACTS §3: *"Im Zweifel liefert er ``None``, und der Aufrufer
    zaehlt ``malformed``."*"""

    def test_a_client_event_the_normalizer_gives_up_on_is_counted(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        before = ingress.health.snapshot().malformed
        ingress.event("client.app.started", channel="system", details="not a mapping")
        self.assertEqual(ingress.health.snapshot().malformed, before + 1)

    def test_it_still_does_not_raise_and_leaves_health_ok(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        ingress.event("client.app.started", channel="system", details=["not", "a", "map"])
        self.assertIs(ingress.health.state, LoggingHealthState.OK)

    def test_no_record_is_enqueued_for_it(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        ingress.event("client.app.started", channel="system", details="not a mapping")
        self.assertEqual([item.type for item in ingress.drain(10, 0.0)], [])

    def test_a_healthy_event_is_still_not_counted_as_malformed(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        ingress.event("client.app.started", channel="system", details={"ok": 1})
        self.assertEqual(ingress.health.snapshot().malformed, 0)
        self.assertEqual(ingress.health.snapshot().enqueued, 1)

    def test_the_server_path_keeps_None_as_a_silent_decision(self):
        """``from_server_result`` returns ``None`` for result kinds that map to
        no record at all. Counting that as malformed would turn a decision
        into an error."""
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        ingress.observe_server_result(None, None)
        self.assertEqual(ingress.health.snapshot().malformed, 0)


class TestLoopFailureBudget(unittest.TestCase):
    """OBS-030 gate observation N-2: ARCH §8.3 counts consecutive failures of
    the LOOP; the two startup guards are not loop iterations."""

    class _FailingOpenStore:
        def __init__(self) -> None:
            self.opened = 0

        def open(self):
            self.opened += 1
            raise RuntimeError("open explodes")

        def write_batch(self, records):
            return (len(records), 0)

        def probe_write(self):
            return True

        def run_retention(self, **_kwargs):
            raise RuntimeError("retention explodes")

        def measure_db_bytes(self):
            return None

        def clear(self):
            return 0

        def close(self):
            return None

    def test_startup_guard_failures_do_not_consume_the_loop_budget(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        store = self._FailingOpenStore()
        worker = LoggingWorker(ingress, store, batch_size=4, flush_interval_s=0.02)
        worker.start()
        try:
            # both startup guards failed; the loop itself is still healthy
            self.assertTrue(wait_until(lambda: store.opened >= 1))
            time.sleep(0.2)
            self.assertEqual(worker._consecutive_loop_failures, 0)  # noqa: SLF001
            self.assertIsNot(ingress.health.state, LoggingHealthState.FAILED_WORKER)
            self.assertTrue(worker.is_alive())
        finally:
            worker.stop(2.0)

    def test_the_startup_failures_are_still_reported(self):
        """The reset must not make the startup failures invisible. Both have
        their own reporting path — a failed open is ``FAILED_STORE`` plus a
        rate-limited stderr line (ARCH §8.3), a failed retention is
        ``retention_errors`` (§11.2) — and neither is a loop failure."""
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        worker = LoggingWorker(ingress, self._FailingOpenStore(),
                               batch_size=4, flush_interval_s=0.02)
        worker.start()
        try:
            self.assertTrue(
                wait_until(lambda: ingress.health.state is LoggingHealthState.FAILED_STORE),
                "the failed open was not visible in Health",
            )
            self.assertTrue(
                wait_until(lambda: ingress.health.snapshot().retention_errors >= 1),
                "the failed startup retention was not counted",
            )
        finally:
            worker.stop(2.0)


class TestProviderCompleteFlag(unittest.TestCase):
    """OBS-050 gate observation N-4: ``complete=False`` means the provider cut
    something off (§8). Only the ``MAX_LIMIT`` clamp does that."""

    def setUp(self) -> None:
        self._directory = tempfile.mkdtemp()
        self.db = Path(self._directory) / "observability.sqlite3"
        store = SQLiteLogStore(self.db)
        store.open()
        store.write_batch([make_record(record_id="r-%02d" % index) for index in range(3)])
        store.close()
        self.provider = LocalLogProvider(self.db)

    def test_a_non_positive_limit_yields_a_complete_page(self):
        for limit in (0, -1, -100):
            with self.subTest(limit=limit):
                page = self.provider.query(QueryFilter(), None, limit)
                self.assertTrue(page.complete)
                self.assertEqual(len(page.records), 3)

    def test_a_limit_above_the_maximum_is_reported_as_incomplete(self):
        page = self.provider.query(QueryFilter(), None, MAX_LIMIT + 1)
        self.assertFalse(page.complete)

    def test_an_ordinary_limit_is_complete(self):
        page = self.provider.query(QueryFilter(), None, DEFAULT_LIMIT)
        self.assertTrue(page.complete)


class TestSinkIsNotRebuiltWithoutReason(unittest.TestCase):
    """OBS-050 gate observations N-1/N-2."""

    class _Config:
        enabled = True
        level = "INFO"
        queue_size = 64
        batch_size = 8
        flush_interval_s = 0.05
        retention_days = 14
        max_entries = 200000
        max_db_bytes = None
        store_enabled = False
        db_path = None
        store_raw_payload = True
        store_transcription_content = False
        file_sink_enabled = False
        file_sink_dir = None

        def __init__(self, **overrides):
            for key, value in overrides.items():
                setattr(self, key, value)

    class _WorkerSpy:
        def __init__(self):
            self.received = []

        def request_settings(self, **settings):
            self.received.append(settings)

    def test_an_unchanged_sink_configuration_hands_over_the_same_object(self):
        directory = tempfile.mkdtemp()
        config = self._Config(file_sink_enabled=True, file_sink_dir=directory)
        manager = ObservabilityManager(config, instance_id="inst-1")
        spy = self._WorkerSpy()
        manager._worker = spy  # noqa: SLF001
        manager._on_config_applied(config)
        manager._on_config_applied(config)
        self.assertEqual(len(spy.received), 2)
        self.assertIs(spy.received[0]["sink"], spy.received[1]["sink"])

    def test_a_changed_sink_configuration_builds_a_new_one(self):
        first = tempfile.mkdtemp()
        second = tempfile.mkdtemp()
        config = self._Config(file_sink_enabled=True, file_sink_dir=first)
        manager = ObservabilityManager(config, instance_id="inst-1")
        spy = self._WorkerSpy()
        manager._worker = spy  # noqa: SLF001
        manager._on_config_applied(config)
        manager._on_config_applied(self._Config(file_sink_enabled=True,
                                                file_sink_dir=second))
        self.assertIsNot(spy.received[0]["sink"], spy.received[1]["sink"])

    def test_a_failing_sink_build_no_longer_swallows_the_enabled_change(self):
        config = self._Config()
        manager = ObservabilityManager(config, instance_id="inst-1")
        manager._worker = self._WorkerSpy()  # noqa: SLF001

        def explode(_config):
            raise RuntimeError("P-8 path check exploded")

        manager._build_sink = explode  # noqa: SLF001
        manager._on_config_applied(self._Config(enabled=False,
                                                file_sink_enabled=True,
                                                file_sink_dir="X:/nowhere"))
        self.assertIs(manager.health.state, LoggingHealthState.DISABLED)


class TestNonBlockingInvariantAnchor(unittest.TestCase):
    """ARCH §6.3 and §7.1/§7.2 — the anchors the mutation checks use."""

    def test_submit_never_blocks_on_a_full_queue(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=8)
        for _ in range(64):
            ingress.submit(make_record(level="ERROR", type="x"))
        started = time.monotonic()
        for _ in range(2000):
            ingress.submit(make_record(level="ERROR", type="x"))
        elapsed = time.monotonic() - started
        # a blocking ``put`` on a full queue would never return at all
        self.assertLess(elapsed, 5.0, "submit blocked on a full queue")

    def test_the_watermark_stops_low_priority_before_the_queue_is_full(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=20)
        accepted = sum(
            1 for _ in range(40)
            if ingress.submit(make_record(level="INFO", type=None, channel="system"))
        )
        self.assertEqual(accepted, 15)
        self.assertGreater(ingress.health.snapshot().dropped_watermark, 0)
        self.assertTrue(
            ingress.submit(make_record(level="ERROR", type="client.app.crashed")),
            "a HIGH record must still pass the watermark",
        )

    def test_the_reader_connection_cannot_write(self):
        directory = tempfile.mkdtemp()
        db = Path(directory) / "observability.sqlite3"
        store = SQLiteLogStore(db)
        store.open()
        store.write_batch([make_record()])
        store.close()
        provider = LocalLogProvider(db)
        connection = provider._connect()  # noqa: SLF001
        try:
            with self.assertRaises(sqlite3.OperationalError):
                connection.execute("DELETE FROM logs")
        finally:
            connection.close()

    def test_a_client_record_without_event_id_is_never_deduplicated(self):
        directory = tempfile.mkdtemp()
        store = SQLiteLogStore(Path(directory) / "observability.sqlite3")
        store.open()
        try:
            inserted, deduplicated = store.write_batch(
                [make_record(record_id="a"), make_record(record_id="b")]
            )
            self.assertEqual((inserted, deduplicated), (2, 0))
        finally:
            store.close()

    def test_a_server_event_id_is_deduplicated_and_the_first_version_wins(self):
        directory = tempfile.mkdtemp()
        db = Path(directory) / "observability.sqlite3"
        store = SQLiteLogStore(db)
        store.open()
        try:
            store.write_batch([make_record(
                record_id="first", producer_kind="server",
                producer_id="voice-stt-server", event_id="evt-1", replayed=False)])
            inserted, deduplicated = store.write_batch([make_record(
                record_id="second", producer_kind="server",
                producer_id="voice-stt-server", event_id="evt-1", replayed=True)])
            self.assertEqual((inserted, deduplicated), (0, 1))
            rows = store._connection.execute(  # noqa: SLF001
                "SELECT record_id FROM logs WHERE event_id = 'evt-1'").fetchall()
            self.assertEqual([row[0] for row in rows], ["first"])
        finally:
            store.close()


class TestFrozenDdlIsPartial(unittest.TestCase):
    """FD-C7 freezes the dedupe key as a **partieller** UNIQUE index, and
    CONTRACTS §5.2 freezes the DDL that creates it.

    This guard is structural on purpose, and the reason is worth writing
    down. The mutation table of the work package expects that dropping
    ``WHERE event_id IS NOT NULL`` would make *"Clientrecords faelschlich
    dedupliziert"*. Measured against SQLite 3.49 that expectation does not
    hold: a UNIQUE index treats every ``NULL`` as distinct, so client rows
    without an ``event_id`` never collide either way, and the mutation has no
    behavioural consequence a functional test could see (OBS-060 finding
    O-2). What the predicate really buys is that the index carries only the
    server rows that have an ``event_id`` — a property of the frozen DDL, and
    therefore what this test pins.
    """

    def test_the_unique_index_is_created_with_its_frozen_predicate(self):
        directory = tempfile.mkdtemp()
        db = Path(directory) / "observability.sqlite3"
        store = SQLiteLogStore(db)
        store.open()
        store.close()
        connection = sqlite3.connect(str(db))
        try:
            row = connection.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type = 'index' AND name = 'ux_logs_producer_event'"
            ).fetchone()
        finally:
            connection.close()
        self.assertIsNotNone(row, "the dedupe index does not exist")
        normalised = " ".join((row[0] or "").split())
        self.assertIn("WHERE event_id IS NOT NULL", normalised)

    def test_the_index_holds_no_entry_for_a_client_row(self):
        """The measurable consequence of the predicate: rows without an
        ``event_id`` are not in the index at all."""
        directory = tempfile.mkdtemp()
        db = Path(directory) / "observability.sqlite3"
        store = SQLiteLogStore(db)
        store.open()
        try:
            store.write_batch([
                make_record(record_id="client-1"),
                make_record(record_id="client-2"),
                make_record(record_id="server-1", producer_kind="server",
                            producer_id="voice-stt-server", event_id="evt-1"),
            ])
            indexed = store._connection.execute(  # noqa: SLF001
                "SELECT COUNT(*) FROM logs "
                "INDEXED BY ux_logs_producer_event WHERE event_id IS NOT NULL"
            ).fetchone()[0]
        finally:
            store.close()
        self.assertEqual(indexed, 1)


class TestTranscriptPolicyAnchor(unittest.TestCase):
    """ARCH §8.7 / FD-D1: the realtime transcript line is a DEBUG line, and the
    default INFO level keeps it out of the store entirely."""

    def test_a_debug_realtime_line_does_not_reach_the_store_at_info_level(self):
        from core.observability.adapters.python_logging import UnifiedLogHandler
        from core.observability.normalizer import from_log_record

        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64, level="INFO")
        handler = UnifiedLogHandler(
            ingress,
            lambda record: from_log_record(
                record, instance_id="inst-1", store_transcription_content=False,
                user_profile=None),
        )
        handler.setLevel(ingress.level)

        logger = logging.getLogger("text")
        logger.setLevel(logging.DEBUG)
        logger.propagate = False
        logger.handlers = [handler]
        try:
            logger.debug("Realtime [seg=3]: streng geheimer zwischentext")
            drained = ingress.drain(10, 0.0)
        finally:
            logger.handlers = []

        self.assertEqual(drained, [], "the realtime DEBUG line reached the queue")

    def test_and_if_it_ever_did_the_content_would_still_be_redacted(self):
        from core.observability.redaction import redact_text

        redacted = redact_text("Realtime [seg=3]: streng geheimer zwischentext",
                               store_transcription_content=False)
        self.assertNotIn("geheimer", redacted)
        self.assertIn("[redacted:", redacted)


class TestInternalRecordsStayHigh(unittest.TestCase):
    """CONTRACTS §1.5: logging's own records are HIGH, so the record that
    explains a gap survives the overload that produced it."""

    def test_record_rejected_is_high(self):
        ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
        ingress.emit_record_rejected("observability.normalizer.client", ValueError("x"))
        [record] = [item for item in ingress.drain(10, 0.0)
                    if item.type == "logging.record_rejected"]
        self.assertIs(record.priority, RecordPriority.HIGH)
        self.assertEqual(set(dict(record.details)), {"component", "exception"})


if __name__ == "__main__":
    unittest.main()
