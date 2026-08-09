"""Single source of truth for the client release version."""

from __future__ import annotations

import re
from pathlib import Path


VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")
APP_DIR = Path(__file__).resolve().parent.parent
VERSION_FILE = APP_DIR / "VERSION"


def read_version(path: Path = VERSION_FILE) -> str:
    """Read and validate the semantic release version."""
    value = path.read_text(encoding="utf-8").strip()
    if VERSION_PATTERN.fullmatch(value) is None:
        raise RuntimeError(f"Invalid version in {path}: {value!r}")
    return value


__version__ = read_version()
