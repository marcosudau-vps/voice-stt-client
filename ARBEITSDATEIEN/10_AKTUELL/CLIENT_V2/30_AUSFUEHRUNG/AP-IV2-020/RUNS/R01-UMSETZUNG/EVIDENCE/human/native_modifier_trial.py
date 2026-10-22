"""Physical Ctrl+Shift+F9 release -> actual product queue -> owned Qt editor.

No microphone, model, synthetic modifier or foreign target. Every attempt needs
its own Start and is stored before the operator chooses Repeat or Accept.
"""
import argparse
import atexit
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import sys
import threading
import time
import uuid

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0,str(ROOT))
from tests.manual.v2.editor_state import owned_editor_path, read_editor_state, operator_started
from tests.manual.v2.stepped_wake_trial import requested

TEXT='Modifiertastenprobe erfolgreich.'
STEPS=[
    'Ablauf lesen · nur Tastentest, nichts sprechen · dann Start',
    'Native Testqueue vorbereiten · bitte warten',
    'Bereitmachen · Countdown abwarten',
    'Strg+Umschalt+F9 zusammen kurz drücken',
    'Alle Tasten wieder loslassen',
    'Automatische Einfügung abwarten · im Testfenster bleiben',
    'Testqueue wird beendet · bitte warten',
    'Ergebnis prüfen · Wiederholen oder Übernehmen',
]


def verdict(aborted,held_seen,native_match):
    return ('ABORTED_BY_OPERATOR' if aborted else 'PASS' if held_seen and native_match
            else 'NOT_PROVEN' if native_match else 'FAIL')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state',type=Path,required=True)
    parser.add_argument('--evidence',type=Path,required=True)
    parser.add_argument('--prepare-seconds',type=int,default=8)
    parser.add_argument('--self-check',action='store_true')
    args=parser.parse_args()
    if not 0 <= args.prepare_seconds <= 30:parser.error('prepare-seconds must be 0..30')
    if args.self_check:
        assert len(STEPS)==8 and all(isinstance(s,str) and s for s in STEPS)
        assert requested(dict(requestTaskId='old',requestAction='abort'),'new',('abort',)) is None
        assert verdict(True,True,True)=='ABORTED_BY_OPERATOR'
        assert verdict(False,True,True)=='PASS'
        assert verdict(False,False,True)=='NOT_PROVEN'
        assert verdict(False,True,False)=='FAIL'
        print('PASS: explicit native-only steps and attempt guard; no OS input/audio')
        return 0
    local=Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    state_path=owned_editor_path(args.state,local)
    os.environ['VOICESTT_CLIENT_HOME']=str(local/'client')
    args.evidence.mkdir(parents=True,exist_ok=False)
    from voice_stt_client.core.config import AppConfig
    from voice_stt_client.core.history import TranscriptHistoryManager
    from voice_stt_client.core.text_injector import TextInjectionQueue,CtypesWindowsInjectionBackend
    from scripts.qualify_v2_real import identity
    from voice_stt_client.ui.hotkeys import CtypesHotkeyBackend,parse_hotkey
    # Reserve, never steal, this known test chord. No control is dispatched;
    # the physical state is read only while the armed owned editor has focus.
    hotkeys=CtypesHotkeyBackend();spec=parse_hotkey('Ctrl+Shift+F9');key_id=0x5D41
    hotkeys.register(0,key_id,spec.modifiers,spec.virtual_key)
    atexit.register(lambda:hotkeys.unregister(0,key_id))

    def control(value):
        path=state_path.parent/'command.json'
        temporary=path.with_suffix('.modifier.tmp')
        temporary.write_text(json.dumps(value),encoding='utf8');temporary.replace(path)
        end=time.monotonic()+5
        while path.exists():
            if time.monotonic()>end:raise TimeoutError('Own editor did not consume command')
            time.sleep(.03)
    def read():return read_editor_state(state_path)
    def save(name,value):
        path=args.evidence/name
        if path.exists():raise FileExistsError('Preserve previous attempt evidence')
        path.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    for number in range(1,101):
        task_id=f'{args.evidence.name}-attempt-{number:03d}'
        control(dict(action='prepare',taskId=task_id,case='native',steps=STEPS,restoreOnStart='',
            phrase='Erwartete Einfügung: '+TEXT,buttonText=f'Tastentest starten – Versuch {number}',
            text='NATIVE TASTENPROBE – NICHTS SPRECHEN'))
        while not operator_started(read(),task_id):time.sleep(.1)
        initial=read();expected_pid=initial['pid']
        transitions=[];sends=[];counter=[0];last=[None]

        def focused():
            value=read()
            return operator_started(value,task_id) and value['pid']==expected_pid
        class Native(CtypesWindowsInjectionBackend):
            def get_foreground_window(self):
                hwnd=super().get_foreground_window()
                _,pid=self.get_window_thread_process_id(hwnd)
                return hwnd if pid==expected_pid and focused() else 0
            def get_pressed_modifiers(self):
                keys=super().get_pressed_modifiers()
                if threading.current_thread().name=='TextInjectionQueueWorker':
                    counter[0]+=1
                    if keys != last[0]:
                        transitions.append(dict(keys=list(keys),timeUtc=datetime.now(UTC).isoformat(),monotonic=time.monotonic()))
                        last[0]=keys
                return keys
            def send_input_keyboard(self,events):
                keys=super().get_pressed_modifiers()
                if not self.get_foreground_window() or keys:
                    sends.append(dict(testGuardRejected=True,keys=list(keys)));return 0
                count=super().send_input_keyboard(events)
                sends.append(dict(testGuardRejected=False,keys=list(keys),sentEvents=count,monotonic=time.monotonic()))
                return count
        config=AppConfig();config.history.persistent.enabled=False
        config.clipboard.restore_previous=True
        backend=Native();history=TranscriptHistoryManager(config.history)
        queue=TextInjectionQueue(config,history,backend)
        done=threading.Event();attempts=[]
        def completed(value):
            attempts.append(dict(status=value.status,error=value.error,source=value.source));done.set()
        queue.on_attempt_result=completed
        aborted=False
        entry=None
        try:
            queue.start()
            control(dict(action='progress',taskId=task_id,step=2,seconds=args.prepare_seconds,text='BEREITMACHEN – NOCH NICHT DRÜCKEN'))
            end=time.monotonic()+args.prepare_seconds
            while time.monotonic()<end:
                if requested(read(),task_id,('abort',)):aborted=True;break
                time.sleep(.05)
            if not aborted:
                control(dict(action='progress',taskId=task_id,step=3,text='JETZT STRG+UMSCHALT+F9 KURZ DRÜCKEN UND LOSLASSEN'))
                while True:
                    if requested(read(),task_id,('abort',)):aborted=True;break
                    if (focused() and {0x10,0x11}.issubset(backend.get_pressed_modifiers())
                            and backend.user32.GetAsyncKeyState(0x78) & 0x8000):break
                    time.sleep(.005)
            if not aborted:
                ids=[str(uuid.uuid4()) for _ in range(4)]
                entry=history.add_entry_with_status(ids[0],ids[2],TEXT,protocol_version=2,
                    activation_id=ids[1],segment_sequence=1,event_id=ids[3],event_seq=1).entry
                if entry is None or not queue.enqueue_reserved(entry):raise RuntimeError('Native test admission failed')
                control(dict(action='progress',taskId=task_id,step=4,text='ALLE TASTEN WIEDER LOSLASSEN'))
                end=time.monotonic()+6
                while not done.wait(.02):
                    if requested(read(),task_id,('abort',)):
                        aborted=True;queue.stop(timeout=2);break
                    if time.monotonic()>end:raise TimeoutError('Native outcome unknown; no automatic retry')
                control(dict(action='progress',taskId=task_id,step=6,text='TESTQUEUE WIRD BEENDET'))
        finally:
            queue.stop(timeout=2)
        time.sleep(.5)
        after=read()
        held_seen=any(t['keys'] for t in transitions)
        native_match=after['testText']==TEXT+' ' and len(sends)==1 and sends[0].get('sentEvents')==4 and attempts==[dict(status='command_sent',error=None,source='automatic')] and not queue._worker_thread.is_alive()
        passed=not aborted and held_seen and native_match
        held_start=next((t['monotonic'] for t in transitions if t['keys']),None)
        release=next((t['monotonic'] for t in transitions if not t['keys'] and held_start is not None and t['monotonic']>=held_start),None)
        result=dict(result=verdict(aborted,held_seen,native_match),taskId=task_id,
            identity=identity(),helperSha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            editorAdapterSha256=hashlib.sha256(Path(__file__).with_name('native_modifier_editor.py').read_bytes()).hexdigest(),
            physicalModifierObservedByProductWorker=held_seen,workerQueries=counter[0],transitions=transitions,
            nativeSend=sends,attempts=attempts,actualCharacters=after['characters'],actualSha256=after['sha256'],
            expectedCharacters=len(TEXT+' '),expectedSha256=hashlib.sha256((TEXT+' ').encode()).hexdigest(),
            workerStopped=not queue._worker_thread.is_alive(),
            heldToReleaseMs=round((release-held_start)*1000,3) if release is not None else None,
            authoritativeTextPreserved=entry.text==TEXT if entry else None,
            origin=dict(entryId=entry.id,sessionId=entry.session_id,activationId=entry.activation_id,
                segmentId=entry.segment_id,eventId=entry.event_id,segmentSequence=entry.segment_sequence) if entry else None,
            boundaries='Human physical Ctrl+Shift+F9, actual native key-state/Clipboard/SendInput/product queue; own armed editor. No synthetic key events, microphone, ASR or server. Not a complete M-case qualification.')
        filename=f'attempt-{number:03d}.json';save(filename,result)
        if aborted:continue
        control(dict(action='review',taskId=task_id,acceptText='Versuch übernehmen / Testblock abschließen',
            text=('NATIVE PROBE BESTANDEN – TEXT PRÜFEN' if passed else 'GEHALTENE TASTEN NICHT ERFASST – BITTE WIEDERHOLEN' if native_match else 'PROBE NICHT BESTANDEN – BITTE WIEDERHOLEN ODER MELDEN')))
        while True:
            decision=requested(read(),task_id,('repeat','accept'))
            if decision:break
            time.sleep(.1)
        save(f'decision-{number:03d}.json',dict(taskId=task_id,decision=decision,evidence=filename))
        if decision=='accept':
            control(dict(action='complete',text='FERTIG – TESTQUEUE BEENDET · BITTE IM CHAT MELDEN'))
            hotkeys.unregister(0,key_id)
            return 0
    raise RuntimeError('100 explicit attempts reached; no automatic further test')


if __name__=='__main__':raise SystemExit(main())
