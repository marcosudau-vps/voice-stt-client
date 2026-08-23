"""Gate-Review II: sink failure isolation + JSONL sink contract (CONTRACTS 11.1)."""
from __future__ import annotations

import io
import json
import sqlite3
import tempfile
import time
from contextlib import redirect_stderr
from pathlib import Path
from uuid import uuid4

from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.sinks.jsonl_file import JsonlSink
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker


def rec():
    return CanonicalLogRecord(
        record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
        producer_kind="client", producer_id="c", instance_id="i",
        scope="instance", channel="system", level="INFO", type="probe")


print("=" * 72)
print("Sink-Ausfall: Sink deaktiviert, EINMAL an stderr, Store laeuft weiter")
print("=" * 72)


class BrokenSink:
    def __init__(self):
        self.calls = 0

    def write_batch(self, records):
        self.calls += 1
        raise OSError("injected sink failure")

    def close(self):
        return None


tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
store = SQLiteLogStore(tmp)
health = LoggingInternalHealth()
ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=512)
sink = BrokenSink()
w = LoggingWorker(ing, store, health=health, sink=sink, batch_size=5, flush_interval_s=0.03)
buf = io.StringIO()
with redirect_stderr(buf):
    w.start()
    for _ in range(50):
        ing.submit(rec())
    time.sleep(0.8)
    w.stop(1.0)
s = health.snapshot()
conn = sqlite3.connect(str(tmp))
rows = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
conn.close()
print(f"sink write attempts     : {sink.calls}  (1 erwartet: danach deaktiviert)")
print(f"sink_errors             : {s.sink_errors}")
print(f"health.state            : {s.state.value}")
print(f"written / rows in store : {s.written} / {rows}")
print(f"stderr                  : {buf.getvalue().strip().splitlines()}")

print()
print("=" * 72)
print("JSONL-Sink Vertrag: schemaVersion als ERSTES Feld, Tagesrotation")
print("=" * 72)
d = Path(tempfile.mkdtemp())
js = JsonlSink(d)
js.write_batch([rec(), rec()])
js.close()
files = sorted(p.name for p in d.iterdir())
print("Dateien:", files)
first = (d / files[0]).read_text(encoding="utf-8").splitlines()[0]
print("erste Zeile:", first[:160])
print("erstes JSON-Feld:", list(json.loads(first).keys())[0])

print()
print("=" * 72)
print("Reihenfolge im Worker: write_batch ZUERST, Sink DANACH (CONTRACTS 11.1)")
print("=" * 72)
order = []


class OrderStore:
    def open(self):
        from core.observability.storage.sqlite import OpenResult
        return OpenResult(True, False, "")

    def write_batch(self, records):
        order.append("store")
        return (len(records), 0)

    def run_retention(self, **kw):
        return (0, 0)

    def measure_db_bytes(self):
        return None

    def probe_write(self):
        return True

    def close(self):
        return None


class OrderSink:
    def write_batch(self, records):
        order.append("sink")

    def close(self):
        return None


h = LoggingInternalHealth()
i2 = ObservabilityIngress(instance_id="p", health=h, queue_size=64)
w2 = LoggingWorker(i2, OrderStore(), health=h, sink=OrderSink())
w2._process_batch([rec()])
print("Reihenfolge:", order)
