# Client V2 – AP-CV2-080 / R01-UMSETZUNG / REVIEW_READY, 2026-10-12

Aktiver Arbeitsblock CLIENT_V2. AP000 bis AP070 **ACCEPTED**; AP070-Aggregat `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3` tatsächlich auf feat/client-v2, Single-Parent/Treegleichheit und unabhängiger PASS/menschlicher Prompt [belegt](30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP080 vollständig umgesetzt, unabhängige Abnahme offen. Branch `work/client-v2/ap-cv2-080`. Spätere Pakete PLANNED, Server-Distributed bleibt bis zum gemeinsamen Abschluss offen.

[Runreport](30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json), [Planungseinstieg](PLANUNG/README.md), [Produktinterfaces](../../../docs/protocol-v2-settings-ui.md).

V2-Trigger-/Session-/Serverdialog, getrennte requested/effective/pending-Werte, schemaabhängige Typen/Grenzen/Defaults/Applypolicies, öffentliche Wake-Mehrfachauswahl. Adminprüfung mit tatsächlichem No-change-PATCH; Windows Credential Manager originbezogen mit Create/Replace/Delete und Memory-only bei Ausfall. Reconnect verlangt ausdrückliche Activation-/Drainentscheidung; asynchrone Replies sind dialog-/generationgebunden.

Qualifikation: 1513 vollständige Windows-Tests, 296 gezielte Regressionstests, 53 neue Clienttests. Reale Serverchecks: UI27, native Windows-UI/Vault29, bestehende Settings38, Supplement55 ohne Skips. compileall/diffcheck und Akten-/Blobprüfung PASS. Vollständige Log-/Hash-/Kandidatenbindung im Evidenzindex.

Nächste Aktion: unabhängiges Review des endgültigen PR-Heads. Umsetzungsbranch ab Übergabe pausiert; kein automatischer Merge/AP090. ROOT_PASS und anschließender menschlicher Übernahmeprompt erforderlich. Reguläre Appkomposition samt koordinierter nativer Hotkey-Persistenz bleibt AP100; reale ASR/Mikrofon-/Wakekalibrierung AP-IV2-020. Die neue Oberfläche ist mit echten Produktionsservices lokal qualifiziert.

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
