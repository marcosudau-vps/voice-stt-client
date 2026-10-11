from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ClientReleaseWorkflowTests(unittest.TestCase):
    def test_tag_last_and_no_tag_push_trigger(self):
        text = (ROOT / ".github/workflows/release.yml").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", text)
        self.assertNotIn("  push:\n", text)
        self.assertLess(text.index("  preflight:"), text.index("  publish-pypi:"))
        self.assertLess(text.index("  publish-pypi:"), text.index("  tag:"))
        self.assertLess(text.index("  tag:"), text.index("  github-release:"))
        self.assertIn("needs: [preflight, publish-pypi]", text)
        self.assertIn("needs: [preflight, tag]", text)
        self.assertLess(text.index("Verify both remote PyPI hashes"), text.index("git tag -a"))
        self.assertIn("source_commit: ${{ steps.identity.outputs.source_commit }}", text)
        self.assertIn("run-id: '${{ inputs.candidate_run_id }}'", text)
        self.assertIn("python scripts/client_release_guard.py verify --dir release", text)


if __name__ == "__main__":
    unittest.main()
