# AP-IV2-010 / R01-UMSETZUNG – REVIEW_READY

**Status REVIEW_READY; vollständiger automatisierter Selbstcheck PASS.** Kein eigener ROOT_PASS.
[Originalauftrag](00_PROMPT_ORIGINAL.md), [vollständige Evidenz](EVIDENCE/INDEX.md), [PR14](https://github.com/marcosudau-vps/voice-stt-client/pull/14).

## Identität und Auftrag

Qualifiziertes tatsächliches Client-/Serverpaar **`0f0687c21f87a3778c3d7979e0bd7cde4ee8a1c4` / `ada13b011e1d3829f78e7f389e3b927795a2b3be`**,
Clienttree `14645a9998a8428b442052b17aa326fe3d5f2171`. Parent/unverändertes Clientprodukt `43759d345b2b88354e4f3b383a4833731621d1e3`.
Harness-/Testcodecommit `6c969a90a8bc6de601258cb4ae17740db8368b77`; danach bis zum
qualifizierten 0f0687c ausschließlich administrative Nachmerge-/Steuerungsunterlagen.
Der finale PR-Head ergänzt ausschließlich administrative Belege; seine eigene SHA
wird aus Git übergeben. Alle Produkt-/Test-/Dependencydateien bleiben gleich.

AP110-R02-PASS, tatsächlicher menschlicher R03-Prompt und PR13-Squash mit genau
einem neuen Single-Parent-Commit und Baumgleichheit geprüft:
[Startprovenienz](EVIDENCE/start-provenance.json). Arbeitsfreigabe aus AP000/R01
gilt workflowweit für Kandidatencommits, normale Paketpushes, PR und Übergabe.
Keine menschliche IV2-010-Übernahmefreigabe und kein Eigenreview.

## Umsetzung und Beweisgrenzen

`ProcessServer` startet die echte gepinnte Produktions-ASGI-App in der eigenen
Servervenv. V2Runtime mit tatsächlichen Services läuft im anderen Windowsprozess.
Dynamische Loopbackports, isolierte Persistenz, begrenzte Readiness/HTTP/waits/
watchdog/cleanup und maximale Serverkapazität1. `serverCommit=unknown` bleibt
unknown; SHA, PID, Interpreter und bytegeprüfte Quellen kompensieren die fehlende
Buildangabe. Empfangene Wirefelder belegen `/ws/v2`, `/ws/logs` und V2-HTTP.
Texte/Token redigiert, PCM ausschließlich als Bytezahl gespeichert.
Negative Admissionproben sind direkte Wire-/Codecproben mit deklarierter
Parentidentität43759d3; positive Fälle verwenden den tatsächlichen Runtime-Hello0f0687c.

Recorder/VAD/ASR/Scheduler und PortAudio sind kontrolliert, Clipboard/SendInput
als expliziter Ausgabesink. AP040s immutable Jobherkunft verhindert, dass der
upstream Recorderfake mit seinem gemeinsamen FIFO B-Cancel dem gehaltenen A-Job
zuschreibt. Kein Produktcode beider Repositories geändert. [Sourcekonsistenz](EVIDENCE/source-consistency.json):
555 unveränderte Serverblobs und unveränderte Produkt-/Test-/Dependencydateien.

28 automatisierte Szenarien konkret gebunden: echte getrennte Prozesscases plus
vorhandene deterministische Reihenfolgen-/Crash-/native Fehlergrenzen, ergänzt
durch sieben tatsächliche Socketsmokes und volle gepinnte Serverregression.
Seltene künstliche Races werden ausdrücklich als solche benannt. Clientseitig
injizierter Gap erhält gepufferten Final einmal; verlorener Final bleibt incomplete,
Logreplay erzeugt weder Ersatztext noch Paste. Recovery1011 schließt autonom ohne
weitere Client-Domainnachricht; bei Kapazität1 folgt neue Session und Aufnahme.

## Verifikation und iterative Klärung

Windows11 Build26300, Python3.12.10, Projektvenv, Qt offscreen, OPENBLAS/OMP=1.
Vollständige Befehle/Exitcodes/Runtime/Hashs/Rohlogs: [validation.json](EVIDENCE/validation.json).

| Prüfung | Ergebnis |
| --- | --- |
| Bestehende Clientbaseline | 1353 PASS / 170.483s, keine Skips |
| Komplette Clientregression bei stabilem HEAD | **1354 PASS**, exit0, 205.875s, keine Skips |
| Getrennte Prozesssuite inkl. Bindungsprüfung | **11 PASS**, exit0 |
| Konkrete zusätzliche Szenariogrenzmethoden | **17 PASS**, exit0 |
| transport/audio/controls/results/settings/feedback/runtime-Smokes | **7/7 PASS**, jeweils exit0 |
| Gesamte schnelle Serverpytest-unit-Suite inkl. reiner pytesttests | **1964 PASS / 14 SKIPPED_EXPECTED**, exit0, 646.938s |
| compileall / diffcheck | PASS / exit0 |
| CI auf 0f0687c inkl. Windows-Vollsuite, EXE, Wheel/sdist, Installationsprobe | [38539692570](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38539692570) SUCCESS; finale administrative PR-CI vor tatsächlicher Übergabe zusätzlich prüfen |

Initiale Fehlversuche bleiben vollständig erhalten. Ein unbounded Baselinelauf
wurde nach Hängen beendet; verbose Wiederholung grün. Servercollection brauchte
httpx/soundfile/dotenv/scipy/torch/webrtcvad; Katalogtests zusätzlich ONNX,
HTTP-Formtests multipart und Audiodecoder faster-whisper/PyAV<19. Neue Ausführungen
schließen diese Umgebungsfehler. FastAPI/Starlette liegen separat in der Servervenv;
Clientversionen wurden wiederhergestellt. Keine Produktfixes versteckt.

Ein administrativer Commit während der ersten finalen Clientsuite änderte die
Git-Buildidentität (6c969a9→0f0687c); der Identitätstest scheiterte korrekt. Die volle
stabile Wiederholung1354 schließt dies. Die komplette Serversuite wurde nach
Decoderinstallation wiederholt. [Supersedierte Läufe](EVIDENCE/initial-validation.json)
bleiben FAIL und werden nicht als Erfolg umgeschrieben.

[Optionale Server-Skips](EVIDENCE/server-skips.json) einzeln aufgelistet: explizite
reale Engine-/Golden-/Loadoptins, bedingter realer Silero-Modellvergleich und
optionaler Originalvektorvergleich (separat bytegleich durch Crossrepo-Hash geprüft).
Keine Collection-/Importfehler und kein übersprungener Pflicht-Prozessfall.
Kein reales Modell-PASS daraus. SC29/30, M-Fälle und empirische Wakekalibrierung
bleiben NOT_RUN/AP-IV2-020.

## GATE-Requirements

| ID | Selbstcheck | Tatsächlicher Beleg |
| --- | --- | --- |
| GATE-01 | PASS | 11 Prozessprüfungen, [Processmanifest](EVIDENCE/process-manifest.json), tatsächliche Wirefelder |
| GATE-02 | PASS | Windows1354 und Server1964/14 mit vollständigen Logs |
| GATE-03 | PASS | SC01..28 unten, drei Endpoints, sieben Smokes, Race-/Settings-/Log-/Recoverygrenzen |
| GATE-04 | PASS | `test_autonomous_terminal_recovery_and_stale_callback`: autonom1011, freier Slot, neue Aufnahme |
| GATE-05 | PASS | unknown unverändert; SHA/Interpreter/PID und vor/nach Prozess geprüfte Quellhashes |
| GATE-06 | PASS | ausschließlich Harness/Tests/Dokumentation, leere Produktdiffs, keine gefundenen Produktdefekte |
| GATE-07 | PASS (unveränderter Referenzfall) | keine Serverkorrektur/Promotion, gleiche SHA und 555 Blobs; neuer Baselinefall nicht eingetreten |

## Einzelne automatisierte Szenariobindung

| ID | Resultat | Konkrete ausgeführte Methode(n) |
| --- | --- | --- |
| SC-01 | PASS | `ProcessCases.test_segments_overlap_interim_and_log_dedup` |
| SC-02 | PASS | `ProcessCases.test_wake_only_and_shared_admission_race` |
| SC-03 | PASS | `ProcessCases.test_wake_only_and_shared_admission_race` |
| SC-04 | PASS | `ProcessCases.test_segments_overlap_interim_and_log_dedup` |
| SC-05 | PASS | `tests.test_v2_mirror.Mirror.test_terminal_before_close_does_not_release_foreground` |
| SC-06 | PASS | `tests.test_v2_mirror.Mirror.test_b_start_before_a_close_and_old_final_during_b` |
| SC-07 | PASS | `tests.test_v2_mirror.Mirror.test_discard_and_failure_before_ended_accepted_interim` |
| SC-08 | PASS | `ProcessCases.test_segments_overlap_interim_and_log_dedup`; `tests.test_v2_results.Results.test_first_discard_failed_empty_then_completed_and_late_interim_never_paste` |
| SC-09 | PASS | `ProcessCases.test_lost_finish_ack_retries_identical_without_second_effect`; `tests.test_v2_transport.Tracker.test_fake_ack_wait_retry_identical_and_revision_guard` |
| SC-10 | PASS | `ProcessCases.test_device_loss_drain_and_led_isolation` |
| SC-11 | PASS | `ProcessCases.test_client_injected_gap_salvages_buffered_final` |
| SC-12 | PASS | `ProcessCases.test_client_dropped_final_is_incomplete_without_log_paste` |
| SC-13 | PASS | `tests.test_v2_mirror.Mirror.test_generation_session_duplicate_and_unknown_sequence` |
| SC-14 | PASS | `ProcessCases.test_wake_sources_settings_and_bootstrap` |
| SC-15 | PASS | `ProcessCases.test_wake_sources_settings_and_bootstrap` |
| SC-16 | PASS | `ProcessCases.test_wake_sources_settings_and_bootstrap` |
| SC-17 | PASS | `ProcessCases.test_device_loss_drain_and_led_isolation` |
| SC-18 | PASS | `ProcessCases.test_device_loss_drain_and_led_isolation` |
| SC-19 | PASS | `ProcessCases.test_autonomous_terminal_recovery_and_stale_callback` |
| SC-20 | PASS | `ProcessCases.test_autonomous_terminal_recovery_and_stale_callback` |
| SC-21 | PASS | `ProcessCases.test_negative_admission` |
| SC-22 | PASS | `ProcessCases.test_settings_atomicity_and_admin`; `tests.test_v2_settings_ui.CoreActions.test_auth_revision_validation_persistence_errors_do_not_unlock` |
| SC-23 | PASS | `ProcessCases.test_segments_overlap_interim_and_log_dedup` |
| SC-24 | PASS | `ProcessCases.test_segments_overlap_interim_and_log_dedup` |
| SC-25 | PASS | `tests.test_v2_results.Migration.test_v1_backup_ids_attempts_origin_and_second_start_idempotent`; `tests.test_v2_results.CrashRecovery.test_real_process_crash_at_five_boundaries_never_auto_reinjects` |
| SC-26 | PASS | `tests.test_v2_controls.Migration.test_defaults_alias_and_explicit_bindings_preserved`; `tests.test_v2_controls.NativeRegistration.test_partial_failure_restores_old_and_apply_rebind_invalidates_old_ids` |
| SC-27 | PASS | `tests.test_v2_settings_ui.CoreActions.test_cancel_targets_captured_activation_and_separate_drain_loss`; `tests.test_v2_settings_ui.CoreActions.test_finish_waits_for_actual_completion_before_reconnect`; `tests.test_v2_settings_ui.CoreActions.test_defer_preserves_foreground_and_background`; `tests.test_v2_runtime_integration.Runtime.test_reconnect_requires_explicit_open_input_or_drain_decision` |
| SC-28 | PASS | `ProcessCases.test_settings_atomicity_and_admin`; `tests.test_v2_settings_ui.Credentials.test_create_replace_delete_and_redacted_repr`; `tests.test_v2_settings_ui.CoreActions.test_store_failure_is_memory_only_and_explicit_error` |

SC21 zusätzlich durch sämtliche gepinnten Wake-/Admissiontests (alias/unknown/
disabled/unloadable/mixedbackend, atomare Auswahl), SC22 durch Session-/REST-
Persistenz-/Revisionstests und Clientfehlergrenzen; SC23 durch `server-audio`
(filtered cursors, retention survivor, store outage, Domainisolation).
SC27 ergänzt `server-runtime` mit tatsächlichem Wait-Drain-Reconnect nach A-Final.
Diese Nachweise wurden im selben Qualifikationsrun tatsächlich ausgeführt.

## Übergabe

Produktinterfaces, Callbackreihenfolge, Generation-/Sessionguards, Daten-/Config-
migration und Ausgaben bleiben unverändert. Reproduzierbarer Harness:
[Integration](../../../../../../../docs/protocol-v2-integration.md). Keine reale ASR-/Wake-/USB-/Fremdanwendungs-/
Playback-/Langlaufqualifikation behauptet.

Frischer unabhängiger Review des ganzen kumulativen PR14 nach grüner finaler CI.
Ab tatsächlicher Übergabe Schreiben und Pushes auf `work/client-v2/ap-iv2-010`
pausiert. Kein Eigenreview, Merge, Serverpromotion, Release/Tag oder AP-IV2-020.
Spätere Übernahme braucht unabhängigen PASS und menschlichen Originalprompt.
