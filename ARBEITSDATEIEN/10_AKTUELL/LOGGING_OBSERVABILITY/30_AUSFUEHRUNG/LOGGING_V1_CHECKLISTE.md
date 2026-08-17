# Logging V1 – Fortschrittscheckliste

Diese Datei ist die zentrale kompakte Fortschrittsanzeige für Logging V1.

## Status

- [x] OBS-000 – Plan Freeze / Architekturfreigabe

- [ ] OBS-010 – Canonical Model & Contracts – Implementierung
- [x] OBS-010 – Gate Review

- [x] OBS-020 – Ingress, Health & Redaction – Implementierung
- [x] OBS-020 – Gate Review

- [x] OBS-030 – Queue, Worker, SQLite & Retention – Implementierung
- [x] OBS-030 – Gate Review

- [ ] OBS-040 – Server Live Adapter & Client Observation Hooks – Implementierung
- [ ] OBS-040 – Gate Review

- [ ] OBS-050 – Local Query, Minimal UI & Settings – Implementierung
- [ ] OBS-050 – Gate Review

- [ ] OBS-060 – V1 Hardening, Evidence & Baseline – Implementierung
- [ ] OBS-060 – Logging V1 Final Gate

## Abschlusskriterium

- [ ] `G-OBS-V1 PASS – LOGGING V1 COMPLETE`

## Regel für Agentenläufe

Jeder abgeschlossene Implementierungs- oder Gate-Auftrag aktualisiert diese Datei selbst:

1. den gerade erfolgreich abgeschlossenen Punkt auf `[x]` setzen,
2. bei FAIL/BLOCKED den Punkt **nicht** abhaken,
3. unter `Aktuell` den nächsten zulässigen Schritt eintragen,
4. keine anderen historischen Häkchen verändern.

## Aktuell

**Abgeschlossen:** OBS-030 – Gate Review II (unabhängiger Re-Review, frische
Session, 2026-08-17) → `OBS-030 GATE PASS – OBS-040 MAY PROCEED`.
Geprüft wurde der tatsächliche Repositoryzustand — Code, `git diff`/
`git status`, eigene Testläufe mit beiden Runnern, eigene Fault-Injection-
und Laufzeitproben sowie ein Vergleichslauf gegen einen aus `b363346` frisch
ausgepackten Baum — nicht die Abschluss-, Korrektur- oder Cleanup-Berichte.
B-1, B-2 und B-3 sind geschlossen; W-1, W-2, W-4, W-5, W-7 korrigiert und
nachgemessen; W-3 als benannte Lücke und W-6 als OBS-050-Scope bestätigt,
ohne einen neuen Zähler zu verlangen. Die offene Auslegungsfrage zu
`ARCH §8.3` „nur verwerfen und zählen" ist **aus dem bestehenden Freeze
entschieden** (Variante 1: `ARCH §5` friert den `FAILED`-Zweig als reines
`return False` ein, `§8.3` referenziert Zähler statt sie zu definieren,
`§8.5 GRENZE 3` benennt den Totalverlust nach Workerausfall ausdrücklich als
Architektureigenschaft und nicht als Mangel) — **kein neuer Zähler, keine
Freeze-Änderung, kein DECISION-REQUIRED-Bedarf für die Abnahme**.
`00_NORMATIV/` ist byte-identisch zu `b363346`.
Teststand: 129 OBS-030-Tests grün (`pytest` **und** `unittest`), 331 Tests
OBS-010+020+030, volle Suite 843 passed / 1 Fehlschlag, dessen Vorbestand
gegen einen sauberen `b363346`-Baum nachgewiesen ist (dort 714 passed / 1
identischer Fehlschlag; Differenz exakt die 129 neuen Tests).
Ein lokaler Commit für den geprüften OBS-030-Endstand wurde erstellt.
Evidence: `40_EVIDENCE/OBS-030/GATE-REVIEW-02_2026-08-17_CLAUDE/`.

**Läuft als Nächstes:** OBS-040 – Server Live Adapter & Client Observation
Hooks (Implementierung, frische Session). Readiness geprüft: keine Blocker.
Mitzunehmen sind die nicht-blockierenden Beobachtungen N-1 bis N-5 des
Gate-Reviews (insbesondere N-1 `logging.record_rejected` und N-4 Übergabe des
Managers an `DesktopApplication` für OBS-050).

**OBS-040 MAY PROCEED.**

## Hinweis zum Ablageort dieser Datei

Diese Datei lag vor dem Korrekturlauf im Arbeitsbaum gelöscht vor, während im
nicht versionierten Verzeichnis
`30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` eine **leere** Zweitfassung
liegt. Wiederhergestellt wurde der kanonische Pfad mit den bisherigen
Häkchen; die Zweitfassung wurde nicht angefasst. Ein bewusster Umzug in das
V2-Verzeichnis ist offen (siehe
`runs/RUN-OBS-030-02_2026-08-17/RUN_LOG.md`, Abschnitt 6).
