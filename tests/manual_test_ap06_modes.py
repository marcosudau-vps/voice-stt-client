"""Safe live smoke for both AP06 session modes (no start, audio or injection)."""

from __future__ import annotations

import asyncio
import json

from websockets.asyncio.client import connect

from core.config import AppConfig, OperatingMode, SessionConfig


async def check_mode(mode: OperatingMode) -> None:
    config = AppConfig.load()
    session_config = SessionConfig(mode=mode.value)
    url = session_config.build_url(config.server.url)
    expected = mode == OperatingMode.WAKE_WORD
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
                "Expected hello, got "
                f"{hello.get('type')}: {hello.get('where')}: "
                f"{hello.get('message')}"
            )
        hello_effective = hello.get("sessionConfig", {}).get(
            "effectiveWakeWordEnabled"
        )
        if hello_effective is not expected:
            raise AssertionError(
                f"{mode.value}: hello effective={hello_effective!r}"
            )
        while True:
            event = json.loads(
                await asyncio.wait_for(
                    websocket.recv(), config.server.ready_timeout
                )
            )
            if event.get("type") == "error":
                raise AssertionError(
                    f"{mode.value}: {event.get('where')}: {event.get('message')}"
                )
            if event.get("type") != "ready":
                continue
            if event.get("ok") is not True:
                raise AssertionError(f"{mode.value}: ready ok=false")
            ready_effective = event.get("sessionConfig", {}).get(
                "effectiveWakeWordEnabled"
            )
            if ready_effective is not expected:
                raise AssertionError(
                    f"{mode.value}: ready effective={ready_effective!r}"
                )
            break
    print(f"✓ {mode.value}: effectiveWakeWordEnabled={expected}")


async def main() -> None:
    for mode in OperatingMode:
        await check_mode(mode)
    print("AP06 MODE CONTRACT LIVE SMOKE PASSED")


if __name__ == "__main__":
    asyncio.run(main())
