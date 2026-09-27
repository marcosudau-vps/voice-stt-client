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
REQUIRED_BUILD_PYTHON = (3, 12, 10)


class BuildError(RuntimeError):
    """Raised when a reproducible executable cannot be produced."""


def verify_build_python(version_info: object | None = None) -> None:
    """Require the interpreter used by the verified Windows V1 build."""
    info = sys.version_info if version_info is None else version_info
    actual = tuple(info[:3])
    if actual != REQUIRED_BUILD_PYTHON:
        expected = ".".join(str(part) for part in REQUIRED_BUILD_PYTHON)
        found = ".".join(str(part) for part in actual)
        raise BuildError(
            f"Windows release builds require Python {expected}; found {found}. "
            "The GUI runtime must be requalified before changing this pin."
        )


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
        StringStruct('FileDescription', 'VoiceSTT Windows Desktop Client'),
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


def verify_frozen_feedback_assets(exe_path: Path) -> None:
    """Check the paths that the frozen sound resolver will actually use."""
    from PyInstaller.archive.readers import CArchiveReader

    source = REPO_ROOT / "voice_stt_client" / "assets" / "feedback_sounds" / "debug"
    sounds = sorted(source.glob("*.wav"))
    if not sounds:
        raise BuildError("No packaged feedback WAV files found")
    bundled = {name.replace("\\", "/") for name in CArchiveReader(str(exe_path)).toc}
    expected = {"voice_stt_client/config.yaml"} | {
        f"voice_stt_client/assets/feedback_sounds/debug/{sound.name}"
        for sound in sounds
    }
    missing = expected - bundled
    if missing:
        raise BuildError(f"Frozen client is missing package assets: {', '.join(sorted(missing))}")


def sanitized_build_path() -> str:
    """Return a PATH that cannot leak unrelated native DLLs into the bundle."""
    windows_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
    candidates = (
        Path(sys.executable).resolve().parent,
        Path(sys.base_prefix).resolve(),
        windows_root / "System32",
        windows_root,
    )
    unique: list[str] = []
    for candidate in candidates:
        value = str(candidate)
        if value.casefold() not in {item.casefold() for item in unique}:
            unique.append(value)
    return os.pathsep.join(unique)


def build(*, clean: bool = False, smoke_test: bool = True, dist_dir: Path | None = None) -> Path:
    if os.name != "nt":
        raise BuildError("The Windows executable must be built on Windows.")
    verify_build_python()
    if dist_dir is not None:
        dist_dir = Path(dist_dir).resolve()
        if dist_dir.parent != REPO_ROOT.resolve() or not dist_dir.name.startswith("dist-"):
            raise BuildError("Alternate dist directory must be a named dist-* folder inside the repository")
        if clean:
            raise BuildError("--clean cannot be combined with --dist-dir")
    if clean:
        clean_outputs()

    exe_path = EXE_PATH if dist_dir is None else dist_dir / EXE_PATH.name

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
        env["PATH"] = sanitized_build_path()
        site_dir = REPO_ROOT / "scripts" / "pyinstaller_site"
        existing_python_path = env.get("PYTHONPATH")
        env["PYTHONPATH"] = os.pathsep.join(
            part for part in (str(site_dir), existing_python_path) if part
        )
        command = [
                sys.executable,
                "-c",
                PYINSTALLER_BOOTSTRAP,
                "--noconfirm",
                "--clean",
            ]
        if dist_dir is not None:
            command.extend(("--distpath", str(dist_dir)))
        command.append(str(SPEC_FILE))
        run(command, env=env)
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    if not exe_path.is_file() or exe_path.stat().st_size == 0:
        raise BuildError(f"Expected executable was not created: {exe_path}")

    if smoke_test:
        verify_frozen_feedback_assets(exe_path)
        for smoke_argument in ("--version", "--verify-gui-runtime"):
            result = subprocess.run(
                [str(exe_path), smoke_argument],
                cwd=REPO_ROOT,
                timeout=60,
                check=False,
            )
            if result.returncode != 0:
                raise BuildError(
                    f"Executable smoke test {smoke_argument} failed with "
                    f"exit code {result.returncode}"
                )

    digest = hashlib.sha256(exe_path.read_bytes()).hexdigest()
    print(f"Built {exe_path.relative_to(REPO_ROOT)} ({exe_path.stat().st_size} bytes)")
    print(f"Version {version}; SHA-256 {digest}")
    return exe_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clean", action="store_true", help="remove previous build output")
    parser.add_argument(
        "--no-smoke", action="store_true", help="skip starting the built executable with --version"
    )
    parser.add_argument("--dist-dir", type=Path, help="build into a separate dist-* folder")
    args = parser.parse_args(argv)
    try:
        build(clean=args.clean, smoke_test=not args.no_smoke, dist_dir=args.dist_dir)
        return 0
    except (BuildError, OSError, subprocess.SubprocessError) as exc:
        print(f"build stopped: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
