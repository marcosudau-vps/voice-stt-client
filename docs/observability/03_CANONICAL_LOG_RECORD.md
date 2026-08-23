# CanonicalLogRecord – Referenz

## Kurz und einfach erklärt

Python-Logs und Serverevents sehen unterschiedlich aus. Damit man beide gemeinsam suchen kann, bekommen alle dieselbe **Karteikarte**.

Darauf stehen: Zeitpunkt, Herkunft, Wichtigkeit, Typ, technische Komponente, IDs, Meldung und strukturierte Details.

## Feldgruppen

### Identität und Zeit

| Feld | Zweck |
|---|---|
| `record_id` | ID dieses lokalen Speichereintrags |
| `received_at` | lokaler Eingangs-/Erzeugungszeitpunkt |
| `source_timestamp` | ursprünglicher Zeitpunkt der Quelle |

`record_id` ist nicht die Serverevent-ID; dafür existiert `event_id`.

### Herkunft

| Feld | Zweck |
|---|---|
| `producer_kind` | grobe Herkunftsklasse |
| `producer_id` | konkrete Produceridentität |
| `instance_id` | konkrete laufende Instanz |
| `scope` | Session/Instanz/global |

### Klassifikation

| Feld | Zweck |
|---|---|
| `channel` | Diagnosebereich |
| `level` | Schweregrad |
| `type` | strukturierter Ereignistyp |
| `component` | technische Komponente/Logger |

Beispiel:

```text
producer_kind = client
channel       = audit
level         = INFO
type          = client.trigger.sent
component     = stt_session
```

### Korrelation

| Feld | Zweck |
|---|---|
| `session_id` | STT-Session |
| `generation` | Verbindungs-/Sessiongeneration |
| `activation_id` | Activation-Kontext |
| `segment_id` | Segment |
| `transcription_id` | Transkriptionsvorgang |
| `command_id` | Request/Ack-Korrelation |
| `event_id` | stabile Serverevent-ID |
| `correlation_id` | generische Korrelation |
| `server_cursor` | Position im Serverjournal |

### Inhalt

| Feld | Zweck |
|---|---|
| `message` | menschenlesbare Kurzbeschreibung |
| `details` | strukturierte Zusatzdaten |
| `raw` | optionaler Originalpayload |
| `replayed` | Replaykennzeichen |

## `message` vs. `details` vs. `raw`

```text
message → für Menschen
details → strukturierte Zusatzdaten
raw     → optionaler möglichst originaler Quellpayload
```

Beispiel:

```json
{
  "message": "Trigger sent",
  "details": {"source": "manual", "attempt": 1}
}
```

## Beispiel: Python-Log

```json
{
  "producer_kind": "client",
  "producer_id": "voice-stt-client",
  "channel": "system",
  "level": "WARNING",
  "type": null,
  "component": "eventstream",
  "session_id": "…",
  "message": "Event stream attempt failed",
  "details": {
    "logger": "eventstream",
    "func": "run",
    "line": 123,
    "thread": "…"
  }
}
```

## Beispiel: strukturierter Clientevent

```json
{
  "producer_kind": "client",
  "producer_id": "voice-stt-client",
  "channel": "audit",
  "level": "INFO",
  "type": "client.trigger.sent",
  "component": "stt_session",
  "session_id": "s-123",
  "generation": 4,
  "command_id": "cmd-88",
  "details": {"source": "manual"}
}
```

## Beispiel: Serverevent

```json
{
  "producer_kind": "server",
  "producer_id": "voice-stt-server",
  "channel": "transcription",
  "level": "INFO",
  "type": "transcription.completed",
  "session_id": "s-123",
  "segment_id": 17,
  "event_id": "evt-…",
  "server_cursor": 8124,
  "replayed": false,
  "raw": {
    "schemaVersion": 1,
    "eventId": "evt-…",
    "cursor": 8124,
    "event": "transcription.completed"
  }
}
```

## Python-LogRecord-Mapping

Konzeptionell:

```text
channel          ← Logger-Mapping, sonst system
component        ← record.name
level            ← record.levelname
type             ← null
message          ← record.getMessage()
source_timestamp ← record.created
```

Details enthalten technische Metadaten wie Logger, Funktion, Zeile, Thread und ausgewählte explizite Extras. Beliebige `args`, lokale Variablen oder pauschale `repr()`-Dumps werden nicht als Diagnosemodell verwendet.

## Regel für IDs

Nur IDs eintragen, die die Komponente sicher kennt. Keine Session-/Activation-ID aus einem globalen „aktuellen Zustand“ dazuerfinden.

Eine fehlende ID ist ehrlicher als eine falsche ID.

## `activation_id`

Vor der Trigger-Migration: anzeigen und filtern ja, clientseitig raten oder als Lifecycle-Wahrheit verwenden nein.

## Inhaltsgrenzen

Die Normalisierung enthält auch Redaction-/Content-Regeln: keine Audio-Rohpayloads, Secrets/Tokens redigieren, Transkriptinhalt nur gemäß Policy. Das ist eine Schutzgrenze des Datenmodells, kein eigener Schwerpunkt dieser Dokumentation.
