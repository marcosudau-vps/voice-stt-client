"""
RealtimeSTT Desktop Client – Entry Point

AP06 provides the regular PySide6 tray application. The proven AP05 headless
client remains available through ``--headless`` for diagnostics.
"""

from __future__ import annotations

import asyncio
import argparse
import logging
import multiprocessing
import signal
import sys
from typing import Optional

from core.config import AppConfig
from core.logging_setup import setup_logging
from core.stt_session import STTSession, TransportState, ClientState
from core.audio_capture import AudioCapture
from core.history import TranscriptHistoryManager
from core.text_injector import TextInjectionQueue, WindowsInjectionBackend
from core.reinsertion import TranscriptReinsertionService
from core.controller import STTController
from core.version import __version__

logger = logging.getLogger("app")


class RealtimeSTTClient(STTController):
    """
    Orchestrates the client components by extending STTController
    and providing Phase 1 headless console output handlers.
    """

    def __init__(
        self,
        config: AppConfig,
        session: Optional[STTSession] = None,
        audio: Optional[AudioCapture] = None,
        history_manager: Optional[TranscriptHistoryManager] = None,
        injection_queue: Optional[TextInjectionQueue] = None,
        reinsertion_service: Optional[TranscriptReinsertionService] = None,
        backend: Optional[WindowsInjectionBackend] = None,
    ):
        super().__init__(
            config,
            session=session,
            audio=audio,
            history_manager=history_manager,
            injection_queue=injection_queue,
            reinsertion_service=reinsertion_service,
            backend=backend,
        )

        # Wire up console callbacks
        self.on_text = self._on_text
        self.on_transport_change = self._on_transport_change

        # Initial dictation request for headless diagnostics
        self.request_initial_auto_start()

    # -------------------------------------------------------------------
    # Console Output Callbacks
    # -------------------------------------------------------------------

    def _on_text(self, segment_id: int, text: str, is_final: bool) -> None:
        """Called when a new or updated transcript segment arrives."""
        prefix = "✓ FINAL" if is_final else "⟳ realtime"
        print(f"  [{prefix}] seg={segment_id}: {text}")

    def _on_transport_change(self, new_state: TransportState) -> None:
        """Called when the transport state changes."""
        indicators = {
            TransportState.DISCONNECTED: "🔴",
            TransportState.CONNECTING: "🟡",
            TransportState.ADMITTED: "🟡",
            TransportState.READY: "🟢",
            TransportState.ERROR: "🔴",
        }
        indicator = indicators.get(new_state, "⚪")
        print(f"\n{indicator} Transport: {new_state.name}")

    def _on_state_change(self, state: ClientState) -> None:
        """Called on every state update."""
        pass  # Headless mode: transport_change handles the console output

    # -------------------------------------------------------------------
    # Main run loop
    # -------------------------------------------------------------------

    async def run(self) -> None:
        """Start all components and run until interrupted."""
        print("═" * 60)
        print("  RealtimeSTT Desktop Client (AP05 Self-Healing Core)")
        print(f"  Server: {self.config.server.url}")
        print("═" * 60)
        print()

        await super().run()


def run_headless(config: AppConfig) -> int:
    """Run the retained AP05 console client for diagnostics."""
    client = RealtimeSTTClient(config)

    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print("\n\nInterrupted – shutting down...")
        if client._loop and client._loop.is_running():
            client._loop.call_soon_threadsafe(
                lambda: asyncio.create_task(client.shutdown())
            )

    signal.signal(signal.SIGINT, signal_handler)

    # Run the async event loop
    try:
        asyncio.run(client.run())
    except (KeyboardInterrupt, asyncio.CancelledError):
        pass
    return 0


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RealtimeSTT Windows Desktop Client"
    )
    parser.add_argument(
        "--headless",
        action="store_true",
        help="run the diagnostic console client without PySide6 tray UI",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Select the regular AP06 GUI or the retained headless diagnostics."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = build_argument_parser().parse_args(arguments)
    config = AppConfig.load()

    # OBS-030 (AR-5/AR-6, FD-R4/OD-22): the manager needs config.logging, so
    # it cannot start before AppConfig.load(); its lifetime is owned here in
    # main()'s try/finally, NOT by DesktopApplication.shutdown() -- four
    # startup-abort paths never reach that, and the headless path never
    # calls it at all.
    from core.observability.manager import ObservabilityManager

    observability = ObservabilityManager(
        config.logging.observability, log_dir=config.logging.log_dir
    )
    observability.start()
    setup_logging(config.logging, observability=observability)

    try:
        if args.headless:
            return run_headless(config)

        from ui.application import run_gui

        return run_gui(config, [sys.argv[0], *arguments])
    finally:
        # Runs AFTER bridge.stop(10.0), which happens inside run_gui's own
        # DesktopApplication.shutdown() before run_gui returns.
        observability.stop(2.0)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
