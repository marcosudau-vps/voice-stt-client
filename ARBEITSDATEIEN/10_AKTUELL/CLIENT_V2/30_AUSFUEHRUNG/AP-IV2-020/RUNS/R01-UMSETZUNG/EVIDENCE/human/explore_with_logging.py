"""Free isolated desktop exploration with the real production log service.

The existing qualification runner retains its own mutex/profile, passive
metrics and local stop command. This adapter supplies the manager/ingress that
the regular app.main normally owns. Constructor wrappers supply dependencies;
the product classes retain their behavior methods.
"""
import argparse
from pathlib import Path
import os
import sys
from types import SimpleNamespace
from unittest.mock import patch

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())
sys.path.insert(0, str(ROOT))


def managed_types(runtime, bridge, desktop, manager):
    class Runtime(runtime):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault('observability', manager.ingress)
            super().__init__(*args, **kwargs)

    class Bridge(bridge):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault('observability', manager.ingress)
            super().__init__(*args, **kwargs)

    class Desktop(desktop):
        def __init__(self, *args, **kwargs):
            kwargs.setdefault('observability', manager.ingress)
            kwargs.setdefault('observability_manager', manager)
            super().__init__(*args, **kwargs)

    return Runtime, Bridge, Desktop


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('manual', 'wake', 'both'), default='both')
    parser.add_argument('--self-check', action='store_true')
    args = parser.parse_args()
    if args.self_check:
        class Capture:
            def __init__(self, *args, **kwargs):
                self.args, self.kwargs = args, kwargs
        manager = SimpleNamespace(ingress=object())
        types = managed_types(Capture, Capture, Capture, manager)
        for cls in types:
            value = cls('config', backend='owned-test-backend')
            assert value.args == ('config',)
            assert value.kwargs['observability'] is manager.ingress
            assert value.kwargs['backend'] == 'owned-test-backend'
            explicit = object()
            assert cls(observability=explicit).kwargs['observability'] is explicit
        assert types[2]().kwargs['observability_manager'] is manager
        print('PASS: shared real-manager ingress reaches Runtime, Bridge and Desktop; manager reaches log UI; explicit options preserved. No GUI/device/server/store was started.')
        return 0
    local = Path(os.environ['LOCALAPPDATA'])/'VoiceSTT-Qualification/AP-IV2-020'
    os.environ['VOICESTT_CLIENT_HOME'] = str(local/'client')
    from voice_stt_client.core.config import AppConfig
    from voice_stt_client.core.logging_setup import setup_logging
    from voice_stt_client.core.observability.manager import ObservabilityManager
    from voice_stt_client.core import v2_runtime
    from voice_stt_client.ui import v2_core_bridge, v2_application
    from tests.manual.v2 import observed_session
    config = AppConfig.load(local/('client-'+args.mode+'.yaml'))
    if config.server.url != 'ws://127.0.0.1:18020/ws/v2':
        raise ValueError('Only the pinned isolated local qualification server is allowed')
    if not Path(config.logging.log_dir).resolve().is_relative_to(local.resolve()):
        raise ValueError('Qualification log store must remain inside its isolated home')
    for name in (config.history.persistent.db_path, config.event_stream.cursor_path):
        if not name or not Path(name).resolve().is_relative_to(local.resolve()):
            raise ValueError('Qualification history and cursor must remain isolated')
    if config.logging.observability.store_transcription_content or config.logging.observability.store_raw_payload:
        raise ValueError('Free exploration requires content/payload logging disabled')
    manager = ObservabilityManager(config.logging.observability, log_dir=config.logging.log_dir)
    runtime, bridge, desktop = managed_types(v2_runtime.V2Runtime, v2_core_bridge.V2CoreBridge,
                                            v2_application.V2DesktopApplication, manager)
    previous_argv = sys.argv
    try:
        manager.start()
        setup_logging(config.logging, observability=manager.ingress)
        with patch.object(v2_runtime, 'V2Runtime', runtime), \
             patch.object(v2_core_bridge, 'V2CoreBridge', bridge), \
             patch.object(v2_application, 'V2DesktopApplication', desktop):
            sys.argv = [sys.argv[0], '--mode', args.mode]
            observed_session.main()
    finally:
        sys.argv = previous_argv
        manager.stop(2.0)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
