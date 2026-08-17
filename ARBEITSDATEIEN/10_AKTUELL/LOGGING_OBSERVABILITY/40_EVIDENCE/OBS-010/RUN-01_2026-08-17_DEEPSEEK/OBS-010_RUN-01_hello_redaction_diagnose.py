# -*- coding: utf-8 -*-
"""
OBS-010 Evidence diagnostics: real ``hello`` structure through redaction.

Dieses Skript liegt ausserhalb des Produkt-Repository-Codes (unter
ARBEITSDATEIEN .../40_EVIDENCE) und schickt die reale ``hello``-Struktur aus
der Serverdokumentation durch den OBS-010-Redaction-/Normalizer-Pfad. Es
belegt, dass ``accessToken`` auf keiner Ebene mehr im Ergebnis erscheint
(R-6 Whitelist, FD-C11, FD-C12).

Lauf:
    python OBS-010_RUN-01_hello_redaction_diagnose.py
Exitcode 0 = Erwartung erfuellt, 1 = Befund.

Referenz "reale Struktur": server-docs-for-client-development/
04-server-events-katalog-und-chronologie.md (Abschnitt ``hello``).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[6]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core.observability.normalizer import from_server_result
from core.observability.redaction import redact_mapping, unfreeze
from core.event_protocol import EventProtocolProcessor, EventStreamAccess
from core.session_coordinator import SessionContext

ACCESS_TOKEN = "ADMIN-SESSION-TOKEN-9371"


def real_hello() -> dict:
    """Struktur aus der Serverdokumentation (04-..., Abschnitt hello)."""
    return {
        "type": "hello",
        "clientId": "browser-client-42",
        "sessionId": "7cb1…",
        "settings": {"language": "de", "wake_word_enabled": True},
        "sessionConfig": {
            "version": 1,
            "requestedWakeWordEnabled": True,
            "effectiveWakeWordEnabled": True,
            "effectiveWakeWordBackend": "openwakeword",
            "effectiveWakeWords": ["hey_jarvis"],
            "source": "session",
            "fallbacks": [],
            "ignoredFields": [],
            "warnings": [],
        },
        "limits": {"maxSessions": 8, "maxActiveSpeakers": 4},
        "supportedEngines": ["faster_whisper", "kroko_onnx"],
        "runtimeSettings": {"activeSessionSafe": ["max_sessions"],
                            "newSessionOnly": ["wake_words"],
                            "startupOnly": ["model"]},
        "logAccess": {
            "available": True,
            "websocketPath": "/ws/logs",
            "historyPath": "/api/logs/events",
            "accessToken": ACCESS_TOKEN,
            "sessionId": "7cb1…",
            "expiresAt": "2026-07-31T14:26:41.537Z",
            "logProtocolVersion": 2,
            "deliveryMode": "sqlite_first",
            "replayAvailable": True,
            "serverInstanceId": "c25…",
            "oldestCursor": 1,
            "latestCursor": 18427,
        },
    }


def check(name: str, condition: bool) -> bool:
    print(("PASS  " if condition else "FAIL  ") + name)
    return condition


def main() -> int:
    failures = 0

    hello_payload = real_hello()

    # 1) Generische Redaction ueber den kompletten Payload.
    unfrozen = unfreeze(hello_payload)
    redacted = redact_mapping(unfrozen)
    blob = json.dumps(redacted)
    failures += not check(
        "redact_mapping(unfreeze(hello)) enthaelt accessToken nicht",
        ACCESS_TOKEN not in blob,
    )
    failures += not check(
        "Ergebnis ist ein JSON-Objekt (kein default=str-Kollaps)",
        isinstance(redacted, dict) and blob.startswith("{"),
    )
    failures += not check(
        "MappingProxyType/tuple/frozenset-Reprs fehlen",
        "mappingproxy(" not in blob and "frozenset(" not in blob,
    )

    # 2) Der OBS-010-Normalizer behandelt einen log.hello-Controlframe ueber
    #    die R-6-Whitelist (raw=None, Token nie in details).
    payload_log_hello = {
        "type": "log.hello",
        "schemaVersion": 1,
        "logProtocolVersion": 2,
        "deliveryMode": "sqlite_first",
        "replayAvailable": True,
        "serverInstanceId": "server-1",
        "oldestCursor": 0,
        "latestCursor": 20,
        "retentionCursor": 0,
        "logAccess": hello_payload["logAccess"],
        "sessionConfig": hello_payload["sessionConfig"],
        "sessionCapabilities": {"version": 1},
    }
    processor = EventProtocolProcessor(
        EventStreamAccess(
            endpoint="wss://stt.voice.marcosudau.com/ws/logs",
            session_id="session-1",
            access_token="session-secret-token",
            server_instance_id="server-1",
            oldest_cursor=0,
            latest_cursor=20,
            channels=("transcription",),
        )
    )
    processor.begin_subscription()
    result = processor.process_mapping(payload_log_hello)
    context = SessionContext(session_id="session-1", generation=7)
    record = from_server_result(
        context, result, client_instance_id="client-instance-1"
    )
    failures += not check(
        "from_server_result(log.hello) erzeugt einen Record",
        record is not None,
    )
    blob_record = repr(record)
    failures += not check(
        "Der Record enthaelt den accessToken auf keiner Ebene",
        ACCESS_TOKEN not in blob_record
        and "accessToken" not in json.dumps(dict(record.details), default=str),
    )
    failures += not check(
        "hello wird NIE raw gespeichert (R-6)",
        record.raw is None,
    )
    failures += not check(
        "Whitelist-Felder sind erhalten (logAccess.available / serverInstanceId)",
        dict(record.details["logAccess"])["available"] is True
        and dict(record.details["logAccess"])["serverInstanceId"] == "c25…",
    )

    print()
    if failures:
        print(f"{failures} Befund(e).")
        return 1
    print("Alle Erwartungen erfuellt. accessToken ist in keinem Ergebnispfad.")
    return 0


if __name__ == "__main__":
    sys.exit(main())