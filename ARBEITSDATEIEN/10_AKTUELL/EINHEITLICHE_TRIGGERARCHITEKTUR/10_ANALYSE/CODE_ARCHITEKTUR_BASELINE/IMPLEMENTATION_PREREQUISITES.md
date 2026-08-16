# IMPLEMENTATION_PREREQUISITES

**Phase C.** Was ein Implementierungsagent verstanden haben muss, bevor er
dieses System sicher umbauen darf – plus Checkpoint über den Stand dieser
Aufnahme.

---

## 1. Implementation Prerequisites Checklist

Jeder Punkt nennt die Datei, an der das Verständnis geprüft werden kann. Ein
Haken ist erst berechtigt, wenn der Agent die genannte Stelle gelesen **und**
die Kontrollfrage beantwortet hat.

### Stream-Lifecycle

```text
[ ] Verstanden, dass `start`/`stop` Streambefehle sind und `stop` serverseitig
    die laufende Activation verwirft.
    Beleg: server.py:2719-2745 stop_streaming -> _reset_activation_locked
    Kontrollfrage: Was passiert mit einer offenen Activation, wenn der Client
    `stop` sendet?

[ ] Verstanden, dass der Client den Stream heute pro Activation auf- und
    abbaut, weil `set_streaming(False)` das Feld `streaming_requested` loescht,
    auf das `_begin_stream_and_trigger` verzweigt.
    Beleg: core/stt_session.py:612-615 gegen core/controller.py:701 und :993
    Kontrollfrage: Wie viele `start`-Kommandos erzeugen drei Diktate?

[ ] Verstanden, dass im Leerlauf kein Audio flieszt, weil das Mikrofon erst in
    `_begin_start_locked` gestartet wird und Pakete bei
    `_dictation_state != ACTIVE` verworfen werden.
    Beleg: core/controller.py:648, :2528-2532
    Kontrollfrage: Wie kann der Server im Idle ein Wake Word hoeren?

[ ] Verstanden, dass der Server Audio ohne vorheriges `start` ablehnt.
    Beleg: server.py:2829-2831
```

### Server-Activation-State-Machine

```text
[ ] Alle neun Methoden, ihre erlaubten Ausgangszustaende und Ablehnungsgruende
    gelesen.
    Beleg: CODE_ARCHITECTURE_BASELINE.md §8.1 / activation.py:164-334

[ ] Den Unterschied zwischen `generation` (nur bei neuer Activation) und
    `version` (bei jeder Aenderung) verstanden, inklusive der Rolle von
    `version` als Stale-Guard der Timer.
    Beleg: activation.py:101-102, :289-300, server.py:3186-3208

[ ] Verstanden, dass `activate()` heute merged statt zu sperren und dass
    `finalized()` keinen Aufrufer hat.
    Beleg: activation.py:177-187 und :312-320
    Kontrollfrage: Wie verlaesst eine Activation mit Segmenten heute die
    Phase `finalizing`?

[ ] Verstanden, dass `_apply_activation_decision_locked` das Gate oeffnet und
    den Timer setzt, und dass Gate-Fehler dort still verschluckt werden.
    Beleg: server.py:3098-3148, insbesondere :3119-3128 und :3131-3140

[ ] Verstanden, dass `segment_active` serverseitig keinen Timer hat.
    Beleg: activation.py:240
```

### Client-State-Authorities

```text
[ ] Die Authority Matrix gelesen und benennen koennen, welche vier doppelten
    Wahrheiten existieren.
    Beleg: STATE_EVENT_COMMAND_ATLAS.md §9.2

[ ] Verstanden, dass `DictationState.ACTIVE` heute keinen ereignis- oder
    zeitgesteuerten Ausgang besitzt.
    Beleg: RUNTIME_FLOWS_AND_CONCURRENCY.md §12.1

[ ] Verstanden, dass `_window_phase` gegen den Produktivserver dauerhaft
    `INACTIVE` bleibt und trotzdem die Trayanzeige des Manual-Pfads bestimmt.
    Beleg: core/controller.py:683-693, :1795-1801 gegen ui/presentation.py:124-139

[ ] Verstanden, welche Thread- und Lockgrenzen gelten: `self._lock`
    (threading.Lock) fuer Felder, `_get_transition_lock()` (asyncio.Lock) fuer
    Uebergaenge, Qt-Signale nur ueber QueuedConnection.
    Beleg: core/controller.py:285-286, :356-359; ui/application.py:173-189
```

### Event- und Commandpfade

```text
[ ] Das vollstaendige Inventar Client->Server und Server->Client gelesen.
    Beleg: STATE_EVENT_COMMAND_ATLAS.md §10.1 bis §10.4

[ ] Verstanden, dass `activation.*` auf dem Kanal `transcription` emittiert
    wird und der Client sie deshalb doppelt verfehlt: unbekannter Ereignisname
    und Kanalpruefung.
    Beleg: server.py:4199-4224 gegen core/event_normalizer.py:31-82, :135-141

[ ] Die Liste der produzierten, aber nicht konsumierten Ereignisse gelesen –
    besonders `activationId`, `primarySource`, `sources` an allen
    Timeline-Events und `availableWakeWords` im `hello`.
    Beleg: STATE_EVENT_COMMAND_ATLAS.md §10.6

[ ] Verstanden, dass es keinen `warning`-Handler im Client gibt.
    Beleg: core/controller.py:1694-1753
```

### Timerbesitzer

```text
[ ] Das Timer-Inventar gelesen und die drei unbegrenzten Zustaende benennen
    koennen (Client ACTIVE, Server finalizing, Server segment_active ohne
    Recorder-Callback).
    Beleg: RUNTIME_FLOWS_AND_CONCURRENCY.md §12 und §12.1

[ ] Verstanden, dass der serverseitige Activation-Timer ein eigener Thread je
    Deadline ist, der ueber `version` und `_activation_timer_generation`
    doppelt abgesichert wird, inklusive der Windows-Granularitaetsschleife.
    Beleg: server.py:3210-3243

[ ] Verstanden, dass der Client-Ack 5 s und die Startbestaetigung 10 s Frist
    hat und dass eine Ueberschreitung die Verbindung recycelt.
    Beleg: core/controller.py:727-744, :932-941
```

### Configmigration

```text
[ ] Verstanden, dass `session.mode` heute drei Laufzeitwirkungen hat:
    Triggerflags, Wake-Word-Armierung, UI-Sichtbarkeit.
    Beleg: CONFIG_UI_FEEDBACK_ATLAS.md §13.3

[ ] Verstanden, dass der Dialog den *effektiven* Wert anzeigt und deshalb
    keine Aenderung meldet, wenn ein Haken auf seinem angezeigten Wert bleibt.
    Beleg: ui/settings_dialog.py:174-182 und :270-283

[ ] Verstanden, dass eine unbekannte Taste in der Nutzer-Config die
    *gesamte* Nutzerdatei verwirft.
    Beleg: core/config.py:852-860

[ ] Verstanden, dass zwei Zahlenwerke fuer dieselben Fristen existieren
    (15/3/15 lokal gegen 15/3/5 serverseitig).
    Beleg: core/config.py:443-445 gegen server.py:962-964
```

### UI-Zustandsherkunft

```text
[ ] Fuer jeden sichtbaren Zustand die Herkunft benennen koennen.
    Beleg: CONFIG_UI_FEEDBACK_ATLAS.md §14.2

[ ] Verstanden, dass es zwei Darstellungswege gibt (Snapshot-Basis und
    zeitlich begrenzter Feedback-Override) und dass der Override nach
    `duration_ms` auf die Basis zurueckfaellt.
    Beleg: ui/tray.py:174-190, :192-228, :252-255

[ ] Verstanden, dass die LED nach einer Transkription auf `ready_state`
    zurueckkehrt, nach einer Activation ohne Sprache aber nicht.
    Beleg: config.yaml:190-193 gegen das Fehlen einer activation.*-Regel
```

### Legacy-/Dead-Code-Grenzen

```text
[ ] Die Kategorisierung ACTIVE / PARTIALLY DISCONNECTED / DEAD /
    COMPATIBILITY / UNKNOWN gelesen.
    Beleg: LEGACY_AND_DEAD_CODE_MAP.md §16

[ ] Verstanden, dass `RealtimeSession` und `VoiceActivityDetector` ein
    vollstaendig toter zweiter Aufnahmeweg sind.
    Beleg: server.py:2067-2535, einzige Erwaehnung server.py:4359

[ ] Verstanden, welche Teile absichtliche Adapter sind und bleiben duerfen
    (`activation_config.mode == "legacy"`, Legacy-Wake-Follow-up,
    `HotkeyConfig.key`, Headless-Modus).
```

### Testdouble-Abweichungen

```text
[ ] Die neun Punkte der Liste "Test sieht gruen aus, weil ..." gelesen.
    Beleg: LEGACY_AND_DEAD_CODE_MAP.md §17.8

[ ] Verstanden, dass `FakeSTTSession` kein `supports_activation_triggers`
    besitzt und deshalb saemtliche Controllertests den Nicht-Activation-Pfad
    fahren.
    Beleg: tests/test_controller.py:158-234 gegen core/controller.py:677-680

[ ] Verstanden, dass `GateAwareRecorder` an der Gate-Grenze treu ist und als
    Vorbild fuer weitere Doubles taugt.
    Beleg: tests/unit/test_server_controlled_e2e.py:65-145
```

### Arbeitsregeln

```text
[ ] Verstanden, dass die Zielbildspezifikation vorhandenem Code, vorhandenen
    Tests und vorhandener Dokumentation vorgeht, und dass mehrere bestehende
    Tests deshalb bewusst ersetzt werden muessen.
    Beleg: TARGET_MIGRATION_MAP.md §2.7

[ ] Verstanden, dass ein gruener Testlauf kein Abnahmenachweis ist und der
    Status ohne reale Abnahme "offen" heisst.
```

---

## 2. Checkpoint – Stand dieser Aufnahme

### 2.1 Vollständig untersucht

| Bereich | Artefakt |
|---|---|
| Repository-Grenzen, Verantwortlichkeiten, Einstiegspunkte | `CODE_ARCHITECTURE_BASELINE.md` §1 |
| Startvorgang Client und Server bis stabiler Idle | dito §2 |
| ActivationController: Methoden, Transitionstabelle, Command-Matrix | dito §8 |
| LED-Grenze und tatsächlich benutzte API | dito §15 |
| Concurrency Map über beide Repositories | `RUNTIME_FLOWS_AND_CONCURRENCY.md` §3 |
| Audio-Datenpfad Mikrofon bis Final, inkl. Verwerfungspunkten | dito §4 |
| Hotkey-Ist-Ablauf je Zustand, mit Entscheidungsbaum | dito §5 |
| Wake-Word-Ist-Ablauf, Armierung und Deaktivierung | dito §6 |
| Side-by-Side-Vergleich Manual/Wake Word über 13 Phasen | dito §7 |
| Sequenzdiagramme A bis J | dito §11 |
| Timer-Inventar und Analyse unbegrenzter Zustände | dito §12 |
| Clientseitige State Machines und Authority Matrix | `STATE_EVENT_COMMAND_ATLAS.md` §9 |
| Event- und Commandinventar beider Kanäle | dito §10 |
| Config-Datenfluss und Doppelsteuerungen | `CONFIG_UI_FEEDBACK_ATLAS.md` §13 |
| Herkunft jedes sichtbaren UI-Zustands | dito §14 |
| Dead Code und halb entfernte Architektur | `LEGACY_AND_DEAD_CODE_MAP.md` §16 |
| Testdouble-Abweichungen an Architekturgrenzen | dito §17 |
| Soll/Ist-Zuordnung und Migrationsreihenfolge | `TARGET_MIGRATION_MAP.md` |

### 2.2 Teilweise untersucht

| Bereich | Was fehlt | Nächster Einstiegspunkt |
|---|---|---|
| Eventstream-Protokoll `/ws/logs` | Replay-, Gap- und Cursor-Semantik nur an der Oberfläche gelesen; die serverseitige SQLite-Ablage wurde nicht geöffnet | `voice-stt-client/core/event_protocol.py` (532 Zeilen), `server.py:6479-6776` |
| Transkriptionspfad ab `InferenceJob` | Scheduler, Fairness-Queue und Engine-Worker nur in ihrer Threadstruktur erfasst | `server.py:1559-2050` |
| Realtime-/Zwischentext | `run_realtime_worker` und der Textstabilisator nicht gelesen | `VoiceSTT/core/realtime.py`, `VoiceSTT/core/realtime_text_stabilizer.py` |
| Wake-Word-Erkennung im Detail | `process_wakeword` nur als Aufrufstelle erfasst | `VoiceSTT/core/wakeword.py` (269 Zeilen) |
| Preroll | Vorhandensein und Einbindung belegt, Puffergrößen nicht durchgerechnet | `VoiceSTT/core/preroll.py` (434 Zeilen) |
| Browserclient | `app_browserclient/client.js` wurde geändert, aber nicht gelesen; er ist eine zweite Gegenstelle des Protokolls | `voice-stt-server/app_browserclient/client.js` |
| Textinjektion | Für die Triggerarchitektur nicht relevant, deshalb nur als Threadgrenze erfasst | `voice-stt-client/core/text_injector.py` |

### 2.3 Noch offen (`UNGEKLÄRT` in den Artefakten)

| Frage | Ort |
|---|---|
| Defaultwert und Wirkung von `continuous_listening` im Recorder (`recording.py:419-423`) | `LEGACY_AND_DEAD_CODE_MAP.md` §16.2 |
| Ob `recorder.wakeup()` außerhalb der Bibliotheks-API benutzt wird | dito |

### 2.4 Nächster sinnvoller Einstiegspunkt

Für die Umsetzung: **AP-1 der Migrationsreihenfolge**
(`TARGET_MIGRATION_MAP.md` §3), also `activation.py` `activate()` und
`finalized()`. Alles Weitere hängt daran.

Für weitere Aufnahme, falls gewünscht: der Eventstream (`event_protocol.py`
plus `server.py:6479-6776`), weil er der einzige Kanal ist, über den die
Activation-Ereignisse den Client heute überhaupt erreichen können.

---

## 3. Arbeitsregeln, die eingehalten wurden

* Keine Produktcode-, Test- oder Configänderung in den drei Repositories.
* Kein Commit, Push, Merge, Rebase, Tag oder PR.
* Analyseartefakte ausschließlich unter
  `zusammenarbeit/aktionen/einheitliche-triggerarchitektur/code-architektur-baseline/`.
* Phase A wurde ohne Rückgriff auf bestehende Architektur-, Plan-, Status- oder
  Reportdokumente erstellt; die aus einem früheren Auftrag im Kontext
  befindlichen Dokumente wurden offengelegt und jede Aussage neu am Code
  belegt. Ein Befund des früheren Berichts wurde dabei widerlegt und in
  `TARGET_MIGRATION_MAP.md` §0 korrigiert.
