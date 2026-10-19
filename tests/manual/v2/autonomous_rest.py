"""Native credential lifecycle and real idle run-pause/reconnect qualification.

No activation, speech recording, paste, global key, LED, sound, admin PATCH or
server lifecycle operation. Only the owned TLS socket is interrupted. Native
credential entries use unique .invalid origins and are removed in finally.
"""
import argparse
import asyncio
from datetime import UTC, datetime
import json
import os
import secrets
import subprocess
import sys
import uuid

from tests.manual.v2.suite_plan import ROOT, PROFILE_RUNTIME, TARGET, TASKS
from tests.manual.v2.suite_session import prepare_profile, save


def credential_child():
    # Expectations travel on the private pipe, never command line or logs.
    from voice_stt_client.core.credential_store import CredentialStore
    data = json.load(sys.stdin)
    value = CredentialStore().read(data['origin'])
    matched = value == data['expected']
    print(json.dumps(dict(matched=matched, pid=os.getpid())))
    return 0 if matched else 1


def native_credentials():
    from voice_stt_client.core.credential_store import CredentialStore, credential_target
    origins = [f'https://ap-iv2-020-{uuid.uuid4().hex}.invalid' for _ in range(2)]
    store = CredentialStore()
    # Refuse to modify even an improbably preexisting target.
    if any(store.read(origin) is not None for origin in origins):
        raise RuntimeError('Unique credential target already exists')
    checks, child_pids = {}, []
    def child_read(origin, expected):
        process = subprocess.run([sys.executable, '-m', 'tests.manual.v2.autonomous_rest', '--credential-child'],
            input=json.dumps(dict(origin=origin, expected=expected)), text=True,
            capture_output=True, timeout=20, cwd=ROOT)
        if process.returncode != 0:
            raise RuntimeError('Fresh credential reader failed; output withheld')
        observed = json.loads(process.stdout)
        child_pids.append(observed['pid'])
        return observed['matched'] and observed['pid'] != os.getpid()
    try:
        first, second = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        store.save(origins[0], first)
        checks['createRead'] = store.read(origins[0]) == first
        checks['freshProcessRead'] = child_read(origins[0], first)
        store.save(origins[0], second)
        checks['replaceRead'] = store.read(origins[0]) == second
        checks['freshProcessReplaced'] = child_read(origins[0], second)
        checks['differentOriginEmpty'] = store.read(origins[1]) is None
        store.save(origins[1], first)
        checks['originIsolation'] = store.read(origins[0]) == second and store.read(origins[1]) == first
        checks['reprRedacted'] = first not in repr(store) and second not in repr(store)
        store.delete(origins[0])
        checks['deleteRead'] = store.read(origins[0]) is None
        checks['freshProcessDeleted'] = child_read(origins[0], None)
        checks['otherOriginSurvivesDelete'] = store.read(origins[1]) == first
    finally:
        # Only these two new owned targets; no enumeration or real host access.
        for origin in origins:
            store.delete(origin)
        checks['allOwnedCredentialsDeleted'] = all(store.read(origin) is None for origin in origins)
    return dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
        targets=[credential_target(origin) for origin in origins], childPids=child_pids,
        boundary='Actual Windows vault create/replace/read/delete across fresh Python processes and two unique origins; no real admin authentication, UI, frozen build or full M-09 claim')


def assess_idle_samples(samples, activation_count, paste_attempts):
    names = {s['name'] for s in samples}
    expected = {'initial', 'manual-paused', 'both-paused', 'manual-reconnect-1',
        'manual-reconnect-2', 'socket-loss', 'mute-signal', 'unmute-signal',
        'wake-mask-only', 'both-paused-final', 'fresh-runtime'}
    by_name = {s['name']: s for s in samples}
    paused = ('both-paused', 'manual-reconnect-1', 'manual-reconnect-2',
              'socket-loss', 'mute-signal', 'unmute-signal', 'both-paused-final')
    checks = dict(allSamples=names == expected, noActivation=activation_count == 0,
        noPaste=paste_attempts == 0,
        pausesConfirmed=all(by_name.get(n,{}).get('desired') == [True,True]
            and by_name.get(n,{}).get('confirmed') == [True,True] for n in paused),
        manualMaskSeparate=by_name.get('manual-paused',{}).get('confirmed') == [True,False],
        wakeMaskSeparate=by_name.get('wake-mask-only',{}).get('confirmed') == [False,True],
        freshRuntimeClearsPause=by_name.get('fresh-runtime',{}).get('confirmed') == [False,False],
        preferencesRetained=bool(samples) and all(s.get('followupMs') == 5000 for s in samples),
        allReady=bool(samples) and all(s.get('ready') is True for s in samples),
        noPending=bool(samples) and all(s.get('pending') == 0 for s in samples))
    reconnect = [by_name.get(n,{}) for n in ('both-paused','manual-reconnect-1','manual-reconnect-2','socket-loss')]
    checks['freshSessions'] = len({s.get('sessionId') for s in reconnect if s.get('sessionId')}) == 4
    checks['increasingGenerations'] = all(a.get('generation',-1) < b.get('generation',-1) for a,b in zip(reconnect,reconnect[1:]))
    checks['audioProgressAfterReconnect'] = all(b.get('sent',0) >= a.get('sent',0)+25 for a,b in zip(reconnect,reconnect[1:]))
    checks['muteAvailability'] = by_name.get('mute-signal',{}).get('audioAvailable') is False
    checks['unmuteAvailability'] = by_name.get('unmute-signal',{}).get('audioAvailable') is True
    return dict(result='PASS' if all(checks.values()) else 'FAIL', checks=checks,
        boundary='Actual source Runtime/HTTP/TLS/PortAudio idle; wake engine disabled. Masks are real server-confirmed, mute is software signal only. No physical mute, activation phase, UI/global key, server restart, pending-final, ASR or frozen qualification.')


async def idle_runtime(folder):
    from voice_stt_client.core.audio_capture import AudioCapture
    from voice_stt_client.core.config import AppConfig
    from voice_stt_client.core.settings_service import SettingsHTTP
    from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
    from voice_stt_client.core.v2_runtime import V2Runtime
    from voice_stt_client.core.v2_transport import V2TransportConfig
    from voice_stt_client.core.version import __version__
    from tests.manual.v2.observed_session import safe_event
    from scripts.qualify_v2_session import process_memory
    device = next(d for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower())
    config = prepare_profile(folder, TARGET, TASKS[0], device['index'])
    config.event_stream.enabled = False
    config.led.enabled = config.feedback.sounds_enabled = False
    config.v2_profile['controls']['enabled'] = False
    config.save(folder/'profile.yaml')
    samples, events, commands, runtimes, cleanups = [], [], [], [], []
    attempted_pastes = []
    class NoTarget(CtypesWindowsInjectionBackend):
        def get_foreground_window(self):
            attempted_pastes.append(True)
            return 0
        def send_input_keyboard(self, events):
            attempted_pastes.append(True)
            return 0
    async def wait(predicate, seconds=200):
        async with asyncio.timeout(seconds):
            while not predicate():
                await asyncio.sleep(.025)
    def create(cfg):
        runtime = V2Runtime(cfg, backend=NoTarget(), http=SettingsHTTP(TARGET, timeout=180),
            transport_config=V2TransportConfig(url=TARGET, client_version=__version__,
                connect_timeout=180, admission_timeout=180, bootstrap_timeout=180))
        runtimes.append(runtime)
        previous = runtime.session.on_message
        def message(binding, event):
            previous(binding,event)
            events.append(dict(timeUtc=datetime.now(UTC).isoformat(), **safe_event(binding,event)))
        runtime.session.on_message = message
        old = runtime.session.on_completion
        def completed(value):
            if old: old(value)
            commands.append(dict(type=str(value.command.type), accepted=value.ack.accepted,
                result=str(value.ack.result), manual=value.command.payload.get('manual'),
                wakeWord=value.command.payload.get('wakeWord'), audioAvailable=value.command.payload.get('audioAvailable')))
        runtime.session.on_completion = completed
        return runtime, asyncio.create_task(runtime.run())
    async def sample(runtime, name, desired, *, audio=True):
        await wait(lambda: runtime.is_ready and not runtime.controls.pause_view.pending
            and runtime.media.audio_available is audio and runtime.session.pending_count == 0)
        view, pause = runtime.get_snapshot(), runtime.controls.pause_view
        if (pause.desired_manual,pause.desired_wake_word) != desired:
            raise AssertionError('Unexpected desired run-pause mask')
        samples.append(dict(name=name, timeUtc=datetime.now(UTC).isoformat(),
            ready=runtime.is_ready, generation=view.generation, sessionId=view.session_id,
            desired=list(desired), confirmed=[pause.confirmed_manual,pause.confirmed_wake_word],
            followupMs=view.mirror.effective_settings.get('activation.followupTimeoutMs'),
            audioAvailable=runtime.media.audio_available, sent=runtime.media.sent,
            pending=runtime.session.pending_count, commands=len(runtime._commands),
            tasks=len(asyncio.all_tasks()), media=runtime.media.counters(), memory=process_memory(),
            wireServerCommit=runtime.session.binding.accepted.payload['serverCommit']))
        save(folder/'samples.json',samples)
        print('Observed '+name, flush=True)
    runtime, runner = create(config)
    try:
        await wait(lambda: runtime.is_ready and runtime.media.sent > 30)
        await sample(runtime,'initial',(False,False))
        await runtime.controls.set_pause('manual',True)
        await sample(runtime,'manual-paused',(True,False))
        result = await runtime.primary_dictation_action()
        if result.success:
            raise AssertionError('Paused primary action was accepted')
        await runtime.controls.set_pause('wakeWord',True)
        await sample(runtime,'both-paused',(True,True))
        for name in ('manual-reconnect-1','manual-reconnect-2','socket-loss'):
            before = runtime.session.binding
            sent_before = runtime.media.sent
            if name == 'socket-loss':
                runtime.session._ws.transport.abort()
            else:
                result = await runtime.reconnect_server()
                if not result.success: raise AssertionError('Reconnect rejected')
            await wait(lambda: runtime.is_ready and runtime.session.binding is not before
                and runtime.media.sent >= sent_before+25)
            await sample(runtime,name,(True,True))
        runtime.set_microphone_muted(True)
        await wait(lambda: runtime.mirror.mirror.view.audio_available is False)
        await sample(runtime,'mute-signal',(True,True),audio=False)
        runtime.set_microphone_muted(False)
        await wait(lambda: runtime.mirror.mirror.view.audio_available is True)
        await sample(runtime,'unmute-signal',(True,True))
        await runtime.controls.set_pause('manual',False)
        await sample(runtime,'wake-mask-only',(False,True))
        await runtime.controls.set_pause('manual',True)
        await sample(runtime,'both-paused-final',(True,True))
        await runtime.shutdown()
        await asyncio.wait_for(runner,15)
        cleanups.append(list(runtime.cleanup_errors))
        # New actual runtime reloads the isolated disk profile. It must not inherit run pauses.
        fresh, fresh_runner = create(AppConfig.load(folder/'profile.yaml'))
        try:
            await wait(lambda: fresh.is_ready and fresh.media.sent > 30)
            await sample(fresh,'fresh-runtime',(False,False))
        finally:
            await fresh.shutdown()
            await asyncio.wait_for(fresh_runner,15)
            cleanups.append(list(fresh.cleanup_errors))
        result = assess_idle_samples(samples,sum(e['type']=='activation.started' for e in events),len(attempted_pastes))
        result.update(samples=samples, commands=commands, cleanups=cleanups,
            device=device, target=TARGET, ownSocketAborted=True)
        result['checks']['cleanShutdown'] = all(not errors for errors in cleanups)
        if not all(result['checks'].values()): result['result']='FAIL'
        return result
    finally:
        await runtime.shutdown()
        await asyncio.wait_for(runner,15)
        save(folder/'events.json',events)
        save(folder/'commands.json',commands)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credential-child',action='store_true')
    parser.add_argument('--profile-runtime',action='store_true')
    args = parser.parse_args()
    if args.credential_child:
        return credential_child()
    if not args.profile_runtime: parser.error('--profile-runtime is required')
    folder = PROFILE_RUNTIME/('autonomous-rest-'+datetime.now().strftime('%Y%m%d-%H%M%S'))
    (folder/'tmp').mkdir(parents=True)
    os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),
        VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'), TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'))
    from scripts.qualify_v2_real import identity
    from voice_stt_client.ui.single_instance import SingleInstanceGuard
    guard = SingleInstanceGuard(r'Local\VoiceSTT_Qualification_AP_IV2_020')
    if not guard.acquire().acquired: raise RuntimeError('Another qualification instance is active')
    save(folder/'identity.json',identity())
    print('Runtime '+str(folder),flush=True)
    try:
        credentials=native_credentials()
        save(folder/'credentials.json',credentials)
        runtime=asyncio.run(idle_runtime(folder))
        save(folder/'runtime.json',runtime)
        result=dict(result='PASS' if credentials['result']==runtime['result']=='PASS' else 'FAIL',
            timeUtc=datetime.now(UTC).isoformat(), folder=str(folder),
            credentials=credentials['result'],runtime=runtime['result'])
        save(folder/'result.json',result)
        print(json.dumps(result),flush=True)
        return 0 if result['result']=='PASS' else 1
    except Exception as error:
        save(folder/'result.json',dict(result='FAIL',errorType=type(error).__name__))
        raise
    finally:
        guard.release()


if __name__ == '__main__':
    raise SystemExit(main())
