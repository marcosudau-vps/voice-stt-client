"""Real isolated tmpfs ENOSPC: pinned server/models, V2 STT and log transport.

Creates one additional labelled local test container, never edits server source.
Only its /data tmpfs is filled; the original qualification server and V1 remain
untouched. Real consented WAV replay, no live microphone or native injection.
The new container is stopped in finally and retained for inspection.
"""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import wave
from urllib.request import urlopen

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'scripts/qualify_v2_real.py').is_file())
sys.path.insert(0, str(ROOT))
from scripts.qualify_v2_real import LOCAL, SERVER, identity, save

NAME = 'voicestt-qualification-iv2-020-logfault'
SOURCE = 'voicestt-qualification-iv2-020'
URL = 'ws://127.0.0.1:18021/ws/v2'


def docker(*args, input=None, timeout=30):
    return subprocess.check_output(['docker', *args], input=input, timeout=timeout,
                                   stderr=subprocess.STDOUT)


def inspect(name):
    return json.loads(docker('inspect', name))[0]


def guard():
    info = inspect(NAME)
    if info['Config']['Labels'].get('voice-stt.qualification') != 'AP-IV2-020-logfault':
        raise RuntimeError('Refuse to mutate another workload')
    return info


async def exercise(audio, evidence):
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.config import ServerConfig, EventStreamConfig
    from voice_stt_client.core.session_coordinator import DualSessionCoordinator
    from voice_stt_client.core.settings_service import SettingsService
    from voice_stt_client.core.v2_mirror import V2MirrorConnection
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
    before = identity()
    session = V2STTSession(V2TransportConfig(url=URL))
    mirror = V2MirrorConnection(session)
    settings = SettingsService(session, V2Profile(desired_settings={'activation.followupTimeoutMs': 5000}))
    logs = DualSessionCoordinator(ServerConfig(url=URL), EventStreamConfig(cursor_persistence_enabled=False))
    trace, finals = [], []
    def record(kind, **fields):
        trace.append(dict(kind=kind, seconds=round(time.monotonic()-started, 3), **fields))
    logs.on_context_change = lambda c: record('log_context', state=str(c.event_state), code=c.unavailable_code)
    old_reduce = mirror.on_reduction
    def reduce(value):
        if old_reduce:
            old_reduce(value)
        for final in value.finals:
            finals.append(dict(segmentId=final.segment_id, characters=len(final.text),
                               textSha256=hashlib.sha256(final.text.encode()).hexdigest()))
    mirror.on_reduction = reduce
    async def bootstrap(client, binding):
        await settings.bootstrap(client, binding)
        await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=True)
        await logs.begin_generation(binding.generation)
        await logs.adopt_hello(binding.generation, binding.accepted.to_mapping())
    session.bootstrap = bootstrap
    task = asyncio.create_task(session.run())
    started = time.monotonic()
    async def wait(predicate, seconds=30):
        async with asyncio.timeout(seconds):
            while not predicate():
                if task.done():
                    await task
                    raise RuntimeError('STT ended unexpectedly')
                await asyncio.sleep(.02)
    try:
        await wait(lambda: session.is_ready and mirror.mirror.view.operations_ready)
        await wait(lambda: str(logs.context.event_state).lower().endswith('live'))
        if session.binding.accepted.payload['serverCommit'] != SERVER:
            raise RuntimeError('Wrong server identity')
        initial_session, generation = session.binding.session_id, session.generation
        guard()
        fill = '''import errno,json,os
p='/data/iv2-020-diskfill.bin'
written=0
try:
 with open(p,'xb',buffering=0) as f:
  while written<80*1024*1024:
   written+=f.write(bytes(65536))
except OSError as e:
 if e.errno!=errno.ENOSPC: raise
 print(json.dumps(dict(errno=e.errno,written=written,freeBytes=os.statvfs('/data').f_bavail*os.statvfs('/data').f_frsize)))
else: raise RuntimeError('Expected bounded tmpfs ENOSPC not reached')
'''
        fault = json.loads(await asyncio.to_thread(docker, 'exec', '-i', NAME, 'python', '-', input=fill.encode()))
        record('real_tmpfs_enospc', **fault)
        ack_start = time.monotonic()
        ack = await session.request(p.CommandType.ACTIVATION, action='activate', source='manual')
        if not ack.ack.accepted:
            raise RuntimeError('Activation during logstore failure rejected')
        record('activation_ack', elapsedSeconds=round(time.monotonic()-ack_start, 3))
        with wave.open(str(audio), 'rb') as wav:
            if (wav.getframerate(), wav.getnchannels(), wav.getsampwidth()) != (16000, 1, 2):
                raise ValueError('Unexpected fixture format')
            pcm = wav.readframes(wav.getnframes()) + bytes(5*32000)
        replay = time.monotonic()
        for offset in range(0, len(pcm), 1280):
            chunk = pcm[offset:offset+1280]
            if not await session.send_audio(chunk, 16000, 1, len(chunk)//2, binding=session.binding):
                raise RuntimeError('Audio rejected during logstore failure')
            await asyncio.sleep(max(0, replay+(offset+len(chunk))/32000-time.monotonic()))
        await wait(lambda: len(finals)>0)
        snapshot = await session.request(p.CommandType.SNAPSHOT_REQUEST)
        if not snapshot.ack.accepted:
            raise RuntimeError('Snapshot failed during logstore failure')
        record('stt_final_during_fault', finals=len(finals), ready=session.is_ready)
        raw_logs = await asyncio.to_thread(docker, 'logs', NAME)
        actual_disk_errors = raw_logs.lower().count(b'database or disk is full')
        guard()
        await asyncio.to_thread(docker, 'exec', NAME, 'python', '-c',
                               "from pathlib import Path;Path('/data/iv2-020-diskfill.bin').unlink()")
        record('fault_released')
        await asyncio.sleep(1)
        snapshot = await session.request(p.CommandType.SNAPSHOT_REQUEST)
        same = session.generation == generation and session.binding.session_id == initial_session
        passed = bool(actual_disk_errors and finals and all(f['characters'] for f in finals)
                      and same and session.is_ready and snapshot.ack.accepted and session.pending_count == 0)
        result = dict(result='PASS' if passed else 'FAIL', identity=before, serverCommit=SERVER,
            containerImage=guard()['Image'], audioSha256=hashlib.sha256(audio.read_bytes()).hexdigest(),
            trace=trace, finals=finals, actualSqliteDiskFullErrors=actual_disk_errors,
            sourceUnchanged=before['sourceSha256']==identity()['sourceSha256'],
            sameSttSessionAndGeneration=same, pending=session.pending_count,
            logContextAtEnd=str(logs.context.event_state), boundaries=__doc__)
        save(evidence/'logstore-diskfull.json', result)
        print(json.dumps({k:result[k] for k in ('result','actualSqliteDiskFullErrors','sameSttSessionAndGeneration')}))
        return 0 if passed else 1
    finally:
        await session.stop()
        await logs.shutdown()
        await mirror.close()
        await asyncio.gather(task, return_exceptions=True)
        save(evidence/'logstore-diskfull-trace.json', trace)


def main(args):
    source = inspect(SOURCE)
    if source['Config']['Labels'].get('voice-stt.qualification') != 'AP-IV2-020':
        raise RuntimeError('Wrong source workload')
    if docker('ps', '-a', '--filter', 'name=^/'+NAME+'$', '--format', '{{.Names}}').strip():
        raise RuntimeError('Refuse to replace an existing fault container')
    models = next(m for m in source['Mounts'] if m['Destination']=='/models/kroko')
    if source['Config']['Cmd'] != ['-m', 'VoiceSTT_server.server', '--config', '/server-qualification.yaml']:
        raise RuntimeError('Unexpected startup command; review before clone')
    created = False
    try:
        docker('create', '--name', NAME, '--label', 'voice-stt.qualification=AP-IV2-020-logfault',
               '-p', '127.0.0.1:18021:8010', '--tmpfs', '/data:rw,size=64m',
               '--mount', 'type=bind,source='+models['Source']+',target=/models/kroko,readonly',
               '--env-file', str(LOCAL/'server-config/guard.env'), source['Image'], *source['Config']['Cmd'])
        created = True
        guard()
        docker('cp', str(LOCAL/'server-config/server.yaml'), NAME+':/server-qualification.yaml')
        docker('start', NAME)
        deadline = time.monotonic()+180
        while time.monotonic()<deadline:
            try:
                with urlopen('http://127.0.0.1:18021/health', timeout=2) as response:
                    if json.load(response).get('ready'):
                        break
            except OSError:
                pass
            time.sleep(.5)
        else:
            raise TimeoutError('Isolated fault server not ready')
        return asyncio.run(exercise(args.audio, args.evidence))
    finally:
        if created:
            guard()
            docker('stop', '--time', '10', NAME)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--audio', type=Path, required=True)
    parser.add_argument('--evidence', type=Path, required=True)
    args = parser.parse_args()
    allowed = (Path(__file__).resolve().parent/'human/samples').resolve()
    if not args.audio.resolve().is_relative_to(allowed):
        parser.error('Only explicitly authorized test fixtures allowed')
    os.environ['VOICESTT_CLIENT_HOME'] = str(LOCAL/'logfault-client')
    raise SystemExit(main(args))
