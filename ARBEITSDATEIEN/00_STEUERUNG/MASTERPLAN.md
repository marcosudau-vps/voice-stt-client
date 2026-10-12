# Client V2 – AP-CV2-080 / R01-UMSETZUNG / REVIEW_READY, 2026-10-12

Aktiver Arbeitsblock CLIENT_V2. AP000 bis AP070 **ACCEPTED**; AP070-Aggregat `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3` tatsächlich auf feat/client-v2, Single-Parent/Treegleichheit und unabhängiger PASS/menschlicher Prompt [belegt](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json). AP080 vollständig umgesetzt, unabhängige Abnahme offen. Branch `work/client-v2/ap-cv2-080`. Spätere Pakete PLANNED, Server-Distributed bleibt bis zum gemeinsamen Abschluss offen.

[Runreport](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/01_REPORT.md), [Evidenz](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-080/RUNS/R01-UMSETZUNG/EVIDENCE/INDEX.md), [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json), [Planungseinstieg](../10_AKTUELL/CLIENT_V2/PLANUNG/README.md), [Produktinterfaces](../../docs/protocol-v2-settings-ui.md).

V2-Trigger-/Session-/Serverdialog, getrennte requested/effective/pending-Werte, schemaabhängige Typen/Grenzen/Defaults/Applypolicies, öffentliche Wake-Mehrfachauswahl. Adminprüfung mit tatsächlichem No-change-PATCH; Windows Credential Manager originbezogen mit Create/Replace/Delete und Memory-only bei Ausfall. Reconnect verlangt ausdrückliche Activation-/Drainentscheidung; asynchrone Replies sind dialog-/generationgebunden.

Qualifikation: 1513 vollständige Windows-Tests, 296 gezielte Regressionstests, 53 neue Clienttests. Reale Serverchecks: UI27, native Windows-UI/Vault29, bestehende Settings38, Supplement55 ohne Skips. compileall/diffcheck und Akten-/Blobprüfung PASS. Vollständige Log-/Hash-/Kandidatenbindung im Evidenzindex.

Nächste Aktion: unabhängiges Review des endgültigen PR-Heads. Umsetzungsbranch ab Übergabe pausiert; kein automatischer Merge/AP090. ROOT_PASS und anschließender menschlicher Übernahmeprompt erforderlich. Reguläre Appkomposition samt koordinierter nativer Hotkey-Persistenz bleibt AP100; reale ASR/Mikrofon-/Wakekalibrierung AP-IV2-020. Die neue Oberfläche ist mit echten Produktionsservices lokal qualifiziert.

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
