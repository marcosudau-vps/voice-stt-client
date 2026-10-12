"""Settings authority, atomic profile migration, bootstrap faults and races."""
import asyncio
from copy import deepcopy
from dataclasses import asdict
import json
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.error import URLError

import yaml

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.command_tracker import TransportLost
from voice_stt_client.core.config import AppConfig
from voice_stt_client.core.settings_service import (
    HttpResponse, NA_KEYS, SERVER_DEFAULT_KEYS, SESSION_KEYS, Setting, SettingsError,
    SettingsHTTP, SettingsService, WakeCatalog,
)
from voice_stt_client.core.v2_profile import V2Profile, migrate_config_file, migrate_profile, seconds_to_ms
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from tests.test_v2_protocol import FIXTURES, ack, event
from tests.test_v2_transport import FakeWebSocket, until


KEY = "activation.followupTimeoutMs"
SCHEMA = FIXTURES["settingsSchema"]
SERVER = FIXTURES["serverSettings"]


def catalog_body(revision=1):
    def entry(key, alias):
        return dict(id=key, displayName=alias, aliases=[alias.lower()], artifactVersion="1", available=True,
            catalogRevision=revision, backends={name: dict(available=True) for name in ("onnx", "tflite")})
    return dict(protocolVersion=2, catalogRevision=revision, wakeWords=[entry("hey_jarvis", "Jarvis"), entry("alexa", "Alexa")])


class FakeHTTP:
    def __init__(self):
        self.schema, self.server, self.catalog = deepcopy(SCHEMA), deepcopy(SERVER), catalog_body()
        self.server["serverVersion"] = self.schema["serverVersion"]
        self.calls = []
        self.patch_status = 200
        self.fail_path = None
        self.hook = None
        self.unknown_after_apply = False

    async def request(self, method, path, *, body=None, admin_key=None):
        self.calls.append((method, path, deepcopy(body)))  # Never retain admin secrets.
        if self.hook:
            await self.hook(method, path)
        if path == self.fail_path:
            raise SettingsError("synthetic_http_failure")
        if method == "GET":
            return HttpResponse(200, deepcopy(self.schema if path.endswith("schema") else self.server if path.endswith("server") else self.catalog))
        if self.patch_status != 200:
            return HttpResponse(self.patch_status, {})
        changed = []
        for entry in self.server["settings"]:
            key = entry["key"]
            if key in body["changes"] and entry["requestedValue"] != body["changes"][key]:
                entry["requestedValue"] = entry["effectiveValue"] = body["changes"][key]
                changed.append(key)
        if changed:
            self.server["settingsRevision"] += 1
        if self.unknown_after_apply:
            raise SettingsError("http_outcome_unknown")
        return HttpResponse(200, dict(accepted=True, result="applied" if changed else "no_change",
            settingsRevision=self.server["settingsRevision"], changedKeys=sorted(changed),
            values={x["key"]: x["requestedValue"] for x in self.server["settings"]},
            effectiveValues={x["key"]: x["effectiveValue"] for x in self.server["settings"]},
            applyPolicies={x["key"]: x["applyPolicy"] for x in self.server["settings"] if x["key"] in changed}))


class SettingsSocket(FakeWebSocket):
    def __init__(self):
        super().__init__()
        self.state = deepcopy(FIXTURES["snapshot"])
        self.state.update(settingsRevision=0, stateVersion=0, lastEventSeq=0)
        self.state["trigger"]["suppressed"] = dict(manual=True, wakeWord=True)
        self.on_send = self.respond
        self.conflicts = 0
        self.reject = None
        self.drop = None
        self.latch = False
        self.snapshot_missing = False
        self.hook = None

    async def send(self, wire):
        if isinstance(wire, str) and json.loads(wire)["type"] == "hello":
            self.sent.append(wire)
            hello = deepcopy(FIXTURES["helloAccepted"])
            hello["snapshot"] = {key: value for key, value in deepcopy(self.state).items() if key != "type"}
            self.push(hello)
        else:
            await super().send(wire)

    async def respond(self, command):
        kind = command["type"]
        if self.hook:
            await self.hook(command)
        if self.drop == kind:
            return
        result = "no_change"
        if self.reject == kind:
            result = "settings_rejected" if kind == p.CommandType.SETTINGS_PATCH else "internal_error"
        elif kind == p.CommandType.SETTINGS_PATCH:
            if self.conflicts:
                self.conflicts -= 1
                self.state["settingsRevision"] += 1
                result = "settings_revision_conflict"
            else:
                self.state["requestedSettings"].update(command["changes"])
                if not self.latch:
                    self.state["effectiveSettings"].update(command["changes"])
                self.state["settingsRevision"] += 1
                result = "applied"
        elif kind == p.CommandType.SUPPRESSION:
            self.state["trigger"]["suppressed"] = {k: command[k] for k in ("manual", "wakeWord")}
        elif kind == p.CommandType.AUDIO_AVAILABILITY:
            self.state["audioAvailable"] = command["audioAvailable"]
        elif kind == p.CommandType.SNAPSHOT_REQUEST and not self.snapshot_missing:
            self.push(deepcopy(self.state))
        reply = ack(result)
        reply.update(commandId=command["commandId"], sessionId=self.session_id, stateVersion=self.state["stateVersion"],
                     settingsRevision=self.state["settingsRevision"])
        self.push(reply)


class Migration(unittest.TestCase):
    def test_mode_flags_and_explicit_both(self):
        catalog = WakeCatalog.parse(catalog_body())
        for mode, flags in (("hotkey", (True, False)), ("wake_word", (False, True))):
            profile = migrate_profile({"session": {"mode": mode}}, catalog)
            profile.require_ready()
            self.assertEqual((profile.manual, profile.wake_word), flags)
        p2 = migrate_profile({"session": {"mode": "invalid", "manual_trigger_enabled": True, "wake_word_trigger_enabled": True}}, catalog)
        p2.require_ready()
        self.assertEqual((p2.manual, p2.wake_word), (True, True))

    def test_invalid_trigger_and_hotkey_conflicts_are_preserved(self):
        for session in ({"mode": "invalid"}, {"manual_trigger_enabled": False, "wake_word_trigger_enabled": False},
                        {"manual_trigger_enabled": "yes"}):
            profile = migrate_profile({"session": session})
            self.assertTrue(profile.issues)
            with self.assertRaises(ValueError):
                profile.require_ready()
        for hotkey in ({"finish_key": "Ctrl+F", "cancel_key": "Ctrl+C"},
                       {"toggle_key": "Ctrl+X", "reinsert_last_key": "Ctrl+X"}):
            profile = migrate_profile({"hotkey": hotkey})
            self.assertEqual(profile.unresolved["hotkey"], hotkey)

    def test_exact_seconds_ms_and_retired_extension_warning(self):
        for seconds, ms in ((2.5, 2500), (.1, 100), (15, 15000)):
            self.assertEqual(seconds_to_ms(seconds), ms)
        for bad in (True, "2", float("nan"), float("inf"), -1, .0001):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                seconds_to_ms(bad)
        raw = dict(dictation_window=dict(initial_speech_timeout=12.125, followup_timeout=2.5,
                                         extension_seconds=15, timeout_warning_seconds=3))
        profile = migrate_profile(raw)
        self.assertEqual(profile.desired_settings, {"activation.initialSpeechTimeoutMs": 12125, KEY: 2500})
        self.assertEqual(profile.retired, {"dictation_window.extension_seconds": 15, "dictation_window.timeout_warning_seconds": 3})
        self.assertNotIn("activation.segmentWatchdogWarningMs", profile.desired_settings)

    def test_colliding_session_and_local_timing_remains_unresolved(self):
        raw = dict(session=dict(followup_timeout=5), dictation_window=dict(followup_timeout=3))
        profile = migrate_profile(raw)
        self.assertNotIn(KEY, profile.desired_settings)
        self.assertEqual(profile.unresolved[KEY], {"session.followup_timeout": 5, "dictation_window.followup_timeout": 3})

    def test_offline_then_online_resolution_unavailable_id_retained(self):
        profile = migrate_profile({"session": {"mode": "wake_word", "wake_words": " Jarvis , Alexa "}})
        self.assertTrue(profile.issues)
        profile = migrate_profile({"v2_profile": asdict(profile)}, WakeCatalog.parse(catalog_body()))
        profile.require_ready()
        self.assertEqual(profile.wake_word_ids, ["hey_jarvis", "alexa"])
        body = catalog_body(); body["wakeWords"][0].update(available=False, unavailableReason="artifact_missing")
        blocked = migrate_profile({"v2_profile": asdict(profile)}, WakeCatalog.parse(body))
        self.assertEqual(blocked.wake_word_ids, profile.wake_word_ids)
        self.assertIn("wake_selection_unavailable", blocked.issues)

    def test_backup_atomic_idempotent_local_fields_preserved(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "profile.yaml"
            original = b'# user comment\naudio: {device: 4}\nclipboard: {restore_previous: true}\nsession: {mode: wake_word, wake_words: Jarvis}\n'
            path.write_bytes(original)
            profile = migrate_config_file(path, WakeCatalog.parse(catalog_body()))
            self.assertEqual(path.with_name(path.name + ".pre-v2.bak").read_bytes(), original)
            first = path.read_bytes()
            migrate_config_file(path, WakeCatalog.parse(catalog_body()))
            self.assertEqual(path.read_bytes(), first)
            loaded = AppConfig.load(path)
            self.assertEqual(loaded.audio.device, 4)
            self.assertTrue(loaded.clipboard.restore_previous)
            self.assertEqual(loaded.v2_profile["wake_word_ids"], profile.wake_word_ids)
            self.assertNotIn("runtimeSuppression", json.dumps(loaded.v2_profile))
            loaded.save_user()
            self.assertEqual(AppConfig.load(path).v2_profile["wake_word_ids"], ["hey_jarvis"])

    def test_write_failure_leaves_original_and_backup(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "profile.yaml"; path.write_bytes(b'session: {mode: hotkey}\n')
            original = path.read_bytes()
            with patch("voice_stt_client.core.v2_profile.os.replace", side_effect=OSError("synthetic")):
                with self.assertRaises(OSError):
                    migrate_config_file(path)
            self.assertEqual(path.read_bytes(), original)
            self.assertEqual(path.with_name(path.name + ".pre-v2.bak").read_bytes(), original)
            self.assertEqual(len(list(path.parent.iterdir())), 2)

    def test_versioned_profile_ignores_legacy_mode_extension(self):
        profile = V2Profile(manual=True, wake_word=True, wake_word_ids=["alexa"])
        migrated = migrate_profile({"v2_profile": asdict(profile), "session": {"mode": "bad", "extension_seconds": 9000}})
        self.assertEqual(migrated, profile)
        with self.assertRaises(ValueError):
            migrate_profile({"v2_profile": {"schema_version": 999}})


class CatalogAndSchema(unittest.TestCase):
    def test_counts_policies_and_schema_without_write_flags(self):
        settings = {x["key"]: Setting.parse(x) for x in SCHEMA["settings"]}
        self.assertEqual(len(settings), 18)
        self.assertEqual(len(SESSION_KEYS), 16)
        self.assertEqual(len(SERVER_DEFAULT_KEYS), 15)
        self.assertTrue(all("writable" not in x for x in SCHEMA["settings"]))
        self.assertTrue(all(settings[x].apply_policy == p.ApplyPolicy.NEXT_ACTIVATION for x in NA_KEYS))
        self.assertTrue(any(s.constraints.get("calibration") == "pending" for s in settings.values()))
        extension = deepcopy(SCHEMA["settings"][0]); extension.update(key="future.setting", applyPolicy="server_restart")
        self.assertEqual(Setting.parse(extension).apply_policy, p.ApplyPolicy.SERVER_RESTART)

    def test_types_ranges_and_no_coercion(self):
        definitions = {x["key"]: Setting.parse(x) for x in SCHEMA["settings"]}
        for key, values in ((KEY, (True, "4000", 3.5, 99, 60001)),
                            ("wakeWord.sensitivity", (True, "0.5", float("nan"), float("inf"), 1.1)),
                            ("wakeWord.selection", ("jarvis", [3])),
                            ("wakeWord.noiseSuppressionEnabled", (1, "true"))):
            for value in values:
                with self.subTest(key=key, value=value), self.assertRaises(SettingsError):
                    definitions[key].validate(value)

    def test_alias_resolution_unicode_trim_dedup_and_ambiguity(self):
        body = catalog_body()
        catalog = WakeCatalog.parse(body)
        self.assertEqual(catalog.resolve(["\u2003JARVIS\u2003", "hey_jarvis", "Alexa"]), ("hey_jarvis", "alexa"))
        body["wakeWords"][1]["aliases"].append("jarvis")
        ambiguous = WakeCatalog.parse(body)
        with self.assertRaises(SettingsError):
            ambiguous.resolve(["Jarvis"])
        with self.assertRaises(SettingsError):
            catalog.resolve(["Hey Alexa"])

    def test_whole_selection_no_common_or_explicit_backend_no_fallback(self):
        body = catalog_body(); body["wakeWords"][0]["backends"]["tflite"].update(available=False, unavailableReason="synthetic")
        body["wakeWords"][1]["backends"]["onnx"].update(available=False, unavailableReason="synthetic")
        catalog = WakeCatalog.parse(body)
        for ids, backend in ((["hey_jarvis", "alexa"], "auto"), (["hey_jarvis"], "tflite"), (["Jarvis"], "auto"), ([], "auto")):
            with self.subTest(ids=ids), self.assertRaises(SettingsError):
                catalog.validate_selection(ids, backend=backend, required=True)

    def test_catalog_metadata_immutable_no_internal_paths(self):
        body = catalog_body(); body["wakeWords"][0]["artifactPath"] = "/private/path"
        body["wakeWords"][0]["backends"]["onnx"]["artifactPath"] = "/private/backend/path"
        catalog = WakeCatalog.parse(body)
        self.assertNotIn("artifactPath", catalog.entries["hey_jarvis"])
        self.assertNotIn("artifactPath", catalog.entries["hey_jarvis"]["backends"]["onnx"])
        with self.assertRaises(TypeError):
            catalog.entries["hey_jarvis"]["available"] = False
        for mutate in (lambda b: b.update(protocolVersion=1), lambda b: b["wakeWords"][0].update(catalogRevision="wrong"),
                       lambda b: b["wakeWords"].append(deepcopy(b["wakeWords"][0]))):
            bad = catalog_body(); mutate(bad)
            with self.assertRaises(SettingsError):
                WakeCatalog.parse(bad)


class Service(unittest.IsolatedAsyncioTestCase):
    async def start(self, *, profile=None, socket=None, http=None, bootstrap=None):
        socket, http = socket or SettingsSocket(), http or FakeHTTP()
        async def connector(*args, **kwargs):
            return socket
        session = V2STTSession(V2TransportConfig(ack_timeout=.2, command_retries=0, bootstrap_timeout=2), connector=connector)
        service = SettingsService(session, profile or V2Profile(desired_settings={KEY: 4000}), http=http, snapshot_timeout=.5)
        session.bootstrap = bootstrap or service.bootstrap
        task = asyncio.create_task(session.run())
        async def cleanup():
            await session.stop(); await service.close(); await asyncio.gather(task, return_exceptions=True)
        self.addAsyncCleanup(cleanup)
        await until(lambda: session.is_ready or task.done())
        return session, service, socket, http

    async def test_preflight_then_na_patch_snapshot_suppression_ready(self):
        session, service, socket, http = await self.start()
        self.assertTrue(session.is_ready)
        self.assertEqual(len(http.calls), 3)
        hello = json.loads(socket.sent[0])
        self.assertEqual(hello["runtimeSuppression"], dict(manual=True, wakeWord=True))
        types = [x["type"] for x in socket.commands]
        self.assertLess(types.index(p.CommandType.SETTINGS_PATCH), types.index(p.CommandType.SUPPRESSION))
        report = service.report()
        self.assertEqual(report.effective[KEY], 4000)
        self.assertEqual(report.session_revision, 1)
        self.assertEqual(report.server_revision, SERVER["settingsRevision"])
        self.assertFalse(report.pending.get(KEY))

    async def test_media_availability_rejection_blocks_before_settings_audio(self):
        from tests.test_v2_audio_recovery import Capture
        from voice_stt_client.core.config import ServerConfig, EventStreamConfig
        from voice_stt_client.core.session_coordinator import DualSessionCoordinator
        from voice_stt_client.core.v2_media import V2MediaConnection
        socket = SettingsSocket(); socket.reject = p.CommandType.AUDIO_AVAILABILITY
        async def connector(*args, **kwargs): return socket
        session = V2STTSession(V2TransportConfig(ack_timeout=.2), connector=connector)
        service = SettingsService(session, V2Profile(desired_settings={KEY: 4000}), http=FakeHTTP())
        capture = Capture()
        media = V2MediaConnection(session, capture, settings_bootstrap=service.bootstrap,
            logs=DualSessionCoordinator(ServerConfig(), EventStreamConfig(enabled=False)))
        media.set_device_available(False)
        task = asyncio.create_task(session.run())
        try:
            await until(task.done)
            self.assertEqual(session.status.state.value, "blocked")
            self.assertEqual(capture.starts, 0)
            self.assertFalse(any(x["type"] in (p.CommandType.SETTINGS_PATCH, p.CommandType.SUPPRESSION) for x in socket.commands))
        finally:
            await media.close(); await service.close(); await asyncio.gather(task, return_exceptions=True)

    async def test_conflict_reread_new_command_id_exactly_once(self):
        socket = SettingsSocket(); socket.conflicts = 1
        session, service, socket, http = await self.start(socket=socket)
        self.assertTrue(session.is_ready)
        patches = [x for x in socket.commands if x["type"] == p.CommandType.SETTINGS_PATCH]
        self.assertEqual([x["baseSettingsRevision"] for x in patches], [0, 1])
        self.assertNotEqual(patches[0]["commandId"], patches[1]["commandId"])
        self.assertEqual(service.report().session_revision, 2)

    async def test_repeated_conflict_blocks_no_audio_no_activation(self):
        socket = SettingsSocket(); socket.conflicts = 2
        session, service, socket, http = await self.start(socket=socket)
        self.assertEqual(session.status.state.value, "blocked")
        self.assertFalse(await session.send_audio(b'\0\0', 16000))
        with self.assertRaises(TransportLost):
            await session.request(p.CommandType.ACTIVATION, action="activate", source="manual")
        self.assertFalse(any(x["type"] == p.CommandType.SUPPRESSION for x in socket.commands))

    async def test_bootstrap_faults_never_release_suppression(self):
        for kind in (p.CommandType.SETTINGS_PATCH, p.CommandType.SNAPSHOT_REQUEST, p.CommandType.SUPPRESSION):
            with self.subTest(kind=kind):
                socket = SettingsSocket(); socket.reject = kind
                session, service, socket, http = await self.start(socket=socket)
                self.assertFalse(session.is_ready)
                self.assertFalse(await session.send_audio(b'\0\0', 16000))
        socket = SettingsSocket(); socket.snapshot_missing = True
        session, service, socket, http = await self.start(socket=socket)
        self.assertFalse(session.is_ready)
        socket = SettingsSocket(); socket.drop = p.CommandType.SETTINGS_PATCH
        session, service, socket, http = await self.start(socket=socket)
        self.assertFalse(session.is_ready)

    async def test_preflight_error_each_read_and_profile_keeps_wire_empty(self):
        for path in ("/api/v2/settings/schema", "/api/v2/settings/server", "/api/v2/wake-words"):
            with self.subTest(path=path):
                http = FakeHTTP(); http.fail_path = path
                session, service, socket, http = await self.start(http=http)
                self.assertFalse(session.is_ready)
                self.assertEqual(socket.sent, [])
        session, service, socket, http = await self.start(profile=V2Profile(wake_word=True, wake_word_ids=["missing"]))
        self.assertEqual(socket.sent, [])

    async def test_ns_preferences_unsupported_selection_next_hello_no_patch(self):
        profile = V2Profile(desired_settings={"wakeWord.noiseSuppressionEnabled": True, "wakeWord.vadThreshold": .5})
        session, service, socket, http = await self.start(profile=profile)
        self.assertTrue(session.is_ready)
        report = service.report()
        self.assertEqual(len(report.unsupported), 2)
        self.assertFalse(any(x["type"] == p.CommandType.SETTINGS_PATCH for x in socket.commands))
        service.select_wake_words(["Alexa"])
        self.assertEqual(service.profile.wake_word_ids, ["alexa"])
        self.assertEqual(service.report().pending["wakeWord.selection"], ("alexa",))
        config = await service.prepare(session)
        self.assertEqual(config.wake_word_ids, ())
        self.assertEqual(service.profile.wake_word_ids, ["alexa"])
        # Disabling Wake retains the local selection but the Hello must omit it.
        p.build_hello(clientVersion="test", clientCommit="test", clientRunId=p.new_id(),
            manual=config.manual, wakeWord=config.wake_word, wakeWordIds=list(config.wake_word_ids),
            suppressManual=True, suppressWakeWord=True)

    async def test_atomic_local_validation_and_scope_authority(self):
        session, service, socket, http = await self.start()
        before = deepcopy(service.profile.desired_settings)
        for changes in ({KEY: 4500, "bogus": 3}, {KEY: True}, {"wakeWord.inferenceBackend": "onnx"},
                        {"runtimeSuppression.manual": False}, {"wakeWord.selection": ["alexa"]},
                        {"wakeWord.vadThreshold": .3}, {"activation.segmentWatchdogRefreshMs": 30000}):
            with self.subTest(changes=changes), self.assertRaises(SettingsError):
                service.set_desired(changes)
            self.assertEqual(service.profile.desired_settings, before)
        self.assertEqual(service.report().effective[KEY], 4000)

    async def test_requested_effective_latched_and_pending_report(self):
        session, service, socket, http = await self.start()
        socket.latch = True
        service.set_desired({KEY: 5000})
        report = await service.apply_session()
        self.assertEqual(report.requested[KEY], 5000)
        self.assertEqual(report.effective[KEY], 4000)
        self.assertEqual(report.pending[KEY], 5000)
        with self.assertRaises(TypeError):
            report.desired[KEY] = 6
        socket.state["effectiveSettings"][KEY] = 5000
        await service.refresh_session()
        self.assertNotIn(KEY, service.report().pending)

    async def test_stale_http_generation_rejected_without_publication(self):
        session, service, socket, http = await self.start()
        old = service.server_revision
        async def invalidate(method, path):
            if path.endswith("server"):
                session.generation += 1
        http.hook = invalidate
        with self.assertRaises(TransportLost):
            await service.read_server()
        self.assertEqual(service.server_revision, old)

    async def test_stale_snapshot_ignored_binding_and_revision(self):
        session, service, socket, http = await self.start()
        report = service.report()
        old = p.parse_snapshot(FIXTURES["snapshot"])
        # A different binding must never update the settings authority.
        service.session.on_message(object(), old)
        self.assertEqual(service.report(), report)
        olddata = deepcopy(socket.state); olddata["settingsRevision"] = 0
        session.on_message(session.binding, p.parse_snapshot(olddata))
        self.assertEqual(service.report(), report)

    async def test_server_revision_patch_no_change_and_unclear_read_no_retry(self):
        session, service, socket, http = await self.start()
        # Server starts at its own revision, unrelated to session revision 1.
        body = await service.patch_server({KEY: 5000}, admin_key="synthetic")
        calls = [x for x in http.calls if x[0] == "PATCH"]
        self.assertEqual(calls[0][2]["baseSettingsRevision"], SERVER["settingsRevision"])
        revision = service.server_revision
        unchanged = await service.patch_server({KEY: 5000}, admin_key="synthetic")
        self.assertEqual(unchanged["result"], "no_change")
        self.assertEqual(service.server_revision, revision)
        http.unknown_after_apply = True
        with self.assertRaisesRegex(SettingsError, "http_outcome_unknown"):
            await service.patch_server({KEY: 6000}, admin_key="synthetic")
        self.assertEqual(len([x for x in http.calls if x[0] == "PATCH"]), 3)
        self.assertEqual(service.server_requested[KEY], 6000)
        self.assertEqual(service.report().session_revision, 1)

    async def test_server_error_codes_reload_no_partial_or_retry(self):
        session, service, socket, http = await self.start()
        for status, code in ((401, "admin_unauthorized"), (403, "admin_disabled"), (409, "settings_revision_conflict"),
                             (422, "server_settings_rejected"), (500, "server_persistence_failed")):
            http.patch_status = status
            with self.subTest(status=status), self.assertRaisesRegex(SettingsError, code):
                await service.patch_server({KEY: 5000}, admin_key="private-synthetic")
            self.assertEqual(service.server_requested[KEY], 3000)
            self.assertEqual(http.calls[-1][:2], ("GET", "/api/v2/settings/server"))
        self.assertNotIn("private-synthetic", repr(http.calls))

    async def test_catalog_revision_cache_and_availability_reload(self):
        session, service, socket, http = await self.start()
        previous = service.catalog
        await service.load_metadata()
        self.assertIs(service.catalog, previous)
        http.catalog = catalog_body(2)
        e = event("wakeword.availability_changed")
        e.update(catalogRevision=2)
        session.on_message(session.binding, p.decode_server_message(e))
        self.assertTrue(service.catalog_stale)
        await service._refresh_task
        self.assertEqual(service.catalog.revision, 2)
        self.assertFalse(service.catalog_stale)

    async def test_input_closed_refreshes_effective_without_explicit_ui_read(self):
        session, service, socket, http = await self.start()
        socket.latch = True
        service.set_desired({KEY: 5000})
        await service.apply_session()
        self.assertIn(KEY, service.report().pending)
        socket.state["effectiveSettings"][KEY] = 5000
        session.on_message(session.binding, p.decode_server_message(event("activation.input_closed")))
        await until(lambda: KEY not in service.report().pending)
        self.assertEqual(service.report().effective[KEY], 5000)

    async def test_availability_reload_rejects_old_revision_and_retries_bounded(self):
        session, service, socket, http = await self.start()
        previous = service.catalog
        e = event("wakeword.availability_changed"); e["catalogRevision"] = 2
        session.on_message(session.binding, p.decode_server_message(e))
        await service._refresh_task
        self.assertTrue(service.catalog_stale)
        self.assertIs(service.catalog, previous)
        self.assertEqual(service.last_metadata_error, "catalog_refresh_failed")
        self.assertEqual(len(http.calls), 9)  # Initial load plus exactly two reads.

    async def test_bootstrap_new_wish_during_confirmation_cannot_claim_ready(self):
        socket = SettingsSocket()
        service_ref = []
        async def hook(command):
            if command["type"] == p.CommandType.SETTINGS_PATCH:
                service_ref[0].set_desired({KEY: 5000})
        socket.hook = hook
        # Service is captured after constructing start, so use its registered
        # prepare callback owner instead of relying on asynchronous timing.
        async def bootstrap(session, binding):
            service_ref.append(session.prepare.__self__)
            await service_ref[0].bootstrap(session, binding)
        session, service, socket, http = await self.start(socket=socket, bootstrap=bootstrap)
        self.assertFalse(session.is_ready)
        self.assertFalse(any(x["type"] == p.CommandType.SUPPRESSION for x in socket.commands))


class HTTP(unittest.IsolatedAsyncioTestCase):
    async def test_origin_tls_routes_and_no_secret_errors(self):
        for url in ("ws://remote.test/ws/v2", "wss://user:secret@remote.test/ws/v2", "wss://remote.test/ws/v2?key=x"):
            with self.assertRaises(SettingsError):
                SettingsHTTP(url)
        http = SettingsHTTP("wss://stt.voice.marcosudau.com/ws/v2")
        self.assertEqual(http.origin, "https://stt.voice.marcosudau.com")
        with self.assertRaises(SettingsError):
            await http.request("GET", "https://evil.test/api/v2/settings/server")
        with patch("voice_stt_client.core.settings_service.build_opener") as opener:
            opener.return_value.open.side_effect = URLError("private-key")
            with self.assertRaises(SettingsError) as caught:
                await http.request("PATCH", "/api/v2/settings/server", body={KEY: 4}, admin_key="private-key")
            self.assertEqual(str(caught.exception), "http_outcome_unknown")

    async def test_bounded_http_timeout_keeps_one_worker_and_loop_responsive(self):
        http = SettingsHTTP("wss://stt.voice.marcosudau.com/ws/v2", timeout=.025)
        release = threading.Event(); calls = []
        def hold(*args):
            calls.append(args); release.wait(1)
            return HttpResponse(200, {})
        http._request = hold
        try:
            with self.assertRaisesRegex(SettingsError, "http_timeout"):
                await http.request("GET", "/api/v2/settings/schema")
            with self.assertRaisesRegex(SettingsError, "http_worker_busy"):
                await http.request("GET", "/api/v2/settings/schema")
            self.assertEqual(len(calls), 1)
        finally:
            release.set()
            await http._worker

    async def test_response_bound_invalid_json_and_redirect_not_followed(self):
        class Response:
            def __init__(self, code, value):
                self.code, self.value = code, value
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self, count): return self.value[:count]
        http = SettingsHTTP("wss://stt.voice.marcosudau.com/ws/v2", max_bytes=20)
        for status, body, code in ((302, b'{}', "http_redirect_forbidden"),
                                   (200, b'x' * 30, "http_response_too_large"),
                                   (200, b'not-json', "invalid_http_json"), (200, b'[]', "invalid_http_shape")):
            with self.subTest(code=code), patch("voice_stt_client.core.settings_service.build_opener") as opener:
                opener.return_value.open.return_value = Response(status, body)
                with self.assertRaisesRegex(SettingsError, code):
                    await http.request("GET", "/api/v2/settings/schema")

    async def test_owner_cancellation_preserves_native_worker_barrier(self):
        http = SettingsHTTP("wss://stt.voice.marcosudau.com/ws/v2", timeout=.2)
        entered, release = threading.Event(), threading.Event()
        def hold(*args):
            entered.set(); release.wait(2)
            return HttpResponse(200, {})
        http._request = hold
        task = asyncio.create_task(http.request("PATCH", "/api/v2/settings/server", body={KEY: 1}))
        try:
            await until(entered.is_set)
            worker = http._worker
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
            self.assertIs(http._worker, worker)
            self.assertFalse(worker.done())
        finally:
            release.set()
            await http._worker


if __name__ == "__main__":
    unittest.main()
