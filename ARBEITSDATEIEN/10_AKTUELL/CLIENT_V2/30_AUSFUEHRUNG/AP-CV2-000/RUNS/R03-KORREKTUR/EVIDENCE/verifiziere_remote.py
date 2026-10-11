"""Fetch required PR artifacts at an immutable SHA and compare their hashes.

Only reads Git/local files and public raw GitHub URLs; writes the requested
verification report. Historical audit/finalization scripts are never invoked.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
from urllib.parse import quote
from urllib.request import urlopen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not re.fullmatch(r"[0-9a-f]{40}", args.commit):
        parser.error("--commit requires the full immutable SHA")
    root = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], text=True).strip())
    block = root / "ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2"
    bundle = block / "PLANUNG/EVIDENCE/WORKFLOWPRUEFUNG_2026-10-11"
    def committed_bytes(path):
        relative = path.relative_to(root).as_posix()
        return subprocess.check_output(["git", "show", f"{args.commit}:{relative}"])

    manifest = json.loads(committed_bytes(bundle / "IMPORT_MANIFEST.json").decode("utf-8-sig"))
    paths = {bundle / "IMPORT_MANIFEST.json"}
    paths.update(bundle / item["path"] for item in manifest["files"])
    record_tree = subprocess.check_output([
        "git", "ls-tree", "-r", "--name-only", "-z", args.commit, "--",
        (block / "30_AUSFUEHRUNG/AP-CV2-000").relative_to(root).as_posix(),
    ]).decode("utf-8")
    paths.update(root / p for p in record_tree.split("\0") if p)
    changed = subprocess.check_output(["git", "diff", "--name-only", "-z", "2dc251df959f97e2a0bb37b10a1a77486ae6eb5a", args.commit]).decode("utf-8")
    paths.update(root / p for p in changed.split("\0") if p and (root / p).is_file())
    paths.discard(args.output.resolve())  # Output cannot prove its own future publication.

    def verify(path):
        relative = path.relative_to(root).as_posix()
        binary = bool(re.search(r"\.zip\.\d{3}$", relative))
        local = committed_bytes(path)
        expected = hashlib.sha256(local if binary else local.replace(b"\r\n", b"\n")).hexdigest()
        url = f"https://raw.githubusercontent.com/marcosudau-vps/voice-stt-client/{args.commit}/{quote(relative, safe='/')}"
        for attempt in range(3):
            try:
                digest = hashlib.sha256()
                size = 0
                with urlopen(url, timeout=60) as response:
                    if binary:
                        while chunk := response.read(1024 * 1024):
                            size += len(chunk)
                            digest.update(chunk)
                    else:
                        remote = response.read()
                        size = len(remote)
                        digest.update(remote.replace(b"\r\n", b"\n"))
                actual = digest.hexdigest()
                return {"path": relative, "url": url, "mode": "byte-exact" if binary else "LF-normalized",
                        "remoteBytes": size, "expectedSha256": expected, "remoteSha256": actual,
                        "result": "PASS" if actual == expected else "FAIL"}
            except Exception as exc:
                if attempt == 2:
                    return {"path": relative, "url": url, "result": "FAIL", "error": str(exc)}
                time.sleep(2)

    results = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        for result in pool.map(verify, sorted(paths)):
            results.append(result)
            if len(results) % 10 == 0 or result["result"] != "PASS":
                print(f"{len(results)}/{len(paths)}: {result['result']} {result['path']}", flush=True)
    report = {"commit": args.commit, "result": "PASS" if all(r["result"] == "PASS" for r in results) else "FAIL",
              "files": len(results), "bundleFiles": len(manifest["files"]) + 1,
              "archiveParts": sum(r.get("mode") == "byte-exact" for r in results), "results": results}
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in report.items() if key != "results"}), flush=True)
    return int(report["result"] != "PASS")


if __name__ == "__main__":
    raise SystemExit(main())
