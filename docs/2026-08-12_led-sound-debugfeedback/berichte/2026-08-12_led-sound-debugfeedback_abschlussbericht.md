# Abschlussbericht: LED-, Sound- und Timeout-Debugfeedback

**Datum:** 12. August 2026  
**Projektroot:** `P:\GithubRepos\marcosudau-vps`  
**Umsetzung:** `voice-stt-client`  
**Status:** Kernfunktion implementiert und technisch abgenommen

## 1. Ergebnis

Das zuvor ausbleibende beziehungsweise kaum wahrnehmbare Gerätefeedback ist im
Desktop-Client behoben. Der ReSpeaker erhält beim Clientstart jetzt zuverlässig
einen sichtbaren Grundzustand, fachliche Ereignisse erzeugen ein bewusst
auffälliges LED- und Soundfeedback und die letzten drei Sekunden des
Nachsprechfensters werden durch einen tickenden Sound sowie einen ablaufenden
LED-Ring angezeigt.

Alle acht ausgelieferten Soundeffekte sind nichtsprachlich. Die zunächst
verwendeten drei Dateien mit Stimme wurden ersetzt. Server und LED-Controller
mussten produktiv nicht geändert werden.

## 2. Ursache

Die ursprüngliche Vermutung einer nicht kontinuierlich rendernden LED-Engine
hat sich nicht bestätigt. LEFX rendert kontinuierlich und überträgt absichtlich
nur geänderte USB-Frames. Die wesentlichen Ursachen lagen im Client:

- Die bereits vorgesehenen Ereignisse `client.lifecycle.started` und
  `client.lifecycle.stopping` wurden produktiv nie veröffentlicht. Damit fehlte
  besonders der initiale dauerhafte LED-Zustand.
- Soundfeedback war in Projekt- und Benutzerkonfiguration deaktiviert; alle
  Soundpfade waren leer und PyInstaller bündelte keine Assets.
- Ein einzelner, für jeden Cue neu geladener `QSoundEffect` konnte schnelle
  Tonfolgen gegenseitig abbrechen.
- Die Diagnosehelligkeit `64/255` war zu niedrig.
- Die technische Eventstream-Degradation erzeugte unnötig ein fachlich
  wirkendes Warn-Overlay.

## 3. Umgesetzte Änderungen

### Lifecycle und Feedbackpfad

- Started- und Stopping-Lifecycle werden exakt einmal in den zentralen
  Feedbackpfad eingespeist.
- Lokale Liveereignisse dürfen LED-Aktionen auch ohne Reducerimpuls auslösen;
  Replay bleibt weiterhin wirkungslos.
- Der LED-Neuaufbau behält Mute-Callback und Gerätebeobachtung.
- Das Stopping-Ereignis kann mit begrenztem Warten vor dem Adapterabbau
  verarbeitet werden; der harte LED-Shutdown bleibt erhalten.
- Jede Feedbackentscheidung erhält eine strukturierte Logzeile mit Ereignis,
  Quelle, Reducerzustand, Replay-/Duplikatstatus, IDs und ausgewählten LED-/
  Soundaktionen. Audio- und Transkriptinhalt wird nicht protokolliert.

### LED

- Diagnosehelligkeit auf `192/255` erhöht.
- Das bestehende deklarative Mapping unterscheidet Start, Wake Word, Aufnahme,
  Verarbeitung, Erfolg, Abbruch, Warnung, Fehler und weitere relevante
  Zustände deutlich.
- `set_overlay` wird durch Mapping, Controllerprotokoll, In-Process-Adapter und
  Qt-Worker bis zum LEFX-Service unterstützt.
- Routineübergänge des Eventstreams bleiben technisch sichtbar, erzeugen aber
  nicht mehr das störende Warn-Overlay.

### Sound

- Jeder Cue besitzt einen eigenen vorgeladenen `QSoundEffect`.
- Absolute Pfade, `~`, Source-Ressourcen und PyInstaller-`_MEIPASS` werden
  stabil aufgelöst.
- Rekonfiguration stoppt und entsorgt alte Player sauber.
- Soundaktionen unterstützen `play` und `stop`; ein anderer Cue beendet einen
  noch laufenden Timeout-Tick.
- Exakt acht WAVs werden reproduzierbar erzeugt, attribuiert und in die EXE
  eingebettet:

| Cue | Nichtsprachliche Quelle |
| --- | --- |
| `wake_word` | `wake_word_triggered.flac` |
| `start` | `center_button_press.flac` |
| `stop` | `mute_switch_on.flac` |
| `complete` | `timer_finished.flac` |
| `cancel` | `center_button_double_press.flac` |
| `warning` | `jack_disconnected.flac` |
| `error` | `mute_switch_off.flac` |
| `timeout_tick` | `easter_egg_tick.mp3` |

Die Quellen stammen aus Home Assistant Voice Preview Edition Sounds von
Clayton Charles Tapp und stehen unter CC BY 4.0. Attribution und
Änderungshinweis liegen direkt neben den ausgelieferten WAVs.

### Timeout-Countdown

Der Countdown folgt nicht einem ungenauen `status(silence)`, sondern dem
jeweils autoritativen Zeitfenster:

- Hotkeymodus: lokaler `FOLLOWUP_WAIT`-Timer nach `recording_ended`.
- Wake-Word-Modus: `wakeword_followup_started.durationSeconds` bis zu neuer
  `recording_started`-Timeline oder `wakeword_followup_timeout`.

In den letzten standardmäßig drei Sekunden startet `timeout_tick` zusammen mit
dem vorhandenen LEFX-`countdown_ring`. Der Ring leert sich, wechselt Grün → Gelb
→ Rot und pulsiert im letzten Fünftel. Neue Sprache, Verlängerung, Stop oder
Timeout beenden das Ticken. Da Timed Overlays keinen adressierbaren Clear-Kanal
besitzen, ersetzt die Clear-Regel den Ring durch ein 1-ms-dunkles Overlay.

## 4. Verifikation

### Automatisiert

| Bereich | Ergebnis |
| --- | --- |
| Client-Baseline | 435 Tests bestanden |
| Client nach erster LED-/Soundkorrektur | 442 Tests bestanden |
| Client nach Countdown | 449 Tests bestanden |
| Client final nach Auto-Start-Race-Fix | **451 Tests in 24,80 s bestanden** |
| Fokussierter Countdown-/Feedbacksatz | 151 Tests bestanden |
| Python-Kompilierung | `compileall` bestanden |
| Server | **378 passed, 13 skipped, 78 subtests passed**, 1 Warnung |
| LED-Controller | **1.519 passed, 3 skipped, 7 deselected**, 1 Warnung |

Der ausgeschlossene LED-Controller-Test
`test_a_running_service_is_reported_rather_than_fought_with` enthält einen
unabhängigen Windows-Fehler: `_process_alive()` verwendet `os.kill(pid, 0)`;
Signal 0 entspricht dort `CTRL_C_EVENT` und unterbricht Pytest selbst. Die
übrige Nicht-Hardware-Suite endet mit Exitcode 0. Die fremde Änderung an
`led_controller_respeaker-v3\uv.lock` blieb unangetastet.

### Build

- Datei: `voice-stt-client\dist\voice-stt-client.exe`
- Version: 0.2.0
- Größe: 73.747.530 Byte
- SHA-256:
  `0b43f3da0ed61304087a32d952ce1c42011f42a717b22c7027ac3888f8f8b7ac`
- PyInstaller-Archiv enthält alle acht WAVs und `ATTRIBUTION.md`.

### Reale Systeme

- Alle acht Cues wurden über das echte Qt-Audiobackend geladen und abgespielt:
  jeweils `Ready`, `playing=True`, keine Fehler.
- Der Countdown wurde am echten ReSpeaker vollständig und mit vorzeitigem Clear
  geprüft: 141 Renderdurchläufe, Sink verfügbar, sauberer Worker-Shutdown.
- Der vollständige ReSpeaker-Mappingtest bestand zuvor alle 13 Ziele.
- Die nach allen Fixes neu gebaute EXE erreichte ReSpeaker, Live-STT-Server,
  Audio-Capture und Eventstream `LIVE` und wurde am Ende aktiv gelassen.

## 5. Wirksame lokale Konfiguration

Vor der gezielten Änderung wurde gesichert:

`C:\Users\marco\AppData\Local\RealtimeSTT Client\config.yaml.backup-debug-feedback-20260812-190600`

Die übrigen Benutzerwerte blieben erhalten. Wirksam sind derzeit Wake-Word-
Modus, Drei-Sekunden-Warnzeit, Tick-Asset, acht Soundpfade, Diagnosehelligkeit
und 32 Feedbackereignisse. Der konfigurierte aktuelle Laufzeitlog liegt unter:

`P:\DockerProjekte\RealtimeSTT_client\logs\client.log`

Der alte Clientprozess aus dem Docker-Projekt wurde beendet; die aktive Fassung
kommt aus dem kanonischen Projektroot. Es wurde kein Windows-Autostarteintrag
gefunden.

## 6. Bekannte Restbeobachtungen

- Im Live-Log schlug `RegisterHotKey` mit Windows-Fehler 1409 fehl, weil eine
  andere Anwendung dieselbe Kombination registriert hat. Der aktive Wake-Word-
  Modus ist davon nicht beeinträchtigt.
- Ein erster Live-Start offenbarte einen echten Auto-Start-Wettlauf. Der
  allgemeine Zustand `_dictation_requested` wurde gleichzeitig als
  One-Shot-Autostart-Signal benutzt; der Wake-Word-Maintainer konnte deshalb
  einen zweiten Start und fatal `start_in_progress` auslösen. Ein separates
  `_initial_auto_start_requested`-Flag behebt die Ursache. Die gezielte
  Reproduktion wechselte von 19/20 fatalen Läufen auf 0/20; zwei neue
  Regressionstests und die finale 451er-Suite sind grün. Der neu gebaute Client
  erreichte anschließend real `LIVE`.
- Die Komponenten des Countdownpfads sind real einzeln geprüft. Für die spätere
  Alltagsabstimmung sollte ein breiter gesprochener Lauf kontrollieren, ob der
  Lautsprecher-Tick trotz Echoausschaltung den VAD anregt.

## 7. Folgearbeit

Nach praktischer Beobachtung kann die bewusst übertriebene Diagnosematrix in
ein ruhigeres Alltagsprofil überführt werden. Getrennte spätere Pakete bleiben
die Untersuchung doppelter Texteinfügung, die größere Feedback-
Einstellungsseite und der geplante Hybridmodus-Umbau.

Der jederzeit übernahmefähige Detailstand befindet sich unter
`zusammenarbeit\arbeitsstaende\2026-08-12_led-sound-debugfeedback_uebergabestand.md`.
