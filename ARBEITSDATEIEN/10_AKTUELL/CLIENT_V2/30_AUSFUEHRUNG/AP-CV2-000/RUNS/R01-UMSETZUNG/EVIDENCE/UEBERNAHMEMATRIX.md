# Dateiweise Feature-/Release-Übernahme

Gemeinsame Basis 1b432c9; Feature 050e776 (Produktbaum 8bab1b3/a80a6b1); Release f625904. Kein Historymerge/Rebase.

| Quelle Feature | Ergebnis | Übernahmeregel | Konflikt |
| --- | --- | --- | --- |
| `.github/workflows/ci.yml` | `.github/workflows/ci.yml` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `.github/workflows/release.yml` | `.github/workflows/release.yml` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `.gitignore` | `.gitignore` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `VERSION` | `VERSION` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `app.py` | `voice_stt_client/app.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `config.yaml` | `voice_stt_client/config.yaml` | Featuredefaults vollständig erhalten; nur Paketablage | keiner |
| `core/__init__.py` | `voice_stt_client/core/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/actions.py` | `voice_stt_client/core/actions.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/audio_capture.py` | `voice_stt_client/core/audio_capture.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/config.py` | `voice_stt_client/core/config.py` | Feature + kompatibles Releasedelta über gemeinsame Basis; Featureflags erhalten, explizite Env-Datei ohne Legacy-Rückfall | keiner |
| `core/controller.py` | `voice_stt_client/core/controller.py` | Feature-Triggercode vollständig erhalten; ausschließlich Imports | keiner |
| `core/event_cursor_store.py` | `voice_stt_client/core/event_cursor_store.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/event_models.py` | `voice_stt_client/core/event_models.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/event_normalizer.py` | `voice_stt_client/core/event_normalizer.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/event_protocol.py` | `voice_stt_client/core/event_protocol.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/event_stream.py` | `voice_stt_client/core/event_stream.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/feedback_mapping.py` | `voice_stt_client/core/feedback_mapping.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/feedback_reducer.py` | `voice_stt_client/core/feedback_reducer.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/history.py` | `voice_stt_client/core/history.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `core/led_controller.py` | `voice_stt_client/core/led_controller.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/logging_settings_metadata.py` | `voice_stt_client/core/logging_settings_metadata.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/logging_setup.py` | `voice_stt_client/core/logging_setup.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/__init__.py` | `voice_stt_client/core/observability/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/adapters/__init__.py` | `voice_stt_client/core/observability/adapters/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/adapters/client_events.py` | `voice_stt_client/core/observability/adapters/client_events.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/adapters/python_logging.py` | `voice_stt_client/core/observability/adapters/python_logging.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/adapters/server_live.py` | `voice_stt_client/core/observability/adapters/server_live.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/health.py` | `voice_stt_client/core/observability/health.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/ingress.py` | `voice_stt_client/core/observability/ingress.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/manager.py` | `voice_stt_client/core/observability/manager.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/models.py` | `voice_stt_client/core/observability/models.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/normalizer.py` | `voice_stt_client/core/observability/normalizer.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/query/__init__.py` | `voice_stt_client/core/observability/query/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/query/base.py` | `voice_stt_client/core/observability/query/base.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/query/local.py` | `voice_stt_client/core/observability/query/local.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/query/service.py` | `voice_stt_client/core/observability/query/service.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/redaction.py` | `voice_stt_client/core/observability/redaction.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/sinks/__init__.py` | `voice_stt_client/core/observability/sinks/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/sinks/base.py` | `voice_stt_client/core/observability/sinks/base.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/sinks/jsonl_file.py` | `voice_stt_client/core/observability/sinks/jsonl_file.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/storage/__init__.py` | `voice_stt_client/core/observability/storage/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/storage/base.py` | `voice_stt_client/core/observability/storage/base.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/storage/sqlite.py` | `voice_stt_client/core/observability/storage/sqlite.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/observability/worker.py` | `voice_stt_client/core/observability/worker.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/reinsertion.py` | `voice_stt_client/core/reinsertion.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/session_coordinator.py` | `voice_stt_client/core/session_coordinator.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/settings_metadata.py` | `voice_stt_client/core/settings_metadata.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `core/stt_session.py` | `voice_stt_client/core/stt_session.py` | Feature-Triggercode vollständig erhalten; ausschließlich Imports | keiner |
| `core/text_injector.py` | `voice_stt_client/core/text_injector.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `core/version.py` | `voice_stt_client/core/version.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `requirements-dev.txt` | `requirements-dev.txt` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `scripts/__init__.py` | `scripts/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `scripts/build.py` | `scripts/build.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `scripts/pyinstaller_runtime_platform.py` | `scripts/pyinstaller_runtime_platform.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `scripts/pyinstaller_site/sitecustomize.py` | `scripts/pyinstaller_site/sitecustomize.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `scripts/release.py` | `scripts/release.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/__init__.py` | `tests/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap06_modes.py` | `tests/manual_test_ap06_modes.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap06_runtime_mode_switch.py` | `tests/manual_test_ap06_runtime_mode_switch.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_adapter_failures.py` | `tests/manual_test_ap07_adapter_failures.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_device_mute.py` | `tests/manual_test_ap07_device_mute.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_end_to_end.py` | `tests/manual_test_ap07_end_to_end.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_event_stream.py` | `tests/manual_test_ap07_event_stream.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_led_disconnect.py` | `tests/manual_test_ap07_led_disconnect.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_led_endurance.py` | `tests/manual_test_ap07_led_endurance.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_led_hardware.py` | `tests/manual_test_ap07_led_hardware.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_ap07_mute_button.py` | `tests/manual_test_ap07_mute_button.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_server_connection.py` | `tests/manual_test_server_connection.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/manual_test_text_injector.py` | `tests/manual_test_text_injector.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/obs050_apply_support.py` | `tests/obs050_apply_support.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_ap06_followup.py` | `tests/test_ap06_followup.py` | Feature + kompatibles Releasedelta über gemeinsame Basis; Warnungs-Wait Feature erhalten, neue UI-Editoren portiert | explizit gelöst |
| `tests/test_ap_cli_000_baseline_characterization.py` | `tests/test_ap_cli_000_baseline_characterization.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_app.py` | `tests/test_app.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_audio_capture.py` | `tests/test_audio_capture.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_build_script.py` | `tests/test_build_script.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_config.py` | `tests/test_config.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_controller.py` | `tests/test_controller.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_core_bridge.py` | `tests/test_core_bridge.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_event_cursor_store.py` | `tests/test_event_cursor_store.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_event_models.py` | `tests/test_event_models.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_event_normalizer.py` | `tests/test_event_normalizer.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_event_protocol.py` | `tests/test_event_protocol.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_event_stream.py` | `tests/test_event_stream.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_feedback_integration.py` | `tests/test_feedback_integration.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_feedback_mapping.py` | `tests/test_feedback_mapping.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_feedback_reducer.py` | `tests/test_feedback_reducer.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_feedback_ui.py` | `tests/test_feedback_ui.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_history.py` | `tests/test_history.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_hotkeys.py` | `tests/test_hotkeys.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_led_feedback.py` | `tests/test_led_feedback.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs010_contracts.py` | `tests/test_obs010_contracts.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs010_models.py` | `tests/test_obs010_models.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs010_normalizer_client.py` | `tests/test_obs010_normalizer_client.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs010_normalizer_python.py` | `tests/test_obs010_normalizer_python.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs010_normalizer_server.py` | `tests/test_obs010_normalizer_server.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs010_query_contracts.py` | `tests/test_obs010_query_contracts.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs010_redaction.py` | `tests/test_obs010_redaction.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs020_contracts.py` | `tests/test_obs020_contracts.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs020_health.py` | `tests/test_obs020_health.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs020_ingress.py` | `tests/test_obs020_ingress.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs020_logging_setup_integration.py` | `tests/test_obs020_logging_setup_integration.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs020_python_logging_handler.py` | `tests/test_obs020_python_logging_handler.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs020_redaction_end_to_end.py` | `tests/test_obs020_redaction_end_to_end.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs030_app_wiring.py` | `tests/test_obs030_app_wiring.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs030_config.py` | `tests/test_obs030_config.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs030_contracts.py` | `tests/test_obs030_contracts.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs030_gate_corrections.py` | `tests/test_obs030_gate_corrections.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs030_jsonl_sink.py` | `tests/test_obs030_jsonl_sink.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs030_manager.py` | `tests/test_obs030_manager.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs030_path_boundaries.py` | `tests/test_obs030_path_boundaries.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs030_sqlite_store.py` | `tests/test_obs030_sqlite_store.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs030_worker.py` | `tests/test_obs030_worker.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs030_worker_fault_injection.py` | `tests/test_obs030_worker_fault_injection.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs040_client_hooks.py` | `tests/test_obs040_client_hooks.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs040_contracts.py` | `tests/test_obs040_contracts.py` | Feature + kompatibles Releasedelta über gemeinsame Basis; Trigger sent/ack_received/ack_dropped erhalten | explizit gelöst |
| `tests/test_obs040_failure_isolation.py` | `tests/test_obs040_failure_isolation.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs040_fanout_hook.py` | `tests/test_obs040_fanout_hook.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs040_hot_path.py` | `tests/test_obs040_hot_path.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs040_server_live_adapter.py` | `tests/test_obs040_server_live_adapter.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs050_contracts.py` | `tests/test_obs050_contracts.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs050_local_provider.py` | `tests/test_obs050_local_provider.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs050_query_service.py` | `tests/test_obs050_query_service.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_obs050_settings.py` | `tests/test_obs050_settings.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs050_ui.py` | `tests/test_obs050_ui.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_obs060_v1_hardening.py` | `tests/test_obs060_v1_hardening.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_reinsertion.py` | `tests/test_reinsertion.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_release.py` | `tests/test_release.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_session_coordinator.py` | `tests/test_session_coordinator.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_single_instance.py` | `tests/test_single_instance.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_stt_session.py` | `tests/test_stt_session.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_text_injector.py` | `tests/test_text_injector.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_trigger_feedback_contract.py` | `tests/test_trigger_feedback_contract.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_trigger_lifecycle.py` | `tests/test_trigger_lifecycle.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `tests/test_ui_application.py` | `tests/test_ui_application.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `tests/test_ui_widgets.py` | `tests/test_ui_widgets.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/__init__.py` | `voice_stt_client/ui/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/application.py` | `voice_stt_client/ui/application.py` | Feature + kompatibles Releasedelta über gemeinsame Basis; Feature-Manualguard und deaktivierte Hotkeys erhalten | keiner |
| `ui/core_bridge.py` | `voice_stt_client/ui/core_bridge.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/feedback.py` | `voice_stt_client/ui/feedback.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `ui/hotkeys.py` | `voice_stt_client/ui/hotkeys.py` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| `ui/led_feedback.py` | `voice_stt_client/ui/led_feedback.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/logs/__init__.py` | `voice_stt_client/ui/logs/__init__.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/logs/log_detail_view.py` | `voice_stt_client/ui/logs/log_detail_view.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/logs/log_filter_bar.py` | `voice_stt_client/ui/logs/log_filter_bar.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/logs/log_page.py` | `voice_stt_client/ui/logs/log_page.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/logs/log_query_controller.py` | `voice_stt_client/ui/logs/log_query_controller.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/logs/log_table_model.py` | `voice_stt_client/ui/logs/log_table_model.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/logs/log_window.py` | `voice_stt_client/ui/logs/log_window.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/overlay.py` | `voice_stt_client/ui/overlay.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/presentation.py` | `voice_stt_client/ui/presentation.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/settings_dialog.py` | `voice_stt_client/ui/settings_dialog.py` | Feature + kompatibles Releasedelta über gemeinsame Basis; effektive Featureflags bei Sync erhalten, Disabled-Präferenz editierbar | keiner |
| `ui/single_instance.py` | `voice_stt_client/ui/single_instance.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `ui/tray.py` | `voice_stt_client/ui/tray.py` | Featureinhalt; nur Import-/Testnamespace angepasst | keiner |
| `voice-stt-client.spec` | `voice-stt-client.spec` | Feature + kompatibles Releasedelta über gemeinsame Basis | keiner |
| Release-only `pyproject.toml` | `pyproject.toml` | f625904 portiert; Namespace/Packaging/Releaseguards | keiner |
| Release-only `voice_stt_client/__init__.py` | `voice_stt_client/__init__.py` | f625904 portiert; Namespace/Packaging/Releaseguards | keiner |
| Release-only `voice_stt_client/__main__.py` | `voice_stt_client/__main__.py` | f625904 portiert; Namespace/Packaging/Releaseguards | keiner |
| Release-only `scripts/client_release_guard.py` | `scripts/client_release_guard.py` | f625904 portiert; Namespace/Packaging/Releaseguards | keiner |
| Release-only `tests/test_client_release_guard.py` | `tests/test_client_release_guard.py` | f625904 portiert; Namespace/Packaging/Releaseguards | keiner |
| Release-only `tests/test_client_release_workflow.py` | `tests/test_client_release_workflow.py` | f625904 portiert; Namespace/Packaging/Releaseguards | keiner |

Assets: alle neun Featuredateien (acht WAV + Attribution) bytegleich ins Paket verschoben. Requirements.txt unverändert. Neue Tests in test_cv2_000_integration.py sichern die Integrationsgrenzen. Alte Baselineassertions werden nicht pauschal entfernt; Namens-/Semantiknachzug siehe assertion-inventory.json und Report.

## Einzeln ersetzte Feature-Assertions (BASE-02/08/12)

AST-Inventar: [assertion-inventory.json](assertion-inventory.json). Keine Release-Testmethode fehlt. Fünf Featuremethodennamen wurden fachlich ersetzt:

| Alte Methode | Fachliche Regel und tatsächlicher Nachfolger |
| --- | --- |
| TestSessionConfigAndMetadata.test_unknown_user_field_rejects_complete_override | V1-kompatibel unbekannte Felder warnen, bekannte Präferenzen behalten: test_unknown_user_field_keeps_valid_override; zusätzlicher Profilroundtrip in IntegratedPreferences |
| TestSettingsDialog.test_dependency_visibility_tracks_mode_and_sound_toggle | V1-Editor bleibt sichtbar, inaktive Felder disabled: test_dependency_fields_remain_visible_but_disable_when_inactive; effektive Flags zusätzlich test_editor_sync_keeps_effective_legacy_trigger_flags |
| TestConfigValidation.test_non_mapping_yaml_root_falls_back_to_valid_defaults | Explizites Profil muss lesbar/mapping sein, kein stiller Defaultstart: test_non_mapping_explicit_yaml_fails_instead_of_silently_using_defaults; Env-Negativtest |
| SoundFeedbackTests.test_frozen_application_uses_pyinstaller_resource_root | Namespace-Ressourcenroot statt Toplevel: test_frozen_application_uses_bundled_package_root plus Wheel-/sdist-Smoke aller WAVs |
| TestDesktopApplication.test_hotkey_conflict_keeps_tray_core_operational | Enabled Manual-Hotkey darf bei vollständigem Konflikt nicht unbedienbar starten: test_hotkey_conflict_without_fallback_aborts_before_core_start und test_startup_replaces_conflicting_key_only_after_real_registration; deaktiviert/Wake-only weiterhin startbar, eigener Integrationsnachweis |

Alle Nachfolger bestehen in beiden vollständigen 1221-Testläufen. Controller/STTSession und Trigger-/Feedback-/Streamstart-Assertions sind per namespace-normalisiertem Vergleich qualifiziert: [source-preservation.txt](source-preservation.txt). Feature-Sounds und Attribution bytegleich. In test_history ausschließlich neue Pfadtestisolation ergänzt; History-DB-Verhalten bleibt vollständig getestet. Änderungen an Application/Settingsdialog zum Erhalt deaktivierter Hotkeys und effektiver Nullable-Flags sind notwendige Anschlusskorrekturen, keine V2-Lifecyclefeatures.
