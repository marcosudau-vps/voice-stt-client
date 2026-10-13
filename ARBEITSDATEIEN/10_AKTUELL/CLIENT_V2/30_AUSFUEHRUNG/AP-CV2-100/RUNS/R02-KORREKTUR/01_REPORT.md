# AP-CV2-100 / R02-KORREKTUR – CI-01

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
