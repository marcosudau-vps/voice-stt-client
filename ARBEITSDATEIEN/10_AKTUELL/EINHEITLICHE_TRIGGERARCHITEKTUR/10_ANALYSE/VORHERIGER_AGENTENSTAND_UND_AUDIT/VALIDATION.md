# VALIDATION – Nachweise je Gate

Grundsatz dieser Aktion: **Ein Test, dessen Assertion durch eine
Zustandsänderung erfüllt wird, die der Test selbst vorgenommen hat, gilt nicht
als Nachweis.** Eine grüne Gesamtsuite allein ist kein Gate-Nachweis.

Rohausgaben liegen unter `evidence/`.

## Gate-Vokabular

Es werden ausschließlich diese drei Werte verwendet:

| Wert | Bedeutung |
| --- | --- |
| **PASS** | **alle** verbindlichen Kriterien dieses Gates sind erfüllt und nachgewiesen |
| **MANUAL VALIDATION REQUIRED** | technisch fertig, aber mindestens ein Kriterium verlangt echte Benutzer- oder Hardwareinteraktion |
| **FAIL** | technisch noch nicht erfüllt |

Ein Gate ist **nie** „PASS für den automatisierbaren Teil". Besitzt es ein
offenes Kriterium, lautet der Status nicht PASS.

## Gate-Übersicht

| Gate | Thema | Status |
| --- | --- | --- |
| 0 | Recovery, Baseline, Ist-Verträge | **PASS** |
| 1 | Recorder Activation Gate | **PASS** |
| 2 | ActivationController | **PASS** |
| 3 | WebSocket-Triggervertrag | **PASS** |
| 4 | Serverintegration Trigger → Gate → Recording | **PASS** |
| 5 | Server bereit für alten und neuen Client | **MANUAL VALIDATION REQUIRED** |
| 6 | Konfigurationsmigration | **PASS** |
| 7 | Client-Lifecycle | **PASS** |
| 8 | Cross-Project Feedbackvertrag | **PASS** |
| 9 | Cross-Repository-Regressionsabnahme | **PASS** |
| 10 | Build und reale E2E-Abnahme | **MANUAL VALIDATION REQUIRED** |
| 11 | Dokumentation, Git und Abschluss | **PASS** |

**Gesamtstatus: MANUAL VALIDATION REQUIRED** – GATE 5 und GATE 10 verlangen
Benutzer- beziehungsweise Hardwareinteraktion. Nach §28 des Originalauftrags
lautet der Abschlussstatus daher nicht `DONE`, sondern `PARTIAL`.

---

## Testumgebung

Zwei Umgebungsprobleme mussten vor jeder belastbaren Messung gelöst werden.
Beide betreffen **nur die Ausführungsumgebung**, keinen Produktcode.

### U-1 – Blockierender `torch`-Import durch stehendes Windows-WMI

`from VoiceSTT.audio_recorder import AudioToTextRecorder` blockierte unbegrenzt.
Ursache über `faulthandler` ermittelt:

```text
torch/__init__.py:247 _load_dll_libraries
  → platform.machine()  → platform.uname() → platform.win32_ver()
  → platform._wmi_query()   ← hängt
```

Auch `Get-CimInstance Win32_OperatingSystem` in PowerShell antwortet auf dieser
Maschine nicht. Die WMI-Abfrage ist maschinenseitig blockiert.

**Behandlung:** Ein `sitecustomize.py` **außerhalb aller Repositories**
(im Scratchpad, per `PYTHONPATH` nur für Testläufe aktiv) füllt
`platform._uname_cache` vor und ersetzt `platform.win32_ver`. Kein
Repository-Inhalt wurde dafür verändert.

**Wirkung:** Importzeit von „hängt unbegrenzt" auf **5,3 s**.

### U-2 – `PermissionError` auf pytest-Basetemp

29 Servertests brachen mit
`PermissionError: [WinError 5] Zugriff verweigert: 'C:\Users\marco\AppData\Local\Temp\pytest-of-marco'`
im Setup ab. Behandlung: `--basetemp` auf ein Scratchpad-Verzeichnis. (Der
vorherige Agent hatte dasselbe Problem offenbar mit einem `temp_pytest/`-Ordner
im Repository umgangen; dieser wurde bewusst nicht übernommen.)

---

## Baseline vor eigenen Änderungen

| Repository | Ergebnis | Datei |
| --- | --- | --- |
| voice-stt-server | **426 passed, 13 skipped, 78 subtests passed** in 18,5 s – 0 Fehlschläge | `evidence/server_baseline.txt` |
| voice-stt-client | **1 failed, 454 passed, 186 subtests passed** in 32,3 s | `evidence/client_baseline.txt` |
| led_controller_respeaker-v3 | **6 failed, 1500 passed, 23 skipped** in 57,5 s | `evidence/led_baseline.txt` |

### Konsistenzprüfung der Serverbaseline

Der erste Serverlauf (vor der AP1-Änderung an `activation_control.py`, aber ohne
`--basetemp`) ergab `397 passed, 13 skipped, 29 errors`. Alle 29 Errors waren
ausschließlich U-2. Es gilt `397 + 29 = 426`; die Testmenge ist also vor und
nach der AP1-Änderung identisch und vollständig grün.

### Baseline-Fehlschlag Client (vorbestehend, nicht durch mich verursacht)

```text
tests/test_ap06_followup.py::TestDictationWindow::
    test_wake_word_followup_uses_server_duration_and_clears_on_speech
AssertionError: CanonicalEventType.CLIENT_DICTATION_TIMEOUT_WARNING not found in []
```

Der Test gehört zum **clientseitigen** Follow-up-/Countdown-Mechanismus, also
genau zu dem Bereich, den AP7 abbauen beziehungsweise auf serverseitige
Autorität umstellen soll. Er wird bei AP7 erneut bewertet.

### Baseline-Fehlschläge LED (vorbestehend, umgebungsbedingt)

Sechs Fehlschläge in `tests/interfaces/test_config.py`, alle mit derselben
Ursache: `discovery.installed_effect_sets()` liefert `{}`, weil die
`.lefxset`-Archive fehlen.

**Belegte Ursache:** Die global installierte Distribution
`led-controller-version-3` ist ein **Editable-Install, der in den eingefrorenen
Antigravity-Arbeitsbereich zeigt**:

```text
core-set        -> …\einheitliche-triggerarchitektur\led_controller_respeaker-v3\
                   packages\led-controller-version-3\src\lefx\sets\core_set\core-set.lefxset
                   exists = False
smartspeaker-set-> …\einheitliche-triggerarchitektur\led_controller_respeaker-v3\
                   packages\…\smartspeaker_set\smartspeaker-set.lefxset
                   exists = False
```

Die Archive fehlen **im Quellstand selbst**. Der Code kommentiert genau diesen
Fall: „in a checkout that means build_effects.py has not run".

Ein `scripts/build_effects.py`-Lauf in meinem eigenen Clone erzeugt die Archive
zwar, ändert aber nichts, weil der Editable-Install weiterhin in den
Fremdarbeitsbereich auflöst. Ein Build **dort** wäre eine Veränderung des
READ-ONLY-Standes und wurde deshalb **nicht** durchgeführt.

**Bewertung:** Diese sechs Fehlschläge sind vorbestehend und
umgebungsbedingt. Zusätzlicher Beweis der Unabhängigkeit: das LED-Repository ist
in meinem Arbeitsbereich `clean` auf `aa2f14b` — `git status --short` liefert
null Zeilen. Es wurde dort **keine einzige Datei geändert**. Damit kann keiner
der Fehlschläge aus meiner Arbeit stammen.

---

## GATE 0 – Baseline verstanden

```text
GATE:   0 – Recovery, Baseline und Ist-Verträge
STATUS: PASS
```

### EVIDENCE

**1. Worktrees, Branch, HEAD, Baseline dokumentiert** — `STATUS.md` Abschnitt 3.

| Repository | Branch | INITIAL_HEAD | dirty |
| --- | --- | --- | --- |
| voice-stt-server | feat/einheitliche-triggerarchitektur | `13c162950b944dc715fdd81983a7465f8eb0fd79` | ja |
| voice-stt-client | feat/einheitliche-triggerarchitektur | `178d32bdf17d4709307e7a2a944888d2cf294e42` | ja |
| led_controller_respeaker-v3 | feat/einheitliche-triggerarchitektur | `aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0` | nein |

**2. Übernahme des Fremdstands verifiziert.** Für alle drei Repositories sind
`git diff HEAD` sowie die Vereinigung aus `git diff --name-only HEAD` und
`git ls-files --others --exclude-standard` zwischen Quelle und eigenem
Arbeitsbereich **byteidentisch** (`diff` liefert keine Abweichung). Einzige
bewusste Auslassung: `temp_pytest/` (Testlaufmüll, siehe U-2).

**3. Keine fremden Änderungen im Scope.** Sämtliche 12 geänderten
beziehungsweise neuen Serverdateien und 7 Clientdateien liegen inhaltlich im
Triggerarchitektur-Umbau. Im LED-Repository existiert kein Dirty-Stand.
Stop-Regel C (§25) greift nicht.

**4. Jede Agentenänderung klassifiziert** — `DECISIONS.md`, Entscheidungen
D-001 bis D-012, jeweils mit Fundstelle und Begründung.

**5. Producer/Consumer der wesentlichen Verträge identifiziert** —
`CONTRACTS.md`, C-01 bis C-09.

**6. Contract-Iststand dokumentiert** — `CONTRACTS.md`.

**7. Baselinenachweise vorhanden** — siehe Tabelle oben.

### Belegte Kernbefunde (Produktionsverdrahtung geprüft)

Der Auftrag verlangt ausdrücklich die Prüfung, ob vorhandene Komponenten im
echten Produktionspfad aufgerufen werden. Ergebnis:

| # | Befund | Beleg |
| --- | --- | --- |
| B-1 | `parse_session_activation_query()` und `resolve_session_activation_config()` haben **null** Produktionsaufrufer | projektweite Suche: Treffer nur an den Definitionsstellen (server.py:950/992) und in Tests, die `ResolvedSessionActivationConfig` direkt konstruieren |
| B-2 | `admit_session()` (server.py:4262) besitzt keinen `activation_config`-Parameter; `/ws/transcribe` (server.py:7061) parst keine Triggerparameter | gelesener Quelltext |
| B-3 | Folge aus B-1/B-2: `self._activation` ist in Produktion **immer** `None`; jeder reale `trigger` erhält `controlled_activation_disabled` | Codepfad in `handle_trigger_command` |
| B-4 | `ActivationController.expire()` hat **null** Produktionsaufrufer; `_activation_timer_generation` wird gesetzt und nie gelesen | projektweite Suche |
| B-5 | `session_capabilities()` (server.py:4608) meldet kein `activationTriggers`; Client-Property `supports_activation_triggers` liefert daher immer `False` | gelesener Quelltext beider Seiten |
| B-6 | `activation.manual_accepted` / `.extended` / `.closed` werden nirgends erzeugt | projektweite Suche |
| B-7 | Client ersetzt `send_start()`/`send_stop()` durch Triggerkommandos (controller.py:610/904) — Verstoß gegen §3 und §26 | gelesener Diff |
| B-8 | Client migriert `mode=wake_word` nach `manual=true / wake_word=true`; §11.6 verbietet das | `SessionConfig.effective_manual_trigger_enabled` |
| B-9 | Der mitgelieferte Test `test_legacy_wake_word_mode_migrates_query_parameters` schreibt genau diesen Fehler als Sollverhalten fest | gelesener Testcode |
| B-10 | Im Client existiert **kein** `trigger_ack`-Handler | projektweite Suche in `core/` und `ui/` |
| B-11 | `_start_wakeword_followup_window()` (server.py:3611, gerufen aus 3575) setzt direkt `recorder.wakeword_detected = True` und startet einen eigenen Timerthread → zweite Recorder-Autorität und paralleler Follow-up-Timer im Controlled-Modus (§2.3, §7.1) | gelesener Quelltext |

### False-Positive-Nachweis in der übernommenen Testsuite

`tests/unit/test_server_controlled_e2e.py::test_04_controlled_session_timeout_expires_gate`
trägt den Kommentar „Wait for timeout to fire in background timer thread",
ruft danach jedoch selbst

```python
session._activation.expire(session._activation._version)
session.recorder.close_controlled_activation()
```

auf und prüft anschließend, dass das Gate geschlossen ist. Da kein
Hintergrundtimer existiert (B-4), beweist der Test ausschließlich, dass der Test
selbst geschlossen hat.

Ergänzend: **keine** der vier neuen Serverdateien benutzt einen echten
WebSocket-/`TestClient`-Einstieg, und **keine** durchläuft
`parse_session_activation_query` oder `resolve_session_activation_config`.

### OPEN FAILURES

- Client: 1 vorbestehender Fehlschlag (`test_ap06_followup.py`), Bewertung in AP7.
- LED: 6 vorbestehende, umgebungsbedingte Fehlschläge; Repository unverändert.

Beide sind als vorbestehend belegt und blockieren GATE 0 nicht.

### DECISION

GATE 0 **PASS**. Die Baseline ist verstanden, der Fremdstand ist abgegrenzt und
klassifiziert, die Verträge sind im Iststand erfasst, und die entscheidende
Frage — ob die Vorarbeit produktiv verdrahtet ist — ist mit einem klaren
**Nein** beantwortet und belegt.

---

## GATE 1 – Recorderautorität bewiesen

```text
GATE:   1 – Recorder Activation Gate
STATUS: PASS
```

### Implementierung

`VoiceSTT/core/activation_control.py` wurde um die in D-001 benannten Lücken
ergänzt:

- **Generationsbindung.** `open_controlled_activation_gate` und
  `close_controlled_activation_gate` nehmen eine `generation` entgegen. Eine
  ältere Generation kann eine neuere weder ersetzen noch schließen — auch nicht
  über den bisher ungeschützten Pfad `close(activation_id=None)`.
- **`abort_controlled_activation_gate`** schließt bedingungslos und hinterlässt
  einen deterministischen Zustand.
- **`shutdown_controlled_activation_gate`** schließt endgültig; spätere `open`
  werden abgelehnt (`_controlled_activation_shutdown`).
- `AudioToTextRecorder.abort()` und `.shutdown()` rufen diese Operationen jetzt
  **im Produktionscode** auf, nicht nur in Tests.
- `recording_activation_gate_is_open` bleibt im Controlled-Modus allein vom
  Gate abhängig; `recorder.wakeword_detected` wird dort nicht gelesen.

### EVIDENCE

**Testdatei neu geschrieben:** `tests/unit/test_recorder_activation_control.py`.

Der Auftrag verlangt in §14 ausdrücklich: „reine `SimpleNamespace`-Tests allein
reichen nicht als AP1-Abnahme." Die übernommene Fassung bestand ausschließlich
aus solchen Attrappen. Die neue Fassung baut eine **echte
`AudioToTextRecorder`-Instanz** (`object.__new__`, damit keine Worker-Prozesse
und Modelle geladen werden) und ruft die **echten Klassenmethoden** auf. Die
VAD-Entscheidung wird mit genau der Funktion getroffen, die
`run_recording_worker` aufruft.

| Pflichtfall §14 | Test | Ergebnis |
| --- | --- | --- |
| 1 Controlled + Gate zu + Sprache → keine Aufnahme | `test_01_controlled_closed_gate_blocks_recording_despite_speech` | PASS |
| 2 Controlled + Gate offen + Sprache → Aufnahme | `test_02_controlled_open_gate_allows_recording` | PASS |
| 3 Legacy unverändert | `test_03_legacy_policy_behaviour_is_unchanged` (4 Varianten inkl. Wakeword-Direktöffnung und Activation-Delay) | PASS |
| 4 Wake Word ohne offenes Gate → keine Aufnahme | `test_04_wake_word_cannot_bypass_a_closed_controlled_gate` | PASS |
| 5 Gate A offen | `test_05_gate_a_is_open` | PASS |
| 6 Activation B ersetzt A | `test_06_activation_b_replaces_a` | PASS |
| 7 spätes Close(A) → B bleibt offen | `test_07_late_close_of_a_must_not_close_b` (+ `test_07b` für stale open) | PASS |
| 8 Cancel → Gate zu | `test_08_cancel_closes_the_gate` | PASS |
| 9 Finish → Gate kontrolliert zu | `test_09_finish_closes_the_gate` | PASS |
| 10 Abort → deterministischer Zustand | `test_10_abort_forces_a_deterministic_closed_state` | PASS |
| 11 Shutdown bei offenem Gate | `test_11_shutdown_during_an_open_gate_closes_it_permanently` | PASS |
| 12 zweiter Trigger während Recording → keine zweite Aufnahme | `test_12_repeated_open_for_the_same_activation_is_a_no_op` + `test_12b_gate_is_only_consulted_while_not_recording` | PASS |
| 13 Gateöffnung gleichzeitig mit VAD | `test_13_gate_opening_concurrent_with_vad_reads` | PASS |
| 14 Gateclose gleichzeitig mit VAD | `test_14_gate_closing_concurrent_with_vad_reads` | PASS |
| 15 mehrfaches Close ohne Fehler/Fremdwirkung | `test_15_multiple_close_calls_are_idempotent` | PASS |

**Racefälle wiederholt.** §14 verlangt: „Ein einmalig grüner Race-Test ist kein
ausreichender Nachweis." Die Fälle 13/14 laufen je 25 interne Wiederholungen mit
3 Leserthreads und 200 Gate-Wechseln. Zusätzlich wurde die ganze Datei fünfmal
hintereinander ausgeführt (`evidence/ap1_race_repeats.txt`):

```text
run 1: 22 passed in 8.01s
run 2: 22 passed in 8.09s
run 3: 22 passed in 8.88s
run 4: 22 passed in 7.86s
run 5: 22 passed in 7.97s
```

**Regression.** Vollständige Serversuite nach der Änderung
(`evidence/ap1_server_regression.txt`):

```text
436 passed, 13 skipped, 78 subtests passed in 21.85s
```

Baseline war `426 passed, 13 skipped`. Die Differenz von +10 entspricht exakt
der neuen Testdatei (vorher 12 Tests, jetzt 22). Keine bestehende Serverprüfung
ist rot geworden.

**`git diff --check`:** sauber (nur die bekannten LF/CRLF-Hinweise, keine
Whitespace-Fehler).

**Kein Wakeword-Bypass:** in `recording_activation_gate_is_open` liegt der
`recorder.wakeword_detected`-Zweig hinter der Controlled-Abfrage und ist damit
im Controlled-Modus unerreichbar; `test_04` weist das mit gesetztem
`wakeword_detected = True` nach.

### OPEN FAILURES

Keine.

### DECISION

GATE 1 **PASS**.

Einschränkung, die bewusst offen bleibt und in AP4 geschlossen wird: das Gate
ist damit als Komponente bewiesen, aber noch **nicht** produktiv mit dem
`ActivationController` verbunden (siehe B-1 bis B-3). Der Nachweis der echten
Verdrahtung gehört zu GATE 4 und wird dort nicht durch GATE 1 vorweggenommen.

---

## GATE 2 – Zustandsmaschine deterministisch

```text
GATE:   2 – ActivationController
STATUS: PASS
```

### Implementierung

`api_fastapi_server/activation.py` wurde gemäß D-003 überarbeitet:

- **`generation` und `version` getrennt.** `generation` steigt nur beim Öffnen
  einer neuen Activation und bleibt über deren Leben stabil; sie gehört in
  Events und in die Gate-Bindung. `version` steigt bei jeder Zustandsänderung
  und bindet geplante Timeouts.
- **`finalizing` ergänzt.** Der Lebenszyklus aus §3 des Auftrags endet jetzt
  wie vorgeschrieben über eine Finalisierungsphase. Das Fenster ist dabei
  geschlossen (`windowOpen == false`, Gate zu), die `activationId` lebt aber
  weiter, damit die nachlaufende Finaltranskription korreliert werden kann.
  `cancel` verwirft den Turn und geht deshalb ohne `finalizing` nach `inactive`.
- **Interne Thread-Sicherheit.** Ein `RLock` schützt alle Operationen. Die
  bisherige Zusage „Callers provide their own synchronization" war nicht
  haltbar, weil der Controller aus der WebSocket-Coroutine, aus
  Recorder-Callbackthreads und ab AP4 aus dem Timeoutthread erreicht wird.
- **Aliasattrappen entfernt.** Die frei gesetzten Attribute `manual_enabled` /
  `wake_word_enabled` konnten von den führenden Feldern abweichen; sie sind
  jetzt Properties. Die stillen Konstruktor-Fallbacks und die Methodenaliase
  `on_recording_start` / `on_recording_end` wurden entfernt; der einzige
  Produktionsaufrufer in `server.py` wurde auf die kanonischen Namen umgestellt.
- **`finalized()`** ergänzt, `segments` gezählt, `already_recording` als
  eigenes deterministisches Ergebnis für ein doppeltes `recording_started`.

### EVIDENCE – Pflichtfälle §15

Die 20 Pflichtfälle waren bereits als legitime Unittests mit injizierter Uhr
vorhanden (D-012) und bleiben grün (`test_01` … `test_20`). Ergänzt wurden:

| Anforderung GATE 2 | Test | Ergebnis |
| --- | --- | --- |
| Generation stabil innerhalb einer Activation | `GenerationAndVersionTests::test_generation_is_stable_for_one_activation` | PASS |
| Version steigt bei jeder Änderung | `test_version_moves_on_every_state_change` | PASS |
| neue Activation erhöht Generation | `test_a_new_activation_raises_the_generation` | PASS |
| Merge erhöht Generation **nicht** | `test_a_merge_does_not_raise_the_generation` | PASS |
| Finalisierungsphase inkl. ID-Erhalt | `FinalizingPhaseTests` (6 Tests) | PASS |
| ungültige Transitionen explizit | `InvalidTransitionTests::test_operations_on_an_inactive_controller_are_refused` (5 Subtests) | PASS |
| `finalized` außerhalb `finalizing` | `test_finalized_outside_finalizing_is_refused` | PASS |
| ungültige Source überall abgelehnt | `test_unknown_source_is_refused_everywhere` (4 Subtests) | PASS |
| doppeltes `recording_started` zählt kein zweites Segment | `test_recording_started_twice_does_not_count_a_second_segment` | PASS |
| `expire` ohne Deadline / inaktiv | `test_expire_is_refused_when_no_deadline_is_armed`, `test_expire_on_an_inactive_controller_is_refused` | PASS |
| Generation-Race / keine doppelte Activation | `ConcurrentTriggerTests` | PASS, siehe Mutationsnachweis |

### EVIDENCE – Mutationsnachweis für die Race-Tests

Die zuerst geschriebene Fassung der Nebenläufigkeitstests war ein **False
Positive meiner eigenen Arbeit**: sie blieb auch dann grün, wenn man das Lock
entfernte. Der kritische Abschnitt von `activate()` ist so kurz, dass sich acht
über eine Barriere gestartete Threads praktisch nie darin verschränken.

Die Tests wurden deshalb so umgebaut, dass sie das Fenster gezielt aufreißen:
`id_factory` wird **innerhalb** des kritischen Abschnitts aufgerufen, also
injiziert der Test eine Factory, die dort 10 ms schläft. Ohne Lock passieren
dann alle Threads die Prüfung „ist schon ein Fenster offen?" und jeder öffnet
eine eigene Activation.

Nachweis der Wirksamkeit (`evidence/ap2_mutation_check.txt`):

```text
1) unverändert:                        39 passed, 9 subtests passed
2) MUTATION self._lock -> nullcontext: 2 failed, 37 passed
     FAILED …::test_near_simultaneous_triggers_yield_exactly_one_activation
     FAILED …::test_a_reader_never_observes_a_half_built_activation
3) wiederhergestellt:                  39 passed, 9 subtests passed
```

Damit ist belegt, dass diese Tests die Thread-Sicherheit tatsächlich prüfen und
nicht nur zufällig grün sind.

**Wiederholungen** (`evidence/ap2_race_repeats.txt`): fünf aufeinanderfolgende
Läufe, jeweils `39 passed, 9 subtests passed`; die Race-Fälle selbst wiederholen
intern je 12-mal.

### EVIDENCE – Regression

`evidence/ap2_server_regression.txt`:

```text
453 passed, 13 skipped, 87 subtests passed in 22.12s
```

Baseline 426, nach AP1 436, jetzt 453. Alle Zuwächse sind neue Tests; keine
bestehende Prüfung ist rot geworden.

### EVIDENCE – Zustandsdiagramm dokumentiert

`voice-stt-server/docs/einheitliche-triggerarchitektur.md`, Abschnitt 2, mit
Mermaid-Diagrammen für Stream- und Activation-Lifecycle sowie Abschnitt 3 für
die Activation-Daten und Abschnitt 4 für die Kollisionssemantik.

### OPEN FAILURES

Keine.

### DECISION

GATE 2 **PASS**. Wie bei GATE 1 gilt: die Zustandsmaschine ist als Komponente
bewiesen; ihre produktive Verdrahtung (Timeout-Scheduler, Gate, Events) ist
Gegenstand von GATE 4 und wird hier ausdrücklich **nicht** als erledigt
behauptet.

---

## GATE 3 – Netzwerkvertrag vollständig

```text
GATE:   3 – WebSocket-Triggervertrag
STATUS: PASS
```

### Implementierung

`handle_trigger_command` wurde gemäß D-005 überarbeitet:

- **Stream-Lifecycle geprüft.** Ein Trigger vor `start`, nach `stop` oder nach
  Close wird mit `stream_not_started` beziehungsweise `session_closed`
  abgelehnt — vorher wurde er unabhängig vom Streamzustand verarbeitet.
- **Ablehnungen sind korrelierbar.** Jede Antwort trägt `commandId`,
  `sessionId` und — wo eine Activation läuft — deren `activationId`.
- **Typprüfung.** `commandId`, `action` und `source` werden auf ihren Typ
  geprüft (`invalid_command_id`, `invalid_action`, `invalid_source`), statt
  über `str(...)` stillschweigend umgedeutet zu werden.
- Idempotenz unverändert beibehalten, Historie über die benannte Konstante
  `TRIGGER_COMMAND_HISTORY`.

Zusätzlich wurde die Query-Auswertung gehärtet: `manualTriggerEnabled=maybe`
ergibt jetzt `invalid_activation_flag` statt still `false` zu werden — sonst
könnte ein Tippfehler eine gültige Anforderung unbemerkt in die verbotene
`false/false`-Kombination kippen.

### EVIDENCE – Pflichtnegativtests §16

`tests/unit/test_server_trigger_contract.py` wurde vollständig neu geschrieben.
Die frühere Fassung setzte `session._activation` direkt und testete damit an der
Session vorbei; die neue Fassung fährt jeden Fall über einen echten WebSocket.

| Pflichtfall §16 | Test | Ergebnis |
| --- | --- | --- |
| fehlendes `commandId` | `test_a_missing_command_id_is_rejected` | PASS |
| falscher Datentyp (`commandId`) | `test_a_wrongly_typed_command_id_is_rejected` | PASS |
| falscher Datentyp (`action`) | `test_a_wrongly_typed_action_is_rejected` | PASS |
| unbekannte Action | `test_an_unknown_action_is_rejected` | PASS |
| ungültige Source | `test_an_invalid_source_is_rejected` | PASS |
| deaktivierte Source | `test_a_disabled_source_is_rejected_with_its_own_reason` | PASS |
| Trigger vor Streamstart | `test_a_trigger_before_stream_start_is_rejected` | PASS |
| Trigger nach Streamstop | `test_a_trigger_after_stream_stop_is_rejected` | PASS |
| Trigger in unzulässigem Zustand | `test_all_four_actions_are_answered` (`cancel` ohne Activation → `not_active`) | PASS |
| doppelte `commandId` | `test_the_same_command_id_never_takes_effect_twice` | PASS |
| gleiche `commandId`, anderer Payload | `test_the_same_command_id_with_another_payload_is_rejected` | PASS |
| malformed JSON | `test_malformed_json_is_answered_with_a_command_error` | PASS |
| Nicht-Objekt-Payload | `test_a_trigger_that_is_not_an_object_is_rejected` | PASS |
| Legacyclient sendet nie Trigger und funktioniert weiter | `test_a_legacy_client_never_sends_a_trigger_and_keeps_working` | PASS |
| unbekannter Befehl | `test_an_unknown_command_still_reports_an_error` | PASS |

### EVIDENCE – Idempotenz

`test_the_same_command_id_never_takes_effect_twice` vergleicht die beiden Acks
auf **Gleichheit** und prüft zusätzlich, dass das Recorder-Gate weiterhin
dieselbe `activationId` hält — also kein zweiter Timer, kein zweites Event und
keine zweite Activation entstanden ist.

### EVIDENCE – Capability entspricht dem Funktionsstand

`activationTriggers.supported = true` wurde **erst nach** der vollständigen
Verdrahtung eingeführt (D-007). Zum Zeitpunkt der Veröffentlichung gilt
nachweislich: `trigger` wird verarbeitet (GATE 3), `trigger_ack` existiert und
ist deterministisch (GATE 3), `commandId` ist idempotent (GATE 3), und die
Activation ist mit dem Recorder verbunden (GATE 4). Damit ist §7.4 eingehalten.

`hello`/`ready` wurden um `activationConfig` **ergänzt**, keine bestehenden
Felder verändert; die bestehenden `start`/`stop`- und Protokolltests bleiben
grün (siehe Regression unter GATE 4).

### DECISION

GATE 3 **PASS**.

---

## GATE 4 – Server-E2E

```text
GATE:   4 – Serverintegration Trigger → Gate → Recording
STATUS: PASS
```

### Implementierung

Der Kernbefund aus AP0 (B-1 bis B-3: der Controlled-Modus war produktiv
unerreichbar) ist behoben:

1. `parse_session_activation_query` wird im WebSocket-Einstieg aufgerufen,
   `resolve_session_activation_config` in `admit_session` angewendet und
   `activation_config` bis in die Session durchgereicht.
2. Generationsgebundener Activation-Timer je Session ruft `expire()` auf,
   schließt das Gate und publiziert `activation_closed`.
3. Rückwärtspfad `recording_started` / `recording_ended` meldet an den
   Controller und schaltet den Timer um.
4. Wake Word läuft über denselben Controller und dasselbe Gate.
5. Der Legacy-Wakeword-Follow-up ist im Controlled-Modus abgeschaltet (D-008).
6. `stop_streaming`, `close` und `clear` setzen die Activation zurück.
7. Alle Timeline-Events tragen `activationId`, `primarySource`, `sources`.

### EVIDENCE – echte E2E-Tests

`tests/unit/test_server_controlled_e2e.py` wurde vollständig ersetzt. Die neue
Fassung fährt über `create_app` und `client.websocket_connect("/ws/transcribe?…")`
und durchläuft damit Query-Parsing, Session-Admission, `handle_trigger_command`,
`ActivationController`, das **echte** Gate-Modul und die Recorder-Callbacks.

Der Recorder ist eine Attrappe — ein echter bräuchte Mikrofon und Modelle —
aber eine, die die **Produktionsfunktionen** aus
`VoiceSTT.core.activation_control` benutzt und vor jedem Segmentstart genau die
Bedingung auswertet, die `run_recording_worker` auswertet. Ihre Legacy-Flags
sind bewusst scharf gestellt (`start_recording_on_voice_activity = True`),
sodass ein fehlendes Gate sofort sichtbar würde.

| Pflicht-E2E §17 | Test | Ergebnis |
| --- | --- | --- |
| Queryparameter erreichen die Session, Capability korrekt | `test_query_parameters_reach_the_session_and_announce_the_capability` | PASS |
| Session ohne Triggerparameter bleibt legacy | `test_a_session_without_trigger_parameters_stays_legacy` | PASS |
| `false/false` abgelehnt | `test_both_triggers_disabled_is_rejected_at_admission` | PASS |
| unparsbares Flag abgelehnt | `test_an_unparsable_trigger_flag_is_rejected_instead_of_silently_false` | PASS |
| **Sprache ohne Trigger erzeugt keine Aufnahme** | `test_speech_without_a_trigger_never_starts_a_recording` | PASS |
| Manual → Gate → Aufnahme, mit Korrelationsfeldern | `test_manual_trigger_opens_the_gate_and_speech_then_records` | PASS |
| Wake Word nur über den Controller | `test_wake_word_reaches_the_recorder_only_through_the_controller` | PASS |
| deaktiviertes Wake Word öffnet nichts | `test_wake_word_is_ignored_when_the_wake_word_trigger_is_disabled` | PASS |
| **Manual → Wake Word: eine Activation, ein Segment** | `test_manual_then_wake_word_stays_one_activation` | PASS |
| **Wake Word → Manual: eine Activation, ein Segment** | `test_wake_word_then_manual_stays_one_activation` | PASS |
| wiederholte Manualtrigger: eine Activation | `test_repeated_manual_triggers_stay_one_activation` | PASS |
| **Timeout schließt das Gate von selbst** | `test_the_server_closes_the_gate_on_its_own_after_the_timeout` | PASS |
| alter Timer beendet verlängerte Activation nicht | `test_a_timeout_does_not_end_an_activation_that_was_extended` | PASS |
| Finish | `test_finish_closes_the_gate` | PASS |
| Cancel | `test_cancel_closes_the_gate` | PASS |
| Streamstop während Activation | `test_stopping_the_stream_ends_the_activation` | PASS |
| Reconnect belebt keine alte Activation | `test_a_reconnect_does_not_revive_the_previous_activation` | PASS |
| nur eine Follow-up-Autorität | `test_controlled_mode_never_starts_the_legacy_followup_window` | PASS |
| Legacy behält seinen Follow-up | `test_legacy_mode_still_starts_the_legacy_followup_window` | PASS |

Für die Kollisionsfälle prüft `_collision()` ausdrücklich:
`len(activation_ids) == 1`, `recorder.recording_starts == 1`,
`len(recording_started-Events) == 1`, stabile `primarySource` und beide Quellen
in `sources`.

### EVIDENCE – Mutationsnachweis (entscheidend)

Eine grüne Suite beweist nichts, solange nicht gezeigt ist, dass sie die
Verdrahtung wirklich prüft. `evidence/ap4_mutation_check.txt`:

| Mutation | Ergebnis |
| --- | --- |
| M0 unverändert | 17 passed |
| **M1 `activation_request=` aus `admit_session` entfernt** — exakt der übernommene Zustand des Vorgängers | **15 failed, 2 passed** |
| M2 Activation-Timer entfernt | 1 failed (der Timeouttest) |
| M3 Gate-Öffnung entfernt | 8 failed |
| M4 Legacy-Wakeword-Follow-up im Controlled-Modus reaktiviert | zunächst **17 passed → Lücke in meinen eigenen Tests** |
| M4b nach Ergänzung von `SingleFollowUpAuthorityTests` | **1 failed** |
| M6 wiederhergestellt | 37 passed |

M4 ist hier ausdrücklich mitprotokolliert, obwohl es eine Schwäche meiner
eigenen Arbeit war: der erste Testsatz hätte die Rückkehr der zweiten
Follow-up-Autorität nicht bemerkt, weil die Legacy-Funktion in dieser Umgebung
(kein Wake-Word-Profil) ohnehin früh aussteigt. Der ergänzte Test prüft deshalb
die **Aufrufstelle** und nicht die umgebungsabhängige Wirkung.

### EVIDENCE – dabei gefundener Produktionsdefekt

Der Activation-Timeout war ein Einmal-Timer. `threading.Event.wait()` kehrt
unter Windows regelmäßig geringfügig zu früh zurück (Granularität ≈ 15 ms);
`expire()` antwortete dann `not_due`, und der Timer verwarf den Timeout
**endgültig**. Folge im Produktivbetrieb: die Activation läuft nie ab und das
Recorder-Gate bleibt für den Rest der Sitzung offen.

Sichtbar wurde das als sporadisch roter E2E-Test (2 von 5 Kaltläufen, jeweils
mit 22 s Laufzeit durch das Auslaufen des Wartebudgets). Behoben durch eine
Warteschleife, die die Restzeit bis zur tatsächlichen Deadline neu ausschöpft.

Stabilitätsnachweis nach der Korrektur (`evidence/ap4_timeout_stability.txt`),
jeweils mit vorher gelöschtem `__pycache__`:

```text
cold run 1..8: 17 passed in ~2,7s
```

### EVIDENCE – Regression

`evidence/ap4_server_regression.txt`:

```text
476 passed, 13 skipped, 87 subtests passed in 26.41s
```

Baseline 426 → AP1 436 → AP2 453 → AP4 476. Kein bestehender Test ist rot.
`git diff --check` sauber.

### OPEN FAILURES

Keine.

### EVIDENCE – vollständige Kollisionsmatrix (Nachtrag R1)

Die erste Fassung wies die Kollisionen nach, zählte aber nicht alle vier
Invarianten getrennt. `CollisionMatrixEndToEndTests` holt das nach: für jeden
der drei Fälle wird einzeln gemessen und protokolliert.

`Scheduler allocations` waren zuvor gar nicht instrumentiert. Ergänzt wurde
dafür ein `CountingScheduler`, der die tatsächlich an den Scheduler übergebenen
Jobs je Session und Art zählt — nicht-invasiv, denn `ManualScheduler` führt
`self.jobs` ohnehin; die Unterklasse macht die Instanzen nur erreichbar.

Gemessene Werte (Ausgabe der Tests):

```text
manual -> wake_word : activationId=[6dd9073cf6a44bdd92c0b00833f2e422]  primarySource=manual
                      sources=[manual, wake_word]  segmentId=[1]
                      recordingStarts=1  finals=1  schedulerAllocations=1

wake_word -> manual : activationId=[9ffe0147ab24424a8273e0abe4a24c89]  primarySource=wake_word
                      sources=[wake_word, manual]  segmentId=[1]
                      recordingStarts=1  finals=1  schedulerAllocations=1

nahezu simultan     : activationId=[e7ae6317a1314d89a7951e9df47a9a06]  primarySource=wake_word
                      sources=[wake_word, manual]  segmentId=[1]
                      recordingStarts=1  finals=1  schedulerAllocations=1
```

Damit gilt für jeden Fall einzeln:
`Activations = 1`, `Segments = 1`, `Finals = 1`, `Scheduler allocations = 1`.

**Der dritte Fall ist ein echter E2E-Fall**, kein Controller-Unittest: der
Manualtrigger läuft über die WebSocket-Empfangsschleife des Servers, das Wake
Word über den Recorder-Callback, beide freigegeben durch eine gemeinsame
Barriere. Zusätzlich wird `uuid4` im Activation-Modul verlangsamt, damit der
kritische Abschnitt breit genug für eine echte Verschränkung ist.

**Mutationsnachweis** (`evidence/r1_collision_mutation.txt`):

| Mutation | Ergebnis |
| --- | --- |
| M0 unverändert | 3 passed |
| M1 Merge entfernt (jeder Trigger öffnet eine neue Activation) | **3 failed** |
| M2 nur Controller-Lock entfernt | 3 passed |
| M4 nur Session-Lock im Wakeword-Pfad entfernt | 1 passed |
| **M5 Session-Lock und Controller-Lock entfernt** | **1 failed: „Activations must be 1, got [2 IDs]"** |
| M6 wiederhergestellt | 3 passed |

M2 und M4 sind bewusst mitprotokolliert: sie zeigen, dass der Server die
Serialisierung **doppelt** absichert — das Session-Lock und das
Controller-Lock schützen unabhängig voneinander. Erst wenn beide fehlen,
entstehen zwei Activations, und genau das erkennt der simultane E2E-Fall.

**Wiederholungen** (`evidence/r1_collision_repeats.txt`): fünf aufeinander
folgende Läufe, jeweils `3 passed`.

### DECISION

GATE 4 **PASS**.

Ausdrückliche Einschränkung: „E2E" bedeutet hier **serverseitig vollständig**
— vom WebSocket-Einstieg bis zum Recorder-Gate und zurück. Es ist **kein**
Nachweis mit echtem Audio, echter Hardware oder echtem Clientbuild; das bleibt
AP10 und wird dort als `MANUAL VALIDATION REQUIRED` ausgewiesen.

---

## GATE 5 – Server bereit für alten und neuen Client

```text
GATE:   5 – Serverdokumentation und kompatibler Rollout
STATUS: MANUAL VALIDATION REQUIRED
```

**Begründung der Einstufung.** Das Gate verlangt ausdrücklich „Browserclient
funktioniert". Der Browserclient wurde im Rahmen dieser Aktion repariert und
sein Drahtverhalten automatisiert gegen den echten Server nachgewiesen — aber
ein tatsächlicher Lauf im Browser braucht einen Browser und eine
Mikrofonfreigabe, also echte Benutzerinteraktion. Nach der geltenden
Gate-Semantik ist das kein PASS.

### Reparierter Browserclient

Der mitgelieferte `app_browserclient/client.js` sprach ein Protokoll, das es
nicht mehr gibt:

| Befund | vorher | jetzt |
| --- | --- | --- |
| WebSocket-Ziel | `ws://localhost:9001` (Wurzelpfad, keine Route) | `.../ws/transcribe` |
| Streamstart | nie gesendet, der Server verwirft daher jedes Audiopaket | sendet `start` nach `ready` |
| Ergebnisnachricht | erwartete `fullSentence` | verarbeitet `realtime` und `final` |
| Audiometadaten | nur `sampleRate` | `sampleRate`, `channels`, `format`, `frames` |
| `index.html` | lud zusätzlich socket.io, das der Server nicht spricht; `div` nicht geschlossen | bereinigt |

Der Client bleibt bewusst ein **Legacyclient**: er sendet keine
Trigger-Queryparameter, bleibt damit im Legacy-Activationmodus und ist so
zugleich die Kompatibilitätsreferenz für „ein alter Client funktioniert weiter".

### EVIDENCE

**1. Statischer Vertragstest** – `tests/unit/test_browser_client_contract.py`,
`BrowserClientSourceContractTests`: prüft Pfad, Startbefehl, Nachrichtentypen
und Audiometadaten der ausgelieferten Datei.

**2. Nachgespieltes Drahtverhalten** – `BrowserClientReplayTests` führt exakt
die Sequenz des Browserclients gegen die echte App aus (gleiche URL, gleicher
`start`, gleiche Paketrahmung) und weist nach, dass der Server sie ohne Fehler
und ohne Warnung akzeptiert, dass die Sitzung `legacy` bleibt, dass Audio vor
`start` korrekt abgelehnt wird und dass ein defektes Paket als
`where: audio_packet` gemeldet wird.

**3. Mutationsnachweis** (`evidence/r3_browser_mutation.txt`): gegen die
**ursprüngliche** Fassung aus `HEAD` schlagen 12 Prüfungen fehl, gegen die
korrigierte bestehen alle:

```text
M0 korrigierter Browserclient : 10 passed, 7 subtests passed
M1 urspruenglicher Client     : 12 failed, 5 passed
M2 wiederhergestellt          : 10 passed, 7 subtests passed
```

**4. Produktionsnaher Smoke-Test** (`evidence/r3_production_smoke.txt`): ein
**echter uvicorn-Prozess** mit der echten App, angesprochen über ein **echtes
TCP-WebSocket** mit der `websockets`-Bibliothek, nicht über den
In-Process-TestClient:

```text
starting real uvicorn server on 127.0.0.1:51384
OK  false/false rejected: code=activation_trigger_required close=1008
OK  unparsable flag rejected: code=invalid_activation_flag close=1008
OK  invalid timing rejected: code=invalid_activation_timing close=1008
OK  wake-word-only without profile rejected: code=activation_wake_word_unavailable close=1008
4 admission checks passed against a real server process
```

Der Smoke-Test deckt bewusst nur den **Admission-Pfad** ab: eine vollständige
Sitzung baut einen echten Recorder, der Transkriptionsmodelle und ein Mikrofon
braucht; beides steht dieser Umgebung nicht zur Verfügung. Diese Grenze wird
benannt, nicht verdeckt.

**5. Legacy-Desktopclient gegen neuen Server** –
`evidence/ap5_legacy_protocol.txt`: `81 passed, 1 skipped, 17 subtests passed`
über `test_fastapi_server_protocol.py`, `test_fastapi_server_multi_user.py`
und `test_fastapi_server_multi_user_asr_integration.py`.

**6. `start`/`stop`, Capability, `trigger`, `trigger_ack`, Eventstream, Replay,
Serverregression** – siehe GATE 3, GATE 4 und GATE 9.

### OFFEN – MANUAL VALIDATION REQUIRED

**M-B1 – Browserclient im echten Browser.** Server starten:

```bash
python -m VoiceSTT_server.server --port 9001
```

Danach `app_browserclient/index.html` im Browser öffnen (bei Bedarf über einen
lokalen Webserver, damit `getUserMedia` erlaubt ist), Mikrofon freigeben und
prüfen: Verbindung steht, `start` geht raus, gesprochener Text erscheint als
Realtime- und danach als Finaltext.

### DECISION

GATE 5 **MANUAL VALIDATION REQUIRED**. Alle automatisierbaren Kriterien sind
erfüllt und belegt; der Browserlauf selbst steht aus.

---

## GATE 6 – Konfigurationsmigration

```text
GATE:   6 – Clientkonfiguration und Migration
STATUS: PASS
```

### Korrigierter Fehler

Der übernommene Stand migrierte `mode = wake_word` nach
`manual = true / wake_word = true` — genau die von §11.6 und §19 verbotene
implizite Migration. Ursache war
`SessionConfig.effective_manual_trigger_enabled`, das bei fehlendem Flag
unbedingt `True` lieferte und den Altmodus ignorierte.

Korrigiert: ein explizites Flag gewinnt weiterhin; fehlt es, entscheidet der
Altmodus **nach der vorgeschriebenen Regel**:

```text
mode = hotkey     ->  manual = true,  wake_word = false
mode = wake_word  ->  manual = false, wake_word = true
```

Ergänzt wurden `effective_wake_word_trigger_enabled` als benanntes Gegenstück,
`migrated_from_legacy_mode` als Auskunft darüber, ob eine Sitzung noch am alten
Feld hängt, sowie eine Typprüfung der beiden Flags. `wake_word_enabled` bleibt
als Alias für die vorhandenen Konsumenten erhalten.

### Korrigierter Test

`tests/test_config.py::TestAP6ConfigMigration::test_legacy_wake_word_mode_migrates_query_parameters`
behauptete `manualTriggerEnabled == "true"` für `mode = wake_word` und
schrieb damit den Fehler als Sollverhalten fest. Der Test wurde auf die
normative Regel korrigiert und heißt jetzt
`test_legacy_wake_word_mode_migrates_to_wake_word_only`.

### EVIDENCE – Pflichtfälle §19

| Pflichtfall | Test | Ergebnis |
| --- | --- | --- |
| alte Hotkeyconfig | `test_legacy_hotkey_mode_migrates_to_manual_only` | PASS |
| alte Wakewordconfig | `test_legacy_wake_word_mode_migrates_to_wake_word_only` | PASS |
| **keine implizite `true/true`-Migration** | `test_no_legacy_mode_ever_migrates_to_both_triggers` (über alle Modi) | PASS |
| fehlendes Feld | `test_a_missing_mode_field_keeps_the_hotkey_default` | PASS |
| ungültiger alter Wert | `test_an_invalid_legacy_mode_value_is_rejected` | PASS |
| neue Config | `test_explicit_flags_override_the_legacy_mode` | PASS |
| beide true | `test_explicit_flags_override_the_legacy_mode` | PASS |
| beide false → Fehler | `test_disabling_all_triggers_raises_validation_error` und `test_disabling_all_triggers_is_rejected_for_every_legacy_mode` | PASS |
| ein Flag explizit, das andere aus dem Modus | `test_a_single_explicit_flag_still_reads_the_other_from_the_mode` | PASS |
| falscher Datentyp | `test_a_non_boolean_trigger_flag_is_rejected` | PASS |
| Queryvertrag | `test_wake_word_details_are_only_sent_when_the_wake_word_is_on`, `test_activation_timings_reach_the_query_when_configured` | PASS |

Persistiertes Userfile und Source-Run sind über die bestehenden
Config-Ladetests der Datei abgedeckt (`35 passed, 68 subtests passed`).
Die PyInstaller-/Frozen-Pfadauflösung gehört zu AP10.

### EVIDENCE – UI und Backend wenden dieselbe Regel an

`ui/settings_dialog.py` liest die Checkboxen über
`effective_manual_trigger_enabled` beziehungsweise `wake_word_enabled` — also
über dieselben Properties, die auch `query_parameters()` und `validate()`
benutzen. Es gibt keine zweite Regelimplementierung.

### EVIDENCE – Regression

`evidence/ap6_client_regression.txt`:

```text
464 passed, 192 subtests passed in 33.33s
```

### Klarstellung zum Baseline-Fehlschlag

Die Baseline wies einen roten Test aus:
`tests/test_ap06_followup.py::TestDictationWindow::test_wake_word_followup_uses_server_duration_and_clears_on_speech`.

Dieser Test ist jetzt grün. **Das ist kein Verdienst meiner Änderung.** Der
Test misst mit `asyncio.sleep(WINDOW * 0.8)` gegen ein Zeitfenster und ist
damit lastabhängig; der Baseline-Lauf fand statt, während parallel die Server-
und die LED-Suite liefen. Isoliert nachgemessen
(`evidence/ap6_followup_flake_check.txt`): **6 von 6 Läufen grün**, jeweils
1,3 s.

Bewertung: vorbestehender lastempfindlicher Timing-Test, kein Sachfehler und
keine von mir vorgenommene Reparatur. Er wird in AP7 erneut betrachtet, weil er
zum clientseitigen Follow-up-Mechanismus gehört, den AP7 auf serverseitige
Autorität umstellt.

### OPEN FAILURES

Keine.

### DECISION

GATE 6 **PASS**.

---

## GATE 7 – Client-Lifecycle

```text
GATE:   7 – Client-Lifecycle
STATUS: PASS
```

### Korrigierter Fehler (D-009)

Der übernommene Stand **ersetzte** `session.send_start()` durch
`send_trigger(activate)` und `session.send_stop()` durch
`send_trigger(finish)`. Das verletzt §3 („`start` und `stop` bleiben
ausschließlich Streambefehle") und §26; fachlich wäre der Audiostream nie
gestartet worden.

Korrigiert: `_begin_stream_and_trigger()` sendet **zuerst** `start` und
**danach** — nur wenn der Server die Capability meldet — den Manualtrigger.
Gegen einen Server ohne Capability bleibt es beim reinen `start`, also exakt
beim Altverhalten.

### Ergänzt (D-011): `trigger_ack` wird konsumiert

- `send_trigger()` registriert das Kommando als **pending**, gebunden an die
  Verbindungsgeneration.
- `request_trigger()` sendet und wartet auf das Ack; ohne Antwort liefert es
  eine Ablehnung mit `ack_timeout` statt zu blockieren.
- `_resolve_trigger_ack()` liefert ein Ack **nur beim ersten Mal**. Ein
  wiederholtes Ack, ein Ack für ein unbekanntes Kommando und ein Ack aus einer
  älteren Generation werden verworfen, bevor irgendein Consumer sie sieht.
- `_discard_pending_triggers()` löst offene Kommandos beim Verbindungswechsel
  als abgelehnt auf.
- Eine Ablehnung führt zu `CommandResult(status="trigger_rejected")` **ohne**
  Verbindungsrecycling — eine Ablehnung ist eine Antwort, kein Transportfehler.
  Damit gibt es kein fachliches Accepted-Feedback vor dem Ack.

### Abgebaute clientseitige Autoritäten

| Stelle | vorher | jetzt |
| --- | --- | --- |
| `_handle_timeline_event` | verzweigte über `config.session.mode` | verzweigt über die Triggerflags; bei serverautoritativer Activation kein lokales Fenster mehr |
| Diktatfenster nach Startbestätigung | `if mode == "hotkey"` | `_client_owns_dictation_window` – nur gegen Server **ohne** Activation-Contract |
| `primary_dictation_action` | `mode == "wake_word"` / `"hotkey"` | Manualflag entscheidet |
| `extend_dictation_window` | `mode != "hotkey"` → `wrong_mode` | `manual_trigger_disabled` |
| `_maintain_wake_word_mode` | `mode != "wake_word"` | Wake-Word-Flag |
| Konfigurationswiederherstellung | `mode == "wake_word"` | Wake-Word-Flag |
| `_wake_mode_desired` Initialisierung | `mode == "wake_word"` | Wake-Word-Flag |
| Hotkeyregistrierung | immer, wenn `hotkey.enabled` | zusätzlich nur, wenn der Manualtrigger aktiv ist |

Der verbliebene lokale Countdown ist reine **Darstellung** einer
serverseitigen Autorität: seine Dauer stammt aus dem Serverevent
(`durationSeconds`). Das erlaubt §20 ausdrücklich.

### EVIDENCE – Pflichttests §20

| Pflichttest | Test | Ergebnis |
| --- | --- | --- |
| Manual-only | `HotkeyRegistrationFollowsTheManualTrigger::test_manual_only_registers_hotkeys` | PASS |
| Wakeword-only | `test_wake_word_only_does_not_register_hotkeys` | PASS |
| beide | `test_both_triggers_register_hotkeys` | PASS |
| Hotkeyregistrierung nur bei aktivem Manual | dieselbe Klasse, 4 Tests | PASS |
| **Wakeword-only scheitert nicht an Hotkeykonflikt** | `test_wake_word_only_does_not_register_hotkeys` (Manager wird gar nicht erst aktiviert) | PASS |
| Trigger vor Ready | `TriggerBeforeReadyAndAfterDisconnect::test_a_trigger_before_the_socket_is_open_is_refused_locally` | PASS |
| Trigger nach Disconnect | `test_a_trigger_after_disconnect_is_refused_locally` | PASS |
| Pending Command während Disconnect | `test_a_disconnect_resolves_pending_commands_as_rejected` | PASS |
| **doppelte Ack** | `test_a_duplicate_ack_is_dropped_and_reaches_no_consumer` | PASS |
| Ack nach Reconnect | `test_a_pending_command_does_not_survive_a_reconnect` | PASS |
| **alte Ack aus alter Generation** | `test_an_ack_from_an_older_generation_is_dropped` | PASS |
| Server ohne Triggercapability | `CapabilityFallback` (3 Tests) und `test_without_the_capability_only_start_is_sent` | PASS |
| Reconnect setzt keine alte Activation fort | `test_a_pending_command_does_not_survive_a_reconnect` | PASS |
| `start`/`stop` bleiben Streambefehle | `StreamCommandsStayStreamCommands` (3 Tests) und `ControllerKeepsTheStreamCommand::test_start_dictation_sends_start_and_the_trigger` | PASS |
| kein Accepted-Feedback vor Ack | `test_a_rejected_trigger_does_not_confirm_the_dictation` | PASS |

### EVIDENCE – Mutationsnachweis

`evidence/ap7_mutation_check.txt`:

| Mutation | Ergebnis |
| --- | --- |
| M0 unverändert | 48 passed |
| **M1 `send_start` wieder durch den Trigger ersetzt** (Zustand des Vorgängers) | 1 failed |
| M2 Ack-Deduplizierung entfernt | 3 failed |
| M3 Generationsprüfung des Acks entfernt | 1 failed |
| M4 wiederhergestellt | 48 passed |

### EVIDENCE – Regression

`evidence/ap7_client_regression.txt` und `evidence/ap7_client_repeats.txt`:

```text
run 1..5: 492 passed, 195 subtests passed in ~32s
```

Baseline 455 Tests → jetzt 492. `git diff --check` sauber.

### Behandlung des lastempfindlichen Tests

`tests/test_ap06_followup.py::TestDictationWindow::test_wake_word_followup_uses_server_duration_and_clears_on_speech`
war schon in der Baseline rot und fiel unter Last erneut aus. Der Test wartete
mit `asyncio.sleep(WINDOW * 0.8)` gegen ein 0,25-Sekunden-Fenster.

Geändert wurde **nur die Wartestrategie**, nicht die Aussage: statt einer festen
Schlafdauer wird jetzt bis zum Eintreffen der Entscheidung gepollt (Obergrenze
`WINDOW * 8`). Die Assertion ist unverändert. Das ist keine Abschwächung im
Sinne von §26, sondern die Beseitigung einer Zeitabhängigkeit; ein
Implementierungsfehler lässt den Test weiterhin scheitern (die Obergrenze
läuft dann ab).

Nachweis: fünf vollständige Suitenläufe hintereinander grün.

### EVIDENCE – Continuous Streaming (Nachtrag R2)

Die zentrale Zielinvariante war zuvor nicht ausdrücklich bewiesen:

> Eine Session besitzt einen kontinuierlichen Audiostream, während mehrere
> Activations unabhängig davon stattfinden.

`ContinuousStreamingInvariant` in `tests/test_trigger_lifecycle.py` beweist sie
über den realen Produktionspfad (`start_dictation`, `stop_dictation`,
`cancel_dictation`, `extend_dictation_window`, `handle_server_event`), nicht
durch Setzen interner Flags. Die Testsession zählt Streambefehle getrennt von
der Sessionbeendigung und modelliert `streaming_requested` wie die echte
`STTSession`.

| Anforderung | Test | Ergebnis |
| --- | --- | --- |
| Stream startet genau einmal, zwei Activations laufen darauf | `test_two_activations_share_one_continuous_stream` | PASS |
| Finish beendet die Activation, nicht den Stream | dito (`stream_stops == 0`) | PASS |
| Cancel beendet die Activation, nicht die Session | `test_cancel_ends_the_activation_and_not_the_session` | PASS |
| Extend erzeugt keinen zweiten Stream | `test_extending_the_window_creates_no_second_stream` | PASS |
| Follow-up-Runden erzeugen keinen zweiten Stream | `test_a_follow_up_round_creates_no_second_stream` | PASS |
| Wake-Word-Aktivierung erzeugt keinen neuen Stream | `test_a_server_driven_activation_does_not_restart_the_stream` | PASS |
| Stream stoppt erst beim Sessionende | `test_the_stream_only_stops_when_the_session_ends` | PASS |
| Legacyverhalten bleibt erhalten | `test_a_legacy_server_keeps_the_old_start_stop_pairing` | PASS |

### Dabei gefundener zweiter Produktionsdefekt

Der Test deckte auf, dass **ab der zweiten Activation** der Startversuch in den
`start_confirmation_timeout` lief. Ursache: die Bestätigung hing an einem
Serverstatuswechsel, der nur den `start`-Befehl begleitet. Da ab der zweiten
Activation kein `start` mehr gesendet wird, kam nie eine Bestätigung.

Korrigiert: bei serverautoritativer Activation gilt das akzeptierte
`trigger_ack` selbst als Bestätigung. Das ist korrekt, weil der Server einen
Trigger nur annimmt, während der Stream läuft — ein akzeptiertes Ack beweist
also den laufenden Stream.

Sichtbar wurde der Defekt auch an der Laufzeit: die betroffenen Tests brauchten
31,5 s (zwei Timeouts à 10 s) und laufen nach der Korrektur in 1,0 s.

**Mutationsnachweis** (`evidence/r2_streaming_mutation.txt`):

```text
M0 unveraendert                    : 7 passed
M1 Ack-Bestaetigung entfernt       : 2 failed  (2. Activation laeuft in den Timeout)
M2 wiederhergestellt               : 7 passed
```

### OPEN FAILURES

Keine.

### DECISION

GATE 7 **PASS**.

---

## GATE 8 – Cross-Project Feedbackvertrag

```text
GATE:   8 – Events, Feedback und LEFX
STATUS: PASS
```

### Selbst gefundene Regression meiner eigenen AP7-Änderung

Durch das Gating auf `_client_owns_dictation_window` wäre gegen einen
triggerfähigen Server **kein Manual-Accepted-Feedback mehr** entstanden — der
Impuls hing im alten Code am Zweig, der das lokale Diktatfenster armt.

Korrigiert: `CLIENT_HOTKEY_ACCEPTED` wird jetzt in **beiden** Fällen genau
einmal publiziert, und zwar erst nachdem der Startversuch bestätigt ist. Gegen
einen triggerfähigen Server ist dieser Punkt per Konstruktion „nach dem Ack",
weil `_begin_stream_and_trigger()` bei einer Ablehnung eine Ausnahme wirft und
der Versuch dann gar nicht bestätigt wird.

Als Korrelations-ID dient dabei die `commandId`
(`_manual_accept_correlation()`), sodass ein wiederholtes Ack im Reducer auf
dieselbe Entscheidung fällt und keinen zweiten Impuls erzeugen kann.

### EVIDENCE – Pflichtnachweise §21

| Anforderung | Test | Ergebnis |
| --- | --- | --- |
| **Manual-Accepted genau einmal** | `ManualAcceptedComesFromTheAck::test_an_accepted_trigger_produces_exactly_one_manual_impulse` | PASS |
| **kein Accepted-Feedback ohne Ack** | `test_a_rejected_trigger_produces_no_manual_impulse` | PASS |
| Legacyserver unverändert | `test_a_legacy_server_still_produces_the_manual_impulse` | PASS |
| **doppeltes Ack erzeugt keinen Doppelimpuls** | `RepeatedAndReplayedEventsProduceNoSecondImpulse::test_the_same_correlation_id_is_only_published_once` | PASS |
| unterschiedliche `commandId` ist ein neuer Impuls | `test_a_different_command_id_is_a_new_impulse` | PASS |
| **Replay erzeugt keinen Impuls** | bestehende Reducer-Logik (`origin is EventOrigin.REPLAY` → `publish=False`), abgedeckt durch `tests/test_feedback_reducer.py` und `tests/test_feedback_integration.py` | PASS |
| Wakeword während Manualactivation ohne zweite Recordingsequenz | `WakeWordDuringManualActivation::test_one_activation_yields_one_recording_sequence` | PASS |
| Recording/Thinking/Success unverändert | `FeedbackMappingCoversTheContract::test_the_events_of_the_trigger_path_all_have_a_rule` | PASS |
| Timeout-Tick/Countdown funktionieren weiterhin | `test_the_countdown_and_the_timeout_sound_are_still_configured` | PASS |
| bestehender Feedback-Fix erhalten | `test_manual_accepted_still_produces_a_sound_and_an_led_effect` | PASS |
| LED-Katalogauflösung vollständig | `test_every_named_led_target_is_a_non_empty_name` | PASS |

### EVIDENCE – Mutationsnachweis

`evidence/ap8_mutation_check.txt`:

| Mutation | Ergebnis |
| --- | --- |
| M0 unverändert | 10 passed |
| **M1 Ablehnung wird ignoriert** (Feedback ohne akzeptiertes Ack) | 1 failed |
| M2 wiederhergestellt | 10 passed |

### EVIDENCE – LED-Suite

`evidence/ap9_led_full.txt`: `6 failed, 1500 passed, 23 skipped`.

Die sechs Fehlschläge sind **zeichengleich** dieselben wie in der Baseline
(`diff` der `FAILED`-Zeilen liefert keine Abweichung) und beruhen auf fehlenden
`.lefxset`-Archiven im Editable-Install, der in den eingefrorenen
Antigravity-Arbeitsbereich zeigt. Das LED-Repository ist in meinem
Arbeitsbereich unverändert (`git status --short` liefert 0 Zeilen), also kann
keiner dieser Fehlschläge aus dieser Aktion stammen.

### Nachtrag R4 – die letzten beiden Gate-Kriterien

Der Originalauftrag listet für GATE 8 unter anderem „Manual während
Wakewordactivation entsprechend", „bestehende Sounds vollständig" und
„Simulator funktioniert". Diese drei waren zuvor nicht einzeln belegt.

| Kriterium | Nachweis | Ergebnis |
| --- | --- | --- |
| Manual während Wakewordactivation | `ManualDuringWakeWordActivation::test_a_manual_trigger_inside_a_wake_word_turn_adds_no_second_sequence` | PASS |
| bestehende Sounds vollständig | `EveryConfiguredSoundCueHasAnAsset` – jede von einem Mapping benannte und jede deklarierte `SoundCueId` besitzt eine `.wav`-Datei; zusätzlich sind die fünf Cues des Triggerpfads namentlich festgenagelt | PASS |
| Simulator funktioniert | `led_controller_respeaker-v3/tests/device/test_simulator_window.py`, **6 passed, 0 skipped** (`evidence/r4_simulator_tests.txt`) – die Tests rendern den Ring mit einem echten `QApplication` in ein Bild und prüfen das Ergebnis | PASS |

### OFFEN

Keine. Der echte ReSpeaker gehört nach dem Originalauftrag zu GATE 10
(„ReSpeaker geprüft"), nicht zu GATE 8; GATE 8 verlangt an Hardwarenähe
ausschließlich „Simulator funktioniert", und das ist oben belegt.

### DECISION

GATE 8 **PASS**.

---

## GATE 9 – Softwareabnahme

```text
GATE:   9 – Cross-Repository-Regressionsabnahme
STATUS: PASS
```

### EVIDENCE – vollständige Suiten

| Repository | Ergebnis | Datei |
| --- | --- | --- |
| voice-stt-server | **476 passed, 13 skipped, 87 subtests** | `evidence/ap9_server_full.txt` |
| voice-stt-client | **502 passed, 218 subtests** | `evidence/ap9_client_full.txt` |
| led_controller_respeaker-v3 | 6 failed, 1500 passed, 23 skipped | `evidence/ap9_led_full.txt` |

Entwicklung der Testmengen:

```text
Server:  426 (Baseline) → 436 (AP1) → 453 (AP2) → 476 (AP4/AP3)
Client:  455 (Baseline) → 464 (AP6) → 492 (AP7) → 502 (AP8)
LED:     1506 unverändert (Repository nicht angefasst)
```

### EVIDENCE – Race- und Reconnecttests mehrfach

| Bereich | Wiederholungen | Datei |
| --- | --- | --- |
| AP1 Recorder-Gate-Races | 5 Läufe + 25 interne Wiederholungen je Fall | `evidence/ap1_race_repeats.txt` |
| AP2 Controller-Races | 5 Läufe + 12 interne Wiederholungen je Fall | `evidence/ap2_race_repeats.txt` |
| AP4 Activation-Timeout (Kaltstart) | 8 Läufe | `evidence/ap4_timeout_stability.txt` |
| AP7 Clientsuite komplett | 5 Läufe | `evidence/ap7_client_repeats.txt` |

### EVIDENCE – Mutationsnachweise statt bloßer Grünfärbung

Der Auftrag stellt fest, dass eine grüne Suite kein Gate-Nachweis ist. Für jeden
kritischen Mechanismus wurde deshalb belegt, dass die Tests ihn wirklich prüfen:

| Datei | Belegt |
| --- | --- |
| `evidence/ap2_mutation_check.txt` | Thread-Sicherheit des ActivationController |
| `evidence/ap4_mutation_check.txt` | Admission-Verdrahtung, Timer, Gate-Öffnung, einzige Follow-up-Autorität |
| `evidence/ap7_mutation_check.txt` | `start` bleibt Streambefehl, Ack-Dedupe, Generationsprüfung |
| `evidence/ap8_mutation_check.txt` | kein Accepted-Feedback ohne akzeptiertes Ack |

### EVIDENCE – LED-Suite jetzt vollständig grün (Nachtrag R5)

Die sechs LED-Fehlschläge der ersten Runde waren **kein** Codefehler, sondern
ein unvollständig vorbereitetes Environment: der Editable-Install von
`led-controller-version-3` zeigt in den eingefrorenen Antigravity-Arbeitsbereich,
in dem `scripts/build_effects.py` nie gelaufen ist, sodass die
`.lefxset`-Archive fehlten.

Reproduzierbarer Setup-Pfad im eigenen Arbeitsbereich:

```bash
python scripts/build_effects.py
```

und beim Testlauf `lefx` aus dem eigenen Clone auflösen, indem die drei
Paketverzeichnisse unter `packages/*/src` auf den `PYTHONPATH` gelegt werden.

Ergebnis (`evidence/r5_led_prepared_env.txt`):

```text
1506 passed, 23 skipped, 1 warning in 60.47s
```

**Null Fehlschläge.**

### Dokumentation der Skips (LED)

Alle 23 Skips stammen aus `tests/device/` und haben genau zwei Ursachen
(`evidence/r5_led_skips.txt`):

| Anzahl | Grund |
| --- | --- |
| 21 | `a reSpeaker is connected but unreachable: [Errno 13] Access denied (insufficient permissions)` |
| 2 | `needs someone at the cable; set LEFX_INTERACTIVE=1` |

**Bemerkenswert:** Ein ReSpeaker **ist angeschlossen**, nur nicht zugreifbar.
Der Hardwaretest scheitert also nicht an fehlender Hardware, sondern an
fehlenden Rechten beziehungsweise am Treiber. Das präzisiert die manuelle
Testanweisung in GATE 10.

### DECISION

GATE 9 **PASS**. Alle drei vollständigen Suiten laufen im korrekt vorbereiteten
Environment ohne Fehlschlag; die Skips sind vollständig aufgeschlüsselt. Die
finalen Zahlen stehen in GATE 11.

---

## GATE 10 – reale Abnahme

```text
GATE:   10 – Build und reale E2E-Abnahme
STATUS: MANUAL VALIDATION REQUIRED
```

Dieses Gate wird **ausdrücklich nicht als bestanden behauptet.** Der
Auftrag verlangt echte Audioeingabe, echten Serverpfad, echten Clientbuild und
echte ReSpeaker-Hardware. Was davon hier durchführbar war, ist unten belegt;
alles Übrige ist als `MANUAL VALIDATION REQUIRED` mit konkreter Testanweisung
ausgewiesen.

### Build – durchgeführt

`python scripts/build.py --clean`, Protokoll in
`evidence/ap10_client_build.txt`.

**Vorbedingung, die zunächst blockierte:** `voice-stt-client.spec` bricht ab,
wenn im installierten `lefx`-Paket keine `.lefxset`-Archive liegen:

```text
RuntimeError: No .lefxset archives found in the installed lefx package.
The build would produce a client whose every LED rule fails to resolve.
```

Ursache ist dieselbe wie bei den sechs LED-Testfehlschlägen: die global
installierte Distribution `led-controller-version-3` ist ein Editable-Install,
der in den **eingefrorenen** Antigravity-Arbeitsbereich zeigt, und dort wurde
`scripts/build_effects.py` nie ausgeführt. Ein Build **dort** wäre eine
Veränderung des READ-ONLY-Standes und wurde deshalb nicht durchgeführt; ein
Umbiegen des globalen Editable-Installs wäre ein Eingriff in die Umgebung des
Benutzers außerhalb des Auftrags.

**Nicht-invasive Auflösung:** `scripts/build_effects.py` wurde im **eigenen**
LED-Clone ausgeführt und `lefx` für den Buildlauf über `PYTHONPATH` aus diesem
Clone aufgelöst. Weder der Fremdstand noch die globale Installation wurden
verändert.

**Ergebnis: Build erfolgreich.**

```text
Dateipfad : voice-stt-client\dist\voice-stt-client.exe
Dateigröße: 78885525 Bytes
SHA-256   : 1ab993751e07f731f15629027bbf499927e1e23149b70d38450fe4d567811796
```

**Smoke-Test des erzeugten Binaries – tatsächlich ausgeführt**
(`evidence/ap10_exe_smoke.txt`):

```text
> dist\voice-stt-client.exe --version
voice-stt-client.exe 0.2.0
exit=0
```

Das Binary startet also, lädt seine Version und beendet sich sauber. Damit ist
der Punkt „echter Clientbuild funktioniert" aus §28 belegt — allerdings nur als
Start-/Versionsnachweis, **nicht** als funktionaler Diktatdurchlauf.

**PyInstaller-/Frozen-Pfadauflösung (§19):** Der Buildlauf durchläuft die
Schutzprüfung des Spec-Files, die genau diese Auflösung testet (die
`.lefxset`-Archive müssen im gebündelten `lefx`-Paket an derselben relativen
Stelle landen). Die Prüfung ist grün, sonst wäre der Build wie zuvor
abgebrochen.

### MANUAL VALIDATION REQUIRED

Die folgenden Punkte sind in dieser Umgebung **nicht** durchführbar. Für jeden
ist unten eine konkrete Testanweisung angegeben.

#### Präzisierung zur ReSpeaker-Hardware

Die LED-Suite meldet für 21 Gerätetests:

```text
a reSpeaker is connected but unreachable: [Errno 13] Access denied
(insufficient permissions)
```

Ein ReSpeaker **ist also angeschlossen**; er ist nur nicht zugreifbar. Der
Hardwaretest scheitert damit nicht an fehlender Hardware, sondern an fehlenden
Rechten beziehungsweise am USB-Treiber. Für die Abnahme genügt daher
voraussichtlich, die Tests mit ausreichenden Rechten beziehungsweise nach
Installation des passenden Treibers zu wiederholen. Zwei weitere Tests
verlangen ausdrücklich eine Person am Kabel (`LEFX_INTERACTIVE=1`).

#### Vorbereitung (einmalig)

```bash
cd P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude\led_controller_respeaker-v3 && python scripts/build_effects.py
```

Danach den Server starten:

```bash
cd P:\GithubRepos\marcosudau-vps-worktrees\einheitliche-triggerarchitektur-claude\voice-stt-server && python -m VoiceSTT_server.server --port 9001
```

#### M-1 – Pflichtmatrix der drei Triggerkombinationen

Je Kombination in `config.yaml` des Clients setzen und den Client starten:

| Nr. | `session.manual_trigger_enabled` | `session.wake_word_trigger_enabled` | Erwartung |
| --- | --- | --- | --- |
| M-1a | `true` | `false` | Hotkey öffnet Aufnahme; Wake Word bleibt wirkungslos |
| M-1b | `false` | `true` | Wake Word öffnet Aufnahme; **kein** Hotkey wird registriert |
| M-1c | `true` | `true` | beide Quellen öffnen dieselbe Activation |

Zu prüfen: `hello.activationConfig.mode == "controlled"` und
`sessionCapabilities.activationTriggers.supported == true` im Clientlog.

#### M-2 – Szenarien mit echter Sprache

1. Hotkey → sprechen → genau ein Final.
2. Hotkey → Follow-up abwarten → erneut Hotkey → sprechen.
3. Hotkey Finish beendet den Turn kontrolliert.
4. Hotkey Cancel verwirft den Turn.
5. Wake Word → sprechen.
6. Wake Word → Follow-up.
7. Manual **während** einer Wakeword-Activation.
8. Wake Word **während** einer Manual-Activation.
9. Beide Quellen nahezu gleichzeitig.
10. Timeout ohne Sprache.

#### M-3 – Protokollpflicht bei Kollisionen

Für die Fälle 7, 8 und 9 sind laut §23 zwingend zu protokollieren:

```text
activationId
primarySource
sources
segmentId
Anzahl Recording Starts
Anzahl Finals
```

Diese Felder stehen in den Timeline-Events; im Clientlog nach
`recording_started` suchen. **Sollwert je Kollision: genau eine
`activationId`, genau ein `recording_started`, genau ein Final.**

#### M-4 – weitere Pflichtszenarien

Countdown-Ring, Timeout-Sound, Reconnect im Idle, Reconnect während einer
Activation, Eventstream-Reconnect, Serverneustart, Mute/Unmute, Textinjektion,
History/Reinsert, **echter ReSpeaker**, alle relevanten Sounds, Clientstart und
Shutdown, sowie ein Legacyclient gegen den neuen Server.

Der **LED-Simulator** gehört nicht mehr zu dieser Liste: er ist automatisiert
abgenommen (`tests/device/test_simulator_window.py`, 6 passed, 0 skipped — die
Tests rendern den Ring mit einem echten `QApplication` in ein Bild und prüfen
das Ergebnis). Zu prüfen bleibt hier nur das Zusammenspiel am echten Gerät.

#### M-5 – Browserclient

Der Client ist auf den aktuellen Vertrag angepasst und automatisiert
abgesichert; siehe GATE 5. Der reale Browserlauf ist dort als **M-B1**
geführt und wird hier nicht doppelt aufgeführt.

#### M-6 – LED-Gerätetests mit Zugriffsrechten

```bash
python -m pytest tests/device -q
```

im LED-Repository mit ausreichenden Rechten ausführen; anschließend die zwei
interaktiven Tests mit `LEFX_INTERACTIVE=1`.

### Was den manuellen Test absichert

Die Kollisionsfälle 7–9 sind serverseitig automatisiert nachgewiesen
(`TriggerCollisionEndToEndTests`, jeweils mit den Zählnachweisen
`Activations = 1`, `recording_started = 1`), ebenso Timeout, Finish, Cancel,
Streamstop und Reconnect. Der manuelle Test prüft darüber hinaus die reale
Audio-, Feedback- und Hardwarekette, die automatisiert nicht erreichbar ist.

### DECISION

GATE 10 **MANUAL VALIDATION REQUIRED**. Build und Smoke-Test des Binaries sind
durchgeführt und belegt; die reale Audio- und Hardwareabnahme steht aus. Damit
lautet der Gesamtstatus nach §28 des Originalauftrags nicht `DONE`, sondern
**`PARTIAL`**.

---

## GATE 11 – Veröffentlichungsfähigkeit

```text
GATE:   11 – Dokumentation, Git und Abschluss
STATUS: PASS
```

### Abweichung vom Originalauftrag (bewusst)

GATE 11 des Originalauftrags sieht Push, Remote-Verifikation und CI-Prüfung
vor. Der aktuelle Auftrag verbietet Commit und Push ausdrücklich. Nach §4 des
Originalauftrags haben explizite aktuelle Benutzerentscheidungen Vorrang, also
bleibt der Push-Teil unausgeführt und wird als bewusst nicht umgesetzt
dokumentiert.

### EVIDENCE – finale Regression (tatsächlich ausgeführte Suiten)

Keine historische Zahl als Soll; die jeweils vorhandene Suite wurde vollständig
ausgeführt.

| Repository | Ergebnis | Datei |
| --- | --- | --- |
| voice-stt-server | **489 passed, 13 skipped, 94 subtests passed, 0 failed** | `evidence/final_server.txt` |
| voice-stt-client | **513 passed, 239 subtests passed, 0 failed** | `evidence/final_client.txt` |
| led_controller_respeaker-v3 | **1506 passed, 23 skipped, 0 failed** | `evidence/final_led.txt` |

**Skips im Einzelnen**

| Repository | Skips | Ursache |
| --- | --- | --- |
| Server | 13 | optionale Transkriptionsengines/Abhängigkeiten nicht installiert |
| Client | 0 | – |
| LED | 23 | 21× ReSpeaker angeschlossen, aber nicht zugreifbar (`Access denied`); 2× erfordern eine Person am Kabel (`LEFX_INTERACTIVE=1`) |

**Build und Frozen-Validierung — der tatsächlich letzte finale Build**
(`evidence/final_build.txt`, `evidence/final_exe_smoke.txt`):

```text
Dateipfad : voice-stt-client\dist\voice-stt-client.exe
Dateigröße: 78885525 Bytes
SHA-256   : 1ab993751e07f731f15629027bbf499927e1e23149b70d38450fe4d567811796
Build     : erfolgreich (PyInstaller 6.21.0)
Smoke-Test: voice-stt-client.exe 0.2.0   exit=0
```

Der SHA-256 wurde nach dem Build unabhängig über die Datei nachgerechnet, nicht
nur aus dem Buildprotokoll übernommen.

**Isolation vom eingefrorenen Fremdstand.** Der Build wurde ausschließlich aus
dem eigenen Arbeitsbereich, dessen drei Repositories und regulären
Python-Abhängigkeiten aufgelöst. Die global installierten
Editable-Distributionen von `led-controller-version-3` tragen über ihre
`.pth`-Dateien Pfade aus dem Antigravity-Arbeitsbereich in `sys.path` ein;
diese werden für den Buildprozess durch ein `usercustomize` **außerhalb aller
Repositories** wieder entfernt.

`usercustomize` und nicht `sitecustomize`, weil `scripts/build.py` sein eigenes
`scripts/pyinstaller_site` **vor** alles andere auf den `PYTHONPATH` stellt und
ein dort liegendes `sitecustomize.py` ein zweites verdeckt hätte. Python
importiert `usercustomize` regulär erst nach `sitecustomize`.

Nachweis im Protokoll:

```text
grep "worktrees\einheitliche-triggerarchitektur\" evidence/final_build.txt
→ 0 Treffer im gesamten Protokoll
```

Die Liste „Module search paths (PYTHONPATH)" enthält keinen einzigen
Antigravity-Pfad mehr.

**`git diff --check`** in allen drei Repositories: Exitcode `0`, siehe
`evidence/final_git.txt`.

### EVIDENCE – korrigierter Evidence-Collector

Der bisherige Collector schrieb hinter `git diff --check` unbedingt `(sauber)`
in die Evidence — auch dann, wenn der Befehl einen Fehler gemeldet hatte. Genau
das war passiert: der Client meldete
`docs/decisions/ADR-001_…md:3: trailing whitespace`, die Evidence behauptete
trotzdem „sauber". Als Nachweis ist das unzulässig.

Der neue Collector (`scratchpad/git_evidence.py`, außerhalb aller Repositories):

- prüft für jeden Befehl den tatsächlichen Rückgabewert;
- trennt stdout und stderr, weil `git diff --check` seine Befunde auf stdout
  meldet und stderr nur Zeilenendenhinweise trägt;
- filtert diese Hinweise in **beiden** Richtungen
  (`LF will be replaced by CRLF` und `CRLF will be replaced by LF`);
- schreibt bei einem Fehler niemals „OK", sondern `FEHLGESCHLAGEN`;
- prüft zusätzlich `INITIAL_HEAD == FINAL_HEAD` gegen die festgehaltenen Werte;
- beendet sich mit Exitcode 1, sobald irgendeine Prüfung fehlschlägt.

**Wirksamkeit in beide Richtungen nachgewiesen:**

```text
A) sauberer Zustand                    -> Exitcode 0, "EVIDENCE-LAUF ERFOLGREICH"
B) künstlich eingefügter Whitespace    -> Exitcode 1, "EVIDENCE-LAUF FEHLGESCHLAGEN"
                                          + "…ADR-001_…md:3: trailing whitespace."
C) wiederhergestellt                   -> Exitcode 0, "EVIDENCE-LAUF ERFOLGREICH"
```

Dabei fiel auch ein Fehler der **ersten** Fassung meines eigenen Collectors auf:
er wertete stdout und stderr gemeinsam aus und meldete deshalb `FEHLGESCHLAGEN`,
obwohl `git diff --check` mit Exitcode 0 sauber war. Behoben durch die
getrennte Auswertung; der Exitcode ist jetzt allein maßgeblich.

### EVIDENCE – behobener Whitespace-Fehler

`docs/decisions/ADR-001_BETRIEBSMODI_HOTKEY_UND_WAKE_WORD.md` enthielt in
Zeile 3 zwei abschließende Leerzeichen (eine Markdown-Zeilenumbruchmarkierung,
von mir beim Kennzeichnen des ADR als abgelöst eingefügt). Ersetzt durch eine
Leerzeile. Reine Dokumentationsänderung, kein Produktcode.

Ergebnis danach in allen drei Repositories:

```text
voice-stt-server             git diff --check  exit=0  OK - keine Whitespace-Fehler
voice-stt-client             git diff --check  exit=0  OK - keine Whitespace-Fehler
led_controller_respeaker-v3  git diff --check  exit=0  OK - keine Whitespace-Fehler
```

### EVIDENCE – kein Commit, kein Push

`evidence/ap11_git_final.txt`:

| Repository | INITIAL_HEAD | FINAL_HEAD | gleich |
| --- | --- | --- | --- |
| voice-stt-server | `13c162950b944dc715fdd81983a7465f8eb0fd79` | `13c162950b944dc715fdd81983a7465f8eb0fd79` | **ja** |
| voice-stt-client | `178d32bdf17d4709307e7a2a944888d2cf294e42` | `178d32bdf17d4709307e7a2a944888d2cf294e42` | **ja** |
| led_controller_respeaker-v3 | `aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0` | `aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0` | **ja** |

`git log -1 --oneline` liefert in allen drei Repositories unverändert den
Ausgangscommit. Sämtliche Arbeit liegt uncommitted im Working Tree. Es wurde
kein `git commit`, `git commit --amend`, `git push`, `git merge`, `git rebase`
oder `git tag` ausgeführt und kein Remote-Ref verändert.

`git diff --check` ist in allen drei Repositories sauber (nur die bekannten
LF/CRLF-Hinweise, keine Whitespace-Fehler).

### EVIDENCE – Antigravity-Quellstand unverändert

**Stufe 1 – Pfad und Größe.** Vor der ersten Aktion wurde ein Manifest aller
2514 Dateien erstellt (`evidence/antigravity_source_manifest_INITIAL.txt`), nach
AP0 (`…_CHECK1.txt`) und am Ende (`…_FINAL.txt`) erneut. Alle drei sind
identisch.

**Stufe 2 – bytegenau über SHA-256.** Pfad und Größe allein hätten eine
Änderung gleicher Länge nicht bemerkt. Für den Cleanup-Schritt wurde deshalb
zusätzlich jede Datei gelesen und gehasht
(`scratchpad/source_manifest.py`, ausschließlich `os.walk` und
`open(..., "rb")` — es wird dort nichts angelegt, verändert oder gelöscht):

```text
vor dem Cleanup : 2514 Dateien, 0 unlesbar
                  MANIFEST-SHA256 9e9dbfbfd4ac330530e340b406aa4659d1c30d24609f99077df36e70cf9f38c7
nach dem Cleanup: 2514 Dateien, 0 unlesbar
                  MANIFEST-SHA256 9e9dbfbfd4ac330530e340b406aa4659d1c30d24609f99077df36e70cf9f38c7

diff BEFORE AFTER → keine Abweichung
UNVERAENDERT: alle 2514 Dateien bytegenau identisch (SHA-256)
```

Dateien: `evidence/antigravity_sha256_BEFORE_CLEANUP.txt`,
`evidence/antigravity_sha256_AFTER_CLEANUP.txt`.

### EVIDENCE – Dokumentation gegen den Code geprüft

| Dokument | Ort |
| --- | --- |
| Zielarchitektur, Gate, Controller, Verträge, IDs, Events, Migration, Rollback, Privacy, Troubleshooting | `voice-stt-server/docs/einheitliche-triggerarchitektur.md` (460 Zeilen, mit Mermaid-Diagrammen) |
| Verlinkung | `voice-stt-server/docs/README.md` |
| Vertragsmatrix | `zusammenarbeit/…/CONTRACTS.md` |
| Entscheidungen zur Vorarbeit | `zusammenarbeit/…/DECISIONS.md` |
| Nachweise | diese Datei |
| Übergabestand | `zusammenarbeit/…/STATUS.md` |
| Abschlussbericht | `zusammenarbeit/…/REPORT.md` |

### OPEN FAILURES

Keine im erlaubten Umfang. Offen bleiben ausschließlich die unter GATE 10
benannten manuellen Abnahmen und der Push-Teil.

### DECISION

GATE 11 **PASS** für den erlaubten Umfang.
