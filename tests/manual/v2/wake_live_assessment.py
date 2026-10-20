"""Assess recorded observations, never convert an operator click to a PASS."""
def assess(rows, *, expected_commit, expected_word, expected_sound, actual_sound, human_accepted):
    wire=[r for r in rows if r['type']=='wire']
    starts=[r for r in wire if r['event']['type']=='activation.started']
    hits=[r for r in wire if r['event']['type']=='wakeword.detected']
    closes=[r for r in wire if r['event']['type']=='activation.input_closed']
    completed=[r for r in wire if r['event']['type']=='activation.completed']
    hello=[r for r in rows if r['type']=='hello.accepted']
    stops=[r for r in rows if r['type']=='operator.command' and r.get('action')=='stop']
    cutoff=min((r['monotonic'] for r in stops),default=float('inf'))
    metrics=[r for r in rows if r['type']=='metrics' and r['monotonic']<=cutoff]
    closed_at=closes[0]['monotonic'] if len(closes)==1 else None
    after=[r for r in metrics if closed_at is not None and r['monotonic']>=closed_at]
    quiet=max((r['monotonic']-closed_at for r in after),default=0)
    aid=starts[0]['event'].get('activationId') if len(starts)==1 else None
    checks=dict(oneActivation=len(starts)==1,oneWake=len(hits)==1,
        selectedWakeId=len(hits)==1 and hits[0]['event'].get('wakeWordId')==expected_word,
        sameActivation=bool(aid) and len(hits)==1 and hits[0]['event'].get('activationId')==aid,
        singleTimeout=len(closes)==1 and closes[0]['event'].get('activationId')==aid
            and closes[0]['event'].get('reason')=='timed_out',
        singleTerminal=len(completed)==1 and completed[0]['event'].get('activationId')==aid,
        boundServer=len(hello)==1 and hello[0].get('serverCommit')==expected_commit,
        boundSession=len(hello)==1 and all(r['event'].get('sessionId')==hello[0]['sessionId'] for r in starts+hits+closes+completed),
        noSpeechOrFinal=not any(r['event']['type'] in ('segment.recording_started','transcription.completed') for r in wire),
        realAudio=bool(metrics) and metrics[-1].get('media',{}).get('sent',0)>100,
        continuedAudioDuringQuiet=bool(after) and all(r.get('audioAvailable') is True for r in after),
        observedFiveSeconds=quiet>=5,
        noQueuedPaste=bool(metrics) and all(r.get('injectionQueue')==0 for r in metrics),
        soundConfiguration=actual_sound is expected_sound,humanAccepted=human_accepted is True)
    status='PASS_SCOPED' if all(checks.values()) else 'FAIL'
    technical={k:v for k,v in checks.items() if k not in ('observedFiveSeconds','humanAccepted')}
    if status=='FAIL' and all(technical.values()): status='NOT_PROVEN'
    return dict(result=status,checks=checks,observedQuietSeconds=round(quiet,3),
        stopAfterCloseSeconds=round(cutoff-closed_at,3) if closed_at is not None and stops else None,
        wakeScore=hits[0]['event'].get('score') if len(hits)==1 else None,
        activationId=aid,sessionId=hello[0]['sessionId'] if len(hello)==1 else None,
        finalSentPackets=metrics[-1]['media']['sent'] if metrics else None,
        boundary='Native source microphone wake/timeout/silence and human perception only; no Frozen, negative phrase, full M02/M10 or long-run qualification')
