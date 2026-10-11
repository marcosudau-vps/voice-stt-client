# AP-CV2-000 / R04-ABNAHME – Evidenzindex

**Reviewed:** `cd872d4bfa8eccd0167337cbab16a572ca70bfd4` / Tree `6aff2fa629b0c01fde502c345e7e31035cee0926`; **canonical_parent:** `050e776cf316eb332177294db0c0a2719c2b4415`; **server_sha:** `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

**Reviewumgebung:** GitHub-Gitobjekte, PR-Diff und GitHub-Actions-Joblog über verbundenen GitHubzugriff; containerseitig nur Linux/Python 3.13 ohne Repository-Checkout/Client-Projektvenv, kein Windows-Prüfhost. **Keine eigenen vollständigen Clienttests oder nativen Win32-Repros ausgeführt.** Änderungen an Workflowdateien/Unterlagen wurden entsprechend ausdrücklichem Auftrag nicht inhaltlich bewertet.

| Beleg | Herkunft/Methode | Ergebnis und Grenze |
| --- | --- | --- |
| [Git-Head] (https://github.com/marcosudau-vps/voice-stt-client/commit/cd872d4bfa8eccd0167337cbab16a572ca70bfd4) | Git-Commitobjekt: SHA/Tree, Parent 210c2ae; PR-Base `050e776cf316eb332177294db0c0a2719c2b4415` | PASS – Identität |
| [Git-PR #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2) | Aktuelle Metadaten, Base/head und kumulatives Paket; PR offen | PASS – Provenienz |
| [Testmerge 5bb8fed](https://github.com/marcosudau-vps/voice-stt-client/commit/5bb8fed74197f1290dddd8132053ba073734451c) | Eltern `050e776cf316eb332177294db0c0a2719c2b4415` und `cd872d4bfa8eccd0167337cbab16a572ca70bfd4`, Tree `6aff2fa629b0c01fde502c345e7e31035cee0926` | PASS – CI testet kandidatenidentischen Baum |
| [Anwendungsquellcode](https://github.com/marcosudau-vps/voice-stt-client/blob/cd872d4bfa8eccd0167337cbab16a572ca70bfd4/voice_stt_client/ui/application.py#L225-L324) | Unabhängige statische Prüfung von `start` und `_register_startup_hotkeys` | R02-F01 statisch geschlossen: Persistenz nach `bridge.start()`, Rollback bei Fehler |
| [Neuer Regressionstest](https://github.com/marcosudau-vps/voice-stt-client/blob/cd872d4bfa8eccd0167337cbab16a572ca70bfd4/tests/test_startup_hotkey_persistence.py) | Testmethoden/Assertions gelesen, Negativ-/Positiv-/Retry-/Save-Fehlerfälle abgeglichen | PASS – fachliche Testabdeckung plausibel; nicht vom Reviewer ausgeführt |
| [Vorher-Repro](../R03-KORREKTUR/EVIDENCE/repro-before.txt) / [gezielter Endtest](../R03-KORREKTUR/EVIDENCE/targeted-final.txt) | Lokale R03-Logs gelesen | 4 vorherige FAIL + 1 PASS; danach gezielte 12 PASS (Selbstbeleg, nicht eigene Ausführung) |
| [Windows-CI 38163179818](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38163179818) | Job 114540194108, vollständiges Remote-Joblog und ausgeführte Steps überprüft: 1233 Unittests/OK, compileall, frozen EXE-/GUI-Smoke, Wheel/sdist/Twine-/Wheel-Importsmoke, Artefakte | **PASS, unabhängig validierter bestehender externer CI-Beleg**, nicht reviewerinitiiert |
| Eigenständige Windows-Regressionssuite und Repro | Kein geeigneter Windows-Host mit installiertem Projektvenv direkt zugänglich; keine reviewerinitiierte vollständige Ausführung/Bediener-Ausführung | **NOT_RUN**, Abnahmevoraussetzung offen |

Die CI zeigt erwartete Exception-Logs aus Negativtests sowie Encoding-Logger-Ausgaben, endet aber mit 1233 Tests und `OK`. Reales Mikrofon/ASR, physische Hotkey-/Hardwarewahrnehmung und finaler V2-Sockettest sind nicht Pflichtteil dieses AP-CV2-000.
