# AP-CV2-020 / R01 – Umsetzung

Status **REVIEW_READY**. Start 2026-10-11, Fortsetzung/Qualifikation 2026-10-12 (Europe/Berlin).
[Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md).

Parent `91065f5f7715aa6653ec5335d9e757b6ef97a067`, Branch `work/client-v2/ap-cv2-020`, Server ada13b0.
Keine fremde WIP, kein offener Paket-PR. AP010-R02-PASS und tatsächliche
menschliche Freigabe/Einzel-Squash vor Start geprüft; [Nachmergebeleg](EVIDENCE/predecessor-canonicalization.json).
Workflowweite Kandidaten-Gitrechte aus dem AP000-Originalauftrag, keine
kanonische Übernahme, Tags/Releases/Serveränderung oder Cleanup beauftragt.

## Ausgangssuite und Umsetzungsskizze

Vor erster Produktänderung vollständige Windowsbaseline:1263 Tests OK,96.614s,
Exit0; [vollständiger Log](EVIDENCE/baseline-full-unittest.txt), [Exit](EVIDENCE/baseline-exit.txt).
Skizze: Hello mit temporär gesperrten Triggern; injizierter Bootstrap und
Freigabe nach Acks; sessiongebundener Pendingtracker mit bytegleichem Retry;
Watermarks schützen Event-vor-Ack; bounded Cancellation/Close/Backoff.

## Ergebnis und Schnittstellen

V2STTSession/V2TransportConfig/SessionBinding/TransportStatus; CommandTracker,
CommandCompletion/AckAdvice und lokale CommandFailure-Untertypen.
[Vollständiger API-/Callback-/Guardvertrag](../../../../../../../docs/protocol-v2-transport.md).
Alle Methoden auf dem asyncio-Coreloop, kein Qt-/Threadzugriff. Callbacks in
Empfangsreihenfolge; alte Bindings/Fremdsessions verworfen, keine Domainphase
aus altem Ack. Snapshotreplay bleibt sichtbar. Ereignislose Acks tragen
Originalpayload und projectable-Flag an den späteren Mirror.

Separate V2-Klasse statt halber Umstellung des bestehenden STTSession/Core;
CV2-030/040/050/070 verwenden deren Schnittstellen, CV2-100 komponiert die App.
Neue Default-URL /ws/v2, typed Legacy-URL-Sperre ohne Profilschreiben/Hostwechsel.
Keine History-/Credentialmigration, neue Audioqueue oder Ergebnisinjektion.
Bestehendes Logging über ClientEventEmitter, kompakt ohne Token/Text/PCM.

## Iterative Prüfungen

27 gezielte Transporttests PASS mit -W error. Alle15 Resultcodes, Serialisierung,
Replay/alte Acks, Fremdsession/Generation, Bootstrap/PCMguards, Kapazität,
4408/Close-/Backoffregeln, stille Annahme, abgebrochene/blockierte Sends,
Shutdown-Cancellation, Close-Abort und Loggingausfall. Fake-Ackwait injiziert
deterministisch einen Timeout ohne echte Wartezeit. Der Snapshot-Replaytest
verwendet100ms statt10ms, damit Windows-Timer/Debugloop die gültige Antwort
nicht überholen; Produktdefaults bleiben5s.

Erste Testharnessfehler: BACKOFF war im Startwait nicht zugelassen; Fakeacks
lagen unter dem Fixture-Snapshot und wurden korrekt nicht projectable. Fake
Initialversion auf0 wie beim echten Server gesetzt. Serverharness verwendete
zunächst den falschen Countvergleich für die reale Sessions-Liste; berichtigt.
Windows-Archiveexport hatte CRLF; alle239 Pythondateien aus Gitblobbytes neu
bereitgestellt und geladene Quellen vor/nach Check byteverifiziert. Keine
Serverproduktänderung. Testlogs der Iterationen bleiben in der Akte.

Echter Loopback-WebSocketcheckpoint21 Fälle mit unveränderter gepinnter
FastAPI-App, GateAwareRecorder/AutoScheduler als Hardware-/Modellgrenze.
Hello/Admission, konfigurierte Sperre, Availability-/Suppressionacks,
Snapshotkorrelation, Activate/Finish, Capacity-/Settingsablehnung und Cleanup.
Noch offene Clientsettings-/Audiointegration ist ausdrücklich Testadapter.
Vollständige finale kandidativen Windows-/Servernachweise stehen unten.

## Offene Grenzen

Kein Eigenreview/ROOT_PASS. Vollständige Runtimekomposition, ASR, Mikrofon,
Hardware/Qt/Clipboard und finale Prozesspaarqualifikation bleiben ihren
Folgepaketen zugeordnet. Server-Distributed bleibt unverändert und offen.

## Kandidatengebundene vollständige Qualifikation

[PR #4](https://github.com/marcosudau-vps/voice-stt-client/pull/4), getesteter Commit `7546298f26e00b83ad4c9510a9b8c1e7e6726fc3`, Tree `7bd496ef70a192781ff999b31695b3ef3fd72210`;
Workingtree vor Prüfung sauber. Nachfolgende Änderungen ausschließlich Akten,
Status/Traceability/Unterlagennachträge; kein Produkt-/Test-/Konfigunterschied.
Windows11 Build26300, Python3.12.10/AMD64, Projektvenv, QT_QPA_PLATFORM=offscreen.
[Befehle/Runtime/Exitcodes/Zeit/Loghashes](EVIDENCE/windows-validation.json).

| Prüfung | Ergebnis | Vollständiger Beleg |
| --- | --- | --- |
| Vorher-Windowsbaseline |1263 OK,96.614s, Exit0 | [Log](EVIDENCE/baseline-full-unittest.txt) |
| Codec/Transport, -W error |57 Tests PASS, Exit0 | [Log](EVIDENCE/targeted-transport-codec-unittest.txt) |
| Reale gepinnte Serverapp via TCP/WS |21 Fälle PASS;46 Pythonquellen byteverifiziert, Exit0 | [Checkpoint](EVIDENCE/server-transport-checkpoint.json) |
| compileall voice_stt_client/scripts/tests |PASS, Exit0 | [Leerer Log](EVIDENCE/compileall.txt), [Exit](EVIDENCE/windows-validation.json) |
| Gesamte Windows-Clientsuite |1290 Tests PASS, Exit0 | [Vollständiger Log](EVIDENCE/windows-full-unittest.txt) |

Keine Pflichtskips, kein V1-Test ersetzt/geschwächt. Erwartete Negativtestlogs
bleiben vollständig erhalten. Diff-/Aktenprüfung vor PR-Übergabe separat
nachgewiesen; Kandidaten-CI zusätzlich geprüft. Ein einziges nachgestelltes
Leerzeichen im historischen fehlgeschlagenen targeted-iteration1-Log wurde
für git diff --check entfernt; finale Pflichtlogs bleiben vollständig und nur
CRLF→LF normalisiert. Frühere Iterationsbelege sind ausdrücklich historische
Fehl-/Debugnachweise, nicht der finale PASS.

## Individuelle Requirementbelege

ACK-/RECONNECT-Status bleibt CLIENT OPEN bis unabhängiger Abnahme. Advice ist
die injizierte Mirror-/Servicegrenze: Snapshotklärung, Settingsneuberechnung,
Audio-/Trigger-/Feldfehlerdarstellung erfolgen beim fachlichen Consumer, nicht
durch einen automatischen Ersatzcommand. Diese Verantwortlichkeiten und
Callbackordnung sind im APIvertrag ausdrücklich dokumentiert. Der Transport
liefert Korrelation, Guard und begrenzten Abschluss für jeden Resultcode.

| ID | Tatsächliche Methode unter tests.test_v2_transport | Selbstcheck |
| --- | --- | --- |
| ACK-01 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-02 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-03 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-04 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-05 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-06 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands`; `Transport.test_closing_input_ack_blocks_more_refresh_for_same_activation` | PASS |
| ACK-07 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-08 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-09 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-10 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-11 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-12 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-13 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-14 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-15 | `Transport.test_all_fifteen_ack_results_complete_once_without_new_commands` | PASS |
| ACK-16 | `Transport.test_event_before_old_ack_and_duplicate_ack_do_not_project` | PASS |
| ACK-17 | `Tracker.test_fake_ack_wait_retry_identical_and_revision_guard`; `Transport.test_retry_exact_bytes_once_and_timeout_no_new_id` | PASS |
| ACK-18 | `Transport.test_eventless_payload_completion_and_snapshot_replay` | PASS |
| ACK-19 | `Transport.test_eventless_payload_completion_and_snapshot_replay`; `Transport.test_same_domain_serialized_other_domain_independent` | PASS |
| ACK-20 | `Transport.test_foreign_session_and_generation_never_confirm_or_publish`; `Transport.test_disconnect_finishes_pending_and_domain_waiters`; `Transport.test_cancel_request_stalled_send_and_audio_loss_invalidate`; `Tracker.test_capacity_cancellation_and_close_clear_waiters` | PASS |
| ACK-21 | `Transport.test_reconnect_new_binding_ids_empty_queue_and_suppression_retained` | PASS |
| RECONNECT-01 | `Transport.test_close_codes_block_or_reconnect_with_capacity_floor`; `Transport.test_malformed_admission_second_hello_and_binary_server_block` | PASS |
| RECONNECT-02 | `Transport.test_4408_only_one_retry_with_stable_process_run_id` | PASS |
| RECONNECT-03 | `Transport.test_handshake_refusal_config_capacity_and_incompatible`; `Transport.test_close_codes_block_or_reconnect_with_capacity_floor` | PASS |
| RECONNECT-04 | `Transport.test_reconnect_new_binding_ids_empty_queue_and_suppression_retained` | PASS |
| RECONNECT-05 | `Transport.test_reconnect_new_binding_ids_empty_queue_and_suppression_retained`; `Transport.test_foreign_session_and_generation_never_confirm_or_publish` | PASS |
| RECONNECT-06 | `Transport.test_admission_and_connect_timeout_no_hanging_run`; `Transport.test_retry_exact_bytes_once_and_timeout_no_new_id`; `Transport.test_close_timeout_aborts_underlying_transport`; `Transport.test_cancel_connect_bootstrap_and_stop_caller_leave_no_tasks` | PASS |
| RECONNECT-07 | `Transport.test_transport_ping_only_and_no_final_inference_timer` | PASS |

Windowsnachweise an Commit/Tree gebunden; Requirements-JSON und Matrix haben dieselben Methoden/Runverweise. AP010-Nachmergebeleg aktualisiert. Originalauftrag, Status, Paketindex, Produkt-/Übergabedokumentation und ein Steuerungsmeilenstein gesichert. Offene Selbstfindings: keine. Frische unabhängige Session prüft AP-CV2-020 PR #4 vom Parent bis zum eingereichten Head samt Code und kandidatengebundenen Windows-/Servernachweisen. Keine eigene unabhängige Abnahme, Übernahme oder Folgepaket. Schreibhoheit wird mit der endgültigen SHA-/Treeübergabe zurückgegeben.
