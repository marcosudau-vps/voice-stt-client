# DECISIONS – Einheitliche serverseitige Triggerarchitektur

Jede Entscheidung nennt Fundstelle, Befund und Begründung. Der übernommene
Stand des vorherigen Agenten gilt als **UNTRUSTED PARTIAL IMPLEMENTATION** und
wurde einzeln geprüft.

---

## D-000 – Aufbau des eigenen Arbeitsbereichs per Clone statt Worktree-Kopie

**Entscheidung:** Die drei Repositories wurden per `git clone --no-hardlinks`
aus `P:\GithubRepos\marcosudau-vps\<repo>` erzeugt, auf den identischen
Ausgangs-HEAD gesetzt und der Arbeitsstand dateiweise übertragen.

**Begründung:** Der Fremdstand liegt in Git-Worktrees, deren `.git`-Datei auf
`P:\GithubRepos\marcosudau-vps\<repo>\.git\worktrees\…` zeigt. Ein Kopieren
dieser Metadaten hätte zwei Arbeitsbereiche an dieselbe Worktree-Registrierung
gebunden; ein `git worktree add` hätte in das gemeinsame Hauptrepository
geschrieben. Der Clone ist die einzige Variante, die den Fremdstand garantiert
nicht berührt. `temp_pytest/` wurde nicht übernommen, weil es reiner
Testlaufmüll ohne Quellcharakter ist.

---

## D-001 – `VoiceSTT/core/activation_control.py` → KORRIGIEREN

**Befund (selbst verifiziert):** Das Modul implementiert ein thread-sicheres
Gate mit `RLock` + `Event` und eine ID-Bindung. `recording_activation_gate_is_open()`
ignoriert im Controlled-Modus korrekt `recorder.wakeword_detected` — der von
§7.1 geforderte Wegfall der zweiten Autorität ist im VAD-Startpfad erfüllt.

**Fehlend gegenüber §14 (AP1):**

- Keine **Generationsbindung**. `close_controlled_activation_gate(activation_id)`
  vergleicht nur die ID. Der geforderte Fall „alte Generation darf neue
  Activation nicht schließen" ist nur zufällig erfüllt, solange IDs eindeutig
  sind, und für `close(None)` überhaupt nicht.
- Kein `abort`/`shutdown`-Verhalten am Gate.
- `open_controlled_activation_gate` mit `replace=True` ersetzt bedingungslos;
  eine ältere Activation könnte eine neuere überschreiben.

**Entscheidung:** Struktur BEHALTEN, um Generation und deterministisches
Abort/Shutdown erweitern.

---

## D-002 – Recorder-Anbindung (`audio_recorder.py`, `initialization.py`, `recording.py`) → BEHALTEN

**Befund:** Die vier Public-Methoden auf `AudioToTextRecorder`
(`set_activation_policy`, `open_controlled_activation`,
`close_controlled_activation`, `controlled_activation_state`) delegieren
sauber an das Modul. `initialize_activation_control(recorder)` wird in
`_assign_initial_attributes` aufgerufen, also bei jeder realen
Recorder-Erzeugung. `recording.py` ersetzt die frühere Inline-Bedingung durch
den Gate-Aufruf und liegt korrekt im Zweig „nicht aufnehmend", sodass ein
zweiter Trigger während laufender Aufnahme strukturell keine zweite Aufnahme
starten kann.

**Entscheidung:** BEHALTEN. Nachweis erfolgt in AP1 über realitätsnahe Tests
statt über `SimpleNamespace`.

---

## D-003 – `api_fastapi_server/activation.py` → KORRIGIEREN

**Befund:** Die Zustandsmaschine ist inhaltlich brauchbar: monotone Deadlines
über `time.monotonic`, stabile `primarySource`, duplikatfreie `sources`,
Generationszähler `_version`, Kollisionsmerge in `activate()`.

**Fehlend / zu korrigieren gegenüber §15 (AP2):**

- `expire()` existiert, hat aber **keinen Produktionsaufrufer**. Ohne Scheduler
  ist der gesamte Timeoutpfad tot (siehe D-006).
- Kein `finalizing`-Zustand; `recording_ended` springt direkt nach
  `followup_wait`. Der Auftrag lässt andere Namen zu, verlangt aber eindeutige
  Semantik für die Finalisierungsphase.
- `_close()` erhöht `_version`, `snapshot()` liefert `generation == _version`.
  Damit ändert sich die „Generation" auch bei reinen Merges. Für die
  Timerbindung ist das korrekt (jede Änderung entwertet alte Timer), für die
  öffentliche Korrelation ist es irreführend, weil `generation` an eine
  Activation gebunden sein soll. Wird getrennt in `generation` (pro Activation)
  und `version` (Änderungszähler).
- Doppelte Aliasnamen (`manual_enabled`/`manual_trigger_enabled`,
  `on_recording_start`/`recording_started`) sind Kompatibilitätsattrappen ohne
  Vertrag. Die Alias-Attribute `manual_enabled`/`wake_word_enabled` werden als
  einfache Attribute gesetzt und laufen bei späterer Änderung auseinander.

**Entscheidung:** Kern BEHALTEN, Punkte oben KORRIGIEREN.

---

## D-004 – Session-Admission für Controlled-Modus → NOT WIRED, ERGÄNZEN

**Befund (selbst verifiziert, entscheidender Fund):**
`parse_session_activation_query()` (server.py:950) und
`resolve_session_activation_config()` (server.py:992) haben **null**
Produktionsaufrufer. Belegt durch projektweite Suche: die einzigen Treffer
außerhalb der Definitionen liegen in `tests/unit/test_server_controlled_e2e.py`,
und auch dort wird nur `ResolvedSessionActivationConfig` **direkt konstruiert**,
nicht die Parse-/Resolve-Kette durchlaufen.

`admit_session()` (server.py:4262) besitzt keinen `activation_config`-Parameter
und reicht folglich nichts durch. `/ws/transcribe` (server.py:7061) liest nur
`parse_session_wake_word_query`.

**Folge:** In Produktion ist `session.activation_config.mode` immer `"legacy"`,
`self._activation` immer `None`. `handle_trigger_command` antwortet real
ausnahmslos mit `accepted: false, reason: "controlled_activation_disabled"`.
Der komplette Controlled-Pfad ist unerreichbar.

**Entscheidung:** ERGÄNZEN in AP4: Query-Parsing im WebSocket-Einstieg,
Durchreichen über `admit_session`, Ablehnung von `false/false` mit
korreliertem Fehler-Close.

---

## D-005 – `handle_trigger_command` → KORRIGIEREN

**Befund:** Grundstruktur (Validierung, `commandId`-Idempotenz mit begrenzter
`OrderedDict`-Historie, deterministisches Wiederholungs-Ack, Konfliktantwort
bei gleicher `commandId` mit abweichendem Payload) entspricht §16 im Ansatz.

**Zu korrigieren:**

- Keine Prüfung des **Stream-Lifecycle**. §16 verlangt Negativfälle „Trigger vor
  Streamstart", „Trigger nach Streamstop", „Trigger nach Close". Aktuell wird
  ein Trigger unabhängig von `self.streaming` verarbeitet.
- Der Ablehnungspfad vor der Idempotenzprüfung (`invalid_action`,
  `invalid_source`, `missing_command_id`, `invalid_payload`) cached nicht,
  ist aber deterministisch – akzeptabel, wird dokumentiert.
- `activationId` wird bei Ablehnung immer auf `None` gesetzt, auch wenn eine
  Activation läuft. Für Korrelierbarkeit von Ablehnungen (§16 „Ablehnungen
  müssen ebenfalls korrelierbar sein") wird die laufende `activationId`
  mitgegeben.
- Keine Erzeugung der von §17 geforderten Activation-Events.

---

## D-006 – Timeout/Scheduler → NOT STARTED, ERGÄNZEN

**Befund:** `self._activation_timer_generation = 0` wird in `__init__` gesetzt
und **nirgends gelesen**. `ActivationController.expire()` besitzt keinen
Produktionsaufrufer. Es existiert kein Timerthread, kein Scheduler-Job und kein
asynchroner Task für Activation-Deadlines.

**Folge:** Eine geöffnete Activation läuft nie ab. Das Recorder-Gate bliebe für
die restliche Sitzungsdauer offen — das genaue Gegenteil des Zielverhaltens.

**Entscheidung:** ERGÄNZEN in AP4: generationsgebundener Timerthread pro
Session, der `expire(expected_version)` aufruft und bei Erfolg Gate schließt und
`activation.closed` publiziert.

---

## D-007 – Capability `activationTriggers` → NOT STARTED, ERGÄNZEN

**Befund:** `session_capabilities()` (server.py:4608) liefert ausschließlich
`wakeWord`. `activationTriggers` existiert serverseitig nicht.
`STTSession.supports_activation_triggers` (Client, stt_session.py) prüft genau
auf `activationTriggers.supported` und liefert daher **immer** `False`.

**Bewertung:** Das ist kein Verstoß gegen §7.4 (es wird nichts Falsches
behauptet), aber es macht den gesamten neuen Clientpfad tot. Die Capability
darf laut §7.4 erst gemeldet werden, wenn `trigger` verarbeitet wird,
`trigger_ack` existiert, `commandId` idempotent ist und die Activation mit dem
Recorder verbunden ist.

**Entscheidung:** Capability wird **erst am Ende von AP4** eingeführt, nachdem
alle vier Bedingungen erfüllt sind — nicht vorher.

---

## D-008 – Zweite Follow-up-Autorität im Server → KORRIGIEREN

**Befund (eigener Fund, in der Vorarbeit nicht adressiert):**
`_start_wakeword_followup_window()` (server.py:3611) wird bei Aufnahmeende
(server.py:3575) aufgerufen und setzt direkt am Recorder
`wakeword_detected = True`, `wake_word_detect_time`, `wake_word_timeout`,
`start_recording_on_voice_activity = True`, `stop_recording_on_voice_deactivity = True`
und startet einen **eigenen Timerthread**
(`_wakeword_followup_timeout_worker`).

Im Controlled-Modus liefe dieser Legacy-Follow-up parallel zum
Follow-up-Fenster des `ActivationController`. §2.3 verbietet ausdrücklich
„ein paralleler Follow-up-Timer"; §7.1 verbietet eine zweite Recorder-Autorität.

**Entscheidung:** Der Legacy-Wakeword-Follow-up wird im Controlled-Modus
vollständig deaktiviert. Im Legacy-Modus bleibt er unverändert.

---

## D-009 – Clientseitige Ersetzung von `send_start`/`send_stop` → VERWERFEN

**Befund:** `core/controller.py:610` ersetzt `session.send_start()` durch
`send_trigger(action="activate")`, `core/controller.py:904` ersetzt
`session.send_stop()` durch `send_trigger(action="finish")`.

**Bewertung:** Direkter Verstoß gegen §3 („`start` und `stop` bleiben
ausschließlich Streambefehle") und gegen §26 („Hotkey auf `start`/`stop`
abbilden" — hier in umgekehrter Richtung). Fachlich wäre der Audiostream nie
gestartet worden, weil `start` nicht mehr gesendet wird. Der Zielzustand
verlangt einen **kontinuierlichen** Stream plus davon unabhängige
Triggerkommandos.

**Entscheidung:** VERWERFEN. `send_start`/`send_stop` bleiben Streambefehle;
Manualtrigger werden zusätzlich gesendet.

---

## D-010 – Clientseitige Migration `mode` → Triggerflags → KORRIGIEREN

**Befund:** `SessionConfig.effective_manual_trigger_enabled` liefert bei
`manual_trigger_enabled is None` unbedingt `True`, unabhängig vom Altwert
`mode`. Für `mode=wake_word` ergibt `query_parameters()` damit
`manualTriggerEnabled=true` **und** `wakeWordTriggerEnabled=true`.

§11.6 und §19 schreiben verbindlich vor:

```text
hotkey    → manual=true  / wake_word=false
wake_word → manual=false / wake_word=true
```

und verbieten die implizite Migration nach `true/true`.

**Verschärfend:** Der mitgelieferte Test
`tests/test_config.py::test_legacy_wake_word_mode_migrates_query_parameters`
behauptet `manualTriggerEnabled == "true"` als Sollverhalten und **zementiert
den Fehler**.

**Entscheidung:** Implementierung KORRIGIEREN, Test KORRIGIEREN. Ein Test, der
eine verbotene Migration festschreibt, ist kein Nachweis.

---

## D-011 – Fehlende `trigger_ack`-Verarbeitung im Client → ERGÄNZEN

**Befund:** `STTSession.send_trigger()` ist fire-and-forget. Es gibt keine
Pending-Command-Verwaltung, keinen Ack-Handler und keine Korrelation über
`commandId`. Der Client kann daher nicht zwischen akzeptiertem und abgelehntem
Trigger unterscheiden.

**Folge:** §20 („Kein fachliches Accepted-Feedback vor Ack") und die
Pflichttests aus GATE 7 (doppelte Ack, Ack nach Reconnect, alte Ack aus alter
Generation, Pending Command während Disconnect) sind nicht erfüllbar.

**Entscheidung:** ERGÄNZEN in AP7.

---

## D-012 – Übernommene Tests: Bewertung

Der Auftrag §0 stellt fest: „Ein fehlender Testnachweis ist kein bestandener
Test." Folgende Bewertung wurde vorgenommen:

| Datei | Bewertung | Entscheidung |
| --- | --- | --- |
| `test_server_activation_controller.py` | Legitime Unittests der Zustandsmaschine mit injizierter Uhr — für AP2 zulässig und sinnvoll. | BEHALTEN, um fehlende Fälle ergänzen |
| `test_recorder_activation_control.py` | Ausschließlich `SimpleNamespace`-Attrappen. §14 sagt ausdrücklich: „reine `SimpleNamespace`-Tests allein reichen nicht als AP1-Abnahme". | BEHALTEN als Schnelltests, um realitätsnahe Tests ERGÄNZEN |
| `test_server_trigger_contract.py` | Setzt `session._activation` direkt; testet damit `handle_trigger_command` isoliert. Als Vertragstest der Ack-Semantik brauchbar, als Integrationsnachweis nicht. | KORRIGIEREN + Integrationstest ergänzen |
| `test_server_controlled_e2e.py` | **False Positive.** Trägt „E2E" im Namen, benutzt aber weder WebSocket noch echten Recorder. `test_04` kommentiert „Wait for timeout to fire in background timer thread", ruft dann selbst `expire()` **und** `close_controlled_activation()` auf und prüft danach, dass das Gate geschlossen ist — der Test beweist nur, dass der Test selbst schließt. | ERSETZEN durch echten WebSocket-E2E-Test |
| `tests/test_config.py::TestAP6ConfigMigration` | Zementiert verbotene `true/true`-Migration. | KORRIGIEREN |
| `tests/test_stt_session.py::test_send_trigger_sends_json_payload` | Prüft nur die Serialisierung, nicht den Lifecycle. | BEHALTEN, ergänzen |

**Grundsatz für alle neuen Tests dieser Aktion:** Ein Test, dessen Assertion
durch eine Zustandsänderung erfüllt wird, die der Test selbst vorgenommen hat,
gilt nicht als Nachweis.

---

## Umsetzungsstand der Entscheidungen D-000 bis D-012

| Entscheidung | Umgesetzt | Nachweis |
| --- | --- | --- |
| D-000 Clone statt Worktree-Kopie | ja | GATE 0 |
| D-001 Gate korrigieren | ja | GATE 1 |
| D-002 Recorder-Anbindung behalten | ja | GATE 1 |
| D-003 ActivationController korrigieren | ja | GATE 2 |
| D-004 Session-Admission ergänzen | ja | GATE 4, Mutation M1 |
| D-005 `handle_trigger_command` korrigieren | ja | GATE 3 |
| D-006 Timeout-Scheduler ergänzen | ja | GATE 4, Mutation M2 |
| D-007 Capability erst nach Verdrahtung | ja | GATE 3/4 |
| D-008 zweite Follow-up-Autorität abschalten | ja | GATE 4, Mutation M4b |
| D-009 Ersetzung von `send_start`/`send_stop` verwerfen | ja | GATE 7, Mutation M1 |
| D-010 Migration korrigieren | ja | GATE 6 |
| D-011 `trigger_ack`-Verarbeitung ergänzen | ja | GATE 7 |
| D-012 Testbewertung | ja | GATE 1–4, 6–8 |

---

## D-013 – Scheduler-Allokationen instrumentieren statt schätzen

**Anlass:** Die Kollisionsmatrix verlangt `Scheduler allocations = 1`. Dafür
existierte keine Messmöglichkeit; die Invariante wurde bis dahin nur indirekt
über „ein Final" erschlossen.

**Entscheidung:** Ein `CountingScheduler` in der Testsuite macht die
tatsächlich an den Scheduler übergebenen Jobs je Session und Art abfragbar.
Das ist nicht-invasiv: `ManualScheduler` führt `self.jobs` ohnehin, die
Unterklasse macht die Instanzen nur erreichbar. **Kein Produktcode** wurde für
die Messung verändert.

---

## D-014 – Der simultane Kollisionsfall wird als echter E2E-Fall geführt

**Anlass:** Ein `ActivationController`-Concurrency-Test ersetzt den dritten
E2E-Fall ausdrücklich nicht.

**Entscheidung:** Der Fall läuft über den echten WebSocket: der Manualtrigger
durch die Empfangsschleife des Servers, das Wake Word über den
Recorder-Callback, beide freigegeben durch eine gemeinsame Barriere.
Zusätzlich wird `uuid4` im Activation-Modul verlangsamt, damit der kritische
Abschnitt breit genug für eine echte Verschränkung ist.

**Befund dabei:** Der Server sichert die Serialisierung **doppelt** ab — über
das Session-Lock und über das Controller-Lock. Erst wenn **beide** entfernt
werden, entstehen zwei Activations. Das ist protokolliert (Mutationen M2, M4,
M5), damit der Nachweis nicht stärker erscheint, als er ist.

---

## D-015 – Browserclient reparieren statt als „vorbestehend" abzulegen

**Anlass:** GATE 5 verlangt „Browserclient funktioniert". Der ausgelieferte
Beispielclient sprach ein Protokoll, das es nicht mehr gibt.

**Entscheidung:** Der Client wird **im Scope repariert** (Pfad, `start`,
Nachrichtentypen, Audiometadaten) statt den Befund nur zu dokumentieren. Er
bleibt bewusst ein Legacyclient ohne Triggerparameter und ist damit zugleich
die Kompatibilitätsreferenz.

**Grenze:** Ein Lauf im echten Browser braucht Browser und Mikrofonfreigabe.
GATE 5 bleibt deshalb `MANUAL VALIDATION REQUIRED` und wird **nicht** als PASS
geführt.

---

## D-016 – LED-Environment vorbereiten statt Fehlschläge wegzuklassifizieren

**Anlass:** Sechs LED-Tests waren rot; die Erklärung „vorbestehend und
umgebungsbedingt" war richtig, aber nicht ausreichend.

**Entscheidung:** Der inzwischen bekannte reproduzierbare Setup-Pfad
(`build_effects.py` im eigenen Clone plus Auflösung von `lefx` über den
`PYTHONPATH`) wird für den Testlauf benutzt. Ergebnis: **1506 passed,
23 skipped, 0 failed**. Der eingefrorene Fremdstand bleibt unangetastet.

---

## D-017 – Anzeige folgt den Triggerflags, nicht dem Legacy-Feld

**Anlass:** Im Dokumentationsaudit fiel auf, dass `ui/presentation.py` über
`snapshot.operating_mode` verzweigt, gespeist aus `session.mode`. Eine Session
mit `wake_word_trigger_enabled=true` bei unverändertem `mode: hotkey` hätte
„Wartet auf Hotkey" angezeigt.

**Entscheidung:** `SessionConfig.presentation_mode` leitet die Anzeige aus den
**effektiven Triggerflags** ab; `core/controller.py` und `ui/application.py`
benutzen es. Das Feld `session.mode` bleibt ausschließlich für die Migration
alter Konfigurationen erhalten und ist in den Settings-Metadaten als
„Legacy-Betriebsmodus" gekennzeichnet.
