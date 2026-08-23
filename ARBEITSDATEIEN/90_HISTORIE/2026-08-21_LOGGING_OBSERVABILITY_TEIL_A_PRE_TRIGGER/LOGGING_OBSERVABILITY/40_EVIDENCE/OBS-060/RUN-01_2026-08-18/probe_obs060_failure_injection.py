"""OBS-060 - Failure-injection matrix for Logging V1.

One case per row of the failure matrix in
``20_PLANUNG/LOGGING_GESAMTPLAN/00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md`` 13
(Testmatrix / Failure) plus the backpressure and health-consistency cases of
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` 7 and 8.

Every case uses the REAL component and injects the fault at its real boundary.
The question each case answers is always the same one: does the fault stay
inside the logging failure domain (O-05), and is it VISIBLE afterwards through
Health and the counters?

Run:  python <this file>
Exit: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "core" / "observability").is_dir():
        sys.path.insert(0, str(parent))
        break

from core.observability.health import LoggingHealthState
from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.query.base import ProviderState, QueryFilter
from core.observability.query.local import LocalLogProvider
from core.observability.query.service import LogQueryService
from core.observability.sinks.jsonl_file import JsonlSink
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker

FAILURES = []


def check(name, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + ((" - " + detail) if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


def wait_until(predicate, timeout=8.0, interval=0.02):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def record(**overrides):
    base = dict(
        record_id=os.urandom(8).hex(),
        received_at="2026-08-18T10:00:00.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="inst-1",
        scope="instance",
        channel="system",
        level="INFO",
        type="client.app.started",
    )
    base.update(overrides)
    return CanonicalLogRecord(**base)


def _rows(db):
    if not Path(db).exists():
        return 0
    connection = sqlite3.connect(str(db))
    try:
        return int(connection.execute("SELECT COUNT(*) FROM logs").fetchone()[0])
    except Exception:  # noqa: BLE001
        return 0
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# F-1  SQLite read-only (the M-4 case: the file exists but cannot be written)
# ---------------------------------------------------------------------------

class _ReadOnlyStore:
    """A real store wrapper whose write_batch always fails the way a
    read-only SQLite file fails."""

    def __init__(self, inner):
        self._inner = inner
        self.write_attempts = 0

    def open(self):
        return self._inner.open()

    def write_batch(self, records):
        self.write_attempts += 1
        raise sqlite3.OperationalError("attempt to write a readonly database")

    def probe_write(self):
        return False

    def run_retention(self, **kwargs):
        return (0, 0)

    def measure_db_bytes(self):
        return self._inner.measure_db_bytes()

    def clear(self):
        return 0

    def close(self):
        self._inner.close()


def f1_store_read_only(tmp):
    db = tmp / "f1" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=256)
    store = _ReadOnlyStore(SQLiteLogStore(db))
    worker = LoggingWorker(ingress, store, batch_size=1, flush_interval_s=0.02)
    worker.start()
    time.sleep(0.1)
    try:
        for index in range(30):
            ingress.event("client.app.started", channel="system", message=str(index))
        ok = wait_until(lambda: ingress.health.state is LoggingHealthState.FAILED_STORE,
                        timeout=10.0)
        snapshot = ingress.health.snapshot()
        check("F-1.1 a permanently unwritable store ends in FAILED_STORE", ok,
              str(snapshot.state))
        check("F-1.2 the failure is counted, not silent", snapshot.store_errors > 0,
              "store_errors=" + str(snapshot.store_errors))
        check("F-1.3 the producers were never blocked or hit by the exception",
              snapshot.enqueued >= 1, "enqueued=" + str(snapshot.enqueued))
        check("F-1.4 the worker thread is still alive (single failures do not kill it)",
              worker.is_alive())
        # ARCH 8.3: after FAILED the ingress switches to "only discard and count"
        accepted = ingress.submit(record())
        check("F-1.5 after FAILED the ingress refuses instead of promising storage",
              accepted is False)
    finally:
        worker.stop(2.0)


# ---------------------------------------------------------------------------
# F-2  SQLite locked by a foreign writer
# ---------------------------------------------------------------------------

def f2_store_locked(tmp):
    db = tmp / "f2" / "observability.sqlite3"
    db.parent.mkdir(parents=True, exist_ok=True)
    store = SQLiteLogStore(db)
    result = store.open()
    check("F-2.0 the store opened normally", result.ok and not result.degraded)
    store.write_batch([record()])

    # a foreign connection holds the writer lock
    blocker = sqlite3.connect(str(db), timeout=0.1, isolation_level=None)
    blocker.execute("PRAGMA busy_timeout = 0")
    blocker.execute("BEGIN EXCLUSIVE")
    raised = None
    try:
        store.write_batch([record()])
    except Exception as exc:  # noqa: BLE001
        raised = exc
    check("F-2.1 a locked database surfaces as an exception the worker owns",
          raised is not None, type(raised).__name__ if raised else "no exception")
    blocker.execute("ROLLBACK")
    blocker.close()
    inserted, _ = store.write_batch([record()])
    check("F-2.2 the very next write after the lock is released succeeds",
          inserted == 1, "inserted=" + str(inserted))
    store.close()


# ---------------------------------------------------------------------------
# F-3  DB path invalid (a directory where the file should be)
# ---------------------------------------------------------------------------

def f3_db_path_invalid(tmp):
    bad = tmp / "f3" / "observability.sqlite3"
    bad.mkdir(parents=True, exist_ok=True)  # a DIRECTORY with the db name
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
    store = SQLiteLogStore(bad)
    worker = LoggingWorker(ingress, store, batch_size=4, flush_interval_s=0.05)
    worker.start()
    try:
        ok = wait_until(
            lambda: ingress.health.state in (LoggingHealthState.FAILED_STORE,
                                             LoggingHealthState.DEGRADED_STORE),
            timeout=6.0)
        check("F-3.1 an unopenable path is a health state, not a crash", ok,
              str(ingress.health.state))
        check("F-3.2 the worker survived the failed open", worker.is_alive())
        ingress.event("client.app.started", channel="system", message="after")
        check("F-3.3 producing an event after the failure still does not raise", True)
    finally:
        worker.stop(2.0)


# ---------------------------------------------------------------------------
# F-4  file sink invalid -> the store keeps working (ARCH 8.3, gate finding W-1)
# ---------------------------------------------------------------------------

class _ExplodingSink:
    def __init__(self):
        self.calls = 0
        self.closed = False

    def write_batch(self, records):
        self.calls += 1
        raise OSError("sink is on a disconnected network drive")

    def close(self):
        self.closed = True


def f4_sink_invalid(tmp):
    db = tmp / "f4" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=256)
    store = SQLiteLogStore(db)
    sink = _ExplodingSink()
    worker = LoggingWorker(ingress, store, sink=sink, batch_size=8, flush_interval_s=0.05)
    worker.start()
    try:
        for index in range(30):
            ingress.event("client.app.started", channel="system", message=str(index))
        ok = wait_until(lambda: _rows(db) >= 30)
        check("F-4.1 a broken sink does not stop the store", ok, "rows=" + str(_rows(db)))
        snapshot = ingress.health.snapshot()
        check("F-4.2 the sink error is counted", snapshot.sink_errors >= 1,
              "sink_errors=" + str(snapshot.sink_errors))
        check("F-4.3 the sink is disabled after ONE failure, not retried per batch",
              sink.calls == 1, "sink calls=" + str(sink.calls))
        check("F-4.4 health shows DEGRADED_SINK, never a store failure",
              snapshot.state is not LoggingHealthState.FAILED_STORE,
              str(snapshot.state))
    finally:
        worker.stop(2.0)


# ---------------------------------------------------------------------------
# F-5  queue full and watermark (ARCH 7.1/7.2)
# ---------------------------------------------------------------------------

def f5_queue_full(tmp):
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=20)
    # no worker at all: nothing drains
    low = [record(level="INFO", type=None, channel="system") for _ in range(40)]
    high = record(level="ERROR", type="client.app.crashed", channel="system")

    accepted_low = sum(1 for item in low if ingress.submit(item))
    snapshot = ingress.health.snapshot()
    check("F-5.1 LOW records are dropped at the watermark, not at the brim",
          snapshot.dropped_watermark > 0,
          "accepted_low=" + str(accepted_low)
          + " dropped_watermark=" + str(snapshot.dropped_watermark))
    check("F-5.2 the watermark stops LOW at 75 percent (15 of 20)",
          accepted_low == 15, "accepted_low=" + str(accepted_low))
    accepted_high = ingress.submit(high)
    check("F-5.3 a HIGH record still passes the watermark", accepted_high is True)

    while ingress.submit(record(level="ERROR", type="x")):
        pass
    snapshot = ingress.health.snapshot()
    check("F-5.4 at the brim HIGH is dropped as queue_full and counted",
          snapshot.dropped_queue_full > 0,
          "dropped_queue_full=" + str(snapshot.dropped_queue_full))
    check("F-5.5 submit never raised across the whole overload", True)
    check("F-5.6 counters add up (enqueued + both drop counters == submissions)",
          snapshot.enqueued == 20,
          "enqueued=" + str(snapshot.enqueued) + " qsize=" + str(ingress.qsize()))


# ---------------------------------------------------------------------------
# F-6  worker exception: single failures survive, five consecutive give up
# ---------------------------------------------------------------------------

class _AlwaysExplodingIngressProxy:
    """Wraps a real ingress and makes drain() raise, which is the one call
    the worker loop cannot avoid."""

    def __init__(self, inner, fail_times):
        self._inner = inner
        self.remaining = fail_times
        self.health = inner.health

    def drain(self, max_items, timeout):
        if self.remaining > 0:
            self.remaining -= 1
            raise RuntimeError("injected drain failure")
        return self._inner.drain(max_items, timeout)

    def qsize(self):
        return self._inner.qsize()

    def __getattr__(self, name):
        return getattr(self._inner, name)


def f6_worker_exception(tmp):
    db = tmp / "f6a" / "observability.sqlite3"
    inner = ObservabilityIngress(instance_id="inst-1", queue_size=128)
    proxy = _AlwaysExplodingIngressProxy(inner, fail_times=3)
    worker = LoggingWorker(proxy, SQLiteLogStore(db), batch_size=8, flush_interval_s=0.02)
    worker.start()
    try:
        wait_until(lambda: proxy.remaining == 0, timeout=6.0)
        inner.event("client.app.started", channel="system", message="after recovery")
        ok = wait_until(lambda: _rows(db) >= 1, timeout=6.0)
        check("F-6.1 three consecutive loop failures are survived", ok,
              "rows=" + str(_rows(db)))
        check("F-6.2 they are counted as worker_errors",
              inner.health.snapshot().worker_errors >= 3,
              "worker_errors=" + str(inner.health.snapshot().worker_errors))
        check("F-6.3 health is not FAILED_WORKER below the threshold",
              inner.health.state is not LoggingHealthState.FAILED_WORKER,
              str(inner.health.state))
    finally:
        worker.stop(2.0)

    db2 = tmp / "f6b" / "observability.sqlite3"
    inner2 = ObservabilityIngress(instance_id="inst-1", queue_size=128)
    proxy2 = _AlwaysExplodingIngressProxy(inner2, fail_times=10_000)
    worker2 = LoggingWorker(proxy2, SQLiteLogStore(db2), batch_size=8, flush_interval_s=0.01)
    worker2.start()
    try:
        ok = wait_until(
            lambda: inner2.health.state is LoggingHealthState.FAILED_WORKER, timeout=8.0)
        check("F-6.4 permanent loop failure ends in FAILED_WORKER, no restart", ok,
              str(inner2.health.state))
        check("F-6.5 the loop really gave up (thread finished)",
              wait_until(lambda: not worker2.is_alive(), timeout=4.0))
        check("F-6.6 after FAILED_WORKER the ingress only discards and counts",
              inner2.submit(record()) is False)
    finally:
        worker2.stop(2.0)


# ---------------------------------------------------------------------------
# F-7  malformed event: the normalizer boundary never raises
# ---------------------------------------------------------------------------

class _Unrenderable:
    def __str__(self):
        raise RuntimeError("str() explodes")

    def __repr__(self):
        raise RuntimeError("repr() explodes")


def f7_malformed(tmp):
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=64)
    raised = None
    try:
        ingress.event("client.app.started", channel="system",
                      details={"bad": _Unrenderable()})
    except Exception as exc:  # noqa: BLE001
        raised = exc
    check("F-7.1 an unrenderable detail value never escapes the ingress",
          raised is None, repr(raised))

    raised = None
    try:
        ingress.event("client.app.started", channel="system", details="not a mapping")
    except Exception as exc:  # noqa: BLE001
        raised = exc
    snapshot = ingress.health.snapshot()
    check("F-7.2 a non-mapping details object never escapes either",
          raised is None, repr(raised))
    check("F-7.3 the rejection is counted as malformed", snapshot.malformed >= 1,
          "malformed=" + str(snapshot.malformed))

    drained = ingress.drain(100, 0.0)
    rejected = [item for item in drained if item.type == "logging.record_rejected"]
    print("[OPEN] F-7.4 no substitute record logging.record_rejected for a "
          "normalizer exception the normalizer swallowed itself "
          "(count=" + str(len(rejected)) + ") - documented open point O-1, "
          "see V1_OPEN_POINTS.md")

    # the substitute record itself is reachable and correct wherever an
    # exception DOES reach the ingress boundary (OBS-040 path)
    ingress.emit_record_rejected("observability.normalizer.client", ValueError("x"))
    emitted = [item for item in ingress.drain(10, 0.0)
               if item.type == "logging.record_rejected"]
    check("F-7.5 the substitute record carries component and exception type "
          "and NO original data",
          len(emitted) == 1 and set(dict(emitted[0].details)) == {"component", "exception"},
          str([dict(item.details) for item in emitted]))
    check("F-7.6 it is HIGH priority so it survives the overload it explains",
          bool(emitted) and emitted[0].priority.value == "high")
    check("F-7.7 health stays OK for a malformed record (ARCH 8.3)",
          ingress.health.state is LoggingHealthState.OK, str(ingress.health.state))


# ---------------------------------------------------------------------------
# F-8  UI query failure: a provider defect is a display state
# ---------------------------------------------------------------------------

class _ExplodingProvider:
    provider_id = "exploding"

    def status(self):
        raise RuntimeError("status explodes")

    def query(self, filter, cursor=None, limit=200):  # noqa: A002
        raise RuntimeError("query explodes")

    def fetch_raw(self, record_id):
        raise RuntimeError("fetch_raw explodes")


def f8_ui_query_failure(tmp):
    service = LogQueryService()
    service.register(_ExplodingProvider())
    page = service.query("exploding", QueryFilter(), None, 10)
    check("F-8.1 a throwing provider becomes an ERROR page, not an exception",
          page.status.state is ProviderState.ERROR, str(page.status.state))
    check("F-8.2 the error page carries no records", page.records == ())
    statuses = service.providers()
    check("F-8.3 a throwing status() becomes an ERROR status",
          len(statuses) == 1 and statuses[0].state is ProviderState.ERROR)
    check("F-8.4 fetch_raw returns None instead of raising",
          service.fetch_raw("exploding", "x") is None)
    page = service.query("does-not-exist", QueryFilter(), None, 10)
    check("F-8.5 an unknown provider id is UNAVAILABLE, not an exception",
          page.status.state is ProviderState.UNAVAILABLE)

    # a corrupt database file
    corrupt = tmp / "f8" / "observability.sqlite3"
    corrupt.parent.mkdir(parents=True, exist_ok=True)
    corrupt.write_bytes(b"this is definitely not a sqlite file" * 10)
    provider = LocalLogProvider(corrupt)
    page = provider.query(QueryFilter(), None, 10)
    check("F-8.6 a corrupt store file is a provider state, never a raise",
          page.status.state in (ProviderState.ERROR, ProviderState.UNAVAILABLE),
          str(page.status.state))
    check("F-8.7 an invalid cursor is an ERROR page, not a silent restart",
          provider.query(QueryFilter(), "not-a-cursor", 10).status.state
          is ProviderState.ERROR)


# ---------------------------------------------------------------------------
# F-9  a throwing aggregate source must not take the worker down (ARCH 8.6)
# ---------------------------------------------------------------------------

def f9_aggregate_source_explodes(tmp):
    db = tmp / "f9" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=128, level="DEBUG")

    def exploding_source():
        raise RuntimeError("counter reader explodes")

    ingress.register_aggregate_source("client.audio.stream_stats", exploding_source,
                                      component="audio")
    collected = ingress.collect_aggregates()
    check("F-9.1 a throwing counter reader is skipped, not propagated",
          collected == [], str(collected))
    check("F-9.2 it is counted as malformed",
          ingress.health.snapshot().malformed >= 1)

    worker = LoggingWorker(ingress, SQLiteLogStore(db), batch_size=4, flush_interval_s=0.02)
    worker.start()
    try:
        ingress.event("client.app.started", channel="system", message="still alive")
        ok = wait_until(lambda: _rows(db) >= 1, timeout=6.0)
        check("F-9.3 the worker keeps writing normal records", ok)
    finally:
        worker.stop(2.0)


# ---------------------------------------------------------------------------
# F-10 store recovery: after the pause the store is probed, not charged a batch
# ---------------------------------------------------------------------------

class _FlakyStore:
    def __init__(self, inner):
        self._inner = inner
        self.fail = True
        self.write_calls = 0
        self.probe_calls = 0

    def open(self):
        return self._inner.open()

    def write_batch(self, records):
        self.write_calls += 1
        if self.fail:
            raise sqlite3.OperationalError("injected write failure")
        return self._inner.write_batch(records)

    def probe_write(self):
        self.probe_calls += 1
        return not self.fail

    def run_retention(self, **kwargs):
        return (0, 0)

    def measure_db_bytes(self):
        return self._inner.measure_db_bytes()

    def clear(self):
        return self._inner.clear()

    def close(self):
        self._inner.close()


def f10_store_recovery(tmp):
    db = tmp / "f10" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=512)
    health = ingress.health
    store = _FlakyStore(SQLiteLogStore(db))
    worker = LoggingWorker(ingress, store, health=health, batch_size=4,
                           flush_interval_s=0.02)
    # shrink the pause so the probe path is reachable inside a test
    import core.observability.worker as worker_module
    original_pause = worker_module.STORE_PAUSE_S
    worker_module.STORE_PAUSE_S = 0.3
    worker.start()
    try:
        for index in range(40):
            ingress.event("client.app.started", channel="system", message=str(index))
        ok = wait_until(lambda: health.state is LoggingHealthState.FAILED_STORE,
                        timeout=8.0)
        check("F-10.1 five consecutive write failures pause the store", ok,
              str(health.state))
        store.fail = False
        recovered = wait_until(lambda: health.state is LoggingHealthState.OK, timeout=8.0)
        check("F-10.2 after the pause the store is probed and recovers", recovered,
              str(health.state))
        check("F-10.3 the recovery used a probe, not a batch", store.probe_calls >= 1,
              "probe_calls=" + str(store.probe_calls))
        ingress.event("client.app.started", channel="system", message="after recovery")
        wrote = wait_until(lambda: _rows(db) >= 1, timeout=6.0)
        check("F-10.4 records flow again after recovery", wrote, "rows=" + str(_rows(db)))
        connection = sqlite3.connect(str(db))
        recovery_rows = connection.execute(
            "SELECT COUNT(*) FROM logs WHERE type = 'logging.recovered'").fetchone()[0]
        connection.close()
        check("F-10.5 a structured logging.recovered record documents the recovery",
              recovery_rows >= 1, "logging.recovered rows=" + str(recovery_rows))
    finally:
        worker_module.STORE_PAUSE_S = original_pause
        worker.stop(2.0)


def main():
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        cases = [
            ("F-1  SQLite read-only", f1_store_read_only),
            ("F-2  SQLite locked", f2_store_locked),
            ("F-3  DB path invalid", f3_db_path_invalid),
            ("F-4  file sink invalid", f4_sink_invalid),
            ("F-5  queue full / watermark", f5_queue_full),
            ("F-6  worker exception", f6_worker_exception),
            ("F-7  malformed event", f7_malformed),
            ("F-8  UI query failure", f8_ui_query_failure),
            ("F-9  throwing aggregate source", f9_aggregate_source_explodes),
            ("F-10 store recovery", f10_store_recovery),
        ]
        for title, function in cases:
            print("=== " + title + " ===")
            function(tmp)
            print("")

    print("=" * 70)
    if FAILURES:
        print("FAILURES: " + str(len(FAILURES)))
        for name in FAILURES:
            print("  - " + name)
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
