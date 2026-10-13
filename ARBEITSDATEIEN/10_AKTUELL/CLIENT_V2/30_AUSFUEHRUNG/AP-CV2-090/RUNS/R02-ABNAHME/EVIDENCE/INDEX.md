# AP-CV2-090 / R02-ABNAHME – Evidenzindex

Review am 2026-10-13. **reviewed_sha** `51d20aa24b41a125acbf2a3cd50df1477eb0c79b`, **reviewed_tree** `d52aeda488d55b61b9d1c1d744ad0ab09fdf69d4`, **canonical_parent** `1bc5be893060e0d6a80e1d890102bfffebb73a17`, **server_sha** `ada13b011e1d3829f78e7f389e3b927795a2b3be`.

## Eigene read-only-Prüfungen

- PR-Metadaten/Base/Head/Status, kompletter Parentvergleich (3 Commits, 73 Dateien), commitgebundener Produkt-/Test-/Checkpointdiff; Skill, Akzeptanzkriterien und FB-Traceability.
- 13 relevante Kern-, UI-/OBS-, Test- und Runner-Gitblobs aus Head direkt gegen `qualifiedGitBlobs` im [R01-Windowsmanifest](../../R01-UMSETZUNG/EVIDENCE/windows-validation.json) abgeglichen: 13/13 PASS.
- R01-Originalprompt, Report, Windows-/Realtime-/Qt-Belege, Testmethoden, CI-Lauf, Paketstatus, Matrix/Manifest/Index und aktive Aktenverweise gegengeprüft. Neue R02-Dateien/Links werden gemeinsam in demselben rein administrativen Commit bereitgestellt; ältere Belege nicht geändert.
- Eigenständige Windowsvollsuite/HW: **NOT_RUN**; R01 Fremdausführung geprüft, nicht wiederholt.

## Im Umsetzungslauf tatsächlich ausgeführte und unabhängig geprüfte Belege

| Beleg | Nachweis | Ergebnis |
| --- | --- | --- |
| [R01-Report](../../R01-UMSETZUNG/01_REPORT.md), [Index](../../R01-UMSETZUNG/EVIDENCE/INDEX.md) | Qualifikation und Beweisgrenzen | PASS |
| [Windowsmanifest](../../R01-UMSETZUNG/EVIDENCE/windows-validation.json) | Runtime/Basis+Diff, Exitcodes, Source-/Loghashes | PASS |
| [Vollsuite](../../R01-UMSETZUNG/EVIDENCE/windows-full-unittest.txt) | 1552 Tests, OK, Exit0, keine Skips | PASS |
| [Gezielte Tests](../../R01-UMSETZUNG/EVIDENCE/targeted-unittest.txt) | 377 Tests, OK, Exit0, `-W error` | PASS |
| [Realer Checkpoint](../../R01-UMSETZUNG/EVIDENCE/server-feedback-checkpoint.json) | 18 PASS; Server-SHA/Quellhashes und explizite Adaptersimulation | PASS |
| [FB-Coverage](../../R01-UMSETZUNG/EVIDENCE/requirement-coverage.md) | FB-01 bis FB-09 mit echten Methodennamen/Fällen | PASS |
| [Publikationsprüfung](../../R01-UMSETZUNG/EVIDENCE/publication-verification.json) | 208 qualifizierte Gitblobs, 1163 Links, diffcheck PASS | PASS |
| [GitHub-CI](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38331762953) | Auf tatsächlichem `head_sha` / Base, ganze Suite/Build-/Wheelsmokes SUCCESS | PASS |

Bewertung und Scopebegrenzungen im [unabhängigen R02-Report](../01_REPORT.md). Offene Pflichtfindings: keine. Keine Produkt-/Test-/Kontraktänderung im Reviewlauf.
