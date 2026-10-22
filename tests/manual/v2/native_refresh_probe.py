"""Automated native F8 -> production Controls -> real ASR/followup diagnostic.

Qt stays in the main thread, asyncio in one worker. No microphone, clipboard,
sound or server lifecycle operation. Only authorized human WAV fixtures replay.
Own successful RegisterHotKey is required before atomic SendInput impulses.
"""
import argparse
import asyncio
import ctypes
import json
import os
from pathlib import Path
import sys
import threading
import time

from tests.manual.v2.suite_plan import ROOT
from tests.manual.v2.suite_session import save
from tests.manual.v2.verify_server_fix import run_case,read_info,check_identity

KEYS = [(0x11,False),(0x10,False),(0x77,False),(0x77,True),(0x10,True),(0x11,True)]


def owned_releases(sent):
    held=[]
    for key,up in KEYS[:sent]:
        if up:
            if key in held:held.remove(key)
        else:held.append(key)
    return [(key,True) for key in reversed(held)]


def assess_native(calls):
    return (len(calls)==6 and [c['phase'] for c in calls]==['idle','followup_wait','followup_wait']*2
        and all(c['slot']=='primary' and c['source']=='WM_HOTKEY' for c in calls)
        and all(c['activationId'] and c['activationId']==calls[i-1]['activationId']
            for i,c in enumerate(calls) if i%3==2)
        and all(calls[i]['activationId'] is None for i in (0,3))
        and all(calls[i][key]==calls[i//3*3][key] for i in range(6) for key in ('generation','sessionId')))


def same_context(expected,view):
    return expected==(view.generation,view.session_id,str(view.input.phase),view.input.activation_id)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--expected-server-commit',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if sys.platform!='win32':raise RuntimeError('Windows required')
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'build').resolve()):raise ValueError('Output must stay in project build')
    out.mkdir(parents=True,exist_ok=True)
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtCore import QObject,Signal,QTimer
    from PySide6.QtWidgets import QApplication
    from voice_stt_client.ui.hotkeys import V2HotkeyManager
    from voice_stt_client.ui.single_instance import SingleInstanceGuard
    from voice_stt_client.core.v2_controls import ControlConfig
    from voice_stt_client.core.text_injector import make_key_input,INPUT
    app=QApplication.instance() or QApplication([])
    guard=SingleInstanceGuard(r'Local\VoiceSTT_Qualification_AP_IV2_020')
    if not guard.acquire().acquired:raise RuntimeError('Qualification client still running')
    class Dispatch(QObject):request=Signal(object)
    dispatch=Dispatch();calls=[];errors=[];state={};done=threading.Event()
    user32=ctypes.WinDLL('user32',use_last_error=True)
    user32.SendInput.argtypes=[ctypes.c_uint,ctypes.POINTER(INPUT),ctypes.c_int]
    user32.SendInput.restype=ctypes.c_uint
    user32.GetAsyncKeyState.argtypes=[ctypes.c_int]
    user32.GetAsyncKeyState.restype=ctypes.c_short
    def send(events):
        values=(INPUT*len(events))(*(make_key_input(key,2 if up else 0) for key,up in events))
        return user32.SendInput(len(values),values,ctypes.sizeof(INPUT))
    def reject(request,error):
        def finish():
            if not request['future'].done():request['future'].set_exception(error)
        request['loop'].call_soon_threadsafe(finish)
    def impulse(request):
        state['request']=request
        if any(user32.GetAsyncKeyState(key)&0x8000 for key in (0x10,0x11,0x12,0x5B,0x5C,0x77)):
            reject(request,RuntimeError('Physical modifier/F8 held; no synthetic input sent'))
            return
        sent=send(KEYS)
        if sent!=len(KEYS):
            releases=owned_releases(sent)
            if releases:send(releases)
            reject(request,RuntimeError('Partial SendInput; own held keys released'))
    dispatch.request.connect(impulse)
    def native_control(slot):
        request=state.get('request')
        if not request or request.get('handled'):
            errors.append('unexpected_or_duplicate_native_callback')
            return
        request['handled']=True
        async def apply():
            view=request['mirror'].mirror.view
            if request['future'].done():
                errors.append('late_native_callback_after_timeout')
                return
            if not same_context(request['context'],view):
                request['future'].set_exception(RuntimeError('Native request session/generation/phase changed'))
                return
            calls.append(dict(source='WM_HOTKEY',slot=str(slot),phase=str(view.input.phase),
                generation=view.generation,sessionId=view.session_id,activationId=view.input.activation_id))
            try:
                result=await request['controls'].press(slot)
                if not request['future'].done():request['future'].set_result(result)
            except Exception as error:
                if not request['future'].done():request['future'].set_exception(error)
        asyncio.run_coroutine_threadsafe(apply(),request['loop'])
    manager=V2HotkeyManager(ControlConfig(primary_key='Ctrl+Shift+F8',secondary_key='',
        wake_pause_key='',reinsert_last_key='',overlay_toggle_key=''),on_control=native_control,application=app)
    async def press(controls,mirror,slot):
        loop=asyncio.get_running_loop();future=loop.create_future()
        view=mirror.mirror.view
        context=(view.generation,view.session_id,str(view.input.phase),view.input.activation_id)
        dispatch.request.emit(dict(loop=loop,future=future,controls=controls,mirror=mirror,context=context))
        return await asyncio.wait_for(future,10)
    async def qualify():
        from scripts.qualify_v2_real import identity
        before=await asyncio.to_thread(read_info)
        if not check_identity(before,args.expected_server_commit):raise ValueError('Selected complete server identity mismatch')
        result=dict(identity=identity(),infoBefore=before,rows=[])
        for name in ('negative_speech','alexa_direct'):
            row=await run_case(name,'control_refresh',None,'natural',args.expected_server_commit,press_control=press)
            result['rows'].append(row)
            if row['result']!='PASS_SCOPED':break
        after=await asyncio.to_thread(read_info)
        result.update(infoAfter=after,nativeCalls=calls,nativeErrors=errors,
            scope='Real Windows SendInput/RegisterHotKey/WM_HOTKEY/Qt -> asyncio Controls -> real TLS ASR and followup; authorized fixture replay/digital silence, no live microphone or paste',
            result='PASS_SCOPED' if before==after and len(result['rows'])==2 and all(r['result']=='PASS_SCOPED' for r in result['rows'])
                and assess_native(calls) and not errors else 'FAIL')
        save(out/'result.json',result)
        state['exit']=0 if result['result']=='PASS_SCOPED' else 1
        print(json.dumps(dict(result=result['result'],nativeCallbacks=len(calls),cases=len(result['rows']))),flush=True)
    def worker():
        async def run():
            state['loop']=asyncio.get_running_loop();state['task']=asyncio.current_task()
            await qualify()
        try:asyncio.run(run())
        except BaseException as error:
            save(out/'error.json',dict(result='FAIL',errorType=type(error).__name__,nativeCalls=calls))
            state['exit']=1
        finally:done.set()
    thread=None;started=time.monotonic()
    try:
        if not manager.register():raise RuntimeError('F8 occupied; no input sent')
        thread=threading.Thread(target=worker,name='native-refresh-core')
        thread.start()
        def tick():
            if done.is_set():app.quit()
            elif time.monotonic()-started>900 and state.get('task'):
                state['loop'].call_soon_threadsafe(state['task'].cancel)
        timer=QTimer();timer.timeout.connect(tick);timer.start(50)
        app.exec()
    finally:
        manager.unregister();guard.release()
        if thread is not None:
            if not done.is_set() and state.get('task'):state['loop'].call_soon_threadsafe(state['task'].cancel)
            thread.join(5)
            if thread.is_alive():raise RuntimeError('Native probe worker did not stop')
    return state.get('exit',1)


if __name__=='__main__':raise SystemExit(main())
