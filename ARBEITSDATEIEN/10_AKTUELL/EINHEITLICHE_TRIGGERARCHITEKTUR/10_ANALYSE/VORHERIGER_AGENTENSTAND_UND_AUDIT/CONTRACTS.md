# CONTRACTS – Cross-Repository-Vertragsmatrix

**Stand:** AP9 – Sollstand nach dem Umbau.
Der ursprüngliche AP0-Iststand ist unten je Vertrag als „Befund bei Übernahme"
erhalten, damit nachvollziehbar bleibt, was verändert wurde.

Legende der Prüfstände:

- **PASS** – erfüllt und durch einen benannten Test belegt
- **N/A** – vom Umbau nicht berührt, mit Begründung
- **MANUAL VALIDATION REQUIRED** – nicht automatisiert prüfbar; konkrete
  Testanweisung in `VALIDATION.md`, GATE 10
- `IST-VERIFIZIERT` – im Code selbst nachgelesen, Fundstelle genannt

Es gibt in dieser Datei bewusst keine Bewertungen wie „wahrscheinlich
kompatibel", „sollte funktionieren" oder „nicht betroffen" ohne Nachweis (§22).

## Übersicht

| Vertrag | Status |
| --- | --- |
| C-01 WebSocket-Session | **PASS** |
| C-02 Trigger / Ack | **PASS** |
| C-03 IDs | **PASS** |
| C-04 Events | **PASS** |
| C-05 Feedback | **PASS** (reale Ausgabe am Gerät offen) |
| C-06 LED/LEFX | **PASS** (echter ReSpeaker offen) |
| C-07 Konfiguration | **PASS** |
| C-08 Recorder-Activation | **PASS** |
| C-09 Legacy | **PASS** (Browserclient offen) |

---

## C-01 – WebSocket-Session-Vertrag `/ws/transcribe`

```text
Contract:        Realtime-Transkriptionssession
Producer:        voice-stt-server, api_fastapi_server/server.py:7061
Consumer:        voice-stt-client core/stt_session.py; Browserclient app_browserclient
Transport:       WebSocket, JSON-Textbefehle + binäre Audiopakete
```

### URL und Queryparameter (IST-VERIFIZIERT)

| Parameter | Quelle | Bemerkung |
| --- | --- | --- |
| `clientId` | server.py:7063 | alternativ Header `x-voicestt-client-id` |
| `wakeWordEnabled` | `parse_session_wake_word_query` | schaltet Wake Word je Session |
| `wakeWordBackend`, `wakeWords`, `wakeWordInferenceFramework`, `wakeWordSensitivity`, `wakeWordActivationDelay`, `wakeWordTimeout`, `wakeWordBufferDuration`, `wakeWordFollowupWindow` | server.py:496–513 | `SESSION_WAKE_WORD_QUERY_FIELDS` / Tuningbereiche |
| `manualTriggerEnabled`, `wakeWordTriggerEnabled`, `initialSpeechTimeout`, `followupTimeout`, `extensionSeconds` | `SESSION_ACTIVATION_QUERY_FIELDS` | **PASS** – im WebSocket-Einstieg geparst, über `admit_session(activation_request=…)` bis in die Session durchgereicht |

**Befund bei Übernahme:** `parse_session_activation_query()` und
`resolve_session_activation_config()` besaßen **keinen Produktionsaufrufer**;
der Client sendete die Parameter bereits, der Server ignorierte sie vollständig.

**Jetzt:** verdrahtet. Unparsbare Werte werden als `invalid_activation_flag` /
`invalid_activation_timing` abgelehnt statt still zu `false` zu werden.
Nachweis: `test_query_parameters_reach_the_session_and_announce_the_capability`,
`test_an_unparsable_trigger_flag_is_rejected_instead_of_silently_false`;
Mutationsnachweis M1 in `evidence/ap4_mutation_check.txt` (15 von 17 E2E-Tests
werden rot, wenn die Verdrahtung entfernt wird).

### Servernachrichten (IST-VERIFIZIERT)

| Typ | Fundstelle | Pflichtfelder |
| --- | --- | --- |
| `hello` | server.py:7147 | `clientId`, `sessionId`, `settings`, `sessionConfig`, `sessionCapabilities`, `limits`, `supportedEngines`, `runtimeSettings`, `logAccess` |
| `ready` | server.py:4699 | `sessionId`, `settings`, `sessionConfig`, `sessionCapabilities`, `limits`, `runtimeSettings`, `ok`, `models` |
| `status` | `publish_status` | Sitzungszustand |
| `timeline` | `_publish_timeline_event` | Zeitachsenereignisse inkl. `wakeword_detected` |
| `realtime`, `final` | Transkriptionspfad | `segmentId`, Text |
| `warning`, `error` | diverse | `where`, ggf. `code` |
| `pong`, `metrics`, `clear` | server.py:7223–7236 | — |
| `trigger_ack` | `handle_trigger_command` | **PASS** – deterministisch, korreliert, idempotent |
| `activationConfig` in `hello`/`ready` | `activation_config_dict()` | **PASS** – additiv ergänzt |

### Clientbefehle (IST-VERIFIZIERT)

| Befehl | Semantik SOLL | Status |
| --- | --- | --- |
| `start` | **nur** Streamstart | **PASS** – serverseitig unverändert; clientseitig korrigiert (`_begin_stream_and_trigger` sendet `start` **und** danach den Trigger). Mutationsnachweis M1 in `evidence/ap7_mutation_check.txt` |
| `stop` | **nur** Streamstop | **PASS** – der Manualstopp sendet jetzt `trigger finish` und lässt den Stream laufen; `stop` bleibt als Streambefehl verfügbar |
| `clear` | Segment verwerfen | IST korrekt |
| `ping`, `metrics` | Diagnose | IST korrekt |
| `trigger` | Activation steuern | **PASS** – fachlich wirksam, inkl. Lifecycle-Prüfung |

### Close Codes (IST-VERIFIZIERT)

| Code | Anlass |
| --- | --- |
| `1008` | `SessionConfigurationError` bei Query-Parsing oder Admission |
| `1011` | Sitzungsinitialisierung fehlgeschlagen |
| `1013` | Sitzungslimit erreicht |

### Fehlersemantik

`SessionConfigurationError.payload()` (server.py:527) erzeugt
`{"type":"error","where":"session_config","code":…,"message":…}` plus Details.
`false/false` wird über `activation_trigger_required` abgelehnt (Close 1008);
neu ergänzt `activation_wake_word_unavailable`, wenn das Wake Word die einzige
Triggerquelle wäre, aber kein Wake-Word-Profil aktiv ist.

**Status:** **PASS** (GATE 3, GATE 4).

---

## C-02 – Triggervertrag `trigger` / `trigger_ack`

```text
Contract:   Serverautoritative Activationsteuerung
Producer:   Client (Command) / Server (Ack)
Consumer:   Server (Command) / Client (Ack)
Transport:  WebSocket JSON auf derselben Session
```

### Command (IST-VERIFIZIERT, server.py `handle_trigger_command`)

```json
{ "type": "trigger", "action": "activate|extend|finish|cancel",
  "source": "manual|wake_word", "commandId": "UUID" }
```

### Ack (IST-VERIFIZIERT)

```json
{ "type": "trigger_ack", "commandId": "...", "accepted": true|false,
  "reason": "...", "activationId": "..."|null, "sessionId": "..." }
```

Bekannte `reason`-Werte im Iststand: `activated`, `merged`, `already_active`,
`extended`, `finished`, `cancelled`, `not_active`, `trigger_disabled`,
`invalid_payload`, `missing_command_id`, `invalid_action`, `invalid_source`,
`command_id_conflict`, `controlled_activation_disabled`.

### Idempotenz (IST-VERIFIZIERT)

`_trigger_command_results` als `OrderedDict`, FIFO-Begrenzung auf 200 Einträge.
Gleiche `commandId` mit gleichem Payload → zwischengespeichertes Ack.
Gleiche `commandId` mit abweichendem Payload → `command_id_conflict`.

### Befund bei Übernahme (behoben)

- keine Lifecycle-Prüfung (Trigger vor Streamstart / nach Stop / nach Close)
- Ablehnungen trugen keine laufende `activationId`
- **Consumer fehlte vollständig:** im Client existierte kein `trigger_ack`-Handler

### Jetzt

- Lifecycle geprüft: `stream_not_started`, `session_closed`
- Ablehnungen tragen die laufende `activationId`
- Typprüfung: `invalid_command_id`, `invalid_action`, `invalid_source`
- Client konsumiert Acks über Pending-Verwaltung, gebunden an die
  Verbindungsgeneration; wiederholte, unbekannte und veraltete Acks werden
  verworfen, bevor ein Consumer sie sieht

**Tests Producer:** `tests/unit/test_server_trigger_contract.py` (18 Tests,
über echten WebSocket).
**Tests Consumer:** `tests/test_stt_session.py::TestTriggerAcknowledgement`
(11 Tests), `tests/test_trigger_lifecycle.py` (17 Tests).
**Cross-Project-Test:** `tests/unit/test_server_controlled_e2e.py` (19 Tests)
prüft die Serverseite über den Produktionseinstieg; die Clientseite prüft
`tests/test_trigger_feedback_contract.py`.

**Status:** **PASS** (GATE 3, GATE 7, GATE 8).

---

## C-03 – ID-Vertrag

| ID | Producer | Scope | Lebensdauer | Invalidierung | Replay | Dedupe | Reconnect | Stand |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `sessionId` | Server (`uuid4().hex`, server.py:7084) | eine WS-Verbindung | Verbindung | Close | n/a | n/a | neue ID | IST-VERIFIZIERT |
| `generation` | Client (`STTSession.generation`) | Verbindungsgeneration | bis Reconnect | Reconnect | n/a | verwirft alte Antworten | inkrementiert | IST-VERIFIZIERT |
| `segmentId` | Server (`SegmentState`) | Aufnahmesegment | Segment | Finalisierung | im Eventstream | über `eventId` | fortlaufend | IST-VERIFIZIERT |
| `activationId` | Server (`ActivationController`) | Activation | bis Finish/Cancel/Timeout/Reset | `finish`/`cancel`/`expire`/`reset` | in allen Timeline-Events | über `generation` | **wird nie wiederbelebt** (`test_a_reconnect_does_not_revive_the_previous_activation`) | **PASS** |
| `commandId` | Client | ein Triggerkommando | Sessionhistorie (200) | FIFO-Verdrängung | — | Ack-Cache serverseitig, Pending-Map clientseitig | Pending wird beim Reconnect verworfen | **PASS** |
| `generation` (Activation) | Server | eine Activation | stabil über deren Leben | neue Activation | in Events | Gate-Bindung | neu | **PASS** |
| `eventId` | Server (Eventhub) | globales Event | dauerhaft | — | ja | ja | ja | IST-VERIFIZIERT |
| `cursor` | Server (Eventhub) | Eventreihenfolge | dauerhaft | — | ja | ja | fortgesetzt | IST-VERIFIZIERT |

**Befund bei Übernahme (behoben):** `activationId`, `primarySource` und
`sources` erschienen in keinem Recording-/Transkriptionsevent.

**Jetzt:** `_publish_timeline_event` ergänzt diese drei Felder automatisch aus
dem laufenden Controller. Nachweis:
`test_manual_trigger_opens_the_gate_and_speech_then_records` prüft sie am
`recording_started`-Event.

**Status:** **PASS** (GATE 4). Für jede ID sind Producer, Scope, Lebensdauer,
Invalidierung, Replay-, Dedupe- und Reconnectverhalten in der Tabelle oben
festgelegt.

---

## C-04 – Eventvertrag

### Kanonische Clientseite (IST-VERIFIZIERT, `core/event_models.py:68`)

```text
server.wakeword.detected
server.recording.started
server.recording.ended
server.transcription.started
server.transcription.completed
server.transcription.discarded
server.transcription.failed
server.transcription.cancelled
server.transcription.rejected

client.hotkey.accepted
client.action.blocked
client.dictation.interrupted
client.dictation.timeout_warning
client.dictation.timeout_warning_cleared
client.transport.disconnected
client.event_stream.{connecting,replaying,live,degraded}
client.microphone.{lost,recovered}
client.injection.{accepted,succeeded,failed}
client.tts.{started,stopped,failed}
client.led.unavailable
client.sound.failed
client.configuration.invalid
client.lifecycle.{started,stopping}
```

### Serverseitige Timeline-Zuordnung (IST-VERIFIZIERT, server.py:3880)

`wakeword_detected → wakeword.detected` usw.

### Befund bei Übernahme (behoben)

`activation.manual_accepted`, `activation.extended` und `activation.closed`
wurden **nirgends erzeugt** und hatten **keinen Consumer**.

### Jetzt

Neu erzeugt werden — additiv, ohne Änderung bestehender Eventnamen:

| Timeline-Event | Strukturiertes Event | `reason` |
| --- | --- | --- |
| `activation_started` | `activation.started` | – |
| `activation_extended` | `activation.extended` | – |
| `activation_closed` | `activation.closed` | `finished`, `cancelled`, `timed_out`, `stream_stopped`, `session_closed`, `client_clear` |

Alle Recording- und Transkriptionsevents tragen zusätzlich `activationId`,
`primarySource` und `sources`.

**Consumerprüfung nach §26:** Der bestehende Consumerpfad für Manual-Feedback
ist `client.hotkey.accepted`. Er wird jetzt aus dem akzeptierten `trigger_ack`
gespeist statt aus einer lokalen Annahme (`_manual_accept_correlation()`,
Korrelation über die `commandId`). Für die drei neuen `activation.*`-Events
wurde **bewusst kein neuer Consumer eingeführt**: der Client leitet sein
Feedback weiterhin aus den bestehenden kanonischen Events ab. Die neuen Events
dienen der Diagnose und der Korrelation im Eventstream.

**Tests Producer:** `test_the_server_closes_the_gate_on_its_own_after_the_timeout`
prüft `activation_closed` samt `reason`.
**Tests Consumer:** `tests/test_trigger_feedback_contract.py`.

**Status:** **PASS** (GATE 4, GATE 8).

---

## C-05 – Feedbackvertrag

```text
Server Event → Client Normalizer (core/event_normalizer.py)
             → Canonical Event (core/event_models.py)
             → Feedback Reducer (core/feedback_reducer.py)
             → Feedback Mapping (core/feedback_mapping.py)
             → Sound (ui/feedback.py) / LEFX (core/led_controller.py, ui/led_feedback.py)
```

Normalizer behandelt laut Iststand die STT-Fallbacktypen `timeline`, `status`,
`final`, `error` sowie den Eventstream `/ws/logs`.
`FeedbackImpulse` und `FeedbackState` sind in `core/event_models.py:34–54`
abschließend definiert.

**Verbindlicher Bestand:** Der Feedback-Fix aus Commit `178d32b`
(„fix(feedback): debug LED and sound feedback") darf nicht zurückgebaut werden
(§21).

### Prüfpunkte nach §11.4

| Frage | Antwort | Nachweis |
| --- | --- | --- |
| Erzeugt der Server das Event korrekt? | ja | `test_manual_trigger_opens_the_gate_and_speech_then_records` |
| Akzeptiert der Client es? | ja | `TestTriggerAcknowledgement` |
| Normalisiert der Client es korrekt? | ja | bestehende `tests/test_event_normalizer.py` |
| Löst Replay einen erneuten Impuls aus? | **nein** | Reducer setzt bei `origin is REPLAY` `publish=False`; `tests/test_feedback_reducer.py` |
| Dedup funktioniert? | ja | `test_the_same_correlation_id_is_only_published_once` |
| Reducer interpretiert es korrekt? | ja | `tests/test_feedback_integration.py` |
| Mapping existiert? | ja | `test_the_events_of_the_trigger_path_all_have_a_rule` |
| Sound-/LED-Ziel existiert? | ja | `test_every_named_led_target_is_a_non_empty_name` |

**Manual-Accepted stammt jetzt aus dem `trigger_ack`** und feuert genau einmal
je akzeptiertem Kommando; eine Ablehnung erzeugt keinen Impuls
(Mutationsnachweis in `evidence/ap8_mutation_check.txt`).

**Feedback-Fix aus `178d32b` erhalten:**
`test_manual_accepted_still_produces_a_sound_and_an_led_effect`.

**Status:** **PASS** (GATE 8), mit der Einschränkung, dass die reale Sound- und
LED-Ausgabe am Gerät nicht geprüft wurde (GATE 10).

---

## C-06 – LED-/LEFX-Vertrag

```text
Producer:  voice-stt-client core/led_controller.py, ui/led_feedback.py
Consumer:  led_controller_respeaker-v3
```

Im LED-Repository existiert **keine** Vorarbeit dieser Aktion; der Referenzstand
`aa2f14b` ist bis zum Schluss unverändert (`git status --short` liefert null
Zeilen). Laut §5 sind Produktcodeänderungen dort nicht vorgesehen, und der
Bedarf ist auch nicht entstanden: die Triggerarchitektur führt kein neues
LED-Verb und kein neues Effektziel ein, sondern benutzt ausschließlich die
bestehenden Mappings.

| Prüfpunkt §11.5 | Status | Begründung |
| --- | --- | --- |
| Verbnamen | **PASS** | unverändert; `LedVerb` nicht angefasst |
| Effects / Presets / Overlays | **PASS** | keine neuen Ziele eingeführt |
| Katalogauflösung | **PASS** | `test_every_named_led_target_is_a_non_empty_name`; zusätzlich prüft die Schutzbedingung im Build-Spec die Auflösung der `.lefxset`-Archive |
| State Restore, Shutdown | **N/A** | vom Umbau nicht berührt; LED-Repo unverändert |
| Simulator | **PASS** | `tests/device/test_simulator_window.py`, 6 passed, 0 skipped: die Tests rendern den Ring mit einem echten `QApplication` in ein Bild und prüfen das Ergebnis |
| echter ReSpeaker | **MANUAL VALIDATION REQUIRED** | Gerät ist **angeschlossen**, aber nicht erreichbar: `[Errno 13] Access denied (insufficient permissions)`. Fehlende Zugriffsrechte beziehungsweise Treiber, nicht fehlende Hardware (GATE 10, M-6) |

**Status:** **PASS** für alle automatisiert prüfbaren Punkte einschließlich
Simulator; der Lauf am echten ReSpeaker bleibt ausdrücklich offen.

---

## C-07 – Konfigurationsvertrag

| Alt | Neu (SOLL) | Status |
| --- | --- | --- |
| `mode=hotkey` | `manual=true`, `wake_word=false` | **PASS** |
| `mode=wake_word` | `manual=false`, `wake_word=true` | **PASS** – vorher fälschlich `true/true` |
| — | keine implizite `true/true`-Migration | **PASS** (`test_no_legacy_mode_ever_migrates_to_both_triggers`) |
| — | `false/false` abgelehnt | **PASS** – Client (`SessionConfig.validate`) **und** Server (`activation_trigger_required`) |
| — | beide Trigger separat steuerbar | **PASS** (`test_explicit_flags_override_the_legacy_mode`) |
| — | UI und Backend wenden dieselbe Regel an | **PASS** – der Settingsdialog liest dieselben Properties wie `query_parameters()` und `validate()` |
| — | ungültiger alter Wert abgelehnt | **PASS** (`test_an_invalid_legacy_mode_value_is_rejected`) |
| — | fehlendes Feld | **PASS** (`test_a_missing_mode_field_keeps_the_hotkey_default`) |
| — | Frozen-/PyInstaller-Pfadauflösung | **PASS** – über den erfolgreichen Build belegt (GATE 10) |

**Befund bei Übernahme (behoben):** `effective_manual_trigger_enabled` lieferte
bei `None` unbedingt `True` und ignorierte den Altmodus; der mitgelieferte Test
`test_legacy_wake_word_mode_migrates_query_parameters` schrieb das als
Sollverhalten fest. Beides ist korrigiert.

Ergänzt: `effective_wake_word_trigger_enabled`, `migrated_from_legacy_mode`
sowie eine Typprüfung beider Flags.

**Status:** **PASS** (GATE 6).

---

## C-08 – Recorder-Activation-Vertrag (serverintern)

```text
Producer:  api_fastapi_server RecorderBackedRealtimeSession
Consumer:  VoiceSTT AudioToTextRecorder über VoiceSTT/core/activation_control.py
```

| Operation | Status |
| --- | --- |
| `set_activation_policy(policy)` | **PASS** |
| `open_controlled_activation(id, replace=…, generation=…)` | **PASS** – jetzt generationsgebunden |
| `close_controlled_activation(id=…, generation=…)` | **PASS** – jetzt generationsgebunden, auch für `close(None)` |
| `abort_controlled_activation()` | **PASS** – neu; `abort()` ruft es produktiv auf |
| `shutdown_controlled_activation_gate()` | **PASS** – neu; nach `shutdown()` wird jedes `open` abgelehnt |
| `controlled_activation_state()` | **PASS** |
| Gate-Auswertung im VAD-Pfad | **PASS** – kein Wakeword-Bypass im Controlled-Modus (`test_04_wake_word_cannot_bypass_a_closed_controlled_gate`) |
| Gate wird produktiv geöffnet und geschlossen | **PASS** – Mutationsnachweis M3 in `evidence/ap4_mutation_check.txt` |

**Konfliktbefund bei Übernahme (behoben):**
`_start_wakeword_followup_window()` setzte am Recorder direkt
`wakeword_detected`, `wake_word_timeout`, `start_recording_on_voice_activity`
und `stop_recording_on_voice_deactivity` und startete einen eigenen
Timerthread. Im Controlled-Modus wäre das eine zweite Recorder-Autorität und
ein paralleler Follow-up-Timer gewesen (§2.3, §7.1 verboten).

**Jetzt:** im Controlled-Modus abgeschaltet, im Legacy-Modus unverändert.
Nachweis: `test_controlled_mode_never_starts_the_legacy_followup_window` und
`test_legacy_mode_still_starts_the_legacy_followup_window`; die Wirksamkeit
dieses Tests ist per Mutation M4b belegt.

**Status:** **PASS** (GATE 1, GATE 4).

---

## C-09 – Legacyvertrag

| Anforderung | Status | Nachweis |
| --- | --- | --- |
| Legacyclient sendet nie `trigger` | **PASS** | `trigger` ist additiv; ein Legacyclient kennt es nicht |
| Sessions ohne Triggerparameter bleiben legacy | **PASS** | `test_a_session_without_trigger_parameters_stays_legacy` |
| Legacyclient funktioniert unverändert | **PASS** | `test_a_legacy_client_never_sends_a_trigger_and_keeps_working`; 81 Tests der bestehenden Protokoll- und Multi-User-Suiten grün (`evidence/ap5_legacy_protocol.txt`) |
| `start`/`stop` serverseitig unverändert | **PASS** | Streambefehle nicht angefasst |
| Legacy-Recorderverhalten unverändert | **PASS** | `test_03_legacy_policy_behaviour_is_unchanged`, `test_legacy_mode_still_starts_the_legacy_followup_window` |
| Feedback-Fix `178d32b` erhalten | **PASS** | `test_manual_accepted_still_produces_a_sound_and_an_led_effect` |
| Bestehende Eventnamen unverändert | **PASS** | nur additive Ergänzungen |
| Browserclient funktioniert | **MANUAL VALIDATION REQUIRED** | Der Client wurde auf den aktuellen Vertrag angepasst (`/ws/transcribe`, `start`, `realtime`/`final`, vollständige Audiometadaten) und ist durch `test_browser_client_contract.py` statisch **und** per Replay gegen die echte App abgesichert. Offen bleibt allein der Lauf im echten Browser mit Mikrofonfreigabe (GATE 5, M-B1) |

**Status:** **PASS** bis auf den ausdrücklich offenen Browserclient.
