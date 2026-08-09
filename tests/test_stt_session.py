"""Deterministic AP05 transport, generation, backoff, and ping tests."""

from __future__ import annotations

import asyncio
import json
import time
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from websockets.protocol import State

from core.config import ServerConfig
from core.stt_session import (
    ClientState,
    STTSession,
    SessionState,
    TransportState,
    reduce,
)


class FakeWebSocket:
    def __init__(self, *, fail_send: bool = False) -> None:
        self.state = State.OPEN
        self.fail_send = fail_send
        self.sent: list[str] = []
        self.close_calls: list[tuple[int, str]] = []
        self.closed = asyncio.Event()

    async def send(self, payload: str) -> None:
        if self.fail_send:
            raise ConnectionError("simulated ping send failure")
        self.sent.append(payload)

    async def close(self, code: int = 1000, reason: str = "") -> None:
        self.close_calls.append((code, reason))
        self.state = State.CLOSED
        self.closed.set()


class ScriptedWebSocket(FakeWebSocket):
    def __init__(self, recv_messages: list[str]) -> None:
        super().__init__()
        self._recv_messages = list(recv_messages)

    async def recv(self) -> str:
        return self._recv_messages.pop(0)

    def __aiter__(self):
        return self

    async def __anext__(self):
        raise StopAsyncIteration


class TestSTTSessionStateAndBackoff(unittest.TestCase):
    def setUp(self) -> None:
        self.config = ServerConfig(
            reconnect_min_delay=0.5,
            reconnect_max_delay=30.0,
            reconnect_jitter=0.3,
            server_busy_min_delay=10.0,
            ping_interval=0.01,
            ping_timeout_count=3,
        )
        self.session = STTSession(self.config)

    def test_client_state_generation_is_preserved_by_reducer(self) -> None:
        state = ClientState(generation=3)
        for event in (
            {"type": "hello", "sessionId": "s1"},
            {"type": "ready", "ok": True},
            {"type": "status", "state": "listening"},
        ):
            state = reduce(state, event)
            self.assertEqual(state.generation, 3)

    def test_first_failure_uses_minimum_and_growth_is_exponential(self) -> None:
        with patch("core.stt_session.random.random", return_value=0.0):
            self.session._backoff_attempt = 1
            self.assertEqual(self.session._backoff_delay(), 0.5)
            self.session._backoff_attempt = 2
            self.assertEqual(self.session._backoff_delay(), 1.0)
            self.session._backoff_attempt = 3
            self.assertEqual(self.session._backoff_delay(), 2.0)

    def test_backoff_is_capped_including_jitter(self) -> None:
        self.session._backoff_attempt = 100
        with patch("core.stt_session.random.random", return_value=1.0):
            self.assertEqual(
                self.session._backoff_delay(),
                self.config.reconnect_max_delay,
            )

    def test_server_busy_uses_long_minimum_but_remains_capped(self) -> None:
        self.session._is_server_busy = True
        self.session._backoff_attempt = 1
        with patch("core.stt_session.random.random", return_value=0.0):
            self.assertEqual(
                self.session._backoff_delay(),
                self.config.server_busy_min_delay,
            )
        self.session._backoff_attempt = 100
        with patch("core.stt_session.random.random", return_value=1.0):
            self.assertEqual(
                self.session._backoff_delay(),
                self.config.reconnect_max_delay,
            )

    def test_successful_admission_clears_busy_label_not_failure_count(self) -> None:
        self.session._is_server_busy = True
        self.session._backoff_attempt = 4
        self.session._apply_event({"type": "hello", "sessionId": "accepted"})
        self.assertFalse(self.session._is_server_busy)
        self.assertEqual(self.session._backoff_attempt, 4)

    def test_ready_and_unsolicited_pong_do_not_reset_backoff(self) -> None:
        self.session._backoff_attempt = 3
        self.session._state.session_id = "current"
        self.session._apply_event({"type": "ready", "ok": True})
        self.session._apply_event({"type": "pong", "sessionId": "current"})
        self.assertEqual(self.session._backoff_attempt, 3)
        self.assertFalse(self.session._first_pong_received)

    def test_only_matching_pending_pong_resets_backoff(self) -> None:
        self.session._backoff_attempt = 3
        self.session._state.session_id = "current"
        self.session._ping_pending = True
        self.session._ping_generation = self.session.generation
        self.session._state.ping_started_at = time.monotonic()

        self.session._apply_event({"type": "pong", "sessionId": "old"})
        self.assertEqual(self.session._backoff_attempt, 3)
        self.assertTrue(self.session._ping_pending)

        self.session._apply_event({"type": "pong", "sessionId": "current"})
        self.assertEqual(self.session._backoff_attempt, 0)
        self.assertFalse(self.session._ping_pending)
        self.assertTrue(self.session._first_pong_received)

    def test_close_code_extraction_supports_both_websockets_shapes(self) -> None:
        direct = SimpleNamespace(code=1013)
        nested = SimpleNamespace(code=None, rcvd=SimpleNamespace(code=1013))
        self.assertEqual(self.session._connection_close_code(direct), 1013)
        self.assertEqual(self.session._connection_close_code(nested), 1013)


class TestSTTSessionAsync(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.config = ServerConfig(
            reconnect_min_delay=0.001,
            reconnect_max_delay=0.02,
            reconnect_jitter=0.0,
            server_busy_min_delay=0.01,
            ping_interval=0.005,
            ping_timeout_count=3,
        )
        self.session = STTSession(self.config)
        self.session._generation = 1
        self.session._state = ClientState(
            transport=TransportState.READY,
            generation=1,
            session_id="session-1",
            ready_ok=True,
            server_status=SessionState.IDLE,
        )

    async def test_send_ping_never_overlaps(self) -> None:
        ws = FakeWebSocket()
        self.session._ws = ws

        self.assertTrue(await self.session.send_ping())
        self.assertFalse(await self.session.send_ping())
        self.assertEqual(len(ws.sent), 1)

        self.session._apply_event(
            {"type": "pong", "sessionId": "session-1"}
        )
        self.assertTrue(await self.session.send_ping())
        self.assertEqual(len(ws.sent), 2)

    async def test_ready_requires_both_protocol_state_and_open_socket(self) -> None:
        self.session._ws = None
        self.assertFalse(self.session.is_ready)
        self.session._ws = FakeWebSocket()
        self.assertTrue(self.session.is_ready)
        await self.session._ws.close()
        self.assertFalse(self.session.is_ready)

    async def test_ping_loop_keeps_one_ping_pending_until_threshold(self) -> None:
        ws = FakeWebSocket()
        self.session._ws = ws
        self.session._running = True

        task = asyncio.create_task(self.session._ping_loop())
        await asyncio.wait_for(ws.closed.wait(), timeout=0.2)
        await asyncio.wait_for(task, timeout=0.2)

        ping_payloads = [
            json.loads(payload)
            for payload in ws.sent
            if json.loads(payload).get("type") == "ping"
        ]
        self.assertEqual(ping_payloads, [{"type": "ping"}])
        self.assertEqual(
            self.session._consecutive_misses,
            self.config.ping_timeout_count,
        )
        self.assertEqual(len(ws.close_calls), 1)
        self.assertEqual(
            self.session._requested_disconnect_reason,
            "ping_timeout",
        )

    async def test_ping_send_failure_recycles_connection(self) -> None:
        ws = FakeWebSocket(fail_send=True)
        self.session._ws = ws
        self.session._running = True

        task = asyncio.create_task(self.session._ping_loop())
        await asyncio.wait_for(ws.closed.wait(), timeout=0.2)
        await asyncio.wait_for(task, timeout=0.2)

        self.assertEqual(len(ws.close_calls), 1)
        self.assertEqual(
            self.session._requested_disconnect_reason,
            "ping_send_error",
        )

    async def test_invalidate_connection_keeps_reconnect_loop_enabled(self) -> None:
        ws = FakeWebSocket()
        self.session._ws = ws
        self.session._running = True

        await self.session.invalidate_connection("start_timeout")

        self.assertTrue(self.session._running)
        self.assertEqual(len(ws.close_calls), 1)
        self.assertEqual(
            self.session._requested_disconnect_reason,
            "start_timeout",
        )

    async def test_stop_cancels_backoff_sleep(self) -> None:
        self.session._backoff_sleep_task = asyncio.create_task(
            asyncio.sleep(100)
        )
        await self.session.stop()
        await asyncio.gather(
            self.session._backoff_sleep_task, return_exceptions=True
        )
        self.assertTrue(self.session._backoff_sleep_task.cancelled())

    async def test_run_retries_until_explicit_stop(self) -> None:
        calls = 0

        async def failing_attempt() -> None:
            nonlocal calls
            calls += 1
            self.session._record_failure("network_unavailable")
            if calls == 4:
                await self.session.stop()

        self.session._connect_and_run = failing_attempt
        await asyncio.wait_for(self.session.run(), timeout=0.2)
        self.assertEqual(calls, 4)

    async def test_repeated_connection_attempts_cleanup_ping_state_and_tasks(self) -> None:
        self.session._running = True

        async def connect_once(*_args, **_kwargs):
            return ScriptedWebSocket(
                [
                    json.dumps(
                        {"type": "hello", "sessionId": "scripted-session"}
                    ),
                    json.dumps({"type": "ready", "ok": True}),
                ]
            )

        with patch("core.stt_session.ws_connect", side_effect=connect_once):
            await self.session._connect_and_run()
            first_generation = self.session.generation
            first_ping_task = self.session._ping_task
            await self.session._connect_and_run()

        self.assertEqual(first_generation, 2)
        self.assertEqual(self.session.generation, 3)
        self.assertIsNotNone(first_ping_task)
        self.assertTrue(first_ping_task.done())
        self.assertIsNotNone(self.session._ping_task)
        self.assertTrue(self.session._ping_task.done())
        self.assertFalse(self.session._ping_pending)
        self.assertIsNone(self.session._ping_generation)

    async def test_admission_error_before_hello_is_classified_server_busy(self) -> None:
        async def rejected_connect(*_args, **_kwargs):
            return ScriptedWebSocket(
                [
                    json.dumps(
                        {
                            "type": "error",
                            "where": "admission",
                            "message": "capacity reached",
                        }
                    )
                ]
            )

        with patch("core.stt_session.ws_connect", side_effect=rejected_connect):
            await self.session._connect_and_run()

        self.assertTrue(self.session.is_server_busy)
        self.assertEqual(self.session.last_failure_reason, "server_busy")
        self.assertEqual(self.session.reconnect_attempt, 1)
        with patch("core.stt_session.random.random", return_value=0.0):
            self.assertEqual(
                self.session._backoff_delay(),
                self.config.server_busy_min_delay,
            )

    async def test_ready_false_is_classified_server_unavailable(self) -> None:
        async def unavailable_connect(*_args, **_kwargs):
            return ScriptedWebSocket(
                [
                    json.dumps({"type": "hello", "sessionId": "unavailable"}),
                    json.dumps({"type": "ready", "ok": False}),
                ]
            )

        with patch(
            "core.stt_session.ws_connect", side_effect=unavailable_connect
        ):
            await self.session._connect_and_run()

        self.assertEqual(
            self.session.last_failure_reason,
            "server_unavailable",
        )
        self.assertEqual(self.session.reconnect_attempt, 1)


if __name__ == "__main__":
    unittest.main()
