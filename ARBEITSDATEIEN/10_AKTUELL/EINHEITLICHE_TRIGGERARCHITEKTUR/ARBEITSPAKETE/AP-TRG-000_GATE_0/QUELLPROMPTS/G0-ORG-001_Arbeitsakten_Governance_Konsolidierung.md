# Auftrag

Führe vor der Fortsetzung der fachlichen Planung und Implementierung der **einheitlichen Triggerarchitektur** eine ausschließlich organisatorische Konsolidierung der Projekt-Arbeitsakten durch.

Dieser Run ist **kein Implementierungsrun der Triggerarchitektur** und darf keinerlei Produktverhalten verändern.

Ziel ist ein eindeutiger, konfliktfreier Arbeits- und Dokumentationsstand, anhand dessen ein neuer Agent innerhalb weniger Minuten zuverlässig feststellen kann:

1. welcher Workstream aktuell aktiv ist,
2. welcher Stand fachlich erreicht wurde,
3. welche Quellen für Soll-, Ist- und Ablauf-Aussagen autoritativ sind,
4. welches Work Package bzw. welcher Planungsschritt als Nächstes zulässig ist,
5. welche Punkte abgeschlossen, zurückgestellt, historisch oder ungeprüft sind,
6. welche Änderungen sich bereits im Working Tree befanden und welche Änderungen durch diesen Run entstanden sind.

## 1. Ausgangslage

Repository/Workspace:

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur`

Branch:

`feat/einheitliche-triggerarchitektur`

Bekannter HEAD zum Zeitpunkt der Auftragserstellung:

`9f136c3 chore(observability): close logging phase before trigger migration`

Die Logging-/Observability-Foundation wurde vorgezogen, um die anschließende Triggerarchitektur-Migration besser beobachten zu können.

Sie wurde am 20.08.2026 **kontrolliert als belastbarer Pre-Migration-Arbeitsstand abgeschlossen**.

Dabei gilt ausdrücklich:

* Es wird **kein formales `G-OBS-V1 PASS`** behauptet.
* Verbleibende formale bzw. Rand-Abnahmen, insbesondere M-1…M-11, werden bewusst im Zuge bzw. nach der Triggerarchitektur-Migration erneut gegen den dann maßgeblichen Gesamtzustand geprüft.
* Der aktuell wieder aufzunehmende Hauptworkstream ist die **einheitliche Triggerarchitektur**.
* Deren fachliches GATE 0 ist noch **nicht bestanden**.

## 2. Wichtige Schutzregel für den vorhandenen Working Tree

Der Working Tree ist beim Start dieses Auftrags voraussichtlich nicht clean.

Vor jeglicher Änderung zwingend ausführen und vollständig im Run-Report festhalten:

```powershell
git branch --show-current
git rev-parse HEAD
git status --short
git diff --stat
git diff
git ls-files --others --exclude-standard
```

Vorhandene Änderungen sind **User-/Projektbestand**.

Verboten sind insbesondere:

* `git clean`
* pauschales `git restore`
* `git reset`
* Verwerfen vorhandener Änderungen
* unbegründetes Löschen
* Überschreiben von Dateien, deren Herkunft nicht geklärt wurde

Jede vorbestehende Änderung muss entweder:

1. nachvollziehbar in die neue Ordnung übernommen,
2. als historisches Artefakt erhalten,
3. als exaktes Duplikat mit Hashnachweis dedupliziert,
4. oder als weiterhin ungeklärter Bestand im Abschlussbericht ausgewiesen werden.

Kein einzigartiger Inhalt darf stillschweigend verloren gehen.

## 3. Erlaubter Scope

Organisatorische bzw. dokumentarische Änderungen sind ausschließlich in folgenden Bereichen zulässig:

* `AGENTS.md`
* `task.md`
* `ÜBERGABE.md`
* `docs/PROJEKTUEBERSICHT.md`
* `ARBEITSDATEIEN/**`

Produktcode ist ausdrücklich Non-Scope, insbesondere:

* `app.py`
* `core/**`
* `ui/**`
* `tests/**`
* produktive Konfigurationslogik
* Server-/LED-Produktcode

Bestehende Produktdokumente außerhalb des erlaubten Scopes nicht verändern.

## 4. Zuerst gezielt lesen

Nicht pauschal sämtliche Arbeitsakten einlesen.

Zwingend zunächst:

1. `ARBEITSDATEIEN/README.md`
2. `ARBEITSDATEIEN/AGENTS.md`
3. `ARBEITSDATEIEN/00_STEUERUNG/ARBEITSPROZESS.md`
4. `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`
5. `ARBEITSDATEIEN/00_STEUERUNG/MASTERPLAN.md`
6. `ARBEITSDATEIEN/00_STEUERUNG/OFFENE_PUNKTE.md`
7. nur das Ende bzw. gezielte relevante Stellen aus `ARBEITSDATEIEN/00_STEUERUNG/LOG_VERLAUF.md`
8. `ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/README.md`
9. `.../00_NORMATIV/ZIELBILD_TRIGGERARCHITEKTUR.md`
10. `.../20_PLANUNG/planung_migration/00_README_ROTER_FADEN.md`
11. `.../20_PLANUNG/planung_migration/01_ENTSCHEIDUNGEN_VOR_IMPLEMENTIERUNG.md`
12. `.../20_PLANUNG/planung_migration/15_OFFENE_FUNDE_UND_AENDERUNGSLOG.md`
13. `.../20_PLANUNG/planung_migration/16_TRACEABILITY_MATRIX.md`
14. `.../10_ANALYSE/CODE_ARCHITEKTUR_BASELINE/LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md`
15. Root-`AGENTS.md`
16. Kopf-/Status-/Quellenabschnitte von `task.md`, `ÜBERGABE.md` und `docs/PROJEKTUEBERSICHT.md`

Weitere Dateien nur öffnen, wenn ein konkreter Konflikt oder eine Verschiebung dies erfordert.

Die umfangreiche Logging-Evidence und historische Trigger-Evidence nicht pauschal lesen.

## 5. Verbindliches Zielmodell der Arbeitssteuerung

### 5.1 `CURRENT_STATE.md`

`CURRENT_STATE.md` wird zu einem **kompakten aktuellen Snapshot**.

Es darf nicht länger ein zweites Verlaufslog sein.

Es soll ausschließlich enthalten:

* aktiver Hauptworkstream,
* aktueller Status/Phase/Gate,
* letzter akzeptierter Meilenstein,
* derzeit aktives bzw. als Nächstes autorisiertes Work Package,
* aktuelle Blocker/noch erforderliche Entscheidungen,
* relevante Repository-Baseline,
* bewusst zurückgestellte Bereiche,
* nächster zulässiger Schritt.

Die umfangreiche historische OBS-Chronologie gehört ausschließlich in `LOG_VERLAUF.md` bzw. die jeweilige Arbeitsakte/Evidence.

Keine historische Information löschen, die nicht bereits anderweitig erhalten ist.

### 5.2 `LOG_VERLAUF.md`

`LOG_VERLAUF.md` bleibt das append-only Meilensteinprotokoll.

Es wird nicht als Pflichtlektüre vollständig geladen.

Keine bereits vorhandenen historischen Einträge umschreiben, außer ein objektiv notwendiger technischer Reparaturgrund wird nachgewiesen.

Für diesen Run am Ende genau einen neuen Meilensteineintrag ergänzen.

### 5.3 `MASTERPLAN.md`

Der Masterplan muss die aktuelle Reihenfolge klar sichtbar machen:

1. Logging / Observability Pre-Migration – kontrolliert abgeschlossen, ohne formales `G-OBS-V1 PASS`
2. Einheitliche Triggerarchitektur – aktuell aktiv, Phase 0 / GATE 0 noch offen
3. Logging / Observability Post-Migration – pending

Keine Run-Details in den Masterplan übernehmen.

### 5.4 `OFFENE_PUNKTE.md`

Nur globale, noch keinem Workstream/Work Package zugeordnete Punkte.

Bereits zugeordnete Trigger- oder Logging-Befunde gehören nicht in diese globale Inbox.

### 5.5 Autoritätshierarchie

Arbeite in `ARBEITSPROZESS.md` und den Agent-Regeln eine eindeutige Trennung ein.

Für Soll-Aussagen:

```text
00_NORMATIV
→ explizit freigegebene Entscheidungen
→ aktives Work Package
```

Für Ist-Aussagen:

```text
realer Produktcode
→ aktuelle Codeanalysen
→ Tests / Evidence
```

Für den Ablaufstatus:

```text
CURRENT_STATE
→ aktives Work Package / Gate
→ LOG_VERLAUF
```

Ungeprüfte Drafts, alte Übergaben, historische Arbeitsakten und alte Planungssnapshots dürfen aktuelle Entscheidungen niemals überschreiben.

## 6. Root-`AGENTS.md` reparieren

Der Root-`AGENTS.md` verweist derzeit noch auf unter anderem:

* `docs/IMPLEMENTATION_ROADMAP.md`
* `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`

Diese Dateien existieren im aktuellen aktiven Stand nicht mehr an diesen Orten und liegen inzwischen im historischen Bereich.

Diese Verweise dürfen keinen Coding-Agenten mehr in eine veraltete Quellenhierarchie schicken.

Passe `AGENTS.md` so an, dass:

1. `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md` der Einstieg in den aktuellen Arbeitsstand ist,
2. `ARBEITSDATEIEN/AGENTS.md` die globale Arbeitsordnung liefert,
3. für einen aktiven Workstream dessen README/AGENTS und aktives Work Package gelesen werden,
4. historische Dokumente ausdrücklich nicht als aktuelle Architekturautorität gelten,
5. weiterhin eine kontextschonende, stufenweise Lektüre vorgeschrieben ist.

Keine fachliche Triggerentscheidung dabei neu erfinden.

## 7. Trigger-Workstream konsolidieren

### 7.1 Workstream-Einstieg

Ergänze einen geeigneten Workstream-`AGENTS.md` unter:

`ARBEITSDATEIEN/10_AKTUELL/EINHEITLICHE_TRIGGERARCHITEKTUR/`

Dieser muss insbesondere enthalten:

* Zweck und Scope,
* Autoritätshierarchie,
* Pflichtlektüre vor einem Run,
* Work-Package-/Run-/Gate-Modell,
* Umgang mit neuen Funden,
* Git-Regeln,
* Abschlussberichtspflicht,
* klare Kennzeichnung, dass GATE 0 derzeit noch offen ist.

### 7.2 README

Der Trigger-README soll Navigationsdatei sein.

Absolute `P:\...`-Pfade durch repository-relative Pfade ersetzen.

Keine mutable Detailhistorie dort duplizieren.

### 7.3 Roter Faden

`20_PLANUNG/planung_migration/00_README_ROTER_FADEN.md` verweist derzeit auf nicht vorhandene Dateien:

* `REFERENZ_ZIELBILD_EINHEITLICHE_TRIGGERARCHITEKTUR.md`
* `REFERENZ_DIAGNOSEBERICHT_TRIGGERARCHITEKTUR.md`

Diese Referenzen auf die tatsächlich vorhandenen kanonischen Quellen korrigieren.

Insbesondere muss das normative Zielbild korrekt auf

`00_NORMATIV/ZIELBILD_TRIGGERARCHITEKTUR.md`

verweisen.

Die aktuelle Code-Only-Architekturaufnahme bzw. deren maßgebliche Abschlussanalyse sauber als Ist-Evidence referenzieren.

### 7.4 Fehlende Phasendateien

Der Rote Faden nennt `02_...` bis `14_...`, die derzeit noch nicht existieren.

Nicht künstlich mit leeren Dateien erzeugen.

Stattdessen eindeutig dokumentieren:

* sie sind geplante Detail-Work-Packages,
* ihre Erstellung/Finalisierung ist Teil des noch offenen GATE-0-/Plan-Freeze-Prozesses,
* ihre Nichtexistenz bedeutet derzeit nicht versehentliches Löschen.

### 7.5 Keine Architekturentscheidungen vorwegnehmen

Die offenen B1–B8 sowie die aus der letzten Architekturklärung stammenden E-/P-Punkte **nicht eigenmächtig entscheiden**.

Dieser Run stellt ausschließlich sicher, dass sie als noch zu konsolidierende GATE-0-Arbeit eindeutig auffindbar sind.

## 8. Hypothetischen Namespace-Entwurf aus aktiver Planung entfernen

Der Ordner

`20_PLANUNG/planung_migration/namespace_system_model/`

enthält einen Entwurf, der sich selbst ausdrücklich als

* hypothetisch,
* ohne Faktenbasis,
* nicht referenzierbar

kennzeichnet.

Er darf deshalb nicht mitten im aktiven Migrationsplan liegen.

Verschiebe ihn verlustfrei in einen eindeutig ungeprüften Bereich, vorzugsweise:

`15_DRAFTS_UNGEPRUEFT/NAMESPACE_SYSTEM_MODEL/`

Bestehende Selbstkennzeichnung erhalten.

Keine Inhalte daraus in normative oder operative Triggerplanung übernehmen.

## 9. Logging-/Observability-Arbeitsakte konsolidieren

Der Pre-Migration-Logging-Workstream ist kontrolliert beendet.

Dabei gilt:

* kein formales `G-OBS-V1 PASS`,
* bestehende Evidence bleibt vollständig erhalten,
* M-1…M-11 und weitere explizit zurückgestellte Punkte müssen für Post-Migration auffindbar bleiben.

Prüfe die aktuelle Dirty-State-Reorganisation sehr sorgfältig.

Bekannt sind insbesondere:

* tracked gelöschte Dateien unter `30_AUSFUEHRUNG/prompts/...`,
* neue/untracked Pfade unter `30_AUSFUEHRUNG/Prompts/...`,
* `LOGGING_V1_PROMPT_PIPELINE_V2/...`,
* `80_DOCS/...`.

Es existieren nachweislich Dateien, die lediglich byte-identisch verschoben wurden, aber auch gelöschte Promptdateien ohne unmittelbar erkennbaren identischen Ersatz.

Regeln:

1. Keine einzigartige Datei verlieren.
2. Exakte Duplikate nur nach Hash-/Inhaltsvergleich deduplizieren.
3. Historische Fix-/Gate-Prompts erhalten, wenn sie Teil der nachvollziehbaren Run-Historie sind.
4. Für das standardisierte Run-System lowercase `prompts` verwenden.
5. Kein paralleles `prompts`/`Prompts`-Namensschema bestehen lassen.
6. Keine generierten ZIP-/Dokumentpakete ungeprüft als normative Arbeitsakten behandeln.
7. Jede Verschiebung/Deduplizierung im Run-Report aufführen.

Wenn der Bestand verlustfrei konsolidiert ist, die abgeschlossene Pre-Migration-Arbeitsakte gemäß der bestehenden Arbeitsordnung in einen geeigneten Historienordner unter

`ARBEITSDATEIEN/90_HISTORIE/`

überführen.

Der Archivname muss deutlich machen:

* Logging/Observability,
* Pre-Migration,
* kontrollierter Abschluss,
* Datum 2026-08-20.

Der Archivierungsvorgang darf nicht fälschlich behaupten, `G-OBS-V1` sei bestanden.

Für zukünftige Logging-Post-Migration-Arbeit jetzt noch keinen umfangreichen neuen Workstream erfinden. Der Masterplan und eine eindeutige Deferred-Referenz genügen.

## 10. Alte Produktstatusdokumente entschärfen, aber nicht neu schreiben

Folgende Dateien beschreiben einen älteren Implementierungsstand vom 12.08.2026:

* `task.md`
* `ÜBERGABE.md`
* `docs/PROJEKTUEBERSICHT.md`

Sie enthalten teilweise das alte Mode-/Follow-up-/Extend-Verhalten und dürfen nicht mehr als aktuelles Soll für die Trigger-Migration verstanden werden.

Diese Dokumente **nicht vollständig auf die neue Zielarchitektur umschreiben**. Das gehört erst zur späteren Dokumentationsfinalisierung nach der Migration.

Stattdessen eine klare, prominente Statuskennzeichnung ergänzen:

* historischer bzw. Pre-Migration-Implementierungsstand,
* Datum,
* nicht maßgeblich für die laufende Triggerarchitektur-Migration,
* Verweis auf die aktuelle Steuerung unter `ARBEITSDATEIEN/`.

Historischen Inhalt ansonsten möglichst unverändert erhalten.

## 11. Arbeitsprozess für zukünftige Agentenruns konkretisieren

`ARBEITSPROZESS.md` so erweitern, dass künftig immer derselbe Ablauf gilt:

```text
Beratung / Entscheidung
→ Entscheidung materialisieren
→ Work Package READY
→ Baseline erfassen
→ Agent Run
→ RUN_REPORT + OUTPUT_INDEX + Evidence
→ unabhängiger Review bei Gate-relevanten Arbeiten
→ PASS oder FAIL
→ bei PASS Status/Verlauf aktualisieren
→ nächstes Work Package
```

Regeln:

* Ein Implementierungsrun vergibt niemals sein eigenes Gate.
* Ein Gate-Review erfolgt in einer frischen Session.
* Neue Funde werden zuerst klassifiziert und nicht automatisch repariert.
* Vor jedem Run Branch, HEAD und Working Tree festhalten.
* Fremde/vorbestehende Änderungen niemals ungefragt zurücksetzen.
* Nach jedem relevanten Run genau einen Meilenstein in `LOG_VERLAUF.md`.
* `CURRENT_STATE.md` enthält nur den neuesten Snapshot.
* Prompt und Abschlussbericht müssen den erlaubten Dateiscope explizit benennen.

## 12. Organisationsskripte prüfen

Prüfe insbesondere:

`ARBEITSDATEIEN/TOOLS/Close-WorkCycle.ps1`

Der aktuelle Defaultpfad verweist auf einen älteren Worktree und das Skript verschiebt unter anderem das globale `LOG_VERLAUF.md`.

Das Skript **nicht mit `-Apply` ausführen**.

Prüfe, ob es mit dem jetzt festgelegten Modell kompatibel ist.

Falls eine kleine, eindeutig sichere Korrektur möglich ist, darf das Organisationsskript innerhalb dieses Auftrags angepasst werden. Bevorzugt repository-/skriptrelative Pfadermittlung statt hartcodierter Worktree-Pfade.

Falls sein Archivierungsmodell grundsätzlich nicht zum neuen Prozess passt, nicht spekulativ neu entwickeln, sondern im Abschlussbericht klar als `DEPRECATED / NEEDS FOLLOW-UP` kennzeichnen.

## 13. Abschlussvalidierung

Mindestens prüfen:

```powershell
git status --short
git diff --stat
git diff --check
```

Zusätzlich gezielt sicherstellen:

* Root-`AGENTS.md` verweist nicht mehr als aktuelle Autorität auf die entfernten alten Roadmap-/Arbeitsordnungsdateien.
* Die aktive Triggerplanung enthält keine gebrochenen `REFERENZ_...`-Verweise mehr.
* Der hypothetische Namespace-Entwurf liegt nicht mehr als scheinbar aktive Migrationsplanung vor.
* Es existiert im standardisierten aktiven Run-System kein konkurrierendes `prompts`/`Prompts`-Schema.
* Kein Produktcode wurde verändert.
* Keine Testdatei wurde verändert.
* Keine einzigartige historische Arbeitsdatei wurde unbegründet gelöscht.
* Logging wird nicht fälschlich als `G-OBS-V1 PASS` bezeichnet.
* `CURRENT_STATE.md` ist ein wirklicher aktueller Snapshot und kein zweites Verlaufslog.
* Der nächste autorisierte Projektschritt ist eindeutig: **Triggerarchitektur Phase 0 / GATE-0-Plan-Freeze und Entscheidungsauflösung**, nicht Produktimplementierung.

## 14. Run-Artefakte

Lege für diesen Run unter dem Trigger-Workstream einen Run-Ordner nach bestehender Konvention an, beispielsweise:

`30_AUSFUEHRUNG/runs/RUN-G0-ORG-001_2026-08-23/`

Mindestens:

### `RUN_REPORT.md`

Enthalten sein müssen:

* Run-ID
* Ausgangs-Branch und Ausgangs-HEAD
* vollständige Klassifikation des vorbestehenden Dirty State
* festgestellte Dokument-/Autoritätskonflikte
* durchgeführte Änderungen
* alle erzeugten/geänderten/verschobenen/entfernten Dateien
* bei Deduplizierungen: Herkunft, Ziel und Nachweis der Inhaltsgleichheit
* neue verbindliche Arbeits-/Quellenhierarchie
* bewusst nicht gelöste fachliche Fragen
* aktueller GATE-0-Status
* Validierungsergebnisse
* verbleibende organisatorische Blocker
* klare Empfehlung für den nächsten Schritt

### `OUTPUT_INDEX.md`

Index aller durch diesen Run erzeugten dauerhaften Artefakte und Evidence.

## 15. Git

Kein:

* Commit
* Push
* Merge
* Rebase
* Tag
* PR

Der Run endet mit den Änderungen im Working Tree und einem vollständigen Abschlussbericht.

## 16. Abbruch-/Entscheidungsregel

Wenn eine organisatorische Änderung nur durch Verlust nicht eindeutig klassifizierbarer bestehender Inhalte möglich wäre:

**nicht löschen und nicht raten.**

Bestand erhalten, Konflikt konkret dokumentieren und als `DECISION REQUIRED` in den Abschlussbericht aufnehmen.

Bei fachlichen Triggerentscheidungen B1–B8 bzw. E-/P-Fragen gilt ebenfalls:

**nicht entscheiden.**

Diese gehören in den anschließenden fachlichen GATE-0-Plan-Freeze.
