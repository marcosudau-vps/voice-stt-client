"""
Text injection management.

Handles enqueuing final transcripts and pasting them into the active foreground application
using the Windows Clipboard API and SendInput via ctypes.
"""

from __future__ import annotations

import abc
import contextlib
import ctypes
from ctypes import wintypes
from enum import Enum
import logging
import queue
import sys
import threading
import time
import uuid
from dataclasses import dataclass
from typing import List, Optional, Tuple

from core.config import AppConfig
from core.history import TranscriptHistoryManager, HistoryEntry

logger = logging.getLogger("text")

# -------------------------------------------------------------------
# SendInput Ctypes Structures (Win32)
# -------------------------------------------------------------------

# Native ULONG_PTR type (pointer-sized integer)
ULONG_PTR = ctypes.c_size_t

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]

class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [
            ("mi", MOUSEINPUT),
            ("ki", KEYBDINPUT),
            ("hi", HARDWAREINPUT),
        ]
    _fields_ = [
        ("type", wintypes.DWORD),
        ("_input", _INPUT),
    ]

INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002

def make_key_input(vk: int, flags: int) -> INPUT:
    inp = INPUT()
    inp.type = INPUT_KEYBOARD
    inp._input.ki.wVk = vk
    inp._input.ki.wScan = 0
    inp._input.ki.dwFlags = flags
    inp._input.ki.time = 0
    inp._input.ki.dwExtraInfo = 0
    return inp

# -------------------------------------------------------------------
# Queue Lifecycle States
# -------------------------------------------------------------------

class QueueState(Enum):
    NEW = "NEW"
    INITIALIZING = "INITIALIZING"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"

# -------------------------------------------------------------------
# Injection Job Model
# -------------------------------------------------------------------

@dataclass(frozen=True)
class InjectionJob:
    """An immutable container representing a pending text injection request."""
    job_id: str
    entry_id: str
    text: str
    timestamp: float

# -------------------------------------------------------------------
# Windows Backend Abstraction
# -------------------------------------------------------------------

class WindowsInjectionBackend(abc.ABC):
    """Abstraction layer for Win32 API calls to allow testing with fake backends."""

    @abc.abstractmethod
    def create_owner_window(self) -> None:
        pass

    @abc.abstractmethod
    def destroy_owner_window(self) -> None:
        pass

    @abc.abstractmethod
    def get_owner_window(self) -> int:
        pass

    @abc.abstractmethod
    def open_clipboard(self, hwnd: int) -> bool:
        pass

    @abc.abstractmethod
    def close_clipboard(self) -> bool:
        pass

    @abc.abstractmethod
    def empty_clipboard(self) -> bool:
        pass

    @abc.abstractmethod
    def is_format_available(self, format_id: int) -> bool:
        pass

    @abc.abstractmethod
    def get_clipboard_data_unicode(self) -> Optional[str]:
        pass

    @abc.abstractmethod
    def set_clipboard_data_unicode(self, text: str) -> bool:
        pass

    @abc.abstractmethod
    def get_clipboard_sequence_number(self) -> int:
        pass

    @abc.abstractmethod
    def get_foreground_window(self) -> int:
        pass

    @abc.abstractmethod
    def get_window_thread_process_id(self, hwnd: int) -> Tuple[int, int]:
        pass

    @abc.abstractmethod
    def send_input_keyboard(self, events: List[Tuple[int, bool]]) -> int:
        pass


class CtypesWindowsInjectionBackend(WindowsInjectionBackend):
    """Real implementation of the Windows backend using ctypes with full type signatures."""

    def __init__(self) -> None:
        if sys.platform != "win32":
            raise OSError("CtypesWindowsInjectionBackend is only supported on Windows.")
        
        # Load DLLs with use_last_error=True
        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        self._owner_hwnd: Optional[int] = None

        self._setup_signatures()

    def _setup_signatures(self) -> None:
        # 1. OpenClipboard
        self.user32.OpenClipboard.argtypes = [wintypes.HWND]
        self.user32.OpenClipboard.restype = wintypes.BOOL

        # 2. CloseClipboard
        self.user32.CloseClipboard.argtypes = []
        self.user32.CloseClipboard.restype = wintypes.BOOL

        # 3. EmptyClipboard
        self.user32.EmptyClipboard.argtypes = []
        self.user32.EmptyClipboard.restype = wintypes.BOOL

        # 4. GetClipboardData
        self.user32.GetClipboardData.argtypes = [wintypes.UINT]
        self.user32.GetClipboardData.restype = wintypes.HANDLE

        # 5. SetClipboardData
        self.user32.SetClipboardData.argtypes = [wintypes.UINT, wintypes.HANDLE]
        self.user32.SetClipboardData.restype = wintypes.HANDLE

        # 6. IsClipboardFormatAvailable
        self.user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
        self.user32.IsClipboardFormatAvailable.restype = wintypes.BOOL

        # 7. GetClipboardSequenceNumber
        self.user32.GetClipboardSequenceNumber.argtypes = []
        self.user32.GetClipboardSequenceNumber.restype = wintypes.DWORD

        # 8. GlobalAlloc
        self.kernel32.GlobalAlloc.argtypes = [wintypes.UINT, ctypes.c_size_t]
        self.kernel32.GlobalAlloc.restype = wintypes.HGLOBAL

        # 9. GlobalLock
        self.kernel32.GlobalLock.argtypes = [wintypes.HGLOBAL]
        self.kernel32.GlobalLock.restype = wintypes.LPVOID

        # 10. GlobalUnlock
        self.kernel32.GlobalUnlock.argtypes = [wintypes.HGLOBAL]
        self.kernel32.GlobalUnlock.restype = wintypes.BOOL

        # 11. GlobalFree
        self.kernel32.GlobalFree.argtypes = [wintypes.HGLOBAL]
        self.kernel32.GlobalFree.restype = wintypes.HGLOBAL

        # 12. GetForegroundWindow
        self.user32.GetForegroundWindow.argtypes = []
        self.user32.GetForegroundWindow.restype = wintypes.HWND

        # 13. GetWindowThreadProcessId
        self.user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]
        self.user32.GetWindowThreadProcessId.restype = wintypes.DWORD

        # 14. SendInput
        self.user32.SendInput.argtypes = [wintypes.UINT, ctypes.c_void_p, ctypes.c_int]
        self.user32.SendInput.restype = wintypes.UINT

        # 15. CreateWindowExW
        self.user32.CreateWindowExW.argtypes = [
            wintypes.DWORD, ctypes.c_wchar_p, ctypes.c_wchar_p, wintypes.DWORD,
            ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
            wintypes.HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID
        ]
        self.user32.CreateWindowExW.restype = wintypes.HWND

        # 16. DestroyWindow
        self.user32.DestroyWindow.argtypes = [wintypes.HWND]
        self.user32.DestroyWindow.restype = wintypes.BOOL

    def create_owner_window(self) -> None:
        if self._owner_hwnd is not None:
            return
        # HWND_MESSAGE is -3
        HWND_MESSAGE = ctypes.c_void_p(-3)
        hwnd = self.user32.CreateWindowExW(
            0, "STATIC", "RealtimeSTT_Owner", 0,
            0, 0, 0, 0,
            HWND_MESSAGE, None, None, None
        )
        if not hwnd:
            err = ctypes.get_last_error()
            raise OSError(f"Failed to create clipboard owner window: {ctypes.WinError(err)}")
        self._owner_hwnd = hwnd
        logger.info("Created clipboard owner window: HWND=%s", hwnd)

    def destroy_owner_window(self) -> None:
        if self._owner_hwnd:
            self.user32.DestroyWindow(self._owner_hwnd)
            logger.info("Destroyed clipboard owner window: HWND=%s", self._owner_hwnd)
            self._owner_hwnd = None

    def get_owner_window(self) -> int:
        return self._owner_hwnd or 0

    def open_clipboard(self, hwnd: int) -> bool:
        return bool(self.user32.OpenClipboard(hwnd))

    def close_clipboard(self) -> bool:
        return bool(self.user32.CloseClipboard())

    def empty_clipboard(self) -> bool:
        return bool(self.user32.EmptyClipboard())

    def is_format_available(self, format_id: int) -> bool:
        return bool(self.user32.IsClipboardFormatAvailable(format_id))

    def get_clipboard_data_unicode(self) -> Optional[str]:
        CF_UNICODETEXT = 13
        h_mem = self.user32.GetClipboardData(CF_UNICODETEXT)
        if not h_mem:
            return None
        ptr = self.kernel32.GlobalLock(h_mem)
        if not ptr:
            return None
        try:
            val = ctypes.c_wchar_p(ptr).value
            return val
        finally:
            self.kernel32.GlobalUnlock(h_mem)

    def set_clipboard_data_unicode(self, text: str) -> bool:
        CF_UNICODETEXT = 13
        GMEM_MOVEABLE = 0x0002
        encoded = text.encode("utf-16-le") + b"\x00\x00"

        h_mem = self.kernel32.GlobalAlloc(GMEM_MOVEABLE, len(encoded))
        if not h_mem:
            return False

        ptr = self.kernel32.GlobalLock(h_mem)
        if not ptr:
            self.kernel32.GlobalFree(h_mem)
            return False

        try:
            ctypes.memmove(ptr, encoded, len(encoded))
        finally:
            self.kernel32.GlobalUnlock(h_mem)

        res = self.user32.SetClipboardData(CF_UNICODETEXT, h_mem)
        if not res:
            self.kernel32.GlobalFree(h_mem)
            return False
        return True

    def get_clipboard_sequence_number(self) -> int:
        return int(self.user32.GetClipboardSequenceNumber())

    def get_foreground_window(self) -> int:
        return int(self.user32.GetForegroundWindow())

    def get_window_thread_process_id(self, hwnd: int) -> Tuple[int, int]:
        pid = wintypes.DWORD()
        tid = self.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        return int(tid), int(pid.value)

    def send_input_keyboard(self, events: List[Tuple[int, bool]]) -> int:
        inputs = []
        for vk, is_up in events:
            flags = KEYEVENTF_KEYUP if is_up else 0
            inputs.append(make_key_input(vk, flags))

        arr = (INPUT * len(inputs))(*inputs)
        res = self.user32.SendInput(len(inputs), arr, ctypes.sizeof(INPUT))
        return int(res)

# -------------------------------------------------------------------
# Clipboard Session Context Manager
# -------------------------------------------------------------------

@contextlib.contextmanager
def clipboard_session(backend: WindowsInjectionBackend, config: AppConfig, owner_hwnd: int):
    """Context manager that opens the clipboard with retries and guarantees CloseClipboard is called in finally."""
    if owner_hwnd == 0:
        raise ValueError("Clipboard session requires a valid, non-zero owner window handle.")

    restore_cfg = config.clipboard
    retries = restore_cfg.open_retries
    delay = restore_cfg.open_retry_delay_ms / 1000.0

    opened = False
    for i in range(retries):
        if backend.open_clipboard(owner_hwnd):
            opened = True
            break
        if i < retries - 1:
            time.sleep(delay)

    if not opened:
        raise OSError("Could not open clipboard after maximum retries.")

    try:
        yield
    finally:
        backend.close_clipboard()

# -------------------------------------------------------------------
# Text Injection Queue Manager
# -------------------------------------------------------------------

class TextInjectionQueue:
    """A thread-safe, serial FIFO queue that handles text injection orders."""

    def __init__(
        self,
        config: AppConfig,
        history_manager: TranscriptHistoryManager,
        backend: WindowsInjectionBackend
    ) -> None:
        self.config = config
        self.history_manager = history_manager
        self.backend = backend

        self._queue: queue.Queue[Optional[InjectionJob]] = queue.Queue()
        self._worker_thread: Optional[threading.Thread] = None
        self._state = QueueState.NEW
        self._lock = threading.Lock()
        self._init_done_event = threading.Event()
        self._init_error: Optional[Exception] = None

    def start(self) -> None:
        """Starts the background worker thread if it is not already running."""
        with self._lock:
            if self._state == QueueState.RUNNING:
                logger.info("Queue is already running.")
                return
            if self._state == QueueState.INITIALIZING:
                logger.info("Queue is currently initializing. Waiting for completion...")
            elif self._state in (QueueState.STOPPING, QueueState.STOPPED):
                if self._init_error is not None:
                    raise self._init_error
                logger.warning("Queue is stopped or stopping. Cannot restart.")
                return
            else:  # NEW
                self._state = QueueState.INITIALIZING
                self._init_done_event.clear()
                self._init_error = None

                self._worker_thread = threading.Thread(
                    target=self._worker_loop,
                    name="TextInjectionQueueWorker",
                    daemon=False  # Must NOT be a daemon thread
                )
                self._worker_thread.start()
                logger.info("Started TextInjectionQueueWorker thread. Waiting for owner initialization...")

        # Wait for initialization outside the lock
        self._init_done_event.wait()
        if self._init_error is not None:
            if (
                self._worker_thread is not None
                and self._worker_thread.is_alive()
                and self._worker_thread != threading.current_thread()
            ):
                self._worker_thread.join(timeout=2.0)
            raise self._init_error

    def stop(self, timeout: Optional[float] = None) -> None:
        """Stops the worker thread after completing currently enqueued jobs."""
        with self._lock:
            if self._state == QueueState.STOPPED:
                logger.info("Queue is already stopped.")
                return
            if self._state == QueueState.STOPPING:
                logger.info("Queue is already stopping.")
                thread_to_join = self._worker_thread
            else:
                self._state = QueueState.STOPPING
                self._queue.put(None)
                thread_to_join = self._worker_thread

        if thread_to_join is not None:
            thread_to_join.join(timeout=timeout)
            if thread_to_join.is_alive():
                logger.warning("Worker thread join timed out after %s seconds.", timeout)
            else:
                with self._lock:
                    self._state = QueueState.STOPPED
                logger.info("Worker thread stopped completely.")
        else:
            with self._lock:
                self._state = QueueState.STOPPED

    def enqueue(self, entry: HistoryEntry) -> bool:
        """
        Defensively copies necessary data and enqueues a new injection job.
        Returns True if successfully enqueued, False if rejected because stopped or not running.
        """
        with self._lock:
            if self._state != QueueState.RUNNING:
                logger.warning("Queue is not running (state=%s). Rejecting entry %s", self._state.value, entry.id)
                return False

            job = InjectionJob(
                job_id=uuid.uuid4().hex,
                entry_id=entry.id,
                text=entry.text,
                timestamp=time.time()
            )
            self._queue.put(job)
            logger.info("Enqueued job %s for entry %s", job.job_id, job.entry_id)
            return True

    def is_running(self) -> bool:
        """Checks if the worker thread is currently running and active."""
        with self._lock:
            return self._worker_thread is not None and self._worker_thread.is_alive()

    def queue_size(self) -> int:
        """Returns the number of waiting jobs currently in the queue."""
        with self._queue.mutex:
            return sum(1 for item in self._queue.queue if item is not None)

    def _worker_loop(self) -> None:
        logger.info("Worker loop started.")
        init_ok = False
        try:
            self.backend.create_owner_window()
            owner_hwnd = self.backend.get_owner_window()
            if owner_hwnd == 0:
                raise OSError("Clipboard owner window creation returned invalid HWND 0.")

            with self._lock:
                if self._state == QueueState.INITIALIZING:
                    self._state = QueueState.RUNNING
                    init_ok = True
                else:
                    logger.info("Queue state changed during initialization (state=%s). Aborting start.", self._state.value)
                    self._init_error = RuntimeError(f"Queue stopped during initialization (state={self._state.value})")
        except Exception as e:
            logger.exception("Failed to initialize worker thread: %s", e)
            self._init_error = e

        if init_ok:
            self._init_done_event.set()
        else:
            try:
                self.backend.destroy_owner_window()
            except Exception:
                logger.exception("Failed to destroy owner window during init cleanup")
            try:
                while not self._queue.empty():
                    self._queue.get_nowait()
                    self._queue.task_done()
            except Exception:
                pass
            with self._lock:
                self._state = QueueState.STOPPED
            self._init_done_event.set()
            logger.info("Worker initialization failed or aborted. Cleanup finished. Worker loop exiting.")
            return

        try:
            while True:
                try:
                    job = self._queue.get()
                    if job is None:
                        logger.info("Sentinel received. Stopping worker loop.")
                        break

                    status = "failed"
                    error_msg = "Unknown error"
                    diagnostics = {}
                    try:
                        status, error_msg, diagnostics = self._process_job(job)
                    except Exception as e:
                        logger.exception("Error processing injection job %s: %s", job.job_id, e)
                        error_msg = str(e)

                    try:
                        self.history_manager.record_injection_attempt(
                            job.entry_id, status=status, error=error_msg
                        )
                    except Exception as ex:
                        logger.exception("Failed to write status to history for entry %s: %s", job.entry_id, ex)

                    logger.info(
                        "Job %s finished. Entry: %s. Length: %d. Status: %s. Phase: %s. HWND: %s. PID: %s. Seq: %s. Events: %s.",
                        job.job_id,
                        job.entry_id,
                        diagnostics.get("text_length", 0),
                        status,
                        diagnostics.get("error_phase"),
                        diagnostics.get("hwnd"),
                        diagnostics.get("pid"),
                        diagnostics.get("seq_num"),
                        diagnostics.get("sent_events")
                    )

                except Exception as e:
                    logger.exception("Fatal unexpected exception in worker loop item: %s", e)
                finally:
                    self._queue.task_done()
        finally:
            try:
                self.backend.destroy_owner_window()
            except Exception:
                logger.exception("Failed to destroy owner window in worker loop finally")
            with self._lock:
                self._state = QueueState.STOPPED
            logger.info("Worker loop finished and state set to STOPPED.")

    def _process_job(self, job: InjectionJob) -> Tuple[str, Optional[str], dict]:
        diagnostics = {
            "job_id": job.job_id,
            "entry_id": job.entry_id,
            "text_length": len(job.text),
            "hwnd": 0,
            "pid": 0,
            "seq_num": 0,
            "sent_events": 0,
            "error_phase": None
        }

        # 1. Skip empty text
        if not job.text:
            diagnostics["error_phase"] = "validation"
            return "skipped", "Empty text", diagnostics

        restore_cfg = self.config.clipboard
        restore_previous = restore_cfg.restore_previous
        backup_text = None
        backup_success = False

        # 2. Try backing up existing clipboard unicode text
        if restore_previous:
            diagnostics["error_phase"] = "clipboard_backup"
            try:
                with clipboard_session(self.backend, self.config, self.backend.get_owner_window()):
                    CF_UNICODETEXT = 13
                    if self.backend.is_format_available(CF_UNICODETEXT):
                        data = self.backend.get_clipboard_data_unicode()
                        if data is not None:
                            byte_len = len(data.encode("utf-16-le"))
                            if byte_len <= restore_cfg.backup_max_bytes:
                                backup_text = data
                                backup_success = True
            except Exception as e:
                logger.warning("Failed to backup clipboard content (non-fatal): %s", e)

        # 3. Write target text to clipboard
        diagnostics["error_phase"] = "clipboard_write"
        clipboard_written = False
        try:
            with clipboard_session(self.backend, self.config, self.backend.get_owner_window()):
                self.backend.empty_clipboard()
                if self.backend.set_clipboard_data_unicode(job.text):
                    clipboard_written = True
                else:
                    if restore_previous and backup_success:
                        self.backend.set_clipboard_data_unicode(backup_text)
        except Exception as e:
            logger.error("Failed to write transcript text to clipboard: %s", e)
            if restore_previous and backup_success:
                try:
                    with clipboard_session(self.backend, self.config, self.backend.get_owner_window()):
                        self.backend.empty_clipboard()
                        self.backend.set_clipboard_data_unicode(backup_text)
                except Exception:
                    pass

        if not clipboard_written:
            return "failed", "Clipboard write failed", diagnostics

        # 4. Get clipboard sequence number immediately after writing
        seq_after_write = self.backend.get_clipboard_sequence_number()
        diagnostics["seq_num"] = seq_after_write

        # 5. Wait for text_injection.paste_delay_ms
        paste_delay = self.config.text_injection.paste_delay_ms / 1000.0
        time.sleep(paste_delay)

        # 6. Capture foreground window
        diagnostics["error_phase"] = "foreground_lookup"
        hwnd = self.backend.get_foreground_window()
        diagnostics["hwnd"] = hwnd
        if hwnd == 0:
            if restore_previous and backup_success:
                self._restore_clipboard(backup_text, seq_after_write)
            return "skipped", "No foreground window", diagnostics

        tid, pid = self.backend.get_window_thread_process_id(hwnd)
        diagnostics["pid"] = pid

        # 7. Simulate Ctrl+V via SendInput
        diagnostics["error_phase"] = "send_input"
        VK_CONTROL = 0x11
        VK_V = 0x56
        events = [
            (VK_CONTROL, False),
            (VK_V, False),
            (VK_V, True),
            (VK_CONTROL, True)
        ]

        send_success = False
        try:
            sent_count = self.backend.send_input_keyboard(events)
            diagnostics["sent_events"] = sent_count
            if sent_count == len(events):
                send_success = True
        except Exception as e:
            logger.exception("SendInput encountered error: %s", e)

        if not send_success:
            if restore_previous and backup_success:
                self._restore_clipboard(backup_text, seq_after_write)
            return "failed", "SendInput failed", diagnostics

        # 8. Restore previous clipboard
        diagnostics["error_phase"] = "clipboard_restore"
        if restore_previous and backup_success:
            self._restore_clipboard(backup_text, seq_after_write)

        diagnostics["error_phase"] = "history_logging"
        return "command_sent", None, diagnostics

    def _restore_clipboard(self, backup_text: Optional[str], seq_after_write: int) -> None:
        try:
            restore_cfg = self.config.clipboard
            restore_delay = restore_cfg.restore_delay_ms / 1000.0
            time.sleep(restore_delay)

            # Confirm sequence number hasn't changed
            current_seq = self.backend.get_clipboard_sequence_number()
            if current_seq != seq_after_write:
                logger.info("Clipboard was changed externally (seq %d -> %d). Restore aborted.", seq_after_write, current_seq)
                return

            with clipboard_session(self.backend, self.config, self.backend.get_owner_window()):
                self.backend.empty_clipboard()
                if backup_text is not None:
                    self.backend.set_clipboard_data_unicode(backup_text)
        except Exception as e:
            logger.error("Failed to restore previous clipboard content: %s", e)
