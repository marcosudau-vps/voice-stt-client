"""Case C: live mode started on a NON-empty result set (the happy path)."""
from __future__ import annotations
import os, sys, tempfile, time
from pathlib import Path
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parents[6]))
from PySide6.QtWidgets import QApplication
from core.observability.models import CanonicalLogRecord
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.query.local import LocalLogProvider
from core.observability.query.service import LogQueryService
from ui.logs.log_page import LogPage, MODE_LIVE
from ui.logs.log_query_controller import LogQueryController

def rec(i):
    return CanonicalLogRecord(record_id=f"r{i:04d}",
        received_at=f"2026-08-17T10:00:{i:02d}.000Z", producer_kind="client",
        producer_id="c", instance_id="i-1", scope="instance", channel="system",
        level="INFO", type="t", component="probe", message=f"Zeile {i}")

def pump(app, s=0.6):
    end = time.monotonic() + s
    while time.monotonic() < end:
        app.processEvents(); time.sleep(0.01)
    app.processEvents()

app = QApplication.instance() or QApplication([])
with tempfile.TemporaryDirectory() as d:
    db = Path(d) / "o.sqlite3"
    store = SQLiteLogStore(db); store.open()
    store.write_batch([rec(i) for i in range(3)])
    svc = LogQueryService(); svc.register(LocalLogProvider(db))
    ctl = LogQueryController(svc); page = LogPage(ctl, page_size=5)
    page.set_mode(MODE_LIVE); pump(app)
    print("C1 after switching to live (non-empty):", [r.record_id for r in page.model.records()])
    store.write_batch([rec(7), rec(8)])
    pump(app, 0.8)
    got = [r.record_id for r in page.model.records()]
    print("C2 after tail:", got)
    asc = all(got[i] < got[i+1] for i in range(len(got)-1))
    dup = len(got) != len(set(got))
    print(f"C  ascending={asc} duplicates={dup}")
    page.stop(); ctl.shutdown(); store.close()
