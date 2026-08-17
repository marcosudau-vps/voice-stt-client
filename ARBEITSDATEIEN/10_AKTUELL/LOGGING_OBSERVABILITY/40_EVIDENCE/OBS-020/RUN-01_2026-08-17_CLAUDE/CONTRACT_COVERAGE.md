# CONTRACT_COVERAGE – OBS-020 RUN-01 (Claude)

Zuordnung: **Anforderung** (normative Quelle) → **Implementierungsstelle** →
**Tests** (Datei::Klasse::Methode).

## 1. Ingress (CONTRACTS §6, ARCH §5/§6.3/§7)

| Anforderung | Implementierung | Tests |
|---|---|---|
| `submit(record) -> bool`, thread-sicher, blockiert nie, wirft nie | `ingress.ObservabilityIngress.submit` | `test_obs020_ingress::TestSubmitPositive`, `TestSubmitNegative`, `TestFailureAndBackpressure::test_submit_never_raises_for_a_wide_input_space` |
| Reihenfolge: Health `FAILED`? → `enabled`/Level? → Wasserstandsregel → `put_nowait` | `ObservabilityIngress.submit` (Implementierungsschritt 1) | `TestFailureAndBackpressure::test_health_failed_state_blocks_submit_before_anything_else`, `TestSubmitNegative::test_disabled_ingress_returns_false_immediately`, `test_level_filter_rejects_below_configured_level` |
| Eine bounded `queue.Queue` (Default 8192), Wasserstandsschwelle 75 % fest | `ingress.DEFAULT_QUEUE_SIZE`, `WATERMARK_RATIO`, `ObservabilityIngress.__init__` | `TestSubmitPositive::test_high_survives_and_low_is_dropped_under_watermark` |
| Prioritätsregel §1.5 inkl. `not replayed` (FD-R1) — Wasserstandsregel muss replayte, typisierte Records verwerfen (N-04) | `models.CanonicalLogRecord.priority` (OBS-010) + `ObservabilityIngress.submit` liest `record.priority` | `test_obs020_ingress::TestSubmitPositive::test_n04_replayed_server_event_with_type_is_dropped_at_watermark` |
| Queue voll → `dropped_queue_full`, kein Wurf | `ObservabilityIngress.submit` (`queue.Full`-Fang) | `TestFailureAndBackpressure::test_queue_full_returns_false_and_counts_without_raising` |
| `NullIngress` verhaltensgleiches No-Op, `NULL_INGRESS`-Modulkonstante | `ingress.NullIngress(ObservabilityIngress)` | `TestNullIngressIsBehaviorallyEquivalent` (alle Methoden) |
| `drain(max_items, timeout)` für den künftigen Worker | `ObservabilityIngress.drain` | `TestDrain` |
| `observe_server_result`/`event` rufen den Normalizer und `submit`, werfen nie nach außen | `ObservabilityIngress.observe_server_result`/`.event` | `test_obs020_contracts::TestIngressSignatures`; End-zu-Ende über `event()`/`observe_server_result()` in `TestNullIngressIsBehaviorallyEquivalent::test_event_and_observe_server_result_are_no_ops` |
| Nichtblockierungsnachweis (ARCH §6.3): 100 000 Submits bei voller Queue, Zeit im ersten Lauf festgeschrieben | `ObservabilityIngress.submit` | `test_obs020_ingress::TestConcurrencyAndTiming::test_100000_submits_against_a_full_queue_timing_baseline` (siehe TEST_RESULTS.md Abschnitt 4) |
| Acht Threads × 5000 Submits: Zähler gehen exakt auf, keine Duplikate | `LoggingInternalHealth`-Zähler unter einem Lock + `ObservabilityIngress.drain` | `TestConcurrencyAndTiming::test_eight_threads_5000_submits_counts_reconcile_no_duplicates` |

## 2. Health (CONTRACTS §11.2, ARCH §7.3/§8)

| Anforderung | Implementierung | Tests |
|---|---|---|
| Zustandsmenge `OK, DROPPING, DEGRADED_SINK, DEGRADED_STORE, FAILED_STORE, FAILED_WORKER, DISABLED` | `health.LoggingHealthState` | `test_obs020_health::TestHealthSnapshotShape::test_state_enum_has_frozen_seven_values` |
| `LoggingHealthSnapshot` mit allen Zählern inkl. `deduplicated` (FD-R5) | `health.LoggingHealthSnapshot` (frozen dataclass) | `test_fresh_health_is_ok_with_zeroed_counters` |
| Alle Zähler unter **einem** Lock | `LoggingInternalHealth.__init__` (`self._lock`), jede `record_*`-Methode | `TestCounters::test_counters_are_thread_safe_under_contention` |
| `is_failed()` nur für `FAILED_STORE`/`FAILED_WORKER` | `LoggingInternalHealth.is_failed` | `TestHealthSnapshotShape::test_is_failed_true_only_for_failed_states` |
| Emergency-Ausgang: eigener Logger `observability.internal`, `propagate=False`, `StreamHandler(sys.stderr)` (G-2) | `health._build_emergency_logger`, `_EmergencyStreamHandler` | `TestEmergencyLoggerContract` (beide Dateien: `test_obs020_health.py`, `test_obs020_contracts.py`) |
| Ratenbegrenzung: höchstens eine Zeile je Code und 60 s, Wiederholungszähler, unabhängig von der Fehlerzahl (G-4) | `health._RateLimiter`, `health.emergency` | `TestEmergencyRateLimit::test_burst_of_2000_within_one_second_yields_at_most_one_line`, `test_repeat_counter_reflects_suppressed_occurrences`, `test_different_codes_have_independent_windows` |
| `sys.stderr is None` abgefangen | `_EmergencyStreamHandler.emit` (liest `sys.stderr` dynamisch, `None`-Check) | `TestEmergencyNeverRaises::test_stderr_is_none_does_not_raise`, `test_counters_keep_incrementing_even_when_stderr_is_broken` |
| `sys.stderr.write` wirft → keine Ausnahme | `_EmergencyStreamHandler.emit`/`handleError` (drei Schutzebenen) | `TestEmergencyNeverRaises::test_stderr_write_raising_does_not_raise` |

## 3. Python-Logging-Handler (CONTRACTS §3.1/§6, ARCH §8.1)

| Anforderung | Implementierung | Tests |
|---|---|---|
| Eine `logger.info`-Zeile → genau ein Record mit korrektem `component`/`channel`/`level` | `python_logging.UnifiedLogHandler.emit` | `test_obs020_python_logging_handler::TestPositive::test_one_log_line_produces_exactly_one_record_with_correct_fields` |
| `exc_info` als Text in `details["exception"]`; `record.args` nirgends | `normalizer.from_log_record` (OBS-010) über den Handler | `TestPositive::test_exc_info_lands_as_text_and_args_appear_nowhere` |
| Vier bestehende `extra`-Felder übernommen | `from_log_record` über den Handler | `TestPositive::test_four_extra_fields_are_carried_through` |
| `submit(None)`/Fremdtyp | `ObservabilityIngress.submit` | `test_obs020_ingress::TestSubmitNegative` |
| `%`-Formatfehler, werfendes `extra.__str__`, namenloser Thread → kein Wurf | `UnifiedLogHandler.emit` (Normalizer fängt intern, Handler fängt zusätzlich) | `TestNegative` (drei Methoden) |
| `enabled=False` → `submit` sofort `False`, nichts gebaut | `ObservabilityIngress.submit` | `test_obs020_ingress::TestSubmitNegative::test_disabled_ingress_returns_false_immediately` |
| Ingress liefert immer `False` → keine Ausnahme, kein stderr je Zeile | `UnifiedLogHandler.emit` (kein `handleError`-Aufruf bei regulärem `False`) | `TestFailure::test_ingress_always_false_no_exception_no_stderr` |
| Normalizer wirft → `handleError` zählt, Anwendung läuft weiter | `UnifiedLogHandler.emit`/`.handleError` | `TestFailure::test_normalizer_raising_routes_through_handle_error_and_continues` |
| Rekursionstest: Fehler über `logging` gemeldet → Anzahl erzeugter Records bleibt begrenzt | `threading.local`-Wiedereintrittssperre (G-1) | `TestFailure::test_reentrant_logging_call_during_emit_stays_bounded` |
| 2000 Fehler in 1 s → ≤ 1 stderr-Zeile, Wiederholungszähler stimmt | `health._RateLimiter` | `test_obs020_health::TestEmergencyRateLimit::test_burst_of_2000_within_one_second_yields_at_most_one_line` |
| `logging.shutdown()`-Äquivalent (`flush`+`close`) wartet nicht auf den Worker (N-03) | `UnifiedLogHandler.flush`/`.close` als No-Ops (G-7) | `TestFlushCloseAreNoOps` (beide Methoden) |
| Doppelter `setup_logging`-Aufruf → genau ein `UnifiedLogHandler` | `root_logger.handlers.clear()` (bestehend, unverändert) + additive Handler-Erzeugung | `test_obs020_logging_setup_integration::TestObservabilityWiring::test_double_setup_logging_call_yields_exactly_one_unified_handler` |
| Datei-/Stdout-Ausgabe zeilenweise identisch zum Zustand vor der Änderung | `core/logging_setup.py` — Funktionskörper byte-identisch, nur additiv erweitert | `TestBackwardCompatibility::test_file_and_stdout_output_identical_with_and_without_observability`; Diagnoseskript (Evidence, altes vs. neues Modul) |
| Ohne `observability`-Parameter verhält sich `setup_logging` exakt wie heute | `core/logging_setup.py` (`if observability is not None:`-Zweig) | `TestBackwardCompatibility::test_without_observability_param_behaves_exactly_as_before` |

## 4. Rekursionssperren G-1..G-7 (ARCH §8.1)

| Sperre | Implementierung | Tests |
|---|---|---|
| G-1 Wiedereintrittssperre (`threading.local`) | `UnifiedLogHandler.emit` | `test_obs020_python_logging_handler::TestFailure::test_reentrant_logging_call_during_emit_stays_bounded` |
| G-2 eigener, nicht propagierender Logger `observability.internal` | `health._build_emergency_logger` | `test_obs020_health::TestEmergencyLoggerContract`, `test_obs020_contracts::TestEmergencyLoggerContract` |
| G-3 `handleError` meldet an Health, nicht an stderr | `UnifiedLogHandler.handleError` → `LoggingInternalHealth.record_malformed` | `TestFailure::test_normalizer_raising_routes_through_handle_error_and_continues`, `test_submit_raising_is_caught_via_handle_error` |
| G-4 harte Ratenbegrenzung, 1 Zeile/Code/60s, Wiederholungszähler | `health._RateLimiter`/`emergency` | `test_obs020_health::TestEmergencyRateLimit` (drei Tests) |
| G-5 kein Logging-Fehler über den Feedbackweg | `health.py` importiert weder `core.event_models` noch `core.feedback_reducer` | `test_obs020_contracts::TestModuleIsolation::test_health_imports_neither_event_models_nor_feedback_reducer` |
| G-6 `logging.records_dropped`/`logging.recovered` schreibt der Worker direkt | Worker existiert erst in OBS-030 — nur die Vorbedingung (Health-Zähler vorhanden) ist hier erfüllt | `test_obs020_health::TestHealthSnapshotShape::test_fresh_health_is_ok_with_zeroed_counters` (Zähler-Shape) |
| G-7 `flush()`/`close()` No-Ops | `UnifiedLogHandler.flush`/`.close` | `test_obs020_python_logging_handler::TestFlushCloseAreNoOps` |

## 5. Redaction — Erhalt der OBS-010-Garantien durch die neue Pipeline

| Anforderung | Implementierung | Tests |
|---|---|---|
| Redaction von Secrets (R-3) end-to-end durch Ingress/Handler | `UnifiedLogHandler` ruft ausschließlich `from_log_record` (OBS-010), keine Umgehung | `test_obs020_redaction_end_to_end::TestSecretsAreRedactedEndToEnd` (zwei Fälle) |
| Erhalt nicht-sensibler Struktur | dieselbe Pipeline | `TestNonSensitiveStructureIsPreserved` |
| Audio-Payload-Abwehr | Hot-Path-Audiofunktionen referenzieren den Ingress nicht (Quellcode-Nachweis) + Abwehrtest für fehlgeleiteten Byte-Payload | `TestAudioPayloadIsNeverReachable` (zwei Tests) |
| Transkript-Policy (R-10), beide Richtungen | `store_transcription_content`-Weiterreichung von `ObservabilityIngress`/Handler-Normalizer an `from_log_record` | `TestTranscriptPolicyEndToEnd` (drei Tests) |
| Keine Mutation von Eingangsdaten | `redact_mapping` baut neue Struktur (OBS-010); hier end-to-end bestätigt | `TestNoMutationOfInputData` |

Details und konkrete Vorher-/Nachher-Beispiele: siehe `REDACTION_CASES.md`.

## 6. Schichtung/Isolation (ARCH §5.2)

| Anforderung | Implementierung | Tests |
|---|---|---|
| `core/**` importiert nie `PySide6` | neue OBS-020-Dateien enthalten keinen `PySide6`/`QtCore`-Bezug | `test_obs020_contracts::TestModuleIsolation::test_no_pyside6_or_qtcore_in_new_obs020_modules` |
| `ingress.py` importiert kein `sqlite3` | `ingress.py` | `test_ingress_module_does_not_import_sqlite3` |
| Handler hält keine Laufzeitreferenzen (Controller/Session/Coordinator) | `adapters/python_logging.py` | `test_python_logging_handler_holds_no_runtime_references` |
| Azyklische Importe aller neuen Module in frischem Interpreter | — | `TestAcyclicImports::test_every_obs020_module_imports_in_a_fresh_interpreter` |
| `Ingress`-Protocol-Signatur (OBS-010) ↔ `ObservabilityIngress.event` (OBS-020) deckungsgleich | `ingress.py` | `TestIngressSignatures::test_event_signature_matches_frozen_ingress_protocol` |

## 7. Run-/Evidence-Auflagen des Auftrags

| Auflage | Erfüllt durch |
|---|---|
| Run-Ordner `RUN-OBS-020-01_2026-08-17_CLAUDE` mit RUN_LOG.md/RESULT.md | `30_AUSFUEHRUNG/Runs/RUN-OBS-020-01_2026-08-17_CLAUDE/` |
| Evidence `40_EVIDENCE/OBS-020/RUN-01_2026-08-17_CLAUDE`: TEST_RESULTS.md, DIFF_SUMMARY.md, CONTRACT_COVERAGE.md, REDACTION_CASES.md | vorhanden |
| Diagnoseskript: Vorher/Nachher-Vergleich `client.log` | `OBS-020_RUN-01_client_log_before_after_diagnose.py` (Exit 0) |
| Steuerungsdateien | `CURRENT_STATE.md`, `LOG_VERLAUF.md` aktualisiert |
| keine bestehende Produktdatei außer der additiv erlaubten / kein bestehender Test geändert | DIFF_SUMMARY.md |
