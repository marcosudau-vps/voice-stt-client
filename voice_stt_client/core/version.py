"""Single source of truth for the client release version."""

from __future__ import annotations

import re
import json
import subprocess
from importlib.metadata import PackageNotFoundError, version as distribution_version
from pathlib import Path


VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")
PACKAGE_DIR = Path(__file__).resolve().parent.parent
SOURCE_ROOT = PACKAGE_DIR.parent
VERSION_FILE = SOURCE_ROOT / "VERSION"
BUNDLED_VERSION_FILE = PACKAGE_DIR / "VERSION"


def _validated_version(path: Path) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if VERSION_PATTERN.fullmatch(value) is None:
        raise RuntimeError(f"Invalid version in {path}: {value!r}")
    return value


def read_version(path: Path | None = None) -> str:
    """Read and validate the semantic release version."""
    if path is not None:
        return _validated_version(path)

    # Source checkouts keep the release source of truth at repository root;
    # PyInstaller places the same file beside the frozen package.
    for candidate in (BUNDLED_VERSION_FILE, VERSION_FILE):
        if candidate.is_file():
            return _validated_version(candidate)

    # An installed wheel carries the canonical version in distribution
    # metadata, so it needs no loose top-level VERSION file.
    try:
        value = distribution_version("voice-stt-client")
    except PackageNotFoundError as exc:
        raise RuntimeError("Could not determine voice-stt-client version") from exc
    if VERSION_PATTERN.fullmatch(value) is None:
        raise RuntimeError(f"Invalid installed voice-stt-client version: {value!r}")
    return value


__version__ = read_version()


def read_build_identity() -> dict:
    """Packaged provenance wins; source identity requires this exact Git root.

    No environment override or parent checkout may impersonate a build SHA.
    Dirty product sources advertise unknown, retaining the base for diagnosis.
    """
    stamp = PACKAGE_DIR / 'build_identity.json'
    if stamp.is_file():
        data = json.loads(stamp.read_text(encoding='utf-8'))
        commit = data.get('clientCommit')
        if (data.get('schemaVersion') != 1 or data.get('version') != __version__
                or not isinstance(commit, str)
                or (commit != 'unknown' and re.fullmatch(r'[0-9a-f]{40}', commit) is None)):
            raise RuntimeError('Invalid packaged build identity')
        return data
    if (SOURCE_ROOT / '.git').exists():
        try:
            def git(*args):
                return subprocess.check_output(['git', '-C', str(SOURCE_ROOT), *args],
                    text=True, stderr=subprocess.DEVNULL, timeout=5).strip()
            if Path(git('rev-parse', '--show-toplevel')).resolve() == SOURCE_ROOT.resolve():
                commit = git('rev-parse', 'HEAD')
                dirty = bool(git('status', '--porcelain', '--', 'voice_stt_client', 'scripts',
                    'setup.py', 'pyproject.toml', 'VERSION', 'requirements.txt', 'requirements-dev.txt', 'MANIFEST.in', 'README.md', 'voice-stt-client.spec'))
                return dict(schemaVersion=1, version=__version__, clientCommit='unknown' if dirty else commit,
                    sourceCommit=commit, sourceDirty=dirty)
        except (OSError, subprocess.SubprocessError):
            pass
    return dict(schemaVersion=1, version=__version__, clientCommit='unknown', sourceCommit='unknown', sourceDirty=None)


BUILD_IDENTITY = read_build_identity()
__commit__ = BUILD_IDENTITY['clientCommit']
