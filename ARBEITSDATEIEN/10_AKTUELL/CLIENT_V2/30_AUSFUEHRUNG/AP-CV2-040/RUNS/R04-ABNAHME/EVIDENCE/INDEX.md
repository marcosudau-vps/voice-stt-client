# AP-CV2-040 / R04 – Evidenzindex

**CHANGES_REQUIRED**, geprüft `7461577b1316ff113bac1c08ea7a836cf4b5023a` / Tree `83dd48d0ccd9110668c23732e3cd4933a50d03c3`; kanonischer Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`; Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

- [R04-Originalauftrag](../00_PROMPT_ORIGINAL.md) – tatsächlicher Benutzerauftrag.
- [R04-Reviewbericht](../01_REPORT.md) – unabhängiges Gesamturteil, Schließung R02-F01, offener R02-F02-Teilfall, Repro/Expected/Actual/Owner/Abnahmeauftrag.
- [R02-Vorreview](../../R02-ABNAHME/01_REPORT.md) – ursprüngliche Pflichtfindings.
- [R03-Korrekturbericht](../../R03-KORREKTUR/01_REPORT.md) – tatsächliche Umsetzung und Eigenbewertung.
- [R03-Volltestmanifest](../../R03-KORREKTUR/EVIDENCE/windows-validation.json) – Python/Windows/venv/Qt, Befehle/Exitcodes/Diffidentität, 188 Gitblobs.
- [Vollständiger Windows-Testlog](../../R03-KORREKTUR/EVIDENCE/windows-full-unittest.txt) – 1373 PASS.
- [Gezielter Testlog](../../R03-KORREKTUR/EVIDENCE/targeted-unittest.txt) – 228 PASS.
- [Vorher-Failurelog](../../R03-KORREKTUR/EVIDENCE/repro-before-fix.txt) – 5 erwartete Regressionen gegen alten Produktstand.
- [Nachher-Fokustests](../../R03-KORREKTUR/EVIDENCE/focused-after-fix.txt) – 34 PASS.
- [Servercheckpoint](../../R03-KORREKTUR/EVIDENCE/server-audio-checkpoint.json) – 46 Fälle und 46 bytegeprüfte Quellen; reale Client- und Server-Laufzeitgrenze ohne echte PortAudiohardware/ASR.
- [R03-Requirementabdeckung](../../R03-KORREKTUR/EVIDENCE/requirement-coverage.md) – 23 IDs mit Testmethoden und Serverfällen.
- [R03-Produktdiff](../../R03-KORREKTUR/EVIDENCE/tested-product.patch) – qualifizierter Patchsha256 `67db3bebf108faae0e2361a6d8eb6221c3e28e561460173f7202c918c53f35de`.
- [R03-Abgabeprüfung](../../R03-KORREKTUR/EVIDENCE/submission-validation.json) – ursprüngliche Kandidaten-/Produkt-/Aktenbindung.
- [Commitgebundene Code-Fundstelle](https://github.com/marcosudau-vps/voice-stt-client/blob/7461577b1316ff113bac1c08ea7a836cf4b5023a/voice_stt_client/core/v2_media.py#L383-L418) – `close()`-Task-Join vor Logcleanup.
- [Commitgebundener Cancellation-Test](https://github.com/marcosudau-vps/voice-stt-client/blob/7461577b1316ff113bac1c08ea7a836cf4b5023a/tests/test_v2_audio_recovery.py#L427-L455) – Cancellation erst nach Task-Join, nicht währenddessen.
- [R03-Kandidatencommit](https://github.com/marcosudau-vps/voice-stt-client/commit/7461577b1316ff113bac1c08ea7a836cf4b5023a) – geprüfte Git-/Treeidentität.

**Eigene Reviewprüfungen:** GitHub-Gitbaum vollständig (1297 Entries, `truncated=false`); 188/188 dem Qualifikationsmanifest entsprechende Git-Blobs; PR-Base/Parent und der kumulative Korrekturdiff anhand GitHub-Compare. CI-API-Attempt2 auf exakt geprüftem SHA SUCCESS. Isolierter `asyncio`-Mockrepro der geprüften Close-Methode: Task-Join-Cancellation führte zu `CancelledError` bei `log_shutdown=False` und `cleanup_complete=False`. Dieser isolierte Test ist **kein** Kandidaten-Repositorytest. R03-Windows-/Serverregressionen **extern ausgeführt, unabhängig geprüft**, Reviewer-Windowsdurchführung **NOT_RUN**. Echte Hardware/ASR **NOT_PROVEN**, späteres Gate.

Reviewer-Reviewcommit und PR-Head nach Bereitstellung über Git ermitteln; diese Akte gibt nicht vor, sich selbst als getestete Produkt-SHA zu enthalten.
