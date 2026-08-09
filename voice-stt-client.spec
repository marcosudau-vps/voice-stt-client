# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path


ROOT = Path.cwd()
version_file = os.environ.get("VOICE_STT_VERSION_FILE")
if not version_file:
    raise RuntimeError("VOICE_STT_VERSION_FILE must be provided by scripts/build.py")

a = Analysis(
    [str(ROOT / "app.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=[
        (str(ROOT / "config.yaml"), "."),
        (str(ROOT / "VERSION"), "."),
    ],
    hiddenimports=["PySide6.QtMultimedia"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
