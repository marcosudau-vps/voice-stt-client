# START HIER – Logging / Observability

Diese Struktur ist so vorbereitet, dass **OBS-000 – Plan Freeze & Baseline** sofort mit Claude gestartet werden kann.

## Installation

Das ZIP **in diesen Ordner entpacken**:

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude\ARBEITSDATEIEN\
```

Im ZIP liegt bereits der Root-Ordner:

```text
AP_THEMA_LOGGING\
```

Falls `AP_THEMA_LOGGING` bereits existiert, die Ordner **zusammenführen**.  
Bestehende Dateien außerhalb dieser neuen Unterstruktur nicht löschen.

Danach liegt der Startprompt hier:

```text
ARBEITSDATEIEN\
AP_THEMA_LOGGING\
30_AUSFUEHRUNG\
prompts\
PRM-OBS-000-01_2026-08-15_PLAN_FREEZE.md
```

Diesen Prompt Claude geben.

---

# Struktur

```text
AP_THEMA_LOGGING/
├── START_HIER.md
├── AGENTS.md
│
├── 00_NORMATIV/
│   └── README.md
│
├── 00_GRUNDLAGEN/
│   ├── LOGGING_ZIELBILD_ARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md
│   ├── LOGGING_V1_ABGRENZUNG_ENTWURF.md
│   └── LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md
│
├── 05_DRAFTS_UNGEPRUEFT/
│   └── ErsterEntwurf_Logging.md
│
├── 10_ANALYSE/
│   └── CLAUDE_VORARBEIT/
│       └── README.md
│
├── 20_PLANUNG/
│   └── LOGGING_GESAMTPLAN/
│       ├── 00_LOGGING_GESAMTIMPLEMENTIERUNGSPLAN.md
│       ├── 01_WORKPACKAGE_INDEX.md
│       ├── 02_OBS000_FREEZE_CHECKLIST.md
│       ├── 03_TRACEABILITY_MATRIX.md
│       └── workpackages/
│
├── 30_AUSFUEHRUNG/
│   ├── prompts/
│   │   └── PRM-OBS-000-01_2026-08-15_PLAN_FREEZE.md
│   └── runs/
│       └── RUN-OBS-000-01_2026-08-15_CLAUDE/
│           ├── README.md
│           ├── RUN_REPORT.md
│           └── OUTPUT_INDEX.md
│
├── 40_EVIDENCE/
│   └── OBS-000/
│       └── README.md
│
├── 90_ARCHIV/
└── TOOLS/
    └── Check-OBS000-Workspace.ps1
```

---

# Wichtig zu den ganz frischen Claude-Dateien

Die folgenden Dateien wurden **nach** dem zuletzt gepackten `ARBEITSDATEIEN.zip` erzeugt und konnten deshalb hier nicht automatisch mitgeliefert werden:

```text
LOGGING_CODE_INTEGRATION_AUDIT.md
LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md
LOGGING_CONCURRENCY_FAILURE_MODEL.md
LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md
LOGGING_V1_IMPLEMENTATION_PLAN.md
LOGGING_OPEN_DECISIONS.md
LOGGING_TEST_MATRIX.md             # falls erzeugt
LOGGING_ADVERSARIAL_REVIEW.md
```

Der Startprompt weist Claude ausdrücklich an, diese Dateien im bestehenden Workspace rekursiv zu finden und geordnet nach:

```text
10_ANALYSE\CLAUDE_VORARBEIT\
```

zu **kopieren**, nicht die Originale zu löschen.

Du musst sie also vor dem Start nicht manuell zusammensuchen, solange sie im Workspace vorhanden sind.

Optional kannst du vorher aus `AP_THEMA_LOGGING` ausführen:

```powershell
.\TOOLS\Check-OBS000-Workspace.ps1
```

Das Skript zeigt nur an, welche Dateien gefunden bzw. nicht gefunden werden. Es verändert nichts.

---

# Autorität

- `00_GRUNDLAGEN` enthält wichtige **Entwürfe/Analysegrundlagen**, noch keine endgültig freigegebene Wahrheit.
- `05_DRAFTS_UNGEPRUEFT` ist ausdrücklich unverbindlich.
- `20_PLANUNG` enthält den aktuellen Gesamtplan.
- `00_NORMATIV` bleibt bis zum erfolgreichen OBS-000-Freeze bewusst leer.
- Erst bei `OBS-000 PASS` darf Claude die finalisierten Sollartefakte unter `00_NORMATIV` ablegen.

---

# Aktueller Lauf

```text
Workstream: OBS
Work Package: OBS-000
Run: RUN-OBS-000-01_2026-08-15_CLAUDE
Prompt: PRM-OBS-000-01_2026-08-15_PLAN_FREEZE.md
```
