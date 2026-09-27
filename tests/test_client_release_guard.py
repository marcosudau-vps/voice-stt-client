from __future__ import annotations

import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path

from scripts.client_release_guard import candidate_files, pypi_states, sha256


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


class ClientReleaseGuardTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.files = {
            "exe": self.root / "voice-stt-client.exe",
            "wheel": self.root / "voice_stt_client-1.0.0-py3-none-any.whl",
            "sdist": self.root / "voice_stt_client-1.0.0.tar.gz",
        }
        for kind, path in self.files.items():
            path.write_bytes(kind.encode())

    def test_candidate_has_exact_three_products(self):
        self.assertEqual(candidate_files(self.root), self.files)
        renamed = self.root / "voice-stt-client-v1.0.0-windows-x64.exe"
        self.files["exe"].rename(renamed)
        self.assertEqual(candidate_files(self.root)["exe"], renamed)
        (self.root / "extra.exe").write_bytes(b"other")
        with self.assertRaises(ValueError):
            candidate_files(self.root)

    def test_absent_and_match(self):
        def absent(_request, timeout):
            raise urllib.error.HTTPError("url", 404, "missing", {}, None)

        dist = {kind: self.files[kind] for kind in ("wheel", "sdist")}
        self.assertEqual(set(pypi_states(dist, fetch=absent).values()), {"ABSENT"})
        payload = {"urls": [{"filename": p.name, "digests": {"sha256": sha256(p)}} for p in dist.values()]}
        self.assertEqual(
            set(pypi_states(dist, fetch=lambda *_a, **_k: FakeResponse(json.dumps(payload).encode())).values()),
            {"MATCH"},
        )

    def test_conflict_and_unexpected_file_stop(self):
        dist = {kind: self.files[kind] for kind in ("wheel", "sdist")}
        payload = {"urls": [{"filename": self.files["wheel"].name, "digests": {"sha256": "0" * 64}}]}
        with self.assertRaisesRegex(ValueError, "conflict"):
            pypi_states(dist, fetch=lambda *_a, **_k: FakeResponse(json.dumps(payload).encode()))
        payload["urls"][0]["filename"] = "unexpected.whl"
        with self.assertRaisesRegex(ValueError, "unexpected"):
            pypi_states(dist, fetch=lambda *_a, **_k: FakeResponse(json.dumps(payload).encode()))


if __name__ == "__main__":
    unittest.main()
