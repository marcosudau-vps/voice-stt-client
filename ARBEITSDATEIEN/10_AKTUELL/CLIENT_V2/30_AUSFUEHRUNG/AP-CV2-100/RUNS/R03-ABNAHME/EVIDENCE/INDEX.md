# AP-CV2-100 / R03-ABNAHME – Evidenzindex

**Gegenstand:** GitHub-PR #12, reviewed_sha `4a35a2d7eba5fa55e79528744320419b8ec0a1b3`, reviewed_tree `18f7516471c97627b92e9221e24e367f30f5cd81`, Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Reviewer: reine commitgebundene Code-/Nachweisprüfung, eigene Windows-Ausführung **NOT_RUN**.

| Nachweis | Herkunft / tatsächliche Prüfung |
| --- | --- |
| [Eigenes Prüfprotokoll](review-source-checks.json) | Git-/CI-Identität und sechs unabhängig gelesene, mit Windowsmanifest verglichene Blob-SHAs |
| [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12) | Aktueller Head/Base bei Review; Compare 3 ahead / 0 behind und 86 geänderte Dateien |
| [Windowsmanifest](../../R02-KORREKTUR/EVIDENCE/windows-validation.json), [Vollsuite](../../R02-KORREKTUR/EVIDENCE/windows-full-unittest.txt), [gezielter Log](../../R02-KORREKTUR/EVIDENCE/targeted-unittest.txt) | Fremdbelege: 1574/203 PASS mit kandidatspezifischen Blobs, Runtime, Befehlen, Exit und SHA256 |
| [Servercheckpoint](../../R02-KORREKTUR/EVIDENCE/server-runtime-checkpoint.json) | 17 tatsächliche zusammengesetzte Checks gegen 45 bytegeprüfte Serverquellen |
| [Abgabeverifikation](../../R02-KORREKTUR/EVIDENCE/submission-verification.json) | 213 qualifizierte Gitblobs und 1174 relative Aktenlinks laut R02-Abgabeprüfung PASS |
| [Headgebundene Windows-CI](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38347923728) | Jobs für Test, compileall, EXE-/sdist-/Wheel-Smokes, Upload completed/success |
| [V2DesktopApplication](https://github.com/marcosudau-vps/voice-stt-client/blob/4a35a2d7eba5fa55e79528744320419b8ec0a1b3/voice_stt_client/ui/v2_application.py), [V2Runtime](https://github.com/marcosudau-vps/voice-stt-client/blob/4a35a2d7eba5fa55e79528744320419b8ec0a1b3/voice_stt_client/core/v2_runtime.py), [V2CoreBridge](https://github.com/marcosudau-vps/voice-stt-client/blob/4a35a2d7eba5fa55e79528744320419b8ec0a1b3/voice_stt_client/ui/v2_core_bridge.py) | F01: fehlende Auditemission/Korrelation im neuen Produktpfad |
| [geerbter Desktop](https://github.com/marcosudau-vps/voice-stt-client/blob/4a35a2d7eba5fa55e79528744320419b8ec0a1b3/voice_stt_client/ui/application.py), [alter Controller](https://github.com/marcosudau-vps/voice-stt-client/blob/4a35a2d7eba5fa55e79528744320419b8ec0a1b3/voice_stt_client/core/controller.py), [bisherige OBS-Vertragstests](https://github.com/marcosudau-vps/voice-stt-client/blob/4a35a2d7eba5fa55e79528744320419b8ec0a1b3/tests/test_obs040_client_hooks.py) | F01: bisherige drei Eventnamen und korrelierter Auditvertrag tatsächlich im Bestand vorhanden |
| [V2-Integrationstests](https://github.com/marcosudau-vps/voice-stt-client/blob/4a35a2d7eba5fa55e79528744320419b8ec0a1b3/tests/test_v2_runtime_integration.py) | Funktionale Qt-/Apply-/Rollbackregression vorhanden, V2-Auditassertions fehlen |

**Urteil:** CHANGES_REQUIRED, offenes Finding `CV2-100-R03-F01`. Keine Produktänderung, kein behaupteter eigener Windows-/Hardwaretest.
