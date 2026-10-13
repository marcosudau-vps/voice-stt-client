"""Prepare an exact multiline PR summary without shell interpolation."""
import json
import os
from pathlib import Path
import subprocess

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
def git(ref): return subprocess.check_output(['git','rev-parse',ref],cwd=ROOT,text=True).strip()
head, tree = git('HEAD'), git('HEAD^{tree}')
manifest = json.loads((EV/'windows-validation.json').read_text(encoding='utf-8'))
repo = 'https://github.com/marcosudau-vps/voice-stt-client'
prefix = f'{repo}/blob/{head}/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG'
body = f'''AP-CV2-100 verbindet die bisher getrennt geprüften V2-Ports zum regulären Desktop- und Headlessprozess: eine Session-/Mirrorautorität für Audio, Settings, Controls, Results, Logs und Feedback. Profilapply koordiniert Qt/Win32-Hotkeys mit atomarer Workerpersistenz und Rollback; Shutdown verarbeitet begonnene Transaktionen vor dem Abmelden der Keys.

**Status:** REVIEW_READY. Frischer unabhängiger Review des gesamten Paketdiffs und der Windowsbelege ausstehend; Umsetzungsschreiben nach Übergabe pausiert.

| Identität | Wert |
| --- | --- |
| Base | feat/client-v2 |
| Kanonischer Parent | dad89bb5d08e6d34abc5cfab57fc76010c5131dc |
| Headbranch | work/client-v2/ap-cv2-100 |
| Eingereichter Kandidat | {head} |
| Kandidatentree | {tree} |
| Serverbaseline | ada13b011e1d3829f78e7f389e3b927795a2b3be |

Validierung auf Windows11/Python3.12.10: **1.573 vollständige Tests ohne Skips**,190 gezielte Tests mit `-W error`,17 tatsächliche Desktop-/Serverchecks mit45 bytegeprüften Quellen, compileall/diffcheck und Akten-/Linkprüfung PASS. Git-Blobs und vollständige Logs kandidatengebunden; spätere administrative PR-Verweise verändern den qualifizierten Produktstand nicht.

[Report]({prefix}/01_REPORT.md), [Evidenzindex]({prefix}/EVIDENCE/INDEX.md), [Windowsmanifest und Befehle]({prefix}/EVIDENCE/windows-validation.json), [vollständiger Windowslog]({prefix}/EVIDENCE/windows-full-unittest.txt), [komponierter Servercheckpoint]({prefix}/EVIDENCE/server-runtime-checkpoint.json).

PortAudio, Win32registrierung/SendInput, Recorder/ASR/Scheduler und physische Sound-/LEDausgabe sind benannte Testgrenzen. Reale Hardware-/ASRqualifikation und V2-Buildabschluss bleiben den späteren Paketen zugeordnet. Kein eigener ROOT_PASS oder Merge; AP110 startet erst nach unabhängigem PASS, menschlichem Übernahmeprompt und tatsächlichem kanonischem Abschluss.
'''
path = Path(os.environ['TEMP'])/'voice-stt-client-ap100-pr.md'
path.write_text(body,encoding='utf-8',newline='\n')
print(path)
