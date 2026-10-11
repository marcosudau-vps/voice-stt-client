"""Validate the specific revision-10 V2 record scheme, not the older block model."""
import json
import re
from pathlib import Path

root = Path(__file__).resolve().parents[8]
block = root / "ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2"
state = json.loads((block / "WORKFLOW_STATUS.json").read_text(encoding="utf-8"))
assert state["activePackage"] == "AP-CV2-000"
assert state["workflowPhase"] == state["packageStatus"] == "REVIEW_READY"
assert state["canonicalParent"] == "050e776cf316eb332177294db0c0a2719c2b4415"
assert state["reviewedCommit"] is state["humanApproval"] is state["writeOwner"] is None
assert state["openFindingIds"] == []
for p in [state["lastRun"]["report"], state["lastRun"]["evidence"], state["workAuthorization"]["source"]]:
    assert (block / p).is_file(), p
reqs = json.loads((block / "PLANUNG/REFERENZ/TRACEABILITY/requirements.json").read_text(encoding="utf-8"))["requirements"]
bases = [r for r in reqs if r["ap"] == "AP-CV2-000"]
assert len(bases) == 12
for r in bases:
    assert r["status"] == "CLIENT OPEN"
    e = r["implementationEvidence"]
    assert e["methods"] and e["state"] == "SELF_CHECK_PASS_REVIEW_READY"
    assert (block / e["report"]).is_file() and (block / e["evidence"]).is_file()
packages = json.loads((block / "PLANUNG/EVIDENCE/package-manifest.json").read_text(encoding="utf-8"))["packages"]
assert packages[0]["status"] == "REVIEW_READY"
assert all(p["status"] == ("CONDITIONAL" if p["id"] == "AP-SV2-FIX" else "PLANNED") for p in packages[1:])
paths = [block / "30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md", block / state["lastRun"]["report"],
         block / state["lastRun"]["evidence"], root / "docs/compatibility.md", root / "docs/RELEASE.md"]
for p in paths:
    for target in re.findall(r"\]\(([^)]+)\)", p.read_text(encoding="utf-8")):
        if "://" not in target and not target.startswith("#"):
            assert (p.parent / target.split("#")[0]).is_file(), (p.name, target)
log = (root / "ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md").read_text(encoding="utf-8")
assert log.count("## AP-CV2-000-R01 ") == 1
print("PASS: revision-10 run records, relative links, 12 requirements, no premature PASS/adoption; one milestone")
