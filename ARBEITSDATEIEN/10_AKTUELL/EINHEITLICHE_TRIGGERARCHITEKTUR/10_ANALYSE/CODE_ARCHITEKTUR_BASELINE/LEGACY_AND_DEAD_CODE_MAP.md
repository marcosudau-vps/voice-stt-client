# LEGACY_AND_DEAD_CODE_MAP

**Phase A – Ist-Zustand ohne Sollbewertung.** Auftragsabschnitte 16 und 17.

Kategorien laut Auftrag:

| Kategorie | Bedeutung in diesem Dokument |
|---|---|
| `ACTIVE` | wird im Produktivpfad aufgerufen und wirkt |
| `PARTIALLY DISCONNECTED` | existiert, schreibt oder liest weiterhin Zustand, aber ein Teil der ursprünglichen Autorität wurde entfernt |
| `DEAD` | im Produktivpfad nicht erreichbar; höchstens Tests rufen es auf |
| `COMPATIBILITY` | absichtlicher Adapter für ältere Gegenstellen oder Konfigurationen |
| `UNKNOWN` | Aufrufbarkeit aus dem Code nicht abschließend bestimmbar |

---

## 16. Dead Code und halb entfernte Architektur

### 16.1 voice-stt-client

| Fund | Datei/Symbol | Befund am Code | Kategorie |
|---|---|---|---|
| Lokale Diktatfenster-Statemaschine | `core/controller.py:85-91` `DictationWindowPhase`, `:1450-1499` `_arm_dictation_window` / `_dictation_window_timeout`, `:1368-1377` `_cancel_dictation_window` | `_arm_dictation_window` wird nur unter `_client_owns_dictation_window` aufgerufen (`:840-848`); dieses ist gegen einen Server mit `activationTriggers` immer `False` (`:683-693`, Server meldet die Fähigkeit bedingungslos, `server.py:4976-4983`). Der Wert wird trotzdem in jeden Snapshot geschrieben (`:431`) und von der UI gelesen (`ui/presentation.py:126-138`). | **PARTIALLY DISCONNECTED** |
| `SEGMENT_ACTIVE`-Übergang | `core/controller.py:1811-1822` | steht hinter `if self._server_owns_activation: … return` (`:1795-1801`) und hinter `if not effective_manual_trigger_enabled: return` (`:1803`) | **DEAD** gegen Produktivserver |
| `FOLLOWUP_WAIT`-Übergang | `core/controller.py:1823-1832` | dito | **DEAD** gegen Produktivserver |
| `_client_owns_dictation_window` (True-Zweig) | `core/controller.py:683-693` | nur erreichbar gegen einen Server **ohne** `activationTriggers` | **COMPATIBILITY** |
| `extend_dictation_window` Phasenzweige | `core/controller.py:1070-1085` | `SEGMENT_ACTIVE`, `WAITING_FIRST_SPEECH`, `FOLLOWUP_WAIT` sind gegen Produktivserver nie gesetzt; erreichbar bleibt nur `state == STARTING` (`:1064`) und der Endzweig `not_active` (`:1086`) | **PARTIALLY DISCONNECTED** |
| `trigger action=extend` | `core/controller.py:1081-1084` | liegt im unerreichbaren Phasenzweig; der Client sendet `extend` im Produktivpfad **nie** | **DEAD** gegen Produktivserver |
| `_maintain_wake_word_mode` | `core/controller.py:2629-2650` | läuft dauerhaft; armiert per `trigger activate source="manual"` (`:631-633`, einzige Aufrufstelle mit Defaultwert `"manual"` `:695`) | **ACTIVE** |
| `_wake_mode_desired` | `core/controller.py:317-319`, `:1151-1160`, `:1294` | Wert wird aus `session.mode` bestimmt, nicht aus `wake_word_trigger_enabled` | **ACTIVE**, gespeist aus Legacy-Feld |
| `session.mode` | `core/config.py:276`, `:301-310`, `:334-336`; `core/settings_metadata.py:145-152`, `visible_when` in `:169,176,184,191,198,205`; `core/controller.py:1151-1160` | wirkt auf Triggerflags, Wake-Word-Armierung, UI-Sichtbarkeit und Darstellungsmodus | **ACTIVE** (Runtime-Autorität, kein reiner Migrationsadapter) |
| `OperatingMode`-Enum | `core/config.py:265-269` | Wertelieferant für `mode` und `presentation_mode` | **ACTIVE** |
| `presentation_mode` | `core/config.py:325-336` | erzeugt aus den Triggerflags wieder einen Betriebsmodusbegriff für die UI | **ACTIVE** |
| `HotkeyConfig.mode` (`toggle`/`actions`) | `core/config.py:501`, geprüft in `:518-519` | keine weitere Lesestelle im Produktivcode | **DEAD** (nur Validierung) |
| `HotkeyConfig.key` | `core/config.py:508`, `:511-513`, `:968-971` | reine Ladezeit-Migration, wird beim Speichern entfernt | **COMPATIBILITY** |
| `AvailabilityState.MICROPHONE_UNAVAILABLE` | `core/controller.py:74`, `ui/presentation.py:82-85` | keine Schreibstelle im Produktivcode; nur `tests/test_ui_widgets.py:152` | **DEAD** |
| `presentation_for_feedback(TransientEvent)` | `ui/presentation.py:173-208` | keine Aufrufstelle außerhalb `tests/test_ui_widgets.py` | **DEAD** |
| `TransientEvent` / `on_feedback_event` / Signal `feedback_received` | `core/controller.py:94-111`, `:334`, `ui/core_bridge.py:28`, `:101` | Signal wird gesetzt, aber in `ui/application.py:173-189` **nicht** verbunden; die Wirkung entsteht ausschließlich über die kanonische Abbildung `:485-497` | **PARTIALLY DISCONNECTED** |
| `_update_dictation_state` | `core/controller.py:446-462` | definiert, keine Aufrufstelle | **DEAD** |
| `ControllerStatus` / `get_status()` | `core/controller.py:148-160`, `:527-547` | keine Aufrufstelle außerhalb Tests (Kommentar nennt sie „AP4 backwards compat") | **DEAD** |
| `RealtimeSTTClient` (headless) | `app.py:31-101`, `run_headless` `:104-123` | nur über `--headless` erreichbar | **COMPATIBILITY** |
| Doppelte Fensterzeiten | `core/config.py:439-461` `DictationWindowConfig` gegen `core/config.py:287-289` `session.*_timeout` | beide beschreiben dieselben Fristen; gegen Produktivserver wirkt nur die Session-Variante | **PARTIALLY DISCONNECTED** |
| `warning`-Nachrichten des Servers | `core/controller.py:1673-1753` | kein Zweig für `event_type == "warning"` | **DEAD** (Empfangsseite fehlt) |
| Lokales VAD | – | `grep -rin "vad\|webrtc\|silero"` über `core/` und `ui/` liefert **nur** einen Docstring (`core/config.py:441`); `requirements.txt` enthält keine VAD-Abhängigkeit | **vollständig entfernt** |

### 16.2 voice-stt-server

| Fund | Datei/Symbol | Befund am Code | Kategorie |
|---|---|---|---|
| `RealtimeSession` | `server.py:2103-2535` | wird **nirgends** instanziiert; die einzige Erwähnung außerhalb der Definition ist eine Typannotation (`server.py:4359`). Produktiv wird ausschließlich `RecorderBackedRealtimeSession` erzeugt (`server.py:4615`) | **DEAD** |
| `VoiceActivityDetector` | `server.py:2067-2102` | einziger Nutzer ist `RealtimeSession.__init__` (`server.py:2110`) | **DEAD** |
| `ActivationController.finalized()` | `activation.py:312-320` | `grep -rn "\.finalized()"` über `api_fastapi_server/` liefert keinen Aufrufer | **DEAD** |
| Phase `finalizing` | `activation.py:34`, `:353-356` | wird erreicht, aber regulär nie verlassen (nur über `activate` oder `reset`) | **PARTIALLY DISCONNECTED** |
| Legacy-Wake-Word-Follow-up | `server.py:3924-3982` `_start_wakeword_followup_window`, Timerthread `:3977-3982` | Aufruf steht hinter `if self._activation is None:` (`server.py:3883-3888`), also nur im Legacy-Admissionmodus | **COMPATIBILITY** |
| `_clear_recorder_followup_gate_locked` | `server.py` (aufgerufen `:2762`, `:2792`, `:4063`, `:4104`) | gehört zum Legacy-Follow-up | **COMPATIBILITY** |
| `activation_config.mode == "legacy"` | `server.py:1047-1056`, `:2555-2562`, `:2603` | für Clients ohne Triggerparameter; der Desktop-Client sendet beide Flags immer (`core/config.py:399-400`) | **COMPATIBILITY** |
| `merged` / `already_active` als akzeptierte Antworten | `activation.py:177-187` | im Produktivpfad erreichbar (Clienttrigger und `_on_wakeword_detected` `server.py:4087`) | **ACTIVE** |
| Gate-Aufrufe in `try/except Exception` | `server.py:3119-3128`, `:3131-3140` | ein Recorder ohne Gate-API führt zu einem stillen `LOGGER.debug`; die Activation gilt trotzdem als akzeptiert und Events werden publiziert | **ACTIVE**, aber fehlerverschluckend |
| `metrics`-Kommando | `server.py:7593-7598` | vom Desktop-Client nicht gesendet | **COMPATIBILITY** |
| `AudioToTextRecorderClient` | `VoiceSTT/audio_recorder_client.py` (987 Zeilen), exportiert in `VoiceSTT/__init__.py:25` | keine Nutzung in `api_fastapi_server/` | **DEAD** im Serverpfad, öffentlicher Bibliotheksexport |
| `recorder.wakeup()` | `VoiceSTT/audio_recorder.py:709-715` | keine Aufrufstelle in `api_fastapi_server/` | **UNKNOWN** (Bibliotheks-API) |
| `recording.py:419-423` `continuous_listening` | `VoiceSTT/core/recording.py` | Rücksetzverhalten nach jeder Aufnahme; hängt an einer Recorderoption, die `_create_recorder` nicht setzt | **UNKNOWN** – Defaultwert wurde nicht geprüft |

### 16.3 led_controller_respeaker-v3

| Fund | Befund | Kategorie |
|---|---|---|
| Gesamtes Repository | `git status` leer, HEAD `aa2f14b`; keine Trigger-, Modus- oder Lifecyclelogik (Suche nach `hotkey|wake_word|wakeword|manual` findet nur `_ring_mode` als USB-Protokollzustand und XVF-Registerbeschreibungen) | **ACTIVE**, reine Darstellung |

### 16.4 Die halb entfernte Hotkey-Architektur im Zusammenhang

Der Code zeigt eine Migration, die an einer bestimmten Stelle angehalten wurde:

1. **Vollständig entfernt:** lokales VAD, lokale Aufnahmeende-Entscheidung.
   Im gesamten Client existiert weder VAD-Code noch eine VAD-Abhängigkeit.
2. **Abgeschaltet, aber nicht ersetzt:** die lokale Fenster-Statemaschine.
   `_client_owns_dictation_window` schaltet sie ab (`:683-693`); die
   Serverereignisse, die ihre Aufgabe übernehmen müssten
   (`activation_started`, `activation_closed`), werden empfangen, aber in
   `_handle_timeline_event` (`:1795-1801`) nur für das Löschen einer Warnung
   verwendet und im Eventnormalizer gar nicht erst erkannt
   (`core/event_normalizer.py:31-82`).
3. **Unverändert geblieben:** `DictationState`/`_dictation_requested` als
   alleinige Entscheidungsgrundlage für Hotkeybedeutung
   (`controller.py:1029-1041`), Buttonfreigabe und Trayanzeige
   (`ui/presentation.py:122-150`).
4. **Neu hinzugekommen, aber an den alten Zustand gehängt:** der
   Trigger-Contract (`send_trigger`/`request_trigger`/`trigger_ack`) schreibt
   sein Ergebnis in genau dieselben lokalen Felder (`:831-833`).

---

## 17. Produktionscode gegen Testdoubles

Untersucht wurden die Doubles, die an Architekturgrenzen stehen. Aufgeführt
sind **nur Abweichungen**.

### 17.1 `STTSession` gegen `FakeSTTSession` (`voice-stt-client/tests/test_controller.py:158-234`)

| # | Produktionsverhalten | Doubleverhalten | Folge |
|---|---|---|---|
| 1 | `supports_activation_triggers` ist `True`, sobald der Server die Fähigkeit meldet (`core/stt_session.py:573-578`); der Server meldet sie bedingungslos (`server.py:4976-4983`) | Attribut **fehlt**; `getattr(self.session, "supports_activation_triggers", False)` (`controller.py:680`) ergibt `False` | **Alle Tests, die `FakeSTTSession` benutzen, fahren den Nicht-Activation-Pfad.** `_client_owns_dictation_window` ist dort `True`, die lokale Fenstermaschine läuft, `_handle_timeline_event` nimmt den alten Zweig. Der Produktivpfad wird von diesen Tests nicht berührt. |
| 2 | `set_streaming(s)` setzt `_streaming` **und** `state.streaming_requested` (`core/stt_session.py:612-615`) | setzt nur `_streaming` (`tests/test_controller.py:191-192`) | `_begin_stream_and_trigger` verzweigt auf `state.streaming_requested` (`controller.py:701`). Der Unterschied entscheidet, ob `start` erneut gesendet wird. |
| 3 | `send_start` sendet und wartet; die Bestätigung kommt später als eigenes `status`-Ereignis über den Socket | `send_start` ruft **synchron** `on_state_change` und `on_event("status", state="listening")` auf (`tests/test_controller.py:205-223`) | Die Startbestätigung ist im Test deterministisch und sofort; Race zwischen Ack und Status wird nicht abgebildet. |
| 4 | `send_start` setzt `state.streaming_requested = True` (`stt_session.py:733`) | setzt es **nicht** | siehe 2 |
| 5 | `send_stop` setzt `_streaming=False` und `streaming_requested=False` | erhöht nur `stop_calls` und setzt `_streaming` | – |
| 6 | Reconnect erzeugt einen frischen `ClientState` mit `streaming_requested=False` (`stt_session.py:947-952`) | `generation` ist eine feste `1`; kein Generationswechsel | Generationsguards (`controller.py:822-824`, `:1487-1493`, `:2557`) werden nicht ausgelöst. |

### 17.2 `StreamCountingSession` (`voice-stt-client/tests/test_trigger_lifecycle.py:318-353`)

| # | Produktionsverhalten | Doubleverhalten | Folge |
|---|---|---|---|
| 7 | `send_start` setzt `streaming_requested=True`; `set_streaming(False)` in `stop_dictation` (`controller.py:993`) setzt es wieder auf `False` | `send_start` setzt `streaming_requested=True` (`:343`), `send_stop` auf `False` (`:348`); `set_streaming` wird **nicht** überschrieben und erbt Abweichung 2 | Nach `stop_dictation` bleibt `streaming_requested` im Double auf `True`. Der Test `test_two_activations_share_one_continuous_stream` (`:404-445`) misst deshalb `stream_starts == 1`. Mit produktionstreuem `set_streaming` misst derselbe Ablauf `stream_starts == 3` (nachgemessen im Diagnoseskript `repro_stream.py`). |

### 17.3 `TriggerCapableSession` (`voice-stt-client/tests/test_trigger_lifecycle.py:217-254`)

| # | Produktionsverhalten | Doubleverhalten | Folge |
|---|---|---|---|
| 8 | `request_trigger` legt einen `_PendingTrigger` an, wartet mit 5 s Timeout auf `trigger_ack`, prüft die Generation und verwirft bei Verbindungswechsel (`stt_session.py:~760-880`) | antwortet synchron mit einem konstruierten `TriggerAck` (`:239-250`) | Ack-Timeout, doppelte Acks, Acks aus alter Generation und der `_pending_triggers`-Lebenszyklus sind an dieser Stelle nicht abgebildet. |

### 17.4 `AudioCapture` gegen `FakeAudioCapture` (`voice-stt-client/tests/test_controller.py:130-155`)

| # | Produktionsverhalten | Doubleverhalten | Folge |
|---|---|---|---|
| 9 | öffnet einen PortAudio-Stream, startet einen Verarbeitungsthread und ruft `on_audio_packet` fortlaufend auf (`core/audio_capture.py:171-185`, `:264-295`) | zählt nur `start_calls`/`stop_calls`; ruft `on_audio_packet` **nie** auf | Der gesamte Audioweg – Verwerfen bei `_dictation_state != ACTIVE` (`controller.py:2528-2532`), Queue-Überlauf, Generationsprüfung, `send_audio` – wird von Controllertests nicht durchlaufen. |
| 10 | `start()` kann scheitern und stellt den Ausgangszustand wieder her (`core/audio_capture.py:186-194`) | scheitert nie | Der Rollbackpfad `controller.py:649-672` wird nur über einen gesonderten Fehler-Fake erreicht. |

### 17.5 `TextInjectionQueue` gegen `FakeInjectionQueue` (`voice-stt-client/tests/test_controller.py:95-128`)

| # | Produktionsverhalten | Doubleverhalten | Folge |
|---|---|---|---|
| 11 | startet einen **non-daemon**-Workerthread (`core/text_injector.py:422-425`) und schreibt in Zwischenablage/Tastatur | keine Threads, sammelt `enqueue_calls` | Für die Triggerarchitektur unkritisch. |

### 17.6 Recorder gegen `FakeRecorder` (`voice-stt-server/tests/unit/test_fastapi_server_multi_user.py:258-347`)

| # | Produktionsverhalten | Doubleverhalten | Folge |
|---|---|---|---|
| 12 | Der Aufnahmestart hängt am Gate (`VoiceSTT/core/recording.py:211-216` → `activation_control.py:185-186`) | `feed_audio` startet die Aufnahme beim **ersten** Paket bedingungslos (`:292-297`) | In diesen Tests kann Audio ohne Activation eine Aufnahme starten. |
| 13 | Recorder besitzt `set_activation_policy`, `open_controlled_activation`, `close_controlled_activation`, `abort_controlled_activation`, `controlled_activation_state` (`VoiceSTT/audio_recorder.py:709-745`) | **keine dieser Methoden** | `set_activation_policy` (`server.py:2604`) ist ungeschützt und würde scheitern; die Gate-Aufrufe in `_apply_activation_decision_locked` sind dagegen in `try/except Exception` gekapselt (`server.py:3119-3128`, `:3131-3140`) und schlucken den Fehler still. Dieses Double ist damit nur im Legacy-Admissionmodus einsetzbar. |
| 14 | Aufnahmeende über `post_speech_silence_duration` und `min_length_of_recording` (`recording.py:288-411`) | Ende nur über explizites `flush_buffered_audio` | Die reale VAD-Endezeit wird nicht getestet. |

### 17.7 Recorder gegen `GateAwareRecorder` (`voice-stt-server/tests/unit/test_server_controlled_e2e.py:65-145`)

| # | Produktionsverhalten | Doubleverhalten | Bewertung |
|---|---|---|---|
| 15 | Gate-Logik in `VoiceSTT/core/activation_control.py` | **verwendet exakt dieses Produktionsmodul** (`initialize_activation_control`, `configure_activation_policy`, `open_controlled_activation_gate`, …) und fragt in `feed_audio` `recording_activation_gate_is_open` | **keine Abweichung an der Gate-Grenze** – dieses Double ist an der wichtigsten Architekturgrenze treu |
| 16 | VAD mit Preroll, `min_length_of_recording`, `post_speech_silence_duration`, Wake-Word-Puffer | keine Zeitlogik; Aufnahme endet über explizite Aufrufe | Zeitverhalten des Aufnahmeendes bleibt ungetestet |
| 17 | `use_wake_words` folgt der Recorderkonfiguration und `process_wakeword` | `use_wake_words = bool(kwargs.get("wake_words"))`, Erkennung wird vom Test ausgelöst | Der Erkennungsweg selbst wird nicht durchlaufen |

### 17.8 Liste „Test sieht grün aus, weil …"

```text
1. … FakeSTTSession das Attribut supports_activation_triggers nicht besitzt und
   damit sämtliche Controllertests den Nicht-Activation-Pfad fahren, während
   der Produktivserver die Fähigkeit immer meldet.

2. … FakeSTTSession.set_streaming das Feld state.streaming_requested nicht
   setzt, obwohl STTSession.set_streaming es setzt und _begin_stream_and_trigger
   genau darauf verzweigt.

3. … StreamCountingSession.send_start streaming_requested setzt, set_streaming
   es aber nie zurücksetzt; damit misst der Continuous-Streaming-Test
   stream_starts == 1, wo der Produktionscode 3 erzeugt.

4. … FakeSTTSession.send_start die Serverbestätigung synchron im selben Aufruf
   liefert und damit jede Latenz und jedes Race zwischen trigger_ack und
   status-Ereignis verschwindet.

5. … FakeAudioCapture niemals ein Audiopaket liefert und der gesamte
   Verwerfungs- und Generationspfad des Audiowegs unausgeführt bleibt.

6. … TriggerCapableSession jeden Trigger sofort und immer beantwortet, wodurch
   Ack-Timeout, doppelte Acks und Acks aus alter Generation nicht auftreten
   können.

7. … FakeRecorder keine Gate-API besitzt und beim ersten Audiopaket
   bedingungslos aufnimmt, sodass in diesen Tests keine Activation nötig ist.

8. … kein Test den Server eine Activation beenden lässt: alle
   Lifecycle-Tests rufen controller.stop_dictation() selbst auf
   (tests/test_trigger_lifecycle.py:415, 431, 452, 541), womit der reale
   Abschlussweg über activation_closed nie durchlaufen wird.

9. … keine Assertion den Zustand nach einem vollständigen Diktatzyklus prüft:
   geprüft werden Zähler (stream_starts, triggers) und Feedbackimpulse, nicht
   dictation_state, dictation_requested oder die Trayanzeige.
```

---

## Vollständigkeitsstand

| Auftragsabschnitt | Status |
|---|---|
| 16 Dead Code / halb entfernte Architektur | vollständig; zwei `UNKNOWN` benannt |
| 17 Produktionscode gegen Testdoubles | vollständig für die Doubles an Architekturgrenzen |
