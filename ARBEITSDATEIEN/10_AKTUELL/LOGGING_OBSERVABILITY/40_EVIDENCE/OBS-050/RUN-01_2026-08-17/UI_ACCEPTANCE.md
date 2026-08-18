# OBS-050 – UI_ACCEPTANCE

Abnahmepunkte der V1-Logansicht und des sechsten Settings-Tabs. Alle
automatisierten Nachweise laufen offscreen (`QT_QPA_PLATFORM=offscreen`),
wie die bestehenden UI-Tests des Repositories.

## 1. Aufbau

```text
LogWindow (nicht-modal, eigenes Fenster, Geometrie in QSettings)
└── LogPage
    ├── LogFilterBar        Quelle · Channel · ab Level · Typ-Präfix · Text
    │                       Session · Activation ⚠ · Segment · Korrelation
    │                       Replayte Records anzeigen
    ├── Steuerzeile         Quelle (Provider) · Modus (Historie|Live) ·
    │                       Automatisch scrollen · Neu laden · Weitere laden
    ├── QSplitter
    │   ├── QTableView + LogTableModel   sieben Spalten
    │   └── LogDetailView                Kopf · details (Baum) · raw (JSON)
    └── Statuszeile         Providerzustand · Zeilenzahl · Health-Snapshot
```

## 2. Abnahmepunkte

| # | Punkt | Ergebnis | Nachweis |
|---|---|---|---|
| A-01 | Fenster ist nicht modal und ein eigenes Top-Level-Fenster | erfüllt | `test_window_is_non_modal_and_top_level` |
| A-02 | Öffnen über Tray-Menü | erfüllt | `test_with_a_manager_the_tray_opens_the_log_window` |
| A-03 | Öffnen über „Logs anzeigen" im Logging-Tab | erfüllt | `test_show_logs_button_emits_the_request` |
| A-04 | Fenster wird einmal erzeugt und wiederverwendet | erfüllt | `test_the_window_is_created_once_and_reused` |
| A-05 | Schließen versteckt, zerstört nicht | erfüllt | `test_closing_hides_instead_of_closing` |
| A-06 | Geometrie überlebt das Schließen | erfüllt | `test_geometry_is_stored_in_qsettings` |
| A-07 | verborgenes Fenster fragt nicht mehr ab | erfüllt | `test_hiding_stops_the_polling` |
| A-08 | sieben Spalten in der eingefrorenen Reihenfolge | erfüllt | `test_seven_frozen_columns_in_the_frozen_order` |
| A-09 | IDs sind Filter, keine Spalten | erfüllt | `test_ids_are_not_columns` |
| A-10 | Zeilenfarbe nur ab WARNING | erfüllt | `test_only_warning_and_above_get_a_row_colour` |
| A-11 | Historie lädt die neueste Seite zuerst, chronologisch dargestellt | erfüllt | `test_history_mode_loads_the_newest_page_first` |
| A-12 | „Weitere laden" blättert per Cursor | erfüllt | `test_load_more_pages_backwards_with_the_cursor` |
| A-13 | am Listenende wird automatisch nachgeladen | erfüllt | `_on_scrolled` → `load_more`, `test_load_more_does_nothing_without_a_next_page` |
| A-14 | Live-Modus wächst ohne Ringbuffer | erfüllt | `test_live_mode_tails_ascending_over_the_same_provider`, Probe P-4 |
| A-15 | kein Mischbetrieb | erfüllt | `test_no_mixed_mode` |
| A-16 | Auto-Scroll schaltet beim Hochscrollen ab | erfüllt | `test_scrolling_up_in_live_mode_turns_auto_scroll_off` |
| A-17 | Filterwechsel entprellt und ersetzt die Seite | erfüllt | `test_filter_change_is_debounced`, `test_filter_change_replaces_the_page_and_reaches_the_provider` |
| A-18 | Auswahl zeigt Details und lädt `raw` nach | erfüllt | `test_selection_loads_the_detail_and_the_raw_payload` |
| A-19 | verspätetes `raw` einer abgewählten Zeile wird verworfen | erfüllt | `test_raw_arrives_separately_and_only_for_the_current_record` |
| A-20 | fehlendes `raw` wird benannt, nicht leer gelassen | erfüllt | `test_missing_raw_is_stated_not_left_blank` |
| A-21 | Kontextmenü setzt Session/Activation/Segment/Typ/Korrelation | erfüllt | `test_context_menu_actions_set_the_filter`, `_show_context_menu` |
| A-22 | Activation-Filter trägt den Unzuverlässigkeitshinweis | erfüllt | `test_activation_filter_carries_the_unreliability_hint` |
| A-23 | Statuszeile zeigt Providerzustand **und** Health | erfüllt | `test_status_line_shows_provider_and_health`, Probe P-4b |
| A-24 | defekter Health-Provider bricht die Statuszeile nicht | erfüllt | `test_a_raising_health_provider_does_not_break_the_status_line` |
| A-25 | veraltete Antwort wird verworfen | erfüllt | `test_a_stale_answer_is_dropped` |
| A-26 | sechs Tabs, „Logging & Diagnose" als sechster | erfüllt | `test_the_dialog_has_six_tabs_with_logging_last` |
| A-27 | jede der neun Einstellungen hat einen Editor | erfüllt | `test_every_logging_setting_has_an_editor` |
| A-28 | Löschen fragt vorher nach | erfüllt | `test_clear_button_asks_before_deleting` |
| A-29 | Löschen läuft über den Manager und meldet die Anzahl | erfüllt | `test_clear_goes_through_the_manager_not_the_query_layer` |
| A-30 | fehlgeschlagenes Löschen wird gemeldet, nicht geworfen | erfüllt | `test_a_failing_clear_is_reported_not_raised` |
| A-31 | ohne Manager: Tray-Eintrag deaktiviert, Dialog meldet es | erfüllt | `test_without_a_manager_the_tray_entry_is_disabled`, `test_clear_without_a_manager_says_so` |
| A-32 | Abbau gibt Fenster und Query-Thread frei | erfüllt | `test_shutdown_releases_the_log_window` |
| A-33 | die UI stoppt den Manager nie | erfüllt | `test_desktop_application_never_stops_the_manager` |

## 3. Bewusst **nicht** in V1

| Gegenstand | Fundstelle |
|---|---|
| Export | CONTRACTS §9.3 („Export: nicht in V1") |
| gespeicherte Filterpresets, komplexe Farbregeln, Charts | ARCH §11.1 |
| Remote-/Admin-Historie, „alle Sessions" | ARCH §10.1, §11.1 |
| Mischbetrieb Live + Historie | CONTRACTS §9.3 |
| Signal je Record | CONTRACTS §9.2 |
| Sortierung nach anderen Spalten als `id` | ARCH §3.2 (`logs.id` ist die lokale Ordnung; `source_timestamp` ist nie Primärsortierung) |

## 4. Manuelle Restpunkte für OBS-060

Diese Punkte sind offscreen **nicht** belastbar prüfbar und gehören in die
manuelle Abnahme des Härtungspakets:

1. Optischer Eindruck von Spaltenbreiten, Schriftgrößen und Zeilenfarben auf
   einem echten Desktop (hell/dunkel).
2. Kontextmenü als echtes Popup inklusive Mausbedienung —
   automatisiert wird der Filter direkt über `apply_context` gesetzt.
3. Verhalten des Live-Modus über längere Zeit unter echter Diktatlast
   (Zeilenzuwachs, Speicher, gefühlte Reaktionszeit).
4. Fenstergeometrie über einen echten Prozessneustart hinweg (`QSettings` mit
   dem Produktions-Organisationsnamen).
5. Zusammenspiel mit dem Tray auf einem Rechner mit mehreren Bildschirmen.
