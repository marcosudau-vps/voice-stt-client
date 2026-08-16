"""AP7 – the client lifecycle around server-authoritative activations.

What these tests pin down:

* `start` and `stop` stay **stream** commands; a manual trigger is an extra
  command on the running stream and never a replacement for it.
* Nothing counts as accepted before the matching `trigger_ack` arrived.
* Against a server without the trigger capability the client behaves exactly
  as before.
* Global hotkeys are only claimed when the manual trigger is a source for the
  session, so a wake-word-only installation cannot fail on a hotkey conflict.
"""

from __future__ import annotations

import asyncio
import json
import unittest

from websockets.protocol import State

from core.config import AppConfig, OperatingMode, ServerConfig, SessionConfig
from core.stt_session import (
    ClientState,
    SessionState,
    STTSession,
    TransportState,
    TriggerAck,
)


class RecordingWebSocket:
    """A socket that only records what the client sent."""

    def __init__(self) -> None:
        self.state = State.OPEN
        self.sent: list[str] = []

    async def send(self, payload) -> None:
        self.sent.append(payload)

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.state = State.CLOSED

    def commands(self) -> list[dict]:
        out = []
        for payload in self.sent:
            if isinstance(payload, (bytes, bytearray)):
                continue
            try:
                out.append(json.loads(payload))
            except json.JSONDecodeError:
                continue
        return out

    def command_types(self) -> list[str]:
        return [command.get("type") for command in self.commands()]


def ready_session(*, capability: bool) -> tuple[STTSession, RecordingWebSocket]:
    session = STTSession(ServerConfig())
    session._generation = 1
    session._state = ClientState(
        transport=TransportState.READY,
        generation=1,
        session_id="session-1",
        ready_ok=True,
        server_status=SessionState.IDLE,
    )
    socket = RecordingWebSocket()
    session._ws = socket
    if capability:
        session._session_capabilities = {
            "activationTriggers": {"supported": True}
        }
    return session, socket


class StreamCommandsStayStreamCommands(unittest.IsolatedAsyncioTestCase):
    async def test_start_is_still_sent_when_the_server_supports_triggers(self):
        session, socket = ready_session(capability=True)

        await session.send_start()
        await session.send_trigger("activate", "manual", "c-1")

        types = socket.command_types()
        self.assertEqual(
            types,
            ["start", "trigger"],
            "the trigger must come *in addition to* start, not instead of it",
        )
        self.assertTrue(session.state.streaming_requested)

    async def test_a_trigger_is_never_mapped_onto_start_or_stop(self):
        session, socket = ready_session(capability=True)
        await session.send_trigger("finish", "manual", "c-2")
        await session.send_trigger("cancel", "manual", "c-3")

        self.assertEqual(socket.command_types(), ["trigger", "trigger"])
        for command in socket.commands():
            self.assertIn(command["action"], {"finish", "cancel"})

    async def test_stop_remains_available_as_a_stream_command(self):
        session, socket = ready_session(capability=True)
        await session.send_start()
        await session.send_stop()
        self.assertEqual(socket.command_types(), ["start", "stop"])
        self.assertFalse(session.state.streaming_requested)


class CapabilityFallback(unittest.IsolatedAsyncioTestCase):
    async def test_a_server_without_the_capability_is_detected(self):
        session, _ = ready_session(capability=False)
        self.assertFalse(session.supports_activation_triggers)

    async def test_a_server_with_the_capability_is_detected(self):
        session, _ = ready_session(capability=True)
        self.assertTrue(session.supports_activation_triggers)

    async def test_a_malformed_capability_block_is_not_trusted(self):
        session, _ = ready_session(capability=False)
        for value in ({"activationTriggers": True}, {"activationTriggers": []},
                      {"activationTriggers": {"supported": "yes-please"}}):
            with self.subTest(value=value):
                session._session_capabilities = value
                self.assertIsInstance(
                    session.supports_activation_triggers, bool
                )
        session._session_capabilities = {"activationTriggers": {}}
        self.assertFalse(session.supports_activation_triggers)


class TriggerBeforeReadyAndAfterDisconnect(unittest.IsolatedAsyncioTestCase):
    async def test_a_trigger_before_the_socket_is_open_is_refused_locally(self):
        session = STTSession(ServerConfig())
        session._ws = None
        with self.assertRaises(ConnectionError):
            await session.send_trigger("activate", "manual", "early-1")
        self.assertEqual(session.pending_trigger_ids, ())

    async def test_a_trigger_after_disconnect_is_refused_locally(self):
        session, socket = ready_session(capability=True)
        await socket.close()
        with self.assertRaises(ConnectionError):
            await session.send_trigger("activate", "manual", "late-1")

    async def test_a_pending_command_does_not_survive_a_reconnect(self):
        session, _ = ready_session(capability=True)
        await session.send_trigger("activate", "manual", "carry-1")
        pending = session._pending_triggers["carry-1"]

        session._discard_pending_triggers("connection_restarted")
        session._generation = 2

        self.assertEqual(session.pending_trigger_ids, ())
        ack = await asyncio.wait_for(pending.future, timeout=1.0)
        self.assertFalse(ack.accepted)

        # An answer that arrives afterwards must change nothing.
        seen: list[dict] = []
        session.on_event = lambda event_type, event: (
            seen.append(event) if event_type == "trigger_ack" else None
        )
        session._apply_event({
            "type": "trigger_ack",
            "commandId": "carry-1",
            "accepted": True,
            "reason": "activated",
            "activationId": "old-activation",
            "sessionId": "session-1",
        })
        self.assertEqual(
            seen, [], "a reconnect must not let an old activation come back"
        )


class HotkeyRegistrationFollowsTheManualTrigger(unittest.TestCase):
    """Hotkeys are only claimed when the manual trigger is actually a source."""

    def _enabled_for(self, session_config: SessionConfig) -> bool:
        config = AppConfig(session=session_config)
        return bool(
            config.hotkey.enabled
            and config.session.effective_manual_trigger_enabled
        )

    def test_manual_only_registers_hotkeys(self):
        self.assertTrue(
            self._enabled_for(SessionConfig(mode=OperatingMode.HOTKEY.value))
        )

    def test_wake_word_only_does_not_register_hotkeys(self):
        self.assertFalse(
            self._enabled_for(SessionConfig(mode=OperatingMode.WAKE_WORD.value)),
            "a wake-word-only session must not claim global hotkeys",
        )

    def test_both_triggers_register_hotkeys(self):
        self.assertTrue(
            self._enabled_for(
                SessionConfig(
                    manual_trigger_enabled=True, wake_word_trigger_enabled=True
                )
            )
        )

    def test_explicitly_disabled_manual_trigger_does_not_register(self):
        self.assertFalse(
            self._enabled_for(
                SessionConfig(
                    manual_trigger_enabled=False, wake_word_trigger_enabled=True
                )
            )
        )


class TriggerCapableSession:
    """A `FakeSTTSession` that also speaks the activation trigger contract."""

    def __init__(self, *, accept: bool = True, reason: str = "activated"):
        from tests.test_controller import FakeSTTSession

        self._inner = FakeSTTSession()
        self.supports_activation_triggers = True
        self.triggers: list[tuple[str, str]] = []
        self._accept = accept
        self._reason = reason

    def __getattr__(self, name):
        return getattr(self._inner, name)

    def __setattr__(self, name, value):
        if name in {"_inner", "supports_activation_triggers", "triggers",
                    "_accept", "_reason"}:
            object.__setattr__(self, name, value)
        else:
            setattr(self._inner, name, value)

    async def request_trigger(self, action, source="manual", command_id=None,
                              timeout=5.0):
        self.triggers.append((action, source))
        return TriggerAck(
            command_id=command_id or "cmd-fake",
            accepted=self._accept,
            reason=self._reason,
            activation_id="act-1" if self._accept else None,
            session_id="fake-session",
            action=action,
            source=source,
        )

    async def send_trigger(self, action, source="manual", command_id=None):
        self.triggers.append((action, source))
        return command_id or "cmd-fake"


class ControllerKeepsTheStreamCommand(unittest.IsolatedAsyncioTestCase):
    """The regression that mattered: `start` must not be replaced."""

    async def _controller(self, session):
        from core.controller import STTController
        from tests.test_controller import FakeAudioCapture, FakeInjectionQueue

        config = AppConfig()
        audio = FakeAudioCapture()
        controller = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=FakeInjectionQueue(),
        )
        controller.start_queue()
        self.addCleanup(lambda: asyncio.run(controller.shutdown()))
        return controller, audio

    async def test_start_dictation_sends_start_and_the_trigger(self):
        session = TriggerCapableSession(accept=True)
        controller, audio = await self._controller(session)

        result = await controller.start_dictation()

        self.assertTrue(result.success, result.message)
        self.assertEqual(
            session.start_calls,
            1,
            "the audio stream must still be started by `start`",
        )
        self.assertEqual(session.triggers, [("activate", "manual")])
        self.assertEqual(audio.start_calls, 1)

    async def test_a_rejected_trigger_does_not_confirm_the_dictation(self):
        session = TriggerCapableSession(accept=False, reason="stream_not_started")
        controller, audio = await self._controller(session)

        result = await controller.start_dictation()

        self.assertFalse(result.success)
        self.assertEqual(result.status, "trigger_rejected")
        self.assertFalse(
            controller.dictation_requested,
            "a rejected trigger must not leave the client believing it started",
        )
        self.assertEqual(audio.stop_calls, 1, "audio capture is rolled back")

    async def test_without_the_capability_only_start_is_sent(self):
        from tests.test_controller import FakeSTTSession

        session = FakeSTTSession()
        controller, _ = await self._controller(session)

        result = await controller.start_dictation()

        self.assertTrue(result.success, result.message)
        self.assertEqual(session.start_calls, 1)
        self.assertFalse(hasattr(session, "triggers"))


class StreamCountingSession(TriggerCapableSession):
    """Counts stream commands separately from session teardown.

    ``FakeSTTSession`` increments one counter for both ``send_stop`` and
    ``stop``, which cannot answer the question this test asks. It also does not
    model ``streaming_requested``, although the real ``STTSession.send_start``
    sets it - and that flag is exactly what stops the controller from starting
    the stream a second time. Both are modelled faithfully here.
    """

    def __init__(self, *, accept: bool = True, reason: str = "activated"):
        super().__init__(accept=accept, reason=reason)
        object.__setattr__(self, "stream_starts", 0)
        object.__setattr__(self, "stream_stops", 0)
        object.__setattr__(self, "session_stops", 0)

    def __setattr__(self, name, value):
        if name in {"stream_starts", "stream_stops", "session_stops"}:
            object.__setattr__(self, name, value)
        else:
            super().__setattr__(name, value)

    async def send_start(self) -> None:
        self.stream_starts += 1
        await self._inner.send_start()
        self._inner.state.streaming_requested = True

    async def send_stop(self) -> None:
        self.stream_stops += 1
        await self._inner.send_stop()
        self._inner.state.streaming_requested = False

    async def stop(self) -> None:
        self.session_stops += 1
        await self._inner.stop()


class ContinuousStreamingInvariant(unittest.IsolatedAsyncioTestCase):
    """AP7 core goal: one session, one continuous stream, many activations.

    ```text
    Session verbinden -> Stream genau einmal starten
    Activation 1 -> Recording / Final / Finish
    Activation 2 -> Recording / Final / Finish
    dabei: Stream-Starts bleibt 1, Stream-Stops bleibt 0
    erst beim Session-/Streamende: Stream-Stops = 1
    ```

    The test drives the real `STTController` production path
    (`start_dictation`, `stop_dictation`, `cancel_dictation`,
    `extend_dictation_window`, `handle_server_event`) rather than setting
    internal flags.
    """

    async def _controller(self, session, config=None):
        from core.controller import STTController
        from tests.test_controller import FakeAudioCapture, FakeInjectionQueue

        config = config or AppConfig()
        config.history.persistent.enabled = False
        audio = FakeAudioCapture()
        controller = STTController(
            config,
            session=session,
            audio=audio,
            injection_queue=FakeInjectionQueue(),
        )
        controller.start_queue()
        self.addCleanup(self._shutdown, controller)
        return controller, audio

    def _shutdown(self, controller):
        import asyncio as _asyncio

        _asyncio.run(controller.shutdown())

    def _timeline(self, controller, session, event, **fields):
        payload = {
            "type": "timeline",
            "sessionId": session.state.session_id,
            "_clientGeneration": session.generation,
            "event": event,
        }
        payload.update(fields)
        controller.handle_server_event("timeline", payload)

    async def test_two_activations_share_one_continuous_stream(self):
        session = StreamCountingSession(accept=True)
        controller, audio = await self._controller(session)

        # --- Activation 1 -------------------------------------------------
        first = await controller.start_dictation()
        self.assertTrue(first.success, first.message)
        self.assertEqual(session.stream_starts, 1, "stream starts exactly once")

        self._timeline(controller, session, "recording_started", activationId="a-1")
        self._timeline(controller, session, "recording_ended", activationId="a-1")
        await controller.stop_dictation()

        self.assertEqual(
            session.stream_starts, 1, "finishing an activation must not restart the stream"
        )
        self.assertEqual(
            session.stream_stops, 0, "finish ends the activation, not the stream"
        )
        self.assertEqual(session.triggers[-1], ("finish", "manual"))

        # --- Activation 2 -------------------------------------------------
        second = await controller.start_dictation()
        self.assertTrue(second.success, second.message)

        self._timeline(controller, session, "recording_started", activationId="a-2")
        self._timeline(controller, session, "recording_ended", activationId="a-2")
        await controller.stop_dictation()

        self.assertEqual(
            session.stream_starts,
            1,
            "a second activation must reuse the running stream",
        )
        self.assertEqual(session.stream_stops, 0)
        self.assertEqual(
            [action for action, _ in session.triggers],
            ["activate", "finish", "activate", "finish"],
        )
        self.assertEqual(
            audio.start_calls, 2, "audio capture follows the dictation, not the stream"
        )

    async def test_cancel_ends_the_activation_and_not_the_session(self):
        session = StreamCountingSession(accept=True)
        controller, _ = await self._controller(session)

        await controller.start_dictation()
        await controller.cancel_dictation()

        self.assertIn(("cancel", "manual"), session.triggers)
        self.assertEqual(session.stream_stops, 0, "cancel must not stop the stream")
        self.assertEqual(session.session_stops, 0, "cancel must not end the session")
        self.assertTrue(
            session.is_ready, "the session stays usable after a cancel"
        )

        # ... and a new activation still works on the same stream.
        again = await controller.start_dictation()
        self.assertTrue(again.success, again.message)
        self.assertEqual(session.stream_starts, 1)

    async def test_extending_the_window_creates_no_second_stream(self):
        session = StreamCountingSession(accept=True)
        controller, _ = await self._controller(session)

        await controller.start_dictation()
        controller.extend_dictation_window()
        controller.extend_dictation_window()

        self.assertEqual(session.stream_starts, 1)
        self.assertEqual(session.stream_stops, 0)

    async def test_a_follow_up_round_creates_no_second_stream(self):
        session = StreamCountingSession(accept=True)
        controller, _ = await self._controller(session)

        await controller.start_dictation()
        for index in range(3):
            self._timeline(
                controller, session, "recording_started", activationId=f"a-{index}"
            )
            self._timeline(
                controller, session, "recording_ended", activationId=f"a-{index}"
            )

        self.assertEqual(
            session.stream_starts, 1, "follow-up rounds reuse the same stream"
        )
        self.assertEqual(session.stream_stops, 0)

    async def test_a_server_driven_activation_does_not_restart_the_stream(self):
        """Wake-word activations are server-driven and touch no stream command."""
        config = AppConfig(
            session=SessionConfig(
                manual_trigger_enabled=False, wake_word_trigger_enabled=True
            )
        )
        session = StreamCountingSession(accept=True)
        controller, _ = await self._controller(session, config)

        await controller.start_dictation()
        starts_after_arming = session.stream_starts

        for index in range(3):
            self._timeline(controller, session, "wakeword_detected")
            self._timeline(
                controller, session, "recording_started", activationId=f"w-{index}"
            )
            self._timeline(
                controller, session, "recording_ended", activationId=f"w-{index}"
            )

        self.assertEqual(starts_after_arming, 1)
        self.assertEqual(
            session.stream_starts,
            1,
            "wake-word activations must not re-create the audio stream",
        )
        self.assertEqual(session.stream_stops, 0)

    async def test_the_stream_only_stops_when_the_session_ends(self):
        from core.controller import STTController
        from tests.test_controller import FakeAudioCapture, FakeInjectionQueue

        session = StreamCountingSession(accept=True)
        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        controller.start_queue()

        await controller.start_dictation()
        await controller.stop_dictation()
        await controller.start_dictation()
        self.assertEqual(session.stream_stops, 0)

        await controller.shutdown()

        self.assertEqual(
            session.stream_starts, 1, "still exactly one stream over the session"
        )
        self.assertEqual(
            session.session_stops, 1, "the session ends exactly once"
        )

    async def test_a_legacy_server_keeps_the_old_start_stop_pairing(self):
        """Without the trigger capability the old contract must still hold."""
        from tests.test_controller import FakeSTTSession

        session = FakeSTTSession()
        controller, _ = await self._controller(session)

        await controller.start_dictation()
        self.assertEqual(session.start_calls, 1)
        await controller.stop_dictation()

        self.assertGreaterEqual(
            session.stop_calls,
            1,
            "a legacy server is still stopped with the stream command",
        )


class TriggerAckShape(unittest.TestCase):
    def test_the_ack_carries_everything_needed_for_correlation(self):
        ack = TriggerAck(
            command_id="c-9",
            accepted=True,
            reason="activated",
            activation_id="a-9",
            session_id="s-9",
            action="activate",
            source="manual",
        )
        self.assertEqual(ack.command_id, "c-9")
        self.assertEqual(ack.activation_id, "a-9")
        self.assertEqual(ack.action, "activate")
        self.assertEqual(ack.source, "manual")


if __name__ == "__main__":
    unittest.main()
