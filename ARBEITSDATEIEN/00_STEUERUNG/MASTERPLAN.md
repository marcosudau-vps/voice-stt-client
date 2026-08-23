# MASTERPLAN

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