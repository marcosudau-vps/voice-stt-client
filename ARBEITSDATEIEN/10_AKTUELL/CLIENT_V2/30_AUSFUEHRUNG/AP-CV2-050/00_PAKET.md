# AP-CV2-050 – Hotkeyrollen, Runpausen und manuelle Controls

Status **ROOT_PASS**, workflowPhase **WAITING_FOR_APPROVAL**. Umsetzung R01 SELF_CHECK_PASS (2026-10-12); unabhängige [R02-ABNAHME](RUNS/R02-ABNAHME/01_REPORT.md) hat den eingereichten Kandidaten `55d6ca6b4d222fac9bba66a4911c7a6b8c236a0a` (Tree `3b0dc469a1a3e577eb4dda0a67e2f3746b9c92cd`) ohne offene Pflichtfindings technisch angenommen. Keine menschliche Freigabe, keine kanonische Übernahme.

[Paketvertrag](../../PLANUNG/ARBEITSPAKETE/AP-CV2-050.md), [R01-Originalauftrag](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md), [R01-Report](RUNS/R01-UMSETZUNG/01_REPORT.md), [R01-Evidenz](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [R02-Originalauftrag](RUNS/R02-ABNAHME/00_PROMPT_ORIGINAL.md), [R02-Report](RUNS/R02-ABNAHME/01_REPORT.md), [R02-Evidenz](RUNS/R02-ABNAHME/EVIDENCE/INDEX.md), [API](../../../../../docs/protocol-v2-controls.md).

Base `feat/client-v2`, Branch `work/client-v2/ap-cv2-050`, kanonischer Parent `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. AP040 nach unabhängigem PASS und menschlicher Freigabe übernommen: [Provenienz](RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json).

R01 hat 1397 vollständige Windows-Unit-Tests, 297 gezielte Tests, 79 Serverchecks und 16 native Win32checks mit vollständigen Logs dokumentiert. R02 hat diese Nachweise unabhängig geprüft; **eigene Windows-Testwiederholung NOT_RUN** (regelkonform). Alle 14 CONTROL-Requirements technisch ROOT_PASS. Nächste Aktion: ausdrückliche menschliche Freigabe für PR #7 abwarten. Bis dahin kein Merge und kein AP060-Start.

[PR #7](https://github.com/marcosudau-vps/voice-stt-client/pull/7) gegen feat/client-v2. Vollständiger qualifizierter Umsetzungscommit `ee1f1a7bb0a55112b61a3cab9c34be561aae274e`, Tree `f1613cb4ecf3292e6442f38c4704162b940c5fea`. Nachfolgende PR-Verweise rein administrativ; finale eingereichte Spitze steht SHA-/Tree-genau in aktueller PR-Beschreibung und finaler Übergabe.
