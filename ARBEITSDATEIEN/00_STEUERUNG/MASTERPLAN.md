# MASTERPLAN

**Aktueller Unterlagenstand:** Revision 10 auf `feat/client-v2`, nach dem unveränderten Revision-9-Start bfade9d als ein ausdrücklich freigegebener Dokumentkorrekturcommit. [Freigabe und Ausnahmeumfang](../10_AKTUELL/CLIENT_V2/PLANUNG/EVIDENCE/VEROEFFENTLICHUNGSAUFTRAG_REV10.md), [Befundbewertung](../10_AKTUELL/CLIENT_V2/PLANUNG/EVIDENCE/BEWERTUNG_PRUEFBEFUNDE_REV10.md). AP-CV2-000 in R01 selbstqualifiziert; R02 unabhängige Abnahme: CHANGES_REQUIRED (nach R02) auf work/client-v2/ap-cv2-000, Parent 050e776cf316eb332177294db0c0a2719c2b4415. [Paketakte](../10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/00_PAKET.md). Nächste Aktion: Korrektur des unabhängigen Reviewfindings CV2-R02-F01 und neuer Windows-Vollreview; keine kanonische Übernahme oder Folgepaketfreigabe.

Stand 2026-10-11. Aktuell wird der Client anhand des vorläufigen Serverfinales auf V2 nachgezogen. Der vollständige eigenständige [Clientplan](../10_AKTUELL/CLIENT_V2/PLANUNG/README.md) und seine Paketfolge sind maßgeblich: CV2-000 bis CV2-110, dann IV2-010/020; Serverfixes nur bei belegtem Bedarf. Gemeinsame Abschlusslinie `feat/client-v2`: erster Commit nur Unterlagen, später ein Aggregat je Paket. Untergeordnete Paketbranches führen Bearbeitung, Planpflege und beauftragte Reviewunterlagen. Die vollständige Planrevision 10 ergänzt den erhaltenen Revision-9-Start durch eine ausdrücklich freigegebene Dokumentkorrektur; aktuelle Rollen-/Zustandsregeln liegen zusammen auf dem Feature-Branch. Paket-PRs und menschlich freigegebene Einzel-Squash-Merges führen die weitere Entwicklung; AP-CV2-000 bleibt offen.

Logging Teil A bleibt Foundation, Teil B bleibt nachgelagert. Server-Distributed bleibt bis zur gemeinsamen Qualifikation offen; keine automatische Serverfeature-/Main-/Releasepromotion. Die folgende frühere Reihenfolge bleibt als historischer Kontext erhalten.

Gemeinsamer Kurzauftrag: [Nächster Schritt](../10_AKTUELL/CLIENT_V2/PLANUNG/SKILLS/voice-stt-client-v2-naechster-schritt/SKILL.md). Rolle/AP aus dokumentiertem Stand selbst ermitteln; [Workflowstatus](../10_AKTUELL/CLIENT_V2/WORKFLOW_STATUS.json) mit offenen Paketlinien abgleichen. Zusätzliches unabhängiges Review bleibt ausdrücklich beauftragbar. AP-CV2-000 CHANGES_REQUIRED (nach R02); Umsetzer-Schreibrecht nach Übergabe pausiert. Kein PASS oder Übernahmeprompt vorhanden; R02-Report: CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R02-ABNAHME/01_REPORT.md.

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
