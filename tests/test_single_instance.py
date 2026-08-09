"""Tests for the Win32 mutex single-instance lifecycle."""

from __future__ import annotations

import unittest

from ui.single_instance import (
    InstanceAcquireStatus,
    SingleInstanceGuard,
)


class FakeMutexBackend:
    def __init__(self, *, already_exists=False, fail=False):
        self.already_exists = already_exists
        self.fail = fail
        self.created = []
        self.closed = []

    def create(self, name):
        self.created.append(name)
        if self.fail:
            raise OSError("simulated mutex failure")
        return 101, self.already_exists

    def close(self, handle):
        self.closed.append(handle)


class TestSingleInstanceGuard(unittest.TestCase):
    def test_first_instance_acquires_and_releases_exactly_once(self):
        backend = FakeMutexBackend()
        guard = SingleInstanceGuard("Local\\test", backend)

        self.assertEqual(
            guard.acquire().status,
            InstanceAcquireStatus.ACQUIRED,
        )
        self.assertTrue(guard.is_acquired)
        self.assertEqual(
            guard.acquire().status,
            InstanceAcquireStatus.ACQUIRED,
        )
        guard.release()
        guard.release()

        self.assertEqual(backend.created, ["Local\\test"])
        self.assertEqual(backend.closed, [101])

    def test_second_instance_closes_non_owned_handle_and_is_rejected(self):
        backend = FakeMutexBackend(already_exists=True)
        guard = SingleInstanceGuard("Local\\test", backend)

        result = guard.acquire()

        self.assertEqual(result.status, InstanceAcquireStatus.ALREADY_RUNNING)
        self.assertFalse(guard.is_acquired)
        self.assertEqual(backend.closed, [101])

    def test_backend_failure_is_controlled(self):
        backend = FakeMutexBackend(fail=True)
        result = SingleInstanceGuard("Local\\test", backend).acquire()
        self.assertEqual(result.status, InstanceAcquireStatus.ERROR)
        self.assertIn("simulated mutex failure", result.error)


if __name__ == "__main__":
    unittest.main()
