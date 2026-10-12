# Client V2 – AP-CV2-050 / R01-UMSETZUNG / REVIEW_READY, 2026-10-12

AP-CV2-000 bis AP-CV2-040 sind **ACCEPTED**. AP040 wurde nach R06-PASS und menschlicher Freigabe tatsächlich in PR6 übernommen: kanonischer Parent `4eb1161eecf12aaf3c7bd7938f04fb4f95f8744f`. [Abschlussprovenienz](30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP-CV2-050 ist **REVIEW_READY**: quellenneutrale Controls, getrennte Runpausen mit sicherem Reconnectbootstrap und atomare Win32-Hotkeyrollen. [R01-Report](30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/01_REPORT.md), [Workflowstatus](WORKFLOW_STATUS.json), [öffentliche API](../../../docs/protocol-v2-controls.md).

**1397 Windowsgesamttests,297 gezielte Tests,79 tatsächliche Serverchecks/46 unveränderte Serverquellblobs und16 native Win32checks**, compileall/diffcheck PASS. Vollständige Logs/Runtime-/Gitblobbindung in der [Evidenz](30_AUSFUEHRUNG/AP-CV2-050/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md). Alle14 Requirements einzeln belegt, bis unabhängiger Abnahme CLIENT OPEN.

Nächste Aktion: frischer unabhängiger Review von AP050 auf dem vollständig veröffentlichten Paketbranch work/client-v2/ap-cv2-050, Base feat/client-v2. Umsetzer pausiert Änderungen/Pushes ab Übergabe. Kein eigener ROOT_PASS, Merge oder AP060-Start. Settingspersistenz/Dialog AP070/080, Appkomposition AP100 und reale Hardware/ASR AP-IV2-020 bleiben ihre geplanten Gates; Server-Distributed bleibt offen. Start `.\venv\Scripts\python.exe -m voice_stt_client` führt weiterhin die bisherige Appkomposition aus.

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
