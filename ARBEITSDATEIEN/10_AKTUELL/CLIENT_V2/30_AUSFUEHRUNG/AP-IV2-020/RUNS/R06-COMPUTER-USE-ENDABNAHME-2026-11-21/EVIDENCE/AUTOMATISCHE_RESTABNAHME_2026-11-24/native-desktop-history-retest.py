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
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.ui.v2_application import V2DesktopApplication
from voice_stt_client.ui.single_instance import SingleInstanceGuard
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH,EventCursorStore
report={'scope':'real native Qt desktop from corrected source, real pinned V2 TLS server, isolated test profile, no microphone or global hotkeys; synthetic isolated history and mock injection','start':datetime.now().astimezone().isoformat(),'checks':{},'evidenceFolder':folder.name}
def save():
    (root/'native-desktop-history-retest.json').write_text(json.dumps(report,indent=2),encoding='utf8')
def check(n,v):
    report['checks'][n]=bool(v);save();print(n,bool(v),flush=True)
def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
cursor_before=digest(DEFAULT_CURSOR_PATH)
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=2147483647
config.led.enabled=False
config.feedback.sounds_enabled=False
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
        check('no_audio_no_hotkeys',not runtime.audio.is_running and not desktop.hotkeys._registered_ids)
        check('tray_available_and_visible',QSystemTrayIcon.isSystemTrayAvailable() and desktop.tray.tray.isVisible())
        check('tray_tooltip_and_menu',bool(desktop.tray.tray.toolTip()) and desktop.tray.settings_action in desktop.tray.menu.actions() and desktop.tray.quit_action in desktop.tray.menu.actions())
        desktop.tray.settings_action.trigger()
        wait(lambda:desktop.settings_dialog is not None and desktop.settings_dialog._view is not None)
        d=desktop.settings_dialog
        wait(lambda:d._view.connected_ready)
        check('native_settings_tabs',d.isVisible() and d.tabs.count()==3)
        d._local_dialog if hasattr(d,'_local_dialog') else None
        local=desktop._local_dialog
        local.show();app.processEvents()
        check('native_local_tabs',local.isVisible() and local.tabs.count()==5)
        check('invalid_audio_retained_and_no_capture',local._editors['audio.device'].currentData()==2147483647 and not runtime.audio.is_running)
        local.close()
        d.close()
        local.show();app.processEvents()
        local.history_refresh_requested.emit()
        wait(lambda:local.history_table.rowCount()==3)
        check('history_three_seeded_rows',local.history_table.rowCount()==3)
        ids=[local.history_table.item(i,0).data(256) for i in range(3)]
        check('history_order_and_id_binding',ids==[e.id for e in reversed(entries)])
        local.history_table.selectRow(1)
        local._reinsert_selected()
        wait(lambda:len(backend.send_input_calls)==1)
        wait(lambda:len(runtime.history.get_recent_entries())==3 if hasattr(runtime.history,'get_recent_entries') else len(runtime.history.get_memory_entries())==3)
        wait(lambda:len(runtime.history.get_memory_entries()[1].attempts)>0)
        check('selected_reinsert_only',len(backend.send_input_calls)==1 and len(runtime.history.get_memory_entries())==3 and any(e.id==entries[1].id and len(e.attempts)==1 for e in runtime.history.get_memory_entries()))
        def answer_yes():
            box=app.activeModalWidget()
            if isinstance(box,QMessageBox):
                button=box.button(QMessageBox.StandardButton.Yes)
                if button:button.click()
        QTimer.singleShot(100,answer_yes)
        local._delete_selected()
        wait(lambda:len(runtime.history.get_memory_entries())==2)
        local.history_refresh_requested.emit()
        wait(lambda:local.history_table.rowCount()==2)
        check('delete_selected_only',set(e.id for e in runtime.history.get_memory_entries())=={entries[0].id,entries[2].id})
        QTimer.singleShot(100,answer_yes)
        local._clear_history()
        wait(lambda:not runtime.history.get_memory_entries())
        local.history_refresh_requested.emit()
        wait(lambda:local.history_table.rowCount()==0)
        check('clear_synthetic_history_only',not runtime.history.get_persistent_entries())
        local._editors['history.enabled'].setChecked(False)
        local._editors['text_injection.paste_delay_ms'].setValue(175)
        local._editors['clipboard.restore_previous'].setChecked(True)
        local.apply_changes()
        wait(lambda:desktop._pending_config is None,15)
        check('local_config_applied',not runtime.history.config.enabled and runtime.queue.config.text_injection.paste_delay_ms==175 and runtime.queue.config.clipboard.restore_previous)
        cfg=AppConfig.load(folder/'profile.yaml')
        check('local_config_saved',not cfg.history.enabled and cfg.text_injection.paste_delay_ms==175 and cfg.clipboard.restore_previous)
        # Widget metadata and actual native Qt geometry under resized viewports.
        from PySide6.QtWidgets import QWidget
        for dialog in (d,local):
            dialog.show()
            for size in ((850,650),(1250,850)):
                dialog.resize(*size);app.processEvents()
                for i in range(dialog.tabs.count()):
                    dialog.tabs.setCurrentIndex(i);app.processEvents()
                    page=dialog.tabs.currentWidget()
                    check(('v2' if dialog is d else 'local')+'_layout_'+str(size[0])+'_'+str(i),page.isVisible() and page.width()>0 and page.height()>0)
            dialog.close()
        check('tray_status',desktop.tray.tray.isVisible() and bool(desktop.tray.tray.toolTip()))
        store=EventCursorStore()
        check('isolated_cursor_path',store.path==folder/'client'/'data'/'event_cursor.json')
    except Exception as exc:
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