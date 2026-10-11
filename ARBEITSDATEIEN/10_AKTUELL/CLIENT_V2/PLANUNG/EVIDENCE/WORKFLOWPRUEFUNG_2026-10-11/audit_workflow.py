"""Inspect committed first-run artifacts; never changes the package or branch."""
from pathlib import Path, PurePosixPath
from urllib.parse import unquote
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import Mock
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys

ROOT = Path(r'P:\GithubRepos\marcosudau-vps')
REPO = ROOT / 'voice-stt-client/workspaces/client-v2'
OUT = Path(__file__).parent
BASE = '050e776cf316eb332177294db0c0a2719c2b4415'
IMPLEMENTED = '8b1c4c157b6b431dac6af69e2e264d0c37579bef'
REVIEW = '2dc251df959f97e2a0bb37b10a1a77486ae6eb5a'
BLOCK = 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'

def git(*args):
    return subprocess.check_output(['git', '-C', str(REPO), *args])

def content(path, commit=REVIEW):
    return git('show', commit + ':' + path).decode('utf-8-sig')

def obj(path, commit=REVIEW):
    return json.loads(content(path, commit))

files = set(git('ls-tree', '-r', '--name-only', REVIEW).decode().splitlines())
state = obj(BLOCK + '/WORKFLOW_STATUS.json')
manifest = obj(BLOCK + '/PLANUNG/EVIDENCE/package-manifest.json')
reqs = obj(BLOCK + '/PLANUNG/REFERENZ/TRACEABILITY/requirements.json')['requirements']
review_changes = git('diff', '--name-only', IMPLEMENTED, REVIEW).decode().splitlines()
remote_base = git('ls-remote', '--heads', 'origin', 'feat/client-v2').decode().split()[0]
remote_head = git('ls-remote', '--heads', 'origin', 'work/client-v2/ap-cv2-000').decode().split()[0]
assert remote_base == BASE and remote_head == REVIEW, 'Snapshot changed during audit'
assert not git('status', '--porcelain').strip(), 'Do not interact with foreign working changes'
assert all(p.startswith('ARBEITSDATEIEN/') and PurePosixPath(p).suffix == '.md' or p == BLOCK + '/WORKFLOW_STATUS.json' for p in review_changes)
assert git('rev-parse', REVIEW + '^').decode().strip() == IMPLEMENTED
assert state['reviewedCommit'] == IMPLEMENTED
assert state['workflowPhase'] == state['packageStatus'] == 'CHANGES_REQUIRED'
assert state['openFindingIds'] == ['CV2-R02-F01']
assert state['writeOwner'] is state['humanApproval'] is None
assert git('show', IMPLEMENTED + ':' + BLOCK + '/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md') == git('show', REVIEW + ':' + BLOCK + '/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md')

broken = []
checked_links = 0
record_paths = [p for p in files if p.startswith(BLOCK + '/30_AUSFUEHRUNG/AP-CV2-000/') and p.endswith('.md')]
for path in sorted(record_paths):
    for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', content(path)):
        target = target.strip('<>').split(' "', 1)[0]
        if re.match(r'^[a-zA-Z][a-zA-Z0-9+.-]*:', target) or target.startswith('#'):
            continue
        destination = posixpath.normpath(posixpath.join(posixpath.dirname(path), unquote(target.split('#')[0])))
        checked_links += 1
        if destination not in files:
            broken.append({'path': path, 'target': target, 'resolved': destination})

pr = json.loads(subprocess.check_output(['gh', 'pr', 'view', '2', '--repo', 'marcosudau-vps/voice-stt-client', '--json', 'number,title,state,baseRefName,baseRefOid,headRefName,headRefOid,mergeStateStatus,reviewDecision,statusCheckRollup,comments,reviews,commits,url']))
assert pr['headRefOid'] == REVIEW and pr['baseRefOid'] == BASE and pr['state'] == 'OPEN'
(OUT / 'pr-snapshot.json').write_text(json.dumps(pr, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

result = {
    'checkedAtUtc': datetime.now(timezone.utc).isoformat(),
    'scope': 'Workflow audit plus isolated deterministic reproduction; not package acceptance or complete regression',
    'canonicalCommit': BASE, 'reviewedImplementationCommit': IMPLEMENTED,
    'reviewDocsCommit': REVIEW, 'localCheckoutCommit': git('rev-parse', 'HEAD').decode().strip(),
    'localCheckoutBehindRemoteReviewCommits': int(git('rev-list', '--count', 'HEAD..' + REVIEW).decode()),
    'workflowPhase': state['workflowPhase'], 'nextAction': state['nextAction'],
    'canonicalBranchUnchanged': True, 'reviewCommitDocsOnly': True,
    'reviewCommitChangedPaths': len(review_changes), 'oldImplementationReportUnmodified': True,
    'packageMetadataStatus': manifest['packages'][0]['status'],
    'packageMetadataMismatch': manifest['packages'][0]['status'] != state['packageStatus'],
    'reviewRequiredEvidencePathsExist': all(BLOCK + '/' + state[k] in files for k in ('reviewReport',)),
    'checkedPackageRecordMarkdownFiles': len(record_paths), 'checkedRelativeRecordLinks': checked_links,
    'brokenRelativeRecordLinks': broken,
    'requirementsTotal': len(reqs), 'currentPackageRequirements': sum(r['ap'] == 'AP-CV2-000' for r in reqs),
    'prBodyStillSaysReviewReady': 'Status: REVIEW_READY' in pr['body'] if 'body' in pr else None,
    'latestPrCommentMentionsChangesRequired': 'CHANGES_REQUIRED' in pr['comments'][-1]['body'],
    'currentHeadCiConclusion': pr['statusCheckRollup'][0]['conclusion'],
    'qualifiedImplementationCommitBeforeCiTestCorrection': state['qualifiedImplementationCommit'],
}

# Execute the exact candidate methods with fake runtime collaborators and real
# persistence confined to synthetic profiles in this durable evidence folder.
assert git('rev-parse', 'HEAD').decode().strip() == IMPLEMENTED
sys.path.insert(0, str(REPO))
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
from voice_stt_client.core.config import AppConfig
from voice_stt_client.ui.application import DesktopApplication
from voice_stt_client.ui.hotkeys import HOTKEY_ID_TOGGLE
from unittest.mock import patch

class Hotkeys:
    enabled = True
    last_failure = (HOTKEY_ID_TOGGLE, OSError(1409, 'simulated hotkey conflict'))
    def __init__(self, success):
        self.success = success
    def register(self):
        return self.success
    def unregister(self):
        pass

results = []
for succeeds in (False, True):
    sandbox = OUT / 'SYNTHETISCHE_PROFILE'
    sandbox.mkdir(exist_ok=True)
    profile = sandbox / ('core-success-v2.yaml' if succeeds else 'core-failure-v2.yaml')
    assert not profile.exists(), 'Do not overwrite reproduction evidence'
    profile.write_text('hotkey:\n  enabled: true\n  toggle_key: Ctrl+Shift+Space\nfeedback:\n  sounds_enabled: false\nled:\n  enabled: false\n', encoding='utf-8')
    before = profile.read_bytes()
    cfg = AppConfig.load(profile)
    trace = []
    original_save = cfg.save_user
    def save():
        trace.append('save_user')
        original_save()
    cfg.save_user = save
    desktop = SimpleNamespace(_started=False, tray=Mock(), config=cfg,
        hotkeys=Hotkeys(False), _on_fatal_error=Mock(), _observe=Mock(),
        _report_lifecycle_started=Mock())
    desktop._create_hotkey_manager = lambda _cfg: Hotkeys(True)
    desktop._register_startup_hotkeys = lambda: DesktopApplication._register_startup_hotkeys(desktop)
    def start_core():
        trace.append('bridge.start')
        return succeeds
    desktop.bridge = SimpleNamespace(start=start_core)
    with patch('voice_stt_client.ui.application.fallback_hotkeys', return_value=['Ctrl+Alt+Shift+F12']):
        started = DesktopApplication.start(desktop)
    after = profile.read_bytes()
    loaded = AppConfig.load(profile)
    assert started == succeeds and before != after
    assert loaded.hotkey.toggle_key == 'Ctrl+Alt+Shift+F12'
    assert trace == ['save_user', 'bridge.start']
    results.append({'coreStartSucceeds': succeeds, 'appStarted': started, 'profileModified': before != after,
        'persistedHotkey': loaded.hotkey.toggle_key, 'callOrder': trace,
        'originalProfileSha256': hashlib.sha256(before).hexdigest(),
        'finalProfileSha256': hashlib.sha256(after).hexdigest(),
        'userProfilesTouched': False,
        'expectedProfilePreservationOnFailure': None if succeeds else 'FAIL_REPRODUCED'})

result['hotkeyReproduction'] = results
result['hotkeyRuntimeBoundary'] = 'Exact application methods + real AppConfig persistence on Windows; fake hotkey registration/core/tray, no real Win32 hardware or full app initialization'
release = content('voice_stt_client/ui/application.py', 'f625904795880ce71acec216e43678f9ec1656d0')
current = content('voice_stt_client/ui/application.py', IMPLEMENTED)
result['samePersistenceOrderingAlreadyInV1'] = all('self.config.save_user()' in s[s.index('def _register_startup_hotkeys'):s.index('def _report_lifecycle_started')] and s.index('hotkeys_ok = self._register_startup_hotkeys()') < s.index('if not self.bridge.start():') for s in (release, current))
result['workingTreeCleanAfterAudit'] = not git('status', '--porcelain').strip()
assert result['workingTreeCleanAfterAudit']
(OUT / 'workflow-audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(json.dumps(result, ensure_ascii=True, indent=2))
