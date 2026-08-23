# LOGGING_CANONICAL_SCHEMA_AND_STORAGE

Deckt Auftragsabschnitte **5, 7, 8, 9**.
Alle Aussagen am Produktivcode belegt. Keine Datenbank angelegt, kein Schema
ausgeführt, kein Produktcode geändert.

---

# 5. Canonical Record gegen reale Daten

## 5.1 Feldprüfung

| Feld | Typ | Pflicht/optional | Quelle | heute vorhanden | Empfehlung |
|---|---|---|---|---|---|
| `record_id` | `str` (uuid4 hex, 32) | **Pflicht** | Client, im Ingress erzeugt | nein | **speichern.** Lokale Identität jedes Records, unabhängig vom Produzenten. `uuid4().hex` wie überall sonst im Projekt (`history.py:429`, `stt_session.py:764`, serverseitig `event_logging.py:953`). |
| `source_timestamp` | `str` ISO-8601 UTC mit `Z` | optional | Server: `EventEnvelope.timestamp` (`event_models.py:143-147`, Format `2026-07-30T14:26:41.537Z`). Python-Log: `LogRecord.created` (float, Epoch). Client-Events: `datetime.now(timezone.utc)` | teilweise | **speichern**, einheitlich als ISO-8601-UTC-Text. Für Python-Logs aus `record.created` konvertieren. Sortierung erfolgt trotzdem nie über dieses Feld allein (§5.3). |
| `received_at` | `str` ISO-8601 UTC | **Pflicht** | Ingress, `datetime.now(timezone.utc)` | nein | **speichern.** Einzige lokal vertrauenswürdige Wanduhrzeit. |
| `monotonic_ns` | `int` | **Pflicht** | `time.monotonic_ns()` im Ingress | nein | **nicht speichern.** Innerhalb eines Prozesses leistet die autoincrement-`id` der lokalen Tabelle dasselbe, prozessübergreifend ist `monotonic_ns` bedeutungslos (kein gemeinsamer Nullpunkt). Im **Speicher** für die Ordnung in Queue und Ringbuffer verwenden. |
| `producer_kind` | `str` Enum-artig: `client` \| `server` \| `led` \| `other` | **Pflicht** | Adapterkonstante; `led` über die `lefx.*`-Regel | nein | **speichern**, als TEXT. |
| `producer_id` | `str` | **Pflicht** | Konstanten `voice-stt-client`, `voice-stt-server`, `respeaker-led-controller` | nein | **speichern.** Teil des Dedupe-Index (§7). |
| `host` | `str` | optional | `socket.gethostname()` | nein, nirgends verwendet | **nicht speichern, Feld in V1 weglassen.** Auf einem Einzelplatz-Desktop ohne Aggregation hat es keinen Abfragewert, ist aber personenbezogen (§12). Wiedereinführbar, sobald Multi-Host-Aggregation kommt – dann als Spalte in der Migration. |
| `instance_id` | `str` | **Pflicht** | Client: `uuid4().hex`, einmal beim Start des Logging-Cores. Server: `EventEnvelope.server_instance_id` (`event_logging.py:700`, `uuid4().hex` **je Prozess**) | server ja, client nein | **speichern.** Beim Server wechselt der Wert bei jedem Neustart – genau das macht ihn diagnostisch wertvoll und ist der Grund für den vollständigen Replay (§7.3). |
| `process_id` | `int` | optional | `os.getpid()`, bei Python-Logs auch `LogRecord.process` | implizit ja | **nicht als Spalte.** Ein Desktop-Client hat einen Prozess je `instance_id`; die Information ist redundant. In `details` der `client.app.started`-Zeile aufnehmen. |
| `channel` | `str`, klein | **Pflicht** | Server: `EventEnvelope.channel`. Client: Adapter/Tabelle (§6 im Audit) | server ja | **speichern.** Werte `system` \| `audit` \| `transcription` \| `performance`. |
| `level` | `str` | **Pflicht** | Python: `record.levelname`. Server: `EventEnvelope.severity` (`info`/`warning`/`error`, `critical` vorgesehen) | ja | **speichern**, normalisiert auf `DEBUG`/`INFO`/`WARNING`/`ERROR`/`CRITICAL`. Unbekannte Severity → `INFO` **und** Originalwert nach `details.source_severity`. |
| `type` | `str` | optional | Server: `EventEnvelope.event` (z. B. `transcription.completed`). Client-Events: Konstante. Python-Logs: **keine** | teilweise | **speichern, nullable.** Ein reiner Python-Log hat keinen Eventtyp; ihn zu erfinden (etwa aus dem Loggernamen) würde eine Kategorie vortäuschen. |
| `component` | `str` | optional | Python: `record.name`. Client-Events: Modul-/Klassenname. Server: **kein direktes Äquivalent** | teilweise | **speichern, nullable.** Für Serverrecords aus dem Namensraumpräfix von `type` ableiten (`transcription.*` → `transcription`), nicht aus `transport`. |
| `session_id` | `str` | optional | Server: `EventEnvelope.session_id`. Client: `STTSession.state.session_id` bzw. `SessionContext.session_id` | ja | **speichern.** Zentraler Join-Schlüssel. |
| `generation` | `int` | optional | **Nur Client**: `STTSession.generation` (`stt_session.py:545`), `SessionContext.generation` | client ja, server **nein** | **speichern, nullable.** Der Server-Envelope trägt keine Clientgeneration. Serverrecords bekommen die Generation aus dem `SessionContext` zum Empfangszeitpunkt (der Hook aus Audit §2.4 liefert sie mit). |
| `activation_id` | `str` | optional | Server: **nicht** im Envelope-Kopf, sondern in `data.activationId` bzw. `extra` (via `_activation_correlation()`, `server.py:2973-2990`) | teilweise | **speichern, nullable, ausdrücklich als diagnostisch markieren.** `LETZTE_ARCHITEKTURKLAERUNGEN_...md §1.2` belegt: die Zuordnung ist zum Publikationszeitpunkt **nicht zuverlässig** (fehlt bei geschlossener Activation, ist bei bereits neu geöffneter Activation falsch). Das Feld darf nie als Wahrheit über die Zugehörigkeit gelten. |
| `segment_id` | `int` | optional | Server: `EventEnvelope.segment_id` (`int >= 0` oder `null`). Client: `final`-Event, `FinalProcessingResult.segment_id` | ja | **speichern.** Serverseitig in der Server-DB als TEXT abgelegt (`event_logging.py:571-575`), im Envelope aber als Integer validiert – clientseitig als INTEGER speichern. |
| `command_id` | `str` | optional | Client: `f"cmd-{uuid4().hex[:12]}"` (`stt_session.py:764`). Server: `trigger_ack.commandId` – aber **nur auf `/ws/transcribe`**, nicht auf `/ws/logs` | ja | **speichern, nullable.** |
| `event_id` | `str` | optional | Server: `EventEnvelope.event_id` (`uuid4().hex`, in der Server-DB `UNIQUE`, `event_logging.py:455`) | ja | **speichern.** Dedupe-Schlüssel (§7). Für Clientrecords immer `NULL`. |
| `correlation_id` | `str` | optional | Client-Feedbackpfad: `NormalizedFeedbackEvent.correlation_id`, bereits namensraumpräfigiert (`event_normalizer.py:282-301`, `controller.py:724`, `:2252`) | ja | **speichern.** Verbindliche Regel: immer `"<namensraum>:<wert>"`, z. B. `trigger:cmd-…`, `injection:<entryId>:…`, `transcription:<transcriptionId>`. |
| `transcription_id` | `str` | optional | Server: `EventEnvelope.transcription_id`, Format `"<sessionId>:<generation>:<segmentId>"` (`structured-logging.md:31`) | ja | **HINZUFÜGEN und speichern.** Begründung unten (§5.2). |
| `scope` | `str`: `session` \| `instance` \| `global` | **Pflicht** | abgeleitet | nein | **speichern.** Nicht ableitbar: ein Serverrecord ohne `session_id` ist `global`, ein Clientrecord ohne `session_id` ist `instance`. Eine Ableitung aus `session_id IS NULL` wäre mehrdeutig. |
| `message` | `str` | optional | Python: `record.getMessage()`. Server: **`extra["meldung"]`** (Befund C-2 im Audit). Client-Events: gerendert | teilweise | **speichern, nullable.** Ausdrücklich als Darstellung markiert. Nie zurückparsen (Zielbild §10). |
| `details` | JSON-Objekt | optional | strukturierte Zusatzfelder; Server: `EventEnvelope.data` | teilweise | **speichern als `details_json TEXT`.** |
| `raw` | JSON-Objekt | optional | Server: `EventProtocolResult.payload` (vollständiges `log.event`-Frame, eingefroren, `event_protocol.py:129`) | ja | **speichern als `raw_json TEXT`, konfigurierbar** über `store_raw_payload`. Nur für **eingehende** Serverevents (Regel R-6 im Audit). |
| `replayed` | `bool` | **Pflicht** | `EventProtocolResult.origin is EventOrigin.REPLAY` bzw. das `replay`-Bool des Frames (`event_protocol.py:389`) | ja | **speichern als INTEGER 0/1.** |

## 5.2 Antworten auf die ausdrücklichen Zusatzfragen

**Brauchen wir `sequence`?** Nein. Die lokale Einfügereihenfolge wird durch
`id INTEGER PRIMARY KEY AUTOINCREMENT` der Logtabelle exakt abgebildet, und
`monotonic_ns` sichert innerhalb des Prozesses die Ordnung vor dem Schreiben.
Ein drittes Ordnungsfeld hätte keine eigene Bedeutung. Für Serverrecords ist
der `cursor` bereits die serverseitige Sequenz – siehe unten.

**Brauchen wir `server_cursor`?** *Diese Frage stellt der Auftrag nicht, sie
folgt aber aus dem Code:* **ja.** `EventEnvelope.cursor` ist die einzige streng
monotone, retentionsfeste Ordnung der Serverereignisse
(`structured-logging.md:41-50`) und der einzige Weg, eine Lücke von einer
Filterlücke zu unterscheiden. Ohne diese Spalte lässt sich die Serverhistorie
lokal nicht rekonstruieren. Empfehlung: Spalte `server_cursor INTEGER NULL`.

**Brauchen wir `schema_version`?** Ja, aber **nicht je Record**.
- In SQLite: `PRAGMA user_version` plus eine Tabelle `schema_meta`. Eine Spalte
  je Zeile wäre 100 % redundant, weil eine Migration ohnehin alle Zeilen in die
  neue Form bringt.
- In den Datei-Sinks (JSONL): **ja, je Zeile**, weil eine JSONL-Datei ohne
  Kontext gelesen wird. Feld `schemaVersion` als erstes Element der Zeile.

**Brauchen wir `provider` / `source_record_id`?** In V1 **nein** als Spalte.
`event_id` identifiziert Serverrecords bereits eindeutig, `record_id` alle
lokalen. Sobald ein `ServerHistoryProvider` existiert, liefert er Records, die
gar nicht in der lokalen DB stehen; dort gehört `provider_id` an das **DTO**
(`LogRecordView.provider_id`, siehe `LOGGING_QUERY_UI_ADMIN_BOUNDARIES.md §15`),
nicht in die Tabelle. Eine Spalte hätte für jede lokal gespeicherte Zeile immer
denselben Wert.

**Brauchen wir separate `server_event_id` und lokale `record_id`?** **Ja, beide,
so wie im Entwurf.** Belege: `record_id` entsteht lokal und existiert auch für
Records ohne Serverherkunft; `event_id` entsteht auf dem Server und ist der
einzige replay-stabile Schlüssel. Die Felder haben unterschiedliche
Lebensdauer, unterschiedliche Autorität und unterschiedliche Eindeutigkeit.
Sie zusammenzulegen würde entweder Clientrecords ohne Identität lassen oder das
Dedupe zerstören.

**Ist `host` sinnvoll oder reicht `instance_id`?** `instance_id` reicht für V1.
Siehe Tabelle. Konkreter Grund gegen `host`: der Windows-Rechnername ist auf
Arbeitsplatzrechnern regelmäßig `VORNAME-PC` und damit ein personenbezogenes
Datum ohne Abfragenutzen, solange nur eine Maschine schreibt.

**Wie sollen Enum-Werte versioniert werden?**
```text
1. Alle Enum-artigen Felder werden als TEXT gespeichert, niemals als Integer-Code.
   Ein numerischer Code erzwingt eine Migration bei jedem neuen Wert.
2. Der Normalizer akzeptiert unbekannte Werte und speichert sie unverändert.
   Beleg für die Notwendigkeit: `severity` ist serverseitig kein geschlossenes
   Enum (Audit C-3), `EventEnvelope.event` ist offen, und `SessionState`
   des Clients hat bereits einen bewussten Vorwärtskompatibilitätspfad
   (`stt_session.py:68-75`, `UNKNOWN` statt Ausnahme).
3. NUR `level` wird auf eine geschlossene Menge abgebildet, weil Filter und
   Priorisierung darauf beruhen. Der Originalwert bleibt in
   `details.source_severity` erhalten.
4. `schema_version` gilt für die Spaltenstruktur, nicht für Wertemengen.
   Ein neuer `channel` oder ein neuer `type` löst KEINE Migration aus.
```

## 5.3 Zeitmodell – Konsequenz aus dem Code

`EventStreamTransport`/`EventProtocolProcessor` garantieren die Reihenfolge
über `cursor`, nicht über Zeitstempel (`event_protocol.py:420-422`). Der
Client-Prozess und der Server-Prozess haben keine gemeinsame Uhr. Verbindliche
Regel für Speicherung und Anzeige:

```text
Sortierung der lokalen Historie   ->  logs.id            (lokale Einfügeordnung)
Sortierung innerhalb Server-Fakten ->  server_cursor
Anzeige/Filter „Zeitbereich"      ->  received_at        (lokale Wanduhr)
Diagnose Zeitversatz               ->  source_timestamp - received_at
NIEMALS                            ->  source_timestamp als Primärsortierung
```

---

# 7. Replay / Dedupe – technische Klärung

## 7.1 Ermittelte Eigenschaften des realen Mechanismus

| Frage | Befund | Beleg |
|---|---|---|
| Event-ID-Format | `uuid.uuid4().hex`, 32 Hexzeichen | `event_logging.py:953` |
| Eindeutigkeit | `event_id TEXT NOT NULL UNIQUE` in der kanonischen Server-SQLite | `event_logging.py:455` |
| Cursor-Format | `cursor INTEGER PRIMARY KEY AUTOINCREMENT`, streng steigend, überlebt Retention-Löschungen | `event_logging.py:454`, `:590-602`, `structured-logging.md:41-50` |
| Lebensdauer | so lange die Zeile in der Server-DB steht; Retention wird **pro Channel** in Tagen konfiguriert, Default `0` = kein automatisches Löschen | `event_logging.py:496-540`, `structured-logging.md:104-112` |
| Serverneustart | `server_instance_id = uuid4().hex` wird **je Prozess neu erzeugt**; die SQLite-Datei bleibt bestehen, die Cursor laufen weiter | `event_logging.py:700` |
| Cursor-Persistenz im Client | atomar (`Tempfile` + `fsync` + `os.replace`), gebunden an `(endpoint, server_instance_id, protocol_version)` | `event_cursor_store.py:89-131` |
| Verhalten nach Serverneustart | Der gespeicherte Cursor wird **verworfen**, weil `server_instance_id` nicht mehr passt → `resume_cursor = 0` → der Server liefert **die gesamte verbliebene Historie** der abonnierten Channels als Replay | `event_cursor_store.py:72-79`, `event_protocol.py:228-239` |
| Replaygrenzen | `log.gap(reason=retention)` meldet gelöschte Bereiche; `log.error(code=cursor_ahead)` meldet einen Cursor oberhalb der Hochwassermarke | `event_protocol.py:454-475`, `:492-495` |
| Vorhandene Dedupe im Client | `EventProtocolProcessor._confirmed_ids`, `OrderedDict`, harte Grenze **2048** (`dedupe_limit`), Duplikate gehen an `on_control` statt `on_event` | `event_protocol.py:182-190`, `:304-306`, `:404-417` |
| Lebensdauer dieser Dedupe | überlebt Reconnects innerhalb desselben `EventStreamAccess` (`begin_subscription` leert `_confirmed_ids` **nicht**), wird bei `reconfigure` geleert und existiert **nicht** über Prozessneustarts | `event_protocol.py:215-221`, `:222-239` |

## 7.2 Warum Dedupe in der Persistenz zwingend ist

Der oft angenommene Fall „ein paar Events doppelt nach kurzem Reconnect" ist
nicht der kritische. Kritisch ist:

```text
Serverprozess startet neu (Deploy, Absturz, Docker-Restart)
  -> neue server_instance_id
  -> Clientcursor passt nicht mehr (event_cursor_store.py:72-79)
  -> resume_cursor = 0
  -> Server replayt ALLES, was in audit+performance+transcription
     noch nicht durch Retention gelöscht ist
  -> Bei Default-Retention 0 (= nie löschen) ist das die vollständige
     Historie der Serverdatenbank.

Die vorhandene In-Memory-Dedupe von 2048 Einträgen fängt das nicht ab.
Ein Clientneustart hebt sie ohnehin vollständig auf.
```

## 7.3 Ergebnis

```text
EMPFOHLENER DEDUPE KEY:

    (producer_id, event_id)

    Umgesetzt als partieller eindeutiger Index auf der lokalen Logtabelle:

        CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_producer_event
            ON logs (producer_id, event_id)
            WHERE event_id IS NOT NULL;

    Schreiben ausschließlich über

        INSERT INTO logs (...) VALUES (...)
        ON CONFLICT (producer_id, event_id) DO NOTHING;

    Für Records ohne event_id (alle Client- und LED-Records) greift der
    partielle Index nicht; ihre Eindeutigkeit ergibt sich daraus, dass
    record_id genau einmal erzeugt wird.

GARANTIEN:

  * event_id ist uuid4 und serverseitig zusätzlich UNIQUE constrained
    (event_logging.py:455). Zwei verschiedene Ereignisse können denselben
    Schlüssel praktisch nicht tragen.
  * Der Schlüssel ist unabhängig von cursor, server_instance_id, Retention
    und Verbindungsgeneration. Er überlebt Serverneustart, Clientneustart,
    Wechsel des Endpoints und einen Wechsel der Server-Instanz.
  * producer_id im Index schützt gegen einen künftigen zweiten Produzenten
    mit eigenem, nicht-uuid-basiertem ID-Schema, ohne heute etwas zu kosten.
  * `replayed` bleibt diagnostisch erhalten: die ERSTE gespeicherte Fassung
    gewinnt. Kommt ein Event zuerst live und später als Replay, bleibt
    replayed=0 -- das ist die gewünschte Aussage „lokal live empfangen".
  * ON CONFLICT DO NOTHING ist in einem Batch-INSERT verlustfrei und
    erfordert kein vorheriges SELECT. Genau dieses Muster wird im Repository
    bereits verwendet (history.py:354-366).

GRENZEN:

  1. Die Dedupe wirkt nur auf der PERSISTENZ. Der Live-Ringbuffer und die
     UI sehen replayte Records ein weiteres Mal; sie sind über `replayed`
     erkennbar und dürfen dort bewusst erscheinen.
  2. Zwei Serverinstanzen HINTER demselben Endpoint (Loadbalancer, Blue/Green)
     erzeugen unabhängige uuid4-Räume. Keine Kollision, aber die lokale
     Historie enthält dann zwei Instanz-IDs -- gewollt und über instance_id
     filterbar.
  3. Wird die Server-SQLite gelöscht und neu angelegt, beginnen die Cursor
     wieder bei 1, die eventIds sind aber neu. Die lokale Historie enthält
     dann alte und neue Records mit überlappenden Cursorwerten. Deshalb darf
     server_cursor NIE ohne instance_id sortiert oder verglichen werden.
  4. `log.gap(reason=retention)` bedeutet endgültigen Datenverlust auf der
     Serverseite. Der Gap selbst wird als eigener Record gespeichert
     (type=`client.eventstream.gap`), damit die Lücke in der lokalen Historie
     sichtbar bleibt statt stillschweigend zu fehlen.
  5. Eine Fehlkonfiguration, bei der zwei Clientinstanzen dieselbe lokale
     DB beschreiben, ist durch `SingleInstanceGuard` (ui/single_instance.py)
     praktisch ausgeschlossen; der Dedupe-Index würde sie zusätzlich
     abfangen, aber die Zähler wären dann nicht mehr aussagekräftig.

FALLS KEINE STABILE GLOBALE ID EXISTIERTE (Alternative, hier NICHT nötig):

    Ersatzschlüssel (producer_id, instance_id, server_cursor). Er wäre
    schwächer, weil er bei einer neu angelegten Server-DB kollidiert
    (Grenze 3) und weil ein Event ohne Cursor -- Serverzustand
    „store degraded", event_logging.py:985 -- gar keinen Schlüssel hätte.
    Da event_id in JEDEM Envelope Pflichtfeld ist (event_models.py:184),
    tritt dieser Fall nicht ein.
```

---

# 8. Bestehende lokale Persistenzmuster

## 8.1 Was existiert

| Speicher | Datei | Pfad | Muster |
|---|---|---|---|
| Transkript-Historie | `core/history.py` | `%LOCALAPPDATA%\RealtimeSTT_Client\transcript_history.db` (`history.py:111-118`) oder `history.persistent.db_path` | SQLite, zwei Tabellen, kurzlebige Verbindungen |
| Eventcursor | `core/event_cursor_store.py` | `%LOCALAPPDATA%\RealtimeSTT Client\event_cursor.json` (`:19-23`) | JSON, atomarer Austausch |
| Benutzerkonfiguration | `core/config.py` | `%LOCALAPPDATA%\RealtimeSTT Client\config.yaml` (`:35-37`) | YAML, atomarer Austausch (`:972-995`) |
| Python-Logdatei | `core/logging_setup.py` | `%LOCALAPPDATA%\RealtimeSTT Client\logs\client.log` | RotatingFileHandler |
| LEFX-Hintergrundzustand | `ui/led_feedback.py:57-63` | `%LOCALAPPDATA%\RealtimeSTT Client\lefx\background_state.json` | von LEFX verwaltet |

**Befund D-1.** Zwei verschiedene Datenverzeichnisse: `RealtimeSTT Client`
(mit Leerzeichen, `config.py:33`) für Logs, Config, Cursor und LEFX –
`RealtimeSTT_Client` (mit Unterstrich, `history.py:115`) für die
Transkript-Historie. Der neue Store gehört in das Verzeichnis mit Leerzeichen,
weil dort bereits vier von fünf Artefakten liegen und `DEFAULT_LOCAL_APP_DIR`
die einzige zentral definierte Konstante ist. **Die bestehende Abweichung wird
nicht repariert** – das wäre eine Produktänderung außerhalb dieses Auftrags.

## 8.2 Bewertung der Muster

### Aus `EventCursorStore` übernehmen – gute Muster

| Muster | Beleg | Warum übernehmen |
|---|---|---|
| Explizites `schema_version` im Datensatz plus strikte Parseprüfung mit Ablehnung statt Reparatur | `:37-45`, `:162-194` | Macht ein Formatupgrade zu einem bewussten Vorgang statt zu einer stillen Fehlinterpretation |
| Atomarer Austausch: `NamedTemporaryFile` im Zielverzeichnis, `flush`, `os.fsync`, `os.replace`, Aufräumen im `finally` | `:110-131` | Für JSONL-Rotation und für Statusdateien direkt wiederverwendbar |
| `threading.RLock` um jeden Zugriff | `:50`, `:63`, `:110` | – |
| Bindung an `(endpoint, instance, protocol)` und Verwerfen bei Nichtübereinstimmung mit Logzeile | `:72-86` | Vorbild für den Umgang mit fremden/alten Daten |
| Ungültige Datei führt zu `return None`, nicht zu einer Ausnahme | `:69-71` | Failure-Isolation, genau das Verhalten, das der Logstore braucht |

### Aus `TranscriptHistoryManager` übernehmen – gute Muster

| Muster | Beleg |
|---|---|
| `INSERT ... ON CONFLICT(...) DO NOTHING` und danach die bestehende ID lesen | `:354-366` |
| Kontextmanager mit `commit`/`rollback`/`close` | `:127-144` |
| Fehler beim DB-Init deaktivieren die Persistenz (`_db_enabled = False`) statt die Anwendung zu stoppen | `:174-178` |
| Cleanup ist ausdrücklich „best effort" und darf nicht durchschlagen | `:369-372`, `:589-590` |

### Aus `TranscriptHistoryManager` NICHT übernehmen

| Antimuster | Beleg | Warum nicht |
|---|---|---|
| Neue `sqlite3.connect()` **pro Operation** | `:120-125`, aufgerufen in jeder Methode | Für einen Logstore mit Batchschreiben ist das der teuerste Teil des Vorgangs. Der Worker besitzt genau eine Verbindung. |
| Kein WAL, kein `busy_timeout` | `:120-125` | Ohne WAL blockiert jeder Leser (LogView) den Schreiber (Worker) und umgekehrt. |
| `cleanup()` **nach jedem Insert** | `:369-372` innerhalb `_save_to_db` | Bei Logvolumen wäre das ein `DELETE`-Scan je Record. Retention gehört auf ein Intervall. |
| `with self._get_connection() as conn:` in `_save_attempt_to_db` (`:381`) – der sqlite3-Kontextmanager committet, **schließt aber nicht** | `:381-385` | Verbindungsleck. Nicht kopieren. |
| Kein `schema_version`, keine Migrationstabelle | gesamte Datei | Ein Schemawechsel wäre nur über `CREATE TABLE IF NOT EXISTS` möglich, also gar nicht. |
| Deduplikationscache lädt **alle** `(session_id, segment_id)` beim Start in den Speicher (`_load_dedup_cache`, `:180-192`) | `:180-192` | Bei Logvolumen unmöglich. Dedupe gehört in den DB-Index (§7). |

## 8.3 Antworten auf die Prüffragen

| Frage | Empfehlung | Begründung am Code |
|---|---|---|
| SQLite connection per worker? | **Ja, genau eine, im Besitz des LoggingWorker-Threads.** `check_same_thread=False` **nicht** setzen – die Verbindung soll den Thread nie verlassen. Leser (LogQueryService) öffnen eigene, kurzlebige **read-only** Verbindungen (`file:...?mode=ro`, `uri=True`). | Es gibt nur einen Schreiber (§10). Zwei Rollen, zwei Verbindungen, keine gemeinsame. |
| WAL sinnvoll? | **Ja, zwingend.** `PRAGMA journal_mode=WAL`, `PRAGMA synchronous=NORMAL`. | Genau die Einstellung, die der Server für denselben Anwendungsfall verwendet (`event_logging.py:449-450`). Ohne WAL sperrt die LogView-Abfrage den Worker. |
| busy timeout? | **Ja**, `PRAGMA busy_timeout=5000` auf beiden Seiten. Serverseitig ist es `timeout=30.0` im `connect` (`event_logging.py:447`); 5 s reichen im Client, weil ein Blockieren des Workers folgenlos ist, ein Blockieren der UI aber nicht. | – |
| schema version? | **Ja**, `PRAGMA user_version` **plus** Tabelle `schema_meta(key,value)` für Nicht-Integer-Metadaten (erzeugende Clientversion, Erstellungszeitpunkt). | `user_version` allein trägt keine Diagnoseinformation. |
| Migrationstabelle? | **Nein.** Eine Liste nummerierter Migrationsschritte im Code, gesteuert über `user_version`; jeder Schritt läuft in einer eigenen Transaktion und erhöht `user_version`. Eine `migrations`-Tabelle wäre eine zweite Wahrheit neben `user_version`. | – |
| Batch insert? | **Ja**, `executemany` innerhalb **einer** Transaktion je Batch. | Ein Commit je Record ist bei WAL zwar billig, aber nicht bei 200 Records je Sekunde im Burst. |
| Cleanupstrategie? | Retention läuft im Worker, **nicht** nach jedem Batch, sondern: höchstens alle 60 s **und** höchstens alle 2000 geschriebenen Records; zusätzlich einmal beim Start. Immer in Blöcken (`LIMIT 5000` je `DELETE`), damit ein einzelnes `DELETE` den Worker nicht sekundenlang bindet. | Gegenmuster: `history.cleanup()` läuft nach jedem Insert (`:369-372`). |
| DB-Größenlimit? | **Ja, aber abgeleitet, nicht als Primärgrenze.** Primär: `retention_days` und `max_entries`. Zusätzlich eine weiche Obergrenze `max_db_bytes` (Default 256 MiB), geprüft im selben Intervall über `PRAGMA page_count * page_size`; bei Überschreitung wird `max_entries` für diesen Lauf gesenkt und ein `logging.retention_pressure`-Record erzeugt. `VACUUM` **nicht** automatisch (blockiert die Datei); stattdessen `PRAGMA auto_vacuum=INCREMENTAL` beim Anlegen und `PRAGMA incremental_vacuum(N)` im Retentionlauf. | `auto_vacuum` muss **vor** der ersten Tabelle gesetzt werden, sonst wirkt es nur nach einem vollen `VACUUM`. |

---

# 9. SQLite-Schema – Planungsentwurf

> Keine Datenbank angelegt. Das Folgende ist ein Entwurf für das später
> freigegebene Work Package.

## 9.1 DDL

```sql
-- Beim Anlegen einer NEUEN Datei, in dieser Reihenfolge:
PRAGMA auto_vacuum = INCREMENTAL;   -- muss vor der ersten Tabelle stehen
PRAGMA journal_mode = WAL;
PRAGMA synchronous  = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_meta (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);
-- Zeilen: created_at, created_by_version, last_migrated_at

CREATE TABLE IF NOT EXISTS logs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,  -- lokale Ordnung

    record_id         TEXT    NOT NULL,                   -- uuid4 hex, lokal
    received_at       TEXT    NOT NULL,                   -- ISO-8601 UTC, Z
    source_timestamp  TEXT,                               -- ISO-8601 UTC, Z

    producer_kind     TEXT    NOT NULL,                   -- client|server|led|other
    producer_id       TEXT    NOT NULL,
    instance_id       TEXT    NOT NULL,

    scope             TEXT    NOT NULL,                   -- session|instance|global
    channel           TEXT    NOT NULL,                   -- system|audit|transcription|performance
    level             TEXT    NOT NULL,                   -- DEBUG..CRITICAL
    type              TEXT,                               -- z. B. transcription.completed
    component         TEXT,                               -- Logger-/Modulname

    session_id        TEXT,
    generation        INTEGER,
    activation_id     TEXT,                               -- diagnostisch, nicht autoritativ
    segment_id        INTEGER,
    transcription_id  TEXT,
    command_id        TEXT,
    event_id          TEXT,                               -- Server-eventId, sonst NULL
    correlation_id    TEXT,                               -- "<namensraum>:<wert>"
    server_cursor     INTEGER,                            -- nur Serverrecords

    replayed          INTEGER NOT NULL DEFAULT 0,         -- 0/1

    message           TEXT,                               -- Darstellung, nie Datenquelle
    details_json      TEXT,                               -- JSON-Objekt oder NULL
    raw_json          TEXT                                -- JSON-Objekt oder NULL
);

-- Dedupe: nur fuer Records mit Server-eventId (§7)
CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_producer_event
    ON logs (producer_id, event_id)
    WHERE event_id IS NOT NULL;

-- Basisliste und Retention: eine Abfrage ohne Filter, neueste zuerst.
-- Wird ueber die PRIMARY KEY (id) bedient, KEIN eigener Index noetig.

-- Der eine breite Arbeitsindex fuer die Standardansicht.
-- Reihenfolge bewusst: erst die Dimension mit der hoechsten Selektivitaet
-- im Alltag (Session), dann die Sortierspalte.
CREATE INDEX IF NOT EXISTS ix_logs_session_id
    ON logs (session_id, id DESC)
    WHERE session_id IS NOT NULL;

-- Zeitbereichsfilter der UI.
CREATE INDEX IF NOT EXISTS ix_logs_received_at
    ON logs (received_at);

-- Die drei Dimensionen, die die Filterleiste kombiniert. Ein gemeinsamer
-- Index statt dreier einzelner: SQLite nutzt pro Tabelle nur einen Index
-- je Abfrage, drei einzelne waeren zwei davon totes Gewicht.
CREATE INDEX IF NOT EXISTS ix_logs_channel_level
    ON logs (channel, level, id DESC);

-- Kontextaktionen "nur diese Activation" / "nur dieses Segment".
CREATE INDEX IF NOT EXISTS ix_logs_activation
    ON logs (activation_id, id DESC)
    WHERE activation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_logs_correlation
    ON logs (correlation_id, id DESC)
    WHERE correlation_id IS NOT NULL;
```

## 9.2 Bewusst NICHT angelegte Indizes

| Kandidat aus dem Zielbildentwurf (§16) | Entscheidung | Begründung |
|---|---|---|
| `source_timestamp` | **nein** | Wird nie sortiert und nie gefiltert (§5.3). Der Zeitbereichsfilter arbeitet auf `received_at`. |
| `producer_kind` | **nein** | Vier Werte, davon in der Praxis zwei. Kardinalität zu gering; SQLite wählt ohnehin den Tabellenscan oder einen der breiteren Indizes. |
| `type` einzeln | **nein** | Der Freitext-/Typfilter ist in der Praxis immer mit `channel` oder `session_id` kombiniert. Wenn Messungen später das Gegenteil zeigen, ist ein Index eine einzeilige Migration. |
| `level` einzeln | **nein** | In `ix_logs_channel_level` enthalten. |
| `segment_id` | **nein** | Immer zusammen mit `session_id` gefiltert, wird von `ix_logs_session_id` bedient. |
| `event_id` einzeln | **nein** | Bereits im UNIQUE-Index enthalten. |
| `component` | **nein** | Wie `type`. |

**Regel:** Jeder Index kostet bei einem schreibintensiven Store Schreibzeit.
Sieben Indizes bei ~20 Spalten wären bereits mehr Index als Daten. Die obige
Auswahl deckt jede Abfrage ab, die die V1-Filterleiste erzeugen kann.

## 9.3 Repräsentation und Nullbarkeit

```text
Zeitstempel      TEXT, ISO-8601 UTC mit "Z", Millisekunden.
                 Begründung: identisch zum Serverformat
                 (structured-logging.md:26) und lexikografisch sortierbar.
                 KEIN Unix-Float -- das wäre ein zweites Format neben dem
                 Serverformat und würde bei jeder Anzeige konvertiert.

level/channel    TEXT, nie Integer (§5.2).
replayed         INTEGER 0/1 (SQLite hat kein BOOLEAN).
segment_id       INTEGER. Achtung: die Server-DB legt es als TEXT ab
                 (event_logging.py:571-575); der Client-Envelope validiert
                 es aber als int (event_models.py:167-173). Lokal INTEGER.
generation       INTEGER, NULL für Serverrecords ohne Kontextbezug.
details_json     TEXT, immer ein JSON-OBJEKT oder NULL, nie ein Skalar.
raw_json         TEXT, nur gesetzt wenn store_raw_payload aktiv UND der
                 Record ein eingehendes Serverevent ist.

NOT NULL sind ausschließlich:
    record_id, received_at, producer_kind, producer_id, instance_id,
    scope, channel, level, replayed
Alles andere ist nullable, weil jedes andere Feld für mindestens eine
reale Recordart nachweislich fehlt (Python-Log hat kein `type`,
Clientrecord hat kein `event_id`, Serverrecord hat kein `command_id`).
```

## 9.4 Migrationsstrategie

```text
user_version = 0   Datei existiert nicht / ist leer -> vollständiges Anlegen
user_version = 1   V1-Schema wie oben

MIGRATIONS = [ (1, _migrate_to_1), ... ]

Ablauf beim Start des Stores:
  1. Datei öffnen. Schlägt das fehl -> Store deaktiviert, Health = FAILED,
     Anwendung läuft weiter (Muster von history.py:174-178).
  2. `PRAGMA user_version` lesen.
  3. Ist die Version HÖHER als bekannt: Store im NUR-LESEN-Modus betreiben
     und Health = DEGRADED_STORE setzen. NICHT löschen, NICHT downgraden.
     Begründung: der Nutzer hat vielleicht nur eine ältere Version gestartet.
  4. Ist sie niedriger: die fehlenden Schritte nacheinander ausführen, jeder
     in einer eigenen Transaktion, danach `PRAGMA user_version = n`.
  5. Schlägt ein Schritt fehl: Rollback, Store deaktiviert, Health = FAILED,
     eine stderr-Zeile. Kein Abbruch der Anwendung.

Es wird NIE eine bestehende Logdatei gelöscht oder umbenannt. Der Store ist
Diagnosematerial; ihn im Fehlerfall wegzuwerfen wäre der schlechteste
denkbare Moment.
```

## 9.5 Retention-Query

```sql
-- 1. Alter, in Blöcken, damit ein einzelnes DELETE den Worker nicht bindet.
DELETE FROM logs
 WHERE id IN (
   SELECT id FROM logs
    WHERE received_at < :cutoff_iso
    ORDER BY id
    LIMIT 5000
 );
-- wiederholen, solange changes() = 5000 UND das Zeitbudget des Laufs reicht

-- 2. Anzahl. Untergrenze über die kleinste zu behaltende id ermitteln,
--    statt "NOT IN (SELECT ... LIMIT n)" wie in history.py:580-586.
--    Grund: das dortige Muster liest bei jedem Lauf die gesamte Tabelle.
SELECT id FROM logs ORDER BY id DESC LIMIT 1 OFFSET :max_entries - 1;
-- -> :floor_id
DELETE FROM logs WHERE id < :floor_id;

-- 3. Weiche Größengrenze
PRAGMA page_count;
PRAGMA page_size;
-- bei Überschreitung: :max_entries für diesen Lauf halbieren, Schritt 2
-- erneut, danach
PRAGMA incremental_vacuum(2000);
```

## 9.6 Pagination-Query (Keyset, nicht OFFSET)

```sql
-- Erste Seite
SELECT id, record_id, received_at, source_timestamp,
       producer_kind, producer_id, instance_id, scope,
       channel, level, type, component,
       session_id, generation, activation_id, segment_id,
       transcription_id, command_id, event_id, correlation_id,
       server_cursor, replayed, message, details_json
  FROM logs
 WHERE (:channels_is_empty OR channel IN (/* ... */))
   AND (:levels_is_empty   OR level   IN (/* ... */))
   AND (:producer_kind IS NULL OR producer_kind = :producer_kind)
   AND (:session_id    IS NULL OR session_id    = :session_id)
   AND (:activation_id IS NULL OR activation_id = :activation_id)
   AND (:segment_id    IS NULL OR segment_id    = :segment_id)
   AND (:correlation   IS NULL OR correlation_id = :correlation)
   AND (:type_prefix   IS NULL OR type LIKE :type_prefix || '%')
   AND (:from_iso      IS NULL OR received_at >= :from_iso)
   AND (:to_iso        IS NULL OR received_at <  :to_iso)
   AND (:text          IS NULL OR message LIKE '%' || :text || '%'
                               OR type    LIKE '%' || :text || '%'
                               OR component LIKE '%' || :text || '%')
 ORDER BY id DESC
 LIMIT :limit;

-- Folgeseite: der Cursor ist die id der letzten Zeile der vorigen Seite.
--   ... AND id < :after_id
-- ORDER BY id DESC LIMIT :limit;
```

```text
Warum Keyset und nicht OFFSET:
  * OFFSET n muss n Zeilen überspringen und wird auf einer wachsenden
    Tabelle mit jeder Seite langsamer.
  * Zwischen zwei Seitenabrufen schreibt der Worker weiter. Mit OFFSET
    verschieben sich alle Zeilen und die UI zeigt Duplikate oder Lücken.
    Mit `id < :after_id` ist die Seitenfolge stabil.
  * `raw_json` wird in der Listenabfrage NICHT geladen. Es ist das mit
    Abstand größte Feld und wird nur in der Detailansicht gebraucht --
    dort über einen gezielten `SELECT raw_json FROM logs WHERE id = ?`.
```

## 9.7 Ablageort

```text
Datei      %LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3
Ableitung  core.config.DEFAULT_LOCAL_APP_DIR / "observability.sqlite3"
Konfig     logging.observability.db_path (None = Standard)

Begründung: DEFAULT_LOCAL_APP_DIR (config.py:33) ist die einzige zentral
definierte Datenverzeichniskonstante und beherbergt bereits logs/,
config.yaml, event_cursor.json und lefx/. Der abweichende
Historienpfad (RealtimeSTT_Client, history.py:115) wird NICHT als Vorbild
genommen und im Rahmen dieses Vorhabens auch nicht angefasst (Befund D-1).

Der Name endet bewusst NICHT auf ".db", damit die Datei nicht mit
transcript_history.db verwechselt wird, und trägt die Endung, die auch
der Server verwendet (voicestt-events.sqlite3).
```
