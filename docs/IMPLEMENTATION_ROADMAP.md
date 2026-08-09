# IMPLEMENTATION_ROADMAP – RealtimeSTT Windows Desktop Client

> **Status:** verbindlicher Gesamtfahrplan  
> **Stand:** 9. August 2026  
> **Aktives Paket:** AP7 Feedback- und Eventsystem; M0–M3 abgenommen  
> **Nächster Meilenstein:** M4 / AP07-C1 – Clientmodelle, Konfiguration und Cursorstore  
> **Separater Restpunkt:** erneuter gesprochener AP6-Wake-Word-Nachweis  
> **Infrastruktur:** öffentliches GitHub-Repository, Windows-CI, PyInstaller-Build und Release-Gate eingerichtet

## Architekturübersicht

Der Client verbindet sich dauerhaft mit:

`wss://stt.voice.marcosudau.com/ws/transcribe`

AP07 ergänzt nach einer verpflichtenden SQLite-first-Härtung des Servers eine
zweite, sessiongebundene Verbindung zu `/ws/logs`. `/ws/transcribe` bleibt für
Audio, Befehle, Realtime- und Finaltext autoritativ. `/ws/logs` wird im
Normalbetrieb die einzige serverseitige Quelle für persistierte fachliche
Feedback- und Lebenszyklusereignisse. Beide Verbindungen werden durch einen
gemeinsamen generationgebundenen SessionCoordinator geführt.

Das Zielsystem trennt:

1. **Qt Main Thread:** Tray, Overlay, Einstellungen und native Windows-Events.
2. **asyncio-Core-Thread:** Controller, WebSocket-Session und asynchrone Befehle.
3. **AudioCapture-Threads:** sounddevice-Aufnahme und PCM16-Paketübergabe.
4. **Injection-Worker:** serialisierte Clipboard-/`SendInput`-Aufträge.
5. **Thread-sichere Dienste:** Transkript-Historie und Reinsertion.

Realtime-Text wird nur dargestellt. Ein Finaltext wird vor dem automatischen Paste-Versuch als HistoryEntry aufgelöst und anschließend über die Injection-Queue verarbeitet.

Der tatsächliche Iststand ist kompakt in `docs/PROJEKTUEBERSICHT.md` beschrieben. Code und erfolgreich ausführbare Tests bleiben für die reale Implementierung maßgeblich.

### Wake-Word-Scope und direkter Betrieb

Der Client besitzt einen sessionlokalen Betriebsmodusselector. Der breite
Entwurf mit benannten Serverprofilen bleibt verworfen.

Der Server stellt inzwischen einen deutlich engeren, versionierten
Session-Create-Contract bereit. Beim WebSocket-Aufbau kann der Client
`wakeWordEnabled=false|true` sowie logische Wake-Word-IDs und optionale
Tuningwerte anfordern. Die effektive Sessionkonfiguration wird in
`hello.sessionConfig` und `ready.sessionConfig` bestätigt, ohne die globale
Serverbaseline oder andere Sessions zu verändern.

Der neue Vertrag ist im Client integriert und auf dem produktiven Server für
beide Betriebsmodi live verifiziert.

Die AP06-Scopekonsolidierung vom 27. Juli ist umgesetzt:

- Hotkeymodus fordert `wakeWordEnabled=false`,
- Wake-Word-Modus fordert `wakeWordEnabled=true`,
- Modus und Wake-Profil werden lokal eingestellt und durch einen
  kontrollierten Reconnect aktiviert,
- ausschließlich die effektive Handshakekonfiguration gilt,
- `session_config`/1008 erzeugt keine blinde Reconnectschleife,
- ein aktives Diktat wird bei Moduswechsel beendet und nicht fortgesetzt.

Der Einstellungsdialog und eine deklarative Metadatenebene über der typisierten
`AppConfig` gehören ebenfalls in AP06. Benutzereinstellungen werden als
per-user Overrides gespeichert; die versionierte `config.yaml` bleibt
sichtbarer Projektdefault.

`docs/decisions/ADR-001_BETRIEBSMODI_HOTKEY_UND_WAKE_WORD.md` bleibt ein
zurückgezogener Entwurf. Die maßgebliche Protokollquelle ist
`server-docs-for-client-development/`.

---

## Arbeitspaket 1: Transkript-Historie `[ABGESCHLOSSEN]`

Ziel ist die thread-sichere Verwaltung finaler Transkripte und ihrer Einfügeversuche im RAM sowie optional in SQLite.

### Implementiert

- `TranscriptHistoryManager` ohne eigenen Worker und ohne PySide6-Abhängigkeit.
- Deduplizierung über `(session_id, segment_id)`.
- In-Memory-Historie mit defensiven Kopien.
- selektive SQLite-Persistenz und append-only Attempts.
- Fallback auf In-Memory-Betrieb bei mehreren SQLite-Fehlern.

### Abnahme

- 30 Unittests in `tests/test_history.py`.
- Integration in den Laufzeitpfad ist ausdrücklich Bestandteil von AP4, nicht AP1.

---

## Arbeitspaket 2: Text-Injection-Queue `[ABGESCHLOSSEN]`

Ziel ist eine eigenständige, thread-sichere und serialisierte Queue für Clipboard-/`SendInput`-Aufträge.

### Implementiert

- Lifecycle `NEW → INITIALIZING → RUNNING → STOPPING → STOPPED`.
- ein nicht-daemonisierter FIFO-Worker.
- Win32 Clipboard und `SendInput` über ctypes.
- Message-only Clipboard-Owner-Window.
- Vordergrundfenster-Erfassung direkt vor dem Paste.
- optionale, sequenzgeschützte Clipboard-Wiederherstellung.
- genau ein finaler Attempt pro angenommenem Queue-Job.

### Abnahme

- 41 Unittests in `tests/test_text_injector.py`.
- Manueller Notepad-Smoke-Test am 25. Juli 2026 erfolgreich: tatsächliche Einfügung und Clipboard-Restore bestätigt.
- Integration von Finalevents ist Bestandteil von AP4.

---

## Arbeitspaket 3: Erneutes Einfügen `[ABGESCHLOSSEN]`

Ziel ist eine UI-neutrale Kernfunktion für das erneute Einfügen des letzten oder eines ausgewählten bestehenden HistoryEntry.

### Implementiert

- `TranscriptReinsertionService`.
- Memory-first-Auflösung mit SQLite-Fallback.
- `reinsert_last()`, `reinsert_entry()` und `get_recent_entries()`.
- Resultatstatus für Erfolg, leere Historie, unbekannte ID, nicht verfügbare Queue und Fehler.
- keine neuen HistoryEntries bei Reinsertion.
- zusätzliche Attempts am ursprünglichen Eintrag.

### Abnahme

- 26 Unittests in `tests/test_reinsertion.py`.
- Hotkey, Tray und Verlaufsauswahl sind in AP6 umgesetzt.
- Controller-Lifecycle in AP4 umgesetzt.

---

## Arbeitspaket 4: Controller-Integration `[ABGESCHLOSSEN]`

Ziel ist ein gemeinsamer, UI-neutraler Lifecycle für STTSession, AudioCapture, History, Injection-Queue und Reinsertion-Service.

### Implementiert und unabhängig verifiziert

- `core/controller.py`: `STTController` verbindet AP1 (History), AP2 (TextInjectionQueue) und AP3 (Reinsertion) UI-neutral.
- `app.py`: Headless-Orchestrierung `RealtimeSTTClient` erweitert `STTController` mit vollständiger Dependency-Injection-Oberfläche.
- Deterministischer, exception-sicherer Lifecycle (`start_queue()`, `run()`, `shutdown()`).
- Primary-Driver Run-Loop (`session.run()` steuert Dauer; Auto-Start Ende führt nicht zum Abbruch).
- Echte konkurrierende Shutdown-Idempotenz mit `asyncio.shield()` Schutz.
- Shutdown ist gegen parallele Aufnahmeübergänge serialisiert; ein abgebrochener
  Shutdown-Waiter cancelt die gemeinsame Cleanup-Task nicht.
- Teilweise Task-Erzeugung und fehlgeschlagener Queue-Start werden ohne
  Task-Leaks oder doppelten Queue-Stop zurückgerollt.
- Logisch-atomare Finalidentitäts-Reservierung unter Lock vor dem History-Aufruf.
- Closing wird atomar mit der Finalidentitäts-Reservierung erneut geprüft.
- Evicted History-Randfall als `DEDUPLICATED` (`duplicate_entry_evicted`) behandelt.
- Asynchrone ehrliche Diktierbefehle (`async start_dictation()`, `stop_dictation()`, `toggle_dictation()`) serialisiert via `_transition_lock` (`asyncio.Lock`) mit Audio-Rollback bei Fehler.

### Abnahme

- 46 Unittests in `tests/test_controller.py`.
- 9 Unittests in `tests/test_app.py`.
- 152 automatische Gesamttests in der Suite erfolgreich (`py_compile` Exit-Code 0).

---

## Arbeitspaket 5: Fehlerverhalten und Selbstheilung `[ABGESCHLOSSEN]`

Ziel ist eine stille, zeitlich unbegrenzte Wiederherstellung des Transports bei
Betriebsstörungen, ohne einen alten Aufnahmeauftrag über eine Sessiongrenze zu
tragen.

### Implementiert

- Ein durch Transportverlust unterbrochenes Diktat wird sofort und dauerhaft beendet (`DICTATION_INTERRUPTED`); kein Resume und kein Audio-Replay nach Reconnect.
- Verworfene Audio-Frames alter Sessions durch Session-Generations-Tracking (`ClientState.generation`, `STTSession._generation`).
- Ein Benutzerstart bei nicht bereitem Transport wird sofort abgelehnt (`ACTION_BLOCKED`), der Zustand bleibt `IDLE` und es wird nichts vorgemerkt.
- `start_dictation()` fordert Serverbestätigung an und wartet bis zu 10.0s (`start_confirmation_timeout`); bei Timeout wird das Diktat abgelehnt (`DICTATION_START_FAILED`) und die WebSocket-Verbindung für sauberen Reconnect geschlossen.
- Stiller Reconnect mit max 30.0s gedeckeltem exponentiellem Backoff einschließlich konfiguriertem Jitteranteil 0,3, 10.0s Mindestverzögerung bei CloseCode 1013 (`server_busy`) und abbrechbarem Sleep (`stop()`).
- Backoff-Reset erfolgt ausschließlich beim ersten gültigen `pong` einer Session (`_first_pong_received`).
- Ping-Miss-Erkennung ohne RTT-Kaschierung mit max 1 ausstehendem Ping (`_ping_pending`) und Schließen des Transports bei Überschreiten von `ping_timeout_count`.
- Persistente UI-neutrale Zustände (`AvailabilityState`, `DictationState`, `ControllerStatusSnapshot`) und sparsame Feedback-Events (`TransientEvent`, `on_snapshot_change`, `on_feedback_event`).
- Erstmaliger Headless-Autostart läuft höchstens einmal beim Initialstart und wird nach Reconnect niemals erneut ausgelöst.
- Startbestätigungen sind an Startversuch, Session-ID und Generation gebunden; ein alter `LISTENING`-Status oder ein Disconnect während `STARTING` kann keinen neuen beziehungsweise abgebrochenen Start aktivieren.
- Timeout und Ping-Ausfall invalidieren ausschließlich die aktuelle Verbindung. Der zeitlich unbegrenzte Reconnect-Loop bleibt aktiv.
- Serverfehler werden nach Admission, Engine/Recorder, Command und Audio-Packet unterschieden und in UI-neutrale Verfügbarkeits- und Feedbackzustände übersetzt.
- Finalevent-Identitäten und sessionbezogene Zustände bleiben über Langzeitbetrieb begrenzt beziehungsweise werden beim Sessionwechsel bereinigt.

### Abnahme

- 10 Unittests in `tests/test_config.py`.
- 18 Unittests in `tests/test_stt_session.py`.
- 62 Unittests in `tests/test_controller.py`.
- 10 Unittests in `tests/test_app.py`.
- 197 automatische Gesamttests in der Suite erfolgreich; zusätzlicher Lauf mit
  `RuntimeWarning` und `ResourceWarning` als Fehler für die 51 unmittelbar
  relevanten Tests ebenfalls erfolgreich (`py_compile` Exit-Code 0).
- Live-Smoke-Test der echten `STTSession` gegen den produktiven Server:
  `hello → ready → gültiger pong → sauberer stop`, ohne Audioübertragung.
- Unabhängiger Korrektur- und Abnahmenachweis:
  `docs/2026-07-25_AP05_ANTIGRAVITY/GESAMTABNAHME_UND_SELBSTFERTIGSTELLUNG.md`.

---

## Arbeitspaket 6: UI-Shell, Betriebsmodi und Einstellungen `[FIX VERIFIZIERT – WAKE-WORD-BEDIENNACHWEIS OFFEN]`

Ziel ist die Windows-Bedienoberfläche auf Basis des stabilen Core-Controllers.

Implementiert:

- PySide6-`QApplication` im Main Thread.
- `QSystemTrayIcon` mit Status, Diktatsteuerung, Reinsertion, Verlauf und
  Beenden.
- passives, nicht fokussierbares und maustransparentes Overlay.
- Qt-Signalbrücke vom Core zur UI und thread-sichere Befehlsbrücke von Qt zum
  asyncio-Core.
- eigener nicht-daemonisierter Core-Thread mit eigener asyncio-Event-Loop und
  genau einem `STTController`.
- native globale Hotkeys über Win32 `RegisterHotKey`:
  `Ctrl+Shift+Space` für Diktat-Toggle und `Ctrl+Alt+Space` für Reinsertion.
- nativer Win32-Single-Instance-Guard vor dem Start weiterer Komponenten.
- Reinsertion über Hotkey, Tray und ID-gebundene Verlaufsauswahl.
- regulärer GUI-Start sowie erhaltener Diagnosepfad `app.py --headless`.
- kontrollierte Fehlerpfade bei Hotkeykonflikt, fehlendem Tray,
  Core-Startfehler und Shutdown.
- typisierte Sessionkonfiguration mit sicherer URL-Erzeugung, effektiver
  Handshakeprüfung und blockierter Reconnectschleife bei `session_config`.
- Hotkey- und Wake-Word-Modus mit kontrolliertem Reconnect.
- generationgebundenes Diktatfenster über `recording_started` /
  `recording_ended`, Initial- und Follow-up-Timer sowie Hotkeyverlängerung.
- deklarative Metadaten, stabile Aktions-IDs und fünfteiliger
  Einstellungsdialog.
- atomare per-user Persistenz, Kandidatenvalidierung und Laufzeit-Rollback.
- statische Mikrofonwahl/-test, Verlaufslöschung und optionales Soundfeedback.
- modusgebundener Tray-Indikator: dunkel-/hellgrün für Hotkey,
  dunkel-/hellblau für Wake Word, weißer Rand für das Sprachwartefenster,
  Gelb ausschließlich für äußere Störungen und Rot für tatsächliche Fehler.

Abschlussstand:

- Vor-AP6-Baseline: 197 Tests.
- Nach der ersten AP6-Umsetzung: 238 Tests erfolgreich.
- Nach Behebung der fehlerhaften Textsignal-Adaption: 239 Tests erfolgreich.
- Nach Umsetzung und Härtung des Folgeumfangs: 257 Tests erfolgreich.
- Nach Indikatorfarbkonzept: 261 Tests erfolgreich und `compileall` grün.
- Nach robustem Moduswechsel-Fix: 264 Tests erfolgreich, `compileall` grün
  und zwei produktive Hotkey↔Wake-Word-Wechselzyklen erfolgreich.
- `py_compile`, nativer Windows-Ressourcen-Smoke und echter vollständiger
  AP06-Live-Smoke mit Qt-Tray, Mutex, Hotkeys, separatem Core-Thread und
  Serverzustand `READY` erfolgreich.
- Paketvertrag:
  `docs/work-packages/AP06_UI_SHELL.md`.
- finaler Abnahmenachweis:
  `docs/2026-07-28_AP06_FOLGEUMFANG_ABSCHLUSS/ABSCHLUSSBERICHT.md`.

Der reale Abschlusstest bestätigte die Bedienprüfungen 1 bis 4 und deckte in
Prüfung 5 zwei Clientfehler auf:

- Nach einem Laufzeitwechsel Hotkey → Wake Word wird der notwendige
  Wake-Word-Maintainer nicht erzeugt.
- Beim Rückwechsel Wake Word → Hotkey wird sein reguläres Ende als fataler
  Helperfehler bewertet und beendet den Core.

Beide Clientfehler sind behoben: Der Maintainer ist nun ein permanenter
Core-Task, Moduswechsel lassen ihn ruhen statt enden, und ein Wechsel nach
Wake Word wird erst nach bestätigter Streamaktivierung erfolgreich gemeldet.
Der frühere Ablauf wurde lokal dreifach, mit absichtlichem Aktivierungsfehler
und Reconnect sowie produktiv in zwei vollständigen Wechselzyklen geprüft.

Die gesprochene Erkennung von `hey_jarvis` bleibt ein kurzer manueller
Hardware-/Server-Bediennachweis. Details:
`docs/2026-07-28_AP06_MODUSWECHSEL_FIX/ABSCHLUSSBERICHT.md`.

Der Server unterstützt beim WebSocket-Aufbau sessionlokal mindestens:

- `wakeWordEnabled=false` für Hotkeybetrieb,
- `wakeWordEnabled=true` für dauerhaften Wake-Word-Betrieb,
- logische Wake-Word-Modell-IDs und optionale Tuningwerte,
- eine effektive Bestätigung in `hello.sessionConfig` und
  `ready.sessionConfig`,
- sichtbare Fallbacks/Warnungen und harte Konfigurationsfehler mit Close 1008.

Diese Schnittstelle ist live verifiziert und in Clientkonfiguration und UI
integriert. Der umgesetzte Folgeumfang umfasst:

- automatisch aus Einstellungsmetadaten aufgebaute Standardfelder,
- getrennte Aktions- und Hotkeyregistrierung,
- fünf Dialogtabs für Verlauf, Allgemein, Verbindung/Betriebsmodus,
  Geräte/Audio sowie Erscheinungsbild/Feedback,
- ein clientseitiges Hotkey-Diktatfenster über den serverseitigen
  VAD-Segmenten,
- 15 Sekunden Initial-Sprach-Timeout,
- konfigurierbares Follow-up-Fenster und standardmäßig 15 Sekunden
  Hotkeyverlängerung,
- optionale Soundeffekte und einen kleinen Overlay-/Statusindikator.

ReSpeaker-LED und das neue Feedback-/Eventsystem sind AP07. Allgemeine
Geräteheilung, Sleep/Wake, Multi-Monitor/DPI, Autostart, weitergehendes
Packaging-/Release-Polish und Langzeit-/Stresstests bleiben AP08. Die
öffentliche Repository-, Commit-CI-, PyInstaller- und Releasebasis wurde als
Voraussetzung für alle weiteren Pakete bereits vorgezogen.
Details und Abnahmekriterien des abgeschlossenen AP06-Folgeumfangs stehen in
`docs/work-packages/AP06_UI_SHELL.md`.

---

## Arbeitspaket 7: Feedback- und Eventsystem `[M0–M3 ABGENOMMEN – M4 OFFEN]`

Ziel ist ein zuverlässiger serverseitiger Feedbackstrom über `/ws/logs`, der
unter einem gemeinsamen SessionCoordinator neben dem bestehenden Audio- und
Textpfad läuft und Qt, Sound sowie ReSpeaker-LED aus einem zentralen
Feedback-Reducer versorgt.

Stand 9. August 2026: Die Servervorstufe, der produktive SQLite-first-
Protokollnachweis und die Synchronisierung des Serververtrags sind als M0–M3
abgeschlossen. Der Servercommit `dedcdd93e836b2a9df4771da8514a09645c7674f`
liegt lokal und auf `origin/main`. Die Clientintegration wurde noch nicht
begonnen; ihr nächster zulässiger Schnitt ist M4.

Verbindliche Eckpunkte:

- Server vor Clientintegration auf SQLite-first härten: Commit vor
  Liveauslieferung, Replay und Live aus derselben Storequelle.
- Jede begonnene Transkription erhält einen terminalen Zustand, einschließlich
  `transcription.discarded(reason=empty_final)`.
- Produktivvertrag anschließend vollständig nach
  `server-docs-for-client-development/` synchronisieren.
- `/ws/transcribe` bleibt autoritativ für Audio, Befehle, Realtime- und
  Finaltext.
- `/ws/logs` ist im Zustand `LIVE` die einzige serverseitige Feedbackquelle.
- Replay rekonstruiert Dauerzustände und löst keine vergangenen Impulse aus.
- Bei nachgewiesener Eventstromdegradation greift ein begrenzter,
  duplikatsicherer `/ws/transcribe`-Fallback.
- Lokale Clienttatsachen bleiben lokal und werden erst im Feedback-Reducer
  zusammengeführt.
- ReSpeaker-LED und Sound sind ausfallisolierte Ausgabeadapter.
- Bestehender AP1–AP6-Core, Threading- und Textinjektionsvertrag bleiben
  geschützt.

Maßgebliche Detailverträge:

- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_GESAMTPLANUNG.md`
- `docs/work-packages/AP07_FEEDBACK_EVENTSYSTEM_IMPLEMENTIERUNGSPLAN.md`

Die Umsetzung ist in Servervorstufe, Vertragsynchronisierung, Clientmodelle,
Eventtransport, Dual-Session-Lifecycle, Reducer/Fallback, UI/Sound, LED,
End-to-End-Härtung und Gesamtabnahme gegliedert. Der jeweils nächste
Meilenstein beginnt nur nach Abnahme seines Vorgängers.

---

## Arbeitspaket 8: Härtung und Polish `[OFFEN]`

Ziel ist der anschließende belastbare Abschluss für den dauerhaften
Windows-Betrieb außerhalb des AP07-Scopes.

Die technische Basis für Repository-Hygiene, Windows-PyInstaller-Build,
Commit-CI und taggesteuerte GitHub-Releases wurde am 9. August 2026 vorgezogen,
damit alle folgenden Pakete sofort durch diese Gates laufen. Für AP08 bleiben:

- allgemeine Reconnect- und Langzeit-Stresstests über die AP07-Abnahme hinaus,
- Mikrofonverlust, Hot-Plug, Gerätewechsel und Wiederanlauf,
- Windows-Sleep/Wake und tatsächliche Gerätewiederherstellung,
- Multi-Monitor- und DPI-Verhalten,
- Autostart und weitergehendes Packaging-/Release-Polish,
- fortlaufende Repository- und Laufzeitdatei-Hygiene,
- abschließende End-to-End- und Bedienprüfungen,
- abschließender Release- und Dokumentationsabgleich.
