"""OBS-060 - End-to-end proof of the complete V1 chain.

Canonical model -> Ingress -> Queue -> Worker -> SQLite -> Query -> UI.

Everything below the UI is the REAL component: the real ``ObservabilityIngress``,
the real ``LoggingWorker`` on its own thread, the real ``SQLiteLogStore`` on a
temporary file, the real ``JsonlSink``, the real ``LocalLogProvider`` and the
real ``LogQueryService``. The UI layer is exercised through the real
``LogQueryController`` with a real Qt event loop (offscreen).

Run:  QT_QPA_PLATFORM=offscreen python <this file>
Exit: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import json
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

from core.observability.ingress import ObservabilityIngress
from core.observability.manager import ObservabilityManager
from core.observability.models import CanonicalLogRecord
from core.observability.query.base import QueryFilter
from core.observability.query.local import LocalLogProvider
from core.observability.query.service import LogQueryService
from core.observability.sinks.jsonl_file import JsonlSink
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker

FAILURES: list = []


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


def _row_count(db):
    if not db.exists():
        return 0
    connection = sqlite3.connect(str(db))
    try:
        return int(connection.execute("SELECT COUNT(*) FROM logs").fetchone()[0])
    except Exception:  # noqa: BLE001
        return 0
    finally:
        connection.close()


# ---------------------------------------------------------------------------
# P-1  the whole chain end to end, with the real worker thread
# ---------------------------------------------------------------------------

def p1_full_chain(tmp):
    db = tmp / "p1" / "observability.sqlite3"
    sink_dir = tmp / "p1" / "sink"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=256)
    store = SQLiteLogStore(db)
    sink = JsonlSink(sink_dir)
    worker = LoggingWorker(ingress, store, sink=sink, batch_size=32, flush_interval_s=0.05)
    worker.start()
    try:
        for index in range(50):
            ingress.event(
                "client.trigger.sent",
                channel="audit",
                component="controller",
                message="trigger " + str(index),
                session_id="session-1",
                generation=1,
                command_id="cmd-" + str(index),
                correlation_id="command:cmd-" + str(index),
            )
        ok = wait_until(lambda: _row_count(db) >= 50)
        check("P-1.1 all 50 client events reach SQLite through the real worker",
              ok, "rows=" + str(_row_count(db)))

        provider = LocalLogProvider(db)
        service = LogQueryService()
        service.register(provider)
        page = service.query("local", QueryFilter(session_id="session-1"), None, 100)
        check("P-1.2 the query layer reads them back through the service",
              len(page.records) == 50, "records=" + str(len(page.records)))
        check("P-1.3 the page carries no raw payload (CONTRACTS 5.7)",
              all(view.raw is None for view in page.records))
        expected = set("command:cmd-" + str(i) for i in range(50))
        check("P-1.4 correlation chain survives the round trip",
              set(view.correlation_id for view in page.records) == expected)

        lines = []
        for path in sorted(sink_dir.glob("*.jsonl")):
            lines.extend(path.read_text(encoding="utf-8").splitlines())
        check("P-1.5 the JSONL sink received the same records", len(lines) >= 50,
              "lines=" + str(len(lines)))
        if lines:
            first = json.loads(lines[0])
            check("P-1.6 schemaVersion is the first JSONL key (CONTRACTS 11.1)",
                  next(iter(first)) == "schemaVersion")
    finally:
        worker.stop(2.0)


# ---------------------------------------------------------------------------
# P-2  canonical identity: record_id survives, event_id dedupes
# ---------------------------------------------------------------------------

def p2_identity_and_dedupe(tmp):
    db = tmp / "p2" / "observability.sqlite3"
    store = SQLiteLogStore(db)
    store.open()
    try:
        server = record(producer_kind="server", producer_id="voice-stt-server",
                        event_id="evt-1", type="transcription.completed",
                        channel="transcription", scope="session",
                        session_id="s1", server_cursor=7)
        inserted, deduped = store.write_batch([server])
        check("P-2.1 first server record inserts", (inserted, deduped) == (1, 0),
              str(inserted) + "/" + str(deduped))
        same_again = record(producer_kind="server", producer_id="voice-stt-server",
                            event_id="evt-1", type="transcription.completed",
                            channel="transcription", scope="session",
                            session_id="s1", server_cursor=7, replayed=True)
        inserted, deduped = store.write_batch([same_again])
        check("P-2.2 the replayed duplicate is deduplicated, not inserted",
              (inserted, deduped) == (0, 1), str(inserted) + "/" + str(deduped))

        rows = store._connection.execute(
            "SELECT replayed FROM logs WHERE event_id = 'evt-1'").fetchall()
        check("P-2.3 the FIRST version wins (ON CONFLICT DO NOTHING)",
              len(rows) == 1 and rows[0][0] == 0, str(rows))

        inserted, _ = store.write_batch([record(), record()])
        check("P-2.4 client records without event_id are never deduplicated",
              inserted == 2, "inserted=" + str(inserted))
    finally:
        store.close()


# ---------------------------------------------------------------------------
# P-3  restart / recovery
# ---------------------------------------------------------------------------

def p3_restart_recovery(tmp):
    db = tmp / "p3" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=128)
    store = SQLiteLogStore(db)
    worker = LoggingWorker(ingress, store, batch_size=16, flush_interval_s=0.05)
    worker.start()
    for index in range(20):
        ingress.event("client.app.started", channel="system", message="run-1 " + str(index))
    wait_until(lambda: _row_count(db) >= 20)
    worker.stop(2.0)
    first_rows = _row_count(db)

    ingress2 = ObservabilityIngress(instance_id="inst-1", queue_size=128)
    store2 = SQLiteLogStore(db)
    worker2 = LoggingWorker(ingress2, store2, batch_size=16, flush_interval_s=0.05)
    worker2.start()
    for index in range(20):
        ingress2.event("client.app.started", channel="system", message="run-2 " + str(index))
    ok = wait_until(lambda: _row_count(db) >= first_rows + 20)
    worker2.stop(2.0)

    check("P-3.1 the history of the first run survives the restart",
          _row_count(db) >= first_rows + 20, "rows=" + str(_row_count(db)))
    connection = sqlite3.connect(str(db))
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    connection.close()
    check("P-3.2 no re-migration on the second open (user_version stays 1)",
          version == 1, "user_version=" + str(version))
    check("P-3.3 the second run really appended", ok)


# ---------------------------------------------------------------------------
# P-4  shutdown flush: stop() is the only flush guarantee (G-7)
# ---------------------------------------------------------------------------

def p4_shutdown_flush(tmp):
    db = tmp / "p4" / "observability.sqlite3"
    ingress = ObservabilityIngress(instance_id="inst-1", queue_size=4096)
    store = SQLiteLogStore(db)
    worker = LoggingWorker(ingress, store, batch_size=500, flush_interval_s=5.0)
    worker.start()
    time.sleep(0.1)
    for index in range(300):
        ingress.event("client.app.started", channel="system", message=str(index))
    stopped = worker.stop(3.0)
    rows = _row_count(db)
    check("P-4.1 stop() returns True (worker joined)", stopped)
    check("P-4.2 the shutdown flush persisted the queued records",
          rows >= 300, "rows=" + str(rows))
    snapshot = ingress.health.snapshot()
    check("P-4.3 nothing was lost uncounted (enqueued == written + dropped_shutdown)",
          snapshot.enqueued == snapshot.written + snapshot.dropped_shutdown,
          "enqueued=" + str(snapshot.enqueued) + " written=" + str(snapshot.written)
          + " dropped_shutdown=" + str(snapshot.dropped_shutdown))


# ---------------------------------------------------------------------------
# P-5  UI layer: the real LogQueryController over the real service
# ---------------------------------------------------------------------------

def p5_ui_layer(tmp):
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        from PySide6.QtCore import QCoreApplication, QEventLoop, QTimer
    except Exception as exc:  # noqa: BLE001
        check("P-5 Qt available", False, str(exc))
        return
    from ui.logs.log_query_controller import LogQueryController

    db = tmp / "p5" / "observability.sqlite3"
    store = SQLiteLogStore(db)
    store.open()
    store.write_batch([
        record(record_id="rec-%03d" % i, type="client.trigger.sent", channel="audit",
               session_id="s-ui", message="row " + str(i),
               raw={"value": i})
        for i in range(12)
    ])
    store.close()

    app = QCoreApplication.instance() or QCoreApplication([])
    service = LogQueryService()
    service.register(LocalLogProvider(db))
    controller = LogQueryController(service)

    pages = []
    loop = QEventLoop()
    QTimer.singleShot(4000, loop.quit)
    controller.page_ready.connect(lambda rid, page: (pages.append(page), loop.quit()))
    controller.request_page("local", QueryFilter(session_id="s-ui"), limit=5)
    loop.exec()

    check("P-5.1 the controller delivered a page from the real provider",
          len(pages) == 1 and len(pages[0].records) == 5,
          "pages=" + str(len(pages)))
    if pages:
        check("P-5.2 the page offers a next cursor (keyset pagination)",
              pages[0].next_cursor is not None)
        check("P-5.3 the list page never carries raw",
              all(view.raw is None for view in pages[0].records))

    raws = []
    loop2 = QEventLoop()
    QTimer.singleShot(4000, loop2.quit)
    controller.raw_ready.connect(
        lambda rid, record_id, payload: (raws.append(payload), loop2.quit()))
    controller.request_raw("local", "rec-003")
    loop2.exec()
    check("P-5.4 the detail view loads raw separately by record_id",
          len(raws) == 1 and raws[0] is not None, "raws=" + str(raws))
    controller.shutdown(wait=True)


# ---------------------------------------------------------------------------
# P-6  the composition root wires the same chain
# ---------------------------------------------------------------------------

class _Config:
    enabled = True
    level = "INFO"
    queue_size = 512
    batch_size = 32
    flush_interval_s = 0.05
    retention_days = 14
    max_entries = 200000
    max_db_bytes = None
    store_enabled = True
    store_raw_payload = True
    store_transcription_content = False
    file_sink_enabled = False
    file_sink_dir = None

    def __init__(self, db_path):
        self.db_path = str(db_path)


def p6_manager(tmp):
    db = tmp / "p6" / "observability.sqlite3"
    db.parent.mkdir(parents=True, exist_ok=True)
    manager = ObservabilityManager(_Config(db), instance_id="inst-mgr")
    manager.start()
    try:
        manager.ingress.event("client.app.started", channel="system",
                              component="probe", message="via manager")
        ok = wait_until(lambda: _row_count(db) >= 1)
        check("P-6.1 the manager chain persists a record", ok,
              "rows=" + str(_row_count(db)))
        page = manager.query_service.query("local", QueryFilter(), None, 10)
        check("P-6.2 the manager query service reads the same store",
              any(view.type == "client.app.started" for view in page.records))
        check("P-6.3 db_path is the resolved path the provider opens",
              Path(manager.db_path) == db, str(manager.db_path))
        snapshot = manager.health_snapshot()
        check("P-6.4 health is OK and counters are consistent",
              snapshot.state.value == "ok" and snapshot.written >= 1,
              str(snapshot.state) + " written=" + str(snapshot.written))
    finally:
        manager.stop(2.0)


def main():
    with tempfile.TemporaryDirectory() as directory:
        tmp = Path(directory)
        print("=== P-1  full chain: ingress -> queue -> worker -> sqlite -> query ===")
        p1_full_chain(tmp)
        print("")
        print("=== P-2  identity, replay and dedupe ===")
        p2_identity_and_dedupe(tmp)
        print("")
        print("=== P-3  restart / recovery ===")
        p3_restart_recovery(tmp)
        print("")
        print("=== P-4  shutdown flush ===")
        p4_shutdown_flush(tmp)
        print("")
        print("=== P-5  UI layer over the real controller ===")
        p5_ui_layer(tmp)
        print("")
        print("=== P-6  composition root ===")
        p6_manager(tmp)

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
