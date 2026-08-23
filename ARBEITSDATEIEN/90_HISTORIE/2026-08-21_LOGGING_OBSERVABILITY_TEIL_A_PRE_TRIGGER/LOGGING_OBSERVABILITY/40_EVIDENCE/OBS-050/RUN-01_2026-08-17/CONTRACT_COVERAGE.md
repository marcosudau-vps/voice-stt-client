# OBS-050 – CONTRACT_COVERAGE

Jede Zeile nennt die normative Fundstelle, die Umsetzung und den Nachweis.
`CONTRACTS` = `LOGGING_CONTRACTS_FREEZE_V1.md`, `ARCH` =
`LOGGING_ARCHITEKTUR_FREEZE_V1.md`, `DEC` = `LOGGING_DECISIONS_FREEZE_V1.md`.

## 1. Query-Layer

| Vorgabe | Fundstelle | Umsetzung | Nachweis |
|---|---|---|---|
| Eigene, kurzlebige Leseverbindungen | CONTRACTS §5.4 | `LocalLogProvider._connect`, in `finally` geschlossen | `test_query_does_not_leave_a_connection_open` |
| `PRAGMA query_only = ON`, **kein** `mode=ro` | CONTRACTS §5.4, W-13 | `_connect` setzt `busy_timeout` und `query_only` | `test_reader_connection_is_query_only`, Probe P-8b |
| Keyset-Pagination statt OFFSET | CONTRACTS §5.7 | `id < :after` / `id > :after`, `ORDER BY id` | `test_keyset_pagination_walks_the_whole_result_without_gaps`, `test_rows_written_between_pages_do_not_shift_the_sequence`, Probe P-3 |
| `raw_json` nicht in der Listenabfrage | CONTRACTS §5.7 | `_LIST_COLUMNS` ohne `raw_json`; `fetch_raw` einzeln | `test_details_are_decoded_but_raw_is_not_loaded`, Probe P-2 |
| Nur Platzhalter, keine Interpolation | CONTRACTS §5.7 | jede Filterbedingung bindet `?` | `_build_list_query`, Filtertests inkl. LIKE-Escaping |
| Filterdimensionen des Vertrags | CONTRACTS §8 | alle Felder von `QueryFilter` ausgewertet | `QUERY_CASES.md`, `TestFilters` |
| Opaker Cursor | CONTRACTS §8.1 | `"id:<n>"`, `encode_/decode_cursor` | `test_cursor_is_opaque_not_a_bare_number` |
| `query()` wirft nie | CONTRACTS §8.1 | jeder Pfad liefert eine `QueryPage` | `TestRawAndFailureStates`, `test_a_raising_provider_never_reaches_the_caller` |
| `status()` ohne I/O, gecacht | CONTRACTS §8 | Feld `_status`, nach jeder Abfrage aktualisiert | `test_status_is_cached_and_needs_no_io` |
| `LogQueryService` ist eine Registry | ARCH §10.3 | `register`/`unregister`/`providers`/`query`/`fetch_raw` | `TestRegistry` |
| Kein `subscribe`/`stream`/`count`/`delete` | CONTRACTS §8.1 | nicht vorhanden | `test_the_query_layer_has_no_subscribe_stream_count_or_delete` |
| Kein `ProviderCapabilities` in V1 | DEC FD-S3 | nicht vorhanden | `test_provider_capabilities_does_not_exist_in_v1` |
| `AUTH_REQUIRED` existiert, wird nie erzeugt | ARCH §10.1 | in `ProviderState` (OBS-010) | `test_auth_required_exists_although_v1_never_produces_it` |
| `scopes=("global",)` als Ausdrucksmittel | ARCH §10.3 | Spaltenfilter `scope IN (...)` | `test_scope_filter_expresses_the_admin_query` |
| Query-Layer schreibt nie (O-14) | ARCH §1.2 | kein Schreib-SQL, Datei wird nie angelegt | `test_no_write_statement_appears_in_the_query_modules`, `test_missing_database_is_unavailable_and_is_never_created`, Probe P-8a |

## 2. UI

| Vorgabe | Fundstelle | Umsetzung | Nachweis |
|---|---|---|---|
| Eigenes, nicht-modales `LogWindow` | CONTRACTS §9.1 | `LogWindow(QWidget)`, `Qt.WindowType.Window` | `test_window_is_non_modal_and_top_level` |
| Erreichbar über Tray **und** Logging-Tab | CONTRACTS §9.1 | `TrayController.logs_action`, `show_logs_button` | `test_with_a_manager_the_tray_opens_the_log_window`, `test_show_logs_button_emits_the_request` |
| Health-Statuszeile im Fenster | CONTRACTS §9.1/§11.2 | `LogPage.status_label`, `QTimer` 1 s | `test_status_line_shows_provider_and_health`, Probe P-4b |
| Query nicht über `CoreBridge`; eigener Executor `max_workers=1` | CONTRACTS §9.2 | `LogQueryController` | `test_the_query_thread_is_not_the_qt_thread` |
| Ergebnis per Signal in den Qt-Thread | CONTRACTS §9.2 | `page_ready`/`raw_ready` | `test_query_runs_off_the_qt_thread_and_answers_by_signal` |
| Filterwechsel entprellt, 300 ms | CONTRACTS §9.2 | `LogFilterBar._debounce` | `test_filter_change_is_debounced` |
| Live als tailende Abfrage, 250 ms, `LIMIT 500`, kein Ringbuffer | CONTRACTS §9.2, DEC FD-S1 | `LogPage._tail`, `LIVE_INTERVAL_MS`, `LIVE_PAGE_SIZE` | `TestNoRingBuffer`, `test_live_mode_tails_ascending_over_the_same_provider`, Probe P-4 |
| Kein Signal je Record | CONTRACTS §9.2 | eine Abfrage je Takt, Seiten statt Einzelsignale | `test_live_mode_...` (eine Abfrage je Tick) |
| Sieben Spalten | CONTRACTS §9.3 | `COLUMNS` | `test_seven_frozen_columns_in_the_frozen_order`, `test_ids_are_not_columns` |
| `QAbstractTableModel` + `QTableView` | CONTRACTS §9.3 | `LogTableModel`, `LogPage.table` | `TestLogTableModel` |
| Seitengröße 200, „Weitere laden" **und** automatisches Nachladen | CONTRACTS §9.3 | `DEFAULT_PAGE_SIZE`, `more_button`, `_on_scrolled` | `test_load_more_pages_backwards_with_the_cursor` |
| Live/Historie als Umschalter, kein Mischbetrieb | CONTRACTS §9.3 | `mode_box`, zwei getrennte Pfade | `test_no_mixed_mode` |
| Auto-Scroll an, schaltet beim Hochscrollen ab | CONTRACTS §9.3 | `autoscroll_box`, `_on_scrolled` | `test_scrolling_up_in_live_mode_turns_auto_scroll_off` |
| Detail als `QSplitter`, `details` Baum, `raw` JSON, bei Auswahl nachgeladen | CONTRACTS §9.3 | `LogPage.splitter`, `LogDetailView` | `TestLogDetailView`, `test_selection_loads_the_detail_and_the_raw_payload` |
| Kontextmenü mit vier Aktionen | CONTRACTS §9.3 | `_show_context_menu` | `test_context_menu_actions_set_the_filter`, `UI_ACCEPTANCE.md` |
| Activation-Filter mit Unzuverlässigkeitshinweis | ARCH §3.4, DEC FD-C2 | sichtbarer Hinweis + Tooltip + Menütext | `test_activation_filter_carries_the_unreliability_hint` |
| Nur Zeilenfarbe nach Level | CONTRACTS §9.3 | `_LEVEL_COLORS` | `test_only_warning_and_above_get_a_row_colour` |
| Kein Export in V1 | CONTRACTS §9.3 | nicht vorhanden | `UI_ACCEPTANCE.md` (Non-Scope-Liste) |
| `hide()` statt `close()`, Geometrie in `QSettings` | CONTRACTS §9.3 | `closeEvent`, `GEOMETRY_KEY` | `test_closing_hides_instead_of_closing`, `test_geometry_is_stored_in_qsettings` |
| Verborgenes Fenster fragt nicht ab | CONTRACTS §9.1 | `hideEvent` → `page.stop()` | `test_hiding_stops_the_polling` |

## 3. Einstellungen

| Vorgabe | Fundstelle | Umsetzung | Nachweis |
|---|---|---|---|
| Sechster Tab „Logging & Diagnose" | CONTRACTS §9.1 | `TAB_NAMES`, Kategorie in den Metadaten | `test_the_dialog_has_six_tabs_with_logging_last` |
| Neun Einträge mit ihren Apply-Policies | CONTRACTS §10.3 | `LOGGING_SETTING_DEFINITIONS` | `TestSettingsMetadata` |
| `db_path`, `queue_size`, `batch_size`, `flush_interval_s`, `max_db_bytes` nur in `config.yaml` | CONTRACTS §10.3 | nicht in den Definitionen | `test_config_only_fields_are_absent_from_the_dialog` |
| `store_enabled`/`db_path` sind `APP_RESTART` | CONTRACTS §10.3 | Policy gesetzt; Manager wendet sie nicht an | `test_store_enabled_change_reports_app_restart`, `test_store_enabled_and_db_path_are_not_applied_at_runtime` |
| `file_sink_dir` nur sichtbar bei aktivem Sink | CONTRACTS §10.3 | `visible_when` | `test_file_sink_dir_is_only_visible_with_the_sink_enabled` |
| Ein Levelwert speist Handler **und** Ingress | ARCH §8.7 | `register_log_handler` + `_on_config_applied` | `test_handler_level_follows_the_single_config_value`, Probe P-5 |
| `apply_config` in der Apply-Kette, nicht werfend, ohne Rückgabe | CONTRACTS §10.4 | eine Zeile nach `_install_runtime_config` | `TestApplyChain` |
| Harte Regel: keine Reconnect-/Audio-Flags | CONTRACTS §10.4 | Flags aus `server`/`session`/`audio` berechnet | `test_pure_observability_change_triggers_no_reconnect` (Fake-Session, deren `reconfigure` durchfällt) |
| `_from_dict`-Sonderbehandlung (N-12) | CONTRACTS §10.2 | bereits in OBS-030 vorhanden | `test_nested_section_survives_a_save_load_roundtrip` |
| P-8: kein Pfad außerhalb des Benutzerprofils | CONTRACTS §4.3 | `validate()` + `ObservabilityManager._resolve_profile_path` | `test_a_path_outside_the_user_profile_is_rejected` |
| Beschreibung nennt auch technische Logzeilen | DEC FD-D1 | Text der Option | `test_the_transcript_option_names_the_surprising_part` |
| „Diagnosehistorie löschen" am Store | DEC FD-S4, CONTRACTS §5.8 | `manager.clear_history()` → Worker → `store.clear()` | `test_clear_goes_through_the_manager_not_the_query_layer`, Probe P-6 |
| „Logs anzeigen" im Logging-Tab | CONTRACTS §10.3 | `show_logs_button` | `test_show_logs_button_emits_the_request` |

## 4. Architekturinvarianten

| Invariante | Umsetzung | Nachweis |
|---|---|---|
| O-01 Logging hat keine Runtime-Autorität | die Ansicht liest; kein Rückgabewert steuert etwas; `apply_config` liefert nichts | `TestApplyChain`, `TestLoggingWorksWithoutTheLogView` |
| O-03 kein produzierender Pfad wartet auf I/O | Query auf eigenem Thread; Warten nur beim Fensterabbau | `test_the_query_thread_is_not_the_qt_thread` |
| O-04 begrenzte Puffer | `LogTableModel.max_rows` schneidet vorn ab | `test_row_count_is_bounded_and_drops_the_oldest` |
| O-05 Failure Isolation | Provider- und Servicefehler werden zu Anzeigezuständen | `TestFailureIsolation`, `test_a_raising_service_never_reaches_the_qt_thread` |
| O-10 die UI kennt SQLite nicht | Importprüfung über alle sechs UI-Module | `test_ui_logs_never_imports_storage_or_sqlite3` |
| O-14 Schreibmonopol | kein Schreib-SQL, keine Datei-Erzeugung, Löschen am Store | `TestReadOnlyConnection`, Probe P-6/P-8 |
| ARCH §5.1 Modulstruktur | drei Query- und sechs UI-Module am eingefrorenen Ort | `TestFrozenModuleStructure` |
| ARCH §5.2 Importrichtung | `query` ohne `ingress`/`worker`/`manager`; `core/**` ohne PySide6 | `TestImportDirection` |
| ARCH §6.2(b) Managerlebensdauer | `DesktopApplication` stoppt ihn nie | `test_desktop_application_never_stops_the_manager` |
| ARCH §10.1 kein Vorgriff auf Teil B | keine Admin-, Remote- oder HTTP-Begriffe in den neuen Modulen | `TestNoLaterWorkPackageIsAnticipated` |
| Logging läuft ohne UI | Subprozess ohne jeden `ui.`/PySide6-Import schreibt und liest | `test_records_are_written_with_no_ui_imported`, Probe P-7 |

## 5. Bewusst nicht umgesetzt

| Gegenstand | Grund |
|---|---|
| Neuer Recordtyp für das Löschen der Historie | §12 ist „die verbindliche Liste"; ein neuer Typ wäre eine Vertragserweiterung ohne `DECISION REQUIRED`. Der Record entstünde außerdem in genau dem Store, der geleert wird. |
| Neuer Zähler in `LoggingHealthSnapshot` | ARCH §7.3 ist eingefroren (Lehre aus dem OBS-030-Cleanup). |
| Neues Konfigurationsfeld | CONTRACTS §10.1 ist eingefroren; die Ansicht braucht keines. |
| `ProviderCapabilities`, Export, Filterpresets, Charts | ARCH §11.1/§11.2, CONTRACTS §9.3 — ausdrücklich nicht V1. |
| Remote-/Admin-Provider, „alle Sessions"-Schalter | ARCH §10.1: nicht einmal deaktiviert. |
