from __future__ import annotations

import asyncio
import unittest
from datetime import datetime, timedelta, timezone

from core.config import EventStreamConfig, ServerConfig
from core.event_models import EventConnectionState, EventEnvelope, EventOrigin
from core.event_protocol import EventProtocolResult, EventResultKind
from core.session_coordinator import DualSessionCoordinator


class FakeEventTransport:
    instances: list["FakeEventTransport"] = []
    fail_run = False

    def __init__(
        self,
        config,
        access,
        processor,
        *,
        on_event,
        on_control,
        on_state_change,
    ) -> None:
        self.config = config
        self.access = access
        self.processor = processor
        self.on_event = on_event
        self.on_control = on_control
        self.on_state_change = on_state_change
        self.stop_calls = 0
        self._stopped = asyncio.Event()
        type(self).instances.append(self)

    async def run(self) -> None:
        self.on_state_change(EventConnectionState.REPLAYING)
        if type(self).fail_run:
            raise RuntimeError("isolated log failure")
        await self._stopped.wait()

    async def stop(self) -> None:
        self.stop_calls += 1
        self._stopped.set()


def future_expiry(hours: float = 1.0) -> str:
    return (
        datetime.now(timezone.utc) + timedelta(hours=hours)
    ).isoformat().replace("+00:00", "Z")


def hello(
    session_id: str,
    *,
    token: str = "secret-session-token",
    available: bool = True,
    expires_at: str | None = None,
) -> dict:
    access = {
        "available": available,
        "websocketPath": "/ws/logs",
        "sessionId": session_id,
        "logProtocolVersion": 2,
        "deliveryMode": "sqlite_first",
        "replayAvailable": True,
        "serverInstanceId": "server-a",
        "oldestCursor": 1,
        "latestCursor": 10,
    }
    if available:
        access["accessToken"] = token
        access["expiresAt"] = expires_at or future_expiry()
    else:
        access["code"] = "log_live_disabled"
        access["reason"] = "disabled"
    return {"type": "hello", "sessionId": session_id, "logAccess": access}


def event_result(session_id: str, event_id: str = "evt-1") -> EventProtocolResult:
    envelope = EventEnvelope.from_mapping(
        {
            "schemaVersion": 1,
            "eventId": event_id,
            "cursor": 5,
            "timestamp": "2026-08-09T10:00:00Z",
            "channel": "transcription",
            "event": "transcription.completed",
            "severity": "info",
            "serverInstanceId": "server-a",
            "sessionId": session_id,
            "data": {},
        }
    )
    return EventProtocolResult(
        kind=EventResultKind.EVENT,
        connection_state=EventConnectionState.LIVE,
        event=envelope,
        origin=EventOrigin.LIVE,
        cursor=5,
    )


class DualSessionCoordinatorTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        FakeEventTransport.instances = []
        FakeEventTransport.fail_run = False
        event_config = EventStreamConfig(cursor_persistence_enabled=False)
        self.coordinator = DualSessionCoordinator(
            ServerConfig(),
            event_config,
            transport_factory=FakeEventTransport,
        )

    async def asyncTearDown(self) -> None:
        await self.coordinator.shutdown()

    async def test_valid_hello_starts_one_session_bound_transport(self) -> None:
        await self.coordinator.begin_generation(1)
        accepted = await self.coordinator.adopt_hello(1, hello("session-1"))
        await asyncio.sleep(0)

        self.assertTrue(accepted)
        self.assertEqual(self.coordinator.context.generation, 1)
        self.assertEqual(self.coordinator.context.session_id, "session-1")
        self.assertEqual(self.coordinator.active_transport_count, 1)
        self.assertEqual(self.coordinator.transport_start_count, 1)
        self.assertNotIn("secret-session-token", repr(self.coordinator.context))
        self.assertNotIn(
            "secret-session-token",
            self.coordinator.context.log_access.endpoint,
        )

    async def test_stale_log_access_after_new_generation_is_rejected(self) -> None:
        await self.coordinator.begin_generation(2)

        accepted = await self.coordinator.adopt_hello(1, hello("stale"))

        self.assertFalse(accepted)
        self.assertEqual(self.coordinator.context.generation, 2)
        self.assertEqual(self.coordinator.transport_start_count, 0)

    async def test_stt_reconnect_during_replay_stops_old_before_new(self) -> None:
        await self.coordinator.begin_generation(1)
        await self.coordinator.adopt_hello(1, hello("session-1"))
        await asyncio.sleep(0)
        old_transport = FakeEventTransport.instances[0]
        self.assertEqual(
            self.coordinator.context.event_state,
            EventConnectionState.REPLAYING,
        )

        await self.coordinator.begin_generation(2)
        await self.coordinator.adopt_hello(2, hello("session-2", token="token-2"))

        self.assertEqual(old_transport.stop_calls, 1)
        self.assertEqual(self.coordinator.context.session_id, "session-2")
        self.assertEqual(self.coordinator.transport_start_count, 2)
        self.assertEqual(self.coordinator.transport_stop_count, 1)

    async def test_event_transport_reconnect_states_do_not_replace_session(self) -> None:
        await self.coordinator.begin_generation(3)
        await self.coordinator.adopt_hello(3, hello("dictation-session"))
        transport = FakeEventTransport.instances[0]

        transport.on_state_change(EventConnectionState.BACKOFF)
        transport.on_state_change(EventConnectionState.CONNECTING)
        transport.on_state_change(EventConnectionState.LIVE)

        self.assertEqual(self.coordinator.context.generation, 3)
        self.assertEqual(self.coordinator.context.session_id, "dictation-session")
        self.assertEqual(self.coordinator.context.event_state, EventConnectionState.LIVE)
        self.assertEqual(self.coordinator.transport_start_count, 1)

    async def test_available_false_never_starts_transport(self) -> None:
        await self.coordinator.begin_generation(1)

        accepted = await self.coordinator.adopt_hello(
            1,
            hello("session-1", available=False),
        )

        self.assertFalse(accepted)
        self.assertEqual(
            self.coordinator.context.event_state,
            EventConnectionState.UNAVAILABLE,
        )
        self.assertEqual(
            self.coordinator.context.unavailable_code,
            "log_live_disabled",
        )
        self.assertEqual(self.coordinator.active_transport_count, 0)

    async def test_expired_token_never_starts_transport(self) -> None:
        await self.coordinator.begin_generation(1)

        accepted = await self.coordinator.adopt_hello(
            1,
            hello("session-1", expires_at=future_expiry(-1)),
        )

        self.assertFalse(accepted)
        self.assertEqual(
            self.coordinator.context.unavailable_code,
            "log_access_expired",
        )

    async def test_active_token_expiry_stops_transport_without_orphan_task(self) -> None:
        expired = asyncio.Event()

        def context_changed(context) -> None:
            if context.unavailable_code == "log_access_expired":
                expired.set()

        self.coordinator.on_context_change = context_changed
        await self.coordinator.begin_generation(1)
        await self.coordinator.adopt_hello(
            1,
            hello("session-1", expires_at=future_expiry(0.00001)),
        )
        transport = FakeEventTransport.instances[0]

        await asyncio.wait_for(expired.wait(), timeout=0.5)

        self.assertEqual(transport.stop_calls, 1)
        self.assertEqual(self.coordinator.active_transport_count, 0)
        self.assertEqual(
            self.coordinator.context.event_state,
            EventConnectionState.UNAVAILABLE,
        )
        self.assertEqual(
            self.coordinator.transport_start_count,
            self.coordinator.transport_stop_count,
        )

    async def test_invalid_expiry_and_missing_token_never_start_transport(self) -> None:
        for mutate in (
            lambda payload: payload["logAccess"].update(expiresAt="not-a-time"),
            lambda payload: payload["logAccess"].pop("accessToken"),
        ):
            with self.subTest(mutate=mutate):
                coordinator = DualSessionCoordinator(
                    ServerConfig(),
                    EventStreamConfig(cursor_persistence_enabled=False),
                    transport_factory=FakeEventTransport,
                )
                self.addAsyncCleanup(coordinator.shutdown)
                await coordinator.begin_generation(1)
                payload = hello("session-1")
                mutate(payload)

                with self.assertRaises(ValueError):
                    await coordinator.adopt_hello(1, payload)

                self.assertEqual(coordinator.transport_start_count, 0)
                self.assertEqual(coordinator.active_transport_count, 0)

    async def test_session_mismatch_is_rejected_before_connect(self) -> None:
        payload = hello("session-1")
        payload["logAccess"]["sessionId"] = "other-session"
        await self.coordinator.begin_generation(1)

        with self.assertRaisesRegex(ValueError, "does not match"):
            await self.coordinator.adopt_hello(1, payload)

        self.assertEqual(self.coordinator.transport_start_count, 0)

    async def test_stale_live_event_is_rejected_after_session_switch(self) -> None:
        accepted_events: list[str] = []

        async def accept(context, result) -> bool:
            accepted_events.append(result.event.event_id)
            return True

        self.coordinator.on_event = accept
        await self.coordinator.begin_generation(1)
        await self.coordinator.adopt_hello(1, hello("session-1"))
        old_transport = FakeEventTransport.instances[0]
        await self.coordinator.begin_generation(2)
        await self.coordinator.adopt_hello(2, hello("session-2", token="token-2"))

        stale_accepted = await old_transport.on_event(event_result("session-1"))
        current_accepted = await FakeEventTransport.instances[1].on_event(
            event_result("session-2", "evt-2")
        )

        self.assertFalse(stale_accepted)
        self.assertTrue(current_accepted)
        self.assertEqual(accepted_events, ["evt-2"])

    async def test_inflight_old_event_cannot_confirm_after_session_switch(self) -> None:
        callback_started = asyncio.Event()
        release_callback = asyncio.Event()

        async def delayed_accept(context, result) -> bool:
            callback_started.set()
            await release_callback.wait()
            return True

        self.coordinator.on_event = delayed_accept
        await self.coordinator.begin_generation(1)
        await self.coordinator.adopt_hello(1, hello("session-1"))
        old_transport = FakeEventTransport.instances[0]
        delivery = asyncio.create_task(
            old_transport.on_event(event_result("session-1"))
        )
        await callback_started.wait()

        await self.coordinator.begin_generation(2)
        await self.coordinator.adopt_hello(2, hello("session-2", token="token-2"))
        release_callback.set()

        self.assertFalse(await delivery)

    async def test_shutdown_during_two_hello_connects_leaves_no_task(self) -> None:
        await self.coordinator.begin_generation(1)

        first = asyncio.create_task(
            self.coordinator.adopt_hello(1, hello("session-1", token="token-1"))
        )
        second = asyncio.create_task(
            self.coordinator.adopt_hello(1, hello("session-1", token="token-2"))
        )
        stopping = asyncio.create_task(self.coordinator.shutdown())
        await asyncio.gather(first, second, stopping)

        self.assertEqual(self.coordinator.active_transport_count, 0)
        self.assertEqual(
            self.coordinator.transport_start_count,
            self.coordinator.transport_stop_count,
        )
        self.assertTrue(all(item.stop_calls == 1 for item in FakeEventTransport.instances))

    async def test_event_stream_failure_is_isolated_and_visible(self) -> None:
        FakeEventTransport.fail_run = True
        await self.coordinator.begin_generation(1)

        await self.coordinator.adopt_hello(1, hello("session-1"))
        await asyncio.sleep(0)
        await asyncio.sleep(0)

        self.assertEqual(
            self.coordinator.context.event_state,
            EventConnectionState.DEGRADED,
        )
        self.assertEqual(self.coordinator.active_transport_count, 0)

    async def test_concurrent_shutdown_stops_transport_exactly_once(self) -> None:
        await self.coordinator.begin_generation(1)
        await self.coordinator.adopt_hello(1, hello("session-1"))
        transport = FakeEventTransport.instances[0]

        await asyncio.gather(
            self.coordinator.shutdown(),
            self.coordinator.shutdown(),
            self.coordinator.shutdown(),
        )

        self.assertEqual(transport.stop_calls, 1)
        self.assertEqual(self.coordinator.transport_stop_count, 1)
        self.assertEqual(self.coordinator.active_transport_count, 0)
        self.assertEqual(
            self.coordinator.context.event_state,
            EventConnectionState.STOPPED,
        )


if __name__ == "__main__":
    unittest.main()
