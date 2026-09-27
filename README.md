# RealtimeSTT Windows Desktop Client

[![CI](https://github.com/marcosudau-vps/voice-stt-client/actions/workflows/ci.yml/badge.svg)](https://github.com/marcosudau-vps/voice-stt-client/actions/workflows/ci.yml)

Windows-Desktop-Client für den vorhandenen RealtimeSTT-Server. Der Client nimmt Mikrofon-Audio auf, überträgt es per WebSocket und verarbeitet Realtime- sowie Final-Transkripte.

Repository: <https://github.com/marcosudau-vps/voice-stt-client>  
Releases: <https://github.com/marcosudau-vps/voice-stt-client/releases>

## Aktueller Entwicklungsstand

Derzeit vorhanden:

- headless Mikrofon-/WebSocket-Core,
- Transkript-Historie im RAM und optional in SQLite,
- serialisierte Text-Injection-Queue für Clipboard + `SendInput`,
- UI-neutraler Dienst zum erneuten Einfügen früherer Finaltexte,
- integrierter Controller für Finalevent → Historie → Textinjektion,
- stille, zeitlich unbegrenzte Transport-Selbstheilung ohne Wiederaufnahme
  abgebrochener Diktate,
- PySide6-Tray mit Status, Diktatsteuerung, Reinsertion und Verlauf,
- passives Overlay für Realtime-, Final- und aktionsbezogenes Feedback,
- native globale Windows-Hotkeys,
- separate asyncio-Core-Loop und nativer Single-Instance-Guard,
- Hotkey- und Wake-Word-Betrieb über sessionlokale Serverkonfiguration,
- serverereignisgesteuertes Hotkey-Diktatfenster mit manueller Verlängerung,
- fünfteiliger Einstellungs- und Verlaufsdialog mit atomaren
  Benutzer-Overrides.

Noch nicht integriert:

- Mikrofon-/Hot-Plug-/Sleep-Wake-Heilung.
- Multi-Monitor-/DPI-Härtung, Autostart und weitergehendes Release-Polish.

AP6 ist einschließlich des konsolidierten Folgeumfangs implementiert. Die im
realen Abschlusstest gefundenen Clientfehler beim Laufzeitwechsel der
Betriebsmodi sind behoben, automatisiert regressionsgetestet und durch
wiederholte Wechsel gegen den produktiven Server verifiziert. Für die formale
Abnahme bleibt nur die erneute gesprochene Wake-Word-Prüfung. Für AP7 sind
M0–M9 abgenommen. Die transportneutralen Eventmodelle, die typisierte
Eventstream-Konfiguration, das YAML-Mapping für Server- und lokale
Clientereignisse, die Cursorpersistenz sowie der isolierte, reconnectende
`/ws/logs`-Transport mit strengem Protokollprocessor sind vorhanden. Der
generationgebundene `DualSessionCoordinator` übernimmt `hello.logAccess`,
invalidiert alte Logsessions bei STT-Reconnect und beendet beide Transporte
deterministisch. Normalisierung, reiner Feedback-Reducer, Replay ohne alte
Impulse und duplikatsicherer STT-Fallback sind in M7 integriert. M8 überträgt
die Reducerausgaben queued in den Qt-Main-Thread und steuert Tray, Overlay und
acht optionale, ausgelieferte und nichtsprachliche Sound-Cues ausschließlich
über das YAML-Mapping. Ein Tick-Cue und der LEFX-`countdown_ring` warnen in den
letzten drei Sekunden des Hotkey- wie Wake-Word-Follow-up-Fensters. M9
ergänzt den koaleszierenden, ausfallisolierten USB-LED-Adapter für den
ReSpeaker XVF3800 einschließlich Nulladapter und sicherem Shutdown. Die akute
M10-Debugfeedback-Korrektur ist automatisiert, im Onefile-Build sowie mit
echtem Sound und echtem ReSpeaker abgenommen; offen bleibt die breitere
gesprochene Bedien-/Disconnect-/Langlaufmatrix.

## Voraussetzungen

- Windows 10 oder 11
- Python 3.12
- funktionierendes Mikrofon

## Einrichtung

Für dieses Projekt werden alle Python-Befehle in der lokalen Projektumgebung ausgeführt:

```powershell
py -3.12 -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Wenn `venv` im Checkout bereits vorhanden und eingerichtet ist, entfällt das erneute Anlegen.

## Start

Regulärer GUI-Start:

```powershell
.\venv\Scripts\python.exe -m voice_stt_client
```

Mit einer ausdrücklichen Konfigurationsdatei:

```powershell
.\venv\Scripts\python.exe -m voice_stt_client --config C:\Pfad\client.yaml
```

Diagnosebetrieb mit Konsolenausgabe:

```powershell
.\venv\Scripts\python.exe -m voice_stt_client --headless
```

Die gebaute Windows-Anwendung benötigt keine lokale Python-Installation. Ein
reproduzierbarer Build entsteht mit:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe scripts\build.py --clean
```

Das Ergebnis liegt unter `dist/voice-stt-client.exe`. Normale Pushes und Pull
Requests führen dieselbe Test- und Buildstrecke in GitHub Actions aus.

Das offizielle 1.0.0-Release läuft ausschließlich in GitHub Actions:
Ein grüner `ci.yml`-Lauf auf `main` liefert die unveränderlichen Artefakte;
`release.yml` veröffentlicht danach PyPI, erstellt zuletzt den Git-Tag und
das GitHub Release. Der alte lokale Schreibpfad in `scripts/release.py` ist
gesperrt. Ablauf und Dry-Run stehen in `docs/RELEASE.md`.

Bedienung:

- `Ctrl+Shift+Space`: im Hotkeymodus Diktierung starten; während des Diktats
  das Zeitfenster verlängern. Im Wake-Word-Modus Betrieb aktivieren/pausieren.
- `Ctrl+Alt+Space`: letzten Finaltext erneut einfügen
- Tray-Menü: Status, Diktatsteuerung, Reinsertion, Verlauf, Einstellungen und
  Beenden

Trayfarben:

- dunkelgrün / hellgrün: Hotkeymodus wartet / nimmt auf,
- dunkelblau / hellblau: Wake-Word-Modus wartet / nimmt auf,
- weißer Rand: scharfgeschaltet und wartet auf erste beziehungsweise weitere
  Sprache,
- gelb: äußeres Netzwerk-, Server-, Audio- oder Mikrofonproblem,
- rot: tatsächlicher interner oder protokollarischer Fehler,
- grau: Wake Word pausiert, Shutdown oder beendet.

Finale Events werden über den Controller dedupliziert, vor jedem
Einfügeversuch in die Historie aufgenommen und an die
Text-Injection-Queue übergeben. Realtime-Zwischentext erscheint nur im
Overlay und wird nie automatisch eingefügt.

## Server

| Zweck | Adresse |
| --- | --- |
| WebSocket | `wss://stt.voice.marcosudau.com/ws/transcribe` |
| Health | `https://stt.voice.marcosudau.com/health` |
| Weboberfläche, kein Client-WebSocket | `https://voice.marcosudau.com` |

## Konfiguration

Die sichtbaren Laufzeitdefaults stehen in der mitgelieferten
`voice_stt_client/config.yaml`. Änderungen aus dem
Einstellungsdialog werden atomar unter
`%USERPROFILE%\.voice-stt\client\config.yaml` gespeichert. Eine vorhandene
Legacy-Datei unter `%LOCALAPPDATA%\RealtimeSTT Client\config.yaml` wird weiter
gelesen, solange die neue Datei noch nicht existiert.
Bei `--config` wird die angegebene Datei über die Paketdefaults gelegt und
Änderungen werden wieder dort gespeichert.
Details zu Pfaden,
Umgebungsvariablen und allen Feldern stehen in
[`docs/CONFIGURATION.md`](docs/CONFIGURATION.md). Zugangsdaten gehören nicht in
die Konfiguration oder das Repository.

Der Hotkeymodus fordert `wakeWordEnabled=false`; der Wake-Word-Modus fordert
`wakeWordEnabled=true` und verwendet standardmäßig die logische Modell-ID
`hey_jarvis`. Maßgeblich ist stets die effektive Konfiguration in
`hello.sessionConfig` und `ready.sessionConfig`. Ein abgelehntes Profil stoppt
weitere Verbindungsversuche bis zu einer echten Konfigurationsänderung.

## Weiterführende Dokumentation

- `docs/USER_GUIDE.md` – Installation, Bedienung, Verbindung, Logs und Fehlerhilfe
- `docs/CONFIGURATION.md` – vollständige Konfigurations-, Environment- und CLI-Referenz
- `docs/PROJEKTUEBERSICHT.md` – kompakter technischer Gesamtüberblick
- `docs/IMPLEMENTATION_ROADMAP.md` – verbindlicher Fahrplan
- `task.md` – aktueller Fortschritt
- `ÜBERGABE.md` – operativer Einstieg
- `docs/work-packages/AP06_UI_SHELL.md` – technischer UI-/Threadingvertrag und laufende AP6-Nachschärfung
- `docs/2026-07-25_AP06_ABNAHME/ABNAHMEBERICHT.md` – AP6-Test- und Smoke-Nachweis
- `docs/2026-07-26_AP06_SERVERVERTRAG_UND_OVERLAY_FIX/PRUEFBERICHT.md` – Overlay-Fix und Live-Prüfung des Sessionvertrags
- `docs/2026-07-28_AP06_FOLGEUMFANG_ABSCHLUSS/ABSCHLUSSBERICHT.md` – finale AP6-Umsetzung, Härtung und Nachweise
- `docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md` – Laufzeitfehleranalyse, Client-/Server-Abgrenzung und neues Farbkonzept
- `docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md` – robuster Lifecycle-Fix, Regression und produktiver Moduswechselnachweis
- `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md` – abgenommener AP5-Vertrag
- `docs/2026-07-25_AP05_ANTIGRAVITY/GESAMTABNAHME_UND_SELBSTFERTIGSTELLUNG.md` – unabhängiger AP5-Korrektur- und Testnachweis
- `server-docs-for-client-development/` – verbindlicher Serverprotokollvertrag
- `docs/RELEASE.md` – Windows-Build, PyPI-Paket und gemeinsamer Releaseablauf
- `docs/COMPATIBILITY.md` – geprüfte V1-Zuordnung und sicherer V2-Historienübergang
