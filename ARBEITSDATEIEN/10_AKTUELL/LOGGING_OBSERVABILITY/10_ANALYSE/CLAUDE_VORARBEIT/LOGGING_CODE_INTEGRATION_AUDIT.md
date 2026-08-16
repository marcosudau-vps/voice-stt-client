# LOGGING_CODE_INTEGRATION_AUDIT

**Auftrag:** `ARBEITSDATEIEN/Implementierungsdateien/prompts/006_Vorbereitung_Logging.md`
**Primäre Quelle:** ausgeführter Produktivcode der drei Repositories. Tests und
Dokumentation nur ergänzend.
**Arbeitsregeln eingehalten:** keine Produktcode-, Test-, Config- oder
Produktdokumentationsänderung; kein Commit, Push, Merge, Rebase, Tag, PR.
Sämtliche Artefakte liegen unterhalb von `ARBEITSDATEIEN/AP_THEMA_LOGGING/analyse_code_integration/`.

Deckt Auftragsabschnitte **1, 2, 3, 4, 6, 12, 17**.

---

# 1. Bestehendes Client-Logging – vollständige Inventarisierung

## 1.1 Initialisierung

`voice-stt-client/core/logging_setup.py` ist der einzige Ort, an dem Handler
gesetzt werden. Aufgerufen wird er genau einmal, in `app.py:148`
(`main()` → `setup_logging(config.logging)`), **vor** der Verzweigung in
GUI oder Headless. Es gibt keinen zweiten Initialisierungspfad und kein
`basicConfig` im Produktivcode.

| Aspekt | Ist-Zustand | Beleg |
|---|---|---|
| Root-Level | `logging.DEBUG` fest; Filterung ausschließlich in den Handlern | `logging_setup.py:74` |
| Vorhandene Handler werden gelöscht | ja, `root_logger.handlers.clear()` | `logging_setup.py:77` |
| Datei-Handler | `RotatingFileHandler(log_dir/"client.log", maxBytes=5 MiB, backupCount=3, encoding=utf-8)` | `logging_setup.py:80-92`, Defaults `config.py:793-794` |
| Log-Verzeichnis | `%LOCALAPPDATA%\RealtimeSTT Client\logs` | `config.py:33-34` |
| Stdout-Handler | optional über `logging.stdout` (Default `True`) | `logging_setup.py:95-99` |
| Formatter Datei | `JsonFormatter` (JSON Lines) wenn `logging.json_format` (Default `True`), sonst `ReadableFormatter` | `logging_setup.py:88-91` |
| Formatter Stdout | immer `ReadableFormatter`, `"%(asctime)s │ %(levelname)-5s │ %(name)-12s │ %(message)s"` | `logging_setup.py:51-58` |
| Per-Channel-Level | nur für die fünf Namen in `CHANNELS` | `logging_setup.py:23`, `:102-108` |
| Dämpfung Dritter | `websockets`, `PIL`, `pystray` → `WARNING` | `logging_setup.py:111-112` |

**Befund L-1.** `CHANNELS = ("connection", "audio", "text", "app", "overlay")`
deckt die real vergebenen Loggernamen **nicht** ab. `controller`,
`event_stream`, `ui.*`, `core.led_controller` und die `__name__`-Logger sind
über `channel_levels` nicht einstellbar. Sie erben faktisch DEBUG vom Root und
werden erst im Handler gefiltert. Kein Fehler, aber die vorhandene
„Channel"-Idee des Clients ist unvollständig und **nicht** deckungsgleich mit den
Server-Channels (§6).

**Befund L-2.** `JsonFormatter` transportiert bereits strukturierte Zusatzfelder,
aber nur eine feste Whitelist: `session_id`, `segment_id`, `event_type`,
`detail` (`logging_setup.py:39`). Das ist der einzige heute existierende
`extra`-Vertrag.

## 1.2 Logger-Hierarchie (real vergebene Namen)

```text
root  (Level DEBUG, zwei Handler)
├── app                     app.py:28
├── connection              core/stt_session.py:34
├── audio                   core/audio_capture.py:24
├── text                    core/history.py:44, core/reinsertion.py:20,
│                           core/text_injector.py:27   (drei Module, ein Name)
├── controller              core/controller.py:48
├── event_stream            core/event_stream.py:27
├── overlay                 (in CHANNELS deklariert, von keinem Modul benutzt)
├── core.config             core/config.py:26            (__name__)
├── core.event_cursor_store core/event_cursor_store.py:17 (__name__)
├── core.session_coordinator core/session_coordinator.py:26 (__name__)
├── core.led_controller     core/led_controller.py:24
├── ui.application          ui/application.py:40
├── ui.core_bridge          ui/core_bridge.py:18
├── ui.feedback             ui/feedback.py:16
├── ui.hotkeys              ui/hotkeys.py:16
├── ui.led_feedback         ui/led_feedback.py:34
├── ui.single_instance      ui/single_instance.py:13
└── lefx.*                  (In-Process-Bibliothek, siehe §17)
```

Drei Namensschemata nebeneinander: fachliche Kanalnamen (`audio`, `text`),
Modulnamen (`__name__`), UI-Präfixe (`ui.*`). Für die Ableitung von
`component` (§5) ist der Loggername brauchbar, für die Ableitung von `channel`
**nicht**.

## 1.3 Komponentenübersicht

| Komponente | heutiges Logging | Logger | strukturierte Daten? | Frequenz | geeignet für Unified Handler? |
|---|---|---|---|---|---|
| `app.py` Einstieg/Headless | `print()` für Konsolenausgabe, sonst nichts | `app` (definiert, ungenutzt) | nein | einmalig | ja, aber die `print()` bleiben (§1.5) |
| `core/stt_session.py` Transport/Reducer | 53 Aufrufe, INFO für Lifecycle, WARNING/ERROR für Fehler, DEBUG für Realtime | `connection` | nein (Textinterpolation) | mittel; DEBUG pro Realtime-Segment | ja – **wichtigste Quelle**, aber ein Teil gehört in strukturierte Events |
| `core/controller.py` Orchestrierung | 58 Aufrufe, sehr breit gestreut | `controller` | nein | mittel | ja |
| `core/text_injector.py` Injektion | 29 Aufrufe, Worker-Lifecycle + Clipboard | `text` | nein | niedrig | ja |
| `core/history.py` SQLite-Historie | 22 Aufrufe, DB-Init/Fehler/Cleanup | `text` | nein | niedrig | ja |
| `core/reinsertion.py` | 16 Aufrufe | `text` | nein | niedrig | ja |
| `core/audio_capture.py` | 13 Aufrufe; **4 davon im Hot Path** | `audio` | nein | Start/Stop niedrig, Overflow/Drop potenziell hoch | ja, aber Hot-Path-Zeilen nur aggregiert (§4) |
| `core/event_stream.py` Transport `/ws/logs` | 3 Aufrufe (Attempt-Fehler, Close, State-Callback) | `event_stream` | nein | niedrig | ja |
| `core/session_coordinator.py` | 2 Aufrufe (Task-Ende, Context-Callback-Fehler) | `core.session_coordinator` | nein | sehr niedrig | ja – auffällig wenig für die zentrale Lifecycle-Klasse |
| `core/config.py` Laden/Speichern | 5 Aufrufe | `core.config` | nein | einmalig | ja, **enthält Pfade** (§12) |
| `core/event_cursor_store.py` | 3 Aufrufe (ungültige/fremde Cursordatei) | `core.event_cursor_store` | nein | selten | ja |
| `core/led_controller.py` | 7 Aufrufe | `core.led_controller` | nein | niedrig | ja |
| `core/event_models.py`, `event_protocol.py`, `event_normalizer.py`, `feedback_reducer.py`, `feedback_mapping.py`, `settings_metadata.py`, `actions.py`, `version.py` | **kein Logging** | – | – | – | bewusst rein; nicht ändern |
| `ui/application.py` | 20 Aufrufe, darunter **die einzige echte `extra=`-Nutzung** | `ui.application` | **ja**, `_log_feedback_decision` (`:266-299`) | je Feedback-Decision, also mittel | ja – Vorbild für den strukturierten Weg |
| `ui/core_bridge.py` | 13 Aufrufe, Thread-/Command-Lifecycle | `ui.core_bridge` | nein | niedrig | ja |
| `ui/led_feedback.py` | 10 Aufrufe, „einmal melden"-Muster | `ui.led_feedback` | nein | niedrig (bewusst entprellt) | ja |
| `ui/hotkeys.py` | 5 Aufrufe (Registrierung) | `ui.hotkeys` | nein | einmalig | ja; **Hotkey-Auslösung wird heute nicht geloggt** |
| `ui/single_instance.py` | 2 Aufrufe | `ui.single_instance` | nein | einmalig | ja |
| `ui/tray.py`, `settings_dialog.py`, `presentation.py`, `overlay.py` | **kein Logging** | – | – | – | UI-Aktionen sind heute unsichtbar |

## 1.4 Klassifikation der vorhandenen Logzeilen

```text
gewöhnliche technische Logs
    Verbindungsaufbau/-abbau, Backoff, Handler-Registrierung, Konfigladen,
    Queue-Worker-Lifecycle, DB-Initialisierung.
    → gehören unverändert über den UnifiedLogHandler.

fachlich interessante Observability-Events (heute nur als Text vorhanden)
    stt_session:  "Sent start command." (:734), "Sent trigger command:
                  action=%s source=%s commandId=%s" (:787), "Session admitted:
                  id=%s (gen %d)" (:1077), "Transport state: %s" (:1339),
                  "Dropping trigger_ack ... generation" (:847)
    controller:   "Server rejected the manual trigger: reason=%s commandId=%s"
                  (:707), "Dictation interrupted (reason: %s)." (:2484),
                  "Successfully enqueued final segment %s (entry_id=%s)" (:2209),
                  "Server error classified without transport reset: where=%s
                  count=%d message=%s" (:1969)
    session_coordinator: "Event stream task ended: %s" (:376)
    → Diese Zeilen sind heute die EINZIGE Quelle für commandId, generation und
      Ablehnungsgrund. Sie müssen zusätzlich als strukturierte Events entstehen,
      damit Diagnosedaten nicht aus Text zurückgeparst werden müssen (Zielbild §10).

hochfrequente Performance-/Audio-Ereignisse   -> HOT PATH
    audio_capture:  "Audio input overflow." / "underflow" (:250-252),
                    "Audio queue full, dropping chunk." (:260)
    stt_session:    "Realtime [seg=%s]: %s" DEBUG (:1303)
    controller:     "Audio send error" DEBUG mit exc_info (:2593)
    → Diese Stellen dürfen den Unified-Weg nur als Zähler/Zustandswechsel
      erreichen, niemals als Zeile pro Chunk (§4).

Fehler-/Exception-Pfade
    Durchgehend `logger.exception(...)` in Callback-Wrappern:
    controller.py:470, :484, :505, :2235, :2371, :2456, :2471;
    stt_session.py:1266, :1282, :1320, :1331, :1338;
    session_coordinator.py:465; event_stream.py:333;
    ui/application.py:333, :526, :612, :629; ui/core_bridge.py:122, :184, :203,
    :261, :359, :405; ui/led_feedback.py:191, :449.
    → Vorbildlich einheitlich. Der Handler bekommt `exc_info` bereits geliefert;
      der Normalizer muss `formatException` in `details.exception` überführen.
```

## 1.5 `print()` und sonstige Nebenwege

`print()` existiert ausschließlich in `app.py` (Zeilen 71, 83, 95-99, 110) und
ausschließlich im **Headless-Diagnosemodus** bzw. im Startbanner. Es gibt keinen
`sys.stdout.write`, kein `warnings.warn` und keinen zweiten Logging-Nebenweg im
Client.

**Empfehlung:** unverändert lassen. Der Headless-Modus ist ein
Diagnosewerkzeug; seine Konsolenausgabe ist die Ausgabe, nicht ein Log. Eine
Umstellung auf Logging würde Verhalten ändern, ohne Nutzen für die
Observability-Historie.

---

# 2. Bestehende Server-Eventstream-Integration

## 2.1 Der reale Pfad, Station für Station

```text
Server  api_fastapi_server/server.py:6479  websocket_logs()
   │      subscribe → log.hello → log.subscribed → log.event* →
   │      log.replay_completed → live log.event* / log.keepalive / log.pong
   ▼
Client  core/event_stream.py  EventStreamTransport
   │      _connect_once   :187   Generation++, begin_subscription() → resume cursor
   │      _run_handshake  :225   SUBSCRIBING bis log.subscribed
   │      _run_replay     :240   REPLAYING bis log.replay_completed
   │      _run_live       :257   LIVE, Ping bei message_timeout
   │      _receive_result :266   Frame → processor.process_frame()
   │      _dispatch       :270   ← ENTSCHEIDENDE STELLE, siehe 2.3
   ▼
Client  core/event_protocol.py  EventProtocolProcessor
   │      strikte Reihenfolgen-/Cursor-/Dedupeprüfung, liefert EventProtocolResult
   ▼
Client  core/session_coordinator.py  DualSessionCoordinator
   │      _handle_event   :308   Bindings-/Session-/Tokenprüfung → self.on_event
   │      _handle_control :340   nur bei result.issue → SessionContext-Update
   │      _handle_state   :356   SessionContext.event_state
   ▼
Client  core/controller.py  STTController
   │      _handle_event_stream_event :2329
   │          → optionaler Hook self.on_event_stream_event   (heute UNBENUTZT)
   │          → feedback_engine.handle_event_stream(...)
   │          → _publish_feedback_decision → self.on_feedback_decision
   ▼
Client  ui/core_bridge.py   Signal feedback_decision_received (QueuedConnection)
   ▼
Client  ui/application.py   _on_feedback_decision :232
             → tray.update_feedback_decision
             → overlay.show_feedback
             → sound_feedback.play
             → led_feedback.submit
```

## 2.2 Ermittelte Eigenschaften

| Frage | Antwort | Beleg |
|---|---|---|
| Verbindungsaufbau | Erst nach `hello.logAccess` der Haupt-Session; Endpoint wird same-origin aus `server.url` + `websocketPath` gebaut | `session_coordinator.py:286-306`, `config.py:247-262` |
| Auth | Session-gebundener `accessToken` aus `hello.logAccess`, **in der ersten WS-Nachricht**, nie in der URL; `EventStreamAccess.access_token` hat `repr=False` | `event_protocol.py:58`, `:103-116` |
| Parameter | `channels` fest `("audit","performance","transcription")`, `afterCursor` aus dem Cursorstore | `session_coordinator.py:305`, `event_protocol.py:222-239` |
| Replay | Server sendet `replay:true`-Events bis `log.replay_completed`; Phasenwechsel wird hart validiert | `event_protocol.py:389-392`, `:434-452` |
| Cursor | `cursor` je Event, streng monoton steigend, wird nach erfolgreicher Verarbeitung committed | `event_protocol.py:284-306` |
| Cursor-Persistenz | Atomarer Dateischreibvorgang (Tempfile + fsync + `os.replace`), gebunden an `(endpoint, serverInstanceId, protocolVersion)` | `event_cursor_store.py:89-131` |
| Eventmodell | `EventEnvelope` mit `schemaVersion, eventId, cursor, timestamp, channel, event, severity, serverInstanceId, transport, clientId, sessionId, requestId, transcriptionId, segmentId, data`, Restfelder in `extra` | `event_models.py:141-199` |
| Normalisierung | `EventNormalizer` kennt **9** Serverevents und verwirft alles andere (`return None`) | `event_normalizer.py:31-82`, `:135-137` |
| Fan-out heute | **keiner.** Genau ein `on_event`-Konsument; `on_control`/`on_state_change` je genau einer | `event_stream.py:52-66` |
| Subscriber-Modell | Einzelne `Optional[Callable]`-Slots, keine Listen | durchgängig |
| Thread-/async-Grenze | Alles im asyncio-Loop des Threads `RealtimeSTT-AsyncCore`; erst `CoreBridge`-Signale wechseln in den Qt-Thread | `ui/core_bridge.py:78-84`, `:91-119` |
| Queueing | `websockets`-eigene `max_queue=512` (`event_stream.py:196`); danach synchrone Verarbeitung ohne eigene Queue | `config.py:190` |
| Fehlerverhalten | `EventProtocolError` → Verbindung neu; `EventAccessInvalid` → Blockade bis `reconfigure`; sonst Backoff | `event_stream.py:114-144` |
| Reconnect | Eigener exponentieller Backoff 0,5–30 s mit Jitter, unabhängig von `/ws/transcribe` | `event_stream.py:335-352` |
| Event-Dedupe | `_confirmed_ids: OrderedDict`, Grenze **2048**, pro `EventStreamAccess`; Duplikate gehen an `on_control`, **nicht** an `on_event` | `event_protocol.py:304-306`, `:404-417`, `event_stream.py:273-275` |
| Eventreihenfolge | Innerhalb einer Verbindung garantiert; `cursor <= _last_seen_cursor` ist ein Protokollfehler | `event_protocol.py:420-422` |

## 2.3 Die entscheidende Stelle

`EventStreamTransport._dispatch` (`event_stream.py:270-286`) macht den
Rückgabewert des `on_event`-Callbacks zur **Protokollentscheidung**:

```python
accepted = await self._call(self._on_event, result)
if accepted is not True:
    raise EventProcessingRejected("event processing wasn't explicitly confirmed")
self._processor.confirm_event(result)   # ← Cursor-Commit auf Platte
```

Dieselbe Semantik reicht bis in den Controller durch:
`DualSessionCoordinator._handle_event` (`session_coordinator.py:323-338`) und
`STTController._handle_event_stream_event` (`controller.py:2341-2347`) geben
jeweils `False` zurück, wenn ein Consumer nicht `True` liefert.

> **Konsequenz: Der vorhandene, heute unbenutzte Hook
> `STTController.on_event_stream_event` darf für Logging NICHT verwendet
> werden.** Ein Logger, der dort hängt, entscheidet über Cursor-Commit und
> Verbindungsleben. Das ist exakt das im Zielbild §2.1 verbotene Muster.

## 2.4 Ergebnis

```text
EMPFOHLENER SERVER-LIVE-HOOK:

    voice-stt-client/core/session_coordinator.py
        DualSessionCoordinator._handle_event    (:308)
        DualSessionCoordinator._handle_control  (:340)

    Ergänzt wird EIN neuer, optionaler, rückgabewertfreier Beobachterschlitz,
    z. B.:

        self.on_observation: Optional[
            Callable[[SessionContext, EventProtocolResult], None]
        ] = None

    Aufruf jeweils als ERSTE Anweisung der beiden Methoden, vor jeder
    bestehenden Prüfung, in try/except, Rückgabewert verworfen:

        observer = self.on_observation
        if observer is not None:
            try:
                observer(self._context, result)
            except Exception:
                pass          # Fehlerbehandlung in der Logging-Failure-Domain

WARUM:

  1. Es ist der schmalste Punkt, durch den JEDES /ws/logs-Frame läuft --
     Events UND Controlframes (log.hello, log.subscribed, log.gap,
     log.error, log.replay_completed, log.pong, log.keepalive) sowie die
     als duplicate markierten Events, die on_event nie erreichen
     (event_stream.py:273-275).
  2. Der SessionContext liegt hier bereits vor: generation, session_id,
     event_state, unavailable_code. Weiter unten (Controller) ist er nur
     noch als Parameter vorhanden; weiter oben (Transport/Processor) gar nicht.
  3. Der Aufruf steht VOR der Bindings-/Token-/Sessionprüfung. Damit werden
     genau die Events sichtbar, die der Runtimepfad verwirft -- der
     diagnostisch wertvollste Fall überhaupt.
  4. Es ist ein echtes Fan-out: der Feedbackzweig läuft unverändert über
     self.on_event weiter. Kein fachlicher Pfad führt DURCH das Logging.
  5. Transport und Protokollprozessor bleiben unangetastet; der Diff ist
     additiv und betrifft eine Klasse.

NICHT VERWENDEN:

  * STTController.on_event_stream_event (controller.py:335, :2341)
      Vorhanden und frei, aber der Rückgabewert entscheidet über
      Cursor-Commit und Verbindungsrecycling (§2.3). Logging würde zur
      Runtime-Autorität.

  * EventStreamTransport._dispatch / on_event / on_control (event_stream.py:270)
      Änderung an der Protokoll-/Transportlogik; on_event trägt dieselbe
      Rückgabesemantik. Zusätzlich fehlt hier der SessionContext.

  * EventProtocolProcessor.process_mapping (event_protocol.py:256)
      Reine Protokollvalidierung, läuft vor der Dedupe-Entscheidung, kennt
      weder generation noch die aktuelle Session. Eine Ergänzung hier würde
      die strikte Validierung mit Fremdlogik vermischen.

  * FeedbackEngine.handle_event_stream (feedback_reducer.py:401)
      Der Normalizer kennt nur 9 Serverevents und liefert für alles andere
      None (event_normalizer.py:135-137). Logging würde genau die unbekannten
      und damit interessanten Events verlieren.

  * ui/application.py::_on_feedback_decision (:232)
      Qt-Thread, nach zwei Filtern (`not decision.publish or decision.replay`
      → return, :236-237). Replay- und Duplikat-Records wären unsichtbar,
      Rohpayload und Cursor sind dort nicht mehr vorhanden.
```

---

# 3. Fan-out-Möglichkeiten

## 3.1 Was an Verteilstrukturen existiert

| Struktur | Ort | Mehrere Subscriber möglich? | Für Logging nutzbar? |
|---|---|---|---|
| `Optional[Callable]`-Slots im Core (`on_event`, `on_text`, `on_transport_change`, `on_state_change`, `on_final_result`, `on_snapshot_change`, `on_feedback_event`, `on_feedback_decision`, `on_session_context_change`, `on_event_stream_event`) | `controller.py:329-343`, `stt_session.py:535-538` | **nein**, je genau einer | nein – alle bis auf zwei sind bereits von `CoreBridge` belegt |
| `CoreBridge`-Qt-Signale (`snapshot_changed`, `feedback_decision_received`, `text_received`, `transport_changed`, `command_completed`, `history_received`, `core_started`, `core_stopped`, `fatal_error`) | `ui/core_bridge.py:26-35` | **ja** – Qt-Signale sind n:m | ja, aber nur für UI-nahe Beobachtung; Qt-Thread, nach Bridge-Filterung |
| `DesktopApplication.device_mute_changed` | `ui/application.py:61` | ja | ja, UI-nah |
| `FeedbackEngine` | `feedback_reducer.py:377` | nein, kein Observer | nein |
| Eventbus / Signal-Verteiler im Core | **existiert nicht** | – | – |
| `_coordinator_tasks` (Task-Set) | `controller.py:282` | – | nein, Lifecyclehilfe |

**Ergebnis:** Es gibt **keinen** Eventbus und **keinen** Mehrfachverteiler im
Core. Die einzige echte n:m-Struktur ist die Qt-Signalebene, und die liegt zu
weit außen und im falschen Thread.

## 3.2 Was minimal ergänzt werden müsste (konzeptionell, nicht implementiert)

```text
Ein einziges, passives Aufnahmeobjekt, das per Konstruktor injiziert wird
und dessen Default ein No-Op ist:

    core/observability/ingress.py
        class ObservabilityIngress:
            def submit(self, record) -> bool      # nie blockierend, nie werfend
            def observe_server_result(ctx, result) -> None
            def observe(self, type, *, channel, level, component, **ids) -> None

Verdrahtung (rein additiv):

    STTController.__init__(..., observability: ObservabilityIngress = NULL_INGRESS)
        self.observability = observability
        self.session_coordinator.on_observation = \
            self.observability.observe_server_result      # <- Fan-out Serverevents

    CoreBridge.__init__(..., observability=...)           # gibt es an den
                                                          # Controller weiter
    DesktopApplication                                    # nutzt dieselbe Instanz
                                                          # für UI-nahe Hooks

Damit ergibt sich exakt die geforderte Form

        Serverevent
        ├── Feedback     (self.on_event → FeedbackEngine, unverändert)
        └── Logging      (on_observation → ObservabilityIngress)

und NICHT

        Serverevent → Logging → Feedback
```

**Warum kein generischer Eventbus.** Ein Bus würde eine zweite
Verteilsemantik neben den bestehenden Callback-Slots und den Qt-Signalen
einführen und wäre der dritte Weg, auf dem Zustand fließt. Für ein
Beobachtungsziel mit genau einem Konsumenten ist ein einzelner injizierter
Ingress ausreichend, testbar (ein Fake reicht) und rückbaubar.

**Warum Konstruktorinjektion statt Modul-Singleton.** `STTController` wird in
den Tests vielfach frei instanziiert (`tests/test_controller.py`,
`test_trigger_lifecycle.py`, …). Ein Singleton würde Testläufe koppeln und
Records zwischen Tests verschleppen. Ein Default-No-Op hält alle bestehenden
Testkonstruktionen unverändert lauffähig.

---

# 4. Strukturierte Client-Observation-Hooks

Legende `Art`: **P** = bestehende Python-Logzeile genügt (Handler fängt sie),
**S** = zusätzlich strukturiertes Event nötig, **P+S** = beides.

| Eventtyp | Datei/Funktion | bereits vorhandene Daten | fehlende Korrelationsfelder | Frequenz | Art |
|---|---|---|---|---|---|
| `client.app.started` | `ui/application.py:191` `start()` / `_report_lifecycle_started` `:207` | Version (`core/version.py`), Config vorhanden | `instance_id`, `process_id` | 1× | S |
| `client.app.stopping` | `ui/application.py:647` `shutdown()` / `_report_lifecycle_stopping` `:217` | – | `instance_id` | 1× | S |
| `client.core.thread_started` / `_stopped` | `ui/core_bridge.py:106-113`, `:142-150` | `worker_thread_id` | – | 1× | P+S |
| `client.controller.run_started` | `core/controller.py:2656` `run()` | Tasknamen | `generation` | 1× | S |
| `client.controller.shutdown_*` | `core/controller.py:1578` `_do_shutdown` | Fehler je Stufe (5 `logger.error`) | – | 1× | P |
| `client.websocket.connecting` / `.connected` / `.disconnected` | `core/stt_session.py:962` `_update_transport`, `:987` (`"WebSocket connected to %s (gen %d)"`), `_record_failure:1414` | `generation`, `target_url`, `reason` | `session_id` (bei connecting noch keine) | je Verbindungsversuch | P+S |
| `client.session.admitted` | `core/stt_session.py:1075-1081` `_wait_for_hello` | `sessionId`, `generation` | – | je Verbindung | P+S |
| `client.session.ready` | `core/stt_session.py:1101` `_wait_for_ready` | `generation` | `session_id` (vorhanden im State) | je Verbindung | S |
| `client.reconnect.scheduled` | `core/stt_session.py:653-655` (`"Reconnecting in %.1fs (attempt %d, gen %d)"`) | delay, attempt, generation | `last_failure_reason` (Attribut vorhanden) | je Fehlschlag | P+S |
| `client.eventstream.state_changed` | `core/event_stream.py:325` `_set_state` bzw. `session_coordinator.py:356` `_handle_state` | `EventConnectionState` | `generation`, `session_id` (im Coordinator vorhanden) | je Zustandswechsel | S |
| `client.eventstream.gap` / `.error` | `session_coordinator.py:340` `_handle_control` | `result.issue`, Rohpayload | `cursor`, `lostFrom/ToCursor` (im Payload) | selten | S |
| `client.eventstream.replay_completed` | über den Hook aus §2.4 | `cursor`, `count` | – | je Verbindung | S |
| `client.hotkey.pressed` | `ui/hotkeys.py` `nativeEventFilter` → Callbacks | Hotkey-ID | **alles**: keine Logzeile, keine IDs | Nutzeraktion | S |
| `client.command.requested` | `ui/core_bridge.py:171` `_submit_coroutine`, `:243` `_submit_sync` | Kommandoname | `correlation_id` je Kommando | Nutzeraktion | S |
| `client.command.completed` | `ui/core_bridge.py:197` `_finish_async_command` | `CommandResult(success,status,message)` | dieselbe `correlation_id` | Nutzeraktion | S |
| `client.trigger.sent` | `core/stt_session.py:787` (`"Sent trigger command: action=%s source=%s commandId=%s"`) | `action`, `source`, `commandId` | `generation`, `session_id` | Nutzeraktion | P+S |
| `client.trigger.ack_received` | `core/stt_session.py:827` `_resolve_trigger_ack` | `commandId`, `accepted`, `reason`, `activationId`, `sessionId` | – (vollständig!) | Nutzeraktion | S |
| `client.trigger.ack_dropped` | `core/stt_session.py:841-853` | `commandId`, Grund (unknown/stale_generation) | – | selten | P+S |
| `client.stream.start_sent` | `core/stt_session.py:734` (`"Sent start command."`) | – | `generation`, `session_id` | je Aktivierung | P+S |
| `client.dictation.start_attempt` / `.confirmed` / `.failed` | `core/controller.py:562` `_begin_start_locked`, `:726` `_await_start_attempt`, `:888` `_fail_start_attempt` | `token`, `generation`, `session_id`, `status`, `reason` | – (vollständig, nur unstrukturiert) | Nutzeraktion | S |
| `client.dictation.interrupted` | `core/controller.py:2473` (`"Dictation interrupted (reason: %s)."`) | `reason` | `generation`, `session_id` | selten | P+S |
| `client.audio.stream_started` / `_stopped` | `core/audio_capture.py:197-204`, `:231` | device, rate, channels, chunk ms/frames | `session_id`, `generation` | je Diktat | P+S |
| `client.audio.device_error` | `core/audio_capture.py:126-128` `logger.exception` | Exception | – | selten | P |
| `client.audio.capture_stats` | **neu**, aggregiert aus `audio_capture._audio_callback` (`:248-260`) und `controller._enqueue_audio_packet` (`:2559-2562`) | heute nur DEBUG-Zeilen | Zähler statt Zeilen | **HOT PATH** | S, aggregiert |
| `client.audio.packets_sent` | `core/controller.py:2572` `_audio_sender` | – | Zähler, Bytes | **HOT PATH** | S, aggregiert |
| `client.settings.apply_started` / `_completed` | `ui/application.py:509` `_apply_settings`, `:548` `_complete_settings_apply` | geänderte Pfade (`changes`), `ApplyPolicy`-Menge, Ergebnis | `correlation_id` je Apply-Vorgang | selten | S |
| `client.settings.runtime_apply` | `core/controller.py:1141` `apply_runtime_config` | `session_changed`, `audio_changed`, `mode_changed`, Ergebnisstatus | dieselbe `correlation_id` | selten | S |
| `client.config.validation_failed` | `core/config.py:854-859` (unbekannte Felder), `ui/settings_dialog.py:288-290` | Feldpfade, Exceptiontext | – | selten | P+S |
| `client.config.loaded` | `core/config.py:871`, `:996` | Pfade | **Pfade sind personenbezogen** (§12) | 1× | P |
| `client.feedback.decision` | `ui/application.py:266-299` `_log_feedback_decision` | **bereits strukturiert**: source, state, revision, duplicate, replay, eventId, correlationId, sound, led | `session_id`, `generation` | je Decision | P+S (Vorbild) |
| `client.led.dispatch_failed` | `ui/led_feedback.py:433` `_report_failure` | reason, „erstes Mal"-Entprellung | – | selten | P+S |
| `client.led.queue_overflow` | `ui/led_feedback.py:274` | verworfene Anzahl | – | selten | P+S |
| `client.sound.failed` | `ui/application.py:301` `_on_sound_failure` | Kategorie | – | selten | P+S |
| `client.action.blocked` | `core/controller.py:472` `_emit_feedback_event` | `TransientEventType`, reason, description, action, timestamp | `generation`, `session_id` (im Aufruf vorhanden) | Nutzeraktion | S |
| `client.server.error_classified` | `core/controller.py:1879` `_handle_error_event` | `where`, `count`, `message`, abgeleiteter `AvailabilityState` | `generation`, `session_id` | selten | P+S |
| `client.injection.enqueued` / `.rejected` | `core/controller.py:2209`, `:2190`, `_emit_final_result:2229` | `entry_id`, `segment_id`, `status`, `reason` | – | je Final | P+S |
| `client.final.deduplicated` | `core/controller.py:2072-2091` | `is_conflict`, **beide Texte** | – | selten | P+S, **redaktionspflichtig** |
| `client.history.persist_failed` | `core/history.py:177`, `:374`, `:387` | Exception | – | selten | P |
| `client.queue.state` | `core/text_injector.py` Worker (`:498`, `:584`), `controller.queue_size()` | Queue-State, Größe | – | periodisch | S, aggregiert |

## 4.1 `HOT PATH` – verbindliche Regeln

```text
HOT PATH
    core/audio_capture.py::_audio_callback         (:237-260)  PortAudio-Thread
    core/audio_capture.py::_process_loop           (:266-295)  Thread audio-process
    core/controller.py::_on_audio_packet_from_thread (:2519)   audio-process-Thread
    core/controller.py::_enqueue_audio_packet      (:2543)     asyncio-Loop
    core/controller.py::_audio_sender              (:2572)     asyncio-Loop
    core/stt_session.py::send_audio                (:900)      asyncio-Loop
    core/stt_session.py::_message_loop             (:1126)     asyncio-Loop
    core/event_stream.py::_run_live / _receive_result (:257)   asyncio-Loop
    core/stt_session.py::_apply_event, Zweig "realtime" (:1301)

Für diese Stellen gilt ohne Ausnahme:
    * kein synchroner DB-Zugriff,
    * kein Dateizugriff,
    * keine Logzeile pro Audiochunk und keine pro Realtime-Segment,
    * kein Format-/JSON-Aufwand im Normalfall,
    * ausschließlich Zähler im Speicher plus ein periodischer Aggregatrecord.

Kein Client-Anwendungsdiktat: bei 40 ms Chunks (config.py:472) sind das
25 Callbacks pro Sekunde und Richtung. Eine Zeile je Chunk erzeugt ~90.000
Records pro Stunde Diktat und macht die lokale Historie unbrauchbar.

Empfohlene Aggregation: ein Record `client.audio.capture_stats` bzw.
`client.audio.stream_stats` je 5 s WÄHREND aktiven Streamings, Channel
"performance", Level DEBUG, mit
    chunks_captured, chunks_dropped_capture_queue, chunks_dropped_send_queue,
    bytes_sent, packets_sent, overflow_count, underflow_count,
    max_send_queue_depth
Zusätzlich EINMALIG bei Zustandswechsel:
    client.audio.stream_started / client.audio.stream_stopped
Die Zähler leben in vorhandenen Objekten (AudioCapture, STTController) und
werden vom Aggregator gelesen, nicht von den Hot-Path-Stellen geschrieben.
```

**Zusätzlicher Befund H-1.** `stt_session._apply_event` loggt bei jedem
`realtime`-Event auf DEBUG (`:1301-1306`) inklusive der ersten 80 Zeichen des
Zwischentextes. Diese Zeile passiert den UnifiedLogHandler und ist damit sowohl
ein Frequenz- als auch ein Datenschutzproblem (§12). Sie muss über den
Level-Filter des Handlers (Default INFO) ausgeschlossen bleiben; der Handler
darf nicht auf DEBUG voreingestellt werden.

**Zusätzlicher Befund H-2.** `controller._audio_sender` (`:2592-2593`) loggt
jeden Sendefehler auf DEBUG mit `exc_info=True`. Bei einem
Verbindungsabriss während des Streamings entstehen dort in kurzer Folge sehr
viele Tracebacks. Auch das bleibt nur durch den Level-Filter beherrschbar.

---

# 6. Channel-Modell – Verifikation

## 6.1 Serverseitiger Ist-Zustand

| Prüfpunkt | Befund | Beleg |
|---|---|---|
| Exakte Schreibweise | **durchgängig klein**: `system`, `audit`, `transcription`, `performance` | `server/docs/structured-logging.md:5-11`, `server.py:6399`, `:6539`, `event_logging.py:764`, `:896` |
| Weitere Channels | nein, genau diese vier | `server.py:6399` (`allowed = {"audit","performance","transcription"}` + `system` nur für Admin) |
| Hat jedes Event einen Channel? | **ja**, Pflichtfeld beim Emittieren und im Envelope | `event_logging.py:955`; clientseitig `_required_string(raw,"channel")` `event_models.py:187` |
| Channel für Desktop-Client erreichbar | nur `audit`, `performance`, `transcription`. `system` ist adminexklusiv | `server.py:6537-6544`; clientseitig hart in `SESSION_CHANNELS` `event_protocol.py:24` und `session_coordinator.py:305` |
| Channel und Eventtyp unabhängig? | **ja.** `transcription.realtime_emitted` und `transcription.performance_summary` liegen auf dem Channel `performance`, tragen aber den Namensraum `transcription.*` | `structured-logging.md:136-141` |
| Severity-Werte | im Code als Literale beobachtet: `info`, `warning`, `error`; `critical` wird in der Priorisierung berücksichtigt, aber nicht als Literal emittiert | `event_logging.py:896`; Literalsuche über `server.py` + `event_logging.py` |

**Befund C-1 (Korrektur am Zielbildentwurf).** Der Zielbildentwurf
(`LOGGING_ZIELBILD_...ENTWURF.md:337-342`) schreibt die Channels großgeschrieben
(`System`, `Audit`, `Transcription`, `Performance`). Der Code kennt
ausschließlich Kleinschreibung. Der kanonische Record muss die **kleine**
Schreibweise übernehmen; andernfalls entstehen zwei Wertemengen für ein Feld.

**Befund C-2.** Der Server legt die menschenlesbare Meldung unter dem Schlüssel
`"meldung"` in den Envelope (`event_logging.py:963-965`). Der Client kennt
diesen Schlüssel nicht und schiebt ihn in `EventEnvelope.extra`
(`event_models.py:198`). Für das Feld `message` des kanonischen Records ist
`extra["meldung"]` damit die einzige serverseitige Quelle. Das ist eine
Fehlerquelle und muss im Normalizer ausdrücklich benannt werden.

**Befund C-3.** `severity` ist serverseitig kein geschlossenes Enum. Der
Normalizer darf nicht `Level(value)` aufrufen, sondern muss unbekannte Werte
durchreichen und auf ein Default-Level abbilden.

## 6.2 Client-Channels

Vorhandene Client-„Channels" (`logging_setup.CHANNELS`) sind Loggernamen, keine
fachlichen Kategorien, und decken die realen Logger nicht ab (Befund L-1). Sie
sind für den kanonischen Record **nicht** wiederverwendbar.

**Antwort auf die Auftragsfrage:** Ja, die vier Server-Channels sind für
Client-Records vollständig wiederverwendbar. Keine zusätzlichen Channels.

```text
system        Prozess-, Transport- und Konfigurationszustand.
              app.started/stopping, core thread, websocket.*, eventstream.*,
              reconnect.*, config.*, alle unstrukturierten Python-Logs ohne
              bessere Zuordnung (Default).

audit         Vom Nutzer oder vom Client absichtlich ausgelöste Handlungen und
              deren Ablehnung.
              hotkey.*, command.*, trigger.sent/ack, dictation.*, settings.*,
              action.blocked, microphone.mute.

transcription Alles am Transkript und an dessen Weiterverarbeitung.
              final.received, final.deduplicated, injection.*, history.*,
              reinsertion.*.

performance   Zahlen. Nur Aggregate, nie Einzelereignisse aus dem Hot Path.
              audio.*_stats, queue.state, timings, drop counters,
              logging.records_dropped.
```

Begründung gegen zusätzliche Client-Channels: Der Channel ist im Zielbild §9
ausdrücklich **orthogonal** zu `producer_kind`. Ein Channel `client_ui` würde
Herkunft in die Kategorie mischen und die Filterlogik verdoppeln, obwohl
`producer_kind=client` plus `component` dieselbe Auswahl bereits erlaubt.
`led` ist ebenfalls kein Channel, sondern `producer_kind` (§17).

Zuordnung für **unstrukturierte** Python-Logs: über eine kleine, explizite
Tabelle Loggername → Channel, mit `system` als Default:

```text
connection, event_stream, core.session_coordinator,
core.event_cursor_store, core.config, ui.core_bridge,
ui.single_instance, ui.application, ui.hotkeys      -> system
audio, core.led_controller, ui.led_feedback, ui.feedback, lefx.*
                                                    -> performance? NEIN -> system
text (history, reinsertion, text_injector)          -> transcription
controller                                          -> system
```

> Bewusst keine Feinzuordnung nach Logzeile. Ein unstrukturierter Text ist
> Diagnosetext; die fachliche Kategorie kommt aus den strukturierten Events.

---

# 12. Privacy- / Redaction-Audit

## 12.1 Befunde am realen Code

| Feld/Quelle | sensitiv? | darf lokal gespeichert werden? | Redaction-Regel |
|---|---|---|---|
| `logAccess.accessToken` in der `hello`-Nachricht, weitergereicht als `event_data` an `STTController.handle_server_event` (`controller.py:1710-1730`) und als Kopie an jeden `on_event`-Konsumenten (`stt_session.py:1313`) | **ja, höchstes Risiko** | **nein** | Schlüssel `accessToken` rekursiv ersetzen durch `"[redacted]"`. Zusätzlich: der `hello`-Rohpayload wird **grundsätzlich nicht** als `raw` gespeichert, sondern nur eine Whitelist (`sessionId`, `logAccess.available`, `.code`, `.reason`, `.expiresAt`, `.logProtocolVersion`, `.serverInstanceId`, `.oldestCursor`, `.latestCursor`). |
| `EventStreamAccess.access_token` | ja | nein | `repr=False` ist gesetzt (`event_protocol.py:58`) und schützt gegen `%r`. Der Normalizer darf `EventStreamAccess` dennoch nie serialisieren. |
| `EventStreamAccess.subscribe_payload()` / das gesendete Subscribe-Frame (`event_stream.py:209-211`) | ja | nein | Ausgehende `/ws/logs`-Frames werden **nicht** protokolliert. Falls je ein `client.eventstream.subscribe`-Record entsteht, nur `channels` und `afterCursor`. |
| Zukünftiger Admin-API-Key | ja | **nein, niemals** | Siehe 12.2. |
| `Authorization` / `X-VoiceSTT-Admin-Key` / `X-VoiceSTT-Log-Token` | ja | nein | Rekursive Schlüsselregel: `authorization`, `token`, `accesstoken`, `apikey`, `admin_key`, `adminkey`, `password`, `secret`, `cookie` (case-insensitiv, ohne Trenner verglichen) → `"[redacted]"`. |
| WebSocket-Queryparameter, geloggt in `stt_session.py:987` (`"WebSocket connected to %s (gen %d)"` mit `target_url`) | teilweise (Konfiguration, Wake Words, Sensitivitäten) | mit Regel | Query aus jeder URL vor Speicherung entfernen (`urlsplit` → `urlunsplit` ohne `query`/`fragment`). Der `/ws/logs`-Endpoint ist bereits queryfrei erzwungen (`event_cursor_store.py:32-33`). |
| **Transkriptionstext** – heute schon im Klartext im Client-Log: `stt_session.py:1296-1300` (`"Final [seg=%s]: %s"`, 80 Zeichen, INFO) und `:1301-1306` (Realtime, DEBUG) | **ja** | konfigurierbar | `store_transcription_content` (Default **false**). Bei `false`: Textfelder durch `"[redacted:<n> chars]"` ersetzen, Zeichenzahl erhalten. Betrifft `text`, `displayText`, `rawText`, `stableText`, `unstableText`, `committedStableText`, `visualUnstableText`. |
| Transkripttext in Konflikt-Warnungen: `controller.py:2077-2080` und `:2145-2148` loggen **beide vollständigen Texte** (`existing=%r, new=%r`) auf WARNING | **ja** | konfigurierbar | Gleiche Regel; hier greift der Level-Filter **nicht**, weil WARNING. Diese zwei Stellen sind die kritischsten unstrukturierten Fundstellen. |
| Transkripttext in `HistoryEntry` / `entry.text` und in Injection-Logs (`text_injector.py:636`, `reinsertion.py:234`) | ja | konfigurierbar | wie oben. Die vorhandene Transkript-Historie (`history.py`) bleibt davon unberührt – sie ist eine bewusste Produktfunktion mit eigener Konfiguration. |
| Dateipfade mit Windows-Benutzernamen: `logging_setup.py:114-119` (`dir=%s`), `history.py:175` (DB-Pfad), `config.py:871`/`:996`, `event_cursor_store.py:70`/`:81` | ja, personenbezogen | ja, mit Regel | Benutzerprofilanteil ersetzen: Präfix `os.path.expanduser("~")` → `"~"`. Keine vollständige Unterdrückung, weil der relative Pfad diagnostisch nötig ist. |
| Hostname / Benutzername | ja | **nicht speichern** | `socket.gethostname()` wird heute nirgends verwendet. Feld `host` in V1 nicht befüllen (§5). |
| Fensternamen / Zielanwendung der Injektion | – | – | **Nicht vorhanden.** `text_injector.py` loggt nur `HWND=%s` (`:267`, `:272`), keinen Fenstertitel. Kein Handlungsbedarf, aber als Regel festhalten, damit es so bleibt. |
| Audioinhalt | – | – | **Nicht vorhanden.** Es werden nur Byteanzahlen und Frames geloggt. Regel: PCM-Bytes dürfen nie in `details` oder `raw`. |
| Serverseitige Rohpayloads | bereits bereinigt | ja | Der Server entfernt Credentials, Authorization, Cookies, Querystrings, Binär-/Audiofelder und unerlaubte Transkriptfelder **vor jedem Sink**, also auch vor `/ws/logs` (`docs/structured-logging.md:66-68`). Der Client redigiert trotzdem erneut – der Server ist eine fremde Vertrauensgrenze und `transcript_log_mode` kann `full` sein. |
| `feedback_mappings`, `led.effect_paths` | nein | ja | – |
| `command_id`, `session_id`, `event_id`, `activation_id`, `transcription_id` | nein | ja | Opake IDs, keine Personendaten. |

## 12.2 Admin-Key – Vorabsicherung

Der Client kennt heute **keinen** Admin-Key. `voice-stt-client/AGENTS.md`
schließt einen Admin-Service für die aktuelle Entwicklungsphase ausdrücklich
aus. Serverseitig existiert er als `settings.admin_api_key` bzw.
`VOICESTT_ADMIN_API_KEY` und wird konstantzeitvergleichend geprüft
(`server.py:5956-5962`).

Verbindliche Vorabregeln, damit ein später in der UI hinterlegter Key nie in
die Logdaten gelangt:

```text
R-1  Der LoggingCore kennt keinen Admin-Key und keine Auth-Objekte.
     Er nimmt ausschließlich CanonicalLogRecords entgegen.
R-2  Der Redaction-Schritt läuft VOR der Übergabe an die Queue, im Producer-
     Thread. Ein unredigierter Record existiert nie in der Queue, nie im
     Ringbuffer und nie in der DB.
R-3  Die Redaction ist eine SCHLÜSSELREGEL, keine Werteregel. Sie darf nicht
     nach „sieht aus wie ein Token" suchen, sondern muss den Schlüsselnamen
     rekursiv prüfen. Werteheuristiken erzeugen falsche Sicherheit.
R-4  Exception-Kontext wird über `formatException` als Text übernommen.
     `record.args`, `locals()` und Objekt-`repr()` werden NICHT gespeichert.
     Begründung: ein `repr()` eines Auth-Objektes ist der klassische Leckweg;
     `EventStreamAccess` schützt sich mit `repr=False`, ein künftiges
     Admin-Objekt vielleicht nicht.
R-5  Ausgehende Frames (`_send_json`, `subscribe_payload`) werden nie roh
     protokolliert.
R-6  `store_raw_payload` gilt nur für EINGEHENDE Serverevents, nie für
     `hello`, nie für Kommandos.
R-7  Die DB-Datei und die Datei-Sinks werden im Benutzerprofil unter
     %LOCALAPPDATA% angelegt, nicht in einem gemeinsamen Verzeichnis.
```

---

# 17. LED-Controller-Erweiterbarkeit (Kurzaudit)

| Prüfpunkt | Befund |
|---|---|
| Aktuelles Logging | Standard-Python-`logging` unter dem geschlossenen Namensraum `lefx.*`: `lefx.device.respeaker.{contention,provider,sink,transport}`, `lefx.engine.{composer,library}`, `lefx.interfaces.{config,discovery,service}` |
| Ausführungsort | **Im selben Prozess wie der Client.** `led-controller-version-3==3.0.3` ist eine reguläre Abhängigkeit (`requirements.txt`); `InProcessLedController` rendert im Thread `RealtimeSTT-LED` (`ui/led_feedback.py:303-305`) |
| Öffentliche Adapterpunkte | `LedFeedback.on_failure` (Callback, `ui/led_feedback.py:75`), `LedController.on_sink_changed` (`:119`), `LedFeedback.unavailable_seconds` (Polling, `:130`), `LedFeedback.submit`-Rückgabewert |
| Event-/Callback-Infrastruktur vorhanden | ja, aber einslotig und bereits von `DesktopApplication` belegt (`ui/application.py:89-98`) |

```text
ERGEBNIS

Ein späterer LedAdapter ist möglich, OHNE CanonicalRecord oder LoggingCore
umzubauen. Für V1 ist er sogar überflüssig:

  * Weil LEFX im selben Prozess läuft, erreichen alle `lefx.*`-Logrecords
    ohnehin den Root-Logger und damit den UnifiedLogHandler. Es ist KEIN
    Transport und KEIN Adapter nötig.
  * Erforderlich ist lediglich EINE Normalizer-Regel:
        logger name startswith "lefx."  ->  producer_kind = "led"
                                            producer_id  = "respeaker-led-controller"
                                            component    = <logger name>
    Damit ist die Herkunftstrennung des Zielbilds (§7.1) erfüllt, ohne dass ein
    Feld, eine Tabelle oder eine Schnittstelle hinzukommt.
  * Ein echter, transportgebundener LedAdapter wird erst nötig, wenn der
    LED-Controller in einen eigenen Prozess oder auf ein eigenes Gerät wandert.
    Er implementiert dann dieselbe Adapterschnittstelle wie ServerLiveAdapter
    und erzeugt denselben CanonicalLogRecord; producer_kind="led" existiert
    dafür bereits.

KEINE LED-Änderung erforderlich und keine vorgenommen.
```

---

# Zusammenfassung der Befunde dieses Dokuments

| ID | Befund | Wirkung auf V1 |
|---|---|---|
| L-1 | `logging_setup.CHANNELS` deckt die realen Loggernamen nicht ab | Client-Channels müssen neu vergeben werden; Server-Channels wiederverwenden |
| L-2 | Es existiert bereits ein `extra`-Vertrag mit vier Feldern | Der neue Vertrag muss diese vier Namen weiter akzeptieren |
| **S-1** | `on_event`-Rückgabewert entscheidet über Cursor-Commit; `on_event_stream_event` ist deshalb als Logging-Hook verboten | Bestimmt die Hookwahl (§2.4) |
| S-2 | Duplikate und alle Controlframes erreichen den Controller nie | Hook muss im Coordinator liegen, nicht im Controller |
| S-3 | Es gibt keinen Eventbus und keinen Mehrfachverteiler im Core | Ein minimaler Ingress muss injiziert werden |
| C-1 | Zielbildentwurf schreibt Channels groß, Code klein | Kleinschreibung ist verbindlich |
| C-2 | Servermeldung liegt unter `"meldung"` und landet in `EventEnvelope.extra` | `message`-Ableitung muss das ausdrücklich behandeln |
| C-3 | `severity` ist kein geschlossenes Enum | Normalizer muss tolerant sein |
| H-1 | Realtime-Text wird auf DEBUG geloggt | Handler-Default darf nie DEBUG sein |
| H-2 | Audio-Sendefehler erzeugen Traceback pro Paket | dito |
| **P-1** | `hello` enthält `logAccess.accessToken` und wird als Dict an alle Eventkonsumenten kopiert | Whitelist statt Blacklist für `hello` |
| P-2 | Transkripttext ist heute bereits im Klartext im Client-Log (INFO und WARNING) | `store_transcription_content` muss auch unstrukturierte Logs erfassen |
| P-3 | Log- und DB-Pfade enthalten den Windows-Benutzernamen | Pfad-Redaction-Regel |
| LED-1 | LEFX läuft in-process und loggt nach `lefx.*` | Kein LedAdapter in V1 nötig, nur eine Normalizer-Regel |
