"""Read-only snapshot of public server defaults; not a session-settings proof."""
import argparse,asyncio
from datetime import UTC,datetime
from pathlib import Path
from voice_stt_client.core.settings_service import SettingsHTTP,SettingsService
from tests.manual.v2.suite_plan import ROOT,TARGET
from tests.manual.v2.suite_session import save
from tests.manual.v2.verify_server_fix import read_info,check_identity


async def main(args):
    out=args.output.resolve()
    if not out.is_relative_to((ROOT/'build').resolve()):raise ValueError('Output must stay in project build')
    info=await asyncio.to_thread(read_info)
    if not check_identity(info,args.expected_server_commit):raise ValueError('Unexpected server build')
    response=await SettingsHTTP(TARGET,timeout=180).request('GET','/api/v2/settings/server')
    if response.status!=200:raise RuntimeError('Server settings GET failed')
    revision,requested,effective=SettingsService._parse_server(response.body)
    # Registry defaults only. No credentials or unrestricted server environment.
    keys=('wakeWord.sensitivity','wakeWord.minConsecutivePredictionFrames',
          'wakeWord.cooldownMs','wakeWord.detectorGain','wakeWord.inferenceBackend',
          'wakeWord.preRollMs','activation.followupTimeoutMs')
    result=dict(timeUtc=datetime.now(UTC).isoformat(),info=info,settingsRevision=revision,
                requested={k:requested[k] for k in keys},effective={k:effective[k] for k in keys},
                scope='Public server defaults at this instant; does not read another session or prove its effective snapshot',
                operations=['GET /api/v2/info','GET /api/v2/settings/server'])
    save(out,result);print('SERVER_DEFAULT_SNAPSHOT_SAVED')


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--expected-server-commit',required=True);p.add_argument('--output',type=Path,required=True)
    asyncio.run(main(p.parse_args()))
