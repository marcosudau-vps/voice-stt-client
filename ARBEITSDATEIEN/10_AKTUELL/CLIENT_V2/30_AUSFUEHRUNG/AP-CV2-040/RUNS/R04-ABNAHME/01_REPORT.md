# AP-CV2-040 / R04 – unabhängige Wiederholungsabnahme nach R03

**Urteil: CHANGES_REQUIRED.** Datum: 2026-10-12 (Europe/Berlin). [Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md). Review auf exakt festgehaltenem Gitstand vor eigenem administrativem Reviewcommit. Kein Merge/Root-PASS/Start des Folgepakets.

## Gitidentität und Scope

| Merkmal | Geprüfter Stand |
| --- | --- |
| Repository/PR | [marcosudau-vps/voice-stt-client #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6), geöffnet |
| PR-Base | `feat/client-v2`, SHA `3df342c3a7cacaa1226743c4d9bee674e94d33db` |
| Kandidat | `work/client-v2/ap-cv2-040` |
| **reviewed_sha** | `7461577b1316ff113bac1c08ea7a836cf4b5023a` |
| **reviewed_tree** | `83dd48d0ccd9110668c23732e3cd4933a50d03c3` |
| canonical_parent | `3df342c3a7cacaa1226743c4d9bee674e94d33db` |
| Serverbaseline | `ada13b011e1d3829f78e7f389e3b927795a2b3be` |
| Korrekturvorgänger | `146839809bc234a2dfe4f02cea37d7ce2e4ff480` (R02-Reviewspitze) |
| aktiver Umsetzungslauf | R03-KORREKTUR, [Bericht](../R03-KORREKTUR/01_REPORT.md) |
| offener Pflichtbefund | `CV2-040-R02-F02` (Restfall: Cancellation während Task-Join) |

Der korrigierte Kandidat ist ein **Single-Parent-Commit** auf der übernommenen Reviewspitze; die kanonische Basis ist unverändert. Der vollständige Parentdiff und insbesondere der kumulative R03-Diff wurden anhand GitHub-PR-Daten, commitgebundener Dateien, Git-Blobs und Vertrags-/Testreferenzen geprüft. Geändert wurden im R03-Produktpfad nur `voice_stt_client/core/v2_media.py`, `tests/test_v2_audio_recovery.py` und der reale Servercheckpoint-Harness `scripts/check_v2_server_audio.py`. R01-/R02-Akten und Requirements-Definitionen bleiben historisch erhalten.

## Ergebnis der beiden R02-Findings

### CV2-040-R02-F01 – CLOSED / PASS

Geräteverlust, Hardware-Mute und inaktives Capture schließen zuerst die lokale PCM-Barriere, senden/bestätigen `audio_availability.set(false)` **vor** potenziell blockierendem nativem `capture.stop()` und bewahren Binding, alte Backgroundfinals und gewünschte Trigger-Suppression. Codebeleg: [`v2_media.py` L295–325](https://github.com/marcosudau-vps/voice-stt-client/blob/7461577b1316ff113bac1c08ea7a836cf4b5023a/voice_stt_client/core/v2_media.py#L295-L325). Drei neue deterministische Tests und echter Checkpoint `devices/false_acked_before_blocked_native_stop` sowie `background/older_final_while_native_stop_blocked` nachgewiesen. Eigenes dynamisches Ausführen: NOT_RUN. Der unabhängige Code-/Fremdbelegrecheck bestätigt die technische Schließung.

### CV2-040-R02-F02 – OFFEN / CHANGES_REQUIRED (Cancellation-Lücke)

**Schwere:** HOCH · **Requirements:** K-04 §6 (kontrollierter Shutdown, unabhängige Logs), AUDIO-09 / LOG-09 · **Owner:** AP-CV2-040-Korrekturagent.

Der ursprüngliche **native Timeoutfall** ist korrekt repariert: getrennte `_cleanup_complete`-Flag, serialisierter Close-Lock, wiederholbarer nativer Join und `logs.shutdown()` in einem inneren `finally` bewältigen die in R02 nachgewiesenen nativen Timeoutvarianten. Die zwei Timeoutregressionen und die echten Serverchecks belegen diese Teilkorrektur.

**Verbleibender reproduzierbarer Fehler:** [`v2_media.py` L397–416](https://github.com/marcosudau-vps/voice-stt-client/blob/7461577b1316ff113bac1c08ea7a836cf4b5023a/voice_stt_client/core/v2_media.py#L397-L416): `await asyncio.gather(*tasks, return_exceptions=True)` (L403) liegt **vor und außerhalb** des `try/finally`-Blocks (L405–416), der das Logcleanup garantiert. Wird `media.close()` durch eine externe `Task.cancel()` während des Joins der Sender-/Lifecycle-Tasks unterbrochen, propagiert `CancelledError`, bevor das Logshutdown erreicht wird. Dies ist ein tatsächliches asynchrones Cancellation-Fenster, etwa wenn der Sender während der Socket-Schließung ausläuft.

**Repro-Schritte:** READY-Session mit laufendem Logtransport. Eine der `_task/_sender`-Tasks beim Cancel kontrolliert in ihrer eigenen asynchronen Cleanup-Phase halten. `close()` starten, bis `gather` auf den Task wartet. Dann `close_task.cancel()` auslösen und den gehaltenen Task freigeben. Prüfen, ob `logs.shutdown()` erfolgt bzw. `active_transport_count == 0`. 

**Expected:** Logs werden unabhängig auch bei Abbruch des Close-Aufrufs kontrolliert beendet; tatsächliche Cancellation/Timeout weiter an Owner melden, unvollständigen nativen Shutdown korrekt retrybar halten.

**Actual:** Bei Cancellation am `gather`-Await wird `logs.shutdown()` nicht aufgerufen; `_cleanup_complete` bleibt false, aber der Logtransport kann nach der unterbrochenen ersten Schließung aktiv bleiben. Isolierter asyncio-Kontrollflussrepro mit derselben `close()`-Methode und gesteuert verzögerter Lifecycle-Cancellation: `CancelledError`, `log_shutdown=False`, `capture_stop=False`, `cleanup_complete=False`. **Dies war ein isolierter Methodentest mit Stubs**, nicht die Ausführung des Repository-Tests. Ein zusätzlicher Kandidaten-Repro durch den Umsetzer ist verlangt.

**Testlücke:** `test_cancelled_close_still_cleans_logs_and_can_retry` wartet ausdrücklich bis `media._task is None` (Test L439–440), womit der `gather`-Join schon beendet ist. Der Test cancelt erst beim nachgelagerten nativen Wait und kann die hier beschriebene Lücke nicht erkennen.

**Verlangte Korrektur/Abnahme:** Task-Join, natives Cleanup und Logcleanup so durch `try/finally` absichern, dass externer Cancel an jeder Await-Grenze einen kontrollierten vollständigen Logshutdown ermöglicht; Cancellation auch während des Logclose berücksichtigt und tatsächlicher unvollständiger Status ausgewiesen. Zusätzlich deterministischen Regressionstest für **Cancellation während noch ausstehendem Task-Join** mit aktivem Logtransport aufnehmen. Erwartete alte F02-Timeouttests weiterhin erhalten. Danach erneute kandidatengebundene gezielte und vollständige Windows-Qualifikation; betroffene unabhängige Log-/Servercheckpoint-Grenze nachweisen.

## Gesamtrequirements, Scope und Nachweise

Alle **23 IDs AUDIO-01 bis AUDIO-12 und LOG-01 bis LOG-11** sind in [R03-Requirementcoverage](../R03-KORREKTUR/EVIDENCE/requirement-coverage.md) auf konkrete Tests/Serverfälle abgebildet. Kontinuierliches Audio, 500-ms-generationgebundene PCMqueue, LED-/Mute-Unabhängigkeit, Resync und neue Session-IDs sowie Beobachter-only-Logs/Cursorbindungs-/Auth-/Tokenredaktionsfälle wurden im vollständigen kumulativen Kandidaten plausibilisiert. Keine Daten-, Credential-, Config- oder Historymigration; Qt-/Settingskomposition bleibt CV2-070/100, echte Hardware-/ASRqualifikation IV2-020. Keine neuen fachlichen Änderungen außerhalb des AP-Bereichs.

| Beleg | Extern im R03-Lauf nachgewiesen | Unabhängige Bewertung |
| --- | --- | --- |
| R03-Repro gegen alten R02-Code | 5/5 erwartete FAILs, mit Reproidentität | PASS als Fehlerrepro-Fremdbeleg |
| Korrigierte Audiotests | 34 PASS, inkl. sechs neue Regressionen | PASS als Fremdbeleg; Task-Join-Cancel nicht getestet |
| gezielte Suite (`-W error`) | 228 PASS, Exit 0 | PASS als Fremdbeleg |
| vollständige Windows-Clientsuite | **1373 PASS**, Exit 0, kein Skip im Log | PASS als unabhängig geprüfter Fremdbeleg |
| realer Servercheckpoint (modellfreie Grenzen) | **46 PASS**, 46 bytegeprüfte Serverquellen | PASS als unabhängig geprüfter Fremdbeleg |
| compileall, Diff-/Aktenprüfung | PASS, Exit 0 | PASS als Fremdbeleg |
| Gitblob-Identität | **188/188 identisch**: `qualifiedGitBlobs` im Manifest vs rekursiver GitHub-Gitbaum des `reviewed_tree` | PASS, eigene unabhängige Prüfung |
| GitHub-CI | Run [38204720433 / Attempt 2](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38204720433/attempts/2), SUCCESS auf genau `7461577b1316ff113bac1c08ea7a836cf4b5023a` | PASS; Attempt 1 scheiterte an 2-s-Startupwait, Retry gleicher SHA vollständig grün |
| neue spezielle Task-Join-Cancellation-Reproduktion im Repo | **NOT_RUN / NOT_PROVEN** | offener Pflichtnachweis |
| reale Mikrofon-/USB-/ASR-/Wakequalität | **NOT_PROVEN**, gemäß Paketgrenze später IV2 | kein Paketpflichtversäumnis |

Windows-Runtime: Windows 11 (Build 26300), Python 3.12.10, Projekt-venv, Qt offscreen. Vollständige R03-Befehle/Exitcodes/Logbelege stehen im [Windowsmanifest](../R03-KORREKTUR/EVIDENCE/windows-validation.json) und [Evidenzindex](../R03-KORREKTUR/EVIDENCE/INDEX.md); die eigenen Windows-/Server-Testläufe des Reviewers waren **NOT_RUN**, keine Wiederholungspflicht bei gültigen Fremdbelegen. Ungeklärtes Cancellationverhalten ist ein Codefinding, nicht eine generische Forderung nach doppelter Windowsprüfung.

## Dokumentation, Gitrechte und Übergabe

Die fachlich geprüfte Spitze `7461577b1316ff113bac1c08ea7a836cf4b5023a` bleibt von einem späteren ausschließlich administrativen Review-Dokumentcommit unterscheidbar. Die vorhandene menschliche Workflow-Gitfreigabe deckt Reviewunterlagen und administrative Status-/Traceability-Verweise auf demselben Paketbranch; sie gestattet weder Produktkorrekturen durch Reviewer noch Merge oder neues Paket. Keine fachlichen Requirements umdefiniert; offene Requirementnachweise bleiben offen. R01/R02/R03-Abgaben und Reprologs erhalten.

**Finales Urteil:** `CHANGES_REQUIRED`, **`CV2-040-R02-F01` geschlossen**, `CV2-040-R02-F02` weiterhin offen aufgrund der beschriebenen Cancellation-Lücke. Nächste Aktion: Korrektur der einzigen verbleibenden Pflichtlücke im **bestehenden PR #6**, vollständige nachgezogene Regression und erneute unabhängige Abnahme des neuen Gesamtstands. `feat/client-v2`, Server-Distributed, Main/Tag/Release bleiben unangetastet. Kein technischer ROOT_PASS, keine menschliche Übernahmefreigabe.
