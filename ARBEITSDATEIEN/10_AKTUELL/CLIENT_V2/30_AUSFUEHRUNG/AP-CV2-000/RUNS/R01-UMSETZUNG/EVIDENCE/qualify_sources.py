"""Reproduce namespace-only core/trigger and installed-resource comparisons."""
import hashlib
import re
import subprocess
from pathlib import Path

root = Path(__file__).resolve().parents[8]
parent = "050e776cf316eb332177294db0c0a2719c2b4415"
files = ["core/controller.py", "core/stt_session.py", "tests/test_trigger_lifecycle.py",
         "tests/test_trigger_feedback_contract.py", "tests/test_ap_cli_000_baseline_characterization.py"]
for original in files:
    old = subprocess.check_output(["git", "show", f"{parent}:{original}"], cwd=root).decode("utf-8-sig")
    newpath = original if original.startswith("tests/") else "voice_stt_client/" + original
    new = (root / newpath).read_text(encoding="utf-8-sig")
    # Normalize only Python namespace prefixes, leaving logger/component names intact.
    old = re.sub(r"(?m)^(\s*(?:from|import) )((?:core|ui)(?:\.|\b))", r"\1voice_stt_client.\2", old)
    for module in ("core", "ui", "app"):
        old = re.sub(r"([\"'])" + module + r"(?=\.[A-Za-z_])", r"\1voice_stt_client." + module, old)
    if original == "tests/test_trigger_feedback_contract.py":
        old = old.replace('/ "assets"', '/ "voice_stt_client"\n            / "assets"')
    assert old.replace("\r\n", "\n") == new.replace("\r\n", "\n"), newpath
    print("PASS namespace-only:", newpath)
for original in ["config.yaml", "requirements.txt"]:
    newpath = "voice_stt_client/" + original if original == "config.yaml" else original
    old = subprocess.check_output(["git", "show", f"{parent}:{original}"], cwd=root)
    assert old.replace(b"\r\n", b"\n") == (root / newpath).read_bytes().replace(b"\r\n", b"\n"), newpath
    print("PASS text-preserved (Git/Windows EOL normalized):", newpath)
for p in sorted((root / "voice_stt_client/assets").rglob("*")):
    if p.is_file():
        original = p.relative_to(root / "voice_stt_client").as_posix()
        old = subprocess.check_output(["git", "show", f"{parent}:{original}"], cwd=root)
        assert old == p.read_bytes(), original
        print("PASS asset:", original, hashlib.sha256(old).hexdigest())
wheel = Path(__file__).with_name("wheel-smoke.txt").read_text(encoding="utf-8-sig")
sdist = Path(__file__).with_name("sdist-smoke.txt").read_text(encoding="utf-8-sig")
assert wheel == sdist, "wheel/sdist package content mismatch"
for p in sorted((root / "voice_stt_client").rglob("*")):
    if p.is_file() and p.suffix in {".py", ".yaml", ".wav", ".md"}:
        expected = f"{hashlib.sha256(p.read_bytes()).hexdigest()} {p.relative_to(root / 'voice_stt_client')}"
        assert expected in wheel, expected
print("PASS: wheel and sdist manifests equal source package; no stale artifact code")
