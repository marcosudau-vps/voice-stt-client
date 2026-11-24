# Gültigkeit der technischen Release-Freigabe und Regressionstests

**Voice-STT-Client V2 – 24.11.2026 – AP-IV2-020/R06**

**GO mit dokumentierten, vom Auftraggeber akzeptierten Restrisiken.**

Die technische Anwenderabnahme ist für den in diesem Commit dokumentierten und gesicherten Produkt-/Teststand abgeschlossen. Die in der Bescheinigung und in der finalen Kriterienmatrix aufgeführten Funktionsbereiche sind in ihrem jeweils dokumentierten Prüfumfang umfassend getestet und freigegeben. Es bestehen keine offenen Anwenderabnahmeblocker. Die akzeptierten Teilnachweise und Restrisiken bleiben unverändert gültig; sie werden nicht in uneingeschränkte PASS-Nachweise umgedeutet.

## Eindeutige Zuordnung zum geprüften Stand

- Kanonischer Ausgangscommit: `9f9fdf2b19f99a6d4f255d76b6cfa9ef3de493b2`.
- Basis der R06-Korrekturen: `17fce388e747daf37b97e96ed1fcf6421338873d`.
- Nachweislich unveränderter Produkt-/Testdiff: SHA-256 gemäß Bericht 11 und `EVIDENCE/FORTSETZUNG_2026-11-23/continuation-provenance.json`.
- Geprüfte EXE SHA-256: `07cab945a8ca568f7a500a62a013a852e60e38a95a919b677453898539a205fe`.
- Final-Testserver-Commit: `e95858e3c010a7e9324b49bb44fee349abe7128a`.
- Git-Baumobjekte der geprüften Produkt-/Testverzeichnisse im aufnehmenden Commit:
  - `scripts/`: `1309a42d6da963e0c77d96e5034e8db115593889`
  - `tests/`: `81dee0f66ef3880ee5af42636df3053937d74f91`
  - `voice_stt_client/`: `d8b75cec9832d0557c2e6b4ebdba3a8de23ef69d`

Die PDF-Bescheinigung ist unverändert archiviert. Ihre Angabe zum damals noch nicht committeden lokalen Korrekturstand beschreibt den Zustand **zum Prüfzeitpunkt**. Durch die gemeinsame Sicherung der identischen Korrekturen und Abnahmedokumente wird dieser Stand jetzt im Repository reproduzierbar referenziert. Maßgeblich sind die Baumobjekte und der Commit, der dieses Dokument enthält; die EXE selbst wird nicht als Git-Binärdatei aufgenommen.

## Gültigkeit bei weiteren Änderungen

1. Unveränderte, nicht von einer Änderung betroffene Funktionsbereiche behalten ihre bestehende technische Freigabe. Eine vollständige erneute manuelle/akustische Endabnahme ohne relevanten Änderungsanlass ist nicht erforderlich.
2. Bei neuen Änderungen ist anhand des Diffs eine Auswirkungsanalyse vorzunehmen. Nur unmittelbar und mittelbar betroffene Funktionen, Schnittstellen, Abhängigkeiten sowie die erforderlichen Integrations-/Regressionstests sind gezielt erneut zu prüfen.
3. Änderungen an gemeinsamen Komponenten, Protokollen, Build-/Runtime-Abhängigkeiten, Sicherheitsgrenzen oder dem qualifizierten Serverstand können einen breiteren Prüfumfang erfordern. Die reguläre automatisierte CI, Build- und Release-Gates bleiben unberührt.
4. Neue Befunde sind mit dem neuen Commit, Prüfumfang und Ergebnis zu dokumentieren. Eine Änderung außerhalb der bestehenden Freigabe wird erst nach erfolgreichem erforderlichem Nachtest in den freigegebenen Stand einbezogen.

## Maßgebliche Unterlagen

- [PDF-Abnahmebescheinigung](Voice-STT-Client-V2_Abnahmebescheinigung_2026-11-24.pdf)
- [Abschlussbericht](27_ABSCHLUSS_ANWENDERABNAHME_2026-11-24.md)
- [Finale Kriterienmatrix](28_FINALER_ABNAHMESTATUS_2026-11-24.md)
- [Letzter Dauerlauf](26_WIEDERHOLUNG_FROZEN_DAUERLAUF_2026-11-24.md)

Die vorliegende Sicherung dokumentiert die ausdrückliche Freigabeentscheidung des Auftraggebers. Sie erzeugt keinen eigenständigen neuen ROOT_PASS oder GitHub-Release und behauptet keinen zusätzlichen unabhängigen Paketreview.
