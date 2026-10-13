# Evidenz – AP-CV2-100 / R02-KORREKTUR

**Status:** REVIEW_READY. Selbstchecks, keine unabhängige Eigenabnahme.
Basis ca3cd4009717d508a75ea236aec60881a39fab43 + staged Produktdiff/Gitblobs,
kanonischer Parent dad89bb5d08e6d34abc5cfab57fc76010c5131dc, Server ada13b0.

| Beleg | Erzeugung / Zweck / Ergebnis |
| --- | --- |
| [Startprovenienz](start-provenance.json), [Treiber](record_start.py) | git rev-parse, gh pr view nach fetch/ff-only; aktueller Head/Base, kein Review und vorheriger Status gesichert |
| [CI-Fehlerlog](ci-failed.txt), [Metadaten](ci-failed.json) | gh run view 38342904213 --log-failed / --json; finaler R01-Head, 1573 Tests, 1 ERROR |
| [Baseline](baseline-event-stream.txt), [Repro](replay-deadline-repro.txt), [Treiber](reproduce_ci.py) | Projektvenv; vollständige Befehle/Exits in Logs; 12 PASS vorher, 1 reproduzierbarer FAIL mit 280-ms-Commit |
| [Korrekturtests](corrected-event-stream.txt) | Projektvenv -W error -m unittest tests.test_event_stream -v; 13 PASS einschließlich langsamer dauerhafter Speicherung |
| [Windowsmanifest](windows-validation.json), [Treiber](qualify_windows.py), [exakte Produktdiff](tested-product.patch.base64) | Windows11/Python3.12.10 und Abhängigkeiten, Befehle/Exits/Hashes; 213 Gitblobs, Base+staged Testdiff; PASS |
| [Gezielte Tests](targeted-unittest.txt) | Tatsächlicher vollständiger Befehl im Manifest; 203 PASS, -W error |
| [Windowsvollsuite](windows-full-unittest.txt) | Projektvenv -m unittest discover -s tests -p test_*.py -v; 1574 PASS, keine Skips |
| [Servercheckpoint](server-runtime-checkpoint.json), [stderr](server-runtime-checkpoint.json.stderr.txt) | scripts/check_v2_server_runtime.py mit manifestgebundenem Servercheckout; 17 reale komponierte Client/Serverchecks, 45 Quellen bytegeprüft, PASS |
| [compileall](compileall.txt) | Projektvenv -m compileall -q voice_stt_client scripts tests; Exit0 PASS |
| [Abgabeprüfung](submission-verification.json), [Treiber](verify_submission.py) | 213 staged Gitblobs und Loghashes unverändert, alle neuen/geänderten Markdownlinks und Status/Manifest/Index PASS; tatsächliche PR-Kurzfassung nach Push separat mit read-only-Aktenprüfer prüfen |
| [PR-Vorbereitung](prepare_pr.py) | Externe PR-Beschreibung aus tatsächlichem veröffentlichtem Head/Tree; optionaler CI-Erfolg erst nach SHA-/Ergebnisprüfung |
| [Dokumentationstreiber](complete_records.py) | neue R02-Akte/aktuelle Verweise; abgeschlossene R01-Akte unangetastet |

Alle Qualification-Logs UTF-8 LF vor SHA256 und Versionierung. Konkrete Runtime,
Laufzeiten und Hashes im Manifest, vollständige Tests/Negativdiagnostik in Logs.
CI-Fehlerlog aus gh run view: lediglich Zeilenenden/Zeilenendleerzeichen normalisiert.
CI des endgültig veröffentlichten Heads vor tatsächlicher Reviewübergabe prüfen;
Run/Head/Tree sowie Ergebnis commitgebunden in PR-Beschreibung und Kommentar.
Original-CI-Log und Repro sind erwartete FAIL-Belege, keine aktuellen PASS-Behauptungen.
Keine reale Mikrofon-/Win32-/ASR-Gesamtabnahme, kein eigener ROOT_PASS.
