"""Reproducible AP110 Windows qualification, project venv only.

Run from the repository root. No publishing, user configuration, physical
audio/USB or global keys. Native Qt probes use temporary isolated data.
"""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import subprocess
import sys
import tarfile
import tempfile
import time

ROOT = Path.cwd().resolve()
EVIDENCE = Path(__file__).resolve().parent
SERVER_ROOT = Path(os.environ.get('AP110_SERVER_ROOT', r'C:\Users\marco\AppData\Local\Temp\voice-stt-ap-cv2-020-ada13b0'))
SERVER_REPO = Path(os.environ.get('AP110_SERVER_REPOSITORY', r'P:\GithubRepos\marcosudau-vps\voice-stt-server\main'))


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args], text=True).strip()


def product_blobs():
    return git('ls-files', '-s', '--', 'voice_stt_client', 'tests', 'scripts',
        '.github', 'pyproject.toml', 'setup.py', 'MANIFEST.in', 'VERSION',
        'requirements.txt', 'requirements-dev.txt', 'voice-stt-client.spec', 'README.md')


def run():
    env = os.environ.copy()
    env.update(PYTHONUTF8='1', QT_QPA_PLATFORM='offscreen', OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
    py = str(ROOT/'venv/Scripts/python.exe')
    head, tree = git('rev-parse', 'HEAD'), git('rev-parse', 'HEAD^{tree}')
    blobs = product_blobs()
    checks = []
    report = dict(candidateCommit=head, candidateTree=tree,
        canonicalParent='62ca35a01fb88b37e16b7003e26c2f9110c131f3',
        serverCommit='ada13b011e1d3829f78e7f389e3b927795a2b3be',
        runtime=dict(executable=sys.executable, python=sys.version, windows=str(sys.getwindowsversion())),
        commands=checks, result='IN_PROGRESS')

    def command(name, args, *, cwd=ROOT, custom_env=None):
        path = EVIDENCE/(name+'.txt')
        started = time.monotonic()
        with path.open('w', encoding='utf8') as log:
            log.write(json.dumps(dict(command=args, cwd=str(cwd), candidateCommit=head))+'\n')
            log.flush()
            done = subprocess.run(args, cwd=cwd, env=custom_env or env, stdout=log, stderr=subprocess.STDOUT)
        text = path.read_text(encoding='utf8')
        count = re.search(r'Ran (\d+) tests', text)
        check = dict(name=name, command=args, cwd=str(cwd), exitCode=done.returncode,
            durationSeconds=round(time.monotonic()-started, 3), log=path.name,
            sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
            testCount=int(count.group(1)) if count else None)
        checks.append(check)
        print(name, done.returncode, flush=True)
        if done.returncode:
            raise RuntimeError('Qualification failed: '+name)

    try:
        command('windows-full', [py, '-m', 'unittest', 'discover', '-s', 'tests', '-p', 'test_*.py'])
        command('windows-targeted', [py, '-m', 'unittest', 'tests.test_v2_release',
            'tests.test_v2_runtime_integration', 'tests.test_v2_feedback', 'tests.test_obs050_settings',
            'tests.test_obs050_ui', 'tests.test_event_stream', 'tests.test_build_script', '-v'])
        command('compileall', [py, '-m', 'compileall', '-q', 'voice_stt_client', 'scripts', 'tests'])
        command('server-runtime', [py, 'scripts/check_v2_server_runtime.py', '--server-root', str(SERVER_ROOT),
            '--server-repository', str(SERVER_REPO)])
        command('pyinstaller-clean', [py, 'scripts/build.py', '--clean'])
        command('python-distributions', [py, '-m', 'build', '--sdist', '--wheel'])
        wheel = next((ROOT/'dist').glob('*.whl'))
        sdist = next((ROOT/'dist').glob('*.tar.gz'))
        exe = ROOT/'dist/voice-stt-client.exe'
        command('twine-check', [py, '-m', 'twine', 'check', str(wheel), str(sdist)])
        command('release-guard', [py, 'scripts/client_release_guard.py', 'candidate', '--dir', 'dist', '--expected-commit', head])
        report['artifacts'] = {p.name:dict(path=str(p), size=p.stat().st_size,
            sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in (wheel, sdist, exe)}
        from PyInstaller.archive.readers import CArchiveReader
        archive = CArchiveReader(str(exe))
        modules = sorted(archive.open_embedded_archive('PYZ.pyz').toc)
        forbidden = [m for m in modules if m.startswith(('core.', 'ui.', 'tests.', 'fastapi', 'starlette'))
            or 'simulat' in m.lower()]
        if forbidden:
            raise AssertionError('Frozen imports contain forbidden modules: '+str(forbidden))
        report['frozenModules'] = dict(count=len(modules), forbidden=forbidden,
            containsV2Runtime='voice_stt_client.core.v2_runtime' in modules)
        if not report['frozenModules']['containsV2Runtime']:
            raise AssertionError('Frozen runtime missing')

        with tempfile.TemporaryDirectory(prefix='cv2-110-installed-') as temp:
            outside = Path(temp)
            target = outside/'wheel-installed'
            command('wheel-install', [py, '-m', 'pip', 'install', '--no-deps', '--target', str(target), str(wheel)], cwd=outside)
            source = outside/'sdist-source'
            source.mkdir()
            with tarfile.open(sdist) as archive:
                archive.extractall(source, filter='data')
            release_tree = next(source.iterdir())
            command('sdist-wheel-rebuild', [py, '-m', 'build', '--wheel', '--outdir', str(outside/'rebuilt')], cwd=release_tree)
            rebuilt = next((outside/'rebuilt').glob('*.whl'))
            rebuilt_target = outside/'rebuilt-installed'
            command('rebuilt-wheel-install', [py, '-m', 'pip', 'install', '--no-deps', '--target', str(rebuilt_target), str(rebuilt)], cwd=outside)
            ready, stop = outside/'server-ready.json', outside/'server-stop'
            with (EVIDENCE/'release-server.txt').open('w', encoding='utf8') as log:
                server_args = [py, str(ROOT/'scripts/check_v2_release_server.py'), '--server-root', str(SERVER_ROOT),
                    '--server-repository', str(SERVER_REPO), '--ready', str(ready), '--stop', str(stop),
                    '--report', str(EVIDENCE/'release-server.json')]
                log.write(json.dumps(dict(command=server_args, candidateCommit=head))+'\n')
                log.flush()
                server = subprocess.Popen(server_args, cwd=outside, env=env, stdout=log, stderr=subprocess.STDOUT,
                    creationflags=subprocess.CREATE_NO_WINDOW)
                try:
                    deadline = time.monotonic()+30
                    while not ready.exists():
                        if server.poll() is not None or time.monotonic()>deadline:
                            raise RuntimeError('Separate server failed readiness')
                        time.sleep(.05)
                    url = json.loads(ready.read_text(encoding='utf8'))['url']
                    for name, root, launcher in (
                        ('source', ROOT, [py, '-m', 'voice_stt_client']),
                        ('wheel', target, [py, '-m', 'voice_stt_client']),
                        ('rebuilt-wheel', rebuilt_target, [py, '-m', 'voice_stt_client']),
                        ('frozen', None, [str(exe)])):
                        probe_env = dict(env, QT_QPA_PLATFORM='windows')
                        probe_env['PYTHONPATH'] = str(root) if root else ''
                        command(name+'-version', launcher+['--version'], cwd=outside, custom_env=probe_env)
                        result_file = EVIDENCE/(name+'-probe.json')
                        command(name+'-native-probe', launcher+['--verify-gui-runtime', '--verification-output', str(result_file),
                            '--verification-server', url], cwd=outside, custom_env=probe_env)
                        value = json.loads(result_file.read_text(encoding='utf8'))
                        if (value['hello']['clientCommit'] != head or value['hello']['clientVersion'] != value['version']
                                or value['network']['serverCommit'] != report['serverCommit']
                                or value['desktop']['serverCommit'] != report['serverCommit']
                                or value['gui']['platform'] != 'windows' or not value['desktop']['coreStopped']):
                            raise AssertionError('Build identity/native desktop checkpoint failed: '+name)
                        if name != 'source' and Path(value['packageRoot']).is_relative_to(ROOT):
                            raise AssertionError('Installed product imported source checkout')
                finally:
                    stop.write_text('stop', encoding='utf8')
                    try:
                        server.wait(20)
                    except subprocess.TimeoutExpired:
                        server.terminate()
                        server.wait(10)
                        raise
                if server.returncode:
                    raise RuntimeError('Server cleanup failed')
            server_report = json.loads((EVIDENCE/'release-server.json').read_text(encoding='utf8'))
            if len(server_report['hellos']) != 8 or any(h['clientCommit'] != head for h in server_report['hellos']):
                raise AssertionError('Server did not observe all real client Hello identities')
            report['receivedHelloCount'] = len(server_report['hellos'])
        if product_blobs() != blobs or git('diff', '--name-only', 'HEAD', '--', 'voice_stt_client', 'tests', 'scripts',
                '.github', 'setup.py', 'MANIFEST.in', 'pyproject.toml', 'README.md'):
            raise AssertionError('Product/test changes during qualification')
        command('diff-check', ['git', '-c', 'core.safecrlf=false', 'diff', '--check'])
        report['result'] = 'PASS'
    finally:
        (EVIDENCE/'candidate-blobs.txt').write_text(blobs+'\n', encoding='utf8')
        (EVIDENCE/'windows-validation.json').write_text(json.dumps(report, indent=2)+'\n', encoding='utf8')


if __name__ == '__main__':
    run()
