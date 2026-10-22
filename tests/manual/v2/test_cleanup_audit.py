import hashlib,json,tempfile,unittest
from pathlib import Path
from tests.manual.v2.cleanup_audit import inspect_folder

class CleanupAudit(unittest.TestCase):
    def test_all_historical_manifest_formats_are_read_only_and_detect_changes(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);s=root/'source';a=root/'archive';s.mkdir();a.mkdir()
            (s/'x').write_bytes(b'fixture');(a/'x').write_bytes(b'fixture')
            h=hashlib.sha256(b'fixture').hexdigest()
            for m in ({'x':h},{'files':{'x':h}},{'files':[dict(path='x',sha256=h)]}):
                (a/'archive-manifest.json').write_text(json.dumps(m),encoding='utf8')
                self.assertEqual(inspect_folder(s,a)['result'],'ARCHIVED_HASH_VERIFIED')
            (s/'x').write_bytes(b'changed')
            self.assertEqual(inspect_folder(s,a)['result'],'ARCHIVE_NEEDS_RECONCILIATION')
            self.assertTrue((s/'x').exists())
    def test_extra_files_or_manifest_escape_never_count_as_verified(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t);s=root/'source';a=root/'archive';s.mkdir();a.mkdir()
            (a/'archive-manifest.json').write_text('{"files": []}',encoding='utf8')
            self.assertEqual(inspect_folder(s,a)['result'],'ARCHIVED_HASH_VERIFIED')
            (s/'new').write_bytes(b'not archived')
            self.assertEqual(inspect_folder(s,a)['result'],'ARCHIVE_NEEDS_RECONCILIATION')
            (a/'archive-manifest.json').write_text(json.dumps({'files':{'../escape':'a'*64}}),encoding='utf8')
            with self.assertRaises(ValueError):inspect_folder(s,a)
