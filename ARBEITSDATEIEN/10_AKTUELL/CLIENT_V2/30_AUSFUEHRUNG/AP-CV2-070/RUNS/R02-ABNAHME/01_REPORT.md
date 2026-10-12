# AP-CV2-070 / R02-ABNAHME – unabhängiger Abschlussbericht

**Technisches Urteil: ROOT_PASS. Offene Pflichtfindings: keine (`[]`).** Die menschliche Übernahme auf feat/client-v2 ist ausdrücklich noch nicht freigegeben.

## Identität, Scope und Vorgehen

- [Originalauftrag](00_PROMPT_ORIGINAL.md), [R01-Umsetzungsbericht](../R01-UMSETZUNG/01_REPORT.md), [Reviewevidenz](EVIDENCE/INDEX.md), [PR #9](https://github.com/marcosudau-vps/voice-stt-client/pull/9).
- **reviewed_sha** `146eff89e89faa48546f913cd7b770d3449d22a6`; **reviewed_tree** `e18b610e4fddfefc9a167c7178931f64f7fcd10e`; **canonical_parent** `473a75d02fb6d00e5664af4328dadaa44da5191a`; **server_sha** `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
- PR-Base `feat/client-v2` exakt am kanonischen Parent; Head `work/client-v2/ap-cv2-070`; zwei Paketcommits, 45 geänderte Pfade. Produktqualifikation am ersten Commit `8b68b4840c7955cd06a2be14736678d83ee729dc`, zweiter Commit administrativer Handoff.
- AP060-Vorgänger wurde per [verifizierter Single-Parent-/Tree-Provenienz](../R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json) tatsächlich übernommen. Als unabhängiger Reviewer an die publizierte Kandidaten-SHA gebundene GitHub-Code-, Diff-, Kontrakt-, Akten- und CI-Prüfung. **Keine eigene Windowsvollsuite, keine Hardwaretestdurchführung.** Vorliegende Plattformtests sind Fremdausführung und wurden unabhängig auf Identität, Methodik, Resultat und Nachvollziehbarkeit geprüft.

## Technische und vertragliche Abnahme

1. **Versionierte Migration:** `core/v2_profile.py` prüft Triggerflags und V1-Modi, überführt Timer via Decimal exakt in ms, erhält Konflikte und unbelegte Legacypräferenzen sichtbar; offline→online-Wake-Aliasauflösung nur über echten dynamischen Katalog. Atomare Dateiersetzung mit unverändertem `.pre-v2.bak`-Backup, Idempotenz und Schreibfehlerabbruch mit erhaltenem Original sind getestet.
2. **HTTP, Schema und Katalog:** `core/settings_service.py` trennt 18 Schemaeinträge, 16 Sessionkeys und 15 Serverdefaults ohne imaginäre writable-/per-entry-Revisionen. Typ-/Werte-/Cross-Fieldvalidierung, dynamische Katalogrevision, Aliasmehrdeutigkeit, kanonische Selektion und Backendprüfung; same-origin HTTPS/TLS, Redirectblock, bounded Responses/Timeout und nicht blockierender, abgeschirmter Worker.
3. **Autoritative Settings:** Eigens getrennte Session- und Serverrevisionen. Session-PATCH beschränkt auf die tatsächlich anwendbaren NA-Felder, atomar; Revisionskonflikt mit frischem Snapshot und neuer commandId höchstens einmal neu berechnet. Bestätigung durch neuen Snapshot, differenzierter Report `desired/requested/effective/pending/unsupported`. Während offener Activation bleiben die gelatchten effektiven Werte erhalten; nach Eingabeschluss wird neu gelesen. NS-Noise/VAD nicht als individuell aktivierbar behauptet. Auswahl für das folgende Hello, nicht per Patch hot-reload; Suppression nur über Commands. Admin-PATCH read-before, ohne automatischen Retry bei unbekanntem Ergebnis.
4. **Bootstrap/Fehlerisolation:** HTTP-Metadaten und Profileignung vor Hello; beide Suppressions initial true; Audioavailability aus dem Medienpfad zuerst, danach Settings-Snapshot/PATCH und bestätigte effektive Werte, zuletzt desired Suppression. Fehlende/Ablehnungs-/Konflikt-/Timeoutnachweise verhindern READY/Audio-/Manualfreigabe. Gültige Generation und Binding sind Voraussetzung für spätere Publikationen.
5. **Schnittstellengrenzen:** Echter gepinnter Client-HTTP-/WebSocket-/Media-/PCM-Checkpoint belegt die kumulative AP070-Wirkung. Geräte-/Recorder-/Modell-Doubles sind offen ausgewiesene kontrollierte Grenzen. Qt/Settingsdialogs und Credential-Manager verbleiben AP080, Appkomposition AP100, reale ASR/Wake-/Hardware-/Kalibrierungsmatrix AP-IV2-020; kein vorzeitiger Abschluss dieser Gates.

## Requirementweise Prüfung

Alle 29 IDs sind mit den angegebenen Methoden und gemessenen Checkpoints im [R01-Coverageindex](../R01-UMSETZUNG/EVIDENCE/requirement-coverage.md) nachgewiesen; die unabhängige Bewertung erfolgt durch Code-/Kontrakt- und Evidenzabgleich, nicht durch eigene Windows-Neuausführung.

| ID | Review | vorhandene ausführbare Methode(n) | Integrationsbeleg |
| --- | --- | --- | --- |
| SET-01 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_counts_policies_and_schema_without_write_flags` | `settings/schema18_session16_server15` |
| SET-02 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_types_ranges_and_no_coercion`; `tests.test_v2_settings_service.Service.test_atomic_local_validation_and_scope_authority` | `atomic/cross_field_conflict` |
| SET-03 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_types_ranges_and_no_coercion`; `tests.test_v2_settings_service.CatalogAndSchema.test_counts_policies_and_schema_without_write_flags` | `wake/calibration_pending_visible`; `bootstrap/na_effective_confirmed` |
| SET-04 | PASS | `tests.test_v2_settings_service.Service.test_server_revision_patch_no_change_and_unclear_read_no_retry`; `tests.test_v2_settings_service.Service.test_preflight_then_na_patch_snapshot_suppression_ready` | `server/independent_revision_confirmed` |
| SET-05 | PASS | `tests.test_v2_settings_service.Service.test_atomic_local_validation_and_scope_authority`; `tests.test_v2_settings_service.Service.test_bootstrap_faults_never_release_suppression` | `atomic/unknown_key`; `atomic/invalid_type`; `atomic/out_of_range`; `atomic/cross_field_conflict`; `atomic/wrong_scope`; `atomic/read_only_runtime_authority` |
| SET-06 | PASS | `tests.test_v2_settings_service.Service.test_conflict_reread_new_command_id_exactly_once` | `revision/session_no_change`; `revision/conflict_reload_new_id`; `na/requested_new_effective_latched` |
| SET-07 | PASS | `tests.test_v2_settings_service.Service.test_requested_effective_latched_and_pending_report`; `tests.test_v2_settings_service.Service.test_input_closed_refreshes_effective_without_explicit_ui_read` | `na/activation_start_snapshot_immutable`; `na/after_close_effective_confirmed` |
| SET-08 | PASS | `tests.test_v2_settings_service.Service.test_preflight_then_na_patch_snapshot_suppression_ready` | `reconnect/na_before_audio` |
| SET-09 | PASS | `tests.test_v2_settings_service.Service.test_ns_preferences_unsupported_selection_next_hello_no_patch` | `wake/selection_pending_no_hot_reload`; `wake/new_hello_selection_effective` |
| SET-10 | PASS | `tests.test_v2_settings_service.Service.test_ns_preferences_unsupported_selection_next_hello_no_patch` | `ns/noise_vad_unsupported_no_false_success`; `reconnect/ns_preference_still_unsupported` |
| SET-11 | PASS | `tests.test_v2_settings_service.Service.test_atomic_local_validation_and_scope_authority` | `atomic/read_only_runtime_authority`; `bootstrap/availability_patch_suppression_order` |
| SET-12 | PASS | `tests.test_v2_settings_service.Service.test_server_revision_patch_no_change_and_unclear_read_no_retry`; `tests.test_v2_settings_service.Service.test_server_error_codes_reload_no_partial_or_retry` | `admin/unauthorized_guard`; `server/validation_failure_atomic_422`; `server/persistence_failure_atomic_500` |
| SET-13 | PASS | `tests.test_v2_settings_service.Service.test_server_revision_patch_no_change_and_unclear_read_no_retry`; `tests.test_v2_settings_service.HTTP.test_bounded_http_timeout_keeps_one_worker_and_loop_responsive` | `server/persistence_failure_atomic_500`; `server/validation_failure_atomic_422` |
| SET-14 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_counts_policies_and_schema_without_write_flags` | `settings/schema18_session16_server15` |
| SET-15 | PASS | `tests.test_v2_settings_service.Migration.test_mode_flags_and_explicit_both`; `tests.test_v2_settings_service.Migration.test_exact_seconds_ms_and_retired_extension_warning`; `tests.test_v2_settings_service.Migration.test_colliding_session_and_local_timing_remains_unresolved`; `tests.test_v2_settings_service.Migration.test_versioned_profile_ignores_legacy_mode_extension` | lokaler Migrations-/Fehlerfall |
| SET-16 | PASS | `tests.test_v2_settings_service.Migration.test_backup_atomic_idempotent_local_fields_preserved`; `tests.test_v2_settings_service.Migration.test_write_failure_leaves_original_and_backup`; `tests.test_v2_settings_service.Migration.test_invalid_trigger_and_hotkey_conflicts_are_preserved` | lokaler Migrations-/Fehlerfall |
| SET-17 | PASS | `tests.test_v2_settings_service.Service.test_preflight_then_na_patch_snapshot_suppression_ready`; `tests.test_v2_settings_service.Service.test_media_availability_rejection_blocks_before_settings_audio`; `tests.test_v2_settings_service.Service.test_bootstrap_faults_never_release_suppression`; `tests.test_v2_settings_service.Service.test_bootstrap_new_wish_during_confirmation_cannot_claim_ready` | `bootstrap/no_pre_ready_audio`; `bootstrap/availability_patch_suppression_order`; `audio/real_capture_media_ws_server_pcm` |
| SET-18 | PASS | `tests.test_v2_settings_service.Migration.test_offline_then_online_resolution_unavailable_id_retained`; `tests.test_v2_settings_service.Service.test_preflight_error_each_read_and_profile_keeps_wire_empty` | `catalog/availability_change_reload_retains_wish`; `catalog/unavailable_whole_selection_blocks` |
| SET-19 | PASS | `tests.test_v2_settings_service.Service.test_atomic_local_validation_and_scope_authority`; `tests.test_v2_settings_service.HTTP.test_origin_tls_routes_and_no_secret_errors` | lokaler Migrations-/Fehlerfall |
| WAKE-01 | PASS | `tests.test_v2_settings_service.Service.test_catalog_revision_cache_and_availability_reload`; `tests.test_v2_settings_service.Service.test_availability_reload_rejects_old_revision_and_retries_bounded`; `tests.test_v2_settings_service.Service.test_stale_http_generation_rejected_without_publication` | `catalog/availability_change_reload_retains_wish` |
| WAKE-02 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_catalog_metadata_immutable_no_internal_paths` | `catalog/real_build_dynamic_metadata` |
| WAKE-03 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_alias_resolution_unicode_trim_dedup_and_ambiguity` | `catalog/real_build_dynamic_metadata` |
| WAKE-04 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_alias_resolution_unicode_trim_dedup_and_ambiguity` | `catalog/canonical_ids_only` |
| WAKE-05 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_whole_selection_no_common_or_explicit_backend_no_fallback`; `tests.test_v2_settings_service.Migration.test_offline_then_online_resolution_unavailable_id_retained` | `catalog/unavailable_whole_selection_blocks` |
| WAKE-06 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_whole_selection_no_common_or_explicit_backend_no_fallback` | `wake/selected_only_canonical_snapshot` |
| WAKE-07 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_counts_policies_and_schema_without_write_flags` | `wake/selected_only_canonical_snapshot`; `bootstrap/na_effective_confirmed` |
| WAKE-08 | PASS | – | `wake/hit_actual_shared_controller`; `wake/started_before_detected`; `wake/latched_no_second_activation` |
| WAKE-09 | PASS | `tests.test_v2_settings_service.CatalogAndSchema.test_counts_policies_and_schema_without_write_flags` | `wake/calibration_pending_visible` |
| WAKE-10 | PASS | – | lokaler Migrations-/Fehlerfall |

## Nachweise und CI

| Quelle | Eigene Entscheidung |
| --- | --- |
| [Windowsvalidierung](../R01-UMSETZUNG/EVIDENCE/windows-validation.json) / [Handoff-Hashvergleich](../R01-UMSETZUNG/EVIDENCE/handoff-verification.json) | **PASS**: Windows-11-Build 26300 / Python 3.12.10 / Projektvenv, vollständige Befehle, Exitcodes, Zeitpunkte, Testzahlen, SHA256-Logs; 199 qualifizierte Produkt-/Test-/Konfigblobs stimmen weiterhin mit dem eingereichten Kandidaten überein. |
| [Windowsvollsuite](../R01-UMSETZUNG/EVIDENCE/windows-full-unittest.txt) | **PASS** 1460 Tests, Exit 0. **Im Umsetzungslauf durchgeführt, Nachweis unabhängig geprüft; eigener Test NOT_RUN (zulässig).** |
| [Gezielte Tests](../R01-UMSETZUNG/EVIDENCE/targeted-unittest.txt) | **PASS** 243 Tests mit `-W error`, Exit 0; 34 neue AP070-Tests. |
| [Echter Settingscheckpoint](../R01-UMSETZUNG/EVIDENCE/server-settings-checkpoint.json) | **PASS** 38 echte HTTP-/WebSocket-/Media-/PCM-Prüffälle, 46 gepinnte Serverquelldateien; modell-/hardwareabhängige Grenzflächen kontrolliert ersetzt. |
| [Server-Supplementtests](../R01-UMSETZUNG/EVIDENCE/server-contracts.json) | **PASS** 55 Tests, 0 Skips, separate Zusatzqualifikation statt Ersatz des Clientcheckpoints. |
| `compileall` und qualifizierter staged Diff | **PASS** laut Windowsmanifest, keine späteren produkt-/testrelevanten Änderungen. |
| [GitHub-CI 38287710413](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38287710413) | **SUCCESS** am geprüften SHA, Tests, Compile, EXE-Smoke, sdist/Wheel und installierter Wheel-Smoke grün. |

## Findings und Übergabe

**Keine neuen oder offenen Pflichtfindings.** ROOT_PASS für das exakt genannte `reviewed_sha`/`reviewed_tree`, nicht für einen unbeobachteten späteren Produktstand. Verwaltungsstatus `packageStatus=ROOT_PASS`, `workflowPhase=WAITING_FOR_APPROVAL`, `humanApproval=null`, `writeOwner=null`. Der gesonderte Reviewaktencommit verändert ausschließlich Dokumentation/Status-/Traceabilitydaten; seine SHA steht in der Übergabe, nicht als Selbstreferenz dieses Reports.

Nächste Aktion: **ausdrückliche menschliche Freigabe zur kanonischen Übernahme von PR #9**, dann aktuellen Head/Base und ausschließlich administrativen Unterschied seit `reviewed_sha` sowie passende CI prüfen. Keine automatische Mergeaktion, kein AP080, kein Main-/Servermerge, Release oder Cleanup.
