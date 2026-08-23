# OBS-CLOSE-001 – Logging/Observability Teil A konsolidieren, archivieren und für Trigger-Fortsetzung abschließen

## 0. Auftrag und Ziel

Führe einen ausschließlich organisatorischen, dokumentarischen und Git-bestandsbezogenen Abschlussrun für den eingeschobenen Workstream **Logging / Observability Teil A – Pre-Trigger Foundation** durch.

Der Logging-/Observability-Workstream wurde während der Planung der einheitlichen Triggerarchitektur bewusst zwischengeschoben, damit für die anschließende Trigger-Migration eine belastbare Diagnose- und Logging-Grundlage vorhanden ist.

Diese Pre-Trigger-Arbeit ist inzwischen fachlich beendet und soll jetzt:

1. vollständig und verlustfrei konsolidiert,
2. eindeutig als abgeschlossener Pre-Trigger-Arbeitszyklus gekennzeichnet,
3. aus `10_AKTUELL` entfernt,
4. als zusammenhängende historische Arbeitsakte unter `90_HISTORIE` archiviert,
5. mit einem historischen Snapshot der zentralen Steuerungsdateien versehen,
6. und in der globalen Projektsteuerung sauber abgeschlossen werden.

Anschließend soll unter `10_AKTUELL` wieder ausschließlich der tatsächlich aktive Hauptworkstream **Einheitliche Triggerarchitektur** verbleiben.

Dieser Run implementiert **keine Triggerarchitektur** und verändert **keinen Produktcode**.

---

# 1. Wesentliche Statusaussage

Der Logging-Workstream wird mit diesem Run **organisatorisch abgeschlossen und archiviert**.

Dabei ist folgende Formulierung verbindlich:

> `Logging / Observability Teil A – Pre-Trigger Foundation` ist als belastbarer Pre-Trigger-Arbeitsstand **CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE**.

Ausdrücklich **nicht** behaupten:

> `G-OBS-V1 PASS`

Ein formales finales `G-OBS-V1 PASS` liegt nicht vor.

Bestimmte verbleibende formale bzw. manuelle Abnahmen und Post-Migration-Prüfungen wurden bewusst zurückgestellt, weil ihr endgültiger Nachweis sinnvollerweise gegen die nach der Triggerarchitektur-Migration maßgebliche Gesamtarchitektur erfolgen soll.

Insbesondere darf die Archivierung niemals so formuliert werden, als seien sämtliche ursprünglich vorgesehenen V1-Gates formal bestanden.

---

# 2. Logging Teil B darf keinesfalls verloren gehen

Logging / Observability besitzt bereits einen geplanten **Teil B / Post-Migration-Ausbau**.

Dieser folgt bewusst **nach der Triggerarchitektur**.

Die bereits geplante Reihenfolge umfasst insbesondere:

- `OBS-100` – Post-Trigger Instrumentation
- `OBS-110` – Server Control, Admin Auth & Capabilities
- `OBS-120` – Remote Server History & Global Logs
- `OBS-130` – Serverweite Admin-Settings
- `OBS-140` – LED-Controller Logging Integration
- `OBS-150` – Erweiterte Sinks / Storage
- `OBS-160` – Advanced Query / UX
- `OBS-170` – Cross-Source Correlation / Forensics
- `OBS-180` – Final Hardening, Docs & Acceptance

Die bestehenden Planungsquellen und Work-Package-Drafts hierfür müssen vollständig erhalten bleiben.

Logging Teil B wird mit diesem Run **nicht aktiviert** und nicht weiter ausgeplant.

Stattdessen muss der globale `MASTERPLAN.md` anschließend eindeutig enthalten:

- Teil A: abgeschlossen und archiviert
- Triggerarchitektur: aktuell aktiv
- Teil B: `DEFERRED / POST-TRIGGER`
- Einstieg nach Trigger: `OBS-100`
- Verweis auf die archivierte Logging-Planungsquelle

Logging Teil B gehört **nicht zusätzlich als offener ungeklärter Punkt** in eine globale Inbox. Es handelt sich um einen bereits geplanten zukünftigen Workstream.

---

# 3. Repository und Schutz des bestehenden Working Trees

Arbeite im Repository-Root.

Vor jeder Änderung zwingend erfassen:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff
git ls-files --others --exclude-standard
```

Den vollständigen Ausgangszustand im `RUN_REPORT.md` dokumentieren.

Der Working Tree enthält bereits Projekt-/Useränderungen und insbesondere uncommittete Logging-Artefakte.

Diese sind **kein Müll** und dürfen nicht pauschal bereinigt werden.

Verboten sind:

- `git clean`
- `git reset`
- pauschales `git restore`
- Verwerfen untracked Dateien
- unbegründetes Löschen
- Überschreiben vorhandener Dateien ohne vorherigen Vergleich

Bei Unsicherheit:

> Bestand erhalten und im Abschlussbericht als `DECISION REQUIRED` ausweisen.

---

# 4. Strikte Scope-Grenzen

## Erlaubter Scope

Organisatorische und dokumentarische Änderungen innerhalb von:

- `ARBEITSDATEIEN/00_STEUERUNG/**`
- `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/**`
- `ARBEITSDATEIEN/90_HISTORIE/**`
- `docs/observability/**`, sofern die vorhandene Logging-Produktdokumentation kontrolliert dorthin überführt wird

## Expliziter Non-Scope

Nicht verändern:

- `app.py`
- `core/**`
- `ui/**`
- `tests/**`
- Trigger-Produktcode
- Server-Produktcode
- LED-Produktcode
- fachliche Triggerplanung
- offene Triggerentscheidungen

Insbesondere nicht verändern oder verschieben:

- `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/20_PLANUNG/planung_migration/namespace_system_model/**`

Der dortige Namespace-Entwurf ist ein bewusst getrenntes hypothetisches Konzept und **kein Bestandteil dieses Auftrags**.

Auch sonstige bereits bestehende uncommittete Änderungen der Triggerarchitektur nicht in diesen Run hineinziehen.

---

# 5. Kontextschonende Bestandsaufnahme

Nicht sämtliche Logging-Artefakte blind vollständig lesen.

Zunächst gezielt lesen:

1. `ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md`
2. `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`
3. relevante Logging-Abschnitte bzw. das Ende von `ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md`
4. `ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/README.md`
5. aktuelle Logging-Gesamtplanung und Work-Package-Index
6. Abschluss-/Statusdokumente des Logging-V1-Workstreams
7. Indexe und Manifeste der uncommitteten Produktdokumentation
8. Prompt-Sequenz bzw. Prompt-Index
9. vorhandene Gate-/Run-/Evidence-Indizes

Weitere Einzeldateien nur lesen, wenn dies für:

- Versionsvergleich,
- Deduplizierung,
- Archivierung,
- Ermittlung der kanonischen Fassung
- oder Vollständigkeitsprüfung

notwendig ist.

Große Evidence-Bestände nicht pauschal inhaltlich lesen.

---

# 6. Uncommitteten Logging-Bestand vollständig inventarisieren

Vor der Archivierung alle vorhandenen Logging-bezogenen tracked, modified und untracked Dateien erfassen und nach mindestens folgenden Kategorien klassifizieren:

1. normative Vorgaben,
2. Analysen,
3. Planung,
4. Implementierungs-/Agentenprompts,
5. Run-Berichte,
6. Gate-Reviews,
7. Evidence,
8. Produktdokumentation,
9. Entwürfe / unbenutzte Vorlagen,
10. Zwischenarchive / erzeugte Pakete,
11. Dubletten,
12. sonstige Dateien.

Für jede Datei bzw. sinnvolle Dateigruppe festhalten:

- aktueller Pfad,
- Git-Status,
- Kategorie,
- kanonisch / historisch / Draft / Duplikat / ungeklärt,
- vorgesehener Zielpfad.

Keine Datei ausschließlich aufgrund ihres Namens löschen oder ersetzen.

---

# 7. Prompt-Bestände und Dubletten kontrolliert konsolidieren

Es existieren mehrere Prompt-Bestände, darunter insbesondere Strukturen wie:

- `30_AUSFUEHRUNG/Prompts/**`
- `30_AUSFUEHRUNG/LOGGING_V1_PROMPT_PIPELINE_V2/Prompts/**`
- weitere vorhandene Prompt-Verzeichnisse

Einige Dateien sind möglicherweise byte-identisch, andere unterscheiden sich.

Regeln:

1. Für identische Dateien Inhalts- bzw. Hashvergleich durchführen.
2. Nur nachgewiesen identische redundante Kopien als Dubletten behandeln.
3. Unterschiedliche Gate-Reviews oder Implementierungsaufträge niemals nur aufgrund ähnlicher Namen deduplizieren.
4. Der tatsächlich verwendete historische Prompt-/Run-Verlauf muss vollständig erhalten bleiben.
5. Eine nachweislich unbenutzte zweite Prompt-Pipeline darf als solche klassifiziert werden, muss aber als historische Planungs-/Draftakte erhalten bleiben, sofern sie einzigartige Inhalte enthält.
6. Für das kanonische Namensschema künftig lowercase `prompts` verwenden.
7. Kein konkurrierendes `prompts`/`Prompts`-Schema innerhalb des final archivierten kanonischen Run-Bestands belassen, sofern dies verlustfrei bereinigt werden kann.

Alle Deduplizierungen im `RUN_REPORT.md` mit Quelle, Ziel und Nachweis dokumentieren.

---

# 8. Produktdokumentation konsolidieren

Es existieren Produktdokumentationsstände mindestens vom:

- 2026-08-20
- 2026-08-21

Die Fassung vom 2026-08-21 besitzt ein umfangreicheres Manifest und ist voraussichtlich die vollständigere Fassung.

Dies jedoch nicht nur annehmen, sondern anhand von:

- `MANIFEST.json`
- Index
- Dateiliste
- ggf. Hash-/Inhaltsvergleich

prüfen.

Besonders sicherstellen, dass keine Datei verloren geht, die zwar im Paket/Manifest enthalten, aber im entpackten Arbeitsordner fehlt.

Bekannter Prüfkandidat:

`13_HEALTH_BACKPRESSURE_FAILURE_ISOLATION.md`

Falls das vorhandene Archiv-/ZIP-Paket diese Datei enthält, der entpackte Dokumentationsordner jedoch nicht, die vollständigere Quelle kontrolliert verwenden.

## Ziel

Die kanonische V1-/Teil-A-Produktdokumentation soll dauerhaft und außerhalb des historischen Arbeitsordners unter:

`docs/observability/`

auffindbar sein.

Dabei:

- nur die kanonische, vollständige Fassung übernehmen,
- keine zwei konkurrierenden Produktdokumentationen nebeneinander als gleichermaßen aktuell veröffentlichen,
- ältere Erstellungsfassungen und Pakete innerhalb der historischen Logging-Arbeitsakte erhalten.

Das zugehörige Manifest ebenfalls erhalten.

Die Produktdokumentation muss weiterhin klar aussagen:

- Teil A / V1 vor Trigger-Migration,
- belastbarer Zwischenabschluss,
- kein künstlich behauptetes `G-OBS-V1 PASS`,
- Teil B folgt nach Trigger.

---

# 9. Historische Logging-Arbeitsakte erzeugen

Nach vollständiger Inventarisierung und kontrollierter Konsolidierung soll der bisherige aktive Logging-Workstream aus:

`ARBEITSDATEIEN/10_AKTUELL/LOGGING_OBSERVABILITY/`

als zusammenhängende Arbeitsakte nach:

`ARBEITSDATEIEN/90_HISTORIE/`

überführt werden.

Bevorzugter Zielordner:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/`

Wenn vorhandene Namenskonventionen zwingend einen anderen Namen nahelegen, darf dieser angepasst werden. Die Bedeutung muss aber eindeutig bleiben.

Die historische Akte soll mindestens enthalten:

```text
2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/
├── README.md
├── LOGGING_OBSERVABILITY/
│   ├── 00_NORMATIV/
│   ├── 10_ANALYSE/
│   ├── 20_PLANUNG/
│   ├── 30_AUSFUEHRUNG/
│   ├── 40_EVIDENCE/
│   ├── 80_DOCS/
│   └── ...
└── STEUERUNG_SNAPSHOT/
```

Bestehende interne Struktur möglichst bewahren.

Nicht unnötig hunderte Dateien neu sortieren, wenn ihre bestehende Workstream-Struktur bereits nachvollziehbar ist.

---

# 10. Archiv-README erstellen

Im Root der historischen Akte eine neue:

`README.md`

erstellen.

Sie muss kompakt und eindeutig enthalten:

## Identität

- Workstream: Logging / Observability
- Abschnitt: Teil A / Pre-Trigger Foundation
- Abschlussdatum
- ursprünglicher Branch
- relevanter Abschluss-HEAD vor diesem Organisationsrun

## Status

Exakte Aussage:

`CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`

und separat:

`Formal G-OBS-V1: NOT PASSED`

## Warum abgeschlossen?

Erklären:

- Logging Foundation wurde bewusst vorgezogen,
- ausreichend belastbare Observability-Basis für Trigger-Migration erreicht,
- verbleibende formale/integrierte Abnahmen bewusst auf den nach der Trigger-Migration maßgeblichen Zustand verschoben.

## Was folgt später?

Logging Teil B:

`OBS-100` bis `OBS-180`

mit Verweis auf die archivierten Planungsquellen.

## Wiederaufnahmebedingung

Triggerarchitektur stabil umgesetzt bzw. entsprechender Masterplan-Meilenstein erreicht.

## Navigationshinweise

Verweise auf:

- Gesamtplan,
- Work Packages,
- Prompt-/Run-Historie,
- Evidence,
- Produktdokumentation,
- Steuerungs-Snapshot.

---

# 11. `MASTERPLAN.md` aktualisieren

Der globale Masterplan muss anschließend sinngemäß eindeutig diese Reihenfolge zeigen:

## 1. Logging / Observability Teil A – Pre-Trigger Foundation

Status:

`CONTROLLED CLOSED / ARCHIVED`

Formal:

`G-OBS-V1 NOT PASSED`

Archivpfad angeben.

## 2. Einheitliche Triggerarchitektur

Status:

`ACTIVE`

Aktueller Stand:

Phase 0 / GATE-0-Planung bzw. der tatsächlich zum Zeitpunkt des Runs belegte aktuelle Stand.

Keine fachlichen Triggerentscheidungen in diesem Run treffen.

## 3. Logging / Observability Teil B – Post-Migration

Status:

`DEFERRED / BLOCKED BY TRIGGER ARCHITECTURE`

Start:

`OBS-100 – Post-Trigger Instrumentation`

Danach:

`OBS-110` bis `OBS-180`

Verweis auf die entsprechenden Planungs-/Work-Package-Dateien innerhalb der archivierten Logging-Akte.

Diese Information muss so deutlich sein, dass Logging Teil B bei späteren Arbeiten nicht vergessen werden kann.

---

# 12. `CURRENT_STATE.md` zu einem echten aktuellen Snapshot machen

`CURRENT_STATE.md` enthält derzeit umfangreiche historische Logging-Verläufe.

Diese Historie darf erhalten bleiben, gehört aber nicht in einen dauerhaft anwachsenden Current-State-Snapshot.

Nach diesem Run soll `CURRENT_STATE.md` kompakt beantworten:

- Was ist aktuell aktiv?
- Wo stehen wir?
- Was wurde zuletzt abgeschlossen?
- Was ist deferred?
- Was ist der nächste zulässige Schritt?

Mindestens enthalten:

```text
Active Workstream:
Einheitliche Triggerarchitektur

Previous Milestone:
Logging / Observability Teil A
CONTROLLED CLOSED / ARCHIVED

Formal G-OBS-V1:
NOT PASSED

Deferred:
Logging / Observability Teil B
Start nach Trigger mit OBS-100

Next:
Fortsetzung Triggerarchitektur / GATE-0-Planung
```

Historische Logging-Inhalte aus `CURRENT_STATE.md` nur dann entfernen, wenn sie vollständig durch:

- `LOG_VERLAUF.md`,
- die Logging-Arbeitsakte
- oder andere bestehende Evidence

erhalten bleiben.

Keine historische Information vernichten.

---

# 13. `LOG_VERLAUF.md` als zentrale historische Quelle behandeln

`ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md` ist für diesen Workstream besonders wichtig.

Die aktuelle Datei enthält aufgrund des Zeitpunkts der Einführung der neuen Arbeitsorganisation einen großen und detaillierten Anteil der Logging-/Observability-Arbeit.

Sie bleibt im aktiven globalen Steuerungsbereich bestehen und wird **nicht verschoben**.

## 13.1 Abschluss-Eintrag

Am Ende des Runs genau einen neuen Meilensteineintrag für diesen Abschluss hinzufügen.

Dieser soll mindestens enthalten:

- Run-ID `OBS-CLOSE-001`,
- Logging Teil A organisatorisch abgeschlossen,
- Status `CONTROLLED CLOSED / ACCEPTED PRE-TRIGGER BASELINE`,
- ausdrücklich `G-OBS-V1 NOT PASSED`,
- Archivpfad,
- kanonischer Pfad der Produktdokumentation,
- Logging Teil B deferred,
- nächster Logging-Einstieg `OBS-100`,
- Triggerarchitektur wieder aktiver Hauptworkstream.

Keine vorhandenen historischen Einträge rückwirkend umschreiben.

---

# 14. Historischen Steuerungs-Snapshot in die Archivakte aufnehmen

Dies ist eine verbindliche Anforderung dieses Runs.

Unter:

`ARBEITSDATEIEN/90_HISTORIE/2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/STEUERUNG_SNAPSHOT/`

sollen **Kopien** folgender globaler Steuerungsdateien abgelegt werden:

```text
LOG_VERLAUF.md
CURRENT_STATE.md
MASTERPLAN.md
```

Die Originaldateien unter:

`ARBEITSDATEIEN/00_STEUERUNG/`

bleiben selbstverständlich bestehen und bleiben die aktiven globalen Dateien.

## Reihenfolge

Der Snapshot wird **erst ganz am Ende** erstellt:

1. Logging-Arbeitsakte konsolidieren,
2. Produktdokumentation festlegen,
3. Masterplan aktualisieren,
4. Current State aktualisieren,
5. finalen OBS-CLOSE-001-Eintrag in `LOG_VERLAUF.md` ergänzen,
6. erst danach die drei Dateien byte-identisch nach `STEUERUNG_SNAPSHOT/` kopieren.

Dadurch enthält die archivierte Kopie von `LOG_VERLAUF.md` auch den endgültigen Abschlussmeilenstein dieses Logging-Zyklus.

## Herkunft dokumentieren

Im `STEUERUNG_SNAPSHOT/README.md` kurz festhalten:

- dass dies unveränderte Kopien der globalen Steuerungsdateien zum Abschlusszeitpunkt sind,
- dass sie ausschließlich historischen Snapshot-Charakter besitzen,
- dass die weiterhin autoritativen veränderlichen Versionen unter `ARBEITSDATEIEN/00_STEUERUNG/` liegen.

Für die drei Kopien Hashes erfassen und im Run-Report dokumentieren.

---

# 15. `10_AKTUELL` nach Abschluss prüfen

Nach erfolgreicher Archivierung soll Logging / Observability Teil A **nicht mehr als aktiver Workstream unter `10_AKTUELL` liegen**.

Zielbild:

```text
ARBEITSDATEIEN/
├── 00_STEUERUNG/
├── 10_AKTUELL/
│   └── EINHEITLICHE_TRIGGERARCHITEKTUR/
└── 90_HISTORIE/
    └── 2026-08-21_LOGGING_OBSERVABILITY_TEIL_A_PRE_TRIGGER/
```

Logging Teil B wird jetzt **nicht** als neuer aktiver Ordner unter `10_AKTUELL` erzeugt.

Seine Fortsetzung ist im Masterplan und in der archivierten Planung verankert.

---

# 16. Git-Trennung gegenüber der Triggerarchitektur

Der aktuelle Branch ist:

`feat/einheitliche-triggerarchitektur`

Das ist kein Fehler und in diesem Run nicht zu ändern.

Die Logging-Arbeit wurde historisch bewusst innerhalb dieses Branches eingeschoben.

Keine:

- Branch-Umschreibung
- Rebase
- Cherry-Pick-Konstruktion
- History-Rewrite
- neuer Logging-Branch

vornehmen.

## Besonders wichtig

Bereits vorhandene uncommittete Trigger-Dateien dürfen nicht Bestandteil der Logging-Konsolidierung werden.

Insbesondere entsprechende Änderungen separat erkennen und im Run-Report als:

`PRE-EXISTING / NON-LOGGING / NOT TO INCLUDE IN LOGGING COMMIT`

ausweisen.

Der Run selbst erstellt **keinen Commit**.

---

# 17. Kein Commit und kein Push

Nicht ausführen:

- `git commit`
- `git push`
- `git merge`
- `git rebase`
- `git tag`
- Pull Request

Ziel ist ein vollständig vorbereiteter und überprüfbarer Working Tree.

Nach dem Run wird der Diff extern geprüft.

Erst nach Freigabe soll ein separater Commit erfolgen, voraussichtlich sinngemäß:

`chore(observability): archive pre-trigger logging workstream`

---

# 18. Run-Artefakte

Der Abschlussrun selbst gehört noch zur Logging-Arbeitsakte und muss deshalb **vor deren Verschiebung** sauber dokumentiert und anschließend mitarchiviert werden.

Lege nach vorhandener Run-Konvention einen Run-Ordner an, beispielsweise:

`30_AUSFUEHRUNG/runs/RUN-OBS-CLOSE-001_2026-08-23/`

Mindestens:

## `RUN_REPORT.md`

Enthalten sein müssen:

### Baseline

- Branch
- Ausgangs-HEAD
- vollständiger relevanter Dirty State

### Inventar

- Logging-bezogene modified/untracked Dateien
- Klassifikation
- kanonische vs. historische vs. Draft-Artefakte

### Deduplizierung

Für jede entfernte bzw. zusammengeführte Dublette:

- Quellpfad
- Zielpfad
- Hash/Inhaltsnachweis
- Begründung

### Produktdokumentation

- verglichene Fassungen
- festgelegte kanonische Fassung
- ggf. rekonstruierte fehlende Dateien
- Ziel unter `docs/observability/`

### Archiv

- endgültiger Archivpfad
- vollständige Beschreibung des Archivaufbaus
- Archive-README

### Steuerung

- Änderungen an `MASTERPLAN.md`
- Änderungen an `CURRENT_STATE.md`
- neuer Eintrag in `LOG_VERLAUF.md`
- erzeugter `STEUERUNG_SNAPSHOT`
- Hashes der drei Snapshot-Dateien

### Deferred Logging Teil B

- expliziter Verweis auf OBS-100 bis OBS-180
- Planungsquelle
- Wiederaufnahmebedingung

### Scope-Schutz

- Liste vorbestehender Non-Logging-/Triggeränderungen
- Nachweis, dass diese nicht verändert wurden

### Validation

- sämtliche Abschlussprüfungen
- verbleibende Unsicherheiten
- `DECISION REQUIRED`, falls vorhanden

### Empfehlung

Klare Aussage, ob der Bestand aus Sicht dieses Runs:

`READY FOR HUMAN REVIEW BEFORE COMMIT`

ist.

## `OUTPUT_INDEX.md`

Index aller durch diesen Run:

- erzeugten,
- verschobenen,
- konsolidierten,
- archivierten

dauerhaften Artefakte.

---

# 19. Abschlussvalidierung

Mindestens ausführen:

```powershell
git status --short
git diff --stat
git diff --check
```

Zusätzlich gezielt prüfen:

- kein Produktcode geändert,
- keine Tests geändert,
- keine Triggerplanung fachlich verändert,
- Namespace-Entwurf unangetastet,
- keine einzigartige Logging-Datei verloren,
- keine ungeklärte Dublette stillschweigend gelöscht,
- kanonische Produktdokumentation vollständig,
- `docs/observability/` vorhanden und nachvollziehbar,
- Logging Teil A nicht mehr unter `10_AKTUELL`,
- historische Logging-Akte vorhanden,
- Archiv-README vorhanden,
- `STEUERUNG_SNAPSHOT/LOG_VERLAUF.md` vorhanden,
- `STEUERUNG_SNAPSHOT/CURRENT_STATE.md` vorhanden,
- `STEUERUNG_SNAPSHOT/MASTERPLAN.md` vorhanden,
- Snapshot-Dateien entsprechen den globalen Dateien zum Abschlusszeitpunkt,
- Masterplan nennt Logging Teil B ausdrücklich,
- OBS-100 bis OBS-180 weiterhin auffindbar,
- `CURRENT_STATE.md` nennt Triggerarchitektur als aktiven Workstream,
- nirgendwo wird fälschlich `G-OBS-V1 PASS` behauptet,
- keine Commit-/Push-Aktion durchgeführt.

---

# 20. Abbruchregel

Wenn bei irgendeiner Datei nicht eindeutig feststellbar ist, ob sie:

- kanonisch,
- historische Evidence,
- eine einzigartige Zwischenfassung
- oder tatsächlich redundante Dublette

ist:

**Nicht löschen.**

Bestand erhalten und als `DECISION REQUIRED` dokumentieren.

Wenn eine gewünschte Archivierungsänderung nur durch Verlust oder Interpretation bestehender Inhalte möglich wäre:

**Run an dieser Stelle nicht eigenmächtig erzwingen.**

Erhalte den Bestand und dokumentiere den Konflikt.

---

# 21. Definition of Done

`OBS-CLOSE-001` ist abgeschlossen, wenn:

1. Logging Teil A vollständig inventarisiert und konsolidiert wurde,
2. keine einzigartige Information verloren ging,
3. die kanonische Produktdokumentation dauerhaft unter `docs/observability/` liegt,
4. der gesamte Pre-Trigger-Logging-Arbeitszyklus als zusammenhängende historische Akte unter `90_HISTORIE` liegt,
5. `LOG_VERLAUF.md`, `CURRENT_STATE.md` und `MASTERPLAN.md` als Abschluss-Snapshot in dieser Akte enthalten sind,
6. die globalen Steuerungsdateien weiterhin unter `00_STEUERUNG` bestehen,
7. Teil B mit OBS-100 bis OBS-180 eindeutig im Masterplan geparkt ist,
8. Triggerarchitektur wieder alleiniger aktiver Hauptworkstream ist,
9. kein Produktcode und keine Triggerplanung verändert wurde,
10. kein Commit oder Push erfolgt ist,
11. `RUN_REPORT.md` und `OUTPUT_INDEX.md` vollständig vorliegen,
12. der Run mit `READY FOR HUMAN REVIEW BEFORE COMMIT` oder einer präzisen Liste verbleibender `DECISION REQUIRED` endet.