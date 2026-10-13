# AP100 R01 – Evidenzindex

Windows11/Python3.12.10, Projektvenv, Qt offscreen. Testsynthese enthält ausschließlich
kontrollierten Text/PCM, keine Nutzeraufnahme, Secrets oder persistierte Laufzeitdaten.
Getesteter Parent `dad89bb5d08e6d34abc5cfab57fc76010c5131dc`, Kandidatenbranch `work/client-v2/ap-cv2-100`, Server `ada13b0`.

| Beleg | Erzeugung / Ergebnis |
| --- | --- |
| [Original-/Planherkunft](input-provenance.json), [Startskript](record_start.py) | Paketvertrag/Requirements/K04-Hash, kanonischer Parent und Branch, tatsächliche AP090-Promotion PASS |
| [Vorgänger](predecessor-canonicalization.json) | gh pr view11 und git Parent/Commitcount/tree; PASS |
| [Baseline](baseline-windows.txt) | Projektvenv unittest discover -s tests -p test_*.py -v, vor Produktänderung1552 PASS, Exit0 |
| [Manifest](windows-validation.json), [Erzeugung](qualify_windows.py) | vollständige Commands, Runtime/Dependencyidentität, Zeit, Exitcode, Zahlen, Log-SHA256 und qualifizierte Gitblobs; PASS |
| [Exakter Produktdiff](tested-product.patch.base64) | git diff --cached --binary --unified=0 HEAD -- voice_stt_client tests scripts; base64, Diff-/Artefakthash im Manifest |
| [Gezielte Tests](targeted-unittest.txt) | -W error unittest tatsächlicher Runtime-/UI-/Config-/SingleInstance-/Hotkey-/OBSmodule; 190 PASS |
| [Servercheckpoint](server-runtime-checkpoint.json), [stderr](server-runtime-checkpoint.json.stderr.txt) | scripts/check_v2_server_runtime.py mit gepinntem Export und Serverrepo; 17 PASS, 45 bytegeprüfte Quellen |
| [compileall](compileall.txt) | -m compileall -q voice_stt_client scripts tests; Exit0 PASS, leerer Log ist erwarteter q-Modus |
| [Windowsvollsuite](windows-full-unittest.txt) | unittest discover -s tests -p test_*.py -v; 1573 PASS, keine Pflichtskips |
| [Erste Regression](initial-regression.txt) | vorhandene SettingsUI/CoreBridge/Application,81 PASS |
| [Erste Integration](runtime-first.txt) | früher Kandidat:16 Tests,3FAIL/1ERROR; snapshotlose Logdecision, Gerätefake und Feedbackgrenze, korrigiert |
| [Zweite Iteration](runtime-second.txt) | früher Kandidat:16 Tests,4FAIL/14ERROR; falscher Enumimport/ungültiges Fixture-LEDverb, korrigiert |
| [Dritte Iteration](runtime-third.txt) | früher Kandidat:16 Tests,1FAIL; No-effect-Stateled im Impulsfixture, korrigiert |
| [Vierte Iteration](runtime-fourth.txt) | Zwischenstand16 PASS |
| [Erweiterte Regression](runtime-expanded.txt) |21 neue plus81 vorhandene Tests,102 PASS |
| [Früher Servercheckpoint](checkpoint-first.txt) | komponierter Desktop-/Serverfluss PASS am früheren Produktstand; Endbeleg siehe Manifest |
| [Falscher Modulaufruf](qualification-command-error.txt) |187 Tests inkl.2 Ladefehler für nicht vorhandene Testmodule; Aufruf korrigiert, alle gültigen Tests im Endlauf PASS |
| [Abgabeprüfung](submission-verification.json), [Prüfskript](verify_submission.py) | Qualifizierte staged Gitblobs und Loghashs unverändert, diffcheck und Akten-/Markdownlinks PASS |

Die finalen Qualificationlogs sind UTF8/LF und per SHA256 im Manifest gesichert.
Zwischenlogs sind datierte Diagnosebelege am früheren Stand, keine Endqualifikation.
Administrative Aktenprüfung und tatsächliche PR-/Head-/Treebindung werden vor Abgabe
zusätzlich gesichert; finale Kandidatenblobs müssen mit dem Manifest übereinstimmen.
