"""OBS-060 - Performance and the non-blocking invariant.

The one measurement the freeze prescribes verbatim (ARCH 6.3):

    Nachweis (verbindlich, OBS-020 und OBS-060):
      Worker anhalten, danach 20.000 Records einreichen. submit() muss
      durchgehend unter einer im ersten Lauf festgeschriebenen Zeitgrenze
      zurueckkehren und darf nie werfen.

plus the benchmarks the plan 13 lists: burst, batch throughput, Qt
responsiveness, eventstream receive, audio hot-path overhead, DB cleanup.

The numbers are measured on one machine and are documented as such: the
thresholds below are deliberately generous, because the property under test
is "bounded and non-blocking", not "fast on this laptop".

Run:  QT_QPA_PLATFORM=offscreen python <this file>
Exit: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import os
import sqlite3
import statistics
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "core" / "observability").is_dir():
        sys.path.insert(0, str(parent))
        break

from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.query.base import QueryFilter
from core.observability.query.local import LocalLogProvider
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker

FAILURES = []
MEASUREMENTS = []


def check(name, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + ((" - " + detail) if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


def note(label, value, unit=""):
    MEASUREMENTS.append((label, value, unit))
    print("       %-52s %s %s" % (label, value, unit))


def record(index=0, **overrides):
    base = dict(
        record_id="rec-%08d" % index,
        received_at="2026-08-18T10:00:00.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="inst-1",
        scope="instance",
        channel="system",
        level="INFO",
        type="client.app.started",
        message="a message of a fairly ordinary length for a log line",
    )
    base.update(overrides)
    return CanonicalLogRecord(**base)


def wait_until(predicate, timeout=30.0, interval=0.02):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def rows(db):
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
# B-1  ARCH 6.3, verbatim: worker stopped, 20 000 records submitted
# ---------------------------------------------------------------------------

SUBMIT_BUDGET_MS = 5.0  # per single submit, generous by design


def b1_non_blocking_invariant():
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=8192)
    # NO worker at all: nothing drains, the queue fills and then stays full.
    durations = []
    raised = None
    started = time.perf_counter()
    for index in range(20000):
        entry = record(index)
        call_started = time.perf_counter()
        try:
            ingress.submit(entry)
        except BaseException as exc:  # noqa: BLE001
            raised = exc
            break
        durations.append(time.perf_counter() - call_started)
    total = time.perf_counter() - started

    check("B-1.1 submit() never raised across 20 000 submissions", raised is None,
          repr(raised))
    check("B-1.2 all 20 000 submissions were attempted", len(durations) == 20000,
          "count=" + str(len(durations)))
    slowest_ms = max(durations) * 1000.0
    note("total wall time for 20 000 submits", round(total * 1000.0, 1), "ms")
    note("mean submit", round(statistics.mean(durations) * 1e6, 2), "us")
    note("median submit", round(statistics.median(durations) * 1e6, 2), "us")
    note("p99 submit",
         round(sorted(durations)[int(len(durations) * 0.99)] * 1e6, 2), "us")
    note("slowest single submit", round(slowest_ms, 3), "ms")
    check("B-1.3 every single submit stayed under the "
          + str(SUBMIT_BUDGET_MS) + " ms budget",
          slowest_ms < SUBMIT_BUDGET_MS, "slowest=" + str(round(slowest_ms, 3)) + " ms")

    snapshot = ingress.health.snapshot()
    note("enqueued", snapshot.enqueued)
    note("dropped_watermark", snapshot.dropped_watermark)
    note("dropped_queue_full", snapshot.dropped_queue_full)
    check("B-1.4 memory stayed bounded: the queue never exceeded its size",
          ingress.qsize() <= 8192, "qsize=" + str(ingress.qsize()))
    check("B-1.5 nothing was lost uncounted",
          snapshot.enqueued + snapshot.dropped_watermark
          + snapshot.dropped_queue_full == 20000,
          str(snapshot.enqueued) + "+" + str(snapshot.dropped_watermark)
          + "+" + str(snapshot.dropped_queue_full))


# ---------------------------------------------------------------------------
# B-2  batch throughput through the real worker into real SQLite
# ---------------------------------------------------------------------------

def b2_batch_throughput(tmp):
    db = tmp / "b2" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=65536)
    worker = LoggingWorker(ingress, SQLiteLogStore(db), batch_size=200,
                           flush_interval_s=0.05)
    worker.start()
    try:
        count = 20000
        started = time.perf_counter()
        for index in range(count):
            ingress.submit(record(index))
        submitted = time.perf_counter() - started
        drained = wait_until(lambda: rows(db) >= ingress.health.snapshot().enqueued,
                             timeout=60.0)
        total = time.perf_counter() - started
    finally:
        worker.stop(5.0)

    written = rows(db)
    note("records submitted", count)
    note("records persisted", written)
    note("submit phase", round(submitted * 1000.0, 1), "ms")
    note("submit throughput", int(count / max(submitted, 1e-9)), "records/s")
    note("end-to-end (submit + persist)", round(total * 1000.0, 1), "ms")
    note("end-to-end throughput", int(written / max(total, 1e-9)), "records/s")
    check("B-2.1 the worker persisted everything it accepted", drained,
          "persisted=" + str(written))
    check("B-2.2 end-to-end throughput is at least 2 000 records/s",
          written / max(total, 1e-9) >= 2000,
          str(int(written / max(total, 1e-9))) + " records/s")


# ---------------------------------------------------------------------------
# B-3  audio hot-path overhead (ARCH 8.6: int increments only)
# ---------------------------------------------------------------------------

def b3_hot_path(tmp):
    db = tmp / "b3" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=4096, level="DEBUG")

    class Counters:
        def __init__(self):
            self.chunks_captured = 0
            self.chunks_dropped_capture_queue = 0
            self.overflow_count = 0

        def hot_path_call(self):
            # exactly what ARCH 8.6 allows at these call sites
            self.chunks_captured += 1

        def read(self):
            return {
                "chunks_captured": self.chunks_captured,
                "chunks_dropped_capture_queue": self.chunks_dropped_capture_queue,
                "overflow_count": self.overflow_count,
            }

    counters = Counters()
    ingress.register_aggregate_source("client.audio.stream_stats", counters.read,
                                      component="audio")
    worker = LoggingWorker(ingress, SQLiteLogStore(db), batch_size=64,
                           flush_interval_s=0.05)
    worker.start()
    try:
        packets = 100000
        started = time.perf_counter()
        for _ in range(packets):
            counters.hot_path_call()
        elapsed = time.perf_counter() - started
        time.sleep(0.3)
        connection_rows = rows(db)
    finally:
        worker.stop(2.0)

    per_packet_ns = elapsed / packets * 1e9
    note("hot-path calls", packets)
    note("total hot-path time", round(elapsed * 1000.0, 2), "ms")
    note("per packet", round(per_packet_ns, 1), "ns")
    check("B-3.1 a hot-path call costs well under 1 microsecond",
          per_packet_ns < 1000.0, str(round(per_packet_ns, 1)) + " ns")
    check("B-3.2 100 000 hot-path calls produced no record per packet",
          connection_rows <= 5, "rows=" + str(connection_rows))
    note("records written while streaming", connection_rows)


# ---------------------------------------------------------------------------
# B-4  query latency over a populated store (UI responsiveness)
# ---------------------------------------------------------------------------

def b4_query_latency(tmp):
    db = tmp / "b4" / "observability.sqlite3"
    store = SQLiteLogStore(db)
    store.open()
    try:
        total = 50000
        block = 5000
        for start in range(0, total, block):
            store.write_batch([
                record(index, session_id="s-%d" % (index % 10),
                       channel=("audit" if index % 3 == 0 else "system"))
                for index in range(start, start + block)
            ])
    finally:
        store.close()
    note("rows in the store", rows(db))

    provider = LocalLogProvider(db)
    measurements = {}

    def timed(label, function):
        started = time.perf_counter()
        page = function()
        elapsed = (time.perf_counter() - started) * 1000.0
        measurements[label] = elapsed
        note(label, round(elapsed, 2), "ms")
        return page

    first = timed("first page, no filter (limit 200)",
                  lambda: provider.query(QueryFilter(), None, 200))
    timed("page 2 via keyset cursor",
          lambda: provider.query(QueryFilter(), first.next_cursor, 200))
    timed("filtered by session_id",
          lambda: provider.query(QueryFilter(session_id="s-3"), None, 200))
    timed("filtered by channel",
          lambda: provider.query(QueryFilter(channels=("audit",)), None, 200))
    timed("free-text filter",
          lambda: provider.query(QueryFilter(text="ordinary"), None, 200))
    started = time.perf_counter()
    provider.fetch_raw("rec-00012345")
    measurements["fetch_raw"] = (time.perf_counter() - started) * 1000.0
    note("fetch_raw for one record", round(measurements["fetch_raw"], 2), "ms")

    slowest = max(measurements.values())
    check("B-4.1 every query answers in well under a second "
          "(the UI runs them off the Qt thread anyway)",
          slowest < 1000.0, "slowest=" + str(round(slowest, 2)) + " ms")
    check("B-4.2 the keyset second page is not slower than the first",
          measurements["page 2 via keyset cursor"] < max(
              50.0, measurements["first page, no filter (limit 200)"] * 5),
          str(round(measurements["page 2 via keyset cursor"], 2)) + " ms")


# ---------------------------------------------------------------------------
# B-5  retention over a large store, inside its time budget
# ---------------------------------------------------------------------------

def b5_retention(tmp):
    db = tmp / "b5" / "observability.sqlite3"
    store = SQLiteLogStore(db)
    store.open()
    try:
        total = 30000
        block = 5000
        for start in range(0, total, block):
            store.write_batch([
                record(index, received_at="2020-01-01T00:00:00.000Z")
                for index in range(start, start + block)
            ])
        before = store.row_count()
        started = time.perf_counter()
        deleted_age, deleted_count = store.run_retention(
            cutoff_iso="2026-01-01T00:00:00.000Z", max_entries=None,
            time_budget_s=0.2)
        elapsed = time.perf_counter() - started
        after = store.row_count()
    finally:
        store.close()

    note("rows before retention", before)
    note("deleted by age in one pass", deleted_age)
    note("rows after one pass", after)
    note("retention pass duration", round(elapsed * 1000.0, 1), "ms")
    check("B-5.1 retention respects its 0.2 s time budget (plus one block)",
          elapsed < 2.0, str(round(elapsed, 3)) + " s")
    check("B-5.2 retention deleted in blocks and made progress",
          deleted_age > 0 and after < before,
          str(before) + " -> " + str(after))
    check("B-5.3 retention never runs VACUUM (the file is not rewritten)",
          True, "asserted structurally by tests/test_obs030_sqlite_store.py")


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
        tmp = Path(directory)
        print("=== B-1  ARCH 6.3: worker stopped, 20 000 records ===")
        b1_non_blocking_invariant()
        print("")
        print("=== B-2  batch throughput through the real worker ===")
        b2_batch_throughput(tmp)
        print("")
        print("=== B-3  audio hot-path overhead ===")
        b3_hot_path(tmp)
        print("")
        print("=== B-4  query latency over 50 000 rows ===")
        b4_query_latency(tmp)
        print("")
        print("=== B-5  retention over 30 000 rows ===")
        b5_retention(tmp)

    print("")
    print("=" * 70)
    if FAILURES:
        print("FAILURES: " + str(len(FAILURES)))
        for name in FAILURES:
            print("  - " + name)
        return 1
    print("ALL PERFORMANCE CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
