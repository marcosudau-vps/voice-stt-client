# Vorbereitung Logging / Observability – Code-Audit und implementation-ready Architekturplan

## Zweck

Wir wollen vor der eigentlichen Triggerarchitektur-Migration eine **strikt beobachtende Logging-/Observability-Foundation im Desktop-Client** einführen.

Die endgültige Planung ist noch nicht freigegeben. Deshalb soll in diesem Auftrag **noch kein Produktcode implementiert oder verändert werden**.

Der Auftrag soll stattdessen die bestehende Client-/Server-Infrastruktur vollständig daraufhin untersuchen, **wie die bereits entworfene Logging-Zielarchitektur konkret und möglichst integrationsarm in den heutigen Code eingebaut werden kann**.

Das Ergebnis soll so konkret sein, dass anschließend aus den Erkenntnissen ein freigegebenes Work Package erstellt und danach weitgehend mechanisch implementiert werden kann.

---

# Arbeitsbereich

Workspace:

```text
P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude
```

Relevante Repositories:

```text
voice-stt-client
voice-stt-server
led_controller_respeaker-v3
```

Arbeitsunterlagen liegen im Bereich:

```text
ARBEITSDATEIEN
```

Insbesondere relevant:

```text
AP_THEMA_LOGGING/
    .unverbindlich_ungeprueft/ErsterEntwurf_Logging.md
    LOGGING_V1_ABGRENZUNG_ENTWURF.md
    LOGGING_ZIELBILD_ARCHITEKTUR_GESAMTSPEZIFIKATION_ENTWURF.md
```

sowie:

```text
Implementierungsdateien/VonModelErstellt/einheitliche-triggerarchitektur/
    code-architektur-baseline/
        LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md
        ...
```

## Autorität der Unterlagen

Wichtig:

- Der erste Logging-Entwurf ist **ungeprüft und unverbindlich**.
- Die Logging-Zielbild- und V1-Dateien sind ebenfalls **Entwürfe**, keine freigegebene Spezifikation.
- Produktivcode ist die primäre Quelle für den tatsächlichen Ist-Zustand.
- Bestehende Tests sind ergänzende Evidence, aber keine automatische Architekturwahrheit.
- `LETZTE_ARCHITEKTURKLAERUNGEN_VOR_PLAN_FREEZE.md` enthält bereits verifizierte Erkenntnisse zur bestehenden Trigger-/Eventarchitektur und darf als Analysegrundlage verwendet werden.

Bekannter und für diesen Auftrag wichtiger Architekturstand:

```text
/ws/transcribe
= Runtime-/Control-Plane für Session und künftig ActivationMirror

/ws/logs
= Observability-/Eventstream
= darf nicht zur fachlichen Lifecycle-Autorität des Clients werden
```

Diese Trennung darf durch das Logging-Vorhaben nicht wieder verwischt werden.

---

# Harte Arbeitsregeln

Für diesen Auftrag:

- KEINE Produktcodeänderungen;
- KEINE Testcodeänderungen;
- KEINE Configänderungen;
- KEINE Änderungen an aktiver Produktdokumentation;
- KEIN Commit;
- KEIN Push;
- KEIN Merge;
- KEIN Rebase;
- KEIN Tag;
- KEIN PR.

Erlaubt:

- vollständige Codeanalyse;
- Tests lesen und bei Bedarf ausführen;
- vorhandene Settings/UI-Strukturen untersuchen;
- Browserclient untersuchen;
- vorhandene DB-/Persistence-Muster untersuchen;
- vorhandene Logging-Konfiguration untersuchen;
- kleine diagnostische Skripte außerhalb der Produktrepos;
- Analyse-/Planungsartefakte im Arbeitsbereich erstellen.

Keine Implementierung beginnen.

---

# 1. Bestehendes Client-Logging vollständig inventarisieren

Untersuche im `voice-stt-client`:

- aktuelles Python-Logging;
- `logging_setup.py` bzw. entsprechende Initialisierung;
- Logger-Hierarchie;
- Handler;
- Formatters;
- Log-Level;
- Datei-Logging, falls vorhanden;
- Console Logging;
- Exception Logging;
- Thread-/Task-bezogene Logs;
- bestehende strukturierte `extra`-Nutzung;
- alle relevanten `logger.*`-Aufrufe;
- Stellen mit `print()` oder sonstigen Nebenwegen.

Erstelle eine Übersicht:

| Komponente | heutiges Logging | Logger | strukturierte Daten? | Frequenz | geeignet für Unified Handler? |
|---|---|---|---|---|---|

Besonders unterscheiden:

```text
gewöhnliche technische Logs
fachlich interessante Observability-Events
hochfrequente Performance-/Audio-Ereignisse
Fehler-/Exception-Pfade
```

---

# 2. Bestehende Server-Eventstream-Integration analysieren

Untersuche exakt den heutigen Pfad:

```text
/ws/logs
→ Client EventStream
→ Normalisierung
→ SessionCoordinator / Controller
→ FeedbackController
→ LED / Sound / UI
```

Ermittle:

- Verbindungsaufbau;
- Auth/Parameter;
- Replay;
- Cursor;
- Persistenz des Cursors;
- Eventmodell;
- Eventnormalisierung;
- Fan-out-Strukturen;
- Subscriber-/Callback-Modell;
- Thread-/async-Grenzen;
- Queueing;
- Fehlerverhalten;
- Reconnect;
- Event-Dedupe;
- Eventreihenfolge.

Die entscheidende Frage:

> An welcher Stelle lässt sich ein `ServerLiveAdapter` als **zusätzlicher passiver Consumer** anbinden, ohne Feedback-, Runtime- oder Eventstreamlogik zu verändern?

Ergebnis ausdrücklich als:

```text
EMPFOHLENER SERVER-LIVE-HOOK:
<konkrete Datei/Klasse/Funktion>

WARUM:
...

NICHT VERWENDEN:
<andere naheliegende Stellen und Begründung>
```

---

# 3. Fan-out-Möglichkeiten prüfen

Die Zielarchitektur verlangt:

```text
Serverevent
├── Feedback
└── Logging
```

und nicht:

```text
Serverevent
→ Logging
→ Feedback
```

Prüfe, welche bestehende Struktur dafür am besten geeignet ist.

Untersuche:

- Eventbus vorhanden?
- Signal-/Callback-Verteiler?
- Coordinator?
- mehrere Subscriber bereits möglich?
- müsste ein kleiner Fan-out-Punkt ergänzt werden?
- kann Logging sauber parallel angeschlossen werden?

Falls minimale zusätzliche Infrastruktur nötig wäre:

> nur konzeptionell beschreiben, noch nicht implementieren.

---

# 4. Strukturierte Client-Observation-Hooks präzisieren

Die letzte Architekturuntersuchung hat bereits Beobachtungspunkte identifiziert.

Verifiziere und konkretisiere sie jetzt für das Logging-Vorhaben.

Mindestens:

```text
App lifecycle
Controller lifecycle
WebSocket connection
Eventstream connection
Reconnect
Hotkey
Trigger command sent
Trigger ack received
Audio capture / stream start-stop
Settings apply
Config validation
Feedback decision
LED dispatch / failure
Warnings / blocked actions
Server error classification
Performance timings
Queue states
```

Für jeden Hook:

| Eventtyp | Datei/Funktion | bereits vorhandene Daten | fehlende Korrelationsfelder | Frequenz | Python-Log oder Structured Event? |
|---|---|---|---|---|---|

Besonders markieren:

```text
HOT PATH
```

für:

- Audio callback;
- Audio packet sender;
- VAD-nahe Pfade;
- WebSocket receive loops;
- hochfrequente Performancepfade.

Für HOT PATH gilt:

> keine synchronen DB-/File-Aufrufe und keine Logzeile pro Audiochunk.

Nur Zustandswechsel bzw. aggregierte Messwerte.

---

# 5. Canonical Record gegen reale Daten prüfen

Nimm das derzeit vorgeschlagene kanonische Modell als Hypothese:

```text
record_id

source_timestamp
received_at
monotonic_ns

producer_kind
producer_id
host
instance_id
process_id

channel
level
type
component

session_id
generation
activation_id
segment_id
command_id
event_id
correlation_id

scope

message
details
raw

replayed
```

Prüfe Feld für Feld am realen Code:

- ist es heute verfügbar?
- wo entsteht es?
- Datentyp?
- Stabilität?
- Sessionübergreifend eindeutig?
- optional oder verpflichtend?
- stammt es von Client oder Server?
- sollte es gespeichert oder nur abgeleitet werden?

Erstelle:

| Feld | Typ | Pflicht/optional | Quelle | heute vorhanden | Empfehlung |
|---|---|---|---|---|---|

Zusätzlich prüfen:

- brauchen wir `sequence`?
- brauchen wir `schema_version`?
- brauchen wir `provider/source_record_id`?
- brauchen wir separate `server_event_id` und lokale `record_id`?
- ist `host` sinnvoll oder reicht `instance_id`?
- wie sollen Enum-Werte versioniert werden?

Keine unnötigen Felder hinzufügen.

---

# 6. Channel-Modell verifizieren

Server-Channels:

```text
System
Audit
Transcription
Performance
```

Prüfe:

- wie sie heute exakt kodiert sind;
- Groß-/Kleinschreibung;
- ob es weitere tatsächliche Channels gibt;
- ob alle Events immer einen Channel besitzen;
- ob Channel und Eventtyp unabhängig sind.

Für Client-Logs bestimmen:

> Können dieselben vier Channels sinnvoll wiederverwendet werden?

Falls zusätzliche Client-Channels wirklich nötig sind:

- konkret begründen;
- minimale Anzahl empfehlen.

Keine Channel-Explosion.

---

# 7. Replay / Dedupe technisch klären

Untersuche den realen `/ws/logs`-Replaymechanismus.

Kläre:

- Event-ID-Format;
- Stabilität;
- Lebensdauer;
- Serverneustart;
- Cursor;
- Replaygrenzen;
- bereits vorhandene Dedupe;
- Verhalten nach Reconnect.

Die entscheidende Frage:

> Welcher eindeutige Schlüssel eignet sich zur lokalen Persistenz, damit replayte Serverevents nicht doppelt gespeichert werden?

Ergebnis:

```text
EMPFOHLENER DEDUPE KEY:
...

GARANTIEN:
...

GRENZEN:
...
```

Falls keine stabile globale ID existiert, genaue Alternative ausarbeiten.

---

# 8. Bestehende lokale Persistenzmuster untersuchen

Suche im Client nach bestehenden SQLite-/Persistence-Lösungen.

Insbesondere:

- TranscriptHistory;
- Cursor Store;
- andere SQLite-Dateien;
- DB-Pfade;
- Datenverzeichnis;
- Migrationen;
- Cleanup;
- Threading;
- Locking;
- Tests.

Bewerte:

> Welche bestehenden Muster sollten für `SQLiteLogStore` wiederverwendet werden?

Nicht blind kopieren.

Untersuchen:

- SQLite connection per worker?
- WAL sinnvoll?
- busy timeout?
- schema version?
- Migrationstabelle?
- Batch insert?
- Cleanupstrategie?
- DB-Größenlimit?

---

# 9. SQLite-Schema konkret vorbereiten

Noch keine DB anlegen.

Aber aus dem Canonical Record ein **implementation-ready Schema** ableiten.

Liefern:

```sql
CREATE TABLE ...
CREATE INDEX ...
```

als Planungsentwurf.

Zusätzlich:

- Schema-Versionierung;
- Migrationsstrategie;
- Dedupe Constraint;
- JSON-Felder;
- Timestamp-Repräsentation;
- Level-/Channel-Speicherung;
- nullable Felder;
- Retention Query;
- Pagination Query.

Prüfen:

> Welche Indizes sind wirklich für die geplanten Filter erforderlich?

Keine unnötige Überindizierung.

---

# 10. Queue / Worker / Backpressure gegen reale Threads planen

Untersuche die tatsächlichen Concurrency-Grenzen des Clients.

Mindestens:

- Qt Main Thread;
- Audio callback thread;
- Audio sender;
- STTSession asyncio loop;
- EventStream asyncio loop;
- Controller;
- LED worker;
- bestehende ThreadPools/Queues.

Dann einen präzisen Vorschlag:

```text
Producer
→ try_enqueue()
→ bounded priority queue
→ LoggingWorker
→ SQLite batch
→ optional sinks
```

Festlegen/empfehlen:

- Queue-Typ;
- Queue-Größe als konfigurierbarer Default;
- Worker Thread vs asyncio Task;
- Batchgröße;
- Flushintervall;
- Shutdown;
- max. Flushzeit;
- Dropstrategie;
- Prioritäten;
- Drop Counter;
- Health State.

Wichtig:

> Logging darf niemals Producer blockieren.

---

# 11. Logging-interne Failure Domain planen

Prüfe vorhandene Error-/Health-Mechanismen.

Plane exakt, wie Fehler innerhalb der Logging-Komponente gemeldet werden, ohne Rekursion:

```text
SQLite failure
File sink failure
Malformed record
Worker crash
Queue overflow
Retention failure
```

Keine dieser Meldungen darf erneut über denselben UnifiedLogHandler laufen.

Empfehle:

- internen Health-State;
- Counters;
- stderr;
- UI-Status;
- Recovery.

---

# 12. Privacy / Redaction Audit

Suche im heutigen Client und Server nach sensiblen Daten, die in Logs oder Raw-Payloads auftauchen könnten:

- Admin API Key;
- Authorization;
- WebSocket Queryparameter;
- Tokens;
- Passwörter;
- Transkriptionstext;
- Dateipfade;
- Host-/Userinformationen;
- Audioinhalt;
- sonstige Secrets.

Erstelle:

| Feld/Quelle | sensitiv? | darf lokal gespeichert werden? | Redaction-Regel |
|---|---|---|---|

Besonders:

> Ein zukünftig in der UI gespeicherter Admin-Key darf niemals durch Python Logging, Raw Payload oder Exception Context in die Logdaten gelangen.

---

# 13. Settings-Architektur untersuchen

Untersuche die reale Settings-Infrastruktur:

- Config-Dataclasses;
- Metadata;
- SettingsDialog;
- dynamische Sichtbarkeit;
- Apply;
- Persistenz;
- Runtime Apply;
- Reconnect;
- Validierung.

Plane, wie ein eigener Logging-Bereich sauber integriert werden kann.

Unterscheide ausdrücklich:

## Logging Configuration

z. B.:

```text
enabled
level
sqlite/history enabled
retention
max entries
file enabled
file format
directory
live buffer size
store transcription content
store raw payload
```

## Log View

ist **keine Config-Komponente**, sondern Query/UI.

Empfehle konkret:

- eigener Settings-Tab?
- eigene Log-Seite?
- beide im bestehenden Dialog?
- welche Komponenten sollten getrennt sein?

Noch keine UI bauen.

---

# 14. LogView gegen bestehende PySide-Architektur planen

Untersuche:

- bestehende Tabs;
- Models;
- Views;
- QTableView-Verwendung;
- Thread→UI Signale;
- Styling;
- Such-/Filterpatterns;
- Settingsdialog-Lifetime.

Danach konkrete Modul-/Klassenempfehlung:

```text
LogTableModel
LogQueryController / QueryService
LogFilterBar
LogDetailView
LogPage
```

Prüfen:

- Live Updates;
- Pagination;
- History;
- Auto-scroll;
- Selection/Details;
- Raw JSON.

V1 bewusst klein halten.

---

# 15. Query Provider Interface zukunftsfest definieren

Dies ist wichtig, obwohl V1 zunächst nur lokale SQLite-Historie nutzt.

Entwerfe die minimale Provider-Schnittstelle so, dass später ohne Umbau möglich sind:

```text
LocalLogProvider
ServerHistoryProvider
ServerGlobalLogProvider
LED Provider
weitere Provider
```

Mindestens berücksichtigen:

```text
query(filter, cursor, limit)
provider status
capabilities
pagination
time ranges
error/auth required
```

Nicht über-engineeren.

Liefern:

- Interface;
- Datenmodelle;
- QueryFilter;
- QueryPage/Result;
- ProviderStatus.

---

# 16. Admin-/Server-Control-Grenze untersuchen

Noch **keine Admin-Funktion implementieren**.

Aber vorhandenen Server-/Browserclient-Code untersuchen:

- Admin API Key;
- Authentifizierungsmechanismus;
- serverweite Einstellungen;
- Modellwahl;
- Runtime Status;
- historische/global Logs;
- bestehende Commands;
- Capability-Modell.

Ziel:

> Sicherstellen, dass V1 keine Schnittstelle baut, die später mit dem vorhandenen Admin-Control-Contract kollidiert.

Insbesondere bestätigen:

```text
LoggingCore
    kennt keinen Admin-Key

ServerHistoryProvider
    darf später ServerControlConnection nutzen

ServerControlConnection
    besitzt Auth/Capabilities
```

Erstelle nur Integrationsgrenzen, keine Umsetzung.

---

# 17. LED-Controller-Erweiterbarkeit prüfen

Nur ein sehr kleiner Audit.

Untersuche:

- aktuelles Python Logging;
- mögliche öffentliche Adapterpunkte;
- ob bereits Event-/Callback-Infrastruktur existiert.

Ziel:

> Bestätigen, dass ein späterer `LedAdapter` möglich ist, ohne CanonicalRecord oder LoggingCore umzubauen.

Keine LED-Änderung.

---

# 18. Modulstruktur gegen echten Repo-Baum validieren

Die bisherige Idee lautet ungefähr:

```text
core/observability/
    models.py
    normalizer.py
    ingress.py
    manager.py
    health.py
    worker.py
    adapters/
    storage/
    query/
    sinks/

ui/logs/
```

Prüfe das gegen die reale Clientstruktur.

Empfehle danach die **konkrete tatsächliche Modulstruktur**.

Dabei vermeiden:

- Monolithdatei;
- unnötige Microservices;
- zyklische Imports;
- Qt-Abhängigkeit im Core;
- direkte DB-Nutzung aus UI.

---

# 19. V1-Implementierungsreihenfolge vorbereiten

Erstelle aus allen Befunden eine kleinschrittige Reihenfolge.

Beispielstruktur:

```text
OBS-01 Canonical Models
OBS-02 Ingress + Health
OBS-03 Python Handler
OBS-04 SQLite Store
OBS-05 Worker / Backpressure
OBS-06 Server Live Adapter
OBS-07 Structured Client Hooks
OBS-08 Query Layer
OBS-09 Settings
OBS-10 Minimal Log View
OBS-11 Failure / Performance Gate
```

Aber Reihenfolge anhand des Codes selbst festlegen.

Für jedes Paket:

- Ziel;
- Dateien;
- neue Komponenten;
- Änderungen bestehender Komponenten;
- Tests;
- Negativtests;
- Failure Tests;
- Akzeptanzkriterien;
- Abhängigkeiten.

---

# 20. Teststrategie vor Implementierung

Entwerfe Tests, die nicht wieder falsche Sicherheit erzeugen.

Mindestens:

## Unit

- Canonical normalization;
- Redaction;
- Dedupe;
- Store;
- Query;
- Backpressure.

## Integration

- Python logging → SQLite;
- Server event → SQLite;
- structured client event → SQLite;
- Replay;
- Shutdown/Flush.

## Failure

- SQLite read-only/unavailable;
- file sink failure;
- queue full;
- malformed record;
- worker exception.

## Runtime isolation

Der wichtigste Test:

```text
Logging kaputt
→ Audio / WebSocket / Controller / Feedback funktionieren weiter
```

## Performance

- Burst;
- Batch write;
- Hot-path overhead.

---

# 21. Keine Triggerarchitektur reparieren

Während dieser Untersuchung können Stellen auffallen, die zur laufenden Triggerarchitektur gehören.

Diese dürfen:

- dokumentiert;
- als Hook identifiziert;
- mit IDs/Korrelation versehen geplant werden.

Sie dürfen **nicht** repariert oder umgebaut werden.

Die Logging-Vorbereitung darf insbesondere nicht:

- ActivationController ändern;
- Finalisierung reparieren;
- Continuous Streaming einführen;
- ActivationMirror implementieren;
- `mode` entfernen;
- Hotkeysemantik ändern;
- Wake-Word-Pause implementieren.

---

# 22. Erwartete Artefakte

Erstelle im Arbeitsbereich einen neuen Logging-Analyseordner und mindestens:

```text
LOGGING_CODE_INTEGRATION_AUDIT.md
LOGGING_CANONICAL_SCHEMA_AND_STORAGE.md
LOGGING_CONCURRENCY_FAILURE_MODEL.md
LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md
LOGGING_V1_IMPLEMENTATION_PLAN.md
LOGGING_OPEN_DECISIONS.md
```

Optional ergänzend:

```text
LOGGING_TEST_MATRIX.md
```

Keine Produktdateien ändern.

---

# 23. Anforderungen an `LOGGING_OPEN_DECISIONS.md`

Nur echte Entscheidungen aufnehmen.

Für jede:

```text
ID
Frage
technische Optionen
Vor-/Nachteile
Empfehlung
blockiert V1? JA/NEIN
```

Keine Fragen aufführen, die anhand des Codes eindeutig beantwortbar sind.

---

# 24. Anforderungen an den Implementation Plan

Der Plan muss so konkret sein, dass ein späterer Coding-Agent nicht erneut die Architektur erfinden muss.

Für jedes Arbeitspaket:

```text
Scope
Non-Scope
Dateien/Komponenten
Sollzustand
Implementierungsschritte
Tests
Negativtests
Failure Tests
Akzeptanzkriterien
Evidence
```

---

# 25. Abschlussbewertung

Am Ende eindeutig beantworten:

```text
A. Ist die vorgeschlagene Logging-Zielarchitektur mit dem heutigen Client vereinbar?
B. Welche Teile können direkt wiederverwendet werden?
C. Welche Teile brauchen neue Infrastruktur?
D. Gibt es technische Blocker für Logging V1?
E. Welche Entscheidungen müssen Marco/Architekturreview noch treffen?
F. Ist V1 danach READY FOR WORK-PACKAGE FREEZE?
```

Klassifikation:

```text
READY FOR FREEZE
DECISIONS REQUIRED
FURTHER INVESTIGATION REQUIRED
```

Falls weitere Untersuchung erforderlich:

> ausschließlich die konkrete fehlende Information nennen.

Keine Implementierung beginnen.

Danach stoppen.





https://github.com/Th0rgal/sandboxed.sh

Super, das haste ich gut hinbekommen. Die heute Morgen veröffentlichte Releaseversion bricht  bei Docker mit dem Fehler ab, dass sie keine Config hat.(deswegen kam das thema heute auf). 
Da ich das so nicht dort stehen lassen möchte, möchte ich, bitte ich dich, jetzt zum Abschluss einmal noch alle Vorbereitungen dafür zu treffen, dass wir eine neue Release-Version hochladen können. 
Also bitte fixe die von dir angesprochenen Punkte. Schau noch mal insgesamt, ob etwas besser abgesichert werden müsste, irgendwie inkonsistent ist oder ob du allgemein noch irgendwo mit dem Pollier-Tuch drüber wischen kannst, 
damit wir bei diesem Versuch die bestmögliche Version des naktuellen Standes veröffentlichen können. 

und weil wir jetzt schon einmal so im Thema bist und ich so gut in dem Projekt auskennst. Gehe doch auch noch mal bitte über die Dokumentation und guck, ob alles richtig dokumentiert ist oder ob etwas fehlt oder  falsch-/unter- repräsentiert ist., usw... 
Dabei möchte  würde ich dich noch um ein kleines Herzensthema von mir bitten. Und zwar, die aktuelle Dokumentation ist zwar gut,  die kommt mir nur sehr unstrukturiert und so ein bisschen durcheinander vor. Wenn du da vielleicht, ich sag mal so eine Indexdatei, wo dann alle Dateien noch mal kurz beschrieben und verlinkt sind, so als Inhaltsübersicht als erste Datei so gesehen. 
Und dann bei den anderen Dateien, die vielleicht so ein bisschen ordnen, nur grob. Aber momentan kommt  zwischendurch etwas, was so eher an die Agents, die auf den Workspaces arbeiten sollen, gerichtet ist. Dann kommt wieder was zur Installation, dass eher für Anwender ist. Dann kommt wieder was für Entwickler, also Release oder so. Dass du das vielleicht so ein bisschen in eine Struktur bringst, die sinnvoll ist.
Und als letzte Datei dort könntest du neu anlegen und auch direkt den ersten Eintrag machen, weil bisher wurde keine geführt, eine CHANGELOG.md... 

Da wir wieder Sorge haben müssen, dass dein Nutzungslimit zwischendurch alle geht, gehe bitte in der folgenden Prioritätsreihenfolge vor. Erst alles, was noch so gefixt werden muss, also wirklich Fehler, beziehungsweise da sind ja dann die Punkte zum Beispiel, die du angesprochen hast. Na, also Produktcode, wenn du so willst. Danach mach bitte einmal so gesehen die Release-Tests, aber ohne was zu pushen oder committen. 
Aber nur einmal testen, ob das Release funktionieren würde oder ob es da irgendwelche Probleme gibt. Und ja, wenn du das gemacht hast, dann eben die Dokumentation. Und geh da auch so vor, dass du so die wichtigsten Sachen zuerst machst und, ja, umso weiter du nach hinten kommst, dann halt immer mehr Richtung Feinschliff gehst. Einfach, weil es dein Nutzungslimit irgendwann aufgebraucht ist.
Ansonsten wäre es halt geil als Ziel, wenn alles soweit fertig ist, dass ich nach diesem Turn das nur noch einmal kurz gegenlesen muss und als Release pushen kann.

