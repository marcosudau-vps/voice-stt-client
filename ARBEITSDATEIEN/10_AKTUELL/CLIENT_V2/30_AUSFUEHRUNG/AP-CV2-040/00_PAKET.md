# AP-CV2-040 – Continuous-Audio, Geräte-Recovery und Logbootstrap

Status **ACCEPTED**, tatsächliche kanonische Übernahme am 2026-10-12 durch PR6 nach R06-PASS und menschlicher Freigabe. Aggregate `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f`, Tree `fde6009d3d9c699a92f7cc0ef8a6452e4903c1e0`, genau ein Parent/Commit; Baumgleichheit zum finalen PR6-Head. [Gesicherter Abschlussnachweis](../AP-CV2-050/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). Vorgängerabschluss auf AP050-Branch fortgeschrieben, kein weiterer AP040-Aggregatecommit.

## Historischer Kopf vor tatsächlicher Übernahme


Status **ROOT_PASS**, workflowPhase READY_FOR_CANONICALIZATION. nach unabhängiger R06-Abnahme am 2026-10-12. Fachlich geprüfter Kandidat `4ef7a13672bf7c50665e08f5eff837fb5d687419`, Tree `f670a6fce6557ff657644037964025e9f7f1ee1e`. [R06-Originalauftrag](RUNS/R06-ABNAHME/00_PROMPT_ORIGINAL.md), [PASS-Bericht](RUNS/R06-ABNAHME/01_REPORT.md), [Evidenzindex](RUNS/R06-ABNAHME/EVIDENCE/INDEX.md). F01 CLOSED_R04, F02 CLOSED_R06, keine offenen Pflichtfindings. 1378 Windows-, 233 gezielte Tests, 52 echte Serverfälle (46 bytegeprüfte Quellen), Git-Blobs 188/188, CI SUCCESS als unabhängig geprüfte Fremdbelege.

PR [#6](https://github.com/marcosudau-vps/voice-stt-client/pull/6) bleibt offen; Base `feat/client-v2` und Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db` unverändert. Menschliche Übernahmefreigabe einschließlich der vorbereiteten Statuskorrektur liegt vor (siehe unten). Noch nicht übernommen; finale Kandidaten-CI und eindeutiger Squash sind erforderlich. Kein AP050-Start oder Release.

## Historischer R05-Korrekturstand


Status **REVIEW_READY**, workflowPhase REVIEW_READY. Aktueller Run R05-KORREKTUR.
[R05-Report](RUNS/R05-KORREKTUR/01_REPORT.md), [Evidenz](RUNS/R05-KORREKTUR/EVIDENCE/INDEX.md), [Originalauftrag](RUNS/R05-KORREKTUR/00_PROMPT_ORIGINAL.md).
F01 unabhängig CLOSED_R04; F02 Task-Join-/Logclose-Cancellation anerkannt, reproduziert und technisch korrigiert. Unabhängige Bestätigung offen.
1378 Windows-/233 gezielte Tests,52 echte Serverfälle/46 Quellen, compileall/diffcheck PASS. Paketbranch ab Übergabe pausiert.
[R04-Abnahme](RUNS/R04-ABNAHME/01_REPORT.md), [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6).

## Historischer R03-/R04-Kopf

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

## Menschliche Dokumentkorrektur- und Übernahmefreigabe

Die grobe Abschlussprüfung ist [online mit dem vorbereiteten Dokumentpatch](https://github.com/marcosudau-vps/voice-stt-client/pull/6#issuecomment-6124596439) dokumentiert; [Patchteil2](https://github.com/marcosudau-vps/voice-stt-client/pull/6#issuecomment-6124597129). Aktueller Head bei Freigabe `efd60e0cba7272c9b18ca21da7e337c1aa89fba9`, kanonischer Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`, technisch geprüfter R06-Kandidat `4ef7a13672bf7c50665e08f5eff837fb5d687419`.

Tatsächlicher ursprünglicher Nutzerauftrag:

> Der Reviewer hat ROOT_PASS PR #6, Arbeitspaket AP-CV2-040 erteilt.
> Bitte prüfe nochmal grob den Umfang, Bewertungsmaßstäbe, Tracabilities, etc...
> Keine fachliche Detailprüfung mehr...
> Wenn du nichts einzuwenden hast, erteile ich dir die Freigabe, um den Pull Request so zu mergen.

Konkrete Rückfrage nach der vorbereiteten Statuskorrektur:

> Gibst du diese Dokumentkorrektur zum Committen und Pushen frei, anschließend den Squash-Merge nach grüner CI?

Tatsächliche Antwort des Auftraggebers:

> Ja, ich erteile dir die Freigabe.

Erlaubt sind die vorbereitete administrative Statuskorrektur, Sicherung dieser Freigabe und genau ein PR-Squash auf feat/client-v2 nach grüner finaler CI. Kein Produkt-/Test-/Kontraktfix und keine zusätzliche fachliche Abnahme. Historische R01–R06-Berichte unverändert erhalten. Noch kein ACCEPTED; nach Merge ergibt sich die Übernahme aus Git/PR, und der nächste Paketbranch führt diesen Nachweis nach.
