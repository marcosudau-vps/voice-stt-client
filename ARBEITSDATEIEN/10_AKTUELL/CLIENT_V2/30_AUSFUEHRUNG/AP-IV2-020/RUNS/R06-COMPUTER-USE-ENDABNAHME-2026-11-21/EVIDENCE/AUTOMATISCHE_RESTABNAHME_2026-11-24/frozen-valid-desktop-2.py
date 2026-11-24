import os,sys,uuid,hashlib,json,subprocess,time,sqlite3,ctypes
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
root=Path(__file__).parent
folder=root/('frozen-valid-'+uuid.uuid4().hex[:8])
folder.mkdir();(folder/'tmp').mkdir()
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'),QT_QPA_PLATFORM='windows')
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from dataclasses import asdict
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=2147483647
config.led.enabled=False;config.feedback.sounds_enabled=False;config.event_stream.enabled=False
config.event_stream.cursor_persistence_enabled=False
config.history.persistent.db_path=str(folder/'history.sqlite')
config.logging.log_dir=str(folder/'logs')
config.logging.observability.db_path=str(folder/'observability.sqlite3')
config.logging.observability.store_transcription_content=False
config.logging.observability.store_raw_payload=False
profile=V2Profile();profile.controls['enabled']=False;config.v2_profile=asdict(profile)
config.save(folder/'profile.yaml')
exe=Path(r'P:\\GithubRepos\\marcosudau-vps\\voice-stt-client\\workspaces\\v2-final-automatik-nachweise-20261121')/'dist-r06-korrektur-lokal-20261123'/'voice-stt-client.exe'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
assert digest(exe)=='07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe'
before=digest(DEFAULT_CURSOR_PATH);prof=digest(folder/'profile.yaml')
r=dict(scope='corrected frozen EXE normal GUI, pinned V2, invalid input deliberately, no hotkeys, Windows WM_QUIT instead of tray click',start=datetime.now().astimezone().isoformat(),folder=folder.name,exeSha256=digest(exe))
p=subprocess.Popen([str(exe),'--config',str(folder/'profile.yaml')],cwd=folder,env=os.environ.copy())
db=folder/'observability.sqlite3'
def rows():
    try:
        with sqlite3.connect(db.as_uri()+'?mode=ro',uri=True,timeout=.1) as c:
            return c.execute('select type,details_json from logs order by id').fetchall()
    except sqlite3.Error:return []
def status():
    entries=rows()
    pid=next((json.loads(d).get('process_id') for t,d in entries if t=='client.app.started'),None)
    states=[json.loads(d).get('state') for t,d in entries if t=='client.v2.transport_state']
    return pid,states
user=ctypes.WinDLL('user32',use_last_error=True)
user.GetWindowThreadProcessId.argtypes=[wintypes.HWND,ctypes.POINTER(wintypes.DWORD)]
user.GetWindowThreadProcessId.restype=wintypes.DWORD
user.PostThreadMessageW.argtypes=[wintypes.DWORD,wintypes.UINT,wintypes.WPARAM,wintypes.LPARAM]
user.PostThreadMessageW.restype=wintypes.BOOL
WINFUNC=ctypes.WINFUNCTYPE(wintypes.BOOL,wintypes.HWND,wintypes.LPARAM)
user.EnumWindows.argtypes=[WINFUNC,wintypes.LPARAM]
user.GetClassNameW.argtypes=[wintypes.HWND,wintypes.LPWSTR,ctypes.c_int]
def windows(pid):
    result=[]
    @WINFUNC
    def visit(h,_):
        owner=wintypes.DWORD()
        thread=user.GetWindowThreadProcessId(h,ctypes.byref(owner))
        if owner.value==pid:
            name=ctypes.create_unicode_buffer(256);user.GetClassNameW(h,name,256)
            result.append((int(h),int(thread),name.value))
        return True
    user.EnumWindows(visit,0)
    return result
try:
    deadline=time.monotonic()+35
    while time.monotonic()<deadline:
        pid,states=status()
        if pid and 'ready' in states:break
        if p.poll() is not None:break
        time.sleep(.25)
    r.update(productPid=pid,states=states,ready=bool(pid and 'ready' in states))
    if r['ready']:
        # Second normal EXE startup while first still holds mutex.
        second=subprocess.Popen([str(exe),'--config',str(folder/'profile.yaml')],cwd=folder,env=os.environ.copy())
        try:r['secondExitCode']=second.wait(20)
        except subprocess.TimeoutExpired:
            subprocess.run(['taskkill','/PID',str(second.pid),'/T','/F'],capture_output=True)
            r['secondTimeout']=True
        r['firstStillRunning']=p.poll() is None
        windows_found=windows(pid)
        r['windowClasses']=[n for _,_,n in windows_found]
        threads={t for _,t,n in windows_found if n.startswith('Qt')}
        r['qtThreads']=len(threads)
        if len(threads)==1:r['quitPosted']=bool(user.PostThreadMessageW(next(iter(threads)),0x12,0,0))
        else:r['quitPosted']=False
    r['exitCode']=p.wait(20)
except subprocess.TimeoutExpired:
    r['timeout']=True
finally:
    if p.poll() is None:
        subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
        p.wait(10);r['forcedCleanup']=True
r['tempRemaining']=[x.name for x in (folder/'tmp').glob('_MEI*')]
r['profileUnchanged']=prof==digest(folder/'profile.yaml')
r['sharedCursorUnchanged']=before==digest(DEFAULT_CURSOR_PATH)
r['lifecycleTypes']=[t for t,d in rows() if t and ('app.' in t or 'shutdown' in t or 'lifecycle' in t)]
r['end']=datetime.now().astimezone().isoformat()
r['result']='PASS_SCOPED' if r.get('ready') and r.get('quitPosted') and r.get('exitCode')==0 and r.get('secondExitCode')==2 and r.get('firstStillRunning') and r['profileUnchanged'] and r['sharedCursorUnchanged'] and not r['tempRemaining'] and not r.get('forcedCleanup') else 'INCOMPLETE_OR_FAIL'
(root/'frozen-valid-desktop.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print(json.dumps(r,indent=2),flush=True)
