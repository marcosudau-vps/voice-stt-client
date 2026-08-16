# Stellungnahme zum Prüfbericht vom 24. Juli 2026

> **Bezug:** `PRUEFBERICHT_2026-07-24.md`  
> **Bezug der Prüfung:** `2026-07-24_PROJEKT_UEBERGABE_REALTIME_STT_CLIENT.md`  
> **Zweck:** Einordnung der Prüffeststellungen, Korrektur missverständlicher Aussagen und Festlegung der für die weitere Dokumentation maßgeblichen Interpretation  
> **Wichtig:** Dieses Dokument autorisiert noch keine Codeänderungen. Technische Korrekturen sollen weiterhin als klar abgegrenzte Arbeitspakete beauftragt werden.

---

## 1. Gesamtbewertung des Prüfberichts

Der Prüfbericht ist insgesamt sorgfältig, sachlich und in den meisten Punkten zutreffend.

Die geprüfte Projektübergabe wurde aus dem damaligen Gesprächsstand, den Dateien zu den Arbeitspaketen 1 bis 3 und dem README des Server-Dokumentationspakets erstellt. Sie war **keine vollständige Repository-Prüfung** von `app.py`, dem gesamten `core/`-Verzeichnis, allen Tests, `AGENTS.md`, `config.yaml`, `requirements.txt` und der realen Projektstruktur.

Daraus resultieren mehrere tatsächlich fehlerhafte oder zu weitgehende Aussagen. Insbesondere die Beschreibung des Audiopfads, die Einordnung des Live-Tests, die Breite der Testabdeckung und die Wiederanlauffähigkeit nach einem Reconnect müssen korrigiert werden.

Die Kernaussagen bleiben jedoch bestehen:

- Arbeitspaket 1 – Historie ist implementiert.
- Arbeitspaket 2 – Text-Injection-Queue ist implementiert.
- Arbeitspaket 3 – Reinsertion-Service ist implementiert.
- Die 96 Tests dieser drei Arbeitspakete sind erfolgreich reproduzierbar.
- Diese Komponenten sind noch nicht in den aktuellen WebSocket-/Audio-Entry-Point integriert.
- Arbeitspaket 4 – Controller-Integration ist der nächste reguläre Entwicklungsschritt.

---

## 2. Verbindliche Korrekturen an der bisherigen Übergabe

### 2.1 Rolle der Übergabe

Die Formulierung, die Übergabe könne als alleinstehender Einstiegspunkt sämtliche Originalquellen ersetzen, wird zurückgenommen.

Korrekt ist:

> Die Übergabe ist ein zentraler Orientierungs- und Quellenindex. Sie ersetzt weder `AGENTS.md` noch die dort festgelegte Pflichtlektüre und Quellenhierarchie.

Für Protokollfragen bleiben die Serverdokumente maßgeblich. Für den tatsächlichen Implementierungsstand sind der vorhandene Code und die vorhandenen Tests maßgeblich. Für die Zielarchitektur bleibt die aktuelle Roadmap maßgeblich.

### 2.2 Tatsächlicher Audiopfad

Die Beschreibung mit lokaler `float32`-Verarbeitung, eigenem Resampling und anschließender PCM16-Konvertierung war falsch.

Der aktuelle Ist-Stand lautet:

- Audioaufnahme über `core/audio_capture.py`
- bevorzugt 16 kHz
- Mono
- direkte PCM16-Aufnahme mit `dtype: int16`
- direkte Byteübernahme aus dem Audio-Callback
- kein lokales Resampling im aktuellen Client
- unterstützt das Gerät 16 kHz nicht, wird die Geräte-Standardrate verwendet und im Audiopaket übermittelt
- das erforderliche Resampling erfolgt in diesem Fall serverseitig

Die tatsächlich vorhandenen zentralen Dateien heißen:

- `core/audio_capture.py`
- `core/stt_session.py`

Verweise auf `core/audio_processor.py` oder `core/stt_client.py` sind im aktuellen Projektstand veraltet beziehungsweise falsch und müssen aus den aktiven Dokumenten entfernt werden.

### 2.3 Umfang der 96 Tests

Die Überschrift „Gesamter Teststand“ war missverständlich.

Korrekt ist:

> **Automatisierter Teststand der Arbeitspakete 1 bis 3: 96 Tests erfolgreich**

Aufteilung:

- 29 History-Tests
- 41 Text-Injection-Tests
- 26 Reinsertion-Tests

Diese Suite deckt derzeit nicht ab:

- `app.py`
- `core/audio_capture.py`
- `core/stt_session.py`
- den WebSocket-Final-Eventpfad zur Historie
- den Pfad von der Historie zur Injection-Queue
- den Wiederanlauf des Streamings nach Reconnect
- reale Mikrofonaufnahme
- reales Clipboard und reales `SendInput`
- PySide6, Tray, Overlay, Hotkeys und Single-Instance-Verhalten

Der Erfolg der 96 Tests belegt damit die drei isolierten Kernbausteine, nicht den vollständigen Client.

### 2.4 Einordnung des Live-Tests

Der vorhandene beziehungsweise historisch ausgeführte `tests/test_connection.py` ist korrekt als folgender Test zu bezeichnen:

> Health-/WebSocket-Handshake-/Ping-Pong-Smoke-Test gegen den realen Server

Er ist kein Mikrofon-, Audio-, Realtime-, Final-Event- oder vollständiger End-to-End-Test.

Offen bleiben insbesondere:

- `{ "type": "start" }`
- Übertragung realer Audiopakete
- `{ "type": "stop" }`
- Empfang eines `realtime`-Events
- Empfang eines `final`-Events
- tatsächliche Mikrofonaufnahme
- vollständiger Pfad bis zur Zielanwendung

### 2.5 Transport-Reconnect und Wiederaufnahme des Diktierbetriebs

Diese beiden Ebenen müssen getrennt dokumentiert werden:

**Implementiert:**

- `STTSession.run()` besitzt einen Transport-Reconnect-Loop mit Backoff und Jitter.

**Nicht implementiert beziehungsweise nicht verifiziert:**

- erneutes `start` nach Aufbau einer neuen Session
- automatische Wiederaufnahme des Audiostreamings nach Reconnect
- vollständige Wiederherstellung des Diktierbetriebs
- End-to-End-Selbstheilung bei Netzwerkverlust

Die bisherige Übergabe war an dieser Stelle zu pauschal.

### 2.6 Ist-Verhalten und Zielverhalten

Die Aussagen

- Finaltext zuerst historisieren,
- danach an die Injection-Queue übergeben,

beschreiben die **verbindliche Zielarchitektur für Arbeitspaket 4**, nicht den derzeitigen Anwendungsablauf.

Der aktuelle Ist-Pfad ist:

```text
WebSocket-Event
-> STTSession._message_loop()
-> STTSession._apply_event() / Reducer
-> app.py on_text(...)
-> Konsolenausgabe
```

Der Zielpfad für finale Events ist:

```text
final
-> eindeutige Session-/Segmentidentität
-> Historie und Deduplizierung
-> genau einmal an die Injection-Queue
-> Attempt-Dokumentation am bestehenden HistoryEntry
```

Realtime-Events bleiben ausschließlich Anzeigezustand und dürfen nicht in die Injection-Queue gelangen.

---

## 3. Einordnung der als unklar gemeldeten Punkte

### 3.1 Python- und Laufzeitvorgaben

Die Ergänzung ist berechtigt.

Verbindlich sind:

- Python 3.12
- vorhandene Projekt-Venv
- Aufrufe über `.\venv\Scripts\python.exe`
- kein unkontrollierter Rückgriff auf ein globales `python`
- PySide6 bleibt das UI-Framework
- globale Hotkeys werden nativ über Win32 umgesetzt

### 3.2 Threading-Modell

Der Zielzustand muss ausdrücklich lauten:

- Qt läuft im Main Thread.
- Der asyncio-Core läuft in einem separaten Thread mit eigenem Event Loop.
- Core zu UI erfolgt über Qt-Signale.
- UI zu Core erfolgt über thread-sichere Befehle beziehungsweise eine explizite Loop-Bridge.
- Im Qt-Main-Thread werden keine blockierenden asyncio-Operationen ausgeführt.

Der heutige Headless-Entry-Point mit `asyncio.run()` im Main Thread ist ein zulässiger Zwischenstand, aber nicht die Zielarchitektur der späteren PySide6-Anwendung.

### 3.3 Bereits beantwortete AP4-Fragen

Die im Übergabedokument als offen genannten Fragen waren als Prüfauftrag für das Einlesen des vollständigen Projekts gedacht. Nach der nun erfolgten Repository-Prüfung gelten folgende Punkte als geklärt:

- `realtime` und `final` treffen in `STTSession._message_loop()` ein.
- Die Verarbeitung läuft über `_apply_event()` und den Reducer.
- `on_text(segment_id, text, is_final)` wird für neue beziehungsweise geänderte Segmentstände aufgerufen.
- `on_event(event_type, event)` erhält jedes Serverevent.
- `sessionId` liegt im Clientzustand und im Originalevent.
- `segmentId` liegt im Originalevent und im reduzierten Segment.
- `app.py` startet derzeit `STTSession` und `AudioCapture`.
- Historie, Injection-Queue und Reinsertion-Service werden dort noch nicht instanziiert.
- Eine eigenständige UI-neutrale Controller-Klasse existiert noch nicht.

Diese Informationen sollen in einer überarbeiteten Übergabe nicht mehr als offene Recherchefragen erscheinen.

### 3.4 Exakt-einmal-Semantik für Final-Events

Der Prüfbericht identifiziert hier zu Recht eine noch offene Integrationsentscheidung.

Wichtig ist:

- `on_text` profitiert von der Reducer-Unterdrückung identischer Wiederholungen, enthält in der bisherigen Signatur aber keine `sessionId`.
- `on_event` enthält das vollständige Originalevent, wird aber für jedes Event ausgelöst.
- Der Rückgabewert von `TranscriptHistoryManager.add_entry()` reicht nicht in jeder Situation allein aus, um „neu angelegt“ sicher von „bereits vorhanden“ zu unterscheiden.

Für Arbeitspaket 4 muss deshalb ausdrücklich festgelegt und getestet werden:

1. welcher Callback beziehungsweise welche neue Controller-Schnittstelle maßgeblich ist,
2. wie `sessionId + segmentId` als Deduplizierungsidentität übernommen werden,
3. wie ein neu verarbeiteter Final-Eintrag von einem bereits bekannten Eintrag unterschieden wird,
4. dass ein doppeltes Final niemals erneut enqueued wird.

Diese Frage ist kein Grund, Arbeitspaket 3 wieder zu öffnen. Sie gehört zur Controller-Integration.

### 3.5 „Lokal sichern“ und SQLite-Persistenz

Hier lag eine sprachliche Mehrdeutigkeit vor.

Die aktuelle, bereits implementierte Semantik lautet:

- Jeder akzeptierte Final-Eintrag wird zunächst in die In-Memory-Historie aufgenommen.
- SQLite-Persistenz ist selektiv und konfigurationsabhängig.
- Kurze und technisch erfolgreich verarbeitete Einträge werden bei `store_all: false` nicht zwangsläufig sofort dauerhaft gespeichert.
- Fehlerhafte oder übersprungene Einfügungen können nachträglich persistiert werden.
- Die In-Memory-Historie ist nicht gleichbedeutend mit Crash-sicherer dauerhafter Speicherung.

Daher muss künftig unterschieden werden zwischen:

- **in die lokale Historie aufnehmen**
- **dauerhaft in SQLite persistieren**

Die bestehende selektive Persistenz ist eine bewusst umgesetzte Konfiguration und nicht automatisch ein Fehler. Falls das Produktziel geändert wird und wirklich jedes Final crash-sicher gespeichert werden soll, muss dies separat entschieden und beispielsweise über `store_all: true` beziehungsweise eine geänderte Persistenzregel umgesetzt werden.

### 3.6 Reinsertion und intern abgefangene SQLite-Fehler

Der Hinweis ist technisch berechtigt, invalidiert Arbeitspaket 3 jedoch nicht.

`TranscriptReinsertionService` besitzt eine definierte Semantik für History-Methoden, die Exceptions melden. Der reale `TranscriptHistoryManager` fängt bestimmte SQLite-Fehler derzeit intern ab und liefert eine leere Liste. Dadurch kann der Reinsertion-Service im integrierten Betrieb nicht jeden echten Persistenzfehler von einem tatsächlich leeren Ergebnis unterscheiden.

Einordnung:

- Die AP3-Service-Semantik und ihre Tests bleiben korrekt.
- Die reale History-Schnittstelle transportiert derzeit nicht alle Fehlerzustände nach außen.
- Dies ist eine bekannte Schnittstellenbegrenzung zwischen Komponenten.
- Eine Änderung daran darf nicht beiläufig in AP4 erfolgen, sondern benötigt eine ausdrücklich festgelegte Fehler-/Resultat-Schnittstelle oder ein kleines separates Korrekturpaket.

### 3.7 Hotkey-Belegung

Hier besteht teilweise ein Missverständnis.

Die beiden genannten Tastenkombinationen sind für **zwei unterschiedliche Aktionen** vorgesehen:

- Aufnahme umschalten: `Ctrl+Shift+Space`
- letzten Transkripttext erneut einfügen: `Ctrl+Alt+Space`

Das ist kein inhaltlicher Konflikt zwischen zwei Standardbelegungen derselben Aktion.

Tatsächlich problematisch sind jedoch:

- Die aktuelle Konfiguration bildet möglicherweise nur eine der beiden Aktionen ab.
- Das vorhandene Zeichenformat stammt noch aus einer früheren `pynput`-Notation.
- Die spätere Implementierung soll native Win32-Hotkeys verwenden.

Vor der Hotkey-Implementierung müssen daher das Konfigurationsschema und das Format vereinheitlicht werden. Die beiden getrennten Aktionen bleiben bestehen.

### 3.8 Noch nicht wirksame Konfigurationsfelder

Der Prüfbericht ist zutreffend:

- `text_injection.final_strategy`
- `text_injection.append_space`
- `text_injection.warn_elevated`

sind derzeit nicht vollständig im Injector wirksam.

Diese Felder müssen bis zu ihrer Implementierung als reservierte beziehungsweise noch nicht umgesetzte Konfigurationsoptionen dokumentiert werden. Insbesondere darf `append_space: true` nicht als bereits aktives Laufzeitverhalten beschrieben werden.

### 3.9 SQLite-Testartefakte im Projekt

`config_path.db` und `param_path.db` sind keine vorgesehenen Laufzeitdaten des Clients, sondern offenbar nicht aufgeräumte Testartefakte.

Der Befund ist berechtigt. Er invalidiert die getestete History-Funktionalität nicht, muss aber in einem kleinen Testhygiene-/Repository-Cleanup behoben werden:

- relative Testpfade durch Pfade unter einem temporären Testverzeichnis ersetzen,
- bestehende Artefakte kontrolliert entfernen,
- Cleanup-Regeln für `*.db`, `__pycache__` und Test-Caches festlegen.

### 3.10 Root-README

Die README-Angaben mit Python 3.10+, globalem `pip` und `python app.py` sind gegenüber den verbindlichen Projektregeln veraltet.

Die README soll später an folgende Betriebsweise angepasst werden:

```powershell
.\venv\Scripts\python.exe -m pip ...
.\venv\Scripts\python.exe app.py
```

und Python 3.12 als verbindliche Version nennen.

### 3.11 Hashmanifest

Die Hash-Regel in der bisherigen Übergabe war als Sicherheitsmaßnahme für zukünftige Agent-Turns formuliert. Dass die Übergabe selbst noch kein vollständiges Manifest enthielt, ist deshalb kein innerer Widerspruch.

Der Verbesserungsvorschlag ist dennoch sinnvoll:

- Für einen freigegebenen Projektstand sollte ein separates Hashmanifest der maßgeblichen Dateien erzeugt werden.
- Dieses Manifest ergänzt die Übergabe, ersetzt aber kein Versionsverwaltungssystem.
- Da das Projekt derzeit offenbar kein eigenes Git-Repository besitzt, ist ein reproduzierbarer Snapshot besonders nützlich.

### 3.12 Begriff „abgenommen“

Mit „abgenommen“ war die im Gespräch erfolgte Prüfung der AP3-Dateien, Tests, Fehlersemantik und gemeldeten Datei-Hashes gemeint. Es handelte sich nicht um eine formale Release- oder Projektabnahme mit hinterlegter abnehmender Person.

Die belastbarere Formulierung lautet daher:

> Arbeitspaket 3 ist abgeschlossen, automatisiert getestet und inhaltlich nachgeprüft.

---

## 4. Einordnung der neu identifizierten technischen Risiken

### 4.1 Threadfremder Zugriff auf `asyncio.Queue`

Der Befund ist ernst zu nehmen.

Ein direkter Aufruf von `asyncio.Queue.put_nowait()` aus dem Audio-Processing-Thread ist keine dokumentierte thread-sichere Übergabe. Der Übergang muss über den zuständigen asyncio-Loop erfolgen, beispielsweise mit einer expliziten thread-sicheren Scheduling-Brücke.

Dieser Punkt sollte vor oder spätestens im Rahmen von AP4 gezielt korrigiert und getestet werden, weil AP4 weitere Threadgrenzen hinzufügt.

### 4.2 Ping-/Pong-Miss-Erkennung

Die beschriebene Logik mit einem nicht zuverlässig zurückgesetzten RTT-/Pong-Zustand ist ein plausibler Defekt im vorhandenen Session-Core.

Dieser Punkt gehört nicht zu den bereits abgeschlossenen Arbeitspaketen 1 bis 3. Er sollte als kleine, separat prüfbare Baseline-Korrektur vor der Aussage eines robusten Headless-Cores behandelt werden.

### 4.3 Wiederaufnahme nach Reconnect

Der Transport-Reconnect ist vorhanden, die erneute Aufnahme des Streamingbetriebs jedoch nicht.

Einordnung für die Planung:

- AP4 muss den Session-Lifecycle korrekt beobachten und darf den vorhandenen Reconnect nicht verschlechtern.
- Die automatische vollständige Wiederaufnahme nach Netzwerkverlust gehört inhaltlich zur Selbstheilung aus AP5.
- Die fehlende Wiederaufnahme muss aber schon jetzt ausdrücklich dokumentiert und bei der AP4-Schnittstellengestaltung berücksichtigt werden.

### 4.4 Schmale Abdeckung von `tests/test_connection.py`

Die Einordnung als Smoke-Test für einen günstigen Normalfall ist korrekt.

Der Test kann bestehen bleiben, sollte aber nicht als Protokoll-Contract- oder End-to-End-Test bezeichnet werden. Später sind tolerant aufgebaute Tests für Startphase, zusätzliche Events, `start`, Audio und Final-Empfang erforderlich.

---

## 5. Präzisierter verbindlicher Kurzstand

### Implementiert

- Headless-Entry-Point mit `STTSession` und `AudioCapture`
- PCM16-Audioaufnahme und binäre Audiopakete
- WebSocket-Grundprotokoll mit `hello`, `ready`, `start`, Events und Ping
- Reducer und Clientzustand
- Transport-Reconnect-Loop
- Konsolenausgabe von Realtime- und Finaltext
- Arbeitspaket 1: Historie
- Arbeitspaket 2: Text-Injection-Queue
- Arbeitspaket 3: Reinsertion-Service

### Automatisiert verifiziert

- 29 History-Tests
- 41 Text-Injection-Tests mit Fake-Backend
- 26 Reinsertion-Tests
- insgesamt 96 erfolgreiche Tests für AP1 bis AP3

### Historisch als Smoke-Test dokumentiert

- Health-Endpunkt
- WebSocket-Handshake
- Ping/Pong gegen den realen Server

### Noch nicht integriert oder implementiert

- Controller zwischen Final-Event, Historie und Injection-Queue
- Instanziierung von Historie, Queue und Reinsertion im Anwendungs-Entry-Point
- automatische Wiederaufnahme des Streamings nach Reconnect
- Qt-/asyncio-Bridge in der Zielarchitektur
- Tray, Overlay, native Hotkeys und Single-Instance-Guard
- Mikrofon-Hot-Plug-Selbstheilung
- Verlaufsauswahl in der UI

### Praktisch weiterhin offen

- Mikrofon bis zu einem echten `final`
- reales Einfügen in Notepad
- kompletter Pfad `final -> History -> Queue -> Zielanwendung`
- Reinsert-last per Hotkey
- Reinsertion über Tray
- Netzwerkverlust mit vollständiger Betriebswiederaufnahme
- Mikrofon entfernen und erneut anschließen

---

## 6. Konsequenz für die weitere Arbeit

Der Prüfbericht soll als Grundlage für eine korrigierte Übergabe verwendet werden.

Vor Beginn der eigentlichen Controller-Implementierung sind folgende Schritte sinnvoll:

1. Projektübergabe als Version 2 korrigieren.
2. Veraltete Dateinamen in aktiven Dokumenten berichtigen.
3. Teststand ausdrücklich auf AP1 bis AP3 begrenzen.
4. Live-Test korrekt als Smoke-Test benennen.
5. Ist- und Zielpfad trennen.
6. Python 3.12, Projekt-Venv und Threading-Modell ergänzen.
7. Aktuellen Eventpfad und AP4-Integrationspunkte eintragen.
8. Exakt-einmal-Semantik für Final-Events vor AP4 festlegen.
9. Testartefakte und veraltete README separat bereinigen.
10. Thread-Übergang und Ping-Logik als kleine Baseline-Korrekturen prüfen.
11. Vollständige Reconnect-Selbstheilung weiterhin als noch offenen Funktionsumfang ausweisen.
12. Ein Hashmanifest des korrigierten Ausgangsstands erstellen.

Arbeitspaket 3 bleibt abgeschlossen. Die neu identifizierten Punkte betreffen überwiegend die bestehende Phase-1-Basis, die Integration zwischen Komponenten, Dokumentationsgenauigkeit und spätere Selbstheilung.

---

## 7. Erwartete Behandlung dieser Stellungnahme

Für die nächste Dokumentationsrevision gilt:

- Die sachlich bestätigten Punkte des Prüfberichts sollen übernommen werden.
- Die hier erläuterten Einordnungen sollen berücksichtigt werden.
- Die beiden Hotkeys dürfen nicht als widersprüchliche Belegung derselben Aktion behandelt werden.
- Selektive SQLite-Persistenz darf nicht stillschweigend in „jedes Final dauerhaft speichern“ geändert werden.
- AP3 darf wegen der realen History-Fehlerbegrenzung nicht ohne separaten Auftrag wieder geöffnet werden.
- Technische Risiken sollen dokumentiert, aber nur in klar abgegrenzten Korrekturpaketen verändert werden.
- Diese Stellungnahme selbst ist noch kein Implementierungsauftrag.
