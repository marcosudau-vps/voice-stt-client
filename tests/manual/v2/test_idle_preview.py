import unittest
from tests.manual.v2.idle_preview import Preview


class DirectIdlePreview(unittest.TestCase):
    def make(self):
        now, controllers = [0.], []
        class Controller:
            def __init__(self, **kwargs):
                self.changed = kwargs['on_sink_changed']
                self.calls, self.closed = [], False
                controllers.append(self)
            def set_state(self, target, config): self.calls.append((target, config))
            def close(self): self.closed = True
        return Preview(Controller, clock=lambda: now[0]), now, controllers

    def test_no_hardware_before_start_and_full_visible_interval_after_availability(self):
        preview, now, controllers = self.make()
        self.assertFalse(controllers)
        preview.start()
        self.assertIsNone(preview.remaining())
        now[0] = 5.
        controllers[0].changed(True, '')
        self.assertEqual(preview.remaining(), 20.)
        now[0] = 24.
        self.assertEqual(preview.remaining(), 1.)
        now[0] = 25.
        self.assertEqual(preview.remaining(), 0.)
        self.assertEqual(controllers[0].calls[0], ('ready_state', dict(color='#FFFFFF', min_brightness=.30, brightness=1.)))
        preview.stop()
        self.assertTrue(controllers[0].closed)

    def test_missing_device_fails_and_repeat_closes_old_output(self):
        preview, now, controllers = self.make()
        preview.start()
        now[0] = 16.
        with self.assertRaises(TimeoutError): preview.remaining()
        preview.start()
        self.assertTrue(controllers[0].closed)
        self.assertIsNone(preview.remaining())
        preview.stop()
        self.assertTrue(controllers[1].closed)


if __name__ == '__main__':
    unittest.main()
