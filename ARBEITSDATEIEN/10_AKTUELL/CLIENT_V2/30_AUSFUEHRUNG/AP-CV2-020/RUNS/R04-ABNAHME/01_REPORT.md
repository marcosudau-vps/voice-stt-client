# AP-CV2-020 / R04 – erneute unabhängige Abnahme

**Verdict: ROOT_PASS.** Beide offenen R02-Pflichtfindings **CV2-020-R02-F01 und CV2-020-R02-F02 unabhängig geschlossen**. Neue offene Pflichtfinding-IDs: **keine**. Stand 2026-10-12, Europe/Berlin.

[Originalauftrag](00_PROMPT_ORIGINAL.md) · [Evidenzindex](EVIDENCE/INDEX.md) · [R02-Negativreview](../R02-ABNAHME/01_REPORT.md) · [R03-Korrektur](../R03-KORREKTUR/01_REPORT.md) · [PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4)

## Gitidentitäten, Umfang und Rolle

- Repo `marcosudau-vps/voice-stt-client`; Base `feat/client-v2` auf `91065f5f7715aa6653ec5335d9e757b6ef97a067`, Kandidatenbranch `work/client-v2/ap-cv2-020`.
- **reviewed_sha:** `6d74c1ae06643e026834bc9164028bec908e26df`; **reviewed_tree:** `f8a57f79c6bf61d7b079a41a53662adeac34c546` (beides Kandidat **vor** dem späteren R04-Reviewdocs-Commit).
- **canonical_parent:** `91065f5f7715aa6653ec5335d9e757b6ef97a067`; **server_sha:** `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
- Getesteter korrigierter Produktcommit `98ab3c0fc5c935019d81d6d6acb1423185cb4793`, Tree `c394dbe3d75086132234cb987469ee6639647af6`. Git-Compare zwischen qualifiziertem Produktcommit und geprüftem Head: genau ein zusätzlicher Commit, 25 ausschließlich administrative/Traceability/Logdateien, **keine Produkt-, Test- oder testrelevanten Konfigurationsänderungen**. Der volle kumulative PR-Diff vom Parent umfasst 64 Dateien; Produktdateien und der vollständige relevante Testcode wurden SHA-gebunden kontrolliert.
- Vorgänger AP-CV2-010 ist durch [tatsächliche Einzelaggregation/PR #3](../R01-UMSETZUNG/EVIDENCE/predecessor-canonicalization.json) bereits kanonisch enthalten; R02-Review und R03-Korrektur im selben PR behalten ihre historischen Identitäten.
- Unabhängiger GitHub-Connector-Review; es wurde **keine** eigene Windows-Vollsuite ausgeführt. Codekontrolle, Quell-/Testmethoden, volle Testlogs/Hashprüfung und Remote-CI bilden die Abnahme, wie die aktuelle Reviewer-Skill ausdrücklich erlaubt.

## Unabhängiger Finding-Recheck

| Finding | Code und neue Regression | Entscheidung |
| --- | --- | --- |
| **CV2-020-R02-F01** | `v2_transport.py:193–205`: `InvalidStatus` wird vor `InvalidHandshake` gefangen; 408 und 5xx mit Backoff, 429 mindestens 10s Kapazitätsbackoff, permanente Ablehnungen/ungültiger Handshake mit redigiertem BLOCKED. Neue Tests `test_http_upgrade_transient_errors_backoff_then_ready` (408/500/502/503/504), `test_http_upgrade_rate_limit_has_capacity_backoff_and_bounded_stop` (429) und `test_http_upgrade_auth_configuration_and_invalid_handshake_block_once` (301/400/401/403/404/405/426/InvalidHandshake/InvalidURI) sowie bounded Shutdown, keine alte Domainbindung. | **CLOSED / PASS** |
| **CV2-020-R02-F02** | `v2_transport.py:285–289`: `_silent_failures=0` erst nach vollem Bootstrap einschließlich Suppression-Ack unmittelbar vor READY. `test_4408_retry_budget_resets_only_after_ready_between_episodes`: 4408→CONFIGURING (Budget bleibt verbraucht)→READY→1011→4408→READY; alte Commands/Futures/Callbacks und stabile clientRunId geprüft. `test_4408_only_one_retry_with_stable_process_run_id` prüft unverändert 4408→4408 ohne READY als BLOCKED. | **CLOSED / PASS** |

Der Korrekturlauf hat die neuen Reproduktionen **vor** der Änderung auf der alten Produktfassung mit `EXPECTED_FAIL` (7 Assertion-Failures, 9 Errors) ausgewiesen und nachher mit `-W error` grün erneut ausgeführt. Dieser Vorher-/Nachher-Nachweis, die Kontrollflussstelle und die fehlenden Nebenwirkungen wurden nicht allein aus Selbstbehauptungen übernommen.

## Weitere fachliche Abnahme des kumulativen Produkts

Unveränderte R01-/R02-Codeabschnitte erneut mit dem vollständigen Parentdiff und der neuen Korrektur abgeglichen: Hello ist erstes Clientframe nach Socketopen; vor Admission/erfolgreichem Bootstrap sind PCM und Nutzercommands gesperrt; fehlender/abgelehnter Bootstrap verbleibt blockiert. `CommandTracker` korreliert Session/Generation/CommandId, speichert unveränderte Retrybytes, begrenzt Inflight/Waiter auf 16, erzwingt Serialisierung gleicher Commandtypen und beendet Futures/Queues bei Verlust. Alle 15 Ackresultcodes und Advice, Event-vor-Ack, alte Versionen, doppelte Replays, Session-/Generationguards, Suppression und Close/Cancel/Shutdown besitzen zugeordnete Tests. Kein V1-Domainping, kein automatisches Nachinjizieren eines verlorenen Finals. Logging bleibt redigiert/isoliert.

### Requirement-Zuordnung

Alle 28 Paket-IDs unter K-01/K-04 gegen die tatsächlichen, im Kandidaten vorhandenen `tests.test_v2_transport`-Methoden, [Requirements-JSON](../../../../PLANUNG/REFERENZ/TRACEABILITY/requirements.json) und [Matrix](../../../../PLANUNG/REFERENZ/TRACEABILITY/TRACEABILITY_MATRIX.md) geprüft. Die Tabellenmethoden stehen im vollständigen R03-Targeted-Log/Source und werden bei PASS nicht umgedeutet.

| ID | geprüfte tatsächliche Testmethoden (Klassenpräfix ausgelassen) | Ergebnis |
| --- | --- | --- |
| ACK-01 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-02 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-03 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-04 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-05 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-06 | `test_all_fifteen_ack_results_complete_once_without_new_commands`; `test_closing_input_ack_blocks_more_refresh_for_same_activation` | PASS |
| ACK-07 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-08 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-09 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-10 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-11 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-12 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-13 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-14 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-15 | `test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-16 | `test_event_before_old_ack_and_duplicate_ack_do_not_project` | PASS |
| ACK-17 | `test_fake_ack_wait_retry_identical_and_revision_guard`; `test_retry_exact_bytes_once_and_timeout_no_new_id` | PASS |
| ACK-18 | `test_eventless_payload_completion_and_snapshot_replay` | PASS |
| ACK-19 | `test_eventless_payload_completion_and_snapshot_replay`; `test_same_domain_serialized_other_domain_independent` | PASS |
| ACK-20 | `test_foreign_session_and_generation_never_confirm_or_publish`; `test_disconnect_finishes_pending_and_domain_waiters`; `test_cancel_request_stalled_send_and_audio_loss_invalidate`; `test_capacity_cancellation_and_close_clear_waiters` | PASS |
| ACK-21 | `test_reconnect_new_binding_ids_empty_queue_and_suppression_retained` | PASS |
| RECONNECT-01 | `test_close_codes_block_or_reconnect_with_capacity_floor`; `test_malformed_admission_second_hello_and_binary_server_block` | PASS |
| RECONNECT-02 | `test_4408_only_one_retry_with_stable_process_run_id`; `test_4408_retry_budget_resets_only_after_ready_between_episodes` | PASS |
| RECONNECT-03 | `test_handshake_refusal_config_capacity_and_incompatible`; `test_close_codes_block_or_reconnect_with_capacity_floor`; `test_http_upgrade_auth_configuration_and_invalid_handshake_block_once`; `test_http_upgrade_rate_limit_has_capacity_backoff_and_bounded_stop` | PASS |
| RECONNECT-04 | `test_reconnect_new_binding_ids_empty_queue_and_suppression_retained` | PASS |
| RECONNECT-05 | `test_reconnect_new_binding_ids_empty_queue_and_suppression_retained`; `test_foreign_session_and_generation_never_confirm_or_publish` | PASS |
| RECONNECT-06 | `test_admission_and_connect_timeout_no_hanging_run`; `test_retry_exact_bytes_once_and_timeout_no_new_id`; `test_close_timeout_aborts_underlying_transport`; `test_cancel_connect_bootstrap_and_stop_caller_leave_no_tasks`; `test_http_upgrade_transient_errors_backoff_then_ready`; `test_http_upgrade_auth_configuration_and_invalid_handshake_block_once`; `test_http_upgrade_rate_limit_has_capacity_backoff_and_bounded_stop` | PASS |
| RECONNECT-07 | `test_transport_ping_only_and_no_final_inference_timer` | PASS |

**Alle 28 Paketrequirements: PASS.** Frühere Selbstchecks bleiben historische Umsetzungsevidenz; unabhängiger R04-Befund ist separat mit reviewed_sha und diesem Report verknüpft. Kein neuer, unbelegter Hardware- oder Folgepaketowner wird hierdurch als fertig markiert.

## Unabhängig validierte Fremdnachweise

| Pflichtfall | geprüfter Beleg und genaue Grenze | R04-Wertung |
| --- | --- | --- |
| Vollständige Windows-Regression | Windows 11 Build 26300/AMD64, Python 3.12.10, Projektvenv und offscreen; `python -m unittest discover -s tests -p 'test_*.py'`, Exit 0, **1294 Tests/97.328 s, OK**; vollständiger SHA-gebundener Log | **PASS (fremd durchgeführt, unabhängig geprüft)** |
| Transport-/Codec-Regression | `python -W error -m unittest tests.test_v2_transport tests.test_v2_protocol -v`; Exit 0, **61 Tests/4.445 s, OK** inklusive aller neuen Findingtests | **PASS (fremd durchgeführt, unabhängig geprüft)** |
| Echte Serverintegration | `scripts/check_v2_server_transport.py`, lokaler echter TCP/WS-Transport über die unveränderte gepinnte FastAPI-App und Produktionroute, **21 Fälle PASS**, 46 gegen Servergit bytegeprüfte Original-Pythonquellen, Exit 0. Nur GateAwareRecorder/AutoScheduler (Hardware/Modelle) und benannter noch nicht implementierter Clientsettings/Audio-Bootstrap werden ersetzt | **PASS (fremd durchgeführt, unabhängig geprüft)** |
| Kompilation/Diff | `compileall -q voice_stt_client scripts tests`, Exit 0; administrativer `git diff --check` Exit 0 | **PASS (externer Lauf/Beleg geprüft)** |
| Remote-CI, exakt eingereichter Head | [GitHub Actions Run 38183803142](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38183803142), Job 114601742905: `head_sha=6d74c1ae06643e026834bc9164028bec908e26df`, abgeschlossen `success`; komplette Suite, Compileall, EXE-Build/Smoke, Wheel-/sdist-Build und installierter Namespace-/Ressourcen-Smoke jeweils erfolgreich | **PASS (direkt geprüft)** |
| Eigene Windows-/Hardware-/ASR-/Qt-Ausführung | kein lokaler Reviewer-Windows-Test; echte Hardware/ASR/Clipboard/Gesamtprozessqualifikation sind späteren Paketen zugeordnet | **NOT_RUN / SKIPPED_EXPECTED**, keine Pflichtlücke für AP-CV2-020 |

**Hashprüfung unabhängig ausgeführt:** Vier vollständige R03-Pflichtlogs am eingereichten SHA über SHA-gebundenes GitHub-File gelesen und deren UTF-8-SHA256 mit `windows-validation.json` abgeglichen: targeted `1496bc06…`, Servercheckpoint `33c48c33…`, compileall `e3b0c442…`, Vollsuite `02ecbdb4…`, alle vier identisch. Kein breit übersprungener Test; der absichtlich ausgelöste UI-Traceback ist erwarteter negativer Test und die Vollsuite endet `OK`.

## Technische Grenzen, Status und nächste Aktion

AP-CV2-020 ist ein eigenständiger, headless V2-Transport mit offengelegten Bootstrap-/Settings-/Audio-/Mirror-Ports. Die App-Komposition folgt CV2-100; reale Gerätesmokes/ASR/Qt/Clipboard und finales Crossrepo-Paar gehören ihren expliziten Folgepaketen. Kein Produkt- oder Serverfix aus dieser Abnahme; Server-Distributed bleibt offen.

**Verdict ROOT_PASS; workflowPhase WAITING_FOR_APPROVAL; openFindingIds [].** F01/F02 sind **nach belegtem Recheck unabhängig geschlossen**, keine neuen Pflichtfindings. Dieses Urteil ist **keine** menschliche Übernahmefreigabe: `humanApproval=null`, kein Merge, kein AP-CV2-030. Nächste Aktion ist allein ein gesonderter ausdrücklicher menschlicher Prompt zur Übernahme des überprüften PR #4 mit Prüfung des finalen administrativen Head-/Base-Diffs, anschließend genau einem kanonischen Aggregatecommit. Ein zukünftiger R04-Reviewdocs-Commit ändert nicht den geprüften Produkt-SHA `6d74c1ae06643e026834bc9164028bec908e26df`.
