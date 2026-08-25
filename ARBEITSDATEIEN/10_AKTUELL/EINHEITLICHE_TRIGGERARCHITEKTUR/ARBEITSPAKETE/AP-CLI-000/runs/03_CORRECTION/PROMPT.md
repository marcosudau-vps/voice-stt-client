# Korrekturauftrag – AP-CLI-000 / Run 03_CORRECTION

Bearbeite ausschließlich die folgenden Root-Review-Befunde in derselben
Claude-Code-Session. Starte keine Subagents und keinen parallelen Claude-Lauf.

## Ausgangspunkt

- AP-Start-HEAD: `db102fdc6dd70e4de798a363608d1e7412533dd7`
- zu amendender lokaler AP-Commit:
  `c8c0fea67bd8f3392e46d2ad997899c401c78f30`
- genau ein Commit, kein Push

## Befunde

1. Die neu ergänzten Baselinepassagen in `task.md` und `ÜBERGABE.md` nennen
   `./venv/Scripts/python.exe` beziehungsweise die Windowsform davon, obwohl
   dieser Worktree keine lokale venv besitzt und der Auftrag ausdrücklich die
   geteilte Umgebung
   `P:\GithubRepos\marcosudau-vps\voice-stt-client\main\venv\Scripts\python.exe`
   festlegt. Korrigiere nur die neuen AP-CLI-000-Passagen, nicht historische
   Betriebsbefehle. Korrigiere ebenso den Baseline-Testbefehl im Run-01-Report.
2. Die Source-Merge-Zuordnung im Run-01-Report schreibt die Umstellung des
   Feedback-Reducers allein `CLI-020` zu. Verbindlich ist die Trennung:
   serverseitige Source-/Admission-Semantik `SRV-010`, manuelle
   Command-/Hotkey-Semantik `CLI-020`, source-neutrales Feedback und die
   betroffenen Feedback-Reducer-Tests `CLI-040`. Korrigiere Abschnitt 4.5 und
   die neue AP-CLI-000-Zusammenfassung in `ÜBERGABE.md` entsprechend; andere
   gültige Folge-AP-Zuordnungen bleiben erhalten.

## Abschluss

- Dokumentiere Befund, Änderung und Nachweis in
  `runs/03_CORRECTION/REPORT.md`.
- Ändere keinen Produktcode und keine Tests; erneute Vollsuite ist für diese
  reine Dokumentkorrektur nicht erforderlich.
- Prüfe die geänderten Dateien und `git diff --check`.
- Stage nur die drei korrigierten Dokumente sowie Prompt/Report dieses Runs.
- Amendiere denselben AP-Commit mit `git commit --amend --no-edit`; kein
  zweiter Commit und kein Push.
- Lass `runs/01_BASELINE/ABNAHME.md` und alle früheren Originalprompts
  unverändert. Alle neu erzeugten Dateien sollen mit genau einem
  Zeilenumbruch, nicht mit einer Leerzeile, enden.
