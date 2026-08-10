"""Muting, checked where it actually happens: on the way out of the queue.

No device is opened here. What is under test is the decision the processing
thread makes about each captured chunk, and that decision is the whole of the
mute -- everything else about capture is unchanged by it.
"""

from __future__ import annotations

import threading
import time
import unittest

from core.audio_capture import AudioCapture
from core.config import AudioConfig


class TestMicrophoneMute(unittest.TestCase):
    def setUp(self) -> None:
        self.capture = AudioCapture(AudioConfig())
        self.packets: list[bytes] = []
        self.capture.on_audio_packet = lambda pcm, *_: self.packets.append(pcm)

    def _drain(self, chunks: list[bytes], settle: float = 0.4) -> None:
        """Run the processing loop over a fixed set of chunks and stop it."""
        for chunk in chunks:
            self.capture._audio_queue.put(chunk)
        self.capture._running = True
        thread = threading.Thread(target=self.capture._process_loop, daemon=True)
        thread.start()
        time.sleep(settle)
        self.capture._running = False
        self.capture._audio_queue.put(None)
        thread.join(timeout=2.0)

    def test_audio_flows_while_unmuted(self) -> None:
        self._drain([b"\x01\x02" * 320, b"\x03\x04" * 320])
        self.assertEqual(len(self.packets), 2)

    def test_nothing_leaves_the_client_while_muted(self) -> None:
        """Dropped rather than sent as silence: silence is still a recording."""
        self.capture.set_muted(True)
        self._drain([b"\x01\x02" * 320, b"\x03\x04" * 320])
        self.assertEqual(self.packets, [])

    def test_unmuting_does_not_replay_what_piled_up(self) -> None:
        """The queue keeps draining while muted, so nothing is waiting behind it."""
        self.capture.set_muted(True)
        self._drain([b"\x01\x02" * 320] * 5)
        self.assertEqual(self.packets, [])

        self.capture.set_muted(False)
        self._drain([b"\x09\x09" * 320])
        self.assertEqual(len(self.packets), 1)

    def test_muting_leaves_the_stream_alone(self) -> None:
        """No device is closed, so unmuting cannot fail on a device somebody
        else took meanwhile."""
        self.capture.set_muted(True)
        self.assertTrue(self.capture.muted)
        self.assertIsNone(self.capture._stream)
        self.capture.set_muted(False)
        self.assertFalse(self.capture.muted)


if __name__ == "__main__":
    unittest.main()
