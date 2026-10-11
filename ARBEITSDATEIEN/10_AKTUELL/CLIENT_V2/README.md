# Aktueller Client-V2-Korrekturstand – AP-CV2-020 / R03, 2026-10-12

AP-CV2-020 **REVIEW_READY** im [PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4), Branch `work/client-v2/ap-cv2-020`, Parent `91065f5f7715aa6653ec5335d9e757b6ef97a067` (AP010 ACCEPTED, unverändert). [R03-Report](30_AUSFUEHRUNG/AP-CV2-020/RUNS/R03-KORREKTUR/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json). Beide R02-Findings berechtigt und selbst korrigiert; unabhängiger Recheck offen. Neue kandidatengebundene Qualifikation `98ab3c0fc5c935019d81d6d6acb1423185cb4793`: **1294 Windows-Tests,61 gezielte Tests,21 Serverfälle und compileall PASS**. Serverada13b0 unverändert. Nächste Aktion: frische unabhängige Abnahme des ganzen PR einschließlich F01/F02; Paketbranch nach finaler Übergabe pausiert. Keine kanonische Übernahme oder AP030; Appkomposition CV2-100, Hardware/ASR später.

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
