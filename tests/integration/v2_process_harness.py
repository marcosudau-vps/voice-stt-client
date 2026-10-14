"""Bounded separate-server lifecycle; no optional-success/skip path."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[2]


class ProcessServer:
    def __init__(self):
        self.folder = tempfile.TemporaryDirectory(prefix='iv2-010-process-')
        self.path = Path(self.folder.name)
        self.process = None

    def start(self):
        root = Path(os.environ['IV2_SERVER_ROOT']).resolve()
        repository = Path(os.environ['IV2_SERVER_REPOSITORY']).resolve()
        executable = root / 'venv/Scripts/python.exe'
        self.log = (self.path/'server.txt').open('w', encoding='utf8')
        env = dict(os.environ, PYTHONUTF8='1', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
        self.command = [str(executable), str(ROOT/'tests/integration/v2_process_server.py'),
            '--server-root', str(root), '--server-repository', str(repository),
            '--ready', str(self.path/'ready.json'), '--stop', str(self.path/'stop'),
            '--report', str(self.path/'server.json')]
        self.process = subprocess.Popen(self.command, cwd=root, env=env,
            stdout=self.log, stderr=subprocess.STDOUT)
        end = time.monotonic()+30
        while not (self.path/'ready.json').exists():
            if self.process.poll() is not None or time.monotonic() > end:
                self.close()
                raise AssertionError((self.path/'server.txt').read_text(encoding='utf8'))
            time.sleep(.02)
        self.identity = json.loads((self.path/'ready.json').read_text())
        assert self.identity['pid'] != os.getpid()
        self.url = self.identity['url']
        self.http = self.url.replace('ws://', 'http://').removesuffix('/ws/v2')
        return self

    async def control(self, action, session_id, **fields):
        def request():
            payload = json.dumps(dict(action=action, sessionId=session_id, **fields)).encode()
            req = urllib.request.Request(self.http+'/_qualification/control', data=payload,
                                         headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.load(response)
        return await asyncio.to_thread(request)

    def close(self):
        if self.process:
            (self.path/'stop').touch()
            try:
                self.process.wait(timeout=15)
            except subprocess.TimeoutExpired:
                self.process.kill(); self.process.wait(timeout=5)
                raise AssertionError('server cleanup timeout')
            finally:
                self.log.close()
        return self.process.returncode if self.process else None

    def report(self):
        return json.loads((self.path/'server.json').read_text(encoding='utf8'))

    def cleanup(self):
        self.folder.cleanup()
