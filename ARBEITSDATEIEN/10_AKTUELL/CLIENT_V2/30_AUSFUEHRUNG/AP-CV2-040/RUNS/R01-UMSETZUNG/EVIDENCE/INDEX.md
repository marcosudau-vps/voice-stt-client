# AP-CV2-040 / R01 – Evidenzindex

[Windowsqualifikationsmanifest](windows-validation.json) ist die vollständige
Identität/Befehls-/Exitcode-/Laufzeit-/Hashliste; Windows/Python3.12,
Projektvenv, Qt offscreen. Der erzeugende Befehl ist
`.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-040/RUNS/R01-UMSETZUNG/EVIDENCE/qualify_windows.py`.
[Reproduktionsskript](qualify_windows.py). Vollständige Logs, keine Auszüge.
Getestete Basis `3df342c3a7cacaa1226743c4d9bee674e94d33db` plus genauer
[Produktdiff](tested-product.patch), Gitblobliste und Vorher/Nachher-Laufzeitbytes.
Administrative Nachträge sind separat in der Abgabeprüfung identifiziert.

| Artefakt | Ergebnis | SHA256 |
| --- | --- | --- |
| [targeted-unittest.txt](targeted-unittest.txt) | PASS / 222 | `7b7664fd039e1065f12104696abe93d6e6597dd6af258736eb431d0466aadf45` |
| [server-audio-checkpoint.json](server-audio-checkpoint.json) | PASS / 41 | `0788d8377fd09128e6e4a287c9744e0a54ee7b1ba821088cdc2356139ca3e08d` |
| [server-audio-checkpoint.json.stderr.txt](server-audio-checkpoint.json.stderr.txt) | vollständiges stderr, absichtlicher Storeclose1011 | `571a0f4fd2075c7b4325a3d60d5b854e2cda138c7fa7758713314359da0d9935` |
| [compileall.txt](compileall.txt) | PASS / Exit0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| [windows-full-unittest.txt](windows-full-unittest.txt) | PASS / 1367 | `335317df380d1b13824d36b6c990478f11e060e844a54653dbe3eda33d4de36e` |
| [baseline.txt](baseline.txt) | Vorherbaseline,128 PASS | `74770c50f2eb8a9f5c1930c5a15328c2fa2cb60f3221c72df43b5199219d5736` |
| [tested-product.patch](tested-product.patch) | exakt gestagter Produkt-/Test-/Harnessdiff | `5d87fe46852c8ee3ecdffed5604e1ce144f93f0cb8aa441fb321408a617963d4` |

Baselinebefehl vor Änderung: `.\venv\Scripts\python.exe -m unittest tests.test_audio_capture tests.test_session_coordinator tests.test_event_protocol tests.test_event_stream tests.test_event_cursor_store tests.test_v2_transport tests.test_v2_mirror`, Qt offscreen.

[Requirementcoverage](requirement-coverage.md) verknüpft alle23 IDs mit
konkreten tatsächlich ausgeführten Methoden und realen Serverfällen.
[Vorgängerübernahme](predecessor-canonicalization.json): Fetch-/PR-/Parent-/
Baumprüfung mit tatsächlichen menschlichen Freigabe-/Abschlusskommentaren.
[Startvertragshashes](start-contract-hashes.json) sichern den unveränderten
fachlichen Ausgangsvertrag vor Implementierung. K-04-Stringsegmentklärung
ist anhand unveränderter Serverquellen und echtem Logcheckpoint belegt.

[Abgabeprüfung](submission-validation.json) enthält tatsächliche
Akten-/Diff-/Produktblob-/Requirementtext-/Loghashprüfung und Veröffentlichungs-
identitäten; nach erfolgreicher Prüfung gesichert, kein eigener ROOT_PASS.

Servercheckpointbefehl steht im Windowsmanifest: `scripts/check_v2_server_audio.py`
mit byteidentischem ada13b0-Export und referenzierter Server-Gitrepositoryprüfung.
Tatsächlicher Capture/Media/Transport über TCP/WS bis FastAPIdecoder/Resampler/
Gate/Controller/Ledger; reale SQLite/WSlogs/Filter/Replay/Pruning/Auth. 46 tatsächlich
geladene Pythonquellen werden gegen den gepinnten Gitblob verglichen.
Substituiert: PortAudiohardware, Modelle/Finalscheduler, Wakeengine-Probe;
Faultinputs: synthetische Retentiontimestamp/Storeavailability. Reale
Hardware/ASR **NOT_PROVEN**, spätere IV2-Gates; kein live-VPS-Eingriff.

Vollsuite: ein bestehender unittest-Progressline-Trailing-Space für Gitdiffcheck entfernt; sämtliche Zeilen erhalten, ursprünglicher Captured-Hash im Windowsmanifest.
