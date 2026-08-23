# Quellen, Producer, Channels und Levels

## Kurz und einfach erklärt

Vier getrennte Fragen helfen beim Einordnen eines Logs:

1. **Wer meldet es?**
2. **Zu welchem Themenbereich gehört es?**
3. **Wie schwerwiegend ist es?**
4. **Was genau ist passiert?**

Darum bleiben Quelle, Channel, Level, Typ und Component getrennt.

```text
Producer/Quelle → Wer?
Channel         → Welcher Diagnosebereich?
Level           → Wie schwerwiegend?
Type            → Was ist fachlich passiert?
Component       → Welche technische Komponente meldet es?
```

## Quellen in V1

### Python-Logging

```python
logger.info(...)
logger.warning(...)
logger.exception(...)
```

Normalerweise:

```text
type = null
component = Loggername
```

### Strukturierte Client-Observations

Beispiele:

```text
client.trigger.sent
client.settings.apply_completed
client.audio.stream_started
```

### Server-/Eventstream-Daten

Serveridentität, Channel, Eventtyp, Replay, `event_id`, Cursor und optional Raw bleiben erhalten.

### LEFX/ReSpeaker-nahe Python-Logs

Logger unter `lefx.*` können als eigene LED-/ReSpeaker-nahe Producerherkunft klassifiziert werden, obwohl sie im Clientprozess laufen.

## Producer-Beispiele

| ProducerKind | ProducerId | Bedeutung |
|---|---|---|
| `client` | `voice-stt-client` | Desktopclient |
| `server` | `voice-stt-server` | Serverevent |
| `led` | LED/ReSpeaker-nahe Producer-ID | Ausgabegerät/LEFX |

## Channels

### `system`

Verbindung, Reconnect, Eventstream, App-/Controller-Lifecycle, Configfehler, technische Ausgabefehler.

### `audit`

Absichtliche Aktionen: Hotkey, Command, Trigger, Ack, Settings Apply.

### `transcription`

Transkriptions-/Textfluss.

### `performance`

Zahlen und Aggregate, nicht Record-pro-Audiopaket.

## Levels

```text
DEBUG
INFO
WARNING
ERROR
CRITICAL
```

Level beantwortet nur „wie schwerwiegend?“, nicht „welcher Themenbereich?“.

## Type

Stabiler strukturierter Ereignisname, z. B.:

```text
client.trigger.sent
client.websocket.disconnected
logging.records_dropped
transcription.completed
```

Normale Python-Logs dürfen `type = null` haben.

## Component

Technischer Ursprung:

```text
eventstream
stt_session
controller
ui.application
core.config
lefx.interfaces.service
```

Der Loggername `event_stream` wurde im UI-Polish auf `eventstream` vereinheitlicht, damit klassische und strukturierte Eventstream-Records dieselbe Componentbezeichnung benutzen.

## Beispielmatrix

| Quelle | Channel | Level | Type | Component |
|---|---|---|---|---|
| Client Python | system | WARNING | `null` | `eventstream` |
| Client strukturiert | audit | INFO | `client.trigger.sent` | `stt_session` |
| Server strukturiert | transcription | INFO | `transcription.completed` | Serverkomponente |
| LEFX Python | system | ERROR | `null` | `lefx.device.respeaker.transport` |

## Warum die Trennung wichtig ist

Dadurch sind Fragen möglich wie:

```text
Alle WARNING/ERROR
Nur audit
Nur Serverrecords vom Typ transcription.completed
Alles aus component=eventstream
```

ohne menschenlesbaren Text parsen zu müssen.
