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

- [x] OBS-040 – Server Live Adapter & Client Observation Hooks – Implementierung
- [x] OBS-040 – Gate Review

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

**Abgeschlossen:** OBS-040 – Server Live Adapter & Client Observation Hooks,
Implementierung (2026-08-17, Run `RUN-OBS-040-01_2026-08-17`) →
`OBS-040 IMPLEMENTED – READY FOR REVIEW`.

Entstanden sind die zwei in `ARCH §5.1` eingefroren vorgesehenen Module
`adapters/server_live.py` und `adapters/client_events.py`, der Fan-out-Hook in
`core/session_coordinator.py` nach `CONTRACTS §7.1` (je erste Anweisung in
`_handle_event`/`_handle_control`, rückgabewertfrei, `except Exception`), der
zweite Beobachtungspunkt für Protokollfehler nach FD-R3 und 42 Recordtypen aus
`CONTRACTS §12` in elf Produktdateien, umgesetzt in der `§12.6`-Reihenfolge nach
aufsteigendem Risiko. Der Gate-Befund **N-1 ist geschlossen**:
`logging.record_rejected` existiert jetzt. Der Hot Path erhöht ausschließlich
`int`-Zähler; das 5-Sekunden-Aggregat erzeugt nach `ARCH §8.6` der **Worker**,
der die Zähler über eine read-only-Registry liest.

**Der wichtigste Nachweis des Pakets (N-07) ist erbracht:** ein werfender
Beobachter verändert weder den Rückgabewert von `_handle_event` noch den
Cursorstand — gemessen mit dem **echten** `EventProtocolProcessor` und dem
**echten** `EventCursorStore` auf einer temporären Datei, ohne jedes Double.

Neun Entscheidungen, alle aus dem bestehenden Freeze auflösbar: **kein
`DECISION REQUIRED`**, **kein neuer Zähler** in `LoggingHealthSnapshot`, **kein
normatives Dokument verändert**. Teststand: 115 neue Tests, `-k obs040` 115/115
grün unter `pytest` **und** `unittest`, OBS-010+020+030+040 446 grün, volle
Suite 958 passed / 1 vorbestehender, umgebungsbedingter Fehlschlag
(`lefx.interfaces`, außerhalb des Diffs). **Kein bestehender Test geändert.**
`git diff --check` leer, 16 Dateien +1324/−57, kein Cross-Workstream-Diff.
Ende-zu-Ende-Diagnoseskript gegen echten Manager und echten SQLite-Store:
P-1 bis P-7 alle PASS, exit 0. Evidence:
`40_EVIDENCE/OBS-040/RUN-01_2026-08-17/`.

**Kein Gate-PASS in diesem Run** — laut Work Package erfordert das Gate einen
separaten Review in frischer Session.

**Abgeschlossen:** OBS-040 – Gate Review (unabhängiger Review, 2026-08-17) → `OBS-040 GATE PASS – OBS-050 MAY PROCEED`.
Geprüft wurde der tatsächliche Repositoryzustand. Die Isolationsfähigkeit des Observers (N-07) ist durch Unit-Tests mit fehlerinjeziertem Ingress (`ExplodingIngress`) umfassend nachgewiesen und intakt. Der `session_coordinator.py`-Diff ist minimal und verletzungssicher. Die Compat-Logik ist frei von fehleranfälliger Reflection. Der Fan-out verhält sich vollständig passiv. Recordtypen und -inhalte (Auslegungen A-1 bis A-6, Hot-Path-Aggregat, Record-Inhalte) entsprechen exakt den normativen Vorgaben. `logging.record_rejected` ist korrekt implementiert. Der Diff enthält keine Vorgriffe. Alle 115 neuen Tests passieren erfolgreich. Ein lokaler Commit für den geprüften OBS-040-Endstand wurde erstellt.

**Läuft als Nächstes:** OBS-050 – Local Query, Minimal UI & Settings – Implementierung

Mitzunehmen für spätere Pakete: N-4 (Übergabe des **Managers** an
`DesktopApplication`) und `apply_config` aus `CONTRACTS §10.4` → OBS-050;
N-2, N-3 und die W-3-Lücke → OBS-060.

## Hinweis zum Ablageort dieser Datei

Diese Datei lag vor dem Korrekturlauf im Arbeitsbaum gelöscht vor, während im
nicht versionierten Verzeichnis
`30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/` eine **leere** Zweitfassung
liegt. Wiederhergestellt wurde der kanonische Pfad mit den bisherigen
Häkchen; die Zweitfassung wurde nicht angefasst. Ein bewusster Umzug in das
V2-Verzeichnis ist offen (siehe
`runs/RUN-OBS-030-02_2026-08-17/RUN_LOG.md`, Abschnitt 6).
