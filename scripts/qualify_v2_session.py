"""Instrument the unchanged V2 desktop for an explicit human test session.

Example: project-venv python scripts/qualify_v2_session.py prepare
Then `run --mode manual|wake|both`. Everything is isolated under LOCALAPPDATA.
The run uses real audio, Qt/Win32, USB, sounds, clipboard and the local server.
It can paste into the foreground application after an activation: launch only
when the operator is ready with an empty test editor. No raw text is exported.
"""
import argparse
import asyncio
from dataclasses import asdict
from datetime import UTC, datetime
import json
import os
from pathlib import Path
import sys
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
LOCAL=Path(os.environ.get('LOCALAPPDATA',Path.home()))/'VoiceSTT-Qualification/AP-IV2-020'


def process_memory():
    import ctypes
    from ctypes import wintypes
    class Counters(ctypes.Structure):
        _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[
            (n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize',
            'QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage',
            'QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
    kernel=ctypes.WinDLL('kernel32',use_last_error=True)
    kernel.GetCurrentProcess.restype=wintypes.HANDLE
    api=ctypes.WinDLL('psapi',use_last_error=True)
    api.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(Counters),wintypes.DWORD]
    counters=Counters();counters.cb=ctypes.sizeof(counters)
    if not api.GetProcessMemoryInfo(kernel.GetCurrentProcess(),ctypes.byref(counters),counters.cb):
        raise ctypes.WinError(ctypes.get_last_error())
    return dict(workingSetBytes=counters.WorkingSetSize,privateBytes=counters.PrivateUsage)


def prepare():
    from voice_stt_client.core.config import AppConfig, DEFAULT_CONFIG_PATH
    from voice_stt_client.core.v2_profile import V2Profile
    from voice_stt_client.core.audio_capture import AudioCapture
    LOCAL.mkdir(parents=True,exist_ok=True)
    device=next(d for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower())
    paths={}
    for mode in ('manual','wake','both'):
        config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
        config.server.url='ws://127.0.0.1:18020/ws/v2'
        config.server.health_url='http://127.0.0.1:18020/health'
        config.audio.device=device['index']
        profile=V2Profile(manual=mode!='wake',wake_word=mode!='manual',
                          wake_word_ids=['hey_jarvis','alexa'] if mode!='manual' else [])
        profile.controls.update(primary_key='Ctrl+Shift+F8',secondary_key='Ctrl+Shift+F9',
            secondary_action='finish',wake_pause_key='Ctrl+Shift+F10',
            reinsert_last_key='Ctrl+Shift+F11',overlay_toggle_key='Ctrl+Shift+F12')
        config.v2_profile=asdict(profile)
        config.history.persistent.db_path=str(LOCAL/'client'/('history-'+mode+'.sqlite'))
        config.history.persistent.store_all=True
        config.history.persistent.min_characters=0
        config.logging.log_dir=str(LOCAL/'client/logs')
        config.logging.observability.store_transcription_content=False
        config.logging.observability.store_raw_payload=False
        config.event_stream.cursor_path=str(LOCAL/'client'/('cursor-'+mode+'.json'))
        path=LOCAL/('client-'+mode+'.yaml')
        if not path.exists():
            config.save(path)
        paths[mode]=str(path)
    print(json.dumps(dict(profiles=paths,device=device),ensure_ascii=True))


def record(name, seconds):
    """Deliberately spoken test sample; never called by preparation/autosmoke."""
    import re
    import wave
    import sounddevice as sd
    from voice_stt_client.core.audio_capture import AudioCapture
    from scripts.qualify_v2_real import digest, save
    if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',name) or not 1<=seconds<=60:
        raise ValueError('Use a safe sample name and 1..60 seconds')
    target=LOCAL/'samples'/(name+'.wav')
    if target.exists():
        raise FileExistsError(target)
    target.parent.mkdir(parents=True,exist_ok=True)
    device=next(d for d in AudioCapture.list_devices() if 'respeaker' in d['name'].lower())
    started=datetime.now(UTC).isoformat()
    data=sd.rec(int(seconds*16000),samplerate=16000,channels=1,dtype='int16',device=device['index'])
    sd.wait()
    with wave.open(str(target),'wb') as handle:
        handle.setnchannels(1);handle.setsampwidth(2);handle.setframerate(16000);handle.writeframes(data.tobytes())
    save(target.with_suffix('.json'),dict(name=name,sha256=digest(target),seconds=seconds,
        startedAtUtc=started,device=device,tester='Human speech / Codex recording',
        annotation='NOT_PROVEN: human wake-end/user-speech-start annotation pending'))
    print(json.dumps(dict(recorded=str(target),sha256=digest(target))))


def run(mode, smoke_seconds=0, smoke_restart=False):
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QTimer
    from voice_stt_client.core.config import AppConfig
    from voice_stt_client.core.v2_runtime import V2Runtime
    from voice_stt_client.ui.v2_core_bridge import V2CoreBridge
    from voice_stt_client.ui.v2_application import V2DesktopApplication
    from voice_stt_client.ui.single_instance import SingleInstanceGuard
    from scripts.qualify_v2_real import identity, save
    config_path=LOCAL/('client-'+mode+'.yaml')
    config=AppConfig.load(config_path)
    if smoke_seconds:
        if mode!='manual':raise ValueError('Autonomous smoke is manual-only')
        config.feedback.sounds_enabled=False
        config.led.enabled=False
        config.v2_profile['controls']['enabled']=False
    folder=LOCAL/'sessions'/datetime.now().strftime('%Y%m%d-%H%M%S')
    folder.mkdir(parents=True)
    trace=folder/'trace.jsonl'
    lock=threading.Lock()
    def emit(kind,**fields):
        with lock, trace.open('a',encoding='utf8') as handle:
            handle.write(json.dumps(dict(kind=kind,monotonic=time.monotonic(),
                timeUtc=datetime.now(UTC).isoformat(),**fields),ensure_ascii=True)+'\n')
    save(folder/'identity.json',dict(candidate=identity(),mode=mode,config=str(config_path),
        configSha256=__import__('hashlib').sha256(config_path.read_bytes()).hexdigest(),
        tester='Codex instrumentation; human interaction separately annotated',
        boundaries='Unmodified production desktop/core, source run; frozen UI separately qualified.'))
    def factory(cfg):
        runtime=V2Runtime(cfg)
        old=runtime.session.on_message
        def message(binding,event):
            old(binding,event)
            fields=dict(type=str(event.type),generation=binding.generation)
            for key in ('activationId','segmentId','eventSeq','stateVersion'):
                if hasattr(event,key):fields[key]=getattr(event,key)
            emit('event',**fields)
        runtime.session.on_message=message
        previous=runtime.session.on_completion
        def completed(value):
            if previous:previous(value)
            emit('ack',type=str(value.command.type),commandId=value.command.commandId,
                 accepted=value.ack.accepted,result=str(value.ack.result))
        runtime.session.on_completion=completed
        old_status=runtime.session.on_status
        def status(value):
            if old_status:old_status(value)
            emit('transport',state=str(value.state),reason=value.reason,generation=value.generation)
        runtime.session.on_status=status
        async def metrics():
            while not runtime.is_closing:
                view=runtime.mirror.mirror.view
                emit('metrics',generation=runtime.session.generation,ready=runtime.is_ready,
                    transport=str(runtime.session.status.state),reason=runtime.session.status.reason,
                    phase=str(view.input.phase),activationId=view.input.activation_id,
                    media=runtime.media.counters(),capture=runtime.audio.capture_counters(),
                    tasks=len(asyncio.all_tasks()),commands=len(runtime._commands),
                    trackerPending=runtime.session.pending_count,memory=process_memory(),
                    activations=len(view.activations),segments=len(view.segments),
                    terminalActivations=sum(a.status in ('completed','cancelled','failed') for a in view.activations.values()),
                    injectionQueue=runtime.queue.queue_size())
                await asyncio.sleep(1)
        # Observe task lifecycle alongside run; never replace production work.
        original_run=runtime.run
        async def measured_run():
            task=asyncio.create_task(metrics(),name='qualification-metrics')
            async def restart():
                while not runtime.is_ready:await asyncio.sleep(.1)
                await asyncio.sleep(2)
                proc=await asyncio.create_subprocess_exec('docker','inspect',
                    'voicestt-qualification-iv2-020','--format',
                    '{{index .Config.Labels "voice-stt.qualification"}}',stdout=asyncio.subprocess.PIPE)
                output,_=await proc.communicate()
                if proc.returncode or output.strip()!=b'AP-IV2-020':
                    raise RuntimeError('Refuse to restart another workload')
                emit('controlled_server_restart')
                proc=await asyncio.create_subprocess_exec('docker','restart','-t','2',
                    'voicestt-qualification-iv2-020',stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
                await asyncio.wait_for(proc.communicate(),30)
                emit('controlled_server_restart_complete',exitCode=proc.returncode)
            fault=asyncio.create_task(restart(),name='qualification-restart') if smoke_restart else None
            try:return await original_run()
            finally:
                if task.done() and not task.cancelled() and task.exception():
                    emit('metrics_failed',errorType=type(task.exception()).__name__)
                task.cancel();await asyncio.gather(task,return_exceptions=True)
                if fault:
                    if fault.done() and not fault.cancelled() and fault.exception():
                        emit('fault_control_failed',errorType=type(fault.exception()).__name__)
                    fault.cancel();await asyncio.gather(fault,return_exceptions=True)
        runtime.run=measured_run
        return runtime
    app=QApplication([])
    app.setOrganizationName('VoiceSTTQualification')
    app.setApplicationName('AP-IV2-020')
    app.setQuitOnLastWindowClosed(False)
    guard=SingleInstanceGuard('Local\\VoiceSTT_Qualification_AP_IV2_020')
    if not guard.acquire().acquired:
        raise RuntimeError('Another qualification desktop is running')
    desktop=None
    try:
        bridge=V2CoreBridge(config,runtime_factory=factory)
        desktop=V2DesktopApplication(app,config,guard,bridge=bridge)
        app.aboutToQuit.connect(desktop.shutdown)
        if not desktop.start():raise RuntimeError('Desktop failed to start')
        save(LOCAL/'active-session.json',dict(pid=os.getpid(),folder=str(folder),mode=mode))
        # File command queue is local-only and preserves every requested action.
        inbox=LOCAL/'commands';inbox.mkdir(exist_ok=True)
        processed={p.name for p in inbox.glob('*.json')}
        allowed={'primary':lambda:bridge.press_control('primary'),
                 'secondary':lambda:bridge.press_control('secondary'),
                 'wake_pause':lambda:bridge.press_control('wake_pause'),
                 'settings':desktop.show_settings,'reconnect':desktop.reconnect_server,
                 'stop':app.quit,'mark':lambda:None}
        def poll():
            for path in sorted(inbox.glob('*.json')):
                if path.name in processed:continue
                processed.add(path.name)
                command=json.loads(path.read_text())
                action=command.get('action')
                if action not in allowed:
                    emit('command_rejected',id=path.name);continue
                emit('command',id=path.name,action=action,case=command.get('case'))
                allowed[action]()
        timer=QTimer();timer.setInterval(100);timer.timeout.connect(poll);timer.start()
        if smoke_seconds:QTimer.singleShot(int(smoke_seconds*1000),app.quit)
        app.exec()
    finally:
        if desktop:desktop.shutdown()
        guard.release()
        emit('session_stopped')
    if smoke_seconds:
        records=[json.loads(line) for line in trace.read_text().splitlines()]
        samples=[r for r in records if r['kind']=='metrics']
        passed=any(r['ready'] and r['media']['sent']>20 for r in samples)
        passed=passed and not any(r['kind']=='metrics_failed' for r in records)
        if smoke_restart:
            passed=passed and any(r['ready'] and r['generation']>=2 and r['media']['sent']>20 for r in samples)
            passed=passed and any(r['kind']=='controlled_server_restart_complete' and r['exitCode']==0 for r in records)
            passed=passed and not any(r['kind']=='fault_control_failed' for r in records)
        save(folder/'smoke.json',dict(result='PASS' if passed else 'FAIL',samples=len(samples),
            boundaries='Actual microphone -> continuous V2 audio -> real local model server, native desktop and core thread; no activation, paste, LED output or sound playback.'))
        if not passed:raise RuntimeError('Instrumented desktop smoke failed')
    print(json.dumps(dict(session=str(folder))))


if __name__=='__main__':
    # Set before any product import; importing helpers in a unit test is inert.
    os.environ['VOICESTT_CLIENT_HOME']=str(LOCAL/'client')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('prepare','run','record'))
    parser.add_argument('--mode',choices=('manual','wake','both'),default='manual')
    parser.add_argument('--name')
    parser.add_argument('--seconds',type=float,default=12)
    parser.add_argument('--smoke-seconds',type=float,default=0)
    parser.add_argument('--smoke-restart',action='store_true')
    args=parser.parse_args()
    if args.action=='prepare':prepare()
    elif args.action=='record':record(args.name,args.seconds)
    else:run(args.mode,args.smoke_seconds,args.smoke_restart)
