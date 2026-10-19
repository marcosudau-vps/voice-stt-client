"""Autonomous read-only HTTP + bounded real manual-only desktop/audio precheck.

No server lifecycle commands, model switches, global keys, activation, LED or
sound output. PCM is transmitted to the human-selected server, never recorded.
"""
import asyncio
import argparse
from datetime import UTC, datetime
import json
import os
import subprocess
import sys
import time
from tests.manual.v2.suite_plan import ROOT, RUNTIME, PROFILE_RUNTIME, TARGET
from tests.manual.v2.suite_session import save


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile-runtime', action='store_true', required=True,
                        help='Explicitly authorized dedicated Windows-profile test runtime')
    parser.parse_args()
    folder = PROFILE_RUNTIME/('preflight-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    folder.mkdir(parents=True)
    (folder/'tmp').mkdir()
    os.environ['VOICESTT_CLIENT_HOME'] = str(folder/'client')
    os.environ['VOICESTT_CLIENT_CONFIG'] = str(folder/'profile.yaml')
    os.environ['TEMP'] = os.environ['TMP'] = str(folder/'tmp')
    from voice_stt_client.core.settings_service import SettingsHTTP
    from voice_stt_client.core.audio_capture import AudioCapture
    from scripts.qualify_v2_real import identity
    async def http():
        client = SettingsHTTP(TARGET, timeout=180)
        output = []
        for path in ('/api/v2/settings/schema', '/api/v2/settings/server', '/api/v2/wake-words'):
            response = await client.request('GET', path)
            output.append(dict(path=path, status=response.status,
                               protocolVersion=response.body.get('protocolVersion')))
        return output
    save(folder/'identity.json', identity())
    save(folder/'http.json', dict(target=TARGET, requests=asyncio.run(http()),
         scope='GET-only; no admin credentials, model mutation or server defaults PATCH'))
    devices = [device for device in AudioCapture.list_devices() if 'respeaker' in device['name'].lower()]
    if not devices:
        raise RuntimeError('No ReSpeaker available')
    state = folder/'editor-state.json'
    def heartbeat():
        save(state, dict(pid=os.getpid(), timeUtc=datetime.now(UTC).isoformat(),
                         editorHasFocus=False, foreground=False))
    heartbeat()
    env = dict(os.environ, QT_QPA_PLATFORM='offscreen')
    log_path = folder/'process.log'
    with log_path.open('w', encoding='utf8') as log:
        child = subprocess.Popen([sys.executable, '-u', '-m', 'tests.manual.v2.suite_session',
            '--folder', str(folder), '--editor-state', str(state), '--target', TARGET,
            '--task', 'finish', '--device', str(devices[0]['index']), '--smoke'],
            cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT)
        started = time.monotonic()
        while child.poll() is None:
            heartbeat()
            if time.monotonic()-started > 660:
                inbox = folder/'commands'
                inbox.mkdir(exist_ok=True)
                save(inbox/'bounded-stop.json', dict(action='stop'))
            if time.monotonic()-started > 690:
                child.terminate()
                child.wait(timeout=10)
                raise TimeoutError('Only the owned preflight child was terminated after failed shutdown')
            time.sleep(.25)
    result = json.loads((folder/'smoke.json').read_text(encoding='utf8')) if (folder/'smoke.json').exists() else {'result': 'FAIL'}
    save(folder/'result.json', dict(**result, exitCode=child.returncode, folder=str(folder)))
    print(json.dumps(dict(result=result['result'], exitCode=child.returncode, folder=str(folder))), flush=True)
    return 0 if child.returncode == 0 and result['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
