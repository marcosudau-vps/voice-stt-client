# Client V2 – AP-CV2-090 / R01-UMSETZUNG / REVIEW_READY, 2026-10-13

Aktiver Arbeitsblock CLIENT_V2. AP000 bis AP080 ACCEPTED; AP080 tatsächlich auf `1bc5be893060e0d6a80e1d890102bfffebb73a17` übernommen, Single-Parent/Baumgleichheit und unabhängiger PASS/menschlicher Prompt [belegt](30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP090 vollständig umgesetzt auf `work/client-v2/ap-cv2-090`; unabhängige Abnahme offen. Spätere Pakete PLANNED, Server-Distributed bleibt offen.

[Runreport](30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-090/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json), [Planungseinstieg](PLANUNG/README.md), [Produktinterfaces](../../../docs/protocol-v2-feedback.md).

Bestehende Feedbackengine mit validiertem V2-Mirroringang, quellenneutralen Phasen und getrenntem Backgrounddrain. Segmentvorschau, Domain-Dedup, diagnostischer Log-/Replaypfad, relative Anzeige ohne Lifecyclecommands; isolierte queued Qt-/Sound-/LEDausgabe. Mappingregeln und Präferenzen bleiben erhalten, UUIDkorrelation nutzt die vorhandene OBSfoundation.

Qualifikation: 1552 vollständige Windows-Tests, 377 gezielte Tests, 39 neue Clienttests; tatsächlicher gepinnter Domain-/Log-/Replay-/Qtcheckpoint 18 Checks. compileall/diffcheck und Akten-/Blobbindung im Evidenzindex. Hardware-/ASR-/Wahrnehmung bleibt AP-IV2-020, reguläre Appkomposition AP100. Start weiterhin `.\venv\Scripts\python.exe -m voice_stt_client`.

Nächste Aktion: unabhängiges Review des endgültigen PR-Heads; Umsetzungsschreiben ab Übergabe pausiert. ROOT_PASS und anschließend ausdrücklicher menschlicher Übernahmeprompt erforderlich. Kein automatischer Merge/AP100.

## Historischer Stand vor AP-CV2-020

# Client V2 – AP-CV2-010

AP-CV2-000 ACCEPTED auf `1cf076bd2ed56929b1a3780bc140da51348a8295`, PR #2. AP-CV2-010 ROOT_PASS (R02; Übernahmefreigabe ausstehend): [Paketakte](30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md), [Workflowstatus](WORKFLOW_STATUS.json). Reiner Codec; unveränderte Serverbaseline ada13b0. Nachmergeprovenienz ist in der AP010-Akte nachgewiesen, kein zweiter AP000-Abschlusscommit.

Die folgenden datierten Angaben bleiben Historie.

# Client V2 – aktive Planung und Entwicklung

Stand 2026-10-11. Gemeinsamer Abschlussbranch: `feat/client-v2`.

- [Dein Ablauf als Auftraggeber](PLANUNG/REFERENZ/GOVERNANCE/AUFTRAGGEBER.md).
- [Planung und beide Agenteneinstiege](PLANUNG/README.md).
- [Status](STATUS.md) und [Verlauf](VERLAUF.md).
- [Branchführung und gemeinsame Planpflege](PLANUNG/REFERENZ/GOVERNANCE/BRANCH_UND_PLANPFLEGE.md).

**Aktueller Paketstand:** AP-CV2-000 ROOT_PASS nach R04-Review und R05-Windows-Volltest (1233 PASS). [Nachweis/Freigabe](30_AUSFUEHRUNG/AP-CV2-000/RUNS/R05-WINDOWS-NACHWEIS/01_REPORT.md). Finale CI prüfen und den freigegebenen Einzel-Squash ausführen; kein Folgepaketstart vor tatsächlicher Übernahme. Windows-Vollsuite künftig Umsetzungspflicht, ChatGPT-Review anhand Code und gültigen Nachweisen.
