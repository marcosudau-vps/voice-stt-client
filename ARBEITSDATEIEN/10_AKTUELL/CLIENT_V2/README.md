# Client V2 – AP-CV2-100 / R03-ABNAHME / CHANGES_REQUIRED, 2026-10-13

Aktiver CLIENT_V2-Arbeitsblock. AP000 bis AP090 tatsächlich ACCEPTED; aktueller kanonischer Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`. Der kumulative [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12) wurde unabhängig auf Kandidat `4a35a2d7eba5fa55e79528744320419b8ec0a1b3` / Tree `18f7516471c97627b92e9221e24e367f30f5cd81` geprüft. **CHANGES_REQUIRED**: Finding `CV2-100-R03-F01`, strukturierte korrelierte Settings-Audits fehlen im neuen V2-Local-Apply-Pfad.

[R03-Report](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/01_REPORT.md), [R03-Evidenz](30_AUSFUEHRUNG/AP-CV2-100/RUNS/R03-ABNAHME/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json).

Extern qualifiziert: 1574 Windows-Tests und 203 gezielte PASS, 17 komponierte Client-/Serverchecks gegen 45 Quellen am Server `ada13b0`, finale [CI 38347923728](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38347923728) erfolgreich. Diese Nachweise ersetzen die noch nötige F01-Korrektur nicht.

Nächste Aktion: F01 im selben PR korrigieren, kandidatengebunden erneut qualifizieren und gesamte AP100-Linie frisch unabhängig prüfen. **Kein ROOT_PASS, kein Merge und kein AP110-Start.**

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
