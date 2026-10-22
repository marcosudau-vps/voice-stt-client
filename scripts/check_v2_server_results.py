"""AP060 production server -> TCP/WebSocket -> mirror -> SQLite -> injection.

Only recorder/model scheduler outputs, settings/audio bootstrap and Windows
Clipboard/SendInput are controlled test boundaries. No user data/live service.
"""
import argparse
import asyncio
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from scripts.check_v2_server_transport import SERVER_SHA,verify_sources,until
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig,HistoryPersistentConfig
from voice_stt_client.core.final_results import V2ResultService
from voice_stt_client.core.history import TranscriptHistoryManager
from voice_stt_client.core.reinsertion import TranscriptReinsertionService
from voice_stt_client.core.text_injector import TextInjectionQueue,WindowsInjectionBackend
from voice_stt_client.core.v2_controls import V2ControlService
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_transport import V2STTSession,V2TransportConfig


class ClipboardAdapter(WindowsInjectionBackend):
    """Explicit OS boundary; exercises the real queue/restore/reservation code."""
    def __init__(self,history):
        self.history=history; self.owner=0; self.clipboard='synthetic prior clipboard'
        self.sequence=1; self.writes=[]; self.pastes=[]; self.pending_before_paste=[]
    def create_owner_window(self): self.owner=1
    def destroy_owner_window(self): self.owner=0
    def get_owner_window(self): return self.owner
    def open_clipboard(self,hwnd): return bool(hwnd)
    def close_clipboard(self): return True
    def empty_clipboard(self): self.clipboard=None; return True
    def is_format_available(self,format_id): return self.clipboard is not None
    def get_clipboard_data_unicode(self): return self.clipboard
    def set_clipboard_data_unicode(self,text):
        self.clipboard=text; self.sequence+=1; self.writes.append(text); return True
    def get_clipboard_sequence_number(self): return self.sequence
    def get_foreground_window(self): return 42
    def get_window_thread_process_id(self,hwnd): return (1,2)
    def get_pressed_modifiers(self): return ()
    def send_input_keyboard(self,events):
        entries=self.history.get_persistent_entries()
        self.pending_before_paste.append(any(a.status=='pending' for e in entries for a in e.attempts))
        self.pastes.append(self.clipboard); return len(events)


async def run(root,repository):
    sys.path.insert(0,str(root))
    import uvicorn
    from api_fastapi_server.server import create_app,ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import ManualScheduler
    verify_sources(root,repository)
    checks=[]; trace=[]; reductions=[]; outcomes=[]
    def check(name,condition):
        if not condition: raise AssertionError(name)
        checks.append(name)
    with tempfile.TemporaryDirectory(prefix='cv2-060-server-') as data,patch.dict(os.environ,{'VOICESTT_SERVER_COMMIT':SERVER_SHA}):
        settings=ServerSettings(data_root_path=data,model_warmup=False,request_logging_enabled=False,
            performance_logging_enabled=False,performance_log_mirror_enabled=False,
            transcription_logging_enabled=False,system_event_logging_enabled=False,event_store_enabled=False,log_live_enabled=False)
        app=create_app(settings,recorder_factory=GateAwareRecorder,scheduler_factory=ManualScheduler)
        service=app.state.voicestt_service
        tcp=socket.socket(); tcp.bind(('127.0.0.1',0)); tcp.listen(16)
        server=uvicorn.Server(uvicorn.Config(app,log_level='error',access_log=False))
        serving=asyncio.create_task(server.serve(sockets=[tcp]))
        async def bootstrap(client,binding):
            await client.bootstrap_command(binding,p.CommandType.AUDIO_AVAILABILITY,audioAvailable=True)
        client=V2STTSession(V2TransportConfig(url=f'ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2',backoff_initial=.02),bootstrap=bootstrap)
        mirror=V2MirrorConnection(client)
        controls=V2ControlService(client,mirror,audio_ready=lambda: True)
        config=AppConfig(); config.history.persistent=HistoryPersistentConfig(enabled=True,store_all=True,retention_days=0,max_entries=0)
        config.text_injection.paste_delay_ms=config.clipboard.restore_delay_ms=0
        config.clipboard.restore_previous=True
        history=TranscriptHistoryManager(config.history,str(Path(data)/'client.sqlite'))
        backend=ClipboardAdapter(history); queue=TextInjectionQueue(config,history,backend)
        mirror.on_reduction=reductions.append
        results=V2ResultService(history,queue,mirror)
        def published(outcome):
            outcomes.append(outcome)
            trace.append(dict(status=outcome.status,sessionId=outcome.final.session_id,
                activationId=outcome.final.activation_id,segmentId=outcome.final.segment_id,
                segmentSequence=outcome.final.segment_sequence,eventId=outcome.final.event_id,
                eventSeq=outcome.final.event_seq,foreground=mirror.mirror.view.input.activation_id))
        results.on_result=published
        queue.start(); running=None
        try:
            await until(lambda: server.started or serving.done())
            running=asyncio.create_task(client.run())
            await until(lambda: client.is_ready and not mirror.mirror.view.snapshot_pending)
            check('admission/pinned_server',client.binding.accepted.payload['serverCommit']==SERVER_SHA)
            domain=service.sessions.get(client.binding.session_id)
            async def settled():
                await until(lambda: client.is_ready and not mirror.mirror.view.snapshot_pending)
            async def activate():
                await settled(); command=await controls.press('primary')
                await until(lambda: mirror.mirror.view.input.activation_id==command.ack.activationId)
                await settled(); return command.ack.activationId
            async def record():
                previous=set(mirror.mirror.view.segments)
                await client.send_audio(b'\0\x40'*640,16000,frames=640)
                await until(lambda: bool(set(mirror.mirror.view.segments)-previous))
                sid=next(iter(set(mirror.mirror.view.segments)-previous))
                return sid
            async def end_recording():
                before=len(service.scheduler.jobs)
                domain.recorder.flush_buffered_audio()
                await until(lambda: len(service.scheduler.jobs)>before)
                await until(lambda: mirror.mirror.view.input.phase==p.InputPhase.FOLLOWUP_WAIT)
                await settled()
                return service.scheduler.jobs[-1]

            aid=await activate(); sid=await record()
            domain._on_realtime_text('synthetic preview only')
            await until(lambda: mirror.mirror.view.segments[sid].preview is not None)
            check('interim/no_sqlite_or_clipboard',not history.get_memory_entries() and not backend.writes and not backend.pastes)
            job_a=await end_recording()
            await controls.control('finish')
            await until(lambda: mirror.mirror.view.input.phase==p.InputPhase.IDLE)
            bid=await activate(); sid_b=await record()
            check('delayed_A/no_output_before_model_result',not outcomes and not backend.pastes)
            service.scheduler.complete(job_a,text='same synthetic final')
            await until(lambda: len([o for o in outcomes if o.status=='queued'])==1)
            check('old_A_while_B/recording_ongoing',mirror.mirror.view.input.phase==p.InputPhase.SEGMENT_ACTIVE)
            job_b=await end_recording()
            service.scheduler.complete(job_b,text='same synthetic final')
            await until(lambda: len([o for o in outcomes if o.status=='queued'])==2)
            await until(lambda: len(backend.pastes)==2 and not history._reservations)
            entries=history.get_persistent_entries()
            check('old_A_while_B/foreground_unchanged',mirror.mirror.view.input.activation_id==bid and trace[0]['foreground']==bid)
            check('old_A_while_B/uuid_origin',entries[0].activation_id==aid and entries[0].segment_id==sid and entries[0].session_id==client.binding.session_id)
            check('identical_texts/distinct_segments',entries[1].activation_id==bid and entries[1].segment_id==sid_b and len(entries)==2)
            check('ordering/server_publication_and_segment_sequence',[e.segment_sequence for e in entries]==[1,2] and entries[0].event_seq<entries[1].event_seq)
            check('reservation/durable_before_paste',all(backend.pending_before_paste))
            check('attempts/one_completed_automatic_per_segment',all(len(e.attempts)==1 and e.attempts[0].source=='automatic' and e.attempts[0].status=='command_sent' for e in entries))
            final_reduction=next(r for r in reductions if r.finals)
            results.consume(final_reduction)
            check('replay/no_repeat_paste',len(backend.pastes)==2)
            await settled(); await controls.control('cancel')
            await until(lambda: mirror.mirror.view.input.phase==p.InputPhase.IDLE)
            check('cancel/published_history_preserved',history.get_persistent_entries()==entries)

            cid=await activate(); sid_c=await record(); job_c=await end_recording()
            service.scheduler.complete(job_c,text='   ')
            await until(lambda: mirror.mirror.view.segments[sid_c].status=='discarded')
            check('empty_final/discard_no_output',len(backend.pastes)==2 and len(history.get_persistent_entries())==2)
            await settled(); await controls.control('finish')
            await until(lambda: mirror.mirror.view.input.phase==p.InputPhase.IDLE)
            old=client.binding
            await client.reconnect(old,'synthetic_results_recovery')
            await until(lambda: client.binding is not None and client.binding is not old and client.is_ready)
            await settled()
            check('reconnect/history_retained',history.get_persistent_entries()==entries)
            check('reconnect/stale_reduction_rejected',results.consume(final_reduction)==())
            check('reinsert/manual_request',TranscriptReinsertionService(history,queue).reinsert_entry(entries[0].id).status.value=='queued')
            await until(lambda: len(backend.pastes)==3 and not history._reservations)
            after=history.get_persistent_entries()
            check('reinsert/separate_manual_attempt',[a.source for a in after[0].attempts]==['automatic','manual'])
            check('clipboard/restore_preserved',backend.clipboard=='synthetic prior clipboard')
            results.close(); await controls.close(); await mirror.close()
            await asyncio.gather(running,return_exceptions=True)
            queue.stop(2)
            check('shutdown/no_pending_jobs_tasks',not history._reservations and not queue.is_running() and running.done())
            return dict(result='PASS',serverCommit=SERVER_SHA,clientHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                checks=checks,checkCount=len(checks),sourceHashes=verify_sources(root,repository),resultTrace=trace,
                runtime=dict(python=sys.version,executable=sys.executable,platform=platform.platform()),
                boundaries='Production server app/route/domain/ledger through real TCP/WebSocket and actual V2STTSession/V2MirrorConnection/V2ControlService/V2ResultService/SQLite/TextInjectionQueue. Pinned GateAwareRecorder/ManualScheduler replace hardware/VAD/ASR; ClipboardAdapter replaces Windows clipboard/SendInput only. Named settings/audio bootstrap; full app composition AP100 and real hardware ASR/focus AP-IV2-020 remain open.')
        finally:
            results.close(); await controls.close(); await mirror.close()
            if running: await asyncio.gather(running,return_exceptions=True)
            queue.stop(2)
            server.should_exit=True
            try: await asyncio.wait_for(serving,10)
            finally: tcp.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-root',required=True,type=Path)
    parser.add_argument('--server-repository',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(asyncio.run(run(args.server_root.resolve(),args.server_repository.resolve())),indent=2))
