import unittest
from tests.manual.v2.frozen_acoustic_probe import expected_append, all_cases_passed


class FrozenAttemptAssessment(unittest.TestCase):
    def test_retry_does_not_require_pasting_previous_failed_history(self):
        self.assertEqual(expected_append('', ['failed first', 'retry'], 1), 'retry ')

    def test_successful_prior_editor_content_is_preserved(self):
        self.assertEqual(expected_append('first ', ['first', 'second '], 1), 'first second ')

    def test_repeating_one_task_cannot_pass_another_missing_task(self):
        rows=[dict(name='manual', nativeTextMatchesHistory=True)]*2
        self.assertFalse(all_cases_passed(rows, ['manual', 'wake']))

    def test_failed_attempt_remains_but_successful_retry_counts(self):
        rows=[dict(name='manual', nativeTextMatchesHistory=False),
              dict(name='manual', nativeTextMatchesHistory=True),
              dict(name='wake', nativeTextMatchesHistory=True)]
        self.assertTrue(all_cases_passed(rows, ['manual', 'wake']))
