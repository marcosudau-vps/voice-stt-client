# AP-CV2-020 / R04 – unabhängiger Evidenzindex

**ROOT_PASS**. reviewed_sha `6d74c1ae06643e026834bc9164028bec908e26df`, reviewed_tree `f8a57f79c6bf61d7b079a41a53662adeac34c546`, canonical_parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`, server_sha `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Die Reviewer-Ausführung erfolgte ausschließlich über commitgebundene GitHub-Quellen, keine eigene Windows-Vollsuite. Originalauftrag [hier](../00_PROMPT_ORIGINAL.md), Entscheidung [hier](../01_REPORT.md).

| Nachweis | Tatsächliche Herkunft/Prüfung | Urteil |
| --- | --- | --- |
| [PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4) / [reviewed Commit](https://github.com/marcosudau-vps/voice-stt-client/commit/6d74c1ae06643e026834bc9164028bec908e26df) | Exakte Base/Head, Commit-/Treeidentität, vollständige 64-Datei-Parentdiffauflistung, Korrekturcompare seit R02 | PASS |
| [V2-Transport](https://github.com/marcosudau-vps/voice-stt-client/blob/6d74c1ae06643e026834bc9164028bec908e26df/voice_stt_client/core/v2_transport.py) / [Tracker](https://github.com/marcosudau-vps/voice-stt-client/blob/6d74c1ae06643e026834bc9164028bec908e26df/voice_stt_client/core/command_tracker.py) / [Transporttests](https://github.com/marcosudau-vps/voice-stt-client/blob/6d74c1ae06643e026834bc9164028bec908e26df/tests/test_v2_transport.py) | Source/Lifecycle/Cancellation/Error/Guard und R02-F01/F02 direkt geprüft | beide CLOSED/PASS |
| [K-01](https://github.com/marcosudau-vps/voice-stt-client/blob/6d74c1ae06643e026834bc9164028bec908e26df/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/REFERENZ/KONTRAKTE/K-01_WIRE_AUDIO_COMMANDS.md) und [K-04](https://github.com/marcosudau-vps/voice-stt-client/blob/6d74c1ae06643e026834bc9164028bec908e26df/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/REFERENZ/KONTRAKTE/K-04_LOGS_AUTH_RECOVERY.md) | Normative Ack/Hello/HTTP-/4408-/Reconnectregeln | PASS |
| [Vorher-Repro](../../R03-KORREKTUR/EVIDENCE/findings-before-fix.json) / [R03-Report](../../R03-KORREKTUR/01_REPORT.md) | Dynamische F01/F02-Repro vor Korrektur; echte Browser-/Fake-Socket-Exceptions | EXPECTED_FAIL (historisch; 7 Failures/9 Errors) |
| [Windowsmanifest](../../R03-KORREKTUR/EVIDENCE/windows-validation.json) | Windows11 Python3.12.10 Testcommit 98ab3c0; Cmd/Runtime/Exit 0/Zeiten/Dateihashes | 1294 + 61 PASS (extern) |
| [Vollständige Windowslogdatei](../../R03-KORREKTUR/EVIDENCE/windows-full-unittest.txt) | UTF-8 LF SHA256 `02ecbdb4100be7e244ec0dcaff2e6309f9e01d31c6408befbbeaafd87a68a036` | PASS und Hash geprüft |
| [Targeted-Log](../../R03-KORREKTUR/EVIDENCE/targeted-transport-codec-unittest.txt) | SHA256 `1496bc068cbce53b8d6d6b3132807a9d9d206b9c24b5e2b8870109779d758705` | PASS und Hash geprüft |
| [Echter gepinnter Servercheckpoint](../../R03-KORREKTUR/EVIDENCE/server-transport-checkpoint.json) | SHA256 `33c48c33e05bfa18c2c5981709653ac884fd86fa992f31ed21b3edcc586f00e3`; 21 Checks und 46 Serverblobs | PASS und Hash geprüft |
| [Compileall-Log](../../R03-KORREKTUR/EVIDENCE/compileall.txt) | Leerer vollständiger Log SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`, Exit 0 | PASS und Hash geprüft |
| [R03-admin Validation](../../R03-KORREKTUR/EVIDENCE/administrative-validation.json) | R03-Kandidatenstatus / Änderungen qualifizierter Produktsha→submitted Head nur administrativ, 25 Pfade | PASS |
| [CI exakt auf Head](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38183803142) | Direkter GitHub-Job-Check ID 114601742905; alle aufgeführten erfolgreichen Steps, inkl. EXE/Wheel/Installationssmokes, head_sha 6d74c1ae06643e026834bc9164028bec908e26df | PASS |
| Traceability / 28 IDs | Alle R03-methods im tatsächlichen Testcode vorhanden, Matrix konsistent; R04-Reviewerbeleg ergänzt | PASS |
| Eigene Windows-/Hardwaretests | Keine vom Reviewer ausgeführt, gemäß Abnahmeskill nicht notwendig; spätere Hardware-/ASR-/UI-Gates unverändert offen | NOT_RUN/SKIPPED_EXPECTED |

Abgrenzung: Extern ausgeführte Tests sind unabhängig validierte Fremdbelege; die unabhängige technische Bewertung des vollständigen Produkts und Findings ist die eigene R04-Leistung. Kein Produktcode wird durch R04 verändert.
