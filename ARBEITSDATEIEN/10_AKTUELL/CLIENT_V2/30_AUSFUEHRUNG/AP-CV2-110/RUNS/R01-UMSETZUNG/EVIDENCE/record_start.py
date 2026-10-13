"""Record actual predecessor provenance and acquire the AP110 writing lease."""
from pathlib import Path
import hashlib
import json
import subprocess

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT / 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()

parent = git('rev-parse', 'origin/feat/client-v2')
assert parent == '62ca35a01fb88b37e16b7003e26c2f9110c131f3' == git('rev-parse', 'HEAD')
pr = json.loads(subprocess.check_output(['gh','pr','view','12','--json',
    'url,state,mergedAt,mergeCommit,headRefOid,baseRefName'], cwd=ROOT, text=True))
assert pr['state'] == 'MERGED' and pr['mergeCommit']['oid'] == parent
assert git('show', '-s', '--format=%P', parent) == 'dad89bb5d08e6d34abc5cfab57fc76010c5131dc'
assert git('rev-parse', parent+'^{tree}') == git('rev-parse', pr['headRefOid']+'^{tree}')
review = BLOCK/'30_AUSFUEHRUNG/AP-CV2-100/RUNS/R05-ABNAHME/01_REPORT.md'
approval = BLOCK/'30_AUSFUEHRUNG/AP-CV2-100/RUNS/R06-UEBERNAHME/00_PROMPT_ORIGINAL.md'
assert 'ROOT_PASS' in review.read_text(encoding='utf-8')
assert 'Bitte führe den Merge durch.' in approval.read_text(encoding='utf-8')
data = dict(parent=parent, tree=git('rev-parse','HEAD^{tree}'), predecessor=pr,
    singleParent=True, treeEquality=True, predecessorReview=str(review.relative_to(ROOT)),
    humanApproval=str(approval.relative_to(ROOT)), planningHashes={})
for path in ['PLANUNG/ARBEITSPAKETE/AP-CV2-110.md','PLANUNG/EVIDENCE/package-manifest.json']:
    data['planningHashes'][path] = hashlib.sha256((BLOCK/path).read_bytes()).hexdigest()
(EV/'start-provenance.json').write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
path = BLOCK/'WORKFLOW_STATUS.json'
status = json.loads(path.read_text(encoding='utf-8'))
status.update(workflowPhase='IMPLEMENTATION_IN_PROGRESS', packageStatus='IN_PROGRESS',
    activePackage='AP-CV2-110', nextPackage='AP-IV2-010', canonicalParent=parent,
    candidateBranch='work/client-v2/ap-cv2-110',pullRequest=None,selectedCandidate=True,
    reviewedCommit=None,reviewReport=None,humanApproval=None,openFindingIds=[],
    writeOwner='AP-CV2-110/R01-UMSETZUNG',blockingReason=None,
    nextAction='Legacyautoritäten abbauen und installierte/frozen V2-Produkte qualifizieren.')
status.pop('reviewedTree',None)
status.pop('correctionEvidence',None)
run='30_AUSFUEHRUNG/AP-CV2-110/RUNS/R01-UMSETZUNG/'
status['lastRun']=dict(id='R01-UMSETZUNG',role='implementation',report=run+'01_REPORT.md',evidence=run+'EVIDENCE/INDEX.md')
status['candidateSelection']=dict(candidateId='AP-CV2-110',source=run+'00_PROMPT_ORIGINAL.md',reason='Ausdrücklicher AP110-Auftrag nach belegtem AP100-Squash.')
status['workAuthorization']['currentImplementationSource']=run+'00_PROMPT_ORIGINAL.md'
path.write_text(json.dumps(status,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
