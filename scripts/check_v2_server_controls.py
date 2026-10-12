"""AP050 actual controls -> transport/mirror -> pinned production server.

Loopback only. Recorder/models, catalog engine probing and timer clock are
explicit model-free boundaries; no production service or user audio involved.
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
import time
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_v2_server_transport import SERVER_SHA, verify_sources, until
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.v2_controls import ControlConfig, ControlIntent, V2ControlService
from voice_stt_client.core.v2_mirror import V2MirrorConnection
from voice_stt_client.core.v2_transport import V2STTSession, V2TransportConfig


async def run(root, repository):
    sys.path.insert(0, str(root))
    import uvicorn
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import AutoScheduler
    from VoiceSTT.core.wake_detection import WakeHit, WakeAttemptPolicy
    verify_sources(root, repository)
    checks, wire = [], []
    def check(name, condition):
        if not condition: raise AssertionError(name)
        checks.append(name)

    with tempfile.TemporaryDirectory(prefix='cv2-050-server-') as data, patch.dict(os.environ, {'VOICESTT_SERVER_COMMIT': SERVER_SHA}):
        settings = ServerSettings(data_root_path=data, model_warmup=False, request_logging_enabled=False,
                                  performance_logging_enabled=False, performance_log_mirror_enabled=False,
                                  transcription_logging_enabled=False, system_event_logging_enabled=False,
                                  event_store_enabled=False, log_live_enabled=False)
        app = create_app(settings, recorder_factory=GateAwareRecorder, scheduler_factory=AutoScheduler)
        service = app.state.voicestt_service
        service.wakeword_catalog.set_artifact_prober(lambda path: None)
        tcp = socket.socket(); tcp.bind(('127.0.0.1', 0)); tcp.listen(16)
        server = uvicorn.Server(uvicorn.Config(app, log_level='error', access_log=False))
        serving = asyncio.create_task(server.serve(sockets=[tcp]))
        url = f'ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2'
        clients, runners = [], []
        try:
            await until(lambda: server.started or serving.done())
            async def start(manual=True, wake=True):
                async def settings_audio_boundary(client, binding):
                    await client.bootstrap_command(binding, p.CommandType.AUDIO_AVAILABILITY, audioAvailable=True)
                client = V2STTSession(V2TransportConfig(url=url, manual=manual, wake_word=wake,
                                      wake_word_ids=('hey_jarvis',) if wake else (), backoff_initial=.02),
                                      bootstrap=settings_audio_boundary)
                client.on_completion = lambda c: wire.append(dict(sessionId=c.ack.sessionId, generation=c.generation,
                    type=str(c.command.type), action=c.command.payload.get('action'),
                    activationId=c.command.payload.get('activationId'), result=str(c.ack.result)))
                mirror = V2MirrorConnection(client)
                controls = V2ControlService(client, mirror, audio_ready=lambda: True)
                clients.append((controls, mirror)); runners.append(asyncio.create_task(client.run()))
                await until(lambda: client.is_ready and not mirror.mirror.view.snapshot_pending)
                check(f'admission/{manual}/{wake}', client.binding.accepted.payload['serverCommit'] == SERVER_SHA)
                return client, mirror, controls

            async def settled(client, mirror):
                await until(lambda: client.is_ready and not mirror.mirror.view.snapshot_pending)

            def wake_hit(domain):
                domain._on_wakeword_detection_start()
                hit = WakeHit(canonical_wake_word_id='hey_jarvis', peak_score=.91, start_frame_index=0,
                    start_sample=1280, qualification_frame_index=0, qualification_sample=1280,
                    finalization_frame_index=1, operational_zero_point_sample=32000, prediction_frame_count=1,
                    policy=WakeAttemptPolicy(sensitivity=.5))
                return domain._on_wakeword_detected(hit)

            for manual, wake in ((True, False), (False, True), (True, True)):
                client, mirror, controls = await start(manual, wake)
                domain = service.sessions.get(client.binding.session_id)
                controller = domain.activation_controller()
                clock = [time.monotonic()]; controller._clock = lambda: clock[0]
                check(f'idle/secondary_noop/{manual}/{wake}', await controls.press('secondary') is None)
                if not manual:
                    check('wake_only/primary_idle_noop', await controls.press('primary') is None)
                    check('wake_only/admission_hit', wake_hit(domain) is not None)
                else:
                    activated = await controls.press('primary')
                    check(f'manual/activate/{wake}', activated.ack.accepted)
                await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.WAITING_FIRST_SPEECH)
                await settled(client, mirror)
                aid = mirror.mirror.view.input.activation_id
                before = len(wire)
                check(f'waiting/refresh_no_wire/{manual}/{wake}', await controls.press('primary') is None and len(wire) == before)
                forced = await client.request(p.CommandType.ACTIVATION, action='refresh', activationId=aid)
                check(f'waiting/forced_invalid_phase/{manual}/{wake}', forced.ack.result == p.AckResult.INVALID_PHASE)
                await asyncio.sleep(.03)
                check(f'waiting/no_warn_retry/{manual}/{wake}', len(wire) == before + 1)
                await controls.set_pause('manual', True); await settled(client, mirror)
                await controls.press('wake_pause'); await settled(client, mirror)
                check(f'pause/open_activation_survives/{manual}/{wake}', mirror.mirror.view.input.activation_id == aid)
                check(f'pause/both_confirmed/{manual}/{wake}', not controls.pause_view.pending and
                      controls.pause_view.confirmed_manual and controls.pause_view.confirmed_wake_word)
                check(f'pause/no_effective_source/{manual}/{wake}', not any(mirror.mirror.view.trigger['effective'].values()))
                await client.send_audio(b'\0\x40' * 640, 16000, frames=640)
                await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.SEGMENT_ACTIVE)
                await settled(client, mirror)
                old_deadline = controller.snapshot()['deadline']
                before = len(wire)
                await client.send_audio(b'\0\x40' * 640, 16000, frames=640)
                await asyncio.sleep(.03)
                check(f'vad/no_watchdog_or_presence_refresh/{manual}/{wake}',
                      controller.snapshot()['deadline'] == old_deadline and len(wire) == before)
                await controls.press('primary'); await settled(client, mirror)
                check(f'segment/no_cumulative_refresh/{manual}/{wake}', controller.snapshot()['deadline'] == old_deadline)
                clock[0] += 580
                await controls.press('primary'); await settled(client, mirror)
                advanced = controller.snapshot()['deadline']
                check(f'segment/minimum_restored/{manual}/{wake}', advanced > old_deadline)
                await controls.press('primary'); await settled(client, mirror)
                check(f'segment/repeat_non_cumulative/{manual}/{wake}', controller.snapshot()['deadline'] == advanced)
                # Actual recorder VAD boundary completes the segment, without a
                # client finish. The production server owns the followup deadline.
                domain.recorder.flush_buffered_audio()
                await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.FOLLOWUP_WAIT)
                await settled(client, mirror)
                followup = controller.snapshot()['deadline']
                clock[0] += .5
                await controls.press('primary'); await settled(client, mirror)
                refreshed = controller.snapshot()['deadline']
                check(f'followup/now_plus_timeout/{manual}/{wake}', abs(refreshed - followup - .5) < .001)
                await controls.press('primary'); await settled(client, mirror)
                check(f'followup/repeat_non_cumulative/{manual}/{wake}', controller.snapshot()['deadline'] == refreshed)
                await until(lambda: any(s.text for s in mirror.mirror.view.segments.values()))
                preserved = {sid: s.text for sid, s in mirror.mirror.view.segments.items() if s.text}
                done = await controls.press('secondary')
                check(f'finish/applied/{manual}/{wake}', done.ack.accepted)
                await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.IDLE)
                await settled(client, mirror)
                await controls.set_pause('manual', False); await controls.set_pause('wakeWord', False)
                await settled(client, mirror)
                if not manual: check('wake_only/second_hit', wake_hit(domain) is not None)
                else: await controls.press('primary')
                await until(lambda: mirror.mirror.view.input.activation_id is not None)
                await settled(client, mirror)
                new_aid = mirror.mirror.view.input.activation_id
                stale = await controls.execute(ControlIntent(client.generation, client.binding.session_id, 'cancel', aid))
                check(f'stale/original_id/{manual}/{wake}', stale.command.payload['activationId'] == aid and stale.ack.result == p.AckResult.STALE_ACTIVATION)
                await settled(client, mirror)
                check(f'stale/new_activation_untouched/{manual}/{wake}', mirror.mirror.view.input.activation_id == new_aid)
                cancelled = await controls.control('cancel')
                check(f'cancel/applied/{manual}/{wake}', cancelled.ack.accepted)
                await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.IDLE)
                check(f'cancel/published_text_preserved/{manual}/{wake}', all(mirror.mirror.view.segments[sid].text == text for sid, text in preserved.items()))
                await settled(client, mirror)
                if not manual: check('wake_only/third_hit', wake_hit(domain) is not None)
                else: await controls.press('primary')
                await until(lambda: mirror.mirror.view.input.activation_id is not None)
                await settled(client, mirror)
                await client.send_audio(b'\0\x40' * 640, 16000, frames=640)
                await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.SEGMENT_ACTIVE)
                await settled(client, mirror)
                finished_recording = await controls.control('finish')
                check(f'finish/recorded_audio_processed/{manual}/{wake}', finished_recording.ack.accepted)
                await until(lambda: mirror.mirror.view.input.phase == p.InputPhase.IDLE and
                            len([s for s in mirror.mirror.view.segments.values() if s.text]) == len(preserved) + 1)
                check(f'finish/new_final_without_deleting_old/{manual}/{wake}', all(
                      mirror.mirror.view.segments[sid].text == text for sid, text in preserved.items()))
                await settled(client, mirror)
                await controls.set_pause('manual', True); await controls.set_pause('wakeWord', True)
                await settled(client, mirror)
                await client.request(p.CommandType.AUDIO_AVAILABILITY, audioAvailable=False)
                await settled(client, mirror)
                check(f'device/pause_preserved/{manual}/{wake}', not controls.pause_view.pending)
                old = client.binding; run_id = client.client_run_id
                await client.reconnect(old, 'synthetic_network_loss')
                await until(lambda: client.binding is not None and client.binding is not old and client.is_ready)
                await settled(client, mirror)
                check(f'reconnect/no_active_gap/{manual}/{wake}', not any(mirror.mirror.view.trigger['effective'].values()) and not controls.pause_view.pending)
                check(f'reconnect/new_session_same_run/{manual}/{wake}', client.binding.session_id != old.session_id and client.client_run_id == run_id)
                await controls.close(); await mirror.close()
            # Genuine independent interpreter gives process-new run ID and
            # unpaused intent; this is not a second service in the same process.
            output = subprocess.check_output([sys.executable, '-c',
                'from voice_stt_client.core.v2_transport import V2STTSession; s=V2STTSession(); print(s.client_run_id, *s._desired_suppression)'],
                cwd=ROOT, text=True).strip().split()
            check('restart/new_run_id_unpaused', output[0] != run_id and output[1:] == ['False', 'False'])
            return dict(result='PASS', serverCommit=SERVER_SHA, clientHead=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
                        checks=checks, checkCount=len(checks), sourceHashes=verify_sources(root, repository), wireTrace=wire,
                        runtime=dict(python=sys.version, executable=sys.executable, platform=platform.platform()),
                        boundaries='Real V2ControlService/V2STTSession/V2MirrorConnection through TCP/WS production server. Pinned GateAwareRecorder/AutoScheduler and synthetic WakeHit replace model/VAD outputs; permissive artifact probe replaces inference engine; server monotonic clock held/advanced for non-cumulative timing. Named settings/audio bootstrap, no Qt/app composition (AP070/100), hardware or ASR claim. Separate actual Win32 smoke.')
        finally:
            for controls, mirror in clients: await controls.close(); await mirror.close()
            await asyncio.gather(*runners, return_exceptions=True)
            server.should_exit = True
            try: await asyncio.wait_for(serving, 10)
            finally: tcp.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-root', required=True, type=Path)
    parser.add_argument('--server-repository', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(asyncio.run(run(args.server_root.resolve(), args.server_repository.resolve())), indent=2))
