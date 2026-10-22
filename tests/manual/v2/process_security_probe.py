"""Read-only security metadata for owned injection source/target processes."""
import ctypes
from ctypes import wintypes as w


def process_security(pid):
    k=ctypes.WinDLL('kernel32',use_last_error=True);a=ctypes.WinDLL('advapi32',use_last_error=True)
    k.OpenProcess.argtypes=[w.DWORD,w.BOOL,w.DWORD];k.OpenProcess.restype=w.HANDLE
    a.OpenProcessToken.argtypes=[w.HANDLE,w.DWORD,ctypes.POINTER(w.HANDLE)];a.OpenProcessToken.restype=w.BOOL
    a.GetTokenInformation.argtypes=[w.HANDLE,ctypes.c_int,w.LPVOID,w.DWORD,ctypes.POINTER(w.DWORD)];a.GetTokenInformation.restype=w.BOOL
    a.GetSidSubAuthorityCount.argtypes=[w.LPVOID];a.GetSidSubAuthorityCount.restype=ctypes.POINTER(ctypes.c_ubyte)
    a.GetSidSubAuthority.argtypes=[w.LPVOID,w.DWORD];a.GetSidSubAuthority.restype=ctypes.POINTER(w.DWORD)
    k.CloseHandle.argtypes=[w.HANDLE]
    p=k.OpenProcess(0x1000,False,pid);token=w.HANDLE()
    if not p:return dict(available=False)
    try:
        if not a.OpenProcessToken(p,8,ctypes.byref(token)):return dict(available=False)
        values={}
        for name,kind in (('integrity',25),('uiAccess',26),('appContainer',29)):
            size=w.DWORD();a.GetTokenInformation(token,kind,None,0,ctypes.byref(size));buffer=ctypes.create_string_buffer(size.value)
            if not a.GetTokenInformation(token,kind,buffer,size,ctypes.byref(size)):values[name]=None;continue
            if kind==25:
                sid=ctypes.cast(buffer,ctypes.POINTER(w.LPVOID))[0]
                values[name]=a.GetSidSubAuthority(sid,a.GetSidSubAuthorityCount(sid)[0]-1)[0]
            else:values[name]=ctypes.cast(buffer,ctypes.POINTER(w.DWORD))[0]
        return dict(available=True,**values)
    finally:
        if token:k.CloseHandle(token)
        k.CloseHandle(p)
