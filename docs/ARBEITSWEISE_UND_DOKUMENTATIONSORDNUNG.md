# Verbindliche Arbeitsweise und Dokumentationsordnung

> **Status:** verbindliche Projektanweisung  
> **Gültig ab:** 24. Juli 2026  
> **Geltungsbereich:** alle zukünftigen Arbeits-, Prüf-, Korrektur- und Übergabepakete  
> **Ziel:** eindeutige Quellen, nachvollziehbare Arbeitsschritte und widerspruchsfreie Übergaben

## 1. Grundprinzip

Das Projekt verwendet wenige kanonische, dauerhaft gepflegte Steuerungsdateien. Jede Datei hat genau eine Aufgabe.

Ein Sachverhalt soll nur an einer Stelle führend beschrieben werden. Andere Dokumente dürfen darauf verweisen oder ihn knapp zusammenfassen, aber keine abweichende zweite Wahrheit aufbauen.

Die sechs wichtigsten Einstiegsdateien sind:

1. `AGENTS.md` – unveränderliche Projekt- und Agentenregeln
2. `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` – diese Arbeits- und Dokumentationsordnung
3. `docs/PROJEKTUEBERSICHT.md` – kompakter technischer Einstieg
4. `docs/IMPLEMENTATION_ROADMAP.md` – Gesamtfahrplan und Zielarchitektur
5. `task.md` – aktueller Arbeits- und Prüfstatus
6. `ÜBERGABE.md` – operativer Einstieg in den zuletzt verifizierten Stand

Code und erfolgreich reproduzierbare Tests bleiben die maßgebliche Wahrheit darüber, was tatsächlich implementiert ist.

---

## 2. Dokumentenlandkarte

| Datei oder Bereich | Verbindliche Aufgabe | Wird aktualisiert, wenn |
| --- | --- | --- |
| `AGENTS.md` | Dauerhafte Regeln, Technologieentscheidungen, Quellenhierarchie, Sicherheits- und Arbeitsvorgaben | sich eine langfristig verbindliche Projektregel ändert |
| `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` | Rollen der Dokumente, Pflegeprozess, Benennung, Abschluss- und Übergaberegeln | sich die Dokumentations- oder Arbeitsweise ändert |
| `docs/PROJEKTUEBERSICHT.md` | Kompakte technische Orientierung über Ziel, Entscheidungen, Iststand und Paketfolge; keine zweite Detailquelle | sich Ziel, Paketstatus oder ein für den Einstieg wesentlicher Fakt ändert |
| `docs/IMPLEMENTATION_ROADMAP.md` | Gesamtziel, Architektur, Reihenfolge und Abnahmekriterien der Arbeitspakete | sich Zielarchitektur, Paketgrenze, Reihenfolge oder Paketstatus ändert |
| `task.md` | Aktueller Fortschritt, offene konkrete Aufgaben, aktive Restpunkte und verifizierte Testzahlen | bei Beginn, Blockierung und Abschluss eines Arbeitspakets sowie nach neuen Testbefunden |
| `ÜBERGABE.md` | Letzter operativ verifizierter Ist-Stand, Start-/Testbefehle, Schnittstellen, bekannte Besonderheiten und nächster Einstiegspunkt | wenn sich der ausführbare Stand, Bedienung, Schnittstellen, Risiken oder Einstiegspunkt relevant ändern |
| `README.md` | Kurzer benutzerorientierter Einstieg, Installation und regulärer Start | wenn sich Installation, Voraussetzungen oder Benutzerstart ändern |
| `config.yaml` | Tatsächliche sichtbare Laufzeitdefaults | wenn ein Default eingeführt oder geändert wird |
| `requirements.txt` | Tatsächliche direkte Python-Abhängigkeiten | wenn Abhängigkeiten geändert werden |
| `server-docs-for-client-development/` | Verbindlicher Serverprotokollvertrag | nur bei nachgewiesener Änderung des Serververtrags |
| `tests/` | Ausführbare Spezifikation des implementierten Verhaltens | zusammen mit jeder relevanten Implementierung oder Fehlerkorrektur |
| `docs/decisions/` (bei Bedarf anzulegen) | Dauerhafte Nachweise einzelner wichtiger Architektur- oder Produktentscheidungen | nur bei einer echten, später erklärungsbedürftigen Entscheidung |
| `docs/evaluations/YYYY-MM-DD_KURZNAME.md` (bei Bedarf) | Ausdrücklich nicht bindender, abgegrenzter Prüfauftrag für eine technisch noch offene Hypothese; keine Entscheidung und kein Implementierungsauftrag | während der zugehörigen Untersuchung; Ergebnisse müssen vor Übernahme in Roadmap, ADR oder Code ausdrücklich bewertet werden |
| `docs/work-packages/APNN_KURZNAME.md` (bei Bedarf) | Detailvertrag und Integrationsgrundlage für ein komplexes, mehrsitziges Arbeitspaket | bei Scope-, Vertrags-, Entscheidungs- oder Abnahmekriterienänderungen dieses Pakets |
| `docs/work-packages/APNN_KURZNAME_AUSFUEHRUNGSAUFTRAG.md` (bei Bedarf) | Operativer, auf ein Arbeitspaket begrenzter Auftrag mit Pflichtlektüre, festgelegten Entscheidungen, Test- und Abgabeformat; ersetzt weder Roadmap noch Paketvertrag | vor Beginn und während gezielter Korrekturrunden des Pakets |
| datierte Ordner unter `docs/` | Prüfberichte, Übergabesnapshots, Audits und Belegsammlungen | nicht fortlaufend; neue Erkenntnisse erhalten einen neuen datierten Bericht |
| `docs/archive/` und vorhandenes `docs/.archive/` | Historische, nicht mehr aktive Dokumente | nur beim bewussten Archivieren |

### 2.1 Was nicht als aktive Quelle gilt

Nicht verbindlich sind:

- automatisch nummerierte Kopien wie `Datei(1).md`,
- Chat-Exports,
- Antigravity-Brain-/Walkthrough-Dateien,
- Download-Sammlungen,
- alte Implementation-Pläne,
- Evaluierungsdokumente unter `docs/evaluations/`, solange ihr Ergebnis nicht
  ausdrücklich in eine aktive Quelle oder ein angenommenes ADR übernommen
  wurde,
- frühere Roadmap-, Task- oder Übergabeversionen,
- Prüf- und Stellungnahmedokumente ohne ausdrücklichen Status als aktive Quelle.

Solche Dateien dürfen zur historischen Klärung verwendet werden, aber niemals den aktuellen Code oder eine kanonische aktive Datei überschreiben.

---

## 3. Welche Information gehört wohin?

### 3.1 `AGENTS.md`: Was immer gilt

Hierhin gehören ausschließlich langfristige Regeln, zum Beispiel:

- verbindliche Technologien,
- verbotene Ersatzframeworks,
- Quellenhierarchie,
- Pflichtlektüre,
- Testpflicht,
- Schutz des vorhandenen Core,
- Datenschutz und Sicherheit,
- Reihenfolge der Arbeitsweise.

Nicht hierhin gehören:

- momentane Testzahlen,
- detaillierte Implementierungsberichte,
- einzelne Bugs,
- kurzfristige To-do-Listen.

### 3.2 Roadmap: Wohin das Projekt geht

`docs/IMPLEMENTATION_ROADMAP.md` beantwortet:

- Was ist das Gesamtziel?
- Welche Architektur ist vorgesehen?
- Welche Arbeitspakete gibt es?
- In welcher Reihenfolge werden sie umgesetzt?
- Was gehört ausdrücklich nicht zum Paket?
- Welche Abnahmekriterien gelten?
- Welcher Paketstatus ist erreicht?

Die Roadmap ist kein Tagesprotokoll. Einzelne Testmethoden, temporäre Fehler und lange Änderungslisten gehören nicht hinein.

### 3.3 Projektübersicht: Worum es geht und wo das Projekt steht

`docs/PROJEKTUEBERSICHT.md` beantwortet kompakt:

- Was ist das Projektziel?
- Welche Entscheidungen sind fest?
- Welche Komponenten existieren wirklich?
- Welche Arbeitspakete sind abgeschlossen oder offen?
- Welche Grenzen und Missverständnisse muss ein neuer Bearbeiter sofort kennen?
- Wo stehen die verbindlichen Details?

Sie darf Inhalte anderer kanonischer Quellen knapp zusammenführen, muss aber auf diese verweisen und darf keine abweichende Architektur, Testzahl oder Paketdefinition etablieren.

### 3.4 Task-Tracker: Was gerade zu tun ist

`task.md` beantwortet:

- Welches Paket ist offen, in Arbeit, blockiert oder abgeschlossen?
- Welche konkreten Punkte fehlen?
- Welche manuellen Prüfungen sind offen?
- Welche verifizierten Testzahlen gelten aktuell?
- Was ist der unmittelbar nächste Arbeitsschritt?

Empfohlene Statusbegriffe:

- `[OFFEN]`
- `[IN ARBEIT]`
- `[BLOCKIERT]`
- `[ABGESCHLOSSEN]`

Ein Paket darf nur als abgeschlossen markiert werden, wenn Code, Tests und die erforderlichen Dokumentationsupdates tatsächlich abgeschlossen sind.

### 3.5 Übergabe: Wo der nächste Agent praktisch einsteigt

`ÜBERGABE.md` beantwortet:

- Was läuft heute tatsächlich?
- Was ist nur geplant?
- Wie wird die Anwendung gestartet und getestet?
- Welche öffentlichen Schnittstellen sind relevant?
- Welche manuellen Prüfungen fehlen?
- Welche Risiken und Besonderheiten muss der nächste Agent kennen?
- Wo soll er konkret weiterlesen und weiterarbeiten?

Die Übergabe ist knapp, operativ und aktuell. Sie ist weder vollständige Roadmap noch Entwicklungsjournal.

### 3.6 README: Was ein Benutzer wissen muss

Die Root-`README.md` enthält nur:

- Zweck des Projekts,
- Voraussetzungen,
- Installation,
- regulären Start,
- kurze Bedienung,
- Verweise auf vertiefende Dokumentation.

Sie darf keine alternative Architektur oder abweichende Python-/Startbefehle definieren.

### 3.7 ADR: Warum eine wichtige Entscheidung getroffen wurde

Für dauerhafte Architektur- oder Produktentscheidungen wird bei Bedarf ein Architecture Decision Record angelegt:

`docs/decisions/ADR-NNN_KURZNAME.md`

Ein ADR ist sinnvoll, wenn:

- mehrere ernsthafte Alternativen bestanden,
- eine Entscheidung spätere Pakete bindet,
- eine bestehende Vorgabe bewusst präzisiert oder geändert wird,
- eine technisch notwendige Abweichung dokumentiert werden muss.

Kein ADR ist nötig für:

- Routineimplementierungen,
- kleine Bugfixes,
- reine Testergänzungen,
- bereits eindeutig in `AGENTS.md` oder Roadmap festgelegte Punkte.

Mindeststruktur:

```markdown
# ADR-NNN – Titel

Status: vorgeschlagen | angenommen | ersetzt
Datum: YYYY-MM-DD

## Kontext
## Entscheidung
## Alternativen
## Folgen
## Betroffene Dokumente und Tests
```

Wird eine Entscheidung ersetzt, bleibt das alte ADR erhalten und verweist auf das neue.

### 3.8 Arbeitspaket-Datei: Detailvertrag für komplexe Pakete

Eine Datei unter `docs/work-packages/` ist sinnvoll, wenn ein Arbeitspaket mehrere bestehende Komponenten integriert, über mehrere Sitzungen bearbeitet wird oder vor der Implementierung mehrere Verträge und Abnahmekriterien zusammengeführt werden müssen.

Sie enthält nur paketbezogene Details:

- Scope und Nicht-Ziele,
- relevante bestehende Schnittstellen,
- Integrationsfluss,
- ausdrücklich offene Entscheidungen,
- Fehler- und Testmatrix,
- Abnahmekriterien.

Sie ersetzt weder Roadmap noch `task.md`. Nach Paketabschluss bleibt sie als technische Paketdokumentation erhalten; Status und tatsächlich erreichte Ergebnisse müssen dann mit Code, Tests, Roadmap, `task.md` und `ÜBERGABE.md` synchronisiert werden.

---

## 4. Verbindlicher Ablauf eines Arbeitspakets

### Phase A – Auftrag abgrenzen

1. Den konkreten Benutzerauftrag bestimmen.
2. Prüfen, welches Arbeitspaket betroffen ist.
3. Spätere Pakete ausdrücklich aus dem Umfang ausschließen.
4. Offene Produktentscheidungen erkennen und vor Implementierung klären.

Dokumentation:

- `task.md`: Paket bei tatsächlichem Beginn auf `[IN ARBEIT]` setzen.
- Roadmap nur ändern, wenn Umfang oder Reihenfolge bewusst geändert wurden.
- Bei einer neuen bindenden Entscheidung gegebenenfalls ADR anlegen.

### Phase B – Quellen und Ausgangslage prüfen

1. Pflichtlektüre aus `AGENTS.md` lesen.
2. Für das Paket relevante Originaldokumente erneut öffnen.
3. Aktuellen Code und Schnittstellen prüfen.
4. Bestehende Tests vor der Änderung ausführen.
5. Ist-Zustand und Ziel-Zustand getrennt beschreiben.

Dokumentation:

- kurzer konkreter Umsetzungsplan im Arbeitskontext,
- bei mehrtägigen oder komplexen Paketen optional eine Paketdatei unter:

  `docs/work-packages/APNN_KURZNAME.md`

Eine Paketdatei ist nur nötig, wenn der Plan über mehrere Sitzungen erhalten bleiben muss. Sie darf Roadmap und Task nicht duplizieren.

### Phase C – Implementieren

1. Kleinste notwendige Änderung vornehmen.
2. Bestehende Schnittstellen und Konventionen respektieren.
3. Keine Folgepakete vorwegnehmen.
4. Keine funktionierenden Core-Komponenten vorsorglich refactoren.
5. Neue oder geänderte Semantik sofort durch Tests absichern.

Dokumentation während der Umsetzung:

- konkrete Arbeitsschritte und Restpunkte in `task.md`,
- wichtige, dauerhafte Entscheidung im ADR,
- keine laufenden Zwischenstände in `ÜBERGABE.md`.

### Phase D – Verifizieren

1. Neue gezielte Tests ausführen.
2. Bestehende Regressionstests ausführen.
3. Gesamtsuite ausführen.
4. Relevante manuelle oder Live-Tests getrennt ausführen.
5. Fehler iterativ beheben.
6. Testseiteneffekte in temporäre Verzeichnisse isolieren.

Testberichte müssen unterscheiden:

- Unit-/Integrationstests,
- Gesamtsuite,
- Connection-Smoke-Test,
- manueller Windows-Test,
- echter Mikrofon-/Server-End-to-End-Test.

„Live-Test erfolgreich“ ohne genaue Testart ist unzulässig.

### Phase E – Dokumentation synchronisieren

Nach erfolgreicher Verifikation werden, soweit betroffen, in dieser Reihenfolge aktualisiert:

1. `task.md`
2. `docs/IMPLEMENTATION_ROADMAP.md`
3. `ÜBERGABE.md`
4. `README.md`
5. Konfigurationsbeispiele und ADRs

Dabei gilt:

- `task.md` erhält konkrete Status- und Testwerte.
- Roadmap erhält Paketstatus und dauerhaft relevante Ziel-/Ist-Aussagen.
- Übergabe erhält den neuen operativen Stand und nächsten Einstieg.
- README wird nur bei benutzerrelevanten Änderungen angepasst.

### Phase F – Abschluss und Materialisierung prüfen

1. Geänderte Dateien erneut direkt aus dem Projektpfad lesen.
2. Prüfen, dass die Änderungen wirklich auf der Festplatte stehen.
3. Sicherstellen, dass keine Testdaten, Logs, Caches oder Datenbanken versehentlich neu im Projekt liegen.
4. Geänderte Dateien und ausgeführte Tests im Abschlussbericht nennen.
5. Bei Übergaben, Releases oder früheren Materialisierungsproblemen zusätzlich Größen und SHA-256-Hashes dokumentieren.
6. Paket auf `[ABGESCHLOSSEN]` setzen.
7. Danach stoppen.

---

## 5. Aktualisierungsmatrix

| Ereignis | Roadmap | Task | Übergabe | README | ADR |
| --- | --- | --- | --- | --- | --- |
| Arbeitspaket beginnt | nur bei geändertem Umfang | ja | nein | nein | falls Entscheidung nötig |
| Implementierungsdetail ohne Außenwirkung | nein | bei relevantem Restpunkt | nein | nein | nein |
| Testzahl ändert sich | Paketstand knapp | ja | ja, wenn Übergabestand relevant | nein | nein |
| Öffentliche Core-Schnittstelle ändert sich | ja | ja | ja | nur bei Benutzerbezug | gegebenenfalls |
| Start-/Installationsweg ändert sich | nur bei Architekturbezug | ja | ja | ja | selten |
| Architekturentscheidung | ja | ja | ja | nur bei Benutzerbezug | ja |
| Bug gefunden, noch nicht behoben | nur bei Planwirkung | ja | ja, wenn Übergaberisiko | nein | selten |
| Bug behoben | nur bei Paket-/Architekturwirkung | ja | ja | nur bei Benutzerwirkung | selten |
| Manueller Test offen/erledigt | nein | ja | ja | nein | nein |
| Paket abgeschlossen | ja | ja | ja | gegebenenfalls | bestehendes ADR finalisieren |
| Reiner Auditbericht | nein | nein | nur bestätigte aktuelle Folgen | nein | nein |

---

## 6. Konventionen gegen Widersprüche

### 6.1 Ist und Ziel immer trennen

Verwende eindeutige Überschriften:

- `Implementiert`
- `Automatisiert verifiziert`
- `Historisch als Smoke-Test dokumentiert`
- `Noch nicht integriert`
- `Geplant`
- `Manuell offen`
- `Bekanntes Risiko`

### 6.2 Präzise Begriffe

Folgende Begriffe dürfen nur mit genauer Bedeutung verwendet werden:

- **getestet:** Welche Tests und welcher Umfang?
- **Live-Test:** Health, Handshake, Audio oder vollständiges End-to-End?
- **abgenommen:** Durch wen und auf welcher Belegbasis?
- **Reconnect:** Nur Transport oder vollständige Betriebswiederaufnahme?
- **gesichert:** Im RAM, persistent in SQLite oder crash-sicher?
- **implementiert:** Als isolierte Komponente oder vollständig integriert?
- **exakt einmal:** Auf Event-, History-, Queue- oder Attempt-Ebene?

### 6.3 Testzahlen nur nach Ausführung

Testzahlen dürfen nur eingetragen werden, wenn:

- der genannte Befehl tatsächlich ausgeführt wurde,
- der Lauf erfolgreich war,
- der Umfang eindeutig genannt wird.

Erwartete oder hochgerechnete Testzahlen werden nicht als Ergebnis dokumentiert.

### 6.4 Keine nummerierten aktiven Kopien

Aktive Dateien behalten ihren kanonischen Namen.

Unzulässig als aktive Quelle:

- `task(1).md`
- `ÜBERGABE_neu.md`
- `IMPLEMENTATION_ROADMAP_final2.md`

Historische Stände erhalten stattdessen:

`YYYY-MM-DD_TYP_KURZTHEMA.md`

und werden in einem datierten Prüf-/Übergabeordner oder im Archiv abgelegt.

### 6.5 Keine parallelen Wahrheiten

Wenn eine kanonische Datei falsch ist:

1. Fehler belegen,
2. kanonische Datei korrigieren,
3. abhängige Zusammenfassungen synchronisieren,
4. alte Version archivieren oder als historischen Beleg belassen.

Nicht dauerhaft eine zweite „korrigierte“ aktive Datei daneben pflegen.

---

## 7. Dokumentkopf-Konvention

Längere operative oder verbindliche Dokumente sollen am Anfang enthalten:

```markdown
> Status: verbindlich | aktiv | historisch | Entwurf
> Stand: YYYY-MM-DD
> Zuständig für: ...
> Letzte Verifikation: ...
```

Für eine Übergabe zusätzlich:

- Projektpfad,
- aktives Arbeitspaket,
- letzter erfolgreicher Testlauf,
- nächster Einstiegspunkt.

---

## 8. Archiv- und Auditregeln

### 8.1 Archiv

Archivierte Dateien:

- bleiben unverändert,
- werden nicht fortlaufend korrigiert,
- überschreiben keine aktive Quelle,
- dienen nur der Nachvollziehbarkeit.

Neue Archivierung erfolgt einheitlich unter:

`docs/archive/`

Der bereits vorhandene Ordner `docs/.archive/` wird bis zu einer ausdrücklich beauftragten Bereinigung ebenfalls als nicht verbindliches Archiv behandelt.

### 8.2 Datierte Prüf- und Übergabeordner

Datierte Ordner wie:

`docs/2026-07-24_PROJEKT_UEBERGABE/`

enthalten Snapshots, Audits, Stellungnahmen und Originalbelege. Sie werden nicht wie die Root-`ÜBERGABE.md` fortlaufend gepflegt.

Ein bestätigter Auditbefund wird erst dann Teil des aktiven Projektstands, wenn die zuständige kanonische Datei aktualisiert wurde.

### 8.3 Aktuelle Übergangssituation

Die Datei:

`docs/2026-07-24_PROJEKT_UEBERGABE/2026-07-24_AKTUALISIERTE_GESAMTUEBERGABE_REALTIME_STT_CLIENT.md`

ist der korrigierte Snapshot vom 24. Juli 2026. Die für den aktuellen Einstieg relevanten Befunde wurden am selben Tag in `docs/PROJEKTUEBERSICHT.md`, Roadmap, `task.md`, Root-`ÜBERGABE.md` und README übernommen. Die datierte Gesamtübergabe bleibt damit historischer Prüfbeleg und wird nicht parallel fortgeschrieben.

---

## 9. Abschlusscheckliste

Ein Arbeitspaket ist erst dokumentarisch abgeschlossen, wenn alle zutreffenden Punkte erfüllt sind:

- [ ] Auftrag und Paketgrenze waren eindeutig.
- [ ] Relevante Originalquellen wurden gelesen.
- [ ] Vorheriger Teststand wurde geprüft.
- [ ] Nur der beauftragte Umfang wurde geändert.
- [ ] Neue Semantik besitzt Tests.
- [ ] Gezielte Tests sind erfolgreich.
- [ ] Gesamtsuite ist erfolgreich.
- [ ] Manuelle und Live-Tests sind getrennt ausgewiesen.
- [ ] `task.md` ist aktuell.
- [ ] Roadmap ist bei Paket-/Architekturänderung aktuell.
- [ ] `ÜBERGABE.md` beschreibt den neuen operativen Stand.
- [ ] README und Konfiguration stimmen bei Benutzer-/Defaultänderungen.
- [ ] Wichtige Entscheidungen besitzen gegebenenfalls ein ADR.
- [ ] Keine Secrets wurden ausgegeben.
- [ ] Keine unerwünschten DB-, Log-, Cache- oder Laufzeitdateien entstanden.
- [ ] Dateien wurden nach dem Schreiben erneut von der Festplatte geprüft.
- [ ] Nächster Einstiegspunkt ist eindeutig.
- [ ] Folgepakete wurden nicht vorweggenommen.

---

## 10. Kurzregel für zukünftige Agenten

> `AGENTS.md` sagt, was immer gilt. Die Roadmap sagt, wohin das Projekt geht. `task.md` sagt, was gerade offen oder erledigt ist. `ÜBERGABE.md` sagt, wie der zuletzt verifizierte Stand praktisch weitergeführt wird. Code und Tests sagen, was wirklich existiert. Serverdokumente sagen, wie das Protokoll tatsächlich funktioniert. ADRs erklären nur wichtige Entscheidungen. Datierte Audits und Archive sind Belege, keine parallele Gegenwart.
