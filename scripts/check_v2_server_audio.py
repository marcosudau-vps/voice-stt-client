"""AP040 production capture/codec/media/WS/log contract at pinned ada13b0.

Only PortAudio hardware and recorder/model/scheduler boundaries are controlled.
No live service, private audio, real ASR, or server product change is involved.
"""

import argparse
import asyncio
from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import platform
import socket
import subprocess
import sys
import tempfile
import threading
from unittest.mock import patch

CLIENT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CLIENT_ROOT))
from scripts.check_v2_server_transport import SERVER_SHA, verify_sources, until
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.audio_capture import AudioCapture
from voice_stt_client.core.config import AudioConfig, ServerConfig, EventStreamConfig
from voice_stt_client.core.event_cursor_store import EventCursorStore
from voice_stt_client.core.event_models import EventConnectionState
from voice_stt_client.core.event_protocol import EventProtocolProcessor, EventProtocolIssue
from voice_stt_client.core.event_stream import EventStreamTransport
from voice_stt_client.core.session_coordinator import DualSessionCoordinator
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_media import V2MediaConnection


async def run(root, repository):
    sys.path.insert(0, str(root))
    import numpy as np
    import uvicorn
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import ManualScheduler
    from websockets.asyncio.client import connect
    from websockets.exceptions import ConnectionClosed

    verify_sources(root, repository)
    checks, measurements, observations = [], [], []
    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    class Recorder(GateAwareRecorder):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.received = []

        def feed_audio(self, samples, original_sample_rate=16000):
            # Aggregate identity/format, no retained raw audio.
            self.received.append((len(samples), original_sample_rate))
            super().feed_audio(samples, original_sample_rate)

        def abort(self):
            # GateAwareRecorder's single final_text FIFO inserts an empty item
            # on abort: that would wake the older, held model job, attributing
            # B's cancel to A. Model the production boundary's independent
            # background result instead; no mutation of server product code.
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
                    text="" if aborted else self.transcription_executor.transcribe(np.ones(32,dtype=np.float32),language="en",use_prompt=True).text
                except RuntimeError:
                    text=""
                self.final_text.put((text,context))
            threading.Thread(target=final,daemon=True).start()
            return True

        def text(self):
            item=self.final_text.get()
            if item is None: return ""
            text,context=item
            # This model boundary returns the immutable job provenance with
            # its delayed result, rather than GateAwareRecorder's shared FIFO
            # context. The production text worker/ledger/publication is real.
            with self.owner.lock:
                self.owner._active_text_context=context
            return text

    class Stream:
        def __init__(self, **kwargs):
            self.active = True
        def start(self): pass
        def stop(self): self.active = False
        def close(self): pass

    with tempfile.TemporaryDirectory(prefix="cv2-040-server-") as data, patch.dict(os.environ, {"VOICESTT_SERVER_COMMIT":SERVER_SHA}), patch(
            "sounddevice.query_devices", return_value={"name":"deterministic PCM", "default_samplerate":48000}), patch(
            "sounddevice.check_input_settings"), patch("sounddevice.InputStream",Stream):
        settings = ServerSettings(data_root_path=data, model_warmup=False, admin_api_key="synthetic-harness-admin",
                                  request_logging_enabled=False, performance_logging_enabled=False,
                                  performance_log_mirror_enabled=False, transcription_logging_enabled=False,
                                  system_event_logging_enabled=False, event_store_enabled=True, log_live_enabled=True)
        app = create_app(settings, recorder_factory=Recorder, scheduler_factory=ManualScheduler)
        tcp = socket.socket(); tcp.bind(("127.0.0.1",0)); tcp.listen(16)
        url = f"ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2"
        server = uvicorn.Server(uvicorn.Config(app,log_level="error",access_log=False))
        serving = asyncio.create_task(server.serve(sockets=[tcp]))
        service = app.state.voicestt_service
        clients, tasks, log_transports, log_tasks = [], [], [], []
        try:
            await until(lambda:server.started or serving.done())
            if serving.done():
                await serving
                raise AssertionError("server startup failed")

            async def start(manual=True,wake=False):
                session = V2STTSession(V2TransportConfig(url=url,manual=manual,wake_word=wake,
                                      wake_word_ids=("hey_jarvis",) if wake else (), backoff_initial=.05))
                mirror = V2MirrorConnection(session)
                reductions=[]; mirror.on_reduction=reductions.append
                config = AudioConfig()
                capture = AudioCapture(config)
                logs = DualSessionCoordinator(ServerConfig(url=url),EventStreamConfig(cursor_path=str(Path(data)/"client-cursor.json")))
                async def observe(context,result):
                    observations.append((context.session_id,result.event.cursor,result.origin.value,result.event.event))
                    return True
                logs.on_event=observe
                media=V2MediaConnection(session,capture,logs=logs,recovery_interval=.02)
                clients.append((media,mirror)); tasks.append(asyncio.create_task(session.run()))
                await until(lambda:session.is_ready or session.status.state.value=="blocked")
                check(f"admission/{manual}/{wake}",session.is_ready)
                await until(lambda:media._gate and not mirror.mirror.view.snapshot_pending)
                domain=service.sessions.get(session.binding.session_id)
                domain.recorder.owner=domain
                return media,mirror,reductions,config,domain

            def feed(media,config):
                frames=media.capture.sample_rate//25
                media.capture._audio_callback(np.full((frames,config.channels),10000,dtype=np.int16),frames,None,None)

            media,mirror,reductions,config,domain=await start()
            binding=media.session.binding; recorder=domain.recorder
            check("capture/no_pre_ready_frames",not recorder.received)
            feed(media,config)
            await until(lambda:len(recorder.received)==1)
            check("audio/idle_received_no_local_gate",recorder.received[-1]==(640,16000) and not recorder.is_recording)
            await until(lambda:media.logs.context.event_state==EventConnectionState.LIVE)
            access=media.logs.context.log_access
            check("logs/bootstrap_session_and_channels",access.session_id==binding.session_id and set(access.channels)=={"audit","transcription","performance"})
            check("logs/memory_only_redacted",access.access_token not in repr(media.logs.context) and access.access_token not in access.endpoint)

            first=await media.session.request(p.CommandType.ACTIVATION,action="activate",source="manual")
            await until(lambda:not mirror.mirror.view.snapshot_pending)
            feed(media,config)
            await until(lambda:bool(mirror.mirror.view.segments))
            segment=next(iter(mirror.mirror.view.segments.values()))
            check("audio/waiting_to_recording",mirror.mirror.view.input.phase==p.InputPhase.SEGMENT_ACTIVE)
            domain._on_realtime_text("synthetic audio preview")
            await until(lambda:mirror.mirror.view.segments[segment.segment_id].preview is not None)
            await media.session.request(p.CommandType.ACTIVATION,action="finish",activationId=first.ack.activationId)
            await until(lambda:mirror.mirror.view.input.phase==p.InputPhase.IDLE and not mirror.mirror.view.snapshot_pending)
            await until(lambda:any(job.kind=="final" for job in service.scheduler.jobs))
            check("background/older_activation_draining",mirror.mirror.view.activations[first.ack.activationId].status=="draining")
            count=len(recorder.received); feed(media,config)
            await until(lambda:len(recorder.received)>count)
            check("audio/draining_idle_still_received",not recorder.is_recording)
            second=await media.session.request(p.CommandType.ACTIVATION,action="activate",source="manual")
            await until(lambda:not mirror.mirror.view.snapshot_pending)
            feed(media,config)
            await until(lambda:len(mirror.mirror.view.segments)==2)
            media.set_led_available(False)
            await asyncio.sleep(.05)
            check("devices/led_only_preserves_foreground",mirror.mirror.view.input.activation_id==second.ack.activationId and media.audio_available)
            old_callback=media.capture.on_audio_packet
            stopped, release_stop = threading.Event(), threading.Event()
            original_stop = media.capture.stop
            def blocked_stop():
                stopped.set()
                release_stop.wait(5)
                original_stop()
            media.capture.stop = blocked_stop
            try:
                media.set_device_available(False)
                old_callback(b"\x10\0"*640,16000,1,640)
                await until(stopped.is_set)
                await until(lambda:mirror.mirror.view.input.phase==p.InputPhase.IDLE and not mirror.mirror.view.audio_available,timeout=2)
                check("devices/false_acked_before_blocked_native_stop",not release_stop.is_set() and
                      media._reported_available==(binding,False) and media.capture.is_running)
                check("devices/open_activation_cancelled",mirror.mirror.view.activations[second.ack.activationId].input_closed and
                      mirror.mirror.view.activations[second.ack.activationId].close_reason in ("cancelled", "audio_unavailable"))
                check("devices/session_and_older_drain_preserved",media.session.binding is binding and mirror.mirror.view.activations[first.ack.activationId].status=="draining")
                count=len(recorder.received); feed(media,config); await asyncio.sleep(.05)
                check("devices/lost_input_sends_no_pcm",len(recorder.received)==count)
                for job in list(service.scheduler.jobs):
                    if job.kind=="final" and job.session_id==binding.session_id:
                        service.scheduler.complete(job,text="synthetic delayed final")
                await until(lambda:any(r.finals for r in reductions))
                check("background/older_final_while_native_stop_blocked",not release_stop.is_set() and
                      len([f for r in reductions for f in r.finals])==1)
            finally:
                release_stop.set()
                media.capture.stop = original_stop
            await until(lambda:media._capture_operation is None)
            config.sample_rate=48000; config.channels=2
            media.set_device_available(True)
            await until(lambda:media._gate and mirror.mirror.view.audio_available)
            feed(media,config); await until(lambda:len(recorder.received)>count)
            check("devices/rebound_48k_stereo_resampled_at_server",recorder.received[-1]==(640,16000))
            check("devices/rebind_no_auto_activation",mirror.mirror.view.input.phase==p.InputPhase.IDLE)
            for job in list(service.scheduler.jobs):
                if job.kind=="final" and job.session_id==binding.session_id:
                    service.scheduler.complete(job,text="synthetic delayed final")
            await until(lambda:any(r.finals for r in reductions))
            check("background/older_final_after_device_cancel",len([f for r in reductions for f in r.finals])==1 and mirror.mirror.view.segments[segment.segment_id].text is not None)

            # Session-filtered global cursor jumps, genuine SQLite-first replay.
            service.events.emit("audit","synthetic.own.one",sessionId=binding.session_id)
            service.events.emit("audit","synthetic.foreign",sessionId="foreign-session")
            service.events.emit("audit","synthetic.own.two",sessionId=binding.session_id)
            await until(lambda:any(x[3]=="synthetic.own.two" for x in observations))
            own=[x[1] for x in observations if x[3].startswith("synthetic.own.")]
            check("logs/filtered_cursor_jump",len(own)==2 and own[1]>own[0]+1)
            check("logs/no_foreign_session",all(x[0]==binding.session_id for x in observations))
            view_before=mirror.mirror.view; final_count=sum(len(r.finals) for r in reductions)
            replay,controls=[],[]
            async def accept(result): replay.append(result); return True
            replay_transport=EventStreamTransport(EventStreamConfig(cursor_persistence_enabled=False),access,
                    EventProtocolProcessor(access),on_event=accept,on_control=controls.append)
            log_transports.append(replay_transport); log_tasks.append(asyncio.create_task(replay_transport.run()))
            await until(lambda:replay_transport.state==EventConnectionState.LIVE)
            check("logs/actual_hello_subscribe_replay_completed",all(any(x.kind.value==kind for x in controls) for kind in ("hello","subscribed","replay_completed")))
            check("logs/replay_no_domain_effect",mirror.mirror.view==view_before and sum(len(r.finals) for r in reductions)==final_count)
            check("logs/opaque_segment_metadata_not_domain_uuid",any(x.event.segment_id is not None for x in replay) and
                  mirror.mirror.view==view_before)
            await replay_transport.stop()

            # Isolated synthetic SQLite timestamp advance; production pruning
            # and filtered watermark computation are unchanged.
            service.events.emit("audit","synthetic.retained.lost",sessionId=binding.session_id)
            store=service.events._store
            with store._lock:
                store._connection.execute("UPDATE events SET timestamp='2000-01-01T00:00:00.000Z' WHERE event_name='synthetic.retained.lost'")
                store._connection.commit()
                store.set_retention({"audit":1})
                store._prune_if_due()
            service.events.emit("audit","synthetic.retained.survivor",sessionId=binding.session_id)
            replay.clear(); controls.clear()
            retention=EventStreamTransport(EventStreamConfig(cursor_persistence_enabled=False),access,
                    EventProtocolProcessor(access),on_event=accept,on_control=controls.append)
            log_transports.append(retention); log_tasks.append(asyncio.create_task(retention.run()))
            await until(lambda:retention.state==EventConnectionState.LIVE)
            check("logs/real_retention_gap",any(x.issue==EventProtocolIssue.RETENTION_GAP for x in controls))
            check("logs/retention_survivors_delivered",any(x.event.event=="synthetic.retained.survivor" for x in replay))
            await retention.stop()

            async def error_probe(name,probe_access,processor=None):
                failed=EventStreamTransport(EventStreamConfig(reconnect_min_delay=.05),probe_access,
                                           processor or EventProtocolProcessor(probe_access),on_event=accept,on_control=controls.append)
                log_transports.append(failed); log_tasks.append(asyncio.create_task(failed.run()))
                await until(lambda:failed.state==EventConnectionState.UNAVAILABLE if name!="store_unavailable" else failed.last_error is not None)
                if name=="store_unavailable":
                    check("logs/"+name,failed.last_error==name or "1011" in failed.last_error)
                else:
                    check("logs/"+name,failed.last_error==name)
                check("logs/"+name+"_domain_ready",media.session.is_ready and media.session.binding is binding)
                await failed.stop()

            await error_probe("authorization",replace(access,access_token="synthetic-invalid-token"))
            ahead_store=EventCursorStore(Path(data)/"ahead.json")
            ahead_store.commit(service.events.latest_cursor()+100,endpoint=access.endpoint,server_instance_id=access.server_instance_id,
                               protocol_version=2,session_id=access.session_id,channels=access.channels)
            await error_probe("cursor_ahead",access,EventProtocolProcessor(access,cursor_store=ahead_store))
            with patch.object(service.events,"store_available",return_value=False):
                await error_probe("store_unavailable",access)
            count=len(recorder.received); feed(media,config); await until(lambda:len(recorder.received)>count)
            check("logs/faults_audio_continues",media._gate)
            check("logs/replay_keeps_published_final",sum(len(r.finals) for r in reductions)==final_count)

            # Network loss: real socket recycle, old audio discarded, new ID.
            await media.session.request(p.CommandType.SUPPRESSION,manual=True,wakeWord=True)
            await media.session.reconnect(binding,"synthetic_network_loss")
            await until(lambda:media.session.binding is not None and media.session.binding is not binding and media._gate)
            new=media.session.binding
            check("reconnect/new_session_and_generation",new.session_id!=binding.session_id and new.generation>binding.generation)
            old_callback(b"\x10\0"*640,16000,1,640)
            check("reconnect/empty_old_queue",media.queue.duration_ms==0)
            check("reconnect/desired_suppression_retained",media.session._desired_suppression==(True,True))
            await until(lambda:media.logs.context.session_id==new.session_id and media.logs.context.log_access is not None)
            check("reconnect/new_log_token",media.logs.context.log_access.access_token!=access.access_token)
            measurements.append(media.counters())
            await until(lambda:media.logs.context.event_state==EventConnectionState.LIVE)
            log_transport=media.logs._transport
            log_task,expiry_task=media.logs._transport_task,media.logs._expiry_task
            entered_close,release_close=threading.Event(),threading.Event()
            original_stop=media.capture.stop
            def blocked_shutdown_stop():
                entered_close.set()
                release_close.wait(5)
                original_stop()
            media.capture.stop=blocked_shutdown_stop
            media.shutdown_timeout=.1
            try:
                try:
                    await media.close()
                except TimeoutError:
                    check("shutdown/native_stop_timeout_reported",entered_close.is_set() and not release_close.is_set())
                else:
                    raise AssertionError("native shutdown timeout missing")
                check("shutdown/native_timeout_real_logs_clean",media.logs.active_transport_count==0 and
                      log_task.done() and expiry_task.done() and log_transport.state==EventConnectionState.STOPPED)
            finally:
                release_close.set()
                media.capture.stop=original_stop
                media.shutdown_timeout=3
            await media.close(); await mirror.close()
            check("shutdown/retry_joins_native_stop",media._capture_operation is None and media._cleanup_complete)
            check("shutdown/media_tasks_and_queue_clean",media._task is None and media._sender is None and not media.capture.is_running and media.queue.duration_ms==0)

            for manual,wake in ((False,True),(True,True)):
                # Model-free boundary, same as pinned wake_catalog_support:
                # real manifest/resolver, no ONNX/TFLite engine loaded.
                service.wakeword_catalog.set_artifact_prober(lambda path:None)
                entered,release=asyncio.Event(),asyncio.Event()
                original_sender=V2MediaConnection._send
                async def held_sender(instance):
                    try:
                        await original_sender(instance)
                    finally:
                        entered.set()
                        await release.wait()
                if not manual:
                    with patch.object(V2MediaConnection,"_send",held_sender):
                        media,mirror,rs,config,domain=await start(manual,wake)
                else:
                    media,mirror,rs,config,domain=await start(manual,wake)
                feed(media,config); await until(lambda:bool(domain.recorder.received))
                check(f"audio/idle_trigger_mode/{manual}/{wake}",domain.recorder.received[-1]==(640,16000))
                await media.session.request(p.CommandType.SUPPRESSION,manual=True,wakeWord=True)
                count=len(domain.recorder.received); feed(media,config)
                await until(lambda:len(domain.recorder.received)>count)
                check(f"audio/wakepause_trigger_mode/{manual}/{wake}",not domain.recorder.is_recording)
                await until(lambda:media.logs.context.event_state==EventConnectionState.LIVE)
                log_transport=media.logs._transport
                log_task,expiry_task=media.logs._transport_task,media.logs._expiry_task
                stopped=asyncio.Event()
                original_session_stop=media.session.stop
                async def stop_session():
                    await original_session_stop()
                    stopped.set()
                media.session.stop=stop_session
                if manual:
                    original_log_stop=log_transport.stop
                    async def held_log_stop():
                        entered.set()
                        await release.wait()
                        await original_log_stop()
                    log_transport.stop=held_log_stop
                case="logclose_cancel" if manual else "task_join_cancel"
                closing=asyncio.create_task(media.close())
                try:
                    await asyncio.wait_for(stopped.wait(),3)
                    await asyncio.wait_for(entered.wait(),3)
                    closing.cancel()
                    if manual:
                        await asyncio.sleep(0)
                        closing.cancel()
                    release.set()
                    try:
                        await asyncio.wait_for(closing,3)
                    except asyncio.CancelledError:
                        check("shutdown/"+case+"_reported",not media._cleanup_complete)
                    else:
                        raise AssertionError(case+" was hidden")
                    check("shutdown/"+case+"_real_logs_clean",media.logs.active_transport_count==0 and
                          log_task.done() and expiry_task.done() and log_transport.state==EventConnectionState.STOPPED)
                finally:
                    release.set()
                    await asyncio.gather(closing,return_exceptions=True)
                    await media.close(); await mirror.close()
                check("shutdown/"+case+"_retry_complete",media._cleanup_complete and
                      media._task is None and media._sender is None and media._log_shutdown_task.done() and not media.capture.is_running)
            hashes=verify_sources(root,repository)
            return {"result":"PASS","serverCommit":SERVER_SHA,"clientHead":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
                    "runtime":{"python":sys.version,"executable":sys.executable,"platform":platform.platform(),"uvicorn":uvicorn.__version__},
                    "sourceHashes":hashes,"checks":checks,"checkCount":len(checks),"audioCounters":measurements,
                    "boundaries":"Real AudioCapture callback/process thread -> bounded V2MediaConnection -> actual V2STTSession TCP/WS -> production FastAPI PCM decoder/resampler/gate/controller/ledger. Real SQLite/log WS/subscribe/filter/replay/pruning/auth routes. PortAudio device substituted; GateAwareRecorder extended with immutable final-job context handoff and held ManualScheduler substitute models; catalog engine probe replaced by permissive model-free probe; isolated synthetic retention timestamps/store availability. Settings and Qt composition remain AP070/100. No real hardware or ASR claim."}
        finally:
            for transport in log_transports: await transport.stop()
            await asyncio.gather(*log_tasks,return_exceptions=True)
            for media,mirror in clients: await media.close(); await mirror.close()
            await asyncio.gather(*tasks,return_exceptions=True)
            server.should_exit=True
            try: await asyncio.wait_for(serving,10)
            finally: tcp.close()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--server-root",required=True,type=Path)
    parser.add_argument("--server-repository",required=True,type=Path)
    args=parser.parse_args()
    print(json.dumps(asyncio.run(run(args.server_root.resolve(),args.server_repository.resolve())),indent=2))


if __name__=="__main__": main()
