# AP-CV2-070 – Konfigurationsmigration und serverautoritativer Settingsservice

Status **ROOT_PASS**, workflowPhase **WAITING_FOR_APPROVAL**, Stand 2026-10-12. Unabhängiges R02-Review bestanden; menschlicher Merge-/Übernahmeprompt noch ausstehend.

[Paketvertrag](../../PLANUNG/ARBEITSPAKETE/AP-CV2-070.md), [Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md), [Report](RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [öffentliche API](../../../../../docs/protocol-v2-settings.md).

Base feat/client-v2, Branch `work/client-v2/ap-cv2-070`, Parent `473a75d02fb6d00e5664af4328dadaa44da5191a`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Vorgänger-PASS, menschliche Freigabe und tatsächliche Übernahme [geprüft](RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json).

1460 Windowsgesamttests, 243 gezielte Tests, 38 echte Serverchecks und 55 gepinnte Supplementtests/keine Skips, compileall/diffcheck PASS. 34 neue Tests; alle29 SET-/WAKE-Requirements einzeln belegt. R02 unabhängiger ROOT_PASS; kein Merge/AP080 ohne menschlichen Prompt. Reale Kalibrierung und Nutzsprachgrenze AP-IV2-020, Appkomposition AP100.

Der exakte Kandidat ergibt sich aus veröffentlichter Branchspitze/PR-Beschreibung. Produkt-/Teststand über Parent, getesteten staged Diff und qualifizierte Gitblobs im Windowsmanifest identifiziert; finale eigene SHA/Tree außerhalb des erzeugenden Commits. Normale Paketbranch-Pushes/PR/Handoff workflowweit autorisiert gemäß Original AP000, keine kanonische Promotion.

[PR #9](https://github.com/marcosudau-vps/voice-stt-client/pull/9) gegen feat/client-v2. Qualifizierter Produkt-/Unterlagencommit `8b68b4840c7955cd06a2be14736678d83ee729dc`, Tree `cd46b9047762829e89dd8f5fd95e5f66d0a9032e`. Nachfolgender PR-Verweisnachtrag administrativ; finale eingereichte SHA/Tree in aktueller PR-Beschreibung und finaler Handoff.

[R02-Reviewreport](RUNS/R02-ABNAHME/01_REPORT.md), [Review-Evidenz](RUNS/R02-ABNAHME/EVIDENCE/INDEX.md), [Originalauftrag](RUNS/R02-ABNAHME/00_PROMPT_ORIGINAL.md). reviewed_sha `146eff89e89faa48546f913cd7b770d3449d22a6`, reviewed_tree `e18b610e4fddfefc9a167c7178931f64f7fcd10e`. Offene Pflichtfindings keine.
