"""Führt die beauftragten Prüfungen aus und sichert vollständige Logs im Run.

Nur ein bereits vorhandener, sauberer Prüfcheckout wird gelesen; kein Gittransport.
"""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import os
import time

parser = argparse.ArgumentParser()
parser.add_argument("--checkout", type=Path, required=True)
parser.add_argument("--python", type=Path, required=True)
args = parser.parse_args()
checkout = args.checkout.resolve(strict=True)
runtime = args.python.resolve(strict=True)
output = Path(__file__).resolve().parent
git = lambda *parts: subprocess.check_output(["git", "-C", str(checkout), *parts], text=True).strip()
assert not git("status", "--porcelain"), "Prüfcheckout muss vor Ausführung sauber sein."
head = git("rev-parse", "HEAD")
assert head == "7c4bb2f7d3f3a79d0b2f0beae5bdbae27795d0fe"
review_head = "cd872d4bfa8eccd0167337cbab16a572ca70bfd4"
changes = git("diff", "--name-only", review_head, head).splitlines()
assert all(path.startswith("ARBEITSDATEIEN/") for path in changes)
environment = dict(os.environ, QT_QPA_PLATFORM="offscreen", OPENBLAS_NUM_THREADS="1", OMP_NUM_THREADS="1")
environment.pop("PYTHONPATH", None)
identity_code = "import json,platform,sys,voice_stt_client; print(json.dumps({'platform':platform.platform(),'python':sys.version,'executable':sys.executable,'module':voice_stt_client.__file__}))"
identity = json.loads(subprocess.check_output([str(runtime), "-c", identity_code], cwd=checkout, env=environment, text=True))
assert identity["platform"].startswith("Windows")
assert identity["python"].startswith("3.12.10")
assert checkout in Path(identity["module"]).resolve().parents
record = {
    "startedAtUtc": datetime.now(timezone.utc).isoformat(),
    "testedCommit": head, "testedTree": git("rev-parse", "HEAD^{tree}"),
    "priorReviewedCommit": review_head, "differencesFromPriorReview": changes,
    "productAndTestsIdenticalToPriorReview": True,
    "checkout": str(checkout), "runtime": identity,
    "environmentOverrides": {key: environment[key] for key in ("QT_QPA_PLATFORM", "OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS")},
    "tests": [],
}
commands = [
    ("windows-full-unittest.txt", [str(runtime), "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]),
    ("startup-persistence.txt", [str(runtime), "-m", "unittest", "tests.test_startup_hotkey_persistence", "-v"]),
    ("compileall.txt", [str(runtime), "-m", "compileall", "-q", "voice_stt_client", "scripts", "tests"]),
    ("diff-check.txt", ["git", "diff", "--check"]),
]
for name, command in commands:
    start = time.monotonic()
    with (output / name).open("w", encoding="utf-8") as log:
        log.write(json.dumps({"command": command, "cwd": str(checkout), "testedCommit": head}) + "\n")
        log.flush()
        completed = subprocess.run(command, cwd=checkout, env=environment, stdout=log, stderr=subprocess.STDOUT)
    result = {"log": name, "command": command, "exitCode": completed.returncode, "seconds": round(time.monotonic() - start, 3)}
    record["tests"].append(result)
    (output / "windows-validation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result), flush=True)
    if completed.returncode:
        raise SystemExit(completed.returncode)
record["finishedAtUtc"] = datetime.now(timezone.utc).isoformat()
record["checkoutStatusAfter"] = git("status", "--porcelain")
assert not record["checkoutStatusAfter"], "Prüfungen dürfen keinen Produktdiff hinterlassen."
record["result"] = "PASS"
(output / "windows-validation.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"result": "PASS", "testedCommit": head}), flush=True)
