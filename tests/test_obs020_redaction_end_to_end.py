"""
OBS-020 end-to-end redaction verification through the new ingress/handler
pipeline (WP-OBS-020 Tests: "Redaction von Secrets", "Erhalt nicht sensibler
Struktur", "Audio-Payload-Abwehr", "Transcript-Policy").

Redaction rules R-1..R-12 themselves are implemented and unit-tested in
OBS-010 (``core/observability/redaction.py``, ``tests/test_obs010_redaction.py``).
OBS-020 adds no new redaction logic (WP-OBS-020 title correction: "Redaction
und Normalizer liegen in OBS-010"). What OBS-020 must prove is that its own
new components — ``ObservabilityIngress`` and ``UnifiedLogHandler`` — do not
bypass or weaken those guarantees anywhere on the new path from a raw
``logging.LogRecord``/structured client event through to the record handed
to ``submit()``.
"""

from __future__ import annotations

import functools
import logging
import unittest
from typing import Any, List, Optional

from core.observability.adapters.python_logging import UnifiedLogHandler
from core.observability.health import LoggingInternalHealth
from core.observability.ingress import ObservabilityIngress
from core.observability.models import CanonicalLogRecord
from core.observability.normalizer import from_log_record


class RecordingIngress:
    def __init__(self) -> None:
        self.health = LoggingInternalHealth()
        self.submitted: List[CanonicalLogRecord] = []

    def submit(self, record: Any) -> bool:
        self.submitted.append(record)
        return True


def build_normalizer(store_transcription_content=False):
    return functools.partial(
        from_log_record,
        instance_id="i" * 32,
        store_transcription_content=store_transcription_content,
        user_profile=None,
    )


def emit(handler: UnifiedLogHandler, msg: str, extra: Optional[dict] = None,
         level=logging.WARNING) -> None:
    record = logging.LogRecord("controller", level, "mod.py", 1, msg, None, None)
    for key, value in (extra or {}).items():
        record.__dict__[key] = value
    handler.emit(record)


class TestSecretsAreRedactedEndToEnd(unittest.TestCase):
    def test_token_in_extra_detail_is_redacted_through_the_handler(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        emit(handler, "auth attempt", extra={
            "detail": {"accessToken": "super-secret-token-value", "ok": True},
        })
        record = ingress.submitted[0]
        detail = dict(record.details["detail"])
        self.assertEqual(detail["accessToken"], "[redacted]")
        self.assertNotIn("super-secret-token-value", repr(dict(record.details)))

    def test_authorization_header_style_key_is_redacted(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        emit(handler, "outbound request", extra={
            "detail": {"headers": {"Authorization": "Bearer abc.def.ghi"}},
        })
        record = ingress.submitted[0]
        headers = dict(dict(record.details["detail"])["headers"])
        self.assertEqual(headers["Authorization"], "[redacted]")
        self.assertNotIn("abc.def.ghi", repr(dict(record.details)))


class TestNonSensitiveStructureIsPreserved(unittest.TestCase):
    def test_non_sensitive_keys_survive_untouched(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        emit(handler, "session update", extra={
            "detail": {
                "session_state": "connected",
                "retry_count": 3,
                "endpoint": "wss://example.invalid/ws/transcribe",
            },
        })
        record = ingress.submitted[0]
        detail = dict(record.details["detail"])
        self.assertEqual(detail["session_state"], "connected")
        self.assertEqual(detail["retry_count"], 3)
        # R-8: query/fragment stripped, but scheme/host/path survive.
        self.assertTrue(detail["endpoint"].startswith("wss://example.invalid/ws/transcribe"))


class TestAudioPayloadIsNeverReachable(unittest.TestCase):
    """CONTRACTS §4.4: "Audioinhalt: kein Weg gefunden -- nur Byte- und
    Framezahlen werden geloggt." OBS-020 must not open a new path. The
    architectural defense is that the hot-path audio functions (ARCH §8.6)
    never call ``submit``/``ingress``/``logging`` at all -- verified here by
    scanning those functions' source for any such call, exactly like the
    non-blocking invariant is verified by source inspection elsewhere in this
    suite."""

    def test_hot_path_audio_functions_never_reference_the_ingress(self):
        import inspect

        from core.audio_capture import AudioCapture

        for name in ("_audio_callback", "_process_loop"):
            with self.subTest(function=name):
                if not hasattr(AudioCapture, name):
                    continue
                source = inspect.getsource(getattr(AudioCapture, name))
                self.assertNotIn("ingress", source)
                self.assertNotIn(".submit(", source)
                self.assertNotIn("logging.", source)

    def test_a_defensive_bytes_payload_would_never_be_stored_verbatim(self):
        """Even if a caller misused ``extra`` with a raw byte blob (which no
        production call site does), the redaction leaf fallback never yields
        the raw bytes object -- only a guarded string form."""
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        pcm_like = bytes(range(256)) * 4  # 1024 bytes, arbitrary binary content
        emit(handler, "misuse guard", extra={"detail": {"payload": pcm_like}})
        record = ingress.submitted[0]
        stored = dict(record.details["detail"])["payload"]
        self.assertIsInstance(stored, str)
        self.assertNotIsInstance(stored, (bytes, bytearray))


class TestTranscriptPolicyEndToEnd(unittest.TestCase):
    def test_final_line_is_char_count_only_by_default(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer(
            store_transcription_content=False,
        ))
        emit(handler, "Final [seg=1]: der geheime Transkriptinhalt",
             level=logging.INFO)
        record = ingress.submitted[0]
        self.assertNotIn("geheime", record.message)
        self.assertIn("[redacted:", record.message)
        self.assertIn(str(len("der geheime Transkriptinhalt")), record.message)

    def test_final_line_is_kept_verbatim_when_opted_in(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer(
            store_transcription_content=True,
        ))
        emit(handler, "Final [seg=1]: der geheime Transkriptinhalt",
             level=logging.INFO)
        record = ingress.submitted[0]
        self.assertIn("der geheime Transkriptinhalt", record.message)

    def test_transcript_keys_in_details_respect_the_same_policy(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer(
            store_transcription_content=False,
        ))
        emit(handler, "final received", extra={
            "detail": {"text": "vertraulicher Text hier", "segment": 1},
        })
        record = ingress.submitted[0]
        detail = dict(record.details["detail"])
        self.assertNotIn("vertraulicher", detail["text"])
        self.assertIn("[redacted:", detail["text"])
        self.assertEqual(detail["segment"], 1)


class TestNoMutationOfInputData(unittest.TestCase):
    def test_extra_mapping_passed_by_the_caller_is_not_mutated(self):
        ingress = RecordingIngress()
        handler = UnifiedLogHandler(ingress, build_normalizer())
        original_detail = {"accessToken": "keep-me-untouched"}
        emit(handler, "check mutation", extra={"detail": original_detail})
        self.assertEqual(original_detail, {"accessToken": "keep-me-untouched"})


if __name__ == "__main__":
    unittest.main()
