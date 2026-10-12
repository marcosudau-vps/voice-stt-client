# AP-CV2-040 – Continuous-Audio, Geräte-Recovery und Logbootstrap

Status **CHANGES_REQUIRED**, workflowPhase CHANGES_REQUIRED.
Aktiver Kandidat R03 wurde in R04 unabhängig geprüft: R02-F01 CLOSED, R02-F02 wegen Cancellation während Task-Join weiter OPEN.
[R03-Report](RUNS/R03-KORREKTUR/01_REPORT.md), [Evidenz](RUNS/R03-KORREKTUR/EVIDENCE/INDEX.md), [Originalauftrag](RUNS/R03-KORREKTUR/00_PROMPT_ORIGINAL.md).
1373 Windows,228 gezielte Tests,46 echte Serverfälle/46 Quellen und compileall/diffcheck PASS.

## Historischer R01-/R02-Stand
Branch `work/client-v2/ap-cv2-040`, Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`, Base `feat/client-v2`.
Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Planrevision 10, Rollenregelversion 7.

[Paketvertrag](../../PLANUNG/ARBEITSPAKETE/AP-CV2-040.md), [Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md), [Report](RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Vorgänger](RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json), [Vertragshashes](RUNS/R01-UMSETZUNG/EVIDENCE/start-contract-hashes.json).

Genau ein vollständiger Umsetzungslauf R01; kein eigener ROOT_PASS, kein Merge oder Folgepaketstart.

[Öffentliche Audio-/Log-API](../../../../../docs/protocol-v2-media.md). Windows 1367, gezielt 222, echter Servercheckpoint 41/46 Quellen, compileall und diffcheck PASS. Kandidatenbindung über Parent plus exakten Produktdiff und Gitblobliste im [Windowsmanifest](RUNS/R01-UMSETZUNG/EVIDENCE/windows-validation.json). Schreibhoheit ab Abgabe pausiert; frischer unabhängiger Review als nächste Aktion.

[PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6) gegen feat/client-v2. Vollständiger qualifizierter Umsetzungscommit `efd8362fc63bc8a98fdbc9edccd4b4074c659393`, Tree `dd63a7822a39ca332a2a62a113ad75b16bf9397b`; spätere reine Veröffentlichungsverweise separat per Blobvergleich. Finale PR-Spitze wird in PR-Kurzfassung und Abgabe aus Git genannt.

## R02 – unabhängige Abnahme (2026-10-12)

**CHANGES_REQUIRED** auf fachlich geprüftem SHA `79cffe19b103cfcc325f5c15a7532da763ff3f9c`, Tree `1449c1b71015d978349826891644565b3711e17a`. [Originalauftrag](RUNS/R02-ABNAHME/00_PROMPT_ORIGINAL.md), [Reviewbericht](RUNS/R02-ABNAHME/01_REPORT.md), [Evidenzindex](RUNS/R02-ABNAHME/EVIDENCE/INDEX.md). Pflichtfindings `CV2-040-R02-F01`, `CV2-040-R02-F02`. Die 1367er-Windows-Vollsuite und der 41er-Servercheckpoint gelten als im Umsetzungslauf durchgeführt und unabhängig geprüfte Fremdbelege; die beiden negativen Fehlerpfade sind nachzutesten. Keine Übernahme; nächster Schritt Korrektur im selben PR.

## R03 – Korrektur (2026-10-12)

[Report](RUNS/R03-KORREKTUR/01_REPORT.md), [Belegindex](RUNS/R03-KORREKTUR/EVIDENCE/INDEX.md), [Windowsmanifest](RUNS/R03-KORREKTUR/EVIDENCE/windows-validation.json). Beide Findings anerkannt/reproduziert; Verweis auf unabhängiges R02-Urteil bleibt erhalten. Neue Prüfung entscheidet über Schließung; kein eigener ROOT_PASS.

## R04 – Unabhängige Abnahme (2026-10-12)

**CHANGES_REQUIRED** auf fachlich geprüftem `7461577b1316ff113bac1c08ea7a836cf4b5023a` / Tree `83dd48d0ccd9110668c23732e3cd4933a50d03c3`. [Originalauftrag](RUNS/R04-ABNAHME/00_PROMPT_ORIGINAL.md), [Bericht](RUNS/R04-ABNAHME/01_REPORT.md), [Evidenz](RUNS/R04-ABNAHME/EVIDENCE/INDEX.md). R02-F01 ist unabhängig geschlossen; nativer Timeout-Teil von F02 behoben, aber bei Abbruch während `gather()` kann Logcleanup ausfallen (F02 bleibt OPEN). Kein Merge, nächste Aktion nur Korrektur im bestehenden PR.
