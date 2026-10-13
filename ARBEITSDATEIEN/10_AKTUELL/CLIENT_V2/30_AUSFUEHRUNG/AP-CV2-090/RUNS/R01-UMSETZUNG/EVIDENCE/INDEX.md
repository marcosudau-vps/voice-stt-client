# AP-CV2-090 / R01 – Evidenzindex

SELF_CHECK_PASS / REVIEW_READY, unabhängige Abnahme offen. Windows11/Python3.12 aus Projektvenv, Qt offscreen im Mainthread. Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`, Parent `1bc5be893060e0d6a80e1d890102bfffebb73a17`. Runtime/Dependencies/Commands/Exitcodes/Duration/Sourcebytes/Gitblobs in [windows-validation.json](windows-validation.json), genaue Kandidatendifferenz in [tested-product.patch.base64](tested-product.patch.base64). Finale Head/Tree extern in der PR.

Erzeugung: `.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/EVIDENCE/qualify_windows.py`; sämtliche darin protokollierten Testsubprozesse und abschließende Diffchecks erfolgreich. Nach der reinen Dokument-Zeichencodierungspflege und einer abschließenden Whitespacekorrektur am Testmodul wurde der gesamte Qualifikationslauf erneut am endgültigen Produkt-/Teststand ausgeführt. [verify_handoff.py](verify_handoff.py) verifiziert zusätzlich Gitblobs, Requirementsmethoden/Fälle und alle aktuellen Aktenlinks.

Baseline vor Änderung: Projektvenv, `QT_QPA_PLATFORM=offscreen`, `-m unittest` mit tests.test_event_models/test_event_normalizer/test_feedback_reducer/test_feedback_mapping/test_feedback_integration/test_feedback_ui/test_led_feedback/test_ui_widgets/test_v2_mirror/test_v2_results `-v`: 185 PASS, Exit0. Baseline-first Importfehler aufgrund nicht existierendem test_ui_presentation ist Diagnoselog, kein PASS. Die vollständigen ursprünglichen Ausgaben bleiben erhalten.

Gezielte Tests: 289 PASS mit `-W error`; gesamte Windows-Clientsuite: 1551 PASS, keine Skips. Neue FBsuite: 38 Fälle, einschließlich 6 unverändert assertierender Qtprozesse mit eigener QApplication. Stets `sys.executable` aus Projektvenv. compileall ist erfolgreich still, daher leere Datei mit protokolliertem Exit0/Hash.

Realer Checkpoint: [18 tatsächlich ausgeführte Checks](server-feedback-checkpoint.json), vollständige stderr separat. Produktions-FastAPI/SQLite/Domain- und Log-TCP-WebSockets/Mirror/Controls/Feedback/queued Qtports und echte Tray-/Overlaywidgets. Deterministisches PCM und kontrollierter Recorder/ASRscheduler ersetzen Mikrofon/ASR; Sound/LED kontrollierte Sinks. Kein produktiver Serverkontakt. Jeder geladene Serverquelltext wird vor/nach dem Run gegen `git show ada13b0:path` aus dem Serverrepository main bytegleich geprüft; Sourcehashes und genaue Grenzerklärung im JSON. Hardware-/Wahrnehmung bleibt IV2-020, Appkomposition AP100.

[FB-Abdeckung einzeln](requirement-coverage.md), [Eingangsprovenienz](input-provenance.json), [AP080 tatsächliche kanonische Übernahme](predecessor-canonicalization.json), [Report](../01_REPORT.md). Alte FAIL-Ausgaben sind Diagnose und werden durch keine PASS-Angabe umgedeutet.

## Artefakthashes

| Artefakt | SHA256 | Rolle |
| --- | --- | --- |
| [baseline-corrected-unittest.txt](baseline-corrected-unittest.txt) | `e928f10d80f0569dc97f5a93a9976243e7fd5fd341ed77709d5b946d520c2a86` | Relevante Voränderungsbaseline: 185 PASS |
| [baseline-unittest.txt](baseline-unittest.txt) | `d1edef18266f010c8b51dcd668c56cb1bce7aa7b0d21c2c72d464948af259e1b` | Entwicklungsdiagnose/Vorqualifikation, kein aktueller Kandidaten-PASS |
| [before-pure-boundary-fix-tested-product.patch.base64](before-pure-boundary-fix-tested-product.patch.base64) | `378d82d7c54428680182f5a4eb4bc4e6be007750b2b40a7db8b86b6917b65447` | Entwicklungsdiagnose/Vorqualifikation, kein aktueller Kandidaten-PASS |
| [before-pure-boundary-fix-windows-full-unittest.txt](before-pure-boundary-fix-windows-full-unittest.txt) | `95b74b6f78e5fcc640b0a508af6b986360900fbd595a5ee39c5065985d9e2cf3` | Entwicklungsdiagnose/Vorqualifikation, kein aktueller Kandidaten-PASS |
| [compileall.txt](compileall.txt) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Kandidatennachweis/Provenienz |
| [feedback-first.txt](feedback-first.txt) | `342c12fdfe0e09e07c435fedec47f2c35d87046ab3eca3161acabc10bd256806` | Entwicklungsdiagnose/Vorqualifikation, kein aktueller Kandidaten-PASS |
| [feedback-obs-targeted.txt](feedback-obs-targeted.txt) | `1d280c82cad6b3295bc53c862b64fe26f7fe0913bfbe6c2c6c2edbc7b3c2b676` | Entwicklungsdiagnose/Vorqualifikation, kein aktueller Kandidaten-PASS |
| [feedback-second.txt](feedback-second.txt) | `a38ffac64d81f9cf0398007cc1df6053fc792cec73a90010159dd613933be7dc` | Entwicklungsdiagnose/Vorqualifikation, kein aktueller Kandidaten-PASS |
| [input-provenance.json](input-provenance.json) | `407b455d2034170280e4daf38f0556cecc56253daa8fa6faf0b106666ef71ddf` | Kandidatennachweis/Provenienz |
| [predecessor-canonicalization.json](predecessor-canonicalization.json) | `ecb8ab78482198d667ecde32661abf2384cb200294c51e229ee8e97879e3b493` | Kandidatennachweis/Provenienz |
| [requirement-coverage.md](requirement-coverage.md) | `aef10d9cc52b84fbc3cbc347f5be051875cf967689323a3e3f7dadc4e3450711` | Kandidatennachweis/Provenienz |
| [server-feedback-checkpoint-stderr.txt](server-feedback-checkpoint-stderr.txt) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Kandidatennachweis/Provenienz |
| [server-feedback-checkpoint.json](server-feedback-checkpoint.json) | `184644be93cc9646a0ea855a8f70d3ede8da8d95849b5b6beea6be5ff9624c9f` | Kandidatennachweis/Provenienz |
| [server-feedback-checkpoint.json.stderr.txt](server-feedback-checkpoint.json.stderr.txt) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Entwicklungsdiagnose/Vorqualifikation, kein aktueller Kandidaten-PASS |
| [targeted-unittest.txt](targeted-unittest.txt) | `d421ca0ac15c47293b95d127a36146888a66d5961a009f7a60987aec4f1eb46f` | Kandidatennachweis/Provenienz |
| [tested-product.patch.base64](tested-product.patch.base64) | `7e6d42fae16b92572629c254f43423f80804d10c1e3c37d338396122d60ce560` | Kandidatennachweis/Provenienz |
| [windows-full-unittest.txt](windows-full-unittest.txt) | `7f09715b84cb77ca909034a8a020a2f0dd70c90e58821f6ba944b2a98279bc06` | Kandidatennachweis/Provenienz |
| [windows-validation.json](windows-validation.json) | `05a4c0a58511ea90608a34f3b2c36e6d389d3ca115d19e322caba503ff1f12e4` | Kandidatennachweis/Provenienz |

[Abgabeprüfung](handoff-verification.json): 208 qualifizierte Blobs, neun Requirements und alle aktuellen Aktenlinks PASS. Das eigene Resultat ist außerhalb seiner Selbsteinbettung gesichert.

[Veröffentlichungsprüfung nach PR-Verweisen](publication-verification.json), unveränderte qualifizierte Produkt-/Test-/Konfigurationsblobs.
