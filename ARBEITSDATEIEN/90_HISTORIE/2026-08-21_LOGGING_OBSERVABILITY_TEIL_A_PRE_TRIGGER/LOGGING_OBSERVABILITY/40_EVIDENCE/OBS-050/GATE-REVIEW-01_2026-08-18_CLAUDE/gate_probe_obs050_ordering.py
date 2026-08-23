"""Independent gate probe: ordering determinism of the OBS-050 log view.

Real SQLiteLogStore, real LocalLogProvider, real LogQueryService, real Qt
LogPage (offscreen). No doubles.
"""
from __future__ import annotations

import os
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.observability.models import CanonicalLogRecord  # noqa: E402
from core.observability.storage.sqlite import SQLiteLogStore  # noqa: E402
from core.observability.query.local import LocalLogProvider  # noqa: E402
from core.observability.query.service import LogQueryService  # noqa: E402
from ui.logs.log_page import LogPage, MODE_LIVE  # noqa: E402
from ui.logs.log_query_controller import LogQueryController  # noqa: E402


def rec(i: int) -> CanonicalLogRecord:
    return CanonicalLogRecord(
        record_id=f"r{i:04d}",
        received_at=f"2026-08-17T10:00:{i:02d}.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="i-1",
        scope="instance",
        channel="system",
        level="INFO",
        type="client.app.started",
        component="probe",
        message=f"Zeile {i}",
    )


def pump(app, seconds=0.5):
    end = time.monotonic() + seconds
    while time.monotonic() < end:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()


def ids(page):
    return [r.record_id for r in page.model.records()]


def main() -> int:
    app = QApplication.instance() or QApplication([])
    failures = 0
    with tempfile.TemporaryDirectory() as d:
        db = Path(d) / "observability.sqlite3"
        store = SQLiteLogStore(db)
        store.open()

        # ---------- Case A: history pagination order ----------
        store.write_batch([rec(i) for i in range(12)])
        service = LogQueryService()
        service.register(LocalLogProvider(db))
        controller = LogQueryController(service)
        page = LogPage(controller, page_size=5)
        page.reload()
        pump(app)
        first = ids(page)
        print("A1 first page (top->bottom):", first)
        page.load_more()
        pump(app)
        after = ids(page)
        print("A2 after 'Weitere laden'  :", after)
        monotone = all(after[i] < after[i + 1] for i in range(len(after) - 1))
        print(f"A  chronologically monotone after load_more: {monotone}")
        if not monotone:
            failures += 1
        page.stop()
        controller.shutdown()

        # ---------- Case B: live mode starting from an empty result set ----------
        db2 = Path(d) / "observability2.sqlite3"
        store2 = SQLiteLogStore(db2)
        store2.open()
        # store exists but the current filter matches nothing yet
        service2 = LogQueryService()
        service2.register(LocalLogProvider(db2))
        controller2 = LogQueryController(service2)
        page2 = LogPage(controller2, page_size=5)
        page2.set_mode(MODE_LIVE)
        pump(app)
        print("B0 rows after switching to live on an empty store:", page2.model.rowCount())
        store2.write_batch([rec(i) for i in range(5)])
        pump(app, 0.8)
        b1 = ids(page2)
        print("B1 after first tail       :", b1)
        pump(app, 0.8)
        b2 = ids(page2)
        print("B2 after second tail      :", b2)
        ascending = all(b2[i] < b2[i + 1] for i in range(len(b2) - 1))
        duplicates = len(b2) != len(set(b2))
        print(f"B  ascending: {ascending}   duplicates present: {duplicates}")
        if not ascending or duplicates:
            failures += 1
        page2.stop()
        controller2.shutdown()

        store.close()
        store2.close()
    print("FAILURES:", failures)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
