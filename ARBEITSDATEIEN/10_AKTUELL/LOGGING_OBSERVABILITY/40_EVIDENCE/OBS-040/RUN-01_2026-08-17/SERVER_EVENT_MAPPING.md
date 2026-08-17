---
id: EV-OBS-040-SERVER-EVENT-MAPPING
run: RUN-OBS-040-01_2026-08-17
work_package: OBS-040
authority: evidence
date: 2026-08-17
---

# OBS-040 – Abbildung der Serverereignisse auf das kanonische Modell

Maßstab: `LOGGING_CONTRACTS_FREEZE_V1.md §3.2`. Die Abbildung selbst wurde in
OBS-010 implementiert (`core/observability/normalizer.py`) und dort
gate-geprüft; OBS-040 **verdrahtet** sie erstmals mit dem echten
Eventstream und weist nach, dass die Abbildung am realen Ergebnis des echten
`EventProtocolProcessor` stimmt. Am Normalizer wurde in diesem Run **keine
Zeile geändert**.

## 1. Der Weg eines Serverereignisses

```text
/ws/logs Textframe
   │
   ▼
EventStreamTransport._receive_result
   └─ EventProtocolProcessor.process_frame   Validierung, Dedupe-Entscheidung,
      │                                       Cursorbuchführung, replay-Flag
      ▼
EventStreamTransport._dispatch
   ├─ EVENT, nicht duplicate ──► on_event  ─► DualSessionCoordinator._handle_event
   ├─ EVENT, duplicate       ──► on_control ─► DualSessionCoordinator._handle_control
   └─ CONTROL                ──► on_control ─► DualSessionCoordinator._handle_control
                                                │
                                    ERSTE Anweisung beider Methoden:
                                                │
                                    _notify_observer(result)
                                                │
                                    ┌───────────┴───────────┐
                                    ▼                       ▼
                        ServerLiveAdapter.observe    (unverändert weiter:
                                    │                 Bindings-/Token-/
                                    ▼                 Sessionprüfung, on_event,
                        Ingress.observe_server_result  Feedbackzweig, Cursor)
                                    │
                                    ▼
                        normalizer.from_server_result
                                    │
                                    ▼
                        Ingress.submit  →  Queue  →  LoggingWorker  →  SQLite
```

Das ist ein echtes Fan-out (O-02): der Feedbackzweig läuft unverändert über
`on_event`, und die Beobachtung liefert keinen Rückgabewert, der irgendetwas
davon beeinflussen könnte (O-01).

## 2. EVENT-Ergebnisse – Feldabbildung, am echten Ergebnis geprüft

Prüfframe (`tests/test_obs040_server_live_adapter.py::envelope`):

```json
{
  "schemaVersion": 1, "eventId": "evt-5", "cursor": 5,
  "timestamp": "2026-08-09T12:00:00Z", "channel": "transcription",
  "event": "transcription.completed", "severity": "info",
  "serverInstanceId": "server-1", "sessionId": "session-1", "segmentId": 7,
  "transcriptionId": "session-1:3:7",
  "data": {"reason": "done", "activationId": "act-9"},
  "meldung": "Transkription abgeschlossen"
}
```

`SessionContext(generation=3, session_id="session-1")`.

| Kanonisches Feld | §3.2-Regel | Beobachteter Wert | Geprüft in |
|---|---|---|---|
| `producer_kind` | `"server"` | `server` | `test_live_event_maps_every_frozen_field` |
| `producer_id` | `"voice-stt-server"` | `voice-stt-server` | dto. |
| `instance_id` | `envelope.server_instance_id` | `server-1` | dto. |
| `scope` | `"session"` wenn `session_id` gesetzt, sonst `"global"` | `session` | dto. + `test_control_frame_without_session_is_scope_instance` |
| `channel` | `envelope.channel` | `transcription` | dto. |
| `level` | normalisiert aus `envelope.severity` (§2.1) | `INFO` | dto., `test_warning_severity_is_mapped_and_ranks_as_high` |
| `type` | `envelope.event` | `transcription.completed` | dto. |
| `component` | Namensraumpräfix von `type`, **nicht** aus `transport` | `transcription` | dto. |
| `session_id` | `envelope.session_id` | `session-1` | dto. |
| `generation` | `context.generation` (aus dem `SessionContext`) | `3` | dto. |
| `activation_id` | **ausschließlich** `envelope.data.activationId` | `act-9` | dto. |
| `segment_id` | `envelope.segment_id`, lokal **INTEGER** | `7` (`isinstance(int)`) | `test_segment_id_is_stored_as_integer_...` |
| `transcription_id` | `envelope.transcription_id` | `session-1:3:7` | dto. |
| `event_id` | `envelope.event_id` | `evt-5` | dto. |
| `server_cursor` | `envelope.cursor` | `5` | dto. |
| `message` | `envelope.extra["meldung"]` (Befund C-2) | `Transkription abgeschlossen` | dto. |
| `details` | `envelope.data`, redigiert | `{reason, activationId}` | dto. |
| `raw` | `result.payload`, **entfroren erst im Worker** | identisch mit `result.payload` (`is`) | `test_raw_is_the_frozen_reference_and_is_not_copied` |
| `replayed` | `result.origin is EventOrigin.REPLAY` | `False` | dto. |
| `command_id` | nur Client | `None` | Probe P-1 |
| `correlation_id` | clientseitig gebildet | `None` für Serverevents | Probe P-1 |

Zusätzlich am **echten Store** verifiziert (Probe P-1): dieselben Werte stehen
nach dem Workertakt so in `logs`.

### Severity

`severity` ist serverseitig **kein** geschlossenes Enum; der Normalizer ruft
deshalb nie `Level(value)`.

```text
severity = "info"     -> level = "INFO"
severity = "warning"  -> level = "WARNING",  priority = HIGH
severity = "notice"   -> level = "INFO",     details["source_severity"] = "notice"
```

Geprüft in `test_unknown_severity_falls_back_to_info_and_keeps_the_original`.

### `raw` und `store_raw_payload`

| Bedingung | `raw` |
|---|---|
| `store_raw_payload = true`, Channel ≠ `performance` | `result.payload`, **identische Referenz**, nicht kopiert (ARCH §8.2) |
| `store_raw_payload = false` | `None` (`test_store_raw_payload_false_stores_no_raw`) |
| Channel `performance` | immer `None` (FD-D2, `test_performance_channel_never_carries_raw`) |
| `log.hello` | **immer** `None`; ausschließlich Whitelist nach R-6 |

Entfrieren, Serialisieren, Redigieren und die 64-KiB-Grenze bleiben Sache des
Workers (OBS-030, `_prepare_record`) — OBS-040 hat daran nichts geändert.

## 3. CONTROL-Ergebnisse

| Serverframe | `type` | `producer_kind` | `component` | `level` | `raw` |
|---|---|---|---|---|---|
| `log.hello` | `client.eventstream.hello` | `client` | `eventstream` | `INFO` | **nie** (R-6-Whitelist) |
| `log.subscribed` | `client.eventstream.subscribed` | `client` | `eventstream` | `INFO` | `result.payload` |
| `log.gap` | `client.eventstream.gap` | `client` | `eventstream` | `WARNING` | `result.payload` |
| `log.error` | `client.eventstream.error` | `client` | `eventstream` | `WARNING` | `result.payload` |
| `log.replay_completed` | `client.eventstream.replay_completed` | `client` | `eventstream` | `INFO` | `result.payload` |
| `log.pong` | `client.eventstream.pong` | `client` | `eventstream` | `INFO` | `result.payload` |
| `log.keepalive` | `client.eventstream.keepalive` | `client` | `eventstream` | `INFO` | `result.payload` |
| EVENT mit `duplicate=True` | `client.eventstream.event` | `client` | `eventstream` | `INFO` | `result.payload` |

`component` ist für Controlframes **fest** `"eventstream"` (FD-R7): die Regel
„Namensraumpräfix von `type`" hätte hier `"client"` ergeben — als Filterwert
nutzlos.

`instance_id` ist bei Controlframes die **Client**-Instanz, nicht die des
Servers (`test_control_frames_take_the_client_instance_id`, Probe P-4).

### `log.hello` – die Whitelist

Der Prüfframe enthält bewusst `logAccess.accessToken`. Beobachtet:

```text
details = {sessionId?, sessionConfig, activationConfig?, sessionCapabilities?,
           logAccess = {available, code?, reason?, expiresAt?,
                        logProtocolVersion?, serverInstanceId,
                        oldestCursor, latestCursor}}
raw     = None
```

`accessToken` ist **nicht** enthalten; `test_hello_is_whitelisted_and_never_stores_raw`
prüft zusätzlich, dass der Tokenwert in keiner Repräsentation der `details`
auftaucht. Probe P-6 prüft dasselbe über **jede** Zeile der echten
Probe-Datenbank (`details_json`, `raw_json`, `message`).

### `log.gap(reason=retention)`

Endgültiger serverseitiger Datenverlust. Wird als eigener Record
`client.eventstream.gap` mit `lostFromCursor`/`lostToCursor` gespeichert, damit
die Lücke in der lokalen Historie **sichtbar** bleibt statt stillschweigend zu
fehlen (`test_gap_keeps_the_lost_cursor_range_visible`).

## 4. replayed, Priorität und Dedupe

```text
replayed = (result.origin is EventOrigin.REPLAY)

HIGH := is_internal
     OR ( NOT replayed
          AND ( level >= WARNING OR channel == "audit" OR type is not None ) )
```

| Fall | `replayed` | `priority` | Geprüft in |
|---|---|---|---|
| Replayphase, `transcription.completed` | `True` | **LOW** | `test_replayed_event_is_marked_and_ranks_as_low` |
| Livephase, identische Form | `False` | HIGH | `test_live_event_of_the_same_shape_ranks_as_high` |
| Serverevent `severity=warning`, live | `False` | HIGH | `test_warning_severity_is_mapped_and_ranks_as_high` |
| Logging-eigener Record | – | HIGH (`is_internal`) | `test_adapter_emits_exactly_one_record_rejected_...` |

Die Wirksamkeit des Flutschutzes ist gemessen, nicht behauptet: 20 replayte
Events auf eine Queue der Größe 8 ergeben `dropped_watermark > 0` und
`enqueued <= 8` (`test_replayed_low_records_are_dropped_above_the_watermark`).

### Dedupe – die korrigierte Testerwartung (W-9)

Verbindlich ist: *„Ein Duplikat erzeugt **keinen** Record mit `replayed=True`.
Es wird beobachtet, normalisiert und an den Store übergeben; der Store fügt
**keine** zweite Zeile ein; `deduplicated` steigt."*

Beobachtet (`test_duplicate_is_observed_but_produces_no_second_stored_row`,
Probe P-2):

| Schritt | Ergebnis |
|---|---|
| Live-Event `evt-5`, bestätigt | ein Record, `event_id="evt-5"`, `replayed=False` |
| dasselbe `evt-5` erneut | `result.duplicate is True`; der Normalizer nimmt den **CONTROL**-Pfad: `producer_kind=client`, `component=eventstream`, `event_id=None`, `replayed=False` |
| Store | `SELECT ... WHERE event_id='evt-5'` liefert **eine** Zeile |
| Zähler | `deduplicated` steigt (Probe P-2: von 0 auf 1) |

Dass das Duplikat den CONTROL-Pfad nimmt, ist die Ursache dafür, dass der
partielle UNIQUE-Index `(producer_id, event_id)` es nicht mit der Originalzeile
verschmelzen kann: ein Clientrecord hat nach §1.1 **immer** `event_id = None`,
und der partielle Index greift für `NULL` nicht. Die Duplikatsbeobachtung bleibt
damit als eigene Zeile erhalten — genau die diagnostische Aussage „der Server
hat es erneut geschickt".

### Cursor- und Instanzordnung

`server_cursor` wird nie ohne `instance_id` verglichen. Über einen
Replay-plus-Live-Verlauf beobachtet: `event_id` `["evt-6", "evt-7"]`,
`server_cursor` `[6, 7]`, `instance_id` einheitlich `{"server-1"}`
(`test_event_id_is_stable_across_live_and_replay_of_the_same_event`).

## 5. Der Beobachter berührt den Cursor nicht

Mit **echtem** `EventCursorStore` auf einer temporären Datei
(`test_observation_neither_commits_nor_advances_the_cursor`, Probe P-3):

| Schritt | `resume_cursor` | Cursordatei |
|---|---|---|
| nach `_handle_event` inkl. Beobachtung | `0` bzw. unverändert | existiert nicht / unverändert |
| nach `processor.confirm_event(result)` | `5` bzw. `6` | existiert, neu geschrieben |

Und mit einem **werfenden** Beobachter (N-07, Probe P-3): Rückgabewert von
`_handle_event` identisch `True`, `resume_cursor` vor und nach dem Dispatch
identisch, Cursordateiinhalt byte-identisch, der Feedbackzweig genau einmal
gelaufen. Erst das anschließende, explizite `confirm_event` bewegt den Cursor.

## 6. Was OBS-040 am Serverpfad ausdrücklich **nicht** tut

- keine Änderung an `core/event_protocol.py`, `core/event_models.py`,
  `core/event_normalizer.py` (unverändert, per Contract-Test belegt)
- keine Änderung am Normalizer der Observability-Domäne
- keine Rekonstruktion von Lifecycle aus Logtext (`message` wird nie
  zurückgeparst, O-06)
- kein Eingriff in Session-, Eventstream-, Cursor- oder Reconnect-Mechanismen
- kein Lesen von `SessionContext.log_access` und damit nie des Session-Log-Tokens
  (per AST-Contract-Test über alle Module unter `core/observability/`)
- keine Vorwegnahme von Remote-History oder Admin-Control aus OBS-100+
