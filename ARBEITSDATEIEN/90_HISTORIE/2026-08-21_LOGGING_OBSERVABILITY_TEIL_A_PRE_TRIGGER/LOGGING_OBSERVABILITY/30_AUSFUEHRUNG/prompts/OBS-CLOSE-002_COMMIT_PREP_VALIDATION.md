# OBS-CLOSE-002 – Commit-Vorbereitung und abschließende Git-Validierung

## 0. Auftrag

Bereite den bereits abgeschlossenen Run `OBS-CLOSE-001` technisch für einen **isolierten Logging-Abschlusscommit** vor und validiere den vollständigen Git-Index.

Dieser Run ist ausschließlich:

- Staging,
- Git-Diff-/Scope-Prüfung,
- Commit-Vorbereitung,
- Dokumentation des finalen Commit-Inhalts.

Es dürfen **keine neuen fachlichen Änderungen** am Logging, an der Triggerarchitektur oder am Produktcode vorgenommen werden.

Es darf **noch kein Commit und kein Push** erfolgen.

Am Ende soll eindeutig feststehen, ob der vorbereitete Index:

`READY TO COMMIT`

ist oder ob konkrete Abweichungen als:

`DECISION REQUIRED`

vorliegen.

---

# 1. Ausgangslage

Repository:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Branch:

`feat/einheitliche-triggerarchitektur`

Ausgangs-HEAD:

`9f136c3b61cfd687af4f1ac4f82b2b7abaf43f41`

Der Run `OBS-CLOSE-001` wurde bereits durchgeführt.

Sein Ergebnis:

- Logging / Observability Teil A wurde nach `90_HISTORIE` verschoben.
- Die bereits zuvor getrackten Logging-Dateien wurden durch `git mv` verschoben und sind deshalb bereits staged.
- Neue Archivartefakte und Produktdokumentation sind teilweise noch untracked.
- `CURRENT_STATE.md`, `LOG_VERLAUF.md` und `MASTERPLAN.md` sind noch unstaged geändert.
- Vorbestehende Triggerarchitektur-Änderungen dürfen **nicht** Teil des Logging-Commits werden.

---

# 2. Unveränderbare Scope-Grenze

Der geplante Commit darf ausschließlich Änderungen aus folgenden Bereichen enthalten:

```text
ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md
ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md
ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md

ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/**

ARBEITSDATEIEN/90_HISTORIE/
2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/**

docs/observability/**
```

Der alte Pfad unter `10_AKTUELL/LOGGING_OBSERVABILITY/**` erscheint dabei
zulässigerweise als Quelle von Deletes/Renames.

## Explizit verboten im Staging

Nichts aus:

```text
ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/**
app.py
core/**
ui/**
tests/**
```

Insbesondere müssen folgende bereits vor `OBS-CLOSE-001` vorhandenen
Triggeränderungen **unstaged/untracked** bleiben:

```text
ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/
20_PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md

ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/README.md

ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/
20_PLANUNG/planung_migration/namespace_system_model/**

ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/
30_AUSFUEHRUNG/prompts/GATE_0/**
```

Diese Dateien nicht verändern, nicht verschieben und nicht stagen.

---

# 3. Keine inhaltlichen Reparaturen

Dieser Run darf keine bestehenden Projekt-/Arbeitsdateien inhaltlich
„verbessern“.

Erlaubt sind ausschließlich:

- korrektes Staging der bereits entstandenen OBS-CLOSE-001-Artefakte,
- Erzeugung des in Abschnitt 8 geforderten Validierungsberichts.

Falls bei der Prüfung ein fachlicher, dokumentarischer oder struktureller
Fehler entdeckt wird:

**nicht eigenmächtig korrigieren.**

Stattdessen:

`DECISION REQUIRED`

im Bericht dokumentieren.

---

# 4. Zuerst Baseline erfassen

Vor jeglichem neuen `git add` erfassen:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff --cached --stat
```

Zusätzlich den bereits gestagten Bestand prüfen.

Es ist erwartet, dass zahlreiche Logging-Dateien als staged Renames `R`
auftreten.

Das ist aufgrund des bereits erfolgten `git mv` korrekt.

---

# 5. Fehlende Logging-Abschlussartefakte gezielt stagen

Ergänze zum bereits staged vorhandenen Logging-Move ausschließlich:

```powershell
git add -- `
  "ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md" `
  "ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md" `
  "ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md" `
  "ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER" `
  "docs/observability"
```

Keine breiten Befehle wie:

```text
git add .
git add -A
git add --all
```

verwenden.

Kein `git add -f`.

Die aufgrund von `*.zip` ignorierten ZIP-Pakete bleiben bewusst
unversioniert.

Sie müssen nicht Bestandteil des Commits werden.

---

# 6. Commit-Scope anschließend maschinell validieren

Nach dem Staging den vollständigen Index prüfen.

## 6.1 Triggerarchitektur darf nicht staged sein

Prüfe:

```powershell
git diff --cached --name-only -- `
  "ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR"
```

Erwartung:

**keine Ausgabe**

Falls dort irgendeine Datei erscheint:

- keinen Commit vorbereiten,
- nichts selbst zurücksetzen,
- Bericht auf `DECISION REQUIRED` setzen.

## 6.2 Vorbestehende Triggeränderungen müssen weiter vorhanden sein

Prüfe separat:

```powershell
git status --short -- `
  "ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR"
```

Erwartet sind weiterhin insbesondere:

- die zwei modified Dateien als **unstaged**,
- `namespace_system_model/**` als untracked,
- `prompts/GATE_0/**` als untracked.

Dokumentiere deren tatsächlichen Status.

Sie dürfen nicht verschwunden und nicht staged sein.

## 6.3 Allowlist für den gesamten Index

Ermittle sämtliche staged Pfade.

Jeder staged Pfad muss genau einer der folgenden Gruppen zuordenbar sein:

```text
ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md
ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md
ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md

ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/**

ARBEITSDATEIEN/90_HISTORIE/
2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/**

docs/observability/**
```

Jeden staged Pfad außerhalb dieser Allowlist als Fehler behandeln.

Keine automatische Korrektur durchführen.

---

# 7. Technische Abschlussprüfung

Mindestens ausführen:

```powershell
git diff --cached --stat
git diff --cached --name-status
git diff --cached --check
git status --short
```

Zusätzlich prüfen:

### Steuerungsdateien

Im staged Diff sicherstellen:

- `CURRENT_STATE.md` ist der kompakte neue Snapshot.
- `LOG_VERLAUF.md` enthält ausschließlich den erwarteten neuen
  OBS-CLOSE-001-Meilenstein zusätzlich zur bisherigen Historie.
- `MASTERPLAN.md` enthält:
  - Logging Teil A abgeschlossen/archiviert,
  - `G-OBS-V1 NOT PASSED`,
  - Triggerarchitektur aktiv,
  - Logging Teil B deferred,
  - Einstieg `OBS-100`.

Keine inhaltliche Änderung vornehmen, falls etwas unerwartet ist;
stattdessen dokumentieren.

### Archiv

Prüfen, dass staged vorhanden sind:

- Archiv-`README.md`
- `STEUERUNG_SNAPSHOT/README.md`
- `STEUERUNG_SNAPSHOT/LOG_VERLAUF.md`
- `STEUERUNG_SNAPSHOT/CURRENT_STATE.md`
- `STEUERUNG_SNAPSHOT/MASTERPLAN.md`
- Run `RUN-OBS-CLOSE-001_2026-08-23`
- dessen `RUN_REPORT.md`
- dessen `OUTPUT_INDEX.md`
- die uncommitteten Logging-Prompts aus OBS-CLOSE-001
- Produktdokumentationsbestände unter `80_DOCS`
- rekonstruierte Datei
  `13_HEALTH_BACKPRESSURE_FAILURE_ISOLATION.md`

### Produktdokumentation

Unter `docs/observability/` müssen staged vorhanden sein:

- `MANIFEST.json`
- `README.md`
- sämtliche laut Manifest erwarteten Kapitel,
- insbesondere `13_HEALTH_BACKPRESSURE_FAILURE_ISOLATION.md`.

### Produktcode

Verifizieren, dass **keine** staged Änderungen aus:

```text
app.py
core/**
ui/**
tests/**
```

vorliegen.

---

# 8. Validierungsartefakt erzeugen

Erstelle:

```text
ARBEITSDATEIEN/90_HISTORIE/
2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/
LOGGING_OBSERVABILITY/
30_AUSFUEHRUNG/
runs/
RUN-OBS-CLOSE-002_2026-08-23/
COMMIT_PREP_REPORT.md
```

Der Bericht muss kompakt, aber vollständig enthalten:

## Baseline

- Branch
- HEAD
- Stagingzustand vor diesem Run

## Durchgeführtes Staging

- welche Pfadgruppen ergänzt wurden
- ausdrückliche Bestätigung, dass kein `git add .`, `-A` oder `-f`
  verwendet wurde

## Scope-Prüfung

- Anzahl staged Dateien/Pfade
- Ergebnis der Allowlist-Prüfung
- Ergebnis der Trigger-Exclusion-Prüfung
- Status der vier vorbestehenden Triggeränderungen

## Diff-Prüfung

- `git diff --cached --stat`
- Ergebnis `git diff --cached --check`
- Anzahl Renames
- Anzahl neuer Dateien
- Anzahl geänderter Dateien
- ggf. Deletes

Keine hunderte Pfade vollständig in den Fließtext kopieren.

Wenn sinnvoll, eine kompakte Zusammenfassung nach Pfadgruppen geben.

## Inhaltliche Stichprobe

Ergebnis der gezielten Prüfung von:

- `CURRENT_STATE.md`
- `LOG_VERLAUF.md`
- `MASTERPLAN.md`
- Archiv-README
- Produktdokumentations-Manifest

## Ignorierte ZIP-Dateien

Bestätigen:

- physisch weiterhin vorhanden,
- wegen `*.zip` ignoriert,
- bewusst nicht mit `-f` staged,
- ihre entpackten relevanten Inhalte sind im Archiv vorhanden.

## Schlussurteil

Entweder exakt:

`READY TO COMMIT`

oder:

`DECISION REQUIRED`

Bei `DECISION REQUIRED` sämtliche konkreten Abweichungen aufführen.

---

# 9. Bericht selbst ebenfalls stagen

Nachdem `COMMIT_PREP_REPORT.md` fertiggestellt ist:

Nur diesen neuen Report zusätzlich stagen.

Danach die vollständigen Prüfungen aus Abschnitt 6 und 7 **noch einmal**
durchführen.

Der Report muss damit selbst Bestandteil des vorbereiteten Logging-Commits
sein.

Falls sich durch das Hinzufügen des Reports das Schlussurteil ändert,
Bericht aktualisieren, erneut stagen und final nochmals prüfen.

---

# 10. Keine weiteren Artefakte notwendig

Kein weiteres `OUTPUT_INDEX.md` anlegen.

`OBS-CLOSE-001` besitzt bereits einen vollständigen Output-Index.

Dieser Run soll bewusst klein bleiben.

---

# 11. Kein Commit

Auch bei vollständig erfolgreicher Prüfung ausdrücklich **nicht** ausführen:

```text
git commit
git push
git merge
git rebase
git tag
```

Der vorbereitete Index bleibt nach dem Run bestehen.

Der Commit erfolgt erst nach externer Sichtung des
`COMMIT_PREP_REPORT.md`.

---

# 12. Definition of Done

Der Run ist abgeschlossen, wenn:

1. alle zum Logging-Abschluss gehörenden Änderungen staged sind,
2. keine Triggerarchitektur-Datei staged ist,
3. keine Produktcode-/Testdatei staged ist,
4. die vier bekannten Triggeränderungen weiterhin unverändert
   unstaged/untracked vorhanden sind,
5. der staged Bestand vollständig innerhalb der Allowlist liegt,
6. `git diff --cached --check` erfolgreich ist,
7. die kanonische Observability-Dokumentation vollständig staged ist,
8. die historische Logging-Akte vollständig staged ist,
9. `COMMIT_PREP_REPORT.md` erzeugt und ebenfalls staged wurde,
10. kein Commit oder Push erfolgt ist,
11. der Abschlussstatus eindeutig `READY TO COMMIT` oder
    `DECISION REQUIRED` lautet.