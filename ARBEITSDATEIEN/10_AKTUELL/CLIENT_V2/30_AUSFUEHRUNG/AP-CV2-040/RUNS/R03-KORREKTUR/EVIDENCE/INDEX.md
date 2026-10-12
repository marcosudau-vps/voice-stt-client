# AP-CV2-040 / R03 – Evidenzindex

[Windowsmanifest](windows-validation.json): Windows/Python3.12/Projektvenv,
Qt offscreen, Dependencies, vollständige Befehle/Exitcodes/Laufzeiten/Testzahlen
und Hashes. Basis `146839809bc234a2dfe4f02cea37d7ce2e4ff480` (übernommene
Reviewspitze) plus genauer [Produkt-/Test-/Harnessdiff](tested-product.patch)
und Gitblobliste identifizieren den korrigierten getesteten Stand. Kanonischer
Featureparent unverändert `3df342c3a7cacaa1226743c4d9bee674e94d33db`.

Erzeugender Befehl:
`.\venv\Scripts\python.exe ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-040/RUNS/R03-KORREKTUR/EVIDENCE/qualify_windows.py`.
[Qualifikationsskript](qualify_windows.py) bewahrt vollständige Logzeilen,
normalisiert UTF-8/LF und entfernt nur Trailing-Space an Testprogresszeilen.
Vor-/Nachher-Quellbytes müssen übereinstimmen.

| Vollständiger Beleg | Ergebnis | SHA256 |
| --- | --- | --- |
| [targeted-unittest.txt](targeted-unittest.txt) | PASS / 228 | `2e01a0455ff30c8c60a178278bde204bee18309f521131dc87310cfea23f1e4a` |
| [server-audio-checkpoint.json](server-audio-checkpoint.json) | PASS / 46 | `9d4e8df8a4b74330eea4440024e3602f6487a2a563e3e0a6342abbf45d6b231a` |
| [server-audio-checkpoint.json.stderr.txt](server-audio-checkpoint.json.stderr.txt) | vollständiges stderr; absichtliches Storeclose1011 | `571a0f4fd2075c7b4325a3d60d5b854e2cda138c7fa7758713314359da0d9935` |
| [compileall.txt](compileall.txt) | PASS / Exit0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| [windows-full-unittest.txt](windows-full-unittest.txt) | PASS / 1373 | `6cb9af956c0c4894ff54dd47e3c31a552d47d05e5b0fe060332daaa99a046294` |
| [baseline-targeted.txt](baseline-targeted.txt) | Vorherbaseline54 PASS | `6118b3488602b67d330bbb6f0e7f276523c81006b92231d1b57545e37092dfff` |
| [repro-before-fix.txt](repro-before-fix.txt) | Erwarteter FAIL,5/5 auf altem Produktstand | `3fe0dbc9ec71f93c3c3425925f02ad7026f818926e4eb0f8813a9f8cd5769af5` |
| [focused-after-fix.txt](focused-after-fix.txt) | PASS,34 neue/erhaltene Audiotests | `829f7f1b1708e3ff1390fefbc0f0b79eae524d64be272dae950bbe5772a0ed0b` |

Vorherbaseline: `.\venv\Scripts\python.exe -W error -m unittest tests.test_v2_audio_recovery tests.test_session_coordinator tests.test_event_stream -v`, vor Produktänderung.
[Reproidentität](repro-identity.json): fünf neue Tests bei unverändertem
Reviewprodukt. Ausgeführte Methoden:
`tests.test_v2_audio_recovery.Media.test_device_loss_reports_false_before_blocked_native_stop`,
`test_hardware_mute_reports_false_before_blocked_native_stop`,
`test_dead_device_reports_false_before_blocked_native_stop`,
`test_native_operation_timeout_closes_logs_and_retries_cleanup`,
`test_native_stop_timeout_closes_logs_and_retries_cleanup` (alle gleicher Klassenprefix).
Reprofail ist erwarteter Fehlernachweis, nicht aktueller Kandidaten-PASS.
Focused-after-fix: `-W error -m unittest tests.test_v2_audio_recovery -v`.

[Requirementcoverage](requirement-coverage.md) nennt alle23 IDs und tatsächliche
Methoden/Serverfälle. [Abgabeprüfung](submission-validation.json) sichert
Akten-/Link-/Diff-/Blob-/Loghashprüfung mit tatsächlicher Kandidatenidentität.

Servercheckpoint: tatsächlicher Capture/PCM/Media/TCP/WS/Decoder/Resampler/
Controller/Ledger-/SQLite-/Logpfad am unveränderten ada13b0. 46 bytegeprüfte
Quellen und46 tatsächliche Fälle. Neu: blockierter nativer Stop, ACK/Cancel
und älterer Final noch vor Stopfreigabe; reale Logtask-/Socketfreigabe trotz
Shutdown-Timeout, danach erneuter erfolgreicher Close. Substituierte Grenzen:
PortAudiohardware, Modelle/Finalscheduler und Wakeengine-Probe; kontrollierte
Thread-Events sind Treiberfaultinputs. Keine echte Hardware-/ASRbehauptung.
Serverstderr zeigt ausschließlich den absichtlichen Store1011-Fehlerpfad.
