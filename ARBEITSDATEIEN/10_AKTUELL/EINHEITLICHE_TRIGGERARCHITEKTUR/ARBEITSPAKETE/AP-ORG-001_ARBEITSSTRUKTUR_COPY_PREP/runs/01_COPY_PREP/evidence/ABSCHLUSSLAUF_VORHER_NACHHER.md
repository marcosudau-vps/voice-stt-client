# DOC-ARCH-002 Abschlusslauf – Vorher/Nachher-Nachweis

## Nur kopiert (COPY-PREP-Run, 23.08.2026)

82 Dateien hash-verifiziert in die neue Struktur kopiert, alte Struktur
zu diesem Zeitpunkt vollständig unangetastet. Details:
`COPY_MAPPING.md` im Arbeitsblock-Root, `evidence/PRE_TRIGGER_TREE_SHA256.txt`
und `evidence/POST_SOURCE_TREE_SHA256.txt`.

## Anschließend bereinigt (Abschlusslauf, 24.08.2026)

### Schritt 1 – Cleanup der Altstruktur im Trigger-Branch (Commit `6b073de`)

10 gemappte Altpfade entfernt (git erkannte sie als Renames, Historie
bleibt erhalten):

- `00_NORMATIV/` → `PLANUNG/00_NORMATIV/`
- `10_ANALYSE/CODE_ARCHITEKTUR_BASELINE/` → `PLANUNG/IST_ANALYSEN/CODE_ARCHITEKTUR_BASELINE/`
- `10_ANALYSE/VORHERIGER_AGENTENSTAND_UND_AUDIT/` → `QUELLEN/REFERENZEN/VORHERIGER_AGENTENSTAND_UND_AUDIT/`
- `20_PLANUNG/planung_migration/{00_README_ROTER_FADEN,15_OFFENE_FUNDE_UND_AENDERUNGSLOG,16_TRACEABILITY_MATRIX}.md` → `PLANUNG/planung_migration/...`
- `20_PLANUNG/planung_migration/namespace_system_model/NamespaceStruktur.md` → gelöscht (Kopien existierten bereits in `PLANUNG/planung_migration/namespace_system_model/` und `IDEEN/NamespaceStruktur.md`)
- `30_AUSFUEHRUNG/prompts/GATE_0/` → gelöscht (Kopie in `ARBEITSPAKETE/AP-TRG-000_GATE_0/QUELLPROMPTS/`)
- `30_AUSFUEHRUNG/prompts/LEGACY_NUMMERIERT/` (6 Dateien) → `QUELLEN/REFERENZEN/ALTE_AGENTENAUFTRAEGE/`
- `30_AUSFUEHRUNG/prompts/BRANCH_MAINTENANCE/` → gelöscht (Kopie in `QUELLEN/REFERENZEN/BRANCH_MAINTENANCE_PROMPTS/`)
- `40_EVIDENCE/VOR_NEUEM_RUN_SYSTEM/` (49 Dateien) → `QUELLEN/REFERENZEN/EVIDENCE_VOR_NEUEM_RUN_SYSTEM/`
- `90_ZWISCHENARCHIV/CLAUDE_SNAPSHOTS/` → gelöscht (Kopie in `QUELLEN/RAW/CLAUDE_SNAPSHOTS/`, gitignored)

4 zusätzliche, nie gemappte, nachweislich leere Altordner entfernt:
`05_GRUNDLAGEN/`, `15_DRAFTS_UNGEPRUEFT/`, `50_TOOLS/`, `30_AUSFUEHRUNG/`
(inkl. leerem `runs/`).

Vor jeder Löschung wurden alle 82 COPY-Paare live erneut auf
Hash-Identität geprüft (82/82 unverändert).

### Schritt 2 – Main→Trigger-Merge (Commit `6370eef`)

`origin/main` (`1b432c9`) in den Trigger-Branch integriert. Dabei
reaktivierte git durch Rename-/Add-Add-Heuristiken unerwartet 73 Dateien
an genau den Alt-Pfaden, die in Schritt 1 gerade entfernt worden waren –
weil `main` unabhängig eine eigene Teilkopie derselben alten Struktur am
selben Pfad besaß, die am gemeinsamen Merge-Vorfahren nicht existierte.

Für alle 73 Dateien wurde vor der erneuten Entfernung verifiziert, dass
ihr Inhalt (nach CRLF/LF-Normalisierung) exakt der bereits vorhandenen
kanonischen Kopie unter `PLANUNG/`/`QUELLEN/` entspricht:

- Erste Stichprobe von 66 Dateien: 39 SHA-256-identisch ohne
  Normalisierung, 27 identisch erst nach CRLF/LF-Normalisierung (reine
  Zeilenenden-Differenz, kein inhaltlicher Unterschied).
- Weitere 7 durch git-Rename-Kollateral zusätzlich reaktivierte Dateien
  (u. a. `20_PLANUNG/planung_migration/{00_README_ROTER_FADEN,...}.md`,
  drei weitere `LEGACY_NUMMERIERT`-Prompts): ebenfalls nach
  CRLF/LF-Normalisierung inhaltlich identisch zur kanonischen Kopie
  verifiziert.
- 0 von 73 Dateien mit echtem inhaltlichem Unterschied.

Alle 73 wurden anschließend erneut entfernt; die zugehörigen, nun
leeren Verzeichnisse (`00_NORMATIV/`, `10_ANALYSE/`, `40_EVIDENCE/`,
`30_AUSFUEHRUNG/prompts/LEGACY_NUMMERIERT/` u. a.) wurden ebenfalls
entfernt.

## Erhalten (bewusst, mit Begründung)

- `20_PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`:
  lokal modifizierte, uncommittete Produktarbeit; nicht Teil dieses
  Organisationslaufs. Kopie mit identischem damaligem Stand liegt
  zusätzlich unter `PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`.
- `README.md` (Arbeitsblock-Root): lokal modifiziert, uncommittete
  Produktarbeit; nur die toten Pfadverweise wurden korrigiert (siehe
  `VERLAUF.md`), der Rest bleibt unangetastet und uncommitted.

## Entstandene Commits

| Repo | Commit | Inhalt |
|---|---|---|
| `main` | `1b432c9` | Arbeitsstruktur-Toolkit, `Test-Arbeitsblock.ps1`-Bugfix |
| `main` | (push) | `origin/main` aktualisiert: `e564f9c..1b432c9` |
| Trigger | `6b073de` | Neue Struktur + Cleanup der 10 gemappten Altpfade + 4 leere Altordner |
| Trigger | `6370eef` | Merge `origin/main` (Konfliktauflösung, erneute Bereinigung der 73 reaktivierten Duplikate) |
| Trigger | `5463eaf` | Kleinkorrektur: `VERLAUF.md`-Zeitstempelformat |

## Validierung nach Abschluss

- `git status --short`: nur `README.md` und
  `01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md` uncommitted (bewusst).
- `git diff --check`: keine echten Fehler.
- Keine Merge-Konfliktmarker repositoryweit.
- `Test-Arbeitsstruktur.ps1` (main): PASS, 0/0.
- `Test-Arbeitsblock.ps1` (Trigger): 1 dokumentierter, bewusster Fehler
  (`20_PLANUNG` – enthält die erhaltene Produktdatei), 0 Warnungen.
- Vollständige Client-Test-Suite (1191 Tests, identisch zu CI): PASS.
- `python -m compileall`: PASS.
