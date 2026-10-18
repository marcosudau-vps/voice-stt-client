"""AP-IV2-020 qualification helpers; never select the user's V1 profile.

Run with the client project venv. Reports contain identities, counters and
test observations, never PCM, transcript content or credentials. Explicit
speech recordings live outside Git and need an operator-supplied test name.
No operation changes server settings or an existing user configuration.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
from datetime import UTC, datetime
import gzip
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
from urllib.parse import urlsplit
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
SERVER = 'ada13b011e1d3829f78e7f389e3b927795a2b3be'
PARENT = 'b80ed8b81ad92bd02ac32553883443d2b7673bcd'
FROZEN_SHA256 = 'dccc449d227e7e3580bbdfa333f7386ac6070f007eee29c40971f863375c6f5d'
LOCAL = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'VoiceSTT-Qualification/AP-IV2-020'
sys.path.insert(0, str(ROOT))


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def identity():
    scopes = ('voice_stt_client', 'tests', 'scripts', 'requirements.txt',
              'requirements-dev.txt', 'pyproject.toml', 'setup.py', 'VERSION')
    names = git('ls-files', '--cached', '--others', '--exclude-standard', '--', *scopes).splitlines()
    hashes = {n: digest(ROOT/n) for n in sorted(set(names)) if (ROOT/n).is_file()}
    return dict(commit=git('rev-parse', 'HEAD'), tree=git('rev-parse', 'HEAD^{tree}'),
                canonicalParent=PARENT, sourceSha256=hashes,
                relevantDiffSha256=hashlib.sha256(git('diff', 'HEAD', '--', *scopes).encode()).hexdigest(),
                runtime=dict(python=sys.version, executable=sys.executable, os=platform.platform()),
                timeUtc=datetime.now(UTC).isoformat())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False)+'\n', encoding='utf8')


def loopback_origin(url):
    parts = urlsplit(url)
    if (parts.scheme != 'http' or parts.hostname not in ('127.0.0.1', 'localhost', '::1')
            or parts.username or parts.password or parts.query or parts.fragment
            or parts.path not in ('', '/')):
        raise ValueError('qualification requires an HTTP loopback origin')
    return url.rstrip('/')


def get_json(url):
    with urlopen(url, timeout=15) as response:
        return json.load(response)


def command(name, argv, evidence, *, timeout=900, extra_env=None):
    """Complete logs and immutable pre/post source identity, including failures."""
    evidence = Path(evidence)
    evidence.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, PYTHONUTF8='1', QT_QPA_PLATFORM='offscreen')
    # Unit path-boundary fixtures deliberately control HOME/default roots.
    # Native session helpers establish their isolated profile before imports.
    env.pop('VOICESTT_CLIENT_HOME', None)
    env.pop('VOICESTT_CLIENT_CONFIG', None)
    if extra_env:
        env.update(extra_env)
    before = identity()
    start = time.monotonic()
    path = evidence/(name+'.txt')
    with path.open('wb') as handle:
        handle.write((json.dumps(dict(command=argv, cwd=str(ROOT)))+'\n').encode())
        handle.flush()
        try:
            result = subprocess.run(argv, cwd=ROOT, env=env, stdout=handle,
                                    stderr=subprocess.STDOUT, timeout=timeout)
            code = result.returncode
        except subprocess.TimeoutExpired:
            code = 124
    raw = path.read_bytes()
    packed = gzip.compress(raw, mtime=0)
    path.with_suffix('.txt.gz').write_bytes(packed)
    path.unlink()
    after = identity()
    result = dict(name=name, command=argv, exitCode=code,
                  durationSeconds=round(time.monotonic()-start, 3),
                  log=name+'.txt.gz', sha256=hashlib.sha256(raw).hexdigest(),
                  gzipSha256=hashlib.sha256(packed).hexdigest(),
                  before=before, after=after,
                  result='PASS' if code == 0 and before['sourceSha256'] == after['sourceSha256']
                         and before['commit'] == after['commit'] else 'FAIL')
    save(evidence/(name+'.json'), result)
    print(name, result['result'], code, flush=True)
    return result


def preflight(evidence):
    import numpy as np
    import sounddevice as sd
    from voice_stt_client.core.audio_capture import AudioCapture
    from voice_stt_client.core.config import AudioConfig
    from voice_stt_client.core.credential_store import CredentialStore
    from lefx.device.respeaker.transport import UsbTransport
    import secrets

    result = dict(identity=identity(), tester='Codex/local Windows',
                  boundaries='Native device access prechecks only; no M-case completion, no speech recording.')
    devices = AudioCapture.list_devices()
    candidates = [d for d in devices if 'respeaker' in d['name'].lower()]
    if not candidates:
        raise RuntimeError('ReSpeaker input missing')
    # Prefer a fully named MME/DirectSound input; indices remain session-local.
    device = candidates[0]
    packets, levels, intervals = [], [], []
    previous = None
    def packet(pcm, rate, channels, frames):
        nonlocal previous
        now = time.monotonic()
        if previous is not None:
            intervals.append((now-previous)*1000)
        previous = now
        packets.append((rate, channels, frames, len(pcm)))
        samples = np.frombuffer(pcm, dtype='<i2').astype('float64')
        levels.append(float(np.sqrt(np.mean(samples*samples))))
    capture = AudioCapture(AudioConfig(device=device['index']), queue_duration_ms=500)
    capture.on_audio_packet = packet
    try:
        capture.probe()
        capture.start()
        time.sleep(3)
    finally:
        capture.stop()
    result['audio'] = dict(device=device, packets=len(packets),
        formats=sorted(set(packets)), counters=capture.capture_counters(),
        rmsMin=min(levels, default=None), rmsMax=max(levels, default=None),
        intervalP95Ms=float(np.percentile(intervals, 95)) if intervals else None,
        result='PASS' if len(packets) >= 40 and all(p[3] == p[1]*p[2]*2 for p in packets) else 'FAIL',
        rawAudioSaved=False)
    transport = UsbTransport()
    try:
        transport.start()
        deadline = time.monotonic()+8
        while not transport.is_connected and time.monotonic() < deadline:
            time.sleep(.05)
        if transport.is_connected:
            result['usb'] = dict(result='PASS', version=list(transport.read('VERSION')),
                gpo=list(transport.read('GPO_READ_VALUES')), stats=transport.stats(),
                writes=False, forceClaim=False)
        else:
            result['usb'] = dict(result='NOT_PROVEN', reason=transport.last_error,
                                 writes=False, forceClaim=False)
    finally:
        transport.close()
    # Random .invalid origin, guaranteed absent before writing; clean up only it.
    vault = CredentialStore()
    origin = 'https://iv2-020-'+secrets.token_hex(16)+'.invalid'
    if vault.read(origin) is not None:
        raise RuntimeError('Unexpected credential collision')
    a, b = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
    try:
        vault.save(origin, a)
        created = vault.read(origin) == a
        vault.save(origin, b)
        replaced = vault.read(origin) == b
    finally:
        vault.delete(origin)
    result['credentials'] = dict(result='PASS' if created and replaced and vault.read(origin) is None else 'FAIL',
        create=created, replace=replaced, delete=vault.read(origin) is None,
        boundaries='Actual Windows Credential Manager; unique disposable origin; no real admin key.')
    frozen = ROOT/'dist/voice-stt-client.exe'
    result['frozen'] = dict(sha256=digest(frozen), result='PASS' if digest(frozen) == FROZEN_SHA256 else 'FAIL')
    save(Path(evidence)/'native-preflight.json', result)
    return result


def server_inventory(origin, evidence):
    origin = loopback_origin(origin)
    schema = get_json(origin+'/api/v2/settings/schema')
    if schema.get('serverCommit') != SERVER or schema.get('secretsExposed') is not False:
        raise RuntimeError('Wrong or unsafe server identity')
    defaults = get_json(origin+'/api/v2/settings/server')
    if defaults.get('serverCommit') != SERVER:
        raise RuntimeError('Server identity changed')
    result = dict(identity=identity(), origin=origin, schema=schema, serverDefaults=defaults,
                  catalog=get_json(origin+'/api/v2/wake-words'),
                  health=get_json(origin+'/health'))
    save(Path(evidence)/'real-server-inventory.json', result)
    return result


def parameter_inventory(evidence):
    import wave
    from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
    from voice_stt_client.core.settings_metadata import SETTING_DEFINITIONS, get_config_value
    from voice_stt_client.core.v2_transport import V2TransportConfig
    from voice_stt_client.core.activation_mirror import MirrorLimits
    from voice_stt_client.core.led_controller import InProcessLedController
    from voice_stt_client.ui.feedback import resolve_sound_asset
    config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
    local=[]
    for definition in SETTING_DEFINITIONS:
        local.append(dict(key=definition.path,default=get_config_value(config,definition.path),
            min=definition.minimum,max=definition.maximum,
            policy=definition.apply_policy.value,authority='client_local',
            source='core/settings_metadata.py + packaged config.yaml'))
    c=InProcessLedController(sink='null')
    effects={}
    try:
        for name in config.feedback_mappings.led_targets():
            detail=c._service.show(name)
            effects[name]={key:detail.get(key) for key in ('qualified_id','version','config','runtime_info')}
    finally:c.close()
    sounds={}
    for name,value in vars(config.feedback).items():
        if name.endswith('_sound') and value:
            path=resolve_sound_asset(value)
            with wave.open(str(path),'rb') as audio:
                sounds[name]=dict(asset=value,durationMs=audio.getnframes()/audio.getframerate()*1000,
                    sha256=digest(path))
    result=dict(identity=identity(),localEditable=local,
        activeV2Transport=asdict(V2TransportConfig()),activeMirror=asdict(MirrorLimits()),
        activeMedia=dict(queueMs=500,recoveryIntervalSeconds=.25,shutdownTimeoutSeconds=3),
        yamlClientSections={name:asdict(getattr(config,name)) for name in
            ('audio','overlay','led','text_injection','clipboard','event_stream')},
        feedbackMappings=config.feedback_mappings.to_mapping(),ledEffects=effects,sounds=sounds,
        caveats=['V2Runtime forwards YAML reconnect bounds/capacity to V2TransportConfig; other transport timings are constructor defaults, not editable YAML server.hello/ready/ping settings.',
                 'Legacy session/dictation_window fields are migration inputs, not V2 timing authorities.',
                 'Packaged LED brightness=192 and sounds_enabled=true override dataclass 64/false.',
                 'NA session wishes re-bootstrap on reconnect; NS noise/VAD require isolated server defaults; reconnect plus session patch cannot activate them.'])
    save(Path(evidence)/'parameter-inventory.json',result)
    return result


async def real_admission(evidence):
    import asyncio
    from voice_stt_client.core import protocol_v2 as p
    from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
    from voice_stt_client.core.v2_mirror import V2MirrorConnection
    from voice_stt_client.core.settings_service import SettingsService
    from voice_stt_client.core.v2_profile import V2Profile
    rows=[]
    for manual,wake in ((True,False),(False,True),(True,True)):
        ids=['hey_jarvis','alexa'] if wake else []
        session=V2STTSession(V2TransportConfig(url='ws://127.0.0.1:18020/ws/v2',
            manual=manual,wake_word=wake,wake_word_ids=tuple(ids)))
        mirror=V2MirrorConnection(session)
        settings=SettingsService(session,V2Profile(manual=manual,wake_word=wake,wake_word_ids=ids))
        async def bootstrap(client,binding):
            await client.bootstrap_command(binding,p.CommandType.AUDIO_AVAILABILITY,audioAvailable=False)
            await settings.bootstrap(client,binding)
        session.bootstrap=bootstrap
        task=asyncio.create_task(session.run())
        started=time.monotonic()
        try:
            async with asyncio.timeout(60):
                while not session.is_ready:
                    if task.done() or session.status.state.value=='blocked':
                        raise RuntimeError('Real admission blocked: '+session.status.reason)
                    await asyncio.sleep(.02)
            if session.binding.accepted.payload['serverCommit']!=SERVER:
                raise RuntimeError('Wrong server')
            result=await session.request(p.CommandType.SNAPSHOT_REQUEST)
            rows.append(dict(manual=manual,wakeWord=wake,wakeWordIds=ids,
                readySeconds=round(time.monotonic()-started,3),accepted=result.ack.accepted,
                audioAvailable=mirror.mirror.view.audio_available,pending=session.pending_count))
        finally:
            await session.stop();await mirror.close();await asyncio.gather(task,return_exceptions=True)
    result=dict(identity=identity(),serverCommit=SERVER,rows=rows,
        result='PASS' if len(rows)==3 and all(r['accepted'] and not r['audioAvailable'] for r in rows) else 'FAIL',
        boundaries='Actual production HTTP/WS, ASR server and selected real Wake ONNX models. Audio explicitly unavailable: no microphone, positive speech, activation, paste or perceptual gate.')
    save(Path(evidence)/'real-admission.json',result)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=('preflight', 'server', 'parameters', 'admission', 'full-suite'))
    parser.add_argument('--evidence', type=Path, required=True)
    parser.add_argument('--origin', default='http://127.0.0.1:18020')
    args = parser.parse_args()
    if args.action == 'preflight':
        result = preflight(args.evidence)
        print(json.dumps({k: v.get('result') for k,v in result.items() if isinstance(v,dict) and 'result' in v}))
    elif args.action == 'server':
        result = server_inventory(args.origin, args.evidence)
        print(json.dumps(dict(serverCommit=result['schema']['serverCommit'],
                              ready=result['health'].get('ready'))))
    elif args.action == 'parameters':
        result=parameter_inventory(args.evidence)
        print(json.dumps(dict(localFields=len(result['localEditable']),ledEffects=len(result['ledEffects']))))
    elif args.action == 'admission':
        import asyncio
        result=asyncio.run(real_admission(args.evidence))
        print(result['result'])
    else:
        result = command('client-full', [sys.executable, '-m', 'unittest', 'discover',
                         '-v', '-s', 'tests', '-p', 'test_*.py'], args.evidence)
        return 0 if result['result'] == 'PASS' else 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
