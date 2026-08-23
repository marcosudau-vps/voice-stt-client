"""
Tests for ``core.observability.sinks.jsonl_file.JsonlSink`` (OBS-030,
CONTRACTS §11.1: FD-D4 - JSONL only).
"""

from __future__ import annotations

import json
import tempfile
import unittest
import uuid
from datetime import datetime, timezone
from pathlib import Path

from core.observability.models import CanonicalLogRecord
from core.observability.sinks.jsonl_file import JsonlSink, SCHEMA_VERSION


def _iso() -> str:
    now = datetime.now(timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S") + f".{now.microsecond // 1000:03d}Z"


def make_record(**overrides) -> CanonicalLogRecord:
    fields = dict(
        record_id=uuid.uuid4().hex,
        received_at=_iso(),
        producer_kind="client",
        producer_id="voice-stt-client",
        instance_id="i" * 32,
        scope="instance",
        channel="system",
        level="INFO",
        replayed=False,
        type=None,
    )
    fields.update(overrides)
    return CanonicalLogRecord(**fields)


class TestJsonlSinkPositive(unittest.TestCase):
    def test_write_batch_creates_one_line_per_record_with_schema_version_first(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = JsonlSink(Path(tmp))
            records = [make_record(message=f"m{i}") for i in range(3)]
            sink.write_batch(records)
            sink.close()

            files = list(Path(tmp).glob("*.jsonl"))
            self.assertEqual(len(files), 1)
            lines = files[0].read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 3)
            for line, record in zip(lines, records):
                parsed = json.loads(line)
                self.assertEqual(list(parsed.keys())[0], "schemaVersion")
                self.assertEqual(parsed["schemaVersion"], SCHEMA_VERSION)
                self.assertEqual(parsed["record_id"], record.record_id)
                self.assertEqual(parsed["message"], record.message)

    def test_details_and_raw_are_json_objects_not_strings(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = JsonlSink(Path(tmp))
            record = make_record(details={"a": 1, "b": [1, 2]}, raw={"c": "d"})
            sink.write_batch([record])
            sink.close()
            files = list(Path(tmp).glob("*.jsonl"))
            parsed = json.loads(files[0].read_text(encoding="utf-8").strip())
            self.assertEqual(parsed["details"], {"a": 1, "b": [1, 2]})
            self.assertEqual(parsed["raw"], {"c": "d"})

    def test_empty_batch_is_a_no_op(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = JsonlSink(Path(tmp))
            sink.write_batch([])
            sink.close()
            self.assertEqual(list(Path(tmp).glob("*.jsonl")), [])


class TestJsonlSinkRotation(unittest.TestCase):
    def test_size_limit_rotates_to_a_second_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = JsonlSink(Path(tmp), max_bytes=200)
            for i in range(20):
                sink.write_batch([make_record(message="x" * 20, details={"i": i})])
            sink.close()
            files = sorted(Path(tmp).glob("*.jsonl"))
            self.assertGreaterEqual(len(files), 2)

    def test_all_records_are_recoverable_across_rotated_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = JsonlSink(Path(tmp), max_bytes=200)
            ids = []
            for i in range(20):
                record = make_record(message="x" * 20, details={"i": i})
                ids.append(record.record_id)
                sink.write_batch([record])
            sink.close()
            seen = []
            for path in sorted(Path(tmp).glob("*.jsonl")):
                for line in path.read_text(encoding="utf-8").strip().splitlines():
                    seen.append(json.loads(line)["record_id"])
            self.assertEqual(sorted(seen), sorted(ids))


class TestJsonlSinkFailure(unittest.TestCase):
    def test_write_failure_disables_sink_and_raises_once(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = JsonlSink(Path(tmp))
            sink.write_batch([make_record()])  # opens a real handle

            class _BrokenHandle:
                def write(self, _value):
                    raise OSError("disk error")

                def tell(self):
                    return 0

                def flush(self):
                    raise OSError("disk error")

                def close(self):
                    pass

            sink._handle.close()  # release the real handle before swapping it
            sink._handle = _BrokenHandle()
            with self.assertRaises(Exception):
                sink.write_batch([make_record()])
            self.assertTrue(sink.disabled)
            # Second call after disabling must be a silent no-op, not a
            # second raise (the caller reports to Health exactly once).
            sink.write_batch([make_record()])

    def test_close_after_failure_is_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            sink = JsonlSink(Path(tmp))
            sink._disabled = True
            sink.close()  # must not raise


if __name__ == "__main__":
    unittest.main()
