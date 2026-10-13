"""Publish R02 self-check records after candidate-bound Windows qualification."""
from pathlib import Path
import json
import re

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT / 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
RUN = EV.parent
PREFIX = '30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/'
validation = json.loads((EV/'windows-validation.json').read_text(encoding='utf-8'))
assert validation['result'] == 'PASS'
counts = {c['log']: c for c in validation['checks']}
full = counts['windows-full-unittest.txt']['testCount']
targeted = counts['targeted-unittest.txt']['testCount']
assert full == 1574 and targeted == 203

def write(path, text):
    path.write_text(text, encoding='utf-8', newline='\n')

status_path = BLOCK/'WORKFLOW_STATUS.json'
status = json.loads(status_path.read_text(encoding='utf-8'))
status.update(workflowPhase='REVIEW_READY', packageStatus='REVIEW_READY', openFindingIds=[], writeOwner=None,
              nextAction='Finalen PR-Head nur bei grüner CI an frische unabhängige Abnahme übergeben; danach keine Paketbranchänderungen. Kein Merge/AP110 ohne PASS und menschlichen Prompt.')
write(status_path, json.dumps(status, ensure_ascii=False, indent=2)+'\n')

manifest_path = BLOCK/'PLANUNG/EVIDENCE/package-manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
package = next(p for p in manifest['packages'] if p['id'] == 'AP-CV2-100')
package.update(status='REVIEW_READY', executionReport=PREFIX+'01_REPORT.md',
               windowsValidation=PREFIX+'EVIDENCE/windows-validation.json',
               checkpointEvidence=PREFIX+'EVIDENCE/server-runtime-checkpoint.json')
write(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2)+'\n')

requirements_path = BLOCK/'PLANUNG/REFERENZ/TRACEABILITY/requirements.json'
requirements = json.loads(requirements_path.read_text(encoding='utf-8'))
for requirement in requirements['requirements']:
    if requirement.get('ap') != 'AP-CV2-100':
        continue
    prior = requirement['implementationEvidence']
    requirement.setdefault('implementationHistory', []).append(prior)
    current = dict(prior)
    current.update(run='R02-KORREKTUR', report=PREFIX+'01_REPORT.md',
                   windowsValidation=PREFIX+'EVIDENCE/windows-validation.json',
                   checkpointEvidence=PREFIX+'EVIDENCE/server-runtime-checkpoint.json')
    requirement['implementationEvidence'] = current
    assert requirement['status'] == 'CLIENT OPEN'
write(requirements_path, json.dumps(requirements, ensure_ascii=False, indent=2)+'\n')

paths = ['task.md', 'ÜBERGABE.md', 'docs/PROJEKTUEBERSICHT.md',
         'ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md', 'ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md',
         'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/README.md', 'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/STATUS.md',
         'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md']
for name in paths:
    path = ROOT/name
    text = path.read_text(encoding='utf-8')
    head, separator, historical = text.partition('## Historischer Stand vor AP-CV2-020')
    assert separator and '/ R01 / REVIEW_READY' in head
    head = head.replace('/ R01 / REVIEW_READY', '/ R02 / REVIEW_READY')
    head = head.replace('1573 Windows-/ 190 gezielte Tests', '1574 Windows-/ 203 gezielte Tests')
    head = head.replace('R01-UMSETZUNG/01_REPORT.md', 'R02-KORREKTUR/01_REPORT.md')
    head = head.replace('R01-UMSETZUNG/EVIDENCE/INDEX.md', 'R02-KORREKTUR/EVIDENCE/INDEX.md')
    head += 'R02 behebt CI-01: großzügige Testfristen für Replay mit dauerhaftem Cursor-IO,\nzusätzlicher 280-ms-Schreibverzögerungsfall, unveränderte Funktionsassertions.\nCI des finalen PR-Heads muss vor tatsächlicher Reviewübergabe grün sein.\n\n'
    write(path, head+separator+historical)

index = BLOCK/'30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md'
text = index.read_text(encoding='utf-8')
text += '\n## Aktueller Korrekturlauf R02\n\n[Originalauftrag](RUNS/R02-KORREKTUR/00_PROMPT_ORIGINAL.md),\n[Report](RUNS/R02-KORREKTUR/01_REPORT.md),\n[Evidenz](RUNS/R02-KORREKTUR/EVIDENCE/INDEX.md).\nCI-01 korrigiert, Windowsvollsuite1574, gezielte203, Servercheckpoint17 PASS.\nR01 bleibt historische Umsetzungsevidenz. Finaler Kandidat: Basis ca3cd400 plus\nR02-Produktdiff/Gitblobs; exakten veröffentlichten Head/Tree und abschließenden\nCI-Erfolg im PR prüfen. Reviewübergabe erst bei grüner finaler CI.\n'
write(index, text)
spec = BLOCK/'PLANUNG/ARBEITSPAKETE/AP-CV2-100.md'
write(spec, spec.read_text(encoding='utf-8')+'\n## Aktueller R02-Korrekturbeleg, 2026-10-13\n\n[Report](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md),\n[Evidenz](../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/EVIDENCE/INDEX.md).\nCI-01 reproduziert und korrigiert; vollständige Windows-Selbstqualifikation erneut\nbestanden. Paketziele und Produktcode unverändert. Frische unabhängige Abnahme offen.\n')
matrix = BLOCK/'PLANUNG/REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md'
write(matrix, matrix.read_text(encoding='utf-8')+'\n## AP-CV2-100 – CI-Korrektur R02, 2026-10-13\n\nFINAL-01/02 und RUNTIME-01 bis RUNTIME-04 bleiben CLIENT OPEN; die oben\nzugeordneten tatsächlichen Methoden wurden im neuen Kandidaten erneut bestanden.\n[Report](../../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md),\n[Windows1574/gezielte203](../../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/EVIDENCE/windows-validation.json),\n[Servercheckpoint17](../../../30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/EVIDENCE/server-runtime-checkpoint.json).\nZusätzliche Legacy-Regressionsabsicherung: `tests.test_event_stream.TestEventStreamTransport.test_cursor_write_failure_replay_tolerates_slow_durable_commit`\nund bestehender `test_cursor_write_failure_replays_without_duplicate_visible_impulse`: Replay nach\nCursor-Schreibfehler, einmaliger sichtbarer Impuls, durable Cursor24, genau zwei\nVerbindungen und sauberer Stop, auch mit 280 ms Schreibverzögerung. Kein Eigen-PASS.\n')

report = '''# AP-CV2-100 / R02-KORREKTUR – CI-01

**Status:** REVIEW_READY. Windows-Selbstchecks bestanden; unabhängige Abnahme offen.
Tatsächliche Reviewübergabe erst nach grüner CI des finalen veröffentlichten Heads.

## Auftrag, Provenienz und Scope

[Originalauftrag](00_PROMPT_ORIGINAL.md). CI vor unabhängiger Abnahme korrigieren,
denselben [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12) verwenden.
Branch `work/client-v2/ap-cv2-100`, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`, Ausgangshead
`ca3cd4009717d508a75ea236aec60881a39fab43`, Tree
`8b79510c47011789aee85976bec9dcc5bbb778a7`. Fetch/fast-forward: bereits aktuell;
keine Reviewakten/aktiven fremden Schreibansprüche vorhanden. Start-/Git-/PR-Zustand
[gesichert](EVIDENCE/start-provenance.json). Gepinnter Server
`ada13b011e1d3829f78e7f389e3b927795a2b3be` unverändert. Vorgängerabschluss
und Gitfreigabe aus R01/WORKFLOW_STATUS bleiben gültig. Keine kanonische Promotion.

## CI-01: Repro, Ursache, Änderung und Nachweis

[Fehlgeschlagene CI](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38342904213):
1573 Tests, genau ein Fehler im bestehenden Legacy-Eventstream-Test
`test_cursor_write_failure_replays_without_duplicate_visible_impulse`.
Vollständiger [Fehlerlog](EVIDENCE/ci-failed.txt) und [Job-/SHA-Metadaten](EVIDENCE/ci-failed.json).
Der Test setzte 100-ms-Replay-/Handshakefristen und einen 500-ms-Gesamtwatchdog,
obwohl er echtes synchrones Cursor-IO mit fsync/replace prüft. Der Runner protokolliert
281 ms Tasklaufzeit, anschließend Replaydeadline, leere Socketliste und TimeoutError.
Dies ist eine zu enge Testfrist für eine Funktionsprüfung, kein nachgewiesener
Produktfehler; Produktionstimeouts und funktionierender Core bleiben unverändert.

Vorher [12 Eventstreamtests PASS](EVIDENCE/baseline-event-stream.txt);
dieselbe Einzelprüfung mit simulierten 280 ms je durable Commit reproduziert
[TimeoutError/FAIL](EVIDENCE/replay-deadline-repro.txt). Der unveränderte
[Reprotreiber](EVIDENCE/reproduce_ci.py) dokumentiert seine Befehle und erwarteten Exits.

Korrektur ausschließlich `tests/test_event_stream.py`: gemeinsame Testhilfe,
5-s-Phasenfristen und 10-s-Gesamtwatchdog für diesen Persistenz-/Replayfall.
Der bisherige Test bleibt erhalten, ein zusätzlicher Fall injiziert 280 ms pro
erfolgreichem synchronem Commit. Alle bisherigen Assertions bleiben erhalten:
ein sichtbarer TRANSCRIPTION_COMPLETED-Impuls mit gleicher Regel, Replayentscheidung,
dauerhafter Cursor24 sowie afterCursor0 auf beiden Verbindungen. Neue Assertions:
genau zwei Generationen, beide Sockets verbraucht, STOPPED. Kein Skip/Retry von Tests,
kein Entfernen funktionaler Abdeckung. [13 gezielte Eventstreamtests PASS](EVIDENCE/corrected-event-stream.txt).

## Vollständige erneute Kandidatenqualifikation

Windows/Python/Abhängigkeiten, Befehle, Testzahlen, Exitcodes, Zeiten, Loghashes und
213 veröffentlichbare Gitblobs im [Windowsmanifest](EVIDENCE/windows-validation.json).
Bindung: getestete Basis ca3cd400 + [exakte staged Testdiff](EVIDENCE/tested-product.patch.base64)
(base64, SHA256 im Manifest). Endhead/Tree nach administrativen Unterlagen aus Git
in PR-Beschreibung/Übergabekommentar; Produktblobgleichheit per
[Abgabeprüfung](EVIDENCE/submission-verification.json).

- 1574 vollständige Windows-Clienttests PASS, keine Skips.
- 203 gezielte Tests mit `-W error` PASS, einschließlich Runtime/Qt/Hotkeys/Settings/Legacy-Replay.
- 17 komponierte App/Core/Qt-/HTTP-/Domain-/Logchecks gegen 45 bytegeprüfte Serverquellen PASS.
- compileall und staged/unstaged Diffprüfung PASS.

Vollständige Logs und erzeugende Befehle im [Evidenzindex](EVIDENCE/INDEX.md).
GitHub-CI qualifiziert zusätzlich den tatsächlichen finalen Head/Base-Testmerge
mit Vollsuite, eingefrorenem EXE-Smoke, Distributionen und installiertem Wheel-Smoke.
Ihr nach dem Push festgestelltes Ergebnis und ihre genaue SHA-Bindung werden im PR
verlinkt; keine vorab erfundene CI-Erfolgsbehauptung in dieser Akte.

## Requirements, Dokumentation und Grenzen

FINAL-01, FINAL-02, RUNTIME-01, RUNTIME-02, RUNTIME-03 und RUNTIME-04:
die individuellen tatsächlichen Methoden aus dem unveränderten
[R01-Paketreport](../R01-UMSETZUNG/01_REPORT.md) wurden im neuen Kandidaten erneut
bestanden. [Requirements](../../../../PLANUNG/REFERENZ/TRACEABILITY/requirements.json)
führen R02-Report/Windows-/Checkpointbelege und behalten R01 in der Historie;
[Matrix](../../../../PLANUNG/REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md) ergänzt
die beiden Legacy-Replaymethoden. Alle sechs IDs bleiben CLIENT OPEN.

Runtimeports, Thread-/Generation-/Sessionguards, Migration, Rollback, reale APIs
und Nebenwirkungen aus R01 unverändert. Steuerung, Paketindex, Manifest, task.md,
ÜBERGABE.md und Projektübersicht auf R02 nachgeführt; historische Reports unverändert.
Ein Steuerungsmeilenstein pro Log für diesen abgeschlossenen Selbstcheckrun.
Reale Hardware-/ASR-/Crossrepo-/abschließende V2-Buildgates bleiben späteren
beauftragten Paketen zugeordnet; die CI-Buildsmokes ersetzen diese nicht.

CI-01 im Selbstcheck behoben; keine offenen Pflichtfindings bekannt.
Nach grüner finaler CI frische unabhängige Abnahme des gesamten kumulativen AP100,
Schreiben und Pushes auf dem Paketbranch pausieren. Kein eigener ROOT_PASS,
kein AP100-Mergeprompt und kein AP110-Start.
'''
write(RUN/'01_REPORT.md', report)
evidence = '''# Evidenz – AP-CV2-100 / R02-KORREKTUR

**Status:** REVIEW_READY. Selbstchecks, keine unabhängige Eigenabnahme.
Basis ca3cd4009717d508a75ea236aec60881a39fab43 + staged Produktdiff/Gitblobs,
kanonischer Parent dad89bb5d08e6d34abc5cfab57fc76010c5131dc, Server ada13b0.

| Beleg | Erzeugung / Zweck / Ergebnis |
| --- | --- |
| [Startprovenienz](start-provenance.json), [Treiber](record_start.py) | git rev-parse, gh pr view nach fetch/ff-only; aktueller Head/Base, kein Review und vorheriger Status gesichert |
| [CI-Fehlerlog](ci-failed.txt), [Metadaten](ci-failed.json) | gh run view 38342904213 --log-failed / --json; finaler R01-Head, 1573 Tests, 1 ERROR |
| [Baseline](baseline-event-stream.txt), [Repro](replay-deadline-repro.txt), [Treiber](reproduce_ci.py) | Projektvenv; vollständige Befehle/Exits in Logs; 12 PASS vorher, 1 reproduzierbarer FAIL mit 280-ms-Commit |
| [Korrekturtests](corrected-event-stream.txt) | Projektvenv -W error -m unittest tests.test_event_stream -v; 13 PASS einschließlich langsamer dauerhafter Speicherung |
| [Windowsmanifest](windows-validation.json), [Treiber](qualify_windows.py), [exakte Produktdiff](tested-product.patch.base64) | Windows11/Python3.12.10 und Abhängigkeiten, Befehle/Exits/Hashes; 213 Gitblobs, Base+staged Testdiff; PASS |
| [Gezielte Tests](targeted-unittest.txt) | Tatsächlicher vollständiger Befehl im Manifest; 203 PASS, -W error |
| [Windowsvollsuite](windows-full-unittest.txt) | Projektvenv -m unittest discover -s tests -p test_*.py -v; 1574 PASS, keine Skips |
| [Servercheckpoint](server-runtime-checkpoint.json), [stderr](server-runtime-checkpoint.json.stderr.txt) | scripts/check_v2_server_runtime.py mit manifestgebundenem Servercheckout; 17 reale komponierte Client/Serverchecks, 45 Quellen bytegeprüft, PASS |
| [compileall](compileall.txt) | Projektvenv -m compileall -q voice_stt_client scripts tests; Exit0 PASS |
| [Abgabeprüfung](submission-verification.json), [Treiber](verify_submission.py) | 213 staged Gitblobs und Loghashes unverändert, alle neuen/geänderten Markdownlinks und Status/Manifest/Index PASS; tatsächliche PR-Kurzfassung nach Push separat mit read-only-Aktenprüfer prüfen |
| [PR-Vorbereitung](prepare_pr.py) | Externe PR-Beschreibung aus tatsächlichem veröffentlichtem Head/Tree; optionaler CI-Erfolg erst nach SHA-/Ergebnisprüfung |
| [Dokumentationstreiber](complete_records.py) | neue R02-Akte/aktuelle Verweise; abgeschlossene R01-Akte unangetastet |

Alle Qualification-Logs UTF-8 LF vor SHA256 und Versionierung. Konkrete Runtime,
Laufzeiten und Hashes im Manifest, vollständige Tests/Negativdiagnostik in Logs.
CI-Fehlerlog aus gh run view: lediglich Zeilenenden/Zeilenendleerzeichen normalisiert.
CI des endgültig veröffentlichten Heads vor tatsächlicher Reviewübergabe prüfen;
Run/Head/Tree sowie Ergebnis commitgebunden in PR-Beschreibung und Kommentar.
Original-CI-Log und Repro sind erwartete FAIL-Belege, keine aktuellen PASS-Behauptungen.
Keine reale Mikrofon-/Win32-/ASR-Gesamtabnahme, kein eigener ROOT_PASS.
'''
write(EV/'INDEX.md', evidence)
prior_verify = EV.parents[1]/'R01-UMSETZUNG/EVIDENCE/verify_submission.py'
write(EV/'verify_submission.py', prior_verify.read_text(encoding='utf-8'))

for path, link in [(BLOCK/'VERLAUF.md', '30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md'),
                   (ROOT/'ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md', '../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R02-KORREKTUR/01_REPORT.md')]:
    text = path.read_text(encoding='utf-8')
    assert 'AP-CV2-100 / R02-KORREKTUR: CI-01' not in text
    write(path, text+'\n## 2026-10-13 – AP-CV2-100 / R02-KORREKTUR: CI-01\n\nCI-Replaytimeout bei 281-ms-Runnerverzögerung reproduziert; Testfristen für\ndurable Cursor-IO korrigiert, 280-ms-Regressionsfall ergänzt, fachliche Assertions\nerhalten und erweitert. Windows1574/gezielte203/Servercheckpoint17/compileall\nPASS, kandidatgebundene vollständige Logs. [R02-Report]('+link+').\nREVIEW_READY im Selbstcheck; tatsächliche Übergabe erst nach grüner finaler PR-CI.\nKeine Eigenabnahme, kanonische Übernahme oder AP110.\n')
print('R02 records complete')
