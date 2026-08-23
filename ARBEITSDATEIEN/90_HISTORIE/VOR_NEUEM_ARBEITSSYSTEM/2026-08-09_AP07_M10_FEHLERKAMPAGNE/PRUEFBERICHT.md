# AP07-M10 – Prüfbericht End-to-End-Härtung und Fehlerkampagne

> **Status:** historischer Prüfbeleg; M10 weiterhin in Arbeit
> **Stand:** 9. August 2026
> **Projekt:** `P:\DockerProjekte\voice-stt-client`
> **Server:** `P:\DockerProjekte\voice-stt-server`

## Ergebnis

Die vollständigen automatisierten Server- und Clientprüfungen, die fokussierte
AP07-Warnungsprüfung, die isolierte lokale Serverkampagne und die sicheren
Live-/Hardware-Smokes sind erfolgreich. Die verbleibenden M10-Punkte benötigen
gesprochenes Mikrofon-Audio und sichtbare Bedienbeobachtung beziehungsweise
einen längeren Realbetrieb. Eingriffe in den produktiven Server sind nicht
mehr erforderlich. M10 ist bis zu diesen Bediennachweisen noch nicht
abgeschlossen.

## Automatisierte Nachweise

### Server

- vollständige Suite zweimal stabil: jeweils **379 bestanden, 13 übersprungen,
  78 Subtests**;
- `compileall` über Server, Anwendungen, Tests und Werkzeuge: erfolgreich;
- `git diff --check`: erfolgreich;
- der erste Lauf scheiterte ausschließlich an einer bereits vorhandenen,
  globalen und nicht zugreifbaren pytest-Tempstruktur. Beide Wertungsläufe
  wurden deshalb mit je einem neuen repositorylokalen `--basetemp` ausgeführt.

Die Suite enthält insbesondere einen echten Neustart über zwei getrennte
Windows-Prozesse mit gemeinsamem temporären SQLite-Store, rotierender
`serverInstanceId` und fortlaufenden Cursorn. Zusätzlich belegt sie
SQLite-first-Commit-vor-Publish,
Storeausfall/Recovery, Replayfortsetzung nach Disconnect, mehrseitiges Replay
mit 1005 Ereignissen, Retentionlücke, sessiongebundene Isolation, leeres Final
mit genau einem `transcription.discarded` und Weiterbetrieb der Transkription
bei degradiertem Eventstore.

### Client

- vollständige Suite nach allen Härtungen zweimal stabil: jeweils **396 Tests
  bestanden**;
- fokussierte AP07-/Reconnect-Suite mit `-W error`: **227 Tests bestanden**;
- `compileall` über `app.py`, `core/`, `ui/`, `scripts/` und `tests`:
  erfolgreich;
- `git diff --check`: erfolgreich.

Abgedeckt sind unter anderem Disconnect während Replay, Cursorfortsetzung,
Shutdown in Replay/Connect/Backoff, Session- und Generationswechsel,
Retentionanzeige, atomarer Fallback/Recovery, Unterdrückung alter
Replayimpulse, Deduplizierung nach mehr als 10.000 Ereignissen, parallele
Reducerzugriffe, leeres Final/Discard, Cursor-Schreibfehler mit Replay ohne
Doppelimpuls, Tokenablauf vor und während einer Session, Backoff nach 100.000
Fehlern ohne Zahlenüberlauf sowie Prozessstart-, Pipe-, Timeout- und
Shutdownfehler des isolierten LED-Adapters.

Der PyInstaller-Onefile-Build ist ebenfalls grün: Version `0.1.0`, 74.758.009
Bytes, SHA-256
`1e6b2b54ed010149bd233d3c77071a096df769de9bac3dfbc41d06d234bd5d5a`.
`--version` beendet mit Exitcode 0; Multiprocessing-Runtime-Hook, `usb.core`,
`libusb_package` und `libusb-1.0.dll` sind in der Analyse enthalten.

## Nicht destruktive Live-Smokes

1. Beide Sessionverträge: `hotkey=False`, `wake_word=True` – bestanden.
2. Zwei Laufzeitwechselzyklen Hotkey → Wake Word → Hotkey über Generationen
   1 bis 5, ohne Mikrofon oder Textinjektion – bestanden.
3. Neuer AP07-Smoke über echten Server: STT-Handshake, sessiongebundenes
   Logtoken, `/ws/logs`, Replay, LIVE und sauberer gemeinsamer Shutdown –
   bestanden.
4. Reale Adapterklassen mit absichtlich nicht vorhandenem USB-Gerät und
   defektem Soundpfad: Fehler isoliert, jeweils einmal gemeldet, sauberer
   Shutdown – bestanden.
5. Physisch angeschlossener ReSpeaker XVF3800: `idle_hotkey`,
   `waiting_for_speech`, `recording`, `finalizing`, `success_pulse`, danach
   bestätigtes `off` und sauberer Prozessabschluss – bestanden.

Reproduzierbare Befehle:

```powershell
$env:PYTHONUTF8='1'
.\venv\Scripts\python.exe -m tests.manual_test_ap06_modes
.\venv\Scripts\python.exe -m tests.manual_test_ap06_runtime_mode_switch
.\venv\Scripts\python.exe -m tests.manual_test_ap07_event_stream

$env:QT_QPA_PLATFORM='offscreen'
.\venv\Scripts\python.exe -m tests.manual_test_ap07_adapter_failures
.\venv\Scripts\python.exe -m tests.manual_test_ap07_led_hardware
```

Die Python-3.12-WMI-Blockade dieses Hosts trat auch beim verzögerten
`libusb-package`-Backendaufbau und in isolierten PyInstaller-Prozessen auf.
Der LED-Zugriff bleibt deshalb in einem abbrechbaren Hilfsprozess; Build und
Onefile-Start erhalten eine frühe, Windows-spezifische Plattforminitialisierung.

## M10-Ablaufmatrix

| Nr. | Szenario | Stand am 9. August 2026 |
|---:| --- | --- |
| 1 | Hotkey bis Final, Historie und Paste | Komponenten und frühere AP06-Bedienprüfung grün; erneuter AP07-Gesamtlauf mit sichtbarem Feedback offen |
| 2 | Wake Word bis Follow-up | Komponenten grün; gesprochener Wake-Word-/AP07-Gesamtlauf offen |
| 3 | Eventstreamdisconnect in Idle/Aufnahme/Finalisierung | automatisiert und in der isolierten lokalen WebSocket-Kampagne grün; sichtbare Beobachtung während gesprochenem Ablauf noch offen |
| 4 | Reconnect, Replay, genau ein Impuls | automatisiert einschließlich Cursor-Schreibfehler und atomarem Replay/LIVE-Wechsel grün; sichtbare Beobachtung noch offen |
| 5 | Storedegradation, Fallback, Recovery | isolierte lokale Server- und Client-Fault-Injection vollständig grün; kein Produktiveingriff erforderlich |
| 6 | STT-Disconnect ohne Audioreplay | automatisiert grün; realer Disconnect während Diktat offen |
| 7 | Hotkey/Wake Word mit neuem Logzugang | zwei echte Moduswechselzyklen und Tokenbindung grün |
| 8 | langer Lauf, hohe Realtime-Aktivität | Grenztests mit >10.000 Events und 1005er Replay grün; realer Langlauf/Latenzmessung offen |
| 9 | Serverneustart, persistenter Store, neue Instanz-ID | über zwei echte Betriebssystemprozesse mit gemeinsamem temporären SQLite-Store grün |
| 10 | Retentionlücke | Server- und Clientanzeige in isolierter Store-/WebSocket-Kampagne grün |
| 11 | leeres Final mit `discarded` | Server und Client automatisiert grün; reale stille Aufnahme offen |
| 12 | kein ReSpeaker und defektes Soundasset | automatisiert und mit realen Adapterklassen grün; zusätzlich echter ReSpeaker-Effektpfad bis `off` grün |
| 13 | Shutdown während Replay/Backoff | automatisiert grün; echter Eventstream-LIVE-Shutdown zusätzlich grün |

## Sicherheits- und Ressourcenprüfung

- keine `.env`, Datenbank- oder Log-Laufzeitdatei ist versioniert;
- Logzugangstoken werden weder in URLs noch in Ausgaben der Smokes
  veröffentlicht;
- die neuen Smokes geben keine Session-ID, Tokens oder Transkriptinhalte aus;
- keine hängenden Eventstream-, LED-, PyInstaller- oder Onefile-Prozesse nach
  den Prüfungen;
- die absichtlich erzeugten Adapterfehler bleiben lokal und nicht fatal.

## Noch erforderliche Entscheidung oder Mitwirkung

Für den Abschluss von M10 fehlen der sichtbare Hotkey-Gesamtlauf, der
gesprochene Wake-Word-/Follow-up-Lauf, ein realer STT-Verlust während eines
Diktats, ein stilles Final und eine längere Latenz-/Ressourcenbeobachtung. Die
Store-, Retention- und Neustartfälle sind in einer separaten lokalen Instanz
erledigt; der produktive Server muss dafür nicht verändert werden. Bis zum
Bediennachweis bleibt M11 gesperrt.
