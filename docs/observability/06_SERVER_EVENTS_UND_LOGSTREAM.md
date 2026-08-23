# Server-Events und Logstream

## Kurz und einfach erklärt

Der Client bekommt vom Server zwei unterschiedliche Arten von Informationen:

1. **Betriebsnachrichten**, die er für die laufende Diktatsession braucht – etwa „bereit“, „Aufnahme läuft“ oder „Text ist final“.
2. Ein **Ereignisjournal**, das vor allem erklärt, was auf dem Server passiert ist und auch nachgeliefert werden kann.

Das erste ist wie ein laufendes Gespräch am Schalter. Das zweite ist wie das Protokollbuch hinter dem Schalter.

Für den aktuellen Betrieb bleibt `/ws/transcribe` maßgeblich. `/ws/logs` ergänzt Diagnose, History und Replay.

---

## 1. Zwei getrennte Serverachsen

```text
/ws/transcribe
    → operative Session
    → hello, ready, status, timeline, realtime, final, ...
    → aktuelle Bedienzustände und Text

/ws/logs
    → strukturierte Beobachtung
    → Eventjournal, Cursor, Replay, Channels
    → Diagnose und Historie
```

Die Observability darf aus `/ws/logs` keine zweite fachliche Zustandsmaschine bauen.

---

## 2. `/ws/transcribe` – dokumentierte Top-Level-Typen

Der produktive Single-WebSocket-Vertrag kennt elf Routingtypen:

| `type` | Zweck |
|---|---|
| `hello` | Session angenommen, Vertrag/Settings/Capabilities |
| `ready` | Server/Modelle bereit |
| `status` | Zustandsmomentaufnahme |
| `timeline` | fachlicher Meilenstein |
| `realtime` | revidierbares Zwischenergebnis |
| `final` | finaler Text |
| `clear` | Antwort auf Clear |
| `pong` | Ping/Pong |
| `metrics` | Sessionmetriken |
| `warning` | behebbarer Warnfall |
| `error` | Protokoll-/Runtime-/Enginefehler |

Diese Namen sind **nicht** identisch mit den strukturierten `/ws/logs`-Eventnamen.

---

## 3. Timeline-Untertypen

`timeline.event` beschreibt fachliche Meilensteine:

| Timeline-Event | Bedeutung |
|---|---|
| `wakeword_wait_started` | Wake-Word-Wartephase beginnt |
| `wakeword_wait_ended` | Wake-Word-Wartephase endet |
| `wakeword_detected` | Wake Word erkannt |
| `wakeword_timeout` | kein Sprachbeginn nach Wake Word |
| `wakeword_followup_started` | Follow-up-Fenster aktiv |
| `wakeword_followup_timeout` | Follow-up abgelaufen |
| `recording_started` | Aufnahme begonnen |
| `recording_ended` | Aufnahme beendet |
| `transcription_started` | Finaltranskription beginnt |
| `realtime_transcript` | Realtime-Meilenstein |
| `final_transcript` | Final-Meilenstein |

`status` ist dagegen ein Snapshot und darf wiederholt eintreffen.

---

## 4. Strukturierter Server-Event-Envelope

Das Server-Observability-System arbeitet mit einem gemeinsamen Envelope, konzeptionell:

```json
{
  "schemaVersion": 1,
  "eventId": "…",
  "cursor": 18427,
  "timestamp": "…",
  "channel": "transcription",
  "event": "transcription.completed",
  "severity": "INFO",
  "serverInstanceId": "…",
  "sessionId": "…",
  "transcriptionId": "…",
  "segmentId": 4,
  "data": {}
}
```

Wesentliche Felder:

- `eventId` – stabile Ereignisidentität;
- `cursor` – Position im Serverjournal;
- `channel`;
- `event`;
- `severity`;
- `serverInstanceId`;
- Korrelationsfelder;
- `data`.

---

## 5. Server-Channels

```text
system
audit
transcription
performance
```

Ein normaler sessiongebundener Client darf im dokumentierten Vertrag typischerweise die eigene Session für:

```text
audit
transcription
performance
```

lesen, nicht globale `system`-Daten.

---

## 6. `/ws/logs` – Transportnachrichten

| Typ | Zweck |
|---|---|
| `log.hello` | Logprotokoll und Serverzustand vorstellen |
| `log.subscribed` | Subscription bestätigt |
| `log.event` | strukturiertes Serverevent |
| `log.replay_completed` | Replayphase beendet |
| `log.gap` | bekannte Lücke sichtbar machen |
| `log.error` | Logstream-/Store-/Cursorfehler |
| `log.pong` | Keepalive/Ping-Antwort |

Beispiel:

```json
{
  "type": "log.event",
  "event": {
    "schemaVersion": 1,
    "cursor": 18427,
    "channel": "transcription",
    "event": "transcription.completed"
  },
  "replay": false
}
```

---

## 7. Replay

```text
replay = true  → historisch nachgeliefert
replay = false → Live-Event
```

`log.replay_completed` markiert den Übergang.

Für den Client gilt:

> Replay darf Diagnose und History vervollständigen, aber keine vergangenen Sounds, LED-Impulse oder andere zeitkritische Effekte erneut auslösen.

Für lokale Persistenz gilt zusätzlich: dieselbe `eventId` soll nicht als zweiter Datensatz gespeichert werden.

---

## 8. Besonders relevante strukturierte Serverevents

### Wake Word

```text
wakeword.wait_started
wakeword.wait_ended
wakeword.detected
wakeword.timeout
wakeword.followup_started
wakeword.followup_timeout
```

### Transcription

```text
transcription.recording_started
transcription.recording_ended
transcription.started
transcription.completed
transcription.failed
transcription.rejected
transcription.cancelled
```

Typische Beziehung:

```text
/ws/transcribe timeline(recording_started)
→ serverseitiges Journal: transcription.recording_started
```

```text
/ws/transcribe timeline(wakeword_detected)
→ serverseitiges Journal: wakeword.detected
```

```text
/ws/transcribe final + timeline(final_transcript)
→ serverseitiges Journal: transcription.completed
```

---

## 9. Warum nicht jedes Serverevent Runtimewirkung bekommt

Servereventtypen können kompatibel erweitert werden.

Unbekannte Events sollen:

- als Diagnoseinformation erhalten bleiben;
- nicht den gesamten Logstream brechen;
- nicht automatisch Feedback oder Lifecycle ändern.

Das erhält Forward Compatibility.

---

## 10. `eventId` und `cursor`

### `eventId`

Identifiziert das Ereignis selbst.

Verwendung:

- Dedupe;
- stabile Identität.

### `cursor`

Identifiziert seine Position im Journal.

Verwendung:

- Replay;
- History;
- Resume;
- Reihenfolge.

Gefilterte Cursor müssen nicht lückenlos sein, weil dazwischen Events anderer Sessions oder Channels liegen können.

---

## 11. `hello.logAccess`

Der normale STT-`hello` kann einen sessiongebundenen Logzugang liefern:

```json
{
  "available": true,
  "websocketPath": "/ws/logs",
  "historyPath": "/api/logs/events",
  "accessToken": "…",
  "sessionId": "…",
  "expiresAt": "…"
}
```

Der Token gehört nur in den Speicher und nicht in Logs, YAML, URL-Queries oder den lokalen Observability-Store.

---

## 12. Wichtigste Grenze

```text
/ws/transcribe + lokale Clientereignisse
    = operative Wahrheit

/ws/logs
    = Beobachtung, Diagnose, Replay, Historie
```

---

## 13. Weiterführende Serverreferenzen

Für den vollständigen operativen WebSocket-Vertrag bleiben die vorhandenen Clientkopien maßgeblich:

```text
server-docs-for-client-development/
├── 02-websocket-protokoll.md
├── 03-server-events-kurzreferenz.md
├── 04-server-events-katalog-und-chronologie.md
└── ...
```

Diese Datei erklärt vor allem die **Einordnung in Observability**.
