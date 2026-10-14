# AP-IV2-020 R01 – Evidenz / BLOCKED

Basis b80ed8b81ad92bd02ac32553883443d2b7673bcd, Tree
b12a3f4dc1f2c51d2c4a70680e63c988e729f666, Server ada13b0.
Tester Codex auf Windows; noch keine menschliche Sprach-/Wahrnehmungsdurchführung.
Kein REVIEW_READY oder ROOT_PASS.

## Maßgebliche Belege

- [Vorgänger-/Gitprovenienz](start-provenance.json).
- [Testfähigkeit, fünf Kategorien](testability.md), [Windowsruntime](windows-runtime.json), [Treiber](windows-drivers.json).
- [Clientbaseline](baseline-client.json) und [vollständiger Log](baseline-client.txt.gz):1354 PASS.
- [Clientvollsuite](client-full.json) und [vollständiger Log](client-full.txt.gz):1360 PASS,176,893s,keine Skips.
- [Native Aufnahme/USB/Vault/EXE](native-preflight.json), [LED/Muteschreiben/Restore](native-led-mute.json).
- [555 exakte Serverblobs/Image/Config](local-server-build.json), [Modelldigests](model-identities.json).
- [Echtmodelladmission Manual/Wake/Both](real-admission.json), [Audio/ASRpipeline](real-audio-pipeline.json).
- [Frozenruntime](frozen-runtime.json), [Produktbaumgleichheit](build-equivalence.json).
- [Instrumentierter Desktop](desktop-identity.json), [rohe redigierte Metrikspur](desktop-trace.jsonl), [Smokeresultat](desktop-smoke.json).
- [Parameter-/LEFX-/Soundinventar](parameter-inventory.json), [Registry/effective/Modelhealth](real-server-inventory.json).
- [Alle realen M-Fälle und tatsächliche Grenzen](real-cases.json).
- **IV2-020-F01**: [zweiter realer Restarttrace](restart-repro-trace.jsonl), [Identität](restart-repro-identity.json), [FAIL](restart-repro-smoke.json),
  [Reprotests](repro_transient_preflight.py), [kompletter Reprolog](repro-transient-preflight.txt.gz),
  [noch nicht angewandter Fixpatch](proposed-client-recovery-fix.patch).
- [Clipboardvorcheck](native-paste.json):NOT_RUN mangels Vordergrundfokus, keine Eingabe/Clipboardänderung.
- [Realer Watchdogversuch](real-watchdog.json):NOT_PROVEN; Aufnahmehardcut30s verhindert60s-Expiry. Kein Produktdefekt daraus abgeleitet.
- [RSS-Messinstrumentierung](measure_wake_resources.py):/proc/self/statm statt fehlendem optionalen psutil; echte Modelle unverändert.
- [Watchdog-Replayharness](watchdog_real_audio.py):echte energieausgewählte Referenzaudiochunks, echte Uhr/ASR, keine menschliche Neusprache.

## Befehle und vollständige Logs

Jede nachfolgende Befehlsakte enthält exakte argv/cwd, Exitcode, Dauer, Windows-/Python-
Runtime, vor/nach Quellidentität, vollständigen komprimierten Log sowie dessen Raw-/Gzip-
SHA256. Loggzip mit Standardgzip lesbar; keine gekürzten Erfolgszitate als Ersatz.
Produktdateien unverändert; spätere Änderungen ausschließlich administrativ.

| Lauf | Wrapperresultat / Exit | Befehlsakte | Vollständiger Log |
| --- | --- | --- | --- |
| baseline-client | PASS baseline / 0 | [baseline-client.json](baseline-client.json) | [baseline-client.txt.gz](baseline-client.txt.gz) |
| client-full | PASS / 0 | [client-full.json](client-full.json) | [client-full.txt.gz](client-full.txt.gz) |
| compileall | PASS / 0 | [compileall.json](compileall.json) | [compileall.txt.gz](compileall.txt.gz) |
| cross-process | PASS / 0 | [cross-process.json](cross-process.json) | [cross-process.txt.gz](cross-process.txt.gz) |
| frozen-probe-exact | PASS / 0 | [frozen-probe-exact.json](frozen-probe-exact.json) | [frozen-probe-exact.txt.gz](frozen-probe-exact.txt.gz) |
| frozen-real-server-probe | PASS / 0 | [frozen-real-server-probe.json](frozen-real-server-probe.json) | [frozen-real-server-probe.txt.gz](frozen-real-server-probe.txt.gz) |
| native-hotkeys | PASS / 0 | [native-hotkeys.json](native-hotkeys.json) | [native-hotkeys.txt.gz](native-hotkeys.txt.gz) |
| native-paste-attempt | FAIL / 1 | [native-paste-attempt.json](native-paste-attempt.json) | [native-paste-attempt.txt.gz](native-paste-attempt.txt.gz) |
| native-settings-ui | PASS / 0 | [native-settings-ui.json](native-settings-ui.json) | [native-settings-ui.txt.gz](native-settings-ui.txt.gz) |
| real-golden-asr-stable | PASS / 0 | [real-golden-asr-stable.json](real-golden-asr-stable.json) | [real-golden-asr-stable.txt.gz](real-golden-asr-stable.txt.gz) |
| real-golden-asr | FAIL / 0 | [real-golden-asr.json](real-golden-asr.json) | [real-golden-asr.txt.gz](real-golden-asr.txt.gz) |
| real-golden-exact | PASS / 0 | [real-golden-exact.json](real-golden-exact.json) | [real-golden-exact.txt.gz](real-golden-exact.txt.gz) |
| real-wake-artifacts | PASS / 0 | [real-wake-artifacts.json](real-wake-artifacts.json) | [real-wake-artifacts.txt.gz](real-wake-artifacts.txt.gz) |
| real-wake-negative | PASS / 0 | [real-wake-negative.json](real-wake-negative.json) | [real-wake-negative.txt.gz](real-wake-negative.txt.gz) |
| real-wake-resources | PASS / 0 | [real-wake-resources.json](real-wake-resources.json) | [real-wake-resources.txt.gz](real-wake-resources.txt.gz) |
| real-watchdog-run | FAIL / 0 | [real-watchdog-run.json](real-watchdog-run.json) | [real-watchdog-run.txt.gz](real-watchdog-run.txt.gz) |
| repro-transient-preflight | FAIL / 1 | [repro-transient-preflight.json](repro-transient-preflight.json) | [repro-transient-preflight.txt.gz](repro-transient-preflight.txt.gz) |
| superseded-client-full | FAIL / 1 | [superseded-client-full.json](superseded-client-full.json) | [superseded-client-full.txt.gz](superseded-client-full.txt.gz) |
| wake-negative-exact | PASS / 0 | [wake-negative-exact.json](wake-negative-exact.json) | [wake-negative-exact.txt.gz](wake-negative-exact.txt.gz) |
| wake-resources-exact-rss | PASS / 0 | [wake-resources-exact-rss.json](wake-resources-exact-rss.json) | [wake-resources-exact-rss.txt.gz](wake-resources-exact-rss.txt.gz) |

Native-paste-attempt hat Wrapperexit1, das tatsächliche Fallresultat ist NOT_RUN wegen
Fokus, kein gesendetes Zeichen. Repro-transient-preflight enthält zwei absichtlich
rote gewünschte Recoveryregressionen und einen grünen permanenten Fehlerkontrollfall.
Diese Fehler sind offen und werden durch die grüne bestehende Vollsuite nicht verdeckt.
Real-watchdog-run hat zusätzlich eine während des Laufs geänderte Helferidentität;
seine tatsächlichen Events zeigen30s-Hardcuts und werden ausschließlich diagnostisch
verwendet. Watchdogprüfung bleibt NOT_PROVEN, kein Warnungs-/Expiry-PASS.

Superseded-client-full:1359/2 Pfadfixturefehler durch injiziertes Profilroot; Helfer
korrigiert, [29 gezielte Checks](harness-env-recheck.txt.gz), vollständiger1360-Lauf
PASS. Erster Goldenlauf wegen Helferidentitätswechsel verworfen; stable und exact
wiederholt. Vor-exact `real-wake-*` und `frozen-real-server-probe` sind Vorchecks;
maßgeblich exact-Runs und separates frozen-runtime.json. Keine davon belegt eine
menschliche positive Wakegrenze oder deutsches ASR-Qualitätsurteil.

Die Prozessharnessbelege `test_*.json` gehören zum11er-Prozesslauf. Produktionscode/
HTTP/WS/Logs sind echt; Recorder/ASR/Audioausgabe dort explizit modellfreie Testgrenzen.
Sie ersetzen keine Realfälle. `accessToken` ist redigiert, Testtexte sind synthetisch.

## Weitere Belege in dieser Akte

- [baseline-client.json](baseline-client.json)
- [baseline-client.txt.gz](baseline-client.txt.gz)
- [build-equivalence.json](build-equivalence.json)
- [client-full.json](client-full.json)
- [client-full.txt.gz](client-full.txt.gz)
- [compileall.json](compileall.json)
- [compileall.txt.gz](compileall.txt.gz)
- [cross-process.json](cross-process.json)
- [cross-process.txt.gz](cross-process.txt.gz)
- [desktop-autosmoke.txt.gz](desktop-autosmoke.txt.gz)
- [desktop-identity.json](desktop-identity.json)
- [desktop-restart-repro.txt.gz](desktop-restart-repro.txt.gz)
- [desktop-restart.txt.gz](desktop-restart.txt.gz)
- [desktop-smoke.json](desktop-smoke.json)
- [desktop-trace.jsonl](desktop-trace.jsonl)
- [frozen-probe-exact.json](frozen-probe-exact.json)
- [frozen-probe-exact.txt.gz](frozen-probe-exact.txt.gz)
- [frozen-real-server-probe.json](frozen-real-server-probe.json)
- [frozen-real-server-probe.txt.gz](frozen-real-server-probe.txt.gz)
- [frozen-runtime.json](frozen-runtime.json)
- [harness-env-recheck.txt.gz](harness-env-recheck.txt.gz)
- [local-server-build.json](local-server-build.json)
- [measure_wake_resources.py](measure_wake_resources.py)
- [model-identities.json](model-identities.json)
- [native-hotkeys.json](native-hotkeys.json)
- [native-hotkeys.txt.gz](native-hotkeys.txt.gz)
- [native-led-mute.json](native-led-mute.json)
- [native-paste-attempt.json](native-paste-attempt.json)
- [native-paste-attempt.txt.gz](native-paste-attempt.txt.gz)
- [native-paste.json](native-paste.json)
- [native-preflight.json](native-preflight.json)
- [native-settings-ui.json](native-settings-ui.json)
- [native-settings-ui.txt.gz](native-settings-ui.txt.gz)
- [parameter-inventory.json](parameter-inventory.json)
- [proposed-client-recovery-fix.patch](proposed-client-recovery-fix.patch)
- [real-admission.json](real-admission.json)
- [real-audio-pipeline.json](real-audio-pipeline.json)
- [real-cases.json](real-cases.json)
- [real-golden-asr-stable.json](real-golden-asr-stable.json)
- [real-golden-asr-stable.txt.gz](real-golden-asr-stable.txt.gz)
- [real-golden-asr.json](real-golden-asr.json)
- [real-golden-asr.txt.gz](real-golden-asr.txt.gz)
- [real-golden-exact.json](real-golden-exact.json)
- [real-golden-exact.txt.gz](real-golden-exact.txt.gz)
- [real-server-inventory.json](real-server-inventory.json)
- [real-wake-artifacts.json](real-wake-artifacts.json)
- [real-wake-artifacts.txt.gz](real-wake-artifacts.txt.gz)
- [real-wake-negative.json](real-wake-negative.json)
- [real-wake-negative.txt.gz](real-wake-negative.txt.gz)
- [real-wake-resources.json](real-wake-resources.json)
- [real-wake-resources.txt.gz](real-wake-resources.txt.gz)
- [real-watchdog-run.json](real-watchdog-run.json)
- [real-watchdog-run.txt.gz](real-watchdog-run.txt.gz)
- [real-watchdog.json](real-watchdog.json)
- [repro-transient-preflight.json](repro-transient-preflight.json)
- [repro-transient-preflight.txt.gz](repro-transient-preflight.txt.gz)
- [repro_transient_preflight.py](repro_transient_preflight.py)
- [restart-repro-identity.json](restart-repro-identity.json)
- [restart-repro-smoke.json](restart-repro-smoke.json)
- [restart-repro-trace.jsonl](restart-repro-trace.jsonl)
- [start-provenance.json](start-provenance.json)
- [superseded-client-full.json](superseded-client-full.json)
- [superseded-client-full.txt.gz](superseded-client-full.txt.gz)
- [test_autonomous_terminal_recovery_and_stale_callback.json](test_autonomous_terminal_recovery_and_stale_callback.json)
- [test_client_dropped_final_is_incomplete_without_log_paste.json](test_client_dropped_final_is_incomplete_without_log_paste.json)
- [test_client_injected_gap_salvages_buffered_final.json](test_client_injected_gap_salvages_buffered_final.json)
- [test_device_loss_drain_and_led_isolation.json](test_device_loss_drain_and_led_isolation.json)
- [test_lost_finish_ack_retries_identical_without_second_effect.json](test_lost_finish_ack_retries_identical_without_second_effect.json)
- [test_negative_admission.json](test_negative_admission.json)
- [test_segments_overlap_interim_and_log_dedup.json](test_segments_overlap_interim_and_log_dedup.json)
- [test_settings_atomicity_and_admin.json](test_settings_atomicity_and_admin.json)
- [test_wake_only_and_shared_admission_race.json](test_wake_only_and_shared_admission_race.json)
- [test_wake_sources_settings_and_bootstrap.json](test_wake_sources_settings_and_bootstrap.json)
- [testability.md](testability.md)
- [wake-negative-exact.json](wake-negative-exact.json)
- [wake-negative-exact.txt.gz](wake-negative-exact.txt.gz)
- [wake-resources-exact-rss.json](wake-resources-exact-rss.json)
- [wake-resources-exact-rss.txt.gz](wake-resources-exact-rss.txt.gz)
- [watchdog_real_audio.py](watchdog_real_audio.py)
- [windows-drivers.json](windows-drivers.json)
- [windows-runtime.json](windows-runtime.json)

- [Finale Quell-/Test-/Stagingkonsistenz](source-consistency.json)
- [Redaktionsprüfung](redaction-check.json)
- [Diffprüfung](diff-check.json), [kompletter Log](diff-check.txt.gz)
- [Aktenprüfung](work-records.json), [kompletter Log](work-records.txt.gz)
