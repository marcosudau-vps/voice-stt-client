# Client V2 – AP-CV2-060 / R01-UMSETZUNG / REVIEW_READY, 2026-10-12

AP-CV2-000 bis AP-CV2-050 sind **ACCEPTED**, zuletzt AP050 auf `ce95c66a7a3b4440faaa33289351871a040ebe19` nach unabhängigem PASS, menschlicher Freigabe und tatsächlicher PR7-Übernahme. [Abschlussbeleg](30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP-CV2-060 ist vollständig umgesetzt und selbstqualifiziert: UUID-Herkunft, verlustfreie V1-Historymigration, Prozessdedup und reservierte Ausgabe mit Crashstatus unknown. [Runreport](30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](30_AUSFUEHRUNG/AP-CV2-060/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](WORKFLOW_STATUS.json), [aktiver Arbeitsblock](README.md), [Planungseinstieg](PLANUNG/README.md).

1426 vollständige Windows-Tests, 323 gezielte Tests und 19 echte gepinnte Serverchecks PASS; compileall/diffcheck PASS. RESULT-01 bis RESULT-13 als Selbstchecks belegt, unabhängige Abnahme offen. **Nächste Aktion:** unabhängiges Review der eingereichten AP060-Spitze. Schreiben ab Übergabe pausiert; kein automatischer Merge oder Folgepaketstart. Settings AP070/080, Feedback AP090, Appkomposition AP100 und reale ASR-/Hardware-/Fokusabnahme AP-IV2-020 bleiben eigene Gates. Die gestartete App verwendet weiter die bestehende Komposition. [Result-API und Migration](../../../docs/protocol-v2-results.md).

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
