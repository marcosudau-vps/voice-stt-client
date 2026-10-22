import io,unittest
from tests.manual.v2.isolated_windows_suite import observed_ids


class DiscoveryEvidence(unittest.TestCase):
    def test_actual_verbose_log_preserves_ids_with_multiline_docstrings(self):
        class Cases(unittest.TestCase):
            def test_plain(self):pass
            def test_documented(self):
                """A real unittest description moves the status to another line."""
        suite=unittest.defaultTestLoader.loadTestsFromTestCase(Cases)
        expected={case.id() for case in suite}
        output=io.StringIO();result=unittest.TextTestRunner(stream=output,verbosity=2).run(suite)
        self.assertTrue(result.wasSuccessful())
        self.assertEqual(observed_ids(output.getvalue()),expected)
        self.assertEqual(observed_ids(output.getvalue()+'\nTraceback (most recent call last):\n'),expected)
