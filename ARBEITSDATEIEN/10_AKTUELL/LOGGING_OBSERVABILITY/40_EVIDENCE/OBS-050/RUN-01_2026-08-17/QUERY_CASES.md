# OBS-050 – QUERY_CASES

Abfragefälle des `LocalLogProvider`, jeweils mit dem Test, der sie belegt.
Alle Fälle laufen gegen eine **echte** SQLite-Datei, die über den echten
`SQLiteLogStore` befüllt wurde — kein Double im Datenpfad.

## 1. Filter je Dimension

| # | Fall | Filter | Erwartung | Test |
|---|---|---|---|---|
| Q-01 | ohne Einschränkung | `QueryFilter()` | alle Zeilen, `AVAILABLE`, `complete=True` | `test_no_filter_returns_everything` |
| Q-02 | Channel | `channels=("audit",)` | nur `audit` | `test_channel_filter` |
| Q-03 | Levelmenge | `levels=("WARNING","ERROR","CRITICAL")` | nur diese Level | `test_level_filter_accepts_a_set_of_levels` |
| Q-04 | Quelle | `producer_kinds=("server",)` | nur Serverzeilen | `test_producer_kind_filter` |
| Q-05 | Scope | `scopes=("global",)` | nur `global` — das Ausdrucksmittel der späteren Adminabfrage | `test_scope_filter_expresses_the_admin_query` |
| Q-06 | Typpräfix | `type_prefix="client.injection"` | nur passende Typen | `test_type_prefix_filter` |
| Q-07 | Session | `session_id="s-1"` | zwei Zeilen | `test_context_filters_...` |
| Q-08 | Segment | `segment_id=3` | eine Zeile | `test_context_filters_...` |
| Q-09 | Activation | `activation_id="act-1"` | eine Zeile | `test_context_filters_...` |
| Q-10 | Korrelation | `correlation_id="trigger:cmd-1"` | eine Zeile | `test_context_filters_...` |
| Q-11 | Freitext über `message` | `text="abgelehnt"` | eine Zeile | `test_text_filter_covers_message_type_and_component` |
| Q-12 | Freitext über `type`/`component` | `text="hotkey"`, `text="ui."` | 1 bzw. 2 Zeilen | dito |
| Q-13 | Zeitfenster | `since`/`until` | `since` inklusive, `until` exklusiv | `test_time_range_since_is_inclusive_and_until_exclusive` |
| Q-14 | Replay ausblenden | `include_replayed=False` | replayte Zeile fehlt | `test_include_replayed_false_hides_replayed_records` |
| Q-15 | Kombination | `session_id` **und** `levels` | konjunktiv | `test_combined_filters_are_conjunctive` |

## 2. Leere, ungültige und feindselige Eingaben

| # | Fall | Erwartung | Test |
|---|---|---|---|
| Q-20 | leere Tupel | keine Einschränkung | `test_empty_tuple_filters_mean_no_restriction` |
| Q-21 | Tupel nur aus `""`/`None` | keine Einschränkung (nicht „nichts passt") | `test_blank_values_in_a_tuple_do_not_match_nothing` |
| Q-22 | unbekannter Wert | leere Seite, Zustand `AVAILABLE` | `test_unknown_filter_values_return_an_empty_but_available_page` |
| Q-23 | `%` im Freitext | wörtliches Prozentzeichen, **nicht** „alles" | `test_text_filter_escapes_like_wildcards` |
| Q-24 | `_` im Freitext | wörtlicher Unterstrich | `test_underscore_in_text_is_literal` |
| Q-25 | halb getippte Segment-ID (`"-"`) | keine Einschränkung, kein Fehler | `test_a_half_typed_segment_id_does_not_restrict` (UI) |
| Q-26 | fremder Cursor (`afterCursor:9`) | `ERROR`-Seite, keine Ausnahme | `test_invalid_cursor_is_an_error_page_not_an_exception` |
| Q-27 | `limit=0` | Standardgröße | `test_non_positive_limit_falls_back_to_the_default` |
| Q-28 | `limit > MAX_LIMIT` | gekappt, `complete=False` | `test_limit_is_capped_and_the_page_reports_it` |

Zu Q-23/Q-24: Ohne Escaping wäre ein `%` im Suchfeld ein Platzhalter — der
Filter bedeutete dann etwas anderes als das, was jemand getippt hat. Das
Escaping benutzt `ESCAPE '\'` und wird für Freitext **und** Typpräfix
angewandt.

## 3. Sortierung und Pagination

| # | Fall | Erwartung | Test |
|---|---|---|---|
| Q-30 | absteigend (Historie) | neueste zuerst, bei Wiederholung identisch | `test_descending_page_is_newest_first_and_deterministic` |
| Q-31 | aufsteigend (Live) | älteste zuerst | `test_ascending_order_is_the_live_tail_direction` |
| Q-32 | Seitenfolge | 25 Zeilen in Seiten à 10, keine Lücke, kein Duplikat | `test_keyset_pagination_walks_the_whole_result_without_gaps` |
| Q-33 | letzte Seite | `next_cursor is None` | `test_next_cursor_is_none_on_the_last_page` |
| Q-34 | genau passende Seite (25/25) | **keine** leere Folgeseite | `test_a_full_page_that_is_exactly_the_rest_reports_no_next_page` |
| Q-35 | Schreiben zwischen zwei Seiten | Seitenfolge bleibt stabil | `test_rows_written_between_pages_do_not_shift_the_sequence` |
| Q-36 | Live-Tail | nur Zeilen **nach** dem Cursor | `test_live_tail_only_returns_rows_after_the_cursor` |
| Q-37 | 750 Zeilen unter laufendem Schreiben | 750 eindeutige Zeilen über 8 Seiten | Probe `P-3` |

Q-34 ist der Grund für die „eine Zeile mehr"-Abfrage: ohne sie ließe sich
„die Seite ist voll" nicht von „es gibt noch mehr" unterscheiden, ohne ein
`COUNT` zu zahlen, das §8.1 ausschließt.

## 4. Detailansicht

| # | Fall | Erwartung | Test |
|---|---|---|---|
| Q-40 | `raw` in der Liste | immer `None` | `test_details_are_decoded_but_raw_is_not_loaded` |
| Q-41 | `fetch_raw` mit Payload | Mapping | `test_fetch_raw_returns_the_stored_payload` |
| Q-42 | `fetch_raw` ohne Payload | `None` | `test_fetch_raw_returns_none_without_a_payload` |
| Q-43 | `fetch_raw` unbekannte ID | `None`, kein Fehler | `test_fetch_raw_of_an_unknown_record_is_none_not_an_error` |
| Q-44 | `details` beschädigt | leeres Mapping statt Absturz | `_loads_mapping` (Fallback), Q-01 deckt den Normalfall |

## 5. Providerzustände

| # | Fall | Zustand | Test |
|---|---|---|---|
| Q-50 | kein `db_path` (`store_enabled: false`) | `UNAVAILABLE` | `test_no_db_path_means_unavailable` |
| Q-51 | Datei fehlt (Worker hat noch nichts geschrieben) | `UNAVAILABLE`, Datei wird **nicht** angelegt | `test_missing_database_is_unavailable_and_is_never_created` |
| Q-52 | Datei ohne `logs`-Tabelle | `UNAVAILABLE` | `test_a_file_without_the_logs_table_is_unavailable_not_an_error` |
| Q-53 | Datei beschädigt | `ERROR` mit kurzem Detail | `test_a_corrupt_file_is_an_error_page_not_an_exception` |
| Q-54 | `status()` nach gelöschter Datei | gecachter Wert, kein I/O | `test_status_is_cached_and_needs_no_io` |
| Q-55 | unbekannter Provider im Service | `UNAVAILABLE` | `test_unknown_provider_is_an_unavailable_page_not_an_exception` |
| Q-56 | Provider wirft in jeder Methode | `ERROR`, `fetch_raw → None`, andere Provider unberührt | `TestFailureIsolation` |

## 6. Leseverbindung

| # | Fall | Erwartung | Test |
|---|---|---|---|
| Q-60 | `PRAGMA query_only` | `1`; `DELETE` scheitert | `test_reader_connection_is_query_only`, Probe `P-8b` |
| Q-61 | Verbindungsleck | Datei nach Abfragen löschbar | `test_query_does_not_leave_a_connection_open` |
| Q-62 | Schreib-SQL im Query-Layer | kein `INSERT`/`UPDATE`/`DELETE`/`CREATE`/`DROP`/`VACUUM` | `test_no_write_statement_appears_in_the_query_modules` |
