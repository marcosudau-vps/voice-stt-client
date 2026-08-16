# LOGGING_GESAMTPLAN

Diese Mappe enthält den vollständigen Logging-/Observability-Implementierungsplan.

## Start

1. `00_NORMATIV/` — die **normative** Grundlage (Architektur, Contracts,
   Entscheidungen). Bei Widerspruch gewinnt sie.
2. `00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md`
3. `01_WORKPACKAGE_INDEX.md`
4. `03_TRACEABILITY_MATRIX.md`
5. das aktive Work Package unter `workpackages/`

`02_OBS000_FREEZE_CHECKLIST.md` ist abgeschlossen und dient nur noch als
Nachweis, wo welche Entscheidung gefallen ist.

## Stand

```text
G-OBS-000 PASS      2026-08-15
Run                 RUN-OBS-000-01_2026-08-15_CLAUDE
OBS-010, OBS-020    READY FOR IMPLEMENTATION
```

Der Plan ist **eingefroren**. Architekturentscheidungen sind geschlossen; eine
Implementierung wählt Details nur **innerhalb** der Verträge. Eine notwendige
Vertragsänderung ist ein `DECISION REQUIRED` — anhalten, begründen, in
`00_NORMATIV/LOGGING_DECISIONS_FREEZE_V1.md` nachtragen. Keine stille
Planänderung.

Eine weitere breite Logging-Voruntersuchung ist **nicht** vorgesehen. Gezielte
Codeprüfungen innerhalb eines Pakets bleiben erlaubt.

## Hinweis zur Doppelablage

Unter `05_DRAFTS_UNGEPRUEFT/LOGGING_GESAMTPLAN/` liegt eine byteidentische Kopie
des Ausgangszustands dieser Mappe. Maßgeblich ist **ausschließlich** die Fassung
hier unter `20_PLANUNG/`. Die Kopie ist veraltet, sobald dieser Plan fortgeführt
wird; sie sollte bei Gelegenheit nach `90_ARCHIV/` verschoben werden.
