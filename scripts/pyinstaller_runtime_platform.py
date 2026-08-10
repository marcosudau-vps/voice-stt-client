"""Avoid Python 3.12 WMI platform probes before frozen app imports."""

import platform
import sys


if sys.platform == "win32":
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
