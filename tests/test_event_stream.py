"""Deterministic isolated transport tests for AP07 M5."""

from __future__ import annotations

import asyncio
import json
import tempfile
import unittest
from pathlib import Path

from websockets.protocol import State

from core.config import EventStreamConfig
from core.event_cursor_store import EventCursorStore
from core.event_models import EventConnectionState
from core.event_models import CanonicalEventType, FeedbackImpulse
from core.feedback_mapping import (
    FeedbackMappingConfig,
    FeedbackRule,
    LedCall,
    LedVerb,
    SoundCueId,
    SoundEffect,
)
from core.feedback_reducer import FeedbackEngine
from core.event_protocol import (
    EventProtocolError,
    EventProtocolProcessor,
    EventStreamAccess,
)
from core.event_stream import EventProcessingRejected, EventStreamTransport
from tests.test_event_protocol import event_message, hello, subscribed


class ScriptedLogSocket:
    def __init__(self, frames) -> None:
        self.frames = list(frames)
        self.sent = []
        self.close_calls = []
        self.state = State.OPEN
        self.closed = asyncio.Event()

    async def send(self, payload):
        self.sent.append(payload)

    async def recv(self):
        if self.frames:
            frame = self.frames.pop(0)
            if isinstance(frame, BaseException):
                raise frame
            return frame
        await self.closed.wait()
        raise ConnectionError("socket closed")

    async def close(self, code=1000, reason=""):
        self.close_calls.append((code, reason))
        self.state = State.CLOSED
        self.closed.set()


def access(session_id="session-1", token="secret-token"):
    return EventStreamAccess(
        endpoint="wss://stt.voice.marcosudau.com/ws/logs",
        session_id=session_id,
        access_token=token,
        server_instance_id="server-1",
        latest_cursor=20,
        channels=("transcription",),
    )


def frames(*, include_live=True):
    result = [
        json.dumps(hello()),
        json.dumps(subscribed()),
        json.dumps(event_message(3, "evt-replay", replay=True)),
        json.dumps({"type": "log.replay_completed", "cursor": 20, "count": 1}),
    ]
    if include_live:
        result.append(json.dumps(event_message(24, "evt-live", replay=False)))
    return result


class TestEventStreamTransport(unittest.IsolatedAsyncioTestCase):
    def make_transport(self, socket, handler, *, store=None, control=None, states=None):
        stream_access = access()
        processor = EventProtocolProcessor(stream_access, cursor_store=store)
        connect_kwargs = {}

        async def connect_factory(endpoint, **kwargs):
            connect_kwargs["endpoint"] = endpoint
            connect_kwargs.update(kwargs)
            return socket

        transport = EventStreamTransport(
            EventStreamConfig(
                connect_timeout=0.1,
                handshake_timeout=0.1,
                replay_timeout=0.1,
                message_timeout=0.05,
                reconnect_min_delay=0.001,
                reconnect_max_delay=0.01,
                reconnect_jitter=0.0,
            ),
            stream_access,
            processor,
            on_event=handler,
            on_control=control,
            on_state_change=(states.append if states is not None else None),
            connect_factory=connect_factory,
        )
        return transport, processor, connect_kwargs

    async def test_handshake_replay_live_and_first_frame_token_policy(self):
        socket = ScriptedLogSocket(frames())
        states = []
        seen = []
        holder = {}

        async def handle(result):
            seen.append((result.event_id, result.origin.value))
            if result.event_id == "evt-live":
                await holder["transport"].stop()
            return True

        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory) / "cursor.json")
            transport, processor, kwargs = self.make_transport(
                socket, handle, store=store, states=states
            )
            holder["transport"] = transport
            await asyncio.wait_for(transport.run(), timeout=0.5)
            record = store.load(
                endpoint=access().endpoint,
                server_instance_id="server-1",
                protocol_version=2,
            )

        subscribe = json.loads(socket.sent[0])
        self.assertEqual(subscribe["type"], "subscribe")
        self.assertEqual(subscribe["accessToken"], "secret-token")
        self.assertNotIn("secret-token", kwargs["endpoint"])
        self.assertEqual(kwargs["max_size"], 1024 * 1024)
        self.assertEqual(kwargs["max_queue"], 512)
        self.assertEqual(seen, [("evt-replay", "replay"), ("evt-live", "live")])
        self.assertEqual(record.cursor, 24)
        self.assertIn(EventConnectionState.REPLAYING, states)
        self.assertIn(EventConnectionState.LIVE, states)
        self.assertEqual(transport.state, EventConnectionState.STOPPED)
        self.assertEqual(processor.resume_cursor, 24)

    async def test_unconfirmed_event_forces_reconnect_without_cursor_commit(self):
        socket = ScriptedLogSocket(frames(include_live=False))

        async def reject(_result):
            return False

        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory) / "cursor.json")
            transport, processor, _ = self.make_transport(socket, reject, store=store)
            transport._running = True
            with self.assertRaises(EventProcessingRejected):
                await transport._connect_once()
            self.assertFalse(store.path.exists())
            self.assertEqual(processor.resume_cursor, 0)

    async def test_binary_and_invalid_json_frames_fail_the_attempt(self):
        for bad_frame in (b"binary", "not json"):
            with self.subTest(frame=bad_frame):
                socket = ScriptedLogSocket([bad_frame])

                async def accept(_result):
                    return True

                transport, _, _ = self.make_transport(socket, accept)
                transport._running = True
                with self.assertRaises(EventProtocolError):
                    await transport._connect_once()

    async def test_shutdown_interrupts_backoff_without_leaking_run_task(self):
        attempts = 0
        backoff_reached = asyncio.Event()

        async def failing_connect(*_args, **_kwargs):
            nonlocal attempts
            attempts += 1
            raise OSError("network down")

        stream_access = access()
        processor = EventProtocolProcessor(stream_access)

        async def accept(_result):
            return True

        def state_changed(state):
            if state is EventConnectionState.BACKOFF:
                backoff_reached.set()

        transport = EventStreamTransport(
            EventStreamConfig(
                connect_timeout=0.05,
                reconnect_min_delay=10,
                reconnect_max_delay=10,
                reconnect_jitter=0,
            ),
            stream_access,
            processor,
            on_event=accept,
            on_state_change=state_changed,
            connect_factory=failing_connect,
        )
        task = asyncio.create_task(transport.run())
        await asyncio.wait_for(backoff_reached.wait(), timeout=0.2)
        await transport.stop()
        await asyncio.wait_for(task, timeout=0.2)
        self.assertEqual(attempts, 1)
        self.assertEqual(transport.state, EventConnectionState.STOPPED)

    def test_backoff_remains_capped_after_extreme_failure_count(self):
        stream_access = access()
        transport = EventStreamTransport(
            EventStreamConfig(
                reconnect_min_delay=0.5,
                reconnect_max_delay=30.0,
                reconnect_jitter=0.0,
            ),
            stream_access,
            EventProtocolProcessor(stream_access),
            on_event=lambda _result: True,
        )
        transport._backoff_attempt = 100_000

        self.assertEqual(transport._backoff_delay(), 30.0)

    async def test_shutdown_interrupts_an_in_progress_connect(self):
        connect_started = asyncio.Event()
        never_finishes = asyncio.Event()

        async def hanging_connect(*_args, **_kwargs):
            connect_started.set()
            await never_finishes.wait()

        stream_access = access()
        processor = EventProtocolProcessor(stream_access)

        async def accept(_result):
            return True

        transport = EventStreamTransport(
            EventStreamConfig(connect_timeout=30),
            stream_access,
            processor,
            on_event=accept,
            connect_factory=hanging_connect,
        )
        task = asyncio.create_task(transport.run())
        await asyncio.wait_for(connect_started.wait(), timeout=0.2)
        await transport.stop()
        await asyncio.wait_for(task, timeout=0.2)
        self.assertEqual(transport.state, EventConnectionState.STOPPED)

    async def test_shutdown_during_replay_leaves_no_pending_receive(self):
        socket = ScriptedLogSocket([
            json.dumps(hello()),
            json.dumps(subscribed()),
        ])
        replaying = asyncio.Event()

        async def accept(_result):
            return True

        def state_changed(state):
            if state is EventConnectionState.REPLAYING:
                replaying.set()

        transport, processor, _ = self.make_transport(socket, accept)
        transport._on_state_change = state_changed
        task = asyncio.create_task(transport.run())
        await asyncio.wait_for(replaying.wait(), timeout=0.2)
        await transport.stop()
        await asyncio.wait_for(task, timeout=0.2)
        self.assertEqual(processor.state, EventConnectionState.STOPPED)
        self.assertEqual(transport.state, EventConnectionState.STOPPED)

    async def test_replay_disconnect_resumes_from_last_confirmed_cursor(self):
        first = ScriptedLogSocket([
            json.dumps(hello()),
            json.dumps(subscribed()),
            json.dumps(event_message(3, "evt-3", replay=True)),
            ConnectionError("disconnect during replay"),
        ])
        second = ScriptedLogSocket([
            json.dumps(hello(latestCursor=25)),
            json.dumps(subscribed(3)),
            json.dumps(event_message(4, "evt-4", replay=True)),
            json.dumps({"type": "log.replay_completed", "cursor": 25, "count": 1}),
            json.dumps(event_message(26, "evt-26", replay=False)),
        ])
        sockets = [first, second]
        seen = []
        holder = {}

        async def connect_factory(*_args, **_kwargs):
            return sockets.pop(0)

        async def accept(result):
            seen.append(result.event_id)
            if result.event_id == "evt-26":
                await holder["transport"].stop()
            return True

        with tempfile.TemporaryDirectory() as directory:
            stream_access = access()
            processor = EventProtocolProcessor(
                stream_access,
                cursor_store=EventCursorStore(Path(directory) / "cursor.json"),
            )
            transport = EventStreamTransport(
                EventStreamConfig(
                    connect_timeout=0.1,
                    handshake_timeout=0.1,
                    replay_timeout=0.1,
                    message_timeout=0.1,
                    reconnect_min_delay=0.001,
                    reconnect_max_delay=0.001,
                    reconnect_jitter=0,
                ),
                stream_access,
                processor,
                on_event=accept,
                connect_factory=connect_factory,
            )
            holder["transport"] = transport
            await asyncio.wait_for(transport.run(), timeout=0.5)

        self.assertEqual(json.loads(first.sent[0])["afterCursor"], 0)
        self.assertEqual(json.loads(second.sent[0])["afterCursor"], 3)
        self.assertEqual(seen, ["evt-3", "evt-4", "evt-26"])

    async def test_cursor_write_failure_replays_without_duplicate_visible_impulse(self):
        first = ScriptedLogSocket([
            json.dumps(hello()),
            json.dumps(subscribed()),
            json.dumps({"type": "log.replay_completed", "cursor": 20, "count": 0}),
            json.dumps(event_message(24, "durable-complete", replay=False)),
        ])
        second = ScriptedLogSocket([
            json.dumps(hello(latestCursor=24)),
            json.dumps(subscribed()),
            json.dumps(event_message(24, "durable-complete", replay=True)),
            json.dumps({"type": "log.replay_completed", "cursor": 24, "count": 1}),
        ])
        sockets = [first, second]
        mapped_rule = FeedbackRule(
            led=(LedCall(LedVerb.EMIT_EVENT, target="success_event"),),
            sound=SoundEffect(SoundCueId.COMPLETE),
        )
        engine = FeedbackEngine(FeedbackMappingConfig(events={
            CanonicalEventType.SERVER_TRANSCRIPTION_COMPLETED.value: mapped_rule,
        }))
        decisions = []
        holder = {}

        async def connect_factory(*_args, **_kwargs):
            return sockets.pop(0)

        async def accept(result):
            decision = engine.handle_event_stream(
                result,
                generation=1,
                session_id="session-1",
            )
            if decision is not None:
                decisions.append(decision)
            return True

        async def control(result):
            if (
                result.kind.value == "replay_completed"
                and not sockets
            ):
                await holder["transport"].stop()

        def state_changed(state):
            decision = engine.update_connection(
                state,
                stt_ready=True,
                generation=1,
                session_id="session-1",
            )
            decisions.append(decision)

        with tempfile.TemporaryDirectory() as directory:
            store = EventCursorStore(Path(directory) / "cursor.json")
            original_commit = store.commit
            fail_once = True

            def flaky_commit(*args, **kwargs):
                nonlocal fail_once
                if fail_once:
                    fail_once = False
                    raise OSError("simulated cursor disk failure")
                return original_commit(*args, **kwargs)

            store.commit = flaky_commit
            stream_access = access()
            processor = EventProtocolProcessor(
                stream_access,
                cursor_store=store,
            )
            transport = EventStreamTransport(
                EventStreamConfig(
                    connect_timeout=0.1,
                    handshake_timeout=0.1,
                    replay_timeout=0.1,
                    message_timeout=0.1,
                    reconnect_min_delay=0.001,
                    reconnect_max_delay=0.001,
                    reconnect_jitter=0,
                ),
                stream_access,
                processor,
                on_event=accept,
                on_control=control,
                on_state_change=state_changed,
                connect_factory=connect_factory,
            )
            holder["transport"] = transport
            await asyncio.wait_for(transport.run(), timeout=0.5)
            record = store.load(
                endpoint=stream_access.endpoint,
                server_instance_id="server-1",
                protocol_version=2,
            )

        visible_completed = [
            decision
            for decision in decisions
            if decision.publish
            and decision.impulse is FeedbackImpulse.TRANSCRIPTION_COMPLETED
        ]
        self.assertEqual(len(visible_completed), 1)
        self.assertEqual(visible_completed[0].rule, mapped_rule)
        self.assertTrue(any(decision.replay for decision in decisions))
        self.assertEqual(record.cursor, 24)
        self.assertEqual(json.loads(first.sent[0])["afterCursor"], 0)
        self.assertEqual(json.loads(second.sent[0])["afterCursor"], 0)

    async def test_auth_error_waits_for_reconfigured_session_access(self):
        denied = ScriptedLogSocket([
            json.dumps({"type": "log.error", "code": "not_authorized"})
        ])
        replacement = ScriptedLogSocket(frames())
        sockets = [denied, replacement]
        unavailable = asyncio.Event()
        holder = {}

        async def connect_factory(*_args, **_kwargs):
            return sockets.pop(0)

        async def accept(result):
            if result.event_id == "evt-live":
                await holder["transport"].stop()
            return True

        def state_changed(state):
            if state is EventConnectionState.UNAVAILABLE:
                unavailable.set()

        first_access = access(token="expired")
        processor = EventProtocolProcessor(first_access)
        transport = EventStreamTransport(
            EventStreamConfig(
                connect_timeout=0.1,
                handshake_timeout=0.1,
                replay_timeout=0.1,
                message_timeout=0.1,
                reconnect_min_delay=0.001,
                reconnect_max_delay=0.001,
                reconnect_jitter=0,
            ),
            first_access,
            processor,
            on_event=accept,
            on_state_change=state_changed,
            connect_factory=connect_factory,
        )
        holder["transport"] = transport
        task = asyncio.create_task(transport.run())
        await asyncio.wait_for(unavailable.wait(), timeout=0.2)
        await transport.reconfigure(access(token="fresh"))
        await asyncio.wait_for(task, timeout=0.5)

        self.assertEqual(json.loads(denied.sent[0])["accessToken"], "expired")
        self.assertEqual(json.loads(replacement.sent[0])["accessToken"], "fresh")
        self.assertNotIn("expired", transport.last_error or "")

    async def test_live_idle_timeout_sends_application_ping(self):
        socket = ScriptedLogSocket([
            json.dumps(hello()),
            json.dumps(subscribed()),
            json.dumps({"type": "log.replay_completed", "cursor": 20, "count": 0}),
        ])
        ping_seen = asyncio.Event()
        original_send = socket.send

        async def send(payload):
            await original_send(payload)
            if json.loads(payload).get("type") == "ping":
                socket.frames.append(json.dumps({
                    "type": "log.pong", "cursor": 20, "serverTime": 1.0
                }))
                ping_seen.set()

        socket.send = send

        async def accept(_result):
            return True

        controls = []

        async def control(result):
            controls.append(result.kind.value)
            if result.kind.value == "pong":
                await transport.stop()

        transport, _, _ = self.make_transport(socket, accept, control=control)
        await asyncio.wait_for(transport.run(), timeout=0.5)
        self.assertTrue(ping_seen.is_set())
        self.assertIn("pong", controls)


if __name__ == "__main__":
    unittest.main()
