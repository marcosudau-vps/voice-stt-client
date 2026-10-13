"""R04 correction records; completed R01/R02/R03 run records stay immutable."""
from pathlib import Path
import json
import os
import re

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
RUN = EV.parent
PREFIX = '30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/'
FINDING = 'CV2-100-R03-F01'
manifest = json.loads((EV/'windows-validation.json').read_text(encoding='utf-8'))
assert manifest['result'] == 'PASS'
assert next(c for c in manifest['checks'] if c['log']=='windows-full-unittest.txt')['testCount'] == 1581
assert next(c for c in manifest['checks'] if c['log']=='targeted-unittest.txt')['testCount'] == 210

def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')
def link(source, target):
    return os.path.relpath(target, source.parent).replace('\\','/')

status_path = BLOCK/'WORKFLOW_STATUS.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
status.update(workflowPhase='REVIEW_READY',packageStatus='REVIEW_READY',openFindingIds=[],
    writeOwner=None,blockingReason=None,nextAction='R04-Kandidat nach grüner finaler PR-CI frisch unabhängig im Gesamtumfang prüfen; Fokus F01. Kein Merge/AP110 ohne ROOT_PASS und menschliche Freigabe.')
status['correctionEvidence'] = dict(findingIds=[FINDING],state='SELF_CHECK_FIXED_REVIEW_PENDING',report=PREFIX+'01_REPORT.md')
write(status_path,json.dumps(status,ensure_ascii=False,indent=2)+'\n')

path = BLOCK/'PLANUNG/EVIDENCE/package-manifest.json'
data = json.loads(path.read_text(encoding='utf-8'))
ap = next(p for p in data['packages'] if p['id']=='AP-CV2-100')
ap.update(status='REVIEW_READY',executionReport=PREFIX+'01_REPORT.md',windowsValidation=PREFIX+'EVIDENCE/windows-validation.json',checkpointEvidence=PREFIX+'EVIDENCE/server-runtime-checkpoint.json',openFindingIds=[])
ap['correctionFindingIds'] = [FINDING]
write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')

methods = ['test_local_settings_audit_correlates_overlay_audio_and_logging_success',
    'test_local_settings_audit_reports_persist_failure_and_restores_audio',
    'test_local_settings_audit_reports_post_save_rollback',
    'test_local_settings_busy_attempt_preserves_pending_audit_correlation',
    'test_local_settings_unavailable_core_finishes_audit_once',
    'test_local_settings_apply_survives_audit_ingress_failure',
    'test_local_settings_shutdown_completes_pending_audit_once']
path = BLOCK/'PLANUNG/REFERENZ/TRACEABILITY/requirements.json'
data = json.loads(path.read_text(encoding='utf-8'))
for req in data['requirements']:
    if req.get('ap') != 'AP-CV2-100': continue
    old = req['implementationEvidence']
    req.setdefault('implementationHistory',[]).append(old)
    current = dict(old)
    current.update(run='R04-KORREKTUR',report=PREFIX+'01_REPORT.md',windowsValidation=PREFIX+'EVIDENCE/windows-validation.json',checkpointEvidence=PREFIX+'EVIDENCE/server-runtime-checkpoint.json')
    if req['id'] == 'RUNTIME-02':
        current['methods'] = old['methods']+['tests.test_v2_runtime_integration.QtRuntime.'+m for m in methods]
        current['correctionFindingId'] = FINDING
    req['implementationEvidence'] = current
    assert req['status'] == 'CLIENT OPEN'
write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')

paths = ['task.md','ÜBERGABE.md','docs/PROJEKTUEBERSICHT.md',
    'ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md','ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md',
    'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/README.md','ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/STATUS.md',
    'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md']
for name in paths:
    path = ROOT/name
    old = path.read_text(encoding='utf-8')
    _, sep, tail = old.partition('## Historischer Stand vor AP-CV2-020')
    assert sep
    report = link(path,RUN/'01_REPORT.md')
    evidence = link(path,EV/'INDEX.md')
    state = link(path,status_path)
    package = link(path,BLOCK/'30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md')
    interfaces = link(path,ROOT/'docs/protocol-v2-runtime.md')
    review = link(path,BLOCK/'30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md')
    header = f'''# Client V2 – AP-CV2-100 / R04-KORREKTUR / REVIEW_READY, 2026-10-13

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED]({review}) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report]({report}), [Evidenz]({evidence}), [Paketakte]({package}),
[Workflowstatus]({state}), [Runtimeinterfaces]({interfaces}).
Start `.\\venv\\Scripts\\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

'''
    write(path,header+sep+tail)

path = BLOCK/'30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md'
text = path.read_text(encoding='utf-8').replace('**Status:** CHANGES_REQUIRED. Stand 2026-10-13. Unabhängige R03-Abnahme: offenes Pflichtfinding CV2-100-R03-F01.',
    '**Status:** REVIEW_READY. Stand 2026-10-13. F01 im R04-Selbstcheck korrigiert; frische unabhängige Abnahme offen.')
text = text.replace('## Aktueller Korrekturlauf R02','## Historischer Korrekturlauf R02').replace('## Aktuelle unabhängige Abnahme R03','## Historische unabhängige Abnahme R03')
write(path,text+'\n## Aktueller Korrekturlauf R04\n\n[Originalauftrag](RUNS/R04-KORREKTUR/00_PROMPT_ORIGINAL.md),\n[Report](RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md).\nF01 mit tatsächlichem V2-Desktop/Bridge/Core reproduziert und korrigiert;\nWindows1581/gezielte210/Servercheckpoint17 PASS. Kandidatgebundene vollständige Logs\nund 213 Gitblobs im R04-Manifest. Neuer Head/Tree und finale CI im PR; danach\nSchreibpause für frischen unabhängigen Gesamt-Review. Kein eigener ROOT_PASS.\n')
path = BLOCK/'PLANUNG/ARBEITSPAKETE/AP-CV2-100.md'
text = path.read_text(encoding='utf-8').replace('**Status:** CHANGES_REQUIRED','**Status:** REVIEW_READY',1)
text = text.replace('## Aktueller unabhängiger R03-Abnahmebefund','## Historischer unabhängiger R03-Abnahmebefund')
write(path,text+'\n## Aktueller R04-Korrekturkandidat, 2026-10-13\n\n[Report](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md),\n[Evidenz](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md).\nF01 im Selbstcheck korrigiert, vollständige Windows-Requalifikation bestanden.\nFachliche Kriterien unverändert; frische unabhängige Vollabnahme nach finaler grüner CI.\n')
path = BLOCK/'PLANUNG/ARBEITSPAKETE/README.md'
text = path.read_text(encoding='utf-8')
_, sep, tail = text.partition('# Arbeitspakete – Index und Liefergrenzen')
assert sep
text = '# Aktueller Paketstand – 2026-10-13\n\nAP000 bis AP090 ACCEPTED; AP100 **REVIEW_READY** nach [R04-Korrektur](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md). F01 im Selbstcheck korrigiert; aktueller Kandidat muss nach grüner finaler CI frisch unabhängig im Gesamtumfang geprüft werden. [Workflowstatus](../../WORKFLOW_STATUS.json). Kein Merge/AP110 ohne PASS und menschliche Freigabe.\n\n'+sep+tail
text = text.replace('Für AP100 gelten [R02-Selbstnachweise]', 'Historische AP100-Quellen: [R02-Selbstnachweise]')
write(path,text)

path = BLOCK/'PLANUNG/REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md'
text = path.read_text(encoding='utf-8')+'\n## AP-CV2-100 – R04-Findingkorrektur, 2026-10-13\n\nF01 im Selbstcheck korrigiert; alle sechs Requirements bleiben CLIENT OPEN.\n[Report](../../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md),\n[Windows1581/gezielte210](../../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/windows-validation.json),\n[Servercheckpoint17](../../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/server-runtime-checkpoint.json).\nAlle bisherigen individuellen AP100-Methoden im neuen Kandidaten erneut ausgeführt.\nRUNTIME-02 / OBS-Korrelation zusätzlich durch folgende tatsächliche QtRuntime-Methoden\nunter tests.test_v2_runtime_integration geprüft:\n\n'
text += '\n'.join('- `'+m+'`' for m in methods)+'\n\nKein historisches R03-Urteil überschrieben; frischer unabhängiger Gesamt-Review offen.\n'
write(path,text)

report = '''# AP-CV2-100 / R04-KORREKTUR – CV2-100-R03-F01

**Status:** REVIEW_READY. Vollständige Selbstchecks; keine unabhängige Eigenabnahme.
Tatsächliche Reviewübergabe erst nach grüner finaler PR-CI.

## Auftrag und Identität

[Originalauftrag](00_PROMPT_ORIGINAL.md), [R03-CHANGES_REQUIRED](../R03-ABNAHME/01_REPORT.md).
Branch `work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12)
gegen `feat/client-v2`; Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`, Server
`ada13b011e1d3829f78e7f389e3b927795a2b3be`. Starthead nach Fetch/Fast-forward
`c5a510f193908d7493f979365e45be6317cd9dab`, sämtliche R03-Unterlagen enthalten;
R03-Nachtrag gegenüber reviewed4a35a2d rein administrativ, Produkt-/Testdiff leer.
[Start-/Git-/PR-Provenienz](EVIDENCE/start-provenance.json); Parent unverändert,
kein fremder aktiver Schreibowner. Fortgeltende Paket-Gitfreigabe und menschlicher
Korrekturprompt gesichert; keine kanonische Übernahmefreigabe.

## F01: Repro, minimale Korrektur und neue Nachweise

Vorherige relevante Suite: 56 Tests PASS. Neue Prüfungen im tatsächlichen
V2DesktopApplication + V2CoreBridge + V2Runtime mit realem aufzeichnendem
ObservabilityIngress: Overlay/Audio/Logging anwenden und AppConfig.save_user gezielt
scheitern lassen. Vor Fix fehlen alle drei Auditereignisse; zwei Reprofälle FAIL.
Vollständige [Baseline](EVIDENCE/baseline-targeted.txt) und
[Vorher-Repro](EVIDENCE/f01-before-fix.txt); Befehle im Evidenzindex.

Produktfix ausschließlich ui/v2_application.py und core/v2_runtime.py:

- Qt erzeugt `settings:<uuid-prefix>` und `client.settings.apply_started` samt
  Policies erst nach Busyprüfung. Bestehender V2CoreBridge-Korrelationsport reicht
  dieselbe ID über CoreBridge an V2Runtime weiter; keine zweite Applyausführung.
- Core emittiert nach der angenommenen lokalen Transaktion genau ein
  `client.settings.runtime_apply`, im finally nach normalem Abschluss oder Rollback.
  Details: `session_changed=false`, tatsächlicher `audio_changed`-Vergleich,
  `mode_changed=false`, `success`, `status`; Session/Generation am Emissionspunkt.
  Flags folgen dem lokalen Port: Server-/Triggerprofilwechsel sind weiterhin
  abgewiesen und gehören SettingsUISession. Reine Overlay-/Loggingänderung hat
  drei false Flags und keinen Reconnect/Audiorestart.
- Qt verwendet den geerbten idempotenten `_complete_settings_observation` für
  `client.settings.apply_completed` mit derselben ID und Resultstatus. IDverbrauch
  verhindert doppelte Abschlüsse; Core-Abweisung und Shutdown schließen offene
  Versuche ebenfalls ab. Busy überschreibt keine laufende ID.
- Vorhandener ClientEventEmitter schirmt Ingressfehler ab. Nur Policies/Flags und
  Status werden publiziert, keine Konfigwerte/Credentials. Korrelations-ID hat
  keine steuernde Wirkung. Kein Server-/Wire-/Schema-/Technologiewechsel.

Sieben neue Methoden in tests.test_v2_runtime_integration.QtRuntime:
'''
report += '\n'.join('- `'+m+'`' for m in methods)
report += '''

Sie prüfen drei Events in Reihenfolge, Auditkanal, identische eindeutige ID, drei
Flags, Erfolgs-/Fehlerstatus, Session/Generation und genau einen UI-Abschluss;
Audio/Persistenzfehler sowie Fehler nach bereits erfolgreichem Speichern sichern
tatsächlichen Memory-/Diskrollback. Zusätzliche Core-Abweisung bewahrt zwei
Started/Completed-Events ohne erfundene Runtimeausführung. Shutdown prüft fertigen
Persistenzschritt, beendeten Core und abgemeldete Keys; Completion darf bereits
`applied` oder wegen UI-Teardown `shutdown` sein, bleibt genau einmal korreliert.

Erster Nachfixlauf: vier Tests FAIL ausschließlich wegen erwarteter Listendarstellung
der Policies; der echte CanonicalLogRecord friert Listen als Tuple ein. Assertion
auf tatsächliches Immutable-Tuple korrigiert, funktionaler Auditvertrag unverändert.
Danach 62 Tests PASS, zusätzlicher Shutdownfall PASS, abschließend alle sieben Fälle
erneut in gezielter Suite und Vollsuite. Sämtliche Iterationslogs erhalten.

## Vollqualifikation und Kandidatenbindung

Windows11/Python3.12.10, Dependencies, vollständige Befehle/Exits/Zahlen/Zeitpunkte,
Loghashes, 213 qualifizierte Gitblobs und lokale Sourcehashes im
[Windowsmanifest](EVIDENCE/windows-validation.json). Basis c5a510f plus
[exakte staged Produkt-/Testdiff](EVIDENCE/tested-product.patch.base64), base64/SHA256.
Finalen Head/Tree nach Unterlagen aus Git in PR/Übergabe ermitteln; administrative
Nachträge verändern keinen qualifizierten Produkt-/Test-/Konfigblob.

- 1581 vollständige Windows-Clienttests PASS, keine Skips.
- 210 gezielte Tests mit -W error PASS (28 Runtime/Qt/Migrationsfälle plus Bestand).
- 17 tatsächliche komponierte Desktop/Core/Qt-/HTTP-/Domain-/Logchecks gegen
  45 bytegeprüfte Serverquellen am gepinnten ada13b0 PASS.
- compileall, staged/unstaged Diffcheck und [Akten-/Blob-/Logprüfung](EVIDENCE/submission-verification.json) PASS.

Vollständige [Belege/Befehle](EVIDENCE/INDEX.md). Nach Push muss finale headgebundene
Windows-CI einschließlich EXE-/sdist-/Wheel-Smokes bestanden sein; tatsächliches
Ergebnis/SHA/Run wird im PR verlinkt, keine vorausgenommene CI-Erfolgsbehauptung.

## Traceability, Dokumentation und Übergabe

FINAL-01/02 und RUNTIME-01 bis RUNTIME-04 bleiben CLIENT OPEN. Die individuellen
[R01-Paketmethoden](../R01-UMSETZUNG/01_REPORT.md) wurden im R04-Kandidaten erneut
bestanden; RUNTIME-02 erhält die sieben tatsächlichen Audit-/Fehlerfälle zusätzlich.
Requirements/Matrix führen R04-Belege, bisherige R01/R02-Belege bleiben in der
Historie. R03-Reviewurteil und komplette Reviewakte unverändert erhalten.
WORKFLOW_STATUS, Manifest, Paket-/Planindex, Steuerung, task.md, ÜBERGABE.md,
Projektübersicht sowie Runtimeinterfaces/OBS-Katalog aktuell; genau ein
R04-Selbstcheckmeilenstein in Block-/Steuerungslog.

Neue öffentliche Signatur entsteht nicht: correlation_id und der Bridgeport
existierten bereits; Runtime nutzt ihn nun tatsächlich. Thread-/Generationguards,
vorhandene Serverautorität, Persistenz-/Rollbackablauf und sonstige Produktports
aus R01 unverändert. Frische unabhängige Abnahme des gesamten kumulativen AP100
mit Fokus F01 erforderlich, Umsetzung nach Übergabe pausiert. F01 im Selbstcheck
behoben, kein eigenes ROOT_PASS. Kein Merge/AP110 ohne unabhängigen PASS und
menschlichen Prompt. Reale Hardware-/ASR-/Crossrepo-/finale V2-Buildgates bleiben
den späteren Paketen zugeordnet; CI-Smokes ersetzen diese nicht.
'''
write(RUN/'01_REPORT.md',report)
index = '''# Evidenz – AP-CV2-100 / R04-KORREKTUR

**Status:** REVIEW_READY. Vollständige Selbstchecks, unabhängige Abnahme offen.
Basis c5a510f193908d7493f979365e45be6317cd9dab plus exakte Produktdiff/Gitblobs,
Parent dad89bb5d08e6d34abc5cfab57fc76010c5131dc, Server ada13b0.

| Beleg | Befehl / Zweck / Ergebnis |
| --- | --- |
| [Startprovenienz](start-provenance.json), [Treiber](record_start.py) | Fetch/ff-only, git rev-parse/diff, gh pr view; R03-Docs übernommen, Head/Base und aktueller Schreib-/Reviewzustand gesichert |
| [Baseline](baseline-targeted.txt) | Projektvenv -W error -m unittest tests.test_v2_runtime_integration tests.test_obs040_client_hooks -v vor erster Änderung; 56 PASS |
| [F01 vor Fix](f01-before-fix.txt) | Projektvenv -W error -m unittest tests.test_v2_runtime_integration.QtRuntime.test_local_settings_audit_correlates_overlay_audio_and_logging_success tests.test_v2_runtime_integration.QtRuntime.test_local_settings_audit_reports_persist_failure_and_restores_audio -v; zwei erwartete FAIL, Auditkette fehlt |
| [Nachfix-Iteration](f01-after-fix.txt) | Baselinebefehl mit neuen Fällen; 62 Tests, vier FAIL wegen Tuple/List-Erwartung der unveränderlichen Policies; erhalten, keine aktuellen Erfolgsbelege |
| [Korrigierte gezielte Tests](f01-corrected-targeted.txt) | Derselbe Befehl nach Assertionkorrektur; 62 PASS |
| [Shutdown](f01-shutdown.txt) | Projektvenv -W error -m unittest tests.test_v2_runtime_integration.QtRuntime.test_local_settings_shutdown_completes_pending_audit_once -v; 1 PASS |
| [Windowsmanifest](windows-validation.json), [Treiber](qualify_windows.py), [exakte Produktdiff](tested-product.patch.base64) | Kandidaten-/Runtime-/Befehls-/Exit-/Testzahl-/SHA256-Bindung, 213 Produkt-/Test-/Konfigblobs; PASS |
| [Gezielter Vollnachweis](targeted-unittest.txt) | Vollständiger Befehl im Manifest; 210 Tests -W error PASS einschließlich aller sieben neuen Qt-Fälle |
| [Vollständige Windows-Suite](windows-full-unittest.txt) | Projektvenv -m unittest discover -s tests -p test_*.py -v; 1581 PASS, keine Skips |
| [Servercheckpoint](server-runtime-checkpoint.json), [stderr](server-runtime-checkpoint.json.stderr.txt) | scripts/check_v2_server_runtime.py mit manifestgebundenen Pfaden; 17 komponierte reale Client/Serverchecks, 45 Quellen bytegeprüft PASS |
| [compileall](compileall.txt) | Projektvenv -m compileall -q voice_stt_client scripts tests; Exit0 PASS |
| [Abgabeprüfung](submission-verification.json), [Treiber](verify_submission.py) | Qualifizierte staged Gitblobs/Loghashes, Paket-/Status-/Manifest-/Markdownlinks PASS; tatsächliche PR-Kurzfassung nach Push separat read-only geprüft |
| [Dokumentationstreiber](complete_records.py), [PR-Vorbereitung](prepare_pr.py) | R04-Unterlagen und externe PR-Beschreibung aus tatsächlichem Head/Tree; CI-Ergebnis nur nach SHA-/Erfolgsprüfung |

Qualification-Logs UTF-8 LF vor Hashbildung; vollständige negative Diagnostik
ist erwarteter Faultinjectionnachweis. Vorher-/Iterationslogs stammen aus
PowerShellredirects, Exit/Zahl im Log; diese ersetzen nicht die qualifizierten Logs.
Tatsächliche endgültige CI/Head/Tree und Übergabe im PR, bevor unabhängiger Review
beginnt. Kein eigener ROOT_PASS oder behaupteter realer Hardware-/ASR-Gate.
'''
write(EV/'INDEX.md',index)
write(EV/'verify_submission.py',(EV.parents[1]/'R02-KORREKTUR/EVIDENCE/verify_submission.py').read_text(encoding='utf-8'))
for path, reportlink in [(BLOCK/'VERLAUF.md',PREFIX+'01_REPORT.md'),
    (ROOT/'ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md','../10_AKTUELL/CLIENT_V2/'+PREFIX+'01_REPORT.md')]:
    text = path.read_text(encoding='utf-8')
    assert 'AP-CV2-100 / R04-KORREKTUR: F01' not in text
    write(path,text+'\n## 2026-10-13 – AP-CV2-100 / R04-KORREKTUR: F01\n\nR03-Reviewakte fetch/ff-only übernommen. Fehlende korrelierte Settingsaudits\nim tatsächlichen V2-Desktop/Bridge/Core reproduziert und minimal ergänzt; sieben\nPositiv-/Negativ-/Rollback-/Busy-/Shutdown-/Ingressfälle hinzugefügt.\nWindows1581/gezielte210/Servercheckpoint17/compileall/diffcheck PASS; neue\nKandidaten-/Log-/Gitblobbindung. [R04-Report]('+reportlink+').\nREVIEW_READY im Selbstcheck, tatsächliche Übergabe nach finaler grüner CI.\nR03-CHANGES_REQUIRED historisch erhalten; frischer Gesamt-Review offen, kein Merge/AP110.\n')
print('R04 records complete')
