# Client V2 – AP-CV2-100 / R01 / REVIEW_READY, 2026-10-13

Aktiver Block CLIENT_V2. AP000 bis AP090 tatsächlich ACCEPTED, zuletzt `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`
über PR #11; unabhängiger PASS, menschlicher Prompt und Git-/PR-Provenienz
[gesichert](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP100 vollständig
selbstqualifiziert auf `work/client-v2/ap-cv2-100`; unabhängige Abnahme offen.

Tatsächlicher V2-Desktop-/Headlessprozess mit gemeinsamem Mirror, Settingsbootstrap,
Media, Controls, Results, Logs und Feedback. Qt-/Core-/Audio-/Clipboard-/LEDworkers
getrennt, profilgebundene Workerpersistenz/Hotkeyrollback und Shutdown getestet.
1573 Windows-/ 190 gezielte Tests und 17 komponierte Serverchecks
an 45 bytegeprüften ada13b0-Quellen PASS; compileall/diffcheck PASS.

[Paketakte](30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md), [Report](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/01_REPORT.md),
[Evidenz](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json),
[Planung](PLANUNG/README.md), [Runtimeinterfaces](../../../docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Nächste Aktion: vollständigen kumulativen Kandidaten unabhängig prüfen; Branch ab
Abgabe pausiert. Kein eigener ROOT_PASS, kein AP100-Mergeprompt, kein AP110-Start.
Server-Distributed sowie Build-/Crossrepo-/Hardware-/ASRgates bleiben offen.

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
