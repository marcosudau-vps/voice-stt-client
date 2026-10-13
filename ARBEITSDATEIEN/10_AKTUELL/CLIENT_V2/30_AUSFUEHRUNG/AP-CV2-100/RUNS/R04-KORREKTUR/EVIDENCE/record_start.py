"""Acquire the authorized R04 correction after preserving the R03 review head."""
from pathlib import Path
import json
import subprocess

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
status_path = BLOCK/'WORKFLOW_STATUS.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
assert git('rev-parse','HEAD') == 'c5a510f193908d7493f979365e45be6317cd9dab'
assert git('rev-parse','origin/feat/client-v2') == status['canonicalParent']
assert not git('diff','--name-only', status['reviewedCommit'],'HEAD','--','voice_stt_client','tests','scripts','.github','config.yaml','requirements.txt','requirements-dev.txt','pyproject.toml')
pr = json.loads(subprocess.check_output(['gh','pr','view','12','--json','headRefOid,baseRefOid,comments,reviews'], cwd=ROOT, text=True, encoding='utf-8'))
assert pr['headRefOid'] == git('rev-parse','HEAD') and pr['baseRefOid'] == status['canonicalParent']
(EV/'start-provenance.json').write_text(json.dumps(dict(head=git('rev-parse','HEAD'),tree=git('rev-parse','HEAD^{tree}'),reviewDocsOnly=True,previousStatus=status,pullRequest=pr),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
status.update(workflowPhase='CORRECTION_IN_PROGRESS',packageStatus='IN_PROGRESS',writeOwner='AP-CV2-100/R04-KORREKTUR',nextAction='F01 mit tatsächlichem V2-Desktop/Bridge/Core reproduzieren und korrigieren; neue Windows-Vollqualifikation und finale CI vor REVIEW_READY.')
status['lastRun'] = dict(id='R04-KORREKTUR',role='correction',report='30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md',evidence='30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md')
status['workAuthorization']['currentCorrectionSource'] = '30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/00_PROMPT_ORIGINAL.md'
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
previous = EV.parents[1]/'R02-KORREKTUR/EVIDENCE/qualify_windows.py'
(EV/'qualify_windows.py').write_text(previous.read_text(encoding='utf-8').replace('R02 correction qualification','R04 correction qualification'),encoding='utf-8',newline='\n')
