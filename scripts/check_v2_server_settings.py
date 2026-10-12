"""AP070 real HTTP/WS settings bootstrap with pinned server and client media.

Only PortAudio, model probing, recorder/model scheduling are test boundaries.
No Qt, real ASR, production service, private audio or server product edits.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_v2_server_transport import SERVER_SHA, verify_sources, until
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.audio_capture import AudioCapture
from voice_stt_client.core.config import AudioConfig, ServerConfig, EventStreamConfig
from voice_stt_client.core.session_coordinator import DualSessionCoordinator
from voice_stt_client.core.settings_service import SettingsHTTP, SettingsService, SettingsError, NA_KEYS
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_media import V2MediaConnection


KEY = "activation.followupTimeoutMs"


async def run(root, repository):
    sys.path.insert(0, str(root))
    import numpy as np
    import uvicorn
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import AutoScheduler
    from VoiceSTT.core.wake_detection import WakeHit, WakeAttemptPolicy
    verify_sources(root, repository)
    checks, wire = [], []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    class Recorder(GateAwareRecorder):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.received = []
        def feed_audio(self, samples, original_sample_rate=16000):
            self.received.append((len(samples), original_sample_rate))
            super().feed_audio(samples, original_sample_rate)

    class Stream:
        def __init__(self, **kwargs):
            self.active = True
        def start(self): pass
        def stop(self): self.active = False
        def close(self): pass

    with tempfile.TemporaryDirectory(prefix="cv2-070-server-") as data, patch.dict(os.environ, {"VOICESTT_SERVER_COMMIT": SERVER_SHA}), patch(
            "sounddevice.query_devices", return_value={"name": "synthetic PCM", "default_samplerate": 16000}), patch(
            "sounddevice.check_input_settings"), patch("sounddevice.InputStream", Stream):
        settings = ServerSettings(data_root_path=data, model_warmup=False, admin_api_key="synthetic-harness-admin",
            request_logging_enabled=False, performance_logging_enabled=False, performance_log_mirror_enabled=False,
            transcription_logging_enabled=False, system_event_logging_enabled=False, event_store_enabled=False, log_live_enabled=False)
        app = create_app(settings, recorder_factory=Recorder, scheduler_factory=AutoScheduler)
        domain_service = app.state.voicestt_service
        domain_service.wakeword_catalog.set_artifact_prober(lambda path: None)
        tcp = socket.socket(); tcp.bind(("127.0.0.1", 0)); tcp.listen(16)
        url = f"ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2"
        server = uvicorn.Server(uvicorn.Config(app, log_level="error", access_log=False))
        serving = asyncio.create_task(server.serve(sockets=[tcp]))
        clients, runners = [], []
        try:
            await until(lambda: server.started or serving.done())
            if serving.done():
                await serving
                raise AssertionError("server startup failed")

            async def start(profile=None, *, unavailable=False):
                client = V2STTSession(V2TransportConfig(url=url, backoff_initial=.02))
                mirror = V2MirrorConnection(client)
                profile = profile or V2Profile(desired_settings={KEY: 4000, "wakeWord.sensitivity": .6,
                    "wakeWord.noiseSuppressionEnabled": True, "wakeWord.vadThreshold": .4})
                service = SettingsService(client, profile)
                config = AudioConfig()
                capture = AudioCapture(config)
                logs = DualSessionCoordinator(ServerConfig(url=url), EventStreamConfig(enabled=False))
                media = V2MediaConnection(client, capture, logs=logs, settings_bootstrap=service.bootstrap, recovery_interval=.02)
                media.set_device_available(not unavailable)
                old_completion = client.on_completion
                def completion(value):
                    wire.append(dict(generation=value.generation, type=value.command.type,
                        commandId=value.command.commandId, result=value.ack.result,
                        settingsRevision=value.ack.settingsRevision))
                    if old_completion:
                        old_completion(value)
                client.on_completion = completion
                reductions = []
                mirror.on_reduction = reductions.append
                clients.append((media, mirror, service)); runners.append(asyncio.create_task(client.run()))
                await until(lambda: client.is_ready or client.status.state.value == "blocked")
                check("bootstrap/ready", client.is_ready)
                await until(lambda: not mirror.mirror.view.snapshot_pending and (unavailable or media._gate))
                domain = domain_service.sessions.get(client.binding.session_id)
                return client, mirror, service, media, config, domain, reductions

            client, mirror, service, media, config, domain, reductions = await start(unavailable=True)
            check("identity/pinned_server", client.binding.accepted.payload["serverCommit"] == SERVER_SHA)
            check("settings/schema18_session16_server15", len(service.schema) == 18 and len(service.report().requested) == 16
                  and len(service.server_requested) == 15)
            check("catalog/real_build_dynamic_metadata", len(service.catalog.entries) > 2 and isinstance(service.catalog.revision, int))
            check("catalog/canonical_ids_only", service.catalog.resolve(["hey_jarvis"]) == ("hey_jarvis",))
            check("bootstrap/no_pre_ready_audio", not domain.recorder.received and not media.capture.is_running)
            types = [x["type"] for x in wire]
            check("bootstrap/availability_patch_suppression_order", types.index(p.CommandType.AUDIO_AVAILABILITY)
                < types.index(p.CommandType.SETTINGS_PATCH) < types.index(p.CommandType.SUPPRESSION))
            report = service.report()
            check("bootstrap/na_effective_confirmed", report.effective[KEY] == 4000 and report.effective["wakeWord.sensitivity"] == .6)
            check("ns/noise_vad_unsupported_no_false_success", len(report.unsupported) == 2
                  and report.effective["wakeWord.noiseSuppressionEnabled"] is False and report.effective["wakeWord.vadThreshold"] == 0)
            media.set_device_available(True)
            await until(lambda: media._gate and mirror.mirror.view.audio_available and not mirror.mirror.view.snapshot_pending)
            frames = media.capture.sample_rate // 25
            media.capture._audio_callback(np.full((frames, 1), 10000, dtype=np.int16), frames, None, None)
            await until(lambda: bool(domain.recorder.received))
            check("audio/real_capture_media_ws_server_pcm", domain.recorder.received[0] == (640, 16000))

            first = await client.request(p.CommandType.ACTIVATION, action="activate", source="manual")
            await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.WAITING_FIRST_SPEECH and not mirror.mirror.view.snapshot_pending)
            service.set_desired({KEY: 5000})
            latched = await service.apply_session()
            check("na/requested_new_effective_latched", latched.requested[KEY] == 5000 and latched.effective[KEY] == 4000 and latched.pending[KEY] == 5000)
            activation = mirror.mirror.view.activations[first.ack.activationId]
            check("na/activation_start_snapshot_immutable", activation.effective_settings[KEY] == 4000)
            await client.request(p.CommandType.ACTIVATION, action="cancel", activationId=first.ack.activationId)
            await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.IDLE and not mirror.mirror.view.snapshot_pending)
            refreshed = await service.refresh_session()
            check("na/after_close_effective_confirmed", refreshed.payload["effectiveSettings"][KEY] == 5000)

            # Bypass local validator to prove real server atomicity/error codes.
            before = service.report()
            for changes, code in (({KEY: 5500, "unknown": 2}, "unknown_key"), ({KEY: True}, "invalid_type"),
                    ({KEY: 99}, "out_of_range"), ({"activation.segmentWatchdogRefreshMs": 30000}, "cross_field_conflict"),
                    ({"wakeWord.inferenceBackend": "onnx"}, "wrong_scope"), ({"runtimeSuppression.manual": False}, "read_only_runtime_authority")):
                rejected = await client.request(p.CommandType.SETTINGS_PATCH, baseSettingsRevision=before.session_revision, changes=changes)
                await service.refresh_session()
                check("atomic/" + code, not rejected.ack.accepted and any(e["code"] == code for e in rejected.ack.payload.get("errors", ()))
                      and service.report().session_revision == before.session_revision and service.report().requested[KEY] == 5000)
            no_change = await client.request(p.CommandType.SETTINGS_PATCH, baseSettingsRevision=before.session_revision, changes={KEY: 5000})
            check("revision/session_no_change", no_change.ack.result == p.AckResult.NO_CHANGE and no_change.ack.settingsRevision == before.session_revision)

            # Force exactly one actual stale revision between read and PATCH.
            original = service._command
            injected = False
            async def conflict(binding, kind, **fields):
                nonlocal injected
                if kind == p.CommandType.SETTINGS_PATCH and not injected:
                    injected = True
                    await client.request(kind, binding=binding, baseSettingsRevision=fields["baseSettingsRevision"], changes={"wakeWord.sensitivity": .7})
                return await original(binding, kind, **fields)
            service._command = conflict
            at = len(wire)
            service.set_desired({KEY: 6000})
            await service.apply_session()
            service._command = original
            attempted = [x for x in wire[at:] if x["type"] == p.CommandType.SETTINGS_PATCH]
            check("revision/conflict_reload_new_id", any(x["result"] == p.AckResult.SETTINGS_REVISION_CONFLICT for x in attempted)
                  and len({x["commandId"] for x in attempted}) == len(attempted) and service.report().effective[KEY] == 6000)

            for changes, status in (({KEY: 7000}, 401),):
                try:
                    await service.patch_server(changes, admin_key="invalid-synthetic")
                except SettingsError as exc:
                    check("admin/unauthorized_guard", exc.status == status)
                else:
                    raise AssertionError("admin guard not enforced")
            patched = await service.patch_server({KEY: 7000}, admin_key="synthetic-harness-admin")
            check("server/independent_revision_confirmed", service.server_revision == 1 and service.report().session_revision > 1
                  and patched["values"][KEY] == 7000 and service.report().effective[KEY] == 6000)
            no_change = await service.patch_server({KEY: 7000}, admin_key="synthetic-harness-admin")
            check("server/no_change_no_revision", no_change["result"] == "no_change" and service.server_revision == 1)
            # Fail the persistence boundary, while keeping real validation and
            # HTTP routing: server state/revision must roll back atomically.
            with patch.object(domain_service.settings_control, "_persist", side_effect=OSError("synthetic-persistence-failure")):
                try:
                    await service.patch_server({KEY: 8000, "wakeWord.sensitivity": .8}, admin_key="synthetic-harness-admin")
                except SettingsError as exc:
                    check("server/persistence_failure_atomic_500", exc.status == 500 and service.server_revision == 1
                          and service.server_requested[KEY] == 7000 and service.server_requested["wakeWord.sensitivity"] == .5)
                else:
                    raise AssertionError("persistence failure hidden")
            response = await service.http.request("PATCH", "/api/v2/settings/server",
                body={"baseSettingsRevision": service.server_revision, "changes": {KEY: 8000, "unknown": 2}}, admin_key="synthetic-harness-admin")
            await service.read_server()
            check("server/validation_failure_atomic_422", response.status == 422 and service.server_revision == 1 and service.server_requested[KEY] == 7000)

            # New session loses old session settings: actual bootstrap reapplies them.
            old_binding = client.binding
            old_report = service.report()
            await client.reconnect(old_binding, "synthetic_network_reconnect")
            await until(lambda: client.binding is not None and client.binding is not old_binding and client.is_ready)
            await until(lambda: media._gate and not mirror.mirror.view.snapshot_pending)
            check("reconnect/na_before_audio", service.report().effective[KEY] == 6000 and not service.report().pending.get(KEY)
                  and service.report().session_id != old_report.session_id)
            check("reconnect/ns_preference_still_unsupported", service.report().effective["wakeWord.noiseSuppressionEnabled"] is False
                  and "wakeWord.noiseSuppressionEnabled" in service.report().unsupported)
            await media.close(); await mirror.close(); await service.close()

            # Real canonical selection at admission, model-free selected engine.
            profile = V2Profile(manual=True, wake_word=True, wake_word_ids=["hey_jarvis"], desired_settings={"wakeWord.sensitivity": .55})
            client, mirror, service, media, config, domain, reductions = await start(profile)
            await service.refresh_session()
            check("wake/selected_only_canonical_snapshot", service.report().effective["wakeWord.selection"] == ("hey_jarvis",))
            service.select_wake_words(["alexa"])
            check("wake/selection_pending_no_hot_reload", service.report().pending["wakeWord.selection"] == ("alexa",)
                  and service.report().effective["wakeWord.selection"] == ("hey_jarvis",))
            old_binding = client.binding
            await client.reconnect(old_binding, "explicit_safe_idle_selection_change")
            await until(lambda: client.binding is not None and client.binding is not old_binding and client.is_ready)
            await until(lambda: not mirror.mirror.view.snapshot_pending)
            domain = domain_service.sessions.get(client.binding.session_id)
            await service.refresh_session()
            check("wake/new_hello_selection_effective", service.report().effective["wakeWord.selection"] == ("alexa",))
            check("wake/calibration_pending_visible", service.schema["wakeWord.preRollMs"].constraints["calibration"] == "pending")
            domain._on_wakeword_detection_start()
            hit = WakeHit(canonical_wake_word_id="alexa", peak_score=.91, start_frame_index=0, start_sample=1280,
                qualification_frame_index=0, qualification_sample=1280, finalization_frame_index=1,
                operational_zero_point_sample=32000, prediction_frame_count=1, policy=WakeAttemptPolicy(sensitivity=.55))
            result = domain._on_wakeword_detected(hit)
            await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.WAITING_FIRST_SPEECH)
            check("wake/hit_actual_shared_controller", result is not None)
            # Receive order remains server-owned: started precedes detected.
            await until(lambda: any(e.type == p.EventType.WAKE_DETECTED for r in reductions for e in r.events))
            received = [e.type for r in reductions for e in r.events]
            check("wake/started_before_detected", received.index(p.EventType.ACTIVATION_STARTED) < received.index(p.EventType.WAKE_DETECTED))
            aid = mirror.mirror.view.input.activation_id
            second_hit = domain._on_wakeword_detected(hit)
            check("wake/latched_no_second_activation", second_hit is None and mirror.mirror.view.input.activation_id == aid)
            await client.request(p.CommandType.ACTIVATION, action="cancel", activationId=aid)
            await service.patch_server({"wakeWord.globalDisabledIds": ["alexa"]}, admin_key="synthetic-harness-admin")
            await until(lambda: service.catalog is not None and not service.catalog_stale and not service.catalog.entries["alexa"]["available"])
            check("catalog/availability_change_reload_retains_wish", service.profile.wake_word_ids == ["alexa"]
                  and not service.catalog.entries["alexa"]["available"])
            try:
                await service.prepare(client)
            except ValueError:
                check("catalog/unavailable_whole_selection_blocks", True)
            else:
                raise AssertionError("unavailable wish admitted")

            return dict(result="PASS", serverCommit=SERVER_SHA,
                clientHead=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                runtime=dict(python=sys.version, executable=sys.executable, platform=platform.platform(), uvicorn=uvicorn.__version__),
                checks=checks, checkCount=len(checks), wire=wire, sourceHashes=verify_sources(root, repository),
                boundaries="Actual SettingsHTTP/SettingsService/profile -> TCP HTTP production schema/server/catalog/admin; actual V2STTSession/Mirror/Media/AudioCapture -> TCP WS production settings/controllers/PCM. PortAudio synthetic device, GateAwareRecorder/AutoScheduler and synthetic WakeHit model outputs, permissive artifact engine probe. No Qt/app composition, real ASR/hardware or empirical wake calibration claim. Stale revision injection only between real client read/patch; no server product edit.")
        finally:
            for media, mirror, service in clients:
                await media.close(); await mirror.close(); await service.close()
            await asyncio.gather(*runners, return_exceptions=True)
            server.should_exit = True
            try:
                await asyncio.wait_for(serving, 10)
            finally:
                tcp.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-root", required=True, type=Path)
    parser.add_argument("--server-repository", required=True, type=Path)
    parser.add_argument("--contracts", action="store_true", help="Run pinned model-free settings/wake contract tests, supplementary to real HTTP/WS smoke")
    args = parser.parse_args()
    if args.contracts:
        root = args.server_root.resolve()
        sys.path.insert(0, str(root))
        from api_fastapi_server.server import create_app  # Source-verifier anchor.
        # These pure contract suites need no TestClient or ASR dependencies.
        # Production REST/WS/settings timer behaviour is proved above over TCP.
        names = ["tests.unit." + name for name in ("test_settings_control_plane",
            "test_wakeword_selected_only", "test_wake_detection", "test_wake_audio_boundary")]
        names.append("tests.unit.test_wakeword_root_findings_c3.DetectorGainTests")
        suite = unittest.defaultTestLoader.loadTestsFromNames(names)
        verify_sources(root, args.server_repository.resolve())
        result = unittest.TextTestRunner(verbosity=2).run(suite)
        print(json.dumps(dict(result="PASS" if result.wasSuccessful() else "FAIL", serverCommit=SERVER_SHA,
            testCount=result.testsRun, skipped=len(result.skipped), testModules=names,
            sourceHashes=verify_sources(root, args.server_repository.resolve()),
            boundaries="Pinned supplementary settings/wake unit contracts, not a substitute for actual client HTTP/WS checkpoint; model doubles, no real calibration."), indent=2))
        raise SystemExit(0 if result.wasSuccessful() else 1)
    print(json.dumps(asyncio.run(run(args.server_root.resolve(), args.server_repository.resolve())), indent=2))


if __name__ == "__main__":
    main()
