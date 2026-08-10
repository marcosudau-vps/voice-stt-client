"""Make PyInstaller's isolated child interpreters deterministic on Windows."""

import platform


platform.system = lambda: "Windows"
platform.machine = lambda: "AMD64"
platform.win32_ver = lambda *args, **kwargs: (
    "11",
    "",
    "",
    "Multiprocessor Free",
)
platform._get_machine_win32 = lambda: "AMD64"
platform._Processor.get = lambda: "AMD64"
