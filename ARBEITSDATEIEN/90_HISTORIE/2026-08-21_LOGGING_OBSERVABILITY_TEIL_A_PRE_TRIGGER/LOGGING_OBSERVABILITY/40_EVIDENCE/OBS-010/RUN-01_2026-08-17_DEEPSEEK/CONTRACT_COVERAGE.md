# CONTRACT_COVERAGE – OBS-010 RUN-01 (DeepSeek)

Zuordnung: **Anforderung** (normative Quelle) → **Implementierungsstelle** →
**Tests** (Datei::Klasse::Methode).

## 1. Canonical Record (CONTRACTS §1)

| Anforderung | Implementierung | Tests |
|---|---|---|
| Feldliste exakt nach §1.1/§1.4 (25 Felder + `is_internal`) | `core/observability/models.py::CanonicalLogRecord` | `test_obs010_models::TestModelInvariants::test_all_frozen_fields_match_contract_2020611_table_11`, `test_optional_fields_default_to_none_required_are_present` |
| `details`/`raw` beim Bau eingefroren (Muster `event_models._freeze`) | `models._freeze` in `__post_init__` | `test_details_are_frozen_after_construction`, `test_raw_is_frozen_after_construction`, `test_record_is_frozen_and_details_are_immutable` |
| Eingefrorene Server-Payloads werden nicht kopiert (ARCH §8.2) | `models._freeze` Identity-Branch für `MappingProxyType` | `test_already_frozen_server_payload_is_not_copied_on_build`, `test_obs010_normalizer_server::TestServerEventMapping::test_raw_reference_is_not_copied_eagerly` |
| Prioritätsableitung §1.5 / FD-R1 (`not replayed`) | `models.CanonicalLogRecord.priority` | `test_obs010_models::TestPriorityDerivation` (alle Zweige + `replayed`) |
| Nichts außerhalb der festgelegten Felder (`monotonic_ns`, `host`, …) | Web disallowed names via `test` | `test_all_frozen_fields_match_contract_2020611_table_11` (Negativ-Liste) |

## 2. Wertemengen (CONTRACTS §2.1/§2.2)

| Anforderung | Implementierung | Tests |
|---|---|---|
| `producer_kind`/`scope`/`level` geschlossen | `models.ProducerKind/Scope/Level`, Validierung in `__post_init__` | `TestEnumValueSets`, `TestPfieldValidation` |
| `channel` offen (unbekannte Werte werden gespeichert) | `models.Channel` als kanonische Vier; `normalizer` reicht durch; Model erfordert nur nicht-leeres str | `test_obs010_normalizer_client::TestClientEventNegative::test_channel_unknown_is_stored_not_rejected` |
| `level` einziger geschlossener Fall, INFO-Rückfall + `source_severity` | `normalizer._normalize_level` | `test_obs010_normalizer_server::...::test_unknown_severity_falls_back_to_info_with_source_severity`, `test_severity_critical_maps_to_critical_level` |
| Channels klein; keine zusätzlichen Client-Channels | `models.Channel` | `TestEnumValueSets::test_channel_canonical_four` |

## 3. Normalizer drei Eingänge (CONTRACTS §3)

### 3.1 Python-`LogRecord` (§3.1, FD-R2, FD-R8)

| Anforderung | Implementierung | Tests |
|---|---|---|
| `LOGGER_CHANNEL_MAP` nur `text→transcription`, sonst `system` | `normalizer.LOGGER_CHANNEL_MAP` | `test_logger_channel_map_has_only_text`, `test_text_logger_maps_to_transcription_channel`, `test_any_other_logger_name_is_system` |
| `lefx.*` → `led`/`respeaker-led-controller`, `channel=system` | `normalizer.from_log_record` | `test_lefx_logger_is_led_producer_with_system_channel` |
| `component=record.name`, `type=None`, gerenderte `message` | `from_log_record` | `test_info_record_from_controller_logger`, `test_type_is_none_from_logger_names` |
| die vier bestehenden `extra`-Felder in `details` | `from_log_record` (Schleife über extra-Vertrag) | `test_four_existing_extra_fields_land_in_details` |
| `session_id`/`generation`/`segment_id` NUR aus `record.__dict__` (FD-R8), Signatur bleibt | `from_log_record` (Parameter vorhanden, Quelle `record.__dict__`) | `test_session_and_generation_come_only_from_record_dict`, `test_without_extra_correlation_is_none`; `test_obs010_contracts::...::test_normalizer_imports_no_runtime_objects` |
| `record.created` → ISO-8601 UTC `Z` | `normalizer._from_created` | `test_source_timestamp_is_iso8601_utc_with_z` |
| `exc_info` → `details["exception"]` als TEXT, Formatierfehler wirft nicht | `from_log_record` | `test_exc_info_rendered_into_details_exception`, `test_exc_info_whose_format_raising_does_not_break_record` |

### 3.2 `(SessionContext, EventProtocolResult)` (§3.2, R-6, WD-9)

| Anforderung | Implementierung | Tests |
|---|---|---|
| EVENT-Ergebnisse Feld für Feld (producer `server`, `instance_id`, `channel`, `level`, `type`, `component`=Namensraumpräfix, `session_id`, `generation` aus Context, `activation_id`, `segment_id`, `transcription_id`, `event_id`, `server_cursor`, `scope`) | `normalizer.from_server_result` + `_map_server_event` | `test_obs010_normalizer_server::TestServerEventMapping::test_real_log_event_frame_fields` (echte Frames aus `test_event_protocol`) |
| `message` aus `extra["meldung"]` (Befund C-2) | `_map_server_event` | `test_meldung_from_rest_payload_becomes_message` |
| `activation_id` nur aus `data.activationId` | `_map_server_event` | `test_activation_id_from_data` |
| `replayed = origin is REPLAY` | `_map_server_event` | `test_real_log_event_frame_fields` (replayed True), `test_live_event_is_not_replayed` |
| `scope`: session/global bei Server | `_normalize_scope` | `test_real_log_event_frame_fields` (session), `test_scope_is_global_for_server_event_without_session` |
| `raw = result.payload`; `store_raw_payload=False` → None; `channel=performance` → nie raw | `_map_server_event` | `test_store_raw_payload_false_sets_raw_to_none`, `test_performance_channel_never_keeps_raw` |
| `details` bei fehlendem `data` leer | `_map_server_event` | `test_envelope_without_data_has_empty_details` |
| CONTROL: producer `client`, `channel=system`, `type=client.eventstream.<kind>`, `component=eventstream` (FD-R7), `WARNING` bei error/gap | `_map_control` | `test_obs010_normalizer_server::TestServerControlMapping` (gap, error, pong), `test_duplicate_event_is_mapped_as_control` |
| `log.gap` als eigener Record mit `lostFromCursor`/`lostToCursor` | `_map_control` | `test_gap_controlframe_maps_to_client_eventstream_gap` |
| `log.hello` NIE raw; nur Whitelist R-6; Redaction läuft zusätzlich | `normalizer._hello_whitelist` | `test_hello_controlframe_is_whitelist_only_no_token`; Diagnose-Skript (Evidence) |
| Duplicate-Events als CONTROL (CONTRACTS §3.2 / W-9) | `from_server_result` | `test_duplicate_event_is_mapped_as_control` |
| wirft nie; `result.event None` bei EVENT → None; Control ohne `client_instance_id` → None | `from_server_result` try/except, `_map_control` Guard | `TestServerNormalizerNeverRaises` |

### 3.3 Strukturierte Client-Observation (§6) und §3.3

| Anforderung | Implementierung | Tests |
|---|---|---|
| `Ingress.event(...)`-Signatur exakt (Protokoll) | `ingress.py::Ingress` | `test_obs010_contracts::TestIngressSignature` |
| `from_client_event` mappt Felder/IDs; `scope` session/instance (§1.3) | `normalizer.from_client_event` | `test_obs010_normalizer_client::TestClientEventMapping` |
| ungültige Eingaben → None (kein Wurf): Level außerhalb, `details` kein Mapping, `segment_id` negativ/bool, fehlende `instance_id` | `from_client_event` + Model-Gate | `TestClientEventNegative` |
| Keine Mutation der übergebenen Payloads | Redaction baut neue Struktur; Model friert ein | `test_details_are_not_mutated`, `test_obs010_models::test_details_are_frozen_after_construction`/`test_raw_is_frozen_after_construction` |

## 4. Redaction (CONTRACTS §4, FD-C11, FD-C12)

| Regel | Implementierung | Tests |
|---|---|---|
| `unfreeze()` (`MappingProxyType→dict`, `tuple→list`, `frozenset→sortierte list`) **vor** Serialisierung (FD-C11) | `redaction.unfreeze` | N-01: `test_obs010_redaction::TestUnfreezeN01` (alle), `test_unfreeze_bounds_also_limit` |
| R-3 Schlüsselregel (case-insensitiv, ohne `_`/`-`; verschachtelt in Listen/Dicts) | `redaction.SENSITIVE_KEYS`, `_key_normalized`, `_redact_value` | `TestSensitiveKeysR3` |
| R-8 URL verliert Query/Fragment | `redaction._sanitize_url`, `_sanitize_urls_in_text` | `TestUrlAndPathRules` |
| R-9 Benutzerprofilpfade → `~`, auch in Tracebacks | `shorten_user_paths` (in `redact_text`/`redact_mapping` angewendet) | `TestUrlAndPathRules::test_user_profile_path_shortened_to_tilde`, `test_path_shortening_works_inside_tracebacks`, `test_path_shortening_with_explicit_profile` |
| R-10 Transkriptfelder; Zeichenzahl erhalten; gilt auch für unstrukturierte Logtexte (N-02) | `TRANSCRIPT_KEYS`, `_redacted_transcript`, `redact_text` | `TestTranscriptKeysR10`, `TestRedactTextN02` (echte Zeilen `Final [seg=%s]: %s` und `existing=%r, new=%r`) |
| R-11 `default=str` nur je Blattwert; JSON-Objekt statt String-Kollaps | `redact_mapping` Leaf-Fallback, `_leaf_to_str` | `TestLeafFallbackR11`, N-01 (JSON-Objekt, keine `mappingproxy(`/`frozenset(`) |
| R-12 Tiefengrenze 16 UND Knotengrenze 500, abgeschnitten + markiert | `_Budget`, `_truncated` | `TestRedactBoundsR12` (zyklisch, 500+ Schlüssel, Tiefe) |
| R-6 hello-Whitelist | `normalizer._hello_whitelist` | `test_hello_controlframe_is_whitelist_only_no_token`, Diagnose-Skript |
| Wert, dessen `__str__`/`__repr__` wirft, wird ersetzt, keine Ausnahme | `_leaf_to_str` (drei Schutzebenen) | `test_throwing_str_and_repr_do_not_propagate`, `test_unfreeze_guards_throwing_repr` |
| `raw` > 64 KiB → `{"_truncated": …}` | (OBS-030 Worker; hier nur eine Kapsel für `_truncated`) | dokumentiert in RESULT/DECISION 6 |

## 5. Protokolle (ARCH §5.1/§5.2, CONTRACTS §8)

| Anforderung | Implementierung | Tests |
|---|---|---|
| `LogStore`-Protokoll (`write_batch → (eingefügt, dedupliziert)`, `clear`) | `storage/base.py` | (Signatur-Stand; Implementierung OBS-030) |
| `Sink`-Protokoll (`write_batch`, `close`), Worker-gebunden | `sinks/base.py` | (Signatur-Stand; Implementierung OBS-030/150) |
| Query: `ProviderState`, `ProviderStatus`, `QueryFilter`, `LogRecordView`, `QueryPage`, `LogProvider` (4 Methoden, „wirft nie") | `query/base.py` | `test_obs010_query_contracts` |
| Schichtung: `models ← redaction ← normalizer ← …`; `core/**` importiert nie PySide6; `normalizer` kein sqlite3; keine Runtime-Importe | Importierstruktur | `test_obs010_contracts::TestModuleIsolation`, `TestAcyclicImports` |

## 6. Run-/Evidence-Auflagen des Auftrags

| Auflage | Erfüllt durch |
|---|---|
| Run-Ordner `RUN-OBS-010-01_2026-08-17_DEEPSEEK` mit RUN_LOG.md/RESULT.md | 30_AUSFUEHRUNG (plus RUN_REPORT.md, OUTPUT_INDEX.md gem. Themen-AGENTS) |
| Evidence `40_EVIDENCE/OBS-010/RUN-01_2026-08-17_DEEPSEEK`: TEST_RESULTS.md, DIFF_SUMMARY.md, CONTRACT_COVERAGE.md | vorhanden |
| Diagnoseskript außerhalb Produktcode: reale `hello`-Struktur → Redaction | `OBS-010_RUN-01_hello_redaction_diagnose.py` (Exit 0) |
| Mutationschecks MT-1/MT-2 | dokumentiert in TEST_RESULTS §4 |
| Steuerungsdateien | `CURRENT_STATE.md`, `LOG_VERLAUF.md` aktualisiert |
| keine bestehende Produktdatei / kein bestehender Test geändert | DIFF_SUMMARY