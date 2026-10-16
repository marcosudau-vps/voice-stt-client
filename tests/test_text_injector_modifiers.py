"""UX02 through real mirror/final/history/worker; only Win32 is replaced."""
import threading
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from tests import test_text_injector_spacing as spacing
from voice_stt_client.core import protocol_v2 as p
from voice_stt_client.core.reinsertion import TranscriptReinsertionService
from voice_stt_client.core.text_injector import CtypesWindowsInjectionBackend
from tests.test_v2_mirror import msg


class ModifierInjection(unittest.TestCase):
    setUp = spacing.OutputSpacing.setUp
    drain = spacing.OutputSpacing.drain

    def publish(self, text='Bewusste Testprobe.'):
        self.seq += 1
        reduction=self.mirror.consume(1,msg(p.EventType.COMPLETED,self.seq,
            sid=p.new_id(),segment_sequence=self.seq,text=text),1)
        self.assertEqual(self.service.consume(reduction)[0].status,'queued')

    def hold(self,key=0x10):
        self.held=True
        self.probed=threading.Event()
        self.reads=0
        def modifiers():
            self.reads += 1
            if self.reads >= 2:self.probed.set()
            return (key,) if self.held else ()
        self.backend.get_pressed_modifiers=modifiers

    def entry(self):
        return self.history.get_persistent_entries()[-1]

    def test_all_modifiers_defer_clipboard_and_send_until_release(self):
        for key in (0x10,0x11,0x12,0x5b,0x5c):
            with self.subTest(key=key):
                self.hold(key)
                before=(len(self.backend.set_calls),len(self.backend.send_input_calls))
                self.publish()
                self.assertTrue(self.probed.wait(.5),'Worker must query held modifiers')
                self.assertEqual((len(self.backend.set_calls),len(self.backend.send_input_calls)),before)
                self.held=False
                self.drain()
                self.assertEqual(len(self.backend.send_input_calls),before[1]+1)
                self.assertEqual(self.entry().text,'Bewusste Testprobe.')
                self.assertEqual(self.entry().attempts[0].status,'command_sent')

    def test_timeout_skips_without_clipboard_change_or_later_retry(self):
        self.hold()
        self.backend.clipboard_data='Unberührte Testablage'
        with patch('voice_stt_client.core.text_injector.MODIFIER_RELEASE_TIMEOUT_S',.03,create=True):
            self.publish();self.drain()
        self.assertEqual(self.backend.clipboard_data,'Unberührte Testablage')
        self.assertEqual(self.backend.set_calls,[])
        self.assertEqual(self.backend.send_input_calls,[])
        self.assertEqual(self.entry().attempts[0].status,'skipped')
        self.assertIn('Modifier',self.entry().attempts[0].error)
        self.held=False
        self.drain()
        self.assertEqual(self.backend.send_input_calls,[])

    def test_shutdown_interrupts_held_modifier_wait(self):
        self.hold();self.publish()
        self.assertTrue(self.probed.wait(.5))
        self.queue.stop(timeout=.5)
        self.assertFalse(self.queue._worker_thread.is_alive())
        self.assertEqual(self.backend.send_input_calls,[])
        self.assertEqual(self.entry().attempts[0].status,'skipped')

    def test_focus_changed_during_wait_is_not_retargeted(self):
        self.hold();self.publish()
        self.assertTrue(self.probed.wait(.5))
        self.backend.foreground_window=99
        self.held=False;self.drain()
        self.assertEqual(self.backend.set_calls,[])
        self.assertEqual(self.backend.send_input_calls,[])
        self.assertEqual(self.entry().attempts[0].status,'skipped')

    def test_clipboard_changed_during_wait_is_not_overwritten(self):
        self.hold();self.publish()
        self.assertTrue(self.probed.wait(.5))
        self.backend.clipboard_data='Neuere bewusste Testablage'
        self.backend.sequence_number+=1
        self.held=False;self.drain()
        self.assertEqual(self.backend.clipboard_data,'Neuere bewusste Testablage')
        self.assertEqual(self.backend.set_calls,[])
        self.assertEqual(self.backend.send_input_calls,[])

    def test_modifier_pressed_after_clipboard_write_also_defers_send(self):
        self.hold();self.held=False
        original=self.backend.set_clipboard_data_unicode
        def write(text):
            result=original(text)
            self.held=True
            return result
        self.backend.set_clipboard_data_unicode=write
        self.publish()
        self.assertTrue(self.probed.wait(.5))
        self.assertEqual(self.backend.send_input_calls,[])
        self.held=False;self.drain()
        self.assertEqual(len(self.backend.send_input_calls),1)

    def test_external_clipboard_before_send_is_not_pasted_or_restored_over(self):
        original=self.backend.get_foreground_window
        def foreground():
            self.backend.clipboard_data='Andere Testablage'
            self.backend.sequence_number+=1
            return original()
        self.backend.get_foreground_window=foreground
        self.publish();self.drain()
        self.assertEqual(self.backend.send_input_calls,[])
        self.assertEqual(self.backend.clipboard_data,'Andere Testablage')
        self.assertEqual(self.entry().attempts[0].status,'skipped')

    def test_manual_reinsert_uses_same_barrier_and_preserves_raw_entry(self):
        self.publish();self.drain()
        entry=self.entry()
        self.hold()
        self.assertEqual(TranscriptReinsertionService(self.history,self.queue)
            .reinsert_entry(entry.id).status.value,'queued')
        self.assertTrue(self.probed.wait(.5))
        self.assertEqual(len(self.backend.send_input_calls),1)
        self.held=False;self.drain()
        self.assertEqual(len(self.backend.send_input_calls),2)
        self.assertEqual(self.entry().id,entry.id)
        self.assertEqual(self.entry().text,entry.text)
        self.assertEqual([a.source for a in self.entry().attempts],['automatic','manual'])

    def test_failed_state_query_fails_closed(self):
        def query():raise OSError('Controlled key-state query fault')
        self.backend.get_pressed_modifiers=query
        self.publish();self.drain()
        self.assertEqual(self.backend.set_calls,[])
        self.assertEqual(self.backend.send_input_calls,[])
        self.assertEqual(self.entry().attempts[0].status,'failed')

    def test_pre_paste_sequence_query_failure_never_sends_input(self):
        self.backend.exception_on_seq_number=True
        self.publish();self.drain()
        self.assertEqual(self.backend.send_input_calls,[])
        self.assertEqual(self.entry().attempts[0].status,'failed')

    def test_partial_send_is_not_retried(self):
        self.hold();self.publish()
        self.assertTrue(self.probed.wait(.5))
        self.backend.send_input_result=2
        self.held=False;self.drain()
        self.assertEqual(len(self.backend.send_input_calls),1)
        self.assertEqual(self.entry().attempts[0].status,'failed')

    def test_native_state_uses_high_bit_and_both_windows_keys(self):
        states={0x10:1,0x11:0x8000,0x12:0,0x5b:-32768,0x5c:-32767}
        backend=CtypesWindowsInjectionBackend.__new__(CtypesWindowsInjectionBackend)
        backend.user32=SimpleNamespace(GetAsyncKeyState=lambda key:states[key])
        self.assertEqual(backend.get_pressed_modifiers(),(0x11,0x5b,0x5c))


if __name__=='__main__':
    unittest.main()
