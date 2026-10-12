# AP080 – individuelle UI-01…UI-10-Nachweise

Eigenprüfung SELF_CHECK_PASS / REVIEW_READY; unabhängiger Status CLIENT OPEN. Alle Methoden sind im gezielten Lauf enthalten, reale Fälle im Offscreen- und nativen Windowscheckpoint. Die native Zusatzprüfung belegt sichtbar bediente HWND und Screenshot; produktive ASR/Hardwarequalifikation bleibt AP-IV2-020.

## UI-01

Triggerquellencheckboxen statt Legacybetriebsmodus; beide gleichzeitig und WakeMehrfachauswahl.

- `tests.test_v2_settings_ui.CoreActions.test_manual_wake_and_wake_only_keep_controls`
- `tests.test_v2_settings_ui.CoreActions.test_triggerless_and_empty_wake_selection_are_atomic_rejections`
- `tests.test_v2_settings_ui.QtSurface.test_local_surface_contains_no_legacy_trigger_or_mode_controls`

Reale Server-/Windowsfälle: `apply/wake_only_controls_retained`.

## UI-02

Requested/effective/default/applypolicy/revision und calibrationStatus sichtbar.

- `tests.test_v2_settings_ui.QtSurface.test_scope_schema_policy_requested_effective_and_calibration_visible`
- `tests.test_v2_settings_ui.QtSurface.test_ns_noise_vad_readonly_and_server_initially_locked`
- `tests.test_v2_settings_ui.QtSurface.test_bool_and_backend_have_typed_editors`
- `tests.test_v2_settings_ui.CoreActions.test_na_apply_keeps_activation_and_confirms_session`
- `tests.test_v2_settings_ui.CoreActions.test_preserved_ns_intent_cannot_be_edited_as_session_setting`

Reale Server-/Windowsfälle: `session/ui_real_patch_snapshot_effective`, `ui/calibration_pending_visible`.

## UI-03

LeereWakegruppe/Ladefehler/unavailableID verständlich; kein stiller Auswahlverlust.

- `tests.test_v2_settings_ui.QtSurface.test_empty_catalog_has_explicit_message`
- `tests.test_v2_settings_ui.QtSurface.test_unavailable_and_unknown_saved_ids_remain_visible`
- `tests.test_v2_settings_ui.QtSurface.test_catalog_failure_keeps_prior_selection`

Reale Server-/Windowsfälle: `ui/real_services_public_read_locked`.

## UI-04

Serverseite gesperrt bis zu einem authgeprüften No-change-PATCH; öffentliche GETs kein Keybeweis.

- `tests.test_v2_settings_ui.CoreActions.test_public_reads_and_saved_key_do_not_unlock`
- `tests.test_v2_settings_ui.CoreActions.test_no_change_check_does_not_mutate_defaults`
- `tests.test_v2_settings_ui.CoreActions.test_keycheck_uses_latest_value_not_stale_ui_default`
- `tests.test_v2_settings_ui.CoreActions.test_claimed_applied_keycheck_is_rejected`
- `tests.test_v2_settings_ui.QtSurface.test_password_check_clears_field_and_unlocks_only_after_patch`

Reale Server-/Windowsfälle: `auth/no_change_defaults_revision_preserved`, `credential/load_without_auth_stays_locked`.

## UI-05

HTTPAdminheader X-VoiceSTT-Admin-Key,401/403/409/422 differenziert; kein erfundener verify/loginEndpoint.

- `tests.test_v2_settings_ui.CoreActions.test_auth_revision_validation_persistence_errors_do_not_unlock`
- `tests.test_v2_settings_ui.QtSurface.test_all_http_errors_have_distinct_user_messages`
- `tests.test_v2_settings_ui.CoreActions.test_conflict_rereads_and_rechecks_once`
- `tests.test_v2_settings_ui.QtSurface.test_server_editor_uses_real_service_and_revision`

Reale Server-/Windowsfälle: `auth/wrong_key_visible_locked`, `server/admin_ui_real_patch`, `server/schema_reject_visible_no_write`.

## UI-06

CredentialManager originbezogen create/replace/delete; QSettings nur Metadaten.

- `tests.test_v2_settings_ui.Credentials.test_normalized_origin_and_isolation`
- `tests.test_v2_settings_ui.Credentials.test_create_replace_delete_and_redacted_repr`
- `tests.test_v2_settings_ui.CoreActions.test_verify_save_replace_delete_and_relock`
- `tests.test_v2_settings_ui.QtSurface.test_qsettings_export_and_config_have_no_key`

Reale Server-/Windowsfälle: `credential/native_create_from_ui`, `credential/native_replace_from_ui`, `credential/native_distinct_replacement`, `credential/native_delete_from_ui`, `credential/origin_isolation`.

## UI-07

Credentialstoreausfall ausschließlich Prozessspeicher; kein Klartextfallback/SecretExport.

- `tests.test_v2_settings_ui.Credentials.test_failure_read_write_delete_redacts_backend`
- `tests.test_v2_settings_ui.CoreActions.test_store_failure_is_memory_only_and_explicit_error`
- `tests.test_v2_settings_ui.QtSurface.test_qsettings_export_and_config_have_no_key`

Reale Server-/Windowsfälle: `secrets/no_qsettings_or_projection_export`, `secrets/no_config_export`.

## UI-08

ReconnectwährendoffenerActivation explizit cancel/finish/vormerken.

- `tests.test_v2_settings_ui.CoreActions.test_reconnect_without_activation_choice_has_no_side_effect`
- `tests.test_v2_settings_ui.CoreActions.test_defer_preserves_foreground_and_background`
- `tests.test_v2_settings_ui.CoreActions.test_finish_waits_for_actual_completion_before_reconnect`
- `tests.test_v2_settings_ui.CoreActions.test_cancel_targets_captured_activation_and_separate_drain_loss`
- `tests.test_v2_settings_ui.CoreActions.test_reapplying_deferred_profile_still_requires_connection_choice`
- `tests.test_v2_settings_ui.QtSurface.test_decision_cancel_default_and_all_three_choices`

Reale Server-/Windowsfälle: `apply/defer_preserves_real_activation`, `apply/finish_real_command_then_reconnect`, `apply/cancel_real_activation_then_reconnect`.

## UI-09

Drainverlust bei SettingsReconnect nennen; ausdrücklich warten oder Verlust wählen.

- `tests.test_v2_settings_ui.CoreActions.test_idle_background_drain_requires_separate_loss_choice`
- `tests.test_v2_settings_ui.CoreActions.test_explicit_discard_idle_drain_reconnects_once`
- `tests.test_v2_settings_ui.CoreActions.test_wait_drain_timeout_keeps_socket_and_restores_pauses`
- `tests.test_v2_settings_ui.CoreActions.test_new_background_drain_during_pause_needs_new_choice`

Reale Server-/Windowsfälle: `drain/decision_cancel_preserves_connection`, `drain/wait_real_terminal_then_reconnect`.

## UI-10

Dialogclose/serverwechsel/alteAsyncresponse entsperrt/ändert keinen neueren Kontext.

- `tests.test_v2_settings_ui.CoreActions.test_generation_changed_during_verify_cannot_unlock`
- `tests.test_v2_settings_ui.CoreActions.test_dialog_closed_during_auth_drops_response`
- `tests.test_v2_settings_ui.CoreActions.test_origin_switch_drops_key_and_cannot_unlock_or_patch`
- `tests.test_v2_settings_ui.CoreActions.test_disconnect_while_decision_open_rejects_old_context`
- `tests.test_v2_settings_ui.QtSurface.test_old_epoch_reply_after_reopen_cannot_unlock_new_origin`
- `tests.test_v2_settings_ui.CoreActions.test_close_while_drain_waiting_restores_pauses_without_reconnect`

Reale Server-/Windowsfälle: `credential/reopen_does_not_unlock`.

[Manifest](windows-validation.json), [gezielte vollständige Logs](targeted-unittest.txt), [Server-UI](server-ui-checkpoint.json), [native Windows-UI/Vault](windows-credential-ui.json), [sichtbarer Dialog](native-dialog.png).
