"""AP-CV2-010: actual client codec against byte-verified ada13b0 server code.

Run in the client venv with a separate read-only server source export/checkout.
No server runtime dependencies, models, socket, persistence or live service.
Package containers bypass only eager __init__ imports. All tested logic is
loaded unmodified from the pinned source. Two audio functions are compiled
unchanged from their AST to avoid importing the model-heavy server entrypoint.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import importlib
import json
import math
from pathlib import Path
import platform
import struct
import subprocess
import sys
from types import ModuleType, SimpleNamespace

import numpy as np

# Direct script execution must resolve this source checkout, not an installation.
CLIENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLIENT_ROOT))
from voice_stt_client.core import protocol_v2 as client


SERVER_SHA = "ada13b011e1d3829f78e7f389e3b927795a2b3be"
SOURCE_FILES = [
    "api_fastapi_server/activation.py", "api_fastapi_server/activation_commands.py",
    "api_fastapi_server/segment_ledger.py", "api_fastapi_server/settings_control.py",
    "api_fastapi_server/protocol.py", "api_fastapi_server/server.py",
    *[f"api_fastapi_server/protocol_v2/{name}.py" for name in (
        "schema", "commands", "handshake", "snapshot", "session", "events", "identity", "ports", "connection")],
    "VoiceSTT/_version.py", "tests/contracts/protocol-v2-vectors.json",
]


def verify_sources(server_root, repository):
    hashes = {}
    for path in SOURCE_FILES:
        pinned = subprocess.check_output(["git", "-C", str(repository), "show", f"{SERVER_SHA}:{path}"])
        actual = (server_root / path).read_bytes()
        if actual != pinned:
            raise AssertionError(f"source differs from pinned commit: {path}")
        hashes[path] = hashlib.sha256(actual).hexdigest()
    vendored = (CLIENT_ROOT / "tests/contracts/protocol-v2-vectors.json").read_bytes()
    if vendored != (server_root / "tests/contracts/protocol-v2-vectors.json").read_bytes():
        raise AssertionError("client vectors differ from actual server")
    return hashes


def package(name, path):
    module = ModuleType(name)
    module.__path__ = [str(path)]
    sys.modules[name] = module


def load_server(server_root):
    package("_cv2_server", server_root / "api_fastapi_server")
    package("_cv2_server.protocol_v2", server_root / "api_fastapi_server/protocol_v2")
    package("VoiceSTT", server_root / "VoiceSTT")
    modules = {}
    for name in ("protocol", "activation", "activation_commands", "segment_ledger", "settings_control",
                 "protocol_v2.schema", "protocol_v2.commands", "protocol_v2.handshake", "protocol_v2.snapshot",
                 "protocol_v2.session", "protocol_v2.events", "protocol_v2.connection"):
        modules[name.rsplit(".", 1)[-1]] = importlib.import_module(f"_cv2_server.{name}")
    # Actual production audio validation/resampling with NumPy; no recorder.
    tree = ast.parse((server_root / "api_fastapi_server/server.py").read_text(encoding="utf-8-sig"))
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name in ("packet_to_server_samples", "resample_int16"):
            functions.append(node)
    if len(functions) != 2:
        raise AssertionError("expected exact production audio seams")
    namespace = {"np": np, "math": math, "SERVER_SAMPLE_RATE": 16000,
                 "AudioPacketError": modules["protocol"].AudioPacketError,
                 "require_positive_int": modules["protocol"].require_positive_int}
    exec(compile(ast.Module(body=functions, type_ignores=[]), "pinned-server.py/audio-seams", "exec"), namespace)
    modules["packet_to_server_samples"] = namespace["packet_to_server_samples"]
    return modules


def run(server_root, repository):
    hashes = verify_sources(server_root, repository)
    server = load_server(server_root)
    checks = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    vectors = json.loads((CLIENT_ROOT / "tests/contracts/protocol-v2-vectors.json").read_text())
    fixtures = json.loads((CLIENT_ROOT / "tests/contracts/protocol-v2-client-fixtures.json").read_text())
    ids = vectors["ids"]
    schema = server["schema"]
    for enum, actual in ((client.CommandType, schema.COMMAND_TYPES), (client.EventType, schema.EVENT_TYPES),
                         (client.InputPhase, schema.INPUT_PHASES), (client.AckResult, schema.RESULT_CODES)):
        check(f"vocabulary/{enum.__name__}", set(enum) == set(actual))
    for value in (client.new_id(), "00000000-0000-0000-0000-000000000000", "invalid", ids["sessionId"].replace("-", "")):
        check(f"uuid/{len(checks)}", client.is_canonical_uuid(value) == schema.is_canonical_uuid(value))

    # Selection boundary only: no real wake models/catalog admission claimed.
    selection_port = SimpleNamespace(resolve_selection=lambda ids: (SimpleNamespace(ids=ids), []))
    replay = server["activation_commands"].CommandReplayCache()
    for item in vectors["validMessages"] + vectors["invalidMessages"]:
        name, data = item["name"], item["message"]
        if item["direction"] == "server_to_client":
            if name == "idle_snapshot":
                try:
                    client.decode_server_message(data)
                except client.ProtocolError:
                    check("vector/idle_snapshot/historical_incomplete_rejected", True)
                else:
                    raise AssertionError("incomplete vector treated as actual snapshot")
            else:
                check(f"vector/{name}/decode", client.decode_server_message(data).to_mapping() == data)
            continue
        if data["type"] == "hello":
            result = server["handshake"].parse_hello(data, server_version="2-test", server_commit=SERVER_SHA)
            check(f"vector/{name}/server_envelope", result.accepted)
            errors = server["handshake"].validate_requested_session(result.hello, selection_port)
            if "expectedErrorCode" in item:
                check(f"vector/{name}/server_rejection", any(x["code"] == item["expectedErrorCode"] for x in errors))
                try:
                    client.encode_client_message(data)
                except client.ProtocolError:
                    check(f"vector/{name}/client_rejection", True)
                else:
                    raise AssertionError("invalid Hello encoded")
            else:
                wire = json.loads(client.encode_client_message(data))
                check(f"vector/{name}/actual_client_hello", not errors and
                      server["handshake"].parse_hello(wire, server_version="2-test", server_commit=SERVER_SHA).accepted)
            continue
        parsed = server["commands"].parse_command(data, session_id=ids["sessionId"])
        if item.get("expectedAck", {}).get("result") == "invalid_payload":
            check(f"vector/{name}/actual_server_invalid_payload", parsed.rejection == "invalid_payload")
            try:
                client.encode_client_message(data)
            except client.ProtocolError:
                check(f"vector/{name}/actual_client_rejection", True)
            else:
                raise AssertionError("invalid command encoded")
        else:
            wire = json.loads(client.encode_client_message(data))
            parsed = server["commands"].parse_command(wire, session_id=ids["sessionId"])
            check(f"vector/{name}/actual_client_command", not parsed.rejected)
            lookup = replay.lookup(parsed.command_id, parsed.payload_key)
            expected = "conflict" if name == "command_id_conflict" else ("replay" if name == "manual_activate_replay" else "miss")
            check(f"vector/{name}/real_replay_cache", lookup.state == expected)
            replay.store(parsed.command_id, parsed.payload_key, {"result": "applied"})

    for kind, fields in ((client.CommandType.SUPPRESSION, dict(manual=True, wakeWord=False)),
                         (client.CommandType.AUDIO_AVAILABILITY, dict(audioAvailable=False)),
                         (client.CommandType.SNAPSHOT_REQUEST, {}),
                         (client.CommandType.SETTINGS_PATCH, dict(baseSettingsRevision=0, changes={"activation.followupTimeoutMs": 4000})),
                         *[(client.CommandType.ACTIVATION, dict(action=action, activationId=ids["activationId"]))
                           for action in ("refresh", "finish", "cancel")]):
        command = client.build_command(kind, ids["sessionId"], **fields)
        parsed = server["commands"].parse_command(json.loads(client.encode_client_message(command)), session_id=ids["sessionId"])
        check(f"command/{kind}/{fields.get('action', '')}", not parsed.rejected)
    for bad in (None, [], {"type": "hello"}, {"type": "unknown"}):
        check(f"ignored/{len(checks)}", server["commands"].parse_command(bad, session_id=ids["sessionId"]) is None)
    for bad in ({**vectors["validMessages"][1]["message"], "commandId": "bad"},
                {**vectors["validMessages"][1]["message"], "protocolVersion": True}):
        parsed = server["commands"].parse_command(bad, session_id=ids["sessionId"])
        check(f"envelope_rejection/{len(checks)}", parsed.rejection == "invalid_payload")
        check(f"envelope_ack_identity/{len(checks)}", (parsed.command_id is None) == (bad.get("commandId") == "bad"))
    tolerant = {**vectors["validMessages"][1]["message"], "protocolVersion": 2.0}
    check("server_version_2_float_tolerance", not server["commands"].parse_command(tolerant, session_id=ids["sessionId"]).rejected)

    registry = server["settings_control"].SettingsRegistry()
    check("registry/16_session_keys", registry.session_keys() == client.SESSION_SETTING_TYPES.keys())
    exported_schema = dict(protocolVersion=2, serverVersion="unknown", serverCommit=SERVER_SHA,
                           secretsExposed=False, settings=registry.schema_payload())
    check("registry/actual_schema", len(client.decode_settings_schema(exported_schema).payload["settings"]) == 18)
    server_settings = server["settings_control"].ServerSettingsState(registry)
    read = client.decode_server_settings(server_settings.server_public(server_commit=SERVER_SHA))
    check("registry/server_defaults", len(read.payload["settings"]) == 15 and read.revisionScope == client.RevisionScope.SERVER)
    session_settings = server["settings_control"].SessionSettingsState(registry)
    for scope, state, patch_method in ((client.RevisionScope.SERVER, server_settings, server_settings.patch_server),
                                       (client.RevisionScope.SESSION, session_settings, session_settings.apply_patch)):
        for base, changes in ((0, {"activation.followupTimeoutMs": 4000}),
                              (1, {"activation.followupTimeoutMs": 4000}),
                              (0, {"activation.followupTimeoutMs": 5000}),
                              (1, {"activation.followupTimeoutMs": True}),
                              (1, {"activation.segmentWatchdogRefreshMs": 30000})):
            request = json.loads(client.encode_server_settings_patch(base, changes))
            actual = patch_method(request["baseSettingsRevision"], request["changes"])
            decoded = client.decode_settings_patch_response(actual.to_dict(), revisionScope=scope)
            check(f"registry/patch/{scope}/{actual.result}/{len(checks)}", decoded.result == actual.result and
                  decoded.settingsRevision == state.settings_revision and decoded.revisionScope == scope)

    controller = server["activation"].ActivationController(id_factory=schema.new_canonical_id)
    ledger = server["segment_ledger"].SegmentLedger(ids["sessionId"])
    state = server["session"].ProtocolSessionState(ids["sessionId"])
    wake_port = SimpleNamespace(capabilities=lambda: dict(catalogRevision=1, availableWakeWordIds=["hey_jarvis"]))
    for active in (False, True):
        if active:
            controller.activate("manual", activation_id=ids["activationId"])
        snapshot = server["snapshot"].build_snapshot(state=state, controller=controller, ledger=ledger,
            audio_available=True, settings_port=session_settings, wake_word_port=wake_port,
            server_version="2-test", server_commit=SERVER_SHA)
        parsed = client.decode_server_message(json.dumps(snapshot))
        check(f"snapshot/actual_{'open' if active else 'idle'}", parsed.to_mapping() == json.loads(json.dumps(snapshot)) and
              len(parsed.payload["effectiveSettings"]) == 16)

    connection = server["connection"].ProtocolV2Connection(SimpleNamespace(), server_version="2-test", server_commit=SERVER_SHA)
    connection.state = state
    for result in schema.RESULT_CODES:
        for phase in schema.INPUT_PHASES:
            connection.session = SimpleNamespace(activation_snapshot=lambda phase=phase: {"phase": phase, "activationId": None})
            actual = connection._emit_ack(ids["activateCommandId"], result)
            parsed = client.decode_server_message(actual)
            check(f"ack/production_projection/{result}/{phase}", parsed.result == result and parsed.inputPhase == phase)

    context = server["events"].ProjectionContext(phase="waiting_first_speech", activation_id=ids["activationId"],
        activation_sequence=1, primary_source="manual", effective_settings=dict(session_settings.settings_projection().effective_settings),
        active_segment_id=ids["segmentId"], active_segment_sequence=1)
    produced = set()
    for legacy, mapped in server["events"].LEGACY_EVENT_TYPES.items():
        payload = dict(activationId=ids["activationId"], activationSequence=1, segmentId=ids["segmentId"],
                       segmentSequence=1, text="synthetic", reason="synthetic_reason", state="completed",
                       catalogRevision=1, availableWakeWordIds=["hey_jarvis"], wakeWordId="hey_jarvis")
        if legacy == "activation_drained":
            states = ("completed", "cancelled", "failed")
        else:
            states = ("completed",)
        for terminal in states:
            payload["state"] = terminal
            # Each mutually exclusive terminal sample gets its own wire state;
            # production memoizes the first terminal identity for one segment.
            sample_state = server["session"].ProtocolSessionState(ids["sessionId"])
            projector = server["events"].EventProjector(sample_state)
            for actual in projector.project(legacy, payload, context):
                parsed = client.decode_server_message(json.dumps(actual))
                check(f"event/production_projection/{actual['type']}/{len(checks)}", parsed.to_mapping() == json.loads(json.dumps(actual)))
                produced.add(actual["type"])
    actual = state.mint_event("activation.trigger_suppressed")
    actual.update(source="manual", reason="trigger_suppressed")
    check("event/production_envelope/trigger_suppressed", client.decode_server_message(actual).type == actual["type"])
    produced.add(actual["type"])
    actual = state.mint_event("settings.changed")
    actual.update(settingsRevision=1, scope="session", changedKeys=["activation.followupTimeoutMs"], applyPolicy="next_activation")
    check("event/production_envelope/settings_changed", client.decode_server_message(actual).type == actual["type"])
    produced.add(actual["type"])
    check("events/all_18_server_generated", produced == set(client.EventType))

    service = SimpleNamespace(settings=SimpleNamespace(max_audio_packet_bytes=524288))
    for rate in (16000, 48000):
        for channels in (1, 2, 8):
            frames = rate * 40 // 1000
            pcm = struct.pack("<h", 1000) * frames * channels
            frame = client.encode_audio_packet(pcm, rate, channels, frames)
            actual = server["protocol"].decode_audio_packet(frame)
            check(f"audio/framing/{rate}/{channels}", actual.audio == pcm and actual.metadata["sampleRate"] == rate)
            samples = server["packet_to_server_samples"](service, actual)
            check(f"audio/production_validation_resample/{rate}/{channels}", samples.size == 640 and samples.dtype == np.int16)
    for metadata, pcm in (({"sampleRate": True}, b"\0\0"), ({"sampleRate": 16000, "frames": 0}, b""),
                          ({"sampleRate": 16000, "channels": 9}, b"\0\0"),
                          ({"sampleRate": 16000, "frames": 2}, b"\0\0"),
                          ({"sampleRate": 16000, "format": "float32"}, b"\0\0")):
        encoded = json.dumps(metadata).encode()
        frame = struct.pack("<I", len(encoded)) + encoded + pcm
        for name, validator in (("server", lambda: server["packet_to_server_samples"](service, server["protocol"].decode_audio_packet(frame))),
                                ("client", lambda: client.decode_audio_packet(frame))):
            try:
                validator()
            except (server["protocol"].AudioPacketError, client.ProtocolError):
                check(f"audio/invalid/{name}/{len(checks)}", True)
            else:
                raise AssertionError(f"invalid audio accepted by {name}")

    return dict(result="PASS", serverCommit=SERVER_SHA, clientModule=str(Path(client.__file__).resolve()),
                runtime=dict(python=sys.version, executable=sys.executable, platform=platform.platform()),
                serverSourceSHA256=hashes, checks=checks, checkCount=len(checks),
                boundaries="Pure server parser/registry/replay/controller/ledger/projector/ack projection; unchanged AST audio validation/resampling. Selection and catalog capabilities are controlled adapters. No WebSocket, model, microphone, runtime settings persistence or UI claim.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-root", required=True, type=Path)
    parser.add_argument("--server-repository", required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.server_root.resolve(), args.server_repository.resolve()), indent=2))


if __name__ == "__main__":
    main()
