# REPORT – Einheitliche serverseitige Triggerarchitektur

**Stand:** 2026-08-14, nach den Restarbeiten R1–R8
**Ergebnis:** `PARTIAL` – **manuelle Restabnahme erforderlich**

| Gate | Status |
| --- | --- |
| 0, 1, 2, 3, 4, 6, 7, 8, 9, 11 | **PASS** |
| 5 – Server bereit für alten und neuen Client | **MANUAL VALIDATION REQUIRED** (Browserlauf) |
| 10 – Build und reale E2E-Abnahme | **MANUAL VALIDATION REQUIRED** (Audio, Hardware) |

Es gilt strikt: **PASS** heißt, dass *alle* verbindlichen Kriterien dieses
Gates erfüllt und nachgewiesen sind. Kein Gate wird als „PASS für den
automatisierbaren Teil" geführt.

Dieser Bericht enthält ausschließlich den tatsächlichen Iststand.

---

## 0. Seit der letzten Abnahme ergänzt

| Punkt | Ergebnis |
| --- | --- |
| **GATE-4-Kollisionsmatrix** | drei getrennte E2E-Fälle mit je vier gezählten Invarianten inkl. **Scheduler allocations** (neu instrumentiert) |
| **Continuous-Streaming-Nachweis** | neuer Lifecycle-Test über den realen Clientpfad; dabei ein **zweiter Produktionsdefekt** gefunden und behoben |
| **GATE 5** | Browserclient repariert, statisch und per Replay geprüft, produktionsnaher Smoke-Test mit echtem uvicorn-Prozess; Gate bewusst auf `MANUAL VALIDATION REQUIRED` gesetzt |
| **GATE 8** | fehlende Kriterien ergänzt (Manual-während-Wakeword, Soundvollständigkeit, Simulator) → jetzt echtes PASS |
| **GATE 9** | LED-Suite im korrekt vorbereiteten Environment **vollständig grün** |
| **Gate-Vokabular** | überall auf PASS / FAIL / MANUAL VALIDATION REQUIRED normalisiert |
| **Dokumentationsaudit** | alle drei Repositories, siehe `DOKUMENTATIONSAUDIT.md` |
| **Cleanup-Schritt** | veraltete Aussagen zu Browserclient, Simulator, ReSpeaker und Build bereinigt; Evidence-Collector korrigiert; Build vom Fremdstand isoliert; SHA-256-Quellschutz |

---

## 1. Was wurde umgesetzt

### voice-stt-server

**Recorder-Gate** (`VoiceSTT/core/activation_control.py`, `VoiceSTT/audio_recorder.py`)

- Generationsbindung für `open`/`close`: eine alte Generation kann eine neuere
  Activation weder ersetzen noch schließen — auch nicht über den bisher
  ungeschützten Pfad `close(activation_id=None)`.
- `abort_controlled_activation_gate` und `shutdown_controlled_activation_gate`.
- `AudioToTextRecorder.abort()` und `.shutdown()` schließen das Gate jetzt im
  **Produktionscode** mit; nach `shutdown()` wird jedes weitere `open` abgelehnt.
- Im Controlled-Modus entscheidet allein das Gate; `recorder.wakeword_detected`
  wird dort nicht ausgewertet.

**ActivationController** (`api_fastapi_server/activation.py`)

- `generation` (stabil je Activation) von `version` (Änderungszähler für die
  Timerbindung) getrennt.
- `finalizing`-Phase ergänzt: das Fenster ist zu und das Gate geschlossen, die
  `activationId` lebt aber weiter, damit die nachlaufende Finaltranskription
  korreliert werden kann. `cancel` verwirft den Turn und geht ohne
  `finalizing` nach `inactive`.
- Interne `RLock`-Synchronisierung — der Controller wird aus der
  WebSocket-Coroutine, aus Recorder-Callbackthreads und aus dem Timeoutthread
  erreicht.
- `finalized()`, Segmentzähler, deterministisches `already_recording`.
- Aliasattrappen entfernt.

**Serverintegration** (`api_fastapi_server/server.py`)

- `parse_session_activation_query` wird im WebSocket-Einstieg aufgerufen und
  über `admit_session(activation_request=…)` bis in die Session durchgereicht.
  **Damit ist der Controlled-Modus erstmals produktiv erreichbar.**
- Strenge Query-Validierung (`invalid_activation_flag`,
  `invalid_activation_timing`) statt stiller Umdeutung nach `false`.
- `activation_trigger_required` für `false/false`; neu
  `activation_wake_word_unavailable`, wenn das Wake Word die einzige Quelle
  wäre, aber kein Wake-Word-Profil aktiv ist.
- `handle_trigger_command`: Lifecycle-Prüfung, korrelierbare Ablehnungen mit
  laufender `activationId`, Typprüfung, Idempotenz über `commandId`.
- Generationsgebundener Activation-Timer je Session.
- Rückwärtspfad `recording_started` / `recording_ended`.
- Wake Word läuft über denselben Controller und dasselbe Gate.
- Legacy-Wakeword-Follow-up im Controlled-Modus abgeschaltet.
- `activation.started` / `.extended` / `.closed`.
- `activationId`, `primarySource`, `sources` auf allen Timeline-Events.
- Capability `activationTriggers` erst nach vollständiger Verdrahtung.
- `activationConfig` in `hello` und `ready`.
- Reset der Activation bei Stream-Stop, Close und Clear.

### voice-stt-client

- `start`/`stop` sind wieder **Streambefehle**; der Manualtrigger wird
  zusätzlich gesendet (`_begin_stream_and_trigger`).
- `trigger_ack` wird konsumiert: Pending-Verwaltung mit `commandId`, gebunden
  an die Verbindungsgeneration; wiederholte, unbekannte und veraltete Acks
  werden verworfen, bevor ein Consumer sie sieht.
- `request_trigger()` mit Timeout; eine Ablehnung führt zu
  `trigger_rejected` **ohne** Verbindungsrecycling.
- Kein fachliches Accepted-Feedback vor dem Ack; Korrelation über die
  `commandId`, sodass ein wiederholtes Ack keinen zweiten Impuls erzeugt.
- Migration korrigiert: `hotkey → true/false`, `wake_word → false/true`;
  keine implizite `true/true`-Migration mehr.
- Betriebsmodus als fachliche Autorität überall durch die Triggerflags ersetzt
  (Timeline-Handling, Diktatfenster, `primary_dictation_action`,
  `extend_dictation_window`, Wake-Word-Streampflege, Konfigurationsrollback).
- Globale Hotkeys werden nur registriert, wenn der Manualtrigger aktiv ist.

### led_controller_respeaker-v3

**Keine Änderung.** Laut Auftrag §5 sind dort keine Produktcodeänderungen
vorgesehen; der Bedarf ist auch nicht entstanden. `git status --short` liefert
null Zeilen.

---

## 2. Was wurde bewusst nicht umgesetzt

- **Kein Commit, kein Push, kein Tag, kein Merge, kein Rebase** (Auftragsverbot).
  Damit entfällt der Push-Teil von GATE 11 des Originalauftrags.
- **Keine Änderung am eingefrorenen Antigravity-Arbeitsbereich**, auch nicht der
  dort fehlende `build_effects.py`-Lauf, der die LED-Testfehlschläge und die
  Build-Vorbedingung erklärt.
- **Kein Umbiegen des globalen Editable-Installs** von
  `led-controller-version-3` — das wäre ein Eingriff in die Umgebung des
  Benutzers außerhalb des Auftrags.

---

## 3. Gefundene echte Defekte

| # | Defekt | Wirkung | Status |
| --- | --- | --- | --- |
| 1 | Controlled-Modus war produktiv unerreichbar: `parse_session_activation_query` und `resolve_session_activation_config` hatten null Produktionsaufrufer | jeder reale `trigger` wurde mit `controlled_activation_disabled` abgelehnt | behoben |
| 2 | Activation-Timeout war ein Einmal-Timer; `Event.wait()` kehrt unter Windows geringfügig zu früh zurück, `expire()` antwortete `not_due`, der Timeout wurde **endgültig** verworfen | Activation läuft nie ab, Recorder-Gate bleibt dauerhaft offen | behoben |
| 3 | Client migrierte `mode=wake_word` nach `true/true` — die vom Auftrag verbotene implizite Migration; ein mitgelieferter Test schrieb das als Sollverhalten fest | Wake-Word-Installationen hätten zusätzlich den Hotkey aktiviert | behoben |
| 4 | Client ersetzte `send_start()` durch `send_trigger(activate)` | der Audiostream wäre nie gestartet worden | behoben |
| 5 | `_start_wakeword_followup_window()` setzte direkt `recorder.wakeword_detected` und startete einen eigenen Timerthread | zweite Recorder-Autorität und paralleler Follow-up-Timer im Controlled-Modus | behoben |
| 6 | Keine Capability `activationTriggers` | der gesamte neue Clientpfad war toter Code | behoben |
| 7 | Kein `trigger_ack`-Consumer im Client | „kein Accepted-Feedback vor Ack" war nicht erfüllbar | behoben |
| 8 | **Selbst verursacht und selbst gefunden:** durch das AP7-Gating wäre das Manual-Accepted-Feedback gegen triggerfähige Server entfallen | kein LED-/Soundfeedback beim Hotkey | behoben |

---

## 4. Gefundene Test-/False-Positive-Lücken

| Fundstelle | Befund |
| --- | --- |
| `test_server_controlled_e2e.py::test_04` (Vorarbeit) | Kommentar „Wait for timeout to fire in background timer thread", ruft dann selbst `expire()` **und** `close_controlled_activation()` auf und prüft danach, dass das Gate geschlossen ist. Es existierte kein Hintergrundtimer. Der Test bewies nur, dass der Test selbst schließt. |
| alle vier neuen Serverdateien der Vorarbeit | keine benutzte einen echten WebSocket-Einstieg; keine durchlief Query-Parsing oder Session-Admission |
| `test_recorder_activation_control.py` (Vorarbeit) | ausschließlich `SimpleNamespace`-Attrappen, obwohl §14 das ausdrücklich als unzureichend benennt |
| `test_config.py::test_legacy_wake_word_mode_migrates_query_parameters` (Vorarbeit) | schrieb die verbotene `true/true`-Migration als Sollverhalten fest |
| **meine eigene erste Fassung** der Nebenläufigkeitstests (AP2) | blieb auch ohne Lock grün; per Mutation nachgewiesen und anschließend wirksam gemacht |
| **meine eigene erste Fassung** der E2E-Tests (AP4) | erkannte die Reaktivierung des Legacy-Follow-ups nicht (Mutation M4); Lücke geschlossen |

---

## 5. Anti-False-Positive-Nachweise

Eine grüne Suite ist kein Gate-Nachweis. Für jeden kritischen Mechanismus wurde
per Mutationstest belegt, dass die Tests ihn wirklich prüfen:

| Datei | Mutation | Ergebnis |
| --- | --- | --- |
| `ap2_mutation_check.txt` | Lock des Controllers entfernt | 2 failed |
| `ap4_mutation_check.txt` | **Admission-Verdrahtung entfernt** (Zustand des Vorgängers) | **15 von 17 failed** |
| `ap4_mutation_check.txt` | Activation-Timer entfernt | 1 failed |
| `ap4_mutation_check.txt` | Gate-Öffnung entfernt | 8 failed |
| `ap4_mutation_check.txt` | Legacy-Follow-up reaktiviert | zunächst 0 failed → Testlücke → nach Ergänzung 1 failed |
| `ap7_mutation_check.txt` | `send_start` wieder durch Trigger ersetzt | 1 failed |
| `ap7_mutation_check.txt` | Ack-Dedupe entfernt | 3 failed |
| `ap7_mutation_check.txt` | Generationsprüfung entfernt | 1 failed |
| `ap8_mutation_check.txt` | Ablehnung ignoriert | 1 failed |

---

## 6. Welche Tests liefen

| Repository | Ergebnis | Baseline |
| --- | --- | --- |
| voice-stt-server | **489 passed, 13 skipped, 94 subtests, 0 failed** | 426 passed |
| voice-stt-client | **513 passed, 239 subtests, 0 failed** | 455 (1 lastabhängiger Fehlschlag) |
| led_controller_respeaker-v3 | **1506 passed, 23 skipped, 0 failed** | zuvor 6 failed wegen unvollständig vorbereitetem Environment |

Die 23 LED-Skips stammen sämtlich aus `tests/device/`: 21-mal ist ein ReSpeaker
angeschlossen, aber nicht zugreifbar (`Access denied`), zweimal wird eine Person
am Kabel verlangt (`LEFX_INTERACTIVE=1`). Server und Client melden 13
beziehungsweise 0 Skips.

Wiederholungsläufe: AP1-Races 5×, AP2-Races 5×, AP4-Timeout 8× aus dem
Kaltstart, Clientsuite 5× vollständig — jeweils grün.

Die sechs LED-Fehlschläge sind vorbestehend und umgebungsbedingt (fehlende
`.lefxset`-Archive im Editable-Install, der in den eingefrorenen Fremdstand
zeigt). Das LED-Repository wurde nicht angefasst.

---

## 7. Welche Builds geprüft wurden

`python scripts/build.py --clean` (PyInstaller 6.21.0), vollständig isoliert vom
eingefrorenen Antigravity-Arbeitsbereich:

```text
Dateipfad : voice-stt-client\dist\voice-stt-client.exe
Dateigröße: 78885525 Bytes
SHA-256   : 1ab993751e07f731f15629027bbf499927e1e23149b70d38450fe4d567811796
Build     : erfolgreich
Smoke-Test: voice-stt-client.exe 0.2.0   exit=0
```

Der SHA-256 wurde nach dem Build unabhängig über die Datei nachgerechnet.

Das Buildprotokoll enthält **keinen einzigen** Pfad aus
`…\marcosudau-vps-worktrees\einheitliche-triggerarchitektur\`; die
Modulsuchpfade zeigen ausschließlich in den eigenen Arbeitsbereich und in
reguläre Python-Abhängigkeiten. Erreicht wird das durch ein `usercustomize`
außerhalb aller Repositories, das die von den Editable-Installationen
eingetragenen Fremdpfade aus `sys.path` entfernt.

## 8. Welche Hardwaretests liefen

**Keine echten Hardwaretests.** Geprüft wurde ausschließlich der
**LED-Simulator**, und zwar automatisiert: `tests/device/test_simulator_window.py`
rendert den Ring mit einem echten `QApplication` in ein Bild und prüft das
Ergebnis (6 passed, 0 skipped).

Echte Audioeingabe und der echte ReSpeaker wurden **nicht** geprüft. Die
konkreten Testanweisungen stehen in `VALIDATION.md`, GATE 10, Abschnitte M-1
bis M-6.

**Präzisierung zum ReSpeaker:** Die LED-Gerätetests melden
`a reSpeaker is connected but unreachable: [Errno 13] Access denied`. Das Gerät
**ist angeschlossen**; der Test scheitert an fehlenden Zugriffsrechten
beziehungsweise am Treiber, nicht an fehlender Hardware.

---

## 9. Welche Verträge sich änderten

Alle Änderungen sind **additiv**:

- neue optionale Queryparameter auf `/ws/transcribe`;
- neuer Befehl `trigger` und neue Antwort `trigger_ack`;
- neues Feld `activationConfig` in `hello` und `ready`;
- neue Capability `activationTriggers`;
- neue Events `activation.started` / `.extended` / `.closed`;
- neue Korrelationsfelder auf bestehenden Timeline-Events.

Kein bestehender Eventname wurde verändert. Details in `CONTRACTS.md`.

---

## 10. Welche Legacyverträge erhalten blieben

- Eine Sitzung ohne die neuen Queryparameter verhält sich exakt wie bisher:
  kein `ActivationController`, Recorder in der `legacy`-Policy, unveränderter
  Wakeword-Follow-up. Nachgewiesen durch
  `test_a_session_without_trigger_parameters_stays_legacy` und
  `test_legacy_mode_still_starts_the_legacy_followup_window`.
- `start`/`stop` bleiben serverseitig unverändert.
- Der Feedback-Fix aus `178d32b` ist erhalten
  (`test_manual_accepted_still_produces_a_sound_and_an_led_effect`).
- 81 Tests der bestehenden Protokoll- und Multi-User-Suiten grün.

---

## 11. Offene Risiken

1. **GATE 10 offen.** Ohne reale Audio- und Hardwareabnahme ist nicht belegt,
   dass die Kette bis LED und Sound am echten Gerät wie vorgesehen wirkt. Die
   Kollisionsfälle sind serverseitig automatisiert nachgewiesen, die reale
   Feedbackkette nicht.
2. **Browserclient: realer Browserlauf offen.** Der Client wurde auf den
   aktuellen Vertrag angepasst und ist automatisiert abgesichert (statischer
   Vertragstest und Replay der exakten Sequenz gegen die echte App). Nicht
   geprüft ist allein die Darstellung im echten Browser mit Mikrofonfreigabe.
3. **Wake-Word-Trigger real ungetestet.** In dieser Umgebung sind keine
   OpenWakeWord-Modelle installiert; der Wake-Word-Pfad wurde über den
   Detektions-Callback geprüft, den die Engine aufruft, nicht über die Engine
   selbst.
4. **Umgebungsabhängigkeiten:** blockierendes Windows-WMI (betrifft jeden
   `torch`-Import) und fehlende `.lefxset`-Archive im Editable-Install, der in
   den eingefrorenen Fremdstand zeigt. Beide sind Umgebungsprobleme, keine
   Codefehler, aber sie blockieren Tests und Build
   ohne die in `VALIDATION.md` beschriebenen Umgehungen.

---

## 12. Was gepusht oder deployt wurde

**Nichts.** Es wurde nicht committet, nicht gepusht, nicht getaggt, nicht
gemergt und nicht gerebased. Alle drei Repositories stehen unverändert auf
ihrem Ausgangs-HEAD; die gesamte Arbeit liegt uncommitted im Working Tree.

```text
voice-stt-server             13c162950b944dc715fdd81983a7465f8eb0fd79  (unverändert)
voice-stt-client             178d32bdf17d4709307e7a2a944888d2cf294e42  (unverändert)
led_controller_respeaker-v3  aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0  (unverändert)
```

Der eingefrorene Antigravity-Arbeitsbereich ist nachweislich unverändert
(Manifest über 2514 Dateien, identisch vor und nach der Arbeit).
