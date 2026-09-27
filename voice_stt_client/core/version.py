"""Single source of truth for the client release version."""

from __future__ import annotations

import re
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
