"""Record authorized correction start; preserve historical R01 records."""
from pathlib import Path
import json
import subprocess

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT / 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
status_path = BLOCK / 'WORKFLOW_STATUS.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
assert head == 'ca3cd4009717d508a75ea236aec60881a39fab43'
assert subprocess.check_output(['git', 'rev-parse', 'origin/feat/client-v2'], cwd=ROOT, text=True).strip() == status['canonicalParent']
(EV / 'start-provenance.json').write_text(json.dumps(dict(head=head, tree=subprocess.check_output(['git', 'rev-parse', 'HEAD^{tree}'], cwd=ROOT, text=True).strip(), previousStatus=status, pullRequest=json.loads(subprocess.check_output(['gh', 'pr', 'view', '12', '--json', 'headRefOid,baseRefOid,comments,reviews'], cwd=ROOT, text=True, encoding='utf-8'))), ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
status.update(workflowPhase='CORRECTION_IN_PROGRESS', packageStatus='IN_PROGRESS', writeOwner='AP-CV2-100/R02-KORREKTUR', openFindingIds=['CI-01'], nextAction='CI-01 reproduzieren, Test korrigieren, Windows-Vollsuite und CI vor erneuter REVIEW_READY-Übergabe bestehen.')
status['lastRun'] = dict(id='R02-KORREKTUR', role='correction', report='30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md', evidence='30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/EVIDENCE/INDEX.md')
status['workAuthorization']['currentCorrectionSource'] = '30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/00_PROMPT_ORIGINAL.md'
status_path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
previous = EV.parents[1] / 'R01-UMSETZUNG/EVIDENCE/qualify_windows.py'
qualification = previous.read_text(encoding='utf-8').replace('R01 implementation qualification', 'R02 correction qualification').replace("'tests.test_v2_runtime_integration',", "'tests.test_event_stream','tests.test_v2_runtime_integration',")
(EV / 'qualify_windows.py').write_text(qualification, encoding='utf-8', newline='\n')
