"""Gate-Review II, independent fault injection for B-1 (worker error isolation).

Run from the repository root:
    python <this file>
"""
from __future__ import annotations

import io
import sys
import threading
import time
from contextlib import redirect_stderr
from uuid import uuid4

from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.worker import LoggingWorker, WORKER_FAILURE_THRESHOLD


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


class FakeStore:
    def __init__(self):
        self.rows = []
        self.opened = False
        self.closed = False

    def open(self):
        from core.observability.storage.sqlite import OpenResult
        self.opened = True
        return OpenResult(True, False, "")

    def write_batch(self, records):
        self.rows.extend(records)
        return (len(records), 0)

    def run_retention(self, **kw):
        return (0, 0)

    def measure_db_bytes(self):
        return None

    def probe_write(self):
        return True

    def clear(self):
        self.rows.clear()
        return 0

    def close(self):
        self.closed = True


class FakeSink:
    def __init__(self):
        self.lines = []
        self.closed = False

    def write_batch(self, records):
        self.lines.extend(records)

    def close(self):
        self.closed = True


def hdr(title):
    print("\n" + "=" * 72)
    print(title)
    print("=" * 72)


# --------------------------------------------------------------------------
# P1  single unexpected exception inside the loop
# --------------------------------------------------------------------------
def p1_single_exception():
    hdr("P1 - one unexpected exception in the worker loop (drain raises once)")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)
    store = FakeStore()
    real_drain = ing.drain
    state = {"boom": True}

    def flaky_drain(max_items, timeout):
        if state["boom"]:
            state["boom"] = False
            raise RuntimeError("injected loop failure")
        return real_drain(max_items, timeout)

    ing.drain = flaky_drain  # type: ignore[method-assign]
    w = LoggingWorker(ing, store, health=health, flush_interval_s=0.05)
    buf = io.StringIO()
    with redirect_stderr(buf):
        w.start()
        time.sleep(0.4)
        for _ in range(3):
            ing.submit(rec())
        time.sleep(0.5)
        alive = w.is_alive()
        w.stop(1.0)
    snap = health.snapshot(queue_depth=ing.qsize())
    print(f"worker alive after the exception : {alive}")
    print(f"worker_errors                    : {snap.worker_errors}")
    print(f"health.state                     : {snap.state.value}")
    print(f"rows written after the exception : {len(store.rows)}")
    print(f"submit() still True              : {ing.submit(rec()) is False}  (False expected only after stop)")
    print(f"stderr captured                  : {buf.getvalue()!r}")
    print(f"contains 'Traceback'             : {'Traceback' in buf.getvalue()}")


# --------------------------------------------------------------------------
# P2  threshold behaviour: 4 consecutive failures then success
# --------------------------------------------------------------------------
def p2_below_threshold():
    hdr(f"P2 - {WORKER_FAILURE_THRESHOLD - 1} consecutive failures, then success")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)
    store = FakeStore()
    real_drain = ing.drain
    left = {"n": WORKER_FAILURE_THRESHOLD - 1}

    def flaky_drain(max_items, timeout):
        if left["n"] > 0:
            left["n"] -= 1
            raise RuntimeError("injected loop failure")
        return real_drain(max_items, timeout)

    ing.drain = flaky_drain  # type: ignore[method-assign]
    w = LoggingWorker(ing, store, health=health, flush_interval_s=0.05)
    with redirect_stderr(io.StringIO()):
        w.start()
        time.sleep(0.5)
        ing.submit(rec())
        time.sleep(0.4)
        alive = w.is_alive()
        accepted = ing.submit(rec())
        time.sleep(0.3)
        w.stop(1.0)
    snap = health.snapshot()
    print(f"worker alive                     : {alive}")
    print(f"worker_errors                    : {snap.worker_errors}")
    print(f"health.state                     : {snap.state.value}")
    print(f"submit() accepted while running  : {accepted}")
    print(f"rows written                     : {len(store.rows)}")


# --------------------------------------------------------------------------
# P3  permanent failure -> FAILED_WORKER, ingress stops accepting
# --------------------------------------------------------------------------
def p3_permanent_failure():
    hdr("P3 - permanently failing loop -> FAILED_WORKER")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)
    store = FakeStore()
    sink = FakeSink()

    def dead_drain(max_items, timeout):
        raise RuntimeError("injected permanent loop failure")

    for _ in range(5):
        ing.submit(rec())
    ing.drain = dead_drain  # type: ignore[method-assign]

    before_threads = {t.name for t in threading.enumerate()}
    buf = io.StringIO()
    with redirect_stderr(buf):
        w = LoggingWorker(ing, store, health=health, sink=sink, flush_interval_s=0.02)
        w.start()
        deadline = time.time() + 5.0
        while w.is_alive() and time.time() < deadline:
            time.sleep(0.05)
        time.sleep(0.3)
    snap = health.snapshot(queue_depth=ing.qsize())
    submits = [ing.submit(rec()) for _ in range(5)]
    obs_threads = [t.name for t in threading.enumerate()
                   if "Observability" in t.name]
    err = buf.getvalue()
    print(f"worker alive                     : {w.is_alive()}")
    print(f"health.state                     : {snap.state.value}")
    print(f"health.is_failed()               : {health.is_failed()}")
    print(f"worker_errors                    : {snap.worker_errors}")
    print(f"dropped_shutdown (leftovers)     : {snap.dropped_shutdown}")
    print(f"queue depth after death          : {ing.qsize()}")
    print(f"submit() after death             : {submits}")
    print(f"observability threads left       : {obs_threads}")
    print(f"store.close() called             : {store.closed}")
    print(f"sink.close() called              : {sink.closed}")
    print(f"stderr contains 'Traceback'      : {'Traceback' in err}")
    print(f"stderr lines                     :")
    for line in err.splitlines():
        print(f"    {line}")
    print(f"threads before                   : {sorted(before_threads)[:0]}")


# --------------------------------------------------------------------------
# P4  _prepare_record: raw that cannot be redacted/serialised
# --------------------------------------------------------------------------
def p4_prepare_record():
    hdr("P4 - _prepare_record failure path (malformed++, loop survives)")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)
    store = FakeStore()
    w = LoggingWorker(ing, store, health=health, flush_interval_s=0.05)

    class Exploding(dict):
        def items(self):
            raise RuntimeError("injected raw failure")

    bad = rec(raw={"ok": 1})
    object.__setattr__(bad, "raw", Exploding(ok=1))
    out = w._prepare_record(bad)
    print(f"returned record raw              : {dict(out.raw) if out.raw else out.raw}")
    print(f"malformed counter                : {health.snapshot().malformed}")

    # dataclasses.replace on a non-dataclass -> the former escape hatch
    class NotADataclass:
        raw = {"a": 1}
    try:
        w._prepare_record(NotADataclass())  # type: ignore[arg-type]
        print("non-dataclass input              : no exception escaped")
    except Exception as exc:  # noqa: BLE001
        print(f"non-dataclass input              : ESCAPED {type(exc).__name__}: {exc}")


# --------------------------------------------------------------------------
# P5  exception in the retention / backpressure part of the iteration
# --------------------------------------------------------------------------
def p5_other_iteration_paths():
    hdr("P5 - exceptions in other _iteration steps")
    for label, attr in (("qsize raises", "qsize"),):
        health = LoggingInternalHealth()
        ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)
        store = FakeStore()
        setattr(ing, attr, lambda: (_ for _ in ()).throw(RuntimeError("injected qsize failure")))
        w = LoggingWorker(ing, store, health=health, flush_interval_s=0.05)
        with redirect_stderr(io.StringIO()):
            w.start()
            time.sleep(0.4)
            alive = w.is_alive()
            w.stop(1.0)
        snap = health.snapshot()
        print(f"{label:32s} : alive={alive} state={snap.state.value} "
              f"worker_errors={snap.worker_errors}")

    # store.run_retention raises permanently
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)

    class RetentionBomb(FakeStore):
        def run_retention(self, **kw):
            raise RuntimeError("injected retention failure")

    store = RetentionBomb()
    w = LoggingWorker(ing, store, health=health, flush_interval_s=0.05)
    with redirect_stderr(io.StringIO()):
        w.start()
        time.sleep(0.3)
        ing.submit(rec())
        time.sleep(0.3)
        alive = w.is_alive()
        w.stop(1.0)
    snap = health.snapshot()
    print(f"{'run_retention raises':32s} : alive={alive} state={snap.state.value} "
          f"retention_errors={snap.retention_errors} worker_errors={snap.worker_errors} "
          f"rows={len(store.rows)}")

    # store.open raises (not returns)
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)

    class OpenBomb(FakeStore):
        def open(self):
            raise RuntimeError("injected open failure")

    store = OpenBomb()
    w = LoggingWorker(ing, store, health=health, flush_interval_s=0.05)
    with redirect_stderr(io.StringIO()):
        w.start()
        time.sleep(0.3)
        ing.submit(rec())
        time.sleep(0.3)
        alive = w.is_alive()
        w.stop(1.0)
    snap = health.snapshot()
    print(f"{'store.open() raises':32s} : alive={alive} state={snap.state.value} "
          f"worker_errors={snap.worker_errors} rows={len(store.rows)}")


# --------------------------------------------------------------------------
# P6  stop() on a never-started worker with queued records
# --------------------------------------------------------------------------
def p6_never_started():
    hdr("P6 - stop() on a never started worker (queue leftovers)")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=64)
    store = FakeStore()
    w = LoggingWorker(ing, store, health=health)
    for _ in range(7):
        ing.submit(rec())
    with redirect_stderr(io.StringIO()):
        ok = w.stop(0.2)
    snap = health.snapshot(queue_depth=ing.qsize())
    print(f"stop() returned                  : {ok}")
    print(f"enqueued                         : {snap.enqueued}")
    print(f"dropped_shutdown                 : {snap.dropped_shutdown}")
    print(f"queue depth                      : {ing.qsize()}")


if __name__ == "__main__":
    p1_single_exception()
    p2_below_threshold()
    p3_permanent_failure()
    p4_prepare_record()
    p5_other_iteration_paths()
    p6_never_started()
    print("\nWORKER_FAILURE_THRESHOLD =", WORKER_FAILURE_THRESHOLD)
