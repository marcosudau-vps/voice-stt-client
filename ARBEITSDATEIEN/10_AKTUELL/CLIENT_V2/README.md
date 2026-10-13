# Client V2 – AP-CV2-100 / R04-KORREKTUR / REVIEW_READY, 2026-10-13

Aktiver CLIENT_V2-Block; AP000 bis AP090 tatsächlich ACCEPTED, kanonischer Parent
`dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Kandidatenbranch
`work/client-v2/ap-cv2-100`, [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12).

R03-[CHANGES_REQUIRED](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md) wurde auf dessen Dokumentenspitze c5a510f übernommen.
F01 im Selbstcheck korrigiert: V2-Local-Apply publiziert Started/Runtime/Completed
mit derselben settings-ID, korrekten Flags und Erfolgs-/Fehlerstatus auch bei
Persistenzfehler und Rollback. Busy, Core-Abweisung, Loggingausfall, Shutdown und
doppelte Completion sind geprüft. R03-Report bleibt unveränderte historische Quelle.

Neue Windows-Vollsuite1581 ohne Skips, gezielte210, 17 komponierte Serverchecks
gegen 45 bytegeprüfte ada13b0-Quellen, compileall/diffcheck PASS.
[R04-Report](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R04-KORREKTUR/EVIDENCE/INDEX.md), [Paketakte](30_AUSFUEHRUNG/AP-CV2-100/00_PAKET.md),
[Workflowstatus](WORKFLOW_STATUS.json), [Runtimeinterfaces](../../../docs/protocol-v2-runtime.md).
Start `.\venv\Scripts\python.exe -m voice_stt_client`; Headless `--headless`.

Tatsächliche Übergabe erst nach grüner CI des finalen PR-Heads. Danach frische
unabhängige Abnahme des gesamten kumulativen AP100 mit Fokus F01; Schreiben pausiert.
Kein eigener ROOT_PASS, kein Merge/AP110 ohne unabhängigen PASS, menschlichen Prompt
und tatsächliche kanonische Übernahme. Reale Hardware-/ASR-/Crossrepo-/abschließende
V2-Buildgates und Server-Distributed bleiben offen.

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
