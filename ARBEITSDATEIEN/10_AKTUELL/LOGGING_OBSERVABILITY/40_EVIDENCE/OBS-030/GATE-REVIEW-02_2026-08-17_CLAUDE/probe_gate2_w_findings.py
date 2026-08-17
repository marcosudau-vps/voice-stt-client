"""Gate-Review II: independent runtime probes for W-1 .. W-7 and §8.3."""
from __future__ import annotations

import io
import os
import sqlite3
import tempfile
import time
from contextlib import redirect_stderr
from pathlib import Path
from uuid import uuid4

from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker


def rec(**kw):
    base = dict(
        record_id=uuid4().hex,
        received_at="2026-08-17T10:00:00.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="probe",
        scope="instance",
        channel="system",
        level="INFO",
        type="probe.event",
    )
    base.update(kw)
    return CanonicalLogRecord(**base)


class OkStore:
    def open(self):
        from core.observability.storage.sqlite import OpenResult
        return OpenResult(True, False, "")

    def write_batch(self, records):
        return (len(records), 0)

    def run_retention(self, **kw):
        return (0, 0)

    def measure_db_bytes(self):
        return None

    def probe_write(self):
        return True

    def clear(self):
        return 0

    def close(self):
        return None


class BrokenStore(OkStore):
    def __init__(self, detail="database is locked"):
        self.detail = detail
        self.write_calls = 0
        self.probe_calls = 0

    def write_batch(self, records):
        self.write_calls += 1
        raise sqlite3.OperationalError(self.detail)

    def probe_write(self):
        self.probe_calls += 1
        return False


class CountingSink:
    def __init__(self):
        self.records = []

    def write_batch(self, records):
        self.records.extend(records)

    def close(self):
        return None


def hdr(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


# --------------------------------------------------------------------------
def w1_store_sink_isolation():
    hdr("W-1  broken SQLite store vs. intact JSONL sink")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=256)
    store = BrokenStore()
    sink = CountingSink()
    w = LoggingWorker(ing, store, health=health, sink=sink,
                      batch_size=1, flush_interval_s=0.02)
    accepted = []
    with redirect_stderr(io.StringIO()):
        w.start()
        for _ in range(20):
            accepted.append(ing.submit(rec()))
            time.sleep(0.03)
        time.sleep(0.3)
        w.stop(1.0)
    snap = health.snapshot(queue_depth=ing.qsize())
    print(f"submit() accepted                : {sum(accepted)}/20")
    print(f"sink records written             : {len(sink.records)}")
    print(f"store write attempts             : {store.write_calls}")
    print(f"health.state                     : {snap.state.value}")
    print(f"store_errors                     : {snap.store_errors}")
    print(f"written                          : {snap.written}")
    print(f"health.is_failed() (ingress gate): {health.is_failed()}")
    print("  -> after FAILED_STORE the INGRESS itself refuses submits, so the")
    print("     sink starves even though _write_sink is now unconditional.")


def w1_degraded_only():
    hdr("W-1b  store failing but still only DEGRADED_STORE (<5 failures)")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=256)
    store = BrokenStore()
    sink = CountingSink()
    w = LoggingWorker(ing, store, health=health, sink=sink,
                      batch_size=100, flush_interval_s=0.05)
    with redirect_stderr(io.StringIO()):
        w.start()
        for _ in range(20):
            ing.submit(rec())
        time.sleep(0.3)
        state_mid = health.state.value
        sink_mid = len(sink.records)
        w.stop(1.0)
    print(f"state after first failing batch  : {state_mid}")
    print(f"sink records after first batch   : {sink_mid}")


# --------------------------------------------------------------------------
def w2_retention_pressure():
    hdr("W-2  logging.retention_pressure record")
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe-instance", health=health, queue_size=256)
    w = LoggingWorker(ing, store, health=health, max_db_bytes=1,
                      batch_size=10, flush_interval_s=0.05, retention_days=14)
    with redirect_stderr(io.StringIO()):
        w.start()
        for _ in range(5):
            ing.submit(rec())
        time.sleep(0.6)
        w.stop(1.0)
    conn = sqlite3.connect(str(tmp))
    rows = conn.execute(
        "SELECT type, channel, level, component, producer_kind, producer_id, "
        "instance_id, scope, replayed, message, details_json "
        "FROM logs WHERE type = 'logging.retention_pressure'"
    ).fetchall()
    total = conn.execute(
        "SELECT COUNT(*) FROM logs WHERE type='logging.retention_pressure'"
    ).fetchone()[0]
    conn.close()
    print(f"retention_pressure records       : {total}")
    for r in rows:
        print("  type            :", r[0])
        print("  channel         :", r[1])
        print("  level           :", r[2])
        print("  component       :", r[3])
        print("  producer_kind   :", r[4])
        print("  producer_id     :", r[5])
        print("  instance_id     :", r[6])
        print("  scope           :", r[7])
        print("  replayed        :", r[8])
        print("  message         :", r[9])
        print("  details_json    :", r[10])


def w2_edge_triggered():
    hdr("W-2b  edge trigger: many retention runs, still one record")
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=4096)
    w = LoggingWorker(ing, store, health=health, max_db_bytes=1,
                      batch_size=50, flush_interval_s=0.02)
    with redirect_stderr(io.StringIO()):
        w.start()
        time.sleep(0.2)
        # force several retention runs by pushing >2000 written records
        for _ in range(2600):
            ing.submit(rec())
        time.sleep(1.5)
        w.stop(2.0)
    conn = sqlite3.connect(str(tmp))
    n = conn.execute(
        "SELECT COUNT(*) FROM logs WHERE type='logging.retention_pressure'"
    ).fetchone()[0]
    conn.close()
    print(f"retention_pressure records       : {n}  (edge-triggered -> expect 1)")


# --------------------------------------------------------------------------
def w3_unattributed_drops():
    hdr("W-3  records dropped because the store is paused/degraded")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=256)
    store = BrokenStore()
    w = LoggingWorker(ing, store, health=health, batch_size=5, flush_interval_s=0.02)
    with redirect_stderr(io.StringIO()):
        w.start()
        for _ in range(5):
            ing.submit(rec())
        time.sleep(0.4)
        w.stop(1.0)
    s = health.snapshot(queue_depth=ing.qsize())
    print(f"enqueued  = {s.enqueued}")
    print(f"written   = {s.written}")
    print(f"dedup     = {s.deduplicated}")
    print(f"dropped_watermark={s.dropped_watermark} queue_full={s.dropped_queue_full} "
          f"shutdown={s.dropped_shutdown} malformed={s.malformed}")
    print(f"store_errors={s.store_errors}  state={s.state.value}")
    print("  -> enqueued != written + dropped_* : the gap is the documented W-3 hole")


# --------------------------------------------------------------------------
def w4_probe_store():
    hdr("W-4  empty test write after the 60s suspension")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=256)
    store = BrokenStore()
    w = LoggingWorker(ing, store, health=health, batch_size=5, flush_interval_s=0.02)
    # drive it into the paused state without waiting 60s
    with redirect_stderr(io.StringIO()):
        for _ in range(6):
            w._write_with_policy([rec()])
        paused_at = w._store_paused_until
        # pretend the pause elapsed
        w._store_paused_until = time.monotonic() - 0.01
        before_writes = store.write_calls
        result = w._write_with_policy([rec()])
    print(f"paused after >=5 failures        : {paused_at is not None}")
    print(f"probe_write() calls              : {store.probe_calls}")
    print(f"write_batch calls during resume  : {store.write_calls - before_writes} (0 expected)")
    print(f"result of the resumed call       : {result}")
    print(f"new pause set                    : {w._store_paused_until is not None}")

    # real SQLite store: probe on a healthy store returns True and writes nothing
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    real = SQLiteLogStore(tmp)
    real.open()
    ok = real.probe_write()
    n = real.row_count()
    real.close()
    print(f"SQLiteLogStore.probe_write()     : {ok}, rows after probe = {n}")


# --------------------------------------------------------------------------
def w5_disabled():
    hdr("W-5  LoggingHealthState.DISABLED")
    from core.config import LoggingObservabilityConfig
    from core.observability.manager import ObservabilityManager
    cfg = LoggingObservabilityConfig(enabled=False)
    mgr = ObservabilityManager(cfg)
    print(f"state with enabled=False         : {mgr.health.state.value}")
    print(f"ingress is NullIngress           : {type(mgr.ingress).__name__}")
    print(f"stop() without worker            : {mgr.stop(0.1)}")
    print(f"clear_history() without worker   : {mgr.clear_history(0.1)}")

    cfg2 = LoggingObservabilityConfig(enabled=True, store_enabled=False)
    mgr2 = ObservabilityManager(cfg2)
    print(f"state with store_enabled=False   : {mgr2.health.state.value}")


# --------------------------------------------------------------------------
def w7_pragma_order():
    hdr("W-7a  PRAGMA order / W-7b records_since_retention / W-7c stop()")
    import re
    src = Path("core/observability/storage/sqlite.py").read_text(encoding="utf-8")
    order = re.findall(r'PRAGMA (journal_mode|synchronous|busy_timeout|foreign_keys)', src)
    print(f"PRAGMA order in open()           : {order[:4]}")
    print(f"expected (CONTRACTS 5.2)         : ['journal_mode', 'synchronous', "
          f"'busy_timeout', 'foreign_keys']")

    # W-7b: retention counter counts WRITTEN records
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=256)
    store = BrokenStore()
    w = LoggingWorker(ing, store, health=health)
    with redirect_stderr(io.StringIO()):
        w._process_batch([rec() for _ in range(10)])
    print(f"records_since_retention after a failed batch : {w._records_since_retention} (0 expected)")

    class GoodStore(OkStore):
        pass
    w2 = LoggingWorker(ing, GoodStore(), health=LoggingInternalHealth())
    w2._process_batch([rec() for _ in range(10)])
    print(f"records_since_retention after a good batch   : {w2._records_since_retention} (10 expected)")


# --------------------------------------------------------------------------
def arch83_counting():
    hdr("ARCH 8.3  'nur verwerfen und zaehlen' after FAILED_WORKER")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)
    health.set_state(LoggingHealthState.FAILED_WORKER, "probe")
    before = health.snapshot()
    results = [ing.submit(rec()) for _ in range(10)]
    after = health.snapshot()
    print(f"submit() results                 : {set(results)}")
    fields = ("enqueued", "written", "deduplicated", "dropped_watermark",
              "dropped_queue_full", "dropped_shutdown", "malformed",
              "store_errors", "sink_errors", "retention_errors", "worker_errors")
    for f in fields:
        b, a = getattr(before, f), getattr(after, f)
        mark = "  <-- changed" if b != a else ""
        print(f"  {f:20s} {b} -> {a}{mark}")
    print("  -> 10 records rejected, NO counter moved: 'verwerfen' yes, 'zaehlen' no.")


if __name__ == "__main__":
    w1_store_sink_isolation()
    w1_degraded_only()
    w2_retention_pressure()
    w2_edge_triggered()
    w3_unattributed_drops()
    w4_probe_store()
    w5_disabled()
    w7_pragma_order()
    arch83_counting()
