"""The whole chain, against the real server, with the real ring.

Everything else is checked against doubles: the reducer against scripted facts,
the LED path against a fake controller or a simulator, the transport against a
scripted socket. This is the one that uses none of them. It connects to the
configured server, dictates once, and records which canonical events actually
arrived and what each of the three channels was asked to do.

Needs a reachable server and somebody to speak. It changes nothing and writes
nothing; it only watches.

    python tests/manual_test_ap07_end_to_end.py
    python tests/manual_test_ap07_end_to_end.py --seconds 20 --no-led
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.config import AppConfig, LedConfig  # noqa: E402
from core.controller import STTController  # noqa: E402
from core.feedback_reducer import FeedbackDecision  # noqa: E402
from ui.led_feedback import LedFeedback  # noqa: E402


def server_is_up(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return response.status == 200, f"HTTP {response.status}"
    except urllib.error.HTTPError as exc:
        return False, f"HTTP {exc.code}"
    except Exception as exc:
        return False, f"{type(exc).__name__}: {exc}"


async def run(config: AppConfig, seconds: float, led: LedFeedback | None) -> int:
    seen: list[tuple[float, str, str, str, str]] = []
    transcripts: list[str] = []
    started = time.monotonic()

    controller = STTController(config)

    def observe(decision: FeedbackDecision) -> None:
        event = decision.event.event_type.value if decision.event else "-"
        rule = decision.rule
        leds = " ".join(
            f"{call.verb.value}:{call.target or call.slot}" for call in rule.led
        ) or "-"
        seen.append(
            (
                round(time.monotonic() - started, 1),
                event,
                leds,
                rule.sound.cue.value if rule.sound else "-",
                rule.app.action.value if rule.app else "-",
            )
        )
        if led is not None:
            led.submit(rule.led, live=decision.impulse is not None)

    controller.on_feedback_decision = observe
    controller.on_text = lambda seg, text, final: (
        transcripts.append(text) if final else None
    )

    task = asyncio.create_task(controller.run())
    print("  warte auf Verbindung ...")
    for _ in range(int(30 / 0.5)):
        await asyncio.sleep(0.5)
        if controller.session.is_connected:
            break
    if not controller.session.is_connected:
        print("  ABBRUCH: keine Verbindung zum Server.")
        await controller.shutdown()
        task.cancel()
        return 1

    print("  verbunden.\n")
    print("=" * 62)
    print(f"  BITTE JETZT DIKTIEREN — {seconds:.0f} Sekunden")
    print("=" * 62 + "\n")

    await controller.start_dictation()
    await asyncio.sleep(seconds)
    await controller.stop_dictation()
    await asyncio.sleep(4.0)

    await controller.shutdown()
    task.cancel()
    try:
        await task
    except (asyncio.CancelledError, Exception):
        pass

    print(f"\n{'Zeit':>6}  {'Ereignis':34} {'LED':28} {'Ton':9} App")
    print("-" * 100)
    for moment, event, leds, sound, app in seen:
        print(f"{moment:6.1f}  {event:34} {leds:28} {sound:9} {app}")

    kanaele = {
        "LED": any(row[2] != "-" for row in seen),
        "Ton": any(row[3] != "-" for row in seen),
        "In-App": any(row[4] != "-" for row in seen),
    }
    server_events = {row[1] for row in seen if row[1].startswith("server.")}

    print()
    print(f"Entscheidungen      : {len(seen)}")
    print(f"Serverereignisse    : {sorted(server_events) or 'KEINE'}")
    print(f"Transkripte         : {transcripts or 'keine'}")
    for name, fired in kanaele.items():
        print(f"Kanal {name:8}      : {'ausgeloest' if fired else 'NICHT ausgeloest'}")

    fehlt = [n for n, f in kanaele.items() if not f]
    if not server_events:
        print("\nBEFUND: keine Serverereignisse — die Kette wurde nicht bewiesen.")
        return 1
    if fehlt:
        print(f"\nBEFUND: {', '.join(fehlt)} blieb stumm. Regeln pruefen.")
        return 1
    print("\nBEFUND: alle drei Kanaele sind aus echten Serverereignissen gelaufen.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seconds", type=float, default=12.0)
    parser.add_argument("--no-led", action="store_true", help="Ring nicht ansteuern")
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    config = AppConfig.load()

    up, detail = server_is_up(config.server.health_url)
    print(f"Server {config.server.health_url}: {detail}")
    if not up:
        print("\nDer Server ist nicht erreichbar. Test uebersprungen — er beweist")
        print("nichts ueber den Client, solange die Gegenstelle fehlt.")
        return 2

    led = None
    if not args.no_led:
        led = LedFeedback(LedConfig(**{**vars(config.led), "enabled": True}))
        led.verify_targets(config.feedback_mappings.led_targets())
        print("Katalog geprueft, Ring aktiv.")

    try:
        return asyncio.run(run(config, args.seconds, led))
    finally:
        if led is not None:
            led.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
