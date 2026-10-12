# Client V2 – AP-CV2-040 / R06-ABNAHME / ROOT_PASS, 2026-10-12

AP-CV2-030 ist ACCEPTED auf `3df342c3a7cacaa1226743c4d9bee674e94d33db`. AP-CV2-040 ist **technisch ROOT_PASS**, Workflow **WAITING_FOR_APPROVAL** nach unabhängiger Abnahme des fachlichen Kandidaten `4ef7a13672bf7c50665e08f5eff837fb5d687419` (Tree `f670a6fce6557ff657644037964025e9f7f1ee1e`). [R06-ROOT_PASS](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R06-ABNAHME/01_REPORT.md); F01 und F02 vollständig geschlossen. 1378 Windows-Tests, 233 gezielte Tests, 52 echte Serverfälle/46 Serverquellen, 188/188 Git-Blobs und CI auf Kandidaten-SHA SUCCESS wurden als Fremdbelege unabhängig validiert. [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6) bleibt offen.

Nächste Aktion: ausdrücklicher menschlicher Übernahmeprompt mit aktuellem Docs-Head, canonical_parent und R06-PASS-Bericht; bis dahin **kein Merge und kein Start AP-CV2-050**. Reale Hardware-/ASR-Gates und Qt-/Settingskomposition bleiben späteren Paketen zugeordnet.


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
