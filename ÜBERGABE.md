# ÜBERGABE – RealtimeSTT Windows Desktop Client

> **Stand:** 9. August 2026  
> **Projektpfad:** `P:\DockerProjekte\voice-stt-client`  
> **Status:** AP07-M0 bis M3 abgenommen; die Clientimplementierung beginnt mit M4  
> **Nächster Schritt:** M4 / AP07-C1 – Modelle, typisierte Konfiguration und Cursorstore  
> **Repository:** `https://github.com/marcosudau-vps/voice-stt-client` (`PUBLIC`)  
> **Automatischer Stand:** Client 271 Tests und Windows-PyInstaller-Build grün;
> Server 377 Tests grün, 13 Skips; beide `compileall`-Prüfungen grün  
> **Live-Stand:** SQLite-first-Protokoll v2, Session-Scope, Zwei-Session-
> Isolation, HTTP-/SQLite-Korrelation und Replay produktiv belegt  
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
abgenommen; Clientcode für AP7 ist noch nicht implementiert. Ab M4 führt AP7
eine zweite sessiongebundene Verbindung zu `/ws/logs`, Replay/Cursor, einen kontrollierten Fallback, zentralen
Feedback-Reducer sowie Sound- und ReSpeaker-LED-Ausgabe ein. Allgemeine
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
|---|---|
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

Letzter belegter automatischer Stand:

```text
Ran 271 tests
OK
```

Zusätzlich erfolgreich:

- `compileall` über `app.py`, `core/`, `ui/` und `tests/`,
- Offscreen-Qt-Smoke des fünfteiligen Einstellungsdialogs,
- produktiver Health-/WebSocket-/Pong-Test,
- Live-Vertragstest:
  `hotkey → effectiveWakeWordEnabled=False`,
  `wake_word + hey_jarvis → effectiveWakeWordEnabled=True`.
- AP07-Servergesamtsuite: 377 Tests erfolgreich, 13 Skips; `compileall` und
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
`docs/2026-08-09_AP07_M0_BIS_M3_ABNAHME/ABSCHLUSSBERICHT.md`.

Die erwarteten Fehlerlogs der Gesamtsuite stammen aus absichtlich simulierten
Negativfällen.

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
- `docs/2026-08-09_AP07_M0_BIS_M3_ABNAHME/ABSCHLUSSBERICHT.md`
- `docs/RELEASE.md`
- `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md`
- `server-docs-for-client-development/`

Historische datierte Ordner bleiben Belege und überschreiben diesen aktuellen
Stand nicht.
