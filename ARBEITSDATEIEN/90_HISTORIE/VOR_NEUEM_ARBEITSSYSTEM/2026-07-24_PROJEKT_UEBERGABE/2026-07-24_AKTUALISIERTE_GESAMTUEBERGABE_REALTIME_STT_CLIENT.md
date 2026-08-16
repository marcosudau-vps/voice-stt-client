# Aktualisierte Gesamtübergabe – RealtimeSTT Windows Desktop Client

> **Stand:** 24. Juli 2026  
> **Projektpfad:** `P:\DockerProjekte\RealtimeSTT_client`  
> **Letzte Verifikation:** 24. Juli 2026  
> **Nächster regulärer Funktionsschritt:** Arbeitspaket 4 – Controller-Integration  
> **Wichtig:** Vor einer AP4-Implementierung sind die in Abschnitt 15 genannten Entscheidungen ausdrücklich festzulegen.

## 1. Zweck und Geltungsbereich

Dieses Dokument ist die konsolidierte operative Übergabe für den nächsten Weiterbearbeitungs-Agenten. Es führt zusammen:

- den tatsächlich vorhandenen Code,
- den aktuell reproduzierbaren Teststand,
- die verbindlichen Projekt- und Servervorgaben,
- den historischen Fact-Check,
- bekannte Dokumentationsfehler,
- technische Risiken,
- noch nicht getroffene Produkt- und Integrationsentscheidungen.

Diese Datei ersetzt für den Einstieg die frühere Datei:

`docs/2026-07-24_PROJEKT_UEBERGABE/2026-07-24_PROJEKT_UEBERGABE_REALTIME_STT_CLIENT.md`

Sie überschreibt jedoch nicht die Quellenhierarchie aus `AGENTS.md`. Bei einem Widerspruch gelten weiterhin, je nach Sachgebiet:

1. `AGENTS.md`,
2. `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` für Dokumentenrollen und Pflegeprozess,
3. die Serverdokumente unter `server-docs-for-client-development/`,
4. `docs/IMPLEMENTATION_ROADMAP.md`,
5. der tatsächlich vorhandene Code und erfolgreich reproduzierbare Tests,
6. `task.md` und die operative Root-`ÜBERGABE.md`.

Die älteren Prüf-, Stellungnahme- und Fact-Check-Dateien im Übergabeordner bleiben als Nachweis des Prüfprozesses erhalten.

---

## 2. Verbindliches Projektziel

Entwickelt wird ein Windows-Desktop-Client für einen bereits vorhandenen RealtimeSTT-Server.

Der fertige Client soll:

1. dauerhaft im Hintergrund laufen,
2. Mikrofon-Audio per WebSocket übertragen,
3. Realtime- und Final-Events korrekt verarbeiten,
4. Realtime-Texte ausschließlich visuell anzeigen,
5. finale Texte in die lokale Historie aufnehmen,
6. finale Texte über Clipboard und `SendInput` in die aktuell fokussierte Anwendung einfügen,
7. fehlgeschlagene oder erneut gewünschte Einfügungen über die Historie wiederholen,
8. Netzwerk- und Mikrofonfehler ohne modale Störungen überstehen,
9. über Tray, Overlay und native globale Hotkeys bedienbar werden.

Das Minimalziel ist zuerst ein stabiler End-to-End-Core. Eine umfangreiche UI ist nachgeordnet.

---

## 3. Verbindliche Technologie- und Architekturentscheidungen

Folgende Entscheidungen sind abgeschlossen und dürfen nicht eigenmächtig ersetzt werden:

- Python 3.12
- vorhandene Projekt-Venv unter `venv\`
- PySide6 als UI-Framework
- Qt im Main Thread
- asyncio-Core in einem separaten Thread, sobald die Qt-Anwendung integriert wird
- native globale Windows-Hotkeys über Win32
- Clipboard und `SendInput` für Textinjektion
- SQLite für persistente Historieneinträge
- keine Einfügung von Realtime-Zwischentexten
- kein `pystray`
- kein `tkinter`
- kein `pynput`
- kein Admin-Service in der aktuellen Entwicklungsphase
- kein lokaler Fallback-STT-Server in der aktuellen Entwicklungsphase
- keine vorsorgliche Neuimplementierung des vorhandenen Core

### 3.1 Aktuelles Threading ist noch nicht das spätere Qt-Threading

Der Zielzustand lautet:

- Qt/PySide6 im Main Thread,
- asyncio-Core in einem separaten Thread,
- Core zu UI über Qt-Signale,
- UI zu Core über thread-sichere Befehle.

Der aktuelle Headless-Stand ist anders:

- `app.py` startet asyncio direkt mit `asyncio.run(...)` im Main Thread.
- `AudioCapture` besitzt einen eigenen Audio-Processing-Thread.
- `TextInjectionQueue` besitzt einen eigenen, nicht als Daemon laufenden Worker-Thread.
- PySide6, Tray, Overlay und Hotkeys sind noch nicht verdrahtet.

Der Zielzustand darf in Dokumenten nicht als bereits implementiertes Ist-Verhalten beschrieben werden.

---

## 4. Verbindliche Serveradressen

| Zweck | Adresse |
| --- | --- |
| WebSocket-Transkription | `wss://stt.voice.marcosudau.com/ws/transcribe` |
| HTTP-Health | `https://stt.voice.marcosudau.com/health` |
| Weboberfläche | `https://voice.marcosudau.com` |

Wichtig:

- `voice.marcosudau.com` ist nicht der WebSocket-Endpunkt des Desktop-Clients.
- Der in einer historischen Planversion enthaltene Host `voice.voice.marcosudau.com` ist falsch.
- Alte OpenAI-kompatible STT-Endpunkte sind nicht die primäre Realtime-WebSocket-Schnittstelle dieses Clients.

---

## 5. Quellenhierarchie für die Weiterarbeit

### 5.1 Serverprotokoll

Für Events, Befehle, Sessiongrenzen, Reconnect, Fehlersemantik und Zustandsübergänge sind ausschließlich die Markdown-Dateien unter folgendem Pfad maßgeblich:

`server-docs-for-client-development/`

Für AP4 besonders relevant:

- `02-websocket-protokoll.md`
- `03-server-events-kurzreferenz.md`
- `04-server-events-katalog-und-chronologie.md`
- `05-client-zustandsmodell.md`
- bei Fehler- und Reconnectfragen zusätzlich `07-robustheit-grenzen-und-sicherheit.md`

### 5.2 Zielarchitektur

Für gewünschte Client-Architektur und die Reihenfolge der Arbeitspakete ist maßgeblich:

`docs/IMPLEMENTATION_ROADMAP.md`

### 5.3 Tatsächlicher Stand

Code und erfolgreich ausführbare Tests bestimmen, was wirklich implementiert ist.

### 5.4 Bekannte Einschränkung aktiver Dokumente

`task.md`, Root-`ÜBERGABE.md` und Root-`README.md` enthalten noch bekannte falsche oder zu breite Aussagen. Diese werden in Abschnitt 13 ausdrücklich aufgelistet und dürfen nicht ungeprüft übernommen werden.

---

## 6. Maßgebliche Serverprotokoll-Fakten

Für die Controller-Integration gelten insbesondere:

1. Eine neue Verbindung erhält `hello` mit einer neuen `sessionId`.
2. Erst `ready` mit `ok: true` gibt den Start frei.
3. Vor Audio muss `{ "type": "start" }` gesendet werden.
4. Audio wird binär gesendet; Befehle und Events sind JSON-Textframes.
5. `segmentId` ist nur innerhalb einer Session eindeutig.
6. Die fachliche Identität eines Transkripts ist mindestens:

   `serverIdentity + sessionId + segmentId`

7. `realtime` ist revidierbar und ersetzt den bisherigen Text desselben Segments vollständig.
8. `final` ist die maßgebliche abgeschlossene Textfassung.
9. Ein `final` kann ohne vorheriges `realtime` eintreffen.
10. Nach `stop` kann ein bereits gepuffertes `final` noch asynchron eintreffen.
11. `timeline(realtime_transcript)` und `timeline(final_transcript)` sind Diagnose-/Chronologieereignisse und keine zweite Transkriptquelle.
12. Reconnect bedeutet eine neue Session und erfordert erneut:

    `hello -> ready -> start`

13. Alte Audiopakete dürfen nicht ungeprüft in die neue Session übertragen werden.
14. Das Protokoll besitzt keine Resume-ID und keine Replay-Bestätigung.
15. Unbekannte Zusatzfelder sind tolerant zu ignorieren.
16. Fehler sind nach `where` zu klassifizieren; nicht jeder Serverfehler rechtfertigt einen Reconnect.

---

## 7. Tatsächlich vorhandener Headless-Pfad

### 7.1 Aktuelle Dateien

Die real vorhandenen Kernmodule heißen:

- `core/audio_capture.py`
- `core/stt_session.py`
- `app.py`

Nicht vorhanden und historisch nicht als frühere reale Dateien belegt sind:

- `core/audio_processor.py`
- `core/stt_client.py`

Diese beiden Namen stammen aus unbelegten Einträgen in zwei späten `task.md`-Versionen und dürfen nicht als frühere Architektur vorausgesetzt werden.

### 7.2 Tatsächlicher Audiopfad

`core/audio_capture.py`:

- verwendet `sounddevice.InputStream`,
- verwendet NumPy-Arrays aus dem Sounddevice-Callback,
- öffnet das Gerät standardmäßig mit:
  - 16 kHz bevorzugt,
  - Mono,
  - `int16`,
  - 40-ms-Blöcken,
- wandelt den bereits als `int16` empfangenen Block mit `indata.tobytes()` in PCM-Bytes um,
- übergibt PCM, Sample-Rate, Kanalzahl und Framezahl an den Callback.

Wenn das Gerät 16 kHz nicht unterstützt:

- wird die Default-Sample-Rate des Geräts verwendet,
- der Client führt lokal kein Resampling durch,
- die tatsächliche Sample-Rate wird im Audiopaket mitgesendet,
- der Server ist für eine nötige Anpassung zuständig.

Es gibt im aktuellen Projekt:

- keinen Float32-Aufnahmepfad als verbindlichen Ist-Stand,
- kein lokales Resampling-Modul,
- keine lokale Float32-zu-PCM16-Konvertierungsstufe.

### 7.3 Aktuelles `app.py`

`RealtimeSTTClient` verbindet derzeit nur:

- `STTSession`,
- `AudioCapture`,
- eine `asyncio.Queue` für Audiopakete,
- Konsolenausgabe für Realtime- und Finaltexte.

Der aktuelle Finalpfad lautet:

`STTSession.on_text -> RealtimeSTTClient._on_text() -> print(...)`

Nicht vorhanden sind im App-Pfad:

- `TranscriptHistoryManager`,
- `TextInjectionQueue`,
- `TranscriptReinsertionService`,
- Controller-Schicht,
- Textinjektion eines Finaltexts,
- PySide6,
- Tray,
- Overlay,
- globale Hotkeys.

### 7.4 Aktuelle Session-Komponente

`core/stt_session.py` enthält:

- Transport- und Sessionzustände,
- einen Event-Reducer,
- Realtime- und Final-Upserts,
- `hello`-/`ready`-Handshake,
- Backoff mit Jitter,
- Anwendungsping,
- `start`, `stop`, `clear`,
- Audio-Paket-Encoding,
- Callback-Schnittstellen:
  - `on_text(segment_id, text, is_final)`,
  - `on_event(event_type, raw_event)`,
  - `on_state_change(state)`,
  - `on_transport_change(transport)`.

Wichtige AP4-Eigenschaft:

- `on_text` enthält keine `sessionId`.
- `on_text` wird nur ausgelöst, wenn der Reducer ein neues oder gegenüber dem bisherigen Segment verändertes Realtime-/Final-Ergebnis erkennt; ein bytegleich wiederholtes Final wird dort normalerweise unterdrückt.
- `on_event` enthält das rohe Serverevent einschließlich `sessionId`, wird aber für jedes Event aufgerufen.
- Die aktuelle `sessionId` ist außerdem im Sessionzustand vorhanden. Ob der Controller sie von dort lesen oder ausschließlich aus dem Rohereignis übernehmen soll, wurde noch nicht festgelegt.
- Callback-Exceptions werden in `STTSession` abgefangen und geloggt; sie beenden die Session nicht automatisch.

---

## 8. Reconnect: klar getrenntes Ist- und Zielverhalten

### 8.1 Implementiert

`STTSession.run()`:

- verbindet neu,
- wartet erneut auf `hello` und `ready`,
- verwendet Backoff und Jitter,
- behandelt Close-Code `1013` mit stärkerem Backoff,
- setzt den Transportzustand neu.

Das ist ein Transport-Reconnect.

### 8.2 Nicht implementiert

Der Diktierbetrieb wird nach einem Disconnect nicht vollständig automatisch wieder aufgenommen:

- `STTSession._connect_and_run()` setzt `_streaming = False`.
- `app.py::_auto_start_when_ready()` startet nur einmal und beendet sich danach.
- Nach einer später neu aufgebauten Session wird kein neues `send_start()` ausgelöst.
- Es gibt keine vollständige Mikrofon-Hot-Plug-/Wiederöffnungslogik.
- Es gibt keinen expliziten Benutzerwunschzustand, der nach Reconnect wiederhergestellt wird.

Korrekte Formulierung:

> Transport-Reconnect ist vorhanden. Automatische Wiederaufnahme von `start`, Audioübertragung und Benutzer-Diktierwunsch ist noch nicht implementiert und nicht verifiziert.

Die vollständige Selbstheilung gehört funktional zu AP5. AP4 darf den vorhandenen Transport-Reconnect nicht verschlechtern.

---

## 9. Arbeitspaket 1 – Transkript-Historie

**Status:** als eigenständige Komponente implementiert  
**Datei:** `core/history.py`  
**Tests:** 29

### 9.1 Öffentliche Datenobjekte

- `HistoryEntry`
- `InjectionAttempt`
- `InjectionStatus`
- `TranscriptHistoryManager`

### 9.2 Öffentliche Schnittstellen

- `add_entry(session_id, segment_id, text, timestamp=None) -> Optional[HistoryEntry]`
- `record_injection_attempt(entry_id, status, error=None, timestamp=None)`
- `get_memory_entries() -> list[HistoryEntry]`
- `get_persistent_entries(limit=None) -> list[HistoryEntry]`
- `cleanup()`

### 9.3 Implementierte Semantik

- In-Memory-Historie ist thread-sicher.
- Rückgaben sind defensive tiefe Kopien.
- Deduplizierung verwendet `(session_id, segment_id)`.
- Ein In-Process-Cache merkt bereits verarbeitete Segmente.
- SQLite besitzt zusätzlich einen UNIQUE-Constraint auf Session und Segment.
- IDs bleiben bei SQLite-Konflikten stabil.
- Injection-Attempts sind append-only.
- Parent und nachträglich persistierender Fehl-/Skipped-Attempt werden atomar gespeichert.
- SQLite-Verbindungen werden über `_db_session()` geschlossen.
- SQLite-Fehler sollen den Client nicht beenden; die Komponente fällt auf RAM-Betrieb zurück.

### 9.4 Selektive Persistenz

Die Default-Konfiguration lautet:

```yaml
history:
  enabled: true
  memory:
    max_entries: 5
  persistent:
    enabled: true
    max_entries: 100
    retention_days: 0
    min_characters: 1000
    store_failed_injections: true
    store_all: false
    db_path: null
```

Ein Finaltext wird sofort in die In-Memory-Historie aufgenommen.

Persistent in SQLite gespeichert wird er standardmäßig, wenn:

- er mindestens 1000 Zeichen lang ist,
- ein Versuch `failed` oder `skipped` ist,
- oder `store_all: true` gesetzt wird.

Ein kurzer, erfolgreich eingefügter Finaltext kann daher ausschließlich im RAM liegen. Nach Prozessende oder nach Rotation aus dem RAM ist er nicht garantiert wiederherstellbar.

Diese selektive Semantik war historisch ausdrücklich vorgesehen. Nicht entschieden wurde jedoch, ob das endgültige Produktziel echte Crash-Sicherheit für jedes Final verlangt. Diese Entscheidung ist vor AP4 offen.

### 9.5 Deduplizierungsgrenze

`add_entry()` kann bei einem bereits verarbeiteten Segment:

- den vorhandenen Eintrag aus RAM zurückgeben,
- den vorhandenen Eintrag aus SQLite zurückgeben,
- oder `None` zurückgeben, wenn das Segment nur noch im In-Process-Cache bekannt ist.

Die Rückgabe unterscheidet nicht eindeutig zwischen:

- „neu angelegt“,
- „bereits vorhanden und wiedergefunden“.

Ein AP4-Controller darf daher nicht einfach jeden nichtleeren Rückgabewert erneut enqueuen, wenn exakt-einmalige Einfügung verlangt wird.

### 9.6 Bekannte Fehlersemantik-Grenze

`get_persistent_entries()` fängt reale SQLite-Lesefehler intern ab und liefert `[]`.

Dadurch kann ein Aufrufer nicht sicher unterscheiden zwischen:

- „Datenbank fehlerfrei leer“,
- „Datenbank-Lesefehler“,
- „Persistenz deaktiviert“.

Das ist für die Reinsertion-Fehlersemantik relevant und benötigt bei gewünschter Unterscheidung eine ausdrückliche API-Korrektur.

---

## 10. Arbeitspaket 2 – Text-Injection-Queue

**Status:** als eigenständige Komponente implementiert  
**Datei:** `core/text_injector.py`  
**Tests:** 41

### 10.1 Öffentliche Schnittstellen

- `start()`
- `enqueue(entry: HistoryEntry) -> bool`
- `stop(timeout=None)`
- `is_running() -> bool`

### 10.2 Lifecycle

`NEW -> INITIALIZING -> RUNNING -> STOPPING -> STOPPED`

- genau ein FIFO-Worker,
- Worker ist kein Daemon,
- parallele `start()`-Aufrufe sind abgesichert,
- Initialisierungsfehler werden fail-closed behandelt,
- `stop()` wartet geordnet auf angenommene Jobs und Thread-Ende,
- nach `STOPPED` kein unbemerkter Neustart.

### 10.3 Win32- und Clipboard-Semantik

- eigenes unsichtbares `HWND_MESSAGE`-Owner-Window,
- kein `OpenClipboard(0)` für den Schreibpfad,
- Clipboard-Schreiben und `SendInput` über `ctypes`,
- vollständige native `INPUT`-Strukturen,
- Foreground-Window wird unmittelbar vor `SendInput` erfasst,
- Ctrl-down, V-down, V-up, Ctrl-up,
- optionales Clipboard-Backup,
- Restore nur bei unveränderter Clipboard-Sequenznummer,
- genau ein abschließender History-Attempt pro angenommenem Queue-Job.

Der Client kann nur dokumentieren, dass der technische Paste-Befehl gesendet wurde. Er kann nicht garantieren, dass die Zielanwendung den Text fachlich angenommen hat.

### 10.4 Tatsächlich wirksame Konfiguration

Wirksam verwendet werden unter anderem:

- `text_injection.paste_delay_ms`
- `clipboard.restore_previous`
- `clipboard.restore_delay_ms`
- `clipboard.backup_max_bytes`
- `clipboard.open_retries`
- `clipboard.open_retry_delay_ms`

Derzeit nur modelliert, aber im produktiven Injection-Pfad nicht wirksam sind:

- `text_injection.final_strategy`
- `text_injection.append_space`
- `text_injection.warn_elevated`

Diese Felder dürfen in der Übergabe nicht als bereits implementiertes Verhalten beschrieben werden.

### 10.5 Offene reale Prüfung

Der Windows-/Notepad-Smoke-Test ist nicht dokumentiert ausgeführt:

```powershell
.\venv\Scripts\python.exe tests\manual_test_text_injector.py
```

Dieser Test ist getrennt von den 41 automatisierten Mock-/Unit-Tests zu behandeln.

---

## 11. Arbeitspaket 3 – Reinsertion

**Status:** als UI-neutrale Komponente implementiert  
**Datei:** `core/reinsertion.py`  
**Tests:** 26

### 11.1 Öffentliche Schnittstellen

- `reinsert_last() -> ReinsertionResult`
- `reinsert_entry(entry_id) -> ReinsertionResult`
- `get_recent_entries(limit=None) -> tuple[HistoryEntry, ...]`

### 11.2 Implementierte Eigenschaften

- keine UI- oder PySide6-Abhängigkeit,
- Memory-first,
- SQLite-Fallback,
- defensive Kopien,
- neueste Einträge zuerst,
- Deduplizierung mit Memory-Präferenz,
- keine neuen `HistoryEntry`-Objekte bei Reinsertion,
- Übergabe ausschließlich über `TextInjectionQueue.enqueue(entry)`,
- Concurrency-Test mit fünf Threads und `threading.Barrier`.

### 11.3 Resultatstatus

- `queued`
- `empty_history`
- `entry_not_found`
- `queue_unavailable`
- `failed`

### 11.4 Attempt-Semantik

- Queue-Ablehnung: best-effort genau ein `skipped`-Attempt
- Enqueue-Exception: best-effort genau ein `failed`-Attempt
- History-Fehler vor Auflösung einer Entry-ID: kein Attempt an unbekannter ID
- erfolgreicher Queue-Auftrag: der Service erzeugt keinen zusätzlichen Attempt; der Queue-Worker protokolliert seinen Abschluss

### 11.5 Historische Abnahme korrekt eingeordnet

AP3 wurde in der früheren Chat-Session:

- inhaltlich geprüft,
- nach zwei zusätzlichen Fehlerfalltests korrigiert,
- über Dateigrößen und SHA-256-Hashes mit den materialisierten Dateien abgeglichen,
- als technisch abgeschlossen bewertet.

Das war keine ausdrücklich formulierte formale Benutzerabnahme.

Der damalige prüfende Chat konnte den vollständigen 96er-Lauf nicht selbst ausführen. Die 96 Tests wurden bei der späteren Projektprüfung und erneut für diese aktualisierte Übergabe unabhängig reproduziert.

---

## 12. Verifizierter Teststand

### 12.1 Frische Unit-Test-Verifikation

Am 24. Juli 2026 wurde mit:

`P:\DockerProjekte\RealtimeSTT_client\venv\Scripts\python.exe`

in einer isolierten temporären Arbeitsumgebung ausgeführt:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Ergebnis:

```text
Ran 96 tests in 2.743s
OK
```

Aufteilung:

| Testdatei | Anzahl |
| --- |---:|
| `tests/test_history.py` | 29 |
| `tests/test_text_injector.py` | 41 |
| `tests/test_reinsertion.py` | 26 |
| **Gesamt** | **96** |

Die während des Laufs ausgegebenen Fehlerlogs stammen aus absichtlich simulierten Fehlerfällen der Tests.

### 12.2 Was diese 96 Tests nicht prüfen

Nicht abgedeckt sind:

- `app.py`,
- `AudioCapture`,
- `STTSession`,
- realer Mikrofonzugriff,
- Audioübertragung an den Server,
- `realtime`-/`final`-End-to-End-Verarbeitung,
- Reconnect mit erneuter `start`-Sequenz,
- PySide6,
- Tray,
- Overlay,
- globale Hotkeys,
- realer Clipboard-/Notepad-Erfolg.

### 12.3 Connection-Smoke-Test

`tests/test_connection.py` ist ein eigenständiges Diagnose-Skript und kein durch `unittest discover` ausgeführter Testfall.

Historisch belegt ist ein erfolgreicher Lauf mit:

- HTTP-Health `ok: true`,
- HTTP-Health `ready: true`,
- WebSocket `hello`,
- WebSocket `ready` mit `ok=true`,
- Anwendungsping/-pong,
- Meldung `ALL TESTS PASSED`.

Das Skript:

- sendet kein `start`,
- sendet kein Audio,
- wartet nicht auf `realtime`,
- wartet nicht auf `final`,
- prüft kein Mikrofon.

Außerdem nimmt seine aktuelle Handshake-Logik nach `hello` direkt das nächste Event als `ready`, obwohl die Serverdokumentation zusätzliche Startphase-Events zulässt. Der produktive `STTSession._wait_for_ready()`-Code ist toleranter.

Korrekte Bezeichnung:

> Historisch erfolgreicher Health-/Handshake-/Ping-Pong-Smoke-Test; kein Transkriptions-End-to-End-Test.

### 12.4 Weiterhin offene manuelle Tests

- realer Notepad-Test,
- physisches Mikrofon bis Server-Audio,
- Empfang mindestens eines `realtime`-Events,
- Empfang mindestens eines `final`-Events,
- späterer kompletter Pfad bis Historie und Textinjektion,
- Hotkey-Reinsertion,
- Reconnect mit Wiederaufnahme,
- Mikrofon-Hot-Plug.

---

## 13. Aufgelöste Missverständnisse und bekannte Dokumentationsabweichungen

| Thema | Falsche oder missverständliche Aussage | Korrekte Einordnung |
| --- | --- | --- |
| Audiopfad | Float32, lokales Resampling, `audio_processor.py` | Direktes `int16`; kein lokales Resampling-Modul |
| Sessiondatei | `core/stt_client.py` | Tatsächlich `core/stt_session.py` |
| 96 Tests | Gesamtclient getestet | Nur AP1 bis AP3 |
| Live-Test | Headless-Audio/Transkription verifiziert | Nur Health/Handshake/Ping-Pong historisch belegt |
| Reconnect | Diktierbetrieb vollständig selbstheilend | Nur Transport-Reconnect vorhanden |
| AP4-Pfad | Final bereits über History und Queue | Ist erst Ziel von AP4 |
| Exakt einmal | bereits durch API gelöst | Nur Abnahmekriterium; Integrationsvertrag offen |
| „lokal gesichert“ | automatisch jedes Final in SQLite | Aktuell zunächst RAM; SQLite selektiv |
| Hotkey | eine widersprüchliche Tastenkombination | Zwei Zielaktionen: Aufnahme und Reinsertion |
| AP3 „abgenommen“ | formale Benutzerabnahme | Technische Chat-/Dateiprüfung |
| Hashregel | schon immer allgemeine Pflicht | Entstand als gezielte Reaktion auf einen Materialisierungsfehler |

### 13.1 Aktuell falsche Einträge in `task.md`

Die Phase-1-Zeilen in `task.md` sind veraltet:

- Audio ist nicht als Float32-/Resampling-Pipeline implementiert.
- `core/audio_processor.py` existiert nicht.
- `core/stt_client.py` existiert nicht.
- „Headless-Betrieb verifiziert gegen Server“ ist zu breit.
- „Live-Verbindungstests erfolgreich“ muss auf den Smoke-Test begrenzt werden.

Die AP1-/AP2-/AP3-Testzahlen in `task.md` sind dagegen korrekt.

### 13.2 Zu breite Aussage in Root-`ÜBERGABE.md`

„Headless Audioaufnahme und Streaming an den Server funktionieren“ ist historisch nicht als echter Mikrofon-/Final-End-to-End-Lauf belegt.

### 13.3 Veraltete Root-`README.md`

Die README nennt:

- Python 3.10+ statt verbindlich Python 3.12,
- globales `pip`,
- globales `python app.py`.

Maßgeblich sind ausschließlich die Projekt-Venv-Befehle aus Abschnitt 18.

### 13.4 Roadmap: Soll und Ist trennen

Die Roadmap beschreibt teilweise bereits die spätere Zwei-Thread-Architektur. PySide6 und die Qt-/asyncio-Brücke sind aber noch nicht implementiert.

### 13.5 Schutzformulierung in `AGENTS.md`

`AGENTS.md` bezeichnet den Headless-Core als fertiggestellt und gegen den realen Server getestet. Diese Formulierung bleibt als Schutzregel maßgeblich: Der vorhandene Core darf nicht vorsorglich neu entworfen werden.

Sie ist jedoch nicht als Beleg für einen Mikrofon-/Transkriptions-End-to-End-Test oder vollständige Selbstheilung zu lesen. Historisch nachgewiesen ist nur der Connection-Smoke-Test. Änderungen am geschützten Core sind weiterhin nur zulässig, wenn:

- die aktive Integration sie zwingend benötigt,
- ein reproduzierbarer Test einen Fehler nachweist,
- oder eine verbindliche Protokollvorgabe verletzt ist.

---

## 14. Bekannte technische Risiken und Repository-Unstimmigkeiten

### R-01 – Fremdthreadiger Zugriff auf `asyncio.Queue`

`AudioCapture` ruft den Audio-Paket-Callback aus seinem Processing-Thread auf.

`app.py::_on_audio_packet_from_thread()` verwendet dort direkt:

```python
self._audio_send_queue.put_nowait(...)
```

`asyncio.Queue` ist nicht für direkten threadübergreifenden Zugriff vorgesehen. Der Kommentar bezeichnet dies als thread-sichere Bridge, verwendet aber weder:

- `loop.call_soon_threadsafe(...)`,
- noch eine andere explizite Thread-Bridge.

Dieser Pfad ist nicht durch die 96 Tests abgedeckt.

### R-02 – Ping-Miss-Erkennung

Im aktuellen Ping-Loop wird:

1. zuerst ein neuer Ping gesendet,
2. dabei `ping_started_at` neu gesetzt,
3. danach sofort geprüft, ob ein Pong vorliegt.

Zusätzlich bleibt `round_trip_ms` nach einem erfolgreichen Pong gesetzt. Dadurch ist die Erkennung aufeinanderfolgender ausbleibender Pongs nicht zuverlässig.

Dieser Pfad ist nicht durch die 96 Tests abgedeckt.

### R-03 – Kein automatisches `start` nach Reconnect

Nach Reconnect wird kein neues `send_start()` ausgelöst. Siehe Abschnitt 8.

### R-04 – Connection-Test zu schmal

Das Standalone-Skript:

- ist nicht Teil der 96 Tests,
- prüft keine Transkription,
- ist weniger tolerant als der produktive Ready-Handshake,
- signalisiert einen reinen Health-Fehler nicht zwingend über einen expliziten Prozessfehlercode.

### R-05 – Relative Testdatenbanken im Projekt

Im Projektwurzelverzeichnis liegen:

- `config_path.db`
- `param_path.db`

Beide stammen sehr wahrscheinlich aus `test_database_path_priorities()` in `tests/test_history.py`, das relative Pfade gegen das aktuelle Arbeitsverzeichnis auflöst.

Diese Dateien sind Testartefakte und keine vorgesehenen Laufzeitdaten.

### R-06 – Cache- und Ignore-Hygiene

Im Projekt liegen `__pycache__`-Verzeichnisse. Ein Git-Repository beziehungsweise `.git` ist derzeit nicht vorhanden. Eine verbindliche `.gitignore` ist nicht vorhanden.

### R-07 – Absoluter Logging-Pfad

`config.yaml` enthält:

`P:\DockerProjekte\RealtimeSTT_client\logs`

Dieser Pfad ist installations- und rechnerabhängig.

### R-08 – Zusätzliche Root-Artefakte

Im Root liegen unter anderem:

- `cleanup.py`
- `cleanup_v1.py`
- `persistent-files.txt`
- `persistent-files2.txt`

Ihre Rolle gehört nicht zum implementierten Laufzeitpfad und sollte vor einer Repository-Bereinigung separat geklärt werden. Sie dürfen nicht beiläufig gelöscht werden.

---

## 15. Vor AP4 ausdrücklich zu treffende Entscheidungen

Diese Punkte sind nicht durch den bisherigen Verlauf abschließend entschieden. Ein Weiterbearbeitungs-Agent darf sie nicht eigenmächtig festlegen.

### E-01 – Crash-Sicherheit jedes Finaltexts

Zu entscheiden:

- selektive SQLite-Persistenz beibehalten,
- oder jedes Final vor dem Paste-Versuch persistent speichern.

Falls selektiv:

- muss dokumentiert sein, dass kurze erfolgreiche Finals nur im RAM verbleiben können.

Falls jedes Final crash-sicher sein soll:

- müssen Default-Konfiguration, History-Tests und AP4-Abnahmekriterien angepasst werden.

### E-02 – History-Fehlerresultat

Zu entscheiden:

- soll `get_persistent_entries()` weiterhin Fehler als leere Liste behandeln,
- oder eine unterscheidbare Resultat-/Fehlerschnittstelle erhalten?

Diese Änderung darf nicht beiläufig in AP4 versteckt werden.

### E-03 – AP4-Eventeingang und Exakt-einmal-Vertrag

Zu entscheiden:

- `on_text`,
- `on_event`,
- oder eine neue UI-neutrale Session-/Controller-Schnittstelle.

Dabei müssen geklärt werden:

- Herkunft der `sessionId`,
- Unterscheidung „HistoryEntry neu“ gegenüber „bereits vorhanden“,
- Verhalten bei `add_entry() -> None`,
- Verhalten bei einem bereits vorhandenen zurückgegebenen Entry,
- Verhalten bei History-Fehler,
- Verhalten bei `enqueue() -> False`,
- Verhalten bei Enqueue-Exception,
- genau ein Attempt je fachlichem Einfügeversuch,
- Sessiongrenze nach Reconnect.

### E-04 – Hotkey-Konfigurationsschema

Dokumentiertes Ziel:

- `Ctrl+Shift+Space`: Aufnahme umschalten,
- `Ctrl+Alt+Space`: letztes Transkript erneut einfügen.

Aktuell gibt es nur:

```yaml
hotkey:
  mode: toggle
  key: <ctrl>+<shift>+space
  auto_start: false
```

Das Format ist als `pynput`-Format kommentiert, obwohl `pynput` verboten ist.

Zu entscheiden ist ein getrenntes, Win32-kompatibles und validierbares Schema für beide Aktionen.

### E-05 – Reihenfolge der Baseline-Korrekturen

Empfohlene Abgrenzung:

- Audio-Thread-Bridge: vor oder als klarer erster Teil von AP4,
- Ping-Miss-Logik: separates kleines Core-Korrekturpaket,
- vollständige Reconnect-/Mikrofon-Selbstheilung: AP5.

Die konkrete Beauftragung muss vor Codeänderungen festgelegt werden.

### E-06 – Repository-Hygiene

Separat zu beauftragen:

- Testpfadkorrektur,
- Entfernen bestätigter DB-Testartefakte,
- Cache-/Ignore-Regeln,
- README-Korrektur,
- Bereinigung aktiver Dokumente,
- Klärung der zusätzlichen Root-Artefakte.

---

## 16. Arbeitspaket 4 – Controller-Integration

**Status:** nicht begonnen

### 16.1 Verbindliches Ziel

Finale Serverevents werden über eine UI-neutrale Controller-Schicht verarbeitet:

1. echtes `final`-Event empfangen,
2. `sessionId`, `segmentId` und `text` übernehmen,
3. fachlich deduplizieren,
4. History-Verarbeitung ausführen,
5. den eindeutig als neu zu verarbeitenden Entry an die Injection-Queue übergeben,
6. Queue-/Attempt-Semantik konsistent protokollieren.

Realtime-Events:

- aktualisieren nur Core-Zustand beziehungsweise später das Overlay,
- werden nie in die Text-Injection-Queue gestellt.

### 16.2 Architekturgrenzen

- Core bleibt frei von PySide6.
- UI führt keine SQLite-Operationen aus.
- UI führt keine direkten WebSocket-Aufrufe aus.
- Callback-Fehler dürfen die WebSocket-Session nicht beenden.
- Queue und Historie werden nur über öffentliche Schnittstellen verwendet.
- Mehrere Finals müssen in definierter Reihenfolge verarbeitet werden.
- Nachlaufende Finals nach `stop` müssen weiterhin verarbeitet werden.
- Eine neue Session darf nicht mit Segmenten der alten Session vermischt werden.

### 16.3 Mindesttests für AP4

Nach Entscheidung von E-01 bis E-05 mindestens:

- einzelnes Final,
- Final ohne vorheriges Realtime,
- mehrfaches identisches Final,
- gleiche `segmentId` in zwei verschiedenen Sessions,
- mehrere Finals in Empfangsreihenfolge,
- Realtime erzeugt keinen Queue-Auftrag,
- History liefert neu,
- History liefert vorhandenen Entry,
- History liefert `None`,
- History-Fehler,
- Queue nicht gestartet,
- Queue-Ablehnung,
- Enqueue-Exception,
- Callback-Fehler beendet Session nicht,
- nachlaufendes Final nach `stop`,
- kontrollierter Start und Shutdown aller beteiligten Komponenten.

### 16.4 Abschlussbedingung

AP4 ist erst abgeschlossen, wenn:

- der Integrationsvertrag dokumentiert ist,
- passende Unit- und Integrationstests vorhanden sind,
- die neuen Tests bestehen,
- alle 96 bestehenden Tests weiterhin bestehen,
- die relevanten Core-/Sessiontests bestehen,
- `task.md`, Roadmap und Root-`ÜBERGABE.md` korrigiert wurden,
- und danach gestoppt wird, ohne AP5 zu beginnen.

---

## 17. Spätere Arbeitspakete

### AP5 – Fehlerverhalten und Selbstheilung

- vollständige Wiederaufnahme nach Netzwerkverlust,
- erneutes `start` in neuer Session,
- Wiederherstellung des Diktierwunsches,
- Mikrofon-Hot-Plug,
- Wiederöffnen des konfigurierten oder Default-Mikrofons,
- modalfreie Statushinweise,
- keine Meldungsschleifen.

### AP6 – UI-Shell

- PySide6-`QApplication`,
- `QSystemTrayIcon`,
- Overlay,
- native Win32-Hotkeys,
- Single-Instance-Guard,
- Qt-/asyncio-Bridge,
- Tray-Verlauf und Reinsertion-Aufrufe.

### AP7 – Härtung und Polish

- Reconnect-Stresstests,
- Mikrofon-Hot-Plug-Stresstests,
- Multi-Monitor/DPI,
- Autostart,
- Logging-Review,
- Packaging,
- Herunterfahren/Abmelden,
- Langzeitbetrieb,
- vollständige Praxis-End-to-End-Tests.

Nicht automatisch mit einem Folgepaket beginnen.

---

## 18. Betriebs- und Prüfkommandos

### 18.1 Python

Verbindlich:

```powershell
.\venv\Scripts\python.exe
```

Aktuell verifiziert:

```text
Python 3.12.10
```

Nicht verwenden:

```powershell
python
pip
```

Installationen nur über:

```powershell
.\venv\Scripts\python.exe -m pip ...
```

### 18.2 Unit-Tests

```powershell
$env:PYTHONIOENCODING='utf-8'
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Beim Testen müssen:

- `LOCALAPPDATA`,
- `TEMP`,
- `TMP`,
- Arbeitsverzeichnis

so isoliert werden, dass keine echte Benutzer-Historie und keine DB-Dateien im Projekt verändert werden.

### 18.3 Connection-Smoke-Test

```powershell
.\venv\Scripts\python.exe tests\test_connection.py
```

Nur als Live-Diagnose ausführen. Er ist kein Mikrofon-/Final-End-to-End-Test.

### 18.4 Manueller Notepad-Test

```powershell
.\venv\Scripts\python.exe tests\manual_test_text_injector.py
```

Nur bewusst mit geöffnetem Notepad und kontrolliertem Fokus ausführen.

### 18.5 Headless-App

```powershell
.\venv\Scripts\python.exe app.py
```

Dieser Lauf greift auf das reale Mikrofon, den Server und die konfigurierte Logdatei zu. Er ist ein manueller Live-Test und nicht mit der Unit-Suite gleichzusetzen.

---

## 19. Datenschutz und Sicherheitsregeln

- `.env` darf nicht ausgegeben oder committed werden.
- API-Keys dürfen nicht in Logs, Tests oder Übergaben erscheinen.
- Die produktive SQLite-Historie liegt unter lokalem Anwendungsdatenpfad, nicht im Repository.
- Laufzeitdaten, Logs und Datenbanken sind keine Projektquellen.
- Keine Dateien allein aufgrund ihres Namens löschen.
- Vor rekursiven Löschungen Zielpfade vollständig auflösen und prüfen.
- Der aktuelle Core darf nur bei reproduzierbarem Fehler, Protokollverstoß oder zwingender Integration geändert werden.

---

## 20. Dateimaterialisierung und reproduzierbare Übergabe

Im bisherigen Verlauf gab es einen Antigravity-Turn, dessen Änderungen im Review sichtbar, aber zunächst nicht zuverlässig im realen Projekt materialisiert waren.

Die Wiederherstellung wurde über:

- erneutes Schreiben in denselben Projektpfad,
- direktes Lesen von der Festplatte,
- Dateigrößen,
- SHA-256-Hashes,
- erneute Testberichte

verifiziert.

Eine allgemeine Hashpflicht war damals noch kein dauerhaft beschlossener Prozess. Für zukünftige Arbeitspakete ist dennoch sinnvoll:

1. geänderte Dateien direkt aus dem realen Projektpfad erneut lesen,
2. absolute Pfade dokumentieren,
3. Größen und Zeitstempel prüfen,
4. SHA-256-Hashes oder einen Git-Commit als Snapshot verwenden,
5. erst danach den Abschluss melden.

Aktuell ist im Projektpfad kein `.git`-Repository vorhanden.

---

## 21. Arbeitsanweisung für den nächsten Agenten

Vor jeder Codeänderung:

1. `AGENTS.md` vollständig lesen.
2. `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` vollständig lesen.
3. Diese aktualisierte Gesamtübergabe lesen.
4. Root-`ÜBERGABE.md`, `task.md` und `docs/IMPLEMENTATION_ROADMAP.md` lesen, aber ihre bekannten Abweichungen aus Abschnitt 13 berücksichtigen.
5. Für AP4 sämtliche relevanten Serverdokumente erneut öffnen.
6. `app.py`, alle Core-Dateien, Config und Tests vollständig prüfen.
7. Die bestehende Testsuite isoliert ausführen.
8. E-01 bis E-05 mit dem Benutzer beziehungsweise im ausdrücklichen Arbeitsauftrag klären.
9. Eine kurze konkrete Umsetzungsskizze für genau das beauftragte Paket erstellen.
10. Nur dieses Paket umsetzen.
11. Neue Tests und Regressionstests ausführen.
12. Fehler iterativ beheben.
13. Aktive Dokumente konsistent aktualisieren.
14. Dateimaterialisierung verifizieren.
15. Danach stoppen.

Nicht zulässig:

- spätere Arbeitspakete vorwegnehmen,
- Core vorsorglich refactoren,
- PySide6 in die bestehenden Core-Komponenten ziehen,
- alternative Frameworks einführen,
- alte Chat-Zusammenfassungen über Code und Originaldokumente stellen,
- „Live-Test“, „Reconnect“, „lokal gesichert“, „exakt einmal“ oder „abgenommen“ ohne genaue Bedeutung verwenden.

---

## 22. Kompakter Übergabestatus

> Implementiert und frisch automatisiert verifiziert sind die drei isolierten Komponenten Transkript-Historie, Text-Injection-Queue und Reinsertion. Ihre 96 Unit-Tests bestehen. Der vorhandene Headless-Core enthält Mikrofonaufnahme, WebSocket-Session, Reducer und Transport-Reconnect, ist aber nicht durch diese 96 Tests abgedeckt. Historisch belegt ist nur ein Health-/Handshake-/Ping-Pong-Smoke-Test; ein echter Lauf vom Mikrofon bis zu einem `final`-Event bleibt offen. Historie, Queue und Reinsertion sind noch nicht in `app.py` integriert. AP4 Controller-Integration ist der nächste reguläre Funktionsschritt, darf aber erst nach ausdrücklicher Festlegung von Crash-Sicherheit, History-Fehlersemantik, Eventeingang/Exakt-einmal-Vertrag, Hotkey-Schema und Reihenfolge der Thread-/Ping-Baseline-Korrekturen implementiert werden.

---

## 23. Quellen dieser konsolidierten Übergabe

Aktive Projektquellen:

- `AGENTS.md`
- `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`
- `app.py`
- `config.yaml`
- `requirements.txt`
- `task.md`
- `ÜBERGABE.md`
- `docs/IMPLEMENTATION_ROADMAP.md`
- `core/*.py`
- `tests/*.py`
- `server-docs-for-client-development/*.md`

Prüf- und Fact-Check-Quellen:

- `docs/2026-07-24_PROJEKT_UEBERGABE/PRUEFBERICHT_2026-07-24.md`
- `docs/2026-07-24_PROJEKT_UEBERGABE/STELLUNGNAHME_ZUM_PRUEFBERICHT_2026-07-24.md`
- `docs/2026-07-24_PROJEKT_UEBERGABE/OFFENPUNKTE_NACH_STELLUNGNAHME_2026-07-24.md`
- `docs/2026-07-24_PROJEKT_UEBERGABE/GESAMTZUSAMMENFASSUNG_FACTCHECK_2026-07-24.md`
- gezielte Originalbelege aus:
  - `bisheriger_projekt_verlauf/chatverlauf_bis_abschluss_arbeitspakt3.html`
  - `bisheriger_projekt_verlauf/referenzierte_datei_versionen/`

Bei zukünftigen Änderungen zählt nicht diese Zusammenfassung allein, sondern weiterhin die in Abschnitt 5 beschriebene Quellenhierarchie.
