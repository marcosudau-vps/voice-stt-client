"""UX02 red diagnostic: real final/history/queue, emulated held OS modifier.

No actual keyboard input or clipboard access. The live editor separately
recorded Ctrl+Shift+V with no insertion. This diagnostic must fail before fix.
"""
from pathlib import Path
import sys
import unittest
import threading

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0,str(ROOT))
from tests.test_text_injector_spacing import OutputSpacing


class HeldShift(unittest.TestCase):
    setUp=OutputSpacing.setUp
    final=OutputSpacing.final
    drain=OutputSpacing.drain

    def test_shift_from_finish_hotkey_must_not_suppress_paste(self):
        held={0x10}  # Actual live editor observed shiftHeld=True.
        self.backend.get_pressed_modifiers=lambda:tuple(held)
        delivered=[]
        native=self.backend.send_input_keyboard
        def send(events):
            for key,up in events:
                if up:held.discard(key)
                else:held.add(key)
                if key==0x56 and not up and 0x11 in held and 0x10 not in held:
                    delivered.append(self.backend.clipboard_data)
            return native(events)
        self.backend.send_input_keyboard=send
        release=threading.Timer(.1,lambda:held.discard(0x10))
        release.start()
        self.addCleanup(lambda:release.join(1))
        self.final('Bewusste Testprobe.')
        entry=self.history.get_persistent_entries()[0]
        self.assertEqual(entry.attempts[0].status,'command_sent')
        self.assertEqual(delivered,['Bewusste Testprobe. '],
            'Held Shift changes Ctrl+V to Ctrl+Shift+V; live Qt target inserted no text')


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HeldShift))
    raise SystemExit(not result.wasSuccessful())
