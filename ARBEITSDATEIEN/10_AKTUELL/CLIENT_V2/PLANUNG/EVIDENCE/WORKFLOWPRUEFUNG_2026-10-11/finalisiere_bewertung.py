from pathlib import Path
from urllib.parse import unquote
import json
import re
import subprocess

archive = Path(__file__).parent
repo = Path(r'P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\client-v2')
snapshot = json.loads(subprocess.check_output(['gh', 'pr', 'view', '2', '--repo', 'marcosudau-vps/voice-stt-client', '--json', 'body,headRefOid,baseRefOid,state,url']))
audit_path = archive / 'workflow-audit.json'
audit = json.loads(audit_path.read_text(encoding='utf-8'))
assert snapshot['headRefOid'] == audit['reviewDocsCommit'] and snapshot['baseRefOid'] == audit['canonicalCommit']
audit['prBodyStillSaysReviewReady'] = 'Status: REVIEW_READY' in snapshot['body']
assert audit['prBodyStillSaysReviewReady']
audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
(archive / 'pr-body-snapshot.json').write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
links = 0
for path in archive.glob('*.md'):
    for target in re.findall(r'(?<!!)\[[^\]]+\]\(([^)]+)\)', path.read_text(encoding='utf-8')):
        if target.startswith(('https:', 'http:', '#')):
            continue
        assert (path.parent / unquote(target.split('#')[0])).exists(), (path.name, target)
        links += 1

log = Path(r'P:\GithubRepos\marcosudau-vps\_workflow-tools\ARBEITSDATEIEN\00_STEUERUNG\LOG_VERLAUF.md')
text = log.read_text(encoding='utf-8-sig')
assert 'WF-CLIENT-V2-AUDIT-001' not in text
text += '''
## WF-CLIENT-V2-AUDIT-001 – 2026-10-11 – erster Umsetzung-/Reviewablauf bewertet

AP-CV2-000/R01 und R02 einschließlich tatsächlicher Remote-/PR-/CI-Provenienz gelesen; maßgeblicher Zustand CHANGES_REQUIRED auf 2dc251d, Feature050e776 unverändert. Review-Docs-Commit ausschließlich administrativ, R01-Report erhalten. Fehlende Review-Testfähigkeit, drei kaputte R02-Paketindexlinks, veralteter Manifest-/PR-Kurzstatus und nicht wiederverwendbarer alter Aktenvalidator konkret bewertet. F01 mit realen Anwendungsmethoden/Persistenz und simuliertem Runtimefehler in ausschließlich synthetischen Profilen bestätigt; Speicherreihenfolge schon in V1 vorhanden. Kleine Regel-/Aktennachbesserungen gemeinsam im ohnehin benötigten AP000-Korrekturlauf empfohlen, fertigen Originalauftragsentwurf abgelegt. Keine Produkt-/Paketaktendatei geändert, kein Review-PASS, Commit/Push/Merge oder Folgepaket. Bewertung und Belege: Themenordner EINHEITLICHE_TRIGGERARCHITEKTUR/40_EVIDENCE/CLIENT_V2_PLANUNG/2026-10-11_ERSTER_DURCHLAUF.
'''
log.write_text(text, encoding='utf-8', newline='\n')
assert not subprocess.check_output(['git', '-C', str(repo), 'status', '--porcelain']).strip()
print(json.dumps({'assessmentLinksChecked': links, 'candidateWorkingTreeClean': True, 'packageChanged': False, 'recommendationAndCorrectionPromptSaved': True, 'currentPrStatusMismatchConfirmed': True}))
