# RealtimeSTT Client – Verbindliche Agent-Regeln

## Projektziel

Dieses Repository enthält einen Windows-Desktop-Client für einen bereits vorhandenen RealtimeSTT-Server.

Der Client läuft dauerhaft im Hintergrund, überträgt Mikrofon-Audio per WebSocket, verarbeitet Realtime- und Final-Transkriptionen und fügt finale Texte über die Windows-Zwischenablage in die aktuell fokussierte Anwendung ein.

Der korrekte Serverhost ist:

`stt.voice.marcosudau.com`

Die Weboberfläche unter `voice.marcosudau.com` ist nicht der WebSocket-Endpunkt des Desktop-Clients.

## Verbindliche Technologieentscheidungen

Folgende Entscheidungen sind abgeschlossen und dürfen nicht eigenmächtig neu verhandelt oder ersetzt werden:

* Python 3.12
* PySide6 als UI-Framework
* Qt im Main Thread
* asyncio-Core in einem separaten Thread
* nativer globaler Windows-Hotkey über Win32
* Clipboard und `SendInput` für das Einfügen finaler Texte
* SQLite für die persistente Transkript-Historie
* keine Einfügung von Realtime-Zwischentexten
* kein pystray
* kein tkinter
* kein pynput
* kein Admin-Service in der aktuellen Entwicklungsphase
* kein lokaler Fallback-STT-Server in der aktuellen Entwicklungsphase

## Quellenhierarchie

Für unterschiedliche Sachgebiete gelten unterschiedliche verbindliche Quellen.

### Serverprotokoll

Für WebSocket-Protokoll, Session-Lebenszyklus, Events, Zustandsübergänge, Reconnect-Verhalten und Fehlersemantik sind ausschließlich die Dateien unter folgendem Pfad maßgeblich:

`server-docs-for-client-development/`

### Zielarchitektur und gewünschtes Verhalten

Für die weitere Client-Architektur, Transkript-Historie, Textinjektion, Clipboard-Verhalten, Threading, UI-Anbindung und Selbstheilung ist folgende Datei maßgeblich:

`docs/IMPLEMENTATION_ROADMAP.md`

### Arbeits- und Dokumentationsordnung

Für die Rollen der Projektdokumente, Aktualisierungszeitpunkte, Benennung, Archivierung, Entscheidungsnachweise und den dokumentarischen Abschluss eines Arbeitspakets ist folgende Datei verbindlich:

`docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`

### Schnelle Projektorientierung

Für einen kompakten Überblick über Projektziel, feste Entscheidungen, tatsächlichen Paketstand und offene Grenzen dient:

`docs/PROJEKTUEBERSICHT.md`

Die Übersicht erleichtert den Einstieg, ersetzt aber weder Roadmap, Code, Tests noch die Serverdokumentation.

### Tatsächlicher Implementierungsstand

Der vorhandene Quellcode und die erfolgreich ausführbaren Tests bestimmen, was im Repository tatsächlich implementiert ist.

### Fortschritt

`task.md` enthält den aktuellen Arbeits- und Testfortschritt.

### Operative Übergabe

`ÜBERGABE.md` enthält Startbefehle, Umgebungsinformationen, bekannte Besonderheiten und den letzten verifizierten Stand.

### Archivierte Dokumente

Dateien unter `docs/archive/` und im bereits vorhandenen `docs/.archive/` sind nicht verbindlich. Datierte Audit-, Prüf- und Übergabeordner unter `docs/` sind Snapshots und Belegsammlungen; sie werden nicht als parallele aktive Projektdokumentation fortgeführt. Historische Dateien dürfen keine aktuelle Entscheidung überschreiben.

## Kontextschonende Pflichtlektüre vor der ersten Codeänderung

Die Lesereihenfolge ist bewusst von allgemeiner Orientierung zu den unmittelbar
implementierungsrelevanten Details geordnet. Dadurch stehen aktiver
Paketvertrag, betroffener Code und zugehörige Tests beim Implementieren am
frischesten im Kontext.

### Stufe 1 – Kanonische Orientierung vollständig lesen

In dieser Reihenfolge:

1. `AGENTS.md`
2. `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`
3. `docs/PROJEKTUEBERSICHT.md`
4. `docs/IMPLEMENTATION_ROADMAP.md`
5. `ÜBERGABE.md`
6. `task.md`

Diese Dateien sind bewusst kompakter als die historischen Belegsammlungen.

### Stufe 2 – Aktiven Ausführungsauftrag und Paketvertrag lesen

1. den ausdrücklich erteilten Ausführungsauftrag für das aktive Paket, sofern
   vorhanden, vollständig lesen;
2. existiert kein eigener Ausführungsauftrag, die zugehörige Paketdatei unter
   `docs/work-packages/` vollständig lesen;
3. existieren beide, benennt der Ausführungsauftrag die zusätzlich benötigten
   Abschnitte der Paketdatei. Doppelte Vertragsdarstellungen werden nicht
   pauschal ein zweites Mal vollständig geladen.

Die Paketdatei beziehungsweise der Ausführungsauftrag muss die für das Paket
relevanten Paketabschnitte, Serverkapitel, Module und Tests ausdrücklich
benennen.

### Stufe 3 – Nur relevante Originalquellen lesen

Vor der Änderung:

1. `server-docs-for-client-development/README.md` als Index lesen;
2. nur die im aktiven Paket genannten Serverkapitel beziehungsweise
   einschlägigen Abschnitte öffnen;
3. mit `rg`, Überschriften- und Symbolsuche zuerst die relevanten Stellen
   lokalisieren;
4. die betroffenen Abschnitte vollständig lesen;
5. die tatsächlich zu ändernden Module, ihre direkten Abhängigkeiten und die
   dazugehörigen Tests vollständig lesen.

Nicht pauschal den gesamten Ordner `server-docs-for-client-development/`, den
gesamten Ordner `core/` oder alle Tests in den Kontext laden.

`app.py`, `config.yaml` und `requirements.txt` werden vollständig gelesen, wenn
das aktive Paket sie ändert oder ihre tatsächlichen Schnittstellen benötigt.

### Ausgeschlossene Quellen

Dateien unter `docs/archive/`, `docs/.archive/`, datierten Audit- und
Übergabeordnern sowie `docs/evaluations/` gehören nicht zur Pflichtlektüre.
Sie werden nur gezielt geöffnet, wenn der aktive Auftrag eine konkrete
historische oder noch offene Frage ausdrücklich dorthin verweist.

Vor jedem neuen Arbeitspaket diese abgestufte Lektüre erneut durchführen. Nicht
ausschließlich auf Chatkontext oder frühere Zusammenfassungen verlassen. Vor
der ersten Codeänderung anschließend die bestehende relevante Testsuite als
Baseline ausführen.

## Python-Umgebung

Für sämtliche Python-Befehle ist ausschließlich die Projektumgebung zu verwenden:

```powershell
.\venv\Scripts\python.exe
```

Nicht den globalen Befehl `python` verwenden.

Installationen erfolgen ausschließlich innerhalb der vorhandenen Projektumgebung.

## Schutz des bestehenden Core

Der vorhandene headless Core ist fertiggestellt und wurde automatisiert sowie gegen den realen Server getestet.

Bestehende Core-Komponenten dürfen nur geändert werden, wenn:

* die Integration des aktiven Arbeitspakets dies zwingend erfordert,
* ein reproduzierbarer Test einen Fehler nachweist,
* oder eine verbindliche Protokollvorgabe verletzt wird.

Keine vorsorglichen Refactorings und keine Neuimplementierung funktionierender Komponenten durchführen.

## Arbeitsweise

Es wird immer nur das ausdrücklich beauftragte Arbeitspaket umgesetzt.

Der vollständige Fahrplan muss bekannt sein, aber spätere Arbeitspakete dürfen nicht vorweggenommen werden.

Vor der Implementierung:

1. aktuellen Codezustand prüfen,
2. relevante Schnittstellen identifizieren,
3. bestehende Tests ausführen,
4. eine kurze konkrete Umsetzungsskizze für das aktive Arbeitspaket erstellen.

Danach das aktive Arbeitspaket vollständig implementieren.

Vor Abschluss:

1. passende automatisierte Tests ergänzen,
2. neue Tests ausführen,
3. bestehende Regressionstests ausführen,
4. Fehler iterativ beheben,
5. `task.md` aktualisieren,
6. `docs/IMPLEMENTATION_ROADMAP.md` bei Paket-, Architektur- oder Abnahmekriterienänderungen aktualisieren,
7. `ÜBERGABE.md` bei einer relevanten Änderung des Übergabestands aktualisieren,
8. weitere Dokumentationspflichten aus `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md` erfüllen.

Nach Abschluss des beauftragten Arbeitspakets stoppen. Nicht automatisch mit dem nächsten Arbeitspaket beginnen.

## Dokumentation von Abweichungen

Falls eine Vorgabe technisch nicht wie beschrieben umsetzbar ist:

1. den konkreten technischen Grund nachweisen,
2. die Auswirkungen beschreiben,
3. die kleinstmögliche Abweichung wählen,
4. die Abweichung dokumentieren.

Keine großflächige Neuplanung und kein Austausch festgelegter Technologien ohne ausdrücklichen Auftrag.

## Datenschutz und Repository-Sicherheit

* `.env` enthält Zugangsdaten und darf nicht ausgegeben oder committed werden.
* API-Keys dürfen weder in Logs noch in Testausgaben erscheinen.
* Die SQLite-Historie liegt im lokalen Anwendungsdatenverzeichnis und nicht im Repository.
* Laufzeitdaten, Logs und lokale Datenbanken dürfen nicht versehentlich als Projektdateien behandelt werden.
