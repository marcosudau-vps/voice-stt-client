# Requirementbelege AP-CV2-050 / R01

Status **SELF_CHECK_PASS / REVIEW_READY**. Unabhängige Abnahme offen; Requirements bleiben CLIENT OPEN.

Alle Methoden gehören `tests.test_v2_controls`. Serverchecks verwenden die Namen/Präfixe in [79 Checks](server-controls-checkpoint.json); die Modi True/False, False/True und True/True sind jeweils separat ausgeführt. Native Namen stehen in [16 Checks](windows-hotkeys.json). Die [Windowsqualifikation](windows-validation.json) bindet alle Methoden, Skripte und Logs an Parent plus exakten Produktdiff und veröffentlichbare Gitblobs.

| Requirement | Tatsächliche Testmethoden | Zusätzlicher tatsächlicher Checkpoint |
| --- | --- | --- |
| CONTROL-01 | `PhaseMatrix.test_idle_effective_manual_and_local_audio_barriers`; `Controls.test_duplicate_pending_and_audio_desired_pause_guards` | `manual/activate; wake_only/primary_idle_noop` |
| CONTROL-02 | `PhaseMatrix.test_all_5_phases_4_actions_2_slots_2_sources` | `idle/secondary_noop; finish/applied; cancel/applied` |
| CONTROL-03 | `PhaseMatrix.test_all_5_phases_4_actions_2_slots_2_sources`; `NativeRegistration.test_controls_registered_without_manual_source_and_wake_slot_only_pause` | `admission/False/True; pause/open_activation_survives; native/all_roles_registered` |
| CONTROL-04 | `NativeRegistration.test_controls_registered_without_manual_source_and_wake_slot_only_pause` | `native/WM_HOTKEY_exactly_once/wake_pause` |
| CONTROL-05 | `Controls.test_complete_mask_coalesces_and_confirmation_waits_for_snapshot` | `pause/both_confirmed; pause/open_activation_survives` |
| CONTROL-06 | `Controls.test_run_restart_pause_reset_and_persisted_base_has_trigger` | `pause/no_effective_source` |
| CONTROL-07 | `Controls.test_lost_ack_reconnect_keeps_intent_without_false_confirmation`; `Controls.test_run_restart_pause_reset_and_persisted_base_has_trigger` | `device/pause_preserved; reconnect/new_session_same_run; reconnect/no_active_gap; restart/new_run_id_unpaused` |
| CONTROL-08 | `Controls.test_complete_mask_coalesces_and_confirmation_waits_for_snapshot`; `Controls.test_pause_during_bootstrap_ack_restored_before_ready`; `Controls.test_lost_ack_reconnect_keeps_intent_without_false_confirmation` | `reconnect/no_active_gap; pause/both_confirmed` |
| CONTROL-09 | `Migration.test_normalization_and_collisions_rejected_before_registration`; `NativeRegistration.test_partial_failure_restores_old_and_apply_rebind_invalidates_old_ids`; `NativeRegistration.test_rollback_failure_exposed_and_no_partial_dispatch`; `Controls.test_duplicate_pending_and_audio_desired_pause_guards` | `native/Win32_1409_recorded; native/atomic_rollback; native/old_ids_invalid; native/WM_HOTKEY_exactly_once/primary` |
| CONTROL-10 | `Controls.test_old_activation_intent_never_retargeted_and_invalid_phase_no_retry`; `PhaseMatrix.test_all_5_phases_4_actions_2_slots_2_sources` | `waiting/refresh_no_wire; waiting/forced_invalid_phase; waiting/no_warn_retry; segment/no_cumulative_refresh; segment/minimum_restored; segment/repeat_non_cumulative; followup/now_plus_timeout; followup/repeat_non_cumulative` |
| CONTROL-11 | `PhaseMatrix.test_no_local_deadline_or_vad_side_effect` | `vad/no_watchdog_or_presence_refresh` |
| CONTROL-12 | `Controls.test_old_activation_intent_never_retargeted_and_invalid_phase_no_retry` | `finish/recorded_audio_processed; finish/new_final_without_deleting_old; cancel/published_text_preserved; stale/original_id` |
| CONTROL-13 | `Controls.test_closing_input_finish_cancel_no_change_and_refresh_blocked`; `Controls.test_old_activation_intent_never_retargeted_and_invalid_phase_no_retry` | `stale/original_id; stale/new_activation_untouched` |
| CONTROL-14 | `Migration.test_defaults_alias_and_explicit_bindings_preserved`; `Migration.test_conflict_does_not_mutate_or_delete_profile`; `NativeRegistration.test_wrong_physical_lparam_rejected_and_utilities_separate` | `native/WM_HOTKEY_exactly_once/reinsert_last; native/WM_HOTKEY_exactly_once/overlay_toggle` |

CONTROL-13: closing_input ist im echten Clienttransport mit korreliertem Ack und Mirror im deterministischen Test geprüft; der TCP-Servercheckpoint prüft ergänzend stale/original_id und neue B unverändert. Die genaue closing_input-Phase wird nicht durch einen künstlichen Server-PASS ersetzt.

CONTROL-14: beide expliziten Legacybindings bleiben im unveränderten Profil am Konflikt erhalten; erst AP070/080 ergänzt Persistenz/Benutzerentscheidung. Kein Profil wird hier still umgeschrieben.
