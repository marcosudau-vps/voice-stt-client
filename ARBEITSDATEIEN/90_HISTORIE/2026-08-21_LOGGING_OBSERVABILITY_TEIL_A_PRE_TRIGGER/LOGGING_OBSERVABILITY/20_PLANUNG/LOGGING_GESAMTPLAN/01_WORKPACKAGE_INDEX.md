# Work-Package Index – Logging / Observability

**Stand:** 2026-08-15, nach `G-OBS-000 PASS`
(Run `RUN-OBS-000-01_2026-08-15_CLAUDE`)

## Statuswerte

```text
DONE   abgeschlossen, Gate bestanden
READY  Scope, Contracts und Tests sind eingefroren; Implementierung darf
       beginnen, sobald die Abhaengigkeit erfuellt ist
DRAFT  Scope steht, aber Details werden erst nach der Vorgaengerstufe
       praezisiert
```

## Teil A – vor der Triggerarchitektur-Migration

| ID | Titel | Phase | Status | Abhängigkeit |
|---|---|---|---|---|
| OBS-000 | Plan Freeze & Baseline | 0 | **DONE** | – |
| OBS-010 | Canonical Model, Redaction, Normalizer & Contracts | A | **READY** | OBS-000 |
| OBS-020 | Ingress, Backpressure, Health & Python-Logging-Handler | A | **READY** | OBS-010 |
| OBS-030 | Worker, SQLite-Store, Retention & JSONL-Sink | A | DRAFT | OBS-010, OBS-020 |
| OBS-040 | Server Live Adapter & Client Observation Hooks | A | DRAFT | OBS-020, OBS-030 |
| OBS-050 | Local Query, Log View & Settings | A | DRAFT | OBS-030 |
| OBS-060 | V1 Hardening, Failure/Perf Gate & Baseline | A | DRAFT | OBS-040, OBS-050 |

**OBS-040 und OBS-050 sind voneinander unabhängig** und können parallel laufen
(Entscheidung `FD-S1`: kein Ringbuffer, der Live-Modus benutzt die
Provider-Schnittstelle).

## Teil B – nach Stabilisierung der Triggerarchitektur

| ID | Titel | Phase | Status | Abhängigkeit |
|---|---|---|---|---|
| OBS-100 | Post-Trigger Instrumentation | B | DRAFT | Trigger-Migration |
| OBS-110 | Server Control, Admin Auth & Capabilities | C | DRAFT | OBS-060 |
| OBS-120 | Remote Server History & Global Logs | C | DRAFT | OBS-110 |
| OBS-130 | Serverweite Admin-Settings | C | DRAFT | OBS-110 |
| OBS-140 | LED-Controller Logging Integration | D | DRAFT | OBS-060 |
| OBS-150 | Erweiterte Sinks / Storage Backends | D | DRAFT | OBS-060 |
| OBS-160 | Advanced Query / UX | E | DRAFT | OBS-120 |
| OBS-170 | Cross-Source Correlation / Forensics | E | DRAFT | OBS-100, OBS-120, OBS-140 |
| OBS-180 | Final Hardening, Docs & Acceptance | Final | DRAFT | alle relevanten |

## Abbildung auf den Nummernkreis des V1-Implementierungsplans

Der V1-Implementierungsplan unter `10_ANALYSE/CLAUDE_VORARBEIT/` benutzt einen
feineren Nummernkreis `OBS-00 … OBS-13`. **Maßgeblich ist der Nummernkreis
dieses Index.** Verbindliche Abbildung:

| dieser Index | V1-Plan |
|---|---|
| OBS-010 | OBS-00, OBS-01 + die Protokolle aus OBS-04/09/12 |
| OBS-020 | OBS-02, OBS-03, OBS-06 |
| OBS-030 | OBS-04, OBS-05, OBS-12 |
| OBS-040 | OBS-07, OBS-08 |
| OBS-050 | OBS-09, OBS-10, OBS-11 |
| OBS-060 | OBS-13 |

Begründung der zwei Titelkorrekturen und der Reihenfolgeanpassung:
`00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md §8`.

## Vorbedingung vor Beginn von OBS-010

Der Arbeitsbaum von `voice-stt-client` trägt 22 nicht committete Änderungen.
Vor OBS-010 ist dieser Zustand festzuschreiben — durch einen Commit oder durch
die ausdrückliche Bestätigung, dass der Baum unverändert bleibt. Details in
`40_EVIDENCE/OBS-000/EV-03_PRODUKT_BASELINE_GIT.md`.
