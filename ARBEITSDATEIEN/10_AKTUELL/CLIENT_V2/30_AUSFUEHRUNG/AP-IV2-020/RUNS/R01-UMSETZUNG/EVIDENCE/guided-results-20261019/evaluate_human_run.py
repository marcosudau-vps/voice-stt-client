"""Read only an archived guided run; export metadata, never speech text or DBs."""
import json,pathlib,hashlib,gzip,sqlite3,collections,sys,shutil
from datetime import datetime,UTC
root=pathlib.Path.cwd();src=root/'build/ap-iv2-020-suite/private-archive/suite-20261019-163837-f0f7f1'
out=root/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-IV2-020/RUNS/R01-UMSETZUNG/EVIDENCE/guided-results-20261019';out.mkdir(exist_ok=True)
def save(name,value):(out/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
def sha(b):return hashlib.sha256(b).hexdigest()
r=json.loads((src/'report.json').read_text(encoding='utf8'));result=[]
for a in r['attempts']:
 p=src/a['attemptId'];rows=[json.loads(x) for x in (p/'events.jsonl').read_text(encoding='utf8').splitlines()];wire=[x for x in rows if x['type']=='wire'];mm=[x for x in rows if x['type']=='metrics'];hist=p/'client/history.sqlite';history=[];injections=[]
 if hist.exists():
  c=sqlite3.connect(hist.resolve().as_uri()+'?mode=ro',uri=True);history=c.execute('select text,event_id from history_entries order by timestamp,id').fetchall();injections=[dict(status=s,source=t,count=n) for s,t,n in c.execute('select status,source,count(*) from injection_attempts group by status,source')];c.close()
 finals=[x for x in wire if x['event']['type']=='transcription.completed'];history_matches=all(any(eid==x['event'].get('eventId') and sha(txt.encode())==x['event'].get('textSha256') for txt,eid in history) for x in finals)
 expected=[sha((txt+' ').encode()) for txt,_ in history];pastes=a.get('nativePastes',[])
 progress=[]
 for i,m in enumerate(mm):
  if i==0 or m['audioAvailable']!=mm[i-1]['audioAvailable']:progress.append(dict(timeUtc=m['timeUtc'],audioAvailable=m['audioAvailable']))
 complete=[dict(timeUtc=x['timeUtc'],**{k:v for k,v in x.items() if k in ['commandType','action','accepted','activationId','commandId']}) for x in rows if x['type']=='command.completed']
 d={k:v for k,v in a.items() if k not in ['folder','observed','editorBeforeSha256','evaluation']};d.update(wireEvents=dict(collections.Counter(x['event']['type'] for x in wire)),commands=complete,controls=[x for x in rows if x['type']=='control.received'],audioTransitions=progress,generations=sorted({x['generation'] for x in rows if x['type']=='runtime.view'}),historyFinalHashesMatch=history_matches,nativePastesMatchHistoryPlusSpace=bool(pastes) and all(x['sha256'] in expected for x in pastes),injectionAttempts=injections,followupEffectiveMs=sorted({x['event']['effectiveFollowupMs'] for x in wire if x['event'].get('effectiveFollowupMs') is not None}),scope='Historical source product7bb5646. Human acceptance is not a complete M-case PASS; corrected USB product requires new qualification.')
 if mm:d['resources']=dict(samples=len(mm),maxTasks=max(x['tasks'] for x in mm),maxPrivateBytes=max(x['memory']['privateBytes'] for x in mm),maxInjectionQueue=max(x['injectionQueue'] for x in mm),lastCapturedChunks=mm[-1]['capture']['chunks_captured'],lastSent=mm[-1]['media']['sent'])
 result.append(d);(out/(a['attemptId']+'-events.jsonl.gz')).write_bytes(gzip.compress((p/'events.jsonl').read_bytes(),mtime=0))
 if a['taskId']=='settings':
  c=sqlite3.connect((p/'client/observability.sqlite3').resolve().as_uri()+'?mode=ro',uri=True)
  save('log-observation.json',dict(recordCount=c.execute('select count(*) from logs').fetchone()[0],producers=dict(c.execute('select producer_kind,count(*) from logs group by producer_kind')),rawStored=c.execute('select count(raw_json) from logs').fetchone()[0],eventStreamStates=[json.loads(v)['state'] for (v,) in c.execute("select details_json from logs where type='client.eventstream.state_changed'")],interpretation='Server facet disabled because zero server records match; Raw absent because isolated store_raw_payload=false. Real event stream subscribing/replaying/live confirmed. No server event payload qualification.'))
  c.close()
save('attempts.json',dict(evaluatedAtUtc=datetime.now(UTC).isoformat(),target=r['target'],tasks=11,attempts=result,boundary=r['boundary'],deferred=r['deferred']))
for name in ['identity.json','operator-events.jsonl','Screenshot_test8.png']:shutil.copyfile(src/name,out/name)
(out/'evaluate_human_run.py').write_bytes(pathlib.Path(__file__).read_bytes())
save('export-manifest.json',{'files':{x.name:sha(x.read_bytes()) for x in out.iterdir() if x.name!='export-manifest.json'},'privateArchive':str(src.relative_to(root)),'privateManifestSha256':sha((src/'archive-manifest.json').read_bytes()),'rawRuntimeFilesNotCommitted':True})
print('Exported',len(result),'attempts. History/native matches:',[(x['taskId'],x['decision'],x['historyFinalHashesMatch'],x['nativePastesMatchHistoryPlusSpace']) for x in result])
