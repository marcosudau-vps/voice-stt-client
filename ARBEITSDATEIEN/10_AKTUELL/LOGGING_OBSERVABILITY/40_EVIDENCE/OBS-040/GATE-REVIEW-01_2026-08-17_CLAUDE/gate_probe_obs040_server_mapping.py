from __future__ import annotations
import tempfile, time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from core.event_cursor_store import EventCursorStore
from core.event_models import EventConnectionState
from core.event_protocol import EventProtocolProcessor
from core.observability.ingress import ObservabilityIngress
from core.observability.adapters.server_live import ServerLiveAdapter
from core.observability.models import RecordPriority
from core.session_coordinator import SessionContext
from tests.test_obs040_server_live_adapter import (
    access, event_frame, hello_frame, replay_completed_frame, subscribed_frame, gap_frame)

fail=[]
def chk(n, ok, d=""):
    print(("[PASS] " if ok else "[FAIL] ")+n+(" — "+d if d else ""))
    if not ok: fail.append(n)

with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as d:
    tmp=Path(d)
    proc=EventProtocolProcessor(access(), cursor_store=EventCursorStore(tmp/"c.json"))
    proc.begin_subscription()
    ing=ObservabilityIngress(instance_id="inst-1", queue_size=512)
    ad=ServerLiveAdapter(ing)
    ctx=SessionContext(generation=7, session_id="session-1", log_access=access(),
                       event_state=EventConnectionState.LIVE,
                       token_expires_at=datetime.now(timezone.utc)+timedelta(hours=1))
    r_hello=proc.process_mapping(hello_frame()); ad(ctx,r_hello)
    r_sub=proc.process_mapping(subscribed_frame(0)); ad(ctx,r_sub)
    r_rc=proc.process_mapping(replay_completed_frame(0,0)); ad(ctx,r_rc)
    r_ev=proc.process_mapping(event_frame(5,"evt-5",replay=False)); ad(ctx,r_ev)
    proc.confirm_event(r_ev)
    r_gap=proc.process_mapping(gap_frame(6,9)); ad(ctx,r_gap)
    recs=ing.drain(50,0.1)
    by={r.type:r for r in recs}
    print("types:", [r.type for r in recs])
    ev=[r for r in recs if r.type=="transcription.completed"][0]
    chk("§3.2 EVENT mapping", (
        ev.producer_kind=="server" and ev.producer_id=="voice-stt-server"
        and ev.instance_id=="server-1" and ev.channel=="transcription"
        and ev.level=="INFO" and ev.component=="transcription"
        and ev.session_id=="session-1" and ev.generation==7
        and ev.activation_id=="act-9" and ev.segment_id==7
        and isinstance(ev.segment_id,int)
        and ev.transcription_id=="session-1:3:7" and ev.event_id=="evt-5"
        and ev.server_cursor==5 and ev.message=="Transkription abgeschlossen"
        and ev.replayed is False and ev.scope=="session"
        and ev.source_timestamp=="2026-08-09T12:00:00Z"),
        f"component={ev.component} msg={ev.message!r} act={ev.activation_id} seg={ev.segment_id} scope={ev.scope}")
    chk("§8.2 raw is the frozen reference, not a copy",
        ev.raw is r_ev.payload, f"raw is payload: {ev.raw is r_ev.payload}")
    ctrl=[r for r in recs if r.type and r.type.startswith("client.eventstream.")]
    chk("§3.2 CONTROL mapping", all(
        c.producer_kind=="client" and c.producer_id=="voice-stt-client"
        and c.instance_id=="inst-1" and c.channel=="system"
        and c.component=="eventstream" for c in ctrl),
        f"{[(c.type,c.component,c.level,c.channel) for c in ctrl]}")
    hello=[c for c in ctrl if c.type=="client.eventstream.hello"]
    chk("R-6 hello never carries raw", bool(hello) and hello[0].raw is None,
        f"raw={None if not hello else hello[0].raw}")
    tok = "session-secret" 
    import json
    blob=json.dumps([[r.type, dict(r.details or {}), (dict(r.raw) if r.raw else None), r.message] for r in recs], default=str)
    chk("no token in any observed record", "another-session-secret" not in blob and "session-secret-token" not in blob)
    gap=[c for c in ctrl if c.type=="client.eventstream.gap"]
    chk("gap record with cursor range and WARNING", bool(gap) and gap[0].level=="WARNING"
        and gap[0].details.get("lostFromCursor")==6 and gap[0].details.get("lostToCursor")==9,
        f"{gap[0].level if gap else None} {dict(gap[0].details) if gap else None}")
    chk("priority: live event HIGH", ev.priority is RecordPriority.HIGH, str(ev.priority))
print()
print("FAILED:",fail if fail else "none")
