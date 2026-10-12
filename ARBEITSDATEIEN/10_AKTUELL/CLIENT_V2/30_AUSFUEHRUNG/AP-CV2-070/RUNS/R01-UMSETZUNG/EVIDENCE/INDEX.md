# AP-CV2-070 / R01 – Evidenzindex

Alle Prüfungen mit `venv/Scripts/python.exe` des Clientprojekts auf Windows/Python3.12.10. Getestete Basis `473a75d02fb6d00e5664af4328dadaa44da5191a`, Branch `work/client-v2/ap-cv2-070`, Server `ada13b011e1d3829f78e7f389e3b927795a2b3be`. `QT_QPA_PLATFORM=offscreen`, `PYTHONUTF8=1`. Kein Nutzeraudio, keine Secrets, keine Laufzeitdatenbank. Kontrolliertes PCM/Modelausgaben sind Testdaten. SELF_CHECK_PASS / REVIEW_READY, kein unabhängiger PASS.

| Artefakt | Erzeugung/Zweck | Ergebnis |
| --- | --- | --- |
| [predecessor-canonicalization.json](predecessor-canonicalization.json) | gh PR8/Git Parent-/Treevergleich + R04/R05 lesen; tatsächliche Vorgängerübernahme | MERGED/Single-Parent/Treegleichheit PASS |
| [input-provenance.json](input-provenance.json) | SHA256 von AP070/K03/K04 über `git show <parent>:<path>` | Ausgangsvertrag identifiziert |
| [baseline-unittest.txt](baseline-unittest.txt) | `venv/Scripts/python.exe -m unittest tests.test_config tests.test_v2_transport tests.test_v2_mirror tests.test_v2_audio_recovery tests.test_v2_controls -v` vor erster Codeänderung | 172 PASS |
| [qualify_windows.py](qualify_windows.py) | `venv/Scripts/python.exe <dieser Evidenzpfad>/qualify_windows.py`; reproduzierbarer Runner, volle Subprozessbefehle/Timeouts/loghashes | finale Gesamtqualifikation PASS |
| [windows-validation.json](windows-validation.json) | Runner: Runtime, zeitgebundene Kommandos, Exitcodes, 199 Gitblobs, lokale SHA256, unveränderter Produktstand, diffcheck | PASS |
| [tested-product.patch.base64](tested-product.patch.base64) | `git diff --cached --binary --unified=0 HEAD -- voice_stt_client tests scripts`, vor Tests base64 gespeichert | exakter getesteter Produktdiff; Datei-/Decoded-SHA256 im Manifest |
| [targeted-unittest.txt](targeted-unittest.txt) | `-W error -m unittest tests.test_v2_settings_service tests.test_config tests.test_v2_transport tests.test_v2_mirror tests.test_v2_audio_recovery tests.test_v2_controls tests.test_obs050_settings -v` | 243 PASS |
| [server-settings-checkpoint.json](server-settings-checkpoint.json), [stderr](server-settings-checkpoint.json.stderr.txt) | `scripts/check_v2_server_settings.py --server-root C:/Users/marco/AppData/Local/Temp/voice-stt-ap-cv2-020-ada13b0 --server-repository P:/GithubRepos/marcosudau-vps/voice-stt-server/main` | 38 echte HTTP/WS/Media/PCM-Checks PASS; 46 gepinnte importierte Quellblobs |
| [server-contracts.json](server-contracts.json), [vollständiges unittest-Log](server-contracts.json.stderr.txt) | derselbe Serverbefehl mit `--contracts`; settings_control_plane, selected_only, detection, audio_boundary, vier DetectorGainTests | 55 PASS / 0 Skips; 48 verifizierte Quellblobs |
| [compileall.txt](compileall.txt) | `-m compileall -q voice_stt_client scripts tests` | Exit0, erwartbar leeres Quietlog |
| [windows-full-unittest.txt](windows-full-unittest.txt) | `-m unittest discover -s tests -p test_*.py -v` | 1460 PASS |
| [requirement-coverage.md](requirement-coverage.md) | alle29 Requirements mit tatsächlich gelaufenen Methoden/Checkpointfällen | SELF_CHECK_PASS, CLIENT OPEN |
| [handoff-verification.json](handoff-verification.json) | read-only Akten-/Linkprüfung, finale Gitblobs/Loghashes gegen Manifest, kein Produktdelta seit Qualifikation | PASS |

Runnerloghashes gelten für UTF8/LF; Produktbytes können lokal CRLF enthalten, veröffentlichte normalisierte Gitblobs sind separat erfasst. Basis plus Diff/Blobs identifiziert den Kandidaten vor dessen erzeugendem Commit. Finale SHA/Tree werden in der PR und Übergabe extern ergänzt. Eine Runnerwiederholung setzt eine passende staged Kandidatendifferenz voraus; zur externen Prüfung zunächst den getesteten Parent und gespeicherten Diff rekonstruieren oder finale Gitblobs vergleichen.

Reale Testgrenze: Produktions-FastAPI plus tatsächliche Clientservices über Loopback-TCP; PortAudio-/Model-/Recordergrenzen kontrolliert. Kein realer Produktionsserver, ASR-/Hardware-/Kalibrierungsnachweis. Empirische Nutzsprachgrenze **NOT_RUN**, AP-IV2-020. Der echte Clientcheckpoint ist der Pflichtbeleg; die Supplementtests ersetzen ihn nicht. Keine automatische kanonische Übernahme.
