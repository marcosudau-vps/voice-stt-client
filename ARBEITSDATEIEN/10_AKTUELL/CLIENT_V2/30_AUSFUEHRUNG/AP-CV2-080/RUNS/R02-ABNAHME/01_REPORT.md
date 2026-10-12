# AP-CV2-080 / R02-ABNAHME – ROOT_PASS

**Datum:** 2026-10-13. **Rolle:** unabhängiger ChatGPT-Reviewer. **Verdict:** ROOT_PASS; Workflow WAITING_FOR_APPROVAL; keine offenen Pflichtfindings. [Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md).

## Identitäten und Prüfumfang

- PR [#10](https://github.com/marcosudau-vps/voice-stt-client/pull/10), Base `feat/client-v2`, Paketbranch `work/client-v2/ap-cv2-080`, **reviewed_sha** `eafd918f456551af694ede4af472ed4515b9fdd6`, **reviewed_tree** `960270c3f786433967aee7b16333be70f41427fe`.
- **canonical_parent** `0c8d52d45a2e942ca8adebb5e5abc4e1aa2d8eb3`; **server_sha** `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
- Qualifizierter Produktcommit `3d8cbd3a0893c51af7cad8c7b862c481d8fe08f7` (Tree `a597232834bb4a1ec1688a7f038ed9293f892bb9`); bis zum geprüften PR-Head ausschließlich sechs administrative Verweis-/Statusänderungen, kein Produkt-/Test-/Kontraktdelta. Parentvergleich umfasst 59 geänderte Dateien, zwei Single-Parent-Commits ohne Basisdrift.
- Bewertet am versionierten [Paketvertrag](../../../../PLANUNG/ARBEITSPAKETE/AP-CV2-080.md), K-03/K-04, vollständigem GitHub-Parentdiff, tatsächlichen Code-/Testdateien, R01-Implementierungsbericht und Fremdtestbelegen. Keine eigene Windows-Vollsuite erforderlich.

## Individuelle fachliche Abnahme

| ID | Bewertete fachliche Wirkung | Referenztest / tatsächlicher Checkpoint | Urteil |
| --- | --- | --- | --- |
| UI-01 | Manual+Wake/Mehrfachauswahl, Wake-only-Controls | `test_manual_wake_and_wake_only_keep_controls`; `apply/wake_only_controls_retained` | PASS |
| UI-02 | Schema-/requested-/effective-/pending-/Default-/Policy-/Kalibrieranzeige | `test_scope_schema_policy_requested_effective_and_calibration_visible`; `session/ui_real_patch_snapshot_effective` | PASS |
| UI-03 | Katalogfehler/unavailable/fehlende Wake-IDs | `test_unavailable_and_unknown_saved_ids_remain_visible; test_catalog_failure_keeps_prior_selection`; `ui/real_services_public_read_locked` | PASS |
| UI-04 | Adminseite nur nach echtem No-change-PATCH | `test_no_change_check_does_not_mutate_defaults`; `auth/no_change_defaults_revision_preserved` | PASS |
| UI-05 | 401/403/409/422-/Persistenzfehler und Revisionsguards | `test_auth_revision_validation_persistence_errors_do_not_unlock`; `auth/wrong_key_visible_locked; server/schema_reject_visible_no_write` | PASS |
| UI-06 | Originbezogener Windows-Credential-Store, Create/Replace/Delete | `test_create_replace_delete_and_redacted_repr`; `credential/native_create_from_ui; credential/native_replace_from_ui; credential/native_delete_from_ui` | PASS |
| UI-07 | No plaintext fallback, QSettings nur Metadaten | `test_store_failure_is_memory_only_and_explicit_error`; `secrets/no_qsettings_or_projection_export; secrets/no_config_export` | PASS |
| UI-08 | Cancel/Finish/Defer bei Activation, keine ungewählte Destruktion | `test_reconnect_without_activation_choice_has_no_side_effect; test_finish_waits_for_actual_completion_before_reconnect`; `apply/defer_preserves_real_activation; apply/finish_real_command_then_reconnect` | PASS |
| UI-09 | Separate Drainentscheidung, Timeout hält Verbindung | `test_idle_background_drain_requires_separate_loss_choice; test_wait_drain_timeout_keeps_socket_and_restores_pauses`; `drain/decision_cancel_preserves_connection; drain/wait_real_terminal_then_reconnect` | PASS |
| UI-10 | Dialogepoch, Generation, Origin, alte Asyncantworten | `test_origin_switch_drops_key_and_cannot_unlock_or_patch; test_old_epoch_reply_after_reopen_cannot_unlock_new_origin`; `credential/reopen_does_not_unlock` | PASS |

Zuordnung und vollqualifizierte Methodennamen: [R01 UI-Coverage](../R01-UMSETZUNG/EVIDENCE/requirement-coverage.md), [Tests](../R01-UMSETZUNG/EVIDENCE/targeted-unittest.txt), [Realserver-UI](../R01-UMSETZUNG/EVIDENCE/server-ui-checkpoint.json), [nativer Windowsvault](../R01-UMSETZUNG/EVIDENCE/windows-credential-ui.json).

## Eigene Code-/Identitätsprüfung

- `SettingsService.verify_admin`: authentifizierender, revisionsgebundener No-change-PATCH auf frisch gelesenen vorhandenen Default; Ergebnis, Revision und Werte geprüft. Öffentliche GETs und gespeicherter Key allein schalten nicht frei; 401/403/409/422/500 werden differenziert.
- `CredentialStore`: natives WinCred mit originhashbasiertem Target, Read/Save/Delete, Fehlerredaktion und ohne Klartextfallback; Qt speichert nur nichtgeheime Metadaten.
- `SettingsUISession.apply_profile`: validates Profil/Controls und beauftragt atomaren Persistenzport; überprüft Activation-/Drain-Identität und ausdrückliche Entscheidungen, schützt ungewählte/alte Destruktion, wartet auf Terminalereignisse, erhält bei Timeout Verbindung/Pauseintention. Die tatsächliche App-/Hotkeyregistrierung folgt verbindlich erst in AP100.
- `V2SettingsBridge` und `V2SettingsDialog`: Qt-Mainthread/Core-Loop-Trennung, Dialogepoch/Request-ID, Origin/Generation-Guards, Invalidierung vor Taskcancel, alte Antworten entsperren keinen neuen Dialog.
- Neun relevante Produkt-, Test- und Runner-Gitblobs am geprüften Commit unabhängig gelesen und mit `qualifiedGitBlobs` des Windowsmanifests verglichen: **9/9 PASS** (Credentialstore, Settingsservice, UIservice, lokale/UI-Dialogs, Bridge, zwei Testdateien, Realcheckpointrunner). Kein eigenständiger vollständiger Rehash aller 205 Manifestblobs; gesamte Blob-/Logbindung zusätzlich durch versionierten Verifier belegt.

## Unabhängig validierte Fremdbelege

| Bereich | Tatsächlicher Befund | Status |
| --- | --- | --- |
| Windows Python 3.12.10 / Projektvenv, qualifizierter Produktdiff | [Windowsmanifest](../R01-UMSETZUNG/EVIDENCE/windows-validation.json), Befehle, Exitcodes, Loghashes, Runtime | PASS |
| Gezielte `-W error` Tests | [296 Testfälle / OK](../R01-UMSETZUNG/EVIDENCE/targeted-unittest.txt) | PASS |
| Vollständige Windows-Regressionssuite | [1513 Testfälle / OK](../R01-UMSETZUNG/EVIDENCE/windows-full-unittest.txt) | PASS |
| Echte lokale gepinnte Services | [Settings38](../R01-UMSETZUNG/EVIDENCE/server-settings-checkpoint.json), [UI27](../R01-UMSETZUNG/EVIDENCE/server-ui-checkpoint.json), [nativ29](../R01-UMSETZUNG/EVIDENCE/windows-credential-ui.json) | PASS (Fremdbeleg) |
| Serverseitige Supplementtests | [55 bestanden, 0 Skips](../R01-UMSETZUNG/EVIDENCE/server-contracts.json) | PASS (Fremdbeleg) |
| Compileall / Diff-/Akten-/Blobprüfung | [Manifest](../R01-UMSETZUNG/EVIDENCE/windows-validation.json), [Abgabeverifier](../R01-UMSETZUNG/EVIDENCE/publication-verification.json) | PASS (Fremdbeleg / Stichprobe) |
| GitHub-CI auf `eafd918f456551af694ede4af472ed4515b9fdd6` | [Run 38303778947](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38303778947): komplette Suite, compileall, EXE, sdist/Wheel, installierter Wheel-Smoke, Upload | PASS |
| Eigene Windows-Vollsuite | Kein Windowsdesktop im ChatGPT-Review; laut Abnahmeskill nicht erforderlich | NOT_RUN, nicht blockierend |

Die frühere native Access Violation beim langen Legacy-Qt-Gesamtprozess ist in [fehlgeschlagenen Diagnosebelegen](../R01-UMSETZUNG/EVIDENCE/windows-full-unittest-failed.txt) transparent bewahrt und wurde nicht als PASS gerechnet. Die neuen Qt-Assertions werden ungekürzt in isolierten Windows-Projektvenv-QApplication-Unterprozessen ausgeführt; die danach komplette grüne Suite und die native UI sind valide. Nichtblockierendes Integrationsrisiko: Zusammengesetzten App-/Qt-Lifecycle in AP100 erneut prüfen.

**Grenzen:** reguläre Appkomposition und physisches Hotkey-Rebind AP100; tatsächliche ASR-/Wake-/Mikrofon- und Kalibrierempirie AP-IV2-020. Der lokale modellfreie TCP/HTTP/WS-Checkpoint ersetzt diese späteren Realgates ausdrücklich nicht; Server-Distributed bleibt offen.

## Entscheidung und Übergabe

**ROOT_PASS** für UI-01 bis UI-10, **offene Findings-IDs: keine**. Der technische PASS bezieht sich ausschließlich auf **reviewed_sha/tree `eafd918f456551af694ede4af472ed4515b9fdd6` / `960270c3f786433967aee7b16333be70f41427fe`**, nicht auf den anschließend erzeugten administrativen R02-Dokumentencommit. Nach Sicherung von Reviewakte und Steuerungsverweisen wird die Schreibhoheit zurückgegeben.

**Workflow: WAITING_FOR_APPROVAL.** Nächste Aktion nur ausdrücklicher menschlicher Übernahmeprompt und gesonderter PR-Head-/Base-/CI-Abgleich. **Kein Merge, Auto-Merge, AP090, Tag oder Server-/Main-Push durch den Reviewer.**
