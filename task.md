# Arbeitsstand und Aufgaben – RealtimeSTT Windows Desktop Client

> **Status:** aktiver Tracker  
> **Stand:** 12. August 2026
> **Aktives Paket:** AP7 Feedback- und Eventsystem `[M10 DEBUG-FEEDBACK-KORREKTUR ABGENOMMEN]`
> **Nächster Schritt:** gesprochene Bedien-/Disconnect-/Langlaufmatrix und alltagstaugliches Feedbacktuning
> **Separater Restpunkt:** AP6-Wake-Word-Bediennachweis mit echtem Mikrofon  
> **Repository/Release:** öffentliches GitHub-Repository und geprüfte Windows-CI-/Release-Strecke eingerichtet

## Phase 1 – Headless Audio-/WebSocket-Core `[VORHANDEN; LIVE UND AUTOMATISIERT TEILVERIFIZIERT]`

- [x] `core/audio_capture.py`: Mono-PCM16-Aufnahme, bevorzugt 16 kHz, 40-ms-Pakete
- [x] `core/stt_session.py`: WebSocket-Handshake, Protokollzustand, Audioübertragung und Transport-Reconnect
- [x] `app.py`: headless Verdrahtung und Konsolenausgabe von Realtime-/Finaltext
- [x] Live-Smoke-Test am 25. Juli 2026 für Health, `hello`, `ready` und `pong`
- [x] manueller Diagnose-End-to-End-Test am 25. Juli 2026 mit temporär korrigierter Thread-Brücke und „Hey Jarvis“: Wake Word, Aufnahme, Realtime und echter Finaltext erfolgreich; 733/733 Pakete gesendet, keine volle Clientqueue
- [x] thread-sichere Übergabe aus dem Audio-Verarbeitungsthread an die asyncio-Queue am 25. Juli 2026 dauerhaft in `app.py` korrigiert: Übergabe über `loop.call_soon_threadsafe`, kein Audio vor erfolgreich gesendetem `start`, sichere Drop-Grenzen bei Stop/Loop-Ende/Queue-Vollstand
- [x] `tests/test_app.py`: 10 Regressionstests für Event-Loop-Bindung, Fremdthread-Übergabe, Start-Gating und Shutdown-/Überlastgrenzen
- [x] manueller Wiederholungstest mit dem dauerhaft korrigierten regulären `app.py` am 25. Juli 2026: Server-Wake-Word deaktiviert, direkte Realtime-Ausgaben und Finaltext `Test eins, zwei, drei, Test.` erfolgreich
- [x] früheren breiten Sessionprofilentwurf nach damaliger Serverprüfung
  verworfen und aus dem Client entfernt
- [x] verworfene Serverprofil-Spezifikation nach `docs/archive/2026-07-25_SERVER_SESSION_PROFILE_SPECIFICATION_VERWORFEN.md` archiviert
- [x] neuer enger Session-Create-Contract des Servers am 26. Juli 2026 live
  verifiziert: Hotkey/Wake Word pro Session, logische Wake-Word-IDs,
  Tuningwerte, sichtbare Fallbacks und Isolation
- [x] Einbindung des neuen Session-Create-Contracts im konsolidierten
  AP6-Paketvertrag festgelegt; Implementierung bleibt Phase 6
- [x] Resume-Frage verbindlich entschieden: Ein unterbrochenes Diktat ist
  beendet; kein automatischer Neustart und kein Audio-Replay nach Reconnect
- [x] zuverlässige Ping-Miss-Erkennung umgesetzt und im AP5-Vertrag abgesichert

Hinweis: Es existieren weder `core/audio_processor.py` noch `core/stt_client.py`. `AudioCapture` liefert bereits `int16`; lokales Resampling ist nicht implementiert.

## Phase 1.5 – Transkript-Historie (AP1) `[ABGESCHLOSSEN]`

- [x] `core/history.py`: RAM- und selektive SQLite-Speicherung finaler Transkripte und Einfügeversuche
- [x] Deduplizierung über `(session_id, segment_id)`
- [x] `tests/test_history.py`: 30 Tests erfolgreich
- [x] Einbindung in den realen Finalevent-Pfad in AP4 umgesetzt

## Phase 2 – Textinjektion (AP2) `[ABGESCHLOSSEN]`

- [x] `core/text_injector.py`: serialisierte FIFO-Queue, Clipboard und `SendInput`
- [x] definierter Queue-Lifecycle und nicht-daemonisierter Worker
- [x] `tests/test_text_injector.py`: 41 Tests mit Test-Backend erfolgreich
- [x] manueller Notepad-Smoke-Test am 25. Juli 2026: `command_sent`, Text im fokussierten Notepad erschienen und vorheriger Clipboard-Inhalt wiederhergestellt
- [x] Einbindung in den realen Finalevent-Pfad in AP4 umgesetzt

## Phase 3 – Erneutes Einfügen (AP3) `[ABGESCHLOSSEN]`

- [x] `core/reinsertion.py`: `TranscriptReinsertionService`
- [x] Memory-first-Auflösung, SQLite-Fallback und definierte Resultatstatus
- [x] `tests/test_reinsertion.py`: 26 Tests erfolgreich
- [x] Controller-Anbindung in AP4 umgesetzt (Korrekturrunde 3 abgeschlossen)
- [x] Hotkey, Tray-Menü und Verlaufsauswahl in AP6 umgesetzt

## Phase 4 – Controller-Integration (AP4) `[ABGESCHLOSSEN]`

- [x] Integrationsgrundlage unter `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md` erstellt
- [x] vollständiger operativer Ausführungs- und Reviewauftrag unter `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md` erstellt
- [x] E-01 bis E-04 für AP4 umgesetzt: History-before-enqueue, getrennte Fehlersemantik, rohes `final`-Event als autoritative Identität, keine Hotkeys
- [x] E-05 für AP4 abgegrenzt: Audio-Thread-Brücke vor AP4 korrigiert; Ping-Miss-Erkennung und endgültige Reconnect-Semantik an AP5 übergeben
- [x] E-07 getrennt und nicht blockierend evaluiert: AP4 nimmt keine Betriebsmodus- oder Wake-Word-Override-Lösung vorweg
- [x] Vollständig exception-sicheren Run-Lifecycle umgesetzt (`try/finally` um `_loop` & `start_queue()`, schrittweise Task-Aufnahme)
- [x] Cancellation-geschützten gemeinsamen Shutdown umgesetzt (`asyncio.shield()`)
- [x] Aufnahmeübergänge atomar serialisiert (`asyncio.Lock`, `_start_dictation_locked`, `_stop_dictation_locked`)
- [x] Vulnerable Lifecycle-Rennen zusätzlich unabhängig abgesichert: partieller Task-Start, Queue-Start-Rollback, Cancellation-geschützter Shutdown, Shutdown gegen Aufnahmeübergang und Finalannahme gegen Closing
- [x] Tests und Typimporte in `app.py` und `tests/test_controller.py` bereinigt; neue Race-Tests verwenden Events statt willkürlicher Wartezeiten
- [x] Kanonische Dokumentation synchronisiert

## Phase 5 – Fehlerverhalten und Selbstheilung (AP5) `[ABGESCHLOSSEN]`

- [x] Produktentscheidung unter `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md` angenommen
- [x] verbindlichen Paketvertrag unter `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md` erstellt
- [x] operativen Ausführungsauftrag unter `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG_AUSFUEHRUNGSAUFTRAG.md` erstellt
- [x] Diktat bei Sessionverlust endgültig beenden; kein Resume und kein Audio-Replay
- [x] Start nur bei `READY`, ohne Vormerkung, und erst nach Serverstatus derselben Session bestätigen (Timeout 10 Sekunden)
- [x] stillen unbegrenzten Reconnect mit gedeckeltem Backoff (30s max einschließlich konfiguriertem Jitteranteil 0,3), CloseCode 1013 Spezialbehandlung (10s min) und sauberer Shutdown-Unterbrechung umgesetzt
- [x] Ping-Miss-Erkennung korrigiert (max 1 ausstehender Ping, ohne RTT-Kaschierung) und deterministisch getestet
- [x] Backoff-Reset ausschließlich beim ersten gültigen `pong` einer Session
- [x] persistente UI-neutrale Zustände (`AvailabilityState`, `DictationState`, `ControllerStatusSnapshot`) und sparsame Feedbackereignisse (`TransientEvent`) bereitstellen
- [x] Session-, Audio-, Task- und Queuegrenzen über Reconnects und Session-Generationen hinweg abgesichert
- [x] Antigravity-Erstimplementierung kritisch nachgeprüft und Race Conditions bei Startbestätigung, Disconnect während `STARTING`, Ping/Pong, Timeout-Reconnect sowie Session-/Audiogrenzen korrigiert
- [x] vollständige AP5- und Regressionstests durchgeführt (197 Tests grün)
- [x] echter `STTSession`-Live-Smoke-Test gegen den produktiven Server ohne Audio erfolgreich: `hello → ready → gültiger pong → sauberer stop`
- [x] Abnahme und Selbstfertigstellung unter `docs/2026-07-25_AP05_ANTIGRAVITY/GESAMTABNAHME_UND_SELBSTFERTIGSTELLUNG.md` dokumentiert

## Phase 6 – UI-Shell, Betriebsmodi und Einstellungen (AP6) `[FIX VERIFIZIERT – WAKE-WORD-BEDIENNACHWEIS OFFEN]`

- [x] verbindlichen Paketvertrag und Ausführungsauftrag unter
  `docs/work-packages/AP06_UI_SHELL*.md` erstellt
- [x] Vor-AP6-Baseline erneut ausgeführt: 197 Tests in 5,530 Sekunden
- [x] PySide6-`QApplication` im Main Thread
- [x] `QSystemTrayIcon` mit Status, Bedienaktionen und dynamischem Verlauf
- [x] passives, nicht fokussierbares und maustransparentes Overlay
- [x] Qt-Signalbrücke vom Core zur UI
- [x] thread-sichere Befehlsbrücke von Qt zum asyncio-Core
- [x] globale Hotkeys via Win32 `RegisterHotKey` mit Konflikt-Rollback
- [x] Reinsertion über Hotkey, Tray und ID-gebundene Verlaufsauswahl
- [x] nativer Win32-Single-Instance-Guard vor dem Corestart
- [x] GUI als regulärer Start; Diagnosepfad über `app.py --headless`
- [x] gezielte AP6-Härtung: 74 Tests erfolgreich
- [x] Gesamtsuite nach erster AP6-Umsetzung: 238 Tests in 6,181 Sekunden erfolgreich
- [x] `py_compile`, nativer Win32-Smoke und vollständiger AP6-Live-Smoke mit
  echtem Tray, Mutex, Hotkeys, separatem Core-Thread und Server-`READY`
  erfolgreich
- [x] Abnahme dokumentiert unter
  `docs/2026-07-25_AP06_ABNAHME/ABNAHMEBERICHT.md`
- [x] Overlay-Signalfehler vom 26. Juli behoben: Core-Payload
  `(segment_id, text, is_final)` wird explizit auf `(text, is_final)` adaptiert
- [x] Regressionstest für die reale CoreBridge→Overlay-Verdrahtung ergänzt
- [x] aktualisierte Server-Client-Dokumentation aus dem Server-Repository nach
  `server-docs-for-client-development/` synchronisiert
- [x] produktiven Session-Wake-Word-Contract aus Clientperspektive geprüft:
  `hello`/`ready`, Hotkey- und Wake-Session, parallele Isolation,
  Startstatus, Soft-Fallbacks und Close 1008 bei hartem Konfigurationsfehler
- [x] aktuelle `STTSession` mit `wakeWordEnabled=false` und
  `wakeWordEnabled=true&wakeWords=hey_jarvis` jeweils bis `READY` geprüft
- [x] Serverauffälligkeit bei Contract-Integration clientseitig gehärtet:
  Hotkey-Session meldet vor `start` wiederholt
  `state=voice` bei `activeClientId=null`; echte Startbestätigung besitzt
  `activeClientId == sessionId`
- [x] `error.where=session_config` bei Integration als deterministischen
  Konfigurationsfehler behandeln und keine blinde Reconnectschleife starten
- [x] Gesamtsuite nach Overlay-Fix: 239 Tests in 6,726 Sekunden erfolgreich;
  `py_compile` erfolgreich
- [x] endgültigen AP6-Folgeumfang am 27. Juli mit dem Benutzer konsolidiert und
  im bestehenden Paketvertrag materialisiert; die frühere Frageliste ist keine
  parallele Quelle mehr
- [x] operativen Folgeauftrag aus
  `docs/work-packages/AP06_UI_SHELL.md` erstellen und vor der ersten
  Codeänderung als Umsetzungsgrundlage freigeben
- [x] typisierte Betriebsmodus- und Session-Wake-Word-Konfiguration ergänzt
- [x] gewünschte Queryparameter sicher erzeugt und effektive
  `hello`-/`ready.sessionConfig` einschließlich Warnungen, Fallbacks und
  1008-Fehlersemantik auswerten
- [x] Hotkey- und Wake-Word-Modus einschließlich kontrolliertem
  Modus-Reconnect implementieren
- [x] Hotkey-Diktatfenster mit 15s Initial-Timeout, konfigurierbarem
  Follow-up-Fenster und 15s Standardverlängerung implementieren; keine lokale
  VAD nachbauen
- [x] Startdefault des regulären Follow-up-Fensters auf 3s festgelegt und in
  Bedienlauf festlegen und anschließend in `config.yaml`, Metadaten,
  Tests und Dokumentation identisch materialisieren
- [x] deklarative Einstellungsmetadaten über der typisierten `AppConfig`
  implementieren; keinen zweiten unabhängigen Wertespeicher einführen
- [x] per-user Override-Konfiguration atomar laden/speichern und sichere
  Apply-/Rollback-Policies umsetzen
- [x] Aktionsregistrierung und frei konfigurierbare, kollisionssichere globale
  Hotkeys implementieren
- [x] Einstellungsdialog mit den Tabs Verlauf, Allgemein,
  Verbindung/Betriebsmodus, Geräte/Audio und Erscheinungsbild/Feedback
  implementieren
- [x] statische Mikrofonwahl und manuellen Mikrofontest angebunden; Hot-Plug und
  automatische Geräteheilung nicht vorwegnehmen
- [x] Verlaufspflege einschließlich definierter Lösch- und
  Deduplizierungssemantik umsetzen
- [x] optionales nicht blockierendes Soundfeedback und kleinen
  Overlay-/Statusindikator umsetzen; nur ausgewählte lizenzgeprüfte Assets
  verwenden
- [x] 18 gezielte neue Härtungstests, vollständige Regression (257 Tests),
  `py_compile`, Offscreen-Qt und sicherer Live-Vertragstest beider Modi
  erfolgreich; der frühere native Windows-Smoke bleibt gültig
- [x] manuelle Bedienprüfungen 1 bis 4 erfolgreich: Hotkey-End-to-End,
  Initial-Timeout, Folgeaufnahme und Verlängerung
- [x] Moduswechselprüfung 5 korrigiert: persistenter Maintainer besteht
  unabhängig vom Startmodus und armt den Stream beim Hinwechsel automatisch
- [x] Rückwechsel korrigiert: Moduswechsel lassen den Maintainer ruhen, sein
  Lifecycle endet nur noch durch den gemeinsamen Core-Shutdown
- [x] atomaren Aktivierungsvertrag ergänzt: Wake-Word-Apply erst nach neuer
  `READY`-Generation und serverbestätigtem Streamstart erfolgreich
- [x] bestätigten Rollback bei Reconnect- oder Streamaktivierungsfehler ergänzt
- [x] frühere Fehlerfolge lokal dreifach, mit Aktivierungsfehler und
  Reconnect-Härtung sowie produktiv in zwei vollständigen Wechselzyklen
  erfolgreich provoziert
- [ ] gesprochenes `hey_jarvis` mit echtem Mikrofon nach dem Fix einmal
  manuell bestätigen
- [x] neues Tray-Farbkonzept umgesetzt: Hotkey dunkel-/hellgrün, Wake Word
  dunkel-/hellblau, weißer Sprachwarte-Rand, Gelb nur für äußere Störungen,
  Rot nur für tatsächliche Fehler
- [x] Fehleranalyse und Client-/Server-Abgrenzung unter
  `docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md`
  dokumentiert
- [x] Implementierung und lokale/produktive Fixverifikation unter
  `docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md` dokumentiert
- [x] AP6-Dokumentation nach tatsächlicher Implementierung erneut
  synchronisieren und erst dann abschließen

## Phase 7 – Feedback- und Eventsystem (AP7) `[M0–M9 ABGENOMMEN – M10 IN ARBEIT]`

- [x] Debug-Feedback-Korrektur vom 12. August 2026 `[ABGENOMMEN]`
  - [x] unveränderte Clientbaseline: 435 Tests in 22,513 Sekunden erfolgreich
  - [x] `client.lifecycle.started`/`stopping` im produktiven GUI-Lifecycle
    genau einmal veröffentlichen und LED-Startzustand real belegen
  - [x] Mute-Beobachtung bei LED-Reconnect/Sinkwechsel erhalten
  - [x] genau acht lizenzierte, rein nichtsprachliche, gebündelte PCM-WAV-Cues mit stabiler
    Source-/PyInstaller-Pfadauflösung bereitstellen
  - [x] Tickton plus selbst rendernden LED-Countdown in den letzten drei
    Sekunden des Hotkey- und Wake-Word-Follow-up-Fensters ergänzen
  - [x] vorübergehend auffälliges LED-/Sound-Mapping und höhere
    Diagnosehelligkeit aktivieren
  - [x] Eventstream-Degradation als technische Tray-Notiz ohne wiederholtes
    Warnoverlay behandeln
  - [x] datensparsame Feedback-Entscheidungsspur für Event-/Korrelationsanalyse
  - [x] 151 fokussierte und 451 vollständige Clienttests, `compileall`,
    Onefile-Build, acht reale Qt-Sounds sowie ReSpeaker-Countdown vollständig
    und vorzeitig beendet abnehmen

- [x] bisherige Diskussion in eine verbindliche Gesamtplanung konsolidiert
- [x] historische Zwischenstände nach
  `docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/`
  verschoben
- [x] Paketvertrag unter
  `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md` erstellt
- [x] detaillierten Meilensteinplan unter
  `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md` erstellt
- [x] M0: Server-/Clientbaselines und Aktionsdokumentation vorbereitet
- [x] M1: Server-EventHub und Store auf SQLite-first umgebaut und durch die
  Servergesamtsuite abgenommen
- [x] M2: `/ws/logs`, Cursorfehler, Empty-Final, Deployment und Liveabnahme;
  `transcription.completed` produktiv zwischen Live, HTTP/SQLite und Replay
  korreliert, Zwei-Session-Scope zusätzlich belegt
- [x] M3: produktiven Serververtrag nach
  `server-docs-for-client-development/` synchronisieren
- [x] M4: immutable Clientmodelle, typisierte Eventstream-Konfiguration,
  strikt validiertes YAML-Mapping für `server.*`- und lokale
  `client.*`-Ereignisse sowie atomaren, endpointgebundenen Cursorstore
- [x] M4-Abnahme: 32 fokussierte Tests, vollständige Regression mit 285 Tests
  und `compileall` erfolgreich; keine UI- oder WebSocketkopplung vorgezogen
- [x] M5: isolierten `/ws/logs`-Transport mit getrenntem Reconnect, Replay,
  Ping/Pong und cancellation-sicherem Shutdown sowie strikten
  Protokollprocessor implementiert
- [x] M5-Abnahme: 23 fokussierte Tests einschließlich `-W error`, vollständige
  Regression mit 308 Tests und `compileall` erfolgreich
- [x] M6: gemeinsamen `DualSessionCoordinator` und generationgebundenen
  `SessionContext` integrieren; `hello.logAccess` nur für dieselbe aktuelle
  STT-Session übernehmen, alte Tokens/Events bei Reconnect invalidieren und
  beide Transporte gemeinsam deterministisch beenden
- [x] M6-Abnahme: 14 neue Race-/Lifecycle-Prüfungen, 59 relevante Tests mit
  `-W error`, vollständige Regression mit 322 Tests und `compileall`
  erfolgreich; Audio-, Finaltext-, Historien- und Injectionpfad unverändert
- [x] M7: exakte Server- und lokale Clientevents normalisieren; reinen Reducer,
  impulsfreies Replay, Ein-Quellen-Regel und duplikatsicheren STT-Fallback
  integrieren
- [x] M7-Abnahme: 30 fokussierte Tests, 183 relevante Tests mit `-W error`,
  vollständige Regression mit 352 Tests, `compileall` und `git diff --check`
  erfolgreich
- [x] M8: veröffentlichte Reducerausgaben queued an Qt, Tray und Overlay
  anbinden; sieben YAML-konfigurierbare Sound-Cues integrieren und alte
  Command-Sounds entfernen
- [x] M8-Abnahme: 13 neue Tests, 232 relevante Tests mit `-W error`, vollständige
  Regression mit 365 Tests, `compileall`, `git diff --check`, Offscreen-Qt-
  Zustandsprüfung und realer Qt-Soundbackend-Smoke erfolgreich
- [x] M9: ReSpeaker XVF3800 über eigenen minimalen USB-Adapter und Nulladapter
  integrieren; Updates koaleszieren, Pulse zurückführen, Fehler drosseln und
  Shutdown sicher begrenzen
- [x] M9-Abnahme: 13 neue Tests, 254 relevante Tests mit `-W error`, vollständige
  Regression mit 378 Tests, realer Firmware-/LED-Smoke, `compileall`,
  `git diff --check` und PyInstaller-Onefile-Build mit libusb erfolgreich
- [ ] M10: automatische und reale End-to-End-Fehlerkampagne `[IN ARBEIT]`
  - [x] Servergesamtsuite zweimal stabil: je 379 Tests, 13 Skips und 78
    Subtests; `compileall` und `git diff --check` grün
  - [x] Clientgesamtsuite nach der Härtung zweimal stabil: je 396 Tests; 227 fokussierte
    AP07-Tests mit `-W error`, `compileall` und `git diff --check` grün
  - [x] sichere Live-Smokes für beide Sessionmodi, zwei Laufzeitmoduswechsel,
    sessiongebundenen `/ws/logs`-Replay/LIVE-Pfad und Adapterausfälle grün
  - [x] Prüfbericht und vollständige 13-Punkte-Matrix unter
    `docs/2026-08-09_AP07_M10_FEHLERKAMPAGNE/PRUEFBERICHT.md`
  - [x] isolierte lokale Store-/Retention-/WebSocket-Kampagne sowie echter
    Neustart über zwei Betriebssystemprozesse mit persistiertem SQLite-Store
  - [x] realer ReSpeaker-Smoke mit fünf Effekten, abschließendem `off` und
    ohne verwaisten Hilfsprozess
  - [x] PyInstaller-Onefile-Build 0.1.0 einschließlich Multiprocessing,
    libusb und `--version`-Smoke
  - [ ] erneuter realer Hotkey-Gesamtlauf mit sichtbarem AP07-Feedback
  - [ ] gesprochener Wake-Word-/Follow-up-Gesamtlauf mit sichtbarem Feedback
  - [ ] sichtbare Disconnect-/Reconnect-Beobachtung während gesprochenem Diktat
  - [ ] realer Langlauf mit Latenz-/Ressourcenbeobachtung
  - [ ] reale stille Aufnahme für terminales `discarded`
- [ ] M11: Dokumentation und operative Gesamtabnahme

## Phase 8 – Härtung und Polish (AP8) `[OFFEN]`

- [ ] allgemeine Reconnect- und Langzeit-Stresstests über AP7 hinaus
- [ ] Mikrofonverlust, Hot-Plug und Gerätewechsel behandeln
- [ ] Windows-Sleep/Wake und tatsächlichen Audiowiederanlauf absichern
- [ ] Multi-Monitor- und DPI-Handling
- [ ] Autostart und weitergehendes Packaging-/Release-Polish; reproduzierbarer
  PyInstaller-Basisbuild, Commit-CI und taggesteuertes GitHub-Release sind
  bereits vorbereitet
- [x] öffentliche Repository-Basis und Laufzeitdatei-Hygiene: Secrets,
  Datenbanken, Caches, Buildausgaben, rohe Exporte und nicht freigegebene
  Sound-Sichtungssammlung werden nicht versioniert
- [ ] vollständige Release-, End-to-End- und Bedienprüfungen

## Repository-, CI- und Release-Vorbereitung `[ABGESCHLOSSEN]`

- [x] öffentliches Repository
  `https://github.com/marcosudau-vps/voice-stt-client` angelegt
- [x] `.gitignore` und `.gitattributes` für Secrets, lokale Laufzeitdaten,
  Buildausgaben und nicht veröffentlichte Rohsammlungen ergänzt
- [x] `VERSION` als einzige Release-Versionsquelle eingeführt; Startparameter
  `--version` und Windows-Dateiversion stimmen überein
- [x] `scripts/build.py` und `voice-stt-client.spec` bauen und prüfen eine
  fensterlose PyInstaller-Onefile-EXE
- [x] `.github/workflows/ci.yml` führt auf normalen Pushes und Pull Requests
  Tests, `compileall`, EXE-Build und Smoke aus und lädt die EXE als Artefakt hoch
- [x] `.github/workflows/release.yml` prüft Tags erneut und erstellt ein
  GitHub-Release mit versionierter EXE und SHA-256-Datei
- [x] `scripts/release.py` bestimmt die nächste Version, rollt lokale
  Prüffehler zurück, wartet auf grünes CI für exakt den Release-Commit und
  taggt erst danach; kein Sync in ein zweites Repository
- [x] lokaler PyInstaller-Build für `0.1.0`: 73.299.320 Byte,
  SHA-256 `ddea29ee62e0a8ba56063d0702b3d1e81c78b4c94db1d93e96bc2fb47e834f37`

---

## Test-Zusammenfassung

Zuletzt am 12. August 2026 ausgeführt (Vor-AP6-Baseline war 197 Tests):

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Ergebnis: **451 Clienttests erfolgreich**; `compileall` über `app.py`,
`core/`, `ui/`, `scripts/` und `tests/` ebenfalls erfolgreich. Die aktuelle
Servergesamtsuite bestand mit **378 Tests bei 13 Skips und 78 Subtests**. Der AP07-Livevertrag wurde mit zwei isolierten
Sessions sowie einem echten Audiofixture-Ereignis geprüft. Details siehe
`ÜBERGABE.md` und
`docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/2026-08-09_AP07_M0_BIS_M3_ABNAHME_ABSCHLUSSBERICHT.md`.

- AP1 Historie: 30
- AP2 Text-Injection-Queue: 41
- AP3 Reinsertion: 26
- Controller-Integration, Lifecycle und AP5-Härtung: 64
- Config-Prüfung: 19
- AP07-M4 Eventmodelle, YAML-Mapping und Cursorstore: 13
- AP07-M5 EventStreamTransport und Protokollprocessor: 23
- AP07-M6 Dual-SessionCoordinator und Race-Integration: 12
- AP07-M7 Normalisierung, Reducer und Controller-Integration: 30
- AP07-M8 Qt-, Tray-, Overlay- und Soundintegration: 13
- AP07-M9 ReSpeaker-USB-LED-Adapter und Replay-Härtung: 13
- Session-, Backoff- und Ping/Pong-Härtung: 18
- `app.py` Audio-Thread-Brücke und DI-Isolation: 10
- native Hotkeys: 6
- Single Instance: 3
- Präsentation, Tray und Overlay: 14
- Qt-/asyncio-Core-Brücke: 6
- GUI-Komposition und Startfehler: 8
- AP6-Folgeumfang (Modi, Einstellungen, Diktatfenster): 22
- Build-, Versions- und Releaseautomation: 7

Nicht durch diesen Lauf geprüft sind ein absichtlich ausgelöster realer
Netzabbruch während eines Mikrofon-Diktats, Mikrofonverlust/Hot-Plug/Sleep-Wake,
Langzeitbetrieb sowie Multi-Monitor-/DPI-Verhalten. Diese Härtung bleibt
ausdrücklich AP8. AP7 besitzt eine eigene Dual-WebSocket- und
Eventstrom-Fehlerkampagne.
