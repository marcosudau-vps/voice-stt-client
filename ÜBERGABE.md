# ÜBERGABE – RealtimeSTT Windows Desktop Client

> **Stand:** 12. August 2026
> **Projektpfad:** `P:\GithubRepos\marcosudau-vps\voice-stt-client`
> **Status:** AP07-M0 bis M9 und akute M10-Debugfeedback-Korrektur abgenommen
> **Nächster Schritt:** verbleibende gesprochene M10-Bedien-, Disconnect- und Langlaufmatrix sowie Alltagstuning
> **Repository:** `https://github.com/marcosudau-vps/voice-stt-client` (`PUBLIC`)  
> **Automatischer Stand:** Client 451 Tests und `compileall` grün; aktueller
> Windows-PyInstaller-Build grün;
> Server 378 Tests, 13 Skips und 78 Subtests grün
> **Live-Stand:** zusätzlich beide Sessionmodi, zwei Laufzeitmoduswechsel und
> sessiongebundener `/ws/logs`-Replay/LIVE-Pfad ohne Audio oder Injection grün
> **Separater Restpunkt:** gesprochenes `hey_jarvis` nach dem AP6-Fix einmal
> mit echtem Mikrofon bestätigen

## 1. Projektziel und aktueller Stand

Der Windows-Client läuft im Hintergrund, überträgt Mikrofon-Audio an
`wss://stt.voice.marcosudau.com/ws/transcribe`, zeigt Realtime-Text nur
passiv an und fügt ausschließlich Finaltexte über Clipboard und `SendInput`
in die fokussierte Anwendung ein.

Implementiert sind:

- AP1: thread-sichere RAM-/SQLite-Transkripthistorie,
- AP2: serialisierte Text-Injection-Queue,
- AP3: Reinsertion früherer Finaltexte,
- AP4: UI-neutraler Integrationscontroller,
- AP5: stille, unbegrenzte Transportheilung ohne Fortsetzung abgebrochener
  Diktate,
- AP6: PySide6-Tray, passives Overlay, native globale Win32-Hotkeys,
  Single Instance, Qt-/asyncio-Brücke, Betriebsmodi, Hotkey-Diktatfenster,
  Einstellungen, Verlaufspflege und optionales Feedback.

Die Servervorstufe und Vertragsynchronisierung von AP7 (M0–M3) sind
abgenommen. M4 stellt immutable Event-/Kontrollmodelle, eine typisierte
Eventstream-Konfiguration, ein strikt validiertes YAML-Mapping für
`server.*`- und lokale `client.*`-Ereignisse sowie einen atomaren,
endpointgebundenen Cursorstore bereit. Mit M5 führt AP7 eine zweite
sessiongebundene Verbindung zu `/ws/logs` ein. Der isolierte Transport und der
strikte Protokollprocessor sind mit M5 einschließlich Replay/Live, Reconnect,
Ping/Pong, expliziter Cursorbestätigung und typisierten Fehlerfällen
implementiert. M6 ergänzt den generationgebundenen `DualSessionCoordinator`:
Er übernimmt `hello.logAccess` ausschließlich für die aktuelle STT-Session,
verwirft alte Tokens und In-Flight-Events beim Reconnect, behandelt
Tokenablauf/`available=false` und beendet beide Transporte deterministisch.
M7 führt exakte Eventnormalisierung, reinen Feedback-Reducer, impulsfreies
Replay, begrenzte Deduplizierung und kontrollierten STT-Fallback ein. M8 bindet
die Reducerausgaben queued an Qt, Tray und Overlay an, wahrt die vorhandenen
Modusfarben und erzeugt optionale Sounds ausschließlich aus den sieben
YAML-konfigurierbaren Cues. Adapterfehler bleiben nicht fatal und werden als
lokales `client.sound.failed` zurückgeführt. M9 steuert den nachgewiesenen
ReSpeaker XVF3800 über einen koaleszierenden USB-Worker, isoliert Gerätefehler
als `client.led.unavailable` und setzt beim Shutdown sicher `off`. Allgemeine
Geräte-Hot-Plug-Heilung, Sleep/Wake, Multi-Monitor/DPI, Autostart,
weitergehendes Packaging-/Release-Polish und Langzeit-/Stresstests folgen als
AP8; die grundlegende GitHub-/CI-/PyInstaller-/Release-Strecke ist bereits da.

## 2. Bedien- und Betriebsmodi

### Hotkeymodus

- Sessionanforderung: `wakeWordEnabled=false`.
- `Ctrl+Shift+Space` startet das Diktat.
- Nach bestätigtem `start` läuft ein Initial-Sprach-Timeout von 15 Sekunden.
- `recording_started` und `recording_ended` des Servers steuern Segment- und
  Follow-up-Phase; es existiert kein lokales VAD.
- Das Follow-up-Fenster beträgt derzeit 3 Sekunden.
- Ein erneuter primärer Hotkeydruck verlängert das aktuelle beziehungsweise
  vorgemerkte Fenster standardmäßig um 15 Sekunden.
- Ein unterbrochenes oder kontrolliert reconnectetes Diktat wird beendet und
  nicht fortgesetzt.

### Wake-Word-Modus

- Sessionanforderung: `wakeWordEnabled=true`.
- Projektdefault für die logische Modell-ID: `hey_jarvis`.
- Nach `ready` wird der Audiostream einmal gestartet und bleibt auch in
  `wakeword_wait` aktiv.
- Nach heilbaren Reconnects wird dieser Hintergrundmodus neu scharfgeschaltet.
- Bewusstes Pausieren über die primäre Aktion bleibt respektiert.

Für beide Modi ist ausschließlich
`sessionConfig.effectiveWakeWordEnabled` in `hello` und `ready` maßgeblich.
Fallbacks, Warnungen und ignorierte Felder werden protokolliert. Ein
`error.where=session_config` beziehungsweise eine widersprechende effektive
Konfiguration pausiert Reconnects bis zu einer tatsächlichen
Konfigurationsänderung.

### Tray- und Feedbackfarben

| Zustand | Farbe |
| --- | --- |
| Hotkeymodus wartet / nimmt auf | dunkelgrün / hellgrün |
| Wake-Word-Modus wartet / nimmt auf | dunkelblau / hellblau |
| wartet auf erste oder weitere Sprache | jeweilige dunkle Modusfarbe mit weißem Rand |
| äußeres Netzwerk-, Server-, Timeout-, Audio- oder Mikrofonproblem | gelb |
| tatsächlicher interner oder protokollarischer Fehler | rot |
| Wake Word pausiert, Shutdown oder beendet | grau |

Gelb und Rot sind damit keine Betriebsmodusfarben. Gelb signalisiert eine
äußere Störung; Rot bleibt echten Fehlerzuständen vorbehalten.

## 3. Einstellungen und Persistenz

`AppConfig` und ihre typisierten Unterobjekte sind die einzige Wertquelle.
`core/settings_metadata.py` beschreibt Darstellung, Grenzen und
Änderungswirkung, speichert aber keine eigenen Laufzeitwerte.

Ladereihenfolge:

1. Code-/Dataclass-Defaults,
2. versionierte `config.yaml`,
3. `%LOCALAPPDATA%\RealtimeSTT Client\config.yaml`.

Der Benutzer-Override wird atomar über temporäre Datei und `os.replace`
geschrieben. Enthält er unbekannte Felder, wird der Override vollständig
verworfen statt teilweise übernommen. Vor jeder Änderung wird eine vollständige
Kandidatenkonfiguration validiert. Hotkey-, Audio- und Sessionübernahmen
besitzen Rollbackpfade.

Der Einstellungsdialog enthält genau:

1. Verlauf,
2. Allgemein,
3. Verbindung & Betriebsmodus,
4. Geräte & Audio,
5. Erscheinungsbild & Feedback.

Der Verlauf unterstützt Reinsertion, einzelnes Löschen und bestätigtes
Gesamtlöschen. Gelöschte Einträge verlieren während des laufenden Prozesses
nicht ihre Deduplizierungsidentität.

## 4. Threading und öffentliche Grenzen

- Qt-Widgets, Tray, Overlay, Dialog und Native Event Filter: Main Thread.
- `STTController`, `STTSession` und asyncio: eigener nicht-daemonisierter
  `RealtimeSTT-AsyncCore`-Thread.
- Audio: sounddevice-Callback-/Verarbeitungsthread, Übergabe via
  `loop.call_soon_threadsafe`.
- Textinjektion: eigener nicht-daemonisierter FIFO-Worker.

Wichtige neue Schnittstellen:

```python
EventStreamAccess(...)
EventProtocolProcessor.begin_subscription()
EventProtocolProcessor.process_frame(frame)
EventProtocolProcessor.confirm_event(result)
await EventStreamTransport.run()
await EventStreamTransport.reconfigure(access)
await EventStreamTransport.stop()

await DualSessionCoordinator.begin_generation(generation)
await DualSessionCoordinator.adopt_hello(generation, hello)
await DualSessionCoordinator.invalidate_generation(generation)
await DualSessionCoordinator.shutdown()

SessionConfig.build_url(base_url)
await STTSession.reconfigure(session_config, server_config)

await STTController.primary_dictation_action()
STTController.extend_dictation_window()
await STTController.cancel_dictation()
await STTController.apply_runtime_config(candidate)

TranscriptHistoryManager.delete_entry(entry_id)
TranscriptHistoryManager.clear_entries()
```

Finaltexte bleiben die einzige Quelle für automatische Historie und
Textinjektion. Realtime- und Timeline-Ereignisse werden nie eingefügt.

## 5. Start und Prüfkommandos

Regulärer Start:

```powershell
.\venv\Scripts\python.exe app.py
```

Headless-Diagnose:

```powershell
.\venv\Scripts\python.exe app.py --headless
```

Automatische Gesamtsuite:

```powershell
$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py" -v
```

Sicherer Live-Smoke beider Sessionmodi, ohne Audio oder Textinjektion:

```powershell
$env:PYTHONUTF8='1'
.\venv\Scripts\python.exe -m tests.manual_test_ap06_modes
```

Sichere AP07-Live-Smokes ohne Aufnahme oder Textinjektion:

```powershell
$env:PYTHONUTF8='1'
.\venv\Scripts\python.exe -m tests.manual_test_ap07_event_stream

$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m tests.manual_test_ap07_adapter_failures
.\venv\Scripts\python.exe -m tests.manual_test_ap07_led_hardware
```

Letzter belegter automatischer Stand:

```text
Ran 396 tests
OK
```

Zusätzlich erfolgreich:

- M10: beide vollständigen Gesamtsuiten wiederholt stabil; Client 396 Tests,
  Server 379 Tests bei 13 Skips und 78 Subtests,
- M10: 227 fokussierte AP07-/Reconnect-Tests mit `-W error`,
- M10: echter sessiongebundener STT- plus `/ws/logs`-Handshake über Replay bis
  LIVE und sauberer gemeinsamer Shutdown,
- M10: reale Adapterklassen mit nicht vorhandenem USB-Gerät und defektem
Soundasset; Fehler isoliert, gedrosselt und Worker sauber beendet,
- Debugfeedback: Start-/Stopping-Lifecycle exakt einmal, Helligkeit 192/255,
  acht ausgelieferte nichtsprachliche PCM-WAVs und unabhängige Cue-Player,
- Timeoutfeedback: `easter_egg_tick` als dreisekündiger Tick-Cue plus LEFX-
  `countdown_ring` für Hotkey- und Wake-Word-Follow-up; neue Sprache stoppt
  beide Ausgaben,
- M10: isolierte Store-/Retention-/WebSocket-Kampagne und persistenter
  Serverneustart über zwei echte Betriebssystemprozesse grün,
- M10: Cursor-Schreibfehler/Replays ohne Doppelimpuls, extreme Backoffzähler,
  Tokenablauf, Prozessstart-, Pipe-, Timeout- und Minimal-Shutdown-Fälle grün,
- M10: echter ReSpeaker-Smoke über fünf Effekte bis `off`, ohne verwaisten
  Hilfsprozess,

- 32 fokussierte AP07-M4-Tests für Konfiguration, Modelle, YAML-Mapping und
  Cursorstore,
- 23 fokussierte AP07-M5-Tests für Protokoll, Replay/Live, Reconnect,
  Cursorbestätigung und Shutdown; zusätzlich mit `-W error` grün,
- 14 neue AP07-M6-Race-/Lifecycle-Tests für Generation, Session-/Tokenbindung,
  Reconnect, stale Events und gemeinsamen Shutdown; 59 relevante Prüfungen
  zusätzlich mit `-W error` grün,
- 30 AP07-M7-Tests für Normalisierung, Reducer, Replay, Quellenwechsel,
  Fallback, Deduplizierung und neutrale Controllerausgabe; 183 relevante
  Prüfungen zusätzlich mit `-W error` grün,
- 13 neue AP07-M8-Prüfungen für queued Qt-Übergabe, Mappingwirkung,
  Eventstream-Zusatzstatus, Replay-/Legacy-Soundunterdrückung und isolierte
  Soundfehler; 232 relevante Prüfungen zusätzlich mit `-W error` grün,
- 13 neue AP07-M9-Prüfungen für USB-Kommandos, Koaleszierung,
  Impulsrückkehr, Replayunterdrückung, Hardwareverlust, Fehlerdrosselung und
  begrenzten Shutdown; 254 relevante Prüfungen zusätzlich mit `-W error` grün,
- ReSpeaker-Hardware: `VID_2886/PID_001A`, Control-Interface 3, Firmware
  `2.0.10`; realer LED-Smoke für sechs Dauerzustände und einen Erfolgsimpuls,
- Windows-Onefile-Build mit gebündelter `libusb-1.0.dll`: 74.758.009 Byte,
  SHA-256 `1e6b2b54ed010149bd233d3c77071a096df769de9bac3dfbc41d06d234bd5d5a`,
- realer Qt-Soundbackend-Smoke mit lokalem Windows-WAV: Asset akzeptiert,
  Backendstatus `Ready`, keine Fehlermeldung,
- `compileall` über `app.py`, `core/`, `ui/`, `scripts/` und `tests/`,
- Offscreen-Qt-Smoke des fünfteiligen Einstellungsdialogs,
- produktiver Health-/WebSocket-/Pong-Test,
- Live-Vertragstest:
  `hotkey → effectiveWakeWordEnabled=False`,
  `wake_word + hey_jarvis → effectiveWakeWordEnabled=True`.
- AP07-Servergesamtsuite: zweimal 379 Tests erfolgreich, 13 Skips; `compileall` und
  `git diff --check` grün.
- Produktiver AP07-Livevertrag: `logProtocolVersion=2`,
  `deliveryMode=sqlite_first`, zwei voneinander isolierte Session-Scope-
  Abonnements sowie Replay nach Reconnect.
- Ein durch die vorhandene Server-Test-WAV ausgelöstes
  `transcription.completed` wurde ohne Ausgabe von Transkriptinhalt über
  Event-ID/Cursor zwischen Live-Stream, HTTP-/SQLite-Historie und Replay
  korreliert.
- PyInstaller-Onefile-Build `dist/voice-stt-client.exe` für Version `0.1.0`:
  73.299.320 Byte; eingebettete Datei-/Produktversion und `--version`-Smoke
  erfolgreich.
- aktueller Debugfeedback-Onefile-Build für Version `0.2.0`: 73.747.530 Byte,
  SHA-256 `0b43f3da0ed61304087a32d952ce1c42011f42a717b22c7027ac3888f8f8b7ac`;
  acht WAVs plus Attribution im Archiv nachgewiesen.

Build und Release:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe scripts\build.py --clean
.\venv\Scripts\python.exe scripts\release.py --dry-run
.\venv\Scripts\python.exe scripts\release.py
```

Der Releasebefehl setzt die Version erst innerhalb eines rückrollbaren lokalen
Gates, wartet vor dem Tag auf grünes GitHub-CI für exakt den Release-Commit und
lässt das Tag-Workflow anschließend EXE und `SHA256SUMS.txt` veröffentlichen.
Details: `docs/RELEASE.md`.

Der vollständige Nachweis für M0–M3 steht unter
`docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/2026-08-09_AP07_M0_BIS_M3_ABNAHME_ABSCHLUSSBERICHT.md`.

Der aktuelle M10-Prüfstand und die noch offene reale 13-Punkte-Matrix stehen
unter `docs/2026-08-09_AP07_M10_FEHLERKAMPAGNE/PRUEFBERICHT.md`. M10 ist noch
nicht abgeschlossen: gesprochenes Hotkey-/Wake-Word-E2E, sichtbarer realer
STT-Disconnect, stilles Final und Langlauf fehlen. Store, Retention und
Serverneustart sind in der isolierten lokalen Kampagne erledigt.

Die erwarteten Fehlerlogs der Gesamtsuite stammen aus absichtlich simulierten
Negativfällen.

Auf diesem Windows-Host können Python-3.12-Plattformabfragen über WMI hängen.
Tests verwenden deshalb feste Windows-Werte. Der native LED-Zugriff läuft in
einem abbrechbaren Hilfsprozess; Build-Isolate und Onefile-App erhalten vor
Abhängigkeitsimporten eine Windows-spezifische Plattforminitialisierung. Der
Build-, Versions- und Prozessabschluss-Smoke ist damit grün.

## 6. Ergebnis des manuellen Schluss-Smokes

Die Prüfungen 1 bis 4 wurden am 28. Juli erfolgreich durchgeführt:

1. Hotkeystart bis Finaltext und Textinjektion;
2. Initial-Timeout ohne Sprache;
3. Folgeaufnahme nach kurzer Pause;
4. Hotkeyverlängerung bei längerer Denkpause.

Prüfung 5 deckte zwei eindeutige Clientfehler auf, die anschließend behoben
wurden:

1. Der Wake-Word-Maintainer existiert nun dauerhaft unabhängig vom Startmodus.
2. Moduswechsel beenden ihn nicht mehr und können daher keinen fatalen
   Helperabschluss erzeugen.
3. Ein Wechsel nach Wake Word gilt erst nach bestätigtem `READY`, gestartetem
   Audio und serverbestätigtem `start` als erfolgreich.
4. Scheitert die Aktivierung, wird die letzte Konfiguration einschließlich
   bestätigter Servergeneration wiederhergestellt.

Die frühere Fehlerfolge wurde lokal dreimal wiederholt. Zusätzlich bestanden
gegen den produktiven Server zwei vollständige Wechselzyklen über die
Generationen 1 bis 5; der Stream war bei jedem Hinwechsel aktiv und der Core
blieb bei jedem Rückwechsel am Leben.

Der sichere Live-Test verwendete absichtlich kein Mikrofon-Audio. Die
tatsächliche Erkennung eines gesprochenen `hey_jarvis` bleibt daher als kurzer
manueller Hardware-/Server-Nachweis offen. Vollständiger Fixnachweis:
`docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md`.

## 7. Maßgebliche Dokumente

- `docs/IMPLEMENTATION_ROADMAP.md`
- `docs/PROJEKTUEBERSICHT.md`
- `task.md`
- `docs/work-packages/AP06_UI_SHELL.md`
- `docs/work-packages/AP06_UI_SHELL_FOLGEUMFANG_AUSFUEHRUNGSAUFTRAG.md`
- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md`
- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md`
- `docs/2026-07-28_AP06_FOLGEUMFANG_ABSCHLUSS/ABSCHLUSSBERICHT.md`
- `docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md`
- `docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md`
- `docs/2026-07-30_PROJEKT_EVENT_FEEDBACK_SYSTEM/zwischenstaende_bis_2026-08-01/2026-08-09_AP07_M0_BIS_M3_ABNAHME_ABSCHLUSSBERICHT.md`
- `docs/RELEASE.md`
- `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md`
- `server-docs-for-client-development/`

Historische datierte Ordner bleiben Belege und überschreiben diesen aktuellen
Stand nicht.
