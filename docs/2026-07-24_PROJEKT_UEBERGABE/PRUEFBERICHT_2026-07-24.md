# Prüfbericht zur Projektübergabe vom 24. Juli 2026

## 1. Gegenstand und Ergebnis in Kurzform

Geprüft wurde die Datei:

`docs/2026-07-24_PROJEKT_UEBERGABE/2026-07-24_PROJEKT_UEBERGABE_REALTIME_STT_CLIENT.md`

Gesamturteil:

Die Übergabe ist sprachlich überwiegend gut strukturiert und vermittelt das grundsätzliche Projektziel sowie den Stand der Arbeitspakete 1 bis 3 verständlich. Sie ist in der jetzigen Form aber **noch nicht zuverlässig genug, um als alleinstehende und widerspruchsfreie Übergabe zu dienen**.

Die wichtigsten Gründe sind:

1. Der beschriebene Phase-1-Audiopfad stimmt nicht mit dem vorhandenen Code überein.
2. Mehrere Dokumente nennen nicht vorhandene Dateien (`core/audio_processor.py`, `core/stt_client.py`).
3. Transport-Reconnect und vollständige Wiederherstellung des Diktierbetriebs werden nicht sauber voneinander abgegrenzt.
4. Die 96 automatisierten Tests sind aktuell reproduzierbar erfolgreich, decken aber ausschließlich die Arbeitspakete 1 bis 3 ab. Sie testen weder `app.py`, `AudioCapture` noch `STTSession`.
5. Der angegebene Live-Test ist nur ein Health-/Handshake-/Ping-Test und kein Mikrofon-, Audio- oder Transkriptions-End-to-End-Test.
6. Mehrere als offen formulierte Fragen zu Arbeitspaket 4 sind anhand des vorhandenen Codes bereits beantwortet.
7. Die Übergabe bezeichnet sich als alleinstehenden Einstiegspunkt, obwohl `AGENTS.md` eine verbindliche Quellenhierarchie und umfangreiche Pflichtlektüre vorgibt.
8. Wesentliche verbindliche Architekturentscheidungen – insbesondere Python 3.12 sowie Qt im Main Thread und asyncio in einem separaten Thread – fehlen oder sind nicht eindeutig genug benannt.
9. Im Code bestehen nicht durch die 96 Tests erfasste Risiken beim Thread-Übergang, beim Ping-Monitoring und beim Wiederanlauf nach Reconnect.
10. Im Projektwurzelverzeichnis liegen zwei SQLite-Testartefakte, obwohl lokale Datenbanken laut Projektregeln nicht als Projektdateien behandelt werden dürfen.

Die Aussage „Arbeitspakete 1 bis 3 abgeschlossen; Arbeitspaket 4 als Nächstes“ ist im Kern korrekt. Die Beschreibung des davor vorhandenen Headless-Cores und der Grad seiner Verifikation müssen jedoch präzisiert werden.

---

## 2. Prüfgrundlage und Vorgehen

### 2.1 Maßgebliche Quellen

Die Prüfung erfolgte entsprechend der in `AGENTS.md` festgelegten Quellenhierarchie:

- Serverprotokoll:
  - sämtliche Markdown-Dateien unter `server-docs-for-client-development/`
- Zielarchitektur:
  - `docs/IMPLEMENTATION_ROADMAP.md`
- tatsächlicher Implementierungsstand:
  - `app.py`
  - alle Python-Dateien unter `core/`
  - alle vorhandenen Tests
- Fortschritt und operative Übergabe:
  - `task.md`
  - `ÜBERGABE.md`
- Konfiguration und Umgebung:
  - `config.yaml`
  - `requirements.txt`
  - `venv/pyvenv.cfg`
- ergänzend:
  - tatsächliche Projektstruktur
  - `README.md`

Die Datei `.env` wurde aus Datenschutzgründen nicht inhaltlich gelesen.

### 2.2 Testprüfung

Der dokumentierte Testbefehl wurde nicht direkt im Projektverzeichnis ausgeführt, weil die Tests dort Cache- und SQLite-Dateien erzeugen können. Stattdessen wurde eine isolierte temporäre Kopie der relevanten Projektdateien außerhalb des Projekts verwendet. `LOCALAPPDATA`, `TEMP` und `TMP` wurden ebenfalls auf temporäre Verzeichnisse umgeleitet und Bytecode-Erzeugung wurde deaktiviert.

Verwendeter Python-Interpreter:

`P:\DockerProjekte\RealtimeSTT_client\venv\Scripts\python.exe`

Ergebnis des reproduzierten Testlaufs:

```text
Ran 96 tests in 2.616s

OK
```

Damit ist der dokumentierte Stand von 29 History-, 41 Text-Injection- und 26 Reinsertion-Tests am 24. Juli 2026 reproduzierbar.

Ein Live-Server- oder Mikrofontest wurde im Rahmen dieser Dokumentenprüfung nicht ausgeführt. Die Übergabe enthält dazu nur historische Aussagen; der praktische Mikrofon-End-to-End-Test und der reale Notepad-Test sind nach den vorhandenen Dokumenten weiterhin offen.

---

## 3. Bestätigte und zutreffende Aussagen

Folgende Kernaussagen der Übergabe stimmen mit den verbindlichen Quellen und dem vorhandenen Code überein:

### 3.1 Projektziel und Serveradresse

- Das Projekt ist ein Windows-Desktop-Client für einen vorhandenen RealtimeSTT-Server.
- Der korrekte WebSocket-Endpunkt ist:
  - `wss://stt.voice.marcosudau.com/ws/transcribe`
- Der Health-Endpunkt ist:
  - `https://stt.voice.marcosudau.com/health`
- `https://voice.marcosudau.com` ist die Weboberfläche und nicht der WebSocket-Endpunkt des Desktop-Clients.
- Realtime-Texte sind revidierbar und dürfen nicht in Zielanwendungen eingefügt werden.
- Nur `final` ist der abgeschlossene Transkripttext.
- Nach einem Reconnect beginnt eine neue Session mit neuer `sessionId`.

### 3.2 Arbeitspaket 1 – Historie

- `core/history.py` ist vorhanden.
- Die Komponente verwaltet In-Memory-Einträge und optionale SQLite-Persistenz.
- Deduplizierung erfolgt über `(session_id, segment_id)`.
- Einfügeversuche werden append-only an bestehenden Einträgen dokumentiert.
- Die Anzahl von 29 Tests in `tests/test_history.py` stimmt.
- Diese 29 Tests sind aktuell erfolgreich.

### 3.3 Arbeitspaket 2 – Text-Injection-Queue

- `core/text_injector.py` ist vorhanden.
- Die Queue besitzt die Zustände:
  - `NEW`
  - `INITIALIZING`
  - `RUNNING`
  - `STOPPING`
  - `STOPPED`
- Der Worker ist ein Nicht-Daemon-Thread.
- Clipboard und `SendInput` werden über `ctypes` und Win32 angesprochen.
- Ein Message-only Owner-Window der Klasse `STATIC` wird verwendet.
- Das Foreground-Window wird erst unmittelbar vor `SendInput` ermittelt.
- Clipboard-Restore ist über die Sequenznummer gegen zwischenzeitliche Fremdänderungen geschützt.
- Die Anzahl von 41 Tests in `tests/test_text_injector.py` stimmt.
- Diese 41 Tests sind aktuell erfolgreich.
- Der reale Notepad-Smoke-Test ist weiterhin offen.

### 3.4 Arbeitspaket 3 – Reinsertion

- `core/reinsertion.py` ist vorhanden.
- `TranscriptReinsertionService` bietet:
  - `reinsert_last()`
  - `reinsert_entry(entry_id)`
  - `get_recent_entries(limit=None)`
- Reinsertion erzeugt keinen neuen `HistoryEntry`.
- Queue-Ablehnung und Enqueue-Exception werden mit den beschriebenen Statuswerten behandelt.
- Die Anzahl von 26 Tests in `tests/test_reinsertion.py` stimmt.
- Diese 26 Tests sind aktuell erfolgreich.

### 3.5 Noch fehlende Integration

- `app.py` instanziiert aktuell weder `TranscriptHistoryManager` noch `TextInjectionQueue` noch `TranscriptReinsertionService`.
- Finale Events werden aktuell nur auf der Konsole ausgegeben.
- Es existiert noch keine PySide6-UI-Implementierung; `ui/` enthält nur `__init__.py`.
- Globaler Hotkey, Tray, Overlay und Single-Instance-Guard sind noch nicht implementiert.
- Arbeitspaket 4 ist damit tatsächlich der nächste reguläre Integrationsschritt.

---

## 4. Kritische Widersprüche und sachlich falsche Aussagen

### K-01 – Die Übergabe kann nicht der alleinstehende Einstiegspunkt sein

**Fundstelle in der geprüften Übergabe:** Zeile 13

Die Übergabe behauptet, als alleinstehender Einstiegspunkt für die weitere Arbeit dienen zu können.

Das widerspricht `AGENTS.md`:

- Dort ist eine verbindliche Quellenhierarchie festgelegt.
- Vor einer ersten Codeänderung müssen unter anderem `AGENTS.md`, `ÜBERGABE.md`, `task.md`, die Roadmap, sämtliche Serverdokumente, der gesamte Core, `app.py`, alle Tests, `config.yaml` und `requirements.txt` gelesen werden.
- Für Protokollfragen sind ausschließlich die Serverdokumente maßgeblich.
- Für Zielarchitektur und gewünschtes Verhalten ist die Roadmap maßgeblich.

**Bewertung:** kritisch

**Empfohlene Korrektur:** Die Übergabe darf als zentraler Orientierungs- und Index-Einstiegspunkt bezeichnet werden, aber nicht als Ersatz für die verbindlichen Originalquellen. Die Quellenhierarchie aus `AGENTS.md` sollte ausdrücklich und vollständig übernommen werden.

### K-02 – Falsche Beschreibung des Audioformats

**Fundstellen in der geprüften Übergabe:** Zeilen 132 bis 134

Die Übergabe behauptet:

- Verarbeitung auf 16 kHz, Mono, `float32`
- Resampling und Konvertierung in PCM16

Der tatsächliche Code arbeitet anders:

- `config.yaml` und `core/config.py` konfigurieren `dtype: int16`.
- `core/audio_capture.py` öffnet `sounddevice.InputStream` direkt mit diesem `int16`-Datentyp.
- Der Callback übernimmt die Bytes direkt über `indata.tobytes()`.
- Eine lokale Float32-Verarbeitung ist nicht vorhanden.
- Ein lokales Resampling ist ebenfalls nicht vorhanden.
- Wenn das Audiogerät 16 kHz nicht unterstützt, wird die Geräte-Standardrate verwendet und an den Server übertragen.
- Laut Codekommentar und Serverprotokoll resampelt in diesem Fall der Server.

**Bewertung:** kritisch

**Empfohlene Korrektur:** Den Ist-Stand so beschreiben:

> Audio wird bevorzugt mit 16 kHz, Mono und PCM16 (`int16`) aufgenommen. Unterstützt das Gerät 16 kHz nicht, verwendet der Client die Standardrate des Geräts und übermittelt diese im Paket; das Resampling auf 16 kHz erfolgt serverseitig.

### K-03 – Verweise auf nicht vorhandene Core-Dateien

**Fundstellen:**

- geprüfte Übergabe, Zeile 390: `core/stt_client.py`
- `task.md`, Zeile 6: `core/audio_processor.py`
- `task.md`, Zeile 7: `core/stt_client.py`

Diese Dateien existieren im aktuellen Projekt nicht.

Die tatsächlichen Komponenten heißen:

- `core/audio_capture.py`
- `core/stt_session.py`

**Bewertung:** kritisch

**Empfohlene Korrektur:** Alle Verweise auf die nicht vorhandenen Dateien ersetzen. In `task.md` müssen außerdem die mit diesen Namen verbundenen Implementierungsbehauptungen korrigiert werden.

### K-04 – „Gesamter Teststand“ ist als Gesamtprojekt-Teststand missverständlich

**Fundstellen in der geprüften Übergabe:** Abschnitt 10, insbesondere Zeilen 308 bis 330

Die Zahl 96 ist korrekt und aktuell reproduzierbar. Sie umfasst jedoch ausschließlich:

- 29 Tests für `core/history.py`
- 41 Tests für `core/text_injector.py`
- 26 Tests für `core/reinsertion.py`

Nicht durch diese Suite getestet werden:

- `app.py`
- `core/audio_capture.py`
- `core/stt_session.py`
- der Eventpfad vom WebSocket-Final bis zur Historie
- der Eventpfad von der Historie bis zur Injection-Queue
- Reconnect mit anschließendem Wiederanlauf des Streamings
- Mikrofonaufnahme
- reales Clipboard und reales `SendInput`
- PySide6-, Tray-, Overlay- und Hotkey-Funktionen

`tests/test_connection.py` enthält keine `unittest.TestCase`-Tests und wird durch den dokumentierten `unittest discover`-Lauf nicht als Testfall ausgeführt.

**Bewertung:** kritisch

**Empfohlene Korrektur:** Abschnitt 10 in „Automatisierter Teststand der Arbeitspakete 1 bis 3“ umbenennen und die nicht abgedeckten Komponenten ausdrücklich nennen.

### K-05 – Der „Live-Verbindungstest“ ist kein Live-End-to-End-Test

**Fundstelle in der geprüften Übergabe:** Zeile 330

`tests/test_connection.py` prüft:

- den HTTP-Health-Endpunkt,
- `hello`,
- das nächste erwartete Event als `ready`,
- `ping`/`pong`.

Der Test sendet nicht:

- `{ "type": "start" }`,
- Audiopakete,
- `{ "type": "stop" }`.

Er wartet weder auf `realtime` noch auf `final`. Er prüft auch kein Mikrofon.

Die Aussage, ein Live-Verbindungstest sei historisch erfolgreich gewesen, kann stimmen. Sie darf aber nicht als Verifikation des vollständigen Headless-Audio- und Transkriptionspfads dargestellt werden.

**Bewertung:** kritisch

**Empfohlene Korrektur:** Den Test als „historisch erfolgreicher Health-/WebSocket-Handshake-/Ping-Test“ bezeichnen. Mikrofon-, Audio- und Final-Event-End-to-End-Test getrennt als offen ausweisen.

### K-06 – Transport-Reconnect und vollständige Selbstheilung werden nicht sauber getrennt

Die Übergabe nennt einerseits eine reconnect-fähige WebSocket-Verbindung als vorhanden und führt andererseits die automatische Wiederherstellung der Serververbindung in Arbeitspaket 5 als offen.

Der Code zeigt einen Zwischenstand:

- `STTSession.run()` besitzt einen Reconnect-Loop mit Backoff und Jitter.
- Bei einer neuen Verbindung wird `_streaming` auf `False` gesetzt.
- `app.py` startet den Stream über `_auto_start_when_ready()` nur einmal.
- Diese Coroutine kehrt nach dem ersten `send_start()` zurück.
- Nach einem späteren Reconnect gibt es im aktuellen `app.py` keinen erneuten `send_start()`-Aufruf.

Damit kann sich der WebSocket-Transport erneut verbinden, der vollständige Diktierbetrieb wird danach aber nicht automatisch wieder aufgenommen.

**Bewertung:** kritisch

**Empfohlene Korrektur:** Den Stand explizit in zwei Ebenen dokumentieren:

- **Implementiert:** Transport-Reconnect des `STTSession`-Objekts.
- **Nicht implementiert/verifiziert:** automatische Wiederaufnahme von Mikrofon-Streaming und `start`-Handshake nach Reconnect sowie die vollständige modalfreie Selbstheilung.

### K-07 – Zielverhalten wird teilweise wie bereits implementiertes Verhalten formuliert

**Fundstellen in der geprüften Übergabe:** insbesondere Abschnitt 3.3, Zeilen 61 bis 65

Die Aussagen

- jeder finale Text werde zuerst in die Historie übernommen,
- erst danach werde ein Einfügeversuch gestartet,

sind als Zielarchitektur korrekt. Sie sind im aktuellen Anwendungsablauf aber noch nicht umgesetzt, weil `app.py` die drei Komponenten nicht instanziiert und finale Events nur ausgibt.

**Bewertung:** kritisch

**Empfohlene Korrektur:** Jede solche Aussage eindeutig als „verbindliches Ziel für Arbeitspaket 4“ kennzeichnen. Den aktuellen Ist-Pfad daneben nennen:

```text
final -> STTSession Reducer -> app.py on_text -> Konsolenausgabe
```

Der Zielpfad ist:

```text
final -> deduplizierte Historie -> Injection-Queue -> Attempt-Dokumentation
```

### K-08 – Quellenbasis der Übergabe ist für den erhobenen Anspruch unvollständig

**Fundstellen in der geprüften Übergabe:** Zeilen 547 bis 560

Als Quellenbasis werden unter anderem nur `core/reinsertion.py`, `tests/test_reinsertion.py` und das Server-README genannt. Für Aussagen über den gesamten Headless-Core, Audio, Reconnect, Konfiguration und alle Tests fehlen in der eigenen Quellenliste insbesondere:

- `AGENTS.md`
- `app.py`
- `core/audio_capture.py`
- `core/stt_session.py`
- `core/config.py`
- `core/history.py`
- `core/text_injector.py`
- `tests/test_history.py`
- `tests/test_text_injector.py`
- `tests/test_connection.py`
- `config.yaml`
- `requirements.txt`
- die einzelnen maßgeblichen Serverprotokolldokumente

**Bewertung:** kritisch

**Empfohlene Korrektur:** Die Quellenbasis vollständig an die Quellenhierarchie aus `AGENTS.md` angleichen.

---

## 5. Wesentliche Unklarheiten und fehlende Abgrenzungen

### U-01 – Python 3.12 fehlt als verbindliche Entscheidung

Die geprüfte Übergabe nennt nur Python als Implementierungssprache. Laut `AGENTS.md` ist jedoch **Python 3.12** verbindlich.

Die vorhandene Projektumgebung verwendet:

```text
Python 3.12.10
```

**Empfehlung:** Python 3.12 und die ausschließliche Verwendung von `.\venv\Scripts\python.exe` ausdrücklich aufnehmen.

### U-02 – Verbindliches Threading-Modell ist nicht vollständig festgehalten

Laut `AGENTS.md` gilt:

- Qt läuft im Main Thread.
- Der asyncio-Core läuft in einem separaten Thread.
- Der globale Hotkey wird nativ über Win32 umgesetzt.

Die Übergabe sagt nur, dass im Qt-Main-Thread keine blockierenden asyncio-Aufrufe laufen dürfen. Das ist schwächer und lässt offen, ob asyncio wirklich in einem separaten Thread betrieben werden soll.

Der aktuelle Headless-Entry-Point ruft `asyncio.run()` im Main Thread auf. Das ist für den gegenwärtigen Headless-Stand nachvollziehbar, muss aber vor der UI-Integration in die festgelegte Zielarchitektur überführt werden.

**Empfehlung:** Ist- und Zielzustand getrennt dokumentieren.

### U-03 – Die AP4-Fragen sind größtenteils bereits beantwortet

Die Übergabe listet in Abschnitt 12 mehrere Fragen als vor Beginn von AP4 noch zu klären. Der vorhandene Code beantwortet bereits:

- `realtime` und `final` treffen in `STTSession._message_loop()` ein.
- Die Verarbeitung läuft über `STTSession._apply_event()` und den Reducer `reduce()`.
- `on_text(segment_id, text, is_final)` wird nur bei einem neuen oder geänderten Segment ausgelöst.
- `on_event(event_type, event)` erhält jedes Event.
- `sessionId` liegt in `ClientState.session_id` und im Originalevent.
- `segmentId` liegt im Originalevent und im `TranscriptSegment`.
- `app.py` startet aktuell `STTSession` und `AudioCapture`.
- Historie, Queue und Reinsertion werden aktuell nirgends im Anwendungs-Entry-Point gestartet.
- Eine UI-neutrale Controller-Klasse existiert noch nicht.

**Empfehlung:** Diese Fragen durch einen Abschnitt „Tatsächlicher aktueller Eventpfad und vorhandene Integrationspunkte“ ersetzen. Nur echte Designentscheidungen sollten offen bleiben.

### U-04 – Deduplizierung und „exakt einmal enqueuen“ brauchen eine explizite AP4-Regel

`TranscriptHistoryManager.add_entry()` verhält sich bei Duplikaten unterschiedlich:

- Ist der Eintrag noch in Memory oder SQLite vorhanden, wird der bestehende `HistoryEntry` zurückgegeben.
- Ist er nur noch im internen Deduplizierungs-Cache bekannt, aber weder in Memory noch SQLite vorhanden, wird `None` zurückgegeben.

Allein aus einem zurückgegebenen `HistoryEntry` lässt sich daher nicht erkennen, ob er gerade neu erstellt oder als Duplikat wiedergefunden wurde.

`STTSession.on_text` unterdrückt identische Wiederholungen auf Reducer-Ebene, während `on_event` jedes `final` weitergibt. Die Wahl des Integrationspunkts beeinflusst somit die Exakt-einmal-Semantik.

**Empfehlung:** Vor AP4 verbindlich festlegen und testen:

- welcher Callback der Controller nutzt,
- wie ein neues Final von einem bereits verarbeiteten Final unterschieden wird,
- dass ein doppeltes Final nicht erneut enqueued wird,
- dass `sessionId + segmentId` die Deduplizierungsidentität bilden.

### U-05 – Persistenz ist selektiv, nicht „jeder Text dauerhaft lokal gesichert“

Die aktuelle Konfiguration lautet:

```yaml
history:
  memory:
    max_entries: 5
  persistent:
    max_entries: 100
    min_characters: 1000
    store_failed_injections: true
    store_all: false
```

Folgen:

- Jeder neue Eintrag wird zunächst in Memory aufgenommen, sofern die Historie aktiviert ist.
- Kurze, erfolgreich eingefügte Transkripte werden standardmäßig nicht sofort persistent gespeichert.
- Memory hält standardmäßig nur fünf Einträge.
- Kurze Einträge werden persistent, wenn ein `failed`- oder `skipped`-Attempt vorliegt.

Damit ist „lokal sichern“ als In-Memory-Sicherung richtig, als dauerhafte Sicherung jedoch falsch oder zumindest missverständlich. Nach einem Prozessabsturz können kurze, noch nicht fehlgeschlagene oder bereits erfolgreich eingefügte Einträge verloren sein.

**Empfehlung:** „In Historie aufnehmen“ und „persistent in SQLite speichern“ konsequent unterscheiden. Außerdem klar benennen, ob das Produktziel wirkliche Crash-Sicherheit für jedes Final verlangt. Falls ja, widerspricht die aktuelle Default-Konfiguration diesem Ziel.

### U-06 – Reinsertion-Fehlersemantik ist mit dem realen History-Manager nur eingeschränkt erreichbar

Die Übergabe beschreibt `FAILED` mit `reason="history_query_failed"` bei History-Lesefehlern.

`TranscriptReinsertionService` kann diesen Status liefern, wenn seine History-Methoden Exceptions auslösen. Die reale Implementierung `TranscriptHistoryManager.get_persistent_entries()` fängt SQLite-Ausnahmen jedoch intern ab und gibt eine leere Liste zurück. Ist SQLite bereits deaktiviert, wird ebenfalls eine leere Liste zurückgegeben.

Dadurch kann der Reinsertion-Service bei einem realen SQLite-Lesefehler „leer“ beziehungsweise „nicht gefunden“ sehen, ohne den Fehler als `history_query_failed` unterscheiden zu können. Die Exception-Semantik wird vor allem durch Test-Doubles geprüft, nicht durch die reale Manager-Integration im Fehlerfall.

**Empfehlung:** In der Übergabe als Einschränkung dokumentieren oder die Schnittstellenentscheidung in einem später ausdrücklich beauftragten Arbeitspaket korrigieren. Im aktuellen Prüfauftrag wurde kein Code geändert.

### U-07 – Hotkey-Belegung ist widersprüchlich

- `docs/IMPLEMENTATION_ROADMAP.md` nennt `Ctrl+Alt+Space`.
- `config.yaml` und `core/config.py` nennen `<ctrl>+<shift>+space`.
- Der Kommentar in `core/config.py` bezeichnet dieses Format noch als „pynput format“, obwohl `pynput` ausdrücklich ausgeschlossen ist.

Die geprüfte Übergabe nennt keine konkrete Standardbelegung und verdeckt damit den vorhandenen Widerspruch.

**Empfehlung:** Vor der Hotkey-Implementierung eine verbindliche Standardbelegung festlegen und das Konfigurationsformat an Win32 `RegisterHotKey` ausrichten.

### U-08 – Mehrere Konfigurationsfelder sind noch nicht wirksam

In `config.yaml` und `core/config.py` existieren:

- `text_injection.final_strategy`
- `text_injection.append_space`
- `text_injection.warn_elevated`

`core/text_injector.py` wertet diese Felder aktuell nicht aus. Es verwendet stets Clipboard plus `Ctrl+V`, übergibt `job.text` unverändert und besitzt keine Elevated-Window-Warnlogik.

**Empfehlung:** Die Übergabe sollte diese Werte als derzeitige Platzhalter beziehungsweise noch nicht implementierte Konfigurationsoptionen kennzeichnen. Insbesondere `append_space: true` darf nicht den Eindruck erwecken, dass tatsächlich ein Leerzeichen angefügt wird.

### U-09 – Testdatenbanken liegen im Projektwurzelverzeichnis

Vorhanden sind:

- `config_path.db`
- `param_path.db`

Beide Dateien sind SQLite-Datenbanken mit jeweils 24.576 Byte und stammen sehr wahrscheinlich aus `test_database_path_priorities()` in `tests/test_history.py`. Dieser Test verwendet relative Pfade im aktuellen Arbeitsverzeichnis und räumt diese beiden Dateien nicht auf.

Das widerspricht `AGENTS.md`:

- Die SQLite-Historie soll im lokalen Anwendungsdatenverzeichnis liegen.
- Laufzeitdaten und lokale Datenbanken dürfen nicht als Projektdateien behandelt werden.

**Empfehlung:** In einem separaten, ausdrücklich beauftragten Bereinigungs-/Testfix-Arbeitspaket:

- Test ausschließlich mit Pfaden unter `self.temp_dir` ausführen,
- bestehende Artefakte kontrolliert entfernen,
- Repository-/Cleanup-Regeln für `*.db`, `__pycache__` und `.pytest_cache` klären.

Im Rahmen dieser Prüfung wurden die Dateien nicht verändert oder gelöscht.

### U-10 – Root-README widerspricht den verbindlichen Betriebsregeln

`README.md` nennt:

- Python 3.10+
- `pip install -r requirements.txt`
- `python app.py`

Verbindlich sind laut `AGENTS.md`:

- Python 3.12
- ausschließlich die vorhandene Projektumgebung
- `.\venv\Scripts\python.exe`

**Empfehlung:** README später an die verbindlichen Regeln angleichen. Bis dahin darf die neue Übergabe den README-Quick-Start nicht ungeprüft übernehmen.

### U-11 – Kein reproduzierbarer Snapshot trotz eigener Hash-Regel

Abschnitt 11 der geprüften Übergabe fordert für künftige Abschlüsse:

- absolute Pfade,
- `LastWriteTime`,
- Dateigröße,
- SHA-256-Hash.

Die Übergabe selbst enthält keinen solchen Snapshot. Außerdem ist das aktuelle Verzeichnis kein Git-Repository. Damit gibt es weder Commit-ID noch Hashmanifest, über das sich der beschriebene Stand eindeutig einem Dateisatz zuordnen lässt.

**Empfehlung:** Der final überarbeitete Übergabestand sollte ein kleines Manifest der maßgeblichen Dateien oder einen separaten Snapshot-Nachweis enthalten.

### U-12 – „Abgenommen“ ist stärker als die übrigen Nachweise

Die geprüfte Übergabe bezeichnet Arbeitspaket 3 als „abgeschlossen und abgenommen“. `task.md`, `ÜBERGABE.md` und die Roadmap belegen „abgeschlossen“, dokumentieren aber keine formale Abnahmehandlung oder abnehmende Person.

**Empfehlung:** Entweder den konkreten Abnahmenachweis ergänzen oder nur „abgeschlossen und automatisiert getestet“ schreiben.

---

## 6. Nicht abgedeckte Code-Risiken, die die Übergabe nennen sollte

Diese Punkte ändern nicht den bestätigten Abschluss der isolierten Arbeitspakete 1 bis 3. Sie relativieren aber die pauschale Aussage eines robusten und verifizierten Headless-Gesamtkerns.

### R-01 – `asyncio.Queue` wird aus einem fremden Thread angesprochen

`AudioCapture` ruft `app.py::_on_audio_packet_from_thread()` aus dem Audio-Processing-Thread auf. Dort wird direkt `asyncio.Queue.put_nowait()` verwendet.

`asyncio.Queue` ist nicht für direkten threadübergreifenden Zugriff ausgelegt. Der Kommentar behauptet zwar eine Bridge zum Event Loop, verwendet aber nicht `loop.call_soon_threadsafe()` oder eine andere explizit thread-sichere Übergabe.

Dieser Pfad wird durch keinen der 96 Tests geprüft.

**Auswirkung:** potenzielle Race Conditions, fehlende Wakeups oder instabiles Verhalten unter Last.

### R-02 – Der Ping-Miss-Zähler prüft nicht zuverlässig ausbleibende Pongs

In `STTSession._ping_loop()`:

- setzt `send_ping()` `ping_started_at` für den gerade neu gesendeten Ping,
- danach wird unmittelbar geprüft, ob `round_trip_ms` noch `None` ist,
- nach dem ersten erfolgreichen Pong bleibt `round_trip_ms` gesetzt,
- vor dem nächsten Ping wird es nicht auf `None` zurückgesetzt.

Nach einem ersten erfolgreichen Pong können spätere ausbleibende Pongs dadurch unentdeckt bleiben. Außerdem wird der erste Miss geprüft, bevor eine reguläre Pong-Wartefrist abgelaufen ist.

Dieser Pfad wird durch keinen der 96 Tests geprüft.

### R-03 – Reconnect nimmt den Stream nicht erneut auf

Wie unter K-06 beschrieben, reconnectet `STTSession`, aber `app.py` sendet nach dem ersten erfolgreichen Start bei späteren Sessions kein neues `start`.

Dieser Pfad wird durch keinen automatisierten Integrationstest geprüft.

### R-04 – Der vorhandene Live-Test ist protokollseitig schmal

`tests/test_connection.py` erwartet nach `hello` direkt das nächste Event und behandelt dieses als `ready`. Die Serverdokumentation erlaubt während der Startphase zusätzliche Events und beschreibt zwei Ready-Varianten. Der eigentliche `STTSession._wait_for_ready()`-Code ist toleranter als der Test.

Der Test ist deshalb eher ein Smoke-Test für einen günstigen Normalfall als ein vollständiger Protokoll-Contract-Test.

---

## 7. Präziser tatsächlicher Projektstand

Der derzeit belastbarste Kurzstand lautet:

### Implementiert

- Headless-Entry-Point mit:
  - `STTSession`
  - `AudioCapture`
  - Konsolenausgabe von Realtime- und Finaltext
- WebSocket-Protokollgrundlagen:
  - `hello`
  - `ready`
  - `start`
  - binäre PCM16-Audiopakete
  - Event-Reducer
  - Transport-Reconnect-Loop
  - Anwendungsping
- Arbeitspaket 1:
  - RAM-/SQLite-Historienkomponente
- Arbeitspaket 2:
  - serialisierte Win32 Text-Injection-Queue
- Arbeitspaket 3:
  - UI-neutraler Reinsertion-Service

### Automatisiert aktuell verifiziert

- 29 History-Tests
- 41 Text-Injection-Tests mit Fake-Backend
- 26 Reinsertion-Tests
- insgesamt 96 Tests, aktuell erfolgreich

### Historisch dokumentiert, in dieser Prüfung nicht erneut live verifiziert

- Health-Endpunkt erreichbar
- WebSocket-Handshake gegen `stt.voice.marcosudau.com`
- Ping/Pong gegen den realen Server

### Nicht implementiert oder nicht integriert

- Controller zwischen Final-Event, Historie und Injection-Queue
- Instanziierung von Historie, Queue und Reinsertion in `app.py`
- automatische Wiederaufnahme des Streamings nach Reconnect
- PySide6-Anwendung und Qt-Signalbrücke
- asyncio-Core in separatem Thread neben Qt
- Tray
- Overlay
- native globale Hotkeys
- Single-Instance-Guard
- Hot-Plug-Wiederherstellung des Mikrofons
- Verlaufsauswahl im UI

### Weiterhin praktisch nicht verifiziert

- reales Mikrofon bis zum `final`-Event
- reales Einfügen in Notepad
- Clipboard-Restore mit echten Fremdanwendungen
- vollständiger Ablauf Final -> Historie -> Queue -> Zielanwendung
- Reinsert-last über Hotkey
- Reinsert über Tray
- Netzwerkverlust mit vollständiger Wiederaufnahme des Diktierbetriebs
- Mikrofon entfernen und wieder anschließen

---

## 8. Empfohlene Überarbeitung der eigentlichen Übergabe

Vor Verwendung als verbindliche Projektübergabe sollten mindestens folgende Änderungen vorgenommen werden:

1. Den Anspruch „alleinstehender Einstiegspunkt“ durch „zentraler Orientierungs- und Quellenindex“ ersetzen.
2. Die verbindliche Quellenhierarchie aus `AGENTS.md` aufnehmen.
3. Python 3.12, die Projekt-Venv und das feste Qt-/asyncio-Threading-Modell ausdrücklich nennen.
4. Den Audio-Ist-Stand auf PCM16-Direktaufnahme und serverseitiges Fallback-Resampling korrigieren.
5. Nicht vorhandene Dateien durch `core/audio_capture.py` und `core/stt_session.py` ersetzen.
6. Die 96 Tests klar als Tests der Arbeitspakete 1 bis 3 kennzeichnen.
7. Den Live-Test exakt als Health-/Handshake-/Ping-Smoke-Test beschreiben.
8. Transport-Reconnect und vollständige Streaming-Selbstheilung getrennt ausweisen.
9. Ist-Verhalten und Zielverhalten konsequent in getrennten Abschnitten darstellen.
10. Den aktuellen Eventpfad und die bereits bekannten AP4-Integrationspunkte dokumentieren.
11. Für AP4 die Exakt-einmal-Regel bei doppelten Final-Events präzisieren.
12. In-Memory-Historie und selektive SQLite-Persistenz sprachlich trennen.
13. Die Einschränkung der realen Reinsertion-Fehlererkennung dokumentieren.
14. Hotkey-Belegung und Konfigurationsformat vereinheitlichen.
15. Noch unwirksame Konfigurationsfelder als Platzhalter markieren.
16. Die Datenbankartefakte und veraltete README in einer Liste bekannter Repository-Unstimmigkeiten nennen.
17. Einen reproduzierbaren Dateisnapshot oder ein Hashmanifest ergänzen.
18. Die nicht durch Tests abgedeckten Thread-, Ping- und Reconnect-Risiken als bekannte technische Risiken aufnehmen.

---

## 9. Zusammenfassung für die Projektleitung

Das Projektziel ist grundsätzlich klar: Ein dauerhafter Windows-Desktop-Client soll Mikrofon-Audio an den RealtimeSTT-Server senden, nur finale Transkripte sicher historisieren und anschließend in die aktuell fokussierte Anwendung einfügen. Realtime-Texte dienen ausschließlich der Anzeige. PySide6, native Win32-Hotkeys, Clipboard/`SendInput`, SQLite sowie die Trennung von Qt-Main-Thread und asyncio-Core sind verbindlich.

Der reale Entwicklungsstand ist: Drei isolierte Kernbausteine – Historie, Text-Injection-Queue und Reinsertion – sind implementiert und mit aktuell erfolgreich reproduzierbaren 96 Tests abgesichert. Sie sind jedoch noch nicht mit dem vorhandenen WebSocket-/Audio-Entry-Point verbunden. Der aktuelle Headless-Client gibt Transkripte nur auf der Konsole aus. Deshalb ist Arbeitspaket 4 tatsächlich der nächste Schritt.

Die Übergabe überschätzt derzeit den Phase-1-Audiopfad, die Breite der Testabdeckung und den Grad der Reconnect-Selbstheilung. Außerdem enthält sie veraltete Dateinamen, lässt verbindliche Architekturdetails aus und vermischt stellenweise Soll- mit Ist-Verhalten. Ohne Korrektur könnte ein nachfolgender Agent falsche Module suchen, unnötig eine lokale Audioverarbeitung voraussetzen, die 96 Tests als Gesamtprojekt-Abdeckung interpretieren oder einen bereits vollständig selbstheilenden Reconnect annehmen.

Empfehlung: Die vorhandene Übergabe nicht unverändert als alleinige Arbeitsgrundlage freigeben. Zuerst die in diesem Bericht als kritisch markierten Punkte korrigieren und danach den Stand mit einem eindeutigen Quellenindex sowie einem reproduzierbaren Dateisnapshot festschreiben.

---

## 10. Änderungsumfang dieser Prüfung

Im Projekt wurde ausschließlich diese Prüfberichtsdatei neu angelegt:

`docs/2026-07-24_PROJEKT_UEBERGABE/PRUEFBERICHT_2026-07-24.md`

Die geprüfte Übergabedatei, Quellcode, Tests, Konfigurationen und sonstigen Projektdateien wurden nicht verändert.
