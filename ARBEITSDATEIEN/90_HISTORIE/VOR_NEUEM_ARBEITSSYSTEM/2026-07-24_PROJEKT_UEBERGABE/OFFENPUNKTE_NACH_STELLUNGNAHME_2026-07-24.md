# Offene Punkte nach der Stellungnahme zum Prüfbericht

> **Stand:** 24. Juli 2026  
> **Auswertungsbasis dieses Dokuments:** ausschließlich `STELLUNGNAHME_ZUM_PRUEFBERICHT_2026-07-24.md`  
> **Zweck:** Trennung zwischen bereits eingeräumten Korrekturen, historisch noch zu prüfenden Tatsachen und weiterhin notwendigen Produkt-/Architekturentscheidungen

## 1. Kurzfazit

Die Stellungnahme übernimmt den wesentlichen Befund des Prüfberichts. Sie korrigiert insbesondere:

- die Rolle der Übergabe,
- die falsche Beschreibung des Audiopfads,
- die veralteten Dateinamen,
- den tatsächlichen Umfang der 96 Tests,
- die Einordnung des Live-Tests,
- die Abgrenzung zwischen Transport-Reconnect und vollständiger Betriebswiederaufnahme,
- die Vermischung von Ist- und Zielverhalten,
- fehlende Python-, Venv- und Threading-Vorgaben,
- bereits aus dem Code beantwortbare AP4-Fragen,
- unwirksame Konfigurationsfelder,
- Testartefakte und die veraltete README.

Damit ist der zentrale Projektstand nach der Stellungnahme klarer:

- AP1 bis AP3 gelten als implementiert und mit 96 Tests abgesichert.
- Diese 96 Tests verifizieren nicht den vollständigen Client.
- AP4 ist weiterhin der nächste reguläre Integrationsschritt.
- Der vorhandene Headless-Core besitzt noch nicht die vollständige Selbstheilung und noch keine Integration mit Historie und Textinjektion.

Die Stellungnahme enthält jedoch mehrere historische Behauptungen und Interpretationen, deren Beleg nicht in der Stellungnahme selbst enthalten ist. Diese Punkte müssen gezielt im Original-Chatverlauf und gegebenenfalls in den referenzierten Dateiversionen geprüft werden.

---

## 2. Durch die Stellungnahme ausreichend geklärte Punkte

Folgende Punkte benötigen für die sachliche Korrektur der Übergabe keinen weiteren historischen Nachweis, weil die Stellungnahme sie ausdrücklich einräumt und sie bereits mit dem aktuellen Repository-Befund übereinstimmen:

1. Die Übergabe ersetzt nicht `AGENTS.md` oder die verbindlichen Originalquellen.
2. Der aktuelle Client nimmt PCM16 direkt auf und besitzt kein lokales Float32-/Resampling-Modul.
3. Die aktuellen Dateien heißen `core/audio_capture.py` und `core/stt_session.py`.
4. Die 96 Tests betreffen ausschließlich AP1 bis AP3.
5. `tests/test_connection.py` ist inhaltlich nur ein Health-/Handshake-/Ping-Pong-Smoke-Test.
6. Transport-Reconnect und Wiederaufnahme des Diktierbetriebs sind verschiedene Funktionsstufen.
7. Final-Historisierung vor Queue-Übergabe ist Ziel von AP4 und noch nicht aktueller App-Ablauf.
8. Python 3.12 und die Projekt-Venv sind verbindlich.
9. Qt soll im Main Thread und der asyncio-Core in einem separaten Thread laufen.
10. Historie, Injection-Queue und Reinsertion sind noch nicht in `app.py` integriert.
11. Eine eigenständige Controller-Klasse existiert noch nicht.
12. Die genannten Text-Injection-Konfigurationsfelder sind teilweise noch nicht wirksam.
13. `config_path.db` und `param_path.db` sind unerwünschte Testartefakte.
14. Das Root-README ist gegenüber den Projektregeln veraltet.
15. Thread-Bridge, Ping-Monitoring und Wiederaufnahme nach Reconnect sind bekannte technische Risiken beziehungsweise Lücken.

Diese Punkte sollten in der späteren Gesamtdokumentation als korrigierter Ist-Stand behandelt werden.

---

## 3. Historisch noch zu prüfende Tatsachen

### H-01 – Gab es einen echten Mikrofon-/Audio-/Final-Livetest?

Die Stellungnahme bezeichnet Mikrofon bis `final` weiterhin als praktisch offen. Frühere Dokumente beschrieben den Headless-Core teilweise als gegen den realen Server getestet.

Zu prüfen ist:

- Wurde jemals `app.py` mit einem realen Mikrofon ausgeführt?
- Wurde dabei `{ "type": "start" }` gesendet und Audio übertragen?
- Wurde mindestens ein `realtime`- oder `final`-Event tatsächlich empfangen?
- Existiert dafür ein protokollierter Konsolenoutput oder nur eine zusammenfassende Behauptung?
- Wurde der Test vor oder nach dem aktuell vorhandenen Stand von `audio_capture.py` und `stt_session.py` durchgeführt?

### H-02 – Nachweis des historischen Connection-Smoke-Tests

Die Stellungnahme spricht von einem historisch ausgeführten Health-/Handshake-/Ping-Pong-Test.

Zu prüfen ist:

- Wurde `tests/test_connection.py` tatsächlich ausgeführt?
- Welcher konkrete Output wurde gemeldet?
- Zu welchem Zeitpunkt und gegen welchen Host?
- Wurde nur `ALL TESTS PASSED` berichtet oder ist der vollständige Eventoutput vorhanden?
- Entspricht die damals ausgeführte Dateiversion der heute vorhandenen Version?

### H-03 – Ursprung der alten Dateinamen

Aktive Dokumente nennen `core/audio_processor.py` und `core/stt_client.py`, obwohl diese Dateien aktuell nicht existieren.

Zu prüfen ist:

- Existierten diese Dateien in einer früheren Projektversion tatsächlich?
- Wurden sie später umbenannt, zusammengeführt oder ersetzt?
- Oder stammen die Namen ausschließlich aus einem Planungsstand beziehungsweise einer unzutreffenden Zusammenfassung?
- Welche Aussagen aus `task.md` gehen noch auf diese frühere Struktur zurück?

Das Ergebnis entscheidet, ob die Begriffe als „historisch überholt“ oder als „von Anfang an sachlich falsch“ bezeichnet werden sollten.

### H-04 – Zwei getrennte Hotkey-Aktionen

Die Stellungnahme erklärt:

- `Ctrl+Shift+Space` für Aufnahme umschalten,
- `Ctrl+Alt+Space` für letztes Transkript erneut einfügen.

Zu prüfen ist:

- Wurde diese Trennung im Originalverlauf ausdrücklich beschlossen?
- Welche Dokument- oder Dateiversion belegt beide Aktionen?
- War `Ctrl+Alt+Space` bereits verbindlich für `reinsert_last()` vorgesehen?
- Bezieht sich der vorhandene einzelne Konfigurationswert eindeutig auf den Aufnahme-Hotkey?
- Gab es alternative oder frühere Belegungen?

### H-05 – Selektive SQLite-Persistenz als bewusste Entscheidung

Die Stellungnahme bezeichnet die selektive Persistenz als bewusst umgesetzte Konfiguration und nicht automatisch als Fehler.

Zu prüfen ist:

- Wo wurde entschieden, nicht jedes Final sofort persistent zu speichern?
- Wurden `min_characters: 1000`, `store_failed_injections: true` und `store_all: false` ausdrücklich festgelegt?
- Welches Produktziel wurde dabei verfolgt: Datenschutz, Datenmenge, Performance oder nur eine vorläufige Default-Konfiguration?
- Wurde ausdrücklich akzeptiert, dass kurze erfolgreiche Transkripte nach Memory-Rotation oder Prozessende verloren gehen können?
- Widerspricht diese Entscheidung einer früheren Anforderung zur Datenverlustvermeidung?

### H-06 – Tatsächliche Grundlage für „AP3 abgenommen“

Die Stellungnahme erklärt „abgenommen“ mit einer im Gespräch erfolgten Prüfung der AP3-Dateien, Tests, Fehlersemantik und Datei-Hashes.

Zu prüfen ist:

- Welche konkreten Prüfungen wurden durchgeführt?
- Wurde die vollständige 96-Test-Suite oder nur AP3 ausgeführt?
- Welche Dateien, Größen, Zeitstempel und Hashes wurden gemeldet?
- Wurde der Dateistand anschließend direkt auf der Festplatte verifiziert?
- Hat der Benutzer AP3 ausdrücklich akzeptiert oder wurde die Abnahme nur vom Agenten formuliert?

Das Ergebnis soll bestimmen, ob künftig „inhaltlich nachgeprüft“, „vom Agenten verifiziert“ oder „vom Benutzer abgenommen“ korrekt ist.

### H-07 – Antigravity-Dateiproblem und Hashregel

Die Stellungnahme behandelt das Hashmanifest als aus einem früheren Dateimaterialisierungsproblem entstandene Zukunftsregel.

Zu prüfen ist:

- Ist der beschriebene Antigravity-Vorfall im Originalchat nachvollziehbar?
- Welche Dateien waren im Review sichtbar, aber nicht auf der Festplatte?
- Wie wurde der Stand wiederhergestellt?
- Wurden danach tatsächlich Hashes der AP3-Dateien ausgegeben?
- Ab welchem Zeitpunkt galt die Hashregel?

### H-08 – Bereits getroffene AP4-Entscheidungen zur Exakt-einmal-Semantik

Die Stellungnahme behandelt Callback-Wahl und Deduplizierungsübergang weiterhin als offene AP4-Entscheidung.

Zu prüfen ist:

- Wurde im bisherigen Verlauf bereits ein konkreter Controller oder Eventadapter vorgesehen?
- Wurde bereits entschieden, `on_text`, `on_event` oder eine neue Session-Schnittstelle zu verwenden?
- Gibt es eine frühere Spezifikation, die „neu angelegt“ gegenüber „bereits vorhanden“ unterscheidet?
- Wurde die Reihenfolge `History -> Queue -> Attempt` bereits mit einer genauen API festgelegt?
- Existieren bereits Abnahmekriterien für doppelte Final-Events und Reconnect-Sessiongrenzen?

### H-09 – Historischer Verifikationsstand von AP1 und AP2

Die Stellungnahme konzentriert sich bei der Gesprächsabnahme besonders auf AP3.

Zu prüfen ist:

- Welche Testläufe und Dateiprüfungen wurden bei AP1 und AP2 dokumentiert?
- Wurden deren Dateien ebenfalls direkt auf der Festplatte verifiziert?
- Gab es bekannte Restpunkte oder Abweichungen, die in späteren Zusammenfassungen verloren gingen?
- Sind die Zahlen 29 und 41 über den gesamten Verlauf stabil oder wurden Tests nachträglich ergänzt?

### H-10 – Einordnung der Baseline-Korrekturen in die Arbeitspakete

Die Stellungnahme schlägt vor:

- Thread-Bridge vor oder spätestens in AP4,
- Ping-Logik als separate Baseline-Korrektur,
- vollständige Reconnect-Selbstheilung weiterhin AP5.

Zu prüfen ist:

- Gab es im bisherigen Verlauf bereits eine verbindliche Paketzuordnung?
- Sollte der vorhandene Core vor AP4 ausdrücklich unverändert bleiben?
- Wurde AP5 bereits so definiert, dass erneutes `start` nach Reconnect dazugehört?
- Würde eine Thread-Bridge-Korrektur in `app.py` AP4 vorwegnehmen oder ist sie notwendige AP4-Integration?

Dieser Punkt ist teils historischer Fact-Check und teils noch zu treffende Planungsentscheidung.

---

## 4. Auch nach einem historischen Fact-Check verbleibende Entscheidungen

Folgende Fragen können durch den Chatverlauf möglicherweise eingeordnet, aber nicht automatisch abschließend entschieden werden. Wenn der Verlauf keine eindeutige Festlegung enthält, brauchen sie einen neuen ausdrücklichen Beschluss:

### E-01 – Crash-Sicherheit jedes Finaltexts

Soll wirklich jedes Final unmittelbar dauerhaft in SQLite gespeichert werden, oder bleibt die selektive Persistenz verbindlich?

### E-02 – Resultat-/Fehlerschnittstelle der Historie

Soll `TranscriptHistoryManager` echte Lesefehler künftig von „leer“ unterscheiden, damit Reinsertion zuverlässig `history_query_failed` melden kann?

### E-03 – Controller-Eingang und Exakt-einmal-Garantie

Welche konkrete Schnittstelle ist für AP4 maßgeblich, und wie wird „neu verarbeitet“ atomar beziehungsweise eindeutig signalisiert?

### E-04 – Hotkey-Konfigurationsschema

Wie werden Aufnahme-Hotkey und Reinsertion-Hotkey getrennt, Win32-kompatibel und validierbar konfiguriert?

### E-05 – Reihenfolge kleiner Baseline-Korrekturen

Werden Thread-Bridge und Ping-Logik vor AP4, innerhalb AP4 oder in separaten vorangestellten Korrekturpaketen umgesetzt?

### E-06 – Repository- und Testhygiene

Wann werden Testpfade korrigiert, Datenbankartefakte entfernt, Cache-Regeln ergänzt und README/aktive Dokumente bereinigt?

### E-07 – Form der endgültigen Übergabe

Soll die korrigierte Übergabe selbst ein Hashmanifest enthalten oder auf ein separates, maschinenlesbares Manifest verweisen?

---

## 5. Ziel des anschließenden Fact-Checks

Der nachfolgende Fact-Check soll nicht den gesamten HTML-Chat linear einlesen. Er soll für H-01 bis H-10 jeweils:

1. mit eindeutigen Suchbegriffen relevante Chatstellen lokalisieren,
2. nur enge Textausschnitte um Treffer lesen,
3. referenzierte Dateiversionen nur bei direkter Relevanz öffnen,
4. Aussagen mit Datum beziehungsweise Gesprächsreihenfolge belegen,
5. zwischen ausdrücklicher Benutzerentscheidung, Agentenbehauptung und tatsächlichem Tool-/Testoutput unterscheiden,
6. jeden Punkt als:
   - bestätigt,
   - teilweise bestätigt,
   - widerlegt,
   - nicht belegbar
   klassifizieren.

Die Ergebnisse werden anschließend in einer gesonderten Gesamtzusammenfassung dokumentiert.
