# AP-CV2-060 / R01-UMSETZUNG – Umsetzungsreport

## Auftrag und Identität

[Tatsächlicher Originalprompt](00_PROMPT_ORIGINAL.md). Ausdrücklicher Auftrag AP060 ab aktuellem feat/client-v2; Rolle Umsetzung nach next-step-Skill. Paketbranch work/client-v2/ap-cv2-060; canonical_parent `ce95c66a7a3b4440faaa33289351871a040ebe19`, Starttree `67ab9a25ad32b82567785304ee684f8c78d6d175`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Checkout P:/GithubRepos/marcosudau-vps/voice-stt-client/workspaces/client-v2. Startworkingtree sauber, keine fremde WIP. [Vertragshashes vor Änderungen](EVIDENCE/start-contract-hashes.json). Fachliche Kriterien/Quellhierarchie/Owner unverändert.

Vorgänger: [R02-PASS](../../../AP-CV2-050/RUNS/R02-ABNAHME/01_REPORT.md), tatsächlich erteilter menschlicher Prompt im Aggregatecommit, gemergter PR7 und Singleparent/Commitzahl/Baumgleichheit [separat nachgewiesen](EVIDENCE/predecessor-canonicalization.json). Workflowweite Kandidatencommit-/Push-/PR-Rechte stammen aus [AP000-Originalauftrag](../../../AP-CV2-000/RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md). Kein AP060-Übernahmeprompt vorhanden.

Getesteter Kandidat nach CI-Selbstkorrektur: getestete Gitbasis `66f44e0be1ec9485d90ec0b918bffafdab2d57f0` plus exakter staged Testdiff, SHA256 `0182f685c645520c6ad2f2194276a720970587bbf45d146dedce2e3d62e389f6`, [Base64-Patch](EVIDENCE/tested-product.patch.base64); vollständiger Produkt-/Testbestand mit 195 Gitblobs und Runtimebytes im [aktuellen Windowsmanifest](EVIDENCE/windows-validation.json). Der kanonische Paketparent bleibt ce95c66; der frühere unveränderte Produktstand und seine Qualifikation sind als before-ci-fix-Belege erhalten. Die endgültige Spitze wird nach Aktencommit in PR/Übergabe aus Git genannt.

## Ergebnis und lokale Entscheidungen

Status **REVIEW_READY** / SELF_CHECK_PASS. V2ResultService verarbeitet die stabilen Finalrefs aus dem autoritativen Mirror, dedupliziert unabhängig von History, schützt ersten Terminalzustand und stellt Jobs in Serverpublikationsfolge zu. Snapshotlisten und Logs erzeugen keine Ausgabe. Alter Final A bleibt A zugeordnet, während B aufnimmt; gleicher Text zweier Segmente erzeugt zwei getrennte Ausgaben.

Historyschema2 erhält V1-IDs/Integer-API/Timestamps/Attempts, erweitert TEXT-Segmentidentität um Protokoll/Activation/Sequences/Event-/Quellenrefs und bewahrt Unique/FK/Cascade. Vor Migration wird SQLite-Backup erstellt, DDL transaktional ausgeführt; Fehler rollbacken. V1-Herkunft bleibt protocol1 mit NULL-Erweiterungen. Ein neuerer unbekannter Schemazähler bleibt unverändert.

Queue reserviert PENDING vor Clipboard/SendInput und finalisiert denselben Attempt; nach Prozessabbruch unknown, kein automatischer Replay. Bewusstes Reinsert nutzt einen neuen source=manual-Versuch. Persistenzpräferenzen bleiben erhalten: bei deaktivierter/gefilterter History prozesslokale Reservierung; bei notwendiger und defekter Persistenz keine Ausgabe. Pendingversuche bleiben bis Abschluss von Retention ausgenommen; bewusste Löschung wird nicht rückgängig gemacht. Vorhandene Clipboardmechanik bleibt unverändert.

Öffentliche Funktionen/Datentypen, Callbackreihenfolge, Threads, Guards, Sideeffects, Datenmigration, Fehlercodes und Folgepaketgrenzen: [Produkt-API](../../../../../../../docs/protocol-v2-results.md). attach_v2_results genau einmal vor Admission; Resultcallbacks im Core, Attemptcallbacks im Worker, keine garantierte Gesamtordnung zwischen den Threads. Controllerpublicresult enthält Generation und Finalrefs; allgemeine Feedback-/Observabilitykomposition bleibt AP090/100. Schließen sperrt neue Reductions, akzeptierte Queuejobs drainen.

Kleine Anschlussänderungen: reinsertion delegiert an reserviertes enqueue_manual und erhält Legacy-Testdoublefallback; Controller besitzt expliziten V2-Anschluss und Shutdownguard. Keine Config-/Credential-/Technologieänderung, kein Serverfix. Keine V1-Testassertion entfernt.

## Requirements, DoD und Prüfung

Alle RESULT-01 bis RESULT-13 einzeln mit tatsächlichen Methoden und Serverchecknamen in [Requirementabdeckung](EVIDENCE/requirement-coverage.md); Matrix/Requirements konsistent. CLIENT-Abnahmestatus bleibt OPEN. Alle Paketakzeptanzkriterien und DoD als Selbstchecks erfüllt, kein eigenes unabhängiges Urteil.

| Prüfung | Ergebnis | Beleg |
| --- | --- | --- |
| Vorher-Baseline | 212 PASS, vor erster Codeänderung | [vollständiger Log](EVIDENCE/baseline.txt) |
| Gezielte Regression, -W error | 323 PASS | [Log](EVIDENCE/targeted-unittest.txt) |
| Vollständige Windows-Clientsuite | 1426 PASS, keine Skips | [Log](EVIDENCE/windows-full-unittest.txt) |
| Gepinnter echter Server-/Clientcheckpoint | 19 PASS, 46 Serverquellen unverändert | [JSON](EVIDENCE/server-results-checkpoint.json), [stderr](EVIDENCE/server-results-checkpoint.json.stderr.txt) |
| compileall | Exit0 PASS | [vollständiger leerer Log](EVIDENCE/compileall.txt) |
| staged/unstaged git diff --check | PASS | [Manifest](EVIDENCE/windows-validation.json) |

Runtime: Windows11 Build26300, Projekt-Python3.12.10; genaue Abhängigkeiten, UTC-Zeiten, Befehle, Exitcodes, Laufzeiten und Log-SHA256 im Manifest. Qt offscreen. Runner [qualify_windows.py](EVIDENCE/qualify_windows.py). 29 neue Tests enthalten reale SQLite-V1fixtures, Backup-/DDLrollback, idempotenten zweiten Start, Unique/FK, Historyoff, Rotation, Concurrentdelivery, gap-/snapshot-/generationguards, Isolierung von Clipboard-/DB-/Callbackfehlern, bewusste Löschung sowie fünf wirkliche os._exit-Kindprozessabbrüche vor/nach Reservierung, am Paste, nach Paste/vor Statuscommit und nach Commit.

Checkpoint: produktiver gepinnter Server über uvicorn/loopback TCP/WebSocket bis realem V2STTSession/V2MirrorConnection/V2ControlService/V2ResultService/SQLite/Injectionworker. GateAwareRecorder/ManualScheduler ersetzen Recorderhardware und Inferenz. Benannter ClipboardAdapter ersetzt native Clipboard/SendInput; er prüft durable pending vor Paste, Restore und manuelles Reinsert. Reale fremde Windowsanwendung/Mikrofon/ASR/Fokus NOT_RUN in diesem Paket, zugeordnetes Realgate AP-IV2-020. Laufende Appkomposition bleibt AP100. Keine reale Gesamtabnahme behauptet.

## Iterative Befunde und Einordnung

Kein offener Pflichtbefund aus Selbstchecks. Initiale neue Fixtures hatten Windows-SQLitelocks und deaktiviertes Restore; Fixtures gezielt korrigiert. Der Idempotenztest zeigte eine unnötige erneute user_version-Schreiboperation: Schema wird nur bei Versionswechsel geschrieben. Gen-/Sessiontest zeigte, dass ein fremdes altes Reductionobjekt die aktuelle Generation sperren konnte; Identitätsabweichung wird vor Lostgenerationmarkierung verworfen.

Der erste Serverharness versuchte zwei gleichzeitig ungelieferte ASRjobs am geteilten GateAwareRecorderkontext; dieser Testadapter unterstützt das nicht. Der fachlich erforderliche Ablauf liefert A bei laufender B-Aufnahme und ist im finalen echten Pfad belegt. Erwartete CancelledError beim Transportshutdown wird im Harness per gather eingesammelt. Keine Serveränderung oder unbewiesene Serverfehlermeldung.

Erster vollständiger Qualifikationslauf TIMEOUT nach 300s am bestehenden Audio-Recoveryfall, ohne Testfailure; [vollständiger Log](EVIDENCE/windows-full-unittest.txt.first-timeout.txt), [Manifest](EVIDENCE/windows-validation.json.first-timeout.txt) erhalten. Unveränderter Kandidat mit 900s-Runnerfenster vollständig grün; der betreffende Fall zusätzlich einzeln PASS. Der spätere volle Lauf ist der maßgebliche Pflichtbeleg. Weitere iterative Diagnoseausgaben sind historische Arbeitsbelege, kein finaler PASS. Bestehende Negativpfadmeldungen/ResourceWarnings der Gesamtsuite sind im Log sichtbar; die gezielte suite mit -W error besteht.

## Abgabe und Wiedereinstieg

Workflow IMPLEMENTATION_IN_PROGRESS → REVIEW_READY; Status/Manifest/Paketkopf/Index synchronisiert, Originalprompt und vollständige Belege veröffentlicht. [Evidenzindex](EVIDENCE/INDEX.md). Aktenlinks und Produkt-/Logbindung werden in [Abgabeverifikation](EVIDENCE/submission-validation.json) geprüft. Meilenstein AP-CV2-060-R01 im zentralen LOG_VERLAUF genau einmal.

Unmittelbar nächste erlaubte Aktion: unabhängige Abnahme des vollständigen eingereichten Kandidaten gegen canonical_parent. Schreiben/Pushes ab endgültiger Übergabe pausiert, writeOwner=null. Kein eigener ROOT_PASS, keine AP060-Promotion, kein AP070-Start. PR wird gegen feat/client-v2 bereitgestellt und mit tatsächlicher finaler SHA/Tree übergeben. Arbeitsfreigabe und spätere menschliche Übernahmefreigabe bleiben getrennt.


Der exakte Produktpatch wird verlustfrei als Base64 transportiert, weil enthaltene entfernte Legacyzeilen nachgestellte Leerzeichen besitzen. productDiffSha256 bezieht sich auf decodierte Patchbytes, productDiffArtifactSha256 auf das veröffentlichte Artefakt. Decode: `base64.decodebytes(Path(artifact).read_bytes())`; keine getestete Quelle wurde verändert.


[PR #8](https://github.com/marcosudau-vps/voice-stt-client/pull/8) gegen feat/client-v2. Früherer vor CI-Selbstkorrektur qualifizierter Umsetzungscommit `66b6e39daa86855ae1314025bc06344eb55f7d39`, Tree `fbe3931c3b68efa510bee1e35db4b77ad7a83f27`. Nachfolgende Veröffentlichungsverweise sind rein administrativ; endgültige eingereichte SHA/Tree stehen in aktueller PR-Beschreibung und finaler Übergabe.


## CI-Selbstkorrektur vor endgültiger Abgabe

CI38267770763 auf dem vorläufigen Kandidaten66f44e0 meldete genau eine Failure in test_failed_backup_never_migrates_or_leaves_partial_backup: Der sqlite.connect-Testhook verglich Pfadstrings, während History db_path.resolve() verwendet. Der GitHub-Tempname RUNNER~1 wurde aufgelöst; der erwartete Backupfehler wurde deshalb nicht injiziert. [Vollständiger CI-Fehlerlog](EVIDENCE/ci-first-failure.txt), [lokaler Vorher-Repro mit äquivalentem alias/../-Pfad](EVIDENCE/ci-path-repro-before.txt).

Kleinste Korrektur ausschließlich im Test: Der Fall verwendet nun absichtlich einen Alias und der Hook vergleicht Path.resolve()-Identität. Produktlogik unverändert. Kein Test entfernt oder abgeschwächt: Backuperror, Rollback/lesbare Legacydaten, kein Teilbackup und erfolgreicher Wiederanlauf bleiben geprüft. Neue vollständige Qualifikation am korrigierten Teststand: 323 targeted, 1426 Windowsgesamttests, 19 echte Serverchecks, compileall/diffcheck PASS. Frühere vollständige PASS-Logs/Manifest/Patch bleiben als *.before-ci-fix.txt erhalten, sie qualifizieren nicht den neuen Testblob. Ursprünglicher Prompt/R01 und ein zentraler Meilenstein bleiben dieselben; noch keine unabhängige Abgabe erfolgt.


Maßgeblich nach CI-Selbstkorrektur: aktuelles Windowsmanifest mit getesteter Basis 66f44e0 plus staged Pfadalias-Testkorrektur, vollständig neu qualifiziertem Testblob und allen 195 qualifizierten Produktblobs. Finale Kandidaten-SHA/Tree stehen in PR und Übergabe.
