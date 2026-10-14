"""Strict candidate/PyPI checks; validation alone never publishes a build."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import re
import tarfile
import zipfile
import urllib.error
import urllib.request
from pathlib import Path


PROJECT = "voice-stt-client"
VERSION = (Path(__file__).resolve().parents[1] / 'VERSION').read_text(encoding='utf8').strip()


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
        directory.rglob(f"voice-stt-client-v{VERSION}-windows-x64.exe")
    )
    found["exe"] = exe
    if any(len(matches) != 1 for matches in found.values()):
        raise ValueError(f"candidate must contain exactly one of each expected artifact: {expected}")
    all_products = [p for p in directory.rglob("*") if p.is_file() and p.suffix in {".exe", ".whl", ".gz"}]
    if len(all_products) != 3:
        raise ValueError("candidate contains unexpected executable or Python distribution")
    return {kind: matches[0] for kind, matches in found.items()}


def validate_distributions(files: dict[str, Path], expected_commit: str | None = None) -> dict:
    """Inspect shipped files, not the checkout or an ancestor's Git metadata."""
    identities = {}
    required = {'voice_stt_client/config.yaml', 'voice_stt_client/build_identity.json',
        'voice_stt_client/resources/protocol-v2-vectors.json',
        'voice_stt_client/resources/protocol-v2-client-fixtures.json',
        'voice_stt_client/resources/protocol-v2-provenance.json'}
    for kind in ('wheel', 'sdist'):
        if kind == 'wheel':
            with zipfile.ZipFile(files[kind]) as archive:
                content = {name: archive.read(name) for name in archive.namelist() if not name.endswith('/')}
        else:
            with tarfile.open(files[kind]) as archive:
                content = {member.name.split('/', 1)[1]: archive.extractfile(member).read()
                    for member in archive.getmembers() if member.isfile()}
        if not required <= content.keys():
            raise ValueError(f'{kind} missing resources: {sorted(required-content.keys())}')
        if len([name for name in content if name.endswith('.wav')]) != 8:
            raise ValueError(f'{kind} must ship eight sound assets')
        for name in content:
            parts = Path(name).parts
            if (name.startswith(('core/', 'ui/', 'tests/', 'ARBEITSDATEIEN/'))
                    or any(part in {'.env', 'client.log', '__pycache__'} for part in parts)
                    or 'simulator' in name.lower() or name.endswith(('.sqlite', '.db', '.pyc'))):
                raise ValueError(f'{kind} contains forbidden file: {name}')
        identity = json.loads(content['voice_stt_client/build_identity.json'])
        if (identity.get('schemaVersion') != 1 or identity.get('version') != VERSION
                or identity.get('sourceDirty') is not False
                or re.fullmatch(r'[0-9a-f]{40}', identity.get('clientCommit', '')) is None
                or expected_commit is not None and identity['clientCommit'] != expected_commit):
            raise ValueError(f'{kind} source identity is not qualified')
        identities[kind] = identity
    if identities['wheel'] != identities['sdist']:
        raise ValueError('wheel and sdist identity differ')
    return identities


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
    parser.add_argument('--expected-commit')
    args = parser.parse_args()
    files = candidate_files(args.dir)
    if args.mode == "candidate":
        validate_distributions(files, args.expected_commit)
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
