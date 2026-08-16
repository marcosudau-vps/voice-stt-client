---
id: OBS-FREEZE-CONTRACTS
status: FROZEN
authority: normative
workstream: OBS
freeze_gate: OBS-000
run: RUN-OBS-000-01_2026-08-15_CLAUDE
last_updated: 2026-08-15
---

# Logging-/Observability-Verträge – FREEZE

> **Geltung.** Normativ ab `G-OBS-000 PASS`. Was hier steht, ist von einem
> Coding-Agenten **umzusetzen, nicht zu entscheiden**. Eine Abweichung
> erfordert `DECISION REQUIRED`.
>
> **Signaturen als Code.** Python-Blöcke sind verbindliche Sollzustände, keine
> Implementierung. Typannotationen, Feldnamen, Nullbarkeit und Rückgabewerte
> sind Vertragsbestandteil. Docstrings und Hilfsmethoden sind es nicht.

---

# 1. CanonicalLogRecord

## 1.1 Feldliste – eingefroren

Prüfmaßstab: Ein Feld ist Kernmodell, wenn danach **gefiltert oder sortiert**
wird oder wenn es **Identität** trägt. Alles andere gehört nach `details`.

| Feld | Typ | Pflicht | Quelle |
|---|---|---|---|
| `record_id` | `str` (uuid4 hex, 32) | **ja** | im Ingress erzeugt. Identifiziert *diesen Speichereintrag*, nicht das Ereignis. |
| `received_at` | `str` ISO-8601 UTC `Z` | **ja** | Ingress, `datetime.now(timezone.utc)`. Einzige lokal vertrauenswürdige Wanduhrzeit. |
| `producer_kind` | `str` | **ja** | `client` \| `server` \| `led` \| `other` |
| `producer_id` | `str` | **ja** | `voice-stt-client` \| `voice-stt-server` \| `respeaker-led-controller` |
| `instance_id` | `str` | **ja** | Client: uuid4 hex, einmal beim Start des Cores. Server: `envelope.server_instance_id`. |
| `scope` | `str` | **ja** | `session` \| `instance` \| `global`. Nicht ableitbar (siehe 1.3). |
| `channel` | `str`, **klein** | **ja** | `system` \| `audit` \| `transcription` \| `performance` |
| `level` | `str` | **ja** | `DEBUG` \| `INFO` \| `WARNING` \| `ERROR` \| `CRITICAL` |
| `replayed` | `bool` | **ja** | `result.origin is EventOrigin.REPLAY`; Clientrecords immer `False`. |
| `source_timestamp` | `str` \| `None` | nein | Server: `envelope.timestamp`. Python-Log: aus `record.created` konvertiert. Clientevent: Erzeugungszeit. |
| `type` | `str` \| `None` | nein | Server: `envelope.event`. Clientevent: Konstante. Python-Log: **`None`** — einen Typ aus dem Loggernamen zu erfinden täuschte eine Kategorie vor. |
| `component` | `str` \| `None` | nein | Python: `record.name`. Server: Namensraumpräfix von `type` (`transcription.*` → `transcription`), **nicht** aus `transport`. |
| `session_id` | `str` \| `None` | nein | zentraler Join-Schlüssel |
| `generation` | `int` \| `None` | nein | **nur Client.** Serverrecords erhalten sie aus dem `SessionContext` zum Empfangszeitpunkt. |
| `activation_id` | `str` \| `None` | nein | **diagnostisch, nicht autoritativ** — siehe Architektur-Freeze §3.4. Ausschließlich aus `envelope.data.activationId`. |
| `segment_id` | `int` \| `None` | nein | Server-Envelope validiert `int >= 0`. Lokal **INTEGER**, auch wenn die Server-DB TEXT ablegt. Konvertierung im Normalizer. |
| `transcription_id` | `str` \| `None` | nein | `envelope.transcription_id`, Format `"<sessionId>:<generation>:<segmentId>"` |
| `command_id` | `str` \| `None` | nein | Client `f"cmd-{uuid4().hex[:12]}"`; serverseitig nur auf `/ws/transcribe` |
| `event_id` | `str` \| `None` | nein | Server-`eventId` (uuid4, serverseitig UNIQUE). **Clientrecords immer `None`.** Dedupe-Schlüssel. |
| `correlation_id` | `str` \| `None` | nein | **immer** `"<namensraum>:<wert>"`, z. B. `trigger:cmd-…`, `injection:<entryId>`, `transcription:<id>` |
| `server_cursor` | `int` \| `None` | nein | `envelope.cursor`. Einzige retentionsfeste Serverordnung. **Nie ohne `instance_id` vergleichen.** |
| `message` | `str` \| `None` | nein | Python: `record.getMessage()`. Server: `envelope.extra["meldung"]`. **Darstellung, nie Datenquelle — nie zurückparsen.** |
| `details` | Mapping | nein | JSON-**Objekt** oder leer, nie ein Skalar. Server: `envelope.data`. |
| `raw` | Mapping \| `None` | nein | nur für **eingehende Serverevents**, nur wenn `store_raw_payload` greift. |

**Ausdrücklich NICHT im Record:** `monotonic_ns`, `host`, `process_id`,
`sequence`, `provider_id`, `source_record_id`, `schema_version`.

## 1.2 Warum `record_id` und `event_id` beide existieren

`record_id` entsteht lokal und existiert auch für Records ohne Serverherkunft.
`event_id` entsteht auf dem Server und ist der einzige replay-stabile Schlüssel.
Unterschiedliche Lebensdauer, unterschiedliche Autorität, unterschiedliche
Eindeutigkeit. Sie zusammenzulegen ließe entweder Clientrecords ohne Identität
oder zerstörte das Dedupe.

## 1.3 Warum `scope` eine eigene Spalte ist – und die vollständige Ableitungsregel

Eine Ableitung aus `session_id IS NULL` allein wäre mehrdeutig. Verbindlich:

```text
session_id gesetzt                      ->  scope = "session"
sonst und producer_kind == "server"     ->  scope = "global"
sonst  (client, led, other)             ->  scope = "instance"
```

Die dritte Zeile ist in OBS-000 nachgetragen worden: Die ursprüngliche
Formulierung nannte nur `server` und `client` und ließ `led` und `other`
undefiniert. Ein `lefx.*`-Record ohne Session ist eine Aussage über **diese
Prozessinstanz**, also `instance`.

## 1.4 Sollzustand

```python
@dataclass(frozen=True)
class CanonicalLogRecord:
    record_id: str
    received_at: str
    producer_kind: str
    producer_id: str
    instance_id: str
    scope: str
    channel: str
    level: str
    replayed: bool = False
    source_timestamp: Optional[str] = None
    type: Optional[str] = None
    component: Optional[str] = None
    session_id: Optional[str] = None
    generation: Optional[int] = None
    activation_id: Optional[str] = None
    segment_id: Optional[int] = None
    transcription_id: Optional[str] = None
    command_id: Optional[str] = None
    event_id: Optional[str] = None
    correlation_id: Optional[str] = None
    server_cursor: Optional[int] = None
    message: Optional[str] = None
    details: Mapping[str, Any] = field(default_factory=dict)
    raw: Optional[Mapping[str, Any]] = None
    is_internal: bool = False          # logging-eigene Records (Prioritaet)

    @property
    def priority(self) -> RecordPriority: ...
```

`details` und `raw` werden beim Bau eingefroren (Muster `event_models._freeze`).

## 1.5 Prioritätsableitung – eingefroren

```python
HIGH  if record.is_internal
      or ( not record.replayed
           and ( level_rank(record.level) >= level_rank("WARNING")
                 or record.channel == "audit"
                 or record.type is not None ) )
else LOW
```

Die Bedingung `not record.replayed` ist eine Korrektur gegenüber der Vorarbeit;
Begründung in `LOGGING_ARCHITEKTUR_FREEZE_V1.md §7.2`.

---

# 2. Wertemengen und Versionierung

## 2.1 Geschlossen vs. offen

```text
GESCHLOSSEN (Normalizer bildet hart ab)
    level          DEBUG | INFO | WARNING | ERROR | CRITICAL
    producer_kind  client | server | led | other
    scope          session | instance | global

OFFEN (Normalizer reicht unbekannte Werte unveraendert durch)
    channel        die vier Serverchannels; ein unbekannter Wert wird
                   gespeichert, nicht abgelehnt
    type           vollstaendig offener Namensraum
    component      offener Text
```

**Regel:** Alle Enum-artigen Felder werden als **TEXT** gespeichert, niemals als
Integer-Code. Ein numerischer Code erzwänge eine Migration bei jedem neuen Wert.

**`level` ist der einzige geschlossene Fall**, weil Filter und Priorisierung
darauf beruhen. Der Originalwert bleibt erhalten:

```text
severity unbekannt  ->  level = "INFO"
                        details["source_severity"] = <Originalwert>
```

Belegt: `severity` ist serverseitig **kein** geschlossenes Enum
(`info`/`warning`/`error` beobachtet, `critical` in der Priorisierung
vorgesehen). Der Normalizer darf deshalb **nie** `Level(value)` aufrufen.

## 2.2 Channels – Kleinschreibung ist verbindlich

Der Zielbildentwurf schreibt die Channels groß (`System`, `Audit`, …). Der
**Code kennt ausschließlich Kleinschreibung**. Verbindlich ist die
Kleinschreibung; andernfalls entstünden zwei Wertemengen für ein Feld.

```text
system         Prozess-, Transport- und Konfigurationszustand.
               app.started/stopping, core thread, websocket.*, eventstream.*,
               reconnect.*, config.*, sowie ALLE unstrukturierten Python-Logs
               ohne bessere Zuordnung (Default).

audit          Vom Nutzer oder vom Client absichtlich ausgeloeste Handlungen
               und deren Ablehnung.
               hotkey.*, command.*, trigger.sent/ack, dictation.*, settings.*,
               action.blocked, microphone.mute.

transcription  Alles am Transkript und dessen Weiterverarbeitung.
               final.received, final.deduplicated, injection.*, history.*,
               reinsertion.*.

performance    Nur Zahlen, nur Aggregate, nie Einzelereignisse aus dem
               Hot Path. audio.*_stats, queue.state, timings, drop counters,
               logging.records_dropped.
```

Keine zusätzlichen Client-Channels. Der Channel ist **orthogonal** zu
`producer_kind`; ein Channel `client_ui` mischte Herkunft in die Kategorie,
obwohl `producer_kind=client` plus `component` dieselbe Auswahl erlaubt.

## 2.3 Schema-Versionierung

```text
SQLite      PRAGMA user_version + Tabelle schema_meta(key, value).
            KEINE Spalte je Zeile -- sie waere zu 100 % redundant, weil eine
            Migration ohnehin alle Zeilen in die neue Form bringt.
            KEINE migrations-Tabelle -- sie waere eine zweite Wahrheit neben
            user_version.

JSONL       schemaVersion je ZEILE, als erstes Feld. Eine JSONL-Datei wird
            kontextlos gelesen.

Geltung     schema_version beschreibt die SPALTENSTRUKTUR, nicht die
            Wertemengen. Ein neuer channel oder ein neuer type loest KEINE
            Migration aus.
```

---

# 3. Normalizer – drei Eingänge

```python
from_log_record(record, *, instance_id, session_id, generation)
        -> CanonicalLogRecord

from_server_result(context, result) -> Optional[CanonicalLogRecord]

from_client_event(type, *, channel, level, component, message, details, **ids)
        -> CanonicalLogRecord
```

**Der Normalizer wirft nie.** Im Zweifel liefert er `None`, und der Aufrufer
zählt `malformed`.

## 3.1 Python-`LogRecord` → Canonical

```text
channel     := LOGGER_CHANNEL_MAP.get(record.name, "system")
producer    := "led" / "respeaker-led-controller",  wenn record.name mit
               "lefx." beginnt; sonst "client" / "voice-stt-client"
component   := record.name
level       := record.levelname
type        := None
message     := record.getMessage()
source_timestamp := record.created -> ISO-8601 UTC "Z"
details     := {"logger": name, "func": funcName, "line": lineno,
                "thread": threadName}
             + die vier bestehenden extra-Felder, falls gesetzt:
                   session_id, segment_id, event_type, detail
             + record.exc_info -> details["exception"] als TEXT
                   (traceback.format_exception)
             NIEMALS record.args, NIEMALS locals(), NIEMALS repr()
```

### Woher `session_id` und `generation` kommen – normativ

```text
session_id  := AUSSCHLIESSLICH record.__dict__.get("session_id"), also der
               bestehende extra-Vertrag. Sonst None.
generation  := AUSSCHLIESSLICH record.__dict__.get("generation"). Sonst None.
segment_id  := AUSSCHLIESSLICH record.__dict__.get("segment_id"). Sonst None.

Der UnifiedLogHandler fragt KEINEN Sessionzustand ab und haelt KEINE Referenz
auf Controller, Session oder Coordinator.

Begruendung: Der Handler laeuft auf sechs verschiedenen Threads, darunter dem
PortAudio-Callbackthread und dem Qt-Mainloop. Eine Leseabfrage des aktuellen
Sessionzustands waere entweder nicht thread-sicher oder braeuchte ein Lock im
Hot Path -- und sie waere eine Kopplung des Loggings an die Runtime, also ein
Verstoss gegen O-01. Wer Korrelationsfelder braucht, benutzt die
strukturierte Client-Observation-API (3.3), nicht eine Python-Logzeile.

Diese Regel ist in OBS-000 nachgetragen worden; die urspruengliche Signatur
liess offen, WER session_id liefert.
```

### `LOGGER_CHANNEL_MAP` – verbindliche Fassung

Das Audit enthielt an dieser Stelle einen unaufgelösten Gedanken im Fließtext
(„→ performance? NEIN → system"). Ein Coding-Agent hätte dort echten
Interpretationsspielraum gehabt. Verbindlich:

```python
LOGGER_CHANNEL_MAP = {
    "text": "transcription",        # history, reinsertion, text_injector
}
# Alles Uebrige, ausnahmslos: "system"
```

```text
NORMATIV
  * Nur "text" wird abgebildet. JEDER andere Loggername -- einschliesslich
    audio, connection, controller, event_stream, core.*, ui.*, lefx.* --
    ergibt channel = "system".
  * Es entsteht NIE der Channel "performance" aus einem Loggernamen.
    "performance" entsteht ausschliesslich aus strukturierten
    Aggregatevents.
  * Es entsteht NIE der Channel "audit" aus einem Loggernamen.
    "audit" entsteht ausschliesslich aus strukturierten Clientevents.

Begruendung: Ein unstrukturierter Text ist Diagnosetext. Die fachliche
Kategorie kommt aus den strukturierten Events, nicht aus einer Feinzuordnung
je Logzeile.
```

Der `lefx.*`-Fall ändert **nur** `producer_kind`/`producer_id`/`component`,
**nicht** den Channel.

## 3.2 `(SessionContext, EventProtocolResult)` → Canonical

```text
EVENT-Ergebnisse
    producer_kind    "server"
    producer_id      "voice-stt-server"
    instance_id      envelope.server_instance_id
    channel          envelope.channel
    level            normalisiert aus envelope.severity (2.1)
    type             envelope.event
    component        Namensraumpraefix von type
    session_id       envelope.session_id
    generation       context.generation            <- aus dem SessionContext
    activation_id    envelope.data.get("activationId")
    segment_id       envelope.segment_id  (int)
    transcription_id envelope.transcription_id
    event_id         envelope.event_id
    server_cursor    envelope.cursor
    message          envelope.extra.get("meldung")   <- Befund C-2
    details          envelope.data
    raw              result.payload                  <- ENTFROREN, siehe 4.1
    replayed         result.origin is EventOrigin.REPLAY
    scope            "session" wenn session_id gesetzt, sonst "global"

CONTROL-Ergebnisse (log.hello, log.subscribed, log.gap, log.error,
                    log.replay_completed, log.pong, log.keepalive,
                    sowie als duplicate markierte Events)
    producer_kind    "client"
    producer_id      "voice-stt-client"
    instance_id      instance_id des Clients
    channel          "system"
    level            "WARNING" bei log.error und log.gap, sonst "INFO"
    type             "client.eventstream.<kind>"
    component        "eventstream"        <- FEST, nicht aus dem type-Praefix
    session_id       context.session_id
    generation       context.generation
    raw              result.payload
    bei log.gap      details.lostFromCursor / lostToCursor
    bei log.hello    NIE raw -- nur die Whitelist aus R-6
    scope            "session" wenn session_id gesetzt, sonst "instance"
```

**`component` bei Controlframes.** Die Regel „Namensraumpräfix von `type`"
ergäbe hier `"client"` — nutzlos als Filterwert. Deshalb ist `component` für
Controlframes fest `"eventstream"`. In OBS-000 nachgetragen; die ursprüngliche
Regel war nur für Serverevents formuliert.

**`message` aus `extra["meldung"]`.** Der Server legt die menschenlesbare
Meldung unter dem deutschsprachigen, undokumentierten Schlüssel `"meldung"` ab;
der Client kennt ihn nicht und schiebt ihn nach `EventEnvelope.extra`. Das ist
die **einzige** serverseitige Quelle für `message` und muss im Normalizer
ausdrücklich behandelt werden — kein stiller Verlass darauf.

**`log.gap(reason=retention)`** bedeutet endgültigen Datenverlust auf der
Serverseite. Der Gap wird als eigener Record gespeichert
(`client.eventstream.gap`), damit die Lücke in der lokalen Historie **sichtbar**
bleibt, statt stillschweigend zu fehlen.

## 3.3 Reihenfolge innerhalb jedes Pfades

```text
1. Felder abbilden
2. Zeit normalisieren
3. Redaction   <- am ENDE jedes Pfades, nicht am Anfang
4. Record bauen und einfrieren
```

---

# 4. Redaction – eingefroren

## 4.1 `unfreeze()` – Pflicht vor jeder Serialisierung

`EventProtocolResult.payload` ist rekursiv eingefroren, und zwar in **drei**
Typen: `MappingProxyType`, `tuple` **und `frozenset`** (verifiziert in
`EV-02 / C-05`, acht Aufrufstellen von `_freeze_mapping`).

`json.dumps` kennt keinen davon. Mit `default=str` kollabierte der gesamte
Payload zu einem einzigen String — und dann greift die **schlüsselbasierte**
Redaction nicht mehr, weil es keine Schlüssel mehr gibt. Das ist nicht nur ein
Formatfehler, sondern ein **Sicherheitsbefund**.

```python
def unfreeze(value):
    """MappingProxyType -> dict, tuple -> list, frozenset -> sortierte list.
    Rekursiv. Tiefen- und Knotengrenze nach R-12."""
```

## 4.2 Die zwölf Regeln

```text
R-1   Der LoggingCore kennt keinen Admin-Key, kein Token, kein Auth-Objekt.
      Er nimmt ausschliesslich CanonicalLogRecords entgegen.

R-2   Redaction im PRODUCER-Thread fuer Records, die der CLIENT selbst baut.
      Fuer serverseitige raw-Payloads im WORKER, weil der Server bereits
      saniert hat (Begruendung: Architektur-Freeze §8.2).

R-3   SCHLUESSELREGEL, keine Werteheuristik. Rekursiv, case-insensitiv,
      ohne "_" und "-" verglichen:
          authorization, token, accesstoken, apikey, adminkey,
          password, secret, cookie, credential
      Treffer -> "[redacted]".
      Eine Werteheuristik ("sieht aus wie ein Token") erzeugt falsche
      Sicherheit und ist verboten.

R-4   Kein record.args, kein locals(), kein Objekt-repr().
      Exception ausschliesslich als formatException-Text.
      Begruendung: Ein repr() eines Auth-Objektes ist der klassische
      Leckweg. EventStreamAccess schuetzt sich mit repr=False, ein
      kuenftiges Admin-Objekt vielleicht nicht.

R-5   Ausgehende Frames (_send_json, subscribe_payload) werden nie roh
      protokolliert. Entsteht je ein client.eventstream.subscribe-Record,
      dann nur mit channels und afterCursor.

R-6   store_raw_payload gilt NUR fuer EINGEHENDE Serverevents.
      hello wird NIE raw. Es wird ausschliesslich ueber eine WHITELIST
      erfasst:
          sessionId,
          logAccess.available/code/reason/expiresAt/logProtocolVersion/
                    serverInstanceId/oldestCursor/latestCursor,
          sessionConfig  (inkl. warnings/fallbacks/ignoredFields),
          activationConfig,
          sessionCapabilities
      Begruendung: hello ist diagnostisch aeusserst wertvoll -- es zeigt
      Fehlkonfigurationen -- enthaelt aber nachweislich
      logAccess.accessToken. Bei einem Payload, der ein Geheimnis traegt,
      ist eine Whitelist die einzig belastbare Form. Die Redaction laeuft
      ZUSAETZLICH.

R-7   Store und Sinks liegen im Benutzerprofil (siehe P-8/P-9).

R-8   Jede URL verliert Query und Fragment vor der Speicherung
      (urlsplit -> urlunsplit ohne query/fragment). Betrifft insbesondere
      die geloggte target_url, die Wake Words und Sensitivitaeten traegt.

R-9   Benutzerprofilpfade werden auf "~" gekuerzt -- auch in Tracebacks.
      Keine vollstaendige Unterdrueckung: der relative Pfad ist
      diagnostisch noetig.

R-10  Transkriptfelder nach store_transcription_content; die ZEICHENZAHL
      bleibt erhalten ("[redacted:<n> chars]").
      Betroffene Schluessel: text, displayText, rawText, stableText,
      unstableText, committedStableText, visualUnstableText.
      GILT AUCH FUER UNSTRUKTURIERTE LOGTEXTE, nicht nur fuer Serverevents.
      Zwingend, weil der Client heute schon Transkripttext im Klartext
      loggt: auf INFO je Final und bei Konflikten VOLLSTAENDIG auf WARNING
      (verifiziert in EV-02 / C-11). Der Levelfilter faengt die
      WARNING-Faelle NICHT ab.

R-11  raw wird als JSON-OBJEKT gespeichert oder gar nicht.
      Ein default=str-Rueckfall auf CONTAINER-Ebene ist VERBOTEN.
      Der Rueckfall gilt ausschliesslich je BLATTWERT.
      Vorher laeuft immer unfreeze() (4.1).

R-12  Tiefengrenze 16 UND Knotengrenze 500. Darueber wird abgeschnitten und
      markiert. Schuetzt den Producer-Thread -- insbesondere den Qt-Thread,
      der ueber _log_feedback_decision selbst Producer ist -- vor einem
      zyklischen oder pathologisch tiefen details.
```

## 4.3 Dateirechte

```text
P-8   Store und Sinks liegen unterhalb von %LOCALAPPDATA%\RealtimeSTT Client\
      und erben damit die Benutzer-ACL. Es wird KEIN eigenes Verzeichnis mit
      abweichenden Rechten angelegt und KEIN Pfad ausserhalb des
      Benutzerprofils akzeptiert. Ein konfigurierter absoluter Pfad wird
      gegen das Benutzerprofil geprueft.
      Vorbild: EventStreamConfig.validate verlangt bereits einen absoluten
      Pfad.

P-9   Beim Anlegen wird geprueft, dass die -wal- und -shm-Geschwister im
      SELBEN Verzeichnis entstehen. Sie enthalten Nutzdaten und gehoeren
      derselben Zugriffskontrolle.

M-11  Nach dem ersten Start werden die effektiven Dateirechte einmalig
      protokolliert (icacls), als Abnahmebeleg.
```

## 4.4 Was nachweislich nicht leckt – und als Regel so bleiben soll

| Weg | Status | Grund |
|---|---|---|
| Token über `repr()` | blockiert | `EventStreamAccess.access_token`, `SessionContext.log_access`, `HotkeyConfig.key` haben `repr=False` |
| Token über URL | kein Weg gefunden | `/ws/logs` ist queryfrei erzwungen; der Token wird in-band im ersten Frame gesendet |
| Audioinhalt | kein Weg gefunden | nur Byte- und Framezahlen werden geloggt. **Regel: PCM-Bytes nie in `details` oder `raw`.** |
| Fenstertitel der Zielanwendung | nicht vorhanden | `text_injector` loggt nur `HWND`. **Regel, damit es so bleibt.** |
| Konfiguration über `%r` einer Dataclass | **offen** | `AppConfig` und Untermodelle haben Standard-`repr`. Heute existiert kein solcher Aufruf; R-4 verbietet ihn dauerhaft. |

---

# 5. SQLite-Store

## 5.1 Ablageort

```text
Datei      %LOCALAPPDATA%\RealtimeSTT Client\observability.sqlite3
Ableitung  core.config.DEFAULT_LOCAL_APP_DIR / "observability.sqlite3"
Konfig     logging.observability.db_path   (None = Standard)
```

`DEFAULT_LOCAL_APP_DIR` ist die einzige zentral definierte
Datenverzeichniskonstante und beherbergt bereits `logs/`, `config.yaml`,
`event_cursor.json` und `lefx/`. Der abweichende Historienpfad
(`RealtimeSTT_Client`, mit Unterstrich) wird **nicht** als Vorbild genommen und
in diesem Vorhaben **nicht** angefasst.

Die Endung ist bewusst **nicht** `.db`, damit die Datei nicht mit
`transcript_history.db` verwechselt wird, und entspricht der Endung, die der
Server verwendet.

## 5.2 DDL – eingefroren

```sql
-- Beim Anlegen einer NEUEN Datei, in dieser Reihenfolge:
PRAGMA journal_mode = WAL;
PRAGMA synchronous  = NORMAL;
PRAGMA busy_timeout = 5000;
PRAGMA foreign_keys = ON;
-- KEIN auto_vacuum. Gestrichen (siehe 5.6); damit entfaellt zugleich die
-- heikle Bedingung "muss vor der ersten Tabelle gesetzt werden".

CREATE TABLE IF NOT EXISTS schema_meta (
    key    TEXT PRIMARY KEY,
    value  TEXT NOT NULL
);
-- Zeilen: created_at, created_by_version, last_migrated_at

CREATE TABLE IF NOT EXISTS logs (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,  -- lokale Ordnung

    record_id         TEXT    NOT NULL,
    received_at       TEXT    NOT NULL,                   -- ISO-8601 UTC, Z
    source_timestamp  TEXT,

    producer_kind     TEXT    NOT NULL,                   -- client|server|led|other
    producer_id       TEXT    NOT NULL,
    instance_id       TEXT    NOT NULL,

    scope             TEXT    NOT NULL,                   -- session|instance|global
    channel           TEXT    NOT NULL,
    level             TEXT    NOT NULL,
    type              TEXT,
    component         TEXT,

    session_id        TEXT,
    generation        INTEGER,
    activation_id     TEXT,                               -- diagnostisch
    segment_id        INTEGER,
    transcription_id  TEXT,
    command_id        TEXT,
    event_id          TEXT,                               -- Server, sonst NULL
    correlation_id    TEXT,                               -- "<namensraum>:<wert>"
    server_cursor     INTEGER,

    replayed          INTEGER NOT NULL DEFAULT 0,         -- 0/1

    message           TEXT,
    details_json      TEXT,                               -- JSON-Objekt oder NULL
    raw_json          TEXT                                -- JSON-Objekt oder NULL
);

-- Dedupe: NUR fuer Records mit Server-eventId
CREATE UNIQUE INDEX IF NOT EXISTS ux_logs_producer_event
    ON logs (producer_id, event_id)
    WHERE event_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_logs_session_id
    ON logs (session_id, id DESC)
    WHERE session_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_logs_received_at
    ON logs (received_at);

CREATE INDEX IF NOT EXISTS ix_logs_channel_level
    ON logs (channel, level, id DESC);

CREATE INDEX IF NOT EXISTS ix_logs_activation
    ON logs (activation_id, id DESC)
    WHERE activation_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS ix_logs_correlation
    ON logs (correlation_id, id DESC)
    WHERE correlation_id IS NOT NULL;
```

## 5.3 Bewusst NICHT angelegte Indizes

| Kandidat aus Zielbild §16 | Entscheidung | Begründung |
|---|---|---|
| `source_timestamp` | nein | wird nie sortiert und nie gefiltert; der Zeitbereichsfilter arbeitet auf `received_at` |
| `producer_kind` | nein | vier Werte, in der Praxis zwei — Kardinalität zu gering |
| `type` einzeln | nein | in der Praxis immer mit `channel` oder `session_id` kombiniert |
| `level` einzeln | nein | in `ix_logs_channel_level` enthalten |
| `segment_id` | nein | immer mit `session_id` gefiltert |
| `event_id` einzeln | nein | im UNIQUE-Index enthalten |
| `component` | nein | wie `type` |

**Bewusste Abweichung vom Zielbildentwurf, hiermit dokumentiert.** Jeder Index
kostet in einem schreibintensiven Store Schreibzeit; sieben Einzelindizes bei
~24 Spalten wären mehr Index als Daten. Zeigen spätere Messungen das Gegenteil,
ist ein Index eine einzeilige Migration.

## 5.4 Verbindungen und Threads

```text
SCHREIBEN
    Genau EINE Verbindung, im Besitz des LoggingWorker-Threads.
    Die Verbindung wird IM WORKER-THREAD erzeugt, NICHT in start().
    check_same_thread bleibt auf dem Standard -- die Verbindung soll den
    Thread nie verlassen.
    Sonst: sqlite3.ProgrammingError beim ersten Batch.

LESEN
    Eigene, kurzlebige Verbindungen des Query-Layers.
    KEIN mode=ro. Eine read-only-Verbindung auf eine WAL-Datenbank ist nicht
    allgemein moeglich -- der oeffnende Prozess braucht Schreibrechte auf die
    -shm-Datei. Stattdessen:
        PRAGMA query_only = ON;
    Der Prozess besitzt die Datei ohnehin (eigenes %LOCALAPPDATA%).
    Nebennutzen: eine fehlerhafte Abfrage kann nie schreiben.

WAL ist zwingend. Ohne WAL sperrt jede LogView-Abfrage den Worker und
umgekehrt.
```

## 5.5 Schreiben, Dedupe und Migration

```sql
INSERT INTO logs (...) VALUES (...)
ON CONFLICT (producer_id, event_id) DO NOTHING;
```

```text
write_batch(records) -> (eingefuegt: int, dedupliziert: int)

  * executemany innerhalb EINER Transaktion je Batch.
  * Der Rueckgabewert speist die Zaehler written und deduplicated.
    Ohne den zweiten Wert ist im Betrieb nicht unterscheidbar, ob ein Replay
    korrekt dedupliziert oder ob gar nichts angekommen ist.
```

**Dedupe-Schlüssel: `(producer_id, event_id)`, partieller UNIQUE-Index.**

```text
GARANTIEN
  * event_id ist uuid4 und serverseitig zusaetzlich UNIQUE.
  * Der Schluessel ist unabhaengig von cursor, server_instance_id, Retention
    und Verbindungsgeneration. Er ueberlebt Serverneustart, Clientneustart,
    Endpointwechsel und Instanzwechsel.
  * producer_id im Index schuetzt gegen einen kuenftigen zweiten Produzenten
    mit eigenem ID-Schema, ohne heute etwas zu kosten.
  * Die ERSTE gespeicherte Fassung gewinnt. Kommt ein Event zuerst live und
    spaeter als Replay, bleibt replayed=0 -- das ist die gewuenschte Aussage
    "lokal live empfangen".
  * Fuer Records ohne event_id (alle Client- und LED-Records) greift der
    partielle Index nicht; ihre Eindeutigkeit ergibt sich daraus, dass
    record_id genau einmal erzeugt wird.

BENANNTE GRENZEN
  1. Die Dedupe wirkt nur auf der PERSISTENZ. Die UI sieht replayte Records
     ein weiteres Mal; sie sind ueber `replayed` erkennbar und duerfen dort
     bewusst erscheinen.
  2. Zwei Serverinstanzen hinter demselben Endpoint erzeugen unabhaengige
     uuid4-Raeume. Keine Kollision; die lokale Historie enthaelt dann zwei
     instance_id -- gewollt und filterbar.
  3. Wird die Server-SQLite geloescht und neu angelegt, beginnen die Cursor
     wieder bei 1, die eventIds sind aber neu. Deshalb darf server_cursor
     NIE ohne instance_id sortiert oder verglichen werden.
  4. Dieselbe event_id aus einer neuen Serverinstanz (nur nach Wiedereinspielen
     eines DB-Backups moeglich) wuerde zu einer Zeile verschmelzen. BEWUSST
     AKZEPTIERT: es IST dasselbe Ereignis. Die gespeicherte instance_id ist
     die des ersten Empfangs; das gehoert in den Migrationskommentar.
```

```text
MIGRATION
  user_version = 0   Datei fehlt oder ist leer -> vollstaendig anlegen
  user_version = 1   V1-Schema wie oben
  MIGRATIONS = [ (1, _migrate_to_1), ... ]

  Ablauf beim Start:
    1. Datei oeffnen. Schlaegt das fehl -> Store deaktiviert, FAILED_STORE,
       Anwendung laeuft weiter.
    2. PRAGMA user_version lesen.
    3. HOEHER als bekannt -> Nur-Lesen, DEGRADED_STORE.
       NICHT loeschen, NICHT downgraden.
    4. Niedriger -> fehlende Schritte nacheinander, jeder in EIGENER
       Transaktion, danach PRAGMA user_version = n.
    5. Schritt scheitert -> Rollback, Store deaktiviert, FAILED_STORE,
       EINE stderr-Zeile. Kein Abbruch der Anwendung.

  Es wird NIE eine bestehende Logdatei geloescht oder umbenannt. Der Store
  ist Diagnosematerial; ihn im Fehlerfall wegzuwerfen waere der schlechteste
  denkbare Moment.
```

## 5.6 Retention

```text
Takt   im Worker, hoechstens alle 60 s UND hoechstens alle 2000 geschriebenen
       Records; zusaetzlich einmal beim Start.
       Zeitbudget je Lauf: 200 ms.
       NIE nach jedem Batch. (Gegenmuster: die vorhandene Transkripthistorie
       ruft cleanup() nach jedem Insert.)

Beide Grenzen wirken; die erste, die greift, gewinnt.
```

```sql
-- 1. Alter, BLOCKWEISE
DELETE FROM logs
 WHERE id IN (
   SELECT id FROM logs
    WHERE received_at < :cutoff_iso
    ORDER BY id
    LIMIT 5000
 );
-- wiederholen, solange changes() = 5000 UND das Zeitbudget reicht

-- 2. Anzahl, EBENFALLS BLOCKWEISE und gegen NULL gesichert
SELECT id FROM logs ORDER BY id DESC LIMIT 1 OFFSET :max_entries - 1;
--   kein Ergebnis  -> nichts zu tun
--   Ergebnis :floor -> blockweise loeschen:
DELETE FROM logs WHERE id IN (
    SELECT id FROM logs WHERE id < :floor ORDER BY id LIMIT 5000
);
-- wiederholen, solange changes() = 5000 UND das Zeitbudget reicht

-- 3. Groesse: NUR MESSEN, NICHT EINGREIFEN
PRAGMA page_count;
PRAGMA page_size;
-- Ueberschreitung von max_db_bytes -> Health-Warnsignal
--   (logging.retention_pressure). KEIN automatisches Absenken von
--   max_entries, KEIN incremental_vacuum, KEIN VACUUM.
```

**Bei `disk full` wird die Retention ausgesetzt** — auch ein `DELETE` braucht
Platz im WAL.

## 5.7 Pagination – Keyset, nicht OFFSET

```sql
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
   AND (:text          IS NULL OR message   LIKE '%' || :text || '%'
                               OR type      LIKE '%' || :text || '%'
                               OR component LIKE '%' || :text || '%')
 ORDER BY id DESC
 LIMIT :limit;

-- Folgeseite:  ... AND id < :after_id
```

```text
raw_json wird in der LISTENabfrage NICHT geladen. Es ist mit Abstand das
groesste Feld und wird nur in der Detailansicht gebraucht -- dort ueber
    SELECT raw_json FROM logs WHERE record_id = ?

Warum Keyset statt OFFSET:
  * OFFSET n ueberspringt n Zeilen und wird mit jeder Seite langsamer.
  * Zwischen zwei Seitenabrufen schreibt der Worker weiter. Mit OFFSET
    verschieben sich alle Zeilen und die UI zeigt Duplikate oder Luecken.
    Mit id < :after_id ist die Seitenfolge stabil.

Parameterbindung ausschliesslich ueber Platzhalter. Kein String-Format,
keine Interpolation.
```

## 5.8 Löschfunktion

```text
LogStore.clear() -> int
    DELETE FROM logs;  PRAGMA wal_checkpoint(TRUNCATE);

Aufruf ueber ObservabilityManager, ausgeloest durch die Schaltflaeche
"Diagnosehistorie loeschen" im Logging-Tab.
NICHT ueber den Query-Layer: Provider schreiben nie (O-14), und eine
Loeschfunktion in der Abfrageschnittstelle waere fuer Remote-Provider
ohnehin unzulaessig.
```

---

# 6. Ingress und Client-Observation-API

```python
class ObservabilityIngress:
    def submit(self, record: CanonicalLogRecord) -> bool:
        """Thread-sicher. Blockiert NIE. Wirft NIE.
        False = nicht angenommen (deaktiviert, gefiltert, verworfen)."""

    def observe_server_result(
        self, context: SessionContext, result: EventProtocolResult
    ) -> None:
        """Der Fan-out-Eingang des ServerLiveAdapters."""

    def event(
        self,
        type: str,
        *,
        channel: str,
        level: str = "INFO",
        component: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Mapping[str, Any]] = None,
        session_id: Optional[str] = None,
        generation: Optional[int] = None,
        activation_id: Optional[str] = None,
        segment_id: Optional[int] = None,
        command_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        transcription_id: Optional[str] = None,
    ) -> None:
        """Die strukturierte Client-Observation-API. Genau EINE Zeile je
        Aufrufstelle."""

    def drain(self, max_items: int, timeout: float) -> list[CanonicalLogRecord]:
        """Nur fuer den Worker."""


class NullIngress(ObservabilityIngress):
    """Verhaltensgleiches No-Op."""

NULL_INGRESS = NullIngress()
```

```text
Verdrahtung -- rein additiv, ohne bestehende Signatur zu brechen:

    core/controller.py
        def __init__(self, config, ...,
                     observability: ObservabilityIngress = NULL_INGRESS):
            self.observability = observability
            self.session_coordinator.on_observation = \
                observability.observe_server_result

    ui/core_bridge.py
        def __init__(self, config, controller_factory=None, parent=None,
                     observability: ObservabilityIngress = NULL_INGRESS):
            self._observability = observability
            self._controller_factory = controller_factory or (
                lambda cfg: STTController(cfg, observability=observability)
            )

Begruendung: ControllerFactory ist Callable[[AppConfig], STTController] und
wird einstellig aufgerufen; ein bestehender Test uebergibt eine eigene
Factory. Eine Signaturaenderung wuerde ihn brechen -- und damit die eigene
Regel "kein bestehender Test wird geaendert". Mit der Default-Factory bleibt
eine von aussen uebergebene Factory einstellig und der Controller erhaelt
NULL_INGRESS.

KONSTRUKTORINJEKTION, kein Modul-Singleton. Der STTController wird in den
Tests vielfach frei instanziiert; ein Singleton wuerde Testlaeufe koppeln
und Records zwischen Tests verschleppen.

KEIN generischer Eventbus. Ein Bus waere eine dritte Verteilsemantik neben
den bestehenden Callback-Slots und den Qt-Signalen. Fuer ein Beobachtungsziel
mit genau einem Konsumenten genuegt ein injizierter Ingress -- testbar mit
einem Fake, rueckbaubar mit einem Parameter.
```

---

# 7. Der Fan-out-Hook

## 7.1 Ort und Form – eingefroren

```python
# core/session_coordinator.py -- rein additiv, ~14 Zeilen

self.on_observation: Optional[
    Callable[[SessionContext, EventProtocolResult], None]
] = None

def _notify_observer(self, result: EventProtocolResult) -> None:
    observer = self.on_observation
    if observer is None:
        return
    try:
        observer(self._context, result)
    except Exception:
        pass          # Fehlerbehandlung liegt in der Logging-Failure-Domain

async def _handle_event(self, binding, result) -> bool:
    self._notify_observer(result)        # <-- ERSTE Anweisung
    ...                                  # alles Uebrige unveraendert

def _handle_control(self, binding, result) -> None:
    self._notify_observer(result)        # <-- ERSTE Anweisung
    ...                                  # alles Uebrige unveraendert
```

## 7.2 Warum genau hier

1. Es ist der schmalste Punkt, durch den jedes **erfolgreich validierte**
   Ergebnis läuft — Events **und** Controlframes (`log.hello`, `log.subscribed`,
   `log.gap`, `log.error`, `log.replay_completed`, `log.pong`, `log.keepalive`)
   sowie die als `duplicate` markierten Events, die `on_event` nie erreichen.
2. Der `SessionContext` liegt hier bereits vor: `generation`, `session_id`,
   `event_state`, `unavailable_code`. Weiter unten ist er nur noch Parameter,
   weiter oben gar nicht vorhanden.
3. Der Aufruf steht **vor** der Bindings-, Token- und Sessionprüfung. Damit
   werden genau die Events sichtbar, die der Runtimepfad verwirft — der
   diagnostisch wertvollste Fall überhaupt.
4. Es ist ein echtes Fan-out: Der Feedbackzweig läuft unverändert über
   `on_event` weiter.
5. Transport und Protokollprozessor bleiben unangetastet; der Diff ist additiv
   und betrifft eine Klasse.

## 7.3 Die Fehlerbehandlung ist Pflicht, nicht Vorsicht

`EventStreamTransport._dispatch` fängt eine durchschlagende Ausnahme mit
`except BaseException`, ruft `self._processor.reject_event(result)` und wirft
weiter (verifiziert in `EV-02 / C-03`). Ein werfender Beobachter würde das
Event also **aktiv verwerfen** und die Verbindung recyceln.

```text
NORMATIV, zwei Ebenen:
  * ServerLiveAdapter.observe() faengt SELBST und meldet an
    LoggingInternalHealth. Dort entsteht die Sichtbarkeit.
  * Das except Exception im Coordinator ist die LETZTE Sicherung und bleibt
    bewusst leer -- sonst haette ausgerechnet die Failure-Domain eine blinde
    Stelle ohne Zaehler und ohne Meldung.
  * BaseException wird NIRGENDS gefangen. asyncio.CancelledError ist seit
    Python 3.8 eine BaseException; sie zu verschlucken wuerde das Abbrechen
    des Eventstream-Tasks brechen.
```

## 7.4 Ausdrücklich verbotene Hookstellen

| Stelle | Warum verboten |
|---|---|
| `STTController.on_event_stream_event` | vorhanden und frei, **aber** sein Rückgabewert entscheidet über Cursor-Commit und Verbindungsrecycling. Logging würde Runtime-Autorität. |
| `EventStreamTransport._dispatch` / `on_event` / `on_control` | Änderung an Protokoll-/Transportlogik; dieselbe Rückgabesemantik; kein `SessionContext`. |
| `EventProtocolProcessor.process_mapping` | reine Protokollvalidierung, vor der Dedupe-Entscheidung, kennt weder `generation` noch die aktuelle Session. |
| `FeedbackEngine.handle_event_stream` | Der Normalizer kennt nur neun Serverevents und liefert für alles andere `None` — genau die unbekannten und damit interessanten Events gingen verloren. |
| `ui/application.py::_on_feedback_decision` | Qt-Thread, **nach** zwei Filtern (`not decision.publish or decision.replay` → return). Replay- und Duplikatrecords wären unsichtbar; Rohpayload und Cursor sind dort nicht mehr vorhanden. |

## 7.5 Zweiter Beobachtungspunkt: Protokollfehler

```python
# core/event_stream.py :: EventStreamTransport.run(), im except-Zweig
# EINE Zeile, kein zusaetzlicher Kontrollfluss.
#   -> client.eventstream.protocol_error
#      details: {"error_type": type(exc).__name__, "message": str(exc)}
#      OHNE das Rohframe -- es liegt dort nicht mehr vor.
```

Begründung: siehe `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.5`, Grenze 1.

---

# 8. Query-Verträge

```python
class ProviderState(str, Enum):
    AVAILABLE     = "available"
    AUTH_REQUIRED = "auth_required"     # von V1 nie erzeugt, aber gueltig
    UNAVAILABLE   = "unavailable"
    ERROR         = "error"


@dataclass(frozen=True)
class ProviderStatus:
    provider_id: str
    display_name: str
    state: ProviderState
    detail: str = ""          # kurz, redigiert, fuer die Statuszeile
    # ProviderCapabilities: in V1 NICHT vorhanden (YAGNI), additiv
    # nachruestbar, weil dies eine frozen dataclass mit Defaults ist.


@dataclass(frozen=True)
class QueryFilter:
    """Rein deklarativ. Kein Provider darf sie veraendern."""
    producer_kinds:  tuple[str, ...] = ()
    producer_ids:    tuple[str, ...] = ()
    instance_ids:    tuple[str, ...] = ()
    channels:        tuple[str, ...] = ()
    levels:          tuple[str, ...] = ()
    types:           tuple[str, ...] = ()
    type_prefix:     Optional[str]   = None
    components:      tuple[str, ...] = ()
    scopes:          tuple[str, ...] = ()

    session_id:       Optional[str] = None
    generation:       Optional[int] = None
    activation_id:    Optional[str] = None
    segment_id:       Optional[int] = None
    command_id:       Optional[str] = None
    correlation_id:   Optional[str] = None
    transcription_id: Optional[str] = None
    event_id:         Optional[str] = None

    since: Optional[str] = None       # ISO-8601 UTC, inklusive
    until: Optional[str] = None       # ISO-8601 UTC, exklusive
    text:  Optional[str] = None       # Freitext ueber message/type/component

    include_replayed: bool = True
    newest_first:     bool = True


@dataclass(frozen=True)
class LogRecordView:
    """Was die UI sieht. Bewusst NICHT das Speichermodell:
    provider_id ist Herkunft der ABFRAGE, nicht des Ereignisses,
    und raw ist optional, weil Listen es nicht laden."""
    provider_id: str
    record_id: str
    received_at: str
    source_timestamp: Optional[str]
    producer_kind: str
    producer_id: str
    instance_id: str
    scope: str
    channel: str
    level: str
    type: Optional[str]
    component: Optional[str]
    session_id: Optional[str]
    generation: Optional[int]
    activation_id: Optional[str]
    segment_id: Optional[int]
    transcription_id: Optional[str]
    command_id: Optional[str]
    event_id: Optional[str]
    correlation_id: Optional[str]
    server_cursor: Optional[int]
    replayed: bool
    message: Optional[str]
    details: Mapping[str, Any] = field(default_factory=dict)
    raw: Optional[Mapping[str, Any]] = None
    cursor: str = ""      # OPAKER Paginierungsschluessel DIESES Records


@dataclass(frozen=True)
class QueryPage:
    provider_id: str
    records: tuple[LogRecordView, ...]
    next_cursor: Optional[str]     # None = keine weitere Seite
    complete: bool                 # False, wenn der Provider abgeschnitten hat
    status: ProviderStatus


class LogProvider(Protocol):
    """Vier Methoden. Mehr braucht V1 nicht, und mehr wuerde spaetere
    Provider zwingen, Dinge zu implementieren, die sie nicht koennen."""

    @property
    def provider_id(self) -> str: ...

    def status(self) -> ProviderStatus:
        """Muss OHNE Netz- oder DB-Zugriff antworten koennen (gecacht).
        Die UI ruft es bei jedem Filterwechsel."""

    def query(self, filter: QueryFilter, cursor: Optional[str] = None,
              limit: int = 200) -> QueryPage:
        """Blockierend. Wird IMMER auf einem Worker-Thread gerufen.
        WIRFT NIE. Fehler kommen als QueryPage mit status.state == ERROR
        und leeren records zurueck."""

    def fetch_raw(self, record_id: str) -> Optional[Mapping[str, Any]]: ...


class LogQueryService:
    """Die einzige Schnittstelle, die die UI kennt."""
    def register(self, provider: LogProvider) -> None: ...
    def providers(self) -> tuple[ProviderStatus, ...]: ...
    def query(self, provider_id: str, filter: QueryFilter,
              cursor: Optional[str] = None, limit: int = 200) -> QueryPage: ...
    def fetch_raw(self, provider_id: str,
                  record_id: str) -> Optional[Mapping[str, Any]]: ...
```

## 8.1 Warum genau so – und was bewusst fehlt

| Entscheidung | Begründung |
|---|---|
| `cursor` als **opaker String** | Der lokale Provider kodiert die `id`, ein späterer Serverprovider `afterCursor`. Ein typisierter Integer-Cursor bildete eines von beidem falsch ab. |
| `query()` wirft **nie** | Ein Providerfehler ist ein Anzeigezustand, kein Programmfehler. Entspricht dem Repository-Muster (`history.get_persistent_entries` liefert `[]` bei Fehler). |
| `status()` **ohne I/O** | Die UI ruft es bei jedem Filterwechsel; ein Netzzugriff dort hielte die Oberfläche an. |
| **kein** `subscribe()`/`stream()` | Ein Provider ist eine Abfrage-, keine Abonnementschnittstelle. Der Live-Modus ist eine tailende **Abfrage** (siehe 9.2). |
| **kein** `count()` | Eine Gesamtzahl über 200.000 Zeilen kostet einen vollen Scan und wird für Keyset-Pagination nicht gebraucht. |
| **kein** `delete()`/`clear()` | Retention und Löschen sind Sache des Stores. Eine Löschfunktion in der Abfrageschnittstelle wäre für Remote-Provider unzulässig (O-14). |
| **kein** `ProviderCapabilities` in V1 | Genau ein Provider, der jeden Filter beantwortet; kein V1-Codepfad läse das Objekt. Additiv nachrüstbar, wenn der erste Provider entsteht, der nicht alles kann. |
| `scopes` als Ausdrucksmittel für „alle Sessions" | `scopes=("global",)` **bedeutet** die spätere Adminabfrage. Damit bleibt `session_id=None` eindeutig „ohne Einschränkung". Reine Festlegung, kein Umbau. |

---

# 9. UI-Verträge

## 9.1 Ort

| Gegenstand | Ort |
|---|---|
| Logging-Konfiguration | **sechster Tab „Logging & Diagnose"** im bestehenden `SettingsDialog` |
| Log View | **eigenes, nicht-modales `LogWindow`**, erreichbar über das Tray-Menü und über einen Knopf im Logging-Tab |
| Health-Anzeige | Statuszeile **im LogWindow** |

```text
Warum die Logansicht KEIN Settings-Tab ist:
 1. Der SettingsDialog ist ein QDialog mit Apply/Close-Buttonbox.
    "Uebernehmen" auf einer Abfrageseite ist bedeutungslos.
 2. Er wird einmal erzeugt und dauerhaft gehalten. Eine Logansicht mit
    Live-Aktualisierung wuerde dauerhaft im Hintergrund abfragen, obwohl
    sie unsichtbar ist.
 3. Diagnose geschieht typischerweise WAEHREND man Einstellungen aendert.
    Beides im selben modalen Fenster erzwingt ein Entweder-oder.
 4. Der Dialog ist auf 820x620 ausgelegt. Eine Logtabelle mit Detailbereich
    braucht eine eigene, frei skalierbare und speicherbare Geometrie.
 5. Der bestehende "Verlauf"-Tab zeigt, wohin das fuehrt: eine QTableWidget,
    die bei jedem Oeffnen ueber request_history(500) neu befuellt wird. Fuer
    200.000 Logzeilen ist dieses Muster nicht tragfaehig.
```

## 9.2 Bauform

```text
Qt-Mainthread
   LogWindow / LogPage / LogFilterBar / LogTableModel / LogDetailView
        |
        |  Signal filter_changed(QueryFilter)   (entprellt, 300 ms)
        v
LogQueryController (QObject, lebt im Qt-Thread)
        |  submit -> ThreadPoolExecutor(max_workers=1)
        v
Query-Worker-Thread
        LogQueryService -> LocalLogProvider -> eigene SQLite-Verbindung
                                               PRAGMA query_only = ON
        |
        |  Ergebnis per Signal (QueuedConnection)
        v
Qt-Mainthread: LogTableModel.append_page(...)
```

**Der Query-Layer läuft NICHT über `CoreBridge`.** `CoreBridge` gehört dem
Core-asyncio-Loop; eine SQLite-Leseabfrage hätte dort nichts zu suchen — sie
würde den Loop blockieren, auf dem Audio und WebSocket liegen.

```text
LIVE-MODUS  -- ohne Ringbuffer

    QTimer (250 ms) im LogPage stellt eine TAILENDE ABFRAGE ueber dieselbe
    Provider-Schnittstelle:
        WHERE id > :last  ORDER BY id  LIMIT 500
    auf dem Primaerschluesselindex, in WAL.

    KEIN Signal je Record: das waere bei Burst-Last eine Flut ueber
    QueuedConnection in den Qt-Loop -- dasselbe Frequenzproblem wie im
    Hot Path, nur in der UI.

    Damit benutzt der Live-Pfad dieselbe Abstraktion wie die Historie.
    Zusatznutzen: Bei totem Worker bleibt die Ansicht nutzbar und zeigt
    schlicht keine neuen Zeilen -- was der Wahrheit entspricht.
```

## 9.3 Umfang V1

| Punkt | Festlegung |
|---|---|
| Spalten | **sieben**: Zeit (`received_at`), Quelle (`producer_kind`), Channel, Level, Typ, Component, Meldung. Session/Activation/Segment nur im Detail und als Filter — die IDs sind Filterkriterien, keine Lesespalten. |
| Model/View | `QAbstractTableModel` + `QTableView`. **Erste Einführung dieses Musters im Repository** — das Repository kennt bisher nur itembasiertes `QTableWidget`, das bei Logdatenmengen nicht tragfähig ist. Deshalb bewusst klein halten. |
| Pagination | Keyset über `id`, Seitengröße 200, „Weitere laden" **und** automatisches Nachladen am Listenende |
| Modi | **Live** und **Historie** als Umschalter. **Kein Mischbetrieb in V1** — er müsste Live-Records gegen die geladene Seite deduplizieren und beim Filterwechsel neu einordnen; das ist der teuerste Teil einer Logansicht. |
| Auto-Scroll | umschaltbar, standardmäßig an; schaltet sich beim Hochscrollen ab |
| Detail | `QSplitter` unterhalb der Tabelle; `details` als Baum, `raw` als eingerücktes JSON, **bei Auswahl nachgeladen** |
| Kontextaktionen | Kontextmenü: „nur diese Session", „nur diese Activation" *(mit Hinweis auf Unzuverlässigkeit)*, „nur dieses Segment", „nur diesen Eventtyp" — setzt jeweils den Filter |
| Farben | nur Zeilenfarbe nach `level` (WARNING/ERROR/CRITICAL) |
| Export | **nicht in V1** |
| Fenster | `hide()` statt `close()`; Geometrie über `QSettings` |

---

# 10. Konfiguration

## 10.1 Schema – eingefroren

```yaml
logging:
  # bestehender Abschnitt bleibt UNVERAENDERT
  level: INFO
  log_dir: ...
  max_bytes: 5242880
  backup_count: 3
  stdout: true
  json_format: true
  channel_levels: {}

  # NEU: eigener Unterabschnitt
  observability:
    enabled: true
    level: INFO                        # speist Handler- UND Ingress-Level
    store_enabled: true
    db_path:                           # null = Standardpfad
    retention_days: 14
    max_entries: 200000
    max_db_bytes: 268435456            # reines Warnsignal
    queue_size: 8192
    batch_size: 200
    flush_interval_s: 0.5
    file_sink_enabled: false
    file_sink_dir:                     # null = <log_dir>/observability
    store_transcription_content: false
    store_raw_payload: true            # gilt nicht fuer channel "performance"
```

**Gestrichen gegenüber dem Entwurf:** `live_buffer_size` (kein Ringbuffer),
`queue_high_size`/`queue_low_size` (eine Queue), `file_sink_format`
(nur JSONL — ein Feld mit genau einer Option ist Überkonfiguration; es kehrt in
OBS-150 zurück, wenn ein zweites Format existiert).

```text
Warum ein Unterabschnitt und kein eigener Top-Level-Abschnitt:
  + Ein Nutzer, der "Logging" sucht, findet alles an einem Ort.
  + logging.level und logging.observability.level stehen sichtbar
    nebeneinander; ihre Verschiedenheit IST die Botschaft.
  + Keine Semantikaenderung an einem existierenden Feld -- ein bestehendes
    Benutzer-config.yaml bleibt gueltig, weil nur Felder HINZUKOMMEN.

Verworfen: die bestehenden Felder max_bytes, backup_count, json_format fuer
den neuen Sink umzudeuten. Das wuerde die Bedeutung vorhandener
Benutzerwerte still aendern.
```

## 10.2 Umsetzungsauflage im Configloader

`AppConfig._from_dict` baut `logging` heute über das generische `_build`, und
`_build` löst **verschachtelte Dataclasses nicht auf** (verifiziert in
`EV-02 / C-09`; `history` wird deshalb bereits gesondert gebaut).

```text
NORMATIV
  LoggingObservabilityConfig braucht dieselbe Sonderbehandlung wie history.
  Ohne sie waere das Feld vorhanden, traege aber IMMER die Defaultwerte --
  ein stiller Fehler, der erst im Betrieb auffiele.
  AppConfig.validate() ruft self.logging.observability.validate().
```

## 10.3 Settings-Einträge und Apply-Policies

```text
Kategorie "Logging & Diagnose" (sechster Tab):

  logging.observability.enabled                     BOOLEAN  IMMEDIATE
  logging.observability.level                       CHOICE   IMMEDIATE
  logging.observability.store_enabled               BOOLEAN  APP_RESTART
  logging.observability.retention_days              INTEGER  IMMEDIATE
  logging.observability.max_entries                 INTEGER  IMMEDIATE
  logging.observability.file_sink_enabled           BOOLEAN  IMMEDIATE
  logging.observability.file_sink_dir               STRING   IMMEDIATE
        visible_when=(logging.observability.file_sink_enabled, True)
  logging.observability.store_transcription_content BOOLEAN  IMMEDIATE
  logging.observability.store_raw_payload           BOOLEAN  IMMEDIATE

  + Schaltflaeche "Diagnosehistorie loeschen"
  + Schaltflaeche "Logs anzeigen" (oeffnet das LogWindow)

NUR in config.yaml, nicht im Dialog:
  db_path, queue_size, batch_size, flush_interval_s, max_db_bytes

Warum store_enabled und db_path APP_RESTART:
  Ein laufender Worker haelt eine offene SQLite-Verbindung. Sie im Betrieb
  zu wechseln erfordert Flush, Close, Reopen und Migration -- ein Fehlerpfad,
  den V1 nicht braucht.
```

## 10.4 Anbindung an die Apply-Kette

```text
core/controller.py :: apply_runtime_config
    nach _install_runtime_config(...) EINE Zeile:
        self.observability.apply_config(candidate.logging.observability)

    apply_config ist NICHT werfend und liefert nichts zurueck; ein Fehler
    dort darf das Apply-Ergebnis nicht beeinflussen.

HARTE REGEL
    Eine reine Observability-Aenderung darf KEINES der Flags
    session_changed, audio_changed oder mode_changed setzen und damit
    KEINEN Reconnect und KEINEN Audio-Neustart ausloesen.
    Nachweis: apply_runtime_config mit einer Fake-Session, deren
    reconfigure bei Aufruf durchfaellt.
```

## 10.5 Dokumentierte, nicht reparierte Altlast

`AppConfig._unknown_paths` verwirft den **kompletten** Benutzer-Override, sobald
ein Feld unbekannt ist. Wer nach dem Speichern einer neuen Konfiguration eine
**ältere** Clientversion startet, verliert alle Benutzereinstellungen still bis
auf eine `logger.error`-Zeile. Das ist heute schon so; die neuen Felder
verschärfen es lediglich.

**Nur dokumentieren, nicht reparieren.** Ein Test hält das Verhalten fest.

---

# 11. Sink- und Health-Verträge

## 11.1 JSONL-Sink

```text
Eine Zeile JSON je Record. schemaVersion als ERSTES Feld
(eine JSONL-Datei wird kontextlos gelesen).
Tagesrotation ueber den Dateinamen; Groessengrenze je Datei.
Verzeichnis: <log_dir>/observability oder file_sink_dir.

Reihenfolge im Worker: write_batch ZUERST, Sink DANACH -- damit ein
Sink-Fehler nie einen SQLite-Rollback ausloest.

Ein Fehler deaktiviert den Sink, meldet EINMAL an Health und laesst den
Store unberuehrt.
```

## 11.2 Health

```python
class LoggingHealthState(str, Enum):
    OK = "ok"; DROPPING = "dropping"
    DEGRADED_SINK = "degraded_sink"; DEGRADED_STORE = "degraded_store"
    FAILED_STORE = "failed_store"; FAILED_WORKER = "failed_worker"
    DISABLED = "disabled"


@dataclass(frozen=True)
class LoggingHealthSnapshot:
    state: LoggingHealthState
    since: Optional[float]          # time.monotonic()
    detail: str                     # kurz, REDIGIERT
    enqueued: int
    written: int
    deduplicated: int               # <- fehlte im Entwurf, siehe Arch §7.3
    dropped_watermark: int
    dropped_queue_full: int
    dropped_shutdown: int
    malformed: int
    store_errors: int
    sink_errors: int
    retention_errors: int
    worker_errors: int
    queue_depth: int
    db_bytes: Optional[int]
```

```text
AUSGABEWEGE
  stderr    ratenbegrenzt, "[observability] <code> (xN): <detail>".
            Der einzige Weg, der ohne funktionierende Infrastruktur traegt.
  UI        Die Statuszeile des LogWindow POLLT den Snapshot (QTimer, 1 s).
            Kein Signal je Fehler -- sonst wiederholt sich das
            Frequenzproblem. Vorbild: der bestehende QTimer, der die
            LED-Verfuegbarkeit pollt.
  Counters  Ueber snapshot() abrufbar, auch fuer Tests. Die Tests pruefen
            ZAEHLER, nicht Logausgaben.
  Recovery  Automatisch und still. Nach Rueckkehr in OK genau EIN Record
            logging.recovered mit den Zaehlern seit Fehlerbeginn, geschrieben
            vom Worker. Kein Dialog, keine Tray-Benachrichtigung: eine
            defekte Diagnose ist kein Ereignis, das ein Diktat unterbrechen
            darf.

GRENZE  Der Health-State wird NICHT persistiert. Nach einem Neustart ist er
        OK, bis der erste Fehler erneut auftritt. Eine Persistenz braeuchte
        einen zweiten Speicher, der dieselben Fehler haben kann.
```

---

# 12. V1-Observation-Hooks – die verbindliche Liste

**Legende.** `P` = bestehende Python-Logzeile genügt (der Handler fängt sie).
`S` = zusätzliches strukturiertes Event. `P+S` = beides; die bestehende
`logger.*`-Zeile wird **nicht** entfernt und **nicht** umformuliert.

## 12.1 Lifecycle und Transport – Channel `system`

| Typ | Ort | Art |
|---|---|---|
| `client.app.started` | `ui/application.py` `start()` | S |
| `client.app.stopping` | `ui/application.py` `shutdown()` | S |
| `client.core.thread_started` / `.thread_stopped` | `ui/core_bridge.py` | P+S |
| `client.controller.run_started` | `core/controller.py` `run()` | S |
| `client.controller.shutdown_*` | `core/controller.py` `_do_shutdown` | P |
| `client.websocket.connecting` / `.connected` / `.disconnected` | `core/stt_session.py` `_update_transport`, `_record_failure` | P+S |
| `client.session.admitted` | `core/stt_session.py` `_wait_for_hello` | P+S |
| `client.session.ready` | `core/stt_session.py` `_wait_for_ready` | S |
| `client.reconnect.scheduled` | `core/stt_session.py` | P+S |
| `client.eventstream.state_changed` | `core/session_coordinator.py` `_handle_state` | S |
| `client.eventstream.gap` / `.error` / `.replay_completed` | über den Fan-out-Hook | S |
| `client.eventstream.protocol_error` | `core/event_stream.py` `run()`, except-Zweig | S |
| `client.config.validation_failed` | `core/config.py`, `ui/settings_dialog.py` | P+S |
| `client.config.loaded` | `core/config.py` | P (Pfade nach R-9) |

## 12.2 Absichtliche Handlungen – Channel `audit`

| Typ | Ort | Art |
|---|---|---|
| `client.hotkey.pressed` | `ui/hotkeys.py` — **heute völlig ungeloggt** | S |
| `client.command.requested` / `.completed` | `ui/core_bridge.py`, gemeinsame `correlation_id` | S |
| `client.trigger.sent` | `core/stt_session.py` `send_trigger` | P+S |
| `client.trigger.ack_received` | `core/stt_session.py` `_resolve_trigger_ack` | S |
| `client.trigger.ack_dropped` | `core/stt_session.py` | P+S |
| `client.stream.start_sent` | `core/stt_session.py` | P+S |
| `client.dictation.start_attempt` / `.confirmed` / `.failed` | `core/controller.py` | S |
| `client.dictation.interrupted` | `core/controller.py` | P+S |
| `client.settings.apply_started` / `.completed` | `ui/application.py`, gemeinsame `correlation_id` | S |
| `client.settings.runtime_apply` | `core/controller.py` `apply_runtime_config`, dieselbe `correlation_id` | S |
| `client.action.blocked` | `core/controller.py` `_emit_feedback_event` | S |
| `client.audio.stream_started` / `.stream_stopped` | `core/audio_capture.py` | P+S |

## 12.3 Transkript – Channel `transcription`

| Typ | Ort | Art |
|---|---|---|
| `client.injection.enqueued` / `.rejected` | `core/controller.py` | P+S |
| `client.final.deduplicated` | `core/controller.py` — **redaktionspflichtig**, loggt heute beide vollständigen Texte auf WARNING | P+S |
| `client.history.persist_failed` | `core/history.py` | P |

## 12.4 Zahlen – Channel `performance`

| Typ | Ort | Art |
|---|---|---|
| `client.audio.stream_stats` | **vom Worker** aus Zählern erzeugt, alle 5 s | S, aggregiert |
| `client.queue.state` | Injection-Worker, periodisch | S, aggregiert |
| `logging.records_dropped` / `logging.recovered` / `logging.retention_pressure` / `logging.record_rejected` | vom Worker | S, intern |

## 12.5 Feedback und Ausgabe – Channel `system`

| Typ | Ort | Art |
|---|---|---|
| `client.feedback.decision` | `ui/application.py` `_log_feedback_decision` — **bereits strukturiert**, das Vorbild; bleibt unverändert und wird nur zusätzlich erfasst | P+S |
| `client.led.dispatch_failed` / `.queue_overflow` | `ui/led_feedback.py` | P+S |
| `client.sound.failed` | `ui/application.py` | P+S |
| `client.server.error_classified` | `core/controller.py` `_handle_error_event` | P+S |

## 12.6 Reihenfolge der Umsetzung – nach aufsteigendem Risiko

```text
1. ui/hotkeys.py, ui/core_bridge.py, ui/application.py
       reine UI-Beobachtung, kein fachlicher Zustand
2. core/audio_capture.py
       NUR Start/Stop plus Zaehlerattribute; die Hot-Path-Methoden erhoehen
       ausschliesslich int-Attribute
3. core/stt_session.py
4. core/controller.py

Ein Abbruch nach Stufe 3 hinterlaesst einen sinnvollen Zwischenstand.
Dies ist der einzige Querschnitt des ganzen Vorhabens (sechs Produktdateien
gleichzeitig) und unvermeidbar, weil Beobachtungspunkte per Definition
verteilt sind.
```

## 12.7 Nicht instrumentiert

- `app.py`-`print()` im Headless-Diagnosemodus: Das ist die **Ausgabe** dieses
  Modus, kein Log. Unverändert lassen.
- Alle in `LOGGING_ARCHITEKTUR_FREEZE_V1.md §8.6` genannten Hot-Path-Funktionen:
  ausschließlich Zähler.
- `realtime`-Events: **kein** strukturierter Record. Der bestehende DEBUG-Log
  bleibt und wird vom Handlerlevel gefiltert.
- Module ohne Logging (`event_models`, `event_protocol`, `event_normalizer`,
  `feedback_reducer`, `feedback_mapping`, `settings_metadata`, `actions`,
  `version`): bewusst rein, nicht ändern.

---

# 13. Wiederverwendung statt Neuerfindung

Diese vorhandenen Muster sind zu übernehmen, nicht neu zu erfinden:

| Vorhanden | Wofür |
|---|---|
| `logging_setup.setup_logging` | bleibt vollständig; ein dritter Handler wird additiv ergänzt |
| Der `extra`-Vertrag aus `JsonFormatter` (`session_id`, `segment_id`, `event_type`, `detail`) | bestehender Vertrag, wird übernommen und erweitert |
| `EventEnvelope` / `EventProtocolResult` / `EventProtocolProcessor` | liefern Envelope, Rohpayload, Cursor, Replayflag und Dedupe unverändert — **keine Änderung nötig** |
| `EventCursorStore` | Muster für atomares Schreiben (`NamedTemporaryFile` + `fsync` + `os.replace`), `schema_version`, strikte Validierung, **Verwerfen statt Reparieren** |
| `TranscriptHistoryManager` | Muster für `ON CONFLICT DO NOTHING`, Kontextmanager mit commit/rollback/close, „Init-Fehler deaktiviert die Persistenz statt die Anwendung zu stoppen" |
| `LedFeedback` | Muster für bounded Queue, Coalescing, „einmal melden", Dauer als abfragbare Zahl, Daemon-Thread mit Timeout-Join |
| `CoreBridge` | Muster für den Thread→Qt-Übergang mit `QueuedConnection` |
| `settings_metadata` + `SettingsDialog` | ein neuer Tab kostet nur Metadaten, keinen Dialogcode |
| `apply_runtime_config` + Rollback | nimmt eine zusätzliche Zeile auf |
| Testkonventionen (`unittest`, `ScriptedLogSocket`, offscreen-Qt) | direkt übertragbar |

**Ausdrücklich NICHT übernehmen** (Antimuster aus `TranscriptHistoryManager`):
neue `sqlite3.connect()` je Operation · kein WAL, kein `busy_timeout` ·
`cleanup()` nach jedem Insert · `with self._get_connection()` (der
sqlite3-Kontextmanager committet, **schließt aber nicht** — Verbindungsleck) ·
kein `schema_version` · Dedupe-Cache, der beim Start alle Schlüssel in den
Speicher lädt.
