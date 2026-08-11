# RealtimeSTT Windows-Client – kompakte Projektübersicht

> **Status:** aktive technische Orientierung  
> **Stand:** 9. August 2026  
> **Zuständig für:** kompaktes Zielbild, aktueller Paketstand und Einstieg in die Projektdokumentation  
> **Letzte Verifikation:** Client 396 Tests zweimal und 227 AP07-/Reconnect-
> Tests mit `-W error`; Server 379 Tests zweimal bei 13 Skips; sichere
> Live-Smokes, isolierte Serverkampagne und echter ReSpeaker-Pfad grün

## 1. Zweck und Einordnung

Diese Datei ist der kurze technische Einstieg für neue Bearbeiter. Sie übernimmt den gut lesbaren Aufbau der historischen Planungszusammenfassung, trennt aber ausdrücklich:

- **implementiert und automatisiert verifiziert (AP1–AP6),**
- **AP07-Servervorstufe und Vertrag (M0–M3) abgenommen,**
- **AP07-Clientgrundlagen, Eventtransport, Reducer/Fallback sowie Qt-, Sound-
  und ReSpeaker-Ausgabe M4–M9 abgenommen; M10-Fehlerkampagne in Arbeit,**
- **manuell oder im Live-Betrieb noch offen.**

Sie ist keine zweite Roadmap und keine zweite Übergabe. Bei Detailfragen gilt die Quellenhierarchie in `AGENTS.md` und `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`.

Die historische Datei

`docs/2026-07-24_PROJEKT_UEBERGABE/bisheriger_projekt_verlauf/import_ungeprueft/chatverlauf_008_bis_038_Zusammenfassung.md`

bleibt als ungeprüfter Planungsbeleg unverändert. Ihre alte Arbeitspaket-Nummerierung ist nicht mehr gültig.

---

## 2. Projektziel

Das Repository entwickelt einen dauerhaft im Hintergrund laufenden Windows-Desktop-Client für einen bereits vorhandenen RealtimeSTT-Server.

Der fertige Client soll:

1. Mikrofon-Audio per WebSocket übertragen,
2. Realtime-Text passiv anzeigen,
3. ausschließlich finale Transkripte vor jedem Einfügeversuch in den internen Verlauf aufnehmen,
4. finale Texte über Windows-Zwischenablage und `SendInput` in die aktuell fokussierte Anwendung einfügen,
5. frühere Finaltexte erneut einfügen können,
6. Tray, Overlay und globale Hotkeys über PySide6 und Win32 bereitstellen,
7. Verbindungs- und Gerätefehler möglichst selbstheilend behandeln.

### Serveradressen

| Zweck | Verbindliche Adresse |
| --- | --- |
| WebSocket-API | `wss://stt.voice.marcosudau.com/ws/transcribe` |
| Health-Endpoint | `https://stt.voice.marcosudau.com/health` |
| Weboberfläche, kein Client-WebSocket | `https://voice.marcosudau.com` |

Die Protokolldetails bestimmt ausschließlich `server-docs-for-client-development/`.

---

## 3. Verbindliche Architekturentscheidungen

| Bereich | Entscheidung |
| --- | --- |
| Sprache | Python 3.12 |
| UI | PySide6; Qt ausschließlich im Main Thread |
| Asynchroner Core | eine asyncio-Event-Loop in einem separaten Thread |
| Audio | `sounddevice`, mono, PCM16; bevorzugt 16 kHz |
| Globaler Hotkey | natives Win32 `RegisterHotKey` |
| Textinjektion | Clipboard und `SendInput`, serialisiert über eine Queue |
| Verlauf | In-Memory-Historie plus selektive SQLite-Persistenz |
| Realtime-Text | Anzeige im Overlay, niemals einfügen |
| Final-Text | vor dem Einfügeversuch an die Historie übergeben |
| Zielfenster | das unmittelbar vor `Ctrl+V` aktive Vordergrundfenster |
| Fokus | kein erzwungenes Zurückholen eines früheren Fensters |

Ausgeschlossen sind in der aktuellen Entwicklungsphase:

- `pystray`, `tkinter`, `pynput` und `qasync`,
- ein Admin-Service oder Admin-Helper,
- ein lokaler Fallback-STT-Server,
- Einfügung von Realtime-Zwischentexten.

### Implementiertes Threading-Modell

```text
Qt Main Thread
  ├─ Tray, Overlay, Einstellungen, Native Event Filter
  └─ Qt-Signale zur Darstellung

asyncio-Core-Thread
  ├─ Controller und Benutzerwunsch
  ├─ STTSession und WebSocket-Lifecycle
  └─ thread-sichere Befehlsannahme aus Qt

AudioCapture
  └─ sounddevice-/Verarbeitungsthread liefert PCM16-Pakete

TextInjectionQueue
  └─ eigener nicht-daemonisierter FIFO-Worker für Clipboard + SendInput
```

Der Core-Bereich ist mit AP4 und AP5 integriert
(`core/controller.py`, `core/stt_session.py`). AP6 setzt dieses Modell in
`ui/core_bridge.py` sowie der PySide6-Shell um.

---

## 4. Tatsächlicher aktueller Stand

### Implementiert & Integriert (AP1–AP6)

- `core/audio_capture.py`: Mikrofonaufnahme als Mono-PCM16, bevorzugt 16 kHz und 40-ms-Pakete.
- `core/stt_session.py`: Server-Handshake, Protokollzustand, Session-Generations, Ping-Miss-Erkennung, 1013-Delay, Backoff-Reset auf Pong.
- `core/history.py`: AP1 Transkript-Historie mit `add_entry_with_status`.
- `core/text_injector.py`: AP2 Text-Injection-Queue.
- `core/reinsertion.py`: AP3 erneutes Einfügen.
- `core/controller.py`: AP4 Controller-Integration & AP5 Zustands- und Selbstheilungsmodell (`AvailabilityState`, `DictationState`, `ControllerStatusSnapshot`, `TransientEvent`, start confirmation 10s timeout, disconnect dictation interruption).
- `ui/core_bridge.py`: thread-sichere Qt-/asyncio-Brücke mit eigenem
  Core-Thread und kontrolliertem Shutdown.
- `ui/hotkeys.py`: native globale Win32-Hotkeys mit atomarem
  Konflikt-Rollback.
- `ui/single_instance.py`: Win32-Mutex vor Core-, Hotkey- und Traystart.
- `ui/tray.py`, `ui/overlay.py`, `ui/presentation.py`: Status, Bedienung,
  Verlauf und passive Darstellung ohne Fokusübernahme; Hotkeystatus in
  Grün-, Wake-Word-Status in Blautönen, weißer Rand für Sprachwartephasen,
  Gelb für äußere Störungen und Rot für tatsächliche Fehler.
- `ui/application.py`: GUI-Komposition und Lifecycle.
- `core/settings_metadata.py`, `core/actions.py`: deklarative
  Einstellungsmetadaten und stabile Aktions-IDs ohne zweite Wertquelle.
- `ui/settings_dialog.py`: fünfteiliger Dialog für Verlauf, Allgemein,
  Verbindung/Betriebsmodus, Geräte/Audio und Erscheinungsbild/Feedback.
- `app.py`: regulärer GUI-Start; der bisherige Diagnosebetrieb bleibt über
  `--headless` erhalten.
- `VERSION`, `scripts/build.py` und `voice-stt-client.spec`: reproduzierbarer
  versionierter Windows-Onefile-Build.
- `.github/workflows/ci.yml` und `release.yml`: normale Commit-CI sowie
  taggesteuertes GitHub-Release nach erneutem Test-/Build-Gate.
- `scripts/release.py`: selbstständige Versionswahl, lokales Rollback bei
  Prüffehlern und exaktes CI-Warten vor dem Tag, ohne zweites Sync-Repository.

### AP07: Servervorstufe und Clientintegration M0–M9 abgenommen

- zweite sessiongebundene Verbindung zu `/ws/logs`,
- abgenommener SQLite-first-Serververtrag als Grundlage,
- implementierte transportneutrale Event-/Kontrollmodelle,
- typisierte Eventstream-Konfiguration und atomare Cursorpersistenz,
- strikt validiertes YAML-Mapping von `server.*`- und lokalen
  `client.*`-Ereignissen auf LED-, Sound- und In-App-Wirkungen,
- isolierter `/ws/logs`-Transport mit Reconnect, Replay und Ping/Pong,
- strikter Protokollprocessor mit expliziter Cursorbestätigung, begrenzter
  Deduplizierung sowie typisierten Gap-, Cursor-, Store- und Authfehlern,
- generationgebundener `DualSessionCoordinator` mit gemeinsamem
  `SessionContext`, Tokenablauf, stale-event-sicherem Sessionwechsel und
  deterministischem Shutdown beider Transporte,
- zentrale Normalisierung und genau eine serverseitige Feedbackquelle,
- reiner Reducer, impulsfreies Replay und duplikatsicherer STT-Fallback,
- integrierte Qt-/Tray-/Overlay-/Soundausgabe aus dem YAML-Mapping,
- ReSpeaker-XVF3800-LED über koaleszierenden, ausfallisolierten USB-Adapter,
- noch offene End-to-End-Fehlerkampagne,
- vollständige Dual-WebSocket- und Fehlerabnahme.

Die bisherige allgemeine Härtung, Multi-Monitor/DPI, Autostart und das
weitergehende Release-Polish folgen getrennt als AP8. Die dafür notwendige
öffentliche Repository-, CI-, PyInstaller- und Releasebasis ist bereits vorhanden.

Der manuelle Abschlusstest hat zwei Clientfehler im Laufzeitwechsel der
Betriebsmodi nachgewiesen. Beide sind behoben und durch wiederholte lokale
sowie produktive Wechsel abgesichert. Offen bleibt nur die erneute gesprochene
Wake-Word-Prüfung mit echtem Mikrofon.

### Wichtige Grenzen des aktuellen Stands

- Die Aufnahme liefert bereits `int16`; es existiert kein `core/audio_processor.py` und kein lokaler Resampler.
- Die WebSocket-Komponente heißt `core/stt_session.py`; ein `core/stt_client.py` existiert nicht.
- Fällt die bevorzugte Samplerate aus, kann `AudioCapture` mit der Geräte-Samplerate arbeiten; eine lokale Umrechnung auf 16 kHz ist nicht implementiert.
- Der zunächst fehlgeschlagene Audio-End-to-End-Lauf führte zur Korrektur der
  Thread-Brücke. Ein anschließender regulärer Lauf belegte Mikrofon,
  Audioübertragung, Realtime-Ausgabe und Finaltext vollständig.

---

## 5. Aktuelle Arbeitspakete

Die folgende Nummerierung ersetzt die alte Planungsnummerierung der importierten Chat-Zusammenfassung.

### AP1 – Transkript-Historie `[ABGESCHLOSSEN]`

**Zweck:** Finaltexte und zugehörige Einfügeversuche thread-sicher verwalten.

**Implementiert:**

- `TranscriptHistoryManager`
- Datenobjekte `HistoryEntry`, `InjectionAttempt` und `InjectionStatus`
- Deduplizierung über `(session_id, segment_id)`
- maximal fünf Einträge im RAM gemäß aktuellem Default
- optionale SQLite-Persistenz unter dem lokalen Anwendungsdatenverzeichnis
- selektive Speicherung nach Länge, Fehlversuch oder `store_all`
- append-only Einfügeversuche
- defensive tiefe Kopien bei Lesezugriffen

**Aktuelle Defaults:**

- RAM: 5 Einträge
- SQLite: maximal 100 Einträge
- Mindestlänge: 1.000 Zeichen
- fehlgeschlagene Einfügungen speichern: ja
- alle Einträge speichern: nein
- Altersgrenze: keine

**Wichtige Grenze:** „Vor Paste in der Historie“ bedeutet derzeit zunächst Schutz im laufenden Prozess. Kurze, noch nicht fehlgeschlagene Texte werden standardmäßig nicht sofort crash-sicher in SQLite gespeichert.

**Verifikation:** 30 Unittests.

### AP2 – Text-Injection-Queue `[ABGESCHLOSSEN]`

**Zweck:** Paste-Aufträge thread-sicher, seriell und ohne Fokusmanipulation ausführen.

**Implementiert:**

- `TextInjectionQueue`
- Lifecycle `NEW → INITIALIZING → RUNNING → STOPPING → STOPPED`
- ein nicht-daemonisierter FIFO-Worker
- Clipboard-Schreiben und `Ctrl+V` per Win32/ctypes
- Message-only Owner-Window für Clipboard-Zugriffe
- Vordergrundfenster-Erfassung unmittelbar vor dem Paste
- optionale Clipboard-Sicherung und sequenzgeschützte Wiederherstellung
- genau ein finaler `InjectionAttempt` pro angenommenem Queue-Job
- Ablehnung neuer Jobs außerhalb von `RUNNING`

**Aktueller Default:** Clipboard-Restore ist deaktiviert.

**Manuell verifiziert am 25. Juli 2026:** realer Notepad-Smoke-Test erfolgreich. `command_sent`, Text erschien im fokussierten Notepad und der vorherige Clipboard-Inhalt wurde wiederhergestellt.

**Verifikation:** 41 Unittests mit Win32-Test-Doubles.

### AP3 – Erneutes Einfügen `[ABGESCHLOSSEN]`

**Zweck:** den letzten oder einen ausgewählten bestehenden Verlaufseintrag erneut an dieselbe Injection-Queue übergeben.

**Implementiert:**

- `TranscriptReinsertionService`
- `reinsert_last()`
- `reinsert_entry(entry_id)`
- `get_recent_entries(limit)`
- Memory-first-Auflösung mit SQLite-Fallback
- unveränderliche Resultate mit den Statuswerten `queued`, `empty_history`, `entry_not_found`, `queue_unavailable` und `failed`
- keine Erzeugung eines neuen `HistoryEntry` bei Reinsertion
- zusätzliche Attempts bleiben am ursprünglichen Eintrag

**Noch offen:** Hotkey, Tray-Menü und grafische Verlaufsauswahl.

**Verifikation:** 26 Unittests.

### AP4 – Controller-Integration `[ABGESCHLOSSEN]`

**Zweck:** AP1, AP2 und AP3 zu einem kontrollierten, UI-neutralen Laufzeitpfad verbinden.

Der verifizierte Zielpfad lautet:

```text
finales Server-Event
  → reale Feldvalidierung (sessionId, segmentId, text)
  → atomare Identitätsreservierung unter Controllerlock
  → Historie/Deduplizierung via add_entry_with_status
  → nur ein neu angelegter Finaltext wird automatisch enqueuet
  → serialisierter Paste-Versuch
  → Attempt am selben HistoryEntry dokumentieren
```

Realtime-Events lösen diesen Pfad nicht aus.

**Implementiert und unabhängig verifiziert:**
- `core/controller.py` (`STTController`, `ControllerStatus`, `CommandResult`, `FinalProcessingResult`)
- `app.py` Headless-Einstiegspunkt erweitert `STTController` mit DI-Oberfläche
- Primary-Driver Run-Loop (`session.run()` steuert Dauer; Auto-Start Ende beendet run() nicht)
- konkurrierende, Cancellation-geschützte Shutdown-Idempotenz (Stop-Zähler exakt 1)
- Shutdown gegen parallele Start-/Stop-/Toggle-Übergänge serialisiert
- exception-sicherer partieller Task-Start und Queue-Start-Rollback
- Logisch-atomare Finalidentitäts-Reservierung unter Lock vor History-Aufruf
- atomare Closing-Nachprüfung unmittelbar bei der Finalreservierung
- Evicted History-Randfall als `DEDUPLICATED` (`duplicate_entry_evicted`)
- Asynchrone ehrliche Diktierbefehle (`async start_dictation`, `stop_dictation`, `toggle_dictation`)

**Verifikation:** 46 Unittests in `tests/test_controller.py`, 9 in
`tests/test_app.py` (insgesamt 152 Tests in der Suite).

### AP5 – Fehlerverhalten und Selbstheilung `[ABGESCHLOSSEN]`

**Zweck:** Stille Selbstheilung des WebSocket-Transports ohne automatische Wiederaufnahme abgebrochener Diktate.

**Implementiert und unabhängig verifiziert:**
- Endgültiger Abbruch laufender Diktate bei Sessionverlust (`DICTATION_INTERRUPTED`); kein Resume & kein Audio-Replay.
- Generations-Tracking (`ClientState.generation`, `STTSession._generation`) verwirft alte Audio-Frames & Server-Events.
- Benutzerstart bei nicht bereitem Transport wird sofort abgelehnt (`ACTION_BLOCKED`), Diktatzustand bleibt `IDLE`.
- Serverbestätigter Start mit 10.0s Timeout (`start_confirmation_timeout`); WS-Close bei Timeout für sauberen Reconnect.
- Stiller Reconnect mit max 30.0s gedeckeltem Backoff einschließlich
  konfiguriertem Jitteranteil 0,3, 10.0s Min-Delay bei CloseCode 1013
  (`server_busy`) und sofort abbrechbarem Backoff-Sleep (`stop()`).
- Backoff-Reset ausschließlich beim ersten gültigen `pong` einer Session (`_first_pong_received`).
- Ping-Miss-Erkennung ohne RTT-Kaschierung mit max 1 ausstehendem Ping (`_ping_pending`).
- Persistente UI-neutrale Zustände (`AvailabilityState`, `DictationState`, `ControllerStatusSnapshot`) und sparsame Events (`TransientEvent`).
- Startbestätigung ausschließlich für den aktuellen Startversuch, die aktuelle
  Session-ID und Generation; alte Statusmeldungen können keinen Start
  bestätigen.
- Disconnect während `STARTING`, Timeout, Stop und Shutdown gewinnen
  deterministisch gegen verspätete Bestätigungen. Timeout beendet nur den
  aktuellen Socket, nicht den Reconnect-Loop.
- Admission-, Engine-/Recorder-, Command- und wiederholte Audiofehler werden
  getrennt klassifiziert; UI-Callbacks dürfen den Core nicht abbrechen.
- Sessionbezogene Finalidentitäten werden bereinigt und bleiben auch bei
  Langzeitbetrieb begrenzt.

**Verifikation:** 10 Tests in `tests/test_config.py`, 18 in
`tests/test_stt_session.py`, 62 in `tests/test_controller.py`, 10 in
`tests/test_app.py`; insgesamt 197 Tests. Zusätzlich wurde die echte
`STTSession` ohne Audio gegen den produktiven Server bis zum gültigen Pong und
sauberen Stop geprüft. Details:
`docs/2026-07-25_AP05_ANTIGRAVITY/GESAMTABNAHME_UND_SELBSTFERTIGSTELLUNG.md`.

### AP6 – UI-Shell, Betriebsmodi und Einstellungen `[FIX VERIFIZIERT – WAKE-WORD-BEDIENNACHWEIS OFFEN]`

Implementiert sind:

- PySide6-`QApplication` im Main Thread,
- Tray-Icon und Menü mit Status, Diktat-Toggle, Reinsertion, dynamischem
  Verlauf und Beenden,
- passives, nicht fokussierbares und maustransparentes Overlay,
- thread-sichere Qt-Signal- und Befehlsbrücke zum separaten asyncio-Core,
- native globale Hotkeys `Ctrl+Shift+Space` und `Ctrl+Alt+Space`,
- nativer Single-Instance-Guard,
- kontrollierte Start-, Konflikt- und Shutdown-Pfade,
- regulärer GUI-Start und erhaltener `--headless`-Diagnosepfad,
- Hotkey- und Wake-Word-Modus über den effektiven Sessionvertrag,
- konfigurierbares, server-VAD-gesteuertes Hotkey-Diktatfenster,
- fünfteiliger Einstellungsdialog und deklarative Metadaten über `AppConfig`,
- stabile Aktionshotkeys und atomare per-user Overrides,
- statische Mikrofonwahl/-test, Verlaufspflege sowie optionales Feedback.

**Verifikation:** insgesamt 264 automatische Tests.
Nativer Windows-Ressourcen-Smoke sowie vollständiger AP06-Live-Smoke mit
echtem Tray, Mutex, Hotkeys, separatem Core-Thread und Serverzustand `READY`
waren erfolgreich. Am 28. Juli bestätigte ein zusätzlicher sicherer
Produktions-Smoke `effectiveWakeWordEnabled=false` und `true` in `hello` und
`ready`; im Wake-Word-Modus wird die logische ID `hey_jarvis` verwendet.

ReSpeaker-LED und das Feedback-/Eventsystem sind nun verbindlich AP7.
Allgemeine Geräteheilung, Sleep/Wake, DPI, Autostart und weitergehendes
Packaging-/Release-Polish bleiben AP8.
Details zum bisherigen AP6-Abschluss:
`docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md`.

### AP7 – Feedback- und Eventsystem `[M0–M9 ABGENOMMEN – M10 IN ARBEIT]`

Bereits abgeschlossen sind Serverbaseline, SQLite-first-Umstellung,
Protokoll-/Deploymentabnahme und die Synchronisierung des produktiven
Serververtrags. M4 hat die Clientmodelle, die typisierte Eventstream-
Konfiguration, das YAML-Feedback-Mapping für Server- und lokale Clientevents
sowie den atomaren Cursorstore ergänzt. M5 implementiert und testet den
isolierten Eventtransport und den strikten Protokollprocessor. M6 koordiniert
beide WebSockets über eine gemeinsame aktuelle Generation und Session,
invalidiert alte Tokens und Events bei STT-Reconnect und isoliert Fehler des
Eventtransports vom Diktatpfad. M7 ergänzt die strikte Normalisierung der
strukturierten Serverevents und lokalen Clienttatsachen, einen reinen,
deterministischen Reducer, impulsfreies Replay, begrenzte Deduplizierung und
den kontrollierten STT-Fallback mit atomarer Rückkehr zum Eventstream. M8
bindet diese Reducerausgaben queued
an Qt, Tray und Overlay an, ersetzt alte befehlsbasierte Sounds durch sieben
konfigurierbare YAML-Cues und führt Soundadapterfehler als kanonische lokale
Tatsache zurück. M9 ergänzt den ReSpeaker-XVF3800-USB-Adapter mit begrenztem
Worker, Impulsrückkehr, Fehlerdrosselung, Nulladapter und sicherem `off` beim
Shutdown. M10 hat die wiederholten Gesamtsuiten, Warnungsprüfung, sichere
Live-Smokes, den echten ReSpeaker-Pfad und die isolierte lokale Store-,
Retention-, WebSocket- und Prozessneustartkampagne bestanden. Gesprochene
Bedien-, STT-Disconnect-, stille Final- und Langlaufprüfungen bleiben offen. Für
die weitere Clientintegration gelten
weiterhin:

- SQLite-first-Servereventstrom als verpflichtende Vorstufe,
- `/ws/logs` als primäre serverseitige Feedbackquelle,
- gemeinsamer SessionCoordinator für `/ws/transcribe` und `/ws/logs`,
- Replay ohne alte Impulse und kontrollierter Fallback ohne Doppelwirkung,
- normalisierte lokale und serverseitige Ereignisse,
- Qt-, Sound- und ReSpeaker-LED-Integration,
- vollständige automatische und reale Fehler-/Reconnectabnahme.

Detailvertrag und Reihenfolge:

- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md`
- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md`

### AP8 – Härtung und Polish `[OFFEN]`

Danach folgen allgemeine Geräteheilung, Sleep/Wake, Multi-Monitor/DPI,
Autostart, weitergehendes Packaging-/Release-Polish sowie Langzeit- und
Bedienprüfungen. Repository-Hygiene, Commit-CI und ein geprüfter
PyInstaller-/GitHub-Releasepfad sind als vorgezogene Basis bereits umgesetzt.

---

## 6. Verifizierter Teststand

Zuletzt am 9. August 2026 wurde die Clientgesamtsuite ausgeführt:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -v
```

Aktuelles Ergebnis nach dem Indikatorfarbkonzept:

```text
Ran 396 tests
OK
```

Der `compileall`-Lauf über sämtliche
Python-Laufzeit- und Testmodule hatte Exit-Code 0.

Aufteilung:

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
- M10-Edge-/Prozess-/Buildhärtung: 18

Diese 396 Tests prüfen zusätzlich zu AP1–AP5:

- native Hotkeyregistrierung, Konflikt-Rollback und Dispatch,
- Single-Instance-Lifecycle,
- alle definierten Statusabbildungen, Tray, Overlay und Verlauf,
- Main-/Core-Thread-Grenzen, Befehlsübergabe und Shutdown,
- GUI-Komposition, Fehlerpfade und `--headless`-Kompatibilität.
- Session-URL, effektive Modusbestätigung und Konfigurationsfehler,
- Diktatfenster, stale Timer und Hotkeyverlängerung,
- Metadaten, Kandidatenvalidierung, atomare Overrides und fünf Dialogtabs,
- Verlaufslöschung mit erhaltener Deduplizierungssemantik.
- modusgebundene Grün-/Blauphasen, weißen Tray-Rand und die
  Gelb-/Rot-Trennung zwischen äußeren Störungen und tatsächlichen Fehlern.
- generationgebundene Übernahme von `hello.logAccess`, STT-/Event-Reconnect-
  Rennen, Tokenablauf, stale In-Flight-Events sowie exakt einmaligen
  Dual-Transport-Shutdown.

Zusätzlich am 25. Juli 2026 manuell verifiziert:

- Health, WebSocket-`hello`, `ready` und `pong`: erfolgreich,
- reale Injection in Notepad einschließlich Clipboard-Restore: erfolgreich,
- Mikrofon, `AudioCapture` und Paketformat: erfolgreich,
- vollständiger Wake-Word-/Realtime-/Finaltext-Pfad mit temporär korrigierter `call_soon_threadsafe`-Brücke: erfolgreich; 733 von 733 Paketen ohne volle Clientqueue gesendet,
- dieselbe Thread-Brücke anschließend dauerhaft in `app.py` implementiert und mit Regressionstests abgesichert,
- regulärer Wiederholungslauf mit serverweit deaktiviertem Wake Word: direkte Realtime-Ausgaben und Finaltext erfolgreich.
- echter Smoke-Test der aktuell gehärteten `STTSession`: `hello`, `ready`,
  anwendungsseitiger Ping, als aktuell validierter Pong erkannte Antwort und
  sauberer Stop erfolgreich; dabei wurde kein Audio gesendet.
- nativer AP6-Windows-Smoke: Mutex schließt eine zweite Instanz aus,
  beide Hotkeys registrieren, echte `WM_HOTKEY`-Nachrichten werden korrekt
  zugeordnet und alle Ressourcen werden freigegeben.
- vollständiger AP6-Live-Smoke: echtes System-Tray verfügbar, Mutex und beide
  Hotkeys aktiv, separater Core-Thread erreicht über die Produktionsbrücke
  `READY` am produktiven Server und beendet sich sauber; Diktat, Audioaufnahme
  und Textinjektion wurden dabei bewusst nicht gestartet.

---

## 7. Integrationsentscheidungen und getrennte Restpunkte

| ID | Klärung |
| --- | --- |
| E-01 | **Für AP4 festgelegt:** stabiler HistoryEntry vor Enqueue; selektive SQLite-Regel bleibt, keine neue Outbox. |
| E-02 | **Für AP4 festgelegt:** normaler Finalpfad muss neu, Duplikat und History-Ausfall unterscheiden; ohne History kein automatischer Paste. Persistente Lesefehler außerhalb dieses Pfads bleiben dokumentiert best-effort. |
| E-03 | **Für AP4 festgelegt:** autoritative Quelle ist das rohe `final`-Event; Deduplizierung über `(sessionId, segmentId)`, kein automatischer Retry durch Eventduplikate. |
| E-04 | **Abgeschlossen in AP6:** semantische Controllerbefehle bleiben die Core-Grenze; die UI bindet nativ `Ctrl+Shift+Space` an Toggle und `Ctrl+Alt+Space` an Reinsertion. |
| E-05 | **Entschieden:** Audio-Thread-Brücke vor AP4 korrigiert. AP5 repariert Ping-Miss und Transportheilung; ein unterbrochenes Diktat wird ausdrücklich nicht wiederaufgenommen. |
| E-06 | Wann werden Testdatenbanken, Cache-/Ignore-Regeln und der absolute Logging-Pfad bereinigt? |
| E-07 | **Abgeschlossen in AP6:** enger Session-Create-Contract für Hotkey-/Wake-Word-Modus ist integriert und für beide Modi live verifiziert. |

E-01 bis E-05 und E-07 sind abgeschlossen. E-05 wurde für AP5 in ADR-002
präzisiert. E-06 bleibt ein getrennter Hygiene-Restpunkt für AP8.

---

## 8. Bekannte technische Risiken

- Die frühere Fremdthread-Übergabe an `asyncio.Queue` erzeugte bestätigte Audiobursts mit 175–199 wartenden 40-ms-Paketen. Sie ist behoben: `app.py` bindet seine Event-Loop und plant Queue-Einträge über `call_soon_threadsafe`; Pakete außerhalb einer aktiven Streaminggrenze werden verworfen. Acht Regressionstests sichern einschließlich des Generationswechsels diese Brücke ab.
- Ein realer Lauf derselben korrigierten Brückenlogik übertrug 700 von 700 Paketen ohne Rückstau; ein weiterer Lauf mit „Hey Jarvis“ bestätigte mit 733 von 733 Paketen den vollständigen Pfad bis zum Finaltext.
- Der frühere breite Sessionprofilentwurf bleibt verworfen. Der Server bietet
  inzwischen stattdessen einen engen sessionlokalen Wake-Word-Contract über
  WebSocket-Queryparameter an.
- `hello.sessionConfig` und `ready.sessionConfig` bestätigen Modus,
  Wake-Word-ID, Fallbacks und Warnungen. Die Produktionsschnittstelle wurde am
  26. Juli 2026 für Hotkey- und Wake-Word-Sessions, Isolation und Fehlerpfade
  live geprüft.
- Der Client erzeugt die Queryparameter selbst und akzeptiert einen Modus erst
  nach übereinstimmender Bestätigung in `hello` und `ready`.
- Im Wake-Word-Modus muss der Client nach `start` auch in `wakeword_wait`
  kontinuierlich Audio senden.
- Ping/Pong, Startbestätigung und Transportverlust sind für AP5 automatisiert
  gehärtet. Ein echter Netzabbruch während eines realen Mikrofon-Diktats wurde
  in dieser Abnahme nicht absichtlich erzeugt; das Verhalten ist durch
  deterministische Race-Tests abgesichert.
- Mikrofonverlust, Hot-Plug, Gerätewechsel und Windows-Sleep/Wake sind bewusst
  nicht Bestandteil von AP5 und bleiben AP8.
- `get_persistent_entries()` kann einen SQLite-Fehler als leere Liste abbilden.
- `add_entry()` unterscheidet im Rückgabewert nicht eindeutig zwischen „neu angelegt“ und „bereits vorhanden“.
- Die nativen Hotkeys sind implementiert, grafisch konfigurierbar und
  automatisch sowie mit echten Win32-Ressourcen verifiziert.

---

## 9. Dokumentenlandkarte

| Dokument | Aufgabe |
| --- | --- |
| `AGENTS.md` | dauerhafte Projekt- und Agentenregeln |
| `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` | verbindliche Pflege- und Arbeitsregeln |
| `docs/PROJEKTUEBERSICHT.md` | dieser kompakte technische Einstieg |
| `docs/IMPLEMENTATION_ROADMAP.md` | führender Gesamtfahrplan und Zielarchitektur |
| `task.md` | aktueller Paket-, Restpunkt- und Teststatus |
| `ÜBERGABE.md` | operativer Einstieg in den zuletzt verifizierten Stand |
| `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md` | abgenommener AP4-Paketvertrag und Integrationsnachweis |
| `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md` | ausgeführter operativer AP4-Auftrag mit Test-, Abgabe- und Reviewvertrag |
| `docs/decisions/ADR-002_STILLE_SELBSTHEILUNG_UND_DIKTATABBRUCH.md` | verbindliche Produktentscheidung zu Reconnect, Diktatabbruch und Feedback |
| `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG.md` | verbindlicher fachlich-technischer AP5-Paketvertrag |
| `docs/work-packages/AP05_FEHLERVERHALTEN_UND_SELBSTHEILUNG_AUSFUEHRUNGSAUFTRAG.md` | freigegebener operativer AP5-Implementierungs- und Testauftrag |
| `docs/2026-07-25_AP05_ANTIGRAVITY/GESAMTABNAHME_UND_SELBSTFERTIGSTELLUNG.md` | unabhängiger Befund, Korrekturen und Testnachweise der AP5-Abnahme |
| `docs/work-packages/AP06_UI_SHELL.md` | abgeschlossener konsolidierter AP6-Paketvertrag |
| `docs/work-packages/AP06_UI_SHELL_AUSFUEHRUNGSAUFTRAG.md` | ausgeführter technischer AP6-Erstauftrag |
| `docs/2026-07-25_AP06_ABNAHME/ABNAHMEBERICHT.md` | Nachweis des technischen AP6-Erststands |
| `docs/2026-07-26_AP06_SERVERVERTRAG_UND_OVERLAY_FIX/PRUEFBERICHT.md` | Overlay-Korrektur sowie Live-Prüfung des neuen Sessionvertrags |
| `docs/2026-07-28_AP06_FOLGEUMFANG_ABSCHLUSS/ABSCHLUSSBERICHT.md` | finale Umsetzung, Härtung und AP6-Abnahme |
| `docs/2026-07-28_AP06_ABSCHLUSSTEST_FEHLERANALYSE/FEHLERANALYSE_UND_INDIKATORFARBEN.md` | fehlgeschlagener Moduswechsel-Smoke, Client-/Server-Abgrenzung und Indikatorfarbkonzept |
| `docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md` | persistenter Maintainer, atomare Aktivierung, Rollback und produktiver Fixnachweis |
| `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md` | verbindlicher AP07-Architektur- und Paketvertrag |
| `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md` | verbindliche Meilensteinfolge von Servervorstufe bis Gesamtabnahme |
| `docs/evaluations/2026-07-25_SERVER_EVALUIERUNG_SESSIONLOKALER_WAKE_WORD_OVERRIDE.md` | historische Evaluierung; durch den implementierten Serververtrag überholt |
| `server-docs-for-client-development/` | verbindlicher Serverprotokollvertrag |
| `README.md` | benutzerorientierter Einstieg; kein Architekturvertrag |
| datierte Ordner und Archive | historische Belege, keine aktive Wahrheit |

### Empfohlene Lesereihenfolge für das nächste Arbeitspaket

1. `AGENTS.md`
2. `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`
3. diese Projektübersicht
4. `docs/IMPLEMENTATION_ROADMAP.md`
5. `ÜBERGABE.md`
6. `task.md`
7. `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md`,
8. `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md`,
9. nur die darin für den freigegebenen Meilenstein benannten
   Serverabschnitte, Module und Tests.

Die genaue, kontextschonende Pflichtlektüre bestimmt `AGENTS.md`. Es werden
weder sämtliche Serverkapitel noch der gesamte Core oder alle Tests pauschal
eingelesen.

---

## 10. Kurzstatus

> Der Audio-/WebSocket-Core sowie AP1–AP6 sind implementiert. Der reguläre
> Start führt in die PySide6-Shell mit Tray, passivem Overlay, nativen Hotkeys,
> Reinsertion und Single-Instance-Guard; `--headless` bleibt als Diagnosepfad.
> Der aktuelle Stand umfasst 396 zweimal grüne automatische Tests, `compileall`, einen
> nativen Windows-Smoke und einen vollständigen AP06-Live-Smoke gegen den
> produktiven Server einschließlich beider effektiver Sessionverträge. Der
> anschließende reale Bedien-Smoke deckte zwei Clientfehler im
> Laufzeit-Moduswechsel auf. Beide sind inzwischen korrigiert und durch zwei
> weitere produktive Wechselzyklen verifiziert. Offen bleibt der gesprochene
> Wake-Word-Nachweis. Für AP7 sind M0–M9 einschließlich produktivem
> SQLite-first-Live-/Replay-Nachweis sowie Clientmodellen, YAML-Mapping und
> Cursorstore, isoliertem Eventtransport und Dual-Session-Lifecycle
> abgeschlossen. M10 ist mit grüner Automatisierung und sicheren Live-Smokes
> in Arbeit; M11 bleibt bis zum Abschluss der realen Matrix gesperrt.
> Die öffentliche GitHub-, Commit-CI-, PyInstaller- und Releasebasis ist mit
> einem lokal gestarteten, versionierten Windows-Build bereits vorbereitet.
