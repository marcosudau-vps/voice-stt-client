---
id: EV-OBS-040-HOOK-MATRIX
run: RUN-OBS-040-01_2026-08-17
work_package: OBS-040
authority: evidence
date: 2026-08-17
---

# OBS-040 – Observation-Hook-Matrix

Vollständige Gegenüberstellung von `LOGGING_CONTRACTS_FREEZE_V1.md §12` und dem
tatsächlichen Code. Legende wie in §12: `P` = bestehende Python-Logzeile
genügt, `S` = zusätzliches strukturiertes Event, `P+S` = beides, wobei die
bestehende `logger.*`-Zeile **nicht** entfernt und **nicht** umformuliert wird.

Spalte „Status": `S umgesetzt` = strukturierter Record vorhanden;
`P – nichts zu tun` = laut §12 genügt die bestehende Logzeile, die der
UnifiedLogHandler aus OBS-020 ohnehin erfasst.

## §12.1 Lifecycle und Transport – Channel `system`

| Typ | §12-Ort | Art | Implementiert in | Status |
|---|---|---|---|---|
| `client.app.started` | `ui/application.py` `start()` | S | `ui/application.py::DesktopApplication.start` | S umgesetzt; `process_id` in `details` nach FD-C3 |
| `client.app.stopping` | `ui/application.py` `shutdown()` | S | `ui/application.py::DesktopApplication.shutdown` | S umgesetzt; erste Anweisung des Teardowns |
| `client.core.thread_started` / `.thread_stopped` | `ui/core_bridge.py` | P+S | `ui/core_bridge.py::_thread_main` | S umgesetzt; bestehende `logger`-Zeilen unverändert |
| `client.controller.run_started` | `core/controller.py` `run()` | S | `core/controller.py::run` | S umgesetzt; **nach** `start_queue()` |
| `client.controller.shutdown_*` | `core/controller.py` `_do_shutdown` | P | – | P – nichts zu tun; die fünf `logger.error`-Zeilen in `_do_shutdown` sind unverändert |
| `client.websocket.connecting` / `.connected` / `.disconnected` | `core/stt_session.py` `_update_transport`, `_record_failure` | P+S | `_fire_transport_change` (connecting/connected), `_record_failure` (disconnected) | S umgesetzt; **benannte Abweichung**, siehe Anmerkung A-1 |
| `client.session.admitted` | `core/stt_session.py` `_wait_for_hello` | P+S | `core/stt_session.py::_wait_for_hello` | S umgesetzt; trägt den effektiven Handshake-Vertrag, **nie** den hello-Payload (R-6) |
| `client.session.ready` | `core/stt_session.py` `_wait_for_ready` | S | `core/stt_session.py::_wait_for_ready` | S umgesetzt |
| `client.reconnect.scheduled` | `core/stt_session.py` | P+S | `core/stt_session.py::run` (Backoff-Zweig) | S umgesetzt; trägt das berechnete Delay |
| `client.eventstream.state_changed` | `core/session_coordinator.py` `_handle_state` | S | `core/session_coordinator.py::_handle_state` | S umgesetzt; nur bei echtem Übergang, **nach** `_set_context` |
| `client.eventstream.gap` / `.error` / `.replay_completed` | über den Fan-out-Hook | S | Normalizer-Controlpfad (`CONTRACTS §3.2`), ausgelöst durch `_notify_observer` | S umgesetzt; kommt vollständig aus dem Fan-out, ohne eigene Aufrufstelle |
| `client.eventstream.protocol_error` | `core/event_stream.py` `run()`, except-Zweig | S | `core/event_stream.py::run` → `_observe_protocol_error` | S umgesetzt; **eine** Zeile, kein zusätzlicher Kontrollfluss, ohne Rohframe |
| `client.config.validation_failed` | `core/config.py`, `ui/settings_dialog.py` | P+S | `ui/settings_dialog.py::apply_changes`, `core/controller.py::apply_runtime_config` | S umgesetzt an zwei Stellen; **benannte Lücke**, siehe A-2 |
| `client.config.loaded` | `core/config.py` | P (Pfade nach R-9) | – | P – nichts zu tun; `core/config.py` unverändert |

## §12.2 Absichtliche Handlungen – Channel `audit`

| Typ | §12-Ort | Art | Implementiert in | Status |
|---|---|---|---|---|
| `client.hotkey.pressed` | `ui/hotkeys.py` — *heute völlig ungeloggt* | S | `ui/hotkeys.py::dispatch_hotkey_id` | S umgesetzt; **vor** dem Callback, trägt die Aktion, nicht die Tastenkombination |
| `client.command.requested` / `.completed` | `ui/core_bridge.py`, gemeinsame `correlation_id` | S | `ui/core_bridge.py`, alle vier Einreichpfade | S umgesetzt; `command_id` + `correlation_id="command:<cmd>"` |
| `client.trigger.sent` | `core/stt_session.py` `send_trigger` | P+S | `core/stt_session.py::send_trigger` | S umgesetzt; **nach** dem Senden |
| `client.trigger.ack_received` | `core/stt_session.py` `_resolve_trigger_ack` | S | `core/stt_session.py::_resolve_trigger_ack` | S umgesetzt; nur für die **erste** Antwort |
| `client.trigger.ack_dropped` | `core/stt_session.py` | P+S | `core/stt_session.py::_observe_ack_dropped`, drei Aufrufstellen | S umgesetzt; `missing_command_id`, `unknown_or_answered`, `stale_generation` |
| `client.stream.start_sent` | `core/stt_session.py` | P+S | `core/stt_session.py::send_start` | S umgesetzt |
| `client.dictation.start_attempt` / `.confirmed` / `.failed` | `core/controller.py` | S | `_begin_start_locked`, `_await_start_attempt`, `_emit_feedback_event` | S umgesetzt; alle drei |
| `client.dictation.interrupted` | `core/controller.py` | P+S | `core/controller.py::_emit_feedback_event` | S umgesetzt; das bestehende `logger.warning` in `_handle_dictation_interrupted` bleibt |
| `client.settings.apply_started` / `.completed` | `ui/application.py`, gemeinsame `correlation_id` | S | `_apply_settings`, `_complete_settings_observation` | S umgesetzt als `.apply_started`/`.apply_completed`; siehe A-3 |
| `client.settings.runtime_apply` | `core/controller.py` `apply_runtime_config`, dieselbe `correlation_id` | S | `core/controller.py::apply_runtime_config` | S umgesetzt; die id reist über ein rein beobachtendes Keyword |
| `client.action.blocked` | `core/controller.py` `_emit_feedback_event` | S | `core/controller.py::_emit_feedback_event` | S umgesetzt |
| `client.audio.stream_started` / `.stream_stopped` | `core/audio_capture.py` | P+S | `core/audio_capture.py::start`/`stop` | S umgesetzt; `.stream_stopped` trägt den Endstand der Zähler |

## §12.3 Transkript – Channel `transcription`

| Typ | §12-Ort | Art | Implementiert in | Status |
|---|---|---|---|---|
| `client.injection.enqueued` / `.rejected` | `core/controller.py` | P+S | `core/controller.py::_observe_final_result` | S umgesetzt; `correlation_id="injection:<entryId>"` |
| `client.final.deduplicated` | `core/controller.py` — **redaktionspflichtig** | P+S | `core/controller.py::_observe_final_result` | S umgesetzt; **kein Text**, nur `text_length` und `conflict` |
| `client.history.persist_failed` | `core/history.py` | P | – | P – nichts zu tun; `core/history.py` unverändert |

## §12.4 Zahlen – Channel `performance`

| Typ | §12-Ort | Art | Implementiert in | Status |
|---|---|---|---|---|
| `client.audio.stream_stats` | **vom Worker** aus Zählern, alle 5 s | S, aggregiert | `core/observability/worker.py::_emit_aggregates_if_due`; Zählerquelle `core/controller.py::_collect_audio_stats` | S umgesetzt; Level `DEBUG`, Channel `performance`, `None` solange nichts streamt |
| `client.queue.state` | Injection-Worker, periodisch | S, aggregiert | `core/text_injector.py::_observe_queue_state` | S umgesetzt; **benannte Auslegung**, siehe A-4 |
| `logging.records_dropped` | vom Worker | S, intern | `worker.py::_check_backpressure_state` (OBS-030) | unverändert vorhanden |
| `logging.recovered` | vom Worker | S, intern | `worker.py::_emit_recovery_record` (OBS-030) | unverändert vorhanden |
| `logging.retention_pressure` | vom Worker | S, intern | `worker.py::_report_retention_pressure` (OBS-030) | unverändert vorhanden |
| `logging.record_rejected` | vom Worker | S, intern | `core/observability/ingress.py::emit_record_rejected`, aufgerufen aus `ingress`, `adapters/server_live.py`, `adapters/python_logging.py` | **neu in OBS-040** (Gate-Befund N-1); siehe A-5 |

## §12.5 Feedback und Ausgabe – Channel `system`

| Typ | §12-Ort | Art | Implementiert in | Status |
|---|---|---|---|---|
| `client.feedback.decision` | `ui/application.py` `_log_feedback_decision` — *bleibt unverändert und wird nur zusätzlich erfasst* | P+S | `ui/application.py::_log_feedback_decision` | S umgesetzt; das bestehende `logger.info` mit seinem `extra`-Block ist **byte-identisch** erhalten |
| `client.led.dispatch_failed` / `.queue_overflow` | `ui/led_feedback.py` | P+S | `_dispatch`, `_enqueue` | S umgesetzt; beide bestehenden `logger`-Zeilen bleiben |
| `client.sound.failed` | `ui/application.py` | P+S | `ui/application.py::_on_sound_failure` | S umgesetzt; nur die Kategorie, nie der volle Key (R-9) |
| `client.server.error_classified` | `core/controller.py` `_handle_error_event` | P+S | `core/controller.py::_handle_error_event` → `_observe_error_classified` | S umgesetzt; siehe A-6 |

## §12.7 Nicht instrumentiert – geprüft

| Vorgabe | Prüfung |
|---|---|
| `app.py`-`print()` im Headless-Modus | `tests/test_obs040_client_hooks.py::test_headless_prints_are_untouched` |
| alle Hot-Path-Funktionen aus `ARCH §8.6` | `tests/test_obs040_hot_path.py::test_no_hot_path_function_touches_the_observation_boundary` über alle neun Funktionen |
| `realtime`-Events: kein strukturierter Record | `test_realtime_events_produce_no_structured_record` |
| Module ohne Logging (`event_models`, `event_protocol`, `event_normalizer`, `feedback_reducer`, `feedback_mapping`, `settings_metadata`, `actions`, `version`) | `test_pure_modules_import_no_observability` (8 Subtests) |

## §12.6 Umsetzungsreihenfolge

Die Reihenfolge nach aufsteigendem Risiko wurde eingehalten und nach jeder Stufe
getestet:

```text
0. core/observability/**            (Adapter, Ingress-Ergänzungen, Worker-Aggregat)
   + core/session_coordinator.py, core/event_stream.py   (Fan-out und §7.5)
1. ui/hotkeys.py, ui/core_bridge.py, ui/application.py,
   ui/led_feedback.py, ui/settings_dialog.py
2. core/audio_capture.py
3. core/stt_session.py
4. core/controller.py, core/text_injector.py
5. app.py                            (Verdrahtung)
```

## Benannte Abweichungen und Auslegungen

**A-1 `client.websocket.*` liegt auf `_fire_transport_change`, nicht auf
`_update_transport`.** §12.1 nennt `_update_transport` und `_record_failure` als
Ort. `_update_transport` delegiert selbst an `_fire_transport_change`; der
Reducerpfad in `_apply_event` ruft `_fire_transport_change` aber **direkt**.
Ein Hook nur in `_update_transport` hätte damit jeden reducergetriebenen
Übergang verloren, `ADMITTED` eingeschlossen — also genau das `connected`-
Ereignis. `.disconnected` liegt dagegen bewusst auf `_record_failure`, weil zwei
Fehlschläge hintereinander den Transportzustand nicht ein zweites Mal ändern und
ein Hook am Zustandsübergang den zweiten Fehlschlag verschluckt hätte. Beide
§12.1-Orte sind damit abgedeckt, und der Hook sieht strikt mehr.
Test: `test_transport_transitions_produce_connecting_and_connected`,
`test_every_failed_connection_produces_one_disconnected_record`.

**A-2 `client.config.validation_failed` entsteht nicht in `core/config.py`.**
§12.1 nennt `core/config.py` und `ui/settings_dialog.py`. Der strukturierte
Anteil ist in `ui/settings_dialog.py` (Dialogvalidierung) und
`core/controller.py::apply_runtime_config` (Kandidatenvalidierung) umgesetzt.
In `core/config.py` selbst ist er **nicht** umsetzbar: `AppConfig.load()` läuft
laut `ARCH §6.2(a)` zwingend **vor** dem Manager (*„Meldungen aus
`AppConfig.load` bleiben verloren — wie heute"*), und ein Modul-Singleton als
Ausweg ist durch `CONTRACTS §6` ausdrücklich verboten
(*„KONSTRUKTORINJEKTION, kein Modul-Singleton"*). Der `P`-Anteil
(`logger.error`) ist dort unverändert vorhanden. **Kein
`DECISION REQUIRED`-Bedarf**: die Vorgabe ist aus dem bestehenden Freeze
auflösbar, weil §6.2(a) den Verlust ausdrücklich als Architektureigenschaft
benennt.

**A-3 Der Recordname lautet `client.settings.apply_completed`.** §12.2 schreibt
*„`client.settings.apply_started` / `.completed`"*. Die Kurzform `.completed`
würde als voller Typ `client.settings.completed` heißen und die Paarung mit
`apply_started` verlieren; die Zeile ist als „apply_started/apply_completed"
gelesen, analog zu `client.injection.enqueued / .rejected` in §12.3, wo die
Kurzform ebenfalls das gemeinsame Präfix teilt. `type` ist nach `CONTRACTS §2.1`
ein **offener** Namensraum, ein neuer Wert löst keine Migration aus.

**A-4 `client.queue.state` ist ereignisgetrieben und ratenbegrenzt, nicht
timergetrieben.** §12.4 sagt „Injection-Worker, periodisch". Der Injection-Worker
blockiert in `queue.get()` **ohne** Timeout. Ihm einen Timeout zu geben, nur
damit Logging ticken kann, wäre eine Änderung des Kontrollflusses eines
fachlichen Pfades für ein Diagnoseaggregat — genau das, was `ARCH §11.4` und
`AGENTS.md` („keine vorsorglichen Refactorings") ausschließen. Umgesetzt ist
daher: ein Record nach jedem Job, höchstens alle 5 s, plus je einer erzwungenen
Zustandsänderung (Worker läuft / Worker gestoppt). Zwischen zwei Jobs ändert
sich die Queuetiefe nicht, ein Timer hätte also Records ohne Information
erzeugt. Test: `test_queue_state_is_aggregated_and_rate_limited`.

**A-5 `logging.record_rejected` ist nur über den Ingress-Wächter erreichbar.**
`ARCH §8.3` verlangt den Ersatzrecord für eine „Normalizer-Ausnahme". Der
Normalizer **wirft konstruktiv nie** (`CONTRACTS §3`: *„Im Zweifel liefert er
`None`"*), weshalb der Pfad in der Praxis nur dann greift, wenn der Normalizer
seinen eigenen Vertrag bricht, oder wenn ein injizierter Ingress/Adapter wirft.
Genau diese drei Stellen rufen ihn jetzt: `ingress.observe_server_result`,
`ingress.event`, `ServerLiveAdapter.observe` und
`UnifiedLogHandler._handle_exception`. Der Record trägt Komponente und
Ausnahmetyp, **nie** Originaldaten, ist `is_internal=True` (also HIGH, damit die
Erklärung der Lücke die Überlast überlebt, in der die Lücke entsteht) und
erhöht `malformed` — Health bleibt `OK`, wie §8.3 es vorschreibt. Tests:
`test_adapter_emits_exactly_one_record_rejected_without_original_data`,
`test_ingress_guard_reports_a_throwing_normalizer`,
`test_a_broken_result_object_produces_no_record_and_no_exception`.

**A-6 `client.server.error_classified` entsteht an genau einer Stelle.**
`_handle_error_event` hat acht Zweige mit eigenem `return`. Der Record wird
einmal erzeugt, unmittelbar nach der Zählung, mit `where`, `count` und
`dictation_state` — das Tripel, aus dem der genommene Zweig deterministisch
rekonstruierbar ist. Acht Aufrufstellen hätten dieselbe Aussage achtfach
formuliert und wären beim nächsten Zweig auseinandergelaufen. Anders als das
bestehende `logger.warning`, das nur für den **unklassifizierten** Rest feuert,
existiert der Record für **jeden** klassifizierten Fehler. Test:
`test_error_classification_is_recorded_with_its_count`.
