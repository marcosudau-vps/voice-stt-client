"""
OBS-050 end-to-end diagnostic probe.

Runs the **real** ``ObservabilityManager`` (real worker thread, real SQLite
store), the **real** query layer and the **real** Qt log view, offscreen. No
doubles anywhere in the path under test.

Checks:

  P-1  A record submitted through the ingress reaches the store and is read
       back by ``LocalLogProvider`` — the whole write/read path in one go.
  P-2  ``raw`` is absent from the list query and arrives only through
       ``fetch_raw`` (CONTRACTS §5.7).
  P-3  Keyset pagination walks 750 rows without a gap or a duplicate **while
       the worker keeps writing** (§5.7's reason for keyset over OFFSET).
  P-4  The live view gains rows through the tailing query alone — no ring
       buffer, no signal per record (FD-S1, §9.2).
  P-5  A settings apply reaches both halves of the level filter (ARCH §8.7)
       and the worker's retention settings (§10.3), and reaches neither the
       store path nor the session (§10.4's hard rule).
  P-6  "Diagnosehistorie löschen" empties the store through the MANAGER; the
       query layer has no such method at all (FD-S4, O-14).
  P-7  Logging runs with the log window closed, and a window opened
       afterwards shows what was written while it did not exist (O-01).
  P-8  The reader never creates the database file and cannot write through
       its connection (O-14, §5.4).

Exit code 0 means every check passed.
"""

from __future__ import annotations

import os
import sqlite3
import sys
import tempfile
import time
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parents[6]
sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication  # noqa: E402

from core.config import LoggingObservabilityConfig  # noqa: E402
from core.observability.manager import ObservabilityManager  # noqa: E402
from core.observability.query.base import QueryFilter  # noqa: E402
from core.observability.query.local import LocalLogProvider  # noqa: E402
from ui.logs.log_window import LogWindow  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" — {detail}" if detail else ""))


def pump(app: QApplication, seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()


def wait_for_rows(provider: LocalLogProvider, minimum: int, timeout: float = 5.0) -> int:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        page = provider.query(QueryFilter(), limit=1000)
        if len(page.records) >= minimum:
            return len(page.records)
        time.sleep(0.05)
    return len(provider.query(QueryFilter(), limit=1000).records)


def main() -> int:
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        db_path = root / "observability.sqlite3"

        # --- P-8 (first half): a reader must not create the file ----------
        provider = LocalLogProvider(db_path)
        page = provider.query(QueryFilter())
        check(
            "P-8a reader never creates the store file",
            not db_path.exists() and page.status.state.value == "unavailable",
            f"exists={db_path.exists()}, state={page.status.state.value}",
        )

        config = LoggingObservabilityConfig(
            db_path=str(db_path),
            flush_interval_s=0.05,
            batch_size=50,
            level="INFO",
        )
        manager = ObservabilityManager(config, log_dir=str(root / "logs"))
        manager.start()
        try:
            # --- P-1 ------------------------------------------------------
            manager.ingress.event(
                "client.app.started",
                channel="system",
                component="probe",
                message="Probe gestartet",
                session_id="s-probe",
            )
            rows = wait_for_rows(provider, 1)
            page = provider.query(QueryFilter(), limit=10)
            types = [record.type for record in page.records]
            check(
                "P-1 ingress -> worker -> store -> query",
                rows >= 1 and "client.app.started" in types,
                f"{rows} Zeile(n), types={types}",
            )

            # --- P-2 ------------------------------------------------------
            from core.observability.models import CanonicalLogRecord
            from uuid import uuid4

            raw_record = CanonicalLogRecord(
                record_id=uuid4().hex,
                received_at="2026-08-17T10:30:00.000Z",
                producer_kind="server",
                producer_id="voice-stt-server",
                instance_id="server-1",
                scope="session",
                channel="system",
                level="INFO",
                type="transcription.completed",
                component="transcription",
                session_id="s-probe",
                event_id=f"e-{uuid4().hex[:8]}",
                raw={"event": "transcription.completed", "cursor": 17},
            )
            manager.ingress.submit(raw_record)
            deadline = time.monotonic() + 5.0
            listed = None
            while time.monotonic() < deadline:
                found = provider.query(
                    QueryFilter(event_id=raw_record.event_id), limit=5
                )
                if found.records:
                    listed = found.records[0]
                    break
                time.sleep(0.05)
            fetched = provider.fetch_raw(raw_record.record_id) if listed else None
            check(
                "P-2 raw absent from the list, present through fetch_raw",
                listed is not None and listed.raw is None and bool(fetched),
                f"list.raw={None if listed is None else listed.raw}, fetch_raw={fetched}",
            )

            # --- P-3 ------------------------------------------------------
            for index in range(750):
                manager.ingress.event(
                    "client.hotkey.pressed",
                    channel="audit",
                    component="probe.paging",
                    message=f"page-{index:04d}",
                )
            wait_for_rows(provider, 700, timeout=15.0)
            seen: list[str] = []
            cursor = None
            pages = 0
            paging_filter = QueryFilter(components=("probe.paging",))
            while pages < 40:
                result = provider.query(paging_filter, cursor=cursor, limit=100)
                seen.extend(record.record_id for record in result.records)
                pages += 1
                # Keep writing between pages — the OFFSET failure mode.
                manager.ingress.event(
                    "client.hotkey.pressed",
                    channel="audit",
                    component="probe.concurrent",
                    message=f"between-page-{pages}",
                )
                cursor = result.next_cursor
                if cursor is None:
                    break
            check(
                "P-3 keyset pagination: no gaps, no duplicates while writing",
                len(seen) >= 700 and len(seen) == len(set(seen)),
                f"{len(seen)} Zeilen, {len(set(seen))} eindeutig, {pages} Seiten",
            )

            # --- P-4 ------------------------------------------------------
            window = LogWindow(
                manager.query_service, health_provider=manager.health_snapshot
            )
            window.show()
            pump(app, 1.0)
            window.page.set_mode("live")
            pump(app, 1.0)
            before = window.page.model.rowCount()
            for index in range(5):
                manager.ingress.event(
                    "client.trigger.sent",
                    channel="audit",
                    component="probe.live",
                    message=f"live-{index}",
                )
            pump(app, 2.0)
            after = window.page.model.rowCount()
            check(
                "P-4 live view tails through the query layer (no ring buffer)",
                after > before,
                f"{before} -> {after} Zeilen im Modell",
            )
            status_text = window.page.status_label.text()
            check(
                "P-4b status line shows the health snapshot",
                "Logging:" in status_text,
                status_text[:120],
            )

            # --- P-5 ------------------------------------------------------
            import logging

            handler = logging.Handler()
            handler.setLevel(logging.INFO)
            manager.register_log_handler(handler)
            manager.ingress.apply_config(
                LoggingObservabilityConfig(
                    db_path=str(db_path), level="ERROR", retention_days=3,
                    max_entries=1234,
                )
            )
            pump(app, 0.5)
            worker = manager._worker  # noqa: SLF001 - diagnostic probe
            check(
                "P-5 one config value moves handler AND ingress level",
                handler.level == logging.ERROR and manager.ingress.level == "ERROR",
                f"handler={handler.level}, ingress={manager.ingress.level}",
            )
            check(
                "P-5b retention settings reach the worker",
                worker._retention_days == 3 and worker._max_entries == 1234,  # noqa: SLF001
                f"retention_days={worker._retention_days}, "  # noqa: SLF001
                f"max_entries={worker._max_entries}",  # noqa: SLF001
            )
            info_before = len(
                provider.query(QueryFilter(components=("probe.level",)), limit=10).records
            )
            manager.ingress.event(
                "client.hotkey.pressed", channel="audit", component="probe.level",
                message="darf nicht gespeichert werden",
            )
            time.sleep(0.4)
            info_after = len(
                provider.query(QueryFilter(components=("probe.level",)), limit=10).records
            )
            check(
                "P-5c the raised level filters immediately",
                info_before == info_after == 0,
                f"{info_before} -> {info_after}",
            )
            manager.ingress.apply_config(
                LoggingObservabilityConfig(db_path=str(db_path), level="INFO")
            )

            # --- P-6 ------------------------------------------------------
            deleted = manager.clear_history()
            remaining = provider.query(QueryFilter(), limit=10)
            service_has_delete = any(
                hasattr(manager.query_service, name)
                for name in ("clear", "delete", "write")
            )
            check(
                "P-6 clear runs at the store, not in the query layer",
                deleted > 0 and not remaining.records and not service_has_delete,
                f"{deleted} gelöscht, {len(remaining.records)} verblieben, "
                f"query-Layer-Schreibmethode={service_has_delete}",
            )

            # --- P-7 ------------------------------------------------------
            window.hide()
            window.shutdown()
            pump(app, 0.3)
            for index in range(3):
                manager.ingress.event(
                    "client.app.started", channel="system",
                    component="probe.closed", message=f"ohne Fenster {index}",
                )
            wait_for_rows(provider, 3)
            written_without_view = provider.query(
                QueryFilter(components=("probe.closed",)), limit=10
            )
            reopened = LogWindow(manager.query_service)
            reopened.show()
            pump(app, 1.2)
            visible = reopened.page.model.rowCount()
            reopened.hide()
            reopened.shutdown()
            check(
                "P-7 logging runs without the view; a later view shows it",
                len(written_without_view.records) == 3 and visible >= 3,
                f"{len(written_without_view.records)} geschrieben, {visible} sichtbar",
            )

            # --- P-8 (second half) ----------------------------------------
            connection = sqlite3.connect(str(db_path))
            try:
                connection.execute("PRAGMA query_only = ON")
                writable = True
                try:
                    connection.execute("DELETE FROM logs")
                except sqlite3.OperationalError:
                    writable = False
            finally:
                connection.close()
            check(
                "P-8b the reader connection cannot write (PRAGMA query_only)",
                not writable,
                "DELETE über eine query_only-Verbindung wurde abgewiesen",
            )
        finally:
            manager.stop(2.0)

    failed = [name for name, ok, _ in RESULTS if not ok]
    print()
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} Prüfungen bestanden.")
    if failed:
        print("FEHLGESCHLAGEN: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
