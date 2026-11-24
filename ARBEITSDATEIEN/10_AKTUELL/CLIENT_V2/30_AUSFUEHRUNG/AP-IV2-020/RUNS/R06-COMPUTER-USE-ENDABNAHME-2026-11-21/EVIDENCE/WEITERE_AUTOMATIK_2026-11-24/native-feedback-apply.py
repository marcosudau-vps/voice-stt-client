import os,sys,json,time,uuid,hashlib,traceback
from pathlib import Path
from datetime import datetime
from dataclasses import asdict,replace
root=Path(__file__).parent
folder=root/('native-desktop-'+uuid.uuid4().hex[:8])
folder.mkdir()
os.chdir(folder)
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),QT_QPA_PLATFORM='windows')
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication,QSystemTrayIcon,QMessageBox,QPushButton
from voice_stt_client.core.v2_runtime import V2Runtime
from voice_stt_client.ui.v2_core_bridge import V2CoreBridge
from tests.test_text_injector import MockInjectionBackend
from voice_stt_client.core.history import TranscriptHistoryManager
from copy import deepcopy
import winsound, sounddevice as sd
from PySide6.QtCore import Qt
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.ui.v2_application import V2DesktopApplication
from voice_stt_client.ui.single_instance import SingleInstanceGuard
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH,EventCursorStore
report={'scope':'real native Qt desktop from corrected source, real pinned V2 TLS server, isolated test profile, real native Qt apply, real LED and QSoundEffect, real acoustic input, mock injection; physical visual/audible change not claimed','start':datetime.now().astimezone().isoformat(),'checks':{},'evidenceFolder':folder.name}
def save():
    (root/'native-feedback-apply.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def check(n,v):
    report['checks'][n]=bool(v);save();print(n,bool(v),flush=True)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
cursor_before=digest(DEFAULT_CURSOR_PATH)
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=next(i for i,x in enumerate(sd.query_devices()) if 'respeaker' in x['name'].casefold() and x['max_input_channels']>0)
config.overlay.enabled=True;config.overlay.show_realtime_text=True
config.led.enabled=True
config.feedback.sounds_enabled=True
from voice_stt_client.core.feedback_mapping import FeedbackMappingConfig,SoundCueId
mapping=config.feedback_mappings.to_mapping()
mapping['events']['server.transcription.completed']['sound']['volume']=.25
mapping['events']['server.transcription.completed']['led'].append({'set_output':{'brightness':.35}})
config.feedback_mappings=FeedbackMappingConfig.from_mapping(mapping)
config.event_stream.enabled=False
config.event_stream.cursor_persistence_enabled=False
config.history.persistent.db_path=str(folder/'history.sqlite')
config.history.persistent.store_all=True
config.history.memory.max_entries=100
config.clipboard.restore_previous=False
config.logging.log_dir=str(folder/'logs')
config.logging.observability.store_transcription_content=False
config.logging.observability.store_raw_payload=False
profile=V2Profile()
profile.controls['enabled']=False
config.v2_profile=asdict(profile)
config.save(folder/'profile.yaml')
config=AppConfig.load(folder/'profile.yaml')
seed=TranscriptHistoryManager(config.history)
entries=[seed.add_entry_with_status('r06-synthetic',i,f'R06 synthetic test {i}').entry for i in range(1,4)]
assert all(entries)
backend=MockInjectionBackend()
app=QApplication([])
app.setQuitOnLastWindowClosed(False)
app.setOrganizationName('R06-Test')
app.setApplicationName('R06-Isolated-Desktop')
guard=SingleInstanceGuard('Local\\CV2_R06_'+uuid.uuid4().hex)
desktop=None
def wait(fn,limit=25):
    end=time.monotonic()+limit
    while time.monotonic()<end:
        app.processEvents()
        if fn():return
        time.sleep(.02)
    raise TimeoutError('Condition not met')
def run():
    global desktop
    try:
        assert guard.acquire().acquired
        bridge=V2CoreBridge(config,runtime_factory=lambda cfg:V2Runtime(cfg,backend=backend))
        desktop=V2DesktopApplication(app,config,guard,bridge=bridge)
        assert desktop.start()
        wait(lambda:desktop._runtime_ready,40)
        runtime=desktop.bridge._controller
        identity=runtime.session.binding.accepted.payload['serverCommit']
        check('server_identity',identity=='e95858e3c010a7e9324b49bb44fee349abe7128a')
        from PySide6.QtMultimedia import QSoundEffect
        wait(lambda:runtime.audio.is_running and runtime.media.audio_available)
        wait(lambda:desktop.led_feedback._sink_available is True,15)
        check('real_usb_sink_available',desktop.led_feedback.is_running)
        desktop.tray.settings_action.trigger()
        wait(lambda:desktop.settings_dialog is not None and desktop.settings_dialog._view is not None)
        d=desktop.settings_dialog;wait(lambda:d._view.connected_ready)
        local=desktop._local_dialog;d.close()
        local.show();app.processEvents()
        old=desktop.led_feedback
        old_brightness=desktop.config.led.brightness
        local._editors['led.brightness'].setValue(100)
        local._editors['feedback.complete_sound'].setText(config.feedback.start_sound)
        local.apply_changes()
        wait(lambda:desktop._pending_config is None and desktop.config.led.brightness==100,20)
        check('brightness_and_sound_path_gui_applied',runtime.config.led.brightness==100 and desktop.sound_feedback.config.complete_sound==config.feedback.start_sound)
        check('led_worker_replaced',desktop.led_feedback is not old and not old.is_running)
        local.close()
        rules=[]
        desktop.bridge.feedback_decision_received.connect(lambda v:rules.append(v.rule))
        def dictate(name,tokens):
            n=len(backend.send_input_calls);previews=[]
            wait(lambda:runtime.is_ready and runtime.media.audio_available and runtime.mirror.mirror.view.manual_available and desktop.bridge._published_view is not None and desktop.bridge._published_view.mirror.manual_available,15)
            report['before_'+name]={'ready':runtime.is_ready,'manualAvailable':runtime.mirror.mirror.view.manual_available,'reportedAvailable':bool(runtime.media._reported_available and runtime.media._reported_available[1])}
            assert desktop.bridge.press_control('primary')
            wait(lambda:bool(runtime.mirror.mirror.view.input.activation_id))
            aid=runtime.mirror.mirror.view.input.activation_id
            start=time.monotonic()
            while time.monotonic()-start<.65:app.processEvents();time.sleep(.02)
            fixture=root.parent/'autonome-restpruefung-2026-11-23'/'fixtures'/(name+'.wav')
            winsound.PlaySound(str(fixture),winsound.SND_FILENAME|winsound.SND_ASYNC|winsound.SND_NODEFAULT)
            start=time.monotonic()
            while time.monotonic()-start<4.1:
                app.processEvents()
                text=desktop.overlay.label.text()
                if desktop.overlay.isVisible() and text and text not in previews and len(backend.send_input_calls)==n:previews.append(text)
                time.sleep(.025)
            if runtime.mirror.mirror.view.input.activation_id==aid:
                import asyncio
                future=asyncio.run_coroutine_threadsafe(runtime.stop_dictation(),desktop.bridge._loop)
                wait(lambda:future.done())
            wait(lambda:runtime.mirror.mirror.view.input.activation_id is None,15)
            wait(lambda:len(backend.send_input_calls)>n,30)
            entries=[e for e in runtime.history.get_memory_entries() if e.activation_id==aid]
            report[name]={'previewCount':len(previews),'previewMarkerMatch':any(any(t in p.casefold() for t in tokens) for p in previews),'finalCount':len(entries),'injectionCount':len(backend.send_input_calls)-n}
            check(name+'_one_final',len(entries)==1 and len(backend.send_input_calls)-n==1 and any(all(t in e.text.casefold() for t in tokens) for e in entries))
            check(name+'_preview_before_injection',report[name]['previewMarkerMatch'])
        dictate('kurz-01',('blau','bahnhof'))
        wait(lambda:desktop.led_feedback._sink_available is True,15)
        check('real_sink_after_apply',desktop.led_feedback.is_running)
        check('configured_final_rule_reached_output',any(rule.sound and rule.sound.cue==SoundCueId.COMPLETE and abs(rule.sound.volume-.25)<.001 and any(call.brightness==.35 for call in rule.led) for rule in rules))
        player=desktop.sound_feedback._effects.get(SoundCueId.COMPLETE)
        check('real_qsound_effect_volume_and_asset',player is not None and abs(player.volume()-.25)<.01 and player.source().toLocalFile().endswith('start.wav'))
        if player is not None:
            wait(lambda:player.status()!=QSoundEffect.Status.Loading,8)
            check('sound_backend_ready',player.status()==QSoundEffect.Status.Ready)
        local.show();app.processEvents()
        local._editors['feedback.sounds_enabled'].setChecked(False)
        local.apply_changes()
        wait(lambda:desktop._pending_config is None and not desktop.sound_feedback.config.sounds_enabled,20)
        local.close()
        dictate('kurz-02',('zitron','tisch'))
        check('sound_disabled_no_player_audio_still_running',not desktop.sound_feedback._effects and runtime.audio.is_running)
        saved=AppConfig.load(folder/'profile.yaml')
        check('feedback_profile_persisted',saved.led.brightness==100 and not saved.feedback.sounds_enabled and saved.feedback.complete_sound==config.feedback.start_sound)
        store=EventCursorStore()
        check('isolated_cursor_path',store.path==folder/'client'/'data'/'event_cursor.json')
    except Exception as exc:
        if desktop and desktop.bridge._controller:
            rt=desktop.bridge._controller
            v=rt.mirror.mirror.view
            report['failureContext']={'ready':rt.is_ready,'audioAvailable':rt.media.audio_available,'manualAvailable':v.manual_available,'reportedAvailable':bool(rt.media._reported_available and rt.media._reported_available[1]),'transport':rt.session.status.state.value,'trigger':dict(v.trigger),'phase':str(v.input.phase)}
        report['errorType']=type(exc).__name__
        report['error']=str(exc)
        traceback.print_exc()
    finally:
        if desktop is not None:
            desktop.tray.quit_action.trigger()
        else:app.quit()
QTimer.singleShot(0,run)
app.exec()
if desktop:
    desktop.shutdown()
    check('shutdown_core_tray',not desktop.bridge.is_running and not desktop.tray.tray.isVisible() and not desktop.hotkeys._registered_ids)
guard.release()
check('shared_cursor_unchanged',cursor_before==digest(DEFAULT_CURSOR_PATH))
report['end']=datetime.now().astimezone().isoformat()
report['result']='PASS_SCOPED' if report['checks'] and all(report['checks'].values()) and 'error' not in report else 'INCOMPLETE_OR_FAIL'
save()
print(report['result'],flush=True)
