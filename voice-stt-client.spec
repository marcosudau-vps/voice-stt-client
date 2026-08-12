# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs


ROOT = Path.cwd()
FEEDBACK_SOUNDS = ROOT / "assets" / "feedback_sounds" / "debug"
version_file = os.environ.get("VOICE_STT_VERSION_FILE")
if not version_file:
    raise RuntimeError("VOICE_STT_VERSION_FILE must be provided by scripts/build.py")

# The effect catalogues are data, not code: lefx.sets.<name>.package_file()
# returns a path beside its own module, so the archives have to land at the same
# relative place inside the bundle. collect_data_files puts them there.
lefx_catalogues = collect_data_files("lefx", includes=["**/*.lefxset"])
if not lefx_catalogues:
    raise RuntimeError(
        "No .lefxset archives found in the installed lefx package. The build "
        "would produce a client whose every LED rule fails to resolve."
    )

a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT)],
    binaries=collect_dynamic_libs("libusb_package"),
    datas=[
        (str(ROOT / "config.yaml"), "."),
        (str(ROOT / "VERSION"), "."),
        (str(FEEDBACK_SOUNDS), "assets/feedback_sounds/debug"),
        *lefx_catalogues,
    ],
    hiddenimports=[
        "PySide6.QtMultimedia",
        "usb.core",
        "usb.util",
        "libusb_package",
        # Reached through importlib by name, so static analysis cannot see them.
        "lefx.sets.core_set",
        "lefx.sets.smartspeaker_set",
        # The hardware output is built directly rather than looked up through
        # entry points, because a frozen build carries no distribution metadata.
        "lefx.device.respeaker.registration",
        # What the effects themselves import. They live inside the .lefxset
        # archives and are extracted and imported at run time, so no static
        # analysis can see them -- a frozen build without these loads the
        # catalogue halfway and says so only in a log line. Kept in step with
        # the sets: an effect that imports something new needs it named here.
        "colorsys",
        "math",
        "random",
    ],
    hookspath=[],
    hooksconfig={},
    # Runs at bootstrap, before the application imports anything. Python's
    # Windows platform probes reach for WMI, which is slow on the first call and
    # can be far worse on a managed machine -- and libusb_package asks for
    # platform.system() while it is being imported. Neutralised once, up front,
    # rather than worked around at each call site.
    runtime_hooks=[str(ROOT / "scripts" / "pyinstaller_runtime_platform.py")],
    # The embedded controller never serves HTTP. Since lefx.interfaces resolves
    # create_app lazily, nothing imports this chain any more -- excluding it
    # keeps that true rather than trusting it to stay true.
    excludes=[
        "fastapi",
        "starlette",
        "uvicorn",
        "pydantic",
        "lefx.interfaces.api",
        "lefx.interfaces.cli",
        # The simulator is a diagnostic tool and a separate program; it has no
        # place in a release build.
        "lefx.device.simulated_respeaker",
    ],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="voice-stt-client",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version=version_file,
)
