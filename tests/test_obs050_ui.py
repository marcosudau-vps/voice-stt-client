"""
OBS-050 — offscreen Qt tests for the log view, the sixth settings tab and
their wiring into ``DesktopApplication``.

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §9.1 (own non-modal window,
sixth tab, status line), §9.2 (debounced filter signal, own executor, live
tail over the same provider interface), §9.3 (seven columns, keyset paging,
two modes without mixing, auto-scroll, detail with lazily loaded raw, context
actions, level colours, ``hide()`` instead of ``close()``), §5.8/FD-S4
("Diagnosehistorie löschen" at the store) and O-01 (the UI is a consumer,
never logging infrastructure).
"""

from __future__ import annotations

import gc
import os
import time
import unittest
from unittest.mock import patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QApplication, QCheckBox, QComboBox, QLineEdit, QMessageBox

from core.config import AppConfig, LedConfig
from core.observability.health import LoggingHealthState, LoggingInternalHealth
from core.observability.query.base import (
    LogRecordView,
    ProviderState,
    ProviderStatus,
    QueryFilter,
    QueryPage,
)
from ui.logs.log_detail_view import NO_SELECTION, RAW_PLACEHOLDER, LogDetailView
from ui.logs.log_filter_bar import ACTIVATION_HINT, LogFilterBar
from ui.logs.log_page import MODE_HISTORY, MODE_LIVE, LogPage
from ui.logs.log_query_controller import LogQueryController
from ui.logs.log_table_model import COLUMNS, LogTableModel
from ui.logs.log_window import GEOMETRY_KEY, LogWindow


def view(index: int = 0, **overrides) -> LogRecordView:
    values = dict(
        provider_id="local",
        record_id=f"r{index}",
        received_at=f"2026-08-17T10:00:{index:02d}.000Z",
        source_timestamp=None,
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="i-1",
        scope="instance",
        channel="system",
        level="INFO",
        type="client.app.started",
        component="ui.application",
        session_id=None,
        generation=None,
        activation_id=None,
        segment_id=None,
        transcription_id=None,
        command_id=None,
        event_id=None,
        correlation_id=None,
        server_cursor=None,
        replayed=False,
        message=f"Zeile {index}",
        details={},
        raw=None,
        cursor=f"id:{index}",
    )
    values.update(overrides)
    return LogRecordView(**values)


class FakeService:
    """A ``LogQueryService`` stand-in that answers from a list of records."""

    def __init__(self, records=(), provider_id="local"):
        self.records = list(records)
        self.provider_id = provider_id
        self.queries = []
        self.raw_calls = []
        self.raw = {"payload": True}

    def providers(self):
        return (
            ProviderStatus(self.provider_id, "Lokale Diagnosehistorie",
                           ProviderState.AVAILABLE, ""),
        )

    def query(self, provider_id, filter, cursor=None, limit=200):  # noqa: A002
        self.queries.append((provider_id, filter, cursor, limit))
        after = None
        if cursor is not None:
            after = int(str(cursor).split(":")[1])
        if filter.newest_first:
            ordered = sorted(self.records, key=lambda r: int(r.cursor.split(":")[1]),
                             reverse=True)
            if after is not None:
                ordered = [r for r in ordered if int(r.cursor.split(":")[1]) < after]
        else:
            ordered = sorted(self.records, key=lambda r: int(r.cursor.split(":")[1]))
            if after is not None:
                ordered = [r for r in ordered if int(r.cursor.split(":")[1]) > after]
        page_records = tuple(ordered[:limit])
        has_more = len(ordered) > limit
        return QueryPage(
            provider_id=provider_id,
            records=page_records,
            next_cursor=page_records[-1].cursor if (has_more and page_records) else None,
            complete=True,
            status=self.providers()[0],
        )

    def fetch_raw(self, provider_id, record_id):
        self.raw_calls.append((provider_id, record_id))
        return self.raw


class QtTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.application = QApplication.instance() or QApplication([])

    def tearDown(self) -> None:
        # Widgets created here have no parent, so their C++ side dies with
        # the Python object. Collecting at a deterministic point — after the
        # cleanups have stopped every timer and query thread — keeps that
        # destruction out of a later test's ``processEvents``.
        self.application.processEvents()
        gc.collect()
        self.application.processEvents()

    def pump(self, seconds: float = 0.35) -> None:
        """Give the query thread time to answer and Qt time to deliver the
        queued signal. The executor is real; this is what makes these tests
        exercise the actual cross-thread path of §9.2."""
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            self.application.processEvents()
            time.sleep(0.01)
        self.application.processEvents()


class TestLogTableModel(QtTestCase):
    def test_seven_frozen_columns_in_the_frozen_order(self):
        """§9.3: Zeit, Quelle, Channel, Level, Typ, Component, Meldung."""
        self.assertEqual(
            COLUMNS,
            ("Zeit", "Quelle", "Channel", "Level", "Typ", "Component", "Meldung"),
        )
        model = LogTableModel()
        self.assertEqual(model.columnCount(), 7)

    def test_ids_are_not_columns(self):
        """§9.3: *"Session/Activation/Segment nur im Detail und als Filter"*."""
        for forbidden in ("Session", "Activation", "Segment", "Korrelation"):
            self.assertNotIn(forbidden, COLUMNS)

    def test_cells_render_the_record(self):
        model = LogTableModel()
        model.append_page([view(1, message="hallo")])
        index = model.index(0, 6)
        self.assertEqual(model.data(index, Qt.ItemDataRole.DisplayRole), "hallo")
        self.assertEqual(
            model.data(model.index(0, 3), Qt.ItemDataRole.DisplayRole), "INFO"
        )

    def test_only_warning_and_above_get_a_row_colour(self):
        model = LogTableModel()
        model.append_page([view(1, level="INFO"), view(2, level="ERROR")])
        self.assertIsNone(model.data(model.index(0, 0), Qt.ItemDataRole.BackgroundRole))
        self.assertIsNotNone(
            model.data(model.index(1, 0), Qt.ItemDataRole.BackgroundRole)
        )

    def test_append_page_grows_and_record_at_returns_the_record(self):
        model = LogTableModel()
        model.append_page([view(1), view(2)])
        model.append_page([view(3)])
        self.assertEqual(model.rowCount(), 3)
        self.assertEqual(model.record_at(2).record_id, "r3")
        self.assertIsNone(model.record_at(99))

    def test_row_count_is_bounded_and_drops_the_oldest(self):
        """O-04: a live view must not grow without a bound."""
        model = LogTableModel(max_rows=5)
        model.append_page([view(index) for index in range(10)])
        self.assertEqual(model.rowCount(), 5)
        self.assertEqual(model.record_at(0).record_id, "r5")

    def test_clear_empties_the_model(self):
        model = LogTableModel()
        model.append_page([view(1)])
        model.clear()
        self.assertEqual(model.rowCount(), 0)


class TestLogFilterBar(QtTestCase):
    def test_default_filter_is_unrestricted(self):
        bar = LogFilterBar()
        current = bar.current_filter()
        self.assertEqual(current.channels, ())
        self.assertEqual(current.producer_kinds, ())
        self.assertIsNone(current.text)
        self.assertTrue(current.include_replayed)

    def test_minimum_level_expands_to_the_closed_set(self):
        bar = LogFilterBar()
        bar.level_box.setCurrentIndex(bar.level_box.findData("WARNING"))
        self.assertEqual(
            bar.current_filter().levels, ("WARNING", "ERROR", "CRITICAL")
        )

    def test_fields_map_onto_the_query_filter(self):
        bar = LogFilterBar()
        bar.producer_box.setCurrentIndex(bar.producer_box.findData("server"))
        bar.channel_box.setCurrentIndex(bar.channel_box.findData("audit"))
        bar.type_edit.setText("client.trigger")
        bar.text_edit.setText("suche")
        bar.session_edit.setText("s-1")
        bar.activation_edit.setText("a-1")
        bar.segment_edit.setText("4")
        bar.correlation_edit.setText("trigger:cmd-1")
        bar.replayed_box.setChecked(False)
        current = bar.current_filter()
        self.assertEqual(current.producer_kinds, ("server",))
        self.assertEqual(current.channels, ("audit",))
        self.assertEqual(current.type_prefix, "client.trigger")
        self.assertEqual(current.text, "suche")
        self.assertEqual(current.session_id, "s-1")
        self.assertEqual(current.activation_id, "a-1")
        self.assertEqual(current.segment_id, 4)
        self.assertEqual(current.correlation_id, "trigger:cmd-1")
        self.assertFalse(current.include_replayed)

    def test_a_half_typed_segment_id_does_not_restrict(self):
        bar = LogFilterBar()
        bar.segment_edit.setText("-")
        self.assertIsNone(bar.current_filter().segment_id)

    def test_filter_change_is_debounced(self):
        """§9.2: entprellt, 300 ms — typing must not fire one query per key."""
        bar = LogFilterBar()
        received = []
        bar.filter_changed.connect(received.append)
        for text in ("a", "ab", "abc"):
            bar.text_edit.setText(text)
        self.application.processEvents()
        self.assertEqual(received, [])
        deadline = time.monotonic() + 2.0
        while not received and time.monotonic() < deadline:
            self.application.processEvents()
            time.sleep(0.01)
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].text, "abc")

    def test_context_action_sets_one_field_and_emits_once(self):
        bar = LogFilterBar()
        received = []
        bar.filter_changed.connect(received.append)
        bar.apply_context(session_id="s-9", type_value="client.app.started")
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].session_id, "s-9")
        self.assertEqual(received[0].type_prefix, "client.app.started")

    def test_activation_filter_carries_the_unreliability_hint(self):
        """FD-C2 / ARCH §3.4: the hint is visible, not just documented."""
        bar = LogFilterBar()
        self.assertIn("unzuverlässig", bar.activation_hint.text())
        self.assertEqual(bar.activation_edit.toolTip(), ACTIVATION_HINT)

    def test_reset_clears_every_field(self):
        bar = LogFilterBar()
        bar.session_edit.setText("s-1")
        bar.reset()
        self.assertIsNone(bar.current_filter().session_id)


class TestLogDetailView(QtTestCase):
    def test_empty_view_says_so(self):
        detail = LogDetailView()
        self.assertEqual(detail.header.text(), NO_SELECTION)

    def test_details_are_shown_as_a_tree(self):
        detail = LogDetailView()
        detail.show_record(view(1, details={"a": {"b": 1}, "c": [1, 2]}))
        self.assertEqual(detail.details_tree.topLevelItemCount(), 2)

    def test_raw_arrives_separately_and_only_for_the_current_record(self):
        """§9.3: raw is loaded on selection; a late answer for a record that
        is no longer selected must be ignored."""
        detail = LogDetailView()
        detail.show_record(view(1))
        detail.set_raw("r999", {"stale": True})
        self.assertNotIn("stale", detail.raw_view.toPlainText())
        detail.set_raw("r1", {"event": "x"})
        self.assertIn('"event": "x"', detail.raw_view.toPlainText())

    def test_missing_raw_is_stated_not_left_blank(self):
        detail = LogDetailView()
        detail.show_record(view(1))
        detail.set_raw("r1", None)
        self.assertEqual(detail.raw_view.toPlainText(), RAW_PLACEHOLDER)

    def test_header_carries_the_ids_that_are_not_columns(self):
        detail = LogDetailView()
        detail.show_record(view(1, session_id="s-1", activation_id="a-1", segment_id=2))
        text = detail.header.text()
        for expected in ("s-1", "a-1", "session=", "activation=", "segment="):
            self.assertIn(expected, text)


class TestLogQueryController(QtTestCase):
    def test_query_runs_off_the_qt_thread_and_answers_by_signal(self):
        service = FakeService([view(index) for index in range(3)])
        controller = LogQueryController(service)
        self.addCleanup(controller.shutdown)
        received = []
        controller.page_ready.connect(lambda rid, page: received.append((rid, page)))
        request_id = controller.request_page("local", QueryFilter(), limit=10)
        self.pump()
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0][0], request_id)
        self.assertEqual(len(received[0][1].records), 3)

    def test_request_ids_increase_so_stale_answers_are_recognisable(self):
        service = FakeService()
        controller = LogQueryController(service)
        self.addCleanup(controller.shutdown)
        first = controller.request_page("local", QueryFilter())
        second = controller.request_page("local", QueryFilter())
        self.assertLess(first, second)

    def test_raw_is_fetched_through_the_service(self):
        service = FakeService([view(1)])
        controller = LogQueryController(service)
        self.addCleanup(controller.shutdown)
        received = []
        controller.raw_ready.connect(
            lambda rid, record_id, raw: received.append((record_id, raw))
        )
        controller.request_raw("local", "r1")
        self.pump()
        self.assertEqual(received, [("r1", {"payload": True})])
        self.assertEqual(service.raw_calls, [("local", "r1")])

    def test_a_raising_service_never_reaches_the_qt_thread(self):
        class Exploding(FakeService):
            def query(self, *args, **kwargs):
                raise RuntimeError("boom")

        controller = LogQueryController(Exploding())
        self.addCleanup(controller.shutdown)
        received = []
        controller.page_ready.connect(lambda rid, page: received.append(page))
        controller.request_page("local", QueryFilter())
        self.pump()
        self.assertEqual(received, [])

    def test_after_shutdown_requests_are_refused(self):
        controller = LogQueryController(FakeService())
        controller.shutdown()
        self.assertEqual(controller.request_page("local", QueryFilter()), 0)
        self.assertEqual(controller.request_raw("local", "r1"), 0)
        controller.shutdown()  # idempotent

    def test_the_query_thread_is_not_the_qt_thread(self):
        """§9.2: the query has its own executor and does not run on
        ``CoreBridge`` or the Qt thread."""
        import threading

        qt_thread = threading.current_thread().name
        seen = []

        class ThreadNameService(FakeService):
            def query(self, *args, **kwargs):
                seen.append(threading.current_thread().name)
                return super().query(*args, **kwargs)

        controller = LogQueryController(ThreadNameService())
        self.addCleanup(controller.shutdown)
        controller.request_page("local", QueryFilter())
        self.pump()
        self.assertEqual(len(seen), 1)
        self.assertNotEqual(seen[0], qt_thread)
        self.assertIn("LogQuery", seen[0])


class TestLogPage(QtTestCase):
    def make_page(self, records=(), health=None):
        service = FakeService(records)
        controller = LogQueryController(service)
        self.addCleanup(controller.shutdown)
        page = LogPage(controller, health_provider=health, page_size=5)
        self.addCleanup(page.stop)
        return page, service

    def displayed(self, page):
        return [record.record_id for record in page.model.records()]

    def test_history_mode_shows_the_newest_page_first_newest_on_top(self):
        """§9.3 + gate finding B-1: the page is shown exactly as the provider
        returned it (``newest_first=True``), newest at the top."""
        page, _service = self.make_page([view(index) for index in range(12)])
        page.reload()
        self.pump()
        self.assertEqual(
            self.displayed(page), ["r11", "r10", "r9", "r8", "r7"]
        )

    def test_display_order_stays_monotone_across_three_history_pages(self):
        """**Regression for B-1.** The gate reproduced a visible time axis
        that jumped backwards at every page boundary::

            r7 … r11, r2 … r6

        Two further pages are loaded here and the COMPLETE displayed order is
        asserted — not just the row count and the fact that a cursor went
        along, which is what let B-1 through (W-1).
        """
        page, service = self.make_page([view(index) for index in range(12)])
        page.reload()
        self.pump()
        page.load_more()
        self.pump()
        page.load_more()
        self.pump()

        shown = self.displayed(page)
        self.assertEqual(
            shown,
            ["r11", "r10", "r9", "r8", "r7",
             "r6", "r5", "r4", "r3", "r2",
             "r1", "r0"],
        )
        # Monotone in the display direction, over every page boundary.
        order = [int(record_id[1:]) for record_id in shown]
        self.assertEqual(order, sorted(order, reverse=True))
        self.assertEqual(len(shown), len(set(shown)))
        # ... and the provider really was asked three times, with a cursor
        # from the second page on (keyset, not OFFSET).
        self.assertEqual(len(service.queries), 3)
        self.assertIsNone(service.queries[0][2])
        self.assertIsNotNone(service.queries[1][2])
        self.assertIsNotNone(service.queries[2][2])

    def test_automatic_load_at_the_list_end_keeps_the_order(self):
        """The same path without a button press: §9.3's *"automatisches
        Nachladen am Listenende"*. "Unten" is the older end, so the appended
        page continues the order instead of breaking it."""
        page, _service = self.make_page([view(index) for index in range(12)])
        page.reload()
        self.pump()
        bar = page.table.verticalScrollBar()
        bar.setMaximum(100)
        page._on_scrolled(bar.maximum())  # noqa: SLF001 - the auto-load edge
        self.pump()
        shown = self.displayed(page)
        self.assertEqual(shown[:6], ["r11", "r10", "r9", "r8", "r7", "r6"])
        order = [int(record_id[1:]) for record_id in shown]
        self.assertEqual(order, sorted(order, reverse=True))

    def test_load_more_pages_backwards_with_the_cursor(self):
        page, service = self.make_page([view(index) for index in range(12)])
        page.reload()
        self.pump()
        page.load_more()
        self.pump()
        self.assertEqual(page.model.rowCount(), 10)
        self.assertIsNotNone(service.queries[-1][2])  # a cursor was passed

    def test_load_more_does_nothing_without_a_next_page(self):
        page, service = self.make_page([view(1)])
        page.reload()
        self.pump()
        before = len(service.queries)
        page.load_more()
        self.pump()
        self.assertEqual(len(service.queries), before)

    def test_live_mode_tails_ascending_over_the_same_provider(self):
        """FD-S1: no ring buffer — the live path is a tailing QUERY."""
        page, service = self.make_page([view(index) for index in range(3)])
        page.set_mode(MODE_LIVE)
        self.pump()
        self.assertEqual(page.mode, MODE_LIVE)
        rows_before = page.model.rowCount()
        service.records.append(view(9, message="neu"))
        self.pump(0.6)
        self.assertGreater(page.model.rowCount(), rows_before)
        self.assertEqual(page.model.record_at(page.model.rowCount() - 1).message, "neu")
        ascending = [q for q in service.queries if not q[1].newest_first]
        self.assertTrue(ascending)
        self.assertTrue(all(q[2] is not None for q in ascending))

    # -- B-2: the live mode derives a response from its REQUEST ----------

    def test_live_start_on_an_empty_result_set_then_records_arrive(self):
        """**Regression for B-2.** The gate reproduced, on an empty store::

            r4, r3, r2, r1, r0, r1, r2, r3, r4

        — the first ascending tail was processed as a descending page
        (reversed), and ``_live_cursor`` was taken from its OLDEST row, so the
        next tail delivered the same records again.
        """
        page, service = self.make_page([])
        page.set_mode(MODE_LIVE)
        self.pump()
        self.assertEqual(page.model.rowCount(), 0)

        service.records.extend(view(index) for index in range(5))
        self.pump(0.8)
        after_first = self.displayed(page)
        self.assertEqual(after_first, ["r0", "r1", "r2", "r3", "r4"])

        # A second and a third tail must add nothing at all.
        self.pump(0.8)
        self.assertEqual(self.displayed(page), after_first)
        self.pump(0.8)
        self.assertEqual(self.displayed(page), after_first)
        self.assertEqual(len(self.displayed(page)), len(set(self.displayed(page))))
        # The cursor was carried forward from the NEWEST delivered record.
        self.assertEqual(page._live_cursor, "id:4")  # noqa: SLF001

    def test_further_records_after_an_empty_start_extend_the_tail(self):
        """Several consecutive tail answers: order kept, no duplicates, and
        the cursor keeps moving to the newest record."""
        page, service = self.make_page([])
        page.set_mode(MODE_LIVE)
        self.pump()
        service.records.extend(view(index) for index in range(3))
        self.pump(0.8)
        service.records.extend(view(index) for index in range(3, 6))
        self.pump(0.8)
        shown = self.displayed(page)
        self.assertEqual(shown, ["r0", "r1", "r2", "r3", "r4", "r5"])
        self.assertEqual(len(shown), len(set(shown)))
        self.assertEqual(page._live_cursor, "id:5")  # noqa: SLF001
        order = [int(record_id[1:]) for record_id in shown]
        self.assertEqual(order, sorted(order))

    def test_live_start_with_a_filter_that_matches_nothing_then_matches(self):
        """The same empty start, but reached through a filter rather than an
        empty store — the everyday case the gate named."""
        page, service = self.make_page([view(index) for index in range(3)])
        # A filter on which nothing matches (yet) is what the view sees as an
        # empty answer set — the store itself is not empty here.
        service.records.clear()
        page.set_mode(MODE_LIVE)
        self.pump()
        self.assertEqual(page.model.rowCount(), 0)
        service.records.extend(view(index) for index in range(2))
        self.pump(0.8)
        self.assertEqual(self.displayed(page), ["r0", "r1"])
        self.pump(0.8)
        self.assertEqual(self.displayed(page), ["r0", "r1"])

    def test_filter_change_during_live_reseeds_without_duplicates(self):
        """A filter change calls ``reload()`` and resets ``_live_cursor`` —
        the exact state that made the old code misread the next tail."""
        page, service = self.make_page([view(index) for index in range(3)])
        page.set_mode(MODE_LIVE)
        self.pump()
        self.assertEqual(self.displayed(page), ["r0", "r1", "r2"])

        page._on_filter_changed(QueryFilter(channels=("audit",)))  # noqa: SLF001
        self.pump(0.8)
        shown = self.displayed(page)
        self.assertEqual(shown, ["r0", "r1", "r2"])
        self.assertEqual(len(shown), len(set(shown)))

        service.records.append(view(7))
        self.pump(0.8)
        shown = self.displayed(page)
        self.assertEqual(shown, ["r0", "r1", "r2", "r7"])
        self.assertEqual(len(shown), len(set(shown)))

    def test_live_start_on_a_populated_store_stays_correct(self):
        """The happy path the gate confirmed as already correct (case C) must
        not regress: seed ascending, tail appended below."""
        page, service = self.make_page([view(index) for index in range(3)])
        page.set_mode(MODE_LIVE)
        self.pump()
        self.assertEqual(self.displayed(page), ["r0", "r1", "r2"])
        service.records.extend([view(7), view(8)])
        self.pump(0.8)
        self.assertEqual(self.displayed(page), ["r0", "r1", "r2", "r7", "r8"])

    def test_a_response_is_interpreted_by_its_request_not_by_the_cursor(self):
        """The structural half of the B-2 fix: the kind is recorded with the
        reserved request id and consumed when the answer arrives, so a
        repeated delivery cannot append the same page twice."""
        page, service = self.make_page([view(index) for index in range(3)])
        page.reload()
        self.pump()
        self.assertIsNone(page._active_kind)  # noqa: SLF001 - consumed
        before = self.displayed(page)
        stale = service.query("local", QueryFilter(), None, 5)
        page._on_page_ready(page._active_request, stale)  # noqa: SLF001
        self.assertEqual(self.displayed(page), before)

    def test_no_mixed_mode(self):
        """§9.3: Live and Historie are alternatives, never both at once."""
        page, _service = self.make_page([view(1)])
        self.assertEqual(page.mode, MODE_HISTORY)
        page.set_mode(MODE_LIVE)
        self.assertEqual(page.mode, MODE_LIVE)
        page.set_mode(MODE_HISTORY)
        self.assertEqual(page.mode, MODE_HISTORY)

    def test_filter_change_replaces_the_page_and_reaches_the_provider(self):
        page, service = self.make_page([view(index) for index in range(3)])
        page.reload()
        self.pump()
        page._on_filter_changed(QueryFilter(channels=("audit",)))  # noqa: SLF001
        self.pump()
        self.assertEqual(service.queries[-1][1].channels, ("audit",))

    def test_a_stale_answer_is_dropped(self):
        page, _service = self.make_page([view(1)])
        page.reload()
        self.pump()
        rows = page.model.rowCount()
        page._on_page_ready(  # noqa: SLF001
            999,
            QueryPage("local", (view(42),), None, True,
                      ProviderStatus("local", "local", ProviderState.AVAILABLE, "")),
        )
        self.assertEqual(page.model.rowCount(), rows)

    def test_selection_loads_the_detail_and_the_raw_payload(self):
        page, service = self.make_page([view(index) for index in range(3)])
        page.reload()
        self.pump()
        page.table.selectRow(0)
        self.pump()
        self.assertIsNotNone(page.detail.record)
        self.assertTrue(service.raw_calls)

    def test_scrolling_up_in_live_mode_turns_auto_scroll_off(self):
        page, _service = self.make_page([view(index) for index in range(3)])
        page.set_mode(MODE_LIVE)
        self.pump()
        self.assertTrue(page.autoscroll_box.isChecked())
        bar = page.table.verticalScrollBar()
        bar.setMaximum(100)
        page._on_scrolled(0)  # noqa: SLF001
        self.assertFalse(page.autoscroll_box.isChecked())

    def test_status_line_shows_provider_and_health(self):
        health = LoggingInternalHealth()
        health.record_written(3)
        health.set_state(LoggingHealthState.DEGRADED_STORE, "database is locked")
        page, _service = self.make_page([view(1)], health=lambda: health.snapshot())
        page.reload()
        self.pump()
        text = page.status_label.text()
        self.assertIn("degraded_store", text)
        self.assertIn("geschrieben 3", text)
        self.assertIn("database is locked", text)

    def test_a_raising_health_provider_does_not_break_the_status_line(self):
        def boom():
            raise RuntimeError("health exploded")

        page, _service = self.make_page([view(1)], health=boom)
        page.refresh_status()
        self.assertIn("Zeilen", page.status_label.text())

    def test_context_menu_actions_set_the_filter(self):
        page, _service = self.make_page([view(1, session_id="s-1")])
        page.filter_bar.apply_context(session_id="s-1")
        self.assertEqual(page.filter_bar.current_filter().session_id, "s-1")

    def test_stop_halts_both_timers(self):
        page, service = self.make_page([view(1)])
        page.set_mode(MODE_LIVE)
        self.pump()
        page.stop()
        before = len(service.queries)
        self.pump(0.6)
        self.assertEqual(len(service.queries), before)


class TestLogWindow(QtTestCase):
    def make_window(self, records=()):
        settings = QSettings("RealtimeSTT-Test", f"obs050-{time.monotonic_ns()}")
        window = LogWindow(FakeService(records), settings=settings)
        self.addCleanup(window.shutdown)
        self.addCleanup(settings.clear)
        return window, settings

    def test_window_is_non_modal_and_top_level(self):
        window, _settings = self.make_window()
        self.assertFalse(window.isModal())
        self.assertIsNone(window.parent())

    def test_closing_hides_instead_of_closing(self):
        """§9.3: ``hide()`` statt ``close()``."""
        window, _settings = self.make_window([view(1)])
        window.show()
        self.pump(0.1)
        window.close()
        self.application.processEvents()
        self.assertFalse(window.isVisible())
        window.show()
        self.pump(0.1)
        self.assertTrue(window.isVisible())

    def test_geometry_is_stored_in_qsettings(self):
        window, settings = self.make_window()
        window.resize(900, 600)
        window.close()
        self.assertIsNotNone(settings.value(GEOMETRY_KEY))

    def test_hiding_stops_the_polling(self):
        """§9.1's second reason for a separate window: a hidden view must not
        keep querying."""
        window, _settings = self.make_window([view(1)])
        window.show()
        self.pump(0.2)
        window.page.set_mode(MODE_LIVE)
        self.pump(0.2)
        window.hide()
        self.application.processEvents()
        before = len(window.page._controller.service.queries)  # noqa: SLF001
        self.pump(0.6)
        self.assertEqual(len(window.page._controller.service.queries), before)  # noqa: SLF001


class TestSettingsTab(QtTestCase):
    def make_dialog(self):
        from ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(AppConfig(), lambda candidate, policies: True)
        self.addCleanup(dialog.close)
        return dialog

    def test_the_dialog_has_six_tabs_with_logging_last(self):
        dialog = self.make_dialog()
        self.assertEqual(dialog.tabs.count(), 6)
        self.assertEqual(dialog.tabs.tabText(5), "Logging & Diagnose")

    def test_every_logging_setting_has_an_editor(self):
        from core.logging_settings_metadata import LOGGING_SETTING_DEFINITIONS

        dialog = self.make_dialog()
        for definition in LOGGING_SETTING_DEFINITIONS:
            with self.subTest(path=definition.path):
                self.assertIn(definition.path, dialog._editors)  # noqa: SLF001

    def test_both_action_buttons_exist(self):
        dialog = self.make_dialog()
        self.assertTrue(dialog.show_logs_button.isEnabled())
        self.assertTrue(dialog.clear_logs_button.isEnabled())

    def test_show_logs_button_emits_the_request(self):
        dialog = self.make_dialog()
        received = []
        dialog.logging_view_requested.connect(lambda: received.append(True))
        dialog.show_logs_button.click()
        self.assertEqual(received, [True])

    def test_clear_button_asks_before_deleting(self):
        dialog = self.make_dialog()
        received = []
        dialog.logging_clear_requested.connect(lambda: received.append(True))
        with patch.object(
            QMessageBox, "warning", return_value=QMessageBox.StandardButton.Cancel
        ):
            dialog.clear_logs_button.click()
        self.assertEqual(received, [])
        with patch.object(
            QMessageBox, "warning", return_value=QMessageBox.StandardButton.Yes
        ):
            dialog.clear_logs_button.click()
        self.assertEqual(received, [True])

    def test_clearing_the_file_sink_directory_means_the_default_again(self):
        """An emptied optional path must become ``None``, not ``""`` — the
        empty string fails P-8 validation."""
        config = AppConfig()
        config.logging.observability.file_sink_dir = str(
            os.path.join(os.path.expanduser("~"), "logs")
        )
        from ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(config, lambda candidate, policies: True)
        self.addCleanup(dialog.close)
        editor = dialog._editors["logging.observability.file_sink_dir"]  # noqa: SLF001
        self.assertIsInstance(editor, QLineEdit)
        editor.setText("")
        value = dialog._editor_value(  # noqa: SLF001
            dialog._definitions["logging.observability.file_sink_dir"]  # noqa: SLF001
        )
        self.assertIsNone(value)

    def test_changing_a_logging_setting_produces_an_immediate_policy(self):
        from core.settings_metadata import ApplyPolicy

        seen = []
        from ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(
            AppConfig(),
            lambda candidate, policies: (seen.append((candidate, policies)), True)[1],
        )
        self.addCleanup(dialog.close)
        editor = dialog._editors["logging.observability.retention_days"]  # noqa: SLF001
        editor.setValue(3)
        dialog.apply_changes()
        self.assertEqual(len(seen), 1)
        candidate, policies = seen[0]
        self.assertEqual(candidate.logging.observability.retention_days, 3)
        self.assertEqual(policies, frozenset({ApplyPolicy.IMMEDIATE}))

    def test_store_enabled_change_reports_app_restart(self):
        from core.settings_metadata import ApplyPolicy

        seen = []
        from ui.settings_dialog import SettingsDialog

        dialog = SettingsDialog(
            AppConfig(),
            lambda candidate, policies: (seen.append(policies), True)[1],
        )
        self.addCleanup(dialog.close)
        editor = dialog._editors["logging.observability.store_enabled"]  # noqa: SLF001
        self.assertIsInstance(editor, QCheckBox)
        editor.setChecked(False)
        dialog.apply_changes()
        self.assertIn(ApplyPolicy.APP_RESTART, seen[0])

    def test_level_editor_offers_the_closed_level_set(self):
        dialog = self.make_dialog()
        editor = dialog._editors["logging.observability.level"]  # noqa: SLF001
        self.assertIsInstance(editor, QComboBox)
        values = [editor.itemData(index) for index in range(editor.count())]
        self.assertEqual(
            values, ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        )


class FakeManager:
    """Only what the UI is allowed to know about the manager."""

    def __init__(self, service=None, clear_result=7, clear_raises=False):
        self.query_service = service or FakeService([view(1)])
        self.clear_calls = 0
        self._clear_result = clear_result
        self._clear_raises = clear_raises
        self.health = LoggingInternalHealth()

    def health_snapshot(self):
        return self.health.snapshot()

    def clear_history(self, timeout=5.0):
        self.clear_calls += 1
        if self._clear_raises:
            raise TimeoutError("clear did not complete in time")
        return self._clear_result


class TestDesktopWiring(QtTestCase):
    def make_desktop(self, manager=None):
        from tests.test_ui_application import FakeBridge, FakeGuard, FakeHotkeyBackend
        from ui.application import DesktopApplication

        class DialogCapableBridge(FakeBridge):
            """The settings dialog wires two history commands the AP06 double
            does not carry; the log view needs the dialog to exist."""

            def delete_history_entry(self, entry_id):
                self.calls.append(("delete_history_entry", entry_id))
                return True

            def clear_history(self):
                self.calls.append("clear_history")
                return True

        config = AppConfig()
        config.led = LedConfig(enabled=False)
        desktop = DesktopApplication(
            self.application,
            config,
            FakeGuard(),
            bridge=DialogCapableBridge(),
            hotkey_backend=FakeHotkeyBackend(),
            observability_manager=manager,
        )
        self.addCleanup(desktop.shutdown)
        return desktop

    def test_without_a_manager_the_tray_entry_is_disabled(self):
        desktop = self.make_desktop(manager=None)
        self.assertFalse(desktop.tray.logs_action.isEnabled())
        desktop.show_logs()  # must not raise
        self.assertIsNone(desktop.log_window)

    def test_with_a_manager_the_tray_opens_the_log_window(self):
        desktop = self.make_desktop(manager=FakeManager())
        self.assertTrue(desktop.tray.logs_action.isEnabled())
        desktop.tray.logs_action.trigger()
        self.pump(0.2)
        self.assertIsNotNone(desktop.log_window)
        self.assertTrue(desktop.log_window.isVisible())

    def test_the_window_is_created_once_and_reused(self):
        desktop = self.make_desktop(manager=FakeManager())
        desktop.show_logs()
        first = desktop.log_window
        desktop.show_logs()
        self.assertIs(desktop.log_window, first)

    def test_clear_goes_through_the_manager_not_the_query_layer(self):
        """FD-S4 / §5.8 / O-14: the deletion happens at the store."""
        manager = FakeManager(clear_result=12)
        desktop = self.make_desktop(manager=manager)
        desktop.show_settings()
        desktop.clear_diagnostics_history()
        self.assertEqual(manager.clear_calls, 1)
        self.assertIn("12", desktop.settings_dialog.logging_status.text())

    def test_a_failing_clear_is_reported_not_raised(self):
        manager = FakeManager(clear_raises=True)
        desktop = self.make_desktop(manager=manager)
        desktop.show_settings()
        desktop.clear_diagnostics_history()
        self.assertIn("fehlgeschlagen", desktop.settings_dialog.logging_status.text())

    def test_clear_without_a_manager_says_so(self):
        desktop = self.make_desktop(manager=None)
        desktop.show_settings()
        desktop.clear_diagnostics_history()
        self.assertIn("Keine Diagnosequelle", desktop.settings_dialog.logging_status.text())

    def test_shutdown_releases_the_log_window(self):
        desktop = self.make_desktop(manager=FakeManager())
        desktop.show_logs()
        window = desktop.log_window
        desktop.shutdown()
        self.assertFalse(window.isVisible())
        self.assertEqual(window.controller.request_page("local", QueryFilter()), 0)

    def test_desktop_application_never_stops_the_manager(self):
        """ARCH §6.2(b)/FD-R4: the manager's lifetime stays in app.py."""
        manager = FakeManager()
        manager.stop_calls = 0

        def stop(timeout=2.0):
            manager.stop_calls += 1

        manager.stop = stop
        desktop = self.make_desktop(manager=manager)
        desktop.start()
        desktop.shutdown()
        self.assertEqual(manager.stop_calls, 0)


if __name__ == "__main__":
    unittest.main()
