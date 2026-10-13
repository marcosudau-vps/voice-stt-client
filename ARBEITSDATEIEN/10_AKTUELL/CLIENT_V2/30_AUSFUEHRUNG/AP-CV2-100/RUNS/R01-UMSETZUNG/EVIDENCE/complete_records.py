"""AP100 R01 administrative records from actual qualification results."""
import json
import os
from pathlib import Path
import re
import subprocess

EV = Path(__file__).resolve().parent
ROOT = EV.parents[7]
BLOCK = ROOT/'ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2'
RUN = EV.parent
PREFIX = '30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG'
PARENT = 'dad89bb5d08e6d34abc5cfab57fc76010c5131dc'
BRANCH = 'work/client-v2/ap-cv2-100'

def write(path, text):
    path.write_text(text.rstrip()+'\n', encoding='utf-8', newline='\n')
def json_write(path, data): write(path, json.dumps(data, ensure_ascii=False, indent=2))

data = json.loads((EV/'windows-validation.json').read_text(encoding='utf-8'))
assert data['result'] == 'PASS'
counts = {c['log']: c for c in data['checks']}
full = counts['windows-full-unittest.txt']['testCount']
targeted = counts['targeted-unittest.txt']['testCount']
checkpoint = counts['server-runtime-checkpoint.json']['serverCheckCount']
sources = counts['server-runtime-checkpoint.json']['verifiedSourceCount']
assert subprocess.check_output(['git','rev-parse','HEAD'], cwd=ROOT, text=True).strip() == PARENT

methods = {
 'FINAL-01': ['Runtime.test_manual_wake_both_and_null_effective_share_bootstrap', 'Runtime.test_multiple_activations_background_final_and_history_before_paste', 'Runtime.test_two_segments_same_activation_same_text_keep_distinct_results', 'Runtime.test_history_disabled_keeps_terminal_dedup'],
 'FINAL-02': ['QtRuntime.test_actual_bridge_thread_qt_output_and_native_role_dispatch', 'QtRuntime.test_shutdown_during_disk_commit_finishes_and_releases_native_keys', 'Runtime.test_pending_command_disconnect_completes_and_shutdown_joins_workers'],
 'RUNTIME-01': ['Runtime.test_restore_confirmed_before_first_pcm_and_ready_projection', 'Runtime.test_disconnect_at_each_bootstrap_boundary_never_releases_pcm', 'Runtime.test_resync_without_snapshot_remains_guarded_and_bounded'],
 'RUNTIME-02': ['QtRuntime.test_profile_transaction_rebind_persist_and_failure_rollback', 'QtRuntime.test_device_enumeration_on_worker_and_local_config_apply', 'Runtime.test_local_audio_probe_and_persist_failure_roll_back_config', 'scripts/check_v2_server_runtime.py:apply/drain_wait_no_destructive_reconnect'],
 'RUNTIME-03': ['Runtime.test_autostart_after_confirmed_ready_only_once', 'QtRuntime.test_dialog_close_reopen_new_lease_and_shutdown_all_workers', 'QtRuntime.test_shutdown_during_disk_commit_finishes_and_releases_native_keys', 'tests.test_single_instance', 'tests.test_startup_hotkey_persistence'],
 'RUNTIME-04': ['Runtime.test_history_fault_isolated_with_diagnostic_and_controls_survive', 'QtRuntime.test_adapter_failure_keeps_capture_controls_and_results_alive', 'Runtime.test_device_loss_preserves_background_results_and_pause', 'scripts/check_v2_server_runtime.py'],
}
matrix_rows = '\n'.join('| '+rid+' | '+', '.join('`'+m+'`' for m in ms)+' |' for rid, ms in methods.items())
report = f'''# AP-CV2-100 – R01 Umsetzung

**Status:** REVIEW_READY. Stand 2026-10-13; vollständige Selbstqualifikation, unabhängige Abnahme offen.

## Auftrag, Herkunft und Gitumfang

[Originalauftrag](00_PROMPT_ORIGINAL.md). AP100 vollständig vom tatsächlichen
`feat/client-v2`-Parent `{PARENT}` umgesetzt, Kandidatenlinie `{BRANCH}`.
AP090: unabhängiger R02-PASS und menschlicher R03-Prompt geprüft; PR #11 tatsächlich
gemergt, genau ein neuer Single-Parent-Commit und Baumgleichheit zur finalen Spitze
[belegt](EVIDENCE/predecessor-canonicalization.json). Server unverändert
`ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Planversion/Hashs [gesichert](EVIDENCE/input-provenance.json).

Gitfreigabe: workflowweiter Originalprompt AP000 erlaubt Kandidatencommit,
normalen Paketbranch-Push und Paket-PR samt Übergabe gegen feat/client-v2.
Keine AP100-Übernahmefreigabe. Finalen eingereichten Head/Tree aus PR/Git ableiten;
der Report schreibt keinen unmöglichen eigenen Commit-SHA voraus.
Der getestete Stand ist exakt Parent plus [staged Produktdiff](EVIDENCE/tested-product.patch.base64),
SHA256 und sämtliche qualifizierten Gitblobs im [Windowsmanifest](EVIDENCE/windows-validation.json).
Spätere Unterlagennachträge verändern keinen Produkt-/Testblob.

## Ergebnis, Schnittstellen und Entscheidungen

Regulärer GUI-/Headless-Start verwendet die gemeinsame `V2Runtime`. Neue Module
`core/v2_runtime.py`, `ui/v2_core_bridge.py`, `ui/v2_application.py` komponieren die
bereits abgenommenen Komponenten über die bestehende Desktop-/Threadhülle.
Die vorgeschlagenen Legacy-Controller-/STTSessiondateien bleiben unverändert;
eine zweite Zustandsmaschine oder Lifecycleautorität wurde nicht übernommen.
Die Auswahl in app.py/run_gui und Raw-Migrationswerte in AppConfig sind nötige
gemeinsame Anschlussänderungen. Legacyproduktabbau bleibt AP110.

Öffentliche Runtime-/Bridge-/UIports, Callbackreihenfolge, Sideeffects, Guards und
Migration sind vollständig in [Produktarchitektur](../../../../../../../docs/protocol-v2-runtime.md)
beschrieben. Controls/Results → Runtimeview → Feedback ist die Reductionsreihenfolge;
Qt bekommt immutable Runtime-/Mirror-/Feedbackansichten. Physical impulses werden
bereits beim Queuen an ihre veröffentlichte Generation/Session/Activation gebunden.
HTTP, Media, Commands und Logs behalten ihre vorhandenen Bindingguards.
Results reserviert Domainfinals, schreibt History und queued anschließend Paste;
Interim und Logreplay sind kein Injektionspfad. Reinsert ist ein eigener Versuch.

Profilapply registriert Rollenkeys im Qtthread, schreibt auf einem Worker atomar
und übernimmt oder rollt zurück. SettingsUISession unterstützt dafür async
Persistenzports. Auch Schließen während Diskcommit lässt Persistenz/Adoption
zusammen abschließen. Shutdown verarbeitet Qt-Replies und meldet Keys danach ab.
Geräteenumeration im lokalen Dialog erfolgt auf einem Worker. Audioapply sperrt
PCM und meldet unavailable vor Stop/Probe; Fehlschlag stellt lokale Konfiguration
wieder her. Runtimefehler von History/Sound/LED sind sekundäre Diagnosen.

`/ws/transcribe` wird origin-treu nach `/ws/v2` ohne Legacyquery migriert.
Migration benutzt tatsächlich geladene Benutzerwerte, bytegleiches Originalbackup
und die vorhandene atomare AppConfig-Persistenz. Keine Laufzeitpausen/Tokens/IDs
werden gespeichert. Konfig-/Datenmigration und Startanleitung stehen in der
[Kompatibilität](../../../../../../../docs/compatibility.md).

## Anforderungen einzeln

Methoden mit Runtime/QtRuntime gehören `tests.test_v2_runtime_integration`.
Alle sechs IDs bleiben CLIENT OPEN bis unabhängiger Abnahme. Die hier angegebenen
Ergebnisse sind SELF_CHECK_PASS_REVIEW_READY, kein eigenes ROOT_PASS.

| ID | Tatsächlicher Nachweis |
| --- | --- |
{matrix_rows}

Für alle Zeilen: [gezielte vollständige Logs](EVIDENCE/targeted-unittest.txt),
[Windowsvollsuite](EVIDENCE/windows-full-unittest.txt) und
[komponierter Servercheckpoint](EVIDENCE/server-runtime-checkpoint.json).
Requirements-JSON und Matrix enthalten denselben individuellen Methoden-/Runbezug.

## Qualifikation und Fehleriteration

Baseline vor Produktänderung: 1552 Windows-Tests, Exit0, keine Skips,177.130s.
Endstand: **{full} Windows-Tests**, **{targeted} gezielte Tests** mit `-W error`,
**{checkpoint} echte Serverchecks** und **{sources} bytegeprüfte Serverquellen** PASS.
compileall und staged/unstaged diffcheck PASS. Python3.12.10 auf Windows11;
vollständige Befehle, Runtime/Dependencies, Dauer, Exitcodes und Loghashs im
Windowsmanifest. {full-1552} neue Integrationstests; keine entfernten/geskippten
V2-Assertions. Ein bestehender Test mocked jetzt die tatsächliche V2-Desktopfactory;
sein Construction-failure-/Mutexfreigabevertrag bleibt identisch.

Die ersten Negativtests fanden snapshotlose diagnostische Entscheidungen,
Gerätelisten-/Einzelgeräteformen, Enum-/Stringfeedback und eine No-effect-Testregel.
Mocks/Assertions wurden am tatsächlichen Vertrag korrigiert; lokale Fehler werden
nun als eigene Kategorien zurückgeführt. Neue Persistenz-/Shutdowntests schützten
die Transaktion vor vorzeitigem Abmelden/Rollback der Keys. Ein Qualifikationsaufruf
nannte zwei nicht vorhandene Testmodule; die gültigen vorhandenen Module wurden
ermittelt und der Lauf vollständig wiederholt. Alle Zwischenlogs bleiben im
[Evidenzindex](EVIDENCE/INDEX.md) als frühere FAIL/diagnostische Belege erhalten.

Servercheckpoint: tatsächliche QApplication/V2DesktopApplication/V2CoreBridge
mit separatem Corethread, unveränderter FastAPI-App, echten HTTP/Domain-/Log-WS
und temporärer SQLite. Restore vor Capture, manueller Lifecycle, Hintergrundfinal,
Drain-wait vor Triggerreconnect, Workerpersistenz, Reinsertion, Qtthread und
Shutdown bestanden. Benannte Grenzen: PortAudio-/Win32registrierung-/SendInput,
GateAwareRecorder/ManualScheduler/ASR und physische Sound-/LEDausgabe.

## Grenzen und Übergabe

Kein offenes Paketpflichtkriterium aus Selbstprüfung; frischer unabhängiger Review
steht aus. AP110, IV2-010 und reale Hardware-/ASR-/Wahrnehmungsqualifikation IV2-020
bleiben PLANNED/offen. Keine Serveränderung, kein Live-Prod-Schreibzugriff.
UI-Corejoin10s, Komponentenclose jeweils7s, Clipboardjoin2s. Nicht abbrechbare
native Betriebssystemcalls sind keine behauptete erfolgreiche OS-Terminierung;
Timeout wird gemeldet und die Media-Cleanupgrenzen bleiben sichtbar.

REVIEW_READY-Übergabe: vollständigen kumulativen Kandidaten gegen `{PARENT}` prüfen,
Windowsbelege commitgebunden validieren, neue unabhängige Reviewakte auf pausiertem
Paketbranch. Keine Pflicht, die Windowsvollsuite routinemäßig erneut auszuführen.
Keine eigene kanonische Übernahme und kein automatischer AP110-Start.
'''
write(RUN/'01_REPORT.md', report)
write(RUN.parent.parent/'00_PAKET.md', f'''# AP-CV2-100 – Paketakte

**Status:** REVIEW_READY. Stand 2026-10-13. Unabhängige Abnahme offen.

Parent `{PARENT}`, Branch `{BRANCH}`, Server `ada13b0`.
Getesteter Kandidat: Parent plus genaue Produktdiff-/Gitblobbindung im Windowsmanifest;
finaler Head/Tree extern in der PR-Beschreibung. Workingtree nach Abgabe sauber,
Umsetzungsschreiben dann pausiert. Kein eigener ROOT_PASS oder menschlicher AP100-Mergeprompt.

[Paketvertrag](../../PLANUNG/ARBEITSPAKETE/AP-CV2-100.md),
[Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md),
[Report](RUNS/R01-UMSETZUNG/01_REPORT.md),
[Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md),
[Workflowstatus](../../WORKFLOW_STATUS.json).

AP090 tatsächlich ACCEPTED über PR #11; Single-Parent-/Baumgleichheit sowie PASS und
menschliche Freigabe [gesichert](RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json).
''')
write(EV/'INDEX.md', f'''# AP100 R01 – Evidenzindex

Windows11/Python3.12.10, Projektvenv, Qt offscreen. Testsynthese enthält ausschließlich
kontrollierten Text/PCM, keine Nutzeraufnahme, Secrets oder persistierte Laufzeitdaten.
Getesteter Parent `{PARENT}`, Kandidatenbranch `{BRANCH}`, Server `ada13b0`.

| Beleg | Erzeugung / Ergebnis |
| --- | --- |
| [Original-/Planherkunft](input-provenance.json), [Startskript](record_start.py) | Paketvertrag/Requirements/K04-Hash, kanonischer Parent und Branch, tatsächliche AP090-Promotion PASS |
| [Vorgänger](predecessor-canonicalization.json) | gh pr view11 und git Parent/Commitcount/tree; PASS |
| [Baseline](baseline-windows.txt) | Projektvenv unittest discover -s tests -p test_*.py -v, vor Produktänderung1552 PASS, Exit0 |
| [Manifest](windows-validation.json), [Erzeugung](qualify_windows.py) | vollständige Commands, Runtime/Dependencyidentität, Zeit, Exitcode, Zahlen, Log-SHA256 und qualifizierte Gitblobs; PASS |
| [Exakter Produktdiff](tested-product.patch.base64) | git diff --cached --binary --unified=0 HEAD -- voice_stt_client tests scripts; base64, Diff-/Artefakthash im Manifest |
| [Gezielte Tests](targeted-unittest.txt) | -W error unittest tatsächlicher Runtime-/UI-/Config-/SingleInstance-/Hotkey-/OBSmodule; {targeted} PASS |
| [Servercheckpoint](server-runtime-checkpoint.json), [stderr](server-runtime-checkpoint.json.stderr.txt) | scripts/check_v2_server_runtime.py mit gepinntem Export und Serverrepo; {checkpoint} PASS, {sources} bytegeprüfte Quellen |
| [compileall](compileall.txt) | -m compileall -q voice_stt_client scripts tests; Exit0 PASS, leerer Log ist erwarteter q-Modus |
| [Windowsvollsuite](windows-full-unittest.txt) | unittest discover -s tests -p test_*.py -v; {full} PASS, keine Pflichtskips |
| [Erste Regression](initial-regression.txt) | vorhandene SettingsUI/CoreBridge/Application,81 PASS |
| [Erste Integration](runtime-first.txt) | früher Kandidat:16 Tests,3FAIL/1ERROR; snapshotlose Logdecision, Gerätefake und Feedbackgrenze, korrigiert |
| [Zweite Iteration](runtime-second.txt) | früher Kandidat:16 Tests,4FAIL/14ERROR; falscher Enumimport/ungültiges Fixture-LEDverb, korrigiert |
| [Dritte Iteration](runtime-third.txt) | früher Kandidat:16 Tests,1FAIL; No-effect-Stateled im Impulsfixture, korrigiert |
| [Vierte Iteration](runtime-fourth.txt) | Zwischenstand16 PASS |
| [Erweiterte Regression](runtime-expanded.txt) |21 neue plus81 vorhandene Tests,102 PASS |
| [Früher Servercheckpoint](checkpoint-first.txt) | komponierter Desktop-/Serverfluss PASS am früheren Produktstand; Endbeleg siehe Manifest |
| [Falscher Modulaufruf](qualification-command-error.txt) |187 Tests inkl.2 Ladefehler für nicht vorhandene Testmodule; Aufruf korrigiert, alle gültigen Tests im Endlauf PASS |

Die finalen Qualificationlogs sind UTF8/LF und per SHA256 im Manifest gesichert.
Zwischenlogs sind datierte Diagnosebelege am früheren Stand, keine Endqualifikation.
Administrative Aktenprüfung und tatsächliche PR-/Head-/Treebindung werden vor Abgabe
zusätzlich gesichert; finale Kandidatenblobs müssen mit dem Manifest übereinstimmen.
''')

manifest_path = BLOCK/'PLANUNG/EVIDENCE/package-manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
for package in manifest['packages']:
    if package['id'] == 'AP-CV2-090':
        package.update(status='ACCEPTED', canonicalCommit=PARENT,
            canonicalTree='e659af24f20d5e9f6bf0213db7df005d8bc01137',
            canonicalizationEvidence=PREFIX+'/EVIDENCE/predecessor-canonicalization.json')
    if package['id'] == 'AP-CV2-100':
        package.update(status='REVIEW_READY', candidateBranch=BRANCH, canonicalParent=PARENT,
            executionReport=PREFIX+'/01_REPORT.md', windowsValidation=PREFIX+'/EVIDENCE/windows-validation.json',
            checkpointEvidence=PREFIX+'/EVIDENCE/server-runtime-checkpoint.json',
            openFindingIds=[], reviewReport=None, humanApproval=None, pullRequest=None)
json_write(manifest_path, manifest)
req_path = BLOCK/'PLANUNG/REFERENZ/TRACEABILITY/requirements.json'
requirements = json.loads(req_path.read_text(encoding='utf-8'))
for req in requirements['requirements']:
    if req['ap'] == 'AP-CV2-090':
        req.update(status='ACCEPTED', canonicalizationEvidence=PREFIX+'/EVIDENCE/predecessor-canonicalization.json')
    if req['id'] in methods:
        req['implementationEvidence'] = dict(state='SELF_CHECK_PASS_REVIEW_READY', candidateRef=BRANCH,
            canonicalParent=PARENT, run='R01-UMSETZUNG', report=PREFIX+'/01_REPORT.md',
            methods=[m if m.startswith(('scripts/', 'tests.')) else 'tests.test_v2_runtime_integration.'+m for m in methods[req['id']]],
            windowsValidation=PREFIX+'/EVIDENCE/windows-validation.json', checkpointEvidence=PREFIX+'/EVIDENCE/server-runtime-checkpoint.json')
json_write(req_path, requirements)
matrix_path = BLOCK/'PLANUNG/REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md'
matrix = matrix_path.read_text(encoding='utf-8')
matrix = '\n'.join(line.replace('| ROOT_PASS |', '| ACCEPTED |') if '[AP-CV2-090]' in line else line for line in matrix.splitlines())
matrix += f'''\n\n## AP-CV2-100 – Umsetzung R01, 2026-10-13

Alle sechs IDs bleiben CLIENT OPEN. Selbstchecks REVIEW_READY auf `{BRANCH}`,
Parent `{PARENT}`. [Report](../../../{PREFIX}/01_REPORT.md),
[Windows-/Kandidatenbindung](../../../{PREFIX}/EVIDENCE/windows-validation.json),
[Servercheckpoint](../../../{PREFIX}/EVIDENCE/server-runtime-checkpoint.json).
Methoden in Runtime/QtRuntime gehören tests.test_v2_runtime_integration.

| ID | Tatsächlich ausgeführte Methode/Fall |
| --- | --- |
{matrix_rows}

AP090 durch tatsächlichen Squash ACCEPTED; [Git-/PR-Provenienz](../../../{PREFIX}/EVIDENCE/predecessor-canonicalization.json).
Historische Reviews bleiben unverändert.
'''
write(matrix_path, matrix)
for ap, status in (('090','ACCEPTED'), ('100','REVIEW_READY')):
    path = BLOCK/f'PLANUNG/ARBEITSPAKETE/AP-CV2-{ap}.md'
    value = path.read_text(encoding='utf-8')
    value = re.sub(r'\*\*Status:\*\* [^.]+\.', '**Status:** '+status+'.', value, count=1)
    value += f'\n\n## Aktueller R01-Nachweis AP100, 2026-10-13\n\n[Report](../../{PREFIX}/01_REPORT.md), [Evidenz](../../{PREFIX}/EVIDENCE/INDEX.md). '+('AP090 tatsächlich kanonisch übernommen; historische Reviewakten erhalten.' if ap=='090' else 'Vollständige Selbstchecks bestanden, unabhängige Abnahme offen; Produktinterfaces in docs/protocol-v2-runtime.md.')+'\n'
    if ap == '100':
        value = value.replace('- [ ]', '- [x]')
    write(path, value)
previous_index = BLOCK/'30_AUSFUEHRUNG/AP-CV2-090/00_PAKET.md'
old = previous_index.read_text(encoding='utf-8')
old = re.sub(r'\*\*Status:\*\*[^\n]+', '**Status:** ACCEPTED. Tatsächlich über PR #11 auf dad89bb übernommen; nachgewiesen im AP100-R01-Start.', old, count=1)
write(previous_index, old+f'\n\n## Kanonischer Abschluss, im AP100-Start gesichert\n\n[Git-/PR-Nachweis](../AP-CV2-100/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json): Single-Parent `{PARENT}`, Ergebnisbaum e659af24, finaler PR-Head68c3b3b0. Vorherige R03-/PR-offen-Angaben oben sind vor dem tatsächlichen Merge entstanden.\n')
workflow_path = BLOCK/'WORKFLOW_STATUS.json'
workflow = json.loads(workflow_path.read_text(encoding='utf-8'))
workflow.update(workflowPhase='REVIEW_READY', packageStatus='REVIEW_READY', writeOwner=None,
    nextAction='Frische unabhängige Abnahme des vollständigen AP100-Kandidaten samt Windowsbelegen; kein Merge/AP110 ohne PASS und menschlichen Prompt.')
json_write(workflow_path, workflow)

for path in [ROOT/'task.md', ROOT/'ÜBERGABE.md', ROOT/'docs/PROJEKTUEBERSICHT.md',
        ROOT/'ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md', ROOT/'ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md',
        BLOCK/'README.md', BLOCK/'STATUS.md', BLOCK/'PLANUNG/README.md']:
    relative = lambda target: os.path.relpath(target, path.parent).replace('\\','/')
    head = f'''# Client V2 – AP-CV2-100 / R01 / REVIEW_READY, 2026-10-13

Aktiver Block CLIENT_V2. AP000 bis AP090 tatsächlich ACCEPTED, zuletzt `{PARENT}`
über PR #11; unabhängiger PASS, menschlicher Prompt und Git-/PR-Provenienz
[gesichert]({relative(EV/'predecessor-canonicalization.json')}). AP100 vollständig
selbstqualifiziert auf `{BRANCH}`; unabhängige Abnahme offen.

Tatsächlicher V2-Desktop-/Headlessprozess mit gemeinsamem Mirror, Settingsbootstrap,
Media, Controls, Results, Logs und Feedback. Qt-/Core-/Audio-/Clipboard-/LEDworkers
getrennt, profilgebundene Workerpersistenz/Hotkeyrollback und Shutdown getestet.
{full} Windows-/ {targeted} gezielte Tests und {checkpoint} komponierte Serverchecks
an {sources} bytegeprüften ada13b0-Quellen PASS; compileall/diffcheck PASS.

[Paketakte]({relative(RUN.parent.parent/'00_PAKET.md')}), [Report]({relative(RUN/'01_REPORT.md')}),
[Evidenz]({relative(EV/'INDEX.md')}), [Workflowstatus]({relative(BLOCK/'WORKFLOW_STATUS.json')}),
[Planung]({relative(BLOCK/'PLANUNG/README.md')}), [Runtimeinterfaces]({relative(ROOT/'docs/protocol-v2-runtime.md')}).
Start `.\\venv\\Scripts\\python.exe -m voice_stt_client`; Headless `--headless`.

Nächste Aktion: vollständigen kumulativen Kandidaten unabhängig prüfen; Branch ab
Abgabe pausiert. Kein eigener ROOT_PASS, kein AP100-Mergeprompt, kein AP110-Start.
Server-Distributed sowie Build-/Crossrepo-/Hardware-/ASRgates bleiben offen.
'''
    old = path.read_text(encoding='utf-8')
    marker = '## Historischer Stand vor AP-CV2-020'
    tail = marker+old.split(marker,1)[1] if marker in old else '## Historischer Stand vor AP100\n\n'+old
    write(path, head+'\n'+tail)

milestone = f'''\n\n## AP-CV2-100-R01 – 2026-10-13 – Desktopkomposition / REVIEW_READY

Vom kanonischen AP090-Parent dad89bb nach belegtem unabhängigen PASS, menschlichem
Prompt und Single-Parent-/Baumgleichheit. Gemeinsamer V2-Desktop-/Core-/Media-/Settings-/
Result-/Feedbackfluss, Workerpersistenz und kontrollierter Rollback/Shutdown.
{full} Windows-/ {targeted} gezielte Tests, {checkpoint} echte komponierte Serverchecks,
compileall/diffcheck PASS. Unabhängige Abnahme offen, Umsetzungsschreiben ab Abgabe
pausiert; keine kanonische Übernahme oder AP110-Implementierung.
'''
for path in [BLOCK/'VERLAUF.md', ROOT/'ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md']:
    relative_report = os.path.relpath(RUN/'01_REPORT.md', path.parent).replace('\\','/')
    write(path, path.read_text(encoding='utf-8')+milestone+f'\n[Runreport]({relative_report}).\n')

compat = ROOT/'docs/compatibility.md'
write(compat, '''# Aktueller V2-Start und Migration – AP-CV2-100, 2026-10-13

GUI und Headless starten dieselbe V2Runtime. Bekannte `/ws/transcribe`-URLs werden
am gleichen Origin nach `/ws/v2` migriert; Profilwünsche kommen aus tatsächlichen
Benutzerwerten. Nach erfolgreichem Bootstrap Originalbackup `.pre-v2.bak` und
atomarer V2-Profilwrite auf Worker, keine gespeicherten Runpausen/Tokens.
Lokale Präferenzen und Historymigration bleiben erhalten. V1-Klassen bleiben noch
für Migration/Regression; finaler Legacyabbau und Build AP110 offen.
[Architektur, öffentliche Ports, Startbefehle und Grenzen](protocol-v2-runtime.md).

## Historische Ergänzungen vor AP100

'''+compat.read_text(encoding='utf-8'))
readme = ROOT/'README.md'
old = readme.read_text(encoding='utf-8')
start = old.index('AP-CV2-000 bis AP-CV2-020')
end = old.index('Die folgende Bestandsbeschreibung')
new = f'''AP-CV2-000 bis AP-CV2-090 sind tatsächlich übernommen. AP-CV2-100 ist REVIEW_READY:
der reguläre Desktop-/Headlessstart komponiert die V2-Runtime samt Mirror, Media,
Settings, Controls, Results, Logs und Feedback. {full} Windows-Tests und
{checkpoint} komponierte Serverchecks PASS. [Runtime und Start](docs/protocol-v2-runtime.md),
[Kompatibilität](docs/compatibility.md),
[Umsetzungsreport](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/{PREFIX}/01_REPORT.md). Unabhängige Abnahme offen.

V2-Bedienung: Primary aktiviert im Idle bei effektivem Manualtrigger; während
offener Eingabe wirkt die konfigurierte Rolle. Secondary und Wakepause bleiben
auch in Wake-only-Sessions registriert. Settingsapply bietet cancel/finish/defer
und getrenntes wait/discard für Hintergrunddrain. Fachliche Phasen sind quellenneutral.

'''
write(readme, old[:start]+new+old[end:])
for name in ['docs/protocol-v2-settings-ui.md', 'docs/protocol-v2-feedback.md']:
    path = ROOT/name
    write(path, '# Appanschluss AP100, 2026-10-13\n\nReguläre Runtimeverdrahtung jetzt umgesetzt; [tatsächliche Appports und Thread-/Persistenzregeln](protocol-v2-runtime.md). Frühere AP100-offen-Angaben unten sind historischer Stand des jeweiligen Pakets.\n\n'+path.read_text(encoding='utf-8'))
follow = BLOCK/'PLANUNG/ARBEITSPAKETE/AP-CV2-110.md'
write(follow, follow.read_text(encoding='utf-8')+'\n\n## AP100-Anschluss, 2026-10-13\n\nTatsächliche Runtime-/Bridge-/Startports und Migrationsgrenzen: [Produktvertrag](../../../../../docs/protocol-v2-runtime.md). AP100 REVIEW_READY, unabhängige Abnahme/kanonische Übernahme noch offen; AP110 bleibt PLANNED.\n')
print('AP100 administrative records generated from verified qualification')
