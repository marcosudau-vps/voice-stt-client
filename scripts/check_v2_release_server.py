"""Separate pinned production server process for installed/frozen client probes.

Recorder/ASR and scheduler are explicit model-free boundaries. Client probes
run in other processes, outside the checkout, with their actual HTTP/WS ports.
"""
import argparse
import asyncio
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile

SHA = 'ada13b011e1d3829f78e7f389e3b927795a2b3be'


def verify(root, repository):
    hashes = {}
    for module in tuple(sys.modules.values()):
        path = getattr(module, '__file__', None)
        if not path:
            continue
        path = Path(path).resolve()
        if path.suffix != '.py' or not path.is_relative_to(root):
            continue
        name = path.relative_to(root).as_posix()
        expected = subprocess.check_output(['git', '-C', str(repository), 'show', f'{SHA}:{name}'])
        actual = path.read_bytes()
        if actual != expected:
            raise AssertionError('Changed server source: ' + name)
        hashes[name] = hashlib.sha256(actual).hexdigest()
    if 'api_fastapi_server/server.py' not in hashes:
        raise AssertionError('Production server not imported')
    return hashes


async def run(args):
    sys.path.insert(0, str(args.server_root))
    import uvicorn
    from api_fastapi_server.server import create_app, ServerSettings
    from tests.unit.test_server_controlled_e2e import GateAwareRecorder
    from tests.unit.test_fastapi_server_multi_user import AutoScheduler
    verify(args.server_root, args.server_repository)
    os.environ['VOICESTT_SERVER_COMMIT'] = SHA
    hellos = []
    legacy_route = None
    with tempfile.TemporaryDirectory(prefix='cv2-110-production-server-') as data:
        settings = ServerSettings(data_root_path=data, model_warmup=False,
            request_logging_enabled=False, performance_logging_enabled=False,
            performance_log_mirror_enabled=False, transcription_logging_enabled=False,
            system_event_logging_enabled=False, event_store_enabled=False, log_live_enabled=False)
        app = create_app(settings, recorder_factory=GateAwareRecorder, scheduler_factory=AutoScheduler)

        async def observed(scope, receive, send):
            async def receive_observed():
                message = await receive()
                text = message.get('text')
                if scope['type'] == 'websocket' and text:
                    payload = json.loads(text)
                    if payload.get('type') == 'hello':
                        # Identity only; never persist access credentials or raw frames.
                        hellos.append({key: payload.get(key) for key in
                            ('clientVersion', 'clientCommit', 'supportedProtocolVersions')})
                return message
            await app(scope, receive_observed, send)

        tcp = socket.socket()
        tcp.bind(('127.0.0.1', 0))
        tcp.listen(16)
        server = uvicorn.Server(uvicorn.Config(observed, log_level='error', access_log=False))
        task = asyncio.create_task(server.serve(sockets=[tcp]))
        try:
            async with asyncio.timeout(20):
                while not server.started:
                    if task.done():
                        await task
                        raise RuntimeError('Server did not start')
                    await asyncio.sleep(.01)
            # A route probe is separate from running a historical V1 client.
            from websockets.asyncio.client import connect
            async with connect(f'ws://127.0.0.1:{tcp.getsockname()[1]}/ws/transcribe') as legacy:
                first = json.loads(await asyncio.wait_for(legacy.recv(), 10))
                second = json.loads(await asyncio.wait_for(legacy.recv(), 10))
                legacy_route = dict(result='PASS', probe='raw V1 route admission only',
                    firstType=first.get('type'), secondType=second.get('type'),
                    readyOk=second.get('ok'))
                if first.get('type') != 'hello' or second.get('type') != 'ready' or not second.get('ok'):
                    raise AssertionError('Pinned legacy route admission failed')
            args.ready.write_text(json.dumps({'url': f'ws://127.0.0.1:{tcp.getsockname()[1]}/ws/v2',
                'serverCommit': SHA, 'pid': os.getpid()}), encoding='utf8')
            # Bounded watchdog and user-controlled stop file; no orphan server.
            async with asyncio.timeout(900):
                while not args.stop.exists():
                    await asyncio.sleep(.1)
        finally:
            server.should_exit = True
            await asyncio.wait_for(task, 10)
            tcp.close()
            args.report.write_text(json.dumps(dict(serverCommit=SHA, hellos=hellos, legacyRoute=legacy_route,
                sourceHashes=verify(args.server_root, args.server_repository),
                boundaries=__doc__.strip()), indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for flag in ('server-root', 'server-repository', 'ready', 'stop', 'report'):
        parser.add_argument('--'+flag, required=True, type=lambda p: Path(p).resolve())
    asyncio.run(run(parser.parse_args()))
