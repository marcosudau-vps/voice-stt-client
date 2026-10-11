"""Strict candidate/PyPI checks for the first client release."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import urllib.error
import urllib.request
from pathlib import Path


PROJECT = "voice-stt-client"
VERSION = "1.0.0"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def candidate_files(directory: Path) -> dict[str, Path]:
    expected = {
        "wheel": f"voice_stt_client-{VERSION}-py3-none-any.whl",
        "sdist": f"voice_stt_client-{VERSION}.tar.gz",
    }
    found = {kind: list(directory.rglob(name)) for kind, name in expected.items()}
    exe = list(directory.rglob("voice-stt-client.exe")) + list(
        directory.rglob("voice-stt-client-v1.0.0-windows-x64.exe")
    )
    found["exe"] = exe
    if any(len(matches) != 1 for matches in found.values()):
        raise ValueError(f"candidate must contain exactly one of each expected artifact: {expected}")
    all_products = [p for p in directory.rglob("*") if p.is_file() and p.suffix in {".exe", ".whl", ".gz"}]
    if len(all_products) != 3:
        raise ValueError("candidate contains unexpected executable or Python distribution")
    return {kind: matches[0] for kind, matches in found.items()}


def pypi_states(files: dict[str, Path], *, fetch=None) -> dict[str, str]:
    expected = {p.name: sha256(p) for p in files.values()}
    if fetch is None:
        fetch = urllib.request.urlopen
    request = urllib.request.Request(
        f"https://pypi.org/pypi/{PROJECT}/{VERSION}/json", headers={"Accept": "application/json"}
    )
    try:
        with fetch(request, timeout=20) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return {name: "ABSENT" for name in expected}
        raise
    urls = payload.get("urls") if isinstance(payload, dict) else None
    if not isinstance(urls, list):
        raise ValueError("invalid PyPI release response")
    remote = {}
    for item in urls:
        if not isinstance(item, dict) or not isinstance(item.get("filename"), str):
            raise ValueError("invalid PyPI file entry")
        digest = (item.get("digests") or {}).get("sha256")
        if not isinstance(digest, str):
            raise ValueError("missing PyPI SHA-256")
        remote[item["filename"]] = digest.lower()
    if set(remote) - set(expected):
        raise ValueError(f"unexpected PyPI files: {sorted(set(remote) - set(expected))}")
    states = {}
    for name, digest in expected.items():
        actual = remote.get(name)
        states[name] = "ABSENT" if actual is None else "MATCH" if actual == digest else "CONFLICT"
    if "CONFLICT" in states.values():
        raise ValueError(f"PyPI file conflict: {states}")
    return states


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=["candidate", "stage", "verify"])
    parser.add_argument("--dir", type=Path, required=True)
    parser.add_argument("--stage-dir", type=Path)
    args = parser.parse_args()
    files = candidate_files(args.dir)
    if args.mode == "candidate":
        print(json.dumps({kind: {"name": p.name, "sha256": sha256(p)} for kind, p in files.items()}))
        return 0
    states = pypi_states({kind: files[kind] for kind in ("wheel", "sdist")})
    if args.mode == "verify":
        if set(states.values()) != {"MATCH"}:
            raise ValueError(f"PyPI publication incomplete: {states}")
    else:
        if args.stage_dir is None:
            raise ValueError("--stage-dir is required for staging")
        args.stage_dir.mkdir(parents=True, exist_ok=True)
        if list(args.stage_dir.iterdir()):
            raise ValueError("staging directory must start empty")
        for kind in ("wheel", "sdist"):
            p = files[kind]
            if states[p.name] == "ABSENT":
                shutil.copy2(p, args.stage_dir / p.name)
        output = os.environ.get("GITHUB_OUTPUT")
        if output:
            with Path(output).open("a", encoding="utf-8") as handle:
                handle.write(f"has_missing={'true' if 'ABSENT' in states.values() else 'false'}\n")
    print(json.dumps(states, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
