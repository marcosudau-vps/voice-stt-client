"""AP050 phase/source matrix, actual transport guards and native rollback."""

import asyncio
from copy import deepcopy
from dataclasses import replace
import os
from types import SimpleNamespace
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.activation_mirror import ActivationMirror, MirrorState
from voice_stt_client.core.config import HotkeyConfig, SessionConfig
from voice_stt_client.core.v2_controls import (
    ActiveAction, ControlConfig, ControlIntent, ControlMigrationConflict,
    ControlSlot, V2ControlService, migrate_hotkeys, plan_control,
)
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig, V2TransportState
from voice_stt_client.core.command_tracker import CommandTimeout
from voice_stt_client.ui.hotkeys import V2HotkeyManager, MOD_NOREPEAT
from tests.test_v2_mirror import snapshot, A, B
from tests.test_v2_transport import FakeWebSocket, no_settings, until


class PhaseMatrix(unittest.IsolatedAsyncioTestCase):
    async def test_all_5_phases_4_actions_2_slots_2_sources(self):
        seen = []
        class Session:
            binding = None
            is_ready = True
            def set_desired_suppression(self, *mask): pass
            async def request(self, kind, **fields):
                seen.append((kind, fields))
                return "actual request boundary"
        session, mirror = Session(), ActivationMirror()
        service = V2ControlService(session, SimpleNamespace(mirror=mirror), audio_ready=lambda: True)
        session.binding = SimpleNamespace(generation=1, session_id=snapshot().sessionId)
        for source in ("manual", "wake_word"):
            for phase in p.InputPhase:
                for action in ActiveAction:
                    for slot in (ControlSlot.PRIMARY, ControlSlot.SECONDARY):
                        with self.subTest(source=source, phase=phase, action=action, slot=slot):
                            raw = snapshot(active=None if phase == p.InputPhase.IDLE else A, phase=phase).to_mapping()
                            raw['input']['primarySource'] = None if phase == p.InputPhase.IDLE else source
                            mirror = ActivationMirror()
                            mirror.begin(1, p.parse_snapshot(raw), 0)
                            service.mirror_connection.mirror = mirror
                            service.config = ControlConfig(primary_action=action, secondary_action=action)
                            before = len(seen)
                            result = await service.press(slot)
                            if phase == p.InputPhase.IDLE:
                                expected = 'activate' if slot == ControlSlot.PRIMARY else None
                            elif action == ActiveAction.NONE or (action == ActiveAction.REFRESH and phase in (
                                    p.InputPhase.WAITING_FIRST_SPEECH, p.InputPhase.CLOSING_INPUT)):
                                expected = None
                            else:
                                expected = str(action)
                            self.assertEqual(len(seen) - before, int(expected is not None))
                            if expected:
                                self.assertEqual(seen[-1][1]['action'], expected)
                                if expected == 'activate':
                                    self.assertEqual(seen[-1][1]['source'], 'manual')
                                    self.assertNotIn('activationId', seen[-1][1])
                                else:
                                    self.assertEqual(seen[-1][1]['activationId'], A)
                                    self.assertNotIn('source', seen[-1][1])
                            else:
                                self.assertIsNone(result)

    async def test_idle_effective_manual_and_local_audio_barriers(self):
        m = ActivationMirror(); m.begin(1, snapshot(), 0)
        self.assertIsNotNone(plan_control(m.view, 'primary', ControlConfig()))
        for effective, audio in ((False, True), (True, False), (False, False)):
            data = snapshot().to_mapping()
            data['trigger']['effective']['manual'], data['audioAvailable'] = effective, audio
            m = ActivationMirror()
            m.begin(1, p.parse_snapshot(data), 0)
            self.assertIsNone(plan_control(m.view, 'primary', ControlConfig()))
        m = ActivationMirror(); m.begin(1, snapshot(), 0)
        m.protocol_fault(1, 0)
        self.assertIsNone(plan_control(m.view, 'primary', ControlConfig()))

    async def test_no_local_deadline_or_vad_side_effect(self):
        m = ActivationMirror(); m.begin(1, snapshot(active=A, phase='segment_active'), 0)
        deadline = m.view.input.deadline
        for now in (10, 100, 10000):
            m.tick(1, now)
            self.assertEqual(m.view.input.phase, p.InputPhase.SEGMENT_ACTIVE)
            self.assertEqual(m.view.input.deadline, deadline)
        intent = plan_control(m.view, 'primary', ControlConfig())
        self.assertEqual(intent, ControlIntent(1, m.view.session_id, 'refresh', A))
        self.assertFalse(hasattr(intent, 'deadline'))


class Controls(unittest.IsolatedAsyncioTestCase):
    async def start(self, *, bootstrap=no_settings, **config):
        class FreshSocket(FakeWebSocket):
            def push(self, value):
                if isinstance(value, dict) and value.get('type') == 'hello.accepted':
                    value['snapshot']['lastEventSeq'] = 0
                    value['snapshot']['settingsRevision'] = 0
                super().push(value)
        sockets = []
        state = {'version': 0, 'mask': (False, False)}
        async def connect(*args, **kwargs):
            socket = FreshSocket(session_id=p.new_id()); sockets.append(socket)
            async def reply(command):
                if command['type'] == p.CommandType.SUPPRESSION:
                    state['version'] += 1
                    state['mask'] = command['manual'], command['wakeWord']
                elif command['type'] == p.CommandType.SNAPSHOT_REQUEST:
                    data = snapshot(version=state['version']).to_mapping()
                    data['sessionId'] = socket.session_id
                    data['trigger']['suppressed'] = dict(manual=state['mask'][0], wakeWord=state['mask'][1])
                    data['trigger']['effective'] = dict(manual=not state['mask'][0], wakeWord=not state['mask'][1])
                    socket.push(data)
                socket.reply(command, revision=0, version=state['version'])
            socket.on_send = reply
            return socket
        session = V2STTSession(V2TransportConfig(ack_timeout=.1, command_retries=0, backoff_initial=.01, **config),
                               bootstrap=bootstrap, connector=connect)
        mirror = V2MirrorConnection(session)
        audio = [True]
        controls = V2ControlService(session, mirror, audio_ready=lambda: audio[0])
        runner = asyncio.create_task(session.run())
        self.addAsyncCleanup(self.cleanup, controls, mirror, runner)
        await until(lambda: session.is_ready and not mirror.mirror.view.snapshot_pending)
        return session, mirror, controls, sockets, state, audio

    async def cleanup(self, controls, mirror, runner):
        await controls.close(); await mirror.close()
        await asyncio.gather(runner, return_exceptions=True)

    async def test_duplicate_pending_and_audio_desired_pause_guards(self):
        session, mirror, controls, sockets, state, audio = await self.start()
        socket = sockets[-1]; held = asyncio.Event(); release = asyncio.Event(); original = socket.on_send
        async def hold(command):
            if command['type'] == p.CommandType.ACTIVATION:
                held.set(); await release.wait()
            await original(command)
        socket.on_send = hold
        first = asyncio.create_task(controls.press('primary'))
        await held.wait()
        self.assertIsNone(await controls.press('primary'))
        self.assertIsNone(await controls.control('finish'))
        release.set(); await first
        self.assertEqual(len([c for c in socket.commands if c['type'] == p.CommandType.ACTIVATION]), 1)
        audio[0] = False
        self.assertIsNone(await controls.press('primary'))
        audio[0] = True
        await controls.set_pause('manual', True)
        self.assertIsNone(await controls.press('primary'))

    async def test_configuring_and_resync_send_no_activation(self):
        session, mirror, controls, sockets, _, _ = await self.start()
        intent = plan_control(mirror.mirror.view, 'primary', controls.config)
        count = len(sockets[-1].commands)
        session._state(V2TransportState.CONFIGURING)
        self.assertIsNone(await controls.execute(intent))
        session._state(V2TransportState.READY)
        mirror.mirror.protocol_fault(session.generation, 0)
        self.assertEqual(mirror.mirror.view.state, MirrorState.RESYNCING)
        self.assertIsNone(await controls.execute(intent))
        self.assertEqual(len(sockets[-1].commands), count)

    async def test_old_activation_intent_never_retargeted_and_invalid_phase_no_retry(self):
        session, mirror, controls, sockets, _, _ = await self.start()
        socket = sockets[-1]
        def foreground(aid, phase, version):
            data = snapshot(version=version, active=aid, phase=phase).to_mapping()
            data['sessionId'] = session.binding.session_id
            session.dispatch(p.parse_snapshot(data), session.binding)
        foreground(A, 'segment_active', 2)
        intent = plan_control(mirror.mirror.view, 'primary', controls.config)
        foreground(B, 'segment_active', 3)
        original = socket.on_send
        async def reply(command):
            if command['type'] == p.CommandType.ACTIVATION:
                socket.reply(command, 'stale_activation', version=3, revision=0, phase='segment_active')
            else:
                # Keep B authoritative during stale-A snapshot clarification.
                if command['type'] == p.CommandType.SNAPSHOT_REQUEST:
                    data = snapshot(version=3, active=B, phase='segment_active').to_mapping()
                    data['sessionId'] = session.binding.session_id; socket.push(data)
                    socket.reply(command, version=3, revision=0)
                else: await original(command)
        socket.on_send = reply
        result = await controls.execute(intent)
        self.assertEqual(result.command.payload['activationId'], A)
        self.assertEqual(result.ack.result, p.AckResult.STALE_ACTIVATION)
        await until(lambda: not mirror.mirror.view.snapshot_pending)
        self.assertEqual(mirror.mirror.view.input.activation_id, B)
        async def invalid(command): socket.reply(command, 'invalid_phase', version=3, revision=0, phase='waiting_first_speech')
        socket.on_send = invalid
        count = len(socket.commands)
        await controls.execute(ControlIntent(session.generation, session.binding.session_id, 'refresh', B))
        await asyncio.sleep(.02)
        self.assertEqual(len(socket.commands), count + 1)

    async def test_complete_mask_coalesces_and_confirmation_waits_for_snapshot(self):
        session, mirror, controls, sockets, _, _ = await self.start()
        socket = sockets[-1]; entered, release = asyncio.Event(), asyncio.Event(); original = socket.on_send
        async def held(command):
            if command['type'] == p.CommandType.SUPPRESSION:
                entered.set(); await release.wait()
            await original(command)
        socket.on_send = held
        first = asyncio.create_task(controls.set_pause('manual', True))
        await entered.wait()
        view = controls.pause_view
        self.assertTrue(view.desired_manual)
        self.assertFalse(view.confirmed_manual)
        self.assertTrue(view.pending)
        second = asyncio.create_task(controls.set_pause('wakeWord', True))
        await asyncio.sleep(0)
        release.set(); await asyncio.gather(first, second)
        await until(lambda: not controls.pause_view.pending)
        self.assertEqual(session._desired_suppression, (True, True))
        self.assertEqual(controls.pause_view.confirmed_wake_word, True)
        masks = [(c['manual'], c['wakeWord']) for c in socket.commands if c['type'] == p.CommandType.SUPPRESSION]
        self.assertEqual(masks[-2:], [(True, False), (True, True)])
        self.assertFalse(mirror.mirror.view.trigger['effective']['manual'])

    async def test_lost_ack_reconnect_keeps_intent_without_false_confirmation(self):
        session, mirror, controls, sockets, _, _ = await self.start()
        binding = session.binding; socket = sockets[-1]
        socket.on_send = lambda command: asyncio.sleep(0)
        with self.assertRaises(CommandTimeout): await controls.set_pause('manual', True)
        self.assertEqual(session._desired_suppression, (True, False))
        self.assertIsNone(controls.pause_view.confirmed_manual)
        await until(lambda: session.is_ready and session.binding is not binding and not controls.pause_view.pending)
        self.assertTrue(controls.pause_view.confirmed_manual)
        self.assertIsNone(await controls.execute(ControlIntent(binding.generation, binding.session_id, 'finish', A)))

    async def test_pause_during_bootstrap_ack_restored_before_ready(self):
        session, mirror, controls, sockets, _, _ = await self.start()
        old = session.binding
        original_connector = session._connector
        held, release = asyncio.Event(), asyncio.Event()
        async def connector(*args, **kwargs):
            socket = await original_connector(*args, **kwargs); original = socket.on_send
            async def reply(command):
                if command['type'] == p.CommandType.SUPPRESSION and not held.is_set():
                    held.set(); await release.wait()
                await original(command)
            socket.on_send = reply
            return socket
        session._connector = connector
        await session.reconnect(old, 'test')
        await held.wait()
        self.assertFalse(session.is_ready)
        await controls.set_pause('wakeWord', True)
        release.set()
        await until(lambda: session.is_ready and session.binding is not old and not controls.pause_view.pending)
        masks = [(c['manual'], c['wakeWord']) for c in sockets[-1].commands if c['type'] == p.CommandType.SUPPRESSION]
        self.assertEqual(masks, [(False, False), (False, True)])
        self.assertTrue(controls.pause_view.confirmed_wake_word)

    async def test_run_restart_pause_reset_and_persisted_base_has_trigger(self):
        _, _, controls, _, _, _ = await self.start()
        await controls.set_pause('manual', True); await controls.set_pause('wakeWord', True)
        fresh, _, fresh_controls, _, _, _ = await self.start()
        self.assertFalse(fresh_controls.pause_view.desired_manual)
        self.assertEqual(fresh._desired_suppression, (False, False))
        # Process identity is established once at import; a real restart test
        # additionally runs an independent interpreter in the server checkpoint.
        self.assertTrue(p.is_canonical_uuid(fresh.client_run_id))
        with self.assertRaises(ValueError):
            SessionConfig(manual_trigger_enabled=False, wake_word_trigger_enabled=False).validate()

    async def test_closing_input_finish_cancel_no_change_and_refresh_blocked(self):
        session, mirror, controls, sockets, _, _ = await self.start()
        data = snapshot(version=2, active=A, phase='closing_input').to_mapping()
        data['sessionId'] = session.binding.session_id
        session.dispatch(p.parse_snapshot(data), session.binding)
        socket = sockets[-1]
        async def reply(command): socket.reply(command, 'no_change', version=2, revision=0, phase='closing_input')
        socket.on_send = reply
        for action in ('finish', 'cancel'):
            result = await controls.control(action)
            self.assertEqual(result.ack.result, p.AckResult.NO_CHANGE)
            self.assertEqual(result.command.payload['activationId'], A)
            self.assertEqual(mirror.mirror.view.input.phase, p.InputPhase.CLOSING_INPUT)
        count = len(socket.commands)
        self.assertIsNone(await controls.control('refresh'))
        self.assertEqual(len(socket.commands), count)


class Migration(unittest.TestCase):
    def test_defaults_alias_and_explicit_bindings_preserved(self):
        cfg = ControlConfig()
        self.assertEqual((cfg.primary_action, cfg.secondary_action, cfg.secondary_key, cfg.wake_pause_key), ('refresh', 'finish', '', ''))
        for field, action in (('finish_key', 'finish'), ('cancel_key', 'cancel')):
            legacy = HotkeyConfig(key='<ctrl>+<shift>+F7', overlay_toggle_key='Alt+F8', **{field: 'Ctrl+F10'})
            result = migrate_hotkeys(legacy)
            self.assertEqual(result.primary_key, 'Ctrl+Shift+F7')
            self.assertEqual(result.secondary_key, 'Ctrl+F10')
            self.assertEqual(result.secondary_action, action)
            self.assertEqual(result.reinsert_last_key, legacy.reinsert_last_key)
            self.assertEqual(result.overlay_toggle_key, legacy.overlay_toggle_key)

    def test_conflict_does_not_mutate_or_delete_profile(self):
        legacy = HotkeyConfig(finish_key='Ctrl+F7', cancel_key='Ctrl+F8')
        before = deepcopy(legacy)
        with self.assertRaises(ControlMigrationConflict) as found: migrate_hotkeys(legacy)
        self.assertIs(found.exception.legacy, legacy)
        self.assertEqual(legacy, before)

    def test_normalization_and_collisions_rejected_before_registration(self):
        self.assertEqual(ControlConfig(primary_key=' shift + control + space ').primary_key, 'Ctrl+Shift+Space')
        for kwargs in (dict(primary_key='Ctrl+é'), dict(primary_key='Ctrl+²'), dict(primary_key='Ctrl+F25'),
                       dict(primary_action='extend'), dict(primary_key='Ctrl+F9', wake_pause_key='<ctrl>+f9'),
                       dict(primary_key='Ctrl+F9', reinsert_last_key='Ctrl+F9'), dict(enabled=1)):
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError): ControlConfig(**kwargs)


class NativeRegistration(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app = QApplication.instance() or QApplication([])

    def start(self, config=None):
        class Backend:
            def __init__(self): self.keys = {}; self.fail_key = None; self.fail_restore = False
            def register(self, hwnd, ident, mods, key):
                if key == self.fail_key or self.fail_restore and key == 0x20:
                    raise OSError(1409, 'synthetic occupied key')
                if (mods, key) in self.keys.values(): raise OSError(1409, 'duplicate')
                self.keys[ident] = (mods, key)
            def unregister(self, hwnd, ident): self.keys.pop(ident, None)
        backend, calls = Backend(), []
        manager = V2HotkeyManager(config or ControlConfig(secondary_key='Ctrl+F8', wake_pause_key='Ctrl+F9'),
                                 on_control=calls.append, on_reinsert_last=lambda: calls.append('reinsert'),
                                 on_overlay_toggle=lambda: calls.append('overlay'), backend=backend, application=self.app)
        self.addCleanup(manager.unregister)
        self.assertTrue(manager.register())
        return manager, backend, calls

    def test_controls_registered_without_manual_source_and_wake_slot_only_pause(self):
        manager, backend, calls = self.start()
        for slot in ControlSlot:
            ident = manager.role_ids[slot]
            self.assertTrue(backend.keys[ident][0] & MOD_NOREPEAT)
            self.assertTrue(manager.dispatch_hotkey_id(ident))
        self.assertEqual(calls, list(ControlSlot))
        self.assertFalse(manager.dispatch_hotkey_id(123))

    def test_partial_failure_restores_old_and_apply_rebind_invalidates_old_ids(self):
        manager, backend, calls = self.start()
        old = manager.role_ids; registrations = dict(backend.keys)
        backend.fail_key = 0x79  # F10, failure after the new primary registers
        replacement = replace(manager.config, primary_key='Ctrl+F11', secondary_key='Ctrl+F10')
        self.assertFalse(manager.apply(replacement))
        self.assertEqual(backend.keys, registrations)
        self.assertEqual(manager.role_ids, old)
        self.assertIsNone(manager.rollback_failure)
        self.assertTrue(manager.dispatch_hotkey_id(old['primary']))
        backend.fail_key = None
        self.assertTrue(manager.apply(replacement))
        self.assertFalse(manager.dispatch_hotkey_id(old['primary']))
        self.assertTrue(manager.dispatch_hotkey_id(manager.role_ids['primary']))
        self.assertEqual(calls, [ControlSlot.PRIMARY, ControlSlot.PRIMARY])

    def test_wrong_physical_lparam_rejected_and_utilities_separate(self):
        manager, backend, calls = self.start()
        ident = manager.role_ids['primary']; mods, key = backend.keys[ident]
        self.assertFalse(manager.dispatch_hotkey_id(ident, ((key + 1) << 16) | (mods & ~MOD_NOREPEAT)))
        self.assertTrue(manager.dispatch_hotkey_id(ident, (key << 16) | (mods & ~MOD_NOREPEAT)))
        manager.dispatch_hotkey_id(manager.role_ids['reinsert_last'])
        self.assertEqual(calls, [ControlSlot.PRIMARY, 'reinsert'])

    def test_rollback_failure_exposed_and_no_partial_dispatch(self):
        manager, backend, _ = self.start()
        backend.fail_key, backend.fail_restore = 0x79, True
        self.assertFalse(manager.apply(replace(manager.config, primary_key='Ctrl+F11', secondary_key='Ctrl+F10')))
        self.assertIsNotNone(manager.rollback_failure)
        self.assertFalse(backend.keys)
        self.assertFalse(manager.dispatch_hotkey_id(manager.role_ids['primary']))

    def test_disabled_and_empty_profiles_no_native_bindings(self):
        manager, backend, _ = self.start(ControlConfig(enabled=False))
        self.assertFalse(backend.keys)
        self.assertTrue(manager.apply(ControlConfig(primary_key='', reinsert_last_key='')))
        self.assertFalse(backend.keys)
