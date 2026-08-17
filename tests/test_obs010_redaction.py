"""
Contract tests for ``core.observability.redaction`` (OBS-010).

Frozen source: ``LOGGING_CONTRACTS_FREEZE_V1.md`` §4 (R-3, R-8, R-9, R-10,
R-11, R-12), FD-C11, FD-C12. The security-relevant cases (N-01, N-02, and
the real ``hello`` payload evidence) live here or in the evidence script.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from types import MappingProxyType
from urllib.parse import urlsplit

from core.observability.redaction import (
    MAX_DEPTH,
    MAX_NODES,
    SENSITIVE_KEYS,
    TRANSCRIPT_KEYS,
    redact_mapping,
    redact_text,
    shorten_user_paths,
    unfreeze,
)


class TestUnfreezeN01(unittest.TestCase):
    """N-01 — the most important single test of this package: a real-style
    ``EventProtocolResult.payload`` (MappingProxyType with nested tuples AND a
    frozenset) must survive ``unfreeze()`` + ``json.dumps`` as a JSON OBJECT,
    must contain neither "mappingproxy(" nor "frozenset(", and the
    key-based redaction must work afterwards."""

    def _payload(self):
        return MappingProxyType({
            "type": "log.event",
            "replay": False,
            "event": MappingProxyType({
                "schemaVersion": 1,
                "eventId": "evt-1",
                "cursor": 5,
                "channel": "transcription",
                "event": "transcription.completed",
                "data": MappingProxyType({
                    "text": "beliebiger Diktattext",
                    "accessToken": "gel8eimer-wert",
                    "tags": ("a", "b", frozenset({"c", "d"})),
                }),
                "revisions": ("r1", "r2"),
            }),
        })

    def test_unfreeze_yields_json_object_without_frozen_reprs(self):
        payload = self._payload()
        unfrozen = unfreeze(payload)
        self.assertIsInstance(unfrozen, dict)
        serialized = json.dumps(unfrozen)
        self.assertNotIn("mappingproxy(", serialized)
        self.assertNotIn("frozenset(", serialized)
        self.assertIn("accessToken", serialized)  # raw payload still complete

    def test_frozenset_becomes_sorted_list(self):
        payload = MappingProxyType({"tags": frozenset({"b", "a", "c"})})
        unfrozen = unfreeze(payload)
        self.assertEqual(unfrozen["tags"], ["a", "b", "c"])

    def test_key_based_redaction_works_after_unfreeze(self):
        payload = self._payload()
        unfrozen = unfreeze(payload)
        redacted = redact_mapping(unfrozen)
        text = json.dumps(redacted)
        self.assertIsInstance(redacted, dict)
        self.assertNotIn("gel8eimer-wert", text)
        self.assertEqual(
            redacted["event"]["data"]["accessToken"], "[redacted]"
        )
        self.assertNotIn("beliebiger Diktattext", text)
        self.assertIn(
            f"[redacted:{len('beliebiger Diktattext')} chars]", text
        )

    def test_unfreeze_does_not_mutate_input(self):
        payload = self._payload()
        unfreeze(payload)
        self.assertIsInstance(payload, MappingProxyType)

    def test_unfreeze_guards_throwing_repr(self):
        class BadObj:
            def __str__(self):
                raise RuntimeError("no str")

            def __repr__(self):
                raise RuntimeError("no repr")

        result = unfreeze({"x": BadObj()})
        self.assertEqual(result["x"], "<unrenderable>")


class TestSensitiveKeysR3(unittest.TestCase):
    def test_key_rule_normalizes_case_underscore_and_dash(self):
        keys = ("accessToken", "access_token", "ACCESS-TOKEN",
                "authorization", "adminKey", "password", "secret", "cookie",
                "credential")
        for key in keys:
            with self.subTest(key=key):
                result = redact_mapping({key: "geheim"})
                self.assertEqual(result[key], "[redacted]")

    def test_sensitive_keys_set_has_exactly_the_frozen_names(self):
        self.assertEqual(
            SENSITIVE_KEYS,
            frozenset({"authorization", "token", "accesstoken", "apikey",
                       "adminkey", "password", "secret", "cookie",
                       "credential"}),
        )

    def test_nested_in_lists_and_dicts_all_replaced(self):
        payload = {
            "config": {
                "auth": {"authorization": "Bearer abc", "token": "t1"},
                "list": [
                    {"accessToken": "in-list"},
                    ["adminKey", {"password": "deep"}],
                ],
            },
        }
        result = redact_mapping(payload)
        text = json.dumps(result)
        for secret in ("Bearer abc", "t1", "in-list", "deep"):
            self.assertNotIn(secret, text)
        self.assertEqual(result["config"]["auth"]["authorization"], "[redacted]")
        self.assertEqual(result["config"]["list"][0]["accessToken"], "[redacted]")
        self.assertEqual(result["config"]["list"][1][1]["password"], "[redacted]")


class TestTranscriptKeysR10(unittest.TestCase):
    def test_all_transcript_keys_redacted_with_char_count(self):
        keys = ("text", "displayText", "rawText", "stableText",
                "unstableText", "committedStableText", "visualUnstableText")
        self.assertEqual(
            TRANSCRIPT_KEYS,
            frozenset(keys),
        )
        payload = {key: "Diktatinhalt-fuer-Test" for key in keys}
        payload.update({"other": "bleibt"})
        result = redact_mapping(payload, store_transcription_content=False)
        for key in keys:
            self.assertEqual(
                result[key],
                f"[redacted:{len('Diktatinhalt-fuer-Test')} chars]",
                key,
            )
        self.assertEqual(result["other"], "bleibt")

    def test_transcription_content_true_keeps_text(self):
        result = redact_mapping(
            {"text": "sichtbar", "accessToken": "x"},
            store_transcription_content=True,
        )
        self.assertEqual(result["text"], "sichtbar")
        self.assertEqual(result["accessToken"], "[redacted]")

    def test_text_in_nested_server_data_is_redacted(self):
        payload = {"event": {"data": {"displayText": "geheim", "id": 3}}}
        result = redact_mapping(payload, store_transcription_content=False)
        self.assertEqual(
            result["event"]["data"]["displayText"], "[redacted:6 chars]"
        )


class TestRedactTextN02(unittest.TestCase):
    """N-02 — R-10 also redacts unstructured log text, verified against the
    real production lines ("Final [seg=%s]: %s", "... existing=%r, new=%r").
    """

    def test_final_line_is_redacted(self):
        text = "Final [seg=12]: hier steht der diktierte satz"
        redacted = redact_text(text, store_transcription_content=False)
        self.assertNotIn("hier steht der diktierte satz", redacted)
        self.assertIn(f"[redacted:{len('hier steht der diktierte satz')} chars]",
                      redacted)
        self.assertTrue(redacted.startswith("Final [seg=12]: "))

    def test_realtime_line_is_redacted(self):
        redacted = redact_text("Realtime [seg=3]: zwischentext",
                               store_transcription_content=False)
        self.assertNotIn("zwischentext", redacted)
        self.assertIn("[redacted:12 chars]", redacted)

    def test_existing_new_conflict_line_is_redacted(self):
        existing = repr("ursprünglicher Text existing")
        new = repr("neu gelieferter Text")
        text = f"Contradictory duplicate final event for ('session', 3): existing={existing}, new={new}"
        redacted = redact_text(text, store_transcription_content=False)
        self.assertNotIn("ursprünglicher Text existing", redacted)
        self.assertNotIn("neu gelieferter Text", redacted)
        self.assertIn("existing=", redacted)
        self.assertIn("new=", redacted)
        self.assertIn(
            f"[redacted:{len('ursprünglicher Text existing')} chars]",
            redacted,
        )
        self.assertIn(
            f"[redacted:{len('neu gelieferter Text')} chars]",
            redacted,
        )

    def test_transcription_content_true_keeps_unstructured_text(self):
        text = "Final [seg=12]: bleibt stehen"
        self.assertEqual(
            redact_text(text, store_transcription_content=True), text
        )


class TestUrlAndPathRules(unittest.TestCase):
    def test_url_loses_query_and_fragment_but_keeps_host_path(self):
        url = "https://stt.voice.marcosudau.com/ws/logs?token=abc&x=1#frag"
        result = redact_mapping({"target_url": url})
        self.assertEqual(
            result["target_url"], "https://stt.voice.marcosudau.com/ws/logs"
        )

    def test_plain_strings_are_unchanged(self):
        result = redact_mapping({"note": "kein url, kein geheimnis"})
        self.assertEqual(result["note"], "kein url, kein geheimnis")

    def test_embedded_url_inside_text_is_sanitized(self):
        redacted = redact_text(
            "connecting to wss://host/ws/logs?accessToken=sekret demo"
        )
        self.assertNotIn("accessToken=sekret", redacted)
        self.assertIn("wss://host/ws/logs", redacted)

    def test_user_profile_path_shortened_to_tilde(self):
        home = str(Path.home())
        path = home + r"\AppData\Local\RealtimeSTT Client\logs"
        self.assertEqual(
            shorten_user_paths(path), r"~\AppData\Local\RealtimeSTT Client\logs"
        )

    def test_path_shortening_works_inside_tracebacks(self):
        home = str(Path.home())
        traceback = (
            "Traceback (most recent call last):\n"
            f'  File "{home}\\some_module.py", line 4, in <module>\n'
            "RuntimeError"
        )
        redacted_tb = shorten_user_paths(traceback)
        self.assertNotIn(home, redacted_tb)
        self.assertIn('"~\\some_module.py"', redacted_tb)

    def test_path_shortening_with_explicit_profile(self):
        profile = Path(r"C:\Users\tester")
        path = r"C:\Users\tester\AppData\Roaming\led"
        self.assertEqual(
            shorten_user_paths(path, user_profile=profile),
            r"~\AppData\Roaming\led",
        )
        # Case-insensitive, forward-slash variant works too.
        self.assertEqual(
            shorten_user_paths(r"c:\users\TESTER\logs", user_profile=profile),
            r"~\logs",
        )

    def test_url_split_consistent_with_rule_r8(self):
        stripped = redact_mapping({"u": "https://a.b/c?p=q#f"})["u"]
        self.assertEqual(urlsplit(stripped).query, "")
        self.assertEqual(urlsplit(stripped).fragment, "")


class TestRedactBoundsR12(unittest.TestCase):
    def test_cyclic_mapping_terminates_and_is_marked(self):
        cyclic = {}
        cyclic["self"] = cyclic
        result = redact_mapping(cyclic)
        self.assertIn("_truncated", _find_marker(result))

    def test_node_limit_is_enforced(self):
        wide = {"k%04d" % i: i for i in range(MAX_NODES + 100)}
        result = redact_mapping(wide)
        self.assertIn("_truncated", _find_marker(result))

    def test_depth_limit_is_enforced(self):
        deep = {"l0": {"l1": {"l2": {"l3": {"l4": {"l5": {"l6": {"l7": {
            "leaf": 1}}}}}}}}}
        # Recurse far below the default MAX_DEPTH (16).
        level = deep
        for _ in range(30):
            level["next"] = {"leaf": 1}
            level = level["next"]
        result = redact_mapping(deep)
        marker = _find_marker(result)
        self.assertIn("_truncated", marker)

    def test_unfreeze_bounds_also_limit(self):
        deep = {"a": {"b": {"c": {"d": {"e": {"f": {"g": {"h": 1}}}}}}}}
        result = unfreeze(deep, max_depth=3)
        marker = _find_marker(result)
        self.assertIn("_truncated", marker)


class TestLeafFallbackR11(unittest.TestCase):
    def test_json_output_is_already_serializable(self):
        class NotJsonable:
            pass

        result = redact_mapping({"value": NotJsonable()})
        self.assertIsInstance(json.dumps(result), str)

    def test_throwing_str_and_repr_do_not_propagate(self):
        class BadObj:
            def __str__(self):
                raise RuntimeError("str broke")

            def __repr__(self):
                raise RuntimeError("repr broke")

        result = redact_mapping({"bad": BadObj()})
        self.assertEqual(result["bad"], "<unrenderable>")


def _find_marker(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "_truncated" and item is True:
                return value
            found = _find_marker(item)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = _find_marker(item)
            if found is not None:
                return found
    return None


if __name__ == "__main__":
    unittest.main()