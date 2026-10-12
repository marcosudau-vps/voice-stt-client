# Client V2 – AP-CV2-030 / REVIEW_READY, 2026-10-12

AP-CV2-020 ist tatsächlich ACCEPTED auf `8fa0f829bece203e4a9d5ee0896dc9c4478f9fc0` (PR #4, R04-PASS, menschliche Freigabe und Baumgleichheit belegt). AP-CV2-030 **REVIEW_READY** auf `work/client-v2/ap-cv2-030`, Parent unverändert. [R01-Report](30_AUSFUEHRUNG/AP-CV2-030/RUNS/R01-UMSETZUNG/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json). Reiner Activation-/Segmentmirror und tatsächliche Transport-/Resyncanbindung;1339 Windows-Tests,106 gezielte Tests,35 Serverfälle/46 bytegeprüfte Quellen und compileall PASS. Alle35 Requirements einzeln belegt.

Nächste Aktion: frische unabhängige Abnahme des vollständigen Paket-PR. Schreibhoheit nach Übergabe pausiert. Appkomposition CV2-100, Audio-/Settingsservices CV2-040/070 und reale ASR-/Hardwarefälle später; Serverbaseline ada13b0 unverändert und Server-Distributed offen. Start weiterhin `.\venv\Scripts\python.exe -m voice_stt_client`. Kein eigener ROOT_PASS, Merge oder Folgepaketstart.

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
