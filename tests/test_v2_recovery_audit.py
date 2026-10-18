"""AP020 reconnect findings: real owners, faulted I/O boundaries, no real-test claims."""
import asyncio
from http.client import IncompleteRead
from io import BytesIO
import json
import ssl
import threading
import time
import unittest
from unittest.mock import patch
from urllib.error import HTTPError, URLError

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.command_tracker import TransportLost
from voice_stt_client.core.config import ServerConfig, EventStreamConfig
from voice_stt_client.core.session_coordinator import DualSessionCoordinator
from voice_stt_client.core.settings_service import SettingsHTTP, SettingsError, SettingsService
from voice_stt_client.core.v2_media import V2MediaConnection
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from tests.test_v2_audio_recovery import Capture
from tests.test_v2_settings_service import FakeHTTP, SettingsSocket, KEY
from tests.test_v2_transport import FakeWebSocket, until, no_settings


class Recovery(unittest.IsolatedAsyncioTestCase):
    async def launch(self, *, sockets=None, bootstrap=None, prepare=None, http=None, media=False, **kwargs):
        sockets = sockets or [FakeWebSocket(), FakeWebSocket(session_id=p.new_id())]
        opened = []
        async def connect(*args, **fields):
            socket = sockets[len(opened)]
            opened.append(socket)
            return socket
        config = dict(backoff_initial=.005, backoff_max=.02, ack_timeout=.2,
                      bootstrap_timeout=.8, command_retries=0)
        config.update(kwargs)
        session = V2STTSession(V2TransportConfig(**config), connector=connect,
                               bootstrap=bootstrap or no_settings, prepare=prepare, jitter=lambda a, b: 1)
        service = port = None
        if http is not None:
            session.bootstrap = None
            mirror = V2MirrorConnection(session)
            service = SettingsService(session, V2Profile(desired_settings={KEY: 4000}), http=http,
                                      snapshot_timeout=.15)
            if media:
                port = V2MediaConnection(session, Capture(), settings_bootstrap=service.bootstrap,
                    logs=DualSessionCoordinator(ServerConfig(), EventStreamConfig(enabled=False)),
                    recovery_interval=.005)
            else:
                session.bootstrap = service.bootstrap
            self.addAsyncCleanup(mirror.close)
            self.addAsyncCleanup(service.close)
        runner = asyncio.create_task(session.run())
        async def cleanup():
            await session.stop()
            if port:
                await port.close()
            await asyncio.gather(runner, return_exceptions=True)
        self.addAsyncCleanup(cleanup)
        return session, runner, opened, service, port

    async def test_temporary_metadata_failures_recover_without_hello_or_audio_early(self):
        for failure in [SettingsError(code) for code in ('http_unavailable', 'http_timeout', 'http_worker_busy')] + [
                SettingsError('http_read_failed', status=code) for code in (408, 429, 500, 502, 503, 504, 599)]:
            with self.subTest(failure=(failure.code, failure.status)):
                http = FakeHTTP()
                attempts = []
                async def fault(method, path):
                    attempts.append(path)
                    if len(attempts) == 1:
                        raise failure
                http.hook = fault
                s, runner, opened, service, media = await self.launch(sockets=[SettingsSocket()], http=http, media=True)
                s.set_desired_suppression(True, True)
                await until(lambda: s.is_ready or runner.done())
                self.assertTrue(s.is_ready)
                self.assertEqual(s.generation, 2)
                self.assertEqual(len(opened), 1)
                self.assertEqual(service.report().effective[KEY], 4000)
                self.assertEqual(opened[0].state['trigger']['suppressed'], dict(manual=True, wakeWord=True))
                self.assertFalse(any(isinstance(w, bytes) for w in opened[0].sent))
                await media.close()

    async def test_prepare_deadline_recycles_without_opening_a_socket(self):
        attempts = []
        async def prepare(session):
            attempts.append(session.generation)
            if len(attempts) == 1:
                await asyncio.Event().wait()
            return session.config
        s, runner, opened, _, _ = await self.launch(prepare=prepare, bootstrap_timeout=.15)
        await until(lambda: s.is_ready or runner.done())
        self.assertTrue(s.is_ready)
        self.assertEqual(attempts, [1, 2])
        self.assertEqual(len(opened), 1)

    async def test_bootstrap_deadline_recycles_and_keeps_pcm_and_triggers_gated(self):
        attempts = []
        async def bootstrap(session, binding):
            attempts.append(binding)
            if len(attempts) == 1:
                self.assertFalse(await session.send_audio(b'\0\0', 16000))
                with self.assertRaises(TransportLost):
                    await session.request(p.CommandType.ACTIVATION, action='activate', source='manual')
                await asyncio.Event().wait()
        s, runner, opened, _, _ = await self.launch(bootstrap=bootstrap, bootstrap_timeout=.15)
        await until(lambda: s.is_ready or runner.done())
        self.assertTrue(s.is_ready)
        self.assertEqual(len(attempts), 2)
        self.assertTrue(opened[0].closed)
        self.assertEqual(opened[0].commands, [])

    async def test_missing_bootstrap_snapshot_or_patch_ack_recycles_new_session_only(self):
        for missing in ('snapshot', 'patch_ack'):
            with self.subTest(missing=missing):
                first, second = SettingsSocket(), SettingsSocket()
                if missing == 'snapshot':
                    first.snapshot_missing = True
                else:
                    async def applied_without_ack(command):
                        if command['type'] == p.CommandType.SETTINGS_PATCH:
                            # The mutation took effect, but its result is unknown to the client.
                            first.state['requestedSettings'].update(command['changes'])
                            first.state['effectiveSettings'].update(command['changes'])
                            first.state['settingsRevision'] += 1
                        else:
                            await SettingsSocket.respond(first, command)
                    first.on_send = applied_without_ack
                s, runner, opened, service, media = await self.launch(
                    sockets=[first, second], http=FakeHTTP(), media=True)
                await until(lambda: s.is_ready or runner.done())
                self.assertTrue(s.is_ready)
                self.assertEqual(s.generation, 2)
                self.assertEqual(service.report().effective[KEY], 4000)
                self.assertTrue(first.closed)
                self.assertFalse(any(c['type'] == p.CommandType.SUPPRESSION for c in first.commands))
                self.assertFalse(any(isinstance(w, bytes) for w in first.sent))
                old_ids = {c['commandId'] for c in first.commands}
                self.assertFalse(old_ids & {c['commandId'] for c in second.commands})
                self.assertLessEqual(sum(c['type'] == p.CommandType.SETTINGS_PATCH for c in first.commands), 1)
                await media.close()

    async def test_late_old_generation_send_failure_cannot_close_recovered_socket(self):
        for audio in (False, True):
            with self.subTest(audio=audio):
                s, runner, opened, _, _ = await self.launch(ack_timeout=1)
                await until(lambda: s.is_ready)
                old = s.binding
                entered, release = asyncio.Event(), asyncio.Event()
                async def stalled(wire):
                    entered.set()
                    await release.wait()
                    raise OSError('old socket failed after replacement')
                opened[0].send = stalled
                operation = asyncio.create_task(s.send_audio(b'\0\0', 16000) if audio else
                    s.request(p.CommandType.SNAPSHOT_REQUEST))
                await entered.wait()
                await s.reconnect(old, 'audit_overlap')
                await until(lambda: (s.is_ready and s.generation == 2) or runner.done())
                self.assertTrue(s.is_ready)
                replacement = s.binding
                release.set()
                with self.assertRaises(OSError):
                    await operation
                self.assertTrue(s.is_ready)
                self.assertIs(s.binding, replacement)
                self.assertFalse(opened[1].closed)
                await s.request(p.CommandType.SNAPSHOT_REQUEST)
                await s.stop()

    async def test_non_json_error_status_is_classified_before_payload_for_get_and_patch(self):
        http = SettingsHTTP('ws://127.0.0.1:18020/ws/v2')
        for method in ('GET', 'PATCH'):
            for status in (401, 403, 408, 429, 500, 502, 503, 504):
                with self.subTest(method=method, status=status):
                    error = HTTPError(http.origin, status, 'unavailable', {}, BytesIO(b'<html>proxy failure</html>'))
                    with patch('voice_stt_client.core.settings_service.build_opener') as opener:
                        opener.return_value.open.side_effect = error
                        response = await http.request(method, '/api/v2/settings/server')
                        self.assertEqual(response.status, status)
                        self.assertEqual(response.body, {})
                        self.assertEqual(opener.return_value.open.call_count, 1)

    async def test_internal_server_error_during_bootstrap_recycles_instead_of_configuration_block(self):
        for kind in (p.CommandType.SETTINGS_PATCH, p.CommandType.SNAPSHOT_REQUEST,
                     p.CommandType.AUDIO_AVAILABILITY, p.CommandType.SUPPRESSION):
            with self.subTest(kind=kind):
                first, second = SettingsSocket(), SettingsSocket()
                async def fail(command):
                    if command['type'] == kind:
                        first.reply(command, 'internal_error', revision=first.state['settingsRevision'])
                    else:
                        await first.respond(command)
                first.on_send = fail
                s, runner, opened, _, media = await self.launch(sockets=[first, second], http=FakeHTTP(), media=True)
                if kind == p.CommandType.AUDIO_AVAILABILITY:
                    media.set_device_available(False)
                await until(lambda: s.is_ready or runner.done())
                self.assertTrue(s.is_ready)
                self.assertEqual(s.generation, 2)
                self.assertTrue(first.closed)
                self.assertFalse(any(isinstance(w, bytes) for w in first.sent))
                await media.close()

    async def test_truncated_success_body_is_transport_loss_not_an_unhandled_worker_failure(self):
        class Truncated(BytesIO):
            code = 200
            def read(self, count):
                raise IncompleteRead(b'{', 10)
        for method, expected in (('GET', 'http_unavailable'), ('PATCH', 'http_outcome_unknown')):
            http = SettingsHTTP('ws://127.0.0.1:18020/ws/v2')
            with self.subTest(method=method), patch('voice_stt_client.core.settings_service.build_opener') as opener:
                opener.return_value.open.return_value = Truncated()
                with self.assertRaisesRegex(SettingsError, expected):
                    await http.request(method, '/api/v2/settings/server')
                self.assertEqual(opener.return_value.open.call_count, 1)

    async def test_certificate_verification_failure_is_permanent_in_http_and_websocket(self):
        http = SettingsHTTP('wss://example.test/ws/v2')
        with self.subTest(boundary='HTTP'), patch('voice_stt_client.core.settings_service.build_opener') as opener:
            opener.return_value.open.side_effect = URLError(ssl.SSLCertVerificationError('untrusted'))
            with self.assertRaisesRegex(SettingsError, 'http_tls_verification_failed'):
                await http.request('GET', '/api/v2/settings/schema')
        attempts = []
        async def connector(*args, **kwargs):
            attempts.append(1)
            raise ssl.SSLCertVerificationError('untrusted')
        s = V2STTSession(V2TransportConfig(backoff_initial=.01), connector=connector)
        runner = asyncio.create_task(s.run())
        self.addAsyncCleanup(s.stop)
        await until(lambda: runner.done() or len(attempts) >= 2)
        self.assertTrue(runner.done())
        self.assertEqual(attempts, [1])
        self.assertEqual(s.status.reason, 'tls_verification_failed')

    async def test_cancelled_native_probe_failure_is_reaped_before_device_recovery(self):
        s = V2STTSession()
        media = V2MediaConnection(s, Capture(), logs=DualSessionCoordinator(
            ServerConfig(), EventStreamConfig(enabled=False)))
        entered, release = threading.Event(), threading.Event()
        def delayed_failure():
            entered.set()
            release.wait(2)
            raise OSError('USB probe failed')
        pending = asyncio.create_task(media._capture_call(delayed_failure))
        try:
            await until(entered.is_set)
            pending.cancel()
            await asyncio.gather(pending, return_exceptions=True)

            release.set()
            await until(media._capture_operation.done)
            with self.assertRaises(OSError):
                await media._capture_call(media.capture.probe)
            # Previous failure is observable once, then a new native call is legal.
            await media._capture_call(media.capture.probe)
            await media.close()
        finally:
            release.set()
            await asyncio.gather(pending, return_exceptions=True)

    async def test_bootstrap_device_and_settings_native_calls_never_overlap(self):
        s = V2STTSession()
        media = V2MediaConnection(s, Capture(), logs=DualSessionCoordinator(
            ServerConfig(), EventStreamConfig(enabled=False)))
        entered, release = threading.Event(), threading.Event()
        lock = threading.Lock()
        active = maximum = 0
        def operation(first=False):
            nonlocal active, maximum
            with lock:
                active += 1
                maximum = max(maximum, active)
            try:
                if first:
                    entered.set()
                    release.wait(2)
                else:
                    time.sleep(.05)
            finally:
                with lock:
                    active -= 1
        first = asyncio.create_task(media._capture_call(lambda: operation(True)))
        await until(entered.is_set)
        waiters = [asyncio.create_task(media._capture_call(operation)) for _ in range(2)]
        await asyncio.sleep(.03)
        release.set()
        await asyncio.gather(first, *waiters)
        await media.close()
        self.assertEqual(maximum, 1)



class RuntimeRecovery(unittest.IsolatedAsyncioTestCase):
    async def test_owned_shutdown_during_preflight_finishes_run_without_cancellation_escape(self):
        from tempfile import TemporaryDirectory
        from tests.test_text_injector import MockInjectionBackend
        from tests.test_v2_runtime_integration import config_in
        from voice_stt_client.core.v2_runtime import V2Runtime
        entered = asyncio.Event()
        http = FakeHTTP()
        async def hold(method, path):
            entered.set()
            await asyncio.Event().wait()
        http.hook = hold
        with TemporaryDirectory() as folder:
            runtime = V2Runtime(config_in(folder), http=http, audio=Capture(), backend=MockInjectionBackend())
            running = asyncio.create_task(runtime.run())
            await entered.wait()
            await runtime.shutdown()
            await asyncio.wait_for(running, 1)
            self.assertFalse(runtime.is_running)
            self.assertFalse(runtime.cleanup_errors)

    async def test_shutdown_rejects_manual_reconnect_without_spawning_a_transport(self):
        from tempfile import TemporaryDirectory
        from tests.test_text_injector import MockInjectionBackend
        from tests.test_v2_runtime_integration import config_in
        from voice_stt_client.core.v2_runtime import V2Runtime
        with TemporaryDirectory() as folder:
            opened = []
            async def connector(*args, **kwargs):
                opened.append(1)
                return SettingsSocket()
            runtime = V2Runtime(config_in(folder), connector=connector, http=FakeHTTP(),
                                audio=Capture(), backend=MockInjectionBackend())
            await runtime.shutdown()
            result = await runtime.reconnect_server()
            spawned = runtime._runner
            try:
                self.assertFalse(result.success)
                self.assertEqual(result.status, 'core_unavailable')
                self.assertIsNone(spawned)
                self.assertEqual(opened, [])
            finally:
                if spawned:
                    spawned.cancel()
                    await asyncio.gather(spawned, return_exceptions=True)


if __name__ == '__main__':
    unittest.main()
