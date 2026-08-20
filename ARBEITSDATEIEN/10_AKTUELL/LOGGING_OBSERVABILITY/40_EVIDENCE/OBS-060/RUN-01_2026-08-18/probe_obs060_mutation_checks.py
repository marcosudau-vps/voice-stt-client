"""OBS-060 - The eight mutation checks.

``WP-OBS-060`` and the plan 13 list eight mutations and state the rule:
**every one of them must turn a test red**. A guard nobody would notice
missing is not a guard.

How this works: the mutation is written into the real source file, the named
test selection is run in a SUBPROCESS, and the file is restored afterwards.
The restore runs in a ``finally`` and is verified against the SHA-256 of the
original bytes; if a single file cannot be restored the probe aborts loudly
instead of leaving a mutated tree behind.

Run:  QT_QPA_PLATFORM=offscreen python <this file>
Exit: 0 when every mutation turned its test red, 1 otherwise.
"""

from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "core" / "observability").is_dir():
        PROJECT_ROOT = parent
        break

FAILURES = []


def check(name, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + ((" - " + detail) if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


TEST_TIMEOUT_S = 240


def run_tests(selection, timeout=TEST_TIMEOUT_S):
    """Run one pytest selection in a subprocess. Returns (exit_code, tail).

    A TIMEOUT counts as red, and deliberately so: the ``put_nowait`` mutation
    turns the non-blocking boundary into a blocking one, and the symptom of a
    blocked producer thread is not a failed assertion but a run that never
    ends. Treating that as "green" would be the one reading that makes the
    mutation check useless.
    """
    environment = dict(os.environ)
    environment.setdefault("QT_QPA_PLATFORM", "offscreen")
    try:
        completed = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider",
             "--tb=no", *selection],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
            env=environment,
        )
    except subprocess.TimeoutExpired:
        return 124, "TIMEOUT after " + str(timeout) + "s (the run never finished)"
    tail = (completed.stdout or "").strip().splitlines()
    return completed.returncode, (tail[-1] if tail else "")


MUTATIONS = [
    {
        "id": "M-1",
        "title": "ON CONFLICT DO NOTHING -> plain INSERT",
        "file": "core/observability/storage/sqlite.py",
        "old": "ON CONFLICT (producer_id, event_id) WHERE event_id IS NOT NULL DO NOTHING\n",
        "new": "",
        "expect_red": [
            "tests/test_obs030_sqlite_store.py",
            "tests/test_obs060_v1_hardening.py::TestNonBlockingInvariantAnchor",
        ],
    },
    {
        "id": "M-2",
        "title": "remove the except Exception in the observer wrapper",
        "file": "core/session_coordinator.py",
        "old": """        try:
            observer(self._context, result)
        except Exception:  # noqa: BLE001 - handling lives in the logging domain
            pass""",
        "new": "        observer(self._context, result)",
        "expect_red": ["tests/test_obs040_fanout_hook.py"],
    },
    {
        "id": "M-3",
        "title": "put_nowait -> blocking put",
        "file": "core/observability/ingress.py",
        "old": "            self._queue.put_nowait(record)",
        "new": "            self._queue.put(record)",
        "expect_red": [
            "tests/test_obs020_ingress.py",
            "tests/test_obs060_v1_hardening.py::TestNonBlockingInvariantAnchor",
        ],
    },
    {
        "id": "M-4",
        "title": "remove the watermark rule",
        "file": "core/observability/ingress.py",
        "old": """        if self._queue.qsize() >= self._watermark and record.priority is not RecordPriority.HIGH:
            self.health.record_dropped_watermark()
            return False""",
        "new": "",
        "expect_red": [
            "tests/test_obs020_ingress.py",
            "tests/test_obs060_v1_hardening.py::TestNonBlockingInvariantAnchor",
        ],
    },
    {
        "id": "M-5",
        "title": "remove the redaction call in the normalizer",
        "file": "core/observability/normalizer.py",
        "old": """def _redact(details: Mapping[str, Any], *, store_transcription_content: bool,
            user_profile: Any) -> Mapping[str, Any]:
    return redact_mapping(""",
        "new": """def _redact(details: Mapping[str, Any], *, store_transcription_content: bool,
            user_profile: Any) -> Mapping[str, Any]:
    return dict(details)
    return redact_mapping(""",
        "expect_red": [
            "tests/test_obs010_normalizer_client.py",
            "tests/test_obs010_contracts.py",
            "tests/test_obs020_redaction_end_to_end.py",
        ],
    },
    {
        "id": "M-6",
        "title": "remove WHERE event_id IS NOT NULL from the unique index",
        "file": "core/observability/storage/sqlite.py",
        "old": """    CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_producer_event
        ON logs (producer_id, event_id)
        WHERE event_id IS NOT NULL
    """,
        "new": """    CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_producer_event
        ON logs (producer_id, event_id)
    """,
        "expect_red": [
            "tests/test_obs030_sqlite_store.py",
            "tests/test_obs060_v1_hardening.py::TestFrozenDdlIsPartial",
        ],
    },
    {
        "id": "M-7",
        "title": "set the handler level to DEBUG",
        "file": "core/logging_setup.py",
        "old": "        observability_handler.setLevel(observability.level)",
        "new": "        observability_handler.setLevel(logging.DEBUG)",
        "expect_red": ["tests/test_obs020_logging_setup_integration.py"],
    },
    {
        "id": "M-8",
        "title": "remove PRAGMA query_only = ON",
        "file": "core/observability/query/local.py",
        "old": '            connection.execute("PRAGMA query_only = ON")',
        "new": "            pass",
        "expect_red": [
            "tests/test_obs050_local_provider.py",
            "tests/test_obs060_v1_hardening.py::TestNonBlockingInvariantAnchor",
        ],
    },
]


CRLF = bytes([13, 10]).decode("ascii")
LF = bytes([10]).decode("ascii")


def line_ending(raw):
    """The file's own newline convention, so a restore is byte-exact.

    ``Path.write_text`` translates a line feed to ``os.linesep`` on Windows
    and would silently rewrite an LF source file to CRLF - a whole-file change
    left behind by a probe that is supposed to change nothing. The sources of
    this repository are LF.
    """
    return CRLF if bytes([13, 10]) in raw else LF


def to_file(text, newline):
    return text.replace(LF, newline).encode("utf-8")


def main():
    # 1. every mutation must apply exactly once, before anything is changed
    originals = {}
    newlines = {}
    for mutation in MUTATIONS:
        path = PROJECT_ROOT / mutation["file"]
        raw = path.read_bytes()
        newlines[path] = line_ending(raw)
        source = raw.decode("utf-8").replace(newlines[path], LF)
        originals.setdefault(path, source)
        occurrences = source.count(mutation["old"])
        if occurrences != 1:
            check(mutation["id"] + " mutation applies to exactly one place",
                  False, "occurrences=" + str(occurrences) + " in " + mutation["file"])
    if FAILURES:
        print("")
        print("aborting: at least one mutation no longer matches the source")
        return 1

    digests = {path: hashlib.sha256(path.read_bytes()).hexdigest()
               for path in originals}

    # 2. the selections must be GREEN before any mutation
    print("=== baseline: every selection green before mutating ===")
    baseline_selection = sorted({
        entry for mutation in MUTATIONS for entry in mutation["expect_red"]
    })
    code, tail = run_tests(baseline_selection)
    check("baseline: all mutation-check selections pass unmutated", code == 0, tail)
    print("")

    try:
        for mutation in MUTATIONS:
            path = PROJECT_ROOT / mutation["file"]
            source = originals[path]
            mutated = source.replace(mutation["old"], mutation["new"], 1)
            path.write_bytes(to_file(mutated, newlines[path]))
            try:
                code, tail = run_tests(mutation["expect_red"])
            finally:
                path.write_bytes(to_file(source, newlines[path]))
            check(mutation["id"] + "  " + mutation["title"] + " -> turns a test red",
                  code != 0,
                  ("exit=" + str(code) + "  " + tail))
    finally:
        # 3. restore and VERIFY, whatever happened above
        print("")
        print("=== restore verification ===")
        for path, source in originals.items():
            path.write_bytes(to_file(source, newlines[path]))
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            ok = actual == digests[path]
            print(("[PASS] " if ok else "[FAIL] ")
                  + "restored byte-identical: " + str(path.relative_to(PROJECT_ROOT)))
            if not ok:
                FAILURES.append("restore " + str(path))

    print("")
    print("=" * 70)
    if FAILURES:
        print("FAILURES: " + str(len(FAILURES)))
        for name in FAILURES:
            print("  - " + name)
        return 1
    print("ALL EIGHT MUTATIONS TURN A TEST RED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
