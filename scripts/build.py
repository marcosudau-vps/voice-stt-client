"""Build and smoke-test the Windows executable with PyInstaller."""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = REPO_ROOT / "VERSION"
SPEC_FILE = REPO_ROOT / "voice-stt-client.spec"
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"
EXE_PATH = DIST_DIR / "voice-stt-client.exe"
VERSION_PATTERN = re.compile(r"\d+\.\d+\.\d+")
PYINSTALLER_BOOTSTRAP = (
    "import platform; "
    "platform.system=lambda:'Windows'; "
    "platform.machine=lambda:'AMD64'; "
    "platform.win32_ver=lambda *args,**kwargs:('11','','','Multiprocessor Free'); "
    "platform._get_machine_win32=lambda:'AMD64'; "
    "platform._Processor.get=lambda:'AMD64'; "
    "from PyInstaller.__main__ import run; run()"
)


class BuildError(RuntimeError):
    """Raised when a reproducible executable cannot be produced."""


def read_version(path: Path = VERSION_FILE) -> str:
    value = path.read_text(encoding="utf-8").strip()
    if VERSION_PATTERN.fullmatch(value) is None:
        raise BuildError(f"Invalid version in {path}: {value!r}")
    return value


def render_windows_version_info(version: str) -> str:
    """Return a PyInstaller version resource derived from ``VERSION``."""
    major, minor, patch = (int(part) for part in version.split("."))
    tuple_value = f"({major}, {minor}, {patch}, 0)"
    return f"""# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={tuple_value},
    prodvers={tuple_value},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo([
      StringTable('040904B0', [
        StringStruct('CompanyName', 'marcosudau-vps'),
        StringStruct('FileDescription', 'RealtimeSTT Windows Desktop Client'),
        StringStruct('FileVersion', '{version}'),
        StringStruct('InternalName', 'voice-stt-client'),
        StringStruct('OriginalFilename', 'voice-stt-client.exe'),
        StringStruct('ProductName', 'voice-stt-client'),
        StringStruct('ProductVersion', '{version}')
      ])
    ]),
    VarFileInfo([VarStruct('Translation', [1033, 1200])])
  ]
)
"""


def _validated_output_dir(path: Path) -> Path:
    resolved = path.resolve()
    if resolved.parent != REPO_ROOT.resolve() or resolved.name not in {"build", "dist"}:
        raise BuildError(f"Refusing to clean unexpected path: {resolved}")
    return resolved


def clean_outputs() -> None:
    """Remove only the two known generated output directories."""
    for path in (BUILD_DIR, DIST_DIR):
        target = _validated_output_dir(path)
        if target.exists():
            shutil.rmtree(target)


def run(command: list[str], *, env: dict[str, str] | None = None) -> None:
    result = subprocess.run(command, cwd=REPO_ROOT, env=env, check=False)
    if result.returncode != 0:
        raise BuildError(f"Command failed with exit code {result.returncode}: {' '.join(command)}")


def build(*, clean: bool = False, smoke_test: bool = True) -> Path:
    if os.name != "nt":
        raise BuildError("The Windows executable must be built on Windows.")
    if clean:
        clean_outputs()

    version = read_version()
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            "w", encoding="utf-8", suffix="-voice-stt-version.txt", delete=False
        ) as handle:
            handle.write(render_windows_version_info(version))
            temp_path = Path(handle.name)

        env = os.environ.copy()
        env["VOICE_STT_VERSION_FILE"] = str(temp_path)
        site_dir = REPO_ROOT / "scripts" / "pyinstaller_site"
        existing_python_path = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(site_dir), existing_python_path) if part
        )
        run(
            [
                sys.executable,
                "-c",
                PYINSTALLER_BOOTSTRAP,
                "--noconfirm",
                "--clean",
                str(SPEC_FILE),
            ],
            env=env,
        )
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    if not EXE_PATH.is_file() or EXE_PATH.stat().st_size == 0:
        raise BuildError(f"Expected executable was not created: {EXE_PATH}")

    if smoke_test:
        result = subprocess.run(
            [str(EXE_PATH), "--version"],
            cwd=REPO_ROOT,
            timeout=60,
            check=False,
        )
        if result.returncode != 0:
            raise BuildError(
                f"Executable smoke test failed with exit code {result.returncode}"
            )

    digest = hashlib.sha256(EXE_PATH.read_bytes()).hexdigest()
    print(f"Built {EXE_PATH.relative_to(REPO_ROOT)} ({EXE_PATH.stat().st_size} bytes)")
    print(f"Version {version}; SHA-256 {digest}")
    return EXE_PATH


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="remove previous build output")
    parser.add_argument(
        "--no-smoke", action="store_true", help="skip starting the built executable with --version"
    )
    args = parser.parse_args(argv)
    try:
        build(clean=args.clean, smoke_test=not args.no_smoke)
        return 0
    except (BuildError, OSError, subprocess.SubprocessError) as exc:
        print(f"build stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
