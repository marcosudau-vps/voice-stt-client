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
M0–M3 abgenommen; der nächste Implementierungsschritt ist M4.

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
.\venv\Scripts\python.exe app.py
```

Diagnosebetrieb mit Konsolenausgabe:

```powershell
.\venv\Scripts\python.exe app.py --headless
```

Die gebaute Windows-Anwendung benötigt keine lokale Python-Installation. Ein
reproduzierbarer Build entsteht mit:

```powershell
.\venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\venv\Scripts\python.exe scripts\build.py --clean
```

Das Ergebnis liegt unter `dist/voice-stt-client.exe`. Normale Pushes und Pull
Requests führen dieselbe Test- und Buildstrecke in GitHub Actions aus.

Ein offizielles Release einschließlich automatischer Versionswahl, doppeltem
Test-/Build-Gate und GitHub-Release-Artefakt wird mit folgendem Befehl erstellt:

```powershell
.\venv\Scripts\python.exe scripts\release.py
```

Details und Dry-Run stehen unter `docs/RELEASE.md`.

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
|---|---|
| WebSocket | `wss://stt.voice.marcosudau.com/ws/transcribe` |
| Health | `https://stt.voice.marcosudau.com/health` |
| Weboberfläche, kein Client-WebSocket | `https://voice.marcosudau.com` |

## Konfiguration

Die sichtbaren Laufzeitdefaults stehen in `config.yaml`. Änderungen aus dem
Einstellungsdialog werden atomar unter
`%LOCALAPPDATA%\RealtimeSTT Client\config.yaml` gespeichert. Zugangsdaten in
`.env` dürfen weder dokumentiert noch committed werden.

Der Hotkeymodus fordert `wakeWordEnabled=false`; der Wake-Word-Modus fordert
`wakeWordEnabled=true` und verwendet standardmäßig die logische Modell-ID
`hey_jarvis`. Maßgeblich ist stets die effektive Konfiguration in
`hello.sessionConfig` und `ready.sessionConfig`. Ein abgelehntes Profil stoppt
weitere Verbindungsversuche bis zu einer echten Konfigurationsänderung.

## Weiterführende Dokumentation

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
- `docs/RELEASE.md` – Windows-Build, Commit-CI und vollautomatisches GitHub-Release
