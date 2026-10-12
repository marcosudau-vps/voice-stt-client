# Client V2 – AP-CV2-050 / R02-ABNAHME / ROOT_PASS, 2026-10-12

AP-CV2-000 bis AP-CV2-040 sind **ACCEPTED**, zuletzt AP040 auf `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f`. AP-CV2-050 hat nach unabhängigem Review **ROOT_PASS** für den Kandidaten `55d6ca6b4d222fac9bba66a4911c7a6b8c236a0a` (Tree `3b0dc469a1a3e577eb4dda0a67e2f3746b9c92cd`). [R02-Report](30_AUSFUEHRUNG/AP-CV2-050/RUNS/R02-ABNAHME/01_REPORT.md), [R01-Windowsbelege](30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md). 1397 Windows-, 297 gezielte, 79 lokale Server-/WebSocket- und 16 native Win32-Checks PASS als unabhängig geprüfte Fremdbelege; eigene Windows-Wiederholung NOT_RUN.

**Nächste Aktion:** ausdrückliche menschliche Übernahmefreigabe für [PR #7](https://github.com/marcosudau-vps/voice-stt-client/pull/7) abwarten. Kein automatischer Merge, kein AP060-Start. Settingspersistenz/Dialog AP070/080, Anwendungskomposition AP100 und reale ASR-/Hardwaregesamtabnahme AP-IV2-020 bleiben separate Gates. Die aktuell gestartete App nutzt weiterhin die bisherige Komposition.

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
