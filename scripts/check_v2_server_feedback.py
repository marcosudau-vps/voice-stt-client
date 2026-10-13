"""AP090 actual pinned domain/log sockets -> mirror/engine -> Qt output ports.

Recorder/VAD/ASR and sound/LED perception are explicit controlled boundaries;
actual widgets, transport, logs, Controls, mirror and feedback run unchanged.
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
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_v2_server_transport import SERVER_SHA, verify_sources
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.config import AppConfig, ServerConfig, EventStreamConfig, OverlayConfig
from voice_stt_client.core.event_models import EventConnectionState
from voice_stt_client.core.event_protocol import EventProtocolProcessor
from voice_stt_client.core.event_stream import EventStreamTransport
from voice_stt_client.core.feedback_reducer import FeedbackEngine
from voice_stt_client.core.session_coordinator import DualSessionCoordinator
from voice_stt_client.core.v2_controls import V2ControlService
from voice_stt_client.core.v2_feedback import V2FeedbackConnection
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from voice_stt_client.ui.feedback import V2FeedbackOutput
from voice_stt_client.ui.overlay import TranscriptOverlay
from voice_stt_client.ui.tray import TrayController


async def run(root, repository):
    sys.path.insert(0, str(root))
    import uvicorn
    from PySide6.QtWidgets import QApplication
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import ManualScheduler
    qt = QApplication.instance() or QApplication([])
    verify_sources(root, repository)
    checks, trace, decisions, log_events, log_controls = [], [], [], [], []
    sounds, leds, failures = [], [], []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)
    async def until(predicate, timeout=10):
        async def wait():
            while True:
                qt.processEvents()
                if predicate():
                    return
                await asyncio.sleep(.01)
        await asyncio.wait_for(wait(), timeout)

    with tempfile.TemporaryDirectory(prefix='cv2-090-server-') as data, patch.dict(os.environ, {'VOICESTT_SERVER_COMMIT': SERVER_SHA}):
        settings = ServerSettings(data_root_path=data, model_warmup=False, request_logging_enabled=False,
            performance_logging_enabled=False, performance_log_mirror_enabled=False,
            transcription_logging_enabled=True, system_event_logging_enabled=False,
            event_store_enabled=True, log_live_enabled=True)
        app = create_app(settings, recorder_factory=GateAwareRecorder, scheduler_factory=ManualScheduler)
        service = app.state.voicestt_service
        tcp = socket.socket(); tcp.bind(('127.0.0.1', 0)); tcp.listen(16)
        url = f'ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2'
        server = uvicorn.Server(uvicorn.Config(app, log_level='error', access_log=False))
        serving = asyncio.create_task(server.serve(sockets=[tcp]))
        config = AppConfig.load()
        engine = FeedbackEngine(config.feedback_mappings)
        logs = DualSessionCoordinator(ServerConfig(url=url), EventStreamConfig(cursor_persistence_enabled=False))
        async def bootstrap(client, binding):
            await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=True)
            await logs.begin_generation(binding.generation)
            await logs.adopt_hello(binding.generation, binding.accepted.to_mapping())
        client = V2STTSession(V2TransportConfig(url=url, backoff_initial=.02), bootstrap=bootstrap)
        mirror = V2MirrorConnection(client)
        reductions = []; mirror.on_reduction = reductions.append
        controls = V2ControlService(client, mirror, audio_ready=lambda: True)
        port = V2FeedbackConnection(mirror, engine)
        overlay = TranscriptOverlay(OverlayConfig())
        tray = TrayController(on_toggle=lambda: None, on_reinsert_last=lambda: None, on_reinsert_entry=lambda x: None,
            on_request_history=lambda: None, on_quit=lambda: None)
        output = V2FeedbackOutput(tray=tray, overlay=overlay, sound=SimpleNamespace(play=sounds.append),
            led=SimpleNamespace(submit=lambda calls, **kw: leds.append((calls, kw))))
        output.failure.connect(failures.append)
        def publish(decision):
            decisions.append(decision)
            s = decision.snapshot
            trace.append(dict(sessionId=s.session_id,generation=s.generation,phase=s.phase.value,
                foreground=s.activation_id,pending=s.pending_count,eventId=decision.event.event_id if decision.event else None,
                eventType=decision.event.event_type.value if decision.event else None,
                segmentId=decision.event.details.get('segmentId') if decision.event else None,
                sound=decision.rule.sound.cue.value if decision.rule.sound else None))
            output.decision_received.emit(decision)
        port.on_decision = publish
        async def logged(context, result):
            log_events.append(result)
            check_count_before = len(sounds)
            assert engine.handle_event_stream(result,generation=context.generation,session_id=context.session_id) is None
            assert len(sounds) == check_count_before
            return True
        logs.on_event = logged
        def log_status(context):
            decision = engine.update_connection(context.event_state, stt_ready=client.is_ready,
                generation=context.generation,session_id=context.session_id)
            if decision.publish:
                publish(decision)
        logs.on_context_change = log_status
        running = replay_task = replay = None
        try:
            await until(lambda: server.started or serving.done())
            running = asyncio.create_task(client.run())
            await until(lambda: client.is_ready and not mirror.mirror.view.snapshot_pending)
            await until(lambda: logs.context.event_state == EventConnectionState.LIVE)
            check('admission/pinned_domain_and_actual_logs',client.binding.accepted.payload['serverCommit']==SERVER_SHA)
            domain = service.sessions.get(client.binding.session_id)
            async def settled():
                await until(lambda: client.is_ready and not mirror.mirror.view.snapshot_pending)
            async def activate():
                await settled()
                reply = await controls.press('primary')
                await until(lambda: mirror.mirror.view.input.activation_id == reply.ack.activationId)
                await settled()
                return reply.ack.activationId
            async def record():
                previous = set(mirror.mirror.view.segments)
                await client.send_audio(b'\0\x40'*640,16000,frames=640)
                await until(lambda: bool(set(mirror.mirror.view.segments)-previous))
                return next(iter(set(mirror.mirror.view.segments)-previous))
            async def end_recording():
                before=len(service.scheduler.jobs)
                domain.recorder.flush_buffered_audio()
                await until(lambda: len(service.scheduler.jobs)>before)
                await until(lambda: mirror.mirror.view.input.phase==p.InputPhase.FOLLOWUP_WAIT)
                await settled()
                return service.scheduler.jobs[-1]
            aid=await activate(); sid=await record()
            domain._on_realtime_text('synthetic A preview')
            await until(lambda: overlay.label.text()=='synthetic A preview')
            check('interim/actual_segment_overlay',overlay._v2_snapshot.previews[0].segment_id==sid)
            job_a=await end_recording()
            await controls.control('finish')
            await until(lambda: mirror.mirror.view.input.phase==p.InputPhase.IDLE)
            await until(lambda: tray.status_action.text()=='Bereit')
            check('idle/drain_is_ready',engine._v2_snapshot.pending_count==1 and engine._v2_snapshot.manual_available)
            bid=await activate(); sid_b=await record()
            domain._on_realtime_text('synthetic B preview')
            await until(lambda: overlay.label.text()=='synthetic B preview')
            service.scheduler.complete(job_a,text='synthetic A final')
            await until(lambda: any(s.cue.value=='complete' for s in sounds))
            await until(lambda: any(r.event.event=='transcription.completed' for r in log_events))
            check('old_A/foreground_B_recording',tray.status_action.text()=='Sprache wird aufgenommen' and engine._v2_snapshot.activation_id==bid)
            check('old_A/B_preview_survives',overlay.label.text()=='synthetic B preview')
            check('old_A/exact_one_complete_sound',sum(s.cue.value=='complete' for s in sounds)==1)
            check('old_A/terminal_led_is_pulse_only',all(c.is_event for d in decisions if d.event and d.event.event_type.value=='server.transcription.completed' for c in d.rule.led))
            final_reduction=next(r for r in reductions if r.finals)
            before=len(sounds)
            for decision in engine.handle_reduction(final_reduction): output.decision_received.emit(decision)
            qt.processEvents()
            check('duplicate/reduction_no_sound',len(sounds)==before)
            access=logs.context.log_access
            replay_events=[]
            async def replayed(result):
                replay_events.append(result)
                assert engine.handle_event_stream(result,generation=client.binding.generation,session_id=client.binding.session_id) is None
                return True
            replay=EventStreamTransport(EventStreamConfig(cursor_persistence_enabled=False),access,
                EventProtocolProcessor(access),on_event=replayed,on_control=log_controls.append)
            replay_task=asyncio.create_task(replay.run())
            await until(lambda: replay.state==EventConnectionState.LIVE)
            check('logs/actual_final_replay',any(r.event.event=='transcription.completed' and r.origin.value=='replay' for r in replay_events))
            check('logs/replay_no_second_sound_or_phase',len(sounds)==before and engine._v2_snapshot.phase==p.InputPhase.SEGMENT_ACTIVE)
            # Log segmentId is an opaque recording label even when its bytes
            # happen to match a domain ID. It never mutates mirror identity.
            check('logs/opaque_recording_label_has_no_domain_authority',
                engine._v2_snapshot.activation_id==bid and
                overlay._v2_snapshot.previews[0].segment_id==sid_b)
            await replay.stop(); await replay_task
            # Exceptions in both controlled physical sinks must not interrupt
            # the genuine command/event stream, or another result cue.
            def failed(*args,**kw): raise RuntimeError('synthetic adapter failure')
            output.sound=SimpleNamespace(play=failed); output.led=SimpleNamespace(submit=failed)
            job_b=await end_recording()
            service.scheduler.complete(job_b,text='synthetic B final')
            await until(lambda: mirror.mirror.view.segments[sid_b].status=='completed')
            await until(lambda: 'sound_failed' in failures and 'led_unavailable' in failures)
            check('adapters/both_failures_isolated',client.is_ready)
            await controls.control('finish')
            await until(lambda: mirror.mirror.view.input.phase==p.InputPhase.IDLE)
            check('adapters/controls_still_operate',client.is_ready)
            old=client.binding
            await client.reconnect(old,'synthetic_feedback_recovery')
            await until(lambda: client.binding is not None and client.binding is not old and client.is_ready)
            await settled()
            await until(lambda: logs.context.event_state==EventConnectionState.LIVE)
            await until(lambda: output._identity==(client.binding.generation,client.binding.session_id))
            check('reconnect/new_session_no_preview',not overlay._v2_snapshot.previews and overlay.label.text()=='')
            check('reconnect/old_reduction_rejected',engine.handle_reduction(final_reduction)==())
            check('reconnect/no_final_replay_impulse',sum(t['sound']=='complete' for t in trace)==2)
            check('logtoken/redacted_context',access.access_token not in repr(logs.context))
            port.close(); output.close()
            await logs.shutdown(); await controls.close(); await mirror.close()
            await asyncio.gather(running,return_exceptions=True)
            check('shutdown/domain_logs_and_output_closed',running.done() and logs.active_transport_count==0 and output._closed)
            return dict(result='PASS',checks=checks,checkCount=len(checks),serverCommit=SERVER_SHA,
                clientHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                sourceHashes=verify_sources(root,repository),decisionTrace=trace,
                runtime=dict(python=sys.version,executable=sys.executable,platform=platform.platform(),qt=os.environ.get('QT_QPA_PLATFORM')),
                boundaries='Actual production FastAPI app, SQLite event store and two TCP WebSockets through V2STTSession/V2MirrorConnection/V2ControlService/DualSessionCoordinator/EventStreamTransport/FeedbackEngine/V2FeedbackConnection/queued V2FeedbackOutput/real Qt tray and overlay. GateAwareRecorder/ManualScheduler replace VAD/ASR, deterministic PCM replaces microphone, sound/LED controlled sinks replace physical perception. Explicit audioavailability/default settings bootstrap; complete app composition AP100, physical feedback and ASR IV2-020 remain open.')
        finally:
            port.close(); output.close(); overlay.close(); tray.tray.hide()
            if replay: await replay.stop()
            if replay_task: await asyncio.gather(replay_task,return_exceptions=True)
            await logs.shutdown(); await controls.close(); await mirror.close()
            if running: await asyncio.gather(running,return_exceptions=True)
            server.should_exit=True
            try: await asyncio.wait_for(serving,10)
            finally: tcp.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-root',required=True,type=Path)
    parser.add_argument('--server-repository',required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(asyncio.run(run(args.server_root.resolve(),args.server_repository.resolve())),indent=2))
