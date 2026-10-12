# AP-CV2-030 / R02 – unabhängige technische Abnahme

**Verdict: ROOT_PASS.** **workflowPhase: WAITING_FOR_APPROVAL.** **Offene Pflichtfindings: keine.** 2026-10-12, Europe/Berlin.

[Originalauftrag](00_PROMPT_ORIGINAL.md) · [Evidenzindex](EVIDENCE/INDEX.md) · [Umsetzungsbericht](../R01-UMSETZUNG/01_REPORT.md) · [Paketakte](../../00_PAKET.md) · [PR #5](https://github.com/marcosudau-vps/voice-stt-client/pull/5)

## Identität, Herkunft und Scope

- Repo `marcosudau-vps/voice-stt-client`, PR #5, Base `feat/client-v2`, Kandidatenbranch `work/client-v2/ap-cv2-030`.
- **reviewed_sha** `d062ce2ec8d6d9c0683dc6be09397e11cdbd7e61`; **reviewed_tree** `7123984bb4b382919e557f4ecef1400de4eced29`; **canonical_parent** `8fa0f829bece203e4a9d5ee0896dc9c4478f9fc0`; **server_sha** `ada13b011e1d3829f78e7f389e3b927795a2b3be`. Dies sind die Identitäten **vor** diesem späteren Reviewdocs-Commit.
- Der qualifizierte Produkt-/Testcommit `93acd2e6a589e04b266019f69e2bcad2998b8904` (Tree `822b72bfabf0f1e59769d98523b6c6ab784136f0`) folgt direkt auf `8fa0f829bece203e4a9d5ee0896dc9c4478f9fc0`. Der einzige Commit bis `d062ce2ec8d6d9c0683dc6be09397e11cdbd7e61` ändert sieben **ausschließlich administrative** Dateien. Der vollständige kumulative Parentvergleich umfasst 45 Dateien. PR-Base hat keinen Rückstand; Vorgänger AP-CV2-020 ist mit Review, menschlicher Freigabe und Einzelsquash tatsächlich übernommen.
- Frische unabhängige GitHub-Connectorprüfung des SHA-gebundenen Codes, vollständigen PR-Dateiumfangs, K-02/K-03, Tests, Paket-/Traceability-Quellen und Umsetzungsbelegen. **Keine eigene Windows-Vollsuite durchgeführt**, da AGENTS/Abnahmeskill die unabhängige Validierung vollständiger kandidatengebundener Fremdlogs gestatten.

## Unabhängige fachliche Codeprüfung

1. `activation_mirror.py`: serverautoritativer Vordergrund mit nur den fünf Phasen, separate Activation-/Segmentprovenienz. Alte Finals verbleiben bei ihrer ursprünglichen Activation und Segment-ID; `activation.completed` setzt den Vordergrund nicht blind idle. Terminal-vor-Close und B-Start-vor-A-Close sind in den tatsächlichen Tests abgedeckt.
2. 18 bekannte Ereignistypen aus K-02 inklusive Interim-/Wake-/Settings-/Watchdogwirkungen und isolierte unbekannte additive Events. Jede echte Eventmutation folgt der `eventSeq` statt Uhrzeit; `stateVersion`-Sprünge ohne Sequenzlücke lösen keinen Scheinresync aus; Session- und Generationguards sind vorhanden.
3. Erste Terminalentscheidung pro Segment, Erhalt von Finaltexten und Cancel-/Failedtombstones, keine Finalfreigabe aus Zwischenständen. Konfliktbehandlung für Segment-ID, Sequenz und Activationidentität. Immutable Präsentationsviews und eingefrorene Activation-Settings.
4. `_snapshot`: alte Versionen/Sequenzen/Settingsrevisionen werden verworfen; Snapshot ersetzt nur snapshotfähige Domänen, nicht bereits empfangene Segmenttexte. Gepufferte Finals bis zum Snapshotcursor werden idempotent nachgetragen, Lifecycle bei historischem Replay nicht rückwärts projiziert. Verlorene Terminal-/Pendinginformationen erscheinen als `terminal_unknown` und `incomplete`, nicht als erfundener Text.
5. Resync: 512 Ereignisse / 4 MiB, zwei Snapshotversuche zu je 5s, Monotonicdeadline, Overflow-/Timeoutreconnect. `V2MirrorConnection` verbindet den bestehenden `V2STTSession`-/CommandTracker, verarbeitet Reducer vor den alten Callbacks, fordert echte Snapshots an, entkoppelt ältere Bindungen und sperrt Aktivierungsbefehle sowohl beim Eintritt als auch unmittelbar vor dem WebSocket-Send. Ack ist kein Foregroundzustand.
6. Der vorhandene V1-Core, UI, Clipboard, Feedback/Logging und die Historie werden nicht unnötig verändert. Appkomposition, Audio- und Settingsports, ASR-/Hardware- und Produktgesamtprüfung sind ausdrücklich den späteren Paketen zugeordnet; dieses Urteil ist **kein** solches E2E-Gate.

## 35/35 Requirement-Nachweise

Jede der 18 FG- und 17 SYNC-IDs wurde gegen `PLANUNG/REFERENZ/TRACEABILITY/requirements.json`, Matrix und den tatsächlich vorhandenen `tests/test_v2_mirror.py`-Quellcode geprüft. Für **jede** zugeordnete Methode wurde deren Existenz und ein Eintrag im vollständigen 106er Targeted-Testlog kontrolliert: **0 Abweichungen**.

| Requirement | Tatsächliche, bestandene Testmethode(n) | Review |
| --- | --- | --- |
| FG-01 | `tests.test_v2_mirror.Mirror.test_server_foreground_phases_and_countdown`; `tests.test_v2_mirror.Mirror.test_idle_with_multiple_drains_allows_manual` | PASS |
| FG-02 | `tests.test_v2_mirror.Mirror.test_manual_and_wake_share_one_foreground` | PASS |
| FG-03 | `tests.test_v2_mirror.Mirror.test_manual_and_wake_share_one_foreground`; `tests.test_v2_mirror.Mirror.test_b_start_before_a_close_and_old_final_during_b` | PASS |
| FG-04 | `tests.test_v2_mirror.Mirror.test_multiple_segments_and_terminal_holes_do_not_block_final` | PASS |
| FG-05 | `tests.test_v2_mirror.Mirror.test_manual_and_wake_share_one_foreground`; `tests.test_v2_mirror.Mirror.test_terminal_before_close_does_not_release_foreground` | PASS |
| FG-06 | `tests.test_v2_mirror.Mirror.test_idle_with_multiple_drains_allows_manual` | PASS |
| FG-07 | `tests.test_v2_mirror.Mirror.test_terminal_before_close_does_not_release_foreground`; `tests.test_v2_mirror.Mirror.test_generated_races_have_id_and_terminal_invariants_each_step` | PASS |
| FG-08 | `tests.test_v2_mirror.Mirror.test_b_start_before_a_close_and_old_final_during_b`; `tests.test_v2_mirror.Mirror.test_generated_races_have_id_and_terminal_invariants_each_step` | PASS |
| FG-09 | `tests.test_v2_mirror.Mirror.test_discard_and_failure_before_ended_accepted_interim`; `tests.test_v2_mirror.Mirror.test_all_terminal_cancel_permutations_first_terminal_wins` | PASS |
| FG-10 | `tests.test_v2_mirror.Mirror.test_segment_identity_and_sequence_collision_degrade`; `tests.test_v2_mirror.Mirror.test_snapshot_cannot_change_activation_identity_or_regress_settings` | PASS |
| FG-11 | `tests.test_v2_mirror.Mirror.test_multiple_segments_and_terminal_holes_do_not_block_final`; `tests.test_v2_mirror.Mirror.test_gap_requests_once_and_buffers_until_snapshot` | PASS |
| FG-12 | `tests.test_v2_mirror.Mirror.test_multiple_segments_and_terminal_holes_do_not_block_final` | PASS |
| FG-13 | `tests.test_v2_mirror.Mirror.test_interims_equal_versions_segment_owned_display_fallback` | PASS |
| FG-14 | `tests.test_v2_mirror.Mirror.test_interims_equal_versions_segment_owned_display_fallback`; `tests.test_v2_mirror.Mirror.test_discard_and_failure_before_ended_accepted_interim` | PASS |
| FG-15 | `tests.test_v2_mirror.Mirror.test_activation_settings_frozen_across_snapshot_and_settings_events` | PASS |
| FG-16 | `tests.test_v2_mirror.Mirror.test_close_reason_command_identity_and_unknown_reasons` | PASS |
| FG-17 | `tests.test_v2_mirror.Connection.test_closing_ack_clarifies_never_overwrites_foreground`; `tests.test_v2_mirror.Mirror.test_snapshot_all_domains_and_safe_immutable_projection` | PASS |
| FG-18 | `tests.test_v2_mirror.Connection.test_1011_recovery_new_session_and_stale_binding_guard`; `tests.test_v2_mirror.Mirror.test_disconnect_retains_text_and_rebind_isolated` | PASS |
| SYNC-01 | `tests.test_v2_mirror.Mirror.test_interims_equal_versions_segment_owned_display_fallback`; `tests.test_v2_mirror.Mirror.test_gap_requests_once_and_buffers_until_snapshot` | PASS |
| SYNC-02 | `tests.test_v2_mirror.Mirror.test_state_version_jump_without_sequence_gap` | PASS |
| SYNC-03 | `tests.test_v2_mirror.Mirror.test_generation_session_duplicate_and_unknown_sequence`; `tests.test_v2_mirror.Connection.test_1011_recovery_new_session_and_stale_binding_guard` | PASS |
| SYNC-04 | `tests.test_v2_mirror.Mirror.test_generation_session_duplicate_and_unknown_sequence`; `tests.test_v2_mirror.Mirror.test_known_additive_fields_cannot_cross_domain_boundaries` | PASS |
| SYNC-05 | `tests.test_v2_mirror.Mirror.test_gap_requests_once_and_buffers_until_snapshot`; `tests.test_v2_mirror.Connection.test_gap_gates_actual_transport_and_resync_before_ack`; `tests.test_v2_mirror.Connection.test_queued_activation_rechecks_resync_guard_before_send` | PASS |
| SYNC-06 | `tests.test_v2_mirror.Mirror.test_snapshot_all_domains_and_safe_immutable_projection` | PASS |
| SYNC-07 | `tests.test_v2_mirror.Mirror.test_snapshot_all_domains_and_safe_immutable_projection`; `tests.test_v2_mirror.Connection.test_eventless_bootstrap_ack_reads_actual_snapshot` | PASS |
| SYNC-08 | `tests.test_v2_mirror.Mirror.test_countdown_uses_receipt_not_wallclock_and_nulls`; `tests.test_v2_mirror.Mirror.test_server_foreground_phases_and_countdown` | PASS |
| SYNC-09 | `tests.test_v2_mirror.Mirror.test_snapshot_all_domains_and_safe_immutable_projection`; `tests.test_v2_mirror.Mirror.test_idle_with_multiple_drains_allows_manual` | PASS |
| SYNC-10 | `tests.test_v2_mirror.Mirror.test_lost_final_and_disappeared_pending_are_incomplete_no_text` | PASS |
| SYNC-11 | `tests.test_v2_mirror.Mirror.test_snapshot_preserves_received_final_and_terminal_dedup`; `tests.test_v2_mirror.Mirror.test_buffered_final_at_or_behind_cursor_salvaged_once` | PASS |
| SYNC-12 | `tests.test_v2_mirror.Mirror.test_buffered_final_at_or_behind_cursor_salvaged_once`; `tests.test_v2_mirror.Mirror.test_buffered_lifecycle_not_applied_backwards` | PASS |
| SYNC-13 | `tests.test_v2_mirror.Mirror.test_lost_final_and_disappeared_pending_are_incomplete_no_text`; `tests.test_v2_mirror.Mirror.test_unseen_buffered_segment_missing_lifecycle_is_unknown` | PASS |
| SYNC-14 | `tests.test_v2_mirror.Mirror.test_buffered_cancel_failed_tombstones_suppress_unpublished_only`; `tests.test_v2_mirror.Mirror.test_buffered_final_before_cancel_remains_published` | PASS |
| SYNC-15 | `tests.test_v2_mirror.Mirror.test_snapshot_equal_version_higher_seq_and_stale_bounds`; `tests.test_v2_mirror.Mirror.test_snapshot_cannot_change_activation_identity_or_regress_settings` | PASS |
| SYNC-16 | `tests.test_v2_mirror.Mirror.test_resync_event_and_byte_overflow_is_incomplete_reconnect`; `tests.test_v2_mirror.Mirror.test_default_512_event_buffer_bound_and_no_duplicate_budget_use`; `tests.test_v2_mirror.Mirror.test_timeout_two_attempts_stale_snapshot_does_not_extend_budget`; `tests.test_v2_mirror.Connection.test_missing_snapshot_even_with_ack_reconnects_bounded` | PASS |
| SYNC-17 | `tests.test_v2_mirror.Mirror.test_countdown_uses_receipt_not_wallclock_and_nulls`; `tests.test_v2_mirror.Mirror.test_start_missing_deadline_clarification_does_not_timeout_activation` | PASS |

## Nachweiskontrolle, Durchführung und Grenzen

| Nachweis | Exakte Aussage | Status |
| --- | --- | --- |
| Windows-Gesamtsuite | Windows 11 Build 26300, Python 3.12.10 Projektvenv, Qt offscreen, vollständiges `unittest discover`-Log: **1339 Tests in 97,760s, OK**, Exit 0, keine breiten Skips | **PASS**, vom Umsetzer ausgeführt, unabhängig gelesen |
| Targeted | `-W error -m unittest tests.test_v2_mirror tests.test_v2_transport tests.test_v2_protocol -v`: **106 Tests in 5,699s, OK**, Exit 0; 45 Mirror-/Anbindungstests | **PASS**, unabhängig gelesener Fremdlauf |
| Echter gepinnter Server | `scripts/check_v2_server_transport.py --with-mirror`: **35/35 PASS** und 46 bytegeprüfte Serveroriginalquellen aus `ada13b011e1d3829f78e7f389e3b927795a2b3be`, reale TCP/WS-/Produkt-FastAPI-/Domain-/Snapshotstrecke. Recorder/Modelle und späterer Clientbootstrap sind ausdrücklich Testgrenzen | **PASS** für den belegten Zwischencheckpoint |
| compileall | `compileall -q voice_stt_client scripts tests`, Exit 0 | **PASS** |
| Kandidaten- und Logidentität | R01-Manifeste mit SHA256 des exakten Produktpatches `0a3c38c4…`, 185 Gitblob-/Runtimequellen und vier vollständigen Loghashes; versionierter `implementation-publication.json`-Abgleich; Git-Compare qualifizierter Produktcommit → vorliegender PR-Kandidat nur administrative Dateien | **PASS** im dokumentierten Nachweisumfang |
| GitHub CI | [Run 38187988549](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38187988549) für **genau `d062ce2ec8d6d9c0683dc6be09397e11cdbd7e61`** `completed/success`; Unit-Vollsuite, Pythonkompilierung, EXE-Build und Smoke, Wheel-/sdist-Build, Wheelinstallation/Ressourcen-Smoke erfolgreich | **PASS**, unmittelbar remote kontrolliert |
| Struktur-/Linkübergabe | R01-Aktenprüfung: 24 referenzierte Dateien, 20 Markdown-Dateien, 245 relative Links, 0 Fehler; Status/Manifest/PR-Base/Head bei Reviewstart `REVIEW_READY` konsistent | **PASS** für eingefrorene R01-Unterlagen |
| Eigene Windows-/reale Hardware-/ASR-/Qt-/Clipboardprüfung | Kein eigener Windowslauf; reale Produktgesamtqualifikation erst in anderen APs | **NOT_RUN / SKIPPED_EXPECTED**, hier kein Pflichtdefizit |

Die vollständigen Laufzeitlogs sind [R01-Evidence](../R01-UMSETZUNG/EVIDENCE/INDEX.md) zugeordnet. Ein eigener erneuter Bytehash aller 185 Dateien wird **nicht** behauptet; Gitidentität und dokumentierter Abgleich wurden geprüft. Sessionledger/Fingerprints wachsen im Lauf der Session; nur der Resyncpuffer hat harte Bounds, wie dokumentiert.

## Urteil und nächste Aktion

**Keine offenen Pflichtfindings. Technische Abnahme: ROOT_PASS für `d062ce2ec8d6d9c0683dc6be09397e11cdbd7e61` / `7123984bb4b382919e557f4ecef1400de4eced29`.** Die Traceability wird ausschließlich um den eigenen Reviewbeleg erweitert; Produkt-, Test-, Kontrakt- und fachliche Requirementtexte bleiben unverändert. Kein Serverfix.

**WAITING_FOR_APPROVAL**, `humanApproval=null`. Nur ein ausdrücklicher menschlicher Übernahmeauftrag mit PR #5, finalem Head, Parent und diesem R02-Report darf die kanonische Einzelaggregation autorisieren. Zuvor ist die neue, reine Reviewdocs-Spitze gegenüber `d062ce2ec8d6d9c0683dc6be09397e11cdbd7e61` zu prüfen und die finale CI zu berücksichtigen. **Kein Merge und kein Folgepaketstart.**
