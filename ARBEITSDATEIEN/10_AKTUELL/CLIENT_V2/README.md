# Client V2 – AP-CV2-040 / R04-ABNAHME / CHANGES_REQUIRED, 2026-10-12

AP-CV2-030 ist ACCEPTED auf `3df342c3a7cacaa1226743c4d9bee674e94d33db` (kanonischer Parent). AP-CV2-040 ist **CHANGES_REQUIRED** nach unabhängigem R04-Review des R03-Korrekturkandidaten `7461577b1316ff113bac1c08ea7a836cf4b5023a`: [R04-Bericht](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R04-ABNAHME/01_REPORT.md). R02-F01 wurde geschlossen; der native Timeoutteil von R02-F02 wurde korrigiert, der Cancellation-Fall während des Task-Joins ist weiterhin offen. [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6).

Die R03-Qualifikation bleibt anerkannt: **1373 Windows-Tests, 228 gezielte Tests, 46 Serverfälle / 46 bytegeprüfte Quellen**, sämtliche 188 qualifikationsgebundenen Gitblobs identisch, CI Attempt 2 SUCCESS. Diese grünen Tests umfassen noch keinen Abbruch während des Task-Joins; es gibt daher keinen ROOT_PASS. Keine fachliche Planänderung oder neue Serverbaseline.

Nächste Aktion: **Korrektur von `CV2-040-R02-F02` im bestehenden Paket-PR**, gezielte Regression bei Cancellation während Task-Join, neue gültige Windows-/betroffene Serverqualifikation und erneute unabhängige Abnahme. `feat/client-v2`, Server-Distributed, Main, Tags und Releases bleiben unverändert. Kein Merge oder Start AP-CV2-050.

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
