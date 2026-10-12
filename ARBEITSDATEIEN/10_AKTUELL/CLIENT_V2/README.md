# Client V2 – AP-CV2-040 / R05-KORREKTUR / REVIEW_READY, 2026-10-12

AP-CV2-030 ist tatsächlich ACCEPTED auf `3df342c3a7cacaa1226743c4d9bee674e94d33db`, dem unveränderten kanonischen Parent. AP-CV2-040 **REVIEW_READY** nach Korrektur des R04-Restbefunds F02. [R05-Report](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R05-KORREKTUR/01_REPORT.md), [R04-Abnahme](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R04-ABNAHME/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json).

F01 ist unabhängig CLOSED_R04. F02 wurde mit Cancellation beim Sender-/Lifecycle-Join und beim Logclose reproduziert. Logcleanup umfasst jetzt alle Shutdown-Awaits; ausstehende Task-/Logjoins bleiben begrenzt und retrybar. Neue Qualifikation: **1378 Windows-Tests, 233 gezielte Tests, 52 echte Serverfälle / 46 bytegeprüfte Quellen**, compileall/diffcheck PASS. Alle 23 Requirements neu belegt; R01–R04-Akten unverändert erhalten. [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6).

Nächste Aktion: frische unabhängige Abnahme des gesamten R05-Kandidaten mit F02-Recheck. Kein eigener ROOT_PASS oder eigene Findingschließung. Paketbranch `work/client-v2/ap-cv2-040` ab Übergabe pausiert. Qt-/Settingskomposition CV2-100/070 und echte Hardware/ASR bleiben spätere Gates; Serverada13b0/Distributed unverändert. Start `.\venv\Scripts\python.exe -m voice_stt_client`. Kein Merge oder Folgepaketstart.

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
