# TARGET_MIGRATION_MAP

**Phase B.** Erst nach Abschluss der Code-Only-Aufnahme erstellt. Sollquelle:
`.claude/ZIELBILD_EINHEITLICHE_TRIGGERARCHITEKTUR.md`.
Ist-Belege stammen aus den Phase-A-Artefakten dieses Ordners.

**Kein zweiter Diagnosebericht.** Dieses Dokument ordnet ausschließlich zu:
behalten / umbauen / entfernen.

---

## 0. Korrektur einer früheren Aussage

Die Code-Only-Aufnahme hat einen Befund des vorangegangenen Diagnoseberichts
widerlegt und das ändert die Migration:

> Der Server veröffentlicht sehr wohl einen realen Wake-Word-Katalog:
> `hello.sessionCapabilities.wakeWord.availableWakeWords` mit `id`, `label`,
> `availableFormats` und `default` (`server.py:4943-4971`), gespeist aus
> `VoiceSTT/core/openwakeword_catalog.py:210-236`.

Die vom Zielbild §14.3 **bevorzugte** Mehrfachauswahl aus einem realen Katalog
ist damit **ohne Protokolländerung baubar**. Sie war fälschlich als eigenes
Serverarbeitspaket eingestuft. Es fehlt allein die Auswertung im Client:
`core/stt_session.py:573-578` liest aus `sessionCapabilities` nur
`activationTriggers`.

---

## 1. Migration Map

Legende: ✔ = trifft zu.

| Ist-Komponente | Sollrolle laut Zielbild | behalten | umbauen | entfernen | Grund |
|---|---|---:|---:|---:|---|
| `VoiceSTT/core/activation_control.py` (Gate) | §2.3, §10: einziger Aufnahmeweg | ✔ | | | Das Gate ist die einzige Autorität für den Aufnahmestart (`recording.py:211-216`), kennt die Triggerquelle nicht und ist generationsgebunden. Erfüllt das Zielbild bereits. |
| `VoiceSTT/core/recording.py` `run_recording_worker` | §1: eine Recording-/VAD-Logik | ✔ | | | Ein Pfad für beide Quellen, belegt. |
| Kein lokales VAD im Client | §11, I-10 | ✔ | | | Vollständig entfernt, nachgewiesen. |
| `trigger` / `trigger_ack` mit `commandId`-Idempotenz | §17: Commands auf laufendem Stream | ✔ | | | Vertrag ist tragfähig; nur die Semantik dahinter stimmt nicht. |
| `ActivationController` als Objekt und Lock-Modell | §10: zentrale Autorität | ✔ | ✔ | | Struktur richtig (RLock, monotone Zeit, `version`-Guard, `generation`). Zu ändern sind `activate`, das Lockkonzept und der Abschluss. |
| `ActivationController.activate()` Merge-Zweig (`activation.py:177-187`) | §5, §7, §8: erster Trigger gewinnt, zweiter wird unterdrückt | | | ✔ | Merge ist in §8 wörtlich ausgeschlossen. Ersatz: `accepted=False, reason="activation_locked"`, **ohne** `sources`-Ergänzung, ohne `version`-Anstieg, ohne Event, ohne Gate-Aufruf. |
| `ActivationController.activate()` aus `finalizing` (`:189-202`) | §5: Lock bis zum stabilen Idle | | ✔ | | Muss bis `finalized()` sperren. |
| `ActivationController.finalized()` (`:312-320`) | §5, §13: Freigabepunkt des Locks | | ✔ | | Struktur richtig, **Aufrufer fehlt**. Muss an das Ende der letzten Transkription der Activation gebunden werden. |
| Ereignis `activation_extended` bei `reason="merged"` (`server.py:3154`) | – | | | ✔ | Entfällt mit dem Lock. `extended` bleibt nur für echtes `extend`. |
| `_on_wakeword_detected` → `activate("wake_word")` (`server.py:4083-4090`) | §7: keine fachliche Wirkung während Activation | | ✔ | | Aufruf bleibt, die Ablehnung wird zum Normalfall: nur Audit, kein Statuswechsel, kein `_wakeword_voice_window = True` während gesetztem Lock. |
| Gate-Aufrufe in `try/except Exception` (`server.py:3119-3140`) | §10 | | ✔ | | Ein Gate, das sich nicht öffnen lässt, darf keine akzeptierte Activation ergeben. Fehler muss die Entscheidung zurücknehmen. |
| `_start_wakeword_followup_window` (Legacy) | §2.3: keine getrennten Follow-up-Pfade | ✔ | | | Bereits im Controlled-Modus abgeschaltet (`server.py:3883-3888`). Als `COMPATIBILITY` belassen. |
| `activation_config.mode = "legacy"` | §12: begrenzter Migrationsadapter | ✔ | | | Zulässiger Adapter für Clients ohne Triggerparameter. |
| `RealtimeSession` + `VoiceActivityDetector` (`server.py:2067-2535`) | – | | | ✔ | Nirgends instanziiert. Zweiter, unbenutzter Aufnahmeweg mit eigenem VAD – genau das Bild, das §2.3 verbietet, auch wenn er tot ist. |
| **Client** `DictationState` / `_dictation_requested` | §11: kein zweiter Lifecycle | | ✔ | | Struktur (Snapshot, Revision, Publish) ist brauchbar. Die **Quelle** muss vom lokalen Kommandoergebnis auf den gespiegelten Activation-Zustand umgestellt werden. |
| `DictationWindowPhase` + `_arm_dictation_window` + `_dictation_window_timeout` | §11: keine lokale Diktat-State-Machine | | | ✔ | Gegen den Produktivserver bereits abgeschaltet, aber weiterhin UI-Quelle. Ersatz ist der Spiegel aus §2. |
| `_client_owns_dictation_window` | – | | | ✔ | Nur sinnvoll, solange Server ohne Contract unterstützt werden. Entfällt mit dem Spiegel; alternativ als klar benannter Adapter isolieren. |
| `extend_dictation_window()` als Zweitbedeutung des Hotkeys (`:1040`) | §6.2: Hotkey bedeutet `finish` | | ✔ | | Funktion darf bleiben (§10 lässt `extend` zu), aber **nicht** als Zweitbedeutung des Diktat-Hotkeys. |
| `primary_dictation_action` Wake-Word-Zweig (`:1031-1038`) | §9: Pause ist eine eigene Bedienfunktion | | | ✔ | „Wake Word pausieren/aktivieren" auf dem normalen Hotkey ist in §9 ausdrücklich verboten. |
| `_maintain_wake_word_mode()` (`:2629-2650`) | §3: ein kontinuierlicher Stream | | | ✔ | Armierungsschleife ist ein Arm-/Disarm-Modell. Mit dem kontinuierlichen Stream entfällt sie ersatzlos. |
| `_wake_mode_desired` | – | | | ✔ | Entfällt mit dem Maintainer; zusätzlich aus `mode` abgeleitet und damit doppelt unzulässig. |
| `_begin_stream_and_trigger(source="manual")` (`:695-712`) | §1: Unterschied endet am Triggereingang | | ✔ | | `start` gehört an den Sessionaufbau, nicht an den Trigger. Der Trigger wird zu einem reinen `trigger`-Kommando. |
| `audio.start()`/`audio.stop()` an der Activation (`:648`, `:992`) | §3, §11 | | ✔ | | Audioerfassung wird an die Session gebunden. |
| Verwerfen von Audio bei `_dictation_state != ACTIVE` (`:2528-2532`, `:2551-2558`, `:2583-2589`) | §3 | | ✔ | | Ersetzen durch Mute-Prüfung und Generationsprüfung. |
| `session.set_streaming(False)` in `stop_dictation` (`:993`) | §3: `stop` ist ein Streambefehl | | | ✔ | Beendet konzeptionell den Stream beim Ende einer Activation. |
| `STTSession.send_start` / `send_stop` | §3: Stream-Lifecycle | ✔ | | | Bleiben Streambefehle; nur ihre Aufrufer ändern sich. |
| `_discard_pending_triggers` bei Verbindungswechsel (`stt_session.py:944-946`, `:1051`) | §16 | ✔ | | | Erfüllt bereits „Pending Commands kontrolliert verwerfen". |
| `_resolve_trigger_ack` mit Generationsprüfung (`:842-880`) | §16 | ✔ | | | Erfüllt „stale Generationen beeinflussen keine Events". |
| `core/event_normalizer.py` `_SERVER_EVENTS` | §10, §15 | | ✔ | | Muss `activation.started`, `activation.suppressed`, `activation.closed`, `activation.finalized` aufnehmen. |
| `CanonicalEventType` (`core/event_models.py:71-105`) | §15 | | ✔ | | Vier neue `server.activation.*`-Werte. |
| `FeedbackEngine` / `FeedbackReducer` | §15: ein Feedbackmodell | ✔ | | | Struktur ist source-neutral und dedupliziert korrekt; nur die Ereignismenge wächst. |
| `feedback_mappings` in `config.yaml` | §15 | ✔ | ✔ | | LED/Sound bereits source-neutral. Zu ergänzen: Regeln für die Activation-Ereignisse (insbesondere Rückkehr auf `ready_state` beim Abschluss ohne Sprache). |
| `presentation_for_snapshot` Zweiteilung (`ui/presentation.py:98-140`) | §15, I-9 | | ✔ | | Ein Zweig, gespeist aus dem gespiegelten Serverzustand. |
| `presentation_for_mapped_action(operating_mode=…)` (`:211-226`) | §15 | | ✔ | | Parameter entfällt; eine Farbfamilie je fachlichem Zustand. |
| `SessionConfig.presentation_mode` (`core/config.py:325-336`) | §12 | | | ✔ | Erzeugt aus Triggerflags wieder einen Betriebsmodusbegriff. |
| `session.mode` als Runtime-Größe | §12: nur einmalige Übersetzung | | ✔ | | Ladezeit-Migration behalten, alle Laufzeit-Lesestellen entfernen. |
| `session.mode` als sichtbare Einstellung (`settings_metadata.py:145-152`) | §14.1 | | | ✔ | Im Dialog ausdrücklich verboten. |
| `visible_when=("session.mode", …)` (6 Stellen) | §14.2, §14.3 | | ✔ | | Umstellen auf `session.wake_word_trigger_enabled`. |
| `SettingsDialog._build_settings_tab` (`:110-128`) | §14.3 | | ✔ | | Gruppen erst nach Sichtbarkeitsprüfung anlegen; `visible_definitions()` (`settings_metadata.py:327-340`) existiert bereits und wird nicht benutzt. |
| Checkbox-Anzeige des **effektiven** Werts (`settings_dialog.py:174-182`, `:270-283`) | §14.2 | | ✔ | | Ein Haken muss den gespeicherten Wert zeigen, sonst überschreibt `mode` ihn unbemerkt. |
| Gruppe „Hotkey-Diktatfenster" (`settings_metadata.py:179-206`) | §14.5 | | ✔ | | Umbenennen und an `session.*_timeout` binden, die tatsächlich an den Server gehen. |
| `DictationWindowConfig` | §14.5 | | ✔ | | Mit `session.initial_speech_timeout` / `followup_timeout` / `extension_seconds` zusammenführen. |
| `session.wake_words` als einzelner String | §14.3: Mehrfachauswahl bevorzugt | | ✔ | | Serverprotokoll kann bereits Listen (`_split_wake_word_ids`, `server.py:684`) und liefert den Katalog. |
| `hello.sessionCapabilities.wakeWord.availableWakeWords` | §14.3 | ✔ | | | Vorhanden, muss nur konsumiert werden. |
| Fehlender Wake-Word-Pause-Hotkey | §9 | | | | **neu zu bauen**: `HotkeyConfig.wake_word_pause_key`, sechste Hotkey-ID, eigene Settings-Definition. |
| Hotkeyregistrierung nur bei Manual-Trigger (`ui/application.py:165-168`) | §9 | | ✔ | | Der Pause-Hotkey muss auch in einer Wake-Word-only-Installation registriert werden. |
| `_emit_feedback_event` Abbildung `DICTATION_START_FAILED → CLIENT_ACTION_BLOCKED` (`:485-489`) | §16: kein Warnloop | | ✔ | | Zwei verschiedene Sachverhalte auf einen Impuls; zusammen mit dem Maintainer die Ursache der Dauerwarnung. |
| `AvailabilityState` / Verfügbarkeitsmodell | §16 | ✔ | | | Bleibt; nach Apply/Reconnect aus dem neuen Serverzustand neu aufbauen. |
| `presentation_for_feedback`, `MICROPHONE_UNAVAILABLE`, `get_status`, `_update_dictation_state`, `HotkeyConfig.mode` | – | | | ✔ | Toter Code (Nachweis in `LEGACY_AND_DEAD_CODE_MAP.md` §16.1). Kein Zielbildbezug, aber Ballast auf dem Umbaupfad. |
| `led_controller_respeaker-v3` | §15 | ✔ | | | Reine Darstellung, keine Triggerentscheidung. Unverändert lassen. |

---

## 2. Antworten auf die Leitfragen des Auftrags

### 2.1 Welche guten neuen Komponenten können unverändert bleiben?

1. **Das Recorder-Gate** (`VoiceSTT/core/activation_control.py`). Es ist der
   Teil, der das Zielbild bereits erfüllt: eine Autorität, quellenblind,
   `(activation_id, generation)`-gebunden, mit sauberem `abort`/`shutdown`.
2. **`run_recording_worker`** als einziger Aufnahme-/VAD-Pfad.
3. **Der Trigger-Contract** (`trigger`/`trigger_ack`, `commandId`-Idempotenz mit
   begrenzter Historie, korrelierte Ablehnungen).
4. **Die Clientseite des Contracts**: `_pending_triggers`,
   `_resolve_trigger_ack`, `_discard_pending_triggers`.
5. **`FeedbackEngine`/`FeedbackReducer`** samt Deduplizierung und
   Replay-Unterdrückung.
6. **Die LED-/Sound-Policy** in `config.yaml` – bereits source-neutral.
7. **Das gesamte LED-Repository.**

### 2.2 Welche Komponenten sind strukturell richtig, nur falsch verdrahtet?

1. **`ActivationController`** – Zustandsmaschine, Locking und Zeitbasis sind
   richtig; falsch sind der Merge-Zweig, die fehlende Sperre über `finalizing`
   und der fehlende Aufrufer von `finalized()`.
2. **Der Client-Snapshotmechanismus** – Revision, Publish, Qt-Anbindung sind
   tragfähig; falsch ist die Quelle der Felder.
3. **`_handle_timeline_event`** – die Struktur „Server meldet, Client folgt"
   existiert; sie behandelt nur die falschen Ereignisse.
4. **Der Settings-Dialog** – `visible_definitions()` ist vorhanden und richtig,
   wird aber vom Dialogaufbau nicht benutzt.
5. **Der Wake-Word-Katalog** – vollständig geliefert, nicht konsumiert.

### 2.3 Welche Altkomponenten müssen vollständig weg?

```text
core/controller.py  DictationWindowPhase + _arm_dictation_window
                    + _dictation_window_timeout + _pending_window_extension
core/controller.py  _maintain_wake_word_mode
core/controller.py  _wake_mode_desired
core/controller.py  _client_owns_dictation_window
core/controller.py  primary_dictation_action Wake-Word-Zweig (Pause/Aktivieren)
core/config.py      SessionConfig.presentation_mode
core/config.py      session.mode als Laufzeitgröße (Ladezeit-Migration bleibt)
core/settings_metadata.py  Definition session.mode und alle visible_when darauf
ui/presentation.py  operating_mode-Parameter und die zweite Farbfamilie
activation.py       Merge-Zweig in activate()
server.py           Ereignis activation_extended mit reason="merged"
server.py           RealtimeSession + VoiceActivityDetector (toter zweiter Weg)
```

### 2.4 Welche Schnittstellen müssen sich ändern?

| Schnittstelle | Änderung |
|---|---|
| `ActivationController.activate(source)` | Rückgabe `accepted=False, reason="activation_locked"` bei gesetztem Lock; keine Zustandsänderung |
| `ActivationController` | neues Feld `locked` bzw. Ableitung aus `phase != inactive`; explizit im `snapshot()` |
| `ActivationController.finalized()` | bekommt einen Aufrufer und einen Hard-Timeout-Fallback |
| Serverereignisse | neu: `activation.finalized`; neu: `activation.suppressed` (rein diagnostisch, §7 letzter Absatz) |
| `hello.activationConfig` | ergänzen um den aktuellen Lock-/Phasenstand für den Wiederaufbau nach Reconnect |
| Client `STTController` | neuer `ActivationMirror` als einzige Quelle; `primary_dictation_action` verzweigt darauf |
| Client `EventNormalizer` | `_SERVER_EVENTS` um vier `activation.*`-Einträge; Kanalprüfung beachten (`activation.*` wird heute auf dem Kanal `transcription` emittiert, `server.py:4212-4224`) |
| `HotkeyConfig` | neues Feld `wake_word_pause_key` |
| `ui/hotkeys.py` | sechste Hotkey-ID |
| `presentation_for_snapshot` / `presentation_for_mapped_action` | ohne `operating_mode` |
| `SessionConfig` | `wake_words` als Liste; `mode` verlässt das Laufzeitmodell |

### 2.5 Welche Zustände müssen zusammengeführt werden?

| heute getrennt | Ziel |
|---|---|
| `DictationState` + `_dictation_requested` + `DictationWindowPhase` (Client) und `ActivationController.phase` (Server) | **ein** gespiegelter Activation-Zustand im Client |
| `DictationWindowConfig` (15/3/15 s) und `session.*_timeout` (→ 15/3/5 s) | **ein** Satz Fristen, serverseitig maßgeblich |
| `_wake_mode_desired` und `activation_config.wake_word_enabled` | entfällt, es bleibt die Triggerkonfiguration |
| `session.mode` und die beiden Triggerflags | nur noch die Flags |
| zwei Trayzweige nach `operating_mode` | ein Zweig aus dem Serverzustand |

### 2.6 Welche neuen Events/Commands fehlen?

```text
Server -> Client   activation.finalized     Rueckkehr nach Idle, loest den Lock
Server -> Client   activation.suppressed    unterdrueckter Trigger, rein diagnostisch
Server -> Client   activation.started/.closed  vorhanden, muessen konsumiert werden
Client  -> Server  (kein neues Command noetig)
```

Der `finish`-Weg existiert bereits als Command; ihm fehlt nur der Auslöser
(Zweitbedeutung des Hotkeys).

### 2.7 Welche Tests müssen bewusst ersetzt werden, weil sie das falsche Soll festschreiben?

| Test | Datei | schreibt fest | Ersatz |
|---|---|---|---|
| `test_05_manual_then_wake_word_merges` | `voice-stt-server/tests/unit/test_server_activation_controller.py:76` | Merge einer zweiten Quelle | Negativtest zu I-5 |
| `test_06_wake_word_then_manual_merges` | dito `:87` | Merge | Negativtest zu I-5 |
| `test_09_sources_contains_triggers_without_duplicates` | dito `:119` | Aggregation mehrerer Quellen | `sources` bleibt einelementig |
| `test_12_trigger_during_followup_extends_deadline` | dito `:147` | zweiter Trigger verlängert | nur `extend` verlängert, `activate` nicht |
| `test_a_merge_does_not_raise_the_generation` | dito `:312` | Merge als Normalfall | entfällt |
| `test_a_trigger_during_finalizing_opens_a_new_activation` | dito `:368` | Lock endet vor der Finalisierung | Negativtest zu I-8 |
| `test_07_simultaneous_triggers_yield_single_activation` | dito `:98` | eine Activation, aber ohne unterdrückten Verlierer | I-7 mit genau einem `activation_locked` |
| `test_two_activations_share_one_continuous_stream` | `voice-stt-client/tests/test_trigger_lifecycle.py:404` | `audio.start_calls == 2`, Beenden per `stop_dictation` | ein Mikrofonstart je Session; Beenden durch Serverereignis |
| `test_extending_the_window_creates_no_second_stream` | dito `:466` | Hotkey verlängert während Activation | Hotkey bedeutet `finish` |
| `test_a_manual_trigger_inside_a_wake_word_turn_adds_no_second_sequence` | `voice-stt-client/tests/test_trigger_feedback_contract.py:284` | „der Server merged ihn" (Kommentar `:293`) | unterdrückter Trigger, kein Merge |
| `test_one_activation_yields_one_recording_sequence` | dito `:353` | `sources=["manual","wake_word"]` | `sources` bleibt einelementig |
| `FakeSTTSession` (Basisdouble) | `voice-stt-client/tests/test_controller.py:158` | fehlendes `supports_activation_triggers`, unvollständiges `set_streaming` | produktionstreues Double plus Kontrakttest |

---

## 3. Reihenfolge der Umsetzung

Bindend, weil jede spätere Stufe die frühere voraussetzt:

```text
1. Server: Lock in activate(), Sperre ueber finalizing, finalized() aufrufen,
   activation.finalized und activation.suppressed emittieren, Hard-Timeout.
2. Client: ActivationMirror aus den Serverereignissen; DictationWindowPhase
   und die lokale Fenstermaschine entfernen; Waechtertimer.
3. Client: kontinuierlicher Stream, Audio an die Session binden,
   _maintain_wake_word_mode entfernen.
4. Client: Hotkeysemantik (Idle -> activate, laufend -> finish) und
   sekundaerer Wake-Word-Pause-Hotkey.
5. Client: session.mode entmachten (nur noch Ladezeit-Migration).
6. Client: UI – ein Darstellungszweig, Gruppen mit Sichtbarkeit,
   Wake-Word-Mehrfachauswahl aus dem vorhandenen Katalog.
7. Beide: Warnschleifen ausschliessen, Testdoubles angleichen,
   falsche Sollannahmen in Tests ersetzen.
8. Reale Abnahme gegen I-1 bis I-11 mit Audio und Hardware.
```

---

## 4. Was diese Migration ausdrücklich **nicht** ist

Aus §16 des Zielbilds: Weder das Ausblenden der Legacy-Combobox noch ein
manuelles Zurücksetzen des weißen Rings, ein Unterdrücken der Warnmeldung oder
ein zusätzliches Wake-Word-Textfeld berühren eine der oben genannten Zeilen mit
Spalte „entfernen". Diese vier Eingriffe sind einzeln in weniger als einer
Stunde machbar und würden den Ist-Zustand aus Phase A unverändert lassen.
