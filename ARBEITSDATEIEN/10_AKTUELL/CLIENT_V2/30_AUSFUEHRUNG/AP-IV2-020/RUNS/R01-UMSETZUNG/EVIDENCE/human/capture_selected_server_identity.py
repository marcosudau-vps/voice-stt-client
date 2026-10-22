"""Read the human-selected VPS evidence and current V2 identities; no mutations.

Never read .env, container environment values, private backups or transcription
logs. SSH uses the existing non-root alias and existing verified host key.
Only the explicit output inside this client repository is written.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = next(p for p in Path(__file__).resolve().parents if (p/'voice_stt_client').is_dir())

REMOTE = r'''
from datetime import datetime, timezone
import getpass
import hashlib
import json
import io
from pathlib import Path
import subprocess
import sys
import tarfile

if getpass.getuser() != 'marco':
    raise RuntimeError('Only the documented non-root marco account is allowed')
pin = 'ada13b011e1d3829f78e7f389e3b927795a2b3be'
base = Path('/home/marco/.codex_projekte/voice-stt-server_umstrukturierung')
result = {'capturedAtUtc': datetime.now(timezone.utc).isoformat(), 'requiredServerCommit': pin,
          'remoteProject': str(base), 'readOnly': True, 'files': [], 'instances': []}
for name in ['evidenz/v2-pro-build-manifest.json', 'evidenz/v2-normal-build-manifest.json',
             'evidenz/quellstaende-final.json']:
    raw = (base/name).read_bytes()
    result['files'].append({'path': str(base/name), 'sha256': hashlib.sha256(raw).hexdigest(),
                            'data': json.loads(raw)})
report = (base/'ABSCHLUSSBERICHT.md').read_bytes()
result['completionReportSha256'] = hashlib.sha256(report).hexdigest()
for name, variant, host, port in [
        ('voice-stt-server-pro-v2', 'pro', 'pro.v2.voice-stt-server.marcosudau.com', '8021'),
        ('voice-stt-server-v2', 'free', 'v2.voice-stt-server.marcosudau.com', '8020')]:
    print('Read-only identity: '+name, file=sys.stderr, flush=True)
    manifest_name = 'v2-pro-build-manifest.json' if variant == 'pro' else 'v2-normal-build-manifest.json'
    manifest = json.loads((base/'evidenz'/manifest_name).read_text())
    inspected = json.loads(subprocess.check_output(['docker', 'inspect', name]))[0]
    image = json.loads(subprocess.check_output(['docker', 'image', 'inspect', inspected['Image']]))[0]
    source_name = 'voice-stt-server-pro' if variant == 'pro' else 'voice-stt-server'
    source = Path('/home/marco/selfhost/apps/services/voice-stt-server/version2-development')/source_name
    git = ['git', '--no-optional-locks', '-c', 'core.fsmonitor=false', '-C', str(source)]
    head = subprocess.check_output(git+['rev-parse', 'HEAD'], text=True).strip()
    dirty = subprocess.check_output(git+['status', '--porcelain', '--untracked-files=no'], text=True).splitlines()
    wheel = Path(manifest['voicesttWheel']['path'])
    wheel_hash = hashlib.sha256(wheel.read_bytes()).hexdigest() if wheel.is_file() else None
    mounts = [m['Destination'] for m in inspected.get('Mounts', [])]
    print('Read-only four-file content comparison: '+name, file=sys.stderr, flush=True)
    content_checks = []
    for relative in ['VoiceSTT/core/recording.py', 'VoiceSTT/core/wake_detection.py',
                     'VoiceSTT/core/openwakeword_engine.py', 'api_fastapi_server/server.py']:
        raw = subprocess.check_output(['docker', 'cp', name+':/opt/venv/lib/python3.12/site-packages/'+relative, '-'], timeout=30)
        with tarfile.open(fileobj=io.BytesIO(raw), mode='r:') as archive:
            files = [member for member in archive.getmembers() if member.isfile()]
            if len(files) != 1:
                raise RuntimeError('Expected exactly one source file')
            installed = archive.extractfile(files[0]).read()
        expected = (source/relative).read_bytes()
        content_checks.append({'path': relative, 'installedSha256': hashlib.sha256(installed).hexdigest(),
                               'sourceSha256': hashlib.sha256(expected).hexdigest(), 'match': installed == expected})
    expected_image = manifest['variants'][variant]['imageId']
    bound_ports = inspected['HostConfig'].get('PortBindings') or {}
    expected_port = any(row.get('HostIp') == '127.0.0.1' and row.get('HostPort') == port
                        for row in bound_ports.get('8010/tcp', []))
    labels = image['Config'].get('Labels') or {}
    item = {'instance': name, 'hostFromDeploymentEvidence': host, 'containerId': inspected['Id'],
            'status': inspected['State']['Status'], 'imageId': inspected['Image'],
            'manifestImageId': expected_image, 'imageMatchesManifest': inspected['Image'] == expected_image,
            'manifestCommit': manifest['gitCommit'], 'manifestGitDirty': manifest['gitDirty'],
            'sourceHead': head, 'trackedSourceChanges': dirty,
            'imageRevision': labels.get('org.opencontainers.image.revision'),
            'portBindings': bound_ports, 'expectedLoopbackPortBound': expected_port,
            'mountTargets': mounts, 'runtimeSourceContentChecks': content_checks,
            'fullWritableLayerDiff': 'NOT_PROVEN: prior optional Docker diff timed out after45s; no full integrity claim',
            'wheelPath': str(wheel), 'wheelExpectedSha256': manifest['voicesttWheel']['sha256'],
            'wheelActualSha256': wheel_hash,
            'wireCommit': 'unknown; captured separately in HTTP and diagnostic hello',
            'modelDifference': 'Pro16 vs Community64; previous local evidence is not transferred'}
    code_mounts = [p for p in mounts if p.startswith(('/opt/venv', '/app', '/opt/voicestt'))]
    item['codeMountOverrides'] = code_mounts
    item['pinBinding'] = ('CONFIRMED_DEPLOYMENT_MANIFEST_AND_CURRENT_IMAGE_SOURCE'
        if head == pin and manifest['gitCommit'] == pin and manifest['gitDirty'] is False
        and labels.get('org.opencontainers.image.revision') == pin
        and not dirty and inspected['Image'] == expected_image and expected_port
        and not code_mounts and all(row['match'] for row in content_checks) else 'NOT_PROVEN')
    result['instances'].append(item)
print(json.dumps(result))
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT.resolve()):
        parser.error('Output must be inside this repository')
    command = ['ssh', '-o', 'BatchMode=yes', '-o', 'StrictHostKeyChecking=yes',
               '-o', 'IdentitiesOnly=yes', '-o', 'ConnectTimeout=15', 'vps_codex',
               'python3 -B -']
    raw = subprocess.check_output(command, input=REMOTE.encode('utf-8'), timeout=180)
    result = json.loads(raw)
    result['captureHelperSha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['remoteReadProgramSha256'] = hashlib.sha256(REMOTE.encode()).hexdigest()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps([{'instance': r['instance'], 'pinBinding': r['pinBinding'],
                       'imageId': r['imageId'], 'sourceHead': r['sourceHead'],
                       'wheelHashMatches': r['wheelActualSha256'] == r['wheelExpectedSha256']}
                      for r in result['instances']]))


if __name__ == '__main__':
    main()
