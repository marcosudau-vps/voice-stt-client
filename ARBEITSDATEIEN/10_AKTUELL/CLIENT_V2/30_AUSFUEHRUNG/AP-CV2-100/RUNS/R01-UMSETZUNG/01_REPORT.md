# AP-CV2-100 – R01 Umsetzung

**Status:** REVIEW_READY. Stand 2026-10-13; vollständige Selbstqualifikation, unabhängige Abnahme offen.

## Auftrag, Herkunft und Gitumfang

[Originalauftrag](00_PROMPT_ORIGINAL.md). AP100 vollständig vom tatsächlichen
`feat/client-v2`-Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc` umgesetzt, Kandidatenlinie `work/client-v2/ap-cv2-100`.
AP090: unabhängiger R02-PASS und menschlicher R03-Prompt geprüft; PR #11 tatsächlich
gemergt, genau ein neuer Single-Parent-Commit und Baumgleichheit zur finalen Spitze
[belegt](EVIDENCE/predecessor-canonicalization.json). Server unverändert
`ada13b011e1d3829f78e7f389e3b927795a2b3be`.
Planversion/Hashs [gesichert](EVIDENCE/input-provenance.json).

Gitfreigabe: workflowweiter Originalprompt AP000 erlaubt Kandidatencommit,
normalen Paketbranch-Push und Paket-PR samt Übergabe gegen feat/client-v2.
Keine AP100-Übernahmefreigabe. Finalen eingereichten Head/Tree aus PR/Git ableiten;
der Report schreibt keinen unmöglichen eigenen Commit-SHA voraus.
Der getestete Stand ist exakt Parent plus [staged Produktdiff](EVIDENCE/tested-product.patch.base64),
SHA256 und sämtliche qualifizierten Gitblobs im [Windowsmanifest](EVIDENCE/windows-validation.json).
Spätere Unterlagennachträge verändern keinen Produkt-/Testblob.

## Ergebnis, Schnittstellen und Entscheidungen

Regulärer GUI-/Headless-Start verwendet die gemeinsame `V2Runtime`. Neue Module
`core/v2_runtime.py`, `ui/v2_core_bridge.py`, `ui/v2_application.py` komponieren die
bereits abgenommenen Komponenten über die bestehende Desktop-/Threadhülle.
Die vorgeschlagenen Legacy-Controller-/STTSessiondateien bleiben unverändert;
eine zweite Zustandsmaschine oder Lifecycleautorität wurde nicht übernommen.
Die Auswahl in app.py/run_gui und Raw-Migrationswerte in AppConfig sind nötige
gemeinsame Anschlussänderungen. Legacyproduktabbau bleibt AP110.

Öffentliche Runtime-/Bridge-/UIports, Callbackreihenfolge, Sideeffects, Guards und
Migration sind vollständig in [Produktarchitektur](../../../../../../../docs/protocol-v2-runtime.md)
beschrieben. Controls/Results → Runtimeview → Feedback ist die Reductionsreihenfolge;
Qt bekommt immutable Runtime-/Mirror-/Feedbackansichten. Physical impulses werden
bereits beim Queuen an ihre veröffentlichte Generation/Session/Activation gebunden.
HTTP, Media, Commands und Logs behalten ihre vorhandenen Bindingguards.
Results reserviert Domainfinals, schreibt History und queued anschließend Paste;
Interim und Logreplay sind kein Injektionspfad. Reinsert ist ein eigener Versuch.

Profilapply registriert Rollenkeys im Qtthread, schreibt auf einem Worker atomar
und übernimmt oder rollt zurück. SettingsUISession unterstützt dafür async
Persistenzports. Auch Schließen während Diskcommit lässt Persistenz/Adoption
zusammen abschließen. Shutdown verarbeitet Qt-Replies und meldet Keys danach ab.
Geräteenumeration im lokalen Dialog erfolgt auf einem Worker. Audioapply sperrt
PCM und meldet unavailable vor Stop/Probe; Fehlschlag stellt lokale Konfiguration
wieder her. Runtimefehler von History/Sound/LED sind sekundäre Diagnosen.

`/ws/transcribe` wird origin-treu nach `/ws/v2` ohne Legacyquery migriert.
Migration benutzt tatsächlich geladene Benutzerwerte, bytegleiches Originalbackup
und die vorhandene atomare AppConfig-Persistenz. Keine Laufzeitpausen/Tokens/IDs
werden gespeichert. Konfig-/Datenmigration und Startanleitung stehen in der
[Kompatibilität](../../../../../../../docs/compatibility.md).

## Anforderungen einzeln

Methoden mit Runtime/QtRuntime gehören `tests.test_v2_runtime_integration`.
Alle sechs IDs bleiben CLIENT OPEN bis unabhängiger Abnahme. Die hier angegebenen
Ergebnisse sind SELF_CHECK_PASS_REVIEW_READY, kein eigenes ROOT_PASS.

| ID | Tatsächlicher Nachweis |
| --- | --- |
| FINAL-01 | `Runtime.test_manual_wake_both_and_null_effective_share_bootstrap`, `Runtime.test_multiple_activations_background_final_and_history_before_paste`, `Runtime.test_two_segments_same_activation_same_text_keep_distinct_results`, `Runtime.test_history_disabled_keeps_terminal_dedup` |
| FINAL-02 | `QtRuntime.test_actual_bridge_thread_qt_output_and_native_role_dispatch`, `QtRuntime.test_shutdown_during_disk_commit_finishes_and_releases_native_keys`, `Runtime.test_pending_command_disconnect_completes_and_shutdown_joins_workers` |
| RUNTIME-01 | `Runtime.test_restore_confirmed_before_first_pcm_and_ready_projection`, `Runtime.test_disconnect_at_each_bootstrap_boundary_never_releases_pcm`, `Runtime.test_resync_without_snapshot_remains_guarded_and_bounded` |
| RUNTIME-02 | `QtRuntime.test_profile_transaction_rebind_persist_and_failure_rollback`, `QtRuntime.test_device_enumeration_on_worker_and_local_config_apply`, `Runtime.test_local_audio_probe_and_persist_failure_roll_back_config`, `scripts/check_v2_server_runtime.py:apply/drain_wait_no_destructive_reconnect` |
| RUNTIME-03 | `Runtime.test_autostart_after_confirmed_ready_only_once`, `QtRuntime.test_dialog_close_reopen_new_lease_and_shutdown_all_workers`, `QtRuntime.test_shutdown_during_disk_commit_finishes_and_releases_native_keys`, `tests.test_single_instance`, `tests.test_startup_hotkey_persistence` |
| RUNTIME-04 | `Runtime.test_history_fault_isolated_with_diagnostic_and_controls_survive`, `QtRuntime.test_adapter_failure_keeps_capture_controls_and_results_alive`, `Runtime.test_device_loss_preserves_background_results_and_pause`, `scripts/check_v2_server_runtime.py` |

Für alle Zeilen: [gezielte vollständige Logs](EVIDENCE/targeted-unittest.txt),
[Windowsvollsuite](EVIDENCE/windows-full-unittest.txt) und
[komponierter Servercheckpoint](EVIDENCE/server-runtime-checkpoint.json).
Requirements-JSON und Matrix enthalten denselben individuellen Methoden-/Runbezug.

## Qualifikation und Fehleriteration

Baseline vor Produktänderung: 1552 Windows-Tests, Exit0, keine Skips,177.130s.
Endstand: **1573 Windows-Tests**, **190 gezielte Tests** mit `-W error`,
**17 echte Serverchecks** und **45 bytegeprüfte Serverquellen** PASS.
compileall und staged/unstaged diffcheck PASS. Python3.12.10 auf Windows11;
vollständige Befehle, Runtime/Dependencies, Dauer, Exitcodes und Loghashs im
Windowsmanifest. 21 neue Integrationstests; keine entfernten/geskippten
V2-Assertions. Ein bestehender Test mocked jetzt die tatsächliche V2-Desktopfactory;
sein Construction-failure-/Mutexfreigabevertrag bleibt identisch.

Die ersten Negativtests fanden snapshotlose diagnostische Entscheidungen,
Gerätelisten-/Einzelgeräteformen, Enum-/Stringfeedback und eine No-effect-Testregel.
Mocks/Assertions wurden am tatsächlichen Vertrag korrigiert; lokale Fehler werden
nun als eigene Kategorien zurückgeführt. Neue Persistenz-/Shutdowntests schützten
die Transaktion vor vorzeitigem Abmelden/Rollback der Keys. Ein Qualifikationsaufruf
nannte zwei nicht vorhandene Testmodule; die gültigen vorhandenen Module wurden
ermittelt und der Lauf vollständig wiederholt. Alle Zwischenlogs bleiben im
[Evidenzindex](EVIDENCE/INDEX.md) als frühere FAIL/diagnostische Belege erhalten.

Servercheckpoint: tatsächliche QApplication/V2DesktopApplication/V2CoreBridge
mit separatem Corethread, unveränderter FastAPI-App, echten HTTP/Domain-/Log-WS
und temporärer SQLite. Restore vor Capture, manueller Lifecycle, Hintergrundfinal,
Drain-wait vor Triggerreconnect, Workerpersistenz, Reinsertion, Qtthread und
Shutdown bestanden. Benannte Grenzen: PortAudio-/Win32registrierung-/SendInput,
GateAwareRecorder/ManualScheduler/ASR und physische Sound-/LEDausgabe.

## Grenzen und Übergabe

Kein offenes Paketpflichtkriterium aus Selbstprüfung; frischer unabhängiger Review
steht aus. AP110, IV2-010 und reale Hardware-/ASR-/Wahrnehmungsqualifikation IV2-020
bleiben PLANNED/offen. Keine Serveränderung, kein Live-Prod-Schreibzugriff.
UI-Corejoin10s, Komponentenclose jeweils7s, Clipboardjoin2s. Nicht abbrechbare
native Betriebssystemcalls sind keine behauptete erfolgreiche OS-Terminierung;
Timeout wird gemeldet und die Media-Cleanupgrenzen bleiben sichtbar.

REVIEW_READY-Übergabe: vollständigen kumulativen Kandidaten gegen `dad89bb5d08e6d34abc5cfab57fc76010c5131dc` prüfen,
Windowsbelege commitgebunden validieren, neue unabhängige Reviewakte auf pausiertem
Paketbranch. Keine Pflicht, die Windowsvollsuite routinemäßig erneut auszuführen.
Keine eigene kanonische Übernahme und kein automatischer AP110-Start.
