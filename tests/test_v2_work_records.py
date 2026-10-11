"""Generic V2 record checks, including the actual R02 link/status defects."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/GEMEINSAM/scripts/pruefe_arbeitsakten.py"
spec = importlib.util.spec_from_file_location("v2_records", SCRIPT)
records = importlib.util.module_from_spec(spec)
spec.loader.exec_module(records)


class WorkRecords(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.block = Path(folder.name)

    def write(self, path, text):
        file = self.block / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(text, encoding="utf-8")
        return file

    def fixture(self, status="REVIEW_READY", package="AP-IV2-020"):
        self.package = package
        prefix = f"30_AUSFUEHRUNG/{package}"
        self.index = self.write(f"{prefix}/00_PAKET.md", f"Status **{status}**\n[Report](RUNS/R02-ABNAHME/01_REPORT.md)\n")
        self.write(f"{prefix}/RUNS/R02-ABNAHME/01_REPORT.md", "Historical status **CHANGES_REQUIRED**\n")
        self.write(f"{prefix}/RUNS/R03-KORREKTUR/00_PROMPT_ORIGINAL.md", "Actual human prompt\n")
        self.write("WORKFLOW_STATUS.json", json.dumps({
            "activePackage": package, "packageStatus": status,
            "reviewReport": f"{prefix}/RUNS/R02-ABNAHME/01_REPORT.md",
            "workAuthorization": {"source": f"{prefix}/RUNS/R03-KORREKTUR/00_PROMPT_ORIGINAL.md"},
        }))
        self.write(f"PLANUNG/ARBEITSPAKETE/{package}.md", f"**Status:** {status}\n")
        self.manifest = self.write("PLANUNG/EVIDENCE/package-manifest.json", json.dumps({"packages": [{
            "id": package, "status": status, "path": f"ARBEITSPAKETE/{package}.md",
        }]}))

    def test_valid_different_packages_and_statuses_preserve_historical_verdict(self):
        for package in ("AP-IV2-020", "AP-CV2-030"):
            for status in ("REVIEW_READY", "CHANGES_REQUIRED", "IN_PROGRESS", "ROOT_PASS", "BLOCKED"):
                with self.subTest(package=package, status=status):
                    self.fixture(status, package)
                    self.assertEqual(records.validate_records(self.block)["result"], "PASS")

    def test_actual_repeated_package_prefix_breaks_relative_link(self):
        self.fixture(package="AP-CV2-000")
        self.index.write_text("Status **REVIEW_READY**\n[Report](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R02-ABNAHME/01_REPORT.md)\n")
        result = records.validate_records(self.block)
        self.assertEqual(result["result"], "FAIL")
        self.assertTrue(any("Broken link" in error for error in result["errors"]))

    def test_actual_stale_manifest_review_ready_after_changes_required(self):
        self.fixture("CHANGES_REQUIRED")
        manifest = json.loads(self.manifest.read_text())
        manifest["packages"][0]["status"] = "REVIEW_READY"
        self.manifest.write_text(json.dumps(manifest))
        self.assertIn("Status mismatch", "\n".join(records.validate_records(self.block)["errors"]))

    def test_missing_referenced_original_prompt_fails(self):
        self.fixture()
        (self.block / f"30_AUSFUEHRUNG/{self.package}/RUNS/R03-KORREKTUR/00_PROMPT_ORIGINAL.md").unlink()
        self.assertEqual(records.validate_records(self.block)["result"], "FAIL")

    def test_package_header_and_index_must_match_active_state(self):
        self.fixture()
        self.index.write_text("Status **IN_PROGRESS**\n")
        self.assertEqual(records.validate_records(self.block)["result"], "FAIL")

    def test_encoded_relative_link_and_code_examples(self):
        self.fixture()
        self.write(f"30_AUSFUEHRUNG/{self.package}/Run note.md", "note")
        with self.index.open("a") as stream:
            stream.write('[Note](Run%20note.md#heading)\n```text\n[Example](not-a-file.md)\n```\n')
        self.assertEqual(records.validate_records(self.block)["result"], "PASS")

    def test_optional_pr_summary_must_match(self):
        self.fixture()
        summary = self.write("pr.md", f"{self.package}\n**Status:** CHANGES_REQUIRED\n")
        self.assertEqual(records.validate_records(self.block, pr_summary=summary)["result"], "FAIL")
        summary.write_text(f"{self.package}\n**Status:** REVIEW_READY\n")
        self.assertEqual(records.validate_records(self.block, pr_summary=summary)["result"], "PASS")
