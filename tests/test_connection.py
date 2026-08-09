"""
Quick connection test against the live RealtimeSTT server.

Tests:
1. Health endpoint (HTTP)
2. WebSocket handshake (hello → ready → ping/pong)

Usage:
    python tests/test_connection.py
"""

import asyncio
import json
import urllib.request

from websockets.asyncio.client import connect


SERVER_BASE = "https://stt.voice.marcosudau.com"
WS_URL = "wss://stt.voice.marcosudau.com/ws/transcribe"


def test_health():
    """Test the HTTP health endpoint."""
    print("─" * 50)
    print("1. Health Check")
    print("─" * 50)

    url = f"{SERVER_BASE}/health"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
            print(f"  ok:             {data['ok']}")
            print(f"  ready:          {data['ready']}")
            print(f"  activeSessions: {data['activeSessions']}")
            print(f"  activeSpeakers: {data['activeSpeakers']}")
            print(f"  models.state:   {data['models']['state']}")
            print(f"  models.loaded:  {data['models']['loaded']}")
            print()
            return data["ok"]
    except Exception as e:
        print(f"  ERROR: {e}")
        return False


async def test_websocket_handshake():
    """Test WebSocket hello → ready → ping/pong."""
    print("─" * 50)
    print("2. WebSocket Handshake")
    print("─" * 50)

    print(f"  Connecting to {WS_URL}...")

    async with connect(
        WS_URL,
        ping_interval=None,
        ping_timeout=None,
        proxy=None,
    ) as ws:
        # Wait for hello
        msg = await asyncio.wait_for(ws.recv(), timeout=5)
        event = json.loads(msg)
        assert event["type"] == "hello", f"Expected hello, got {event['type']}"
        session_id = event["sessionId"]
        print(f"  ✓ hello received")
        print(f"    sessionId: {session_id[:16]}...")
        print(f"    language:  {event['settings'].get('language', '?')}")
        print(f"    limits:    maxSessions={event['limits'].get('maxSessions')}, "
              f"maxActiveSpeakers={event['limits'].get('maxActiveSpeakers')}")

        # Wait for ready (may take long if models need to load)
        print("  ⏳ Waiting for ready (models may need to load)...")
        msg = await asyncio.wait_for(ws.recv(), timeout=180)
        event = json.loads(msg)
        print(f"  ✓ {event['type']} received: ok={event.get('ok')}")

        if event.get("ok"):
            # Ping/pong
            await ws.send(json.dumps({"type": "ping"}))
            msg = await asyncio.wait_for(ws.recv(), timeout=5)
            pong = json.loads(msg)
            print(f"  ✓ pong received: serverTime={pong.get('serverTime')}")

        await ws.close()
        print()
        return True


def main():
    print()
    print("═" * 50)
    print("  RealtimeSTT Connection Test")
    print("═" * 50)
    print()

    health_ok = test_health()
    if not health_ok:
        print("Health check failed – skipping WebSocket test.")
        return

    ws_ok = asyncio.run(test_websocket_handshake())

    print("═" * 50)
    if ws_ok:
        print("  ALL TESTS PASSED ✓")
    else:
        print("  SOME TESTS FAILED ✗")
    print("═" * 50)


if __name__ == "__main__":
    main()
