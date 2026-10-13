# Evidenz – AP-CV2-100 / R04-KORREKTUR

**Status:** REVIEW_READY. Vollständige Selbstchecks, unabhängige Abnahme offen.
Basis c5a510f193908d7493f979365e45be6317cd9dab plus exakte Produktdiff/Gitblobs,
Parent dad89bb5d08e6d34abc5cfab57fc76010c5131dc, Server ada13b0.

| Beleg | Befehl / Zweck / Ergebnis |
| --- | --- |
| [Startprovenienz](start-provenance.json), [Treiber](record_start.py) | Fetch/ff-only, git rev-parse/diff, gh pr view; R03-Docs übernommen, Head/Base und aktueller Schreib-/Reviewzustand gesichert |
| [Baseline](baseline-targeted.txt) | Projektvenv -W error -m unittest tests.test_v2_runtime_integration tests.test_obs040_client_hooks -v vor erster Änderung; 56 PASS |
| [F01 vor Fix](f01-before-fix.txt) | Projektvenv -W error -m unittest tests.test_v2_runtime_integration.QtRuntime.test_local_settings_audit_correlates_overlay_audio_and_logging_success tests.test_v2_runtime_integration.QtRuntime.test_local_settings_audit_reports_persist_failure_and_restores_audio -v; zwei erwartete FAIL, Auditkette fehlt |
| [Nachfix-Iteration](f01-after-fix.txt) | Baselinebefehl mit neuen Fällen; 62 Tests, vier FAIL wegen Tuple/List-Erwartung der unveränderlichen Policies; erhalten, keine aktuellen Erfolgsbelege |
| [Korrigierte gezielte Tests](f01-corrected-targeted.txt) | Derselbe Befehl nach Assertionkorrektur; 62 PASS |
| [Shutdown](f01-shutdown.txt) | Projektvenv -W error -m unittest tests.test_v2_runtime_integration.QtRuntime.test_local_settings_shutdown_completes_pending_audit_once -v; 1 PASS |
| [Windowsmanifest](windows-validation.json), [Treiber](qualify_windows.py), [exakte Produktdiff](tested-product.patch.base64) | Kandidaten-/Runtime-/Befehls-/Exit-/Testzahl-/SHA256-Bindung, 213 Produkt-/Test-/Konfigblobs; PASS |
| [Gezielter Vollnachweis](targeted-unittest.txt) | Vollständiger Befehl im Manifest; 210 Tests -W error PASS einschließlich aller sieben neuen Qt-Fälle |
| [Vollständige Windows-Suite](windows-full-unittest.txt) | Projektvenv -m unittest discover -s tests -p test_*.py -v; 1581 PASS, keine Skips |
| [Servercheckpoint](server-runtime-checkpoint.json), [stderr](server-runtime-checkpoint.json.stderr.txt) | scripts/check_v2_server_runtime.py mit manifestgebundenen Pfaden; 17 komponierte reale Client/Serverchecks, 45 Quellen bytegeprüft PASS |
| [compileall](compileall.txt) | Projektvenv -m compileall -q voice_stt_client scripts tests; Exit0 PASS |
| [Abgabeprüfung](submission-verification.json), [Treiber](verify_submission.py) | Qualifizierte staged Gitblobs/Loghashes, Paket-/Status-/Manifest-/Markdownlinks PASS; tatsächliche PR-Kurzfassung nach Push separat read-only geprüft |
| [Dokumentationstreiber](complete_records.py), [PR-Vorbereitung](prepare_pr.py) | R04-Unterlagen und externe PR-Beschreibung aus tatsächlichem Head/Tree; CI-Ergebnis nur nach SHA-/Erfolgsprüfung |

Qualification-Logs UTF-8 LF vor Hashbildung; vollständige negative Diagnostik
ist erwarteter Faultinjectionnachweis. Vorher-/Iterationslogs stammen aus
PowerShellredirects, Exit/Zahl im Log; diese ersetzen nicht die qualifizierten Logs.
Tatsächliche endgültige CI/Head/Tree und Übergabe im PR, bevor unabhängiger Review
beginnt. Kein eigener ROOT_PASS oder behaupteter realer Hardware-/ASR-Gate.
