# AP-CV2-100 / R03-ABNAHME – CHANGES_REQUIRED

**Datum:** 2026-10-13. **Rolle:** unabhängiger ChatGPT-Reviewer. **Urteil:** **CHANGES_REQUIRED**. **Offenes Pflichtfinding:** `CV2-100-R03-F01`. [Originalauftrag](00_PROMPT_ORIGINAL.md), [Evidenzindex](EVIDENCE/INDEX.md).

## Identität und kumulativer Parentdiff

- [PR #12](https://github.com/marcosudau-vps/voice-stt-client/pull/12), Base `feat/client-v2`, Headbranch `work/client-v2/ap-cv2-100`, offen und ungemergt vor dem Review-Docs-Commit.
- **reviewed_sha:** `4a35a2d7eba5fa55e79528744320419b8ec0a1b3`; **reviewed_tree:** `18f7516471c97627b92e9221e24e367f30f5cd81`; **canonical_parent:** `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`; **server_sha:** `ada13b011e1d3829f78e7f389e3b927795a2b3be`.
- GitHub-Vergleich: 3 Commits ahead, 0 behind, 86 geänderte Dateien, Merge-Base = Parent. Fachvertrag [AP100](../../../../PLANUNG/ARBEITSPAKETE/AP-CV2-100.md) und K-01 bis K-04; Paket-/Runakten und Traceability geprüft.
- Reviewzugang: commitgebundene GitHub-Dateien/Diffs, keine lokale Windows-Testumgebung; unabhängige Code-/Test-/Nachweisprüfung. Keine Produkt-/Test-/Serveränderungen.

## Unabhängige Requirementbewertung

| ID | Geprüfter Pfad und Referenztests | Urteil |
| --- | --- | --- |
| FINAL-01 | Ein V2Runtime-/Mirror-/Control-/Result-/Feedbackowner; `Runtime.test_manual_wake_both_and_null_effective_share_bootstrap`, `test_multiple_activations_background_final_and_history_before_paste`, `test_history_disabled_keeps_terminal_dedup` | PASS |
| FINAL-02 | Qt/Core-/Generationtrennung und Shutdown-Replypump; `QtRuntime.test_actual_bridge_thread_qt_output_and_native_role_dispatch`, `test_shutdown_during_disk_commit_finishes_and_releases_native_keys` | PASS |
| RUNTIME-01 | READY/PCM erst nach bestätigtem Settingsbootstrap, Resync-/Disconnectguards; `Runtime.test_restore_confirmed_before_first_pcm_and_ready_projection`, `test_disconnect_at_each_bootstrap_boundary_never_releases_pcm` | PASS |
| RUNTIME-02 | Profil-Apply/Qt-/Hotkeyrollback und Drain: `QtRuntime.test_profile_transaction_rebind_persist_and_failure_rollback`, `test_device_enumeration_on_worker_and_local_config_apply`, Servercheck `apply/drain_wait_no_destructive_reconnect`; bisherige Audit-/Korrelationsverträge im V2-Apply allerdings verloren | **FAIL – CV2-100-R03-F01** |
| RUNTIME-03 | Autostart/SingleInstance, Worker-/Shutdowncleanup; `Runtime.test_autostart_after_confirmed_ready_only_once`, `QtRuntime.test_dialog_close_reopen_new_lease_and_shutdown_all_workers` | PASS |
| RUNTIME-04 | Reale Paketklassen mit gezielten Socket/Geräte-/SendInput-Grenzen; History-/Adapter-/Resync-Faultinjection und 17 komponierte Serverchecks | PASS für geprüfte Funktionsfälle; Paket wegen F01 gesperrt |

## CV2-100-R03-F01 – Korrelierte Settings-Auditereignisse fehlen im tatsächlichen V2-Desktop

**Severity:** mittel, **blockierendes Pflichtfinding**, **Owner:** AP100-Umsetzer, **Zuordnung:** RUNTIME-02 / Erhalt bestehender OBS-Verträge.

**Soll:** Für lokalen Settings-Apply `client.settings.apply_started`, genau ein `client.settings.apply_completed` und `client.settings.runtime_apply` mit derselben `settings:<id>`-Korrelation sowie korrekten Änderungsflags/Erfolgs- bzw. Fehlerstatus, auch bei Persistenzfehler/Rollback.

**Ist (durch unabhängigen statischen Codevergleich verifiziert):**

1. Geerbtes `voice_stt_client/ui/application.py:DesktopApplication._apply_settings` emittiert `client.settings.apply_started` und bewahrt eine Korrelations-ID; `_complete_settings_observation` emittiert `client.settings.apply_completed`.
2. Neues `voice_stt_client/ui/v2_application.py:V2DesktopApplication` überschreibt `_apply_settings` und `_complete_settings_apply` ohne Auditaufrufe und ruft `self.bridge.apply_runtime_config(candidate)` ohne `settings_correlation_id` auf.
3. Neues `voice_stt_client/core/v2_runtime.py:V2Runtime.apply_runtime_config(..., correlation_id=None)` ignoriert die ID und publiziert `client.settings.runtime_apply` nicht. Diese Eventemission besteht im alten `core/controller.py:STTController.apply_runtime_config`, welches der reguläre V2-Desktop nicht verwendet.
4. `tests/test_obs040_client_hooks.py::test_runtime_apply_carries_the_three_flags_and_the_correlation` belegt den bisherigen Korrelationsvertrag, testet aber Legacy-STTController. Die neuen `QtRuntime`-Apply-/Rollbacktests assertieren kein einziges dieser drei Auditereignisse.

**Auswirkung:** Reale lokale V2-Konfigurationsübernahmen und fehlgeschlagene Applies besitzen nicht mehr den bestehenden korrelierten Auditverlauf. Allgemeine Commandlogs des CoreBridge ersetzen den Settings-Audit nicht. Grün laufende Tests beweisen die ausgelassene Emission nicht.

**Repro-/Korrekturauftrag:** Im tatsächlichen `V2DesktopApplication` + `V2CoreBridge` + `V2Runtime` mit einem aufzeichnenden Observability-Ingress lokale Overlay-/Audioeinstellung erfolgreich anwenden, dann `AppConfig.save_user` gezielt fehlschlagen lassen. Audit-Events, gemeinsame Korrelations-ID, korrekte drei Flags und genau einen Abschluss einschließlich Fehl-/Rollbackstatus assertieren. Minimalen V2-Fix samt Positiv-/Negativregression implementieren; danach gezielte Tests, vollständige Windows-Clientsuite und neue kandidatgebundene CI sowie erneuten unabhängigen Gesamt-Review. **Eigene Laufzeitrepro des Auditfehlers vom Reviewer: NOT_RUN** (Codebefund; keine falsche Hardware-Ausführungsbehauptung).

## Unabhängig validierte externe Nachweise

- R02-[Windowsmanifest](../R02-KORREKTUR/EVIDENCE/windows-validation.json), vollständige Logs, `testedBase=ca3cd400...` plus staged Produktdiff, 213 qualifizierte Gitblobs/Hashes: **1574 Windows-Tests PASS, 0 Skips**, **203 gezielte Tests `-W error` PASS**, compileall/diffcheck PASS; Windows11/Python3.12.10. Extern ausgeführt, unabhängig auf Bindung und Ergebnis geprüft.
- [Servercheckpoint](../R02-KORREKTUR/EVIDENCE/server-runtime-checkpoint.json): **17/17** tatsächliche Desktop/Core/Qt-/HTTP-/Domain-/Logchecks, 45 bytegeprüfte Serverquellen am gepinnten `ada13b011e1d3829f78e7f389e3b927795a2b3be`, PASS. Explizit kontrollierte Grenzen: PortAudio, Win32, SendInput, Recorder/ASR/Scheduler, physische Sound-/LEDausgabe.
- Sechs unabhängig per GitHub abgefragte Gitblobs stimmen exakt mit `R02/windows-validation.json:qualifiedGitBlobs` überein (Runtime, CoreBridge, Desktop, app.py und zwei Testmodule); R02-Abgabeprüfung dokumentiert alle 213 Blob-/Loghashbindungen und 1174 Links. [Prüfprotokoll](EVIDENCE/review-source-checks.json).
- [GitHub Actions Run 38347923728](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38347923728): `completed/success` am geprüften Head, Tests, compileall, EXE-Build/Smoke, sdist/wheel/twine, installierter Wheel-Smoke und Upload PASS. R02 hat das vorherige CI-01-Replay-Timeout mit erweiterten Testfristen und 280-ms-Verzögerungsassertions ohne Produktcodeänderung korrigiert.
- Eigene Windows-Suite/physische Hardware vom Reviewer **NOT_RUN**; laut Rollen-Skill nicht verpflichtend erneut auszuführen. Spätere Gates: CV2-110 finaler Auslieferungsbuild, IV2-010 Crossrepo-Paarqualifikation, IV2-020 reale ASR-/Wake-/USB-/Clipboard-/Feedbackwahrnehmung.

## Verdict / Übergabe

**CHANGES_REQUIRED, offene Finding-IDs: [`CV2-100-R03-F01`]**; kein ROOT_PASS, keine kanonische Übernahme und kein AP110-Start. Korrektur auf **demselben PR #12** im Folgeauftrag; die abschließende unabhängige Abnahme muss den **gesamten neuen Kandidaten** beurteilen.

Geprüfte Identität bleibt die obige `reviewed_sha/tree` **vor dem administrativen R03-Dokumentcommit**. Späterer eigener Docs-Commit wird in der Übergabe mit tatsächlich ermittelter SHA separat benannt.
