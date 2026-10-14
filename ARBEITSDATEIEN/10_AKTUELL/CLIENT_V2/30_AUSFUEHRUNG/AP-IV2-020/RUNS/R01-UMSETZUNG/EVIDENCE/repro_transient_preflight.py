"""Desired recovery regression, deliberately red until a product fix is authorized.

The separate real Docker-restart traces prove the actual user-visible fault.
These focused cases isolate classification without hardware/network timing.
Not part of a claimed green real gate; full logs retain the failures.
"""
import asyncio
from pathlib import Path
import sys
import unittest
from unittest.mock import AsyncMock

sys.path.insert(0,str(Path(__file__).resolve().parents[8]))
from voice_stt_client.core.settings_service import SettingsError,SettingsService
from voice_stt_client.core.v2_profile import V2Profile
from voice_stt_client.core.v2_transport import V2STTSession,V2TransportConfig


class TransientSettingsRecovery(unittest.IsolatedAsyncioTestCase):
    async def test_temporary_metadata_outage_is_retryable(self):
        service=SettingsService(V2STTSession(),V2Profile())
        service.load_metadata=AsyncMock(side_effect=SettingsError('http_unavailable'))
        with self.assertRaises(OSError):
            await service.prepare(service.session)

    async def test_preflight_timeout_retries_instead_of_latching_blocked(self):
        second=asyncio.Event()
        calls=[]
        async def prepare(session):
            calls.append(True)
            if len(calls)==1:raise TimeoutError()
            second.set()
            raise ValueError('permanent_test_stop_after_retry_observed')
        session=V2STTSession(V2TransportConfig(backoff_initial=.01,backoff_max=.02),prepare=prepare)
        task=asyncio.create_task(session.run())
        try:
            await asyncio.wait_for(second.wait(),.5)
            self.assertGreaterEqual(len(calls),2)
        finally:
            await session.stop()
            await asyncio.gather(task,return_exceptions=True)

    async def test_invalid_schema_remains_a_configuration_error(self):
        service=SettingsService(V2STTSession(),V2Profile())
        service.load_metadata=AsyncMock(side_effect=SettingsError('invalid_schema'))
        with self.assertRaises(SettingsError):
            await service.prepare(service.session)


if __name__=='__main__':unittest.main(verbosity=2)
