"""Focused experiment: is the ARCH 8.3 store recovery reachable at all?

ARCH 8.3, row "Store wirft beim Schreiben":
    "nach 5 aufeinanderfolgenden Fehlschlaegen Store fuer 60 s aussetzen,
     danach mit einem leeren Testschreibvorgang pruefen"
CONTRACTS 11.2:
    "Recovery  Automatisch und still."
"""
import os, sqlite3, sys, tempfile, time
from pathlib import Path

sys.path.insert(0, r"P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur")

import core.observability.worker as worker_module
from core.observability.health import LoggingHealthState
from core.observability.ingress import ObservabilityIngress
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker


class FlakyStore:
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


def wait_until(pred, timeout=10.0):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        if pred():
            return True
        time.sleep(0.02)
    return pred()


worker_module.STORE_PAUSE_S = 0.5

with tempfile.TemporaryDirectory() as d:
    db = Path(d) / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="i", queue_size=4096)
    store = FlakyStore(SQLiteLogStore(db))
    worker = LoggingWorker(ingress, store, batch_size=1, flush_interval_s=0.02)
    worker.start()
    time.sleep(0.2)

    # enough single-record batches to cross the 5-failure threshold
    for i in range(12):
        ingress.event("client.app.started", channel="system", message=str(i))

    reached = wait_until(lambda: ingress.health.state is LoggingHealthState.FAILED_STORE, 10)
    print("FAILED_STORE reached          :", reached, ingress.health.state)
    print("write_calls at that moment    :", store.write_calls)
    print("queue depth                   :", ingress.qsize())

    # the store is healthy again from now on
    store.fail = False
    print("")
    print("--- store is healthy again; waiting well past the 0.5 s pause ---")
    time.sleep(3.0)
    print("state after 3 s               :", ingress.health.state)
    print("probe_write calls             :", store.probe_calls)
    print("rows in db                    :",
          (sqlite3.connect(str(db)).execute("SELECT COUNT(*) FROM logs").fetchone()[0]
           if db.exists() else 0))

    print("")
    print("--- a producer tries to log again ---")
    accepted = ingress.submit_probe if False else None
    ok = ingress.event("client.app.started", channel="system", message="after")
    print("qsize after the new event     :", ingress.qsize(),
          "(0 means the ingress refused it)")
    time.sleep(1.5)
    print("state                         :", ingress.health.state)
    print("probe_write calls             :", store.probe_calls)
    print("rows in db                    :",
          (sqlite3.connect(str(db)).execute("SELECT COUNT(*) FROM logs").fetchone()[0]
           if db.exists() else 0))
    worker.stop(2.0)
