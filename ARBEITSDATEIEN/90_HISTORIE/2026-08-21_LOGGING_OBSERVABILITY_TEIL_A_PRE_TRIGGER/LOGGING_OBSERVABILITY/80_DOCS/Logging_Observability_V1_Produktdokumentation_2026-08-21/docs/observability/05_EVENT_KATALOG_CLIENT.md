# Event-Katalog – strukturierte Client-Events

## Kurz und einfach erklärt

Ein normales Log sagt oft nur: „Etwas ist passiert.“

Ein strukturiertes Event sagt genauer: „**Dieser definierte Vorgang** ist passiert – und hier sind die IDs, mit denen er zu anderen Vorgängen gehört.“

Diese Datei ist das Wörterbuch für die strukturierten Ereignisse, die der Client im V1-Stand gezielt erzeugt oder als definierte Observation führt.

> **Hinweis:** Der Katalog beschreibt den pre-trigger V1-Baseline-Stand. Nach der Triggerarchitektur-Migration wird er in OBS-100 gegen den neuen serverautoritativen Lifecycle neu abgeglichen und erweitert.

---

## 1. Leseschlüssel

- **S** – strukturiertes Observability-Event.
- **P** – klassisches Python-Logging trägt die Information.
- **P+S** – bewusst beide Formen vorhanden.

Nicht jeder technische Logsatz bekommt einen eigenen `type`. Ein stabiler Eventtyp ist dort sinnvoll, wo Korrelation, Filterung, Tests oder spätere Analyse davon profitieren.

---

## 2. System / Lifecycle

| Typ | Typischer Ort | Art | Bedeutung |
|---|---|---:|---|
| `client.app.started` | `app.py` | S | Anwendung gestartet |
| `client.app.stopping` | `app.py` | S | kontrollierter Shutdown beginnt |
| `client.core.thread_started` | UI/Core-Bridge | S | Core-Thread gestartet |
| `client.core.thread_stopped` | UI/Core-Bridge | S | Core-Thread beendet |
| `client.controller.run_started` | `core/controller.py` | S | Controller-Runloop gestartet |
| `client.controller.shutdown_*` | `core/controller.py` | P/S | Shutdown-Schritte |
| `client.websocket.connecting` | `core/stt_session.py` | P+S | STT-Transport verbindet |
| `client.websocket.connected` | `core/stt_session.py` | P+S | WebSocket verbunden |
| `client.websocket.disconnected` | `core/stt_session.py` | P+S | Verbindung getrennt |
| `client.session.admitted` | `core/stt_session.py` | P+S | Session vom Server angenommen |
| `client.session.ready` | `core/stt_session.py` | S | Session/Server bereit |
| `client.reconnect.scheduled` | `core/stt_session.py` | P+S | Reconnect geplant |
| `client.eventstream.state_changed` | `core/session_coordinator.py` | S | Eventstream-Zustand geändert |
| `client.eventstream.gap` | Eventstream-Fan-out | S | Lücke erkannt |
| `client.eventstream.error` | Eventstream-Fan-out | S | Eventstreamfehler |
| `client.eventstream.replay_completed` | Eventstream-Fan-out | S | Replayphase beendet |
| `client.eventstream.protocol_error` | `core/event_stream.py` | S | Protokollfehler |
| `client.config.validation_failed` | Config / Settings | P+S | Konfiguration ungültig |
| `client.config.loaded` | `core/config.py` | P | Config geladen |

### Warum diese Gruppe wichtig ist

Mit dieser Gruppe kann man einen Transport-/Sessionverlauf rekonstruieren, ohne Meldungstexte zu parsen:

```text
connecting
→ connected
→ admitted
→ ready
→ disconnected
→ reconnect.scheduled
```

Die tatsächliche fachliche Sessionsteuerung bleibt trotzdem außerhalb der Observability.

---

## 3. Audit / Benutzer- und Steueraktionen

| Typ | Typischer Ort | Art | Relevante IDs |
|---|---|---:|---|
| `client.hotkey.pressed` | `ui/hotkeys.py` | S | ggf. `correlation_id` |
| `client.command.requested` | `ui/core_bridge.py` | S | `correlation_id` |
| `client.command.completed` | `ui/core_bridge.py` | S | gleiche `correlation_id` |
| `client.trigger.sent` | `core/stt_session.py` | P+S | Session, Generation, Command |
| `client.trigger.ack_received` | `core/stt_session.py` | S | Command, Session |
| `client.trigger.ack_dropped` | `core/stt_session.py` | P+S | Command, Session |
| `client.stream.start_sent` | `core/stt_session.py` | P+S | Session, Generation |
| `client.dictation.start_attempt` | `core/controller.py` | S | Session/Korrelation |
| `client.dictation.confirmed` | `core/controller.py` | S | Session |
| `client.dictation.failed` | `core/controller.py` | S | Session/Fehlerkontext |
| `client.dictation.interrupted` | `core/controller.py` | P+S | Session |
| `client.settings.apply_started` | `ui/application.py` | S | `correlation_id` |
| `client.settings.apply_completed` | `ui/application.py` | S | gleiche `correlation_id` |
| `client.settings.runtime_apply` | `core/controller.py` | S | gleiche `correlation_id` |
| `client.action.blocked` | `core/controller.py` | S | abhängig von Aktion |
| `client.audio.stream_started` | `core/audio_capture.py` | P+S | Session/Audio-Kontext |
| `client.audio.stream_stopped` | `core/audio_capture.py` | P+S | Session/Audio-Kontext |

### Typische Kette

```text
client.hotkey.pressed
→ client.command.requested
→ client.trigger.sent
→ client.trigger.ack_received
→ client.command.completed
```

Diese Kette ist besonders wertvoll, weil sie später mit `command_id` und `correlation_id` statt nur über Zeitstempel abgeglichen werden kann.

---

## 4. Transcription / Textverarbeitung

| Typ | Typischer Ort | Art | Bedeutung |
|---|---|---:|---|
| `client.injection.enqueued` | `core/controller.py` | P+S | Textinjektion in Queue aufgenommen |
| `client.injection.rejected` | `core/controller.py` | P+S | Textinjektion abgelehnt |
| `client.final.deduplicated` | `core/controller.py` | P+S | doppeltes Final unterdrückt |
| `client.history.persist_failed` | `core/history.py` | P | Historienpersistenz fehlgeschlagen |

Diese Events betreffen **lokale Tatsachen**. Ein Serverevent kann z. B. ein Final melden; ob der Client den Text anschließend tatsächlich in die lokale Injection-Queue gestellt hat, weiß nur der Client.

---

## 5. Performance / interne Observability

| Typ | Erzeugung | Art | Bedeutung |
|---|---|---:|---|
| `client.audio.stream_stats` | Aggregation | S | Audio-/Queue-Metriken |
| `client.queue.state` | Aggregation | S | Queuezustand |
| `logging.records_dropped` | Observability Worker | S | Records kontrolliert verworfen |
| `logging.recovered` | Observability Worker | S | Loggingpfad hat sich erholt |
| `logging.retention_pressure` | Observability Worker | S | Größen-/Retention-Hinweis |
| `logging.record_rejected` | Observability intern | S | Record konnte nicht angenommen werden |

Hochfrequente Messwerte sollen aggregiert werden. V1 vermeidet ausdrücklich eine Record-pro-Frame-/Packet-Flut.

---

## 6. Feedback und Ausgabe

| Typ | Typischer Ort | Art | Bedeutung |
|---|---|---:|---|
| `client.feedback.decision` | `ui/application.py` | P+S | Feedbackentscheidung beobachtet |
| `client.led.dispatch_failed` | `ui/led_feedback.py` | P+S | LED-Ausgabe fehlgeschlagen |
| `client.led.queue_overflow` | `ui/led_feedback.py` | P+S | LED-Queue überlastet |
| `client.sound.failed` | `ui/application.py` | P+S | Soundausgabe fehlgeschlagen |
| `client.server.error_classified` | `core/controller.py` | P+S | Serverfehler klassifiziert |

Wichtig: Diese Events **beobachten** Entscheidungen oder Ausgabefehler. Sie führen nicht selbst Sound oder LED aus.

---

## 7. Bewusst nicht als strukturierter Einzelstrom instrumentiert

### Realtime-Textupdates

Der Realtime-Strom wird nicht ungefiltert als eigener strukturierter Record pro Update gespiegelt.

### Audio-Hot-Path

Keine Records pro:

- Audiopaket;
- Frame;
- Callback;
- VAD-nahem Einzelereignis.

Stattdessen Aggregate und Zustandswechsel.

### Headless-`print()`

Programmausgabe eines Diagnose-/Headless-Modus ist nicht automatisch ein Canonical Event.

---

## 8. Namenskonvention

Clientevents:

```text
client.<bereich>.<ereignis>
```

Beispiele:

```text
client.websocket.connected
client.trigger.sent
client.settings.apply_completed
```

Logging-interne Ereignisse:

```text
logging.<ereignis>
```

Serverevents behalten ihren serverseitigen Namen und werden nicht in ein künstliches `client.server.*`-Schema umbenannt.

---

## 9. Wie der Katalog gepflegt wird

Ein neuer stabiler Eventtyp braucht mindestens:

1. eindeutige Bedeutung;
2. Channel;
3. typisches Level;
4. Producer/Component;
5. definierte IDs;
6. Tests, wenn er Teil eines wichtigen Vertrags ist;
7. Aktualisierung dieses Katalogs.

Die Triggerarchitektur-Migration ist der nächste große Anlass für eine systematische Revision.
