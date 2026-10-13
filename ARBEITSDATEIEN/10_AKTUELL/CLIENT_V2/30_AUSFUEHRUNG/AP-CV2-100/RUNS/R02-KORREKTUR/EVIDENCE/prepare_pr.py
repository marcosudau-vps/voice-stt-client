"""Prepare external PR body from actual Git identities and optional successful CI."""
from pathlib import Path
import json
import os
import subprocess
import sys

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()
head, tree = git('rev-parse', 'HEAD'), git('rev-parse', 'HEAD^{tree}')
base = 'dad89bb5d08e6d34abc5cfab57fc76010c5131dc'
assert git('rev-parse', 'origin/feat/client-v2') == base
url = 'https://github.com/marcosudau-vps/voice-stt-client/blob/'+head+'/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/'
ci = 'GitHub-CI des finalen Heads wird nach dem Push geprüft; tatsächliche Reviewübergabe erst bei vollständigem Erfolg.'
if len(sys.argv) > 1:
    run = json.loads(subprocess.check_output(['gh','run','view',sys.argv[1],'--json','headSha,conclusion,url'],cwd=ROOT,text=True))
    assert run['headSha'] == head and run['conclusion'] == 'success', run
    ci = '[Finale Windows-CI PASS]('+run['url']+'): vollständige Tests, compileall, EXE-Build/Smoke, sdist/wheel/twine, installierter Wheel-Smoke und Artefaktupload auf diesem Head.'
body = f'''AP-CV2-100 verbindet die V2-Ports zum regulären Desktop-/Headlessprozess: eine Session-/Mirrorautorität für Audio, Settings, Controls, Results, Logs und Feedback. Profilapply koordiniert Qt/Win32-Hotkeys mit atomarer Workerpersistenz und Rollback; Shutdown verarbeitet begonnene Transaktionen vor dem Abmelden der Keys.

**Status:** REVIEW_READY. R02 korrigiert CI-01 vor frischer unabhängiger Abnahme des gesamten Paketdiffs; kein eigener ROOT_PASS.

Der bestehende Cursor-Replaytest überschritt seine 100-ms-Testfrist bei 281 ms Laufzeit auf dem Windows-Runner. R02 verwendet großzügige Phasenfristen und ergänzt denselben Replay-/Dedupfall mit 280 ms Schreibverzögerung. Alle bisherigen Funktionsassertions bleiben erhalten, genau zwei Verbindungen und STOPPED werden zusätzlich geprüft. Produktcode und Produktionstimeouts unverändert.

| Identität | Wert |
| --- | --- |
| Base | feat/client-v2 |
| Kanonischer Parent | {base} |
| Headbranch | work/client-v2/ap-cv2-100 |
| Eingereichter Kandidat | {head} |
| Kandidatentree | {tree} |
| Serverbaseline | ada13b011e1d3829f78e7f389e3b927795a2b3be |

Windows11/Python3.12.10: **1.574 vollständige Tests ohne Skips**, 203 gezielte Tests mit `-W error`, 17 tatsächliche Desktop-/Serverchecks mit 45 bytegeprüften Quellen, compileall/diffcheck und Akten-/Linkprüfung PASS. 213 Produkt-/Test-/Konfigblobs und vollständige Logs kandidatengebunden.

{ci}

[R02-Report]({url}R02-KORREKTUR/01_REPORT.md), [R02-Evidenzindex]({url}R02-KORREKTUR/EVIDENCE/INDEX.md), [Windowsmanifest/Befehle]({url}R02-KORREKTUR/EVIDENCE/windows-validation.json), [vollständiger Windowslog]({url}R02-KORREKTUR/EVIDENCE/windows-full-unittest.txt), [Servercheckpoint]({url}R02-KORREKTUR/EVIDENCE/server-runtime-checkpoint.json), [ursprüngliche vollständige Umsetzung/Requirements/Ports]({url}R01-UMSETZUNG/01_REPORT.md).

PortAudio, Win32registrierung/SendInput, Recorder/ASR/Scheduler und physische Sound-/LEDausgabe sind benannte Testgrenzen. Reale Hardware-/ASRqualifikation und abschließende V2-Buildgates bleiben den späteren Paketen zugeordnet. Nach tatsächlicher Übergabe Paketbranch für den unabhängigen Review pausiert; kein Merge oder AP110 ohne PASS, menschlichen Übernahmeprompt und tatsächlichen kanonischen Abschluss.
'''
output = Path(os.environ['TEMP'])/'voice-stt-client-ap100-r02-pr.md'
output.write_text(body,encoding='utf-8',newline='\n')
print(output)
