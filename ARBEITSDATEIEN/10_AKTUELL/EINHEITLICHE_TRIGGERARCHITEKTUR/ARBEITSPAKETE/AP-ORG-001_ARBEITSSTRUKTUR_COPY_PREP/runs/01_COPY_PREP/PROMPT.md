# DOC-ARCH-002 – Arbeitsstruktur V2 einführen und Triggerbestand COPY-ONLY vorbereiten

## 0. Sicherheitsziel

Dieser Run ist ausdrücklich eine **COPY-ONLY-Migration** für den bestehenden Trigger-Arbeitsblock.

Der Agent darf im Trigger-Arbeitsblock **nichts löschen, nichts verschieben, nichts umbenennen und keine bestehende Datei überschreiben**, nur um die neue Struktur herzustellen.

Ziel ist:

1. repositoryweite Arbeitsstruktur auf `main` einführen;
2. bestehende Trigger-Unterlagen zusätzlich in die neue Zielstruktur **kopieren**;
3. vollständige Hash-/Pfadnachweise erzeugen;
4. alte Struktur vollständig unangetastet stehen lassen;
5. anschließend einen manuellen Review ermöglichen;
6. erst in einem späteren separaten Cleanup-Run alte Pfade entfernen.

### WICHTIG

Dieser Run ist NICHT die endgültige Bereinigung.

Nach erfolgreichem Abschluss existieren im Trigger-Arbeitsblock absichtlich:
- die alte Struktur,
- UND die neu aufgebaute Struktur parallel.

Das ist gewollt.

---

# 1. Verbotene Operationen im Trigger-Arbeitsblock

Im gesamten Trigger-Arbeitsblock sind in diesem Run verboten:

- `Move-Item`
- `Remove-Item`
- `git rm`
- Umbenennungen bestehender Dateien/Ordner
- Überschreiben bestehender Dateien
- `git reset --hard`
- `git clean`
- `git stash`
- Rebase
- Force-Checkout
- Force-Push
- blindes `git add -A`

Auch leere Altordner werden in diesem Run NICHT entfernt.

---

# 2. Session

Session-Startordner:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS`

Prompt:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS\DOC-ARCH-002_SAFE_COPY_ONLY_ARBEITSSTRUKTUR_EINFUEHRUNG_UND_TRIGGER_VORBEREITUNG.md`

Toolkit:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS\arbeitsstruktur_toolkit_v2.zip`

Checksum:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS\arbeitsstruktur_toolkit_v2.sha256.txt`

Standalone Main:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\main`

Trigger-Workspace:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

---

# 3. Bekannter Ausgangsstand

Bekannt nach WS-NORM-002:

- `main`: `f317d0b`
- Trigger-Branch: `feat/einheitliche-triggerarchitektur`
- bekannter Trigger-HEAD: `dd0af5e`

Diese Werte nur als Referenz verwenden und tatsächliche Stände zu Beginn prüfen.

Der Trigger-Workspace enthält bewusst lokale Änderungen und untracked Dateien. Der komplette tatsächliche Pre-Run-Status ist zu erfassen und zu schützen.

Bekannte Beispiele:

- modifiziert:
  `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/README.md`

- modifiziert:
  `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/20_PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`

- untracked:
  `.../namespace_system_model/NamespaceStruktur.md`

- untracked:
  `.../30_AUSFUEHRUNG/prompts/GATE_0/...`

Diese Liste ist nicht abschließend.

---

# 4. Preflight und Recovery-Sicherung

Vor jeder Änderung:

1. tatsächliche Branches, HEADs und Remotes erfassen;
2. `git status --porcelain=v2` für Main und Trigger sichern;
3. Trigger-Diff als Binary-Patch außerhalb des Worktrees sichern;
4. untracked Trigger-Dateien vollständig außerhalb des Worktrees kopieren;
5. SHA-256-Manifest aller vorhandenen Dateien im aktuellen Trigger-Arbeitsblock erzeugen.

Sicherungsziel:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS\DOC-ARCH-002_BACKUP\`

Mindestens:

```text
DOC-ARCH-002_BACKUP/
├── PRE_STATUS.txt
├── PRE_DIFF_BINARY.patch
├── PRE_UNTRACKED_FILES.txt
├── PRE_TRIGGER_TREE_SHA256.txt
└── untracked/
```

Wenn diese Sicherung nicht vollständig gelingt:

`COPY PREPARATION BLOCKED`

Keine weiteren Änderungen.

---

# 5. Toolkit prüfen

Checksum prüfen.

ZIP außerhalb aller Worktrees entpacken.

PowerShell-Skripte syntaktisch prüfen.

Keine Toolkit-Datei verändern.

---

# 6. Main: repositoryweite Arbeitsstruktur einführen

Diese Phase darf wie geplant im Standalone-Main-Clone durchgeführt werden.

Voraussetzung:
Main sauber.

## 6.1 Toolkit installieren

Kopiere:

`.agents/skills/arbeitsstruktur/`

in den Main-Repository-Root.

## 6.2 Initialize ausführen

`Initialize-Arbeitsstruktur.ps1`

Das Skript darf:
- Root-`AGENTS.md` erstellen oder seinen markierten Abschnitt ergänzen;
- Root-`CLAUDE.md` erstellen oder seinen markierten Abschnitt ergänzen;
- fehlende globale Arbeitsstrukturdateien ergänzen;
- `20_ZURUECKGESTELLT/README.md` anlegen.

Bestehende Dateien nicht überschreiben.

## 6.3 Validieren

`Test-Arbeitsstruktur.ps1`

PASS erforderlich.

## 6.4 Optional: Logging Teil B zurückgestellt abbilden

Nur wenn anhand bestehender Unterlagen eindeutig belegt, darf ein kleiner Arbeitsblock unter:

`ARBEITSDATEIEN/20_ZURUECKGESTELLT/LOGGING_OBSERVABILITY_TEIL_B/`

angelegt werden.

Keine Inhalte erfinden.

## 6.5 Main-Governance minimal aktualisieren

Nur sachlich notwendige Änderungen an:
- `CURRENT_STATE.md`
- `MASTERPLAN.md`
- `LOG_VERLAUF.md`
- `ARBEITSPROZESS.md`

Keine Behauptung, dass Trigger schon integriert oder implementiert sei.

## 6.6 Main committen

Commit:

`docs(project): introduce deterministic Arbeitsblock structure`

Push und CI prüfen.

---

# 7. Trigger: COPY-ONLY-Zielstruktur zusätzlich anlegen

Arbeitsort:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

WICHTIG:
Die bestehende alte Struktur bleibt vollständig stehen.

Äußerer Pfad:

`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/`

Zusätzlich anzulegende neue Bereiche:

```text
EINHEITLICHE_TRIGGERARCHITEKTUR/
├── STATUS.md
├── VERLAUF.md
├── PLANUNG/
│   ├── README.md
│   └── ...
├── IDEEN/
│   ├── README.md
│   └── ...
├── ARBEITSPAKETE/
│   ├── README.md
│   └── ...
└── QUELLEN/
    ├── README.md
    ├── RAW/
    └── REFERENZEN/
```

Bestehende Root-`README.md` NICHT überschreiben oder umschreiben.

---

# 8. COPY-ONLY-Zuordnung

Alle Quellpfade bleiben bestehen.

Die folgenden Inhalte werden **kopiert**, nicht verschoben.

## 8.1 `00_NORMATIV`

Aktuelle normative/Planungsunterlagen zusätzlich nach:

`PLANUNG/`

kopieren.

Quelle bleibt unangetastet.

## 8.2 `10_ANALYSE/CODE_ARCHITEKTUR_BASELINE`

Zusätzlich nach:

`PLANUNG/IST_ANALYSEN/CODE_ARCHITEKTUR_BASELINE/`

kopieren.

## 8.3 `10_ANALYSE/VORHERIGER_AGENTENSTAND_UND_AUDIT`

Zusätzlich nach:

`QUELLEN/REFERENZEN/VORHERIGER_AGENTENSTAND_UND_AUDIT/`

kopieren.

## 8.4 `20_PLANUNG/planung_migration`

Aktuelle Planungsdokumente zusätzlich nach:

`PLANUNG/`

oder sinnvolle Unterordner kopieren.

Die lokal modifizierte Datei

`01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`

muss in der Zielkopie exakt denselben aktuellen Working-Tree-Inhalt besitzen.

Quelle bleibt unverändert.

## 8.5 Namespace-Idee

`namespace_system_model/NamespaceStruktur.md`

zusätzlich kopieren nach:

`IDEEN/NamespaceStruktur.md`

Die Quelldatei bleibt stehen.

Die Zielkopie muss inhaltsidentisch sein.

Nicht als Projektwissen verwenden.

## 8.6 GATE_0

Bestehende GATE-0-Prompts zusätzlich in ein neues Arbeitspaket kopieren:

```text
ARBEITSPAKETE/
└── AP-TRG-000_GATE_0/
    ├── README.md
    ├── PLAN.md
    └── runs/
        └── ...
```

Bestehende Prompts unter `30_AUSFUEHRUNG/prompts/GATE_0/` bleiben stehen.

Keine Prompts ausführen.

## 8.7 LEGACY_NUMMERIERT

Zusätzlich kopieren nach:

`QUELLEN/REFERENZEN/ALTE_AGENTENAUFTRAEGE/`

## 8.8 BRANCH_MAINTENANCE

Zusätzlich kopieren nach:

`QUELLEN/REFERENZEN/BRANCH_MAINTENANCE_PROMPTS/`

sofern vorhanden.

## 8.9 Alte Evidence

`40_EVIDENCE/VOR_NEUEM_RUN_SYSTEM/`

zusätzlich kopieren nach:

`QUELLEN/REFERENZEN/EVIDENCE_VOR_NEUEM_RUN_SYSTEM/`

Nicht zippen.

## 8.10 Claude Snapshots

`90_ZWISCHENARCHIV/CLAUDE_SNAPSHOTS/`

zusätzlich kopieren nach:

`QUELLEN/RAW/CLAUDE_SNAPSHOTS/`

RAW / UNINDEXED.

---

# 9. Neue Standarddateien

## `STATUS.md`

Neu erzeugen.

Darf nur tatsächliche Fakten enthalten:
- Arbeitsblock
- Status AKTIV
- aktuelle Phase
- Branch
- HEAD
- letzter bestätigter Meilenstein
- geplante/aktive APs
- Blocker
- nächster Schritt
- Main→Trigger-Integration steht noch aus

## `VERLAUF.md`

Neu erzeugen.

Vorhandene eindeutig triggerbezogene Verlaufseinträge dürfen kopiert/übernommen werden, aber bestehende globale Verlaufsdateien nicht verändern.

Neuen COPY-ONLY-Migrationseintrag mit realem Zeitstempel ergänzen.

## `PLANUNG/README.md`

Standard aus Toolkit V2 verwenden.

## `IDEEN/README.md`

Standard-Agentensperre aus Toolkit V2 verwenden.

## `ARBEITSPAKETE/README.md`

Standard aus Toolkit V2 verwenden.

## `QUELLEN/README.md`

Kurz erklären:
- RAW = unbearbeitet / optional unindexiert
- REFERENZEN = historische oder unterstützende Artefakte
- nicht automatisch normativ
- gezieltes Lesen bei fachlichem Bedarf erlaubt
- keine prophylaktische Vollindexierung großer Rohquellen

---

# 10. Kein Test-Arbeitsblock gegen Altstruktur erzwingen

WICHTIG:

`Test-Arbeitsblock.ps1` betrachtet die alten Ordner absichtlich als im neuen Endmodell unzulässig.

Da dieser Run die alten Ordner bewusst NOCH stehen lässt, darf ein FAIL wegen weiterhin vorhandener Altordner NICHT als Migrationsfehler gewertet werden.

Stattdessen:

- neue Zielstruktur separat validieren;
- Pflichtdateien prüfen;
- SHA-256-Vergleich Source→Copy durchführen;
- dokumentieren, welche Altordner erst im späteren Cleanup entfernt werden.

Optional darf `Test-Arbeitsblock.ps1` ausgeführt werden, aber nur als **erwarteter Pre-Cleanup-Befund**. Der Report muss dann klar festhalten, dass der Fehler ausschließlich aus absichtlich verbliebenen Altordnern resultiert.

---

# 11. Migrations-/Copy-Mapping

Erzeuge:

`COPY_MAPPING.md`

mit:

| Quellpfad | Zielpfad | Aktion | Source SHA-256 | Target SHA-256 | Ergebnis |
|---|---|---|---|---|---|

Aktion in diesem Run ausschließlich:
- `COPY`
- `CREATE_NEW`
- `KEEP_UNTOUCHED`

Kein `MOVE`, `DELETE`, `RENAME`.

---

# 12. Schutz-Nachweis

Erzeuge nach der Copy-Phase erneut ein SHA-256-Manifest der ALTEN Quellstruktur.

Vergleiche mit `PRE_TRIGGER_TREE_SHA256.txt`.

Für alle Quellpfade, die in diesem Run nicht bewusst durch vorhandene lokale Benutzeränderungen sowieso verändert wurden, muss gelten:

**Source vor Run = Source nach Run**

Insbesondere bekannte geschützte Dateien müssen am ursprünglichen Pfad weiter vorhanden sein und denselben Inhalt besitzen wie vor der Copy-Phase.

---

# 13. Organisations-Arbeitspaket für den Run

Neu anlegen:

```text
ARBEITSPAKETE/
└── AP-ORG-001_ARBEITSSTRUKTUR_COPY_PREP/
    ├── README.md
    ├── PLAN.md
    └── runs/
        └── 01_COPY_PREP/
            ├── PROMPT.md
            ├── REPORT.md
            └── evidence/
```

Evidence mindestens:
- `PRE_STATUS.txt`
- `POST_STATUS.txt`
- `COPY_MAPPING.md`
- `PRE_TRIGGER_TREE_SHA256.txt`
- `POST_SOURCE_TREE_SHA256.txt`
- `TARGET_TREE_SHA256.txt`
- `STRUCTURE_TREE.txt`
- `VALIDATION.txt`
- `DELETE_CANDIDATES_FOR_MANUAL_REVIEW.md`

`DELETE_CANDIDATES_FOR_MANUAL_REVIEW.md` enthält nur Vorschläge für den späteren Cleanup.

NICHTS daraus in diesem Run löschen.

---

# 14. Trigger-Commit

Dieser Run darf die neu hinzugefügten COPY-Zielartefakte und das Organisations-Arbeitspaket committen.

Dabei dürfen die bereits vor dem Run vorhandenen lokalen modifizierten/untracked Quelldateien NICHT versehentlich als eigenständige neue Änderungen gestaged werden, sofern sie nicht ohnehin aufgrund ihrer neuen Zielkopien Bestandteil des neuen Pfads sind.

Kein `git add -A`.

Commit-Nachricht:

`docs(trigger): prepare Arbeitsblock structure without deleting legacy files`

Push auf den Trigger-Branch.

CI abwarten, sofern ausgelöst.

---

# 15. Noch kein Cleanup und kein Main→Trigger-Merge

Nach diesem Run ausdrücklich NICHT:

- alte Triggerordner löschen;
- alte Dateien entfernen;
- alte Struktur commit-seitig bereinigen;
- Main in Trigger mergen;
- Trigger nach Main mergen.

Nächster menschlicher Schritt:

1. Copy-Mapping und neue Struktur prüfen;
2. manuell entscheiden, welche Altpfade sicher gelöscht werden dürfen;
3. erst danach separaten Cleanup-Run erstellen.

---

# 16. Abschlussbericht

Neutral:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\SESSION_PROMPTS\DOC-ARCH-002_COPY_PREP_REPORT.md`

Versioniert zusätzlich im Organisations-Arbeitspaket.

Der Report muss ausdrücklich bestätigen:

- alte Quellstruktur vollständig erhalten;
- keine Datei gelöscht;
- keine Datei verschoben;
- keine bestehende Datei überschrieben;
- neue Struktur zusätzlich aufgebaut;
- Hash-Vergleich erfolgreich;
- Liste der späteren Löschkandidaten vorhanden;
- kein Main→Trigger-Merge.

Schlussurteil exakt:

`COPY-ONLY PREPARATION COMPLETE – READY FOR MANUAL CLEANUP REVIEW`

oder

`COPY-ONLY PREPARATION BLOCKED`
