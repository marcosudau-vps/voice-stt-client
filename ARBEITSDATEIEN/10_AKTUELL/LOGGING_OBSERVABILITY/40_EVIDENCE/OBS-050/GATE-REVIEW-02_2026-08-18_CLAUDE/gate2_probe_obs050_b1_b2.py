"""OBS-050 Re-Gate probe: B-1 and B-2 against the corrected LogPage.

Real SQLiteLogStore, real LocalLogProvider, real LogQueryService, real Qt
LogPage (offscreen). No doubles anywhere in the path under test.
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
from core.observability.query.base import QueryFilter  # noqa: E402
from core.observability.query.local import LocalLogProvider, decode_cursor  # noqa: E402
from core.observability.query.service import LogQueryService  # noqa: E402
from core.observability.storage.sqlite import SQLiteLogStore  # noqa: E402
from ui.logs.log_page import LogPage, MODE_HISTORY, MODE_LIVE  # noqa: E402
from ui.logs.log_query_controller import LogQueryController  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def rec(i: int, channel: str = "system") -> CanonicalLogRecord:
    return CanonicalLogRecord(
        record_id=f"r{i:04d}",
        received_at=f"2026-08-18T10:{i // 60:02d}:{i % 60:02d}.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="i-1",
        scope="instance",
        channel=channel,
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


def rows(page):
    return [r.record_id for r in page.model.records()]


def cursor_ids(page):
    return [decode_cursor(r.cursor) for r in page.model.records()]


def build(db, page_size=5):
    service = LogQueryService()
    service.register(LocalLogProvider(db))
    controller = LogQueryController(service)
    return controller, LogPage(controller, page_size=page_size)


def main() -> int:
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as d:
        # ================= B-1: history over more than three pages =========
        db = Path(d) / "hist.sqlite3"
        store = SQLiteLogStore(db)
        store.open()
        store.write_batch([rec(i) for i in range(23)])
        controller, page = build(db, page_size=5)
        page.reload()
        pump(app)
        first = cursor_ids(page)
        check("B1-a first history page is descending (newest on top)",
              first == sorted(first, reverse=True) and len(first) == 5,
              f"ids={first}")

        # four explicit "Weitere laden" -> five pages in total
        for _ in range(4):
            page.load_more()
            pump(app)
        walked = cursor_ids(page)
        strictly_desc = all(walked[i] > walked[i + 1] for i in range(len(walked) - 1))
        check("B1-b five pages stay strictly descending, no direction break",
              strictly_desc, f"{len(walked)} Zeilen, erste={walked[:3]}, letzte={walked[-3:]}")
        check("B1-c no duplicates across pages",
              len(walked) == len(set(walked)), f"{len(walked)} Zeilen / {len(set(walked))} eindeutig")

        expected = sorted(
            [decode_cursor(r.cursor)
             for r in LocalLogProvider(db).query(QueryFilter(), limit=1000).records],
            reverse=True,
        )
        check("B1-d no omissions: the walked set equals the store",
              walked == expected[:len(walked)] and len(walked) == 23,
              f"gelaufen={len(walked)}, im Store={len(expected)}")
        check("B1-e last page reports no further page",
              page._next_cursor is None and not page.more_button.isEnabled(),  # noqa: SLF001
              f"next_cursor={page._next_cursor!r}")  # noqa: SLF001
        page.stop()
        controller.shutdown()

        # ---- automatic loading at the end of the list ---------------------
        controller, page = build(db, page_size=5)
        page.resize(400, 160)
        page.show()
        page.reload()
        pump(app)
        before = len(rows(page))
        bar = page.table.verticalScrollBar()
        for _ in range(4):
            bar.setValue(bar.maximum())
            pump(app, 0.4)
        auto = cursor_ids(page)
        check("B1-f automatic loading at the list end keeps the same order",
              len(auto) > before
              and all(auto[i] > auto[i + 1] for i in range(len(auto) - 1))
              and len(auto) == len(set(auto)),
              f"{before} -> {len(auto)} Zeilen, strikt absteigend={all(auto[i] > auto[i+1] for i in range(len(auto)-1))}")
        page.hide()
        page.stop()
        controller.shutdown()
        store.close()

        # ================= B-2: live start on an empty result ==============
        db2 = Path(d) / "live.sqlite3"
        store2 = SQLiteLogStore(db2)
        store2.open()
        controller, page = build(db2, page_size=5)
        page.set_mode(MODE_LIVE)
        pump(app)
        check("B2-a live seed on an empty store shows nothing and no cursor",
              page.model.rowCount() == 0 and page._live_cursor is None,  # noqa: SLF001
              f"rows={page.model.rowCount()}, cursor={page._live_cursor!r}")  # noqa: SLF001

        store2.write_batch([rec(i) for i in range(5)])
        pump(app, 0.9)
        t1 = cursor_ids(page)
        check("B2-b first tail after the empty seed is ascending, no duplicates",
              t1 == sorted(t1) and len(t1) == len(set(t1)) == 5, f"ids={t1}")
        check("B2-c cursor points at the newest processed record",
              page._live_cursor is not None  # noqa: SLF001
              and decode_cursor(page._live_cursor) == max(t1),  # noqa: SLF001
              f"cursor={decode_cursor(page._live_cursor)}, max={max(t1)}")  # noqa: SLF001

        store2.write_batch([rec(i) for i in range(5, 9)])
        pump(app, 0.9)
        t2 = cursor_ids(page)
        store2.write_batch([rec(i) for i in range(9, 12)])
        pump(app, 0.9)
        t3 = cursor_ids(page)
        check("B2-d further tails continue behind the cursor, no duplicates, nothing lost",
              t3 == sorted(t3) and len(t3) == len(set(t3)) == 12
              and t3[:len(t2)] == t2,
              f"{len(t1)} -> {len(t2)} -> {len(t3)} Zeilen")
        page.stop()
        controller.shutdown()

        # ---- filter without hits, then a filter change in live mode -------
        db3 = Path(d) / "filter.sqlite3"
        store3 = SQLiteLogStore(db3)
        store3.open()
        store3.write_batch([rec(i, channel="system") for i in range(4)])
        controller, page = build(db3, page_size=5)
        page.set_mode(MODE_LIVE)
        pump(app)
        page._on_filter_changed(QueryFilter(channels=("audit",)))  # noqa: SLF001
        pump(app, 0.6)
        check("B2-e live filter without hits stays empty",
              page.model.rowCount() == 0, f"rows={page.model.rowCount()}")
        store3.write_batch([rec(i, channel="audit") for i in range(20, 24)])
        pump(app, 0.9)
        f1 = cursor_ids(page)
        check("B2-f matching rows arriving later tail correctly under the filter",
              f1 == sorted(f1) and len(f1) == len(set(f1)) == 4, f"ids={f1}")

        page._on_filter_changed(QueryFilter())  # noqa: SLF001
        pump(app, 0.9)
        f2 = cursor_ids(page)
        check("B2-g filter change in live mode reseeds without duplicates",
              f2 == sorted(f2) and len(f2) == len(set(f2)), f"{len(f2)} Zeilen: {f2}")
        page.stop()
        controller.shutdown()

        # ---- already populated normal case --------------------------------
        controller, page = build(db3, page_size=5)
        page.set_mode(MODE_LIVE)
        pump(app)
        n1 = cursor_ids(page)
        store3.write_batch([rec(30), rec(31)])
        pump(app, 0.9)
        n2 = cursor_ids(page)
        check("B2-h populated live start still ascends and appends",
              n1 == sorted(n1) and n2 == sorted(n2)
              and len(n2) == len(set(n2)) and n2[:len(n1)] == n1 and len(n2) == len(n1) + 2,
              f"{len(n1)} -> {len(n2)} Zeilen")
        page.stop()
        controller.shutdown()

        # ---- the response kind must come from the request ------------------
        controller, page = build(db3, page_size=5)
        page.reload()
        pump(app)
        kind_after = page._active_kind  # noqa: SLF001
        page._live_cursor = "id:1"  # noqa: SLF001 - poison the old decision state
        page.load_more()
        pump(app)
        poisoned = cursor_ids(page)
        check("B2-i a stale _live_cursor no longer changes how an answer is read",
              poisoned == sorted(poisoned, reverse=True) and len(poisoned) == len(set(poisoned)),
              f"ids={poisoned}, kind nach Antwort={kind_after!r}")
        page.stop()
        controller.shutdown()
        store2.close()
        store3.close()

    failed = [name for name, ok, _ in RESULTS if not ok]
    print(f"\n{len(RESULTS) - len(failed)}/{len(RESULTS)} Pruefungen bestanden.")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
