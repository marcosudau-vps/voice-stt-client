import tempfile
import unittest
from pathlib import Path

from core.version import read_version
from scripts.build import render_windows_version_info
from scripts.release import Abort, determine_release_version, next_patch, write_version


class VersionTests(unittest.TestCase):
    def test_repository_version_is_valid(self):
        self.assertRegex(read_version(), r"^\d+\.\d+\.\d+$")

    def test_next_patch(self):
        self.assertEqual(next_patch("1.2.3"), "1.2.4")

    def test_first_release_reuses_untagged_version(self):
        self.assertEqual(determine_release_version("0.1.0", set()), "0.1.0")

    def test_tagged_version_advances_patch(self):
        self.assertEqual(
            determine_release_version("0.1.0", {"v0.1.0"}),
            "0.1.1",
        )

    def test_version_behind_tag_is_rejected(self):
        with self.assertRaises(Abort):
            determine_release_version("0.1.0", {"v0.2.0"})

    def test_write_version_uses_single_line(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "VERSION"
            write_version("2.3.4", path)
            self.assertEqual(path.read_text(encoding="utf-8"), "2.3.4\n")

    def test_windows_version_resource_uses_release_version(self):
        rendered = render_windows_version_info("2.3.4")
        self.assertIn("filevers=(2, 3, 4, 0)", rendered)
        self.assertIn("ProductVersion', '2.3.4'", rendered)


if __name__ == "__main__":
    unittest.main()
