"""UX01: output spacing through mirror, final consumer, SQLite and queue worker.

Only Win32 I/O is replaced; authoritative finals and persisted origins stay raw.
"""
from pathlib import Path
import tempfile
import threading
import unittest

from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.activation_mirror import ActivationMirror
from voice_stt_client.core.config import AppConfig, HistoryPersistentConfig
from voice_stt_client.core.final_results import V2ResultService
from voice_stt_client.core.history import TranscriptHistoryManager
from voice_stt_client.core.reinsertion import TranscriptReinsertionService
from voice_stt_client.core.text_injector import TextInjectionQueue
from tests.test_text_injector import MockInjectionBackend
from tests.test_v2_mirror import msg, snapshot


class OutputSpacing(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.db = Path(tmp.name) / 'history.sqlite'
        self.config = AppConfig()
        self.config.history.persistent = HistoryPersistentConfig(
            enabled=True, store_all=True, max_entries=0, retention_days=0)
        self.config.text_injection.paste_delay_ms = 0
        self.config.clipboard.restore_previous = False
        self.config.clipboard.restore_delay_ms = 0
        self.history = TranscriptHistoryManager(self.config.history, str(self.db))
        self.backend = MockInjectionBackend()
        self.queue = TextInjectionQueue(self.config, self.history, self.backend)
        self.queue.start()
        self.addCleanup(lambda: self.queue.stop(timeout=2))
        self.service = V2ResultService(self.history, self.queue)
        self.mirror = ActivationMirror()
        self.service.consume(self.mirror.begin(1, snapshot(), 1))
        self.seq = 0

    def final(self, text):
        self.seq += 1
        reduction = self.mirror.consume(1, msg(
            p.EventType.COMPLETED, self.seq, sid=p.new_id(),
            segment_sequence=self.seq, text=text), 1)
        outcomes = self.service.consume(reduction)
        self.assertEqual(outcomes[0].status, 'queued')
        self.drain()
        self.assertEqual(reduction.finals[0].text, text)
        return reduction

    def drain(self):
        # Bounded wait also verifies that the serial worker has no stranded job.
        done = threading.Event()
        def barrier():
            self.queue._queue.join()
            done.set()
        waiter = threading.Thread(target=barrier, daemon=True)
        waiter.start()
        self.assertTrue(done.wait(3), 'Injection worker did not drain')
        waiter.join(1)

    def test_default_separates_finals_without_changing_history_or_replay(self):
        self.assertTrue(self.config.text_injection.append_space)
        originals = ['Erster Satz.', 'Zweiter Satz äöü.']
        reductions = [self.final(text) for text in originals]
        for reduction in reductions:
            self.assertEqual([o.status for o in self.service.consume(reduction)],
                             ['deduplicated'])
        self.drain()
        entries = self.history.get_persistent_entries()
        self.assertEqual([e.text for e in entries], originals)
        self.assertEqual([e.text_length for e in entries], list(map(len, originals)))
        self.assertEqual(self.backend.set_calls, [t + ' ' for t in originals])
        self.assertEqual(len(self.backend.send_input_calls), 2)
        for entry, reduction in zip(entries, reductions):
            final = reduction.finals[0]
            self.assertEqual((entry.session_id, entry.activation_id, entry.segment_id,
                              entry.segment_sequence, entry.event_id, entry.event_seq),
                             (final.session_id, final.activation_id, final.segment_id,
                              final.segment_sequence, final.event_id, final.event_seq))
            self.assertEqual([(a.source, a.status) for a in entry.attempts],
                             [('automatic', 'command_sent')])
        self.assertEqual(TranscriptHistoryManager(self.config.history, str(self.db))
                         .get_persistent_entries(), entries)
        self.assertEqual(len(self.backend.send_input_calls), 2)

    def test_manual_reinsertion_adds_one_suffix_and_separate_attempt(self):
        self.final('Noch einmal.')
        entry = self.history.get_persistent_entries()[0]
        result = TranscriptReinsertionService(self.history, self.queue).reinsert_entry(entry.id)
        self.assertEqual(result.status.value, 'queued')
        self.drain()
        entries = self.history.get_persistent_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual((entries[0].id, entries[0].text), (entry.id, 'Noch einmal.'))
        self.assertEqual([(a.source, a.status) for a in entries[0].attempts],
                         [('automatic', 'command_sent'), ('manual', 'command_sent')])
        self.assertEqual(self.backend.set_calls, ['Noch einmal. ', 'Noch einmal. '])
        self.assertEqual(len(self.backend.send_input_calls), 2)

    def test_disabled_preference_preserves_exact_payload(self):
        self.config.text_injection.append_space = False
        self.final('Ohne Zusatz.')
        self.assertEqual(self.backend.set_calls, ['Ohne Zusatz.'])

    def test_existing_trailing_whitespace_is_preserved_exactly(self):
        texts = ['Leerzeichen. ', 'Zeilenende.\n', 'Tab.\t', 'Unicode.\u00a0']
        for text in texts:
            self.final(text)
        self.assertEqual(self.backend.set_calls, texts)

    def test_clipboard_restore_keeps_spaced_payload_and_raw_history(self):
        self.config.clipboard.restore_previous = True
        self.backend.clipboard_data = 'Benutzerablage'
        self.final('Ausgabe.')
        self.assertEqual(self.backend.set_calls, ['Ausgabe. ', 'Benutzerablage'])
        self.assertEqual(self.backend.clipboard_data, 'Benutzerablage')
        entry = self.history.get_persistent_entries()[0]
        self.assertEqual(entry.text, 'Ausgabe.')
        self.assertEqual([a.status for a in entry.attempts], ['command_sent'])


if __name__ == '__main__':
    unittest.main()
