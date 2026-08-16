# Gesamtkonzept für das Client-Feedback-, Event- und Logsystem

## 1. Zweck dieses Dokuments

Dieses Dokument beschreibt die empfohlene Zielarchitektur für die Clientseite eines STT-Systems mit:

- `/ws/transcribe` für Audio, Sessionsteuerung sowie Realtime- und Finaltranskripte,
- `/ws/logs` für strukturierte, persistierte und wiederaufnehmbare Ereignisse,
- `GET /api/logs/events` für historische, administrativ geschützte Ereignisabfragen.

Der Schwerpunkt liegt auf dem Feedback-System des Desktop-Clients:

- Aufnahmestart- und Aufnahmestoppsounds,
- Wakeword-Bestätigung,
- Abschluss- und Fehlersounds,
- dauerhafte LED-Zustände,
- kurzzeitige LED-Effekte,
- LED-Overlays wie ein Follow-up-Fenster,
- robuste Wiederherstellung nach Verbindungsunterbrechungen.

Das Dokument ist als **zu prüfendes Gesamtkonzept** für einen Entwicklungsagenten gedacht. Der Agent soll die Architektur nicht ungeprüft übernehmen, sondern sie zuerst mit dem tatsächlichen Stand des Server-Branches und der vorhandenen Clientarchitektur abgleichen.

Die Architekturentscheidung ist bewusst klar formuliert. Abweichungen sollen nur empfohlen werden, wenn der konkrete Code des Server-Branches nachweislich technische Gründe dafür liefert.

---

## 2. Ausgangssituation

Der Desktop-Client verwaltet beziehungsweise soll zukünftig verwalten:

- das lokale Mikrofon,
- die Audiopaketerzeugung,
- den Audiostream zum STT-Server,
- Push-to-Talk und später Wakewordbetrieb,
- den Empfang von Realtime- und Finaltranskripten,
- die lokale Transkripthistorie,
- das Einfügen finaler Texte,
- die lokale Sprachausgabe,
- Sounds für Benutzerfeedback,
- den LED-Ring des ReSpeaker,
- Live-Logs der aktuellen Session,
- historische Serverereignisse,
- Diagnose- und Performanceinformationen.

Die eigentliche STT-Verarbeitung läuft weiterhin größtenteils auf dem Server. Dort existieren unterschiedliche Verarbeitungsphasen, unter anderem Wakeword-Wartephase, Wakeword-Erkennung, Aufnahmebeginn, Realtime-Inferenz, Aufnahmeende, finale Inferenz sowie Abschluss oder Fehler einer Transkription.

Der Server besitzt bereits einen produktiven STT-WebSocket. Zusätzlich wird das Logging- und Ereignissystem grundlegend erweitert.

---

## 3. Geplanter neuer Serverstand

Der geplante Serverstand sieht vier strukturierte Channels vor:

| Channel | Aufgabe |
| --- | --- |
| `system` | Technischer Serverbetrieb, Worker, Scheduler, Speicher- und Infrastrukturfehler |
| `audit` | Administrative, sicherheitsrelevante und nachvollziehbare Zustandsänderungen |
| `transcription` | Fachlicher Lebenszyklus von Wakeword, Aufnahme und Transkription |
| `performance` | Latenzen, Queuezeiten, Realtime-Kadenz und Ressourcenmesswerte |

Alle Channels sollen einen gemeinsamen, versionierten Event-Envelope verwenden. Ein geplantes Ereignis enthält unter anderem:

```json
{
  "schemaVersion": 1,
  "eventId": "01K...",
  "cursor": 18427,
  "timestamp": "2026-07-30T14:26:41.537Z",
  "channel": "transcription",
  "event": "transcription.completed",
  "severity": "info",
  "serverInstanceId": "server-20260730-01",
  "transport": "websocket",
  "clientId": "client-123",
  "sessionId": "session-456",
  "requestId": null,
  "transcriptionId": "tr-789",
  "segmentId": 3,
  "data": {
    "language": "de",
    "engine": "faster_whisper",
    "model": "medium",
    "audioDurationMs": 2840,
    "totalLatencyMs": 912
  }
}
```

Vorgesehene Kerneigenschaften:

- eindeutige `eventId`,
- fortlaufender `cursor`,
- strukturierte maschinenlesbare Eventnamen,
- Persistenz in JSONL und SQLite,
- Live-Auslieferung über `/ws/logs`,
- Replay nach Cursor,
- Lückenerkennung,
- Wiederaufnahme nach Reconnect,
- Session- oder Administratorauthentifizierung,
- einheitliches Ereignismodell für HTTP- und WebSocket-Transkriptionen.

Diese Eigenschaften machen `/ws/logs` nicht zu einem gewöhnlichen Logstream, sondern zu einem **strukturierten, persistenten Ereignisstrom**.

---

# 4. Verbindliche architektonische Zielentscheidung

## 4.1 Primäre Feedbackquelle

Serverseitige Feedbacks werden primär durch strukturierte Live-Ereignisse aus:

```text
/ws/logs
Channel: transcription
```

ausgelöst.

Dazu gehören insbesondere:

- Wakeword erkannt,
- Aufnahme begonnen,
- Aufnahme beendet,
- finale Verarbeitung begonnen,
- Transkription erfolgreich abgeschlossen,
- Transkription fehlgeschlagen,
- Transkription abgelehnt oder abgebrochen,
- Follow-up-Fenster begonnen oder beendet.

Die bisherige STT-Verbindung `/ws/transcribe` bleibt die kanonische Quelle für:

- Audiotransport,
- Sessionsteuerung,
- Realtime-Text,
- finalen Transkripttext,
- unmittelbare technische Sessionfehler.

Die eigentlichen Texte werden nicht aus dem Logging-System rekonstruiert.

## 4.2 Warum `/ws/logs` als primäre Feedbackquelle

Der neue Log-WebSocket ist für Feedback grundsätzlich besser geeignet als ausschließlich flüchtige STT-WebSocket-Events, weil er:

- eindeutige Eventidentitäten bereitstellt,
- eine fortlaufende Reihenfolge besitzt,
- Lücken erkennen kann,
- Ereignisse nach einem Reconnect nachliefern kann,
- Transkriptionen transportübergreifend korrelieren kann,
- eine strukturierte fachliche Ereignissprache bereitstellt,
- die Zuverlässigkeit nicht ausschließlich von einer dauerhaft störungsfreien Live-Verbindung abhängig macht.

Der Client kann dadurch unterscheiden zwischen:

- einem nie erzeugten Ereignis,
- einem noch nicht empfangenen Ereignis,
- einem nachgelieferten Ereignis,
- einem doppelt empfangenen Ereignis,
- einer tatsächlichen Lücke im Ereignisstrom.

## 4.3 Keine Auswertung formatierter Logtexte

Feedback darf niemals aus menschenlesbaren Meldungen abgeleitet werden.

Zulässig sind ausschließlich strukturierte Felder:

```json
{
  "channel": "transcription",
  "event": "transcription.recording_started"
}
```

Logtexte dürfen sich ändern, übersetzt werden oder zusätzliche Details enthalten, ohne die Clientlogik zu beeinflussen.

---

# 5. Die zwei WebSockets haben unterschiedliche Aufgaben

## 5.1 `/ws/transcribe`

Der bestehende STT-WebSocket ist für die aktive Sprachsession zuständig.

### Client → Server

- `start`,
- `stop`,
- `clear`,
- `ping`,
- `metrics`,
- binäre PCM-Audiopakete.

### Server → Client

- `hello`,
- `ready`,
- `status`,
- `timeline`,
- `realtime`,
- `final`,
- `clear`,
- `pong`,
- `metrics`,
- `warning`,
- `error`.

### Kanonische Verwendung auf dem Client

- Realtime-Anzeige aus `realtime`,
- finaler Text aus `final`,
- technische Sessionsteuerung,
- Start- und Stopplogik,
- Verbindungs- und Recorderdiagnose,
- gegebenenfalls klar definierter Feedback-Fallback.

## 5.2 `/ws/logs`

Der neue Log-WebSocket ist für strukturierte Ereignisse vorgesehen.

### Aufgaben

- Live-Ereignisse empfangen,
- Channels abonnieren,
- Session- oder Adminauthentifizierung,
- Cursor-Replay,
- Keepalive,
- Lückenerkennung,
- Wiederaufnahme,
- Session- und Transkriptionsdiagnose,
- Feedbacktrigger aus dem `transcription`-Channel.

## 5.3 `GET /api/logs/events`

Die Historien-API ist für ältere Ereignisse vorgesehen.

### Aufgaben

- ältere Sessions abrufen,
- nach Zeitraum filtern,
- nach Channel und Event filtern,
- administrative Diagnose,
- einzelne Transkriptionen rekonstruieren,
- Performanceverläufe untersuchen.

Historische API-Ereignisse dürfen niemals unmittelbar Sounds oder vergangene Kurzzeiteffekte auslösen.

---

# 6. Empfohlener Client-Datenfluss

Die Events sollen **nicht direkt vom Log-WebSocket zum FeedbackController** gehen.

Dazwischen liegt eine Verarbeitungskette:

```text
/ws/logs
   │
   ▼
LogStreamClient
   │
   ▼
LogProtocolProcessor
   │
   ▼
LogEventRouter
   ├──► LiveLogBuffer / Log-UI
   ├──► Performance-Modell
   ├──► Transkriptionsdiagnose
   ├──► Systemstatus
   ├──► Audit-Ansicht
   └──► FeedbackEventMapper
              │
              ▼
       FeedbackController
          │          │
          ▼          ▼
     SoundPlayer   LedAdapter
```

Ein einzelnes strukturiertes Event kann gleichzeitig:

- in der Logansicht erscheinen,
- für Performance- oder Diagnosemodelle ausgewertet werden,
- den Zustand einer Transkription aktualisieren,
- in ein normalisiertes Feedbackevent übersetzt werden.

Es wird nicht zwischen „Log oder Feedback“ gewählt. Ein fachliches Event kann beiden Zwecken dienen.

---

# 7. Verantwortlichkeiten der Komponenten

## 7.1 `LogStreamClient`

Der `LogStreamClient` ist ausschließlich für den Transport zuständig.

### Verantwortlichkeiten

- Verbindung zu `/ws/logs`,
- Session- oder Adminauthentifizierung,
- Subscribe-Nachricht,
- Empfang von Textframes,
- Senden und Empfangen von Keepalives,
- Erkennen eines Verbindungsabbruchs,
- Reconnect mit Backoff,
- Übergabe roher Protokollnachrichten an die nächste Schicht.

### Nicht verantwortlich für

- Cursorinterpretation,
- Eventdeduplizierung,
- Logdarstellung,
- Feedbackregeln,
- LED- oder Soundsteuerung.

## 7.2 `LogProtocolProcessor`

Diese Einheit verarbeitet die Zuverlässigkeits- und Protokollebene.

### Verantwortlichkeiten

- Protokollnachricht dekodieren,
- `schemaVersion` prüfen,
- `log.hello`, `log.subscribed`, `log.event`, `log.replay_completed`, `log.gap`, `log.error` und `log.pong` unterscheiden,
- Replayzustand verwalten,
- `eventId` deduplizieren,
- Cursorfolge prüfen,
- Lücken erkennen,
- falsche oder ungültige Envelopes abweisen,
- Event einer Session und einem Zugriffsscope zuordnen,
- verarbeiteten Cursor kontrolliert bestätigen beziehungsweise speichern.

### Grundregel

Der Cursor darf erst als verarbeitet gespeichert werden, nachdem das Event erfolgreich validiert, dedupliziert, fachlich übernommen und an die relevanten Empfänger verteilt wurde.

## 7.3 `LogEventRouter`

Der Router verteilt ein gültiges strukturiertes Event an einen oder mehrere fachliche Empfänger.

```text
channel=system
    → Systemstatus
    → Logansicht
    → optional FeedbackEventMapper für schwere Betriebsfehler

channel=audit
    → Auditansicht
    → Logansicht

channel=transcription
    → Transkriptionsdiagnose
    → Logansicht
    → FeedbackEventMapper

channel=performance
    → Performance-Modell
    → Logansicht
```

Der Router führt selbst keine LED- oder Soundaktionen aus.

## 7.4 `FeedbackEventMapper`

Der Mapper bildet den Serververtrag auf ein internes, stabiles Clientmodell ab.

```text
Server:
channel = transcription
event   = transcription.recording_started

Client:
FeedbackEventKind.RECORDING_STARTED
```

### Aufgaben

- feedbackrelevante Serverevents auswählen,
- aktuelle Session prüfen,
- erforderliche IDs validieren,
- Live oder Replay kennzeichnen,
- Serverfelder auf interne Felder abbilden,
- nicht relevante Events ignorieren,
- aus einem Serverevent gegebenenfalls Zustandsupdate und Impuls erzeugen.

Der `FeedbackController` soll weder Channelnamen noch Servereventnamen kennen müssen.

## 7.5 `FeedbackController`

Der Controller ist die zentrale fachliche Instanz für Sound und LED.

### Verantwortlichkeiten

- aktuellen Feedbackzustand verwalten,
- aktive und ausstehende Transkriptionen verfolgen,
- Zustandsprioritäten anwenden,
- verspätete Ereignisse korrekt behandeln,
- dauerhafte LED-States setzen,
- Overlays starten und beenden,
- kurze LED-Events auslösen,
- Sounds auslösen,
- Live und Replay unterschiedlich behandeln,
- lokale und serverseitige Feedbackquellen zusammenführen.

### Nicht verantwortlich für

- WebSocket-Verbindung,
- Cursor,
- Authentifizierung,
- JSON-Parsing,
- Loghistorie,
- Serverprotokollversionen.

## 7.6 `SoundPlayer`

Der `SoundPlayer` kennt nur logische Soundnamen:

```text
wakeword_detected
recording_started
recording_ended
transcription_completed
transcription_failed
warning
error
```

Er weiß nichts über Sessions, Transkriptionen, WebSockets, Cursor oder Replay.

## 7.7 `LedAdapter`

Der `LedAdapter` bildet abstrakte Clientaktionen auf die konkrete LED-Steuerung ab.

### States

```text
idle
connecting
disconnected
wakeword_wait
listening
recording
processing
speaking
warning
error
```

### Overlays

```text
followup_window
doa
volume
progress
```

### Events

```text
wakeword_detected
recording_started
recording_ended
transcription_completed
transcription_failed
timeout
```

Der Adapter soll keine Entscheidungen über fachliche Zustände treffen.

---

# 8. Normalisiertes Feedbackmodell

Der Server-Envelope soll nicht unverändert bis zum FeedbackController durchgereicht werden.

Ein mögliches internes Modell:

```python
@dataclass(frozen=True)
class FeedbackEvent:
    kind: FeedbackEventKind
    source: FeedbackSource
    delivery_mode: DeliveryMode
    timestamp: datetime
    session_id: str | None = None
    transcription_id: str | None = None
    segment_id: int | None = None
    data: Mapping[str, object] = field(default_factory=dict)
```

Mögliche Werte:

```python
class DeliveryMode(Enum):
    LIVE = "live"
    REPLAY = "replay"
    LOCAL = "local"
```

```python
class FeedbackSource(Enum):
    LOG_STREAM = "log_stream"
    STT_FALLBACK = "stt_fallback"
    MICROPHONE = "microphone"
    HOTKEY = "hotkey"
    TTS = "tts"
    INJECTION = "injection"
    CLIENT = "client"
```

Ein Feedbackevent kann intern in zwei Wirkungen zerlegt werden:

```python
@dataclass(frozen=True)
class FeedbackInstruction:
    target_state: FeedbackState | None
    impulse: FeedbackImpulse | None
    overlay_action: OverlayAction | None
```

Damit kann dasselbe fachliche Ereignis einen dauerhaften Zustand setzen, einen kurzen Impuls auslösen oder ein Overlay verändern.

---

# 9. Live- und Replay-Verarbeitung

Die Unterscheidung zwischen Live und Replay ist zwingend.

## 9.1 Live-Ereignis

Ein Live-Ereignis darf:

- den internen Zustand verändern,
- einen Sound auslösen,
- einen kurzen LED-Effekt auslösen,
- ein Overlay starten oder beenden.

```text
transcription.recording_started
    → Zustand RECORDING
    → Startsound
    → kurzer LED-Startimpuls
```

## 9.2 Replay-Ereignis

Ein Replay-Ereignis darf:

- den Zustand rekonstruieren,
- eine Transkription als aktiv, abgeschlossen oder fehlgeschlagen markieren,
- einen weiterhin gültigen LED-State wiederherstellen,
- ein zeitlich noch gültiges Overlay wiederherstellen.

Ein Replay-Ereignis darf nicht:

- einen alten Aufnahmestartton nachholen,
- einen alten Abschlusston abspielen,
- einen vergangenen Kurzzeiteffekt erneut starten,
- ein bereits abgelaufenes Follow-up-Fenster mit voller Dauer neu starten.

```text
Replay: transcription.recording_started
    → Zustand gegebenenfalls auf RECORDING korrigieren
    → kein Sound
    → kein kurzer LED-Impuls
```

## 9.3 Erforderliche Serververifikation

Der Agent muss im Branch prüfen, wie Replay tatsächlich gekennzeichnet wird:

- explizites Feld am Event,
- eigener Replayrahmen,
- Zustand zwischen `log.subscribed` und `log.replay_completed`,
- anderer implementierter Mechanismus.

Die Clientarchitektur muss den tatsächlichen Vertrag verwenden.

---

# 10. Deduplizierung und Cursor

## 10.1 `eventId`

`eventId` dient als eindeutige Ereignisidentität.

```text
eventId bereits verarbeitet
    → Event vollständig ignorieren
```

Dies verhindert doppelte Sounds, LED-Impulse, Logeinträge und Zustandsübergänge.

## 10.2 `cursor`

Der Cursor dient der Reihenfolge, Lückenerkennung, Wiederaufnahme und Speicherung des letzten vollständig verarbeiteten Standes.

`eventId` und `cursor` erfüllen unterschiedliche Aufgaben und dürfen nicht verwechselt werden.

## 10.3 Persistenz auf dem Client

Der gespeicherte Cursor sollte mindestens getrennt werden nach:

```text
serverIdentity
accessScope
sessionId oder Adminscope
```

Bei einem Wechsel von `serverInstanceId` muss geprüft werden, ob der bisherige Cursor weiterhin gültig ist.

## 10.4 Begrenzte Deduplizierung

Der Client soll nicht unbegrenzt alle `eventId`s im Arbeitsspeicher halten.

Mögliche Strategie:

- begrenzter LRU-Speicher für zuletzt verarbeitete Event-IDs,
- Cursor als dauerhafte Hauptposition,
- zusätzlicher persistenter kleiner Deduplizierungsbereich rund um den letzten Cursor,
- idempotente fachliche Reducer.

Die konkrete Strategie soll anhand des Serververhaltens festgelegt werden.

---

# 11. Korrelation von Session, Transkription und Segment

## 11.1 `sessionId`

Identifiziert eine konkrete STT-Sitzung beziehungsweise einen logischen Vorgang.

## 11.2 `transcriptionId`

Identifiziert eine fachlich vollständige Transkription. Sie ist für das Feedback wichtiger als ausschließlich `segmentId`, weil sie transportübergreifend eindeutig sein soll.

## 11.3 `segmentId`

Korreliert die Transkription mit einem Segment innerhalb einer WebSocket-Session.

## 11.4 Verspätete Abschlussereignisse

Der FeedbackController muss folgenden Ablauf korrekt behandeln:

```text
Transkription A: recording_ended
Transkription B: recording_started
Transkription A: completed
```

Das Abschlussereignis von A darf einen Abschlussimpuls für A auslösen und A als abgeschlossen markieren. Es darf aber nicht den dauerhaften State von B überschreiben.

Der Controller benötigt daher mindestens:

```text
active_recording_transcription_id
active_processing_transcription_ids
latest_started_transcription_id
current_session_id
```

---

# 12. Eventmapping für das Feedback-System

Die tatsächlichen Eventnamen müssen im Server-Branch verifiziert werden.

| Serverevent | Interne Bedeutung | Sound | LED-State | LED-Event / Overlay |
| --- | --- | --- | --- | --- |
| `wakeword.wait_started` | wartet auf Wakeword | keiner | `wakeword_wait` | – |
| `wakeword.wait_ended` | Wake-Wartephase verlassen | keiner | neu berechnen | – |
| `wakeword.detected` | Wakeword erkannt | Bestätigungston | `listening` oder eigener Übergang | kurzer Wakeword-Effekt |
| `wakeword.timeout` | keine Sprache nach Wakeword | optional Timeoutton | `wakeword_wait` | Timeout-Effekt |
| `wakeword.followup_started` | Folgefenster aktiv | keiner | Grundzustand bleibt | Follow-up-Overlay starten |
| `wakeword.followup_timeout` | Folgefenster abgelaufen | optional dezent | neu berechnen | Overlay entfernen |
| `transcription.accepted` | Auftrag angenommen | normalerweise keiner | optional vorbereitend | – |
| `transcription.started` | Transkriptionsvorgang aktiv | keiner | abhängig vom Ablauf | – |
| `transcription.recording_started` | Aufnahme läuft | Startton oder bestätigter Startimpuls | `recording` | kurzer Start-Effekt |
| `transcription.recording_ended` | Aufnahme beendet | optional Stoppton | `processing` | kurzer Stop-Effekt |
| `transcription.completed` | erfolgreich abgeschlossen | Fertigton | neu berechnen | Erfolgseffekt |
| `transcription.failed` | Verarbeitung fehlgeschlagen | Fehlerton | `error` oder vorherigen State erhalten | Fehlereffekt |
| `transcription.rejected` | Auftrag abgelehnt | Ablehnungston | Warnung/Fehler | Warn-/Fehlereffekt |
| `transcription.cancelled` | Vorgang abgebrochen | optional Abbruchton | neu berechnen | Abbrucheffekt |

---

# 13. Lokale Feedbackquellen

Nicht jedes Feedback soll vom Server kommen.

## 13.1 Hotkey

```text
Hotkey gedrückt
    → optional unmittelbarer lokaler Aktivierungsimpuls
```

Dieser bestätigt nur, dass der Client die Benutzeraktion registriert hat. Er bestätigt nicht, dass der Server bereits aufnimmt.

## 13.2 Mikrofon

Lokale Ereignisse:

- Mikrofon geöffnet,
- Mikrofon konnte nicht geöffnet werden,
- Audiogerät verloren,
- Audiostream lokal gestoppt.

## 13.3 TTS

```text
TTS beginnt
    → State SPEAKING

TTS endet
    → vorherigen fachlichen State neu bestimmen
```

Da der Client die Ausgabe verwaltet, ist er die zuverlässigste Quelle für diesen Zustand.

## 13.4 Texteingabe

Mögliche lokale Ereignisse:

- Text erfolgreich eingefügt,
- Einfügen fehlgeschlagen,
- Zielanwendung nicht mehr verfügbar.

## 13.5 Verbindungszustände

STT- und Logtransport müssen getrennt dargestellt werden. Eine getrennte Logverbindung darf nicht automatisch den gesamten Client auf `disconnected` setzen.

---

# 14. Besonderheit bei Aufnahmesounds

Ein serverbestätigter Aufnahmestartton trifft erst ein, nachdem der Server den Start erkannt und das Event erzeugt hat.

```text
Server beginnt Aufnahme
    → Event wird erzeugt
    → Event wird persistiert und/oder versendet
    → Client empfängt Event
    → Client spielt Ton
```

Der Ton könnte dadurch in das Mikrofon zurückgelangen.

## Empfohlene Behandlung

### Push-to-Talk

- optionaler sehr kurzer lokaler Aktivierungston beim Hotkey,
- serverbestätigtes `recording_started` primär für LED und Zustandsbestätigung,
- je nach Echo-Unterdrückung kann ein zweiter Startton deaktiviert werden.

### Wakeword

- `wakeword.detected` ist der früheste sinnvolle serverbestätigte Trigger,
- kurzer Wakeword-Bestätigungston,
- anschließend `recording_started` vor allem für LED-State und Diagnose.

Die konkrete Soundpolicy soll konfigurierbar sein.

---

# 15. Zustandsmodell des FeedbackControllers

Mögliche Grundzustände:

```text
DISCONNECTED
CONNECTING
IDLE
WAKEWORD_WAIT
LISTENING
RECORDING
PROCESSING
SPEAKING
WARNING
ERROR
```

Nicht jeder Servereventname wird ein eigener Grundzustand:

- `wakeword.detected` ist primär ein kurzer Eventimpuls,
- `followup_started` ist ein Overlay,
- `transcription.completed` ist ein Abschlussimpuls,
- `recording` und `processing` sind dauerhafte States.

## 15.1 Zustandsprioritäten

Eine mögliche Prioritätsordnung:

```text
ERROR
SPEAKING
RECORDING
PROCESSING
WAKEWORD_WAIT / LISTENING
IDLE
DISCONNECTED
```

Diese Reihenfolge ist ein Ausgangspunkt und muss mit den tatsächlichen Betriebsabläufen abgeglichen werden.

## 15.2 Overlays und Events überschreiben den Grundzustand nicht dauerhaft

```text
Grundstate = RECORDING
kurzer LED-Effekt = WAKEWORD_DETECTED
danach automatisch zurück zu RECORDING
```

Ein Follow-up-Overlay läuft über dem Grundzustand und endet durch Timeout, neue Aufnahme, explizites Endevent oder Sessionwechsel.

---

# 16. Rolle der vier Logchannels

## 16.1 `transcription`

Primäre Quelle für serverseitiges Benutzerfeedback:

- Wakeword,
- Aufnahme,
- Transkriptionslebenszyklus,
- Abschluss,
- Fehler,
- Abbruch.

## 16.2 `performance`

Nur für Monitoring und Diagnose. Keine normalen Feedbacktrigger für einzelne Realtime-Abstände, Queuezeiten oder normale Latenzwerte.

## 16.3 `audit`

Keine Aufnahme-, Wakeword- oder Abschlusssounds. Audit dient Administration, Authentifizierung, Konfigurationsänderungen und Nachvollziehbarkeit.

## 16.4 `system`

Kann übergeordnete Zustände beeinflussen:

- `server.ready`,
- `worker.failed`,
- `recorder.failed`,
- `scheduler.overloaded`,
- `server.error`.

Nur eine klar definierte Whitelist schwerwiegender Systemevents darf den FeedbackController erreichen.

---

# 17. Fallback über `/ws/transcribe`

## 17.1 Normalbetrieb

Im Normalbetrieb löst ausschließlich `/ws/logs` die serverseitigen Feedbackimpulse aus.

Es darf keine parallele doppelte Auslösung aus `/ws/logs` und `/ws/transcribe` geben.

## 17.2 Möglicher Fallback

Ein Fallback kann sinnvoll sein, wenn:

- `/ws/logs` nicht verbunden ist,
- die Sessionauthentifizierung noch nicht abgeschlossen ist,
- Replay läuft und der Client trotzdem unmittelbares Feedback benötigt,
- der Serverbranch keine ausreichende Live-Latenz garantiert.

Mögliche Fallbackevents:

- `timeline(wakeword_detected)`,
- `timeline(recording_started)`,
- `timeline(recording_ended)`,
- `final`,
- relevante `error`-Events.

## 17.3 Fallbackregeln

- Fallback nur, wenn der Logstream nachweislich nicht `LIVE` ist.
- Fallbackevents werden in dasselbe normalisierte Feedbackmodell übersetzt.
- Wenn das zugehörige Logevent später per Replay kommt, darf kein zweiter Impuls entstehen.
- Wenn der Serverbranch eine schnelle und verlässliche Logverbindung garantiert, kann zunächst vollständig auf den Fallback verzichtet werden.

Der Agent soll diese Entscheidung anhand des tatsächlichen Codes treffen und eindeutig begründen.

---

# 18. Authentifizierung

## 18.1 Sessionzugriff

Ein normaler Desktop-Client soll nur Ereignisse der eigenen aktuellen Session sehen.

Der Agent muss im Branch prüfen:

- woher der Client das Token erhält,
- ob es im STT-`hello` enthalten ist,
- wie lange es gültig ist,
- ob es nach Sessionende noch kurz nutzbar bleibt,
- wie es bei Reconnect behandelt wird,
- ob es erneuert werden kann,
- welche Channels damit abonnierbar sind.

Tokens dürfen nicht in URL-Queryparametern, Logs, Fehlermeldungen oder ungeschützten Konfigurationsdateien erscheinen.

## 18.2 Administratorzugriff

Administratorzugriff wird benötigt für:

- globale Live-Logs,
- andere Sessions,
- Audit,
- Systemdetails,
- historische API.

Unter Windows sollte ein dauerhaft gespeichertes Admin-Credential nicht im Klartext in YAML oder `.env` liegen. Eine kostenlose passende Lösung ist der Windows Credential Manager.

---

# 19. Historische Logs und UI

## 19.1 Live-Logpuffer

Der Client soll nicht unbegrenzt alle Live-Events im Speicher halten.

Empfehlung:

- konfigurierbarer Ringpuffer,
- beispielsweise 5.000 bis 20.000 sichtbare Ereignisse,
- ältere UI-Einträge werden entfernt,
- Cursor und fachlicher Zustand bleiben erhalten.

## 19.2 Qt-Modell

Für große Logmengen sollte ein `QAbstractTableModel` oder vergleichbares Modell verwendet werden.

Nicht geeignet:

- tausende einzelne `QLabel`,
- ein eigenes Widget pro Logevent,
- vollständige Historie in einem unlimitierten Textfeld.

## 19.3 Live-Ansicht

Sinnvolle Filter:

- Channel,
- Severity,
- Session,
- Transkription,
- Segment,
- Eventname,
- Zeitraum,
- Freitext.

## 19.4 Historienansicht

- cursorbasierte Pagination,
- Abbruch laufender Abfragen,
- getrennte Live- und Historienmodelle,
- keine Sounds oder LED-Effekte aus historischen Ergebnissen.

---

# 20. Empfohlene Modulstruktur

Die endgültige Struktur soll an die vorhandene Clientarchitektur angepasst werden.

```text
core/
├── stt_session_client.py
├── server_event_dispatcher.py
├── client_state.py
└── client_event_router.py

logging_client/
├── log_stream_client.py
├── log_history_client.py
├── log_protocol_models.py
├── log_protocol_processor.py
├── log_event_router.py
├── log_cursor_store.py
└── log_buffer.py

feedback/
├── feedback_models.py
├── feedback_event_mapper.py
├── feedback_controller.py
├── feedback_policy.py
├── sound_player.py
└── led_adapter.py
```

Diese Struktur ist kein Zwang. Der Agent soll unnötige Parallelklassen vermeiden und bestehende geeignete Komponenten weiterverwenden.

---

# 21. Threading und PySide6

Die WebSocket- und Logverarbeitung darf die Qt-Oberfläche nicht blockieren.

Der Agent soll prüfen und planen:

- in welchem Thread oder Async-Kontext die WebSockets laufen,
- wie strukturierte Events threadsicher in den Qt-Hauptthread gelangen,
- welche Komponenten `QObject` sein müssen,
- welche Signale verwendet werden,
- ob der FeedbackController im Hauptthread arbeitet,
- ob Sound und LED eigene Worker benötigen,
- wie Shutdown und Reconnect sauber beendet werden.

Mögliche Signale:

```text
log_transport_state_changed
log_event_received
log_gap_detected
log_replay_started
log_replay_completed
feedback_event_received
feedback_state_changed
sound_failed
led_failed
```

---

# 22. Fehler- und Degradationsverhalten

## 22.1 Log-WebSocket fällt aus

- STT-Verbindung und Audio dürfen weiterlaufen.
- UI zeigt den Logtransport separat als getrennt.
- Feedback kann je nach finaler Fallbackentscheidung eingeschränkt oder über `/ws/transcribe` fortgesetzt werden.
- Nach Reconnect wird Replay durchgeführt.
- Replay erzeugt keine alten Impulse.

## 22.2 STT-WebSocket fällt aus

- Audioübertragung stoppt,
- Sessionstate wird ungültig,
- Logstream kann eventuell noch administrative Ereignisse liefern,
- Aufnahmefeedback wird nicht fortgesetzt,
- Client versucht kontrollierten Reconnect.

## 22.3 `log.gap`

- Lücke sichtbar markieren,
- Replay oder History-Nachladung starten,
- keine Annahme vollständiger Historie,
- Feedbackzustand nach Möglichkeit rekonstruieren,
- keine vergangenen Sounds nachholen.

## 22.4 Token abgelaufen

- Logstream in `AUTH_REQUIRED`,
- Reauthentifizierung versuchen,
- keine Endlosschleife mit ungültigem Token,
- STT-Session unabhängig weiterführen, sofern möglich.

## 22.5 Unbekannter Eventtyp

- Event loggen und anzeigen,
- nicht als Fehler des gesamten Streams behandeln,
- nicht an Feedback weitergeben,
- Forward-Compatibility erhalten.

---

# 23. Anforderungen an die Serverereignisse

Feedbackrelevante Events müssen eine hohe Zustellklasse besitzen:

```text
wakeword.detected
transcription.recording_started
transcription.recording_ended
transcription.completed
transcription.failed
transcription.rejected
transcription.cancelled
```

Sie sollten:

- vor Live-Auslieferung eine `eventId` erhalten,
- einen Cursor erhalten,
- persistent gespeichert werden,
- per Replay abrufbar sein,
- gegenüber detaillierten Performanceevents priorisiert werden.

Verwerfbar dürfen eher einzelne Realtime-Performancepunkte, Debugdetails und engmaschige Messwerte sein.

Der Agent muss die tatsächliche Persistenz- und Versandfolge im Servercode prüfen.

---

# 24. Vom Agenten zu prüfende Kernfragen

## Server-Envelope

- Welche Felder sind tatsächlich implementiert?
- Welche sind Pflichtfelder?
- Welche sind nur geplant?
- Ist `schemaVersion` vorhanden?
- Ist `serverInstanceId` stabil?

## Cursor

- global oder pro Channel?
- wird er vor oder nach Persistenz vergeben?
- ist er streng monoton?
- was passiert bei Serverneustart?
- wie wird ein ungültiger Cursor behandelt?

## Replay

- wie wird Replay gestartet?
- wie werden mehrere Seiten geliefert?
- wie endet Replay?
- wann beginnt Live-Auslieferung?
- kann zwischen Replay und Live eine Lücke entstehen?

## Eventpersistenz

- welche Events werden in SQLite gespeichert?
- welche nur in JSONL?
- welche nur live?
- können kritische Transcription-Events verworfen werden?

## Authentifizierung

- wie wird der Sessiontoken ausgegeben?
- welche Channels darf er abonnieren?
- welche Lebensdauer besitzt er?
- wie funktioniert Adminauthentifizierung?

## Eventnamen

- stimmen die geplanten Namen mit dem Code überein?
- existieren doppelte Eventnamen in mehreren Channels?
- sind Wakewordevents vollständig?
- existieren fehlende Ereignisse für das Feedback?

## Latenz

- wie groß ist die zusätzliche Verzögerung zwischen fachlichem Vorgang und `/ws/logs`?
- erfolgt Persistenz synchron vor Liveversand?
- ist die Latenz für LED und Sound geeignet?

---

# 25. Empfohlene Tests

## Parser und Protokoll

- gültiger Envelope,
- unbekannte optionale Felder,
- unbekannte Eventtypen,
- ungültige Schema-Version,
- fehlende Pflichtfelder.

## Cursor und Replay

- fortlaufende Cursor,
- doppeltes Event,
- ausgelassener Cursor,
- `log.gap`,
- Replay über mehrere Seiten,
- Reconnect während Replay,
- Serverinstanzwechsel.

## Feedbackmapping

- jedes relevante Transcription-Event,
- nicht relevante Performanceevents,
- Audit löst kein Feedback aus,
- schwere Systemevents,
- lokale Feedbackevents.

## Live und Replay

- Live-Aufnahmestart spielt Sound,
- Replay-Aufnahmestart spielt keinen Sound,
- Replay stellt LED-State wieder her,
- abgelaufenes Follow-up-Overlay wird nicht neu gestartet.

## Zustandspriorität

- alte Transkription abgeschlossen, während neue aufnimmt,
- TTS startet während Processing,
- Fehler während Recording,
- Logstreamausfall während Aufnahme,
- neue Session nach Reconnect.

## Fallback

Falls implementiert:

- Logstream nicht live → STT-Fallback aktiv,
- Logstream kehrt zurück,
- Replay liefert dasselbe Ereignis,
- Sound bleibt genau einmal,
- kein Zustandsverlust.

## Integration

- echter Test gegen Server-Branch,
- künstliche Verzögerungen,
- doppelte Events,
- vertauschte fachliche Abschlussereignisse,
- absichtlicher Socketabbruch,
- Tokenablauf,
- Gap und Replay.

---

# 26. Empfohlene Arbeitspakete für eine spätere Umsetzung

## Arbeitspaket 1 – Verifizierter Vertrag

- tatsächliche Endpunkte,
- tatsächlicher Envelope,
- Authentifizierung,
- Eventkatalog,
- Cursor und Replay,
- dokumentierte Sequenzen.

## Arbeitspaket 2 – Logtransport

- `/ws/logs`,
- Subscribe,
- Sessionauthentifizierung,
- Keepalive,
- Reconnect,
- Transportzustand.

## Arbeitspaket 3 – Protokollprozessor

- Envelopeparser,
- Replayzustand,
- Cursor,
- Deduplizierung,
- Gap-Erkennung.

## Arbeitspaket 4 – Router und Logmodell

- Channeldispatch,
- Live-Puffer,
- Performance- und Diagnoserouting,
- Qt-Modell.

## Arbeitspaket 5 – Feedback-Mapping

- Serverevents auf interne Feedbackevents,
- lokale Ereignisse integrieren,
- Session- und Transkriptionskorrelation.

## Arbeitspaket 6 – FeedbackController

- Zustandsautomat,
- Prioritäten,
- Live-/Replay-Regeln,
- verspätete Ereignisse,
- Overlays und Impulse.

## Arbeitspaket 7 – Sound und LED

- SoundPlayer,
- LedAdapter,
- konfigurierbare Policy,
- Fehlerbehandlung,
- deaktivierbare Ausgabekanäle.

## Arbeitspaket 8 – Historien-API

- Adminauthentifizierung,
- Filter,
- Pagination,
- Historienansicht,
- keine Feedbackauslösung.

## Arbeitspaket 9 – Fallback

Nur falls die Analyse ihn als notwendig bewertet:

- Whitelist aus `/ws/transcribe`,
- normalisierte Ersatzereignisse,
- quellenübergreifende Deduplizierung,
- Rückkehr zum Log-Primärbetrieb.

---

# 27. Erwarteter Analyseauftrag für den Agenten

Bevor Code geändert wird, soll der Agent einen ausführlichen Bericht erstellen.

Der Bericht soll:

1. den tatsächlichen Server-Branch untersuchen,
2. Planung und Code vergleichen,
3. alle Eventtypen und Felder dokumentieren,
4. Authentifizierung und Replay verifizieren,
5. die Latenz- und Zuverlässigkeitseigenschaften bewerten,
6. das hier beschriebene Zielbild prüfen,
7. Blocker und notwendige Serverkorrekturen benennen,
8. eine eindeutige endgültige Clientempfehlung abgeben,
9. danach einen konkreten Implementierungsplan erstellen.

Die Empfehlung soll nicht als unverbindliche Liste gleichwertiger Varianten enden. Der Agent soll den technisch besten Weg festlegen und begründen.

---

# 28. Endgültige Empfehlung dieses Gesamtkonzepts

## Primäre Triggerquelle

```text
/ws/logs
Channel: transcription
```

## Datenfluss

```text
/ws/logs
→ LogStreamClient
→ LogProtocolProcessor
→ LogEventRouter
→ FeedbackEventMapper
→ FeedbackController
→ SoundPlayer und LedAdapter
```

Parallel gehen dieselben Events an Logansicht, Diagnose, Performanceauswertung und Transkriptionshistorie.

## Textquelle

```text
/ws/transcribe
→ realtime
→ final
```

## Replayregel

```text
Replay:
    Zustand rekonstruieren
    keine alten Sounds
    keine vergangenen Kurzzeiteffekte

Live:
    Zustand aktualisieren
    Sounds, LED-Events und Overlays auslösen
```

## Fallback

`/ws/transcribe` ist kein paralleler Normaltrigger. Ein kontrollierter Fallback wird nur implementiert, wenn der konkrete Server-Branch zeigt, dass der Logstream zeitweise nicht schnell oder verfügbar genug ist.

## Feedbackarchitektur

Das Feedback-System ist ein eigenständiges, testbares Modul innerhalb des Desktop-Clients. Es ist kein separater Prozess und enthält keine Transport- oder Logginglogik.

## Wichtigste Leitregel

> Strukturierte Serverevents werden einmal technisch validiert und anschließend zentral verteilt. Das Feedback-System erhält ausschließlich normalisierte fachliche Ereignisse und bleibt vollständig vom konkreten WebSocket- und Logprotokoll entkoppelt.

---

# 29. Quellenbasis

Dieses Konzept basiert auf den bereitgestellten Unterlagen:

- `02-websocket-protokoll.md`
- `03-server-events-kurzreferenz.md`
- `04-server-events-katalog-und-chronologie.md`
- `05-client-zustandsmodell.md`
- dem Dokument zum geplanten neuen strukturierten Logging- und Eventsystem mit den Channels `system`, `audit`, `transcription` und `performance`.

Der tatsächliche Server-Branch bleibt für alle Implementierungsdetails die maßgebliche Quelle.
