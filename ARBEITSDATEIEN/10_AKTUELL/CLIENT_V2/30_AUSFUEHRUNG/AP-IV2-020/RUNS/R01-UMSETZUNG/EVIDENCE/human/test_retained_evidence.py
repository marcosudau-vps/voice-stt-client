"""Protect the retrospective matcher against falsely joining different sessions."""
from pathlib import Path
import unittest

from resolve_retained_evidence import select_observation


class ObservationIdentityTests(unittest.TestCase):
    def setUp(self):
        self.trace = [{'kind': 'ack', 'commandId': 'own', 'timeUtc': '2026-10-19T10:00:00+00:00'}]
        self.event = {'timeUtc': '2026-10-19T10:00:01+00:00'}

    def test_command_identity_wins_over_folder_and_clock(self):
        path, _, count, method = select_observation(self.trace, [
            (Path('different-folder'), [{'timeUtc': '2026-10-19T10:00:10+00:00'}], {'own'})])
        self.assertEqual(path, Path('different-folder'))
        self.assertEqual(count, 1)
        self.assertEqual(method, 'SHARED_COMMAND_IDS')

    def test_conflicting_command_identity_cannot_fall_back_to_time(self):
        self.assertIsNone(select_observation(self.trace, [(Path('other'), [self.event], {'foreign'})])[0])

    def test_legacy_unique_time_is_explicitly_weaker(self):
        result = select_observation(self.trace, [(Path('legacy'), [self.event], set())])
        self.assertEqual(result[0], Path('legacy'))
        self.assertIn('NOT_COMMAND_ID_PROOF', result[3])

    def test_legacy_ambiguous_time_cannot_choose_a_session(self):
        self.assertIsNone(select_observation(self.trace, [
            (Path('one'), [self.event], set()), (Path('two'), [self.event], set())])[0])

    def test_same_command_in_multiple_observers_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Ambiguous'):
            select_observation(self.trace, [
                (Path('one'), [self.event], {'own'}), (Path('two'), [self.event], {'own'})])


if __name__ == '__main__':
    unittest.main()
