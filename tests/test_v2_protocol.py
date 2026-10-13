"""Codec assertions only; a separate script runs against pinned server code."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
import hashlib
import json
from pathlib import Path
import struct
import unittest
from uuid import UUID

from voice_stt_client.core import protocol_v2 as p
def legacy_audio_encoder(pcm, sample_rate, channels=1, frames=None):
    metadata = {"sampleRate": sample_rate}
    if channels is not None: metadata["channels"] = channels
    metadata["format"] = "pcm_s16le"
    if frames is not None: metadata["frames"] = frames
    header = json.dumps(metadata).encode("utf8")
    return struct.pack("<I", len(header)) + header + bytes(pcm)


ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = ROOT / "tests/contracts"
VECTORS = json.loads((CONTRACTS / "protocol-v2-vectors.json").read_text(encoding="utf-8"))
FIXTURES = json.loads((CONTRACTS / "protocol-v2-client-fixtures.json").read_text(encoding="utf-8"))
IDS = VECTORS["ids"]


def vector(name):
    return deepcopy(next(x["message"] for group in ("validMessages", "invalidMessages")
                         for x in VECTORS[group] if x["name"] == name))


def event(name):
    return deepcopy(next(x for x in FIXTURES["events"] if x["type"] == name))


def ack(result="applied", phase="idle"):
    return dict(type="command.ack", protocolVersion=2, sessionId=IDS["sessionId"],
                commandId=IDS["activateCommandId"], accepted=result in ("applied", "no_change"),
                result=result, activationId=None, inputPhase=phase, stateVersion=0, settingsRevision=0)


class VocabularyAndVectors(unittest.TestCase):
    def test_vocabulary_and_endpoint_match_pinned_manifest(self):
        path = ROOT / "ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/REFERENZ/KONTRAKTE/VEKTOREN/protocol-vocabulary.json"
        vocabulary = json.loads(path.read_text())
        for field, enum in (("commands", p.CommandType), ("events", p.EventType),
                            ("resultCodes", p.AckResult), ("inputPhases", p.InputPhase)):
            self.assertEqual(set(vocabulary[field]), {x.value for x in enum})
        self.assertEqual(p.WEBSOCKET_PATH, "/ws/v2")
        for name in ("start", "stop", "ready", "ping", "timeline", "status"):
            with self.subTest(name=name), self.assertRaises(p.ProtocolError):
                p.parse_client_message(dict(type=name))
            self.assertIsNone(p.decode_server_message(dict(type=name)))

    def test_vendored_vectors_are_byte_identical_and_hashed(self):
        provenance = json.loads((CONTRACTS / "protocol-v2-provenance.json").read_text())
        vendored = (ROOT / provenance["path"]).read_bytes()
        self.assertEqual(vendored, (ROOT / provenance["planningPath"]).read_bytes())
        self.assertEqual(hashlib.sha256(vendored).hexdigest(), provenance["sha256"])
        self.assertEqual(provenance["serverCommit"], "ada13b011e1d3829f78e7f389e3b927795a2b3be")

    def test_every_original_vector_is_directionally_classified(self):
        seen = []
        for item in VECTORS["validMessages"] + VECTORS["invalidMessages"]:
            with self.subTest(vector=item["name"], direction=item["direction"]):
                name, data = item["name"], item["message"]
                classification = FIXTURES["classifications"].get(name)
                seen.append(name)
                if classification in ("reject_locally", "historical_incomplete_snapshot_rejected"):
                    parser = p.parse_client_message if item["direction"] == "client_to_server" else p.decode_server_message
                    with self.assertRaises(p.ProtocolError):
                        parser(data)
                elif item["direction"] == "client_to_server":
                    encoded = p.encode_client_message(data)
                    self.assertEqual(json.loads(encoded), data)
                    # conflict is valid wire syntax, replay belongs to server.
                    if classification:
                        self.assertEqual(name, "command_id_conflict")
                else:
                    self.assertEqual(p.decode_server_message(data).to_mapping(), data)
        self.assertEqual(len(seen), 12)


class ClientMessages(unittest.TestCase):
    def test_hello_builder_and_uuid_generation(self):
        hello = p.build_hello(clientVersion="2-test", clientCommit="unknown", clientRunId=p.new_id(),
                              manual=True, wakeWord=True, wakeWordIds=["hey_jarvis"],
                              suppressManual=True, suppressWakeWord=True)
        self.assertIsInstance(hello, p.Hello)
        self.assertEqual(UUID(hello.clientRunId).version, 4)
        self.assertTrue(all(p.is_canonical_uuid(p.new_id()) for _ in range(20)))
        self.assertEqual(p.parse_client_message(json.loads(p.encode_client_message(hello))), hello)

    def test_uuid_canonical_not_version_restricted(self):
        self.assertTrue(p.is_canonical_uuid("00000000-0000-0000-0000-000000000000"))
        self.assertTrue(p.is_canonical_uuid("abcdefab-cdef-1000-8000-abcdefabcdef"))
        for bad in ("ABCDEFAB-CDEF-1000-8000-ABCDEFABCDEF", IDS["sessionId"].replace("-", ""),
                    " " + IDS["sessionId"], "{" + IDS["sessionId"] + "}", None, True, 1):
            with self.subTest(value=bad):
                self.assertFalse(p.is_canonical_uuid(bad))
                data = vector("manual_activate")
                data["commandId"] = bad
                with self.assertRaises(p.ProtocolError):
                    p.parse_client_message(data)

    def test_hello_trigger_selection_and_suppression_matrix(self):
        for manual in (False, True):
            for wake in (False, True):
                for selected in (False, True):
                    for paused in (False, True):
                        with self.subTest(manual=manual, wake=wake, selected=selected, paused=paused):
                            data = vector("hello_v2")
                            data["requestedSession"]["trigger"] = dict(manual=manual, wakeWord=wake)
                            data["requestedSession"]["wakeWordIds"] = ["hey_jarvis"] if selected else []
                            data["runtimeSuppression"] = dict(manual=paused, wakeWord=paused)
                            if (manual or wake) and selected == wake:
                                self.assertEqual(p.parse_client_message(data).to_mapping(), data)
                            else:
                                with self.assertRaises(p.ProtocolError):
                                    p.parse_client_message(data)

    def test_hello_missing_required_fields_and_bool_integer(self):
        for key in vector("hello_v2"):
            data = vector("hello_v2")
            del data[key]
            with self.subTest(missing=key), self.assertRaises(p.ProtocolError):
                p.parse_client_message(data)
        for versions in ([], [True], [2.0], ["2"], [1]):
            data = vector("hello_v2")
            data["supportedProtocolVersions"] = versions
            with self.subTest(versions=versions), self.assertRaises(p.ProtocolError):
                p.parse_client_message(data)
        for key in ("manual", "wakeWord"):
            for parent in ("trigger", "runtimeSuppression"):
                data = vector("hello_v2")
                mask = data["requestedSession"][parent] if parent == "trigger" else data[parent]
                mask[key] = 1
                with self.assertRaises(p.ProtocolError):
                    p.parse_client_message(data)

    def test_all_commands_and_controls_encode_without_rewriting(self):
        cases = [(p.CommandType.ACTIVATION, dict(action="activate", source="manual"))]
        cases += [(p.CommandType.ACTIVATION, dict(action=action, activationId=IDS["activationId"]))
                  for action in ("refresh", "finish", "cancel")]
        cases += [(p.CommandType.SUPPRESSION, dict(manual=True, wakeWord=False)),
                  (p.CommandType.AUDIO_AVAILABILITY, dict(audioAvailable=False)),
                  (p.CommandType.SETTINGS_PATCH, dict(baseSettingsRevision=0, changes={"activation.followupTimeoutMs": 4000})),
                  (p.CommandType.SNAPSHOT_REQUEST, {})]
        for kind, payload in cases:
            with self.subTest(kind=kind, payload=payload):
                command = p.build_command(kind, IDS["sessionId"], **payload)
                self.assertEqual(UUID(command.commandId).version, 4)
                wire = json.loads(p.encode_client_message(command))
                self.assertEqual({key: wire[key] for key in payload}, payload)
                self.assertIs(type(wire["protocolVersion"]), int)
                self.assertEqual(p.parse_client_message(wire), command)

    def test_forbidden_activation_field_combinations(self):
        for action in ("refresh", "finish", "cancel"):
            for source in (None, "manual", "wake_word"):
                with self.subTest(action=action, source=source), self.assertRaises(p.ProtocolError):
                    p.build_command(p.CommandType.ACTIVATION, IDS["sessionId"], action=action,
                                    source=source, activationId=IDS["activationId"])
        for fields in (dict(action="extend", activationId=IDS["activationId"]),
                       dict(action="activate", source="wake_word"),
                       dict(action="activate", source="manual", activationId=None),
                       dict(action="activate", source="manual", activationId=IDS["activationId"]),
                       dict(action="finish", activationId=None)):
            with self.subTest(fields=fields), self.assertRaises(p.ProtocolError):
                p.build_command(p.CommandType.ACTIVATION, IDS["sessionId"], **fields)

    def test_command_envelope_and_payload_negatives(self):
        for key, values in {"protocolVersion": (True, 2.0, "2", None, 1),
                            "sessionId": (None, "compact"), "commandId": (None, "compact")}.items():
            for value in values:
                data = vector("manual_activate")
                data[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(p.ProtocolError):
                    p.parse_client_message(data)
        for kind, fields in ((p.CommandType.SUPPRESSION, dict(manual=1, wakeWord=True)),
                             (p.CommandType.SUPPRESSION, dict(manual=True)),
                             (p.CommandType.AUDIO_AVAILABILITY, dict(audioAvailable=None)),
                             (p.CommandType.SETTINGS_PATCH, dict(baseSettingsRevision=True, changes={"x": 1})),
                             (p.CommandType.SETTINGS_PATCH, dict(baseSettingsRevision=0, changes={})),
                             (p.CommandType.SETTINGS_PATCH, dict(baseSettingsRevision=-1, changes={"x": 1}))):
            with self.subTest(kind=kind, fields=fields), self.assertRaises(p.ProtocolError):
                p.build_command(kind, IDS["sessionId"], **fields)

    def test_additive_fields_immutable_and_retry_string(self):
        data = vector("manual_activate")
        data["extension"] = {"nested": [1, {"future": True}]}
        parsed = p.parse_client_message(data)
        wire = p.encode_client_message(parsed)
        data["extension"]["nested"][1]["future"] = False
        self.assertTrue(parsed.payload["extension"]["nested"][1]["future"])
        with self.assertRaises(TypeError):
            parsed.payload["extension"]["x"] = 1
        with self.assertRaises(FrozenInstanceError):
            parsed.commandId = p.new_id()
        clone = parsed.to_mapping()
        clone["extension"]["nested"].clear()
        self.assertEqual(p.encode_client_message(parsed), wire)


class ServerMessages(unittest.TestCase):
    def test_all_ack_results_and_phases(self):
        for result in p.AckResult:
            for phase in p.InputPhase:
                with self.subTest(result=result, phase=phase):
                    data = ack(result, phase)
                    parsed = p.decode_server_message(data)
                    self.assertIsInstance(parsed, p.CommandAck)
                    self.assertEqual(parsed.result, result)
                    self.assertEqual(parsed.inputPhase, phase)
                    self.assertEqual(parsed.to_mapping(), data)
                    data["accepted"] = not data["accepted"]
                    with self.assertRaises(p.ProtocolError):
                        p.decode_server_message(data)

    def test_ack_error_fields_and_nullable_activation(self):
        data = ack("settings_rejected")
        data["errors"] = [dict(field="wakeWord.selection", code="wake_word_unavailable", message="synthetic", reason="unknown", wakeWordId="missing")]
        self.assertEqual(p.decode_server_message(data).to_mapping(), data)
        data["activationId"] = IDS["activationId"]
        self.assertEqual(p.decode_server_message(data).activationId, IDS["activationId"])
        del data["activationId"]
        with self.assertRaises(p.ProtocolError):
            p.decode_server_message(data)

    def test_all_18_events_and_required_field_omissions(self):
        self.assertEqual({x["type"] for x in FIXTURES["events"]}, set(p.EventType))
        for original in FIXTURES["events"]:
            with self.subTest(event=original["type"]):
                data = deepcopy(original)
                data["future"] = [None, {"a": 2}]
                parsed = p.decode_server_message(json.dumps(data))
                self.assertIs(type(parsed), p.Event)
                self.assertEqual(parsed.to_mapping(), data)
                for key in original:
                    missing = deepcopy(original)
                    del missing[key]
                    with self.subTest(missing=key), self.assertRaises(p.ProtocolError):
                        p.decode_server_message(missing)

    def test_event_bool_int_uuid_null_negatives(self):
        for key in ("eventSeq", "stateVersion", "occurredAtUnixMs", "segmentSequence"):
            for value in (True, 1.0, "1", -1, None):
                data = event("transcription.interim")
                data[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(p.ProtocolError):
                    p.decode_server_message(data)
        for key in ("sessionId", "eventId", "activationId", "segmentId"):
            data = event("transcription.completed")
            data[key] = None
            with self.subTest(key=key), self.assertRaises(p.ProtocolError):
                p.decode_server_message(data)

    def test_minimal_and_rich_interim_defensive_optional_fields(self):
        minimal = event("transcription.interim")
        self.assertEqual(p.decode_server_message(minimal).preview_text, "synthetic preview")
        rich = vector("transcription_interim_event")
        rich["timing"] = {"futureTime": 12}
        rich["internalRevision"] = {"newFormat": 1}
        rich["unknown"] = ["additive"]
        self.assertEqual(p.decode_server_message(rich).to_mapping(), rich)
        rich["displayText"] = 27
        self.assertEqual(p.decode_server_message(rich).preview_text, rich["text"])
        self.assertIsNone(p.decode_server_message(event("transcription.completed")).preview_text)

    def test_unknown_valid_event_preserves_sequence_without_domain_effect(self):
        data = event("transcription.interim")
        data["type"] = "future.event"
        for key in ("activationId", "segmentId", "segmentSequence", "text"):
            del data[key]
        data["stateVersion"] = 0
        parsed = p.decode_server_message(data)
        self.assertIsInstance(parsed, p.UnknownEvent)
        self.assertEqual(parsed.eventSeq, data["eventSeq"])
        self.assertEqual(parsed.to_mapping(), data)
        for key in ("eventId", "eventSeq", "stateVersion", "occurredAtUnixMs", "sessionId", "protocolVersion"):
            broken = deepcopy(data)
            del broken[key]
            with self.subTest(key=key), self.assertRaises(p.ProtocolError):
                p.decode_server_message(broken)
        self.assertIsNone(p.decode_server_message(dict(type="future.message", diagnostic="synthetic")))

    def test_invalid_text_frames_and_non_finite_json(self):
        for frame in (b"{}", "{broken", "[]", "null", "1", [], None,
                      '{"type":"future.event","eventSeq":NaN}',
                      {"type": "future.message", "extra": float("inf")}):
            with self.subTest(frame=frame), self.assertRaises(p.ProtocolError):
                p.decode_server_message(frame)

    def test_handshake_rejections_have_no_session_and_carry_error_details(self):
        for kind in ("protocol.incompatible", "session.rejected"):
            data = dict(type=kind, reason="synthetic", serverVersion="unknown", serverCommit="unknown", supportedProtocolVersions=[2])
            if kind == "session.rejected":
                data["errors"] = [dict(field="requestedSession", code="capacity", message="synthetic")]
            self.assertIsInstance(p.decode_server_message(data), p.HandshakeRejected)
            data["sessionId"] = None
            with self.assertRaises(p.ProtocolError):
                p.decode_server_message(data)


class SnapshotsAndSettings(unittest.TestCase):
    def test_snapshot_has_full_separate_maps_and_embedded_shape(self):
        data = deepcopy(FIXTURES["snapshot"])
        parsed = p.parse_snapshot(data)
        self.assertIsInstance(parsed, p.Snapshot)
        self.assertEqual(len(parsed.payload["requestedSettings"]), 16)
        self.assertEqual(set(parsed.payload["requestedSettings"]), set(p.SESSION_SETTING_TYPES))
        embedded = {key: value for key, value in data.items() if key != "type"}
        self.assertEqual(p.parse_snapshot(embedded, embedded=True).to_mapping(), embedded)
        with self.assertRaises(p.ProtocolError):
            p.parse_snapshot(data, embedded=True)
        for map_key in ("requestedSettings", "effectiveSettings"):
            for key in p.SESSION_SETTING_TYPES:
                broken = deepcopy(data)
                del broken[map_key][key]
                with self.subTest(map=map_key, key=key), self.assertRaises(p.ProtocolError):
                    p.parse_snapshot(broken)

    def test_snapshot_revisions_bool_and_input_null_omission(self):
        for key in ("stateVersion", "lastEventSeq", "settingsRevision"):
            for value in (True, 0.0, -1):
                data = deepcopy(FIXTURES["snapshot"])
                data[key] = value
                with self.subTest(key=key, value=value), self.assertRaises(p.ProtocolError):
                    p.parse_snapshot(data)
        for key in FIXTURES["snapshot"]["input"]:
            data = deepcopy(FIXTURES["snapshot"])
            del data["input"][key]
            with self.subTest(missing=key), self.assertRaises(p.ProtocolError):
                p.parse_snapshot(data)
        for key in ("activationId", "primarySource", "deadlineAtUnixMs", "remainingMs", "closeRequested"):
            data = deepcopy(FIXTURES["snapshot"])
            data["input"][key] = IDS["activationId"] if key == "activationId" else (True if key == "closeRequested" else 1)
            with self.subTest(key=key), self.assertRaises(p.ProtocolError):
                p.parse_snapshot(data)

    def test_snapshot_open_phases_pending_order_and_additions(self):
        for phase in list(p.InputPhase)[1:]:
            data = deepcopy(FIXTURES["snapshot"])
            data["input"].update(phase=phase, activationId=IDS["activationId"], primarySource="wake_word",
                                 deadlineAtUnixMs=None, remainingMs=None, closeRequested=phase == p.InputPhase.CLOSING_INPUT)
            pending = dict(activationId=p.new_id(), activationSequence=1, inputClosedReason="unknown_extension",
                           processingState="draining", acceptedSegmentCount=2, terminalSegmentCount=1)
            later = dict(pending, activationId=p.new_id(), activationSequence=2)
            data["pendingActivations"] = [pending, later]
            data["requestedSettings"]["future.setting"] = {"value": 1}
            self.assertEqual(p.parse_snapshot(data).to_mapping(), data)
            for entries in ([later, pending], [pending, pending], [dict(pending, activationId=IDS["activationId"])],
                            [dict(pending, activationSequence=True)]):
                broken = deepcopy(data)
                broken["pendingActivations"] = entries
                with self.subTest(phase=phase, entries=entries), self.assertRaises(p.ProtocolError):
                    p.parse_snapshot(broken)

    def test_schema_read_patch_have_distinct_forms_and_revision_scopes(self):
        schema = p.decode_settings_schema(FIXTURES["settingsSchema"])
        read = p.decode_server_settings(FIXTURES["serverSettings"])
        self.assertIsInstance(schema, p.SettingsSchema)
        self.assertEqual(len(schema.payload["settings"]), 18)
        self.assertFalse(hasattr(schema, "settingsRevision"))
        self.assertEqual(len(read.payload["settings"]), 15)
        self.assertEqual(read.revisionScope, p.RevisionScope.SERVER)
        for data, decoder in ((FIXTURES["settingsSchema"], p.decode_server_settings),
                              (FIXTURES["serverSettings"], p.decode_settings_schema),
                              (FIXTURES["snapshot"], p.decode_server_settings)):
            with self.assertRaises(p.ProtocolError):
                decoder(data)
        response = dict(accepted=True, result="applied", settingsRevision=7, changedKeys=["activation.followupTimeoutMs"],
                        values={"activation.followupTimeoutMs": 4000}, effectiveValues={"activation.followupTimeoutMs": 3000},
                        applyPolicies={"activation.followupTimeoutMs": "next_activation"})
        for scope in p.RevisionScope:
            parsed = p.decode_settings_patch_response(response, revisionScope=scope)
            self.assertEqual(parsed.revisionScope, scope)
            self.assertEqual(parsed.settingsRevision, 7)
        request = p.encode_server_settings_patch(7, response["values"])
        self.assertEqual(json.loads(request), dict(baseSettingsRevision=7, changes=response["values"]))

    def test_settings_numbers_and_maps_not_coerced(self):
        for original, decoder, value_keys in ((FIXTURES["settingsSchema"], p.decode_settings_schema, ("defaultValue",)),
                                               (FIXTURES["serverSettings"], p.decode_server_settings, ("requestedValue", "effectiveValue"))):
            for bad in (True, "5000", float("nan")):
                for key in value_keys:
                    data = deepcopy(original)
                    data["settings"][0][key] = bad
                    with self.subTest(key=key, bad=bad), self.assertRaises(p.ProtocolError):
                        decoder(data)
        for bad in (True, -1, 2.0):
            with self.assertRaises(p.ProtocolError):
                p.encode_server_settings_patch(bad, {"x": 1})
        for bad in ({}, [], {"x": float("inf")}):
            with self.assertRaises(p.ProtocolError):
                p.encode_server_settings_patch(0, bad)

    def test_hello_accepted_log_token_repr_and_unavailable(self):
        data = deepcopy(FIXTURES["helloAccepted"])
        parsed = p.decode_server_message(data)
        token = data["logAccess"]["accessToken"]
        self.assertEqual(parsed.logAccess.accessToken, token)
        for item in (parsed, parsed.logAccess, parsed.snapshot):
            self.assertNotIn(token, repr(item))
        self.assertNotIn("logAccess", parsed.payload)
        self.assertEqual(parsed.to_mapping(), data)
        data["logAccess"]["accessToken"] = "changed"
        self.assertEqual(parsed.logAccess.accessToken, token)
        data["logAccess"] = dict(available=False, code="store_unavailable", reason="synthetic")
        unavailable = p.decode_server_message(data)
        self.assertFalse(unavailable.logAccess.available)
        self.assertIsNone(unavailable.logAccess.accessToken)

    def test_log_access_shape_paths_identity_expiry_and_no_secret_errors(self):
        for key in FIXTURES["helloAccepted"]["logAccess"]:
            data = deepcopy(FIXTURES["helloAccepted"])
            del data["logAccess"][key]
            with self.subTest(missing=key), self.assertRaises(p.ProtocolError):
                p.decode_server_message(data)
        for key, value in (("websocketPath", "https://evil.example/ws/logs"),
                           ("historyPath", "//evil.example/history"),
                           ("historyPath", "/\\evil.example"),
                           ("sessionId", p.new_id()), ("expiresAt", "synthetic-memory-only-token"),
                           ("expiresAt", "2030-01-01"), ("latestCursor", True), ("logProtocolVersion", 2.0)):
            data = deepcopy(FIXTURES["helloAccepted"])
            data["logAccess"][key] = value
            with self.subTest(key=key, value=value), self.assertRaises(p.ProtocolError) as caught:
                p.decode_server_message(data)
            self.assertNotIn("synthetic-memory-only-token", str(caught.exception))
        data = deepcopy(FIXTURES["helloAccepted"])
        data["snapshot"]["sessionId"] = p.new_id()
        with self.assertRaises(p.ProtocolError):
            p.decode_server_message(data)


class AudioCodec(unittest.TestCase):
    def test_audio_exact_existing_bytes_16_48khz_mono_stereo_eight_channels(self):
        for rate in (16000, 48000):
            for channels in (1, 2, 8):
                for frames in (2, rate * 40 // 1000):
                    with self.subTest(rate=rate, channels=channels, frames=frames):
                        pcm = struct.pack("<hh", -32768, 32767) * (frames * channels // 2)
                        encoded = p.encode_audio_packet(pcm, rate, channels, frames)
                        self.assertEqual(encoded, legacy_audio_encoder(pcm, rate, channels, frames))
                        parsed = p.decode_audio_packet(encoded)
                        self.assertEqual(parsed.pcm, pcm)
                        self.assertEqual(parsed.metadata["frames"], frames)
                        self.assertEqual(struct.unpack("<I", encoded[:4])[0], len(json.dumps(dict(sampleRate=rate, channels=channels, format="pcm_s16le", frames=frames)).encode()))

    def test_audio_optional_metadata_defaults_and_byte_example(self):
        self.assertEqual(p.decode_audio_packet(p.encode_audio_packet(b"", 16000)).pcm, b"")
        with self.assertRaises(p.ProtocolError):
            p.encode_audio_packet(b"", 16000, frames=0)
        self.assertEqual(p.encode_audio_packet(b"\x00\x00", 16000),
                         legacy_audio_encoder(b"\x00\x00", 16000))
        metadata = b'{"sampleRate":16000}'
        frame = struct.pack("<I", len(metadata)) + metadata + b"\x00\x80\xff\x7f"
        self.assertEqual(p.decode_audio_packet(frame).pcm, b"\x00\x80\xff\x7f")
        for pcm in (bytearray(b"\0\0"), memoryview(b"\0\0")):
            self.assertEqual(p.encode_audio_packet(pcm, 16000), p.encode_audio_packet(b"\0\0", 16000))

    def test_audio_sample_channel_frames_limits_and_bool_rejected(self):
        for rate in (True, 0, -1, 16000.0, "16000", None):
            with self.subTest(rate=rate), self.assertRaises(p.ProtocolError):
                p.encode_audio_packet(b"\0\0", rate)
        for channels in (True, 0, 9, -1, 1.0):
            with self.subTest(channels=channels), self.assertRaises(p.ProtocolError):
                p.encode_audio_packet(b"\0\0", 16000, channels)
        for frames in (True, -1, 2.0, 0, 2):
            with self.subTest(frames=frames), self.assertRaises(p.ProtocolError):
                p.encode_audio_packet(b"\0\0", 16000, frames=frames)
        for pcm, channels in ((b"\0", 1), (b"\0\0", 2), ("pcm", 1)):
            with self.assertRaises(p.ProtocolError):
                p.encode_audio_packet(pcm, 16000, channels)
        pcm = b"\0" * p.DEFAULT_MAX_AUDIO_PACKET_BYTES
        self.assertEqual(len(p.decode_audio_packet(p.encode_audio_packet(pcm, 48000)).pcm), len(pcm))
        with self.assertRaises(p.ProtocolError):
            p.encode_audio_packet(pcm + b"\0\0", 16000)
        with self.assertRaises(p.ProtocolError):
            p.encode_audio_packet(b"\0\0", 16000, max_audio_packet_bytes=1)
        for bad_limit in (True, -1, 1.0):
            with self.assertRaises(p.ProtocolError):
                p.decode_audio_packet(b"\0\0\0\0", max_audio_packet_bytes=bad_limit)
        with self.assertRaises(p.ProtocolError):
            p.decode_audio_packet(b"\0" * (65536 + 5), max_audio_packet_bytes=0)

    def test_audio_metadata_boundary_and_invalid_binary_frames(self):
        prefix, suffix = b'{"sampleRate":16000,"extension":"', b'"}'
        metadata = prefix + b"x" * (65536 - len(prefix) - len(suffix)) + suffix
        self.assertEqual(len(metadata), 65536)
        self.assertEqual(p.decode_audio_packet(struct.pack("<I", len(metadata)) + metadata).pcm, b"")
        cases = (b"", b"123", b"VSTT", struct.pack("<I", 65537), struct.pack("<I", 5) + b"{}",
                 struct.pack("<I", 1) + b"\xff", struct.pack("<I", 2) + b"[]")
        for data in cases:
            with self.subTest(frame=data[:10]), self.assertRaises(p.ProtocolError):
                p.decode_audio_packet(data)
        for metadata in ({"sampleRate": True}, {"sampleRate": 16000, "format": "float32"},
                         {"sampleRate": 16000, "frames": 3}, {"sampleRate": 16000, "channels": 2}):
            encoded = json.dumps(metadata).encode()
            with self.subTest(metadata=metadata), self.assertRaises(p.ProtocolError):
                p.decode_audio_packet(struct.pack("<I", len(encoded)) + encoded + b"\0\0")


if __name__ == "__main__":
    unittest.main()
