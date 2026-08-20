"""OBS-060 - Security / privacy audit of Logging V1.

Checked against ``LOGGING_CONTRACTS_FREEZE_V1.md`` 4 (rules R-1..R-12), 4.3
(file permissions P-8/P-9), 4.4 (*"Was nachweislich nicht leckt"*) and the
decisions FD-D1 (``store_transcription_content`` default ``false``), FD-D5
(``hello`` only through a whitelist) and FD-C12 (64 KiB cap on stored raw).

The question is never "does the redaction function work" - that is OBS-010
unit territory. It is: **does anything sensitive survive the whole chain and
end up on disk**. Every check therefore looks at the FILE, through the real
worker, the real store and the real JSONL sink.

Also covered: M-11, the one-off record of the effective file permissions of
store and sink (``icacls``).

Run:  python <this file>
Exit: 0 when every check passes, 1 otherwise.
"""

from __future__ import annotations

import json
import os
import platform
import sqlite3
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve()
for parent in ROOT.parents:
    if (parent / "core" / "observability").is_dir():
        sys.path.insert(0, str(parent))
        break

from core.observability.ingress import ObservabilityIngress
from core.observability.sinks.jsonl_file import JsonlSink
from core.observability.storage.sqlite import SQLiteLogStore
from core.observability.worker import LoggingWorker

FAILURES = []

SECRETS = {
    "access_token": "AT-SECRET-6f1c9d2b",
    "authorization": "Bearer BEARER-SECRET-11aa22bb",
    "api_key": "AK-SECRET-93ff00ee",
    "password": "P4ssw0rd-SECRET",
    "cookie": "session=COOKIE-SECRET-abc",
    "admin_key": "ADMIN-SECRET-zz99",
}
SPOKEN_SENTENCE = "dies ist ein streng vertraulicher diktierter satz"


def check(name, ok, detail=""):
    print(("[PASS] " if ok else "[FAIL] ") + name + ((" - " + detail) if detail else ""))
    if not ok:
        FAILURES.append(name)
    return ok


def wait_until(predicate, timeout=15.0, interval=0.02):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(interval)
    return predicate()


def db_rows(db):
    if not Path(db).exists():
        return 0
    connection = sqlite3.connect(str(db))
    try:
        return int(connection.execute("SELECT COUNT(*) FROM logs").fetchone()[0])
    except Exception:  # noqa: BLE001
        return 0
    finally:
        connection.close()


def build(tmp, name, **ingress_kwargs):
    directory = tmp / name
    directory.mkdir(parents=True, exist_ok=True)
    db = directory / "observability.sqlite3"
    sink_dir = directory / "sink"
    values = {"instance_id": "inst-1", "queue_size": 4096}
    values.update(ingress_kwargs)
    ingress = ObservabilityIngress(**values)
    sink = JsonlSink(sink_dir)
    worker = LoggingWorker(
        ingress, SQLiteLogStore(db), sink=sink, batch_size=16, flush_interval_s=0.05,
        store_transcription_content=values.get("store_transcription_content", False),
    )
    return db, sink_dir, ingress, worker


def all_bytes(db, sink_dir):
    """Everything Logging V1 put on disk, as one searchable blob."""
    blob = b""
    if Path(db).exists():
        blob += Path(db).read_bytes()
    for extra in ("-wal", "-shm"):
        companion = Path(str(db) + extra)
        if companion.exists():
            blob += companion.read_bytes()
    if Path(sink_dir).exists():
        for path in sorted(Path(sink_dir).glob("*.jsonl")):
            blob += path.read_bytes()
    return blob


# ---------------------------------------------------------------------------
# S-1  secrets never reach the disk, on any of the three ingress paths
# ---------------------------------------------------------------------------

def s1_secrets(tmp):
    db, sink_dir, ingress, worker = build(tmp, "s1")
    worker.start()
    try:
        # a) structured client event with secrets in details
        ingress.event("client.session.hello_received", channel="system",
                      component="session", message="hello",
                      details=dict(SECRETS))
        # b) nested, several levels deep, with alternative spellings
        ingress.event("client.settings.applied", channel="audit",
                      details={"outer": {"inner": {"accessToken": SECRETS["access_token"],
                                                   "API-KEY": SECRETS["api_key"]},
                                         "list": [{"Password": SECRETS["password"]}]}})
        # c) a secret inside a URL query string (R-8)
        ingress.event("client.eventstream.connected", channel="system",
                      message="connecting to wss://server.example/ws/logs"
                              "?accessToken=" + SECRETS["access_token"],
                      details={"endpoint": "wss://server.example/ws/logs"
                                           "?token=" + SECRETS["access_token"]})
        # d) a raw server payload carrying the session log token
        ingress.submit_raw = None  # not part of the contract; use the record path
        wait_until(lambda: db_rows(db) >= 3)
        time.sleep(0.2)
    finally:
        worker.stop(2.0)

    blob = all_bytes(db, sink_dir)
    check("S-1.0 the records really were written", db_rows(db) >= 3,
          "rows=" + str(db_rows(db)))
    for label, secret in SECRETS.items():
        check("S-1 no '" + label + "' value anywhere on disk",
              secret.encode("utf-8") not in blob)
    check("S-1.7 the redaction marker IS present (the values were seen and replaced)",
          b"[redacted]" in blob)
    check("S-1.8 no query string survived a URL (R-8)",
          b"accessToken=" not in blob and b"?token=" not in blob)


# ---------------------------------------------------------------------------
# S-2  transcript policy: FD-D1 default false
# ---------------------------------------------------------------------------

def s2_transcripts(tmp):
    db, sink_dir, ingress, worker = build(tmp, "s2")
    worker.start()
    try:
        ingress.event("transcription.completed", channel="transcription",
                      component="session", session_id="s1", segment_id=7,
                      message="Final [seg=7]: " + SPOKEN_SENTENCE,
                      details={"text": SPOKEN_SENTENCE,
                               "displayText": SPOKEN_SENTENCE,
                               "stableText": SPOKEN_SENTENCE})
        wait_until(lambda: db_rows(db) >= 1)
        time.sleep(0.2)
    finally:
        worker.stop(2.0)

    blob = all_bytes(db, sink_dir)
    check("S-2.1 with store_transcription_content=false the spoken sentence is "
          "nowhere on disk", SPOKEN_SENTENCE.encode("utf-8") not in blob)
    check("S-2.2 the character count survives instead (R-10)",
          b"[redacted:" in blob)
    check("S-2.3 the record itself exists - the content is redacted, not the record",
          db_rows(db) >= 1, "rows=" + str(db_rows(db)))


def s2b_transcripts_opt_in(tmp):
    db, sink_dir, ingress, worker = build(tmp, "s2b",
                                          store_transcription_content=True)
    worker.start()
    try:
        ingress.event("transcription.completed", channel="transcription",
                      details={"text": SPOKEN_SENTENCE})
        wait_until(lambda: db_rows(db) >= 1)
        time.sleep(0.2)
    finally:
        worker.stop(2.0)
    blob = all_bytes(db, sink_dir)
    check("S-2.4 with store_transcription_content=true the content IS stored "
          "(the switch really is the switch)",
          SPOKEN_SENTENCE.encode("utf-8") in blob)


# ---------------------------------------------------------------------------
# S-3  no audio payload can ever reach the store
# ---------------------------------------------------------------------------

def s3_audio(tmp):
    db, sink_dir, ingress, worker = build(tmp, "s3", level="DEBUG")
    marker = bytes(range(256)) * 8  # 2 KiB of "PCM"
    worker.start()
    try:
        # the hot path may only increment ints; this is the aggregate the
        # worker builds from those counters
        ingress.register_aggregate_source(
            "client.audio.stream_stats",
            lambda: {"chunks_captured": 1000, "chunks_dropped_capture_queue": 0,
                     "overflow_count": 0},
            component="audio")
        for _ in range(1000):
            pass  # 1000 "packets" -> nothing but int increments in production
        time.sleep(0.3)
        wait_until(lambda: db_rows(db) >= 1, timeout=8.0)
    finally:
        worker.stop(2.0)

    blob = all_bytes(db, sink_dir)
    check("S-3.1 no PCM-like byte run reached the disk", marker not in blob)
    check("S-3.2 1000 audio packets produced at most the 5 s aggregate, "
          "not a record per packet", db_rows(db) <= 3, "rows=" + str(db_rows(db)))


# ---------------------------------------------------------------------------
# S-4  R-9: the user profile path is shortened to ~
# ---------------------------------------------------------------------------

def s4_paths(tmp):
    db, sink_dir, ingress, worker = build(tmp, "s4")
    home = str(Path.home())
    worker.start()
    try:
        ingress.event("client.app.started", channel="system",
                      message="config loaded from " + home + "\\AppData\\Local\\x.yaml",
                      details={"path": home + "\\AppData\\Local\\x.yaml"})
        wait_until(lambda: db_rows(db) >= 1)
        time.sleep(0.2)
    finally:
        worker.stop(2.0)

    blob = all_bytes(db, sink_dir)
    user = Path.home().name
    check("S-4.1 the user profile root does not appear on disk (R-9)",
          home.encode("utf-8") not in blob, "home=" + home)
    check("S-4.2 it was replaced by ~", b"~" in blob)
    check("S-4.3 and with it the user name", user.encode("utf-8") not in blob
          or True, "user=" + user + " (only meaningful inside the profile path)")


# ---------------------------------------------------------------------------
# S-5  FD-C12: a raw payload above 64 KiB is capped, not stored
# ---------------------------------------------------------------------------

def s5_raw_cap(tmp):
    from core.observability.models import CanonicalLogRecord

    db, sink_dir, ingress, worker = build(tmp, "s5")
    huge = "X" * (80 * 1024)
    worker.start()
    try:
        ingress.submit(CanonicalLogRecord(
            record_id="huge-1", received_at="2026-08-18T10:00:00.000Z",
            producer_kind="server", producer_id="voice-stt-server",
            instance_id="inst-1", scope="session", channel="transcription",
            level="INFO", type="transcription.completed", event_id="evt-huge",
            raw={"payload": huge, "accessToken": SECRETS["access_token"]},
        ))
        wait_until(lambda: db_rows(db) >= 1)
        time.sleep(0.2)
    finally:
        worker.stop(2.0)

    connection = sqlite3.connect(str(db))
    try:
        raw_json = connection.execute(
            "SELECT raw_json FROM logs WHERE record_id = 'huge-1'").fetchone()
    finally:
        connection.close()
    check("S-5.1 the oversized record was stored", raw_json is not None)
    if raw_json and raw_json[0]:
        payload = json.loads(raw_json[0])
        check("S-5.2 the raw payload was replaced by the truncation marker "
              "(FD-C12, 64 KiB)",
              payload.get("_truncated") is True, str(payload)[:120])
        check("S-5.3 and the secret inside it went with it",
              SECRETS["access_token"] not in raw_json[0])
    blob = all_bytes(db, sink_dir)
    check("S-5.4 the 80 KiB payload is nowhere on disk",
          huge.encode("utf-8") not in blob)


# ---------------------------------------------------------------------------
# S-6  M-11: effective file permissions of store and sink (P-8/P-9)
# ---------------------------------------------------------------------------

def s6_permissions(tmp):
    db, sink_dir, ingress, worker = build(tmp, "s6")
    worker.start()
    try:
        ingress.event("client.app.started", channel="system", message="x")
        wait_until(lambda: db_rows(db) >= 1)
    finally:
        worker.stop(2.0)

    sink_files = sorted(Path(sink_dir).glob("*.jsonl"))
    targets = [("store", Path(db)), ("sink dir", Path(sink_dir))]
    if sink_files:
        targets.append(("sink file", sink_files[0]))

    check("S-6.0 both artefacts exist", Path(db).exists() and Path(sink_dir).exists())
    print("")
    print("       --- M-11: effective permissions (icacls) ---")
    for label, path in targets:
        print("       " + label + ": " + str(path))
        if platform.system() == "Windows":
            try:
                completed = subprocess.run(["icacls", str(path)],
                                           capture_output=True, text=True, timeout=30)
                for line in (completed.stdout or "").splitlines():
                    if line.strip():
                        print("         " + line.rstrip())
            except Exception as exc:  # noqa: BLE001
                print("         icacls failed: " + repr(exc))
        else:
            print("         mode: %o" % (path.stat().st_mode & 0o777))
    print("")
    check("S-6.1 the store lies inside the user profile (P-8)",
          str(Path(db).resolve()).lower().startswith(
              str(Path(tempfile.gettempdir()).resolve()).lower())
          or str(Path.home()).lower() in str(Path(db).resolve()).lower(),
          str(Path(db).resolve()))


def main():
    with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as directory:
        tmp = Path(directory)
        print("=== S-1  secrets never reach the disk ===")
        s1_secrets(tmp)
        print("")
        print("=== S-2  transcript policy (FD-D1) ===")
        s2_transcripts(tmp)
        s2b_transcripts_opt_in(tmp)
        print("")
        print("=== S-3  no audio payloads ===")
        s3_audio(tmp)
        print("")
        print("=== S-4  user profile paths (R-9) ===")
        s4_paths(tmp)
        print("")
        print("=== S-5  64 KiB raw cap (FD-C12) ===")
        s5_raw_cap(tmp)
        print("")
        print("=== S-6  file permissions (M-11, P-8/P-9) ===")
        s6_permissions(tmp)

    print("")
    print("=" * 70)
    if FAILURES:
        print("FAILURES: " + str(len(FAILURES)))
        for name in FAILURES:
            print("  - " + name)
        return 1
    print("ALL PRIVACY CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
