# Client V2 – AP-CV2-040 / CHANGES_REQUIRED, 2026-10-12

AP-CV2-030 ist tatsächlich ACCEPTED auf `3df342c3a7cacaa1226743c4d9bee674e94d33db` (PR #5, unabhängiger R02-PASS, menschliche Freigabe und Single-Parent-/Baumgleichheit: [Übernahmebeleg](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json)). AP-CV2-040 **CHANGES_REQUIRED** auf `work/client-v2/ap-cv2-040`, Parent `3df342c3a7cacaa1226743c4d9bee674e94d33db`. [R01-Report](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R01-UMSETZUNG/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json), [aktive Planung](PLANUNG/README.md).

Sessionlanger Audioflow, begrenzte PCMqueue, getrennte Audio-/LEDavailability und V2-Logbootstrap am bestehenden Capture-/Logpfad. 1367 Windows-Tests, 222 gezielte Tests, 41 echte Serverfälle mit 46 bytegeprüften Quellen sowie compileall/diffcheck PASS. Alle 23 Anforderungen einzeln belegt; unabhängige R02-Abnahme mit zwei Pflichtfindings abgeschlossen: [Abnahmebericht](30_AUSFUEHRUNG/AP-CV2-040/RUNS/R02-ABNAHME/01_REPORT.md).

Nächste Aktion: Korrektur der R02-Pflichtfindings F01/F02 im bestehenden Paket-PR; Schreibhoheit ab Übergabe pausiert. Appkomposition CV2-100, Settingsbootstrap CV2-070 und reale Mikrofon-/ASR-/Hardwarefälle bleiben ihren späteren Paketen zugeordnet. Serverbaseline ada13b0 unverändert, Server-Distributed offen. Start weiterhin `.\venv\Scripts\python.exe -m voice_stt_client`. Kein eigener ROOT_PASS, Merge oder Folgepaketstart.

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
