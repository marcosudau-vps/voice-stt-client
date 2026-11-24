import json,sqlite3,collections
from pathlib import Path
root=Path(__file__).parent
old=Path(r'C:\Users\marco\OneDrive\Desktop\Voice-STT-Client-V2-Finalabnahme\Nachweise\Folge-20261123-203715')/'Testprofil'
db=old/'observability.sqlite3'
con=sqlite3.connect(db.as_uri()+'?mode=ro',uri=True)
cols=[r[1] for r in con.execute('pragma table_info(logs)')]
print('cols',cols)
counts=con.execute('select type,count(*) from logs group by type order by count(*) desc').fetchall()
print('types',counts)
allow={'state','reason','error_type','errorType','generation','retry_delay','delay','status','code','closeCode','close_code','source','eventType','category','transport','failure_category','message_type','reason_code','previous_state','attempt','is_ready'}
rows=[]
for row in con.execute('select * from logs order by id'):
    d=dict(zip(cols,row));kind=d.get('type') or ''
    if not any(t in kind for t in ('transport','health','reconnect','error','failure','audio','led','session')):continue
    try:details=json.loads(d.get('details_json') or '{}')
    except ValueError:continue
    reduced={k:v for k,v in details.items() if k in allow and isinstance(v,(str,int,float,bool,type(None)))}
    if 'transport' in kind or 'health' in kind or 'failure' in kind or 'error' in kind or 'reconnect' in kind:
        rows.append(dict(type=kind,timestamp=d.get('timestamp') or d.get('ts') or d.get('occurred_at'),details=reduced))
logcounts=collections.Counter()
for line in (old/'logs/client.log').read_text(encoding='utf8',errors='replace').splitlines():
    try:r=json.loads(line)
    except ValueError:continue
    msg=r.get('msg','')
    if 'using default' in msg:logcounts['old_misleading_fallback']+=1
    if r.get('level') in ('WARNING','ERROR'):logcounts['level_'+r['level']]+=1
report=dict(scope='historical guided run evidence read-only; safe event fields only',typeCounts=counts,transportHealthRows=rows,logCounts=dict(logcounts))
(root/'historical-transport-analysis.json').write_text(json.dumps(report,indent=2),encoding='utf8')
print(json.dumps(dict(logCounts=dict(logcounts),transportHealthRows=rows),indent=2))
