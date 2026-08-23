# Plan – AP-ORG-001

## Scope

1. Toolkit-Checksum prüfen, ZIP außerhalb der Worktrees entpacken,
   Skripte syntaktisch prüfen.
2. Preflight-Sicherung von Branch, HEAD, Status, Diff und untracked Dateien
   des Trigger-Workspace außerhalb des Worktrees.
3. Main: Toolkit installieren, `Initialize-Arbeitsstruktur.ps1` und
   `Test-Arbeitsstruktur.ps1` ausführen, minimale Governance-Ergänzung
   (LOG_VERLAUF.md).
4. Trigger: neue Zielstruktur zusätzlich anlegen, bestehende Unterlagen
   per COPY (Source→Target-SHA-256 verglichen) übernehmen.
5. Schutz-Nachweis: SHA-256-Manifest der Altstruktur vor/nach dem Run
   vergleichen.
6. `COPY_MAPPING.md` und `DELETE_CANDIDATES_FOR_MANUAL_REVIEW.md`
   erzeugen.
7. Abschlussbericht in `SESSION_PROMPTS/DOC-ARCH-002_COPY_PREP_REPORT.md`.

## Nicht-Ziele

- Kein Main→Trigger-Merge.
- Kein Löschen, Verschieben, Umbenennen oder Überschreiben bestehender
  Dateien.
- Kein Commit, kein Push (in diesem Run per explizitem Auftrag
  ausgeschlossen).

## Akzeptanzkriterien

- [x] Toolkit-Checksum verifiziert.
- [x] Preflight-Backup vollständig (`PRE_STATUS.txt`, Binary-Diff,
      untracked-Kopien, SHA-256-Manifest).
- [x] `Test-Arbeitsstruktur.ps1` auf main: PASS (0 Fehler, 0 Warnungen).
- [x] Alle COPY-Ziele: Source-SHA-256 = Target-SHA-256 (82/82).
- [x] Alle 677 vorbestehenden Trigger-Dateien nach dem Run identisch zu
      vorher (0 Abweichungen).
- [x] Neue Pflichtdateien vorhanden.
- [x] `COPY_MAPPING.md` und `DELETE_CANDIDATES_FOR_MANUAL_REVIEW.md`
      erzeugt.

## Validierung

Siehe `runs/01_COPY_PREP/evidence/VALIDATION.txt`.

## Abschluss

Kein Commit in diesem Run (siehe Nicht-Ziele).
