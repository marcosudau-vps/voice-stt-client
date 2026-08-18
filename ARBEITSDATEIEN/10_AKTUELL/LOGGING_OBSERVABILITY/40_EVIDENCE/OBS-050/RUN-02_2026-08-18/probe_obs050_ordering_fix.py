"""
OBS-050 RUN-02 — Laufzeitnachweis für die Gate-Befunde B-1 und B-2.

Echter ``SQLiteLogStore``, echter ``LocalLogProvider``, echter
``LogQueryService``, echtes Qt-``LogPage`` (offscreen). Kein Double.

Geprüft wird die **Anzeigereihenfolge**, richtungsbewusst:

  A   Historie über drei Seiten: streng monoton **absteigend**, keine
      Duplikate, kein Rückwärtssprung an einer Seitengrenze (B-1).
  A2  dieselbe Strecke über das automatische Nachladen am Listenende.
  B   Live auf **leerem** Ergebnis, danach eintreffende Records: streng
      monoton aufsteigend, keine Duplikate, Cursor aus dem **neuesten**
      Record; mehrere aufeinanderfolgende Tails (B-2).
  C   Live auf befülltem Store — die vom Gate bestätigte Gegenprobe darf
      nicht regressieren.
  D   Filterwechsel im laufenden Live-Modus (setzt ``_live_cursor`` zurück —
      genau der Zustand, der B-2 ausgelöst hat).

Zur Einordnung von Fall A: Der Gate-Review nennt zwei zulässige minimale
Korrekturen; dieser Lauf hat **Variante 1** gewählt ("Die Umkehrung je Seite
entfällt; die Tabelle zeigt durchgehend absteigend (neueste oben). Das passt
ohne weitere Änderung zum bestehenden Nachladen-am-Listenende, weil 'unten'
dann 'älter' bedeutet."). Die Gate-Probe prüft hart auf *aufsteigend* und
meldet für Variante 1 deshalb ``monotone: False``; diese Probe prüft dieselbe
Eigenschaft — keine Rückwärtssprünge über Seitengrenzen — in der tatsächlichen
Anzeigerichtung.

Exitcode 0 = alle Prüfungen bestanden.
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
from core.observability.query.local import LocalLogProvider  # noqa: E402
from core.observability.query.service import LogQueryService  # noqa: E402
from core.observability.storage.sqlite import SQLiteLogStore  # noqa: E402
from ui.logs.log_page import MODE_LIVE, LogPage  # noqa: E402
from ui.logs.log_query_controller import LogQueryController  # noqa: E402

RESULTS: list = []


def check(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, bool(ok), detail))
    print(f"[{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def rec(index: int) -> CanonicalLogRecord:
    return CanonicalLogRecord(
        record_id=f"r{index:04d}",
        received_at=f"2026-08-18T10:00:{index % 60:02d}.000Z",
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="i-1",
        scope="instance",
        channel="system",
        level="INFO",
        type="client.app.started",
        component="probe",
        message=f"Zeile {index}",
    )


def pump(app, seconds: float = 0.6) -> None:
    deadline = time.monotonic() + seconds
    while time.monotonic() < deadline:
        app.processEvents()
        time.sleep(0.01)
    app.processEvents()


def ids(page: LogPage) -> list:
    return [record.record_id for record in page.model.records()]


def strictly_descending(values: list) -> bool:
    return all(values[i] > values[i + 1] for i in range(len(values) - 1))


def strictly_ascending(values: list) -> bool:
    return all(values[i] < values[i + 1] for i in range(len(values) - 1))


def build(directory: Path, name: str, count: int):
    db = directory / name
    store = SQLiteLogStore(db)
    store.open()
    if count:
        store.write_batch([rec(index) for index in range(count)])
    service = LogQueryService()
    service.register(LocalLogProvider(db))
    controller = LogQueryController(service)
    return store, controller


def main() -> int:
    app = QApplication.instance() or QApplication([])
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)

        # ---------------- A: Historie ueber drei Seiten -------------------
        store, controller = build(root, "a.sqlite3", 12)
        page = LogPage(controller, page_size=5)
        page.reload()
        pump(app)
        first = ids(page)
        page.load_more()
        pump(app)
        page.load_more()
        pump(app)
        shown = ids(page)
        print("A1 erste Seite      :", first)
        print("A2 nach drei Seiten :", shown)
        check(
            "A  Historie: streng absteigend ueber drei Seiten, keine Duplikate",
            strictly_descending(shown)
            and len(shown) == len(set(shown))
            and len(shown) == 12,
            f"{len(shown)} Zeilen, monoton={strictly_descending(shown)}, "
            f"eindeutig={len(shown) == len(set(shown))}",
        )
        check(
            "A' kein Rueckwaertssprung an einer Seitengrenze",
            shown[4] > shown[5] and shown[9] > shown[10],
            f"Grenze 1: {shown[4]} > {shown[5]}, Grenze 2: {shown[9]} > {shown[10]}",
        )
        page.stop()
        controller.shutdown()
        store.close()

        # ---------------- A2: automatisches Nachladen --------------------
        store, controller = build(root, "a2.sqlite3", 12)
        page = LogPage(controller, page_size=5)
        page.reload()
        pump(app)
        bar = page.table.verticalScrollBar()
        bar.setMaximum(100)
        page._on_scrolled(bar.maximum())  # noqa: SLF001
        pump(app)
        shown = ids(page)
        print("A3 nach Auto-Nachladen am Listenende:", shown)
        check(
            "A2 automatisches Nachladen am Listenende haelt die Ordnung",
            strictly_descending(shown) and len(shown) == 10,
            f"{len(shown)} Zeilen, monoton={strictly_descending(shown)}",
        )
        page.stop()
        controller.shutdown()
        store.close()

        # ---------------- B: Live auf leerem Ergebnis --------------------
        store, controller = build(root, "b.sqlite3", 0)
        page = LogPage(controller, page_size=5)
        page.set_mode(MODE_LIVE)
        pump(app)
        empty_rows = page.model.rowCount()
        store.write_batch([rec(index) for index in range(5)])
        pump(app, 0.9)
        b1 = ids(page)
        pump(app, 0.9)
        b2 = ids(page)
        store.write_batch([rec(index) for index in range(5, 8)])
        pump(app, 0.9)
        b3 = ids(page)
        print("B0 Zeilen nach Live-Start auf leerem Store:", empty_rows)
        print("B1 nach erstem Tail     :", b1)
        print("B2 nach zweitem Tail    :", b2)
        print("B3 nach weiteren Records:", b3)
        check(
            "B  Live-Start auf leerem Ergebnis: aufsteigend, keine Duplikate",
            empty_rows == 0
            and b1 == ["r0000", "r0001", "r0002", "r0003", "r0004"]
            and b2 == b1,
            f"leer={empty_rows}, erster Tail={b1}, zweiter Tail unveraendert={b2 == b1}",
        )
        check(
            "B' weitere Tails setzen die Reihenfolge fort, ohne Duplikate",
            strictly_ascending(b3) and len(b3) == len(set(b3)) and len(b3) == 8,
            f"{len(b3)} Zeilen, monoton={strictly_ascending(b3)}, "
            f"eindeutig={len(b3) == len(set(b3))}",
        )
        live_cursor = page._live_cursor  # noqa: SLF001
        check(
            "B'' Cursor steht auf dem neuesten Record",
            live_cursor is not None and str(live_cursor).endswith(":8"),
            f"live_cursor={live_cursor}",
        )
        page.stop()
        controller.shutdown()
        store.close()

        # ---------------- C: Live auf befuelltem Store --------------------
        store, controller = build(root, "c.sqlite3", 3)
        page = LogPage(controller, page_size=5)
        page.set_mode(MODE_LIVE)
        pump(app)
        c1 = ids(page)
        store.write_batch([rec(7), rec(8)])
        pump(app, 0.9)
        c2 = ids(page)
        print("C1 nach Umschalten auf Live:", c1)
        print("C2 nach Tail               :", c2)
        check(
            "C  Live auf befuelltem Store (Gate-Gegenprobe) unveraendert korrekt",
            strictly_ascending(c2) and len(c2) == len(set(c2)) and len(c2) == 5,
            f"{c2}",
        )
        page.stop()
        controller.shutdown()
        store.close()

        # ---------------- D: Filterwechsel im Live-Modus -----------------
        store, controller = build(root, "d.sqlite3", 3)
        page = LogPage(controller, page_size=5)
        page.set_mode(MODE_LIVE)
        pump(app)
        page._on_filter_changed(QueryFilter(levels=("INFO",)))  # noqa: SLF001
        pump(app, 0.9)
        d1 = ids(page)
        store.write_batch([rec(9)])
        pump(app, 0.9)
        d2 = ids(page)
        print("D1 nach Filterwechsel   :", d1)
        print("D2 nach weiterem Record :", d2)
        check(
            "D  Filterwechsel im Live-Modus: kein Duplikat, Reihenfolge haelt",
            strictly_ascending(d2) and len(d2) == len(set(d2)) and len(d2) == 4,
            f"{d2}",
        )
        page.stop()
        controller.shutdown()
        store.close()

    failed = [name for name, ok, _ in RESULTS if not ok]
    print()
    print(f"{len(RESULTS) - len(failed)}/{len(RESULTS)} Pruefungen bestanden.")
    if failed:
        print("FEHLGESCHLAGEN: " + ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
