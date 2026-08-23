# Arbeitsstruktur-Toolkit V2

Vorgesehener Zielpfad im Repository:

```text
/
├── AGENTS.md                       # bestehend -> Abschnitt wird angehängt; sonst neu
├── CLAUDE.md                       # bestehend -> Verweisabschnitt wird angehängt; sonst neu
├── .agents/
│   └── skills/
│       └── arbeitsstruktur/
│           ├── SKILL.md
│           └── scripts/
└── ARBEITSDATEIEN/
    ├── 00_STEUERUNG/
    ├── 10_AKTUELL/
    ├── 20_ZURUECKGESTELLT/
    └── 90_HISTORIE/
```

## Neu in V2

- `AGENTS.md` liegt im Repository-Root und wird **idempotent** verwaltet.
- Vorhandene `AGENTS.md` wird nicht überschrieben; der markierte Arbeitsstruktur-Abschnitt wird nur einmal angehängt.
- `CLAUDE.md` wird analog ergänzt/erstellt.
- `CLAUDE.md` verweist auf `AGENTS.md` und behandelt `.agents/` ausdrücklich wie `.claude/`.
- `PLANUNG/README.md` enthält nun:
  - Planungsleitfaden,
  - Standard für Arbeitspakete,
  - prüfbare Akzeptanzkriterien,
  - Validierungsregeln,
  - automatische Commit-Regel nach erfolgreichem AP,
  - Beispiel eines Implementierungsplans.
- Neues `Test-Arbeitsstruktur.ps1` validiert die repositoryweite Grundstruktur.
- Verlaufseinträge werden auf Feature-Branches nur lokal geführt und erst beim Abschluss/promoten in den globalen Verlauf übernommen.

## Beispiel

```powershell
# Einmalig bzw. idempotent Basis ergänzen
.\.agents\skills\arbeitsstruktur\scripts\Initialize-Arbeitsstruktur.ps1

# Repositoryweite Struktur prüfen
.\.agents\skills\arbeitsstruktur\scripts\Test-Arbeitsstruktur.ps1

# Arbeitsblock anlegen
.\.agents\skills\arbeitsstruktur\scripts\New-Arbeitsblock.ps1 `
  -Name "EINHEITLICHE_TRIGGERARCHITEKTUR" `
  -Title "Einheitliche Triggerarchitektur"

# Arbeitsblock prüfen
.\.agents\skills\arbeitsstruktur\scripts\Test-Arbeitsblock.ps1 `
  -Name "EINHEITLICHE_TRIGGERARCHITEKTUR"
```

Die Strukturverwaltungsskripte führen selbst keine Git-Commits oder Pushes aus. Der automatische Commit nach erfolgreichem Arbeitspaket ist eine dokumentierte Arbeitsregel für Implementierungsagenten.
