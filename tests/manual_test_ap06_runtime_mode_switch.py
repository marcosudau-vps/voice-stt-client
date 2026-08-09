"""Live AP06 mode-switch regression without microphone audio or text injection."""

from __future__ import annotations

import asyncio
import copy
import time

from core.config import AppConfig
from core.controller import DictationState, STTController
from core.stt_session import STTSession


class SafeAudioCapture:
    """Records lifecycle calls without opening a real microphone."""

    def __init__(self) -> None:
        self.on_audio_packet = None
        self.start_calls = 0
        self.stop_calls = 0
        self._running = False

    def start(self) -> None:
        self.start_calls += 1
        self._running = True

    def stop(self) -> None:
        self.stop_calls += 1
        self._running = False

    @property
    def is_running(self) -> bool:
        return self._running


class SafeInjectionQueue:
    """Satisfies the controller lifecycle without touching the clipboard."""

    def __init__(self) -> None:
        self.config = None
        self._running = False

    def start(self) -> None:
        self._running = True

    def stop(self, timeout=None) -> None:
        del timeout
        self._running = False

    def is_running(self) -> bool:
        return self._running

    def queue_size(self) -> int:
        return 0

    def enqueue(self, entry) -> bool:
        del entry
        raise AssertionError("Live mode-switch smoke must not inject text")


async def wait_until(predicate, timeout: float, description: str) -> None:
    deadline = asyncio.get_running_loop().time() + timeout
    while asyncio.get_running_loop().time() < deadline:
        if predicate():
            return
        await asyncio.sleep(0.05)
    raise TimeoutError(description)


async def main() -> None:
    config = AppConfig.load()
    config.history.enabled = False
    config.history.persistent.enabled = False
    config.session.mode = "hotkey"

    session = STTSession(
        config.server,
        config.session,
        require_session_contract=True,
    )
    audio = SafeAudioCapture()
    queue = SafeInjectionQueue()
    controller = STTController(
        config,
        session=session,
        audio=audio,
        injection_queue=queue,
    )
    run_task = asyncio.create_task(controller.run(), name="live-controller")
    started_at = time.monotonic()

    try:
        await wait_until(
            lambda: session.is_ready,
            config.server.hello_timeout + config.server.ready_timeout + 5,
            "Initial hotkey session did not reach READY",
        )
        print("✓ initial hotkey session READY")

        for cycle in range(1, 3):
            wake_config = copy.deepcopy(controller.config)
            wake_config.session.mode = "wake_word"
            wake_result = await controller.apply_runtime_config(wake_config)
            if not wake_result.success:
                raise AssertionError(
                    f"Cycle {cycle}: wake-word apply failed: {wake_result}"
                )
            if controller.dictation_state != DictationState.ACTIVE:
                raise AssertionError(
                    f"Cycle {cycle}: wake-word stream is not ACTIVE"
                )
            if not audio.is_running or not session.is_streaming:
                raise AssertionError(
                    f"Cycle {cycle}: wake-word stream was not armed"
                )
            if run_task.done():
                raise AssertionError(
                    f"Cycle {cycle}: Core stopped after hotkey → wake_word"
                )
            print(
                f"✓ cycle {cycle}: hotkey → wake_word, "
                f"generation={session.generation}, stream armed"
            )

            hotkey_config = copy.deepcopy(controller.config)
            hotkey_config.session.mode = "hotkey"
            hotkey_result = await controller.apply_runtime_config(hotkey_config)
            if not hotkey_result.success:
                raise AssertionError(
                    f"Cycle {cycle}: hotkey apply failed: {hotkey_result}"
                )
            if controller.dictation_state != DictationState.IDLE:
                raise AssertionError(
                    f"Cycle {cycle}: hotkey runtime is not IDLE"
                )
            if audio.is_running or session.is_streaming:
                raise AssertionError(
                    f"Cycle {cycle}: old wake-word stream remained active"
                )
            await asyncio.sleep(0.25)
            if run_task.done():
                error = run_task.exception()
                raise AssertionError(
                    f"Cycle {cycle}: Core stopped after wake_word → hotkey: "
                    f"{error}"
                )
            print(
                f"✓ cycle {cycle}: wake_word → hotkey, "
                f"generation={session.generation}, Core still alive"
            )

        print(
            "AP06 LIVE RUNTIME MODE-SWITCH REGRESSION PASSED "
            f"({time.monotonic() - started_at:.1f}s)"
        )
    finally:
        await controller.shutdown()
        await asyncio.wait_for(run_task, 10.0)


if __name__ == "__main__":
    asyncio.run(main())
