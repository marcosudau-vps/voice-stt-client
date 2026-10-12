# R05-Evidenzindex

[Report](../01_REPORT.md), [Originalauftrag](../00_PROMPT_ORIGINAL.md).

- [Baseline](baseline-targeted.txt), [Basis/Befehl/Exit/Hash](baseline-identity.json): 60 PASS vor Produktänderung.
- [Repros](repro-before-fix.txt), [Identität](repro-identity.json): drei erwartete FAILs auf R04-Produktbasis, nur Tests ergänzt.
- [Qualifikationsscript](qualify_windows.py): ausschließlich Projektvenv; tatsächliche vollständige Befehle/Runtime/Exitcodes in [Windowsmanifest](windows-validation.json).
- [Gezielte Suite](targeted-unittest.txt): 233 PASS mit warnings=error.
- [Gesamte Windows-Suite](windows-full-unittest.txt): 1378 PASS, keine Skips.
- [Servercheckpoint](server-audio-checkpoint.json), [vollständiger stderr](server-audio-checkpoint.json.stderr.txt): 52 PASS, 46 bytegeprüfte ada13b0-Quellen. Store1011 stammt aus absichtlich eingespeistem Fehlerfall.
- [compileall](compileall.txt): echter leerer Erfolgsoutput, Exit 0; keine erfundenen Logs.
- [Exakter Produktdiff](tested-product.patch), [Requirementcoverage](requirement-coverage.md), [Abgabeprüfung](submission-validation.json).

Qualifikation erzeugt mit `.\venv\Scripts\python.exe` und dem oben versionierten Script.
UTF-8/LF-Logs mit ausschließlich abgeschnittenen Zeilenendleerzeichen; alle Outputzeilen erhalten.
Runtimebytes und Git-normalisierte Blobidentität getrennt im Manifest; Quellhashes vor/nach Lauf identisch.

| Datei | SHA256 |
| --- | --- |
| [targeted-unittest.txt](targeted-unittest.txt) | `f20aaa00896aaa88633734f281b94e45c49dd37ed7cc01eaa67bf47ec3951244` |
| [server-audio-checkpoint.json](server-audio-checkpoint.json) | `7316eac1e03c60fd75ef54ef0a36324fe1ed82939247fe1b1299be4e57c69d6e` |
| [server-audio-checkpoint.json.stderr.txt](server-audio-checkpoint.json.stderr.txt) | `571a0f4fd2075c7b4325a3d60d5b854e2cda138c7fa7758713314359da0d9935` |
| [compileall.txt](compileall.txt) | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| [windows-full-unittest.txt](windows-full-unittest.txt) | `3926de56bb6915be7a0c0cf99cfdb8649fc6a077839b1bb5bcd17a71898c3b6f` |

[Qualifikationswiederholung](qualification-retry.json) dokumentiert einen 240-s-Harness-Timeout ohne PASS und zwei danach vollständige erfolgreiche Läufe auf unveränderten Quellen. [Vollständiger Diagnoselog](windows-full-diagnostic.txt), SHA256 `7ddcbb89c14a5343c86653540b1c32246d9551e91c0bfee3b4af47ad468dd9ae`.
