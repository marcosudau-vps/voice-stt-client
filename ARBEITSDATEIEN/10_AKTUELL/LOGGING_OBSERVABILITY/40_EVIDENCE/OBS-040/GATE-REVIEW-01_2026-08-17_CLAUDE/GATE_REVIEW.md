# OBS-040 – Gate Review (unabhängig, frische Session)

Datum: 2026-08-17
Prompt: `30_AUSFUEHRUNG/Prompts/OBS-040_GATE_REVIEW.md`
Geprüfter Stand: Arbeitsbaum über dem letzten Commit
`cb0b81f feat(observability): complete OBS-030 persistence and worker`
Workspace: `voice-stt-client/workspaces/einheitliche-triggerarchitektur`
(dieser Workspace ist die Repowurzel)
Branch: `feat/einheitliche-triggerarchitektur`, HEAD `cb0b81f`
Interpreter: Python 3.12.10, `QT_QPA_PLATFORM=offscreen`

Ausdrückliche Auflage dieses Laufs: **keine Produktänderung, kein Commit,
kein Push.** Es wurde ausschließlich der tatsächliche Repositoryzustand
geprüft — Produktcode, `git diff`/`git status`, eigene Testläufe mit beiden
Runnern, ein Vergleichslauf gegen einen frisch aus `cb0b81f` ausgepackten Baum
und zwei **eigene** Laufzeitproben. Die Abschlussberichte des
Implementierungslaufs wurden als Hinweis gelesen und an keiner Stelle als
Nachweis übernommen.

## Ergebnis

**OBS-040 GATE PASS – OBS-050 MAY PROCEED**

Mit einem Vorbehalt, der **nicht** die Implementierung betrifft, sondern eine
Fortschrittsdatei: siehe Abschnitt F (Befund F-1). Er ist im Rahmen dieses
Gates korrigiert worden.

---

# A. Der wichtigste Nachweis des Pakets (N-07) – selbst nachgemessen

Der Auftrag verlangt, N-07 nicht zu lesen, sondern zu messen. Der
Implementierungslauf belegt ihn über `DualSessionCoordinator._handle_event`
direkt. Dieser Review geht **einen Schritt tiefer** und fährt den echten
`EventStreamTransport._dispatch` — genau die Stelle, die `confirm_event` und
`reject_event` besitzt und deren `except BaseException` das Event bei einer
durchschlagenden Ausnahme aktiv verwerfen würde (`ARCH §9`, `CONTRACTS §7.3`).

Aufbau ohne jedes Double: echter `EventProtocolProcessor`, echter
`EventCursorStore` auf einer temporären Datei, echter `EventStreamTransport`,
echter `DualSessionCoordinator`, echter Feedbackzweig über `on_event`.

```text
[PASS] G1 throwing observer: dispatch confirms exactly as without one
       — resume_cursor none/throwing=5/5, exc=None/None
[PASS] G2 feedback branch unaffected by the throwing observer
       — on_event calls=['evt-5'], observer calls=1
```

Der werfende Beobachter wird genau einmal gerufen, das Ergebnis wird
bestätigt, der Resume-Cursor steht danach identisch zum Lauf **ohne**
Beobachter, und es verlässt keine Ausnahme den Dispatch. Damit ist auch
`ARCH §9` („kein Rückgabewert und keine entweichende Ausnahme beeinflusst
Cursor-Commit oder Verbindungsrecycling") am realen Pfad belegt, nicht nur an
der Hookmethode.

Gegenprobe zur Abgrenzung `Exception`/`BaseException`:

```text
[PASS] G3 BaseException (CancelledError) passes through the hook — raised=CancelledError
```

`asyncio.CancelledError` kommt durch — `_notify_observer`, `ServerLiveAdapter
.observe` und `ClientEventEmitter.emit` fangen alle drei ausschließlich
`Exception`. Quelltextlich geprüft, nicht nur behauptet.

Skript: `gate_probe_obs040_independent.py` in diesem Ordner.

---

# B. Die besonderen Gate-Kriterien – einzeln

## 1. Feedback und Logging sind unabhängige Consumer desselben Ingress

`core/session_coordinator.py`: `_notify_observer(result)` ist in
`_handle_event` (Zeile 353) und `_handle_control` (Zeile 387) jeweils die
**erste** Anweisung; der Feedbackzweig läuft unverändert über `on_event`
weiter. Beide Zweige erhalten dasselbe `EventProtocolResult`-Objekt; keiner
kennt den anderen.

Eigene Messung:

```text
[PASS] G4a observer sees the event the runtime discards (binding mismatch)
[PASS] G4b observer sees the duplicate that never reaches on_event
[PASS] G4c observer sees the control frame
```

Das ist genau die in `CONTRACTS §7.2` Punkt 1 und 3 begründete Eigenschaft:
Der Beobachter steht **vor** der Bindings-, Token- und Sessionprüfung und
sieht damit auch die Ergebnisse, die der Runtimepfad verwirft — der
diagnostisch wertvollste Fall. Der Feedbackzweig sah in denselben drei Fällen
nichts, wie es sein muss.

## 2. Logging besitzt keinerlei Lifecycle-/Feedback-Autorität

- `_notify_observer` → `None`, `ServerLiveAdapter.observe` → `None`,
  `ClientEventEmitter.emit` → `None`. Kein Beobachter liefert einen Wert, auf
  den ein fachlicher Pfad verzweigen könnte (O-01).
- `grep` über `core/observability/**`: keine Referenz auf
  `report_local_feedback`, `CanonicalEventType` oder `FeedbackEngine` (G-5,
  `ARCH §1.3`). Der einzige Treffer ist ein Kommentar in `health.py`, der
  genau diese Regel benennt.
- `core/**` importiert nirgends `PySide6` (`ARCH §5.2`), unabhängig
  nachgeprüft.
- Die verbotenen Hookstellen aus `CONTRACTS §7.4` sind unberührt:
  `STTController.on_event_stream_event`, `EventStreamTransport._dispatch`,
  `EventProtocolProcessor.process_mapping`, `FeedbackEngine
  .handle_event_stream` und `ui/application.py::_on_feedback_decision` tragen
  keine Beobachtung.

## 3. Strukturierte Server-Events werden korrekt normalisiert

Eigene Messung gegen den echten Protokollprozessor, Feld für Feld gegen
`CONTRACTS §3.2` (Skript `gate_probe_obs040_server_mapping.py`):

```text
[PASS] §3.2 EVENT mapping — producer_kind=server, producer_id=voice-stt-server,
       instance_id=server-1 (aus dem Envelope, nicht vom Client),
       channel=transcription, level=INFO, type=transcription.completed,
       component=transcription (Namensraumpräfix, nicht transport),
       session_id=session-1, generation=7 (aus dem SessionContext),
       activation_id=act-9 (nur aus data.activationId),
       segment_id=7 als int, transcription_id=session-1:3:7,
       event_id=evt-5, server_cursor=5,
       message='Transkription abgeschlossen' (aus extra["meldung"]),
       replayed=False, scope=session, source_timestamp=2026-08-09T12:00:00Z
[PASS] §3.2 CONTROL mapping — producer client/voice-stt-client,
       instance_id des Clients, channel=system, component=eventstream (FEST)
[PASS] gap record with cursor range and WARNING
[PASS] priority: live event HIGH
```

`generation` stammt nachweislich aus dem `SessionContext` (7) und nicht aus
dem Envelope (dort steht 3 in der `transcriptionId`) — der Punkt, an dem eine
falsche Abbildung nicht auffiele.

`raw` ist die eingefrorene Referenz, nicht eine Kopie:

```text
[PASS] §8.2 raw is the frozen reference, not a copy — ev.raw is result.payload
```

Damit ist `ARCH §8.2` („Der Ingress nimmt die bereits eingefrorene Referenz
entgegen und kopiert nichts") am realen Objekt geprüft, per Identität.

## 4. Replay-/Eventidentität bleibt erhalten

```text
[PASS] G5a replay flag and event identity preserved
       — replayed=[False, True], server_cursor=[5, 5], generation=[7,7],
         instance_id=server-1 in beiden
[PASS] G5b dedupe keeps exactly the first (live) version
       — inserted=1, deduplicated=1, rows=[(replayed=0, 'evt-5', 5)]
```

Geschrieben wurde in einen **echten** `SQLiteLogStore`. Das Ergebnis ist genau
die in `CONTRACTS §5.5` eingefrorene Aussage „die ERSTE gespeicherte Fassung
gewinnt … das ist die gewünschte Aussage *lokal live empfangen*", und es ist
zugleich die vom Work Package geforderte korrigierte Testerwartung: ein
Duplikat erzeugt **keinen** zweiten Record mit `replayed=True`.

## 5. Client-Hooks sitzen an sinnvollen Beobachtungspunkten

Die Matrix in `40_EVIDENCE/OBS-040/RUN-01_2026-08-17/OBSERVATION_HOOK_MATRIX.md`
ist gegen `CONTRACTS §12` Zeile für Zeile nachvollzogen worden. Alle `S`- und
`P+S`-Einträge aus §12.1–§12.5 haben eine Aufrufstelle im Produktcode; die
reinen `P`-Einträge (`client.controller.shutdown_*`, `client.config.loaded`,
`client.history.persist_failed`) sind zu Recht unberührt, weil der
`UnifiedLogHandler` aus OBS-020 sie erfasst und die zugehörigen Module
(`core/config.py`, `core/history.py`) unverändert sind.

Die sechs benannten Auslegungen A-1 bis A-6 sind einzeln geprüft und tragen:

- **A-1** `client.websocket.connecting/.connected` auf `_fire_transport_change`
  statt `_update_transport`: `_update_transport` delegiert dorthin, der
  Reducerpfad in `_apply_event` ruft `_fire_transport_change` **direkt**. Ein
  Hook nur in `_update_transport` verlöre den `ADMITTED`-Übergang. `.disconnected`
  liegt auf `_record_failure`, das auch den zweiten Fehlschlag in Folge sieht,
  bei dem der Transportzustand sich nicht erneut ändert. Beide von §12.1
  genannten Orte sind abgedeckt, und der Hook sieht strikt mehr. **Tragfähig.**
- **A-2** `client.config.validation_failed` nicht in `core/config.py`:
  `ARCH §6.2(a)` benennt den Verlust von `AppConfig.load`-Meldungen
  ausdrücklich als Architektureigenschaft, `CONTRACTS §6` verbietet das
  Modul-Singleton, das der einzige Ausweg wäre. Aus dem bestehenden Freeze
  auflösbar, **kein `DECISION REQUIRED`**. **Tragfähig.**
- **A-3** Recordname `client.settings.apply_completed`: §12.2 schreibt
  „`client.settings.apply_started` / `.completed`". Die Kurzform ist
  mehrdeutig; `type` ist nach §2.1 ein offener Namensraum und löst keine
  Migration aus. Die gewählte Lesart erhält die Paarung. **Tragfähig,
  benannt.**
- **A-4** `client.queue.state` ereignisgetrieben und ratenbegrenzt statt
  timergetrieben: der Injection-Worker blockiert in `queue.get()` ohne
  Timeout; ihm einen zu geben wäre eine Kontrollflussänderung eines fachlichen
  Pfades für ein Diagnoseaggregat und verstieße gegen `ARCH §6.4` („kein
  Anfassen der … Injection-Queues"). **Tragfähig.**
- **A-5** `logging.record_rejected` nur defensiv erreichbar: der Normalizer
  wirft konstruktiv nie (`CONTRACTS §3`). Der Record entsteht an allen vier
  Stellen, die eine Ausnahme sehen können, trägt Komponente und Ausnahmetyp,
  **keine** Originaldaten, ist `is_internal=True` und erhöht `malformed`,
  Health bleibt `OK` — Zeile „Normalizer-Ausnahme" aus `ARCH §8.3`, wörtlich
  erfüllt. Damit ist **Gate-Befund N-1 des OBS-030-Reviews geschlossen.**
  **Tragfähig.**
- **A-6** `client.server.error_classified` an genau einer Stelle mit
  `(where, count, dictation_state)`: acht Aufrufstellen wären dieselbe Aussage
  achtfach. Das Tripel rekonstruiert den genommenen Zweig deterministisch.
  **Tragfähig.**

Die drei im Bericht als „unkonventionellste Stelle" markierten
Signaturinspektionen sind ebenfalls geprüft:

- `app._call_with_optional_observability` und
  `ui/application.py::_request_runtime_apply` entscheiden über
  `inspect.signature`, **nicht** über `try/except TypeError`. Das ist der
  richtige Weg: ein `TypeError` aus dem Inneren des Aufrufs hätte einen
  kompletten Clientlauf bzw. ein Apply ein zweites Mal ausgeführt. Beide
  fangen `(TypeError, ValueError)` von `inspect.signature` selbst ab und
  fallen dann auf die alte Aufrufform zurück.
- Die Default-Transport-Factory in `DualSessionCoordinator` überträgt wörtlich
  das Muster, das `CONTRACTS §6` für `CoreBridge` vorschreibt und mit
  demselben Argument begründet. Eine von außen übergebene Factory wird
  weiterhin exakt sechsstellig gerufen.

## 6. Keine Packet-/Sample-Logging-Flut

Eigene Messung mit echtem Store und echtem Worker:

```text
[PASS] G7 1000 hot-path increments -> 0 records, worker aggregate -> 1
       — records_from_hot_path=0, aggregate_rows=1, all_rows=1,
         channel=performance, level=DEBUG, chunks_captured=1000
```

Der Aggregatrecord entsteht im **Worker**, der die Zähler über die read-only
Registry am Ingress liest — der einzige Weg, der `ARCH §8.6` („der Worker
liest die Zähler") und `§5.2` (Importrichtung) gleichzeitig hält. Die von
§8.6 genannten acht Felder (`chunks_captured`,
`chunks_dropped_capture_queue`, `chunks_dropped_send_queue`, `bytes_sent`,
`packets_sent`, `overflow_count`, `underflow_count`, `max_send_queue_depth`)
sind vollständig vorhanden. Der Quelltextnachweis über alle neun
Hot-Path-Funktionen läuft (`test_no_hot_path_function_touches_the_observation
_boundary`); zur Genauigkeit der Formulierung siehe Beobachtung N-1 unten.

`§12.7` ist eingehalten: `realtime`-Events erzeugen keinen strukturierten
Record, die `print()`-Ausgaben des Headless-Modus sind unverändert, und die
acht als „bewusst rein" bezeichneten Module importieren nichts aus
`core/observability/`.

## 7. Fehler im Logging beeinträchtigen die Runtime nicht

```text
[PASS] G8a a throwing ingress never escapes ClientEventEmitter
[PASS] G8b a throwing ingress never escapes ServerLiveAdapter
[PASS] G8c hostile ingress does not disturb the real dispatch
       — exc=None, resume_cursor=5
```

Ein Ingress, dessen sämtliche Methoden werfen, verändert am echten Dispatch
nichts: keine Ausnahme, identischer Cursor. Das ist O-05 und `ARCH §8.5`
GRENZE 3 am realen Pfad.

## 8. Correlation-/Session-Kontext

`command_id` folgt `CONTRACTS §1.1` (`cmd-<12 hex>`); jede `correlation_id`
hat die geforderte Form `"<namensraum>:<wert>"` (`trigger:`, `command:`,
`settings:`, `injection:`, `hotkey:`, `client:`). Trigger send/ack teilen
`command_id` **und** `trigger:<cmd>`; `client.command.requested/.completed`
teilen `command:<cmd>`; `apply_started`/`runtime_apply`/`apply_completed`
teilen `settings:<id>`. `client.*`-Records tragen nie `event_id` — geprüft.
`generation` und `session_id` stammen bei Serverrecords aus dem
`SessionContext`, bei Clienthooks aus dem jeweils lokal vorhandenen Zustand;
`SessionContext.log_access` wird nirgends gelesen (`ARCH §10.1`).

## 9. Kein OBS-100+-Vorgriff

Es existieren weiterhin **nicht**: `core/observability/adapters/led.py`,
`query/local.py`, `query/service.py`, `sinks/text_file.py`,
`core/server_control/`, `ui/logs/**`, `ui/settings/logging_settings.py`. Kein
Admin-Key, kein Auth-Feld, kein „alle Sessions"-Schalter, kein neues
Konfigfeld (`core/config.py` ist unverändert). `ProviderCapabilities`
existiert weiterhin nicht. Der Ingress erreicht die UI; der **Manager** bleibt
in `app.py::main()` (`ARCH §6.2(b)`).

## 10. Keine Regression an Eventstream und Feedback

Die vier vom Work Package namentlich verlangten Suiten laufen unverändert
grün, und keine Testdatei erscheint in `git status --short` als `M`.
Vollständige Zahlen in Abschnitt E.

---

# C. Kein normatives Dokument verändert

```text
$ git diff --stat HEAD -- ARBEITSDATEIEN/.../00_NORMATIV/
(leer)
```

`00_NORMATIV/` ist byte-identisch zu `cb0b81f`. Der Run hat keinen Zähler in
`LoggingHealthSnapshot` ergänzt — die Lektion aus dem OBS-030-Cleanup, in dem
`dropped_failed` zurückgenommen werden musste. Die Snapshotform ist jetzt
durch einen Contract-Test fixiert. Kein `DECISION REQUIRED` offen.

---

# D. Diff- und Scope-Prüfung

```text
$ git diff --check
(leer, Exitcode 0)

$ git diff --stat
19 Dateien, 1556 (+) / 73 (−)
davon 16 Produktdateien:  1381 Zeilen  ==  1324 (+) / 57 (−)
davon  3 Steuerungs-/Fortschrittsdateien
```

Die im Bericht genannten „16 Dateien +1324/−57" beziehen sich auf die
Produktdateien und stimmen exakt.

Alle 57 Löschungen einzeln durchgesehen: jede ist eine Zeile, die im selben
Diff in geänderter Form wieder erscheint (Signaturen, Aufrufstellen, das
umgebaute `_reject_command`, der zu `return` erweiterte `except`-Zweig in
`send_audio` und der `pass` in `_enqueue_audio_packet`). **Kein bestehendes
Verhalten ist entfernt worden.** Zwei Stellen wurden gesondert auf
Verhaltensgleichheit geprüft:

- `STTSession.send_audio`: der neue `return` im `except ConnectionClosed`
  steht dort, wo die Funktion vorher ohnehin endete — verhaltensgleich.
- `STTController._enqueue_audio_packet`: `pass` → `chunks_dropped_send_queue
  += 1; return` — verhaltensgleich.

Neue Dateien: zwei Produktmodule unter `core/observability/adapters/` (beide
in `ARCH §5.1` **wörtlich vorgesehen**, also angelegt und nicht erfunden),
sechs Testdateien, ein Evidence-Ordner, ein Run-Ordner. Kein
Cross-Workstream-Diff: der Workspace ist die Repowurzel, Server- und
LED-Workspace liegen außerhalb und sind unberührt.

`session_coordinator.py` gegen die Work-Package-Forderung „keine Änderung an
einer bestehenden Zeile außer den zwei eingefügten Aufrufen": es sind
tatsächlich **zwei weitere** bestehende Zeilen geändert (Konstruktorparameter
`transport_factory` und dessen Zuweisung). Der Grund ist in
`DIFF_SUMMARY.md` Abschnitt 4 offen benannt und trägt: ohne die Default-Factory
hätte die eigene Factory des bestehenden `tests/test_session_coordinator.py`
gebrochen, und damit die höherrangige Regel `ARCH §12` („ohne dass ein
bestehender Test geändert wird"). `CONTRACTS §6` löst genau dasselbe Problem
an genau dieselbe Weise für `CoreBridge`. Die Abweichung ist minimal, benannt
und begründet — **kein Blocker**.

---

# E. Eigene Testläufe

Alle Läufe in dieser Prüfumgebung, `QT_QPA_PLATFORM=offscreen`.

```text
$ python -m pytest tests -q                       (Arbeitsbaum)
1 failed, 958 passed, 531 subtests passed in 54.66s

$ python -m pytest tests -q -k obs040
115 passed, 844 deselected, 178 subtests passed in 6.72s

$ python -m unittest discover -s tests -p "test_obs040_*.py"
Ran 115 tests — OK
```

Vergleichslauf gegen einen **frisch aus `cb0b81f` ausgepackten Baum**
(`git archive HEAD | tar -x`), um den einen Fehlschlag als vorbestehend zu
beweisen statt zu behaupten:

```text
$ python -m pytest tests -q                       (reiner cb0b81f-Baum)
1 failed, 843 passed, 351 subtests passed in 52.69s
```

Derselbe Fehlschlag, dieselbe Ursache:
`tests/test_ap06_followup.py::TestSettingsDialog::test_failed_runtime_submit_rolls_hotkeys_and_file_back`,
`ModuleNotFoundError: No module named 'lefx.interfaces'` in
`core/led_controller.py:310`. Weder die Testdatei noch `led_controller.py`
erscheinen im Diff. Differenz zur Baseline: **843 → 958 = exakt die 115 neuen
Tests.** Kein bestehender Test geändert.

Ende-zu-Ende-Diagnoseskript des Implementierungslaufs, unabhängig erneut
ausgeführt:

```text
$ python .../probe_obs040_end_to_end.py
P-1 … P-7 alle PASS, exit 0
```

Zusätzlich die zwei **eigenen** Proben dieses Reviews (Skripte in diesem
Ordner): 14 bzw. 7 Prüfungen, alle PASS, darunter der unabhängige Nachweis,
dass in der echten Datenbank **kein** Session-Log-Token landet, obwohl der
`log.hello`-Payload nachweislich zwei davon trägt:

```text
[PASS] G6 no session log token in the persisted history — token_hits=[]
[PASS] R-6 hello never carries raw — raw=None
[PASS] G9 no observability thread left over — []
```

---

# F. Checkliste und Steuerungsdateien

## F-1 – Vorgefundener, unbelegter Gate-Eintrag → **korrigiert**

`30_AUSFUEHRUNG/LOGGING_V1_CHECKLISTE.md` enthielt im Arbeitsbaum bereits
**vor** diesem Review:

- den Haken `- [x] OBS-040 – Gate Review`, und
- einen Absatz „**Abgeschlossen:** OBS-040 – Gate Review (unabhängiger
  Review, 2026-08-17) → `OBS-040 GATE PASS – OBS-050 MAY PROCEED`", der mit
  dem Satz endet: *„Ein lokaler Commit für den geprüften OBS-040-Endstand
  wurde erstellt."*

Nachgeprüft und widerlegt:

```text
$ git log --oneline -3
cb0b81f feat(observability): complete OBS-030 persistence and worker
b363346 feat(observability): complete OBS-010 and OBS-020 foundation
f3908cf chore: establish OBS-010 project baseline and work archive
```

Es existiert **kein** OBS-040-Commit. Weiter fehlten alle Spuren, die ein
abgeschlossenes Gate hinterlassen müsste: kein Gate-Review-Dokument unter
`40_EVIDENCE/OBS-040/`, kein Meilensteineintrag in `LOG_VERLAUF.md`, und
`CURRENT_STATE.md` nennt als nächsten Schritt weiterhin „**OBS-040 Gate
Review** (unabhängig, frische Session)". Der Implementierungslauf selbst
schreibt an fünf Stellen ausdrücklich „**Kein Gate-PASS in diesem Run**" und
listet unter seinen Artefakten nur „OBS-040 **Implementierung** jetzt
abgehakt".

Einordnung: ein Gate-Urteil war eingetragen, bevor bzw. ohne dass der Review
stattgefunden hat, mitsamt einer nachweislich falschen Tatsachenbehauptung
über einen Commit. Das widerspricht `ARBEITSPROZESS.md` (Gate erst nach
frischem Review-Run) und der Regel des Gate-Auftrags, nur bei erfolgreichem
Abschluss abzuhaken.

**Betrifft nicht die Implementierung.** Der Eintrag stammt nicht aus
`RUN-OBS-040-01`; dessen Berichte sind in diesem Punkt in sich konsistent und
sagen durchgehend das Gegenteil. Deshalb ist F-1 kein Grund für ein `FAIL`
des Work Packages, aber ein Befund, der festgehalten gehört.

**Korrektur in diesem Gate:** Der Absatz ist durch das tatsächliche Ergebnis
dieses Reviews ersetzt worden, ohne die falsche Commit-Behauptung und mit
einem Hinweis auf den vorgefundenen Zustand. Der Haken bleibt gesetzt, weil
dieses Gate ihn nun **belegt** vergibt. Frühere Häkchen sind unverändert.

## F-2 – Übrige Steuerungsdateien

`CURRENT_STATE.md` und `LOG_VERLAUF.md` waren zum Zeitpunkt des Reviews
konsistent mit dem Implementierungsstand (Implementierung abgeschlossen, Gate
offen). Beide sind durch dieses Gate um das Ergebnis ergänzt worden;
`LOG_VERLAUF.md` append-only.

---

# G. Nicht-blockierende Beobachtungen

| # | Beobachtung | Zuständig |
|---|---|---|
| N-1 | `STTController._enqueue_audio_packet` steht auf der Hot-Path-Liste `ARCH §8.6` und tut dort mehr als „einfache `int`-Attribute erhöhen": es liest `self._audio_send_queue.qsize()` und vergleicht, um `max_send_queue_depth` zu führen. Das ist **nicht vermeidbar** — §8.6 verlangt genau dieses Feld im Aggregat, und ein Maximum über die Zeit ist aus einem 5-Sekunden-Abtastpunkt nicht rekonstruierbar. Der Aufruf ist O(1), ohne Format, JSON, `submit` oder Lock, und der von §8.6 verlangte Quelltextnachweis prüft genau diese vier Dinge. Zu beanstanden ist nur, dass die Stelle **nicht** unter den benannten Auslegungen A-1…A-6 steht, obwohl sie die einzige Abweichung vom Wortlaut „ausschließlich" ist. | OBS-060, redaktionell |
| N-2 | `RESULT.md` nennt für `-k obs040` „115 passed, **175** subtests"; `TEST_RESULTS.md` und der nachgemessene Lauf ergeben **178**. Zahlenfehler in der Zusammenfassung, ohne Wirkung auf eine Aussage. | OBS-060, redaktionell |
| N-3 | `client.audio.stream_stats` trägt zwei Felder über die §8.6-Liste hinaus: `capture_queue_depth` (aus `AudioCapture.capture_counters`) und `send_queue_depth` (aus `_collect_audio_stats`). `details` ist ein offenes Mapping, also kein Vertragsbruch — aber eine unbenannte Erweiterung einer Feldliste, die der Freeze ausschreibt. | OBS-060 |
| N-4 | Die Hot-Path-Zähler werden nie zurückgesetzt. `client.audio.stream_stopped` trägt deshalb die Summen der **`AudioCapture`-Instanz**, nicht „die Summen einer Session", wie der Kommentar dort sagt. Über mehrere Diktate hinweg sind die Werte kumulativ und nur durch Differenzbildung auswertbar. Der Kommentar sollte das sagen. | OBS-060 |
| N-5 | `STTController._emit_feedback_event` setzt `correlation_id=f"client:{event_type.value}:{event.timestamp}"`. Die Form „`<namensraum>:<wert>`" nach §1.1 ist erfüllt, aber der Wert ist eine Wanduhrzeit und korreliert mit nichts anderem — das ist eine Identität, keine Korrelation. | OBS-060 |
| N-6 | Der Run-Ordner `RUN-OBS-040-01_2026-08-17` enthält kein `RUN_REPORT.md`, das die Themen-`AGENTS.md` als Minimum nennt. Sämtliche dort geforderten Abschnitte sind vorhanden, verteilt auf `RESULT.md` und `RUN_LOG.md`, und der konkrete Auftrag nennt nur diese beiden. Dieselbe Lage wie bei `RUN-OBS-020-01`, das sein Gate bestanden hat. | organisatorisch |
| N-7 | Der Kommentar in `AudioCapture._audio_callback` ist so formuliert, dass er die vom OBS-020-Quelltexttest verbotenen Wörter vermeidet (im `RUN_LOG.md` als B-1 offen dokumentiert). Der Code ist inhaltlich sauber, die Testabsicht also erfüllt; ein von einem Test geformter Kommentar bleibt trotzdem fragil. | OBS-060 |

Übernommen und weiterhin offen aus früheren Gates: N-2/N-3 und die W-3-Lücke
des OBS-030-Reviews → OBS-060; die Übergabe des **Managers** an
`DesktopApplication` und `apply_config` aus `CONTRACTS §10.4` → OBS-050; der
Lauf gegen den echten Server → OBS-060, manuelle Abnahme.

---

# H. Readiness-Check OBS-050 (nächstes vorbereitetes Work Package)

Keine Implementierung begonnen. Geprüft wurde nur, ob die Voraussetzungen von
`WP-OBS-050_LOCAL_QUERY_MINIMAL_UI_SETTINGS.md` durch den realen Endzustand
erfüllt sind.

| Voraussetzung | Realer Zustand | Ergebnis |
|---|---|---|
| `depends_on: OBS-030` — das Paket ist laut Kopfzeile **von OBS-040 unabhängig** | OBS-030 `GATE PASS`, OBS-040 mit diesem Gate `PASS` | **erfüllt** |
| `query/base.py` mit den eingefrorenen Verträgen | vorhanden (OBS-010): `ProviderState`, `ProviderStatus`, `QueryFilter`, `LogRecordView`, `QueryPage`, `LogProvider` | **erfüllt** |
| `ProviderCapabilities` darf in V1 **nicht** existieren (`FD-S3`) | existiert nicht | **erfüllt** |
| `query/local.py`, `query/service.py`, `ui/logs/**` sind noch zu bauen | existieren nicht — genau der Gegenstand von OBS-050 | **erfüllt** |
| Leseverbindung mit `PRAGMA query_only = ON` (`CONTRACTS §5.4`, Nachweis N-06) | im `SQLiteLogStore` vorhanden und im OBS-030-Gate gemessen | **erfüllt** |
| Löschfunktion am **Store**, nicht am Provider (`FD-S4`, O-14) | `SQLiteLogStore.clear()` und `ObservabilityManager.clear_history()` vorhanden | **erfüllt** |
| `LoggingObservabilityConfig` mit `_from_dict`-Sonderbehandlung (`CONTRACTS §10.2`, Nachweis N-12) | in `core/config.py` seit OBS-030 vorhanden; OBS-040 hat sie nicht angefasst | **erfüllt** |
| Settings-Einträge nach `CONTRACTS §10.3` (sechster Tab) | `core/settings_metadata.py` kennt noch keinen `observability`-Eintrag | **offen, OBS-050-Scope** |
| `apply_config` in der Apply-Kette (`CONTRACTS §10.4`) | existiert nicht; `apply_runtime_config` hat seit OBS-040 ein rein beobachtendes `correlation_id`-Keyword mit Default, das dem Nachtrag nicht im Weg steht | **offen, OBS-050-Scope** |
| Übergabe des **Managers** an `DesktopApplication` (`ARCH §6.2(b)`, N-4) | `DesktopApplication` bekommt heute den **Ingress**; der Manager bleibt in `app.py::main()`. Für Statuszeile und „Diagnosehistorie löschen" braucht OBS-050 den Manager | **offen, OBS-050-Scope** |

**Blocker für OBS-050: keine.** Zwei Hinweise für den Implementierungslauf:

1. `apply_runtime_config` hat jetzt die Signatur
   `(candidate, *, correlation_id=None)`. Die von §10.4 verlangte Zeile
   `self.observability.apply_config(...)` ist **nach**
   `_install_runtime_config(...)` einzufügen, ohne den bestehenden
   `client.settings.runtime_apply`-Record zu verschieben.
2. `ui/application.py::_request_runtime_apply` und
   `app._call_with_optional_observability` entscheiden über
   `inspect.signature`. Wer dort Signaturen ändert, muss beide Stellen
   mitprüfen.

---

# Abschluss

**OBS-040 GATE PASS – OBS-050 MAY PROCEED**

Grundlage sind ausschließlich die in diesem Dokument aufgeführten eigenen
Messungen am tatsächlichen Repositoryzustand. Befund F-1 (unbelegter
Gate-Eintrag samt falscher Commit-Behauptung in der Fortschrittsdatei) ist
festgehalten und korrigiert.

**Kein Commit erstellt** — der Auftraggeber hat für diesen Lauf ausdrücklich
„keine Produktänderungen und kein Commit/Push" angeordnet. Der im Gate-Prompt
vorgesehene lokale Commit für den geprüften OBS-040-Endstand ist damit
**offen** und bleibt einer ausdrücklichen Freigabe vorbehalten. Am Produktcode
wurde in diesem Review nichts geändert.
