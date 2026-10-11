# R05 – Evidenzindex

Getestete SHA `7c4bb2f7d3f3a79d0b2f0beae5bdbae27795d0fe`; Parent `050e776cf316eb332177294db0c0a2719c2b4415`. [Runreport](../01_REPORT.md), [Originalauftrag/Freigabe](../00_PROMPT_ORIGINAL.md).

- [Ausführungshelfer](fuehre_windows_nachweise.py): tatsächliche Befehle, eingefrorener sauberer Checkout, Windows-/Python-/Quellimportprüfung, vollständige Logs; kein Gittransport.
- [Runtime und Ergebnisse](windows-validation.json): Checkout, getestete SHA/Tree, unveränderter Produkt-/Teststand gegenüber R04, Laufzeit, Exitcodes und sauberer Endzustand.
- [Windows-Vollsuite](windows-full-unittest.txt): 1.233 PASS, keine Skips, einschließlich aller bestehenden OBS-/Feedback-/History-/Clipboard-/Build-/Trigger- und neuen Tests.
- [Unveränderte Windows-Originalbytes](windows-full-unittest.cp1252.txt): CP1252-Ausgabe; die oben verlinkte lesbare Fassung ist verlustfrei nach UTF-8 konvertiert. Original-/Text-SHA256 und bestätigter Textgleichheitsnachweis stehen im Runtime-JSON; kein Testresultat wurde verändert.
- [Startup-Profilrepros](startup-persistence.txt): fünf PASS; realer Profil-Dateischutz mit kontrollierten Backend-/Core-Fakes, keine physische Win32-/Mikrofonabnahme.
- [compileall](compileall.txt), [Diffprüfung](diff-check.txt).
- [Aktuelle Akten-/Linkprüfung](records-validation.json), [Skillprüfung](skill-validation.json) und [Scope-/Metadaten-/historische Unverändertheitsprüfung](scope-validation.json).
- [Vorbereitete PR-Kurzfassung](pr-body.md): ROOT_PASS, Nutzerfreigabe und aus Git aufzulösende finale Kandidatenidentität; im tatsächlichen PR nach Push aktualisieren.

Die abschließende CI und der gemergte PR sind online unter [PR #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2) sichtbar. Finale Git-/CI-/Squash-IDs können erst nach den jeweiligen Aktionen genannt werden; der Abschlussagent verifiziert Single-Parent, genau einen neuen Commit und Baumgleichheit. R01 bis R04 bleiben unverändert erhalten.
