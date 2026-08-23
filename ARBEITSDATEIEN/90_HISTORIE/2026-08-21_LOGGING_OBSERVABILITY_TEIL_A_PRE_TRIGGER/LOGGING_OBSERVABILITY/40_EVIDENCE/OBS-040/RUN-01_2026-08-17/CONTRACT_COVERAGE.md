---
id: EV-OBS-040-CONTRACT-COVERAGE
run: RUN-OBS-040-01_2026-08-17
work_package: OBS-040
authority: evidence
date: 2026-08-17
---

# OBS-040 – Contract-Deckung

Für jede OBS-040-relevante Vorgabe der drei normativen Dokumente: Ort der
Umsetzung, Nachweis, Status. `NICHT OBS-040` heißt: die Vorgabe gehört zu einem
anderen Paket und ist hier unverändert.

Die Zeilen sind bewusst so formuliert, dass eine behauptete Umsetzung ohne
Code-Entsprechung auffällt — das war der blockierende Befund B-2 des ersten
OBS-030-Gates.

## 1. Die verbindlichen Vorgaben aus dem Work Package

| Vorgabe | Umsetzung | Nachweis | Status |
|---|---|---|---|
| Hookstelle `DualSessionCoordinator._handle_event` und `_handle_control`, jeweils als **erste** Anweisung, rückgabewertfrei, in `try/except Exception` | `core/session_coordinator.py::_notify_observer` + je erste Anweisung | `test_notify_observer_is_the_first_statement_of_both_dispatch_paths` (Quelltextprüfung), `test_notify_observer_is_return_value_free` | **UMGESETZT** |
| Verbotene Hookstellen unberührt | `STTController.on_event_stream_event` weiter frei und unbenutzt von Logging; `_dispatch`, `process_mapping`, `handle_event_stream`, `_on_feedback_decision` ohne Observation | `test_forbidden_hook_locations_carry_no_observation` (6 Subtests) | **UMGESETZT** |
| `BaseException` wird nirgends gefangen; `asyncio.CancelledError` kommt durch | `except Exception` in `_notify_observer`, `ServerLiveAdapter.observe`, `ClientEventEmitter.emit` | `test_base_exception_from_the_observer_is_not_swallowed`, `test_cancellation_is_never_swallowed`, `test_cancellation_still_propagates` | **UMGESETZT** |
| Zweiter Beobachtungspunkt im `except`-Zweig von `EventStreamTransport.run()` → `client.eventstream.protocol_error`, ohne Rohframe | `core/event_stream.py::run` (eine Zeile) → `_observe_protocol_error` | `test_a_protocol_violation_becomes_a_structured_record`, `test_the_record_never_carries_a_raw_frame` | **UMGESETZT** |
| Injektionsweg über die Default-Factory in `CoreBridge`; `ControllerFactory` bleibt einstellig | `ui/core_bridge.py::__init__` | `test_the_controller_factory_stays_single_argument`, `test_the_default_factory_hands_the_ingress_to_the_controller` | **UMGESETZT** |
| Hookliste vollständig nach `CONTRACTS §12`, Reihenfolge nach aufsteigendem Risiko | 42 Recordtypen | `OBSERVATION_HOOK_MATRIX.md`, `test_every_implemented_type_appears_in_its_module` (42 Subtests, je Recordtyp einer) | **UMGESETZT** |
| Hot-Path-Regeln `ARCH §8.6`: dort ausschließlich `int`-Zähler; das 5-Sekunden-Aggregat erzeugt der **Worker**, der die Zähler liest | Zähler in `audio_capture.py`, `stt_session.py`, `controller.py`; Aggregat in `worker.py::_emit_aggregates_if_due` | `test_no_hot_path_function_touches_the_observation_boundary` (9 Subtests), `TestNoPerPacketLogging` (3), `TestWorkerProducesTheAggregate` (6), Probe P-5 | **UMGESETZT** |
| `raw` wird im Producer nicht kopiert und nicht serialisiert | `ingress.observe_server_result` übernimmt die eingefrorene Referenz | `test_raw_is_the_frozen_reference_and_is_not_copied` (Identitätsprüfung) | **UMGESETZT** |
| Korrigierte Testerwartung: ein Duplikat erzeugt **keinen** Record mit `replayed=True` | CONTROL-Pfad des Normalizers | `test_duplicate_is_observed_but_produces_no_second_stored_row`, Probe P-2 | **UMGESETZT** |
| `lefx.*`-Normalizer-Regel scharf schalten | `normalizer.from_log_record` (OBS-010) läuft ab OBS-020 im echten Handler; OBS-040 ändert daran nichts | `tests/test_obs010_normalizer_python.py` unverändert grün; siehe Punkt 6 | **UNVERÄNDERT WIRKSAM** |

## 2. `LOGGING_ARCHITEKTUR_FREEZE_V1.md`

| § | Vorgabe | Umsetzung / Nachweis | Status |
|---|---|---|---|
| §1.1 O-01 | Logging besitzt keine fachliche Runtime-Autorität; kein Rückgabewert eines Beobachters steuert einen fachlichen Ablauf | `_notify_observer` → `None`; `ClientEventEmitter.emit` → `None`; `ServerLiveAdapter.observe` → `None`. N-07 und `TestObserverFailureDoesNotAffectTheClient` (7 Tests) | **UMGESETZT** |
| §1.1 O-02 | Fan-out statt Vermittlung | `on_event` (Feedback) und `on_observation` (Logging) sind zwei unabhängige Zweige derselben Dispatchstelle; `TestIndependentFanOut` (4) | **UMGESETZT** |
| §1.1 O-03 | Non-Blocking, ausschließlich `put_nowait` | unverändert aus OBS-020; `test_a_full_queue_never_blocks_a_producer` (1000 Beobachtungen auf Queue-Größe 1) | **UMGESETZT** |
| §1.1 O-04 | Bounded Memory | unverändert; die neue Aggregatquellen-Registry ist nach `type` geschlüsselt und wächst daher nicht mit der Zeit; `test_the_counter_source_is_registered_and_removed_again` | **UMGESETZT** |
| §1.1 O-05 | Failure Isolation | `TestObserverFailureDoesNotAffectTheClient`, `TestDeadWorkerDoesNotAffectTheClient`, `TestAdapterFailureIsolation`, `test_a_throwing_source_is_counted_and_does_not_break_the_worker` | **UMGESETZT** |
| §1.1 O-06 | Struktur statt Textparsing; `message` wird nie zurückgeparst | kein Hook liest `message`; `message` wird nur geschrieben | **UMGESETZT** |
| §1.1 O-07 | `producer_kind`/`channel`/`level`/`type` bleiben vier getrennte Dimensionen | keine neuen Channels; `test_each_wrapper_sets_its_own_channel` | **UMGESETZT** |
| §1.1 O-08 | Replay Safety | `test_replayed_event_is_marked_and_ranks_as_low`, Dedupe-Nachweis, Probe P-2 | **UMGESETZT** |
| §1.1 O-09 | Secrets werden nie persistiert | R-6-Whitelist am echten hello; Probe P-6 prüft jede Zeile der echten DB; `test_no_session_hook_leaks_the_access_token` | **UMGESETZT** |
| §1.1 O-10 – O-13 | Query Independence, Extensible Boundaries, Admin Separation, Control-Plane-Trennung | keine Query-/Admin-/Control-Änderung in OBS-040; `test_v1_still_does_not_create_the_modules_arch_51_excludes` | **NICHT BERÜHRT** |
| §1.2 O-14 | Schreibmonopol Ingress → Worker → Store | der Adapter schreibt nie selbst; alles geht über `submit`; der Worker schreibt seine eigenen Records direkt (G-6, wie OBS-030) | **UMGESETZT** |
| §1.3 | Ein Logging-Fehler wird **niemals** über `report_local_feedback`, `CanonicalEventType` oder die `FeedbackEngine` gemeldet | `test_the_logging_core_never_reaches_the_feedback_domain` (AST-Prüfung über alle Module unter `core/observability/`) | **UMGESETZT** |
| §3.4 | `activation_id` nur aus `envelope.data.activationId`, nie geraten, nie zum Gruppieren | Normalizer unverändert; der Client-Hook `trigger.ack_received` übernimmt `activationId` **aus dem Ack**, also aus einer Serverangabe, und markiert nichts als autoritativ | **UMGESETZT** |
| §5.1 | Modulstruktur eingefroren, inkl. `adapters/client_events.py` und `adapters/server_live.py` | beide angelegt; `TestFrozenModuleStructure` (3 Tests, 8 Subtests) | **UMGESETZT** |
| §5.2 | Importrichtung; `adapters` kennen `ingress` + `normalizer`, nicht umgekehrt; `core/**` importiert nie PySide6 | `TestLayeringAndImportDirection` (4 Tests, über 100 Subtests) | **UMGESETZT** |
| §6.1 | sechs reale Producer-Threads | Hooks liegen auf Qt-Thread (`ui/**`), asyncio-Core (`stt_session`, `controller`, `session_coordinator`, `event_stream`), LED-Thread (`led_feedback._dispatch`), Injection-Worker (`text_injector._worker_loop`), PortAudio-Pfad **nur Zähler** | **UMGESETZT** |
| §6.2 | Lebenszyklus: Manager in `app.py::main()`, `DesktopApplication` bekommt ihn übergeben und stoppt ihn **nicht** | `app.py` übergibt den **Ingress** an `run_gui`; der Manager bleibt in `main()`s `try/finally`. Die Übergabe des **Managers** bleibt OBS-050 (N-4), weil erst dort etwas davon gebraucht wird | **UMGESETZT, mit benannter Restaufgabe** |
| §6.3 | Nichtblockierungs-Invariante | unverändert aus OBS-020; `test_a_full_queue_never_blocks_a_producer` | **UMGESETZT** |
| §6.4 | kein `QueueHandler`, keine Änderung an `setup_logging`, kein Anfassen der Audio-/LED-/Injection-Queues, kein Thread je Sink | `core/logging_setup.py` unverändert; keine Queue umgebaut; `text_injector` bekam **keinen** Timeout und **keinen** Timer | **UMGESETZT** |
| §7.1 – §7.3 | eine Queue, Wasserstandsregel, Prioritätsregel inkl. `not replayed`, eingefrorener Zählersatz | unverändert; `test_the_health_snapshot_has_exactly_the_frozen_fields`, `test_replayed_low_records_are_dropped_above_the_watermark` | **UMGESETZT, Zählersatz unverändert** |
| §8.1 G-1 – G-7 | Rekursionssperren | unverändert aus OBS-020/030; `emit_record_rejected` benutzt **keinen** `logger`, sondern nur `submit` und kann daher keine Rekursion öffnen | **UMGESETZT** |
| §8.2 | Redaction: clienterzeugte Records im Producer, `raw` im Worker; `raw` nicht kopiert | `test_raw_is_the_frozen_reference_and_is_not_copied`; Worker `_prepare_record` unverändert | **UMGESETZT** |
| §8.3 Zeile „Normalizer-Ausnahme" | Record verworfen, **ein** Ersatzrecord `logging.record_rejected` mit Komponente und Ausnahmetyp, **ohne** Originaldaten, Health bleibt `OK`, `malformed++` | `ingress.emit_record_rejected`; `test_adapter_emits_exactly_one_record_rejected_without_original_data`, `test_ingress_guard_reports_a_throwing_normalizer` | **UMGESETZT (neu, Befund N-1)** |
| §8.3 übrige Zeilen | Store/Sink/Queue/Worker-Fehlerfälle | unverändert aus OBS-030 | **NICHT OBS-040** |
| §8.5 GRENZE 1 | der Hook sieht jedes **validierte** Ergebnis, nicht jedes Frame; Gegenmaßnahme ist der zweite Beobachtungspunkt | `TestProtocolErrorObservationPoint` (3) | **UMGESETZT** |
| §8.5 GRENZE 2 | Verhaltensgleichheit, nicht Latenzgleichheit | `test_a_slow_observer_delays_but_does_not_change_the_outcome` dokumentiert die Grenze messend | **DOKUMENTIERT** |
| §8.5 GRENZE 3 | toter Worker verliert Records; `RotatingFileHandler` bleibt die Rückfallebene | `test_a_failed_worker_makes_submit_return_false_but_nothing_else`; `core/logging_setup.py` unverändert | **UMGESETZT** |
| §8.5 GRENZE 4 | harter Prozessabbruch verliert die Queue | unverändert | **NICHT OBS-040** |
| §8.6 | Hot-Path-Regeln inkl. Quelltextnachweis | `test_no_hot_path_function_touches_the_observation_boundary` über alle neun genannten Funktionen; die Aggregatfelder `chunks_captured`, `chunks_dropped_capture_queue`, `chunks_dropped_send_queue`, `bytes_sent`, `packets_sent`, `overflow_count`, `underflow_count`, `max_send_queue_depth` sind alle vorhanden | **UMGESETZT** |
| §8.7 | Handler-Level für Python-Logs, Ingress-Level für strukturierte Events, ein Konfigwert speist beide | unverändert; zusätzlich prüft `test_the_ingress_level_still_filters_the_debug_aggregate`, dass das DEBUG-Aggregat den Ingress-Level respektiert | **UMGESETZT** |
| §9 | ein werfender Beobachter beeinflusst weder Cursor-Commit noch Verbindungsrecycling | **N-07**, Probe P-3 | **UMGESETZT** |
| §10.1 | der Core sieht den Session-Log-Token auch nicht indirekt | `test_the_logging_core_never_reads_the_session_log_token` (AST, Attributzugriffe) | **UMGESETZT** |
| §10.2 – §10.9 | Zukunftsgrenzen Teil B | nichts vorgezogen; `test_v1_still_does_not_create_the_modules_arch_51_excludes` | **NICHT BERÜHRT** |
| §11.1 / §11.2 | was V1 nicht baut / was gestrichen ist | kein Ringbuffer, keine zweite Queue, kein `ProviderCapabilities`, kein Text-Sink, keine aktive Größenbremse, keine `host`/`process_id`-Spalte (`process_id` steht in `details` von `client.app.started`, FD-C3) | **EINGEHALTEN** |
| §11.4 | V1 repariert nicht gleichzeitig die Triggerarchitektur | kein fachlicher Umbau; Ausnahme laut §11.4 sind „ausschließlich minimale, rein beobachtende Hooks" | **EINGEHALTEN** |
| §12 | Baseline-Regel: vollständige bestehende Suite grün, **ohne** dass ein bestehender Test geändert wird | 958 passed / 1 vorbestehender Fehlschlag; `git status --short` zeigt keine geänderte Testdatei | **UMGESETZT** |

## 3. `LOGGING_CONTRACTS_FREEZE_V1.md`

| § | Vorgabe | Umsetzung / Nachweis | Status |
|---|---|---|---|
| §1.1 / §1.4 | Feldliste und Sollzustand | unverändert; `client.*`-Records tragen nie `event_id` (Serverfeld) — geprüft in Probe P-4 und `test_final_...` | **EINGEHALTEN** |
| §1.3 | vollständige `scope`-Ableitung | unverändert; `test_control_frame_without_session_is_scope_instance` | **EINGEHALTEN** |
| §1.5 | Prioritätsableitung | unverändert; `is_internal` nur für logging-eigene Records — das Audio-Aggregat setzt es bewusst **nicht** (`test_the_worker_reads_the_registered_counters`) | **EINGEHALTEN** |
| §2.1 / §2.2 | geschlossene vs. offene Wertemengen, Channels klein | keine neuen Channels; alle neuen `type`-Werte im offenen Namensraum | **EINGEHALTEN** |
| §3.1 | Python-`LogRecord`-Pfad, `session_id` nur aus `record.__dict__` | unverändert (FD-R8) | **NICHT OBS-040** |
| §3.2 | Server-/Controlabbildung | `SERVER_EVENT_MAPPING.md`, 22 Tests | **VERDRAHTET UND GEPRÜFT** |
| §3.3 | Reihenfolge je Pfad, Redaction am Ende | unverändert | **NICHT OBS-040** |
| §4.1 / §4.2 R-1 – R-12 | Redaction | unverändert; R-6 am echten hello geprüft; R-10 in `client.final.deduplicated` **verschärft** (kein Text, nur Zeichenzahl); R-8 wirkt auf `details` aller neuen Hooks | **EINGEHALTEN** |
| §4.3 P-8 / P-9 / M-11 | Dateirechte | unverändert aus OBS-030 | **NICHT OBS-040** |
| §5 | SQLite-Store | unverändert; die Probe schreibt in einen echten Store und liest mit `PRAGMA query_only = ON` | **NICHT OBS-040** |
| §6 | Ingress- und Client-Observation-API, Verdrahtung, Konstruktorinjektion statt Singleton, kein Eventbus | `test_the_ingress_keyword_is_optional_everywhere` (12 Subtests), `test_the_controller_stores_the_ingress_under_the_frozen_name`, `test_a_default_controller_observes_nothing`, `test_null_ingress_answers_the_full_obs040_surface` | **UMGESETZT** |
| §7.1 – §7.5 | Fan-out-Hook, Begründung, Fehlerbehandlung, verbotene Stellen, Protokollfehler | 18 Tests in `test_obs040_fanout_hook.py` | **UMGESETZT** |
| §8 | Query-Verträge | unverändert, nichts implementiert | **NICHT OBS-040** |
| §9 | UI-Verträge (LogWindow, Logging-Tab) | nichts implementiert | **NICHT OBS-040 (OBS-050)** |
| §10.1 – §10.5 | Konfiguration | unverändert; OBS-040 hat **kein** Konfigfeld hinzugefügt | **NICHT OBS-040** |
| §10.4 | eine reine Observability-Änderung setzt keines der Flags `session_changed`/`audio_changed`/`mode_changed` | `test_runtime_apply_carries_the_three_flags_and_the_correlation` prüft die drei Flags am Record; die dort verlangte Zeile `self.observability.apply_config(...)` gehört zu OBS-050 (es gibt in V1 kein `apply_config`) | **TEILWEISE – siehe Punkt 5** |
| §11.1 / §11.2 | Sink- und Health-Verträge | unverändert; Snapshotform per Test fixiert | **EINGEHALTEN** |
| §12 | V1-Observation-Hooks | `OBSERVATION_HOOK_MATRIX.md` | **UMGESETZT** |
| §13 | Wiederverwendung statt Neuerfindung | `setup_logging` unverändert; der `extra`-Vertrag unverändert; `EventEnvelope`/`EventProtocolResult`/`EventProtocolProcessor` unverändert; `CoreBridge`-Muster für den Thread→Qt-Übergang unverändert; die Antimuster aus `TranscriptHistoryManager` nicht übernommen | **EINGEHALTEN** |

## 4. `LOGGING_DECISIONS_FREEZE_V1.md`

| Entscheidung | Status in OBS-040 |
|---|---|
| FD-N1/OD-01 Paketname `observability` | eingehalten; die zwei neuen Module liegen unter `core/observability/adapters/` |
| FD-C1 – FD-C12 | Datenmodell unverändert; `process_id` in `details` von `client.app.started` (FD-C3), `transcription_id` aus dem Envelope übernommen (FD-C1), `activation_id` als diagnostisch (FD-C2), `raw` als Objekt oder gar nicht (FD-C11/C12) |
| FD-D1 – FD-D9 | Defaults unverändert; FD-D2 (`raw` außer Channel `performance`) am echten Event geprüft; FD-D5 (hello nur Whitelist) am echten hello geprüft |
| FD-S1 – FD-S4 | kein Ringbuffer, eine Queue, kein `ProviderCapabilities`, `clear()` unverändert am Store |
| FD-R1/OD-19 replayte Records sind LOW | geprüft und messend belegt |
| FD-R2/OD-20 `LOGGER_CHANNEL_MAP` | unverändert |
| **FD-R3/OD-21 zweiter Beobachtungspunkt, in OBS-040** | **umgesetzt** |
| FD-R4/OD-22 Lebensdauer des Managers | eingehalten; der Ingress reist, der Manager bleibt in `main()` |
| FD-R5/OD-23 Zähler `deduplicated` | unverändert; Probe P-2 zeigt ihn steigen |
| FD-R6 `scope` für `led`/`other` | unverändert |
| FD-R7 `component` bei Controlframes fest `eventstream` | geprüft |
| FD-R8 Herkunft von `session_id`/`generation` bei Python-Logs | unverändert; die neuen Hooks benutzen die **strukturierte** API, genau wie FD-R8 es begründet |
| FD-B1 – FD-B5 Teil B | nichts vorgezogen; `producer_kind="led"` bleibt die Vorkehrung, ein `LedAdapter` entsteht nicht |
| W-9 korrigierte Duplikat-Erwartung | umgesetzt und geprüft |
| W-14 Redaction-Ort | eingehalten |

## 5. Offene Punkte, die **nicht** OBS-040 gehören

| Punkt | Fundstelle | Zuständig |
|---|---|---|
| `self.observability.apply_config(candidate.logging.observability)` in `apply_runtime_config` | `CONTRACTS §10.4` | **OBS-050.** In V1 existiert kein `apply_config` auf dem Ingress, und §10.3 weist die zugehörigen Settings-Einträge dem sechsten Tab zu — also OBS-050. OBS-040 hat die Methode **nicht** erfunden; die harte Regel aus §10.4 (keine Reconnect-Flags durch eine Observability-Änderung) ist trotzdem schon als Record beobachtbar. |
| Übergabe des **Managers** an `DesktopApplication` | `ARCH §6.2(b)`, Gate-Befund N-4 | **OBS-050** (Statuszeile im LogWindow, „Diagnosehistorie löschen") |
| Logging-Tab, LogWindow, `query/local.py`, `query/service.py` | `CONTRACTS §8`, `§9`, `ARCH §5.1` | **OBS-050** |
| `_consecutive_loop_failures` wird von den zwei Guards vor der Workerschleife mitgezählt | Gate-Befund N-2 | **OBS-060** (unverändert übernommen) |
| `app.py::main()`: Manager/`setup_logging` liegen vor dem `try` | Gate-Befund N-3 | **OBS-060** (unverändert übernommen) |
| W-3-Lücke aus dem OBS-030-Gate | OBS-030-Gate-Review | **OBS-060** |
| Lauf gegen den echten Server | – | **OBS-060**, manuelle Abnahme |
| Verzeichnisschreibweise `prompts/` vs. `Prompts/` | Gate-Befund N-5 | organisatorisch; dieser Run hat den bestehenden versionierten Pfad `30_AUSFUEHRUNG/runs/` benutzt und keine zweite Schreibweise erzeugt |

## 6. Zur Zeile „`lefx.*`-Normalizer-Regel scharf schalten"

Das Work Package führt sie im Scope: *„sie **beweist** die Erweiterbarkeit des
Producer-Modells, ohne dass ein Adapter entsteht."*

Befund: die Regel ist **bereits scharf** und war es vor diesem Run.
`normalizer.from_log_record` bildet jeden Loggernamen mit Präfix `lefx.` auf
`producer_kind="led"` / `producer_id="respeaker-led-controller"` /
`component=<loggername>` ab (OBS-010, gate-geprüft), und seit OBS-020 läuft
dieser Pfad im echten `UnifiedLogHandler` am Root-Logger — LEFX läuft
in-process und seine Records erreichen den Root-Logger ohnehin (FD-B5).
OBS-040 musste dafür **nichts** ändern und hat nichts geändert; ein Eingriff
wäre eine Änderung an einem gate-abgenommenen Pfad ohne Anlass gewesen. Die
zugehörigen Tests aus OBS-010 (`tests/test_obs010_normalizer_python.py`) sind
unverändert grün. Ein echter `LedAdapter` bleibt nach FD-B5 Teil B (OBS-140).

## 7. Was dieser Run ausdrücklich **nicht** behauptet

- **Kein Gate-PASS.** Grüne eigene Tests sind laut Work Package und
  `ARBEITSPROZESS.md` kein Fertigstellungsnachweis; das Gate erfordert einen
  separaten Review in frischer Session.
- Kein Lauf gegen den echten Server.
- Keine Aussage über OBS-050-Funktionalität (Query, UI, Settings).
- Keine Änderung an einem normativen Dokument. `00_NORMATIV/` erscheint nicht in
  `git status --short`.
