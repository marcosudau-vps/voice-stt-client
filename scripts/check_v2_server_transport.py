"""Actual V2STTSession over loopback TCP/WebSocket to the pinned server app.

Use a separate git archive export of ada13b0. All imported server sources are
byte-verified. The production endpoint, admission, controller, ledger, command
cache and projection run unchanged; only recorder/models/scheduler and the
not-yet-delivered client settings/audio bootstrap are named test boundaries.
No server product edit, hardware, live service or user data is used.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
from unittest.mock import patch

CLIENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLIENT_ROOT))
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.command_tracker import TransportLost
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig, V2TransportState

SERVER_SHA = "ada13b011e1d3829f78e7f389e3b927795a2b3be"


async def until(predicate, timeout=10):
    async def poll():
        while not predicate():
            await asyncio.sleep(.01)
    await asyncio.wait_for(poll(), timeout)


def verify_sources(root, repository):
    hashes = {}
    paths = {Path(module.__file__).resolve() for module in tuple(sys.modules.values())
             if getattr(module, "__file__", None)}
    for path in sorted(paths):
        if not path.is_relative_to(root) or path.suffix != ".py":
            continue
        relative = path.relative_to(root).as_posix()
        pinned = subprocess.check_output(["git", "-C", str(repository), "show", f"{SERVER_SHA}:{relative}"])
        actual = path.read_bytes()
        if actual != pinned:
            raise AssertionError(f"server source differs: {relative}")
        hashes[relative] = hashlib.sha256(actual).hexdigest()
    if "api_fastapi_server/server.py" not in hashes:
        raise AssertionError("actual server app not loaded")
    return hashes


async def run(root, repository):
    sys.path.insert(0, str(root))
    import uvicorn
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import AutoScheduler
    from websockets.asyncio.client import connect
    from websockets.exceptions import ConnectionClosed

    # Reject altered sources before starting any server service. A second check
    # at the end includes modules loaded lazily by create_app/domain admission.
    verify_sources(root, repository)

    checks, trace = [], []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    with tempfile.TemporaryDirectory(prefix="cv2-020-server-data-") as data_root, patch.dict(
            os.environ, {"VOICESTT_SERVER_COMMIT": SERVER_SHA}):
        settings = ServerSettings(data_root_path=data_root, max_sessions=1, model_warmup=False,
                                  request_logging_enabled=False, performance_logging_enabled=False,
                                  performance_log_mirror_enabled=False, transcription_logging_enabled=False,
                                  system_event_logging_enabled=False, event_store_enabled=False, log_live_enabled=False)
        app = create_app(settings, recorder_factory=GateAwareRecorder, scheduler_factory=AutoScheduler)
        tcp = socket.socket()
        tcp.bind(("127.0.0.1", 0))
        tcp.listen(16)
        port = tcp.getsockname()[1]
        server = uvicorn.Server(uvicorn.Config(app, log_level="error", access_log=False))
        serving = asyncio.create_task(server.serve(sockets=[tcp]))
        sessions, tasks = [], []
        try:
            await until(lambda: server.started or serving.done())
            if serving.done():
                await serving
                raise AssertionError("server not started")
            url = f"ws://127.0.0.1:{port}/ws/v2"
            # Direct initial frame probes use the actual endpoint rejection.
            for name, wire in (("binary_first", b"\0\0"), ("invalid_first", "[]")):
                async with connect(url) as raw:
                    await raw.send(wire)
                    try:
                        await asyncio.wait_for(raw.recv(), 2)
                    except ConnectionClosed as exc:
                        check(f"server/{name}/4400", exc.rcvd.code == 4400)
                    else:
                        raise AssertionError("initial frame unexpectedly admitted")

            ready = asyncio.Event()
            async def test_bootstrap(client, binding):
                check("bootstrap/audio_gated", not await client.send_audio(b"\0\0", 16000))
                check("bootstrap/hello_suppressed", all(binding.accepted.snapshot.payload["trigger"]["suppressed"].values()))
                await ready.wait()
                await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=False)
                await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=True)

            client = V2STTSession(V2TransportConfig(url=url), bootstrap=test_bootstrap)
            messages, completions = [], []
            client.on_message = lambda binding, message: messages.append((binding, message))
            client.on_completion = completions.append
            client.on_status = lambda status: trace.append(dict(state=str(status.state), generation=status.generation,
                                                                reason=status.reason))
            sessions.append(client)
            tasks.append(asyncio.create_task(client.run()))
            await until(lambda: client.binding is not None)
            admitted = client.binding
            check("hello/real_server_commit", admitted.accepted.payload["serverCommit"] == SERVER_SHA)
            check("hello/session_uuid", p.is_canonical_uuid(admitted.session_id))
            check("hello/log_store_unavailable_still_admitted", not admitted.accepted.logAccess.available)
            check("hello/configuring_not_ready", client.status.state == V2TransportState.CONFIGURING)
            ready.set()
            await until(lambda: client.is_ready)
            check("bootstrap/availability_and_suppression_acks", len(completions) == 3 and all(x.ack.accepted for x in completions))
            completion = await client.request(p.CommandType.SNAPSHOT_REQUEST)
            await until(lambda: any(isinstance(message, p.Snapshot) for _, message in messages))
            snapshot = next(message for _, message in messages if isinstance(message, p.Snapshot))
            check("snapshot/ack_same_session", completion.ack.sessionId == snapshot.sessionId == admitted.session_id)
            check("snapshot/typed_actual_state", snapshot.payload["audioAvailable"] and not snapshot.payload["trigger"]["suppressed"]["manual"])
            check("snapshot/command_uuid", p.is_canonical_uuid(completion.command.commandId))

            # Real capacity refusal while the first session owns the slot.
            async def no_settings(client, binding):
                pass
            limited = V2STTSession(V2TransportConfig(url=url), bootstrap=no_settings, jitter=lambda a, b: 1)
            sessions.append(limited)
            tasks.append(asyncio.create_task(limited.run()))
            await until(lambda: limited.status.state in (V2TransportState.BACKOFF, V2TransportState.BLOCKED))
            check("admission/capacity_long_backoff", limited.status.reason == "session_limit_reached" and limited.status.retry_delay >= 10)
            await limited.stop()

            # Actual manual activation/finish: server event ordering may lead ack.
            activated = await client.request(p.CommandType.ACTIVATION, action="activate", source="manual")
            check("commands/activate_ack", activated.ack.accepted and p.is_canonical_uuid(activated.ack.activationId))
            finished = await client.request(p.CommandType.ACTIVATION, action="finish", activationId=activated.ack.activationId)
            check("commands/finish_correlated", finished.ack.commandId == finished.command.commandId)
            check("commands/domain_events_received", any(isinstance(message, p.Event) for _, message in messages))
            await client.stop()
            await until(lambda: not app.state.voicestt_service.metrics()["sessions"])
            check("disconnect/no_pending_or_callbacks", client.pending_count == 0 and client.binding is None and client._receiver is None)
            check("disconnect/server_slot_released", not app.state.voicestt_service.metrics()["sessions"])
            try:
                await client.request(p.CommandType.SNAPSHOT_REQUEST, binding=admitted)
            except TransportLost:
                check("disconnect/old_binding_rejected", True)
            else:
                raise AssertionError("old session command sent")

            # Syntactically valid hello, atomically rejected by actual selection.
            rejected = V2STTSession(V2TransportConfig(url=url, wake_word=True,
                                                     wake_word_ids=("synthetic_missing_wake_word",)), bootstrap=no_settings)
            sessions.append(rejected)
            tasks.append(asyncio.create_task(rejected.run()))
            await until(lambda: rejected.status.state == V2TransportState.BLOCKED)
            check("admission/config_rejection_no_loop", rejected.generation == 1 and rejected.status.reason == "session_configuration_rejected")
            await until(lambda: not app.state.voicestt_service.metrics()["sessions"])
            check("admission/rejection_no_slot_leak", not app.state.voicestt_service.metrics()["sessions"])
            hashes = verify_sources(root, repository)
            return dict(result="PASS", serverCommit=SERVER_SHA, clientHead=subprocess.check_output(
                ["git", "-C", str(CLIENT_ROOT), "rev-parse", "HEAD"], text=True).strip(),
                        runtime=dict(python=sys.version, executable=sys.executable, platform=platform.platform(),
                                     uvicorn=uvicorn.__version__), sourceHashes=hashes,
                        checks=checks, checkCount=len(checks), transportTrace=trace,
                        boundaries="Real loopback TCP/WebSocket and production FastAPI app, admission/controller/ledger/replay/projection. Same process asyncio loops; pinned GateAwareRecorder/AutoScheduler replace only hardware/models. Named bootstrap supplies availability; real settings/audio/Qt composition remains AP040/070/100. No ASR/hardware/live claim.")
        finally:
            for client in sessions:
                await client.stop()
            await asyncio.gather(*tasks, return_exceptions=True)
            server.should_exit = True
            try:
                await asyncio.wait_for(serving, 10)
            finally:
                tcp.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-root", required=True, type=Path)
    parser.add_argument("--server-repository", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.server_root.resolve(), args.server_repository.resolve())), indent=2))


if __name__ == "__main__":
    main()
