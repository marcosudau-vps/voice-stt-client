"""Real Windows registration collision in two owned processes; no key input."""
import argparse,ctypes,json,subprocess,sys
from ctypes import wintypes


def registration():
    api=ctypes.WinDLL('user32',use_last_error=True)
    api.RegisterHotKey.argtypes=[wintypes.HWND,ctypes.c_int,wintypes.UINT,wintypes.UINT]
    api.RegisterHotKey.restype=wintypes.BOOL
    api.UnregisterHotKey.argtypes=[wintypes.HWND,ctypes.c_int];api.UnregisterHotKey.restype=wintypes.BOOL
    ctypes.set_last_error(0);ok=bool(api.RegisterHotKey(None,0x4A71,0x4000|1|2|4,0x87))
    return api,ok,ctypes.get_last_error()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--child',action='store_true',help=argparse.SUPPRESS)
    args=parser.parse_args()
    api,ok,error=registration()
    try:
        if args.child:
            print(json.dumps(dict(acquired=ok,error=error)))
            return 0
        if not ok:
            print(json.dumps(dict(result='NOT_RUN_KEY_OCCUPIED',error=error)));return 2
        child=subprocess.run([sys.executable,'-m','tests.manual.v2.native_collision_probe','--child'],capture_output=True,text=True,timeout=15)
        observed=json.loads(child.stdout)
        result='PASS_SCOPED' if child.returncode==0 and not observed['acquired'] and observed['error']==1409 else 'FAIL'
        print(json.dumps(dict(result=result,parentAcquired=True,child=observed,
            key='Ctrl+Alt+Shift+F24',scope='Real separate-process Windows hotkey collision. No generated input, existing key takeover or foreign registration removal.')))
        return 0 if result=='PASS_SCOPED' else 1
    finally:
        if ok:api.UnregisterHotKey(None,0x4A71)


if __name__=='__main__':raise SystemExit(main())
