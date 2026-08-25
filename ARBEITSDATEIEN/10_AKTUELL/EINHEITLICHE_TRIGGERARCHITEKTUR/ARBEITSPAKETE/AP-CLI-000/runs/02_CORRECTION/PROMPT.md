# Korrekturauftrag – AP-CLI-000 / Run 02_CORRECTION

Setze ausschließlich die Root-Befunde am bereits lokal commiteten
AP-CLI-000 um. Du arbeitest in derselben Claude-Code-Session und darfst keine
Subagents oder parallelen Claude-Läufe starten.

## Ausgangspunkt

- Branch: `feat/einheitliche-triggerarchitektur`
- Start-HEAD des AP: `db102fdc6dd70e4de798a363608d1e7412533dd7`
- zu amendender lokaler AP-Commit:
  `c369442d7ac8b432dd2e2c5bee829b09d99c8c08`
- kein Push

## Root-Befunde

`git diff --check db102fdc6dd70e4de798a363608d1e7412533dd7..HEAD`
meldet `new blank line at EOF` in:

1. `AP-CLI-000/README.md` Zeile 18;
2. `AP-CLI-000/runs/01_BASELINE/evidence/README.md` Zeile 5;
3. `AP-CLI-000/runs/01_BASELINE/ABNAHME.md` Zeile 6.

Korrigiere nur die ersten beiden Dateien. `ABNAHME.md` gehört ausschließlich
der Root-Endabnahme und bleibt unverändert; Root ersetzt dort anschließend den
Platzhalter.

## Abschluss

1. Entferne genau die beiden überzähligen Leerzeilen am Dateiende.
2. Fülle `runs/02_CORRECTION/REPORT.md` mit Befund, Änderung und Nachweis.
3. Prüfe die beiden Dateien mit einem auf sie begrenzten Range-`diff --check`.
4. Stage nur diese beiden Dateien und den Korrekturreport/-prompt.
5. Amendiere den vorhandenen AP-Commit mit `git commit --amend --no-edit`;
   erstelle keinen zweiten Commit.
6. Prüfe sauberen Working Tree und genau einen Commit seit Start-HEAD.
7. Führe keinen Push aus und ändere weder Produktcode noch Tests.
