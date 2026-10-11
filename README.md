# RealtimeSTT Windows Desktop Client

[![CI](https://github.com/marcosudau-vps/voice-stt-client/actions/workflows/ci.yml/badge.svg)](https://github.com/marcosudau-vps/voice-stt-client/actions/workflows/ci.yml)

Windows-Desktop-Client für den vorhandenen RealtimeSTT-Server. Der Client nimmt Mikrofon-Audio auf, überträgt es per WebSocket und verarbeitet Realtime- sowie Final-Transkripte.

Repository: <https://github.com/marcosudau-vps/voice-stt-client>  
Releases: <https://github.com/marcosudau-vps/voice-stt-client/releases>

## Aktueller Entwicklungsstand

Aktiver Einstieg ist [Client V2](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/PLANUNG/README.md).
AP-CV2-000 hat die Feature-/Releasebasis in `voice_stt_client` technisch qualifiziert (REVIEW_READY nach R03-Korrektur).
Der Paketkandidat ist noch nicht unabhängig abgenommen oder auf `feat/client-v2`
übernommen. Der bestehende Transport ist weiterhin V1; die Migration auf den
gepinnten V2-Serververtrag erfolgt in den Folgepaketen. Aktuelle Startbefehle,
Benutzerpfade und Grenzen: [Kompatibilität](docs/compatibility.md).

Die folgende Bestandsbeschreibung ist historische Produktorientierung.

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

Das Ergebnis liegt unter `dist/voice-stt-client.exe`. Pushes auf main/feat/client-v2 und Pull
Requests führen dieselbe Test- und Buildstrecke in GitHub Actions aus.

Offizielle Veröffentlichungen erfolgen ausschließlich im separat freigegebenen
Releaseworkflow aus geprüften Main-CI-Artefakten. Der frühere lokale
Tag-first-Publishpfad ist deaktiviert. Dieser V2-Paketbranch wird nicht
veröffentlicht; `VERSION` übernimmt den vorhandenen Wert 1.0.0, die konkrete
Kandidatenidentität bestimmen Branch und Commit. Siehe
[Kompatibilität und Migration](docs/compatibility.md).

Bedienung:

- `Ctrl+Shift+Space`: bei aktivem Manualtrigger Diktierung starten; während des
  Diktats das Zeitfenster verlängern. Ist nur der Wake-Word-Trigger aktiv,
  aktiviert beziehungsweise pausiert die Taste den Betrieb. Ohne aktiven
  Manualtrigger registriert der Client den Hotkey gar nicht erst.
- `Ctrl+Alt+Space`: letzten Finaltext erneut einfügen
- Tray-Menü: Status, Diktatsteuerung, Reinsertion, Verlauf, Einstellungen und
  Beenden

Trayfarben:

- dunkelgrün / hellgrün: Manualtrigger wartet / nimmt auf,
- dunkelblau / hellblau: Wake-Word-Trigger wartet / nimmt auf,
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

Die sichtbaren Laufzeitdefaults stehen in `config.yaml`. Änderungen aus dem
Einstellungsdialog werden atomar unter
`%LOCALAPPDATA%\RealtimeSTT Client\config.yaml` gespeichert. Zugangsdaten in
`.env` dürfen weder dokumentiert noch committed werden.

Die Session wird über zwei unabhängige Triggerschalter aufgebaut:
`manualTriggerEnabled` und `wakeWordTriggerEnabled`. Mindestens einer muss aktiv
sein; `false/false` lehnt der Server ab. Ist der Wake-Word-Trigger aktiv, fordert
der Client zusätzlich `wakeWordEnabled=true` und verwendet standardmäßig die
logische Modell-ID `hey_jarvis`.

Alte Konfigurationen werden migriert: `mode: hotkey` ergibt `manual=true /
wake_word=false`, `mode: wake_word` ergibt `manual=false / wake_word=true`. Eine
stillschweigende Migration auf `true/true` findet nicht statt.

Maßgeblich ist stets die effektive Konfiguration in `hello.activationConfig`,
`hello.sessionConfig` und `ready.*`. Ein abgelehntes Profil stoppt weitere
Verbindungsversuche bis zu einer echten Konfigurationsänderung.

## Weiterführende Dokumentation

- `docs/PROJEKTUEBERSICHT.md` – kompakter technischer Gesamtüberblick
- `PLANUNG/` des aktiven Arbeitsblocks unter `ARBEITSDATEIEN/10_AKTUELL/` – verbindlicher Fahrplan (Einstieg über `ARBEITSDATEIEN/00_STEUERUNG/CURRENT_STATE.md`; ersetzt das frühere `docs/IMPLEMENTATION_ROADMAP.md`)
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

R03 korrigiert die Hotkey-Persistierung bei fehlgeschlagenem Corestart; [aktueller Korrekturreport](ARBEITSDATEIEN/10_AKTUELL/CLIENT_V2/30_AUSFUEHRUNG/AP-CV2-000/RUNS/R03-KORREKTUR/01_REPORT.md). Unabhängige Abnahme weiterhin offen.
