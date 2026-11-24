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
from PySide6.QtWidgets import QApplication,QSystemTrayIcon
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.ui.v2_application import V2DesktopApplication
from voice_stt_client.ui.single_instance import SingleInstanceGuard
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH,EventCursorStore
report={'scope':'real native Qt desktop from corrected source, real pinned V2 TLS server, isolated test profile, no microphone or global hotkeys, actual Admin UI final test origin only, reversible default with CAS restoration','start':datetime.now().astimezone().isoformat(),'checks':{},'evidenceFolder':folder.name}
def save():
    (root/'native-final-admin.json').write_text(json.dumps(report,indent=2),encoding='utf8')
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
config.logging.log_dir=str(folder/'logs')
config.logging.observability.store_transcription_content=False
config.logging.observability.store_raw_payload=False
profile=V2Profile()
profile.controls['enabled']=False
config.v2_profile=asdict(profile)
config.save(folder/'profile.yaml')
config=AppConfig.load(folder/'profile.yaml')
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
    import re, shlex
    from voice_stt_client.core.settings_service import SettingsHTTP,SettingsService
    from voice_stt_client.core.credential_store import CredentialStore
    from urllib.request import urlopen
    origin='https://final.v2.voice-stt-server.marcosudau.com'
    secret_file=Path(r'S:\VPS_Spiegelverzeichnis\vps\home\marco\selfhost\secrets\voice-stt.env')
    key=None
    for line in secret_file.read_text(encoding='utf-8-sig').splitlines():
        match=re.match(r'^\s*(?:export\s+)?VOICESTT_ADMIN_API_KEY\s*=\s*(.*)$',line)
        if match:
            value=match.group(1).strip()
            if value.startswith(('"',"'")):
                values=shlex.split(value,comments=True,posix=True)
                key=values[0] if len(values)==1 else None
            else:
                key=value.split(' #',1)[0].strip()
            break
    invalid='r06-invalid-'+uuid.uuid4().hex
    before=None;trial=None;attempted=False;restored=False;http=SettingsHTTP(config.server.url,timeout=12)
    param='activation.followupTimeoutMs'
    def info():
        with urlopen(origin+'/api/v2/info',timeout=12) as f:
            d=json.load(f)
        return (d.get('serverCommit'),d.get('serverInstanceId'))
    def read():
        resp=http._request('GET','/api/v2/settings/server',None,None)
        if resp.status!=200:raise RuntimeError('server read failed')
        return SettingsService._parse_server(resp.body)
    def patch(revision,value,auth):
        return http._request('PATCH','/api/v2/settings/server',{'baseSettingsRevision':revision,'changes':{param:value}},auth)
    def same_values(snapshot,base):return snapshot[1]==base[1] and snapshot[2]==base[2]
    def verified(d,k):
        d.key.setText(k);d.remember.setChecked(False);d.verify_button.click()
        wait(lambda:'läuft' not in d.status.text(),35)
        return d._view.admin_verified and d.apply_server_button.isEnabled() and not d.key.text()
    def gui_patch(d,value):
        d._editors['server'][param].setText(str(value))
        if d._changes('server')!={param:value}:raise RuntimeError('unexpected GUI change set')
        d.apply_server_button.click();wait(lambda:'läuft' not in d.status.text(),35)
    store=CredentialStore();vault_before=None;vault_read=False
    expected='e95858e3c010a7e9324b49bb44fee349abe7128a'

    try:
        if not isinstance(key,str) or not key or '\n' in key or '\r' in key:raise RuntimeError('authorized admin key unavailable')
        pin=info();assert pin[0]==expected and pin[1]
        report['serverInstance']=pin[1];before=read();report['baselineRevision']=before[0];report['baselineValue']=before[1][param];save()
        vault_before=store.read(origin);vault_read=True
        assert guard.acquire().acquired
        desktop=V2DesktopApplication(app,config,guard)
        assert desktop.start()
        wait(lambda:desktop._runtime_ready,40)
        runtime=desktop.bridge._controller
        identity=runtime.session.binding.accepted.payload['serverCommit']
        check('server_identity',identity=='e95858e3c010a7e9324b49bb44fee349abe7128a')
        assert identity==expected
        desktop.tray.settings_action.trigger()
        wait(lambda:desktop.settings_dialog is not None and desktop.settings_dialog._view is not None)
        d=desktop.settings_dialog;wait(lambda:d._view.connected_ready)
        d.timer.stop();d.tabs.setCurrentIndex(2)
        check('locked_before_verification',not d._view.admin_verified and not d.apply_server_button.isEnabled() and not d._editors['server'][param].isEnabled())
        check('invalid_key_rejected',not verified(d,invalid) and not d.apply_server_button.isEnabled())
        check('invalid_key_defaults_unchanged',same_values(read(),before))
        valid=verified(d,key)
        check('positive_admin_dialog_unlock',valid and d._editors['server'][param].isEnabled())
        if not valid:raise RuntimeError('Admin verification rejected')
        check('verify_no_change',read()[0]==before[0] and same_values(read(),before))
        current=before[1][param];trial=current+100 if current<=59900 else current-100
        d._view.schema[param].validate(trial)
        if info()!=pin or read()!=before:raise RuntimeError('concurrent server change, refuse write')
        attempted=True
        gui_patch(d,trial)
        changed=read();report['changedRevision']=changed[0];report['testValue']=trial;save()
        check('admin_gui_change_confirmed',changed[0]==before[0]+1 and changed[1][param]==trial and d._view.server_requested[param]==trial)
        check('only_expected_default_changed',all(changed[1][k]==v for k,v in before[1].items() if k!=param))
        if changed[1][param]!=trial:raise RuntimeError('change not confirmed')
        # Stale revision with current value cannot change anything, must reject.
        stale=patch(before[0],trial,key)
        check('stale_revision_rejected',stale.status==409 and read()==changed)
        check('wrong_key_write_rejected',patch(changed[0],current,invalid).status in (401,403) and read()==changed)
        generation=runtime.session.generation
        desktop.reconnect_server()
        wait(lambda:runtime.is_ready and runtime.session.generation>generation,30)
        d._request('load');wait(lambda:'läuft' not in d.status.text(),25)
        check('reconnect_requires_new_admin_verification',not d._view.admin_verified and not d.apply_server_button.isEnabled())
        check('new_session_effective_changed_default',runtime.mirror.mirror.view.effective_settings.get(param)==trial)
        if not verified(d,key):raise RuntimeError('admin reverify failed')
        check('reverified_new_generation',True)
        if info()!=pin or read()!=changed:raise RuntimeError('concurrent server change, refuse blind restore')
        gui_patch(d,current)
        after=read();report['restoredRevision']=after[0]
        restored=same_values(after,before)
        check('gui_restore_exact_original_defaults',restored and after[0]==changed[0]+1)
        generation=runtime.session.generation
        desktop.reconnect_server();wait(lambda:runtime.is_ready and runtime.session.generation>generation,30)
        check('new_session_effective_original_default',runtime.mirror.mirror.view.effective_settings.get(param)==current)
        d._request('load');wait(lambda:'läuft' not in d.status.text(),25)
        check('admin_locked_after_restore_reconnect',not d._view.admin_verified and not d.apply_server_button.isEnabled())
        d.close()
        # No persistent real credential; exercise real Windows vault in a dedicated synthetic origin.
        test_origin='https://r06-'+uuid.uuid4().hex+'.invalid'
        fake='r06-test-'+uuid.uuid4().hex
        assert store.read(test_origin) is None
        try:
            store.save(test_origin,fake)
            check('native_credential_roundtrip_isolated',store.read(test_origin)==fake)
        finally:store.delete(test_origin)
        check('native_credential_deleted_isolated',store.read(test_origin) is None)
        check('existing_admin_vault_unchanged',store.read(origin)==vault_before)
    except Exception as exc:
        report['errorType']=type(exc).__name__
        # Never log arbitrary HTTP exceptions or credential material.
        print('ADMIN TEST EXCEPTION',type(exc).__name__,flush=True)
    finally:
        if attempted and before is not None and not restored:
            try:
                now=read()
                if same_values(now,before):
                    restored=True
                elif info()==pin and now[1][param]==trial and now[0]==before[0]+1 and all(now[1][k]==v for k,v in before[1].items() if k!=param):
                    result=patch(now[0],before[1][param],key)
                    restored=result.status==200 and same_values(read(),before)
                    report['emergencyRestoreUsed']=True
                else:report['manualRestoreRequired']=True
            except Exception:report['manualRestoreRequired']=True
        report['restoredExact']=restored if attempted else None
        if before is not None:
            try:
                check('final_server_defaults_unchanged',same_values(read(),before))
                check('same_server_instance',info()==pin)
            except Exception:report['finalReadbackFailed']=True
        if vault_read:
            try:check('real_credential_not_modified',store.read(origin)==vault_before)
            except Exception:report['vaultReadFailed']=True
        if desktop is not None:desktop.tray.quit_action.trigger()
        else:app.quit()
        # No key in own generated evidence or profile.
        try:check('no_admin_key_in_owned_files',not any(key.encode() in p.read_bytes() for p in folder.rglob('*') if p.is_file()) if key else False)
        except Exception:report['secretScanFailed']=True
        key=None;vault_before=None;save()
QTimer.singleShot(0,run);app.exec()
if desktop:
    desktop.shutdown();check('shutdown_core_tray',not desktop.bridge.is_running and not desktop.tray.tray.isVisible() and not desktop.hotkeys._registered_ids)
guard.release()
check('shared_cursor_unchanged',cursor_before==digest(DEFAULT_CURSOR_PATH))
report['end']=datetime.now().astimezone().isoformat()
report['result']='PASS_SCOPED' if report['checks'] and all(report['checks'].values()) and not report.get('errorType') and report.get('restoredExact') else 'INCOMPLETE_OR_FAIL'
save();print(report['result'],flush=True)
