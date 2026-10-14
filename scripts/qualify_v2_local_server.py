"""Build/start only the isolated, local AP-IV2-020 model server.

The base image supplies dependencies; all server source/assets come from the
exact Git archive. The client venv runs this orchestrator. No VPS, release,
production container, production config or existing credential is changed.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys
import time

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.qualify_v2_real import LOCAL, SERVER, get_json, save
from scripts.export_v2_server import export

NAME = 'voicestt-qualification-iv2-020'
IMAGE = 'voicestt-qualification:iv2-020-ada13b0-free'
VOLUME = 'voicestt-qualification-iv2-020-free-data'


def docker(*args, **kw):
    return subprocess.check_output(['docker', *args], text=True, **kw).strip()


def prepare(args):
    LOCAL.mkdir(parents=True, exist_ok=True)
    context = LOCAL/'server-image'
    source = context/'source-exact'
    config_dir = LOCAL/'server-config'
    config_dir.mkdir(exist_ok=True)
    if not source.exists():
        export(args.server_repository, source)
    # Verify every archived blob, including models. No dirty worktree source.
    entries = subprocess.check_output(['git','-C',str(args.server_repository),
                                      'ls-tree','-rz',SERVER]).split(b'\0')
    expected = {}
    for entry in entries:
        if not entry:
            continue
        meta, name = entry.split(b'\t',1)
        _mode, kind, oid = meta.split()
        if kind != b'blob':
            continue
        name = name.decode('utf8')
        data = (source/name).read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual != oid.decode():
            raise RuntimeError('Changed server archive: '+name)
        expected[name] = hashlib.sha256(data).hexdigest()
    base_id = docker('image','inspect',args.base_image,'--format','{{.Id}}')
    if args.build:
        dockerfile = context/'Dockerfile.qualification'
        dockerfile.write_text(f'''FROM {args.base_image}
COPY source-exact/ /qualified/
WORKDIR /qualified
ENV PYTHONPATH=/qualified VOICESTT_SERVER_COMMIT={SERVER} VOICESTT_WAKEWORD_ASSET_ROOT=/qualified/VoiceSTT/assets/wakeword_models VOICESTT_KROKO_MODEL_ROOT=/models/kroko OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2
ENTRYPOINT ["python"]
CMD ["-m", "VoiceSTT_server.server", "--config", "/server-qualification.yaml"]
''', encoding='utf8')
        with (LOCAL/'server-build-reproducible.txt').open('wb') as handle:
            subprocess.run(['docker','build','--pull=false','-f',str(dockerfile),'-t',IMAGE,str(context)],
                env=dict(os.environ, DOCKER_BUILDKIT='0'), stdout=handle,
                stderr=subprocess.STDOUT, check=True, timeout=600)
    image_id = docker('image','inspect',IMAGE,'--format','{{.Id}}')
    inspected = subprocess.run(['docker','inspect',NAME], capture_output=True,text=True)
    if inspected.returncode == 0:
        current = json.loads(inspected.stdout)[0]
        if current['Config']['Labels'].get('voice-stt.qualification') != 'AP-IV2-020':
            raise RuntimeError('Container name belongs to another workload')
        if current['Image'] != image_id:
            raise RuntimeError('Existing qualification container uses another image; preserve it for diagnosis')
        if not current['State']['Running']:
            docker('start',NAME)
    else:
        config = yaml.safe_load((source/'config.yaml').read_text(encoding='utf8'))['settings']
        config.update(transcription_engine='kroko_onnx',
            model='Kroko-DE-Community-64-L-Streaming-001.data',
            realtime_transcription_engine='kroko_onnx',
            realtime_model='Kroko-DE-Community-64-L-Streaming-001.data',
            use_main_model_for_realtime=True,model_warmup=True,
            model_idle_unload_enabled=False,model_memory_policy_enabled=False,
            data_root_path='/data',request_log_transcripts=False,transcript_log_mode='none',
            request_log_stdout=False,performance_log_stdout=False,save_audio_files=False)
        config['stt_engine_settings']={'kroko_onnx':dict(enabled=True,runtime_variant='free',
            auto_download_enabled=False,custom_paths=['/models/kroko'])}
        for key in ('transcription_engine_options','realtime_transcription_engine_options'):
            config[key]={'num_threads':2}
        path=config_dir/'server.yaml'
        path.write_text(yaml.safe_dump({'version':1,'settings':config},sort_keys=False),encoding='utf8')
        guard=config_dir/'guard.env'
        if not guard.exists():
            guard.write_text('VOICESTT_ADMIN_API_KEY='+secrets.token_urlsafe(32)+'\n',encoding='utf8')
        docker('volume','create','--label','voice-stt.qualification=AP-IV2-020',VOLUME)
        docker('create','--user','0','--name',NAME,'--label','voice-stt.qualification=AP-IV2-020',
            '--publish','127.0.0.1:18020:8010','--mount',f'type=volume,source={VOLUME},target=/data',
            '--mount',f'type=bind,source={args.model_root.resolve().as_posix()},target=/models/kroko,readonly',
            '--env-file',str(guard),IMAGE)
        docker('cp','-L',str(path),NAME+':/server-qualification.yaml')
        docker('start',NAME)
    deadline=time.monotonic()+180
    while True:
        try:
            health=get_json('http://127.0.0.1:18020/health')
            if health.get('ready'):
                break
        except OSError:
            pass
        if time.monotonic()>deadline:
            raise TimeoutError('Local model server is not ready; inspect redacted startup errors')
        time.sleep(.5)
    # Hash actual image contents rather than trusting the advertised SHA alone.
    verify='''import json,hashlib,sys,pathlib
expected=json.load(sys.stdin)
bad=[n for n,h in expected.items() if hashlib.sha256((pathlib.Path('/qualified')/n).read_bytes()).hexdigest()!=h]
print(json.dumps({'verifiedBlobs':len(expected),'mismatches':bad}))
raise SystemExit(bool(bad))'''
    checked=json.loads(docker('exec','-i',NAME,'python','-c',verify,input=json.dumps(expected)))
    schema=get_json('http://127.0.0.1:18020/api/v2/settings/schema')
    if schema.get('serverCommit') != SERVER:
        raise RuntimeError('Wrong local server identity')
    result=dict(serverCommit=SERVER,baseImageId=base_id,imageId=image_id,
        containerId=docker('inspect',NAME,'--format','{{.Id}}'),
        sourceVerification=checked,modelRootReadOnly=True,dataVolume=VOLUME,
        origin='http://127.0.0.1:18020',health=health,sourceSha256=expected,
        configurationSha256=hashlib.sha256((config_dir/'server.yaml').read_bytes()).hexdigest(),
        configuration=yaml.safe_load((config_dir/'server.yaml').read_text()),
        boundaries='Local source-qualified model server; native dependencies from base image; container UID0; isolated synthetic admin guard. No release or VPS promotion.')
    save(args.evidence/'local-server-build.json', result)
    print(json.dumps(dict(result='PASS',imageId=image_id,verifiedBlobs=checked['verifiedBlobs'])))


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--server-repository',type=Path,required=True)
    parser.add_argument('--model-root',type=Path,required=True)
    parser.add_argument('--base-image',default='voice-stt-server:2.0.0')
    parser.add_argument('--build',action='store_true')
    parser.add_argument('--evidence',type=Path,required=True)
    prepare(parser.parse_args())
