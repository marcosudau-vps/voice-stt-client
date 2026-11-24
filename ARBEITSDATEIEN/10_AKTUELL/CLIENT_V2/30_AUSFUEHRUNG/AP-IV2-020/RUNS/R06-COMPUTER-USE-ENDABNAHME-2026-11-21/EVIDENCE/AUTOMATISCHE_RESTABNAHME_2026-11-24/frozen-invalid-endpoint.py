import os,sys,uuid,hashlib,json,subprocess,time
from pathlib import Path
from datetime import datetime
root=Path(__file__).parent
folder=root/('frozen-invalid-'+uuid.uuid4().hex[:8])
folder.mkdir();(folder/'tmp').mkdir()
os.environ.update(VOICESTT_CLIENT_HOME=str(folder/'client'),VOICESTT_CLIENT_CONFIG=str(folder/'profile.yaml'),TEMP=str(folder/'tmp'),TMP=str(folder/'tmp'),QT_QPA_PLATFORM='windows')
from voice_stt_client.core.config import AppConfig,DEFAULT_CONFIG_PATH
from voice_stt_client.core.v2_profile import V2Profile
from dataclasses import asdict
from voice_stt_client.core.event_cursor_store import DEFAULT_CURSOR_PATH
config=AppConfig._load_single(DEFAULT_CONFIG_PATH)
config.server.url='wss://final.v2.voice-stt-server.marcosudau.com/ws/invalid-r06'
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
r=dict(scope='corrected onefile EXE normal GUI entry, invalid V2 route, deliberately disabled input and hotkeys, no production writes',start=datetime.now().astimezone().isoformat(),folder=folder.name,exeSha256=digest(exe))
p=subprocess.Popen([str(exe),'--config',str(folder/'profile.yaml')],cwd=folder,env=os.environ.copy())
try:r['exitCode']=p.wait(30)
except subprocess.TimeoutExpired:
    r['timeout']=True
    subprocess.run(['taskkill','/PID',str(p.pid),'/T','/F'],capture_output=True)
    p.wait(10)
r['tempRemaining']=[x.name for x in (folder/'tmp').glob('_MEI*')]
r['profileUnchanged']=prof==digest(folder/'profile.yaml')
r['sharedCursorUnchanged']=before==digest(DEFAULT_CURSOR_PATH)
r['logFiles']=[x.name for x in (folder/'logs').glob('*') if x.is_file()]
raw='\n'.join(x.read_text(encoding='utf8',errors='replace') for x in (folder/'logs').glob('*.log'))
r['invalidHttpOriginLogged']='invalid_http_origin' in raw
r['fatalCoreLogged']='Core konnte nicht gestartet werden' in raw or 'Core thread terminated' in raw
r['end']=datetime.now().astimezone().isoformat()
r['result']='PASS_SCOPED_REJECTED_NOT_RECOVERABLE_UI' if r.get('exitCode',0)!=0 and r['invalidHttpOriginLogged'] and r['profileUnchanged'] and r['sharedCursorUnchanged'] and not r['tempRemaining'] else 'INCOMPLETE_OR_FAIL'
(root/'frozen-invalid-endpoint.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print(json.dumps(r,indent=2),flush=True)
