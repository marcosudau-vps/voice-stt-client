# Client V2 – AP-CV2-060 / R04-ABNAHME / ROOT_PASS, 2026-10-12

AP000 bis AP050 ACCEPTED; kanonischer Parent ce95c66. AP060: R02-CHANGES_REQUIRED wegen einzigem Finding CV2-060-R02-F01; in R03 ausschließlich den dokumentierten öffentlichen Klassennamen zu STTController korrigiert. [Korrekturreport](30_AUSFUEHRUNG/AP-CV2-060/RUNS/R03-KORREKTUR/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-060/RUNS/R03-KORREKTUR/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json), [Planungseinstieg](PLANUNG/README.md).

Produkt/Test/Config und die unabhängig geprüften 1426 Windows-/323 gezielten/19 Servernachweise unverändert. Neue lokale Vollsuite beim Docfix NOT_RUN, wie R02 ausdrücklich vorsieht. **Aktueller Stand: R04-ROOT_PASS / WAITING_FOR_APPROVAL.** F01 unabhängig geschlossen. **Nächste Aktion:** ausdrücklichen menschlichen Übernahmeprompt für PR #8 abwarten; kein Merge/AP070 ohne Freigabe. Appkomposition AP100 und reale Hardware/ASR/Fokusprüfung IV2-020 bleiben offen.

**Maßgeblicher aktueller Abnahmenachweis:** [R04-ROOT_PASS](30_AUSFUEHRUNG/AP-CV2-060/RUNS/R04-ABNAHME/01_REPORT.md) auf `1d81bb0230cfc5a099b7870488f6b42cd4735d5a`. R01-Testbelege und R03-Dokumentkorrektur bleiben unverändert; keine menschliche Übernahmefreigabe.

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
