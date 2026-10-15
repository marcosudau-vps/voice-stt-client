"""Real pinned local server + real ReSpeaker recovery; controlled HTTP/ack faults.

All mutations are session scoped. No activation, paste, admin key, LED or V1
profile access. Fault adapter drops one real session PATCH ack; never simulates
its success. A loopback HTTP proxy changes responses, not server product code.
"""
import argparse
import asyncio
from collections import deque
from dataclasses import asdict
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import threading
import time
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.qualify_v2_real import LOCAL, SERVER, identity, save
from scripts.qualify_v2_session import process_memory


async def run(evidence):
    from websockets.asyncio.client import connect
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.audio_capture import AudioCapture
    from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
    from voice_stt_client.core.settings_service import SettingsHTTP
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.v2_runtime import V2Runtime
    from voice_stt_client.core.v2_transport import V2TransportConfig

    container = 'voicestt-qualification-iv2-020'
    label = subprocess.check_output(['docker', 'inspect', container, '--format',
        '{{index .Config.Labels "voice-stt.qualification"}}'], text=True).strip()
    if label != 'AP-IV2-020':
        raise RuntimeError('Refuse to operate another workload')
    with urlopen('http://127.0.0.1:18020/health', timeout=10) as response:
        health = json.load(response)
    with urlopen('http://127.0.0.1:18020/api/v2/settings/schema', timeout=10) as response:
        schema = json.load(response)
    if schema.get('serverCommit') != SERVER or not health.get('ready'):
        raise RuntimeError('Wrong/unready server')

    faults = deque([408, 429, 500, 502, 503, 504, 'timeout'])
    trace, lock = [], threading.Lock()
    def record(kind, **fields):
        with lock:
            trace.append(dict(kind=kind, seconds=round(time.monotonic()-started, 3), **fields))
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass
        def do_GET(self):
            with lock:
                fault = faults.popleft() if faults else None
            if fault is not None:
                record('http_fault', status=fault)
                if fault == 'timeout':
                    time.sleep(1)
                    return
                self.send_response(fault)
                self.end_headers()
                try:
                    self.wfile.write(b'<html>controlled local temporary failure</html>')
                except (BrokenPipeError, ConnectionResetError):
                    pass
                return
            try:
                if self.path not in ('/api/v2/settings/schema', '/api/v2/settings/server', '/api/v2/wake-words'):
                    self.send_error(404)
                    return
                with urlopen('http://127.0.0.1:18020'+self.path, timeout=.5) as response:
                    body = response.read(1024*1024)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(body)
            except (OSError, BrokenPipeError):
                self.close_connection = True
    proxy = ThreadingHTTPServer(('127.0.0.1', 0), Handler)
    worker = threading.Thread(target=proxy.serve_forever, daemon=True)
    started = time.monotonic()
    worker.start()
    dropped, opened = [], []
    class AckFault:
        def __init__(self, ws, fault):
            self.ws, self.fault, self.command_id = ws, fault, None
        async def send(self, wire):
            if self.fault and isinstance(wire, str):
                message = json.loads(wire)
                if message['type'] == p.CommandType.SETTINGS_PATCH:
                    self.command_id = message['commandId']
            await self.ws.send(wire)
        async def recv(self):
            while True:
                wire = await self.ws.recv()
                message = json.loads(wire)
                if self.command_id and message.get('type') == 'command.ack' and message.get('commandId') == self.command_id:
                    dropped.append(self.command_id)
                    record('real_patch_ack_dropped', commandId=self.command_id)
                    continue
                return wire
        async def close(self):
            await self.ws.close()
        @property
        def transport(self):
            return self.ws.transport
    async def connector(*args, **kwargs):
        ws = AckFault(await connect(*args, **kwargs), fault=not opened)
        opened.append(ws)
        return ws
    config = AppConfig._load_single(DEFAULT_CONFIG_PATH)
    config.server.url = 'ws://127.0.0.1:18020/ws/v2'
    config.audio.device = next(d['index'] for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower())
    profile = V2Profile(desired_settings={'activation.followupTimeoutMs': 4000})
    profile.controls['enabled'] = False
    config.v2_profile = asdict(profile)
    config.history.persistent.db_path = str(LOCAL/'recovery-audit/history.sqlite')
    config.event_stream.enabled = False
    config.led.enabled = False
    config.feedback.sounds_enabled = False
    Path(config.history.persistent.db_path).parent.mkdir(parents=True, exist_ok=True)
    http = SettingsHTTP(f'ws://127.0.0.1:{proxy.server_port}/ws/v2', timeout=.35)
    runtime = V2Runtime(config, http=http, connector=connector, transport_config=V2TransportConfig(
        url=config.server.url, backoff_initial=.15, backoff_max=1, ack_timeout=.4,
        bootstrap_timeout=3, command_retries=1))
    await runtime.controls.set_pause('manual', True)
    await runtime.controls.set_pause('wakeWord', True)
    previous = runtime.session.on_status
    def status(value):
        previous(value)
        record('transport', state=str(value.state), reason=value.reason, generation=value.generation)
    runtime.session.on_status = status
    before = identity()
    running = asyncio.create_task(runtime.run())
    metrics, restarts = [], []
    async def wait(predicate, timeout=60):
        async with asyncio.timeout(timeout):
            while not predicate():
                if running.done():
                    await running
                    raise RuntimeError('Runtime stopped')
                if runtime.session.status.state.value == 'blocked':
                    raise RuntimeError('Runtime permanently blocked')
                await asyncio.sleep(.05)
    def sample():
        value = dict(generation=runtime.session.generation, tasks=len(asyncio.all_tasks()),
            pending=runtime.session.pending_count, media=runtime.media.counters(), memory=process_memory())
        metrics.append(value)
        return value
    try:
        await wait(lambda: runtime.is_ready and runtime.media.sent > 25)
        if len(dropped) != 2:  # One command and its byte-identical allowed retry.
            raise RuntimeError('Lost real PATCH ack scenario did not execute')
        if len(set(dropped)) != 1 or len(opened) != 2:
            raise RuntimeError('Uncertain command was not isolated to its original session')
        sample()
        for cycle in range(3):
            old = runtime.session.binding
            sent = runtime.media.sent
            restart_started = time.monotonic()
            record('restart', cycle=cycle+1)
            process = await asyncio.create_subprocess_exec('docker', 'restart', '-t', '2', container,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
            # Overlap an explicit reconnect with server loss; old binding only.
            await asyncio.sleep(.15)
            await asyncio.gather(runtime.reconnect_server(), runtime.reconnect_server())
            output, errors = await asyncio.wait_for(process.communicate(), 30)
            if process.returncode:
                raise RuntimeError('Qualification container restart failed')
            await wait(lambda: runtime.is_ready and runtime.session.binding is not old and runtime.media.sent > sent+25)
            b, view = runtime.session.binding, runtime.mirror.mirror.view
            assert b.accepted.payload['serverCommit'] == SERVER
            assert (view.generation, view.session_id) == (b.generation, b.session_id)
            assert dict(view.trigger['suppressed']) == dict(manual=True, wakeWord=True)
            assert runtime.settings.report().effective['activation.followupTimeoutMs'] == 4000
            assert not view.activations and runtime.queue.queue_size() == 0
            assert runtime.session.pending_count == 0
            restarts.append(dict(cycle=cycle+1, recoverySeconds=round(time.monotonic()-restart_started, 3),
                                 generation=b.generation, sessionId=b.session_id))
            sample()
        # Shutdown while HTTP restoration is still outstanding.
        with lock:
            faults.extend(['timeout'] * 5)
        generation = runtime.session.generation
        await runtime.reconnect_server()
        await wait(lambda: runtime.session.generation > generation)
        stopped = time.monotonic()
        await asyncio.wait_for(runtime.shutdown(), 10)
        await asyncio.wait_for(running, 5)
        assert not runtime.audio.is_running and not runtime.cleanup_errors
        assert runtime.session.binding is None and runtime.session.pending_count == 0
        assert not [t for t in asyncio.all_tasks() if t is not asyncio.current_task() and
                    t.get_name().startswith(('v2-', 'qualification-')) and not t.done()]
        after = identity()
        result = dict(result='PASS', before=before, after=after, serverCommit=SERVER,
            boundaries=__doc__, trace=trace, restarts=restarts, metrics=metrics,
            shutdownSeconds=round(time.monotonic()-stopped, 3), droppedAckCommandIds=dropped,
            productSourcesUnchanged=before['sourceSha256'] == after['sourceSha256'],
            realAudio=True, humanCases='NOT_PROVEN', paste='NOT_RUN', logStream='disabled for this test')
        if not result['productSourcesUnchanged']:
            raise RuntimeError('Sources changed during qualification')
        save(evidence/'real-recovery.json', result)
        print(json.dumps(dict(result='PASS', restarts=restarts, shutdownSeconds=result['shutdownSeconds'])))
    finally:
        await runtime.shutdown()
        await asyncio.gather(running, return_exceptions=True)
        proxy.shutdown()
        proxy.server_close()
        worker.join(2)
        save(evidence/'real-recovery-trace.json', trace)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    # Establish isolation before product imports resolve user paths.
    os.environ['VOICESTT_CLIENT_HOME'] = str(LOCAL/'recovery-audit')
    asyncio.run(run(args.evidence))
