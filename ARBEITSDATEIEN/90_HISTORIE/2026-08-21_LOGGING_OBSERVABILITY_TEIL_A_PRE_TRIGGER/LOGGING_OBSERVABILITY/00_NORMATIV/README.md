# 00_NORMATIV

Hier liegen ausschließlich freigegebene, finalisierte Sollartefakte.

Ein Entwurf wird **nicht** allein durch Verschieben in diesen Ordner normativ.
Der zugehörige `RUN_REPORT.md` muss die Freigabe-/Freeze-Entscheidung
dokumentieren.

---

## Aktueller Stand

`OBS-000` wurde am **2026-08-15** mit **PASS** abgeschlossen
(Run `RUN-OBS-000-01_2026-08-15_CLAUDE`).

| Datei | Inhalt |
|---|---|
| `LOGGING_ARCHITEKTUR_FREEZE_V1.md` | Invarianten, Endzustand, Komponenten, Nebenläufigkeit, Failure Domain, Hot-Path-Regeln, Zukunftsgrenzen |
| `LOGGING_CONTRACTS_FREEZE_V1.md` | CanonicalRecord, Normalizer, Redaction, SQLite-Schema, Query-Verträge, UI-Verträge, Konfiguration, Hookliste |
| `LOGGING_DECISIONS_FREEZE_V1.md` | Jede geschlossene Entscheidung mit Begründung; Widerspruchsregister; Korrektur der Work-Package-Grenzen |

Alle drei tragen im Frontmatter:

```text
status: FROZEN
authority: normative
workstream: OBS
freeze_gate: OBS-000
```

## Autorität

Bei Widerspruch gilt:

1. diese drei Dateien;
2. das aktive Work Package unter `20_PLANUNG/LOGGING_GESAMTPLAN/workpackages/`;
3. realer Produktcode für Ist-Aussagen;
4. die Analysen unter `10_ANALYSE/`;
5. die Entwürfe unter `00_GRUNDLAGEN/`.

`05_DRAFTS_UNGEPRUEFT/` ist niemals normativ.

## Änderungsregel

Nach dem Freeze sind Architekturentscheidungen eingefroren. Eine Implementierung
darf Details nur **innerhalb** der festgelegten Verträge wählen. Wird eine
Vertragsänderung nötig:

```text
DECISION REQUIRED
  -> anhalten
  -> im Run Report des Pakets begruenden
  -> in LOGGING_DECISIONS_FREEZE_V1.md nachtragen
  -> KEINE stille Planaenderung
```
