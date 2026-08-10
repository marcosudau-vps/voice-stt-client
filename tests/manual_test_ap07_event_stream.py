"""Safe live AP07 smoke for the session-bound reliable event stream.

The smoke opens one hotkey STT session and its advertised ``/ws/logs``
connection. It does not start audio capture and does not inject text.
"""

from __future__ import annotations

import asyncio
import copy
import json

from websockets.asyncio.client import connect

from core.config import AppConfig
from core.event_models import EventConnectionState
from core.session_coordinator import DualSessionCoordinator


async def wait_for_ready(websocket, timeout: float) -> None:
    while True:
        message = json.loads(await asyncio.wait_for(websocket.recv(), timeout))
        if message.get("type") == "error":
            raise AssertionError(
                f"STT session failed: {message.get('where')}: "
                f"{message.get('message')}"
            )
        if message.get("type") == "ready":
            if message.get("ok") is not True:
                raise AssertionError("STT ready response reported ok=false")
            return


async def main() -> None:
    config = AppConfig.load()
    event_config = copy.deepcopy(config.event_stream)
    event_config.cursor_persistence_enabled = False
    states: list[EventConnectionState] = []
    live = asyncio.Event()

    def on_context_change(context) -> None:
        states.append(context.event_state)
        if context.event_state is EventConnectionState.LIVE:
            live.set()

    coordinator = DualSessionCoordinator(
        config.server,
        event_config,
        on_context_change=on_context_change,
    )
    await coordinator.begin_generation(1)
    url = config.session.build_url(config.server.url)

    try:
        async with connect(
            url,
            ping_interval=None,
            ping_timeout=None,
            proxy=None,
        ) as websocket:
            hello = json.loads(
                await asyncio.wait_for(
                    websocket.recv(), config.server.hello_timeout
                )
            )
            if hello.get("type") != "hello":
                raise AssertionError(
                    f"Expected STT hello, got {hello.get('type')!r}"
                )
            if not await coordinator.adopt_hello(1, hello):
                raise AssertionError("Server hello did not yield usable log access")

            await wait_for_ready(websocket, config.server.ready_timeout)
            await asyncio.wait_for(
                live.wait(),
                config.event_stream.connect_timeout
                + config.event_stream.handshake_timeout
                + config.event_stream.replay_timeout,
            )

            context = coordinator.context
            if context.session_id != hello.get("sessionId"):
                raise AssertionError("Event stream is not bound to the STT session")
            if context.log_access is None or not context.token_is_valid():
                raise AssertionError("Event stream access is absent or expired")
            if coordinator.active_transport_count != 1:
                raise AssertionError("Expected exactly one active event transport")
    finally:
        await coordinator.shutdown()

    required = {
        EventConnectionState.CONNECTING,
        EventConnectionState.SUBSCRIBING,
        EventConnectionState.REPLAYING,
        EventConnectionState.LIVE,
        EventConnectionState.STOPPED,
    }
    missing = required.difference(states)
    if missing:
        raise AssertionError(f"Missing event-stream states: {sorted(missing)}")
    if coordinator.active_transport_count != 0:
        raise AssertionError("Event transport remained active after shutdown")

    print(
        "AP07 EVENT STREAM LIVE SMOKE PASSED "
        "(session-bound token, replay, live, clean shutdown)"
    )


if __name__ == "__main__":
    asyncio.run(main())
