"""Gate-Review II: independent P-8 path boundary probe (B-3)."""
from __future__ import annotations

import io
import os
import tempfile
from contextlib import redirect_stderr
from pathlib import Path

from core.config import (
    DEFAULT_LOCAL_APP_DIR,
    LoggingObservabilityConfig,
    is_inside_user_profile,
    user_profile_roots,
)
from core.observability.manager import ObservabilityManager

print("USERPROFILE            :", os.environ.get("USERPROFILE"))
print("HOME                   :", os.environ.get("HOME"))
print("Path.home()            :", Path.home())
print("LOCALAPPDATA           :", os.environ.get("LOCALAPPDATA"))
print("DEFAULT_LOCAL_APP_DIR  :", DEFAULT_LOCAL_APP_DIR)
print("user_profile_roots()   :")
for r in user_profile_roots():
    print("   ", r)

home = str(Path.home())

CASES = [
    ("gueltig: Profilpfad (Store-Default)",           str(DEFAULT_LOCAL_APP_DIR / "observability.sqlite3"), True),
    ("gueltig: irgendwo im Profil",                   home + r"\obs\obs.sqlite3", True),
    ("gueltig: Profilwurzel selbst",                  home, True),
    ("gueltig: Forward-Slashes im Profil",            home.replace("\\", "/") + "/obs/o.sqlite3", True),
    ("gueltig: gemischte Gross-/Kleinschreibung",     home.upper() + r"\obs\o.sqlite3", True),
    ("gueltig: doppelte Separatoren",                 home + r"\\obs\\o.sqlite3", True),
    ("gueltig: '.'-Segment im Profil",                home + r"\obs\.\o.sqlite3", True),
    ("gueltig: ~ expandiert",                         r"~\obs\o.sqlite3", True),
    ("ABSOLUTER FREMDPFAD",                           r"C:\ProgramData\somewhere-else\o.sqlite3", False),
    ("ABSOLUTER FREMDPFAD (Windows-Dir)",             r"C:\Windows\Temp\o.sqlite3", False),
    ("'..'-ESCAPE aus dem Profil",                    home + r"\AppData\..\..\..\ProgramData\o.sqlite3", False),
    ("'..'-ESCAPE direkt",                            home + r"\..\..\ProgramData\o.sqlite3", False),
    ("FREMDPROFIL",                                   str(Path(home).parent / "anderer-nutzer" / "o.sqlite3"), False),
    ("FREMDPROFIL mit aehnlichem Praefix",            home + "-evil\\o.sqlite3", False),
    ("WINDOWS-LAUFWERKSPFAD (anderes Laufwerk)",      r"D:\logs\o.sqlite3", False),
    ("WINDOWS-LAUFWERKSPFAD (Wurzel C:)",             r"C:\o.sqlite3", False),
    ("UNC-PFAD",                                      r"\\fileserver\share\logs\o.sqlite3", False),
    ("UNC-PFAD (admin share)",                        r"\\127.0.0.1\C$\o.sqlite3", False),
    ("RELATIVER PFAD",                                r"obs\o.sqlite3", False),
    ("LAUFWERKSRELATIV (C:obs)",                      r"C:obs\o.sqlite3", False),
    ("LEERSTRING",                                    "", False),
    ("NUR LEERZEICHEN",                               "   ", False),
]

print("\n" + "=" * 100)
print("1) Config-Grenze: LoggingObservabilityConfig.validate()  (db_path und file_sink_dir)")
print("=" * 100)
print(f"{'Fall':45s} {'erwartet':10s} {'db_path':10s} {'file_sink_dir':14s} {'is_inside':10s}")
fails = []
for label, value, expect_ok in CASES:
    def check(field):
        kw = {field: value}
        cfg = LoggingObservabilityConfig(**kw)
        try:
            cfg.validate()
            return "AKZEPT"
        except ValueError:
            return "ABGEL."
    r_db = check("db_path")
    r_sink = check("file_sink_dir")
    inside = is_inside_user_profile(value) if value.strip() else False
    exp = "AKZEPT" if expect_ok else "ABGEL."
    ok = (r_db == exp) and (r_sink == exp)
    if not ok:
        fails.append((label, value, exp, r_db, r_sink))
    print(f"{label:45s} {exp:10s} {r_db:10s} {r_sink:14s} {str(inside):10s} {'' if ok else '  <== ABWEICHUNG'}")

print("\n" + "=" * 100)
print("2) Produktiver Managerpfad: ObservabilityManager._resolve_profile_path")
print("=" * 100)
default_db = DEFAULT_LOCAL_APP_DIR / "observability.sqlite3"
for label, value, expect_ok in CASES:
    buf = io.StringIO()
    with redirect_stderr(buf):
        resolved = ObservabilityManager._resolve_profile_path(value, default_db, "db_path")
    used_default = Path(resolved) == Path(default_db)
    inside = is_inside_user_profile(resolved)
    note = "uebernommen" if not used_default else "DEFAULT statt Konfigwert"
    warned = "path_outside_user_profile" in buf.getvalue()
    flag = ""
    if expect_ok and used_default:
        flag = "  <== gueltiger Pfad wurde verworfen"
    if (not expect_ok) and not used_default:
        flag = "  <== UNGUELTIGER PFAD WURDE UEBERNOMMEN"
    if not inside:
        flag += "  <== ERGEBNIS AUSSERHALB DES PROFILS"
    print(f"{label:45s} {note:26s} warn={str(warned):5s} inside={str(inside):5s}{flag}")

print("\n" + "=" * 100)
print("3) Manager end-to-end: Store-/Sink-Pfad bei feindlicher Konfiguration")
print("=" * 100)
hostile = r"C:\ProgramData\obs-gate-review\o.sqlite3"
hostile_dir = r"\\fileserver\share\obs"
cfg = LoggingObservabilityConfig(
    db_path=hostile, file_sink_enabled=True, file_sink_dir=hostile_dir
)
buf = io.StringIO()
with redirect_stderr(buf):
    mgr = ObservabilityManager(cfg)
store = mgr._worker._store
sink = mgr._worker._sink
print("store path :", getattr(store, "path", None))
print("sink dir   :", getattr(sink, "_directory", getattr(sink, "directory", None)))
print("inside profile (store):", is_inside_user_profile(getattr(store, "path", "")))
print("stderr:", buf.getvalue().strip())
print("Verzeichnis C:\\ProgramData\\obs-gate-review angelegt?",
      Path(r"C:\ProgramData\obs-gate-review").exists())

print("\n" + "=" * 100)
print("4) AppConfig.validate() ruft die Observability-Validierung?")
print("=" * 100)
from core.config import AppConfig
cfg = AppConfig()
cfg.logging.observability.db_path = r"C:\ProgramData\evil\o.sqlite3"
try:
    cfg.validate()
    print("AppConfig.validate(): AKZEPTIERT  <== P-8 nicht durchgesetzt")
except ValueError as exc:
    print("AppConfig.validate(): ValueError ->", exc)

print("\n" + "=" * 100)
print("5) P-9: -wal/-shm im selben Verzeichnis")
print("=" * 100)
from core.observability.storage.sqlite import SQLiteLogStore
tmp = Path(tempfile.mkdtemp()) / "sub" / "obs.sqlite3"
s = SQLiteLogStore(tmp)
s.open()
from uuid import uuid4
from core.observability.models import CanonicalLogRecord
s.write_batch([CanonicalLogRecord(
    record_id=uuid4().hex, received_at="2026-08-17T10:00:00.000Z",
    producer_kind="client", producer_id="p", instance_id="i",
    scope="instance", channel="system", level="INFO")])
siblings = sorted(p.name for p in tmp.parent.iterdir())
s.close()
print("Dateien im Zielverzeichnis:", siblings)

if fails:
    print("\nABWEICHUNGEN:")
    for f in fails:
        print("  ", f)
else:
    print("\nAlle Config-Grenzfaelle verhalten sich wie erwartet.")
