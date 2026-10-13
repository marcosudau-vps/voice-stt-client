"""AP110 runtime retirement, packaged identity and preserved utility gates."""
import ast
import asyncio
from copy import deepcopy
from dataclasses import asdict
import json
import os
from pathlib import Path
import runpy
import subprocess
import tarfile
import zipfile
import io
import tempfile
import unittest
from unittest.mock import patch

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
from voice_stt_client.core.version import __version__, read_build_identity
from voice_stt_client.core.v2_runtime import V2Runtime, runtime_profile, v2_endpoint
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig, V2TransportState
from tests.test_v2_runtime_integration import config_in
from tests.test_text_injector import MockInjectionBackend
from tests.test_obs040_failure_isolation import ExplodingIngress

ROOT = Path(__file__).resolve().parents[1]


class RuntimeRetirement(unittest.TestCase):
    def test_logs_cannot_select_lifecycle_before_first_domain_snapshot(self):
        from voice_stt_client.core.feedback_reducer import FeedbackEngine
        from voice_stt_client.core.feedback_mapping import FeedbackMappingConfig
        from voice_stt_client.core.event_models import EventConnectionState
        from tests.test_event_normalizer import log_result
        engine = FeedbackEngine(FeedbackMappingConfig())
        self.assertFalse(hasattr(engine, 'handle_stt_fallback'))
        self.assertIsNone(engine.handle_event_stream(log_result('transcription.recording_started'),
            generation=1, session_id='legacy'))
        decision = engine.update_connection(EventConnectionState.LIVE, stt_ready=True,
            generation=1, session_id='legacy')
        self.assertFalse(decision.publish)
        self.assertIsNone(decision.snapshot)

    def test_product_has_no_v1_controller_transport_or_headless_class(self):
        for path in (ROOT/'voice_stt_client').rglob('*.py'):
            tree = ast.parse(path.read_text(encoding='utf8'))
            classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}
            self.assertTrue(classes.isdisjoint({'STTController', 'STTSession', 'RealtimeSTTClient'}), path)
        from voice_stt_client.core.config import SessionConfig
        self.assertFalse(hasattr(SessionConfig, 'build_url'))
        self.assertFalse(hasattr(SessionConfig, 'query_parameters'))

    def test_only_local_metadata_is_editable_in_retained_dialog(self):
        from voice_stt_client.core.settings_metadata import SETTING_DEFINITIONS
        for definition in SETTING_DEFINITIONS:
            self.assertFalse(definition.path.startswith(('session.', 'dictation_window.', 'server.', 'hotkey.')))

    def test_v1_messages_do_not_become_v2_state(self):
        for kind in ('ready', 'status', 'timeline', 'start', 'stop', 'extend', 'trigger_ack'):
            with self.subTest(kind=kind):
                self.assertIsNone(p.decode_server_message({'type': kind, 'ok': True, 'state': 'recording'}))

    def test_packaged_defaults_have_v2_endpoint_and_no_timer_wishes(self):
        config = AppConfig.load(user_path=Path(tempfile.gettempdir())/'ap110-absent-config.yaml')
        self.assertEqual(config.server.url, 'wss://stt.voice.marcosudau.com/ws/v2')
        self.assertEqual(runtime_profile(config).desired_settings, {})
        self.assertEqual(v2_endpoint('wss://example/ws/transcribe?mode=wake'), 'wss://example/ws/v2')
        self.assertEqual(v2_endpoint('wss://example/other'), 'wss://example/other')

    def test_v2_profile_ignores_stale_legacy_mode_and_timers(self):
        from voice_stt_client.core.v2_profile import V2Profile
        config = AppConfig()
        config.v2_profile = asdict(V2Profile())
        config.session.mode = 'retired-invalid-mode'
        config.hotkey.mode = 'retired-invalid-mode'
        config.hotkey.toggle_key = 'retired-invalid-key'
        config.dictation_window.followup_timeout = -99
        config.validate()
        self.assertEqual(runtime_profile(config).desired_settings, {})

    def test_fixtures_are_exact_pinned_copies(self):
        for name in ('protocol-v2-vectors.json', 'protocol-v2-client-fixtures.json', 'protocol-v2-provenance.json'):
            self.assertEqual((ROOT/'tests/contracts'/name).read_bytes(),
                (ROOT/'voice_stt_client/resources'/name).read_bytes())

    def test_windows_checkout_keeps_pinned_resource_bytes(self):
        # Reproduce the runner's checkout conversion, not merely this working
        # tree's bytes. Git must preserve all packaged contract files under
        # core.autocrlf=true before Python imports or tests can touch them.
        with tempfile.TemporaryDirectory() as folder:
            checkout = Path(folder)
            def git(*args):
                return subprocess.check_output(['git', '-C', str(checkout), *args],
                    stderr=subprocess.STDOUT)
            git('init', '--quiet')
            git('config', 'core.autocrlf', 'true')
            git('config', 'core.safecrlf', 'false')
            (checkout/'.gitattributes').write_bytes((ROOT/'.gitattributes').read_bytes())
            expected = {}
            for source in ('tests/contracts', 'voice_stt_client/resources'):
                for name in ('protocol-v2-vectors.json', 'protocol-v2-client-fixtures.json', 'protocol-v2-provenance.json'):
                    relative = source+'/'+name
                    data = subprocess.check_output(['git', '-C', str(ROOT), 'show', 'HEAD:'+relative])
                    target = checkout/relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
                    expected[relative] = data
            git('add', '--', '.gitattributes', 'tests', 'voice_stt_client')
            exported = checkout/'exported'
            git('checkout-index', '--all', '--force', '--prefix='+exported.as_posix()+'/')
            for relative, data in expected.items():
                self.assertEqual((exported/relative).read_bytes(), data, relative)


class BuildIdentity(unittest.TestCase):
    def test_distribution_guard_rejects_secret_namespace_and_dirty_identity(self):
        from scripts.client_release_guard import validate_distributions
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            files = {'wheel': root/'candidate.whl', 'sdist': root/'candidate.tar.gz'}
            content = {name.relative_to(ROOT).as_posix(): name.read_bytes()
                for name in (ROOT/'voice_stt_client/resources').glob('*.json')}
            content['voice_stt_client/config.yaml'] = DEFAULT_CONFIG_PATH.read_bytes()
            for index in range(8): content[f'voice_stt_client/assets/{index}.wav'] = b'fixture'
            identity = dict(schemaVersion=1, version=__version__, clientCommit='d'*40,
                sourceCommit='d'*40, sourceDirty=False)
            def archives(extra=None, dirty=False):
                identity['sourceDirty'] = dirty
                values = dict(content)
                values['voice_stt_client/build_identity.json'] = json.dumps(identity).encode()
                if extra: values[extra] = b'forbidden'
                with zipfile.ZipFile(files['wheel'], 'w') as archive:
                    for name, data in values.items(): archive.writestr(name, data)
                with tarfile.open(files['sdist'], 'w:gz') as archive:
                    for name, data in values.items():
                        member = tarfile.TarInfo('package/'+name)
                        member.size = len(data)
                        archive.addfile(member, io.BytesIO(data))
            archives()
            self.assertEqual(validate_distributions(files, 'd'*40)['wheel'], identity)
            with self.assertRaises(ValueError): validate_distributions(files, 'e'*40)
            for extra in ('core/legacy.py', 'ui/legacy.py', 'voice_stt_client/.env', 'voice_stt_client/history.db', 'tests/test_fake.py'):
                archives(extra)
                with self.subTest(extra=extra), self.assertRaises(ValueError): validate_distributions(files)
            archives(dirty=True)
            with self.assertRaises(ValueError): validate_distributions(files)

    def test_transport_hello_uses_canonical_release_identity(self):
        config = V2TransportConfig()
        self.assertEqual(config.client_version, __version__)
        self.assertEqual(config.client_commit, read_build_identity()['clientCommit'])

    def test_installed_stamp_wins_and_invalid_identity_is_rejected(self):
        from voice_stt_client.core import version
        with tempfile.TemporaryDirectory() as folder, patch.object(version, 'PACKAGE_DIR', Path(folder)):
            stamp = Path(folder)/'build_identity.json'
            for commit in ('b'*40, 'unknown', 'fake-sha'):
                stamp.write_text(json.dumps(dict(schemaVersion=1, version=__version__, clientCommit=commit)), encoding='utf8')
                if commit == 'fake-sha':
                    with self.assertRaises(RuntimeError): read_build_identity()
                else: self.assertEqual(read_build_identity()['clientCommit'], commit)

    def test_sdist_rebuild_preserves_original_identity(self):
        namespace = runpy.run_path(str(ROOT/'setup.py'))
        identity = namespace['identity']
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root/'voice_stt_client').mkdir()
            value = dict(schemaVersion=1, version=__version__, clientCommit='c'*40,
                sourceCommit='c'*40, sourceDirty=False)
            (root/'voice_stt_client/build_identity.json').write_text(json.dumps(value), encoding='utf8')
            with patch.dict(identity.__globals__, ROOT=root):
                self.assertEqual(identity(), value)

    def test_unknown_server_identity_is_not_promoted_to_pinned_proof(self):
        from tests.test_v2_protocol import FIXTURES
        value = deepcopy(FIXTURES['helloAccepted'])
        value['serverCommit'] = 'unknown'
        value['snapshot']['serverCommit'] = 'unknown'
        self.assertEqual(p.decode_server_message(value).payload['serverCommit'], 'unknown')


class FailureIsolation(unittest.IsolatedAsyncioTestCase):
    async def test_broken_logging_keeps_transport_status_and_control_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            ingress = ExplodingIngress()
            runtime = V2Runtime(config_in(folder), backend=MockInjectionBackend(), observability=ingress)
            try:
                runtime.session._state(V2TransportState.CONNECTING, 'synthetic')
                self.assertEqual(runtime.get_snapshot().transport, 'connecting')
                result = await runtime.primary_dictation_action()
                self.assertFalse(result.success)
                self.assertGreater(ingress.calls, 0)
            finally:
                await runtime.shutdown()

    async def test_legacy_endpoint_is_blocked_without_any_connector_call(self):
        calls = []
        async def connector(*args, **kwargs): calls.append(args)
        session = V2STTSession(V2TransportConfig(url='ws://127.0.0.1/ws/transcribe'), connector=connector)
        await session.run()
        self.assertEqual(session.status.state, V2TransportState.BLOCKED)
        self.assertEqual(calls, [])

    async def test_packaging_probe_cannot_contact_live_services(self):
        from voice_stt_client.release_probe import network_probe
        for url in ('wss://stt.voice.marcosudau.com/ws/v2', 'ws://example/ws/v2', 'ws://localhost/ws/transcribe'):
            with self.subTest(url=url), self.assertRaises(ValueError): await network_probe(url)


class StartupPreferences(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from PySide6.QtWidgets import QApplication
        cls.qt = QApplication.instance() or QApplication([])

    def desktop(self, config, *, succeeds=True):
        from voice_stt_client.ui.v2_application import V2DesktopApplication
        from tests.test_ui_application import FakeBridge, FakeGuard, FakeHotkeyBackend, FakeLedFeedback
        class Conflict(FakeHotkeyBackend):
            def register(self, hwnd, hotkey_id, modifiers, virtual_key):
                if virtual_key == 0x20 and modifiers & 4 and not modifiers & 1:
                    raise OSError(1409, 'synthetic occupied space')
                super().register(hwnd, hotkey_id, modifiers, virtual_key)
        bridge = FakeBridge(succeeds)
        desktop = V2DesktopApplication(self.qt, config, FakeGuard(), bridge=bridge,
            hotkey_backend=Conflict(), led_feedback=FakeLedFeedback())
        self.addCleanup(desktop.shutdown)
        return desktop

    def test_failed_start_and_retry_restore_original_bindings_and_profile_bytes(self):
        with tempfile.TemporaryDirectory() as folder:
            config = config_in(folder)
            config.save_user()
            before = config._config_source_path.read_bytes()
            desktop = self.desktop(config, succeeds=False)
            original = deepcopy(desktop.hotkeys.config)
            with patch('voice_stt_client.ui.application.QMessageBox.critical'):
                self.assertFalse(desktop.start())
            self.assertEqual(desktop.hotkeys.config, original)
            self.assertEqual(config._config_source_path.read_bytes(), before)
            desktop.bridge.start_result = True
            self.assertTrue(desktop.start())
            self.assertNotEqual(desktop.hotkeys.config, original)
            self.assertTrue(desktop.config._needs_profile_persist)
            # GUI never writes a provisional preference before worker bootstrap.
            self.assertEqual(config._config_source_path.read_bytes(), before)

    def test_disabled_keys_keep_preferences_and_register_nothing(self):
        with tempfile.TemporaryDirectory() as folder:
            config = config_in(folder)
            config.v2_profile['controls']['enabled'] = False
            desktop = self.desktop(config)
            self.assertTrue(desktop.start())
            self.assertEqual(desktop._hotkey_backend.registered, [])
            self.assertEqual(desktop.config.v2_profile, config.v2_profile)


if __name__ == '__main__':
    unittest.main()
