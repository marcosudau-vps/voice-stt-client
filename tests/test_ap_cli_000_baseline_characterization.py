"""AP-CLI-000 – deterministic characterization for one baseline gap that
previously had no reproducible test, only the throwaway diagnostic script
``repro_stream.py`` referenced by
``ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/PLANUNG/ANALYSEN/LEGACY_AND_DEAD_CODE_MAP.md``
(section 17.2, Fund 7). That script no longer exists in the repository.

``core/stt_session.py``'s real ``set_streaming`` also writes
``state.streaming_requested`` (``core/stt_session.py:622-625``), in addition
to ``send_start``/``send_stop`` doing the same. ``FakeSTTSession``
(``tests/test_controller.py``) only updates ``self._streaming`` in its own
``set_streaming`` and never touches ``state.streaming_requested``.
``StreamCountingSession`` (``tests/test_trigger_lifecycle.py``) patches this
gap for ``send_start``/``send_stop`` but not for ``set_streaming``, which it
inherits unchanged. Because ``core/controller.py``'s
``_stop_dictation_locked`` (around line 1118) calls
``self.session.set_streaming(False)`` unconditionally - including on the
server-owns-activation branch whose comment claims the stream "keeps
running" - the existing ``ContinuousStreamingInvariant`` suite cannot show
whether the next activation actually resends `start`.

This test only records the current, reproducible behaviour against a double
that mirrors the real side effect. It changes no product code and does not
decide whether the flag or the comment is the intended contract; that
question belongs to the AP that replaces this local `streaming_requested`
bookkeeping with the v2 transport (see NACHVERFOLGUNG/TRACEABILITY.md,
CORE-05/CORE-06, owned by CLI-010).
"""

from __future__ import annotations

import unittest

from core.config import AppConfig
from core.controller import STTController
from tests.test_controller import FakeAudioCapture, FakeInjectionQueue
from tests.test_trigger_lifecycle import StreamCountingSession


class ProductionFaithfulStreamCountingSession(StreamCountingSession):
    """``StreamCountingSession`` with a ``set_streaming`` that mirrors the
    real ``STTSession.set_streaming`` (``core/stt_session.py:622-625``): it
    must also update ``state.streaming_requested``, not only the internal
    ``_streaming`` flag.
    """

    def set_streaming(self, streaming: bool) -> None:
        self._inner.set_streaming(streaming)
        self._inner.state.streaming_requested = streaming


class StreamRestartsAfterFinishWithAFaithfulDouble(unittest.IsolatedAsyncioTestCase):
    async def _controller(self, session):
        config = AppConfig()
        config.history.persistent.enabled = False
        controller = STTController(
            config,
            session=session,
            audio=FakeAudioCapture(),
            injection_queue=FakeInjectionQueue(),
        )
        controller.start_queue()
        self.addCleanup(self._shutdown, controller)
        return controller

    def _shutdown(self, controller):
        import asyncio

        asyncio.run(controller.shutdown())

    async def test_a_second_activation_resends_start_despite_the_finish_comment(self):
        session = ProductionFaithfulStreamCountingSession(accept=True)
        controller = await self._controller(session)

        first = await controller.start_dictation()
        self.assertTrue(first.success, first.message)
        self.assertEqual(session.stream_starts, 1)

        await controller.stop_dictation()
        self.assertIn(
            ("finish", "manual"),
            session.triggers,
            "stop_dictation must still finish the activation, not the stream",
        )

        second = await controller.start_dictation()
        self.assertTrue(second.success, second.message)
        self.assertEqual(
            session.stream_starts,
            2,
            "characterization: set_streaming(False) in "
            "_stop_dictation_locked (core/controller.py:1118) clears "
            "streaming_requested even on the server-owns-activation path, so "
            "_begin_stream_and_trigger (core/controller.py:815) resends "
            "`start` on the next activation instead of reusing the stream "
            "as the inline comment at core/controller.py:1123-1125 claims",
        )


if __name__ == "__main__":
    unittest.main()
