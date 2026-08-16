# Ausführungsauftrag: Server-Eventstrom konsequent SQLite-first ausliefern

> **Datum:** 1. August 2026  
> **Status:** zur direkten Übergabe an einen Umsetzungsagenten  
> **Zielrepository:** `P:\DockerProjekte\voice-stt-server`  
> **Geprüfte Ausgangsbasis:** lokaler Branch `main`, Commit `33bde82`  
> **Wichtig:** Vor der Ausführung den aktuellen Branch, HEAD und Worktree erneut prüfen. Keine fremden Änderungen zurücksetzen.

---

## 1. Direkter Auftrag an den Umsetzungsagenten

Setze im Repository `P:\DockerProjekte\voice-stt-server` den nachfolgend vollständig beschriebenen Umbau des strukturierten Eventsystems um.

Das Ziel ist ein einheitlicher, SQLite-first arbeitender Eventstrom:

```text
Strukturiertes Event wird erzeugt
    → zentral bereinigen und validieren
    → in SQLite mit seinem endgültigen Cursor committen
    → erst nach erfolgreichem Commit live über /ws/logs sichtbar machen
    → anschließend optional nach JSONL und stdout spiegeln
```

Für alle tatsächlich erzeugten strukturierten Events gilt dieselbe Zustelllogik. Es gibt keine getrennte Best-Effort-Klasse für Performanceevents. Die Menge der Performanceevents wird ausschließlich vor ihrer Erzeugung über vorhandene Schalter wie `performance_logging_enabled` und `realtime_log_detail=off|summary|events` begrenzt.

Ein Event, das als normales `log.event` über `/ws/logs` ausgeliefert wird, muss bereits in SQLite gespeichert und über denselben Cursor per Replay abrufbar sein.

Arbeite den Auftrag vollständig ab, ergänze die Tests, führe die relevante und danach die vollständige Testsuite aus und erfülle die Dokumentationsordnung des Serverrepositories. Stoppe nach Abschluss dieses Pakets.

---

## 2. Verbindliche Zielentscheidungen

Die folgenden Entscheidungen sind für diesen Auftrag festgelegt und nicht erneut als gleichwertige Varianten zu diskutieren.

### 2.1 SQLite ist die kanonische Ereignisquelle

SQLite ist für strukturierte Serverevents die führende Quelle für:

- Cursorvergabe,
- Live-Auslieferung,
- Replay,
- HTTP-Historie,
- Reihenfolge und Eventidentität.

JSONL und stdout sind ausschließlich optionale Spiegel. Ein Ausfall eines Spiegels darf die kanonische SQLite-Historie und den Live-Eventstrom nicht unvollständig machen.

### 2.2 Kein Liveversand vor dem Commit

Der Server darf ein normales `log.event` erst nach erfolgreichem SQLite-Commit veröffentlichen.

Nicht zulässig ist der heutige unabhängige Fan-out:

```text
Event
  ├── Store-Queue
  └── Publish-Queue
```

Ziel:

```text
Event
  → SQLite-Commit
  → Commit-Benachrichtigung
  ├── /ws/logs liest committed Events
  ├── JSONL-Spiegel
  └── stdout-Spiegel
```

### 2.3 Alle erzeugten Events besitzen dieselbe Garantie

Wenn ein Channel oder eine Detailstufe deaktiviert ist, entsteht das betreffende Event nicht. Sobald `StructuredEventHub.emit()` ein Event akzeptiert und dieses später als `log.event` sichtbar wird, muss es jedoch SQLite-committed und replaybar sein.

Performanceumfang wird durch Erzeugungspolitik begrenzt:

- `performance_logging_enabled=false`: keine Performanceevents,
- `realtime_log_detail=off`: keine Realtime-Details und keine Summary,
- `summary`: nur Zusammenfassung,
- `events`: alle vorgesehenen Detailereignisse; auch diese laufen SQLite-first.

Es darf keine zweite, schwächere WebSocket-Zustellklasse entstehen.

### 2.4 Fehler werden sichtbar, nicht verschleiert

Wenn SQLite nicht schreiben kann:

- wird das betroffene Event nicht als normales `log.event` gesendet,
- wird kein Cursor ausschließlich im Arbeitsspeicher als erfolgreich fortgeschrieben,
- wird der Eventstream als degradiert markiert,
- erhalten aktive `/ws/logs`-Clients eine Protokollfehlermeldung mit maschinenlesbarem Fehlercode,
- wird die Log-WebSocket-Verbindung mit einem Serverfehlercode kontrolliert geschlossen,
- bleibt `/ws/transcribe` grundsätzlich funktionsfähig,
- darf keine rekursive `storage.failed`-Endlosschleife entstehen.

Der Zuverlässigkeitsvertrag lautet damit:

> At-least-once-Replay über WebSocket-Unterbrechungen, solange der SQLite-Eventstore schreibbar ist. Bei einem Storeausfall erfolgt ein expliziter Fail-stop des Eventstroms statt einer ungespeicherten Scheinauslieferung.

### 2.5 Live und Replay stammen aus derselben Quelle

Der Live-WebSocket soll committed SQLite-Events ab einem Cursor fortlaufend auslesen. Eine Commit-Benachrichtigung darf den Handler wecken, ist aber selbst nicht die Eventquelle. Verlorene oder zusammengefasste Wakeups dürfen nicht zu Eventverlust führen, weil der Handler immer anhand des SQLite-Cursors nachliest.

### 2.6 Der bestehende Event-Envelope bleibt kompatibel

Der Event-Envelope behält `schemaVersion: 1` und seine vorhandenen Felder. Die Semantik des Log-WebSocket-Protokolls wird zusätzlich explizit versioniert.

`log.hello` und `hello.logAccess` erhalten mindestens:

```json
{
  "logProtocolVersion": 2,
  "deliveryMode": "sqlite_first",
  "replayAvailable": true
}
```

Bestehende Felder bleiben erhalten.

### 2.7 Jede begonnene Transkription erhält einen terminalen Zustand

Der dokumentierte Randfall eines leeren finalen WebSocket-Ergebnisses wird geschlossen. Wenn `recorder.text()` nach Normalisierung leer ist, entsteht ein terminales Event:

```text
transcription.discarded
```

mit mindestens:

- `sessionId`,
- `clientId`,
- `transcriptionId`,
- `segmentId`,
- `transport: websocket`,
- `data.reason: empty_final`.

Das Segment muss dabei genau einmal finalisiert werden. Es wird kein leeres `final`-Textframe an den Transkriptionsclient gesendet.

---

## 3. Verbindliche Pflichtlektüre vor der ersten Änderung

Lies vollständig beziehungsweise in der genannten Reihenfolge:

1. `AGENTS.md`
2. `docs/.archiv/README.md`
3. `docs/structured-logging.md`
4. `docs/client-development/README.md`
5. `docs/client-development/02-websocket-protokoll.md`
6. `docs/client-development/06-http-api-und-authentifizierung.md`
7. `docs/client-development/07-robustheit-grenzen-und-sicherheit.md`
8. `docs/.archiv/neues_logging_event_system/2026-07-30_LOGGING_EVENT_SYSTEM.md`
9. `docs/.archiv/neues_logging_event_system/2026-08-01_logging-projekt-live-stand.md`
10. `docs/.archiv/neues_logging_event_system/2026-08-01_NEUES_LOGGING_EVENT_SYSTEM_ABWEICHUNGEN.md`
11. `VoiceSTT_server/event_logging.py`
12. die relevanten Abschnitte aus `api_fastapi_server/server.py`
13. die betroffenen Tests in:
    - `tests/unit/test_server_operations.py`
    - `tests/unit/test_fastapi_server_multi_user.py`
    - `tests/unit/test_openai_compatible_endpoint.py`

Prüfe außerdem mit `rg` sämtliche Aufrufstellen von:

- `StructuredEventHub.emit`,
- `events.emit`,
- `ChannelLogManager.event`,
- `subscribe`, `subscribe_async`,
- `latest_cursor`, `query`, `flush`, `close`,
- `log.gap`, `storage.failed`,
- `logAccess`, `/ws/logs`, `afterCursor`,
- `transcription.completed`, `transcription.cancelled` und leeren Finaltexten.

---

## 4. Dokumentationsprozess vor der Implementierung

Der Umbau ändert Architektur, öffentliches Protokoll und Fehlersemantik. Deshalb ist der Prozess aus `docs/.archiv/README.md` verpflichtend.

Vor der ersten Codeänderung:

1. Ergänze im Register `docs/.archiv/README.md` eine neue Aktion mit Status `Geplant`.
2. Lege einen neuen Ordner an, beispielsweise:

   ```text
   docs/.archiv/sqlite_first_eventstream/
   ```

3. Lege darin eine datierte Gesamtplanung an:

   ```text
   YYYY-MM-DD_SQLITE_FIRST_EVENTSTREAM_PLAN.md
   ```

4. Übernimm in diese Planung mindestens Ziel, Nicht-Ziele, feste Entscheidungen, aktuelle Implementierungsanalyse, Protokolländerungen, Risiken, Umsetzungsschritte, Tests und Abnahmekriterien aus diesem Auftrag.
5. Setze den Registerstatus beim tatsächlichen Implementierungsbeginn auf `In Umsetzung`.

Der abgeschlossene Ordner `docs/.archiv/neues_logging_event_system/` wird nicht rückwirkend umgeschrieben.

---

## 5. Aktueller Implementierungsstand und konkret zu ersetzendes Verhalten

### 5.1 `StructuredEventHub.emit()`

Aktuell in `VoiceSTT_server/event_logging.py`:

- vergibt `_next_cursor()` vor der Persistenz,
- erzeugt den vollständigen Envelope,
- ermittelt unabhängig die Ziele `store`, `file`, `stdout` und `publish`,
- legt dasselbe Payload parallel in voneinander unabhängige Queues,
- kann pro Sink Events verwerfen,
- kann ein Event live publizieren, obwohl der Store-Write später fehlschlägt.

Dieses Verhalten ist der Kern des Umbaus.

### 5.2 `SQLiteEventStore.append()`

Der Store:

- arbeitet bereits mit WAL,
- serialisiert Zugriffe über `RLock`,
- vergibt bei fehlendem Cursor einen monotonen Wert,
- schreibt Envelope und indizierte Kontextfelder,
- committet pro Append,
- liefert den Cursor zurück.

Diese Komponente ist als Grundlage geeignet. Die Cursorvergabe wird vollständig beim erfolgreichen Store-Commit konzentriert.

### 5.3 Aktuelle Sink-Queues

Der Hub besitzt derzeit Queue und Worker für:

- `store`,
- `file`,
- `stdout`,
- `publish`,
- zusätzlich eine Control-Queue.

Nach dem Umbau darf es keine unabhängige Store- und Publish-Reihenfolge mehr geben.

### 5.4 Aktueller `/ws/logs`-Handler

Der Handler in `api_fastapi_server/server.py`:

- registriert einen Live-Subscriber,
- erfasst `latest_cursor`,
- replayt SQLite bis zu diesem Wasserstand,
- verarbeitet danach Payloads aus einer Subscriber-Queue,
- kann Subscriber-Drops als `log.gap` melden.

Der neue Handler verwendet die Subscriberbenachrichtigung nur als Wakeup und liest committed Events anschließend immer aus SQLite.

### 5.5 Aktuelle Konfigurationsabhängigkeiten

Relevant sind insbesondere:

- `event_store_enabled`,
- `event_store_path`,
- `event_log_queue_size`,
- `log_live_enabled`,
- `transcription_logging_enabled`,
- `performance_logging_enabled`,
- `system_event_logging_enabled`,
- `request_logging_enabled`,
- `realtime_log_detail`,
- `transcript_log_mode`.

Der aktuelle Server erlaubt `log_live_enabled=true` bei deaktiviertem Store. Das ist mit dem neuen Vertrag nicht zulässig.

### 5.6 Aktueller Empty-Final-Randfall

In der Textschleife wird:

```python
text = (text or "").strip()
if not text:
    continue
```

ausgeführt. Dadurch entstehen weder ein Finaltext noch ein terminales strukturiertes Event. Dieser Pfad wird im Auftrag geschlossen.

---

## 6. Zielarchitektur im Server

```text
HTTP / WebSocket / Recorder / Scheduler / Lifecycle
                         │
                         ▼
              StructuredEventHub.emit()
                         │
             Redaction und Envelopebasis
                         │
                         ▼
               SQLiteEventStore.append()
                 Cursor + COMMIT erfolgreich
                         │
              ┌──────────┴───────────┐
              ▼                      ▼
     Commit-Wakeup/Store-Tail   optionale Spiegel
              │                 JSONL / stdout
              ▼
          /ws/logs
       Replay und Live-Tail
       aus derselben SQLite-Tabelle
```

Wesentliche Eigenschaft:

```text
Jedes gesendete log.event
    == ein bereits gespeicherter SQLite-Datensatz
```

---

## 7. Konkrete Änderungen in `VoiceSTT_server/event_logging.py`

### 7.1 Cursorvergabe aus dem Hub entfernen

Entferne beziehungsweise ersetze:

- `_cursor` als unabhängige In-Memory-Wahrheit,
- `_cursor_lock`, soweit danach nicht mehr benötigt,
- `_next_cursor()`.

Der Cursor wird erst im SQLite-Append festgelegt. `StructuredEventHub.latest_cursor()` fragt den Store ab und darf keinen höheren, ausschließlich im Speicher vergebenen Wert liefern.

Bei Serverneustart setzt sich der Cursor wie bisher aus dem SQLite-High-Watermark fort.

### 7.2 `SQLiteEventStore.append()` atomar und eindeutig machen

Passe `append()` so an, dass:

1. unter dem vorhandenen Storelock der nächste Cursor ermittelt wird,
2. eine neue Payloadkopie mit genau diesem Cursor entsteht,
3. Metadaten und `payload_json` denselben Cursor enthalten,
4. der Insert committed wird,
5. erst danach die committed Payload oder mindestens der committed Cursor zurückgegeben wird.

Bevorzugt wird die Rückgabe der committed Payload, damit der Hub keine zweite potenziell abweichende Envelopekopie aufbaut.

Ein fehlgeschlagener Insert darf:

- den Cursor nicht als erfolgreich veröffentlichen,
- keinen normalen Liveversand auslösen,
- keinen Cursor ausschließlich im Hub vorziehen.

Die bestehende High-Watermark-Logik über Tabelle und `sqlite_sequence` bleibt erhalten, damit durch Retention gelöschte Cursor nicht wiederverwendet werden.

### 7.3 `StructuredEventHub.emit()` auf Store-first umstellen

Der neue Ablauf ist verbindlich:

1. Channel- und Detailentscheidung prüfen.
2. Felder zentral redigieren.
3. `eventId`, Zeitstempel, Channel, Eventname, Severity, Instanz-ID und Kontextfelder aufbauen.
4. Noch keinen extern sichtbaren Cursor im Hub vergeben.
5. Payload synchron über `SQLiteEventStore.append()` committen.
6. Bei Erfolg die committed Payload verwenden.
7. Commit-Wakeup für Live-Subscriber signalisieren.
8. Erst danach JSONL- und stdout-Spiegel enqueuen.
9. `eventId` wie bisher zurückgeben.

Die SQLite-Arbeit findet damit bewusst im Emit-Pfad statt. Das Eventaufkommen enthält keine Audiopakete; Realtime-Detailmengen werden über `realtime_log_detail` gesteuert. Miss die Auswirkungen durch Tests und dokumentiere eine nachweisbare problematische Latenz, statt vorsorglich wieder einen parallelen Store-/Publish-Fan-out einzuführen.

### 7.4 Store muss für Livezugriff vorhanden sein

Wenn kein Store vorhanden ist:

- darf kein `/ws/logs`-Livevertrag mit `deliveryMode=sqlite_first` angeboten werden,
- darf die History-API nicht so tun, als sei Replay verfügbar,
- muss `hello.logAccess` den Zugriff als nicht verfügbar kennzeichnen oder weglassen,
- müssen Konfiguration und Health den Grund sichtbar machen.

Validiere mindestens:

```text
log_live_enabled=true
    erfordert event_store_enabled=true
```

Da der Client serverseitige Feedbackevents aus dem Transkriptionschannel erwartet, gilt für den vorgesehenen Produktivmodus zusätzlich:

```text
log_live_enabled=true
    erfordert transcription_logging_enabled=true
```

Bestehende reine Prozesslogs bleiben unabhängig davon möglich.

### 7.5 Commit-Wakeup statt Payload-Publish-Queue

Ersetze die Publish-Payload-Queue durch eine leichte Commit-Benachrichtigung.

Anforderungen:

- Subscriber werden nur darüber informiert, dass der Store einen neuen High-Watermark besitzt.
- Mehrere Wakeups dürfen zusammenfallen.
- Ein verlorener beziehungsweise zusammengefasster Wakeup verliert kein Event.
- Jeder Handler liest anhand seines eigenen Scan-Cursors aus SQLite nach.
- Ein periodischer Keepalive-/Timeoutdurchlauf prüft den Store ebenfalls, sodass selbst ein verpasster Wakeup korrigiert wird.

Eine mögliche interne Oberfläche ist:

```text
subscribe_commits(loop, asyncio_event)
unsubscribe_commits(subscription_id)
notify_committed(cursor)
```

Die genaue private Benennung darf an den vorhandenen Stil angepasst werden. Die externe Semantik ist festgelegt.

### 7.6 Optionale Spiegel erst nach Commit

JSONL und stdout erhalten nur committed Payloads mit finalem Cursor.

Ein Fehler oder Queueüberlauf eines Spiegels:

- darf den SQLite-Datensatz nicht beeinflussen,
- darf keinen Replay-Gap behaupten,
- darf als Spiegel-/Diagnosefehler gezählt und protokolliert werden,
- darf gegebenenfalls ein persistiertes, gedrosseltes Systemevent erzeugen,
- darf keine Rekursion gegen denselben fehlgeschlagenen Spiegel auslösen.

Passe `drop_counts()` und die Tests so an, dass zwischen kanonischem Store und optionalen Spiegeln klar unterschieden wird.

### 7.7 Storefehlerzustand

Führe im Hub einen thread-sicheren Zustand für die Eventstore-Verfügbarkeit ein, mindestens:

```text
ready
degraded
closed
```

Erfasse außerdem:

- letzten Fehlerzeitpunkt,
- bereinigte Fehlerbeschreibung ohne Secrets,
- optional Zahl fehlgeschlagener Commits.

Bei Append-Fehler:

1. keine normale Publish-/Spiegelweitergabe dieses Events,
2. Zustand `degraded`,
3. Prozesslogger mit gedrosselter Fehlermeldung,
4. nicht persistente Protokollkontrollmeldung an aktive Log-WebSockets,
5. kontrolliertes Schließen dieser WebSockets mit Code 1011,
6. kein rekursives `emit("system", "storage.failed")` über denselben kaputten Store.

Ein später erfolgreicher Commit darf den Zustand wieder auf `ready` setzen. Dokumentiere, dass Ereignisse, die während eines bestätigten Storeausfalls nicht committed werden konnten, nicht replaybar sind und der Client den expliziten Degradationszeitraum sichtbar halten muss.

### 7.8 `query()`, `latest_cursor()`, `flush()` und `close()`

Passe den Lifecycle an die neue Struktur an:

- `query()` liest direkt aus dem Store; es gibt keine vorgelagerte Storequeue mehr zu joinen.
- `latest_cursor()` liefert den committed SQLite-High-Watermark.
- `flush()` wartet nur auf tatsächlich verbliebene Spiegelqueues und Controlarbeiten.
- `close()` verhindert neue Emits, leert Spiegel kontrolliert, beendet Wakeups/Subscriber und schließt danach SQLite.
- Shutdown bleibt idempotent und darf keine Worker verlieren.

### 7.9 Ältesten verfügbaren Cursor bereitstellen

Ergänze im Store eine Abfrage des ältesten noch verfügbaren Cursors. Retention kann alte Datensätze entfernen; ein Client muss erkennen können, wenn sein `afterCursor` älter als die noch vorhandene Historie ist.

Mindestens erforderlich:

- `oldest_cursor()` im Store/Hub,
- `oldestCursor` in `log.hello`,
- `oldestCursor` in History-Antworten,
- eine explizite `log.gap`-Kontrollmeldung mit Ursache `retention`, wenn der angeforderte Cursor nachweislich vor der verfügbaren Storehistorie liegt.

Cursor-Sprünge innerhalb eines gefilterten Sessionstreams sind weiterhin normal und dürfen nicht als Gap interpretiert werden.

---

## 8. Konkrete Änderungen am `/ws/logs`-Handler

### 8.1 Handshake

Behalte Authentifizierung und Scoping bei:

- erste Nachricht muss `subscribe` sein,
- Sessiontoken bleibt auf genau eine Session begrenzt,
- Adminzugriff darf global filtern,
- Tokens stehen nicht in der URL.

Ergänze `log.hello` mindestens um:

```json
{
  "type": "log.hello",
  "schemaVersion": 1,
  "logProtocolVersion": 2,
  "deliveryMode": "sqlite_first",
  "replayAvailable": true,
  "serverInstanceId": "...",
  "oldestCursor": 1,
  "latestCursor": 1234
}
```

### 8.2 Lückenloser Replay-/Live-Übergang

Verwende folgenden Ablauf:

1. Commit-Wakeup abonnieren.
2. Committed `latestCursor` als Replay-Wasserstand erfassen.
3. `log.hello` und `log.subscribed` senden.
4. SQLite seitenweise für `(afterCursor, replayWatermark]` abfragen.
5. Replayevents mit `replay: true` senden.
6. `log.replay_completed` mit dem Wasserstand senden.
7. Eigenen globalen Scan-Cursor auf den Replay-Wasserstand setzen.
8. Bei Commit-Wakeup oder spätestens beim Keepalive neuen committed High-Watermark lesen.
9. SQLite für `(scanCursor, newWatermark]` abfragen.
10. passende Events mit `replay: false` senden.
11. Scan-Cursor auch dann auf den globalen Wasserstand setzen, wenn Filter keine eigenen Events ergaben.

Damit sind globale Cursorsprünge durch andere Sessions oder Channels korrekt.

### 8.3 Keine Payloadabhängigkeit vom Wakeup

Die Wakeup-Nachricht enthält höchstens einen Wasserstand. Der Handler darf sich nicht darauf verlassen, dass jeder einzelne Cursor als Queuepayload angekommen ist.

Bei mehreren schnellen Commits genügt ein Wakeup:

```text
Wakeup
    → latest committed cursor lesen
    → alles seit eigenem scanCursor aus SQLite nachziehen
```

### 8.4 Storefehler

Bei degradiertem Store:

- neue `/ws/logs`-Verbindungen erhalten `log.error`,
- Fehlercode mindestens `event_store_unavailable`,
- Fehlertext enthält keine Interna oder Secrets,
- Verbindung wird mit 1011 geschlossen,
- bestehende Verbindungen werden ebenfalls informiert und geschlossen.

Kein `log.event` darf in diesem Zustand als durable/replaybar ausgegeben werden.

### 8.5 Cursorfehler

Definiere und teste:

- `afterCursor < 0`: wie bisher auf 0 normalisieren oder als Protokollfehler ablehnen; einheitlich dokumentieren,
- `afterCursor > latestCursor`: `log.error` mit Code `cursor_ahead` und kontrollierter Close oder explizite Resetaufforderung,
- `afterCursor` vor verfügbarer Retention: `log.gap` mit `reason: retention`, anschließend Replay ab ältestem verfügbaren Bereich,
- nicht fortlaufende gefilterte Cursor: zulässig.

### 8.6 Ping, Pong und Keepalive

Behalte:

- Client-Ping,
- `log.pong`,
- `serverTime`,
- Keepalive bei Leerlauf.

Die dort gemeldeten Cursor sind ausschließlich committed Cursor.

---

## 9. Änderungen an `hello.logAccess`, Konfiguration und Status

### 9.1 `hello.logAccess`

Wenn verfügbar, behalte die heutigen Felder und ergänze:

```json
{
  "available": true,
  "websocketPath": "/ws/logs",
  "historyPath": "/api/logs/events",
  "accessToken": "...",
  "sessionId": "...",
  "expiresAt": "...",
  "logProtocolVersion": 2,
  "deliveryMode": "sqlite_first",
  "replayAvailable": true
}
```

Wenn Store oder Livezugriff nicht verfügbar sind, darf kein scheinbar nutzbarer Tokenvertrag ausgegeben werden. Verwende entweder:

- `logAccess.available=false` mit maschinenlesbarem Grund,
- oder lasse `logAccess` aus und dokumentiere dies eindeutig.

Bevorzugt wird die explizite `available=false`-Form, weil Clients dadurch Konfigurationsfehler von älteren Serverversionen unterscheiden können.

### 9.2 Konfigurationsvalidierung

Ergänze eine klare Validierung:

```text
log_live_enabled=true && event_store_enabled=false
    → Konfigurationsfehler

log_live_enabled=true && transcription_logging_enabled=false
    → Konfigurationsfehler für den vorgesehenen Clientvertrag
```

Die Validierung muss gelten für:

- YAML/CLI beim Start,
- Runtime-Validierungsendpunkte,
- Runtimeupdates, soweit die Felder dort änderbar sind.

Ein Runtimeupdate darf den Store nicht inkonsistent unter einem aktiven Livevertrag deaktivieren.

### 9.3 Logging- und Health-Antworten

Ergänze in `/api/logging` beziehungsweise der passenden bestehenden Statusantwort mindestens:

- `deliveryMode: sqlite_first`,
- `logProtocolVersion: 2`,
- `eventStore.state`,
- `eventStore.oldestCursor`,
- `eventStore.latestCursor`,
- `replayAvailable`,
- bereinigte Information zum letzten Storefehler.

`/health` soll bei einem für den Produktivvertrag erforderlichen, aber degradierten Eventstore einen sichtbaren Teilzustand liefern. Entscheide anhand der bestehenden Healthsemantik, ob `ok` dadurch insgesamt false wird; dokumentiere die Entscheidung. Verberge den Ausfall nicht.

---

## 10. Terminales Event für leere Finalergebnisse

Ändere die Textschleife in `api_fastapi_server/server.py`.

Aktueller Pfad:

```text
recorder.text()
    → leer
    → continue
    → kein terminales Event
```

Zielpfad:

```text
recorder.text()
    → leer
    → Generation prüfen
    → Segment genau einmal finalisieren
    → transcription.discarded(reason=empty_final) emitten
    → Realtime-Summary gegebenenfalls sauber schließen
    → wartenden Sessionstatus veröffentlichen
    → kein leeres final-Textframe senden
```

Implementiere dafür eine kleine dedizierte Methode analog zu `_publish_final_text()`. Sie muss:

- Generationen beachten,
- `segment_state.final()` genau einmal aufrufen,
- Timeline-/Segmentdaten soweit vorhanden korrelieren,
- `transcriptionId` über die vorhandene `_transcription_id()`-Logik bilden,
- `transcription.discarded` im Transkriptionschannel erzeugen,
- Reason und relevante Dauer-/Enginefelder ohne Text aufnehmen,
- keinen neuen parallelen Segmentzähler einführen.

Ergänze `transcription.discarded` in:

- Eventkatalog,
- Kurzreferenz,
- Structured-Logging-Dokumentation,
- Cliententwicklungsdokumentation,
- Tests.

---

## 11. Zu ändernde beziehungsweise zu prüfende Dateien

Mindestens betroffen:

### Produktivcode

- `VoiceSTT_server/event_logging.py`
- `api_fastapi_server/server.py`
- gegebenenfalls `VoiceSTT_server/operations.py`, falls Kompatibilitätsfassaden angepasst werden müssen
- `config.yaml`

### Tests

- `tests/unit/test_server_operations.py`
- `tests/unit/test_fastapi_server_multi_user.py`
- `tests/unit/test_openai_compatible_endpoint.py`
- bei Bedarf eine neue fokussierte Testdatei für das Durable-Event-Protokoll

### Aktive Dokumentation

- `docs/structured-logging.md`
- `docs/client-development/README.md`
- `docs/client-development/02-websocket-protokoll.md`
- `docs/client-development/03-server-events-kurzreferenz.md`
- `docs/client-development/04-server-events-katalog-und-chronologie.md`
- `docs/client-development/06-http-api-und-authentifizierung.md`
- `docs/client-development/07-robustheit-grenzen-und-sicherheit.md`
- `docs/configuration.md`
- bei tatsächlicher Benutzer-/Betriebsänderung `README.md` und `RELEASE_NOTES.md`

### Aktionsdokumentation

- `docs/.archiv/README.md`
- neuer Ordner `docs/.archiv/sqlite_first_eventstream/`

Ändere keine fachfremden Engines oder Schedulerkomponenten ohne reproduzierbaren Bedarf.

---

## 12. Bestehende Tests, die fachlich ersetzt oder angepasst werden müssen

### 12.1 Storefehler-Test

Der heutige Test `test_event_hub_cursor_remains_unique_after_store_write_failure` erwartet, dass Events trotz Storefehler live ankommen und der fehlende Storecursor nur als Gap erscheint.

Diese Erwartung ist nach dem Umbau falsch.

Neue Erwartung:

- fehlgeschlagenes Event wird nicht normal publiziert,
- committed `latestCursor` steigt nicht durch den Fehlschlag,
- Hub wird degradiert,
- Subscriber erhält Storefehlerkontrollsignal,
- nach Wiederherstellung entstehen nur committed Cursor,
- keine Cursorduplikate oder ausschließlich im Speicher existierenden Cursor.

### 12.2 Überlast-Test

Der heutige Test `test_event_hub_overload_never_blocks_emit_and_reports_gap` prüft bewusst Best-Effort-Dateiverluste.

Ersetze beziehungsweise teile ihn:

- SQLite-first-Vertrag bleibt vollständig,
- ein langsamer JSONL-Spiegel darf committed Store/Replay nicht beschädigen,
- Spiegel-Drops werden als Spiegelproblem gezählt,
- der Client-Eventstrom meldet deswegen keinen History-Gap,
- Performanceeventmenge wird über `realtime_log_detail` begrenzt.

### 12.3 Persist-and-publish-Test

Erweitere `test_event_hub_persists_and_publishes_session_scoped_events` um die nachweisbare Reihenfolge:

- solange der Store-Commit blockiert, wird kein Eventsubscriber bedient,
- unmittelbar nach erfolgreichem Commit ist genau dasselbe `eventId`/Cursor-Paar in Store und Livepfad sichtbar.

---

## 13. Neue Pflichtprüfungen

### 13.1 Store-first-Reihenfolge

- Storeappend künstlich blockieren.
- Event in einem separaten Thread emitten.
- Vor Freigabe des Storeappends darf kein normales Subscriber-/WebSocketevent sichtbar sein.
- Nach Commit müssen Store und Live dasselbe Event enthalten.

### 13.2 Storefehler

- Append wirft einmalig und dauerhaft Fehler.
- Kein unpersistiertes `log.event` wird gesendet.
- Cursor steigt nicht bei fehlgeschlagenem Commit.
- Hubstatus wird degradiert.
- aktive Log-WebSockets erhalten `event_store_unavailable` und Close 1011.
- kein rekursiver Fehlersturm.
- Wiederherstellung wird getestet.

### 13.3 Live-Tail aus SQLite

- mehrere Events schnell committen, aber nur einen Wakeup auslösen.
- Client erhält alle passenden committed Events in Cursorreihenfolge.
- fremde Sessions und nicht abonnierte Channels bleiben ausgefiltert.
- global übersprungene Cursor werden nicht als Gap behandelt.

### 13.4 Replay-/Live-Race

- während eines mehrseitigen Replays weitere Events committen.
- jedes passende Event erscheint genau einmal.
- ältere Events tragen `replay: true`.
- nach dem Wasserstand committed Events tragen `replay: false`.
- kein Event zwischen Replay und Live geht verloren.

### 13.5 Langsamer oder getrennter Client

- Client trennt nach Cursor N.
- Server committed N+1 bis N+x.
- Reconnect mit `afterCursor=N` liefert alle passenden Events.
- eine langsame WebSocketausgabe verändert weder Store noch andere Sessions.

### 13.6 Mehr als 1000 Events

- bestehendes mehrseitiges Replay bleibt grün.
- zusätzlich Live-Tail nach dem Replay testen.

### 13.7 Retention und Cursor

- älteste Events werden kontrolliert entfernt.
- `oldestCursor` stimmt.
- zu alter Cursor erzeugt expliziten Retention-Gap.
- neue Cursor werden nicht wiederverwendet.

### 13.8 Konfigurationsvertrag

- Live ohne Store wird abgelehnt.
- Live ohne Transkriptionschannel wird abgelehnt.
- Runtimeupdate kann keine aktive inkonsistente Kombination erzeugen.
- `hello.logAccess` meldet Fähigkeiten korrekt.

### 13.9 Empty Final

- leeres beziehungsweise whitespace-only Recorderresultat.
- kein leeres `final`-Frame.
- genau ein `transcription.discarded`.
- korrekte Session-, Transkriptions- und Segment-IDs.
- Segmentzähler schreitet genau einmal weiter.
- wartender Status wird wiederhergestellt.
- kein zusätzliches `completed`/`failed`/`cancelled` für dasselbe Segment.

### 13.10 Datenschutz

- Store-first verändert Redaction nicht.
- Tokens, Authheader, Querystrings, Audio und unerlaubte Texte fehlen weiterhin in Store, Live, JSONL und stdout.
- Storefehlermeldungen enthalten keine Pfade oder Secrets, die für Sessionclients nicht vorgesehen sind.

### 13.11 Lifecycle

- `flush()` und `close()` bleiben idempotent.
- keine Worker- oder asyncio-Task-Leaks.
- Shutdown während Replay, Livewait und Storefehler endet kontrolliert.

---

## 14. Baseline und Testbefehle

Vor der ersten Codeänderung mindestens ausführen:

```powershell
.\.venv\Scripts\python.exe -m unittest -v `
  tests.unit.test_server_operations `
  tests.unit.test_fastapi_server_multi_user `
  tests.unit.test_openai_compatible_endpoint
```

Falls die vorhandene Umgebung Abhängigkeiten vermissen lässt, dokumentiere exakt den Importfehler. Verwende nicht still den globalen Python-Interpreter und installiere keine unnötigen Modellpakete.

Nach der Implementierung zuerst die fokussierten Tests, danach die vollständigen schnellen Unit-/Contract-Tests:

```powershell
.\.venv\Scripts\python.exe -m unittest -v `
  tests.unit.test_server_operations `
  tests.unit.test_fastapi_server_multi_user `
  tests.unit.test_openai_compatible_endpoint

.\.venv\Scripts\python.exe -m unittest discover -s tests\unit -p "test_*.py" -v

.\.venv\Scripts\python.exe -m compileall `
  VoiceSTT_server `
  api_fastapi_server `
  tests\unit
```

Führe Fehler iterativ bis zu grünen Tests zurück. Übersprungene Golden-/Realmodelltests getrennt ausweisen; sie ersetzen nicht die schnellen Contracttests.

### Zusätzlicher Last-/Latenznachweis

Ergänze einen deterministischen Test oder Benchmark mit mehreren Sessions und aktivem `realtime_log_detail=events`, der mindestens nachweist:

- keine fehlenden committed Event-IDs,
- monotone Cursor,
- vollständiges Replay,
- keine zusätzlichen Audio- oder Finaldrops gegenüber dem bestehenden Fake-Scheduler-Test,
- keine unkontrollierte Speicherzunahme,
- keine Deadlocks durch SQLite-Locks.

Dokumentiere gemessene Emit-/Commitlatenzen. Erfinde keinen Erfolg, wenn die synchrone SQLite-Persistenz nachweislich den Audio-/Transkriptionspfad unvertretbar beeinträchtigt. In diesem Fall stoppe, dokumentiere den konkreten Messbefund und schlage als eng begrenzte Abweichung einen einzelnen FIFO-Commitworker vor, bei dem Live und Spiegel trotzdem ausschließlich nach erfolgreichem Commit geweckt werden. Führe keinen parallelen Store-/Publish-Fan-out wieder ein.

---

## 15. Nicht-Ziele

Nicht Bestandteil dieses Pakets:

- Änderung des Audioformats oder `/ws/transcribe`-Paketformats,
- Umbau der ASR-Engines,
- neue Adminrollen,
- neue Clientimplementierung,
- Persistenz von Access Tokens,
- Exactly-once-Verarbeitung auf Clientseite,
- externe Datenbank statt SQLite,
- Kafka, Redis oder anderer zusätzlicher Broker,
- Änderung des Transkripttext-Datenschutzmodus außer notwendiger Dokumentationsanpassung,
- nachträgliches Umschreiben des abgeschlossenen alten Archivordners.

---

## 16. Abnahmekriterien

Das Paket ist erst abgeschlossen, wenn alle folgenden Punkte erfüllt sind:

1. Kein normales `/ws/logs`-Event wird vor seinem SQLite-Commit gesendet.
2. Live und Replay verwenden dasselbe gespeicherte `eventId`/Cursor-Paar.
3. Der Hub besitzt keine unabhängig vorauseilende Cursorwahrheit mehr.
4. Store- und Publish-Payloadqueues können nicht mehr gegeneinander auseinanderlaufen.
5. Zusammengefasste Commit-Wakeups verlieren keine Events.
6. Ein WebSocket-Reconnect ab letztem Cursor liefert alle noch gespeicherten Events.
7. Storeausfall erzeugt explizite Eventstream-Degradation und keine ungespeicherte Normalauslieferung.
8. JSONL-/stdout-Probleme beschädigen weder Store noch Replay.
9. `logProtocolVersion: 2`, `deliveryMode: sqlite_first` und Replayfähigkeit werden offengelegt.
10. Livezugriff ohne Eventstore ist nicht mehr als scheinbar zuverlässige Konfiguration möglich.
11. Leere Finalergebnisse erzeugen genau ein terminales `transcription.discarded`.
12. Authentifizierung, Sessionisolation und Redaction bleiben erhalten.
13. Gezielte Tests, vollständige schnelle Suite und `compileall` sind grün oder ein echter Umgebungsblocker ist präzise nachgewiesen.
14. Aktive Fach- und Clientdokumentation entspricht dem neuen Vertrag.
15. Archivplanung, Soll-/Ist-Vergleich und gegebenenfalls Abweichungsdatei sind angelegt.
16. Das Archivregister wird erst nach vollständiger Gegenprüfung auf `Abgeschlossen` gesetzt.

---

## 17. Dokumentarischer Abschluss

Nach der Implementierung:

1. Erstelle im neuen Aktionsordner:

   ```text
   YYYY-MM-DD_SQLITE_FIRST_EVENTSTREAM_UMSETZUNGSVERGLEICH.md
   ```

2. Prüfe darin jeden Planpunkt gegen Code, Tests und tatsächlich veröffentlichten Stand.
3. Erstelle bei jeder materiellen Abweichung zusätzlich:

   ```text
   YYYY-MM-DD_SQLITE_FIRST_EVENTSTREAM_ABWEICHUNGEN.md
   ```

4. Aktualisiere die aktive Fachdokumentation außerhalb des Archivs.
5. Prüfe alle Links.
6. Bei Deployment:
   - GitHub-Commit und Branch nachweisen,
   - laufendes Image/Containerstand prüfen,
   - `/health`, `/api/logging`, History und `/ws/logs` live prüfen,
   - Store-first-Reihenfolge anhand eines realen Events nachvollziehen,
   - keine Secrets oder Eventinhalte unnötig im Bericht ausgeben.
7. Setze den Registerstatus erst danach auf `Abgeschlossen`.

---

## 18. Erwartetes Abschlussformat des Agenten

Berichte am Ende knapp und überprüfbar:

1. welche Dateien geändert wurden,
2. wie der SQLite-first-Datenfluss jetzt funktioniert,
3. welche öffentlichen Protokollfelder hinzugekommen sind,
4. wie Storeausfall und Recovery behandelt werden,
5. wie der Empty-Final-Fall geschlossen wurde,
6. welche gezielten Tests mit welchem Ergebnis liefen,
7. Ergebnis der vollständigen Testsuite und von `compileall`,
8. welche manuellen oder produktiven Prüfungen noch offen sind,
9. welche Abweichungen dokumentiert wurden,
10. Pfade zu Planung, Soll-/Ist-Vergleich und aktiver Fachdokumentation.

Keine Fortsetzung mit einem weiteren Arbeitspaket ohne neuen Auftrag.
