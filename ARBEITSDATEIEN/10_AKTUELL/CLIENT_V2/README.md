# Client V2 – AP-CV2-070 / R01-UMSETZUNG / REVIEW_READY, 2026-10-12

Aktiver Arbeitsblock CLIENT_V2. AP000 bis AP060 **ACCEPTED**; tatsächliches AP060-Aggregat `473a75d02fb6d00e5664af4328dadaa44da5191a` auf feat/client-v2, Single-Parent und Treegleichheit sowie PASS/menschlicher Prompt [belegt](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP070 ist vollständig umgesetzt und zur unabhängigen Abnahme bereit, Branch `work/client-v2/ap-cv2-070`. Spätere Pakete bleiben PLANNED; Server-Distributed bleibt bis zum gemeinsamen Abschluss offen.

[Runreport](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-070/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json), [Planungseinstieg](PLANUNG/README.md), [Produktinterfaces](../../../docs/protocol-v2-settings.md).

Versionierte V1→V2-Migration mit Backup/Reparatur; dynamischer öffentlicher Wake-Katalog; serverautoritativer Settingsservice mit getrennten Wünschen/requested/effective/pending/unsupported und Revisionsräumen. Reconnectbootstrap bestätigt NA-Werte vor Audiofreigabe. NS-Noise/VAD bleibt nicht individuell startbar; Auswahl wirkt erst beim nächsten Hello. Keine Qt-/Credentialpersistenz, Appkomposition AP100.

Qualifikation: 1460 vollständige Windows-Tests, 243 gezielte Regressionstests, 38 echte HTTP/WS/Media/PCM-Checks und 55 gepinnte Settings-/Wake-Supplementtests ohne Skips; compileall/diffcheck PASS. 34 neue Clienttests. Empirische Wake-/ASR-/Hardwarequalifikation weiterhin AP-IV2-020, kein Nachweis optimaler Kalibrierung.

Nächste Aktion: unabhängiges AP070-Review des veröffentlichten PR-Heads und dieser Kandidatennachweise. Ab Übergabe Umsetzungsänderungen auf dem Paketbranch pausiert. ROOT_PASS und menschlicher Übernahmeprompt erforderlich; kein automatischer Merge/AP080. Runtime Python3.12 in Projektvenv; Testreproduktion über den Runner im Evidenzindex. Die reguläre App bleibt bis AP100 auf dem bisherigen Pfad.

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
