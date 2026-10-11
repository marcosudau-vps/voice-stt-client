# AP-CV2-000 / R02-ABNAHME – Review-Evidenzindex

- Prüfkandidat: `8b1c4c157b6b431dac6af69e2e264d0c37579bef`
- Tree: `cc099b87c450b91ad4eefddf11a3715ddf4ccf3e`
- Parent: `050e776cf316eb332177294db0c0a2719c2b4415`
- Serverbaseline: `ada13b011e1d3829f78e7f389e3b927795a2b3be`
- Umgebung des Reviewers: GitHub-Remote-Dateiansicht/Gitdaten und Actions-Protokolle; **kein** lokaler Windows-Checkout und **keine** lauffähige Projekt-venv.
- Der Reviewer hat **keinen** Test ausgeführt. Der nachfolgend geprüfte Windows-CI-Lauf ist ein externer Runnerbeleg und ausdrücklich keine eigene Regressionsausführung.

| ID | Beleg | Vorgehen/Identität | Ergebnis |
| --- | --- | --- | --- |
| EV-01 | [PR #2](https://github.com/marcosudau-vps/voice-stt-client/pull/2), Git-Refs und Git-Commitobjekte | Head `8b1c4c157b6b431dac6af69e2e264d0c37579bef`, Base `050e776cf316eb332177294db0c0a2719c2b4415`, Headtree `cc099b87c450b91ad4eefddf11a3715ddf4ccf3e`; drei Paketcommits, Base unverändert | PASS – Remote-Provenienz |
| EV-02 | [GitHub Actions 38145266161](https://github.com/marcosudau-vps/voice-stt-client/actions/runs/38145266161) | Windows-CI-Job 114487166298; tatsächliche Steps/Joblog eingesehen | Externe CI: PASS; 1221 Unittests, compileall, EXE-Smoke, Wheel/sdist/Twine, Wheelimport, Artefakt-Upload |
| EV-03 | [Quellcode startup-hotkey](https://github.com/marcosudau-vps/voice-stt-client/blob/8b1c4c157b6b431dac6af69e2e264d0c37579bef/voice_stt_client/ui/application.py#L225-L315) | Statischer Datenfluss `start()` → `_register_startup_hotkeys()` → `save_user()` → `bridge.start()` | Finding CV2-R02-F01; Kontrollfluss im eingereichten Source nachgewiesen, **kein dynamischer Repro** |
| EV-04 | [Hotkey-Backend](https://github.com/marcosudau-vps/voice-stt-client/blob/8b1c4c157b6b431dac6af69e2e264d0c37579bef/voice_stt_client/ui/hotkeys.py#L155-L305) | Fehler bei `RegisterHotKey` → `last_failure`, Kandidat `register()` | Statische Prüfung |
| EV-05 | [Konfigurationspfad und Persistenz](https://github.com/marcosudau-vps/voice-stt-client/blob/8b1c4c157b6b431dac6af69e2e264d0c37579bef/voice_stt_client/core/config.py#L1005-L1250) | `AppConfig.load()` und `save_user()`, atomisches Ersetzen der Profil-YAML | Statische Prüfung |
| EV-06 | [AP-Paketvertrag](https://github.com/marcosudau-vps/voice-stt-client/blob/8b1c4c157b6b431dac6af69e2e264d0c37579bef/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/ARBEITSPAKETE/AP-CV2-000.md), [R01](https://github.com/marcosudau-vps/voice-stt-client/blob/8b1c4c157b6b431dac6af69e2e264d0c37579bef/ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R01-UMSETZUNG/01_REPORT.md) | BASE-01…12, Zwischencheckpoint, Selbsttests und Produktgrenzen gelesen | Dokument-/Requirement-Sichtung, kein umfassender eigener Produktlauf |
| EV-07 | Eigenständige vollständige Windows-Clientsuite und fehlergerichtete Hotkey-Repros | Kein lokaler Windows-Checkout/venv ausführbar und kein externer Bedienernachweis dieses Reviewruns | **NOT_RUN**, ROOT_PASS ausgeschlossen |

Statische Prüfmethode: konkreten Kontrollfluss mit Dateipfaden/Zeilen und vorliegenden Tests verglichen; fehlende dynamische Wirkung ausdrücklich nicht als gemessen ausgegeben. Der im CI-Log sichtbare erwartete SQLite-Lock-Fehler stammt aus einem negativen Historytest; der betreffende Job endet trotzdem mit 1221 Tests und OK.
