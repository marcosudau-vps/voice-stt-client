"""
RealtimeSTT Desktop Client – Entry Point

The regular PySide6 tray and headless diagnostics share the V2Runtime.
"""

from __future__ import annotations

import asyncio
import argparse
import inspect
import logging
import multiprocessing
import signal
import sys
from pathlib import Path
from typing import Optional

from voice_stt_client.core.config import AppConfig
from voice_stt_client.core.logging_setup import setup_logging
from voice_stt_client.core.version import __version__

logger = logging.getLogger("app")




def run_headless(config: AppConfig, observability=None) -> int:
    """Run the same V2 composition without the Qt/Win32 control surface."""
    from voice_stt_client.core.v2_runtime import V2Runtime
    from voice_stt_client.core.observability.ingress import NULL_INGRESS
    client = V2Runtime(config, observability=observability or NULL_INGRESS)
    client.on_snapshot_change = lambda view: print(
        f"V2 generation={view.generation} transport={view.transport} ready={view.ready} reason={view.reason}")

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


def _call_with_optional_observability(target, config: AppConfig, observability):
    """Call ``target(config)``, adding ``observability=`` only if it takes it.

    ``run_headless`` is replaced by test doubles with the pre-OBS-040
    one-argument signature. The capability is therefore decided by INSPECTING
    the signature — never by catching a ``TypeError`` around the call, which
    would re-run a whole client session if the exception came from inside it.
    """
    try:
        supported = "observability" in inspect.signature(target).parameters
    except (TypeError, ValueError):
        supported = False
    if supported:
        return target(config, observability=observability)
    return target(config)


def build_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="RealtimeSTT Windows Desktop Client"
    )
    parser.add_argument(
        "--config",
        type=Path,
        help=(
            "use this YAML configuration instead of the default layered "
            "configuration"
        ),
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
    parser.add_argument(
        "--verify-gui-runtime",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    parser.add_argument('--verification-output', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--verification-server', help=argparse.SUPPRESS)
    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Select the V2 GUI or headless diagnostics."""
    arguments = list(sys.argv[1:] if argv is None else argv)
    args = build_argument_parser().parse_args(arguments)
    # The release build invokes this hidden probe from the frozen executable.
    # Importing the complete GUI module catches missing or incompatible Qt
    # DLLs without starting a tray instance or touching user configuration.
    if args.verify_gui_runtime:
        from voice_stt_client.release_probe import run_probe
        run_probe(args.verification_output, args.verification_server)
        return 0

    config = AppConfig.load(args.config)

    # OBS-030 (AR-5/AR-6, FD-R4/OD-22): the manager needs config.logging, so
    # it cannot start before AppConfig.load(); its lifetime is owned here in
    # main()'s try/finally, NOT by DesktopApplication.shutdown() -- four
    # startup-abort paths never reach that, and the headless path never
    # calls it at all.
    from voice_stt_client.core.observability.manager import ObservabilityManager

    observability = ObservabilityManager(
        config.logging.observability, log_dir=config.logging.log_dir
    )

    # ARCH §6.2 asks for the try/finally "um den GESAMTEN Ablauf". Only the
    # CONSTRUCTOR stays outside it: before it returns there is no manager to
    # stop, so a failure there has nothing to clean up. Everything from
    # ``start()`` onwards is inside, because a failure in ``setup_logging``
    # used to skip ``observability.stop(2.0)`` and leave the started worker
    # unflushed (OBS-030 gate observation N-3).
    try:
        observability.start()
        setup_logging(config.logging, observability=observability)

        if args.headless:
            return _call_with_optional_observability(
                run_headless, config, observability.ingress
            )

        from voice_stt_client.ui.application import run_gui

        # OBS-040: the ingress is what every producer in the UI gets.
        # OBS-050 additionally hands over the MANAGER (readiness point N-4) --
        # the log view needs the read-only query service, the health snapshot
        # and "Diagnosehistorie loeschen". The manager's LIFETIME still stays
        # here (ARCH §6.2(b), FD-R4): the UI is handed the object and never
        # stops it.
        return run_gui(
            config,
            [sys.argv[0], *arguments],
            observability=observability.ingress,
            observability_manager=observability,
        )
    finally:
        # Runs AFTER bridge.stop(10.0), which happens inside run_gui's own
        # DesktopApplication.shutdown() before run_gui returns.
        observability.stop(2.0)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    raise SystemExit(main())
