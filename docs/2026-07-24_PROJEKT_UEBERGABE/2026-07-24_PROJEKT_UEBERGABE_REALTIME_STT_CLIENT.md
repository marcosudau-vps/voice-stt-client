# Projektübergabe – RealtimeSTT Windows Desktop Client

> **Stand:** 24. Juli 2026  
> **Projektpfad:** `P:\DockerProjekte\RealtimeSTT_client`  
> **Aktueller Entwicklungsstand:** Arbeitspakete 1 bis 3 abgeschlossen; nächster regulärer Schritt ist Arbeitspaket 4 – Controller-Integration.

---

## 1. Zweck dieses Dokuments

Dieses Dokument fasst den aktuellen Projektstand, die verbindlichen Architekturentscheidungen, die bereits umgesetzten Arbeitspakete, die noch offenen Schritte sowie die für die weitere Entwicklung maßgeblichen Server- und Client-Fakten in einer einzigen Übergabe zusammen.

Es soll als alleinstehender Einstiegspunkt für die weitere Arbeit mit einem Entwicklungsagenten dienen. Frühere Zwischenstände, alte Planungsvarianten und einzelne Chatverläufe sollen für den Einstieg nicht mehr zusammengesucht werden müssen.

---

## 2. Ziel des Projekts

Entwickelt wird ein robuster Windows-Desktop-Client für den vorhandenen RealtimeSTT-Server.

Der Client soll im Hintergrund laufen und auf Minimalbasis zunächst zuverlässig folgende Aufgaben erfüllen:

1. Verbindung zum STT-Server herstellen und aufrechterhalten.
2. Mikrofon-Audio erfassen und per WebSocket an den Server übertragen.
3. Realtime- und finale Transkriptionsereignisse empfangen und korrekt verarbeiten.
4. Die Aufnahme über einen globalen Hotkey steuern.
5. Finale Transkriptionen zuerst lokal sichern und anschließend über die Zwischenablage in die aktuell fokussierte Anwendung einfügen.
6. Fehlgeschlagene oder verpasste Einfügungen über eine lokale Historie erneut verfügbar machen.
7. Alle Komponenten eventgetrieben und thread-sicher miteinander verbinden.
8. Erst nach einem stabilen Minimalbetrieb um Tray-Icon, Overlay, Komfortfunktionen und weitere UI-Elemente erweitern.

Der Schwerpunkt liegt auf Zuverlässigkeit, sauberer Zustandsführung und Datenverlustvermeidung. Eine umfangreiche Benutzeroberfläche ist ausdrücklich nicht der erste Meilenstein.

---

## 3. Verbindliche Grundentscheidungen

### 3.1 Technologiestack

- **Python** bleibt die Implementierungssprache.
- **PySide6** ist das verbindliche UI-Framework.
- Der Core bleibt so lange wie möglich frei von PySide6-Abhängigkeiten.
- Globale Hotkeys werden über native Windows-Funktionen umgesetzt, insbesondere `RegisterHotKey`.
- Clipboard- und Tastaturinjektion werden über native Win32-APIs und `ctypes` umgesetzt.
- `pystray`, `tkinter` und `pynput` werden nicht als Ersatzarchitektur eingeführt.
- SQLite bleibt die persistente lokale Historie.
- Der bestehende WebSocket-, Audio- und Reconnect-Core wird nicht grundlegend ersetzt.

### 3.2 Fokus- und Einfügesemantik

- Es wird **kein Zielfenster beim Start der Aufnahme festgelegt**.
- Unmittelbar vor dem tatsächlichen Paste-Vorgang wird das dann aktuelle Foreground-Window ermittelt.
- Der Benutzer darf während der Aufnahme oder kurz vor dem finalen Transkript in eine andere Anwendung wechseln.
- Der Client aktiviert kein früheres Fenster automatisch und erzwingt keinen Fokuswechsel.
- Finale Texte werden über Clipboard und simuliertes `Ctrl+V` eingefügt.
- Realtime-Texte werden nicht in Anwendungen eingefügt; sie dienen nur dem visuellen Feedback.
- Der Client behauptet nicht, den tatsächlichen Einfügeerfolg im Zielprogramm sicher erkannt zu haben. Er kann nur dokumentieren, ob der technische Paste-Befehl gesendet, abgelehnt, übersprungen oder durch einen technischen Fehler verhindert wurde.

### 3.3 Datenverlustschutz

- Jeder finale Text wird zuerst in die Historie übernommen.
- Erst danach wird ein Einfügeversuch gestartet.
- Ein fehlgeschlagener oder nicht eindeutig bestätigbarer Paste-Vorgang darf nicht zum Verlust der Transkription führen.
- Wiederholtes Einfügen erzeugt keinen neuen Historieneintrag, sondern einen weiteren Versuch am vorhandenen Eintrag.
- Persistente Historiedaten liegen im lokalen Anwendungsdatenverzeichnis des Benutzers und nicht im Projektordner.

### 3.4 Entwicklungsreihenfolge

Arbeitspakete werden strikt nacheinander umgesetzt.

Ein Arbeitspaket gilt erst als abgeschlossen, wenn:

- der Code implementiert ist,
- passende automatisierte Tests vorhanden sind,
- alle relevanten Tests erfolgreich laufen,
- Task-Tracker, Roadmap und Übergabedokumentation aktualisiert wurden,
- und die tatsächlich geschriebenen Dateien auf der Festplatte verifiziert wurden.

Mit dem folgenden Arbeitspaket wird nicht begonnen, bevor der aktuelle Schritt abgenommen ist.

---

## 4. Verbindliche Serveradressen

Die aktuell korrekten Adressen lauten:

| Zweck | Adresse |
|---|---|
| WebSocket-Transkription | `wss://stt.voice.marcosudau.com/ws/transcribe` |
| Health-Endpunkt | `https://stt.voice.marcosudau.com/health` |
| Server-Weboberfläche | `https://voice.marcosudau.com` |

Ein früher in einem Planungsdokument genannter Host `voice.voice.marcosudau.com` ist überholt und darf nicht mehr verwendet werden.

Der ältere OpenAI-kompatible STT-Endpunkt unter `stt.marcosudau.com` gehört nicht zur primären Realtime-WebSocket-Integration dieses Clients.

---

## 5. Maßgebliche Serverprotokoll-Fakten

Das Server-Dokumentationspaket wurde aus dem implementierten Servercode abgeleitet. Für die Client-Entwicklung sind insbesondere folgende Regeln bindend:

1. `hello` bedeutet, dass die Verbindung zugelassen wurde.
2. `ready` bedeutet, dass die Session betriebsbereit ist.
3. Audio darf erst nach erfolgreichem `ready` gesendet werden.
4. Vor dem ersten Audiopaket muss der Client den JSON-Befehl `{ "type": "start" }` senden.
5. Clientbefehle und Serverevents werden als JSON-Textframes übertragen.
6. Audio wird binär übertragen.
7. Realtime-Ergebnisse sind revidierbar. Ein neues `realtime`-Event desselben `segmentId` ersetzt den bisherigen Zwischenstand.
8. Erst ein `final`-Event ist das abgeschlossene Ergebnis.
9. Eine neue WebSocket-Verbindung erzeugt eine neue Session und damit eine neue `sessionId`.
10. Nach einem Reconnect werden alte Segmente nicht in der neuen Session fortgeführt.
11. Unbekannte zusätzliche Felder in Serverevents müssen tolerant ignoriert werden.
12. Laufzeiteinstellungen aus `hello.settings`, `ready.settings` beziehungsweise der Runtime-Konfiguration sind maßgeblich; ein eingechecktes Serverprofil ist kein unveränderlicher Protokollvertrag.

Für Arbeitspaket 4 sind besonders relevant:

- Server-Events – Kurzreferenz
- Server-Events – Katalog und Chronologie
- Client-Zustandsmodell

---

## 6. Aktueller Implementierungsstand

### 6.1 Bestehender Headless-Core

Der grundlegende Client-Core ist vorhanden und wurde bereits gegen den realen Server getestet.

Vorhanden beziehungsweise verifiziert sind:

- Audioaufnahme über `sounddevice`
- Verarbeitung auf 16 kHz, Mono, `float32`
- Resampling und Konvertierung in PCM16
- Reconnect-fähige WebSocket-Verbindung
- Serverevent-Verarbeitung und Zustandsmodell
- Logging und Konfiguration
- erfolgreicher Headless-Verbindungstest gegen `stt.voice.marcosudau.com`

Die konkrete Verdrahtung des vorhandenen WebSocket-/Session-Cores mit Historie und Injection-Queue ist noch nicht erfolgt. Genau das ist Gegenstand von Arbeitspaket 4.

---

## 7. Arbeitspaket 1 – Transkript-Historie

**Status: abgeschlossen**

### Implementierte Komponente

`core/history.py`

### Umgesetzte Aufgaben

- Aufnahme finaler Transkriptionen
- eindeutige interne Entry-ID
- Speicherung von `session_id` und `segment_id`
- Deduplizierung über Session und Segment
- Zeitstempel und Textlänge
- In-Memory-Historie
- optionale SQLite-Persistenz
- append-only Einfügeversuche
- Bereinigung über konfigurierbare Grenzen
- Datenbankzugriffe über kurzlebige Verbindungen
- defensive Fehlerbehandlung bei SQLite-Problemen

### Zentrale Semantik

- Neue Final-Texte erscheinen sofort in der In-Memory-Historie.
- Doppelte Final-Events derselben Session und desselben Segments erzeugen keinen zweiten Eintrag.
- SQLite-Fehler dürfen den übrigen Client nicht beenden.
- `max_entries: 0` bedeutet unbegrenzt.
- `retention_days: 0` bedeutet keine altersbasierte Löschung.
- Bereinigung erfolgt erst nach erfolgreicher Speicherung des neuen Eintrags.
- Einträge können abhängig von Textlänge, Fehlversuchen und Konfiguration persistent gespeichert werden.

### Teststand

- **29 Tests erfolgreich**

---

## 8. Arbeitspaket 2 – Text-Injection-Queue

**Status: abgeschlossen**

### Implementierte Komponente

`core/text_injector.py`

### Umgesetzte Aufgaben

- thread-sichere FIFO-Queue
- genau ein aktiver Einfügeversuch gleichzeitig
- defensive Kopie der zu verarbeitenden Daten
- eigener Worker-Thread
- Win32-Clipboard-Integration
- `SendInput` für `Ctrl+V`
- Ermittlung des Foreground-Window unmittelbar vor dem Paste-Vorgang
- optionales Clipboard-Backup und Restore
- Schutz über Clipboard-Sequenznummer
- begrenzte Wiederholungsversuche bei gesperrtem Clipboard
- Protokollierung genau eines Versuchsergebnisses pro Queue-Job
- fail-closed Initialisierung des Clipboard-Owner-Windows

### Queue-Lifecycle

`NEW -> INITIALIZING -> RUNNING -> STOPPING -> STOPPED`

Weitere Festlegungen:

- Der Worker ist kein Daemon-Thread.
- Nach `STOPPED` erfolgt kein unbemerktes Neustarten.
- `stop()` beendet die Queue geordnet über Sentinel und `join()`.
- Die UI darf die Queue später ausschließlich über öffentliche Methoden ansprechen.

### Clipboard-Semantik

- Bei deaktivierter Wiederherstellung bleibt der Transkriptionstext im Clipboard.
- Bei aktivierter Wiederherstellung wird nur ein unterstützter und ausreichend kleiner Inhalt gesichert.
- Ein Restore erfolgt nur, wenn keine andere Anwendung das Clipboard zwischenzeitlich verändert hat.
- Ein Restore-Fehler macht einen bereits gesendeten Paste-Befehl nicht nachträglich zu einem fehlgeschlagenen Paste-Versuch.

### Teststand

- **41 Tests erfolgreich**

### Noch offene manuelle Prüfung

Der reale Notepad-Smoke-Test ist weiterhin offen:

```powershell
.\venv\Scripts\python.exe tests/manual_test_text_injector.py
```

---

## 9. Arbeitspaket 3 – Erneutes Einfügen

**Status: abgeschlossen und abgenommen**

### Implementierte Komponente

`core/reinsertion.py`

### Öffentliche Schnittstelle

`TranscriptReinsertionService`

- `reinsert_last()`
- `reinsert_entry(entry_id)`
- `get_recent_entries(limit=None)`

### Umgesetzte Semantik

#### `reinsert_last()`

- Memory-first Auswahl
- SQLite nur als Fallback, wenn Memory leer oder nicht lesbar ist
- Auswahl des jüngsten Eintrags über `(timestamp, id)`
- bei vollständig leerem, fehlerfrei gelesenem Verlauf: `EMPTY_HISTORY`
- bei Memory- oder Persistenzfehler ohne auflösbaren Eintrag: `FAILED` mit `reason="history_query_failed"`

#### `reinsert_entry(entry_id)`

- Memory-first Suche
- SQLite-Fallback nur, wenn der Eintrag im Memory nicht gefunden wurde oder Memory nicht lesbar war
- `ENTRY_NOT_FOUND` nur dann, wenn beide Quellen fehlerfrei gelesen wurden und die ID in keiner Quelle existiert
- sobald eine der benötigten Quellen fehlschlägt und kein Eintrag aufgelöst werden kann: `FAILED` mit `reason="history_query_failed"`

#### `get_recent_entries(limit)`

- liest Memory und Persistenz unabhängig best-effort
- dedupliziert nach Entry-ID
- Memory-Version gewinnt bei Duplikaten
- sortiert neueste Einträge zuerst
- liefert ein unveränderliches `tuple`
- gibt defensive Kopien zurück
- unterstützt `None`, `0` und positive Limits
- negative Limits erzeugen `ValueError`

### Queue- und Attempt-Semantik

- Erfolgreicher Queue-Auftrag: `QUEUED`
- gestoppte oder nicht verfügbare Queue: `QUEUE_UNAVAILABLE`
- Queue-Ablehnung erzeugt einen `skipped`-Attempt
- Enqueue-Exception erzeugt einen `failed`-Attempt
- History-Lesefehler vor Auflösung eines Eintrags erzeugen keinen Attempt an einer unbekannten Entry-ID
- Reinsertion erzeugt keinen neuen `HistoryEntry`

### Nebenläufigkeit

Der Service ist gegen parallele Reinsertion-Aufrufe abgesichert. Der Concurrency-Test verwendet fünf Threads und eine `threading.Barrier`.

Geprüft wird:

- kein Thread bleibt nach dem Join aktiv,
- exakt fünf Queue-Aufträge werden erzeugt,
- alle verwenden dieselbe bestehende Entry-ID,
- es entsteht kein zusätzlicher HistoryEntry,
- der Service erzeugt bei erfolgreichen Enqueues keinen eigenen InjectionAttempt.

### Teststand

- **26 Tests erfolgreich**

---

## 10. Gesamter Teststand

| Bereich | Tests |
|---|---:|
| Historie | 29 |
| Text-Injection-Queue | 41 |
| Reinsertion | 26 |
| **Gesamt** | **96** |

Der dokumentierte vollständige Testlauf war erfolgreich:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Ergebnis:

```text
Ran 96 tests
OK
```

Auch der Live-Verbindungstest gegen den realen Server wurde erfolgreich abgeschlossen.

---

## 11. Wichtige Erkenntnis aus dem Antigravity-Dateiproblem

Bei einem Turn zeigte Antigravity die korrekten Änderungen im Review-Diff an, während die Projektdateien auf der Festplatte unverändert blieben.

Die Unterhaltung und die Review-Daten waren im Antigravity-Brain gespeichert. Das interne Brain-Verzeichnis enthielt außerdem Git-Snapshots. Der betroffene Turn konnte schließlich dadurch wiederhergestellt werden, dass der Agent in derselben Unterhaltung erneut angewiesen wurde, den vorherigen Stand zu materialisieren und anschließend die Dateien direkt von der Festplatte zu lesen.

### Verbindliche Sicherheitsmaßnahme für weitere Agent-Turns

Bei Abschluss eines Arbeitspakets soll der Agent künftig:

1. die geänderten Dateien erneut direkt aus `P:\DockerProjekte\RealtimeSTT_client` lesen,
2. für jede relevante Datei den absoluten Pfad ausgeben,
3. `LastWriteTime`, Dateigröße und SHA-256-Hash ausgeben,
4. erst danach die finalen Ergebnisse melden.

Ein sichtbarer Review-Diff oder eine erfolgreiche Tool-Rückmeldung allein gilt nicht als Nachweis, dass die Dateien dauerhaft im Projekt angekommen sind.

---

## 12. Nächster regulärer Schritt – Arbeitspaket 4

**Status: noch offen**

### Ziel

Historie, Text-Injection-Queue und Reinsertion-Service werden mit dem bestehenden WebSocket-/Audio-Core verbunden.

Ein finales Serverevent darf nicht direkt an eine Clipboard-Funktion weitergereicht werden. Der verbindliche Ablauf lautet:

1. `final`-Event empfangen
2. Session- und Segmentidentität aus dem Event übernehmen
3. finalen Text in der Historie speichern beziehungsweise deduplizieren
4. nur den erfolgreich aufgelösten HistoryEntry an die Injection-Queue übergeben
5. Queue-Ergebnis und späteren Attempt am vorhandenen HistoryEntry dokumentieren

Realtime-Events dürfen ausschließlich den aktuellen Zwischenstand beziehungsweise später das Overlay aktualisieren.

### Architekturvorgaben

- Der Core bleibt frei von PySide6.
- Die UI führt keine Datenbankoperationen aus.
- Die UI führt keine direkten WebSocket-Aufrufe aus.
- Core-zu-UI-Kommunikation erfolgt später über Qt-Signale.
- UI-zu-Core-Kommunikation erfolgt über thread-sichere Befehle.
- Im Qt-Main-Thread laufen keine blockierenden asyncio-Aufrufe.
- Der bestehende Reconnect-Mechanismus darf nicht beeinträchtigt werden.
- Final-Events werden exakt einmal verarbeitet.
- Fehler der Historie oder Injection-Queue dürfen die WebSocket-Session nicht beenden.

### Vor Beginn von AP4 noch einzulesende Dateien

Aus dem Client-Projekt:

- `app.py`
- vorhandene WebSocket-/Session-Komponenten, beispielsweise:
  - `core/stt_session.py`
  - `core/stt_client.py`
- `core/config.py`
- `core/history.py`
- `core/text_injector.py`
- vorhandene Tests des App-, Session- oder Event-Cores
- aktuelle Projektstruktur für Projektwurzel, `core\` und `tests\`

Aus dem Server-Dokumentationspaket:

- `03-server-events-kurzreferenz.md`
- `04-server-events-katalog-und-chronologie.md`
- `05-client-zustandsmodell.md`

### Vor AP4 zu klärende Detailfragen

- Wo treffen `realtime`- und `final`-Events aktuell im Client ein?
- Gibt es bereits einen Event-Reducer oder geschieht die Verarbeitung direkt in der Session?
- Welche konkreten Felder liefert das finale Event?
- Wie werden `sessionId` und `segmentId` heute im Client verfügbar gemacht?
- Wo werden Audioaufnahme, WebSocket-Session und Queue gestartet beziehungsweise gestoppt?
- Welche bestehende Klasse soll künftig die Rolle des UI-neutralen Controllers übernehmen?
- Ist für AP4 bereits eine abstrakte Core-Event-Schnittstelle vorgesehen oder muss sie neu eingeführt werden?
- Welche Fehler werden aktuell vom Session-Core abgefangen, und welche dürfen nicht bis zum Reconnect-Loop durchschlagen?

### Abnahmekriterien für AP4

- Ein `final`-Event erzeugt exakt einen deduplizierten Historieneintrag.
- Der HistoryEntry wird vor dem Enqueue-Versuch erstellt.
- Realtime-Events werden nicht in die Injection-Queue gestellt.
- Mehrere Final-Events bleiben in Empfangsreihenfolge.
- Fehler in History oder Injection stoppen weder Session noch Reconnect.
- Start und Stop aller Komponenten sind deterministisch.
- Unit- und Integrations-Tests prüfen den vollständigen Eventpfad.
- Dokumentation und Task-Tracker werden aktualisiert.
- Es wird noch nicht mit AP5 begonnen.

---

## 13. Arbeitspaket 5 – Fehlerverhalten und Selbstheilung

**Status: offen**

### Ziel

Netzwerk- und Mikrofonprobleme werden im Hintergrund behandelt, ohne modale Dialoge und ohne unbeabsichtigtes Beenden der Anwendung.

### Noch umzusetzen

- automatische Wiederherstellung der Serververbindung
- Hot-Plug-Erkennung für Mikrofone
- Wiederöffnung des konfigurierten oder aktuellen Standardmikrofons
- Zustandsgründe für blockierte Benutzeraktionen
- kurze nicht blockierende Hinweise
- keine wiederholten störenden Meldungen ohne Benutzeraktion

### Beispiele für Zustandsmeldungen

- `Server nicht erreichbar – Verbindung wird wiederhergestellt`
- `Kein Mikrofon verfügbar – erneuter Versuch läuft`
- `Keine gespeicherte Transkription vorhanden`

---

## 14. Arbeitspaket 6 – UI-Shell

**Status: offen**

### Geplanter Umfang

- PySide6-`QApplication`
- `QSystemTrayIcon`
- minimales Tray-Menü
- kleines frameless Overlay
- globale Hotkeys über native Win32-Funktionen
- Qt-/asyncio-Integration
- Single-Instance-Guard
- Verlaufsauswahl im Tray
- Auslösen von `reinsert_last()` per Hotkey
- kurze nicht blockierende Statushinweise

### Wichtige Abgrenzung

Die UI wird erst auf den stabilen Core aufgesetzt. Datenbank, WebSocket und Queue bleiben Core-Verantwortung.

---

## 15. Arbeitspaket 7 – Härtung und Polish

**Status: offen**

### Noch umzusetzen

- Reconnect-Stresstests
- wiederholte Mikrofon-Hot-Plug-Tests
- Multi-Monitor- und DPI-Verhalten
- Autostart
- Logging-Review
- Packaging und reproduzierbarer Start
- Prüfung des Verhaltens bei Herunterfahren und Abmelden
- Langzeitbetrieb und Ressourcenverbrauch
- praxisnahe End-to-End-Tests

---

## 16. Noch offene manuelle Prüfungen

Unabhängig von den automatisierten Tests fehlen derzeit noch mindestens:

1. Realer Notepad-Smoke-Test der Textinjektion
2. Praktischer Mikrofon-End-to-End-Test
3. Späterer vollständiger Ablauf:
   - Hotkey drücken
   - Mikrofonaufnahme
   - Audio an Server
   - Realtime-Feedback
   - Final-Event
   - Speicherung in Historie
   - Einfügung in das aktuell fokussierte Fenster
4. Reinsert-last über globalen Hotkey
5. Reinsert über Tray-Verlauf
6. Netzwerkverlust und erfolgreicher Reconnect
7. Entfernen und erneutes Anschließen des Mikrofons

---

## 17. Nicht Bestandteil der aktuellen Minimalphase

Folgende Erweiterungen werden vorerst nicht umgesetzt:

- lokaler STT-Fallback-Server
- Admin-Helper oder Windows-Service
- garantierte Erkennung eines aktiven Textfeldes
- anwendungsspezifische UI-Automation
- geräteübergreifende Historien-Synchronisierung
- umfangreiches History-Fenster
- Live-Einfügung von Realtime-Text
- frei kombinierbare Aufnahme- und Wake-Word-Modi
- umfangreiche UI vor stabilem End-to-End-Core

---

## 18. Empfohlene Arbeitsweise für den nächsten Agenten

1. Zuerst alle für AP4 benötigten Clientdateien und die drei relevanten Serverdokumente lesen.
2. Den bestehenden Eventpfad vollständig beschreiben.
3. Bestehende Architektur beibehalten und nur die kleinste notwendige Controller-Schicht ergänzen.
4. Vor dem Schreiben konkrete Integrationspunkte und Verantwortlichkeiten festlegen.
5. AP4 isoliert umsetzen.
6. Unit- und Integrations-Tests ergänzen.
7. Gesamtsuite ausführen.
8. Dateien direkt von der Festplatte erneut lesen.
9. Pfade, Größen, Zeitstempel und SHA-256-Hashes dokumentieren.
10. Task-Tracker, Roadmap und Übergabe aktualisieren.
11. Danach stoppen und nicht mit AP5 beginnen.

---

## 19. Quellenbasis dieser Übergabe

Diese Übergabe beruht auf:

- dem aktuellen Projektstand nach Abschluss von Arbeitspaket 3,
- `task.md`,
- `ÜBERGABE.md`,
- `docs/IMPLEMENTATION_ROADMAP.md`,
- `core/reinsertion.py`,
- `tests/test_reinsertion.py`,
- dem README des Server-Dokumentationspakets,
- den festgelegten Architektur- und Prozessentscheidungen der bisherigen Planung.

Bei Widersprüchen zwischen älteren Planungsständen und dem aktuell geprüften Code gilt der zuletzt verifizierte Code- und Teststand.
