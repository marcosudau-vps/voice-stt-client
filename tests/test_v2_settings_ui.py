"""AP080 real client services with deterministic HTTP/socket fault boundaries."""
import asyncio
from copy import deepcopy
from dataclasses import asdict, replace
import json
import gc
import os
from pathlib import Path
import tempfile
import threading
import time
import subprocess
import sys
import unittest
from unittest.mock import patch

from PySide6.QtCore import QCoreApplication, QEvent, QSettings, Qt
from PySide6.QtWidgets import QApplication, QDialog, QDialogButtonBox

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.activation_mirror import ActivationView, InputView
from voice_stt_client.core.credential_store import CredentialError, CredentialStore, credential_target
from voice_stt_client.core.settings_service import SettingsError, SettingsService
from voice_stt_client.core.settings_ui_service import ApplyChoice, ApplyContext, SettingsUISession
from voice_stt_client.core.v2_controls import V2ControlService
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from voice_stt_client.ui.settings_dialog import SettingsDialog
from voice_stt_client.ui.v2_settings_bridge import UIReply, V2SettingsBridge
from voice_stt_client.ui.v2_settings_dialog import ApplyDecisionDialog, V2SettingsDialog
from tests.test_v2_settings_service import FakeHTTP, SettingsSocket, KEY
from tests.test_v2_transport import until

A = "30000000-0000-4000-8000-000000000001"


class CredBackend:
    def __init__(self):
        self.values = {}
        self.fail = False

    def _check(self):
        if self.fail:
            raise OSError("synthetic-secret-backend-error")

    def read(self, target):
        self._check()
        return self.values.get(target)

    def write(self, target, value):
        self._check()
        self.values[target] = value

    def delete(self, target):
        self._check()
        self.values.pop(target, None)


async def runtime(*, profile=None, http=None, persist=None, wait_timeout=.1):
    socket, http = SettingsSocket(), http or FakeHTTP()
    http.origin = "https://stt.voice.marcosudau.com"
    async def connector(*args, **kwargs):
        return socket
    session = V2STTSession(V2TransportConfig(ack_timeout=.2, bootstrap_timeout=2), connector=connector)
    mirror = V2MirrorConnection(session)
    profile = profile or V2Profile(desired_settings={KEY: 4000})
    socket.state["trigger"]["configured"] = dict(manual=profile.manual, wakeWord=profile.wake_word)
    socket.state["effectiveSettings"]["wakeWord.selection"] = list(profile.wake_word_ids)
    settings = SettingsService(session, profile, http=http)
    controls = V2ControlService(session, mirror, audio_ready=lambda: True)
    session.bootstrap = settings.bootstrap
    run = asyncio.create_task(session.run())
    await until(lambda: session.is_ready)
    await until(lambda: not mirror.mirror.view.snapshot_pending)
    backend = CredBackend()
    saved = []
    ui = SettingsUISession(settings, controls, mirror, credential_store=CredentialStore(backend),
        persist_profile=persist or (lambda candidate: saved.append(asdict(candidate))), wait_timeout=wait_timeout)
    async def cleanup():
        ui.invalidate()
        await controls.close()
        await mirror.close()
        await settings.close()
        await asyncio.gather(run, return_exceptions=True)
    return ui, socket, http, backend, saved, cleanup


class Credentials(unittest.TestCase):
    def test_normalized_origin_and_isolation(self):
        self.assertEqual(credential_target("https://STT.voice.marcosudau.com/"), credential_target("https://stt.voice.marcosudau.com:443"))
        self.assertNotEqual(credential_target("https://stt.voice.marcosudau.com"), credential_target("https://other.test"))
        self.assertNotEqual(credential_target("http://localhost:1234"), credential_target("http://localhost:1235"))

    def test_bad_origins_never_become_targets(self):
        for origin in ("https://user:key@host", "http://host", "https://host/path", "https://host?key=x", "https://host#x", "https://host:bad"):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                credential_target(origin)

    def test_create_replace_delete_and_redacted_repr(self):
        store = CredentialStore(CredBackend())
        origin = "https://example.test"
        self.assertIsNone(store.read(origin))
        store.save(origin, "synthetic-first")
        self.assertEqual(store.read(origin), "synthetic-first")
        store.save(origin, "synthetic-replacement")
        self.assertEqual(store.read(origin), "synthetic-replacement")
        self.assertIsNone(store.read("https://other.test"))
        self.assertNotIn("synthetic", repr(store))
        store.delete(origin)
        self.assertIsNone(store.read(origin))
        store.delete(origin)

    def test_failure_read_write_delete_redacts_backend(self):
        backend = CredBackend(); backend.fail = True
        store = CredentialStore(backend)
        for method, args in ((store.read, ()), (store.save, ("synthetic-private",)), (store.delete, ())):
            with self.subTest(method=method.__name__), self.assertRaises(CredentialError) as caught:
                method("https://example.test", *args)
            self.assertNotIn("synthetic", repr(caught.exception))
        self.assertEqual(backend.values, {})


class CoreActions(unittest.IsolatedAsyncioTestCase):
    async def start(self, **kwargs):
        self.ui, self.socket, self.http, self.backend, self.saved, cleanup = await runtime(**kwargs)
        self.addAsyncCleanup(cleanup)

    async def test_public_reads_and_saved_key_do_not_unlock(self):
        await self.start()
        self.assertFalse((await self.ui.load()).admin_verified)
        self.ui.store.save(self.ui.origin, "synthetic-private")
        loaded = await self.ui.load_credential()
        self.assertTrue(loaded.credential_saved)
        self.assertFalse(loaded.admin_verified)
        self.assertNotIn("synthetic-private", repr(loaded))

    async def test_no_change_check_does_not_mutate_defaults(self):
        await self.start()
        before = deepcopy(self.http.server)
        view = await self.ui.verify("synthetic-private")
        self.assertTrue(view.admin_verified)
        self.assertEqual(self.http.server, before)
        calls = [x for x in self.http.calls if x[0] == "PATCH"]
        self.assertEqual(len(calls), 1)
        self.assertNotIn("synthetic-private", repr(calls))

    async def test_keycheck_uses_latest_value_not_stale_ui_default(self):
        await self.start()
        self.http.server["settings"][0]["requestedValue"] += 100
        before = deepcopy(self.http.server)
        await self.ui.verify("synthetic")
        self.assertEqual(self.http.server, before)

    async def test_conflict_rereads_and_rechecks_once(self):
        await self.start()
        count = 0
        original = self.http.request
        async def request(method, path, **kwargs):
            nonlocal count
            if method == "PATCH":
                count += 1
                self.http.patch_status = 409 if count == 1 else 200
            return await original(method, path, **kwargs)
        self.http.request = request
        self.assertTrue((await self.ui.verify("synthetic")).admin_verified)
        self.assertEqual(count, 2)

    async def test_auth_revision_validation_persistence_errors_do_not_unlock(self):
        await self.start()
        for status, code in ((401, "admin_unauthorized"), (403, "admin_disabled"), (409, "settings_revision_conflict"),
                             (422, "server_settings_rejected"), (500, "server_persistence_failed")):
            self.http.patch_status = status
            with self.subTest(status=status), self.assertRaisesRegex(SettingsError, code):
                await self.ui.verify("synthetic")
            self.assertFalse(self.ui.view().admin_verified)

    async def test_claimed_applied_keycheck_is_rejected(self):
        await self.start()
        original = self.http.request
        async def request(method, path, **kwargs):
            result = await original(method, path, **kwargs)
            if method == "PATCH":
                result.body["result"] = "applied"
            return result
        self.http.request = request
        with self.assertRaisesRegex(SettingsError, "admin_check_not_no_change"):
            await self.ui.verify("synthetic")
        self.assertFalse(self.ui.view().admin_verified)

    async def test_store_failure_is_memory_only_and_explicit_error(self):
        await self.start()
        self.backend.fail = True
        with self.assertRaises(CredentialError):
            await self.ui.verify("synthetic-private", remember=True)
        self.assertTrue(self.ui.view().admin_verified)
        self.assertFalse(self.ui.view().credential_saved)
        self.assertNotIn("synthetic-private", repr(self.ui.view()))
        self.assertEqual(self.backend.values, {})

    async def test_verify_save_replace_delete_and_relock(self):
        await self.start()
        await self.ui.verify("synthetic-one", remember=True)
        await self.ui.verify("synthetic-two", remember=True)
        self.assertEqual(self.ui.store.read(self.ui.origin), "synthetic-two")
        view = await self.ui.delete_credential()
        self.assertFalse(view.admin_verified)
        self.assertFalse(view.credential_saved)
        self.assertIsNone(self.ui.store.read(self.ui.origin))

    async def test_generation_changed_during_verify_cannot_unlock(self):
        await self.start()
        async def hook(method, path):
            if method == "PATCH":
                self.ui.settings.session.generation += 1
        self.http.hook = hook
        with self.assertRaises(Exception):
            await self.ui.verify("synthetic")
        self.assertFalse(self.ui.view().admin_verified)

    async def test_dialog_closed_during_auth_drops_response(self):
        await self.start()
        async def hook(method, path):
            if method == "PATCH":
                self.ui.invalidate()
        self.http.hook = hook
        with self.assertRaisesRegex(SettingsError, "dialog_closed"):
            await self.ui.verify("synthetic")
        self.assertIsNone(self.ui._key)

    async def test_admin_write_requires_verified_guard(self):
        await self.start()
        with self.assertRaisesRegex(SettingsError, "admin_check_required"):
            await self.ui.patch_server({KEY: 5000})
        await self.ui.verify("synthetic")
        view = await self.ui.patch_server({KEY: 5000})
        self.assertEqual(view.server_requested[KEY], 5000)

    async def test_rejected_write_relocks_on_401_or_403(self):
        await self.start()
        await self.ui.verify("synthetic")
        self.http.patch_status = 401
        with self.assertRaises(SettingsError):
            await self.ui.patch_server({KEY: 5000})
        self.assertFalse(self.ui.view().admin_verified)

    def candidate(self):
        profile = asdict(self.ui.settings.profile)
        profile.update(wake_word=True, wake_word_ids=["alexa"])
        return profile

    def foreground(self):
        mirror = self.ui.mirror.mirror
        mirror.input = InputView(p.InputPhase.WAITING_FIRST_SPEECH, A)
        mirror.activations[A] = ActivationView(A)
        self.socket.state["input"].update(phase="waiting_first_speech", activationId=A,
            primarySource="manual", deadlineAtUnixMs=1787616015000, remainingMs=15000)

    def background(self):
        mirror = self.ui.mirror.mirror
        mirror.activations[A] = ActivationView(A, input_closed=True, status="draining", accepted_count=1)

    async def test_triggerless_and_empty_wake_selection_are_atomic_rejections(self):
        await self.start()
        for values in (dict(manual=False, wake_word=False), dict(wake_word=True, wake_word_ids=[])):
            candidate = asdict(self.ui.settings.profile); candidate.update(values)
            with self.assertRaises(ValueError):
                await self.ui.apply_profile(candidate, self.ui.context())
            self.assertEqual(self.saved, [])

    async def test_manual_wake_and_wake_only_keep_controls(self):
        await self.start()
        candidate = self.candidate()
        candidate["manual"] = False
        view = await self.ui.apply_profile(candidate, self.ui.context(), choice=ApplyChoice.DEFER)
        self.assertFalse(view.profile["manual"])
        self.assertTrue(view.profile["wake_word"])
        self.assertEqual(view.profile["controls"]["primary_key"], "Ctrl+Shift+Space")
        self.assertTrue(self.saved)

    async def test_na_apply_keeps_activation_and_confirms_session(self):
        await self.start()
        self.foreground()
        candidate = asdict(self.ui.settings.profile); candidate["desired_settings"][KEY] = 5000
        view = await self.ui.apply_profile(candidate, self.ui.context())
        self.assertEqual(view.settings.requested[KEY], 5000)
        # Socket snapshots are an idle projection; no activation command was sent.
        self.assertFalse(any(x["type"] == p.CommandType.ACTIVATION for x in self.socket.commands))

    async def test_reconnect_without_activation_choice_has_no_side_effect(self):
        await self.start(); self.foreground()
        with self.assertRaisesRegex(SettingsError, "activation_choice_required"):
            await self.ui.apply_profile(self.candidate(), self.ui.context())
        self.assertEqual(self.saved, [])
        self.assertEqual(self.ui.context().activation_id, A)

    async def test_idle_background_drain_requires_separate_loss_choice(self):
        await self.start(); self.background()
        with self.assertRaisesRegex(SettingsError, "drain_choice_required"):
            await self.ui.apply_profile(self.candidate(), self.ui.context())
        self.assertEqual(self.saved, [])

    async def test_defer_preserves_foreground_and_background(self):
        await self.start(); self.foreground()
        count = len(self.socket.commands)
        context = self.ui.context()
        await self.ui.apply_profile(self.candidate(), context, choice=ApplyChoice.DEFER)
        self.assertEqual(self.ui.context(), context)
        self.assertEqual(len(self.socket.commands), count)

    async def test_context_race_rejects_old_activation_or_drain(self):
        await self.start()
        context = self.ui.context()
        self.foreground()
        with self.assertRaisesRegex(SettingsError, "apply_context_changed"):
            await self.ui.apply_profile(self.candidate(), context, choice=ApplyChoice.CANCEL, drain_choice="discard")
        self.assertEqual(self.saved, [])

    async def test_persistence_failure_leaves_profile_and_commands(self):
        def fail(candidate): raise OSError("synthetic-secret")
        await self.start(persist=fail)
        before = asdict(self.ui.settings.profile)
        with self.assertRaisesRegex(SettingsError, "profile_persistence_failed"):
            await self.ui.apply_profile(self.candidate(), self.ui.context(), choice=ApplyChoice.DEFER)
        self.assertEqual(asdict(self.ui.settings.profile), before)

    async def test_wait_drain_timeout_keeps_socket_and_restores_pauses(self):
        await self.start(); self.background()
        # Retain deterministic drain data through snapshot refreshes.
        original = self.socket.respond
        async def respond(command):
            await original(command)
            if command["type"] == p.CommandType.SNAPSHOT_REQUEST:
                asyncio.get_running_loop().call_later(.001, self.background)
        self.socket.on_send = respond
        with self.assertRaisesRegex(SettingsError, "drain_pending_retry"):
            await self.ui.apply_profile(self.candidate(), self.ui.context(), drain_choice="wait")
        self.assertTrue(self.ui.settings.session.is_ready)
        self.assertFalse(self.ui.controls.pause_view.desired_manual)
        self.assertFalse(self.ui.controls.pause_view.desired_wake_word)

    async def test_explicit_discard_idle_drain_reconnects_once(self):
        await self.start(); self.background()
        calls = []
        async def reconnect(binding, reason): calls.append((binding, reason))
        self.ui.settings.session.reconnect = reconnect
        await self.ui.apply_profile(self.candidate(), self.ui.context(), drain_choice="discard")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][1], "user_settings_apply")

    async def test_finish_waits_for_actual_completion_before_reconnect(self):
        await self.start(); self.foreground()
        observed = []
        original = self.socket.respond
        async def respond(command):
            if command["type"] == p.CommandType.ACTIVATION:
                observed.append(command["action"])
                mirror = self.ui.mirror.mirror
                mirror.input = InputView()
                self.socket.state["input"].update(phase="idle", activationId=None, primarySource=None,
                    deadlineAtUnixMs=None, remainingMs=None)
                mirror.activations[A] = replace(mirror.activations[A], input_closed=True, status="draining")
                def complete():
                    mirror.activations[A] = replace(mirror.activations[A], status="completed")
                asyncio.get_running_loop().call_later(.025, complete)
            await original(command)
        self.socket.on_send = respond
        async def reconnect(binding, reason):
            observed.append("reconnect")
            self.assertEqual(self.ui.mirror.mirror.view.activations[A].status, "completed")
        self.ui.settings.session.reconnect = reconnect
        await self.ui.apply_profile(self.candidate(), self.ui.context(), choice=ApplyChoice.FINISH, drain_choice="wait")
        self.assertEqual(observed, ["finish", "reconnect"])

    async def test_cancel_targets_captured_activation_and_separate_drain_loss(self):
        await self.start(); self.foreground()
        targets = []
        original = self.socket.respond
        async def respond(command):
            if command["type"] == p.CommandType.ACTIVATION:
                targets.append((command["action"], command["activationId"]))
                self.ui.mirror.mirror.input = InputView()
                self.socket.state["input"].update(phase="idle", activationId=None, primarySource=None,
                    deadlineAtUnixMs=None, remainingMs=None)
                self.ui.mirror.mirror.activations[A] = ActivationView(A, input_closed=True, status="cancelled")
            await original(command)
        self.socket.on_send = respond
        calls = []
        async def reconnect(binding, reason): calls.append(reason)
        self.ui.settings.session.reconnect = reconnect
        await self.ui.apply_profile(self.candidate(), self.ui.context(), choice=ApplyChoice.CANCEL, drain_choice="discard")
        self.assertEqual(targets, [("cancel", A)])
        self.assertEqual(calls, ["user_settings_apply"])

    async def test_close_while_drain_waiting_restores_pauses_without_reconnect(self):
        await self.start(); self.background()
        task = asyncio.create_task(self.ui.apply_profile(self.candidate(), self.ui.context(), drain_choice="wait"))
        await until(lambda: self.ui.controls.pause_view.desired_wake_word)
        self.ui.invalidate()
        with self.assertRaisesRegex(SettingsError, "dialog_closed"):
            await task
        self.assertTrue(self.ui.settings.session.is_ready)
        self.assertFalse(self.ui.controls.pause_view.desired_manual)

    async def test_origin_switch_drops_key_and_cannot_unlock_or_patch(self):
        await self.start()
        await self.ui.verify("synthetic-private")
        self.http.origin = "https://other.test"
        with self.assertRaisesRegex(SettingsError, "server_origin_changed"):
            await self.ui.patch_server({KEY: 5000})
        self.assertIsNone(self.ui._key)

    async def test_preserved_ns_intent_cannot_be_edited_as_session_setting(self):
        await self.start(profile=V2Profile(desired_settings={"wakeWord.vadThreshold": .4}))
        candidate = asdict(self.ui.settings.profile)
        candidate["desired_settings"][KEY] = 5500
        await self.ui.apply_profile(candidate, self.ui.context())
        self.assertEqual(self.ui.settings.profile.desired_settings["wakeWord.vadThreshold"], .4)
        candidate["desired_settings"]["wakeWord.vadThreshold"] = .8
        with self.assertRaisesRegex(SettingsError, "not_individually_startable"):
            await self.ui.apply_profile(candidate, self.ui.context())

    async def test_reapplying_deferred_profile_still_requires_connection_choice(self):
        await self.start(); self.foreground()
        candidate = self.candidate()
        await self.ui.apply_profile(candidate, self.ui.context(), choice=ApplyChoice.DEFER)
        with self.assertRaisesRegex(SettingsError, "activation_choice_required"):
            await self.ui.apply_profile(candidate, self.ui.context())
        self.assertEqual(self.ui.context().activation_id, A)

    async def test_hotkey_collision_preserves_saved_profile(self):
        await self.start()
        candidate = asdict(self.ui.settings.profile)
        candidate["controls"]["secondary_key"] = candidate["controls"]["primary_key"]
        with self.assertRaises(ValueError):
            await self.ui.apply_profile(candidate, self.ui.context())
        self.assertEqual(self.saved, [])

    async def test_disconnect_while_decision_open_rejects_old_context(self):
        await self.start(); self.foreground()
        context = self.ui.context()
        self.ui.settings.session.binding = None
        with self.assertRaisesRegex(SettingsError, "apply_context_changed"):
            await self.ui.apply_profile(self.candidate(), context, choice=ApplyChoice.CANCEL)
        self.assertEqual(self.saved, [])

    async def test_explicit_migration_repair_preserves_unknown_and_retired(self):
        await self.start()
        original = self.ui.settings.profile
        original.unresolved = {"hotkey": {"finish_key": "Ctrl+F", "cancel_key": "Ctrl+C"}, "unknown-field": 17}
        original.retired = {"dictation_window.extension_seconds": 15}
        candidate = asdict(original)
        candidate["unresolved"] = {}  # Cannot bypass by deleting provenance.
        with self.assertRaisesRegex(SettingsError, "profile_repair_required"):
            await self.ui.apply_profile(candidate, self.ui.context(), repair_fields=["hotkey"])
        self.assertEqual(original.unresolved["unknown-field"], 17)
        del original.unresolved["unknown-field"]  # Explicit external repair boundary.
        candidate = asdict(original)
        await self.ui.apply_profile(candidate, self.ui.context(), repair_fields=["hotkey"])
        self.assertEqual(self.ui.settings.profile.unresolved, {})
        self.assertEqual(self.ui.settings.profile.retired, {"dictation_window.extension_seconds": 15})

    async def test_new_background_drain_during_pause_needs_new_choice(self):
        await self.start()
        original = self.socket.respond
        async def respond(command):
            if command["type"] == p.CommandType.SUPPRESSION and command["manual"]:
                self.background()
            await original(command)
        self.socket.on_send = respond
        with self.assertRaisesRegex(SettingsError, "apply_context_changed"):
            await self.ui.apply_profile(self.candidate(), self.ui.context(), drain_choice="discard")
        self.assertTrue(self.ui.settings.session.is_ready)


class QtSurface(unittest.TestCase):
    """Own a QApplication lifetime rather than pumping legacy suite widgets.

    A full discovery process also exercises old GUI/native-filter fixtures.
    Their pending events survive long headless suites and caused a reproducible
    Windows access violation when this new suite pumped QApplication again.
    Each surface case therefore executes its unchanged assertions in a fresh
    project-venv process. Core faults and the real server checkpoint retain
    their shared-session/cross-thread coverage; no case is skipped.
    """
    def __init__(self, methodName="runTest"):
        super().__init__(methodName)
        if os.environ.get("VOICE_STT_QT_TEST_CHILD") != "1":
            setattr(self, methodName, self._run_isolated)

    def _run_isolated(self):
        environment = dict(os.environ, VOICE_STT_QT_TEST_CHILD="1", QT_QPA_PLATFORM="offscreen", PYTHONUTF8="1")
        child = subprocess.run([sys.executable, "-X", "faulthandler", "-W", "error", "-m", "unittest",
            "tests.test_v2_settings_ui.QtSurface." + self._testMethodName, "-v"],
            cwd=Path(__file__).resolve().parents[1], env=environment, capture_output=True,
            text=True, encoding="utf-8", timeout=30)
        self.assertEqual(child.returncode, 0, child.stdout + child.stderr)
        self.assertIn("Ran 1 test", child.stderr)

    @classmethod
    def setUpClass(cls):
        if os.environ.get("VOICE_STT_QT_TEST_CHILD") != "1":
            return
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls.app = QApplication.instance() or QApplication([])

    def setUp(self):
        if os.environ.get("VOICE_STT_QT_TEST_CHILD") != "1":
            return
        # Earlier Qt suites leave cyclic, parentless Python widget wrappers.
        # Collect those on the GUI thread before starting the asyncio worker;
        # their C++ destruction must not occur in a worker's allocation/GC.
        gc.collect()
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.app.processEvents()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.loop.run_forever)
        self.thread.start()
        data = asyncio.run_coroutine_threadsafe(runtime(), self.loop).result(5)
        self.ui, self.socket, self.http, self.backend, self.saved, self.cleanup = data
        self.bridge = V2SettingsBridge(self.loop, lambda: self.ui)
        self.dialog = V2SettingsDialog(self.bridge)
        self.dialog.show()
        self.wait(lambda: self.dialog._view is not None)
        self.dialog.timer.stop()

    def tearDown(self):
        if os.environ.get("VOICE_STT_QT_TEST_CHILD") != "1":
            return
        self.dialog.close()
        self.app.processEvents()
        asyncio.run_coroutine_threadsafe(self.cleanup(), self.loop).result(5)
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join(5)
        self.loop.close()
        self.dialog.deleteLater()
        self.bridge.deleteLater()
        # processEvents alone does not deliver DeferredDelete without exec().
        QCoreApplication.sendPostedEvents(None, QEvent.Type.DeferredDelete)
        self.app.processEvents()

    def wait(self, condition):
        deadline = time.monotonic() + 5
        while not condition():
            self.app.processEvents()
            if time.monotonic() > deadline:
                self.fail("Qt request timed out")
            time.sleep(.002)
        self.app.processEvents()

    def test_scope_schema_policy_requested_effective_and_calibration_visible(self):
        self.assertEqual(self.dialog.tabs.count(), 3)
        self.assertIn("Sessionrevision", self.dialog.revisions.text())
        row = self.dialog._rows["session"][KEY]
        table = self.dialog._tables["session"]
        self.assertEqual(table.item(row, 2).text(), "4000")
        self.assertEqual(table.item(row, 3).text(), "4000")
        self.assertEqual(table.item(row, 4).text(), "3000")
        self.assertEqual(table.item(row, 6).text(), "Nächstes Diktat")
        row = self.dialog._rows["session"]["wakeWord.preRollMs"]
        self.assertIn("calibration pending", table.item(row, 7).text())
        self.assertIn("ms", table.item(self.dialog._rows["session"][KEY], 7).text())

    def test_ns_noise_vad_readonly_and_server_initially_locked(self):
        for key in ("wakeWord.noiseSuppressionEnabled", "wakeWord.vadThreshold"):
            self.assertFalse(self.dialog._editors["session"][key].isEnabled())
        self.assertFalse(self.dialog.apply_server_button.isEnabled())
        self.assertTrue(all(not e.isEnabled() for e in self.dialog._editors["server"].values()))

    def test_bool_and_backend_have_typed_editors(self):
        from PySide6.QtWidgets import QComboBox
        self.assertIsInstance(self.dialog._editors["server"]["wakeWord.noiseSuppressionEnabled"], QComboBox)
        self.assertIsInstance(self.dialog._editors["server"]["wakeWord.inferenceBackend"], QComboBox)

    def test_empty_catalog_has_explicit_message(self):
        from voice_stt_client.core.settings_service import WakeCatalog
        self.dialog._view = replace(self.dialog._view, catalog=WakeCatalog(1, {}))
        self.dialog.render(reset=True)
        self.assertEqual(self.dialog.wake_list.count(), 0)
        self.assertIn("Keine Wake Words", self.dialog.catalog_status.text())

    def test_old_epoch_reply_after_reopen_cannot_unlock_new_origin(self):
        previous = self.dialog._view
        epoch = self.bridge.epoch
        self.dialog.close()
        self.bridge._factory = lambda: SettingsUISession(self.ui.settings, self.ui.controls, self.ui.mirror,
            credential_store=self.ui.store, persist_profile=lambda p: None)
        self.dialog.show()
        self.wait(lambda: self.dialog._view is not None)
        self.dialog.timer.stop()
        self.dialog._receive(UIReply(epoch, 9999, "verify", view=replace(previous, admin_verified=True)))
        self.assertFalse(self.dialog._view.admin_verified)

    def test_password_check_clears_field_and_unlocks_only_after_patch(self):
        self.dialog.key.setText("synthetic-private")
        self.dialog.verify_button.click()
        self.assertEqual(self.dialog.key.text(), "")
        self.wait(lambda: self.dialog._view.admin_verified)
        self.assertTrue(self.dialog.apply_server_button.isEnabled())
        self.assertTrue(any(x[0] == "PATCH" for x in self.http.calls))

    def test_bad_key_error_is_visible_and_locked(self):
        self.http.patch_status = 401
        self.dialog.key.setText("synthetic-wrong")
        self.dialog.verify_button.click()
        self.wait(lambda: "401" in self.dialog.status.text())
        self.assertFalse(self.dialog.apply_server_button.isEnabled())

    def test_all_http_errors_have_distinct_user_messages(self):
        for status in (403, 409, 422, 500):
            self.http.patch_status = status
            self.dialog.key.setText("synthetic")
            self.dialog.verify_button.click()
            self.wait(lambda: str(status) in self.dialog.status.text())
            self.assertFalse(self.dialog.apply_server_button.isEnabled())

    def test_server_editor_uses_real_service_and_revision(self):
        self.dialog.key.setText("synthetic")
        self.dialog.verify_button.click()
        self.wait(lambda: self.dialog._view.admin_verified)
        self.dialog._editors["server"][KEY].setText("5500")
        self.dialog.apply_server_button.click()
        self.wait(lambda: self.dialog._view.server_requested[KEY] == 5500)

    def test_session_draft_survives_inspect_requested_effective_refresh(self):
        editor = self.dialog._editors["session"][KEY]
        editor.setText("5700")
        self.dialog._request("inspect")
        self.wait(lambda: not self.bridge.busy)
        self.assertEqual(editor.text(), "5700")

    def test_qsettings_export_and_config_have_no_key(self):
        with tempfile.TemporaryDirectory() as folder:
            meta = QSettings(str(Path(folder)/"settings.ini"), QSettings.Format.IniFormat)
            self.dialog.metadata = meta
            self.dialog.key.setText("synthetic-private")
            self.dialog.remember.setChecked(True)
            self.dialog.verify_button.click()
            self.wait(lambda: self.dialog._view.credential_saved)
            meta.sync()
            self.assertNotIn("synthetic-private", Path(meta.fileName()).read_text())
            self.assertNotIn("synthetic-private", repr(self.dialog._view))
            self.assertNotIn("synthetic-private", repr(self.ui.settings.profile))
            self.assertTrue(all(key.endswith(("/saved", "/target")) for key in meta.allKeys()))

    def test_unavailable_and_unknown_saved_ids_remain_visible(self):
        v = self.dialog._view
        profile = p._thaw(v.profile); profile["wake_word_ids"] = ["missing"]
        self.dialog._view = replace(v, profile=profile)
        self.dialog.render(reset=True)
        self.assertIn("missing", self.dialog.selected_wake_ids())
        self.assertIn("nicht verfügbar", self.dialog.wake_list.item(self.dialog.wake_list.count()-1).text())

    def test_catalog_failure_keeps_prior_selection(self):
        self.dialog.wake_list.item(0).setCheckState(Qt.CheckState.Checked)
        previous = self.dialog.selected_wake_ids()
        self.http.fail_path = "/api/v2/wake-words"
        self.dialog.reload_button.click()
        self.wait(lambda: "synthetic_http_failure" in self.dialog.status.text())
        self.assertEqual(self.dialog.selected_wake_ids(), previous)

    def test_dialog_close_and_old_reply_do_not_unlock(self):
        epoch = self.bridge.epoch
        reply = UIReply(epoch, 1000, "verify", view=replace(self.dialog._view, admin_verified=True))
        self.dialog.close()
        self.dialog._receive(reply)
        self.assertFalse(self.dialog.apply_server_button.isEnabled())
        self.assertIsNone(self.dialog._view)

    def test_rejected_triggerless_ui_does_not_persist(self):
        self.dialog.manual.setChecked(False)
        self.dialog.wake.setChecked(False)
        self.dialog.apply_profile_button.click()
        self.assertEqual(self.saved, [])
        self.assertIn("Mindestens eine", self.dialog.status.text())

    def test_local_surface_contains_no_legacy_trigger_or_mode_controls(self):
        from voice_stt_client.core.config import AppConfig
        with patch("voice_stt_client.ui.settings_dialog.AudioCapture.list_devices", return_value=[]):
            local = SettingsDialog(AppConfig(), lambda *args: True, v2_local=True)
        self.assertFalse(any(key.startswith(("session.", "dictation_window.", "hotkey.", "server.")) for key in local._editors))
        self.assertIn("clipboard.restore_previous", local._editors)
        self.assertIn("audio.device", local._editors)
        local.close(); local.deleteLater()

    def test_decision_cancel_default_and_all_three_choices(self):
        context = ApplyContext(1, "session", A, ("older",))
        decision = ApplyDecisionDialog(context)
        self.assertFalse(decision.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
        self.assertIsNone(decision.plan())
        for choice in ApplyChoice:
            decision.choice.setCurrentIndex(decision.choice.findData(choice))
            decision.drain.setCurrentIndex(decision.drain.findData("wait"))
            self.assertTrue(decision.buttons.button(QDialogButtonBox.StandardButton.Ok).isEnabled())
            decision.accept()
            self.assertEqual(decision.plan(), (choice, "wait"))
        decision.reject()
        self.assertIsNone(decision.plan())
        decision.deleteLater()


if __name__ == "__main__":
    unittest.main()
