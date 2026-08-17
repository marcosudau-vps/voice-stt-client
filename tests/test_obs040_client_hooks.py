"""
OBS-040 — the V1 client observation hooks of ``LOGGING_CONTRACTS_FREEZE_V1.md``
§12, and their correlation fields.

Frozen sources: §12.1 (lifecycle/transport, channel ``system``), §12.2
(intentional actions, channel ``audit``), §12.3 (transcript, channel
``transcription``), §12.4 (numbers, channel ``performance``), §12.5 (feedback
and output, channel ``system``), §12.6 (implementation order by ascending
risk), §12.7 (what is deliberately NOT instrumented), §2.2 (channel
definitions), §1.1 (which field carries which id);
``LOGGING_ARCHITEKTUR_FREEZE_V1.md`` §8.6 (hot-path rules), O-01/O-05
(a logging failure never reaches the client function).
"""

from __future__ import annotations

import asyncio
import logging
import unittest
from unittest.mock import patch

from core.config import AppConfig
from core.controller import (
    DictationState,
    FinalProcessingResult,
    FinalProcessingStatus,
    STTController,
    TransientEventType,
)
from core.observability.adapters.client_events import ClientEventEmitter
from core.observability.ingress import NULL_INGRESS, ObservabilityIngress
from core.stt_session import STTSession, TransportState
from tests.test_controller import (
    FakeAudioCapture,
    FakeInjectionQueue,
    FakeSessionCoordinator,
    FakeSTTSession,
)
from core.history import TranscriptHistoryManager


def build_ingress(**changes) -> ObservabilityIngress:
    values = {"instance_id": "client-instance-1", "queue_size": 4096, "level": "DEBUG"}
    values.update(changes)
    return ObservabilityIngress(**values)


def records_of(ingress: ObservabilityIngress, type_: str) -> list:
    return [record for record in ingress.drain(4096, 0.0) if record.type == type_]


def _sources(ingress: ObservabilityIngress) -> list:
    """The registered aggregate sources, as ``(type, component, callable)``."""
    with ingress._aggregate_lock:
        return [
            (type_, component, source)
            for type_, (component, source) in ingress._aggregate_sources.items()
        ]


def all_records(ingress: ObservabilityIngress) -> dict:
    grouped: dict = {}
    for record in ingress.drain(4096, 0.0):
        grouped.setdefault(record.type, []).append(record)
    return grouped


# ---------------------------------------------------------------------------
# The emitter itself: the boundary every hook goes through.
# ---------------------------------------------------------------------------


class TestClientEventEmitter(unittest.TestCase):
    def test_a_throwing_ingress_never_reaches_the_call_site(self):
        """O-05: *"Logging-Ausfall beeinflusst die eigentliche Clientfunktion
        nicht."* The emitter is the single guard that makes that true for ANY
        ingress implementation, not just the concrete one."""

        class Exploding:
            def event(self, *args, **kwargs):
                raise RuntimeError("ingress exploded")

        emitter = ClientEventEmitter(Exploding(), component="unit")
        # No assertRaises: nothing may escape.
        self.assertIsNone(emitter.system("client.test"))

    def test_cancellation_still_propagates(self):
        class Cancelling:
            def event(self, *args, **kwargs):
                raise asyncio.CancelledError()

        emitter = ClientEventEmitter(Cancelling())
        with self.assertRaises(asyncio.CancelledError):
            emitter.audit("client.test")

    def test_the_component_default_is_applied_and_overridable(self):
        ingress = build_ingress()
        emitter = ClientEventEmitter(ingress, component="default-component")
        emitter.system("client.a")
        emitter.system("client.b", component="explicit")
        records = {record.type: record for record in ingress.drain(10, 0.0)}
        self.assertEqual(records["client.a"].component, "default-component")
        self.assertEqual(records["client.b"].component, "explicit")

    def test_each_wrapper_sets_its_own_channel(self):
        ingress = build_ingress()
        emitter = ClientEventEmitter(ingress)
        emitter.system("client.s")
        emitter.audit("client.a")
        emitter.transcription("client.t")
        emitter.performance("client.p")
        channels = {
            record.type: record.channel for record in ingress.drain(10, 0.0)
        }
        self.assertEqual(
            channels,
            {
                "client.s": "system",
                "client.a": "audit",
                "client.t": "transcription",
                "client.p": "performance",
            },
        )

    def test_null_ingress_produces_nothing_and_raises_nothing(self):
        emitter = ClientEventEmitter(NULL_INGRESS)
        emitter.audit("client.hotkey.pressed")
        self.assertEqual(NULL_INGRESS.drain(10, 0.0), [])


# ---------------------------------------------------------------------------
# §12.1 / §12.2: core/stt_session.py
# ---------------------------------------------------------------------------


class TestSessionHooks(unittest.IsolatedAsyncioTestCase):
    def build(self):
        ingress = build_ingress()
        config = AppConfig()
        session = STTSession(config.server, config.session, observability=ingress)
        return ingress, session

    def test_transport_transitions_produce_connecting_and_connected(self):
        ingress, session = self.build()
        session._update_transport(TransportState.CONNECTING)
        session._state.session_id = "session-9"
        session._fire_transport_change(TransportState.ADMITTED)

        grouped = all_records(ingress)
        self.assertEqual(len(grouped["client.websocket.connecting"]), 1)
        self.assertEqual(len(grouped["client.websocket.connected"]), 1)
        self.assertEqual(
            grouped["client.websocket.connected"][0].session_id, "session-9"
        )
        self.assertEqual(grouped["client.websocket.connecting"][0].channel, "system")

    def test_every_failed_connection_produces_one_disconnected_record(self):
        """Two failures in a row must produce two records -- the transport
        state does not change again, which is exactly why the hook sits on
        ``_record_failure`` and not on the state transition."""
        ingress, session = self.build()
        session._record_failure("network_timeout")
        session._record_failure("network_unavailable")

        records = records_of(ingress, "client.websocket.disconnected")
        self.assertEqual(len(records), 2)
        self.assertEqual(
            [dict(record.details)["reason"] for record in records],
            ["network_timeout", "network_unavailable"],
        )
        self.assertEqual([dict(r.details)["attempt"] for r in records], [1, 2])
        self.assertEqual({record.level for record in records}, {"WARNING"})

    def test_server_busy_is_visible_in_the_disconnect_record(self):
        ingress, session = self.build()
        session._record_failure("server_busy", server_busy=True)
        [record] = records_of(ingress, "client.websocket.disconnected")
        self.assertTrue(dict(record.details)["server_busy"])

    async def test_trigger_send_and_ack_share_one_command_id(self):
        """§12.2 / §1.1: ``command_id`` is the correlation key between send and
        ack, and ``correlation_id`` carries it namespaced as
        ``trigger:<commandId>``."""
        ingress, session = self.build()
        sent = []

        async def fake_send_json(payload):
            sent.append(payload)

        session._send_json = fake_send_json
        session._ws_is_open = lambda: True
        session._state.session_id = "session-1"

        command_id = await session.send_trigger("activate", "manual")
        session._apply_event(
            {
                "type": "trigger_ack",
                "commandId": command_id,
                "accepted": True,
                "reason": "",
                "activationId": "act-1",
                "sessionId": "session-1",
            }
        )

        grouped = all_records(ingress)
        [sent_record] = grouped["client.trigger.sent"]
        [ack_record] = grouped["client.trigger.ack_received"]
        self.assertEqual(sent_record.command_id, command_id)
        self.assertEqual(ack_record.command_id, command_id)
        self.assertEqual(sent_record.correlation_id, f"trigger:{command_id}")
        self.assertEqual(ack_record.correlation_id, f"trigger:{command_id}")
        self.assertEqual(sent_record.channel, "audit")
        self.assertEqual(ack_record.channel, "audit")
        self.assertTrue(dict(ack_record.details)["accepted"])
        # §3.4: activation_id is taken over as diagnostic information.
        self.assertEqual(ack_record.activation_id, "act-1")

    async def test_a_repeated_ack_is_recorded_as_dropped_not_as_received(self):
        ingress, session = self.build()

        async def fake_send_json(payload):
            return None

        session._send_json = fake_send_json
        session._ws_is_open = lambda: True
        command_id = await session.send_trigger("activate", "manual")
        ack = {
            "type": "trigger_ack",
            "commandId": command_id,
            "accepted": True,
            "reason": "",
        }
        session._apply_event(dict(ack))
        session._apply_event(dict(ack))

        grouped = all_records(ingress)
        self.assertEqual(len(grouped["client.trigger.ack_received"]), 1)
        [dropped] = grouped["client.trigger.ack_dropped"]
        self.assertEqual(
            dict(dropped.details)["reason"], "unknown_or_answered"
        )
        self.assertEqual(dropped.command_id, command_id)
        self.assertEqual(dropped.level, "WARNING")

    async def test_an_ack_without_a_command_id_is_dropped_and_correlation_stays_empty(self):
        ingress, session = self.build()
        session._apply_event({"type": "trigger_ack", "accepted": True})
        [dropped] = records_of(ingress, "client.trigger.ack_dropped")
        self.assertEqual(dict(dropped.details)["reason"], "missing_command_id")
        self.assertIsNone(dropped.command_id)
        self.assertIsNone(dropped.correlation_id)

    async def test_stream_start_sent_is_recorded_after_the_send(self):
        ingress, session = self.build()
        session._ws_is_open = lambda: True
        session._state.transport = TransportState.READY
        session._state.ready_ok = True
        sent = []

        async def fake_send_json(payload):
            sent.append(payload)

        session._send_json = fake_send_json
        await session.send_start()

        self.assertEqual(sent, [{"type": "start"}])
        [record] = records_of(ingress, "client.stream.start_sent")
        self.assertEqual(record.channel, "audit")

    async def test_a_failed_send_produces_no_start_record(self):
        ingress, session = self.build()
        session._ws_is_open = lambda: True
        session._state.transport = TransportState.READY
        session._state.ready_ok = True

        async def failing_send(payload):
            raise ConnectionError("closed")

        session._send_json = failing_send
        with self.assertRaises(ConnectionError):
            await session.send_start()
        self.assertEqual(records_of(ingress, "client.stream.start_sent"), [])

    def test_reconnect_scheduled_carries_the_computed_delay(self):
        ingress, session = self.build()
        session._record_failure("network_unavailable")
        ingress.drain(100, 0.0)

        # Reproduce exactly what ``run()`` does around the backoff sleep.
        delay = session._backoff_delay()
        session._observe.system(
            "client.reconnect.scheduled",
            details={
                "delay_s": round(delay, 3),
                "attempt": session._backoff_attempt,
                "reason": session._last_failure_reason,
                "server_busy": False,
            },
            generation=session._generation,
        )
        [record] = records_of(ingress, "client.reconnect.scheduled")
        details = dict(record.details)
        self.assertGreater(details["delay_s"], 0.0)
        self.assertEqual(details["attempt"], 1)
        self.assertEqual(details["reason"], "network_unavailable")

    def test_session_admitted_reports_the_effective_handshake_contract(self):
        ingress, session = self.build()
        session._state.session_id = "session-2"
        session._effective_session_config = {
            "effectiveWakeWordEnabled": False,
            "warnings": ["deprecated_field"],
            "fallbacks": [],
            "ignoredFields": ["foo"],
        }
        session._observe.system(
            "client.session.admitted",
            details={
                "warnings": ["deprecated_field"],
                "fallbacks": [],
                "ignored_fields": ["foo"],
                "effective_wake_word_enabled": False,
                "supports_activation_triggers": False,
            },
            session_id="session-2",
            generation=1,
        )
        [record] = records_of(ingress, "client.session.admitted")
        details = dict(record.details)
        self.assertEqual(list(details["warnings"]), ["deprecated_field"])
        self.assertEqual(list(details["ignored_fields"]), ["foo"])
        self.assertEqual(record.session_id, "session-2")

    def test_no_session_hook_leaks_the_access_token(self):
        ingress, session = self.build()
        session._record_failure("network_unavailable")
        session._update_transport(TransportState.CONNECTING)
        for record in ingress.drain(100, 0.0):
            self.assertNotIn("accessToken", repr(dict(record.details)))
            self.assertNotIn("token", repr(dict(record.details)).lower())


# ---------------------------------------------------------------------------
# §12.1 - §12.5: core/controller.py
# ---------------------------------------------------------------------------


class TestControllerHooks(unittest.IsolatedAsyncioTestCase):
    def build(self):
        ingress = build_ingress()
        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=FakeSTTSession(),
            audio=FakeAudioCapture(),
            history_manager=TranscriptHistoryManager(config.history),
            injection_queue=FakeInjectionQueue(),
            session_coordinator=FakeSessionCoordinator(),
            observability=ingress,
        )
        return ingress, controller

    def test_the_controller_stores_the_ingress_under_the_frozen_name(self):
        """CONTRACTS §6 spells out ``self.observability = observability``."""
        ingress, controller = self.build()
        self.assertIs(controller.observability, ingress)

    def test_a_default_controller_observes_nothing(self):
        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=FakeSTTSession(),
            audio=FakeAudioCapture(),
            history_manager=TranscriptHistoryManager(config.history),
            injection_queue=FakeInjectionQueue(),
            session_coordinator=FakeSessionCoordinator(),
        )
        self.assertIs(controller.observability, NULL_INGRESS)

    def test_the_fan_out_hook_is_installed_on_the_coordinator(self):
        ingress, controller = self.build()
        self.assertIs(
            controller.session_coordinator.on_observation,
            controller.server_live_adapter,
        )
        self.assertIs(controller.server_live_adapter.ingress, ingress)
        # The feedback branch is untouched and independent (O-02).
        self.assertEqual(
            controller.session_coordinator.on_event,
            controller._handle_event_stream_event,
        )

    def test_action_blocked_is_an_audit_record(self):
        ingress, controller = self.build()
        controller._emit_feedback_event(
            TransientEventType.ACTION_BLOCKED,
            reason="transport_not_ready",
            description="Transport not ready",
            action="start_dictation",
        )
        [record] = records_of(ingress, "client.action.blocked")
        self.assertEqual(record.channel, "audit")
        self.assertEqual(record.level, "WARNING")
        details = dict(record.details)
        self.assertEqual(details["reason"], "transport_not_ready")
        self.assertEqual(details["action"], "start_dictation")
        self.assertTrue(record.correlation_id.startswith("client:"))

    def test_dictation_failed_and_interrupted_use_their_own_types(self):
        ingress, controller = self.build()
        controller._emit_feedback_event(
            TransientEventType.DICTATION_START_FAILED, "audio_start_failed", "x"
        )
        controller._emit_feedback_event(
            TransientEventType.DICTATION_INTERRUPTED, "transport_loss", "y"
        )
        grouped = all_records(ingress)
        self.assertEqual(len(grouped["client.dictation.failed"]), 1)
        self.assertEqual(len(grouped["client.dictation.interrupted"]), 1)

    def test_error_classification_is_recorded_with_its_count(self):
        ingress, controller = self.build()
        for _ in range(3):
            controller._handle_error_event(
                {"type": "error", "where": "audio_packet", "message": "bad packet"}
            )
        records = records_of(ingress, "client.server.error_classified")
        self.assertEqual(len(records), 3)
        self.assertEqual(
            [dict(record.details)["count"] for record in records], [1, 2, 3]
        )
        self.assertEqual({record.level for record in records}, {"ERROR"})
        self.assertEqual({record.channel for record in records}, {"system"})
        self.assertEqual(
            {dict(record.details)["where"] for record in records}, {"audio_packet"}
        )

    def test_final_deduplication_records_the_length_but_never_the_text(self):
        """§12.3: *"redaktionspflichtig, loggt heute beide vollstaendigen Texte
        auf WARNING"*. No text at all reaches the record."""
        ingress, controller = self.build()
        secret = "der geheime Transkriptinhalt"
        controller._emit_final_result(
            FinalProcessingResult(
                status=FinalProcessingStatus.DEDUPLICATED,
                session_id="session-1",
                segment_id=4,
                text=secret,
                reason="duplicate",
                is_conflict=True,
            )
        )
        [record] = records_of(ingress, "client.final.deduplicated")
        self.assertEqual(record.channel, "transcription")
        self.assertEqual(record.level, "WARNING")
        details = dict(record.details)
        self.assertEqual(details["text_length"], len(secret))
        self.assertTrue(details["conflict"])
        self.assertNotIn("geheime", repr(details))
        self.assertNotIn("geheime", repr(record.message))
        self.assertEqual(record.segment_id, 4)

    def test_injection_enqueued_and_rejected(self):
        ingress, controller = self.build()
        controller._emit_final_result(
            FinalProcessingResult(
                status=FinalProcessingStatus.QUEUED,
                session_id="session-1",
                segment_id=1,
                text="hello",
                entry_id="entry-1",
            )
        )
        controller._emit_final_result(
            FinalProcessingResult(
                status=FinalProcessingStatus.QUEUE_UNAVAILABLE,
                session_id="session-1",
                segment_id=2,
                text="hello",
                entry_id="entry-2",
                reason="queue_unavailable",
            )
        )
        grouped = all_records(ingress)
        [enqueued] = grouped["client.injection.enqueued"]
        [rejected] = grouped["client.injection.rejected"]
        self.assertEqual(enqueued.correlation_id, "injection:entry-1")
        self.assertEqual(rejected.correlation_id, "injection:entry-2")
        self.assertEqual(rejected.level, "WARNING")
        self.assertEqual(enqueued.channel, "transcription")

    async def test_runtime_apply_carries_the_three_flags_and_the_correlation(self):
        """§10.4: a pure observability change must set none of
        session_changed/audio_changed/mode_changed. The record makes that rule
        checkable from the stored history."""
        ingress, controller = self.build()
        candidate = AppConfig()
        candidate.history.persistent.enabled = False
        result = await controller.apply_runtime_config(
            candidate, correlation_id="settings:abc123"
        )
        self.assertTrue(result.success)
        [record] = records_of(ingress, "client.settings.runtime_apply")
        details = dict(record.details)
        self.assertFalse(details["session_changed"])
        self.assertFalse(details["audio_changed"])
        self.assertFalse(details["mode_changed"])
        self.assertEqual(record.correlation_id, "settings:abc123")
        self.assertEqual(record.channel, "audit")

    async def test_an_invalid_candidate_produces_a_validation_failed_record(self):
        ingress, controller = self.build()

        class Broken(AppConfig):
            def validate(self):
                raise ValueError("server.url must not be empty")

        with self.assertRaises(ValueError):
            await controller.apply_runtime_config(Broken())
        [record] = records_of(ingress, "client.config.validation_failed")
        details = dict(record.details)
        self.assertEqual(details["source"], "apply_runtime_config")
        self.assertEqual(details["error_type"], "ValueError")
        self.assertEqual(record.level, "WARNING")

    async def test_start_attempt_and_confirmation_share_a_correlation_id(self):
        ingress, controller = self.build()
        controller._loop = asyncio.get_running_loop()
        immediate, attempt = controller._begin_start_locked()
        self.assertIsNone(immediate)
        self.assertIsNotNone(attempt)
        [record] = records_of(ingress, "client.dictation.start_attempt")
        self.assertEqual(
            record.correlation_id,
            f"hotkey:{attempt.generation}:{attempt.token}",
        )
        self.assertEqual(record.channel, "audit")
        attempt.send_task.cancel()
        await asyncio.gather(attempt.send_task, return_exceptions=True)

    async def test_run_started_is_recorded_after_the_queue_started(self):
        ingress, controller = self.build()
        controller._loop = asyncio.get_running_loop()
        task = asyncio.create_task(controller.run())
        found = []
        for _ in range(200):
            await asyncio.sleep(0.005)
            found = records_of(ingress, "client.controller.run_started")
            if found:
                break
        await controller.shutdown()
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

        self.assertEqual(len(found), 1)
        record = found[0]
        self.assertEqual(record.channel, "system")
        details = dict(record.details)
        self.assertIn("operating_mode", details)
        self.assertIn("wake_word_enabled", details)

    async def test_the_counter_source_is_registered_and_removed_again(self):
        """ARCH §8.6: the worker outlives the controller, so the read-only
        counter source has to be withdrawn when the controller goes away."""
        ingress, controller = self.build()
        self.assertEqual(
            [type_ for type_, _, _ in _sources(ingress)],
            ["client.audio.stream_stats"],
        )
        await controller.shutdown()
        self.assertEqual(_sources(ingress), [])


# ---------------------------------------------------------------------------
# §12.2 / §12.4: core/audio_capture.py and its counters
# ---------------------------------------------------------------------------


class TestAudioCaptureHooks(unittest.TestCase):
    def test_stream_stopped_reports_the_final_counters(self):
        from core.audio_capture import AudioCapture

        ingress = build_ingress()
        config = AppConfig()
        capture = AudioCapture(config.audio, observability=ingress)
        capture.chunks_captured = 42
        capture.chunks_dropped_capture_queue = 3
        capture.overflow_count = 1
        capture._running = True
        capture.stop()

        [record] = records_of(ingress, "client.audio.stream_stopped")
        details = dict(record.details)
        self.assertEqual(details["chunks_captured"], 42)
        self.assertEqual(details["chunks_dropped_capture_queue"], 3)
        self.assertEqual(details["overflow_count"], 1)
        self.assertEqual(record.channel, "audit")

    def test_capture_counters_snapshot_is_a_plain_int_mapping(self):
        from core.audio_capture import AudioCapture

        capture = AudioCapture(AppConfig().audio)
        counters = capture.capture_counters()
        self.assertTrue(all(isinstance(value, int) for value in counters.values()))
        self.assertIn("chunks_captured", counters)


# ---------------------------------------------------------------------------
# §12.4: core/text_injector.py -- client.queue.state
# ---------------------------------------------------------------------------


class TestInjectionQueueStateHook(unittest.TestCase):
    def test_queue_state_is_aggregated_and_rate_limited(self):
        from core.text_injector import TextInjectionQueue

        ingress = build_ingress()
        config = AppConfig()
        config.history.persistent.enabled = False
        history = TranscriptHistoryManager(config.history)
        queue = TextInjectionQueue(config, history, None, observability=ingress)

        queue._observe_queue_state("after_job")
        # Immediately again: the rate limit suppresses it.
        queue._observe_queue_state("after_job")
        # A state change is forced through regardless.
        queue._observe_queue_state("worker_stopped", force=True)

        records = records_of(ingress, "client.queue.state")
        self.assertEqual(len(records), 2)
        self.assertEqual(
            [dict(record.details)["phase"] for record in records],
            ["after_job", "worker_stopped"],
        )
        for record in records:
            self.assertEqual(record.channel, "performance")
            self.assertEqual(record.level, "DEBUG")
            details = dict(record.details)
            self.assertIn("queue_size", details)
            self.assertIn("jobs_processed", details)
            # Aggregated numbers only -- never a job or a text.
            self.assertNotIn("text", details)
            self.assertNotIn("entry_id", details)


# ---------------------------------------------------------------------------
# §12.7: what must stay uninstrumented
# ---------------------------------------------------------------------------


class TestDeliberatelyNotInstrumented(unittest.TestCase):
    def test_realtime_events_produce_no_structured_record(self):
        """§12.7: *"realtime-Events: KEIN strukturierter Record. Der bestehende
        DEBUG-Log bleibt und wird vom Handlerlevel gefiltert."*"""
        ingress = build_ingress()
        config = AppConfig()
        session = STTSession(config.server, config.session, observability=ingress)
        session._state.session_id = "session-1"
        session._apply_event(
            {
                "type": "realtime",
                "sessionId": "session-1",
                "segmentId": 1,
                "text": "zwischentext",
            }
        )
        for record in ingress.drain(100, 0.0):
            self.assertNotIn("realtime", (record.type or ""))

    def test_pure_modules_import_no_observability(self):
        """§12.7: *"Module ohne Logging (event_models, event_protocol,
        event_normalizer, feedback_reducer, feedback_mapping,
        settings_metadata, actions, version): bewusst rein, nicht aendern."*"""
        import pathlib

        root = pathlib.Path(__file__).resolve().parents[1] / "core"
        for name in (
            "event_models",
            "event_protocol",
            "event_normalizer",
            "feedback_reducer",
            "feedback_mapping",
            "settings_metadata",
            "actions",
            "version",
        ):
            with self.subTest(module=name):
                source = (root / f"{name}.py").read_text(encoding="utf-8")
                self.assertNotIn("observability", source)

    def test_headless_prints_are_untouched(self):
        """§12.7: the ``print()`` calls of the headless diagnostic mode are the
        OUTPUT of that mode, not a log."""
        import pathlib

        source = (
            pathlib.Path(__file__).resolve().parents[1] / "app.py"
        ).read_text(encoding="utf-8")
        self.assertIn('print(f"  [{prefix}] seg={segment_id}: {text}")', source)


if __name__ == "__main__":
    unittest.main()
