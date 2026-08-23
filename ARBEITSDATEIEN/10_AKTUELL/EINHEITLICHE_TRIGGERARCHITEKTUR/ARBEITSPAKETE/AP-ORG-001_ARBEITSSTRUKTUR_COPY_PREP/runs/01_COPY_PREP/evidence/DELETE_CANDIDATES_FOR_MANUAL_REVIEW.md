# Löschkandidaten für späteren, separaten Cleanup-Run

**WICHTIG: Dies ist ausschließlich eine Vorschlagsliste für den manuellen Review.**
**In diesem Run wurde NICHTS davon gelöscht, verschoben, umbenannt oder überschrieben.**

Alle unten genannten Pfade existieren nach diesem Run unverändert weiter.
Eine endgültige Löschentscheidung setzt voraus, dass die jeweilige Kopie in
der neuen Struktur inhaltlich geprüft und für ausreichend befunden wurde.

| Alter Pfad | Ersetzt durch (neue Kopie) | Hinweis |
|---|---|---|
| `00_NORMATIV/` | `PLANUNG/00_NORMATIV/` | 1 Datei, SHA-256 identisch |
| `10_ANALYSE/CODE_ARCHITEKTUR_BASELINE/` | `PLANUNG/IST_ANALYSEN/CODE_ARCHITEKTUR_BASELINE/` | 8 Dateien, SHA-256 identisch |
| `10_ANALYSE/VORHERIGER_AGENTENSTAND_UND_AUDIT/` | `QUELLEN/REFERENZEN/VORHERIGER_AGENTENSTAND_UND_AUDIT/` | 7 Dateien, SHA-256 identisch |
| `20_PLANUNG/planung_migration/` (inkl. `namespace_system_model/`) | `PLANUNG/planung_migration/` | 5 Dateien, SHA-256 identisch; enthält die lokal modifizierte `01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md` – Kopie besitzt denselben aktuellen Working-Tree-Inhalt |
| `20_PLANUNG/planung_migration/namespace_system_model/NamespaceStruktur.md` | `IDEEN/NamespaceStruktur.md` | zusätzlich einzeln kopiert; **Zielkopie ist ausdrücklich kein Projektwissen** (IDEEN-Agentensperre) |
| `30_AUSFUEHRUNG/prompts/GATE_0/` | `ARBEITSPAKETE/AP-TRG-000_GATE_0/runs/00_QUELLPROMPTS/` | 1 Datei, SHA-256 identisch; AP wurde noch nicht ausgeführt |
| `30_AUSFUEHRUNG/prompts/LEGACY_NUMMERIERT/` | `QUELLEN/REFERENZEN/ALTE_AGENTENAUFTRAEGE/` | 6 Dateien, SHA-256 identisch |
| `30_AUSFUEHRUNG/prompts/BRANCH_MAINTENANCE/` | `QUELLEN/REFERENZEN/BRANCH_MAINTENANCE_PROMPTS/` | 1 Datei, SHA-256 identisch |
| `40_EVIDENCE/VOR_NEUEM_RUN_SYSTEM/` | `QUELLEN/REFERENZEN/EVIDENCE_VOR_NEUEM_RUN_SYSTEM/` | 49 Dateien, SHA-256 identisch |
| `90_ZWISCHENARCHIV/CLAUDE_SNAPSHOTS/` | `QUELLEN/RAW/CLAUDE_SNAPSHOTS/` | 3 Dateien, SHA-256 identisch |

## Nicht Teil der COPY-Zuordnung dieses Runs (unklarer Status)

Diese Pfade wurden in diesem Run weder kopiert noch bewertet und sind daher
**nicht** als Löschkandidaten vorgeschlagen. Sie benötigen im nächsten
Review eine eigene Entscheidung, ob und wohin sie noch übernommen werden
sollen, bevor über eine Löschung nachgedacht wird:

- `05_GRUNDLAGEN/`
- `15_DRAFTS_UNGEPRUEFT/`
- `30_AUSFUEHRUNG/runs/`
- `50_TOOLS/`

## Voraussetzung für den späteren Cleanup-Run

1. Menschlicher Review dieser Liste und von `COPY_MAPPING.md`.
2. Stichprobenhafte oder vollständige inhaltliche Prüfung der neuen Kopien.
3. Erst danach: separater, ausdrücklich als Cleanup deklarierter Auftrag,
   der Löschen/Verschieben/Umbenennen erlaubt.
