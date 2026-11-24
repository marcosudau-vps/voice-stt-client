import os,sys,uuid,hashlib,json,subprocess,time,sqlite3,ctypes,argparse,statistics
import sounddevice as sd
from ctypes import wintypes
from pathlib import Path
from datetime import datetime
root=Path(__file__).parent
folder=root/('frozen-idle-'+uuid.uuid4().hex[:8])
folder.mkdir();(folder/'tmp').mkdir()
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'),QT_QPA_PLATFORM='windows')
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from dataclasses import asdict
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/v2'
config.server.health_url='https://final.v2.voice-stt-server.marcosudau.com/health'
config.audio.device=next(i for i,d in enumerate(sd.query_devices()) if 'respeaker' in d['name'].casefold() and d['max_input_channels']>0)
config.led.enabled=True;config.feedback.sounds_enabled=True;config.event_stream.enabled=False
config.event_stream.cursor_persistence_enabled=False
config.history.persistent.db_path=str(folder/'history.sqlite')
config.logging.log_dir=str(folder/'logs')
config.logging.observability.db_path=str(folder/'observability.sqlite3')
config.logging.observability.store_transcription_content=False
config.logging.observability.store_raw_payload=False
profile=V2Profile(manual=True,wake_word=False);profile.controls['enabled']=False;config.v2_profile=asdict(profile)
config.save(folder/'profile.yaml')
exe=Path(r'P:\\GithubRepos\\marcosudau-vps\\voice-stt-client\\workspaces\\v2-final-automatik-nachweise-20261121')/'dist-r06-korrektur-lokal-20261123'/'voice-stt-client.exe'
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None
assert digest(exe)=='07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe'
before=digest(DEFAULT_CURSOR_PATH);prof=digest(folder/'profile.yaml')
r=dict(scope='corrected frozen EXE real ReSpeaker capture and LED enabled, real V2 transport, idle-only no wake or native hotkeys, periodic CPU/RAM metrics, no clipboard, WM_QUIT',start=datetime.now().astimezone().isoformat(),folder=folder.name,exeSha256=digest(exe))
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
parser=argparse.ArgumentParser();parser.add_argument('--seconds',type=int,default=180);args=parser.parse_args()
r['targetSeconds']=args.seconds;r['samples']=[]
out=root/'frozen-idle-resource.json'
def save():
    tmp=out.with_suffix('.tmp');tmp.write_text(json.dumps(r,indent=2),encoding='utf8')
    try:tmp.replace(out)
    except PermissionError:pass
# Process counters from Windows without psutil or shell overhead.
kernel=ctypes.WinDLL('kernel32',use_last_error=True);psapi=ctypes.WinDLL('psapi',use_last_error=True)
class PMC(ctypes.Structure):
    _fields_=[('cb',wintypes.DWORD),('PageFaultCount',wintypes.DWORD)]+[(n,ctypes.c_size_t) for n in ('PeakWorkingSetSize','WorkingSetSize','QuotaPeakPagedPoolUsage','QuotaPagedPoolUsage','QuotaPeakNonPagedPoolUsage','QuotaNonPagedPoolUsage','PagefileUsage','PeakPagefileUsage','PrivateUsage')]
kernel.OpenProcess.argtypes=[wintypes.DWORD,wintypes.BOOL,wintypes.DWORD];kernel.OpenProcess.restype=wintypes.HANDLE
kernel.CloseHandle.argtypes=[wintypes.HANDLE]
kernel.GetProcessTimes.argtypes=[wintypes.HANDLE]+[ctypes.POINTER(wintypes.FILETIME)]*4
psapi.GetProcessMemoryInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(PMC),wintypes.DWORD]
def sample(pid):
    handle=kernel.OpenProcess(0x1000|0x10,False,pid)
    if not handle:return None
    try:
        m=PMC();m.cb=ctypes.sizeof(m)
        times=[wintypes.FILETIME() for _ in range(4)]
        if not psapi.GetProcessMemoryInfo(handle,ctypes.byref(m),m.cb) or not kernel.GetProcessTimes(handle,*[ctypes.byref(x) for x in times]):return None
        cpu=sum((x.dwHighDateTime<<32|x.dwLowDateTime)/1e7 for x in times[2:])
        return dict(privateMiB=round(m.PrivateUsage/2**20,3),workingMiB=round(m.WorkingSetSize/2**20,3),cpuSeconds=cpu)
    finally:kernel.CloseHandle(handle)
pid=None
try:
    deadline=time.monotonic()+35
    while time.monotonic()<deadline:
        pid,states=status()
        if pid and states and states[-1]=='ready':break
        if p.poll() is not None:break
        time.sleep(.25)
    r.update(productPid=pid,states=states,ready=bool(pid and states and states[-1]=='ready'))
    if r['ready']:
        start=time.monotonic()
        while True:
            elapsed=time.monotonic()-start
            pid_now,states=status()
            s=sample(pid)
            if s:
                s.update(seconds=round(elapsed,2),state=states[-1] if states else None);r['samples'].append(s)
            r['states']=states;r['elapsedSeconds']=round(elapsed,2);save()
            if elapsed>=args.seconds or p.poll() is not None:break
            time.sleep(min(5,max(.05,args.seconds-elapsed)))
    if p.poll() is None and pid:
        threads={t for _,t,n in windows(pid) if n.startswith('Qt')}
        r['quitPosted']=len(threads)==1 and bool(user.PostThreadMessageW(next(iter(threads)),0x12,0,0))
    r['exitCode']=p.wait(20)
except Exception as exc:
    r['error']=type(exc).__name__
finally:
    if p.poll() is None:
        subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
        p.wait(10);r['forcedCleanup']=True
r['tempRemaining']=[x.name for x in (folder/'tmp').glob('_MEI*')]
r['profileUnchanged']=prof==digest(folder/'profile.yaml')
r['sharedCursorUnchanged']=before==digest(DEFAULT_CURSOR_PATH)
log=folder/'logs/client.log'
text=log.read_text(encoding='utf8') if log.exists() else ''
r['audioStartCount']=text.count('Audio capture started:')
r['audioStopCount']=text.count('Audio capture stopped.')
r['ledAvailable']='output available (respeaker)' in text
r['fallbackMessages']=text.count('using default')
r['errorLogCount']=sum(1 for l in text.splitlines() if '"level": "ERROR"' in l)
r['unexpectedStatesAfterReady']=[]
if 'ready' in r['states']:r['unexpectedStatesAfterReady']=[s for s in r['states'][r['states'].index('ready')+1:] if s not in ('ready','stopping','closed')]
ss=r['samples']
if len(ss)>1:
    r['resources']=dict(firstPrivateMiB=ss[0]['privateMiB'],lastPrivateMiB=ss[-1]['privateMiB'],peakPrivateMiB=max(s['privateMiB'] for s in ss),changeMiB=round(ss[-1]['privateMiB']-ss[0]['privateMiB'],3),meanCoreCpuPct=round(100*(ss[-1]['cpuSeconds']-ss[0]['cpuSeconds'])/(ss[-1]['seconds']-ss[0]['seconds']),3))
r['end']=datetime.now().astimezone().isoformat()
r['result']='PASS_SCOPED_IDLE' if r.get('ready') and r.get('elapsedSeconds',0)>=args.seconds and len(ss)>=2 and r.get('quitPosted') and r.get('exitCode')==0 and r['audioStartCount']==1 and r['ledAvailable'] and not r['unexpectedStatesAfterReady'] and not r['errorLogCount'] and r['profileUnchanged'] and r['sharedCursorUnchanged'] and not r['tempRemaining'] and not r.get('forcedCleanup') else 'INCOMPLETE_OR_FAIL'
save();print(json.dumps({k:v for k,v in r.items() if k!='samples'},indent=2),flush=True)
