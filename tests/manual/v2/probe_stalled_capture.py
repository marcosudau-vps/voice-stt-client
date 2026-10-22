"""Controlled native capture stall at the selected existing Pro-V2 server.

No activation, saved speech, injection, server lifecycle or model changes.
This is an injected driver fault, never a physical USB qualification.
"""
import argparse
import asyncio
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sys
import time

from tests.manual.v2.suite_plan import ROOT, PROFILE_RUNTIME, TARGET, TASKS
from tests.manual.v2.suite_session import prepare_profile, save


async def probe(folder, installed):
    if installed:
        sys.path.insert(0, str(installed.resolve()))
    from voice_stt_client.core.audio_capture import AudioCapture
    from voice_stt_client.core.settings_service import SettingsHTTP
    from voice_stt_client.core.v2_runtime import V2Runtime
    from voice_stt_client.core.v2_transport import V2TransportConfig
    from voice_stt_client.core.version import __version__
    import voice_stt_client
    device = next(d for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower())
    config = prepare_profile(folder, TARGET, TASKS[0], device['index'])
    config.event_stream.enabled = False
    config.led.enabled = False
    config.feedback.sounds_enabled = False
    runtime = V2Runtime(config, http=SettingsHTTP(TARGET, timeout=180),
        transport_config=V2TransportConfig(url=TARGET, client_version=__version__,
            connect_timeout=180, admission_timeout=180, bootstrap_timeout=180))
    commands, activations = [], []
    prior = runtime.session.on_completion
    def completed(value):
        if prior:
            prior(value)
        commands.append(dict(type=str(value.command.type),
            audioAvailable=value.command.payload.get('audioAvailable'), accepted=value.ack.accepted))
    runtime.session.on_completion = completed
    prior_message = runtime.session.on_message
    def message(binding, event):
        prior_message(binding, event)
        if str(event.type) == 'activation.started':
            activations.append(True)
    runtime.session.on_message = message
    async def wait(predicate, seconds):
        async with asyncio.timeout(seconds):
            while not predicate():
                await asyncio.sleep(.02)
    task = asyncio.create_task(runtime.run())
    try:
        await wait(lambda: runtime.session.is_ready and runtime.media.sent > 30, 200)
        binding = runtime.session.binding
        stream = runtime.audio._stream
        class ActiveDriver:
            # Simulate only the driver's false active flag, not PCM or network.
            active = True
            def stop(self): stream.stop()
            def close(self): stream.close()
        await asyncio.to_thread(stream.abort)
        runtime.audio._stream = ActiveDriver()
        lost_at = time.monotonic()
        await wait(lambda: any(x['type']=='audio_availability.set' and x['audioAvailable'] is False and x['accepted'] for x in commands), 6)
        await wait(lambda: runtime.media._gate and runtime.audio._stream is not stream
                   and not isinstance(runtime.audio._stream, ActiveDriver), 15)
        before = runtime.media.sent
        await wait(lambda: runtime.media.sent > before + 25, 10)
        availability = [x for x in commands if x['type']=='audio_availability.set']
        assert [x['audioAvailable'] for x in availability] == [False, True]
        assert all(x['accepted'] for x in availability)
        assert runtime.session.binding is binding and not activations
        return dict(result='PASS', timeUtc=datetime.now(UTC).isoformat(),
            productModule=str(Path(voice_stt_client.__file__).resolve()),
            target=TARGET, sessionId=binding.session_id, generation=binding.generation,
            wireServerCommit=binding.accepted.payload['serverCommit'],
            availability=availability, activations=0, captured=runtime.audio.chunks_captured,
            sent=runtime.media.sent, recoverySeconds=round(time.monotonic()-lost_at,3),
            failures=runtime.media.capture_failures,
            boundary='Controlled native stream abort with falsely active driver flag; not physical USB, no activation/final, no frozen desktop qualification.')
    finally:
        await runtime.shutdown()
        await asyncio.gather(task, return_exceptions=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile-runtime', action='store_true', required=True)
    parser.add_argument('--installed-root', type=Path)
    args = parser.parse_args()
    if args.installed_root and not args.installed_root.resolve().is_relative_to(ROOT.resolve()):
        parser.error('Installed test package must be inside the project')
    suffix = 'wheel' if args.installed_root else 'source'
    folder = PROFILE_RUNTIME/('stall-'+suffix+'-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    (folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),
        VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'), TEMP=str(folder/'tmp'), TMP=str(folder/'tmp'))
    try:
        result = asyncio.run(probe(folder, args.installed_root))
    except Exception as error:
        save(folder/'result.json', dict(result='FAIL', errorType=type(error).__name__))
        raise
    save(folder/'result.json', result)
    print(json.dumps(dict(folder=str(folder), **result)), flush=True)


if __name__ == '__main__':
    main()
