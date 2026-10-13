"""External PR body from actual final candidate and optionally verified successful CI."""
from pathlib import Path
import json
import os
import subprocess
import sys

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
def git(*args):
    return subprocess.check_output(['git', *args],cwd=ROOT,text=True).strip()
head, tree = git('rev-parse','HEAD'), git('rev-parse','HEAD^{tree}')
base = 'dad89bb5d08e6d34abc5cfab57fc76010c5131dc'
assert git('rev-parse','origin/feat/client-v2') == base
url = 'https://github.com/marcosudau-vps/voice-stt-client/blob/'+head+'/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/'
ci = 'Finale Windows-CI des veröffentlichten Heads wird noch geprüft; tatsächliche Reviewübergabe erst bei vollständig grünem Ergebnis.'
if len(sys.argv)>1:
    run = json.loads(subprocess.check_output(['gh','run','view',sys.argv[1],'--json','headSha,conclusion,url'],cwd=ROOT,text=True))
    assert run['headSha'] == head and run['conclusion'] == 'success', run
    ci = '[Finale Windows-CI PASS]('+run['url']+'): Vollsuite, compileall, EXE-Build/Smoke, sdist/wheel/twine, installierter Wheel-Smoke und Artefaktupload auf diesem Head.'
body = f'''AP-CV2-100 verbindet die V2-Ports zum regulären Desktop-/Headlessprozess: eine Session-/Mirrorautorität für Audio, Settings, Controls, Results, Logs und Feedback. Profilapply koordiniert Qt/Win32-Hotkeys mit atomarer Workerpersistenz und Rollback; Shutdown verarbeitet begonnene Transaktionen vor dem Abmelden der Keys.

**Status:** REVIEW_READY. R04 korrigiert `CV2-100-R03-F01` im Selbstcheck. Frische unabhängige Abnahme des gesamten kumulativen Pakets mit Fokus F01 erforderlich; kein eigener ROOT_PASS. Der unveränderte R03-CHANGES_REQUIRED-Report bleibt die historische Reviewquelle.

Im tatsächlichen V2-Local-Apply fehlten Started/Runtime/Completed-Audits und ihre gemeinsame settings-ID. R04 stellt diese Kette über den vorhandenen Bridgeport wieder her. Runtimeaudit enthält die drei Änderungsflags und Erfolgs-/Fehlerstatus auch nach Persistenzfehler/Rollback; der idempotente UI-Abschluss verhindert doppelte Events. Sieben neue Tests mit realem V2-Desktop/Bridge/Core und echtem ObservabilityIngress prüfen Overlay/Audio/Logging, Persistenz-/Postsavefehler, Busy/Core-Abweisung, Loggingausfall und Shutdown. Bestehender Serververtrag, Technologien und funktionale Assertions erhalten.

| Identität | Wert |
| --- | --- |
| Base | feat/client-v2 |
| Kanonischer Parent | {base} |
| Headbranch | work/client-v2/ap-cv2-100 |
| Eingereichter Kandidat | {head} |
| Kandidatentree | {tree} |
| Serverbaseline | ada13b011e1d3829f78e7f389e3b927795a2b3be |

Neue Windows11/Python3.12.10-Qualifikation: **1.581 vollständige Tests ohne Skips**, 210 gezielte `-W error` PASS, 17 komponierte tatsächliche Desktop-/Serverchecks mit 45 bytegeprüften Quellen, compileall/diffcheck sowie Akten-/Linkprüfung PASS. 213 Produkt-/Test-/Konfigblobs, vollständige Befehle/Logs und exakte Base+Produktdiff kandidatengebunden. R02-CI-01-Fix erhalten.

{ci}

[R04-Report]({url}R04-KORREKTUR/01_REPORT.md), [R04-Evidenzindex]({url}R04-KORREKTUR/EVIDENCE/INDEX.md), [Windowsmanifest/Befehle]({url}R04-KORREKTUR/EVIDENCE/windows-validation.json), [vollständiger Windowslog]({url}R04-KORREKTUR/EVIDENCE/windows-full-unittest.txt), [Servercheckpoint]({url}R04-KORREKTUR/EVIDENCE/server-runtime-checkpoint.json), [unveränderter R03-Findingreport]({url}R03-ABNAHME/01_REPORT.md), [ursprüngliche gesamte Umsetzung/Requirements/Ports]({url}R01-UMSETZUNG/01_REPORT.md).

PortAudio, Win32registrierung/SendInput, Recorder/ASR/Scheduler und physische Sound-/LEDausgabe sind benannte Testgrenzen. Reale Hardware-/ASRqualifikation und abschließende V2-Buildgates bleiben den späteren Paketen zugeordnet. Nach tatsächlicher Übergabe Paketbranch für unabhängigen Review pausiert; kein Merge/AP110 ohne PASS, menschlichen Übernahmeprompt und tatsächlichen kanonischen Abschluss.
'''
output = Path(os.environ['TEMP'])/'voice-stt-client-ap100-r04-pr.md'
output.write_text(body,encoding='utf-8',newline='\n')
print(output)
