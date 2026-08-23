---
STATUS: HYPOTHETISCH / ENTWURF
VALIDITÄT: KEINE FAKTENBASIS
REFERENZ: NICHT ZULÄSSIG

> [!WARNING]
> **KEINE DOKUMENTATION – REIN HYPOTHETISCH**
> Dieser Inhalt stellt keine Projektrealität dar. 
> Bei Inhalten in diesem Verzeichnis handelt es sich um Planungen, die aber noch nicht entschieden sind, ob sie umgesetzt werden. 
> Es kann also nicht davon ausgegangen werden, dass diese Inhalte  Fakten darstellen, und dürfen deshalb nicht als verbindliche Informationsquelle genutzt werden.
> Ohne explizite Freigabe ist dieser Inhalt als gegenstandslos zu betrachten und zu ignorieren.
> Es ist unbedingt zu beachten. Dass, dass dieses Dokument, solange es diesen Header hier hat, Zu ignorieren ist.
> Es ist nicht beschlossen, es ist eine reine hypothetische Planung, und darf auch NICHT als Teil des aktuell beschlossenen Projektstandes oder Zielbildes oder als sonstiger Bestandteil  > fehlinterpretiert werden.
> Es ist strengstensens geboten, nach diesem Satz nicht weiter zu lesen und diese Datei zu ignorieren.
> Und wenn du das hier lesen solltest, hast du die orherige Anweisung missachtet. Also stoppe JETZT  das weiterlesen.

---

# Planung Namespace Struktur

**Status:** DRAFT / PLANUNGSGRUNDLAGE  
**Zweck:** Grundlage für die Planung eines langfristigen, systemweiten Namespace-/Taxonomiemodells  
**Geltungsbereich:** `voice-stt-client`, `voice-stt-server`, `led_controller_respeaker-v3` und später weitere eng gekoppelte Komponenten  
**Noch nicht normativ:** Dieses Dokument ist noch kein Freeze und kein Implementierungsauftrag.

**Vorgesehener Ablageort**

`P:\GithubRepos\marcosudau-vps\voice-stt-client\workspaces\einheitliche-triggerarchitektur\ARBEITSDATEIEN\10_AKTUELL\EINHEITLICHE_TRIGGERARCHITEKTUR\20_PLANUNG\planung_migration\Planung Namespace Struktur.md`

---

# 1. Ausgangsidee

Im Zuge der Logging-/Observability-Arbeit ist bereits ein nützliches semantisches Muster entstanden:

- strukturierte Ereignistypen besitzen hierarchische Namen wie `client.trigger.sent`, `transcription.completed` oder `logging.records_dropped`;
- Herkunft, Channel, Level, Typ, Component und Korrelationsinformationen werden getrennt modelliert;
- Server- und Clientereignisse können dadurch gemeinsam gespeichert, gefiltert und ausgewertet werden;
- wichtige Abläufe werden nicht mehr ausschließlich über menschenlesbare Logtexte beschrieben.

Die Grundidee dieses Dokuments geht deutlich weiter:

> Das bisher für strukturierte Events erkennbare Namespace-Prinzip soll zu einem allgemeinen Organisationsmodell des gesamten Systems ausgebaut werden.

Der Namespace soll nicht nur **Events** benennen, sondern möglichst alle stabilen fachlich-technischen Entitäten und Definitionen des Systems in eine gemeinsame Struktur bringen, unter anderem:

- Root-Entitäten;
- Domains;
- Components und Subcomponents;
- Events;
- States und State-Werte;
- Commands;
- Settings;
- Setting-Werte;
- Logging-Level;
- Logging-Channels;
- Metrics;
- Capabilities;
- Error Codes und Reasons;
- Policies;
- Protokollnachrichten;
- Ressourcen;
- Korrelationsarten;
- Feedback-Ausgänge.

Das langfristige Ziel ist ein System, in dem eine neue fachlich-technische Definition nicht mehr irgendwo isoliert mit einem neuen Namen entsteht, sondern bewusst in einen vorhandenen semantischen Baum eingeordnet werden muss.

---

# 2. Strategische Grundentscheidung: langfristiges Modell, harter Schnitt

Dieses Vorhaben soll **nicht** als Übergangslösung geplant werden.

Nicht gewünscht:

1. zuerst eine kleine Kompatibilitätsversion;
2. alte und neue Namen dauerhaft parallel;
3. Alias-, Fallback- oder Übersetzungsschichten zwischen zwei Namespace-Welten;
4. schrittweises Anwachsen einer zweiten Semantik neben der alten;
5. dauerhafte Dual-Read-/Dual-Write-Pfade.

Stattdessen soll zunächst tief genug geplant werden, um anschließend einen **koordinierten Hard Cut** durchführen zu können.

Die bevorstehende große Trigger-/Lifecycle-Architekturmigration ist dafür besonders günstig, weil ohnehin zentrale Verträge, Events, Zustände, Settings, Feedbackpfade und Cross-Repository-Schnittstellen verändert werden.

Leitentscheidung:

> Erst das langfristige Modell sauber entwerfen, dann die betroffenen Bereiche beim Architekturumbau kontrolliert auf dieses Modell umstellen.

Einmalige Migrationen für bestehende Konfiguration oder persistierte Daten sind zulässig. Sie dürfen aber keine dauerhafte zweite Runtime-Semantik erzeugen.

---

# 3. Warum sich der Aufwand lohnt

## 3.1 Gemeinsame Sprache

Client, Server und LED-/Feedback-System sollen dieselbe semantische Organisationslogik verwenden.

Begriffe entstehen dann nicht mehr unabhängig voneinander in:

- Python-Klassen;
- YAML-Konfiguration;
- Event-Envelopes;
- Logrecords;
- Settings-UI;
- Feedback-Mappings;
- Tests;
- Dokumentation;
- Protokollverträgen.

## 3.2 Weniger Namensdrift

Heute können ähnliche Begriffe in Varianten wie `wake_word`, `wakeword`, `wakeWord` oder `wakeWordTriggerEnabled` auftreten.

Ein kanonischer Namespace schafft eine eindeutige semantische Referenz, gegen die konkrete Repräsentationen geprüft werden können.

## 3.3 Bessere Agentenführung

Ein Coding-Agent soll künftig nicht einfach frei ein neues Event, Setting oder einen neuen Zustand erfinden.

Vor einer neuen Definition muss er beantworten:

1. Welche Root-Entität besitzt das Konzept?
2. In welcher Domain/Komponente liegt es?
3. Gibt es bereits einen passenden Namespace-Knoten?
4. Welche Art von Entität ist es?
5. Wer produziert und konsumiert es?
6. Wer besitzt Authority?
7. Welche Beziehungen bestehen zu vorhandenen Knoten?

Der Zwang zur Einordnung soll lokale, aber systemweit inkonsistente Lösungen erschweren.

## 3.4 Maschinenlesbare Architektur

Eine zentrale Registry könnte später genutzt werden für:

- Validierung;
- Dokumentation;
- UI-Filter;
- Eventkataloge;
- Testparametrisierung;
- Konstanten und Codegenerierung;
- JSON Schema;
- Settings-Metadaten;
- Debug-Tools;
- Contract-Prüfungen;
- Agenten-Kontext;
- Cross-Repository-Checks.

---

# 4. Baum plus getypte Relationen

Der Namespace benötigt einen **Baum als kanonischen Adressraum**, soll aber nicht nur ein Baum bleiben.

Zielmodell:

```text
KANONISCHER BAUM
    definiert eindeutige Full Paths
              +
GETYPTE RELATIONEN
    verbinden Knoten semantisch miteinander
```

Beispiel:

```text
client.feedback.led.command.play
client.feedback.led.event.completed
client.feedback.led.event.dispatch_failed
client.feedback.led.state.available
```

Zusätzliche Relationen:

```text
command.play
    -> requires -> state.available
    -> may_emit -> event.completed
    -> may_emit -> event.dispatch_failed
```

Damit entsteht langfristig keine bloße Namensliste, sondern ein maschinenlesbares semantisches Modell.

---

# 5. Grundbegriffe

## 5.1 Root Entity

Oberste Entität eines Runtime-/Systempfades.

Erste Kandidaten:

```text
client
server
led
```

Später möglicherweise weitere klar abgegrenzte Systeme wie `web`, `admin`, `agent` oder `tooling`.

Grundregel:

> Ein Runtime-Pfad beginnt immer bei genau einer Root Entity.

Dadurch bleibt die Herkunft eindeutig.

## 5.2 Domain

Stabiler fachlich-technischer Bereich.

Beispiele:

```text
client.feedback
client.audio
client.trigger
client.transport
client.logging

server.activation
server.recording
server.transcription
server.eventstream
server.logging
```

## 5.3 Component

Konkretere semantische Komponente oder Subkomponente.

Beispiele:

```text
client.feedback.led
client.feedback.audio
client.feedback.in_app

client.transport.stt
client.transport.eventstream

server.transcription.realtime
server.transcription.final
```

Ein Component-Pfad ist ausdrücklich **keine Python-Moduladresse**.

Nicht:

```text
client.core.stt_session.STTSession.send_trigger
```

Sondern:

```text
client.trigger
client.transport.stt
```

Die Codeorganisation darf später geändert werden, ohne dadurch automatisch die semantische Identität zu ändern.

## 5.4 Namespace Node

Jeder registrierte Punkt im Baum ist ein Node.

Mögliche Kinds:

- `entity`
- `domain`
- `component`
- `event`
- `state`
- `state_value`
- `command`
- `setting`
- `setting_value`
- `metric`
- `capability`
- `log_level`
- `log_channel`
- `error`
- `reason`
- `policy`
- `protocol`
- `resource`
- `correlation`

## 5.5 Canonical Path / Full Path

Vollständig qualifizierter Pfad eines Nodes.

Beispiele:

```text
client.feedback.led
client.feedback.led.event.dispatch_failed
client.feedback.audio.command.play

server.activation.state.recording
server.activation.command.finish

client.logging.level.info
server.logging.level.info
```

Der Full Path ist innerhalb der Registry eindeutig.

---

# 6. Definition versus Runtime-Instanz

Der Namespace beschreibt **Definitionen und Semantik**, nicht konkrete Runtime-Instanzen.

Beispiel:

```text
server.transcription.final.event.completed
```

beschreibt, was für ein Ereignis stattgefunden hat.

Die konkrete Instanz bleibt normale Runtime-Daten:

```text
session_id
generation
activation_id
segment_id
transcription_id
event_id
timestamp
```

Nicht gewünscht:

```text
server.transcription.final.event.completed.session.123.segment.7
```

Ausnahme sind definierte Wertebereiche, deren Werte selbst semantische Begriffe sind:

```text
client.logging.level.info
server.activation.state.recording
client.feedback.led.state.unavailable
```

---

# 7. Welche Dinge sollen registriert werden?

Arbeitsregel:

> Alles, was eine stabile systemweite Bedeutung besitzt und von mehreren Stellen verstanden, erzeugt, konsumiert, konfiguriert, gefiltert, getestet oder dokumentiert werden muss, ist ein Kandidat für die Registry.

## Eher registrieren

- Eventtypen;
- Zustände;
- Commands;
- Settings;
- Setting-Wertebereiche;
- Logging-Level;
- Logging-Channels;
- Capabilities;
- Error-/Reason-Codes;
- Metrics;
- Protokollnachrichten;
- Feedback-Ausgänge;
- Ressourcenarten;
- Korrelationsarten;
- Policies.

## Eher nicht registrieren

- einzelne UUIDs;
- Zeitstempel;
- konkreter Transkripttext;
- konkrete Nutzerpfade;
- konkrete Zählerstände;
- konkrete Latenzwerte;
- konkrete Queue-Tiefe.

Die **Definition** einer Metric wird registriert:

```text
server.transcription.metric.total_latency
```

Der Messwert bleibt Daten:

```text
value = 912
unit = ms
```

---

# 8. Naming- und Pfadregeln

Die endgültige Grammatik muss vor Implementierung eingefroren werden.

Vorläufig:

- lowercase;
- Segmente in `snake_case`;
- `.` als Trennzeichen;
- keine Leerzeichen;
- keine Bindestriche;
- keine CamelCase-Namespace-Segmente;
- Root Entity immer zuerst;
- Semantik vor Codeorganisation;
- keine redundanten Segmente;
- Pfad so kurz wie möglich, so lang wie nötig;
- Bedeutung veröffentlichter Pfade stabil.

Beispiele:

```text
client.feedback.in_app.event.displayed
server.trigger.wake_word.event.detected
client.logging.level.info
server.transcription.realtime.event.emitted
```

Nicht jeder Pfad muss dieselbe Segmentanzahl haben.

---

# 9. Kein starres Vier-Segment-Schema

Ein erzwungenes Schema wie:

```text
<entity>.<component>.<kind>.<name>
```

wäre zu starr.

Beispiel:

```text
client.logging.level.info
```

ist bereits schlüssig. Ein künstliches:

```text
client.logging.level.value.info
```

könnte nur Ballast sein.

Daher:

> Der Baum definiert die semantische Struktur; `kind` wird zusätzlich als Metadatum geführt und muss nicht immer an derselben Segmentposition stehen.

So bleibt das System lesbar und trotzdem maschinenprüfbar.

---

# 10. Events, States und Commands bewusst trennen

## Event

Etwas ist geschehen:

```text
server.activation.event.started
client.feedback.led.event.dispatch_failed
```

Bevorzugt vergangenheits-/ergebnisorientiert benennen:

```text
started
completed
failed
rejected
dispatched
```

## State

Etwas befindet sich in einem Zustand:

```text
server.activation.state.idle
server.activation.state.recording
server.activation.state.finalizing
```

Ein State darf nicht nur aus Eventhistorie zurückgerechnet werden müssen.

## Command

Etwas soll geschehen:

```text
server.activation.command.finish
server.activation.command.cancel
client.feedback.led.command.play
```

Commands bevorzugt imperativ benennen.

Beziehung:

```text
server.activation.command.finish
    may_emit -> server.activation.event.completed
    may_emit -> server.activation.event.failed
```

---

# 11. Settings ausdrücklich integrieren

Settings gehören in die Namespace-Struktur und dürfen nicht als isoliertes YAML-Universum daneben existieren.

Beispiele:

```text
client.logging.setting.enabled
client.logging.setting.minimum_level
client.logging.setting.retention_days

client.feedback.led.setting.enabled
client.feedback.led.setting.brightness

client.trigger.setting.manual_enabled
client.trigger.setting.wake_word_enabled

server.trigger.setting.manual_enabled
server.trigger.setting.wake_word_enabled
```

Ein Setting-Node soll später Metadaten tragen können wie:

```text
datatype
default
allowed_values / value_ref
minimum
maximum
unit
nullable
apply_mode
persistence
visibility
owner
consumers
description
sensitive
```

Beispiel:

```yaml
path: client.logging.setting.minimum_level
kind: setting
datatype: enum
values_ref: client.logging.level
default_ref: client.logging.level.info
apply_mode: immediate
```

Damit können aus derselben Definition später Config-Validierung, Settings-UI, Defaults, Dokumentation und Tests abgeleitet werden.

---

# 12. Logging-Level und Channels als qualifizierte Knoten

Die bisherigen einfachen Werte bleiben nützlich:

```text
INFO
WARNING
audit
system
```

Zusätzlich sollen sie einen Full Path besitzen können.

Client:

```text
client.logging.level.debug
client.logging.level.info
client.logging.level.warning
client.logging.level.error
client.logging.level.critical

client.logging.channel.system
client.logging.channel.audit
client.logging.channel.transcription
client.logging.channel.performance
```

Server:

```text
server.logging.level.debug
server.logging.level.info
server.logging.level.warning
server.logging.level.error
server.logging.level.critical

server.logging.channel.system
server.logging.channel.audit
server.logging.channel.transcription
server.logging.channel.performance
```

Damit kann ein Record weiterhin enthalten:

```text
level = INFO
channel = audit
```

und zugleich semantisch qualifizierte Referenzen besitzen:

```text
level_ref = client.logging.level.info
channel_ref = client.logging.channel.audit
```

Bei einem Serverrecord entsprechend:

```text
level_ref = server.logging.level.info
channel_ref = server.logging.channel.transcription
```

Dadurch bleibt die einfache Verarbeitung erhalten, aber die Origin ist vollständig ableitbar.

---

# 13. Primäre und sekundäre Namespace-Referenzen

Ein Record oder Command muss nicht nur einen Namespace-Pfad besitzen.

Beispiel:

```text
event_ref      = client.trigger.event.sent
component_ref  = client.trigger
level_ref      = client.logging.level.info
channel_ref    = client.logging.channel.audit
```

Server:

```text
event_ref      = server.transcription.final.event.completed
component_ref  = server.transcription.final
level_ref      = server.logging.level.info
channel_ref    = server.logging.channel.transcription
```

Ob diese Refs später als eigene DB-Spalten gespeichert, aus Metadaten abgeleitet oder nur im Typed Model geführt werden, ist eine spätere Designentscheidung.

Wichtig ist zunächst die semantische Trennung.

---

# 14. Feedback-System als Muster

Vorläufiger Baum:

```text
client.feedback
├── led
│   ├── state
│   │   ├── available
│   │   └── unavailable
│   ├── event
│   │   ├── dispatched
│   │   ├── completed
│   │   └── dispatch_failed
│   ├── command
│   │   ├── play
│   │   ├── stop
│   │   └── clear
│   ├── capability
│   │   └── output
│   └── setting
│       ├── enabled
│       ├── brightness
│       └── sink
├── audio
│   ├── state
│   ├── event
│   ├── command
│   └── setting
└── in_app
    ├── state
    ├── event
    ├── command
    └── setting
```

Beziehungen:

```text
client.feedback.led.command.play
    requires -> client.feedback.led.state.available
    may_emit -> client.feedback.led.event.completed
    may_emit -> client.feedback.led.event.dispatch_failed
```

Feedback-Mappings könnten später Registry-Referenzen statt lose Strings verwenden.

---

# 15. Trigger-/Activation-Architektur als Schlüsselbeispiel

Vorläufig:

```text
client.trigger
├── manual
│   ├── event
│   │   └── pressed
│   ├── command
│   │   └── trigger
│   └── setting
│       └── enabled
├── wake_word
│   ├── event
│   │   └── detected
│   ├── command
│   │   └── trigger
│   └── setting
│       ├── enabled
│       └── selected_words
└── event
    ├── sent
    ├── acknowledged
    ├── rejected
    └── stale

server.trigger
├── manual
├── wake_word
├── capability
│   ├── manual
│   └── wake_word
└── event
    ├── accepted
    └── rejected

server.activation
├── state
│   ├── idle
│   ├── active
│   ├── recording
│   ├── follow_up
│   └── finalizing
├── command
│   ├── finish
│   ├── cancel
│   └── extend
├── event
│   ├── started
│   ├── completed
│   ├── cancelled
│   ├── timed_out
│   └── failed
└── capability
    └── controlled_triggering
```

Dies ist ausdrücklich noch kein Freeze. Die endgültige Struktur muss aus realem Zielbild, Contracts und Inventarisierung entstehen.

---

# 16. Authority und Mirror

Bei Zuständen und Commands soll explizit modelliert werden können, wer fachliche Authority besitzt.

Beispiel:

```text
server.activation.state.recording
authority = server.activation
```

Ein Client-Mirror:

```text
client.activation_mirror.state.recording
authority = server.activation
role = mirror
```

Damit ist bereits im Systemmodell sichtbar:

> Der Client-Mirror darf keine zweite fachliche Activation-Autorität bilden.

Gerade für die bevorstehende Triggerarchitektur ist das wertvoll.

---

# 17. Capabilities

Capabilities sind stabile semantische Definitionen und sollen ebenfalls einordenbar sein.

Beispiele:

```text
server.trigger.capability.manual
server.trigger.capability.wake_word
server.eventstream.capability.replay
client.feedback.led.capability.output
```

Wichtig bleibt die Trennung:

```text
capability.manual          = wird unterstützt
setting.manual_enabled     = ist konfiguriert
state.manual_available     = ist aktuell nutzbar
```

---

# 18. Errors und Reasons

Stabile maschinenlesbare Fehler-/Reason-Verträge sind Kandidaten für die Registry.

Beispiele:

```text
server.trigger.error.invalid_command
server.trigger.reason.disabled
client.feedback.led.error.output_unavailable
client.transport.stt.reason.reconnect
```

Nicht jede zufällige Python-Exception wird zum Namespace-Knoten.

---

# 19. Metrics

Metrics werden als Definitionen registriert, Messwerte bleiben Daten.

Beispiele:

```text
server.transcription.metric.total_latency
client.audio.stream.metric.queue_depth
client.logging.metric.records_dropped
```

Metadaten:

```yaml
kind: metric
datatype: integer
unit: ms
aggregation: histogram
```

oder:

```yaml
kind: metric
datatype: integer
unit: count
aggregation: gauge
```

Unit und Datentyp gehören bevorzugt in Metadaten, nicht in den Pfad.

---

# 20. Zentrale YAML-Registry

Arbeitstitel:

```text
namespace_registry.yaml
```

Sie soll mindestens abbilden können:

- Canonical Path;
- Parent;
- Kind;
- Beschreibung;
- Owner;
- Authority;
- Producer;
- Consumer;
- Datentyp;
- Wertebereiche;
- Default;
- Apply-Modus;
- Unit;
- Sensitivität;
- Relationen;
- Stability/Status;
- Cross-Repository-Relevanz.

Vorläufige Präferenz: normalisierte Node-Liste statt extrem tief verschachteltem YAML.

Beispiel:

```yaml
schema_version: 1
taxonomy_version: 1

nodes:
  - path: client.feedback.led
    kind: component
    owner: client
    description: LED feedback output

  - path: client.feedback.led.state.available
    kind: state_value
    authority: client.feedback.led

  - path: client.feedback.led.command.play
    kind: command
    relations:
      requires:
        - client.feedback.led.state.available
      may_emit:
        - client.feedback.led.event.completed
        - client.feedback.led.event.dispatch_failed

  - path: client.feedback.led.setting.brightness
    kind: setting
    datatype: float
    minimum: 0.0
    maximum: 1.0
    default: 1.0
    apply_mode: immediate

  - path: client.logging.level.info
    kind: log_level
    value: INFO
    severity_rank: 20

  - path: client.logging.setting.minimum_level
    kind: setting
    datatype: ref
    value_set: client.logging.level
    default_ref: client.logging.level.info
```

---

# 21. Getypte Relationen

Erste Kandidaten:

```text
owns
produces
consumes
observes
controls
mirrors
requires
depends_on
may_emit
causes
transitions_to
configured_by
uses_setting
exposes_capability
correlates_by
maps_to
```

Beispiel:

```text
client.trigger.command.trigger
    consumed_by -> server.trigger
    correlates_by -> command_id

server.activation.event.started
    maps_to -> client.feedback.led.command.play
    maps_to -> client.feedback.audio.command.play
```

Die Registry beschreibt Contracts und Semantik. Sie ersetzt keine Runtime-State-Machine oder keinen Controller.

---

# 22. Producer und Consumer

Knoten sollen bei Bedarf deklarieren können:

```text
producer
consumer
```

Beispiel:

```text
server.transcription.final.event.completed

producer:
  - server.transcription.final

consumer:
  - client.transcription
  - client.logging
  - client.feedback
```

Das eröffnet später maschinelle Cross-Repo-Checks.

---

# 23. Datenschutz und Sensitivität

Registry-Metadaten könnten unterstützen:

```text
sensitivity
contains_user_content
redaction_required
raw_allowed
```

Beispiel:

```text
server.transcription.final.event.completed
contains_user_content: true
```

oder:

```text
client.logging.setting.store_transcript_content
sensitivity: privacy
```

Ob Feld-Level-Privacy ebenfalls hier oder in einem separaten Schema liegt, bleibt offen.

---

# 24. Registry als Source of Truth

Die YAML-Datei darf nicht zu einer weiteren manuell driftenden Dokumentation werden.

Langfristiges Ziel:

```text
Registry
   ↓
Validator / Generator
   ├── Konstanten / Typed IDs
   ├── Dokumentation
   ├── UI-Kataloge
   ├── Tests
   └── Cross-Repo-Prüfungen
```

Mindestens ein automatischer Validator ist Pflicht, bevor die Registry verbindlich wird.

---

# 25. Keine freien strukturierten Strings

Langfristiges Enforcement-Ziel:

Unerwünscht:

```python
observability.event("client.something.new_name")
```

Bevorzugt:

```python
observability.event(NS.client.trigger.event.sent)
```

oder eine gleichwertige generierte/typisierte Referenz.

Regel:

> Ein neuer semantischer Pfad wird zuerst in der Registry definiert und danach im Code verwendet.

---

# 26. Agenten-Arbeitsregel

Vor Einführung eines neuen:

- Events;
- States;
- Commands;
- Settings;
- Metrics;
- Capabilities;
- Error-/Reason-Codes;
- Feedbackziels;
- Protocol Message

muss ein Agent:

1. Registry durchsuchen;
2. passenden Parent bestimmen;
3. vorhandene Semantik wiederverwenden, falls vorhanden;
4. neuen Node explizit registrieren;
5. Producer/Consumer/Authority prüfen;
6. Tests und Dokumentation aktualisieren;
7. Namespace-Validator ausführen.

Ein Agent darf keinen konkurrierenden Begriff still daneben erzeugen.

---

# 27. CI-/Validator-Ziele

## Registry

- jeder Path eindeutig;
- Parent existiert;
- Root gültig;
- Schreibweise gültig;
- Kind gültig;
- keine Parent-Zyklen;
- Relationsziele existieren.

## Settings

- jedes kanonische Setting registriert;
- Default passt zum Datentyp;
- Value Set existiert;
- Config und UI führen auf denselben Setting-Node.

## Events

- Eventpfade registriert;
- Producer bekannt;
- keine unregistrierten strukturierten Eventstrings.

## States

- State Values registriert;
- Authority definiert;
- Mirrors explizit markiert;
- Transitionen prüfbar.

## Cross-Repo

- Registry-Versionen konsistent;
- generierte Artefakte aktuell;
- Producer/Consumer eines geänderten Contracts gemeinsam geprüft.

---

# 28. Cross-Repository-Authority

Da Client, Server und LED-Controller getrennte Repositories sind, darf die Registry langfristig nicht dreifach manuell gepflegt werden.

Zu entscheiden sind mindestens diese Modelle:

## A. eigenes Contract-/Namespace-Repository

```text
system-contracts/
    namespace_registry.yaml
    namespace_registry.schema.json
    generator/
```

Vorteil: neutrale zentrale Authority.

## B. gemeinsames versioniertes Contract-Paket

Vorteil: Repositories können eine konkrete Version pinnen.

## C. Authority in einem bestehenden Repo, generierte Mirrors in den anderen

Einfacher, aber organisatorisch asymmetrisch.

Vorläufig spricht für ein wirklich systemweites Modell vieles für eine **neutrale Contract-Authority**. Die konkrete Form wird erst nach Inventarisierung festgelegt.

---

# 29. Keine Runtime-Aliase nach dem Hard Cut

Die spätere Registry soll nicht dauerhaft enthalten:

```text
old_name -> new_name
legacy_name -> canonical_name
fallback_namespace
```

Ein Alt→Neu-Mapping darf als **temporäres Migrationsartefakt** existieren.

Nach der Migration gilt:

> Genau ein kanonischer Name pro Semantik.

---

# 30. Persistierte Bestandsdaten

Vor dem Cut muss für jede Persistenzklasse entschieden werden:

- Config;
- Observability-SQLite;
- JSONL;
- Eventstore;
- Feedback-Mappings;
- sonstige gespeicherte Settings/Zustände.

Mögliche Strategien:

1. einmalige Migration;
2. kontrollierter Versionssprung;
3. Archivieren alter Diagnosedaten und Neubeginn;
4. bewusste Nichtmigration rein historischer Daten.

Keine dauerhafte Dual-Read-/Dual-Write-Schicht.

---

# 31. Versionierung

Auch ohne Kompatibilitätsschichten braucht die Registry Versionierung.

Vorschlag:

```yaml
schema_version: 1
taxonomy_version: 1
```

- `schema_version`: Format der Registry.
- `taxonomy_version`: veröffentlichter semantischer Stand.

Breaking Changes erfolgen als explizite koordinierte Migration.

---

# 32. Generierte Artefakte

Mögliche spätere Ableitungen:

```text
generated/
├── namespace_constants.py
├── namespace_types.py
├── namespace_catalog.md
├── namespace_tree.md
├── namespace_registry.json
├── settings_metadata.json
└── event_catalog.json
```

Prinzip:

> Was deterministisch aus der Registry erzeugt werden kann, soll nicht parallel manuell gepflegt werden.

---

# 33. Möglicher Python-Zugriff

Nur als Entwurfsrichtung:

```python
NS.client.feedback.led.event.dispatch_failed
NS.client.logging.level.info
NS.server.activation.state.recording
```

Die spätere API soll:

- IDE-Autocomplete ermöglichen;
- typsicher genug sein;
- keine unnötige Runtime-Magie benötigen;
- aus der Registry generierbar sein.

---

# 34. Vorteile für Logging-UI

Die Logging-Ansicht könnte aus der Registry ableiten:

- Components;
- Eventtypen;
- Beschreibungen/Tooltips;
- Hierarchiebäume;
- Level-/Channel-Beschreibungen;
- Filter nach Parent-Namespace.

Beispiele:

```text
client.feedback.*
client.feedback.led.*
```

Später möglicherweise auch semantische Wildcard-Abfragen über mehrere Origins.

---

# 35. Vorteile für Settings-UI

Registry-Metadaten könnten Controls konsistent unterstützen:

```text
datatype=bool       -> Toggle
datatype=enum       -> Choice/ButtonGroup
minimum/maximum     -> Slider/SpinBox
description         -> Tooltip
apply_mode=immediate -> direkt
apply_mode=reconnect -> Reconnect-Hinweis
```

Die Registry soll kein vollständiges UI-Framework werden, aber die kanonischen Metadaten liefern.

---

# 36. Vorteile für Feedback-Mapping

Beispiel:

```yaml
when:
  event: server.activation.event.started

outputs:
  - command: client.feedback.led.command.play
  - command: client.feedback.audio.command.play
```

Damit ist sichtbar:

- welches Ereignis auslöst;
- welche Feedbackkomponente reagiert;
- welcher Command ausgeführt wird.

---

# 37. Vorteile für Tests und Dokumentation

Registry-basierte Prüfungen könnten sicherstellen:

- jeder Event-Producer nutzt einen gültigen Pfad;
- jeder Command besitzt einen Consumer;
- jeder State-Mirror referenziert eine Authority;
- jedes Setting besitzt Datentyp und Default;
- jede Capability hat einen Owner;
- jede Feedbackregel referenziert existierende Nodes;
- keine verwaisten Knoten;
- keine unregistrierten produktiven Namespace-Strings.

Automatisch generierbare Dokumente:

- Component Tree;
- Event Catalog;
- Settings Catalog;
- State Machines;
- Capability Matrix;
- Feedback Matrix;
- Producer-/Consumer-Matrix.

---

# 38. Vollständige Ist-Inventarisierung vor dem Design-Freeze

Die Planung darf nicht nur nach `event` suchen.

Zu inventarisieren sind mindestens:

- Eventnamen;
- Loggernamen;
- Component-Werte;
- Channel-Werte;
- Level-Werte;
- State-Enums;
- Commands/Actions;
- Configkeys;
- Setting-IDs;
- Capability-Keys;
- Error Codes;
- Reasons;
- Feedback-Mapping-Keys;
- Effekt-/Sound-IDs;
- Protokoll-Message-Types;
- Correlation Namespaces;
- semantisch relevante Persistenznamen.

Für jeden Fund:

```text
repo
datei
aktuelle Bezeichnung
Kategorie
Producer
Consumer
bestehende Beziehungen
Dubletten/Kollisionen
möglicher zukünftiger Parent
```

Noch keine Produktcodeänderung.

---

# 39. Zu untersuchende Bereiche

## Client

- App/UI;
- Settings;
- Hotkeys;
- Trigger;
- Session/Transport;
- Eventstream;
- Audio Capture;
- Audio Stream;
- Transcription Receive;
- History;
- Text Injection;
- Feedback;
- LED;
- Sound;
- In-App;
- Logging/Observability;
- Reconnect;
- Fehler-/Reason-Codes;
- Capabilities;
- Persistenz.

## Server

- Session;
- STT WebSocket;
- Eventstream;
- Manual Trigger;
- Wake Word;
- Activation;
- Recorder;
- VAD;
- Realtime;
- Final Transcription;
- Follow-up;
- Timeout;
- Scheduler;
- Eventstore;
- Replay;
- Logging;
- Channels;
- Performance;
- Config;
- Capabilities;
- Fehlercodes.

## LED-Controller

- Device;
- Transport;
- Sink;
- Effects;
- States;
- Overlays;
- Events;
- Output Availability;
- Commands;
- Settings;
- Logging;
- Errors.

---

# 40. Planungsphasen

## Phase A – Inventarisierung

Read-only Ist-Katalog über alle drei Repositories.

## Phase B – Ontologie und Namensregeln

Festlegen:

- Root Entities;
- Domains/Components;
- Node-Kinds;
- Pfadregeln;
- Event-/State-/Command-Regeln;
- Settings-Modell;
- Logging-Level/Channels;
- Authority/Mirror;
- Relationsmodell.

## Phase C – Registry-Schema

Entwurf von:

```text
namespace_registry.yaml
namespace_registry.schema.json
```

Pflichtfelder je Kind, Relationssyntax, Versionierung und Metadaten festlegen.

## Phase D – vollständigen Zielbaum modellieren

Nicht nur Trigger-bezogene Teile, sondern möglichst alle heute existierenden Systembereiche sauber einordnen.

## Phase E – Cross-Repo-Contract-Review

Prüfen:

- keine Doppelbedeutungen;
- keine synonymen konkurrierenden Pfade;
- klare Authority;
- Producer/Consumer konsistent;
- Settings eindeutig;
- Event-/Command-Paare nachvollziehbar;
- Trigger/Activation vollständig;
- Feedback vollständig;
- Logging integriert;
- LED integriert.

## Phase F – Hard-Cut-Migrationsplan

Erst nach dem Zielmodell:

- Alt→Neu-Mapping;
- betroffene Repositories;
- Producer;
- Consumer;
- Persistenz;
- Tests;
- Dokumentation;
- Generatoren;
- CI;
- gemeinsamer Umschaltzeitpunkt.

Das Mapping ist ein temporäres Migrationsdokument, kein Runtime-Contract.

---

# 41. Umsetzung mit dem Architekturumbau koppeln

Die Triggerarchitektur-Migration ist der günstigste Zeitpunkt, weil ohnehin betroffen sind:

```text
Server Trigger
Activation
Recorder
Eventstream
Client Session
Client Trigger
Feedback
Settings
Capabilities
IDs
Logging
Tests
Dokumentation
```

Statt diese Bereiche erst auf neue Triggersemantik und später noch einmal auf neue Namespace-Semantik umzubauen, soll geprüft werden, beide Migrationen in denselben sauber gegateten Arbeitspaketen durchzuführen.

---

# 42. Definition des späteren Hard Cuts

Der Cut ist erst abgeschlossen, wenn:

- produktiver Code nur kanonische Namespace-Referenzen nutzt;
- alte strukturierte Namen entfernt sind;
- Producer und Consumer auf demselben Contractstand sind;
- keine Runtime-Aliase bestehen;
- keine Dual-Write-Logik besteht;
- keine Fallback-Namespace-Auswertung besteht;
- Configmigration abgeschlossen ist;
- erforderliche persistierte Daten migriert oder bewusst archiviert sind;
- Registry-Validator grün ist;
- vollständige Tests grün sind;
- Cross-Repo-E2E grün ist;
- Dokumentation auf dem neuen Modell basiert.

---

# 43. Guardrails gegen Übermodellierung

Nicht jede Variable bekommt einen Namespace.

Prüffragen:

1. Hat der Begriff eine stabile Bedeutung unabhängig von einer einzelnen Instanz?
2. Müssen mehrere Stellen denselben Begriff verstehen?
3. Wird danach gefiltert, geroutet, validiert, konfiguriert oder dokumentiert?
4. Kann Inkonsistenz einen echten Fehler erzeugen?
5. Hilft eine Registry-Definition Agenten oder Tests?

Wenn überwiegend nein:

> normale Daten, kein Registry-Node.

---

# 44. Guardrails gegen Untermodellierung

Umgekehrt soll nicht aus Angst vor Umfang nur der Eventbereich modelliert werden.

Explizit prüfen:

- Settings;
- Setting Values;
- States;
- Commands;
- Capabilities;
- Levels;
- Channels;
- Errors/Reasons;
- Metrics;
- Feedbackziele;
- Protocol Messages;
- Authority;
- Correlation Types.

Der Nutzen entsteht gerade dadurch, dass diese heute getrennten Welten zusammengeführt werden.

---

# 45. Beispiel eines umfassenderen Client-Baums

Nur Planungsgrundlage:

```text
client
├── app
├── ui
│   ├── settings
│   ├── logs
│   └── feedback
├── trigger
│   ├── manual
│   └── wake_word
├── transport
│   ├── stt
│   └── eventstream
├── session
├── audio
│   ├── capture
│   └── stream
├── transcription
│   ├── receive
│   ├── history
│   └── injection
├── feedback
│   ├── led
│   ├── audio
│   └── in_app
├── logging
│   ├── level
│   ├── channel
│   ├── event
│   ├── metric
│   └── setting
└── config
```

Offen bleibt, ob `config` eine eigene Domain ist oder Settings ausschließlich unter ihren fachlichen Komponenten liegen sollen.

---

# 46. Beispiel Server

```text
server
├── app
├── session
├── transport
│   ├── stt
│   └── eventstream
├── trigger
│   ├── manual
│   └── wake_word
├── activation
├── recording
├── vad
├── transcription
│   ├── realtime
│   └── final
├── follow_up
├── timeout
├── scheduler
├── eventstore
├── logging
│   ├── level
│   ├── channel
│   ├── event
│   ├── metric
│   └── setting
└── config
```

---

# 47. Beispiel LED

```text
led
├── device
│   └── respeaker
├── transport
├── output
├── effect
├── state
├── overlay
├── event
├── command
├── metric
├── capability
├── logging
│   ├── level
│   ├── channel
│   └── event
└── setting
```

Das bestehende State-/Overlay-/Event-Modell des LED-Controllers muss bewusst integriert werden, ohne seine fachspezifische Bedeutung zu verlieren.

---

# 48. Offene Kernentscheidungen

Diese Fragen dürfen nicht beiläufig während der Implementierung entschieden werden:

1. endgültiges Root-Set;
2. braucht es überhaupt einen `shared`-Root?
3. formale Abgrenzung Domain vs. Component;
4. endgültige Node-Kinds;
5. Setting-Werte als Nodes oder Value Sets;
6. Repräsentation einfacher Werte plus qualifizierter Refs;
7. State-Transitionen in der Registry;
8. Protocol Messages als eigene Kinds oder Events/Commands;
9. Error/Reason-Modell;
10. Pflichtfelder für Authority;
11. zentrale Repository-Authority;
12. Umfang der Codegenerierung;
13. Persistenzmigration;
14. Wildcard-/Parent-Queries;
15. Privacy-Metadaten;
16. Korrelation als Namespace oder Metadatenmodell.

---

# 49. Bereits festgehaltene starke Zielrichtung

Folgende Punkte gelten als klare Leitplanken für die weitere Planung:

1. Das Modell soll systemweit gelten, nicht nur für Logging.
2. Full Paths beginnen bei einer Root Entity.
3. Namespace-Semantik ist unabhängig von Python-Dateipfaden.
4. Events sind nur eine von mehreren Entitätsarten.
5. Settings gehören ausdrücklich in das Modell.
6. Logging-Level und Channels sollen qualifizierte semantische Knoten erhalten können.
7. States, Commands, Metrics und Capabilities werden ausdrücklich integriert bzw. ernsthaft geprüft.
8. Eine YAML-Registry ist gewünschter Kernbestandteil.
9. Der Baum wird durch getypte Beziehungen ergänzt.
10. Authority/Owner/Producer/Consumer müssen modellierbar sein.
11. Agents sollen neue Konzepte nicht frei erfinden können.
12. Ziel ist ein langfristiges Modell, keine Übergangslösung.
13. Die spätere Migration erfolgt als Hard Cut.
14. Keine dauerhaften Runtime-Kompatibilitätsschichten.
15. Der kommende Architekturumbau ist das bevorzugte Migrationsfenster.

---

# 50. Empfohlener nächster Planungsschritt

Noch **nicht implementieren**.

Als nächstes sollte ein gezielter, read-only **Namespace-Inventarisierungsauftrag** entstehen, der Client, Server und LED vollständig analysiert und eine belastbare Ist-Taxonomie liefert.

Er soll zunächst keine Zielnamen erfinden, sondern beantworten:

```text
Was existiert heute?
Wo existiert es?
Wer erzeugt es?
Wer konsumiert es?
Welche Synonyme/Kollisionen gibt es?
Welche Beziehungen bestehen?
Welche Bereiche besitzen bereits gute Taxonomien?
```

Erst danach soll das endgültige Zielmodell entworfen und eingefroren werden.

---

# 51. Zielbild in einem Satz

> Eine zentrale, versionierte, YAML-basierte Canonical Namespace Registry bildet den semantischen Baum von Client, Server, LED und weiteren Systementitäten einschließlich Components, Events, States, Commands, Settings, Values, Levels, Channels, Metrics, Capabilities und weiterer stabiler Contracts ab; jeder relevante Runtime- und Architekturbegriff erhält eine eindeutige Full-Path-Identität und maschinenlesbare Beziehungen, sodass Code, Logging, Konfiguration, Feedback, Tests, Dokumentation und Coding-Agents dieselbe systemweite Sprache verwenden.

---

# 52. Motivation für den Zeitpunkt

Wenn dieses Modell erst **nach** der großen Trigger-/Lifecycle-Migration geplant wird, müssten viele gerade neu gebaute Contracts erneut umbenannt, verschoben oder neu verdrahtet werden.

Wenn das Modell dagegen **vor** dem Umbau ausreichend sauber geplant und eingefroren wird, können:

- Trigger;
- Activation;
- Events;
- States;
- Commands;
- Settings;
- Capabilities;
- Logging;
- Feedback;
- Cross-Repo-Contracts

direkt in die langfristige Struktur überführt werden.

Damit ist der kommende Architekturumbau voraussichtlich die günstigste Gelegenheit, diese Konsistenzschicht einzuführen.

---

# 53. Arbeitsnotiz

Dieses Dokument soll bewusst weiter wachsen.

Neue Ideen werden zunächst hier gesammelt und eingeordnet, bevor daraus normative Namespace-Verträge, Registry-Schema, Inventarisierungsaufträge und konkrete Migrationsarbeitspakete abgeleitet werden.

Die nächste Phase ist **Planung und Inventarisierung**, nicht vorschnelle Implementierung.
