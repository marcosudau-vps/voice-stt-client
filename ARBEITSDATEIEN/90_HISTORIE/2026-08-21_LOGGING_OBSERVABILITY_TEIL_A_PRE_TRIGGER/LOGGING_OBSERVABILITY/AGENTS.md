# AGENTS.md – AP_THEMA_LOGGING

## Zweck

Dieser Bereich steuert den Logging-/Observability-Workstream.

## Vor jeder Arbeit lesen

1. `START_HIER.md`
2. `20_PLANUNG/LOGGING_GESAMTPLAN/00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md`
3. das konkrete Work-Package
4. die im Prompt genannten Grundlagen

## Autorität

Reihenfolge bei Widersprüchen:

1. nach OBS-000 freigegebene Dateien in `00_NORMATIV/`
2. explizit freigegebene Entscheidungen/Contracts
3. aktives Work Package
4. realer Produktcode für Ist-Aussagen
5. aktuelle Codeanalysen
6. Tests als Evidence
7. historische/ungeprüfte Entwürfe

`05_DRAFTS_UNGEPRUEFT/` ist niemals automatisch normativ.

## Run-System

Jeder Agentenauftrag besitzt:

```text
Prompt: 30_AUSFUEHRUNG/prompts/PRM-...
Run:    30_AUSFUEHRUNG/runs/RUN-...
```

Im Run-Ordner mindestens pflegen:

- `RUN_REPORT.md`
- `OUTPUT_INDEX.md`

## Ablageregel

Arbeits-/Zwischenergebnisse des Runs → Run-Ordner.

Dauerhafte Artefakte nach fachlichem Zweck:

- Soll/Freigabe → `00_NORMATIV`
- Analyse → `10_ANALYSE`
- Planung → `20_PLANUNG`
- Evidence → `40_EVIDENCE`
- historisch/abgelöst → `90_ARCHIV`

Nicht dauerhaft nach Agentenname organisieren.

## Scope

Neue Funde nicht automatisch reparieren.

```text
Fund
→ dokumentieren
→ Blocker?
   ├─ ja: aktuelles WP
   └─ nein: späteres WP / Findings
```

## Git

Ohne ausdrückliche Freigabe verboten:

- Commit
- Push
- Merge
- Rebase
- Tag
- PR
- History Rewrite

## Abschluss eines Runs

`RUN_REPORT.md` enthält mindestens:

- Run-ID
- Work Package
- Ausgangszustand
- durchgeführte Arbeiten
- erzeugte/geänderte Dateien
- Entscheidungen
- offene Entscheidungen
- Tests/Evidence
- Blocker
- Gate-Empfehlung
- nächster Schritt
