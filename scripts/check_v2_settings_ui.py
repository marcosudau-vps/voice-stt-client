"""AP080 Qt -> actual core services -> pinned production HTTP/WS app.

--native additionally proves a real Windows Qt window and the current-user
Credential Manager lifecycle. Only an isolated random loopback server/vault
target and temporary client configuration are used; no production writes.
"""
from __future__ import annotations

import argparse
import asyncio
import ctypes
from dataclasses import asdict
import datetime
import json
import os
from pathlib import Path
import platform
import secrets
import socket
import subprocess
import sys
import tempfile
import threading
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_v2_server_transport import SERVER_SHA, verify_sources, until
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig
from voice_stt_client.core.credential_store import CredentialStore
from voice_stt_client.core.settings_service import SettingsService
from voice_stt_client.core.settings_ui_service import SettingsUISession, ApplyChoice
from voice_stt_client.core.v2_controls import V2ControlService
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig


def run(root, repository, native=False, screenshot=None):
    os.environ["QT_QPA_PLATFORM"] = "windows" if native else "offscreen"
    from PySide6.QtCore import QSettings, Qt, QTimer
    from PySide6.QtTest import QTest
    from PySide6.QtWidgets import QApplication, QDialog
    from voice_stt_client.ui.v2_settings_bridge import V2SettingsBridge
    from voice_stt_client.ui.v2_settings_dialog import V2SettingsDialog
    if native and sys.platform != "win32":
        raise RuntimeError("native Windows required")
    sys.path.insert(0, str(root))
    import uvicorn
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import ManualScheduler
    source_hashes = verify_sources(root, repository)
    app = QApplication.instance() or QApplication([])
    loop = asyncio.new_event_loop()
    worker = threading.Thread(target=loop.run_forever, name="AP080-actual-core")
    worker.start()
    checks = []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    def core(coroutine):
        try:
            return asyncio.run_coroutine_threadsafe(coroutine, loop).result(15)
        except TimeoutError:
            if state.get("session"):
                raise AssertionError("core checkpoint timeout: " + str(state["session"].status) +
                    "; mirror=" + str(state["mirror"].mirror.view.state) + "; parser=" + repr(state.get("protocol_errors", []))) from None
            raise
    def wait(condition, timeout=10):
        end = time.monotonic() + timeout
        while not condition():
            app.processEvents()
            if time.monotonic() > end:
                raise AssertionError("Qt/core checkpoint timeout")
            time.sleep(.005)
        app.processEvents()
    KEY = "activation.followupTimeoutMs"
    vault = CredentialStore()
    state = {}
    decode = p.decode_server_message
    def decode_checked(frame):
        try:
            return decode(frame)
        except p.ProtocolError as error:
            state.setdefault("protocol_errors", []).append(str(error))
            raise
    p.decode_server_message = decode_checked
    with tempfile.TemporaryDirectory(prefix="cv2-080-checkpoint-") as folder:
        async def start():
            state["key"] = secrets.token_urlsafe(24)
            config = ServerSettings(data_root_path=str(Path(folder)/"server"), model_warmup=False,
                admin_api_key=state["key"], request_logging_enabled=False, performance_logging_enabled=False,
                performance_log_mirror_enabled=False, transcription_logging_enabled=False,
                system_event_logging_enabled=False, event_store_enabled=False, log_live_enabled=False)
            server_app = create_app(config, recorder_factory=GateAwareRecorder, scheduler_factory=ManualScheduler)
            service = server_app.state.voicestt_service
            service.wakeword_catalog.set_artifact_prober(lambda path: None)
            tcp = socket.socket(); tcp.bind(("127.0.0.1", 0)); tcp.listen(16)
            url = f"ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2"
            server = uvicorn.Server(uvicorn.Config(server_app, log_level="error", access_log=False))
            serving = asyncio.create_task(server.serve(sockets=[tcp]))
            await until(lambda: server.started)
            session = V2STTSession(V2TransportConfig(url=url, backoff_initial=.02))
            mirror = V2MirrorConnection(session)
            settings = SettingsService(session, V2Profile(desired_settings={KEY: 4000}))
            controls = V2ControlService(session, mirror, audio_ready=lambda: True)
            async def bootstrap(client, binding):
                await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=True)
                await settings.bootstrap(client, binding)
            session.bootstrap = bootstrap
            running = asyncio.create_task(session.run())
            await until(lambda: session.is_ready and not mirror.mirror.view.snapshot_pending)
            state.update(server=server, serving=serving, tcp=tcp, session=session, mirror=mirror,
                settings=settings, controls=controls, running=running, server_service=service)
            check("server/pinned_admission", session.binding.accepted.payload["serverCommit"] == SERVER_SHA)
            def persist(profile):
                candidate = AppConfig(v2_profile=asdict(profile))
                candidate.save_user(Path(folder)/"client.yaml")
            def factory():
                return SettingsUISession(settings, controls, mirror, credential_store=vault,
                                         persist_profile=persist, wait_timeout=2)
            state["factory"] = factory
            return settings.http.origin

        async def close():
            await state["controls"].close()
            await state["mirror"].close()
            await state["settings"].close()
            await asyncio.gather(state["running"], return_exceptions=True)
            state["server"].should_exit = True
            await asyncio.wait_for(state["serving"], 10)
            state["tcp"].close()

        dialog = bridge = None
        origin = None
        try:
            with patch.dict(os.environ, {"VOICESTT_SERVER_COMMIT": SERVER_SHA}):
                origin = core(start())
                check("credential/isolated_target_initially_absent", vault.read(origin) is None)
                meta = QSettings(str(Path(folder)/"metadata.ini"), QSettings.Format.IniFormat)
                bridge = V2SettingsBridge(loop, state["factory"])
                dialog = V2SettingsDialog(bridge, metadata=meta)
                received = set()
                bridge.replied.connect(lambda reply: received.add(reply.request_id), Qt.ConnectionType.QueuedConnection)
                def wait_reply():
                    request_id = bridge._request_id
                    wait(lambda: not bridge.busy and request_id in received)
                dialog.show()
                wait(lambda: dialog._view is not None)
                dialog.timer.stop()
                check("ui/real_services_public_read_locked", not dialog._view.admin_verified and not dialog.apply_server_button.isEnabled())
                check("ui/core_is_separate_thread", worker.ident != threading.get_ident())
                if native:
                    user32 = ctypes.WinDLL("user32", use_last_error=True)
                    user32.IsWindow.argtypes = [ctypes.c_void_p]
                    user32.IsWindowVisible.argtypes = [ctypes.c_void_p]
                    hwnd = int(dialog.winId())
                    check("windows/real_visible_dialog", bool(user32.IsWindow(hwnd)) and bool(user32.IsWindowVisible(hwnd)))
                def click(button):
                    if native:
                        QTest.mouseClick(button, Qt.MouseButton.LeftButton)
                    else:
                        button.click()
                    # Future completion precedes its queued UI projection.
                    # Await the rendered reply before editing the next draft.
                    wait_reply()
                dialog.tabs.setCurrentIndex(2)
                dialog.key.setText("incorrect-synthetic-key")
                click(dialog.verify_button)
                wait(lambda: "401" in dialog.status.text())
                check("auth/wrong_key_visible_locked", not dialog._view.admin_verified)
                before = core(state["settings"].read_server())
                dialog.key.setText(state["key"])
                dialog.remember.setChecked(True)
                click(dialog.verify_button)
                wait(lambda: dialog._view.admin_verified and dialog._view.credential_saved)
                after = core(state["settings"].read_server())
                check("auth/no_change_defaults_revision_preserved", before == after)
                check("credential/native_create_from_ui", vault.read(origin) == state["key"])
                dialog.key.setText(state["key"])
                click(dialog.verify_button)
                check("credential/native_replace_from_ui", vault.read(origin) == state["key"])
                replacement = secrets.token_urlsafe(24)
                vault.save(origin, replacement)
                check("credential/native_distinct_replacement", vault.read(origin) == replacement)
                vault.save(origin, state["key"])
                other = "https://ap080-isolation-" + secrets.token_hex(8) + ".invalid"
                check("credential/origin_isolation", vault.read(other) is None)
                meta.sync()
                check("secrets/no_qsettings_or_projection_export", state["key"] not in Path(meta.fileName()).read_text()
                      and state["key"] not in repr(dialog._view))
                dialog._editors["server"][KEY].setText("6500")
                click(dialog.apply_server_button)
                wait(lambda: dialog._view.server_requested[KEY] == 6500)
                check("server/admin_ui_real_patch", dialog._view.server_requested[KEY] == 6500)
                dialog._editors["server"][KEY].setText("99")
                click(dialog.apply_server_button)
                check("server/schema_reject_visible_no_write", "Ungültiger Wert" in dialog.status.text()
                      and dialog._view.server_requested[KEY] == 6500)
                # Close and re-open uses a new credential lease, not old unlock.
                dialog.close(); dialog.show()
                wait(lambda: dialog._view is not None)
                dialog.timer.stop()
                check("credential/reopen_does_not_unlock", not dialog._view.admin_verified)
                click(dialog.load_key_button)
                wait(lambda: dialog._view.credential_saved)
                check("credential/load_without_auth_stays_locked", not dialog._view.admin_verified and dialog.key.text() == "")
                click(dialog.verify_button)
                wait(lambda: dialog._view.admin_verified)
                check("credential/loaded_key_guard_verified", dialog._view.admin_verified)
                click(dialog.delete_key_button)
                wait(lambda: not dialog._view.credential_saved)
                check("credential/native_delete_from_ui", vault.read(origin) is None and not dialog._view.admin_verified)

                dialog.tabs.setCurrentIndex(1)
                dialog._editors["session"][KEY].setText("5500")
                click(dialog.apply_profile_button)
                wait(lambda: dialog._view.settings.effective[KEY] == 5500)
                check("session/ui_real_patch_snapshot_effective", dialog._view.settings.requested[KEY] == 5500)
                check("profile/actual_local_persistence", AppConfig.load(Path(folder)/"client.yaml").v2_profile["desired_settings"][KEY] == 5500)
                check("secrets/no_config_export", state["key"] not in (Path(folder)/"client.yaml").read_text())
                # Open a real manual activation. Defer is chosen through the
                # actual nested Qt decision dialog, without tearing down input.
                async def activate():
                    await until(lambda: not state["mirror"].mirror.view.snapshot_pending)
                    result = await state["controls"].press("primary")
                    await until(lambda: state["mirror"].mirror.view.input.activation_id == result.ack.activationId)
                    return result.ack.activationId
                aid = core(activate())
                dialog._request("inspect"); wait(lambda: dialog._view.context.activation_id == aid)
                dialog.wake.setChecked(True)
                for index in range(dialog.wake_list.count()):
                    item = dialog.wake_list.item(index)
                    if item.data(Qt.ItemDataRole.UserRole) == "hey_jarvis":
                        item.setCheckState(Qt.CheckState.Checked)
                def choose(value, drain="wait"):
                    decision = dialog._decision
                    if decision is None:
                        QTimer.singleShot(10, lambda: choose(value, drain)); return
                    decision.choice.setCurrentIndex(decision.choice.findData(value))
                    decision.drain.setCurrentIndex(decision.drain.findData(drain))
                    decision.accept()
                QTimer.singleShot(20, lambda: choose(ApplyChoice.DEFER))
                click(dialog.apply_profile_button)
                wait(lambda: dialog._view.profile["wake_word"])
                check("apply/defer_preserves_real_activation", dialog._view.context.activation_id == aid)
                # Changing an already deferred wish still needs reconnect:
                # its baseline is the current Hello, not just saved profile.
                dialog.manual.setChecked(False)
                QTimer.singleShot(20, lambda: choose(ApplyChoice.FINISH))
                generation = dialog._view.context.generation
                click(dialog.apply_profile_button)
                wait(lambda: not bridge.busy)
                if "Anfrage bestätigt" not in dialog.status.text() and "Profil gespeichert" not in dialog.status.text():
                    raise AssertionError("finish_apply: " + dialog.status.text())
                dialog.timer.start()
                dialog._request("inspect")
                wait(lambda: dialog._view.context.generation > generation)
                dialog.timer.stop()
                check("apply/finish_real_command_then_reconnect", dialog._view.context.activation_id is None)
                core(until(lambda: state["session"].is_ready and not state["mirror"].mirror.view.snapshot_pending))
                dialog._request("load"); wait_reply()
                check("apply/wake_only_controls_retained", not dialog.manual.isChecked() and dialog.wake.isChecked()
                      and bool(dialog.controls["primary_key"].text()))
                # Restore Manual via the UI, then make real background ASR work
                # using the scheduler boundary while retaining production ledger.
                dialog.manual.setChecked(True)
                generation = dialog._view.context.generation
                click(dialog.apply_profile_button)
                dialog.timer.start()
                wait(lambda: dialog._view.context.generation > generation)
                core(until(lambda: state["session"].is_ready and not state["mirror"].mirror.view.snapshot_pending))
                dialog.timer.stop()
                async def drain():
                    aid = await activate()
                    domain = state["server_service"].sessions.get(state["session"].binding.session_id)
                    await state["session"].send_audio(b'\0\x40'*640, 16000, frames=640)
                    await until(lambda: state["mirror"].mirror.view.input.phase == p.InputPhase.SEGMENT_ACTIVE)
                    before = len(state["server_service"].scheduler.jobs)
                    domain.recorder.flush_buffered_audio()
                    await until(lambda: len(state["server_service"].scheduler.jobs) > before)
                    await until(lambda: state["mirror"].mirror.view.input.phase == p.InputPhase.FOLLOWUP_WAIT
                                and not state["mirror"].mirror.view.snapshot_pending)
                    result = await state["controls"].control("finish")
                    await until(lambda: state["mirror"].mirror.view.input.phase == p.InputPhase.IDLE)
                    return aid, state["server_service"].scheduler.jobs[-1]
                drain_id, job = core(drain())
                dialog._request("inspect")
                wait(lambda: drain_id in dialog._view.context.drain_ids)
                dialog.wake.setChecked(False)
                generation = dialog._view.context.generation
                QTimer.singleShot(20, lambda: dialog._decision.reject())
                click(dialog.apply_profile_button)
                check("drain/decision_cancel_preserves_connection", dialog._view.context.generation == generation
                      and drain_id in dialog._view.context.drain_ids)
                async def complete_later():
                    await asyncio.sleep(.15)
                    state["server_service"].scheduler.complete(job, text="synthetic checkpoint final")
                asyncio.run_coroutine_threadsafe(complete_later(), loop)
                QTimer.singleShot(20, lambda: choose(ApplyChoice.FINISH, "wait"))
                click(dialog.apply_profile_button)
                dialog.timer.start()
                wait(lambda: dialog._view.context.generation > generation)
                core(until(lambda: state["session"].is_ready and not state["mirror"].mirror.view.snapshot_pending))
                dialog.timer.stop()
                check("drain/wait_real_terminal_then_reconnect", not dialog._view.context.drain_ids)
                # Also exercise the explicit current-activation cancel path.
                aid = core(activate())
                dialog._request("inspect"); wait(lambda: dialog._view.context.activation_id == aid)
                dialog.wake.setChecked(True)
                generation = dialog._view.context.generation
                QTimer.singleShot(20, lambda: choose(ApplyChoice.CANCEL, "discard"))
                click(dialog.apply_profile_button)
                dialog.timer.start()
                wait(lambda: dialog._view.context.generation > generation)
                core(until(lambda: state["session"].is_ready and not state["mirror"].mirror.view.snapshot_pending))
                dialog.timer.stop()
                check("apply/cancel_real_activation_then_reconnect", dialog._view.context.activation_id is None)
                check("ui/calibration_pending_visible", any("calibration pending" in dialog._tables["session"].item(row,7).text()
                      for row in range(dialog._tables["session"].rowCount())))
                if screenshot is not None:
                    dialog.tabs.setCurrentIndex(1)
                    app.processEvents()
                    check("windows/dialog_capture_saved", dialog.grab().save(str(screenshot)))
                return dict(result="PASS", checkCount=len(checks), checks=checks, serverCommit=SERVER_SHA,
                    clientHead=subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
                    sourceHashes=source_hashes, runtime=dict(python=sys.version, executable=sys.executable,
                        platform=platform.platform(), qt=app.platformName(), tester="Codex on local Windows desktop",
                        startedAtUtc=datetime.datetime.now(datetime.UTC).isoformat(), coreThread=worker.ident,
                        qtThread=threading.get_ident()),
                    boundaries="Actual Qt dialog/bridge in main thread and SettingsUISession/SettingsService/Controls/Mirror/transport in separate asyncio thread, TCP HTTP/WS production pinned app. Real current-user Windows Credential Manager with random loopback target; real native Qt window only with --native. Synthetic widget input, model-free GateAwareRecorder/ManualScheduler, artifact probe and temporary profile persistence port; app composition, physical hotkey rebinding, ASR/audio calibration remain later gates.")
        finally:
            if dialog is not None:
                dialog.close(); app.processEvents()
            if origin is not None:
                vault.delete(origin)
            if state.get("running"):
                core(close())
            loop.call_soon_threadsafe(loop.stop)
            worker.join(10)
            loop.close()
            p.decode_server_message = decode


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-root", type=Path, required=True)
    parser.add_argument("--server-repository", type=Path, required=True)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--screenshot", type=Path)
    args = parser.parse_args()
    print(json.dumps(run(args.server_root.resolve(), args.server_repository.resolve(), args.native, args.screenshot), indent=2))
