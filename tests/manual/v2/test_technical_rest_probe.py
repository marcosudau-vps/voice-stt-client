import unittest
from tests.manual.v2.technical_rest_probe import admission_consistent


class Admission(unittest.TestCase):
    def test_refresh_success_is_not_a_second_manual_activation(self):
        self.assertTrue(admission_consistent('wake_word',[dict(action='refresh',accepted=True)]))
        self.assertTrue(admission_consistent('wake_word',[dict(action='activate',accepted=False)]))
        self.assertTrue(admission_consistent('manual',[dict(action='activate',accepted=True)]))
        self.assertFalse(admission_consistent('manual',[dict(action='refresh',accepted=True)]))
