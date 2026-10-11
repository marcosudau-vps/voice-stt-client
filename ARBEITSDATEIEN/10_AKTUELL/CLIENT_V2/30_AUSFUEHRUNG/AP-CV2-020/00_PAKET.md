# AP-CV2-020 – V2-Transport und Commandkorrelation

Status **CHANGES_REQUIRED**, workflowPhase CHANGES_REQUIRED.
Branch work/client-v2/ap-cv2-020, Base feat/client-v2, Parent 91065f5f7715aa6653ec5335d9e757b6ef97a067.
Server ada13b011e1d3829f78e7f389e3b927795a2b3be.
[PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4).

[Paketvertrag Revision10](../../PLANUNG/ARBEITSPAKETE/AP-CV2-020.md),
[API und Bootstrapgrenze](../../../../../docs/protocol-v2-transport.md),
[Vorgänger-PASS/Freigabe/Übernahme](RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json).
[Startvertragshashes](RUNS/R01-UMSETZUNG/EVIDENCE/start-contract-hashes.json).

| Run | Rolle / Stand | Original | Report / Evidenz |
| --- | --- | --- | --- |
| R01-UMSETZUNG | Umsetzung / REVIEW_READY (historisch) | [Prompt](RUNS/R01-UMSETZUNG/00_PROMPT_ORIGINAL.md) | [Report](RUNS/R01-UMSETZUNG/01_REPORT.md), [Index](RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md) |
| R02-ABNAHME | unabhängige Abnahme / CHANGES_REQUIRED | [Prompt](RUNS/R02-ABNAHME/00_PROMPT_ORIGINAL.md) | [Report](RUNS/R02-ABNAHME/01_REPORT.md), [Index](RUNS/R02-ABNAHME/EVIDENCE/INDEX.md) |

Windowsqualifikation auf 7546298f26e00b83ad4c9510a9b8c1e7e6726fc3, Tree 7bd496ef70a192781ff999b31695b3ef3fd72210:1290 Gesamttests,57 gezielte Tests,
21 echte Serverchecks/46 byteverifizierte Quellen und compileall PASS.
Nachträge nur administrativ; finale eingereichte SHA/Tree aus Git-/PR-Übergabe.

Nächste Aktion: frische unabhängige Session prüft PR #4 vom Parent bis zum
endgültigen Head samt Code und kandidatengebundenen Nachweisen. Schreibhoheit
nach Abgabe pausiert (writeOwner=null). Unabhängiger PASS und menschliche
Übernahmefreigabe für AP020 bleiben offen. Kein Eigenreview oder Folgepaket.

## Aktueller unabhängiger R02-Review (2026-10-12)

**CHANGES_REQUIRED**: [R02-Bericht](RUNS/R02-ABNAHME/01_REPORT.md) mit CV2-020-R02-F01 (WebSocket-HTTP-Upgrade-Fehler ohne Recovery) und CV2-020-R02-F02 (4408-Zähler bleibt über READY erhalten). Review-ID: Kandidat 2b79a9a23a6be554a2a2a05ff3256a63ccf022d4, Tree 647a0b4070d666e37b475841d094d4e37cc43e40; nachfolgender Dokumentcommit ist keine Produktabnahme. R01-Windows-/Serverpass bleibt historischer Fremdbeleg. Korrektur im PR #4 beauftragen; danach neue Regression und frische unabhängige Abnahme. Keine Übernahmefreigabe.
