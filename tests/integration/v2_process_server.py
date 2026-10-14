"""Pinned production ASGI app in a separate interpreter; loopback test controls.

Controls stimulate recorder/model outputs, never replace the production wire,
session, settings, ledger, log store or domain controller. No product edits.
"""
import argparse
import asyncio
import json
import hashlib
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.check_v2_release_server import SHA


def verify(root, repository):
    hashes={}
    for module in tuple(sys.modules.values()):
        filename=getattr(module,'__file__',None)
        if not filename: continue
        path=Path(filename).resolve()
        if path.suffix!='.py' or not path.is_relative_to(root) or path.is_relative_to(root/'venv'):
            continue
        name=path.relative_to(root).as_posix()
        expected=subprocess.check_output(['git','-C',str(repository),'show',f'{SHA}:{name}'])
        if path.read_bytes()!=expected: raise AssertionError('Changed server source: '+name)
        hashes[name]=hashlib.sha256(expected).hexdigest()
    assert 'api_fastapi_server/server.py' in hashes
    return hashes


def redact(value):
    if isinstance(value, dict):
        return {k: ('<redacted>' if k in ('accessToken', 'text', 'rawText', 'displayText')
                    else redact(v)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v) for v in value]
    return value


async def run(args):
    # Server tests must resolve from the export, not the client's tests package.
    sys.path.insert(0, str(args.server_root))
    import uvicorn
    from fastapi import Request
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import ManualScheduler
    from VoiceSTT.core.wake_detection import WakeHit, WakeAttemptPolicy
    import numpy as np
    verify(args.server_root, args.server_repository)
    os.environ.pop('VOICESTT_SERVER_COMMIT', None)  # Manifest proves unknown identity.
    wire = []
    with tempfile.TemporaryDirectory(prefix='iv2-010-server-data-') as data:
        settings = ServerSettings(data_root_path=data, model_warmup=False, max_sessions=1,
            admin_api_key='synthetic-process-admin', request_logging_enabled=False,
            performance_logging_enabled=False, performance_log_mirror_enabled=False,
            transcription_logging_enabled=True, system_event_logging_enabled=False,
            event_store_enabled=True, log_live_enabled=True)
        class Recorder(GateAwareRecorder):
            # Reuse AP040's immutable model-job boundary; the upstream test
            # recorder FIFO would attribute a later cancel to an older job.
            def abort(self):
                self.abort_controlled_activation()
                self.is_recording = False
                self._active_recording_context = None

            def flush_buffered_audio(self, min_abs_level=50):
                if not self.is_recording:
                    return False
                self.has_audio=False; self.is_recording=False; self.recording_stops+=1
                if self.on_recording_stop: self.on_recording_stop()
                context=self._current_transcription_context
                def final():
                    aborted=self.on_transcription_start(None) if self.on_transcription_start else False
                    try:
                        text='' if aborted else self.transcription_executor.transcribe(
                            np.ones(32,dtype=np.float32),language='en',use_prompt=True).text
                    except RuntimeError:
                        text=''
                    self.final_text.put((text,context))
                threading.Thread(target=final,daemon=True).start()
                return True

            def text(self):
                item=self.final_text.get()
                if item is None: return ''
                text,context=item
                # The production caller captures this immutable context.
                owner=service.sessions.get(self._qualification_session_id)
                if owner:
                    with owner.lock: owner._active_text_context=context
                return text

        app = create_app(settings, recorder_factory=Recorder,
                         scheduler_factory=ManualScheduler)
        service = app.state.voicestt_service
        service.wakeword_catalog.set_artifact_prober(lambda path: None)

        @app.post('/_qualification/control')
        async def control(request: Request):
            body = await request.json()
            action = body['action']
            domain = service.sessions.get(body.get('sessionId'))
            if action == 'inspect':
                return dict(exists=domain is not None,
                    jobs=[dict(index=i, sessionId=j.session_id, kind=j.kind)
                          for i, j in enumerate(service.scheduler.jobs)])
            if domain is None:
                raise ValueError('test session missing')
            domain.recorder._qualification_session_id=body['sessionId']
            if action == 'flush':
                domain.recorder.flush_buffered_audio()
            elif action == 'interim':
                domain._on_realtime_text(body['text'])
            elif action == 'complete':
                job = service.scheduler.jobs[body['index']]
                assert job.session_id == body['sessionId'] and job.kind == 'final'
                service.scheduler.complete(job, text=body['text'])
            elif action == 'wake':
                domain._on_wakeword_detection_start()
                hit = WakeHit(canonical_wake_word_id='hey_jarvis', peak_score=.91,
                    start_frame_index=0, start_sample=1280, qualification_frame_index=0,
                    qualification_sample=1280, finalization_frame_index=1,
                    operational_zero_point_sample=32000, prediction_frame_count=1,
                    policy=WakeAttemptPolicy(sensitivity=.5))
                return dict(accepted=domain._on_wakeword_detected(hit) is not None)
            elif action == 'recovery':
                wire.append(dict(direction='test_control', action='recovery',sessionId=body['sessionId']))
                domain.fail_closed_for_recovery(None)
            else:
                raise ValueError('unsupported test action')
            return dict(ok=True)

        async def observed(scope, receive, send):
            async def incoming():
                frame = await receive()
                if scope['type'] == 'websocket':
                    if frame.get('text'):
                        wire.append(dict(direction='client_to_server', path=scope['path'],
                                         payload=redact(json.loads(frame['text']))))
                    elif frame.get('bytes'):
                        wire.append(dict(direction='client_to_server', path=scope['path'],
                                         audioBytes=len(frame['bytes'])))
                return frame
            async def outgoing(frame):
                if scope['type'] == 'websocket':
                    if frame.get('text'):
                        wire.append(dict(direction='server_to_client', path=scope['path'],
                                         payload=redact(json.loads(frame['text']))))
                    elif frame['type'] == 'websocket.close':
                        wire.append(dict(direction='server_to_client', path=scope['path'],
                                         closeCode=frame.get('code')))
                await send(frame)
            if scope['type'] == 'http' and not scope['path'].startswith('/_qualification'):
                wire.append(dict(direction='http', path=scope['path'], method=scope['method']))
            await app(scope, incoming, outgoing)

        tcp = socket.socket()
        tcp.bind(('127.0.0.1', 0)); tcp.listen(16)
        server = uvicorn.Server(uvicorn.Config(observed, log_level='error', access_log=False))
        task = asyncio.create_task(server.serve(sockets=[tcp]))
        try:
            async with asyncio.timeout(20):
                while not server.started:
                    if task.done():
                        await task
                        raise RuntimeError('server startup failed')
                    await asyncio.sleep(.01)
            args.ready.write_text(json.dumps(dict(url=f'ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2',
                pid=os.getpid(), serverCommit=SHA, executable=sys.executable)), encoding='utf8')
            async with asyncio.timeout(180):
                while not args.stop.exists():
                    await asyncio.sleep(.05)
        finally:
            server.should_exit = True
            await asyncio.wait_for(task, 10)
            tcp.close()
            args.report.write_text(json.dumps(dict(serverCommit=SHA, pid=os.getpid(),
                sourceHashes=verify(args.server_root, args.server_repository), wire=wire,
                boundaries=__doc__), indent=2), encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('server-root', 'server-repository', 'ready', 'stop', 'report'):
        parser.add_argument('--'+name, required=True, type=Path)
    args = parser.parse_args()
    asyncio.run(run(args))
