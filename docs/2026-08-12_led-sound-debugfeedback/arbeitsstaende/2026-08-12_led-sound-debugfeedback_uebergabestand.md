# Übergabestand: LED-, Sound- und Timeout-Debugfeedback

**Stand:** 12. August 2026, 19:45 Uhr  
**Status:** Implementierung, Race-Fix, Regressionen, Build und reale technische Abnahme abgeschlossen.  
**Federführung:** `P:\GithubRepos\marcosudau-vps\voice-stt-client`  
**Zweck:** Vollständiger Wiederanlaufpunkt für einen Agenten ohne Gesprächskontext.

## 1. Auftrag und Ziel

Das akute Problem war fehlendes beziehungsweise kaum sichtbares ReSpeaker-LED-
Feedback und nicht hörbares Soundfeedback. Für die Diagnosephase soll das
Feedback bewusst auffällig sein. Zusätzlich sollen in den letzten drei Sekunden
des Nachsprechfensters der nichtsprachliche Sound `easter_egg_tick.mp3` und ein
ablaufender LED-Ring warnen. Effekte mit gesprochener Stimme dürfen nicht
verwendet werden.

Der Benutzer hat ausdrücklich erlaubt, den echten ReSpeaker zu verwenden, echte
Sounds abzuspielen, den Live-Server abzufragen und blockierende eigene
Clientprozesse zu beenden. Ein VPS-Login ist nicht erforderlich; alle drei
Repositories sind laut Benutzer aktuell.

## 2. Repositories und Schutz fremder Arbeit

Ausgangscommits:

- Client: `467a6b699b470df4a7bb15e1c81126c37036facd`
- Server: `13c162950b944dc715fdd81983a7465f8eb0fd79`
- LED-Controller: `aa2f14bd13dd75bce2221fdcadd50b38a5c8c1b0`

Ein anderer Agent arbeitet parallel an einem anderen Auftrag. Unbekannte
Änderungen nicht zurücksetzen. Im LED-Repository ist `uv.lock` fremd geändert
(Versionswerte `3.0.2` auf `3.0.3`); die Datei wurde nicht angefasst. Das
Server-Repository ist sauber. Sämtliche Produktänderungen dieses Pakets liegen
im Client-Repository; die Dateien unter `zusammenarbeit/` liegen außerhalb der
drei Git-Repositories.

## 3. Gesicherte Ursache

- Die LEFX-Engine rendert kontinuierlich. Der echte Ring bestand alle 13
  Hardwareziele; geänderte Frames werden korrekt übertragen.
- Der Client veröffentlichte `client.lifecycle.started` und
  `client.lifecycle.stopping` vorher nie. Dadurch fehlte besonders der
  initiale dauerhafte LED-Zustand.
- Sounds waren in Projekt- und Benutzerkonfiguration deaktiviert, alle Pfade
  leer und keine Assets in der EXE gebündelt.
- Ein einziges, bei jedem Cue umgeladenes `QSoundEffect` konnte schnelle
  Tonfolgen gegenseitig abbrechen.
- Die Helligkeit `64/255` war für den Diagnosezweck praktisch zu dunkel.
- `client.event_stream.degraded` erzeugte neben seiner technischen Tray-Notiz
  ein unnötiges Warn-Overlay.
- `status(silence)` ist kein autoritatives Segmentende und darf den Countdown
  nicht auslösen. Im Hotkeymodus gilt der bestehende lokale `FOLLOWUP_WAIT`-
  Timer; im Wake-Word-Modus gilt `wakeword_followup_started` mit
  `durationSeconds` bis `recording_started` oder `wakeword_followup_timeout`.

## 4. Implementierte Produktänderungen

### Lifecycle, LED und Diagnose

- `ui/application.py`: Started-/Stopping-Lifecycle exakt einmal, kompakte
  inhaltsarme Feedback-Entscheidungsspur, lokale Live-LED-Regeln ohne
  Reducerimpuls sowie erhaltener Mute-Callback nach LED-Neuaufbau.
- `ui/core_bridge.py`: optional begrenztes Warten auf die Verarbeitung lokalen
  Feedbacks, damit das Stopping-Ereignis vor dem Abbau nicht verloren geht.
- `core/led_controller.py` und `ui/led_feedback.py`: öffentliches
  `set_overlay` bis zum LEFX-Service weitergereicht.
- `config.yaml`: Diagnosehelligkeit `192/255`, auffällige Ereignismatrix und
  technische Eventstream-Degradation ohne App-Warnwirkung.

### Sound und Paketierung

- `ui/feedback.py`: stabile Auflösung absoluter, `~`- und relativer
  Source-/PyInstaller-Pfade; ein vorgeladener Player je Cue; sichere
  Rekonfiguration; explizites `play|stop` für den Tick-Cue.
- `voice-stt-client.spec`: vollständige Bündelung des Debug-Soundordners.
- `scripts/build_debug_feedback_sounds.ps1`: reproduzierbare ffmpeg-Erzeugung.
- `assets/feedback_sounds/debug/`: exakt acht ausgelieferte PCM-WAVs plus
  `ATTRIBUTION.md`. Der große Rohquellenordner bleibt ignoriert.

Verwendete ausschließlich nichtsprachliche Quellen:

| Cue | Quelle |
| --- | --- |
| `wake_word` | `wake_word_triggered.flac` |
| `start` | `center_button_press.flac` |
| `stop` | `mute_switch_on.flac` |
| `complete` | `timer_finished.flac` |
| `cancel` | `center_button_double_press.flac` |
| `warning` | `jack_disconnected.flac` |
| `error` | `mute_switch_off.flac` |
| `timeout_tick` | `easter_egg_tick.mp3` |

Alle Quellen stammen aus Home Assistant Voice Preview Edition Sounds,
Clayton Charles Tapp, CC BY 4.0. Die drei zunächst verwendeten sprachhaltigen
Factory-/Cloud-Dateien wurden vollständig aus Buildskript und Attribution
entfernt.

### Timeout-Countdown

- Neue kanonische Ereignisse:
  `client.dictation.timeout_warning` und
  `client.dictation.timeout_warning_cleared`.
- Neue Konfiguration:
  `dictation_window.timeout_warning_seconds` (Standard 3,0 s) und
  `feedback.timeout_tick_sound`.
- Startregel: `countdown_ring`, 3.000 ms, Grün → Gelb → Rot, letzte 20 Prozent
  pulsierend; parallel `timeout_tick`.
- Frühe neue Sprache, Verlängerung, Stop oder Timeout beenden den Tick. Weil
  Timed Overlays keinen Clear-Kanal besitzen, ersetzt die Clear-Regel den Ring
  deterministisch durch ein 1-ms-dunkles Overlay.
- Hotkey- und Wake-Word-Modus benutzen dieselbe Warnlogik, aber jeweils ihren
  autoritativen Timer. Der effektive Alltagsmodus ist derzeit `wake_word`.

## 5. Verifikation und Artefakte

### Client

- Baseline vor Änderungen: 435 Tests erfolgreich.
- Nach erster LED-/Soundkorrektur: 442 Tests erfolgreich.
- Nach Countdown: 449 Tests erfolgreich.
- Nach dem abschließenden Auto-Start-Race-Fix: **451 Tests in 24,80 s**,
  erfolgreich.
- `compileall` erfolgreich.
- Fokussierte Countdown-/Mapping-/UI-/Bridge-Tests: 151 erfolgreich.
- `git diff --check` war nach dem Produktcode grün; nach den abschließenden
  Dokumentänderungen erneut ausführen.

### Server und LED-Controller

- Server mit isoliertem Tempordner: **378 passed, 13 skipped, 78 subtests
  passed**, eine Warnung, 12,68 s.
- LED-Controller, kompletter sinnvoller Nicht-Hardware-Rest: **1.519 passed,
  3 skipped, 7 deselected**, eine Warnung, 51,76 s.
- Der einzeln ausgeschlossene vorhandene Windows-Test
  `test_a_running_service_is_reported_rather_than_fought_with` unterbricht sich
  selbst: `_process_alive()` ruft `os.kill(pid, 0)` auf; Signal 0 entspricht
  unter Windows `CTRL_C_EVENT`. Das ist ein unabhängiger Test-/Plattformfehler,
  kein Fehler dieser LED-Änderung. Log:
  `led_controller_respeaker-v3\tests\.cache\codex-session-trace-20260812-192801-out.txt`.
- Erfolgreicher Restlauf:
  `led_controller_respeaker-v3\tests\.cache\codex-nonhardware-minus-session-20260812-192850-out.txt`.

### Build, Sound und echtes Gerät

- PyInstaller-Onefile-Build Version 0.2.0:
  `voice-stt-client\dist\voice-stt-client.exe`
- Größe: 73.747.530 Byte.
- SHA-256:
  `0b43f3da0ed61304087a32d952ce1c42011f42a717b22c7027ac3888f8f8b7ac`
- Archivprüfung: alle acht WAVs und Attribution enthalten.
- Echter Qt-Audiotest: alle acht Cues jeweils `Ready`, `playing=True`, keine
  gemeldeten Fehler.
- Echter ReSpeaker-Countdown: früher Clear und voller Ablauf erfolgreich;
  141 Renderdurchläufe, Sink verfügbar, Worker sauber beendet.
- Vorheriger kompletter ReSpeaker-Lauf: alle 13 Mappingziele erfolgreich.
- Der nach allen Fixes neu erstellte Build erreichte am 12. August um 19:44 Uhr
  ReSpeaker, Server `READY`, Audio-Capture und Eventstream `LIVE` und läuft beim
  Schreiben dieses Dokuments weiter. Prozess vor Übernahme stets neu prüfen;
  Logpfad siehe unten.

## 6. Wirksame Benutzerkonfiguration und Laufzeit

Sicherung:

`C:\Users\marco\AppData\Local\RealtimeSTT Client\config.yaml.backup-debug-feedback-20260812-190600`

Die wirksame Konfiguration wurde gezielt aktualisiert und behielt alle übrigen
Werte. Geladener Zustand: `session.mode=wake_word`, Warnzeit 3,0 s, Tickpfad
gesetzt und 32 Feedbackereignisse. Die Logging-Konfiguration zeigt weiterhin
auf:

`P:\DockerProjekte\RealtimeSTT_client\logs\client.log`

Deshalb ist `%LOCALAPPDATA%\RealtimeSTT Client\logs\client.log` nicht der
aktuelle Laufzeitnachweis. Es wurde kein Startup-, Registry-Run- oder
Scheduled-Task-Eintrag gefunden. Der alte Client aus `P:\DockerProjekte` wurde
beendet; gestartet wird ausschließlich die kanonische Projektroot-Fassung.

Aktueller Start:

`voice-stt-client\dist\voice-stt-client.exe`

Bekannte Laufzeitbeobachtungen:

- `RegisterHotKey` meldet Fehler 1409, weil die Tastenkombination bereits von
  einer anderen Anwendung registriert ist. Der aktive Wake-Word-Modus und die
  hier implementierte Feedbackkette funktionieren trotzdem.
- Ein erster echter Build-Start um 19:29 Uhr offenbarte einen reproduzierbaren
  Auto-Start-Wettlauf: `_auto_start_when_ready()` deutete den allgemeinen
  Zustand `_dictation_requested` fälschlich als eigenes One-Shot-Signal,
  während der Wake-Word-Maintainer bereits startete. Ein separates
  `_initial_auto_start_requested`-Flag beseitigt die Zustandsverwechslung und
  erhält die bisherige öffentliche Semantik. Direkte Reproduktion: vorher
  19/20 fatal, nach Fix 0/20. Zwei neue Regressionstests sichern Wake-Word-
  Hintergrundstart und Stop vor `READY`; der finale Build erreichte `LIVE`.

## 7. Restpunkte und nächste sinnvolle Schritte

1. Breiten gesprochenen Alltags-E2E-Lauf durchführen: Wake Word, Sprache,
   Nachsprechfenster, Tick/Ring, neue Sprache und Timeout. Die Komponenten sind
   einzeln real geprüft; besonders beobachten, ob der Lautsprecher-Tick trotz
   Echoausschaltung den VAD anregt.
2. Danach die bewusst auffällige Diagnosekonfiguration im Alltag beobachten
   und erst in einem Folgepaket auf eine ruhigere Konfiguration reduzieren.

## 8. Nicht-Ziele dieses Pakets

- Keine Änderung der Server-VAD-/Recorderlogik.
- Keine neue allgemeine Profilarchitektur oder große Feedback-
  Einstellungsseite.
- Keine Änderung am größeren geplanten Hybridmodus-Umbau.
- Doppeltes Texteinfügen bleibt ein getrenntes Folgeproblem; die neue
  datensparsame Korrelationsspur erleichtert dessen Diagnose.

## 9. Referenzen

- Implementierungsplan:
  `zusammenarbeit\planungen\2026-08-12_implementierungsplan_led-sound-debugfeedback.md`
- Voruntersuchung:
  `zusammenarbeit\berichte\2026-08-12_led-steuerung_untersuchungsbericht.md`
- Abschlussbericht (bei Abschluss anzulegen):
  `zusammenarbeit\berichte\2026-08-12_led-sound-debugfeedback_abschlussbericht.md`

Dieses Dokument muss nach jeder weiteren Code-, Test-, Laufzeit- oder
Entscheidungsänderung aktualisiert werden, bevor die Aufgabe abgegeben wird.
