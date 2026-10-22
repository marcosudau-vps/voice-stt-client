import tempfile,unittest
from pathlib import Path
from tests.manual.v2.admin_guard_probe import read_key


class ExplicitAdminSource(unittest.TestCase):
    def test_quoted_literal_is_not_environment_interpolated(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.env';p.write_text('VOICESTT_ADMIN_API_KEY="sample-${UNSET_VALUE}-#-literal"\n')
            self.assertEqual(read_key(p),'sample-${UNSET_VALUE}-#-literal')

    def test_missing_key_does_not_fall_back_to_environment_or_another_variable(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.env';p.write_text('OTHER_KEY=sample\n')
            with self.assertRaises(ValueError):read_key(p)

    def test_multiline_value_is_rejected_without_echoing_it(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.env';p.write_text('VOICESTT_ADMIN_API_KEY="line1\nline2"\n')
            with self.assertRaisesRegex(ValueError,'missing or invalid'):read_key(p)
