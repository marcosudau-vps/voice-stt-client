# AP-CV2-090 / R01 – Evidenzindex

SELF_CHECK_PASS / REVIEW_READY, unabhängige Abnahme offen. Windows11/Python3.12 aus Projektvenv, Qt offscreen im Mainthread. Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`, Parent `1bc5be893060e0d6a80e1d890102bfffebb73a17`. Runtime/Dependencies/Commands/Exitcodes/Duration/Sourcebytes/Gitblobs in [windows-validation.json](windows-validation.json), genaue Kandidatendifferenz in [tested-product.patch.base64](tested-product.patch.base64). Finale Head/Tree extern in der PR.

Erzeugung: `.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/EVIDENCE/qualify_windows.py`; sämtliche darin protokollierten Testsubprozesse und abschließende Diffchecks erfolgreich. Nach der reinen Dokument-Zeichencodierungspflege und einer abschließenden Whitespacekorrektur am Testmodul wurde der gesamte Qualifikationslauf erneut am endgültigen Produkt-/Teststand ausgeführt. [verify_handoff.py](verify_handoff.py) verifiziert zusätzlich Gitblobs, Requirementsmethoden/Fälle und alle aktuellen Aktenlinks.

Baseline vor Änderung: Projektvenv, `QT_QPA_PLATFORM=offscreen`, `-m unittest` mit tests.test_event_models/test_event_normalizer/test_feedback_reducer/test_feedback_mapping/test_feedback_integration/test_feedback_ui/test_led_feedback/test_ui_widgets/test_v2_mirror/test_v2_results `-v`: 185 PASS, Exit0. Baseline-first Importfehler aufgrund nicht existierendem test_ui_presentation ist Diagnoselog, kein PASS. Die vollständigen ursprünglichen Ausgaben bleiben erhalten.

Gezielte Tests: 377 PASS mit `-W error`; gesamte Windows-Clientsuite: 1552 PASS, keine Skips. Neue FBsuite: 39 Fälle, einschließlich 7 unverändert assertierender Qtprozesse mit eigener QApplication. Stets `sys.executable` aus Projektvenv. compileall ist erfolgreich still, daher leere Datei mit protokolliertem Exit0/Hash.

Realer Checkpoint: [18 tatsächlich ausgeführte Checks](server-feedback-checkpoint.json), vollständige stderr separat. Produktions-FastAPI/SQLite/Domain- und Log-TCP-WebSockets/Mirror/Controls/Feedback/queued Qtports und echte Tray-/Overlaywidgets. Deterministisches PCM und kontrollierter Recorder/ASRscheduler ersetzen Mikrofon/ASR; Sound/LED kontrollierte Sinks. Kein produktiver Serverkontakt. Jeder geladene Serverquelltext wird vor/nach dem Run gegen `git show ada13b0:path` aus dem Serverrepository main bytegleich geprüft; Sourcehashes und genaue Grenzerklärung im JSON. Hardware-/Wahrnehmung bleibt IV2-020, Appkomposition AP100.

[FB-Abdeckung einzeln](requirement-coverage.md), [Eingangsprovenienz](input-provenance.json), [AP080 tatsächliche kanonische Übernahme](predecessor-canonicalization.json), [Report](../01_REPORT.md). Alte FAIL-Ausgaben sind Diagnose und werden durch keine PASS-Angabe umgedeutet.

## Artefakthashes

| Artefakt | SHA256 | Rolle |
| --- | --- | --- |
| [baseline-corrected-unittest.txt](baseline-corrected-unittest.txt) | `e928f10d80f0569dc97f5a93a9976243e7fd5fd341ed77709d5b946d520c2a86` | Relevante Voränderungsbaseline: 185 PASS |
| [baseline-unittest.txt](baseline-unittest.txt) | `d1edef18266f010c8b51dcd668c56cb1bce7aa7b0d21c2c72d464948af259e1b` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [before-pure-boundary-fix-tested-product.patch.base64](before-pure-boundary-fix-tested-product.patch.base64) | `378d82d7c54428680182f5a4eb4bc4e6be007750b2b40a7db8b86b6917b65447` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [before-pure-boundary-fix-windows-full-unittest.txt](before-pure-boundary-fix-windows-full-unittest.txt) | `95b74b6f78e5fcc640b0a508af6b986360900fbd595a5ee39c5065985d9e2cf3` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [compileall.txt](compileall.txt) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Aktueller Kandidatennachweis/Provenienz |
| [feedback-first.txt](feedback-first.txt) | `342c12fdfe0e09e07c435fedec47f2c35d87046ab3eca3161acabc10bd256806` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [feedback-obs-targeted.txt](feedback-obs-targeted.txt) | `1d280c82cad6b3295bc53c862b64fe26f7fe0913bfbe6c2c6c2edbc7b3c2b676` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [feedback-second.txt](feedback-second.txt) | `a38ffac64d81f9cf0398007cc1df6053fc792cec73a90010159dd613933be7dc` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [input-provenance.json](input-provenance.json) | `407b455d2034170280e4daf38f0556cecc56253daa8fa6faf0b106666ef71ddf` | Aktueller Kandidatennachweis/Provenienz |
| [predecessor-canonicalization.json](predecessor-canonicalization.json) | `ecb8ab78482198d667ecde32661abf2384cb200294c51e229ee8e97879e3b493` | Aktueller Kandidatennachweis/Provenienz |
| [requirement-coverage.md](requirement-coverage.md) | `4ba986d063c263ea287f06601428e95e6af8689b671f24a06b8c10cc38ab7337` | Aktueller Kandidatennachweis/Provenienz |
| [server-feedback-checkpoint-stderr.txt](server-feedback-checkpoint-stderr.txt) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [server-feedback-checkpoint.json](server-feedback-checkpoint.json) | `fb0ad934391adfaa9a8ac519a8f45ba842f409218045da6dd7b831a29a1cabf0` | Aktueller Kandidatennachweis/Provenienz |
| [server-feedback-checkpoint.json.stderr.txt](server-feedback-checkpoint.json.stderr.txt) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | Aktueller Kandidatennachweis/Provenienz |
| [targeted-unittest.txt](targeted-unittest.txt) | `b49b9eaba718a7e4474bedc04a2df4a0b792e1214e2f1ffdafc0341e42a062ac` | Aktueller Kandidatennachweis/Provenienz |
| [tested-product.patch.base64](tested-product.patch.base64) | `976294b4a2919c02dc6ec69555d34b11244e234cfed8e2a6658dfeef8ee3863b` | Aktueller Kandidatennachweis/Provenienz |
| [viewer-baseline.txt](viewer-baseline.txt) | `33cdf4a28f5b33c465c3dd591a7097129cacc31503c8736cd8602dad8066fed1` | OBS-050 vor UIänderung: 87 PASS |
| [viewer-repro.txt](viewer-repro.txt) | `4e9d3c1d8b4ec71b4d9870aceff6a6c426acee737637817e6d218608078e8229` | Vorqualifikation/Diagnose, kein aktueller Kandidaten-PASS |
| [windows-full-unittest.txt](windows-full-unittest.txt) | `023914e2b9aeecf18c57243bf608c9819300b8075223636981081e5c01be8a1d` | Aktueller Kandidatennachweis/Provenienz |
| [windows-validation.json](windows-validation.json) | `b91b1b43d70c7e555f460c74e7a504b55e65200aa44c75343006b5ce60a35ee6` | Aktueller Kandidatennachweis/Provenienz |
[Abgabeprüfung](handoff-verification.json): 208 qualifizierte Blobs, neun Requirements und alle aktuellen Aktenlinks PASS. Das eigene Resultat ist außerhalb seiner Selbsteinbettung gesichert.

[Veröffentlichungsprüfung nach PR-Verweisen](publication-verification.json), unveränderte qualifizierte Produkt-/Test-/Konfigurationsblobs.

UUID-Vieweranschluss vor Änderung: [87 OBS-050-Baselinefälle](viewer-baseline.txt), [tatsächlicher FAIL-Repro](viewer-repro.txt), danach ganze Qualifikation erneut. [Frühere Qualifikation](BEFORE-VIEWER-FIX/windows-validation.json) am ersten Kandidaten ist superseded; deren vollständige Logs und Hashes bleiben zusammen erhalten.
