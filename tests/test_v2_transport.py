"""Receive-ordered fake socket, lost acks, generation races and bounded waits."""

import asyncio
from copy import deepcopy
import json
import unittest
from unittest.mock import patch

from websockets.exceptions import ConnectionClosedError, InvalidHandshake, InvalidStatus, InvalidURI
from websockets.frames import Close
from websockets.datastructures import Headers
from websockets.http11 import Response

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.command_tracker import (
    AckAdvice, CommandCapacity, CommandTimeout, CommandTracker, TransportLost,
)
from voice_stt_client.core.v2_transport import (
    CLIENT_RUN_ID, DEFAULT_V2_URL, V2STTSession, V2TransportConfig, V2TransportState,
)
from tests.test_v2_protocol import FIXTURES, IDS, ack, event


async def until(condition):
    async def poll():
        while not condition():
            await asyncio.sleep(0)
    await asyncio.wait_for(poll(), 2)


def close_error(code):
    return ConnectionClosedError(Close(code, "synthetic"), Close(code, "synthetic"), True)


class FakeWebSocket:
    """No V1 handshake shortcut. Admission and replies traverse real decoder."""

    def __init__(self, *, session_id=None, admission=True):
        self.inbox = asyncio.Queue()
        self.sent = []
        self.closed = False
        self.on_send = None
        self.admission = admission
        self.session_id = session_id or IDS["sessionId"]

    def push(self, message):
        self.inbox.put_nowait(json.dumps(message) if isinstance(message, dict) else message)

    async def send(self, wire):
        if self.closed:
            raise close_error(1006)
        self.sent.append(wire)
        if isinstance(wire, str):
            message = json.loads(wire)
            if message["type"] == "hello" and self.admission:
                hello = deepcopy(FIXTURES["helloAccepted"])
                hello["sessionId"] = hello["snapshot"]["sessionId"] = hello["logAccess"]["sessionId"] = self.session_id
                hello["snapshot"]["trigger"]["suppressed"] = {"manual": True, "wakeWord": True}
                hello["snapshot"]["stateVersion"] = 0
                self.push(hello)
            elif self.on_send:
                await self.on_send(message)
            elif message["type"] != "hello":
                self.reply(message)

    def reply(self, command, result="applied", *, version=0, revision=3, phase="idle"):
        reply = ack(result, phase)
        reply.update(sessionId=self.session_id, commandId=command["commandId"],
                     stateVersion=version, settingsRevision=revision)
        self.push(reply)

    async def recv(self):
        value = await self.inbox.get()
        if isinstance(value, BaseException):
            raise value
        return value

    async def close(self):
        if not self.closed:
            self.closed = True
            self.inbox.put_nowait(close_error(1000))

    @property
    def commands(self):
        return [json.loads(x) for x in self.sent if isinstance(x, str) and json.loads(x)["type"] != "hello"]


async def no_settings(session, binding):
    """Named test boundary; real settings/audio services arrive in AP040/070."""


class Transport(unittest.IsolatedAsyncioTestCase):
    async def start(self, socket=None, *, bootstrap=no_settings, **config):
        socket = socket or FakeWebSocket()
        calls = []
        async def connect(url, **kwargs):
            calls.append((url, kwargs))
            return socket
        session = V2STTSession(V2TransportConfig(**config), bootstrap=bootstrap, connector=connect,
                               jitter=lambda a, b: 1)
        task = asyncio.create_task(session.run())
        self.addAsyncCleanup(session.stop)
        self.addAsyncCleanup(self.finish_task, task)
        await until(lambda: session.is_ready or task.done() or session.status.state in (
            V2TransportState.BLOCKED, V2TransportState.BACKOFF))
        return session, socket, task, calls

    async def finish_task(self, task):
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)

    async def test_hello_first_bootstrap_gate_and_callback_order(self):
        socket = FakeWebSocket()
        release = asyncio.Event()
        seen = []
        async def bootstrap(session, binding):
            self.assertFalse(await session.send_audio(b"\0\0", 16000))
            with self.assertRaises(TransportLost):
                await session.request(p.CommandType.ACTIVATION, action="activate", source="manual")
            await release.wait()
            await session.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=False)
        async def connector(*args, **kwargs):
            return socket
        session = V2STTSession(bootstrap=bootstrap, connector=connector)
        session.on_status = lambda status: seen.append(status.state)
        session.on_accepted = lambda binding: seen.append("accepted")
        session.on_completion = lambda completion: seen.append(completion.command.type)
        task = asyncio.create_task(session.run())
        self.addAsyncCleanup(self.finish_task, task)
        self.addAsyncCleanup(session.stop)
        await until(lambda: session.binding is not None)
        self.assertEqual(json.loads(socket.sent[0])["runtimeSuppression"], {"manual": True, "wakeWord": True})
        self.assertEqual(socket.commands, [])
        release.set()
        await until(lambda: session.is_ready)
        self.assertEqual([x["type"] for x in socket.commands], [p.CommandType.AUDIO_AVAILABILITY, p.CommandType.SUPPRESSION])
        self.assertLess(seen.index("accepted"), seen.index(p.CommandType.SUPPRESSION))
        self.assertLess(seen.index(p.CommandType.SUPPRESSION), seen.index(V2TransportState.READY))
        self.assertTrue(await session.send_audio(b"\0\0", 16000))
        self.assertIsInstance(socket.sent[-1], bytes)

    async def test_missing_and_invalid_bootstrap_permanently_block(self):
        async def fails(session, binding):
            raise ValueError("synthetic")
        for bootstrap in (None, fails):
            with self.subTest(bootstrap=bootstrap):
                session, socket, task, _ = await self.start(bootstrap=bootstrap, bootstrap_timeout=.01)
                self.assertEqual(session.status.state, V2TransportState.BLOCKED)
                self.assertFalse(await session.send_audio(b"\0\0", 16000))
                await task
                self.assertEqual(session.pending_count, 0)
                self.assertTrue(socket.closed)

    async def test_all_fifteen_ack_results_complete_once_without_new_commands(self):
        session, socket, _, _ = await self.start()
        for result in p.AckResult:
            async def reply(message):
                socket.reply(message, result)
            socket.on_send = reply
            count = len(socket.sent)
            completion = await session.request(p.CommandType.ACTIVATION, action="activate", source="manual")
            self.assertEqual(completion.ack.result, result)
            self.assertIsInstance(completion.advice, AckAdvice)
            if result in (p.AckResult.STALE_ACTIVATION, p.AckResult.INTERNAL_ERROR):
                self.assertEqual(completion.advice, AckAdvice.SNAPSHOT)
            elif result in (p.AckResult.COMMAND_ID_CONFLICT, p.AckResult.INVALID_PAYLOAD, p.AckResult.STALE_SESSION):
                self.assertEqual(completion.advice, AckAdvice.CLIENT_ERROR)
            elif result == p.AckResult.SETTINGS_REVISION_CONFLICT:
                self.assertEqual(completion.advice, AckAdvice.SETTINGS_CONFLICT)
            elif result == p.AckResult.SETTINGS_REJECTED:
                self.assertEqual(completion.advice, AckAdvice.SETTINGS_ERRORS)
            elif result in (p.AckResult.APPLIED, p.AckResult.NO_CHANGE):
                self.assertEqual(completion.advice, AckAdvice.COMPLETE)
            self.assertEqual(completion.ack.accepted, result in (p.AckResult.APPLIED, p.AckResult.NO_CHANGE))
            self.assertEqual(len(socket.sent), count + 1)
            self.assertEqual(session.pending_count, 0)

    async def test_event_before_old_ack_and_duplicate_ack_do_not_project(self):
        session, socket, _, _ = await self.start()
        delivered = []
        session.on_message = lambda binding, message: delivered.append(message)
        completed = []
        session.on_completion = completed.append
        async def reply(command):
            data = event("activation.phase_changed")
            data.update(stateVersion=10)
            socket.push(data)
            socket.reply(command, version=3, phase="closing_input")
            socket.reply(command, version=3, phase="closing_input")
        socket.on_send = reply
        completion = await session.request(p.CommandType.ACTIVATION, action="finish", activationId=IDS["activationId"])
        await until(lambda: socket.inbox.empty())
        self.assertFalse(completion.projectable)
        self.assertEqual(len(completed), 1)
        self.assertEqual(delivered[0].stateVersion, 10)
        self.assertEqual(session._tracker.state_version, 10)

    async def test_eventless_payload_completion_and_snapshot_replay(self):
        session, socket, _, _ = await self.start()
        for kind, fields in ((p.CommandType.SUPPRESSION, dict(manual=True, wakeWord=False)),
                             (p.CommandType.AUDIO_AVAILABILITY, dict(audioAvailable=False)),
                             (p.CommandType.ACTIVATION, dict(action="refresh", activationId=IDS["activationId"]))):
            completion = await session.request(kind, **fields)
            self.assertTrue(completion.projectable)
            self.assertEqual({k: completion.command.payload[k] for k in fields}, fields)
        delivered = []
        session.on_message = lambda binding, message: delivered.append(message)
        sends = 0
        async def reply(command):
            nonlocal sends
            sends += 1
            snapshot = deepcopy(FIXTURES["snapshot"])
            snapshot["stateVersion"] = sends
            if sends == 2:
                socket.reply(command, version=0)
            socket.push(snapshot)
        socket.on_send = reply
        session._tracker.ack_timeout = .1
        completion = await session.request(p.CommandType.SNAPSHOT_REQUEST)
        await until(lambda: len(delivered) == 2)
        self.assertEqual(socket.sent[-1], socket.sent[-2])
        self.assertFalse(completion.projectable)
        self.assertEqual([x.stateVersion for x in delivered], [1, 2])

    async def test_retry_exact_bytes_once_and_timeout_no_new_id(self):
        session, socket, _, _ = await self.start(ack_timeout=.01)
        async def drops(message):
            pass
        socket.on_send = drops
        count = len(socket.sent)
        with self.assertRaises(CommandTimeout):
            await session.request(p.CommandType.ACTIVATION, action="activate", source="manual")
        self.assertEqual(len(socket.sent), count + 2)
        self.assertEqual(socket.sent[-1], socket.sent[-2])
        self.assertFalse(session.is_ready)
        self.assertEqual(session.pending_count, 0)
        self.assertTrue(socket.closed)

    async def test_same_domain_serialized_other_domain_independent(self):
        session, socket, _, _ = await self.start()
        async def drops(message):
            pass
        socket.on_send = drops
        first = asyncio.create_task(session.request(p.CommandType.SUPPRESSION, manual=True, wakeWord=False))
        await until(lambda: session.pending_count == 1)
        second = asyncio.create_task(session.request(p.CommandType.SUPPRESSION, manual=False, wakeWord=True))
        other = asyncio.create_task(session.request(p.CommandType.SNAPSHOT_REQUEST))
        await until(lambda: session.pending_count == 2)
        self.assertEqual(len([x for x in socket.commands if x["type"] == p.CommandType.SUPPRESSION]), 2)  # bootstrap + first
        for command in socket.commands[-2:]:
            socket.reply(command)
        await first
        await other
        await until(lambda: len(socket.commands) == 4)
        socket.reply(socket.commands[-1])
        await second

    async def test_disconnect_finishes_pending_and_domain_waiters(self):
        session, socket, _, _ = await self.start()
        socket.on_send = lambda message: asyncio.sleep(0)
        first = asyncio.create_task(session.request(p.CommandType.SUPPRESSION, manual=True, wakeWord=False))
        second = asyncio.create_task(session.request(p.CommandType.SUPPRESSION, manual=False, wakeWord=True))
        await until(lambda: session.pending_count == 1)
        socket.inbox.put_nowait(close_error(1011))
        results = await asyncio.wait_for(asyncio.gather(first, second, return_exceptions=True), 1)
        self.assertTrue(all(isinstance(x, TransportLost) for x in results))
        self.assertEqual(session.pending_count, 0)

    async def test_foreign_session_and_generation_never_confirm_or_publish(self):
        session, socket, _, _ = await self.start()
        binding = session.binding
        socket.on_send = lambda message: asyncio.sleep(0)
        request = asyncio.create_task(session.request(p.CommandType.SNAPSHOT_REQUEST))
        await until(lambda: session.pending_count == 1)
        reply = ack()
        reply["commandId"] = socket.commands[-1]["commandId"]
        reply["sessionId"] = p.new_id()
        self.assertFalse(session.dispatch(p.decode_server_message(reply), binding))
        reply["sessionId"] = binding.session_id
        from voice_stt_client.core.v2_transport import SessionBinding
        old = SessionBinding(binding.generation - 1, binding.accepted)
        self.assertFalse(session.dispatch(p.decode_server_message(reply), old))
        self.assertFalse(request.done())
        self.assertTrue(session.dispatch(p.decode_server_message(reply), binding))
        await request
        delivered = []
        session.on_message = lambda *args: delivered.append(args)
        data = event("transcription.completed")
        data["sessionId"] = p.new_id()
        self.assertFalse(session.dispatch(p.decode_server_message(data), binding))
        self.assertEqual(delivered, [])
        await session.stop()
        self.assertFalse(session.dispatch(p.decode_server_message(reply), binding))
        with self.assertRaises(TransportLost):
            await session.request(p.CommandType.SNAPSHOT_REQUEST, binding=binding)

    async def test_stop_cancel_double_close_and_backoff_are_bounded(self):
        session, socket, task, _ = await self.start()
        socket.on_send = lambda message: asyncio.sleep(0)
        request = asyncio.create_task(session.request(p.CommandType.SNAPSHOT_REQUEST))
        await until(lambda: session.pending_count == 1)
        await asyncio.wait_for(asyncio.gather(session.stop(), session.stop()), 1)
        with self.assertRaises(TransportLost):
            await request
        self.assertTrue(task.done())
        self.assertIsNone(session.binding)
        self.assertIsNone(session._receiver)
        self.assertEqual(session.status.state, V2TransportState.CLOSED)
        self.assertTrue(socket.closed)

    async def test_close_codes_block_or_reconnect_with_capacity_floor(self):
        for code in (4400, 4406, 4409, 1011, 1013, 1006):
            with self.subTest(code=code):
                socket = FakeWebSocket(admission=False)
                socket.inbox.put_nowait(close_error(code))
                session, socket, task, _ = await self.start(socket)
                if code in (4400, 4406, 4409):
                    await task
                    self.assertEqual(session.status.state, V2TransportState.BLOCKED)
                    self.assertEqual(session.generation, 1)
                else:
                    await until(lambda: session.status.state == V2TransportState.BACKOFF)
                    delay = session.status.retry_delay
                    self.assertGreaterEqual(delay, 10 if code == 1013 else .5)
                await session.stop()

    async def test_4408_only_one_retry_with_stable_process_run_id(self):
        sockets = [FakeWebSocket(admission=False), FakeWebSocket(admission=False)]
        for socket in sockets:
            socket.inbox.put_nowait(close_error(4408))
        calls = 0
        async def connector(*args, **kwargs):
            nonlocal calls
            socket = sockets[calls]
            calls += 1
            return socket
        session = V2STTSession(V2TransportConfig(backoff_initial=.01), bootstrap=no_settings, connector=connector)
        await asyncio.wait_for(session.run(), 1)
        self.assertEqual(calls, 2)
        self.assertEqual(session.status.reason, "repeated_hello_timeout")
        self.assertEqual({json.loads(s.sent[0])["clientRunId"] for s in sockets}, {CLIENT_RUN_ID})

    async def test_http_upgrade_transient_errors_backoff_then_ready(self):
        for code in (408, 500, 502, 503, 504):
            with self.subTest(code=code):
                calls, statuses = [], []
                socket = FakeWebSocket()
                async def connector(*args, **kwargs):
                    calls.append(1)
                    if len(calls) == 1:
                        raise InvalidStatus(Response(code, "synthetic", Headers()))
                    return socket
                session = V2STTSession(V2TransportConfig(backoff_initial=.02),
                                       bootstrap=no_settings, connector=connector, jitter=lambda a, b: 1)
                session.on_status = statuses.append
                runner = asyncio.create_task(session.run())
                self.addAsyncCleanup(self.finish_task, runner)
                self.addAsyncCleanup(session.stop)
                await until(lambda: session.status.state == V2TransportState.BACKOFF or runner.done())
                self.assertEqual(session.status.state, V2TransportState.BACKOFF)
                self.assertEqual(len(calls), 1)
                self.assertEqual(session.status.retry_delay, .02)
                await until(lambda: session.is_ready or runner.done())
                self.assertTrue(session.is_ready)
                self.assertEqual(len(calls), 2)
                self.assertTrue(any(s.reason == f"http_upgrade_{code}" for s in statuses))
                await session.request(p.CommandType.SNAPSHOT_REQUEST)
                await session.stop()
                self.assertTrue(runner.done())
                self.assertTrue(socket.closed)
                self.assertEqual(session.pending_count, 0)
                self.assertIsNone(session._receiver)

    async def test_http_upgrade_rate_limit_has_capacity_backoff_and_bounded_stop(self):
        calls = []
        async def connector(*args, **kwargs):
            calls.append(1)
            raise InvalidStatus(Response(429, "synthetic", Headers()))
        session = V2STTSession(bootstrap=no_settings, connector=connector, jitter=lambda a, b: 1)
        runner = asyncio.create_task(session.run())
        self.addAsyncCleanup(self.finish_task, runner)
        self.addAsyncCleanup(session.stop)
        await until(lambda: session.status.state == V2TransportState.BACKOFF or runner.done())
        self.assertEqual(session.status.state, V2TransportState.BACKOFF)
        self.assertGreaterEqual(session.status.retry_delay, 10)
        self.assertEqual(calls, [1])
        await asyncio.wait_for(session.stop(), 1)
        self.assertTrue(runner.done())
        self.assertIsNone(session.binding)
        self.assertIsNone(session._ws)
        self.assertEqual(session.pending_count, 0)

    async def test_http_upgrade_auth_configuration_and_invalid_handshake_block_once(self):
        failures = [(InvalidStatus(Response(code, "synthetic", Headers())), f"http_upgrade_{code}")
                    for code in (301, 400, 401, 403, 404, 405, 426)]
        failures += [(InvalidHandshake("synthetic credential must not leak"), "invalid_websocket_handshake"),
                     (InvalidURI("wss://example.test:bad/ws/v2", "synthetic"), "invalid_endpoint")]
        for failure, reason in failures:
            with self.subTest(reason=reason):
                calls, statuses = [], []
                async def connector(*args, **kwargs):
                    calls.append(1)
                    raise failure
                session = V2STTSession(bootstrap=no_settings, connector=connector)
                session.on_status = statuses.append
                await asyncio.wait_for(session.run(), 1)
                self.assertEqual(calls, [1])
                self.assertEqual(session.status.state, V2TransportState.BLOCKED)
                self.assertEqual(session.status.reason, reason)
                self.assertNotIn(V2TransportState.BACKOFF, [s.state for s in statuses])
                self.assertNotIn("credential", repr(statuses))
                self.assertEqual(session.pending_count, 0)
                self.assertIsNone(session._runner)
                self.assertIsNone(session._receiver)
                self.assertIsNone(session.binding)

    async def test_4408_retry_budget_resets_only_after_ready_between_episodes(self):
        sockets = [FakeWebSocket(admission=False), FakeWebSocket(),
                   FakeWebSocket(admission=False), FakeWebSocket(session_id=p.new_id())]
        sockets[0].inbox.put_nowait(close_error(4408))
        sockets[2].inbox.put_nowait(close_error(4408))
        calls, bindings, lost = [], [], []
        release = asyncio.Event()
        async def bootstrap(session, binding):
            if len(calls) == 2:
                await release.wait()
        async def connector(*args, **kwargs):
            socket = sockets[len(calls)]
            calls.append(1)
            return socket
        session = V2STTSession(V2TransportConfig(backoff_initial=.01), bootstrap=bootstrap,
                               connector=connector, jitter=lambda a, b: 1)
        session.on_accepted = bindings.append
        session.on_lost = lost.append
        runner = asyncio.create_task(session.run())
        self.addAsyncCleanup(self.finish_task, runner)
        self.addAsyncCleanup(session.stop)
        await until(lambda: session.status.state == V2TransportState.CONFIGURING or runner.done())
        self.assertEqual(session._silent_failures, 1)  # admission alone isn't success
        release.set()
        await until(lambda: session.is_ready or runner.done())
        self.assertTrue(session.is_ready)
        old = session.binding
        sockets[1].on_send = lambda message: asyncio.sleep(0)
        pending = asyncio.create_task(session.request(p.CommandType.SNAPSHOT_REQUEST))
        await until(lambda: session.pending_count == 1)
        sockets[1].inbox.put_nowait(close_error(1011))
        with self.assertRaises(TransportLost):
            await asyncio.wait_for(pending, 1)
        await until(lambda: (session.is_ready and session.generation == 4) or runner.done())
        self.assertTrue(session.is_ready)
        self.assertEqual(len(calls), 4)
        self.assertEqual(session._silent_failures, 0)
        self.assertNotEqual(old.session_id, session.binding.session_id)
        self.assertEqual(lost, [old])
        self.assertFalse(session.dispatch(p.decode_server_message(event("transcription.completed")), old))
        self.assertEqual({json.loads(s.sent[0])["clientRunId"] for s in sockets}, {CLIENT_RUN_ID})
        self.assertEqual(session.pending_count, 0)
        await session.request(p.CommandType.SNAPSHOT_REQUEST)
        await session.stop()
        self.assertEqual(lost, bindings)
        self.assertTrue(all(s.closed for s in sockets))

    async def test_handshake_refusal_config_capacity_and_incompatible(self):
        for kind, reason in (("protocol.incompatible", "unsupported"), ("session.rejected", "bad_config"),
                             ("session.rejected", "session_limit_reached")):
            socket = FakeWebSocket(admission=False)
            socket.push(dict(type=kind, reason=reason, serverVersion="test", serverCommit="unknown",
                             supportedProtocolVersions=[2], errors=[]))
            session, _, task, _ = await self.start(socket)
            if reason == "session_limit_reached":
                await until(lambda: session.status.state == V2TransportState.BACKOFF)
                self.assertGreaterEqual(session.status.retry_delay, 10)
            else:
                await task
                self.assertEqual(session.status.state, V2TransportState.BLOCKED)
            self.assertEqual(session.pending_count, 0)
            self.assertEqual(socket.commands, [])
            await session.stop()

    async def test_endpoint_default_legacy_profile_blocks_without_rewrite(self):
        self.assertEqual(DEFAULT_V2_URL, "wss://stt.voice.marcosudau.com/ws/v2")
        for url in ("wss://custom.example/ws/transcribe", "wss://voice.marcosudau.com/ws/transcribe"):
            session, _, task, calls = await self.start(url=url)
            await task
            self.assertEqual(session.status.reason, "legacy_endpoint_requires_migration")
            self.assertEqual(session.config.url, url)
            self.assertEqual(calls, [])
        config = V2TransportConfig(url="wss://custom.example/ws/v2?clientId=desktop")
        self.assertIsNone(config.endpoint_issue)

    async def test_transport_ping_only_and_no_final_inference_timer(self):
        session, socket, _, calls = await self.start()
        kwargs = calls[0][1]
        self.assertEqual(kwargs["ping_interval"], 20)
        self.assertEqual(kwargs["ping_timeout"], 20)
        socket.push(event("transcription.accepted"))
        await until(lambda: socket.inbox.empty())
        for _ in range(50):
            await asyncio.sleep(0)
        self.assertTrue(session.is_ready)
        self.assertEqual([x["type"] for x in socket.commands], [p.CommandType.SUPPRESSION])

    async def test_admission_and_connect_timeout_no_hanging_run(self):
        socket = FakeWebSocket(admission=False)
        async def connector(*args, **kwargs):
            return socket
        session = V2STTSession(V2TransportConfig(admission_timeout=.01), connector=connector)
        task = asyncio.create_task(session.run())
        await until(lambda: session.status.state == V2TransportState.BACKOFF)
        await session.stop()
        self.assertTrue(task.done())
        self.assertTrue(socket.closed)
        async def hanging_connect(*args, **kwargs):
            await asyncio.Event().wait()
        session = V2STTSession(V2TransportConfig(connect_timeout=.01), connector=hanging_connect)
        task = asyncio.create_task(session.run())
        await until(lambda: session.status.state == V2TransportState.BACKOFF)
        await session.stop()
        self.assertTrue(task.done())

    async def test_reconnect_new_binding_ids_empty_queue_and_suppression_retained(self):
        sockets = [FakeWebSocket(), FakeWebSocket(session_id=p.new_id())]
        calls = 0
        async def connector(*args, **kwargs):
            nonlocal calls
            socket = sockets[calls]
            calls += 1
            return socket
        session = V2STTSession(V2TransportConfig(backoff_initial=.01), bootstrap=no_settings, connector=connector)
        task = asyncio.create_task(session.run())
        self.addAsyncCleanup(self.finish_task, task)
        self.addAsyncCleanup(session.stop)
        await until(lambda: session.is_ready)
        old = session.binding
        await session.request(p.CommandType.SUPPRESSION, manual=True, wakeWord=False)
        sockets[0].inbox.put_nowait(close_error(1011))
        await until(lambda: session.is_ready and session.generation == 2)
        self.assertNotEqual(old.session_id, session.binding.session_id)
        self.assertEqual(session.pending_count, 0)
        self.assertEqual(sockets[1].commands[0]["manual"], True)
        self.assertEqual({json.loads(s.sent[0])["clientRunId"] for s in sockets}, {CLIENT_RUN_ID})
        self.assertNotEqual(sockets[0].commands[0]["commandId"], sockets[1].commands[0]["commandId"])

    async def test_closing_input_ack_blocks_more_refresh_for_same_activation(self):
        session, socket, _, _ = await self.start()
        async def reply(command):
            socket.reply(command, "closing_input", phase="closing_input")
        socket.on_send = reply
        completion = await session.request(p.CommandType.ACTIVATION, action="refresh", activationId=IDS["activationId"])
        self.assertEqual(completion.advice, AckAdvice.CLOSING)
        count = len(socket.sent)
        with self.assertRaises(TransportLost):
            await session.request(p.CommandType.ACTIVATION, action="refresh", activationId=IDS["activationId"])
        self.assertEqual(len(socket.sent), count)

    async def test_bootstrap_rejected_ack_and_envelope_override_block(self):
        socket = FakeWebSocket()
        async def reply(command):
            socket.reply(command, "settings_rejected")
        socket.on_send = reply
        async def bootstrap(session, binding):
            await session.bootstrap_command(binding, p.CommandType.SETTINGS_PATCH,
                                            baseSettingsRevision=0, changes={"activation.followupTimeoutMs": 3000})
        session, _, task, _ = await self.start(socket, bootstrap=bootstrap)
        await task
        self.assertEqual(session.status.reason, "configuration_command_rejected")
        self.assertFalse(session.is_ready)
        self.assertEqual(len(socket.commands), 1)
        session, socket, _, _ = await self.start()
        count = len(socket.sent)
        with self.assertRaises(p.ProtocolError):
            await session.request(p.CommandType.SNAPSHOT_REQUEST, commandId=p.new_id())
        self.assertEqual(len(socket.sent), count)

    async def test_malformed_admission_second_hello_and_binary_server_block(self):
        for frame in (b"\0", "[]", '{"type":"hello.accepted"}'):
            socket = FakeWebSocket(admission=False)
            socket.push(frame)
            session, socket, task, _ = await self.start(socket)
            await task
            self.assertEqual(session.status.state, V2TransportState.BLOCKED)
            self.assertTrue(socket.closed)
        for frame in (b"\0", FIXTURES["helloAccepted"]):
            session, socket, task, _ = await self.start()
            socket.push(frame)
            await until(lambda: task.done())
            self.assertEqual(session.status.reason, "invalid_server_protocol")
            self.assertEqual(session.pending_count, 0)

    async def test_cancel_request_stalled_send_and_audio_loss_invalidate(self):
        session, socket, _, _ = await self.start()
        socket.on_send = lambda message: asyncio.Event().wait()
        request = asyncio.create_task(session.request(p.CommandType.SNAPSHOT_REQUEST))
        await until(lambda: session.pending_count == 1)
        request.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await request
        self.assertFalse(session.is_ready)
        self.assertEqual(session.pending_count, 0)
        self.assertTrue(socket.closed)
        session, socket, _, _ = await self.start(ack_timeout=.01)
        socket.on_send = lambda message: asyncio.Event().wait()
        with self.assertRaises(TimeoutError):
            await session.request(p.CommandType.SNAPSHOT_REQUEST)
        self.assertFalse(session.is_ready)
        self.assertEqual(session.pending_count, 0)
        session, socket, _, _ = await self.start()
        async def broken_send(wire):
            raise OSError("synthetic socket loss")
        socket.send = broken_send
        with self.assertRaises(OSError):
            await session.send_audio(b"\0\0", 16000)
        self.assertFalse(session.is_ready)
        self.assertTrue(socket.closed)

    async def test_cancel_connect_bootstrap_and_stop_caller_leave_no_tasks(self):
        entered = asyncio.Event()
        async def hanging_connect(*args, **kwargs):
            entered.set()
            await asyncio.Event().wait()
        session = V2STTSession(connector=hanging_connect)
        runner = asyncio.create_task(session.run())
        await entered.wait()
        await asyncio.wait_for(session.stop(), 1)
        self.assertTrue(runner.done())
        async def hanging_bootstrap(session, binding):
            entered.set()
            await asyncio.Event().wait()
        entered.clear()
        socket = FakeWebSocket()
        async def connector(*args, **kwargs):
            return socket
        session = V2STTSession(bootstrap=hanging_bootstrap, connector=connector)
        runner = asyncio.create_task(session.run())
        await entered.wait()
        stopper = asyncio.create_task(session.stop())
        await asyncio.sleep(0)
        stopper.cancel()
        await asyncio.gather(stopper, return_exceptions=True)
        await until(lambda: runner.done())
        self.assertTrue(socket.closed)
        self.assertIsNone(session.binding)
        self.assertFalse(any(t.get_name() in ("v2-receive", "v2-bootstrap") for t in asyncio.all_tasks()))

    async def test_close_timeout_aborts_underlying_transport(self):
        session, socket, _, _ = await self.start(close_timeout=.01)
        from types import SimpleNamespace
        aborted = []
        socket.transport = SimpleNamespace(abort=lambda: aborted.append(True))
        async def stalled_close():
            await asyncio.Event().wait()
        socket.close = stalled_close
        await asyncio.wait_for(session.stop(), 1)
        self.assertEqual(aborted, [True])
        self.assertIsNone(session._ws)

    async def test_diagnostic_failure_isolated_and_no_token_or_text(self):
        from types import SimpleNamespace
        records = []
        def record(kind, **fields):
            records.append((kind, fields))
            raise RuntimeError("broken logger")
        socket = FakeWebSocket()
        async def connector(*args, **kwargs):
            return socket
        session = V2STTSession(bootstrap=no_settings, connector=connector,
                               observability=SimpleNamespace(event=record))
        runner = asyncio.create_task(session.run())
        await until(lambda: session.is_ready)
        await session.request(p.CommandType.SNAPSHOT_REQUEST)
        await session.stop()
        self.assertTrue(runner.done())
        self.assertTrue(records)
        for secret in (FIXTURES["helloAccepted"]["logAccess"]["accessToken"], "synthetic preview"):
            self.assertNotIn(secret, repr(records))

    async def test_invalid_endpoint_and_bounds_do_not_connect(self):
        for url in ("https://example.com/ws/v2", "wss://user:secret@example.com/ws/v2", "wss://example.com/ws/v2#x"):
            session, _, task, calls = await self.start(url=url)
            await task
            self.assertEqual(session.status.reason, "invalid_endpoint")
            self.assertEqual(calls, [])
        for fields in (dict(ack_timeout=0), dict(admission_timeout=float("nan")), dict(close_timeout=True),
                       dict(command_retries=2), dict(capacity_min=1), dict(max_pending=0)):
            with self.assertRaises(ValueError):
                V2TransportConfig(**fields)


class Tracker(unittest.IsolatedAsyncioTestCase):
    async def test_capacity_cancellation_and_close_clear_waiters(self):
        tracker = CommandTracker(IDS["sessionId"], 1, max_pending=2)
        sent = []
        async def send(wire):
            sent.append(wire)
        command = lambda: p.build_command(p.CommandType.SNAPSHOT_REQUEST, IDS["sessionId"])
        first = asyncio.create_task(tracker.request(command(), send))
        second = asyncio.create_task(tracker.request(command(), send))
        await until(lambda: tracker._callers == 2)
        with self.assertRaises(CommandCapacity):
            await tracker.request(command(), send)
        tracker.close()
        results = await asyncio.gather(first, second, return_exceptions=True)
        self.assertTrue(all(isinstance(x, TransportLost) for x in results))
        self.assertEqual(tracker.pending_count, 0)
        self.assertEqual(tracker._callers, 0)

    async def test_fake_ack_wait_retry_identical_and_revision_guard(self):
        tracker = CommandTracker(IDS["sessionId"], 5)
        command = p.build_command(p.CommandType.AUDIO_AVAILABILITY, IDS["sessionId"], audioAvailable=False)
        sent = []
        async def send(wire):
            sent.append(wire)
            if len(sent) == 2:
                reply = ack()
                reply["commandId"] = command.commandId
                tracker.observe(0, 2)
                tracker.resolve(p.decode_server_message(reply), 5)
        real_wait = asyncio.wait_for
        waits = 0
        async def fake_wait(awaitable, timeout):
            nonlocal waits
            if isinstance(awaitable, asyncio.Future):
                waits += 1
                if waits == 1:
                    awaitable.cancel()
                    raise TimeoutError
            return await real_wait(awaitable, timeout)
        with patch("voice_stt_client.core.command_tracker.asyncio.wait_for", fake_wait):
            completed = await tracker.request(command, send)
        self.assertEqual(sent[0], sent[1])
        self.assertFalse(completed.projectable)
        self.assertEqual(waits, 2)


if __name__ == "__main__":
    unittest.main()
