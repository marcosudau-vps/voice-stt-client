"""
Independent runtime probe for the OBS-030 gate findings (RUN-OBS-030-02).

Mirrors the probes the gate review ran (GATE-REVIEW-01, sections B-1 and B-3)
so the before/after can be compared line by line. Run from the client
workspace root:

    python ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/40_EVIDENCE/OBS-030/RUN-02_2026-08-17/probe_obs030_gate_fixes.py

This file is evidence, not product code: nothing imports it.
"""

from __future__ import annotations

import os
import sys
import tempfile
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(WORKSPACE))

from core.config import DEFAULT_LOCAL_APP_DIR, LoggingObservabilityConfig  # noqa: E402
from core.observability.ingress import ObservabilityIngress  # noqa: E402
from core.observability.models import CanonicalLogRecord  # noqa: E402
from core.observability.storage.sqlite import OpenResult  # noqa: E402
from core.observability.worker import LoggingWorker  # noqa: E402


def iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"


def record(**over) -> CanonicalLogRecord:
    fields = dict(
        record_id=uuid.uuid4().hex, received_at=iso(), producer_kind="client",
        producer_id="voice-stt-client", instance_id="i" * 32, scope="instance",
        channel="system", level="INFO", replayed=False, type=None,
    )
    fields.update(over)
    return CanonicalLogRecord(**fields)


class Store:
    def __init__(self, *, fail=None, db_bytes=None):
        self.rows, self.fail, self.db_bytes = [], fail, db_bytes

    def open(self):
        return OpenResult(True, False, "")

    def write_batch(self, records):
        if self.fail:
            raise self.fail
        self.rows.extend(records)
        return (len(records), 0)

    def probe_write(self):
        return self.fail is None

    def clear(self):
        return 0

    def run_retention(self, **_k):
        return (0, 0)

    def measure_db_bytes(self):
        return self.db_bytes

    def close(self):
        pass


class Sink:
    def __init__(self):
        self.rows = []

    def write_batch(self, records):
        self.rows.extend(records)

    def close(self):
        pass


class BoomIngress(ObservabilityIngress):
    """The gate review's probe: ``drain`` raises."""

    def __init__(self, *, failures, **kw):
        super().__init__(**kw)
        self.failures = failures

    def drain(self, max_items, timeout):
        if self.failures != 0:
            if self.failures > 0:
                self.failures -= 1
            time.sleep(0.01)
            raise RuntimeError("boom")
        return super().drain(max_items, timeout)


def live_worker_threads():
    return [t.name for t in threading.enumerate() if t.name == "RealtimeSTT-Observability"]


def probe_b1_single():
    print("== B-1a  single unexpected worker exception ==")
    ing = BoomIngress(failures=1, instance_id="i" * 32, queue_size=100)
    store = Store()
    worker = LoggingWorker(ing, store, health=ing.health, batch_size=10, flush_interval_s=0.02)
    worker.start()
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline and ing.health.snapshot().worker_errors < 1:
        time.sleep(0.02)
    accepted = ing.submit(record(message="after boom"))
    deadline = time.monotonic() + 3
    while time.monotonic() < deadline and not store.rows:
        time.sleep(0.02)
    snap = ing.health.snapshot()
    print(f"  worker alive after boom : {worker.is_alive()}")
    print(f"  worker_errors           : {snap.worker_errors}")
    print(f"  health.state            : {ing.health.state.value}")
    print(f"  submit() after boom     : {accepted}")
    print(f"  rows written after boom : {len(store.rows)}")
    worker.stop(2.0)


def probe_b1_permanent():
    print("== B-1b  permanently failing worker loop ==")
    ing = BoomIngress(failures=-1, instance_id="i" * 32, queue_size=100)
    store = Store()
    worker = LoggingWorker(ing, store, health=ing.health, batch_size=10, flush_interval_s=0.02)
    print(f"  queued before boom      : {ing.submit(record(message='queued'))}")
    worker.start()
    deadline = time.monotonic() + 6
    while time.monotonic() < deadline and worker.is_alive():
        time.sleep(0.02)
    snap = ing.health.snapshot()
    print(f"  worker alive            : {worker.is_alive()}")
    print(f"  health.state            : {ing.health.state.value}")
    print(f"  health.is_failed()      : {ing.health.is_failed()}")
    print(f"  worker_errors           : {snap.worker_errors}")
    print(f"  live observability thrds: {live_worker_threads()}")
    depth_before = ing.qsize()
    results = [ing.submit(record()) for _ in range(5)]
    print(f"  submit() after death    : {results}")
    print(f"  queue depth unchanged   : {ing.qsize() == depth_before}")
    snap = ing.health.snapshot()
    print(f"  dropped_shutdown        : {snap.dropped_shutdown}")


def probe_w1_sink():
    print("== W-1  broken store must not silence the sink ==")
    ing = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
    store, sink = Store(fail=RuntimeError("store broken")), Sink()
    worker = LoggingWorker(ing, store, health=ing.health, sink=sink,
                           batch_size=20, flush_interval_s=0.02)
    worker._process_batch([record() for _ in range(20)])
    print(f"  store rows              : {len(store.rows)}")
    print(f"  sink lines written      : {len(sink.rows)}")
    print(f"  health.state            : {ing.health.state.value}")


def probe_w2_pressure():
    print("== W-2  logging.retention_pressure as a canonical record ==")
    ing = ObservabilityIngress(instance_id="i" * 32, queue_size=100)
    store = Store(db_bytes=1024)
    worker = LoggingWorker(ing, store, health=ing.health, max_db_bytes=512)
    worker._run_retention_if_due(force=True)
    worker._run_retention_if_due(force=True)
    pressure = [r for r in store.rows if r.type == "logging.retention_pressure"]
    print(f"  pressure records        : {len(pressure)} (edge-triggered)")
    for r in pressure:
        print(f"    type={r.type} channel={r.channel} level={r.level} "
              f"is_internal={r.is_internal} details={dict(r.details)}")


def probe_b3_paths():
    print("== B-3  P-8 path boundaries ==")
    system_drive = os.environ.get("SystemDrive", "C:")
    cases = [
        ("db_path", f"{system_drive}\\ProgramData\\somewhere-else\\observability.sqlite3"),
        ("db_path", str(DEFAULT_LOCAL_APP_DIR / ".." / ".." / ".." / ".." / "escaped.sqlite3")),
        ("db_path", "observability.sqlite3"),
        ("file_sink_dir", f"{system_drive}\\ProgramData\\sink"),
        ("db_path", str(DEFAULT_LOCAL_APP_DIR / "observability.sqlite3")),
        ("file_sink_dir", str(DEFAULT_LOCAL_APP_DIR / "logs" / "observability")),
    ]
    for field, value in cases:
        try:
            LoggingObservabilityConfig(**{field: value}).validate()
            verdict = "ACCEPTED"
        except ValueError:
            verdict = "REJECTED"
        print(f"  {verdict:8s} {field} = {value}")
    print(f"  DEFAULT_LOCAL_APP_DIR   = {DEFAULT_LOCAL_APP_DIR}")


def probe_w4_probe_write():
    print("== W-4  empty test write after the store pause ==")
    from core.observability.storage.sqlite import SQLiteLogStore
    with tempfile.TemporaryDirectory() as tmp:
        store = SQLiteLogStore(Path(tmp) / "obs.sqlite3")
        print(f"  probe_write() unopened  : {store.probe_write()}")
        store.open()
        print(f"  probe_write() open      : {store.probe_write()}")
        store.close()
        print(f"  probe_write() closed    : {store.probe_write()}")


if __name__ == "__main__":
    probe_b1_single()
    probe_b1_permanent()
    probe_w1_sink()
    probe_w2_pressure()
    probe_w4_probe_write()
    probe_b3_paths()
