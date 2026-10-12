# AP-CV2-070 – Konfigurationsmigration und serverautoritativer Settingsservice

Status **REVIEW_READY**, workflowPhase **REVIEW_READY**, Stand 2026-10-12. R01-Umsetzung vollständig qualifiziert; unabhängige Abnahme offen. Paketbranch ab Übergabe für Umsetzung pausiert.

[Paketvertrag](../../PLANUNG/ARBEITSPAKETE/AP-CV2-070.md), [Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md), [Report](RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [öffentliche API](../../../../../docs/protocol-v2-settings.md).

Base feat/client-v2, Branch `work/client-v2/ap-cv2-070`, Parent `473a75d02fb6d00e5664af4328dadaa44da5191a`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Vorgänger-PASS, menschliche Freigabe und tatsächliche Übernahme [geprüft](RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json).

1460 Windowsgesamttests, 243 gezielte Tests, 38 echte Serverchecks und 55 gepinnte Supplementtests/keine Skips, compileall/diffcheck PASS. 34 neue Tests; alle29 SET-/WAKE-Requirements einzeln belegt. CLIENT OPEN bis unabhängiger Abnahme. Kein eigener ROOT_PASS oder Merge/AP080. Reale Kalibrierung und Nutzsprachgrenze AP-IV2-020, Appkomposition AP100.

Der exakte Kandidat ergibt sich aus veröffentlichter Branchspitze/PR-Beschreibung. Produkt-/Teststand über Parent, getesteten staged Diff und qualifizierte Gitblobs im Windowsmanifest identifiziert; finale eigene SHA/Tree außerhalb des erzeugenden Commits. Normale Paketbranch-Pushes/PR/Handoff workflowweit autorisiert gemäß Original AP000, keine kanonische Promotion.
