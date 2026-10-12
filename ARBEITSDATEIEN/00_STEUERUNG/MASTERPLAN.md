# Client V2 – AP-CV2-040 / R04-ABNAHME / CHANGES_REQUIRED, 2026-10-12

AP-CV2-030 ist ACCEPTED auf `3df342c3a7cacaa1226743c4d9bee674e94d33db` (kanonischer Parent). AP-CV2-040 ist **CHANGES_REQUIRED** nach unabhängigem R04-Review des R03-Korrekturkandidaten `7461577b1316ff113bac1c08ea7a836cf4b5023a`: [R04-Bericht](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-040/RUNS/R04-ABNAHME/01_REPORT.md). R02-F01 wurde geschlossen; der native Timeoutteil von R02-F02 wurde korrigiert, der Cancellation-Fall während des Task-Joins ist weiterhin offen. [PR #6](https://github.com/marcosudau-vps/voice-stt-client/pull/6).

Die R03-Qualifikation bleibt anerkannt: **1373 Windows-Tests, 228 gezielte Tests, 46 Serverfälle / 46 bytegeprüfte Quellen**, sämtliche 188 qualifikationsgebundenen Gitblobs identisch, CI Attempt 2 SUCCESS. Diese grünen Tests umfassen noch keinen Abbruch während des Task-Joins; es gibt daher keinen ROOT_PASS. Keine fachliche Planänderung oder neue Serverbaseline.

Nächste Aktion: **Korrektur von `CV2-040-R02-F02` im bestehenden Paket-PR**, gezielte Regression bei Cancellation während Task-Join, neue gültige Windows-/betroffene Serverqualifikation und erneute unabhängige Abnahme. `feat/client-v2`, Server-Distributed, Main, Tags und Releases bleiben unverändert. Kein Merge oder Start AP-CV2-050.

## Historischer Stand vor AP-CV2-020

# MASTERPLAN – AP-CV2-010

AP-CV2-000 tatsächlich CANONICALIZED/ACCEPTED auf `1cf076bd2ed56929b1a3780bc140da51348a8295` (PR #2; PASS und menschliche Freigabe vorhanden). Aktiver Auftrag AP-CV2-010, ROOT_PASS (R02); Workflow WAITING_FOR_APPROVAL auf `work/client-v2/ap-cv2-010`. [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json), [Paketakte](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-010/00_PAKET.md). Kein automatischer Folgepaketstart.

Die folgende datierte Steuerung bleibt Historie.

# MASTERPLAN

Stand 2026-10-11. [Aktiver Client-V2-Block](../10_AKTUELL/CLIENT_V2/README.md). **AP-CV2-000 ROOT_PASS / READY_FOR_CANONICALIZATION** nach R04-Produktreview und R05-Windows-Volltest (1233 PASS). [Abnahme/Freigabe](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R05-WINDOWS-NACHWEIS/01_REPORT.md), [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json).

Nächste Aktion: finale CI/Base050e776 prüfen und gemäß gesichertem Nutzerauftrag genau einen AP-CV2-000-Squash auf feat/client-v2 ausführen. Erst tatsächlicher Git-/PR-Nachweis gibt AP-CV2-010 frei; keine automatische Umsetzung. Der versionierte Stand bleibt vor Merge ROOT_PASS. Nach Merge kanonischen Abschluss aus Git/PR ableiten und auf dem nächsten Paketbranch nachführen.

[Planung/Rollen](../10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Nächster-Schritt-Skill](../10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md). Planrevision10, Rollenregelversion7: Windows-Vollsuite im Umsetzungslauf, ChatGPT-Reviewer prüft Code und gültige Belege ohne Pflichtwiederholung. Serverada13b0 bleibt Distributedreferenz; Logging/Feedback-Bestand und spätere reale Hardwaregates bleiben erhalten. Keine externe Arbeitsablage erforderlich.

Die folgende Vorfassung ist historische Provenienz, keine aktuelle Arbeitsanweisung.

---

## Historischer Masterplan

Aktuelle Reihenfolge:

1. Logging / Observability Teil A – Pre-Trigger Foundation
   - OBS-010, OBS-020, OBS-030, OBS-040, OBS-050, OBS-060
   - Status: `CONTROLLED CLOSED / ARCHIVED`
   - Formal: `G-OBS-V1 NOT PASSED`
   - Archiv: `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/`
   - Kanonische Produktdokumentation: `docs/observability/`
   - Abgeschlossen mit Run `OBS-CLOSE-001` (2026-08-23)
2. Einheitliche Triggerarchitektur
   - Status: `ACTIVE` — nächster aktiver Entwicklungsabschnitt des Gesamtprojekts.
   - Branch-Separation / Merge (PR #1) / Aufräumphase von Logging Teil A nach
     `main` ist abgeschlossen (`OBS-CLOSE-001/002`, `BS-001..003`,
     `WS-NORM-001`, `WS-NORM-002`); Logging Teil A ist damit Bestandteil der
     Main-Baseline.
   - Aktueller Stand: siehe `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/`
     (Phase 0 / GATE-0-Planung bzw. der zum jeweiligen Zeitpunkt tatsächlich belegte Stand)
   - Keine Trigger-Fachentscheidungen wurden durch `WS-NORM-001`/`WS-NORM-002`
     verändert; diese Runs sind rein organisatorisch.
3. Logging / Observability Teil B – Post-Migration
   - Status: `DEFERRED / BLOCKED BY TRIGGER ARCHITECTURE`
   - **Darf nicht vergessen werden.** Startet erst nach stabiler Umsetzung der
     einheitlichen Triggerarchitektur (Punkt 2).
   - Start: `OBS-100` – Post-Trigger Instrumentation
   - Danach: `OBS-110`, `OBS-120`, `OBS-130`, `OBS-140`, `OBS-150`, `OBS-160`,
     `OBS-170`, `OBS-180`
   - Planungsquelle (archiviert, vollständig erhalten):
     `ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/LOGGING_OBSERVABILITY/20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/WP-OBS-100_*.md`
     bis `WP-OBS-180_*.md`
   - Wiederaufnahmebedingung: Triggerarchitektur stabil umgesetzt bzw.
     entsprechender Masterplan-Meilenstein erreicht.
