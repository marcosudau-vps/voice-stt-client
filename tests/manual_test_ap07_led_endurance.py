"""What the LED path costs while it is just sitting there.

The render loop runs at its configured rate whether or not anything is
happening, and the transport proves the link every couple of seconds. Both are
by design; the question is what they add up to over an hour of a tray
application doing nothing, and whether anything grows that should not.

Two phases, so idle and busy can be told apart:

  * idle  -- the service runs, nothing is submitted
  * busy  -- feedback arrives at a realistic pace

    python tests/manual_test_ap07_led_endurance.py --minutes 10
    python tests/manual_test_ap07_led_endurance.py --minutes 120 --sink simulator
"""

from __future__ import annotations

import argparse
import ctypes
import ctypes.wintypes as wintypes
import logging
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import LedConfig  # noqa: E402
from core.feedback_mapping import LedCall, LedVerb  # noqa: E402
from ui.led_feedback import LedFeedback  # noqa: E402

CYCLE = (
    LedCall(LedVerb.SET_STATE, target="waiting"),
    LedCall(LedVerb.SET_STATE, target="listening"),
    LedCall(LedVerb.SET_STATE, target="thinking"),
    LedCall(LedVerb.EMIT_EVENT, target="success_event", config={"duration_ms": 700}),
    LedCall(LedVerb.SET_STATE, target="ready_state"),
)


class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
    _fields_ = [
        ("cb", wintypes.DWORD),
        ("PageFaultCount", wintypes.DWORD),
        ("PeakWorkingSetSize", ctypes.c_size_t),
        ("WorkingSetSize", ctypes.c_size_t),
        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPagedPoolUsage", ctypes.c_size_t),
        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
        ("PagefileUsage", ctypes.c_size_t),
        ("PeakPagefileUsage", ctypes.c_size_t),
    ]


class FILETIME(ctypes.Structure):
    _fields_ = [("low", wintypes.DWORD), ("high", wintypes.DWORD)]

    @property
    def seconds(self) -> float:
        return ((self.high << 32) | self.low) / 1e7


_k32 = ctypes.WinDLL("kernel32", use_last_error=True)
_psapi = ctypes.WinDLL("psapi", use_last_error=True)

# Declared rather than assumed. Without these, ctypes truncates the pseudo
# handle to a 32-bit int and mangles the pointers on x64 -- every call then
# fails and every reading comes back zero, which looks exactly like a process
# that uses nothing at all. A measurement that cannot fail loudly is worse than
# no measurement, because it gets believed.
_k32.GetCurrentProcess.restype = wintypes.HANDLE
_k32.GetCurrentProcess.argtypes = []
_k32.GetProcessHandleCount.restype = wintypes.BOOL
_k32.GetProcessHandleCount.argtypes = [wintypes.HANDLE, ctypes.POINTER(wintypes.DWORD)]
_k32.GetProcessTimes.restype = wintypes.BOOL
_k32.GetProcessTimes.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
    ctypes.POINTER(FILETIME),
]
_psapi.GetProcessMemoryInfo.restype = wintypes.BOOL
_psapi.GetProcessMemoryInfo.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(PROCESS_MEMORY_COUNTERS),
    wintypes.DWORD,
]


def _checked(ok: int, what: str) -> None:
    if not ok:
        raise OSError(f"{what} failed (Windows error {ctypes.get_last_error()})")


def sample() -> dict[str, float]:
    """Working set, handles, threads and CPU seconds of this process."""
    handle = _k32.GetCurrentProcess()

    counters = PROCESS_MEMORY_COUNTERS()
    counters.cb = ctypes.sizeof(counters)
    _checked(
        _psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb),
        "GetProcessMemoryInfo",
    )

    handles = wintypes.DWORD()
    _checked(
        _k32.GetProcessHandleCount(handle, ctypes.byref(handles)),
        "GetProcessHandleCount",
    )

    creation, exited, kernel, user = FILETIME(), FILETIME(), FILETIME(), FILETIME()
    _checked(
        _k32.GetProcessTimes(
            handle,
            ctypes.byref(creation),
            ctypes.byref(exited),
            ctypes.byref(kernel),
            ctypes.byref(user),
        ),
        "GetProcessTimes",
    )

    reading = {
        "rss_mb": counters.WorkingSetSize / 1024 / 1024,
        "handles": float(handles.value),
        "threads": float(threading.active_count()),
        "cpu_s": kernel.seconds + user.seconds,
    }
    if reading["rss_mb"] <= 0 or reading["handles"] <= 0:
        raise OSError(f"implausible reading from the process counters: {reading}")
    return reading


def run_phase(
    name: str, seconds: float, feedback: LedFeedback | None, interval: float
) -> tuple[dict, dict]:
    print(f"\n--- {name}: {seconds / 60:.0f} min ---")
    print(f"{'min':>5} {'RSS MB':>8} {'Handles':>8} {'Threads':>8} {'CPU s':>8}")
    first = sample()
    latest = first
    started = time.monotonic()
    step = 0
    next_report = started

    while time.monotonic() - started < seconds:
        if feedback is not None:
            feedback.submit((CYCLE[step % len(CYCLE)],), live=True)
            step += 1
        time.sleep(interval)
        now = time.monotonic()
        if now >= next_report:
            latest = sample()
            print(
                f"{(now - started) / 60:5.1f} {latest['rss_mb']:8.1f} "
                f"{latest['handles']:8.0f} {latest['threads']:8.0f} "
                f"{latest['cpu_s']:8.1f}"
            )
            next_report = now + 60.0
    latest = sample()
    return first, latest


def report(name: str, first: dict, last: dict, seconds: float) -> list[str]:
    minutes = seconds / 60 or 1.0
    cpu = last["cpu_s"] - first["cpu_s"]
    print(
        f"  {name}: CPU {cpu:.1f}s ueber {minutes:.1f} min "
        f"= {cpu / seconds * 100:.2f}% eines Kerns"
    )
    print(
        f"  {name}: RSS {first['rss_mb']:.1f} -> {last['rss_mb']:.1f} MB "
        f"({(last['rss_mb'] - first['rss_mb']) / minutes:+.2f} MB/min)"
    )
    print(
        f"  {name}: Handles {first['handles']:.0f} -> {last['handles']:.0f}, "
        f"Threads {first['threads']:.0f} -> {last['threads']:.0f}"
    )

    problems = []
    if (last["rss_mb"] - first["rss_mb"]) / minutes > 0.5:
        problems.append(f"{name}: Speicher waechst um mehr als 0,5 MB/min")
    if last["handles"] - first["handles"] > 50:
        problems.append(f"{name}: mehr als 50 Handles dazugekommen")
    if last["threads"] - first["threads"] > 2:
        problems.append(f"{name}: Threads sind gewachsen")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minutes", type=float, default=10.0)
    parser.add_argument("--sink", default="respeaker")
    parser.add_argument("--interval", type=float, default=2.0, help="Takt im Betrieb")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")

    half = args.minutes * 60 / 2
    failures: list[str] = []
    feedback = LedFeedback(
        LedConfig(enabled=True, sink=args.sink, brightness=24),
        on_failure=failures.append,
    )
    # Start the render loop before measuring, so the idle phase measures a
    # running service rather than the cost of starting one.
    feedback.submit((LedCall(LedVerb.SET_STATE, target="ready_state"),), live=True)
    time.sleep(2.0)

    problems: list[str] = []
    try:
        first, last = run_phase("Leerlauf", half, None, 5.0)
        problems += report("Leerlauf", first, last, half)

        first, last = run_phase("Betrieb", half, feedback, args.interval)
        problems += report("Betrieb", first, last, half)
    finally:
        stopped = feedback.shutdown()

    print()
    print(f"sauber beendet : {stopped}")
    print(f"Ausfaelle      : {failures or 'keine'}")
    print(f"befund         : {problems or 'nichts waechst'}")
    return 1 if problems or not stopped else 0


if __name__ == "__main__":
    raise SystemExit(main())
