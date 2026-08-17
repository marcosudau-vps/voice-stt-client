"""Gate-Review II: independent end-to-end / contract probes for OBS-030."""
from __future__ import annotations

import io
import json
import logging
import sqlite3
import tempfile
import threading
import time
from contextlib import redirect_stderr
from pathlib import Path
from uuid import uuid4

from core.config import LoggingConfig, LoggingObservabilityConfig
from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.manager import ObservabilityManager
from core.observability.models import CanonicalLogRecord, RecordPriority
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker


def hdr(t):
    print("\n" + "=" * 72)
    print(t)
    print("=" * 72)


def srec(event_id, replayed=False, **kw):
    base = dict(
        record_id=uuid4().hex,
        received_at="2026-08-17T10:00:00.000Z",
        producer_kind="server",
        producer_id="voice-stt-server",
        instance_id="srv-1",
        scope="instance",
        channel="system",
        level="INFO",
        type="server.event",
        event_id=event_id,
        replayed=replayed,
        raw={"payload": {"a": 1}},
    )
    base.update(kw)
    return CanonicalLogRecord(**base)


# --------------------------------------------------------------------------
def e2e_logger_to_sqlite():
    hdr("E2E  logger.info -> UnifiedLogHandler -> Ingress -> Worker -> SQLite")
    from core.logging_setup import setup_logging
    tmp = Path(tempfile.mkdtemp())
    db = tmp / "observability.sqlite3"
    cfg = LoggingObservabilityConfig(db_path=None, file_sink_enabled=False)
    mgr = ObservabilityManager(cfg)
    # redirect the store to a temp file (the frozen default would be the real profile)
    mgr._worker._store = SQLiteLogStore(db)
    mgr.start()
    log_cfg = LoggingConfig(log_dir=str(tmp / "logs"), stdout=False)
    setup_logging(log_cfg, observability=mgr)
    logging.getLogger("core.controller").info("gate review e2e probe %s", "xyz")
    time.sleep(1.0)
    mgr.stop(2.0)
    conn = sqlite3.connect(str(db))
    rows = conn.execute(
        "SELECT channel, level, component, message, producer_kind, scope, "
        "details_json FROM logs WHERE message LIKE '%gate review e2e probe%'"
    ).fetchall()
    total = conn.execute("SELECT COUNT(*) FROM logs").fetchone()[0]
    conn.close()
    print(f"rows total in store              : {total}")
    for r in rows:
        print(f"  channel={r[0]} level={r[1]} component={r[2]}")
        print(f"  message={r[3]!r}")
        print(f"  producer_kind={r[4]} scope={r[5]} details={r[6]}")
    print(f"logger.info reached SQLite       : {len(rows) == 1}")
    # remove the handler again so later probes are unaffected
    root = logging.getLogger()
    for h in list(root.handlers):
        root.removeHandler(h)


# --------------------------------------------------------------------------
def dedupe_and_restart():
    hdr("Dedupe-Identitaet ueber Prozess-/Store-Neustart + Persistenz")
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    store.open()
    ins1, dedup1 = store.write_batch([srec("evt-1"), srec("evt-2")])
    store.close()

    store2 = SQLiteLogStore(tmp)
    store2.open()
    rows_after_reopen = store2.row_count()
    ins2, dedup2 = store2.write_batch([srec("evt-1", replayed=True), srec("evt-3")])
    rows = store2.row_count()
    replayed_flag = store2._connection.execute(
        "SELECT replayed FROM logs WHERE event_id='evt-1'"
    ).fetchall()
    store2.close()
    print(f"1. Lauf : inserted={ins1} deduplicated={dedup1}")
    print(f"nach close()/reopen Zeilen       : {rows_after_reopen}")
    print(f"2. Lauf : inserted={ins2} deduplicated={dedup2}")
    print(f"Zeilen gesamt                    : {rows}")
    print(f"replayed-Flag fuer evt-1         : {replayed_flag} (erste Fassung gewinnt -> [(0,)])")

    # records without event_id are never deduplicated
    store3 = SQLiteLogStore(Path(tempfile.mkdtemp()) / "o.sqlite3")
    store3.open()
    a = CanonicalLogRecord(record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
                           producer_kind="client", producer_id="voice-stt-client",
                           instance_id="i", scope="instance", channel="system", level="INFO")
    i, d = store3.write_batch([a, a])
    print(f"ohne event_id: inserted={i} deduplicated={d} (kein partieller Index)")
    store3.close()


# --------------------------------------------------------------------------
def migration_cases():
    hdr("Migration: user_version=99 (nur lesen) und fehlgeschlagene Migration")
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    store.open()
    store.write_batch([srec("evt-a")])
    store.close()
    conn = sqlite3.connect(str(tmp))
    conn.execute("PRAGMA user_version = 99")
    conn.commit()
    conn.close()
    size_before = tmp.stat().st_size
    s2 = SQLiteLogStore(tmp)
    res = s2.open()
    rows = s2.row_count()
    ins, ded = s2.write_batch([srec("evt-b")])
    s2.close()
    print(f"open() -> ok={res.ok} degraded={res.degraded} detail={res.detail}")
    print(f"Zeilen unveraendert vorhanden    : {rows}")
    print(f"write_batch im Nur-Lese-Betrieb  : inserted={ins} deduplicated={ded}")
    print(f"Datei existiert weiterhin        : {tmp.exists()} (Groesse {size_before} -> {tmp.stat().st_size})")

    # failing migration -> rollback, file untouched
    tmp2 = Path(tempfile.mkdtemp()) / "obs2.sqlite3"
    import core.observability.storage.sqlite as sq

    def boom(conn, *, created_by_version):
        conn.execute("CREATE TABLE schema_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        raise sqlite3.OperationalError("injected migration failure")

    orig = sq._MIGRATIONS
    sq._MIGRATIONS = ((1, boom),)
    try:
        s3 = SQLiteLogStore(tmp2)
        r = s3.open()
        print(f"fehlgeschlagene Migration        : ok={r.ok} detail={r.detail}")
        c = sqlite3.connect(str(tmp2))
        tables = [t[0] for t in c.execute(
            "SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        uv = c.execute("PRAGMA user_version").fetchone()[0]
        c.close()
        print(f"Tabellen nach Rollback           : {tables}  user_version={uv}")
        print(f"Datei geloescht?                 : {not tmp2.exists()}")
    finally:
        sq._MIGRATIONS = orig


# --------------------------------------------------------------------------
def n05_foreign_thread():
    hdr("N-05  Verbindung aus einem Fremdthread")
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    result = {}

    def opener():
        store.open()

    t = threading.Thread(target=opener)
    t.start()
    t.join()

    def foreign():
        try:
            store.write_batch([srec("evt-x")])
            result["err"] = None
        except Exception as exc:  # noqa: BLE001
            result["err"] = f"{type(exc).__name__}: {exc}"

    t2 = threading.Thread(target=foreign)
    t2.start()
    t2.join()
    print("Fehler aus dem Fremdthread       :", result["err"])
    print("check_same_thread bleibt Standard:", "check_same_thread" not in
          Path("core/observability/storage/sqlite.py").read_text(encoding="utf-8")
          .split("def open")[1].split("def ")[0])


# --------------------------------------------------------------------------
def backpressure_and_recovery():
    hdr("Backpressure: Wasserstand, HIGH-Schutz, Recovery-Record")
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=20)
    lows, highs = [], []
    for i in range(40):
        low = CanonicalLogRecord(record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
                                 producer_kind="client", producer_id="c", instance_id="i",
                                 scope="instance", channel="system", level="INFO")
        high = CanonicalLogRecord(record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
                                  producer_kind="client", producer_id="c", instance_id="i",
                                  scope="instance", channel="system", level="ERROR")
        lows.append(ing.submit(low))
        highs.append(ing.submit(high))
    s = health.snapshot(queue_depth=ing.qsize())
    print(f"LOW akzeptiert  : {sum(lows)}/40")
    print(f"HIGH akzeptiert : {sum(highs)}/40")
    print(f"dropped_watermark={s.dropped_watermark} dropped_queue_full={s.dropped_queue_full} "
          f"enqueued={s.enqueued} queue_depth={s.queue_depth}")
    print(f"Buchhaltung enqueued+watermark+full = {s.enqueued + s.dropped_watermark + s.dropped_queue_full} (80 erwartet)")

    # HIGH-Sonderregel: replayed Serverevent mit type ist LOW
    r = srec("e", replayed=True)
    print(f"replayed Serverevent mit type    : {r.priority.value} (low erwartet)")
    print(f"nicht replayed, mit type         : {srec('e2').priority.value} (high erwartet)")
    print(f"internal record                  : "
          f"{CanonicalLogRecord(record_id='x', received_at='2026-08-17T10:00:00.000Z', producer_kind='client', producer_id='c', instance_id='i', scope='instance', channel='performance', level='DEBUG', is_internal=True).priority.value} (high erwartet)")

    # recovery record
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    health2 = LoggingInternalHealth()
    ing2 = ObservabilityIngress(instance_id="probe", health=health2, queue_size=20)
    w = LoggingWorker(ing2, store, health=health2, queue_size=20,
                      batch_size=50, flush_interval_s=0.02,
                      watermark_recovery_hold_s=0.2)
    with redirect_stderr(io.StringIO()):
        w.start()
        for _ in range(200):
            ing2.submit(CanonicalLogRecord(
                record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
                producer_kind="client", producer_id="c", instance_id="i",
                scope="instance", channel="system", level="INFO"))
        time.sleep(1.2)
        w.stop(2.0)
    conn = sqlite3.connect(str(tmp))
    rows = conn.execute(
        "SELECT type, channel, level, details_json FROM logs "
        "WHERE type='logging.records_dropped'").fetchall()
    conn.close()
    print(f"logging.records_dropped Records  : {len(rows)} (genau 1 erwartet)")
    for r in rows:
        print("   ", r)


# --------------------------------------------------------------------------
def retention_probe():
    hdr("Retention: Alter, Anzahl, kein VACUUM")
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    store.open()
    old = [CanonicalLogRecord(record_id=uuid4().hex, received_at="2020-01-01T00:00:00.000Z",
                              producer_kind="client", producer_id="c", instance_id="i",
                              scope="instance", channel="system", level="INFO")
           for _ in range(50)]
    new = [CanonicalLogRecord(record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
                              producer_kind="client", producer_id="c", instance_id="i",
                              scope="instance", channel="system", level="INFO")
           for _ in range(50)]
    store.write_batch(old + new)
    a, b = store.run_retention(cutoff_iso="2026-01-01T00:00:00.000Z",
                               max_entries=None, time_budget_s=1.0)
    print(f"nach Alter geloescht={a}  verbleibend={store.row_count()}")
    a2, b2 = store.run_retention(cutoff_iso=None, max_entries=20, time_budget_s=1.0)
    print(f"nach Anzahl geloescht={b2} verbleibend={store.row_count()}")
    a3, b3 = store.run_retention(cutoff_iso=None, max_entries=999, time_budget_s=1.0)
    print(f"max_entries > Zeilenzahl -> geloescht={b3} (0 erwartet, NULL-gesichert)")
    src = Path("core/observability/storage/sqlite.py").read_text(encoding="utf-8")
    print(f"'VACUUM' im Store-Quelltext      : {'VACUUM' in src.upper().replace('WAL_CHECKPOINT(TRUNCATE)','')}")
    print(f"'auto_vacuum' im Quelltext       : {'auto_vacuum' in src}")
    store.close()


# --------------------------------------------------------------------------
def no_ringbuffer_and_single_queue():
    hdr("Kein Memory-Ringbuffer, genau eine Queue")
    import re
    hits = []
    for p in Path("core/observability").rglob("*.py"):
        text = p.read_text(encoding="utf-8")
        for pat in ("deque", "ring_buffer", "live_buffer", "RingBuffer"):
            if pat in text:
                hits.append((str(p), pat))
        for m in re.finditer(r"queue\.Queue\(", text):
            hits.append((str(p), "queue.Queue("))
    print("Treffer:", hits if hits else "keine")


# --------------------------------------------------------------------------
def shutdown_accounting():
    hdr("Shutdown-Buchhaltung mit Queue-Resten")
    tmp = Path(tempfile.mkdtemp()) / "obs.sqlite3"
    store = SQLiteLogStore(tmp)
    health = LoggingInternalHealth()
    ing = ObservabilityIngress(instance_id="probe", health=health, queue_size=4096)
    w = LoggingWorker(ing, store, health=health, queue_size=4096,
                      batch_size=20, flush_interval_s=0.05)
    buf = io.StringIO()
    with redirect_stderr(buf):
        w.start()
        time.sleep(0.1)
        for _ in range(3000):
            ing.submit(CanonicalLogRecord(
                record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
                producer_kind="client", producer_id="c", instance_id="i",
                scope="instance", channel="system", level="INFO"))
        ok = w.stop(0.2)
    s = health.snapshot(queue_depth=ing.qsize())
    total = s.written + s.dropped_shutdown + s.dropped_watermark + s.dropped_queue_full
    left = [t.name for t in threading.enumerate() if "Observability" in t.name]
    print(f"stop() -> {ok}")
    print(f"enqueued={s.enqueued} written={s.written} dropped_shutdown={s.dropped_shutdown} "
          f"watermark={s.dropped_watermark} queue_full={s.dropped_queue_full}")
    print(f"written+dropped_* = {total}   enqueued+watermark+full = "
          f"{s.enqueued + s.dropped_watermark + s.dropped_queue_full}")
    print(f"restliche Observability-Threads  : {left}")
    print(f"stderr-Zeilen                    : {buf.getvalue().strip().splitlines()}")


if __name__ == "__main__":
    e2e_logger_to_sqlite()
    dedupe_and_restart()
    migration_cases()
    n05_foreign_thread()
    backpressure_and_recovery()
    retention_probe()
    no_ringbuffer_and_single_queue()
    shutdown_accounting()
