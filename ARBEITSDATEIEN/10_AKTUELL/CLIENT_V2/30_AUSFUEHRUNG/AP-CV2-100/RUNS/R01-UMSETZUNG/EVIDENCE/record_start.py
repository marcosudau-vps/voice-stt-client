"""Record actual AP100 start and verify predecessor Git/PR provenance."""
from pathlib import Path
import hashlib
import json
import subprocess

B = Path('ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2')
R = B / '30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG'
E = R / 'EVIDENCE'

def git(*args):
    return subprocess.check_output(['git', *args], text=True).strip()

state = json.loads((B / 'WORKFLOW_STATUS.json').read_text(encoding='utf-8-sig'))
canonical = git('rev-parse', 'HEAD')
head = '68c3b3b0add5890fc578744ae0b0609e8fa09cec'
parent = '1bc5be893060e0d6a80e1d890102bfffebb73a17'
pr = json.loads(subprocess.check_output(['gh', 'pr', 'view', '11', '--json',
    'number,url,state,mergeCommit,headRefOid,baseRefOid'], text=True))
assert pr['state'] == 'MERGED' and pr['mergeCommit']['oid'] == canonical
assert pr['headRefOid'] == head and git('show', '-s', '--format=%P', canonical) == parent
assert git('rev-parse', head + '^{tree}') == git('rev-parse', canonical + '^{tree}')
assert git('rev-list', '--count', parent + '..' + canonical) == '1'
(E / 'predecessor-canonicalization.json').write_text(json.dumps(dict(
    result='PASS', package='AP-CV2-090', canonicalCommit=canonical, parent=parent,
    head=head, tree=git('rev-parse', canonical + '^{tree}'), pr=pr,
    checks=['MERGED', 'one_new_commit', 'single_parent', 'tree_equality'],
    reviewReport='30_AUSFUEHRUNG/AP-CV2-090/RUNS/R02-ABNAHME/01_REPORT.md',
    humanPrompt='30_AUSFUEHRUNG/AP-CV2-090/RUNS/R03-UEBERNAHME/00_PROMPT_ORIGINAL.md'
), indent=2) + '\n', encoding='utf-8')
state.update(workflowPhase='IMPLEMENTATION_IN_PROGRESS', packageStatus='IN_PROGRESS',
    activePackage='AP-CV2-100', nextPackage='AP-CV2-110', canonicalParent=canonical,
    candidateBranch='work/client-v2/ap-cv2-100', pullRequest=None, selectedCandidate=True,
    lastRun=dict(id='R01-UMSETZUNG', role='implementation',
        report='30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/01_REPORT.md',
        evidence='30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md'),
    reviewedCommit=None, reviewedTree=None, reviewReport=None, openFindingIds=[],
    humanApproval=None, writeOwner='AP-CV2-100/R01-UMSETZUNG/Codex-2026-10-13',
    blockingReason=None, nextAction='AP100 umsetzen, qualifizieren und als Paket-PR abgeben.',
    candidateSelection=dict(candidateId='AP-CV2-100',
        source='30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md',
        reason='Ausdruecklicher Auftrag nach belegter AP090-Uebernahme.'))
(B / 'WORKFLOW_STATUS.json').write_text(json.dumps(state, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
files = ['PLANUNG/ARBEITSPAKETE/AP-CV2-100.md', 'PLANUNG/REFERENZ/TRACEABILITY/requirements.json',
         'PLANUNG/REFERENZ/KONTRAKTE/K-04_LOGS_AUTH_RECOVERY.md']
(E / 'input-provenance.json').write_text(json.dumps(dict(canonicalParent=canonical,
    branch=state['candidateBranch'], planHashes={f: hashlib.sha256((B / f).read_bytes()).hexdigest()
    for f in files}), indent=2) + '\n', encoding='utf-8')
print('AP100 start and AP090 provenance recorded')
