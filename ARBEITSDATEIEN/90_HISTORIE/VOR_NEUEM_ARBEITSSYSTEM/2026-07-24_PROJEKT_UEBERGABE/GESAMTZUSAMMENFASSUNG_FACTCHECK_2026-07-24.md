# Gesamtzusammenfassung und Fact-Check zur Projektübergabe

> **Stand:** 24. Juli 2026  
> **Prüfgegenstand:** Übergabe, Prüfbericht, Stellungnahme sowie gezielte Originalbelege aus dem bisherigen Projektverlauf  
> **Änderungsumfang:** Für diese Prüfung wurden außerhalb dieses Übergabeordners keine Dateien verändert.

## 1. Ergebnis in einem Satz

Die Stellungnahme korrigiert den ursprünglichen Übergabestand im Wesentlichen zutreffend; der gezielte Abgleich mit dem Originalverlauf bestätigt den Connection-Smoke-Test, die Testhistorie von AP1 bis AP3, die zwei vorgesehenen Hotkey-Aktionen und die AP3-Prüfung, widerlegt aber die Darstellung der alten Modulnamen als belegte frühere Dateien und zeigt, dass mehrere angeblich bereits geklärte Punkte weiterhin echte Produkt- oder Integrationsentscheidungen sind.

## 2. Belastbarer Gesamtstand

Der aktuell belastbare Projektstand lautet:

- Das Projektziel ist ein dauerhaft laufender Windows-Desktop-Client, der Mikrofon-Audio per WebSocket an `stt.voice.marcosudau.com` überträgt, Realtime-Texte nur anzeigt und finale Texte historisiert und per Clipboard/`SendInput` in die aktuell fokussierte Anwendung einfügt.
- Der vorhandene Headless-Pfad nimmt Audio direkt als Mono-PCM16 mit 16 kHz auf. Ein lokaler Float32-/Resampling-Pfad ist im aktuellen Projekt nicht vorhanden.
- Die aktuellen Core-Dateien heißen `core/audio_capture.py` und `core/stt_session.py`.
- AP1 Transkript-Historie, AP2 Text-Injection-Queue und AP3 UI-neutrale Reinsertion sind als getrennte Komponenten implementiert.
- Die im aktuellen Prüfbericht isoliert reproduzierten 96 Tests entfallen auf:
  - 29 History-Tests,
  - 41 Text-Injection-Tests,
  - 26 Reinsertion-Tests.
- Diese 96 Tests prüfen weder `app.py` noch `AudioCapture`, `STTSession`, Mikrofonbetrieb, Server-End-to-End-Transkription, PySide6, Tray, Overlay oder globale Hotkeys.
- Ein historischer Health-/WebSocket-Handshake-/Ping-Pong-Test gegen den Server ist belegt.
- Ein echter Lauf vom physischen Mikrofon über Audioübertragung bis zu einem `realtime`- oder `final`-Event ist nicht belegt und wurde im Verlauf wiederholt ausdrücklich als offen bezeichnet.
- Historie, Queue und Reinsertion sind noch nicht mit dem finalen Server-Event in `app.py` verbunden. AP4 Controller-Integration bleibt der nächste reguläre Integrationsschritt.
- Der Transport-Reconnect in `STTSession` ist nicht mit einer vollständig automatischen Wiederaufnahme des Diktierbetriebs gleichzusetzen.
- Thread-Übergang, Ping-Miss-Erkennung und Wiederaufnahme des Streamings nach Reconnect sind nicht durch die 96 Tests abgesicherte technische Risiken.

## 3. Vorgehen und Quellenwert

Der große HTML-Export wurde nicht linear vollständig eingelesen. Die Prüfung erfolgte entsprechend der Aufgabenstellung in kleinen Schritten:

1. Aus der Stellungnahme wurden zehn historische Prüfpunkte H-01 bis H-10 abgeleitet.
2. Für jeden Punkt wurden eindeutige Suchbegriffe verwendet.
3. Nur enge Textbereiche um relevante Treffer wurden gelesen.
4. Behauptungen wurden, soweit möglich, mit referenzierten Dateiversionen abgeglichen.
5. Es wurde unterschieden zwischen:
   - tatsächlichem Testoutput,
   - Bericht eines ausführenden Agenten,
   - nachträglicher Prüfung in der damaligen Chat-Session,
   - verbindlichem Zieltext,
   - bloßer Empfehlung oder Vermutung.

Verwendete Hauptquellen:

- `STELLUNGNAHME_ZUM_PRUEFBERICHT_2026-07-24.md`
- `PRUEFBERICHT_2026-07-24.md`
- `bisheriger_projekt_verlauf/chatverlauf_bis_abschluss_arbeitspakt3.html`
- die einschlägigen Versionen unter `bisheriger_projekt_verlauf/referenzierte_datei_versionen/`
- der unverändert gelassene aktuelle Projektcode und die im Prüfbericht dokumentierte isolierte Testsuite

Die höchste Beweiskraft haben der aktuelle Code, reproduzierbare Tests und konkrete Konsolenausgaben. Chat-Zusammenfassungen und alte Dokumentversionen belegen dagegen vor allem, was damals behauptet, geplant oder als abgenommen bezeichnet wurde.

## 4. Ausgeführter Fact-Check

### H-01 – Echter Mikrofon-/Audio-/Final-Livetest

**Ergebnis: Bestätigt offen.**

Im Verlauf findet sich kein belastbarer Beleg, dass `app.py` mit einem physischen Mikrofon bis zu einem empfangenen `realtime`- oder `final`-Event durchlaufen wurde.

Stattdessen wird der Test mehrfach ausdrücklich als offen geführt:

- HTML-Zeilen 1677–1691: Health-Test, WebSocket-Handshake und Server-Protokolltest bestanden; Mikrofon-End-to-End-Test durch den Benutzer noch offen.
- HTML-Zeilen 4630–4635: Connection-Test bestanden; der physische Mikrofon-End-to-End-Test wird separat durchgeführt.
- Die referenzierten `task.md`-Versionen unterscheiden ebenfalls zwischen erfolgreichem Connection-Test und offenem praktischem Mikrofontest.

Eine frühere Forderung oder Absicht, diesen Test auszuführen, ist kein Ausführungsnachweis.

**Konsequenz:** In einer korrigierten Übergabe darf nicht pauschal stehen, der Audiopfad sei real gegen den Server end-to-end verifiziert. Zulässig ist nur die engere Aussage zum Connection-Smoke-Test.

### H-02 – Historischer Connection-Smoke-Test

**Ergebnis: Ausführung und Ergebnis bestätigt; Versionsidentität nur teilweise belegbar.**

Der HTML-Export enthält konkreten gemeldeten Output:

- HTML-Zeilen 3972–3993:
  - Health Check `ok: True`,
  - `ready: True`,
  - `hello received`,
  - `ready received: ok=True`,
  - `pong received`,
  - `ALL TESTS PASSED`.
- HTML-Zeilen 4630–4635 bestätigen den später dokumentierten Abschlussstatus.

Damit ist mehr als eine bloße pauschale Erfolgsbehauptung vorhanden. Der Test prüfte jedoch nur HTTP-Health, WebSocket-Handshake und Ping/Pong. Er sendete kein Mikrofon-Audio und wartete nicht auf ein Transkript.

Nicht lückenlos belegbar ist, dass die damals ausgeführte Datei bytegenau der heute vorhandenen `tests/test_connection.py` entspricht. Für diese Datei liegt in den bereitgestellten Referenzversionen kein damaliger Hash oder vollständiger Dateisnapshot vor.

**Konsequenz:** Korrekte Formulierung: „Historisch erfolgreich ausgeführter Health-/Handshake-/Ping-Pong-Smoke-Test; kein Audio-/Transkriptions-End-to-End-Test.“

### H-03 – Ursprung von `core/audio_processor.py` und `core/stt_client.py`

**Ergebnis: Als frühere reale Dateien nicht belegbar; die historische-Dateinamen-Erklärung ist zu verwerfen.**

Die Namen finden sich in den bereitgestellten Referenzdateien nur in `task(6).md` und `task(7).md`. Dort werden sie ohne beigefügten Codebeleg als erledigte Komponenten genannt.

Weitere Feststellungen:

- Keine bereitgestellte frühere Codeversion enthält diese Module.
- Frühere `task.md`-Versionen nennen bereits `core/audio_capture.py` und `core/stt_session.py`.
- `core/stt_client.py` erscheint im Chat einmal lediglich als vom damaligen Assistenten genannte mögliche Alternative: „`core/stt_session.py` oder `core/stt_client.py`; falls beide existieren, beide“. Das belegt keine Existenz.
- `core/audio_processor.py` erscheint außerhalb der beiden späten Task-Versionen nicht als tatsächliche Projektdatei.

Es gibt somit keinen Beleg für eine Umbenennung oder Zusammenführung dieser Module.

**Konsequenz:** Nicht „historisch überholte Dateinamen“ schreiben, sondern: „unbelegte beziehungsweise sachlich falsche Angaben in zwei späten Tracker-Versionen“. Maßgeblich sind `core/audio_capture.py` und `core/stt_session.py`.

### H-04 – Zwei getrennte Hotkey-Aktionen

**Ergebnis: Als dokumentiertes Ziel bestätigt; das aktuelle Konfigurationsschema bleibt offen.**

Der Verlauf und mehrere Roadmap-Versionen unterscheiden eindeutig:

- `Ctrl+Shift+Space`: Aufnahme ein-/ausschalten,
- `Ctrl+Alt+Space`: letztes Transkript erneut einfügen.

Belege:

- HTML-Zeile 1242 schlägt `Ctrl+Shift+Space` für Toggle in der ersten Version vor.
- HTML-Zeilen 1962–1963 und 2281–2282 nennen beide Zuordnungen gemeinsam.
- `referenzierte_datei_versionen/IMPLEMENTATION_ROADMAP.md`, Zeilen 131–132, enthält dieselben zwei Aktionen.
- Der verbindliche Umsetzungsfahrplan enthält die Zuordnung ebenfalls.

Die Belegung wurde damit in einen als verbindlich bezeichneten Fahrplan übernommen. Eine separate Benutzeräußerung, in der beide Tastenkombinationen einzeln bestätigt werden, wurde nicht gefunden; die Verbindlichkeit folgt aus der Übernahme des Gesamtfahrplans.

Der aktuelle einzelne Hotkey-Konfigurationswert bildet die zwei Aktionen nicht eindeutig und Win32-gerecht ab.

**Konsequenz:** Kein inhaltlicher Konflikt zwischen den zwei Tastenkombinationen. Offen bleibt E-04, also das getrennte, validierbare Win32-Konfigurationsschema.

### H-05 – Selektive SQLite-Persistenz

**Ergebnis: Die selektive Persistenz ist ausdrücklich spezifiziert; eine bewusste Akzeptanz des Crash-Verlusts kurzer erfolgreicher Finals ist nicht belegt.**

Der historische Fahrplan legt fest:

- jeder Finaltext wird unmittelbar von der Historienkomponente entgegengenommen,
- die letzten Einträge liegen im Arbeitsspeicher,
- nur ausgewählte Einträge werden persistent in SQLite gespeichert,
- persistent gespeichert werden insbesondere:
  - Texte ab `min_characters`,
  - Einträge mit übersprungenem oder technisch fehlgeschlagenem Einfügeversuch,
  - später optional alle Finals.

Konkrete Defaults:

```yaml
min_characters: 1000
store_failed_injections: true
store_all: false
```

Belege:

- `Verbindlicher Umsetzungsfahrplan für die nächste Entwicklungsphase.md`, Zeilen 31–86.
- `IMPLEMENTATION_ROADMAP.md`, Zeilen 49–64.
- HTML-Zeilen 4436–4449 beschreiben ausdrücklich einen kurzen, nicht persistenten Eintrag.
- HTML-Zeilen 4601–4609 dokumentieren die dafür korrigierte Deduplizierung und atomare Persistenz bei fehlgeschlagenen beziehungsweise übersprungenen Versuchen.

Die historische Formulierung „zuerst lokal gesichert“ kann daher innerhalb der damaligen Planung auch eine Aufnahme in die In-Memory-Historie meinen. Sie bedeutet nicht automatisch „jedes Final vor dem Paste auf SQLite committen“.

Nicht gefunden wurde:

- eine begründete Entscheidung aus Datenschutz-, Performance- oder Mengengründen,
- eine ausdrückliche Akzeptanz, dass ein kurzes erfolgreich eingefügtes Final nach Memory-Rotation oder Prozessabbruch dauerhaft verloren sein kann.

Damit besteht weiterhin eine echte Zielunklarheit: Soll „kein Datenverlust“ nur für fehlgeschlagene Einfügungen gelten, oder soll jedes Final crash-sicher sein?

**Konsequenz:** Die aktuelle Implementierung ist nicht versehentlich selektiv, aber E-01 muss vor AP4 ausdrücklich entschieden werden.

### H-06 – Grundlage der Bezeichnung „AP3 abgenommen“

**Ergebnis: Historische inhaltliche Prüfung bestätigt; es war eine Chat-/Agentenabnahme, keine gesonderte formale Benutzerfreigabe.**

Der Verlauf zeigt eine mehrstufige AP3-Prüfung:

1. Ein zunächst gemeldeter Stand mit 24 AP3-Tests und 94 Gesamttests wurde anhand der Dateien geprüft.
2. Dabei wurde eine noch fehlende Fehlerfallabdeckung erkannt.
3. Zwei zusätzliche Tests wurden gefordert.
4. Der ausführende Agent meldete anschließend:
   - 26 Reinsertion-Tests,
   - 29 History-Tests,
   - 41 Text-Injection-Tests,
   - 96 Tests im Gesamtlauf,
   - jeweils `OK`.
5. Für fünf geänderte Dateien wurden Größe und SHA-256-Hash ausgegeben.
6. Die Dateien wurden erneut hochgeladen; die damalige Chat-Session verglich Größe und Hash und stellte Übereinstimmung fest.

Wichtige Belege:

- HTML-Zeilen 897–911: Auftrag für zwei zusätzliche Tests, Testläufe und Hash-Ausgabe.
- HTML-Zeilen 927–954: gemeldete Testausgaben und Hashes.
- HTML-Zeilen 960–1008: Prüfung der Dateien, Aussage „Arbeitspaket 3 ist jetzt sauber abgeschlossen und abgenommen“ und ausdrücklicher Hinweis, dass die Chat-Session den vollständigen Projektlauf nicht selbst wiederholen konnte.

Die damalige Abnahme beruhte daher auf:

- inhaltlicher Dateiprüfung,
- bytegenauer Zuordnung der hochgeladenen Dateien zum Agentenbericht,
- vom ausführenden Agenten gemeldeten erfolgreichen Testläufen.

Sie war nicht identisch mit einer unabhängigen erneuten Ausführung der 96 Tests durch die Chat-Session. Diese unabhängige Reproduzierbarkeit wurde erst im aktuellen Prüfbericht in einer isolierten Kopie festgestellt.

Eine gesonderte ausdrückliche Benutzerformulierung „Ich nehme AP3 ab“ wurde nicht gefunden.

**Konsequenz:** Präzise Bezeichnung: „AP3 wurde in der bisherigen Chat-Session inhaltlich geprüft und als technisch abgeschlossen bewertet; der heutige Prüfbericht hat die 96 Tests unabhängig reproduziert.“ Nicht pauschal „vom Benutzer formal abgenommen“ schreiben.

### H-07 – Antigravity-Dateimaterialisierung und Hashregel

**Ergebnis: Vorfall und AP3-Hashprüfung bestätigt; eine allgemeine Zukunftsregel ist nicht als damaliger Beschluss belegt.**

Der HTML-Verlauf dokumentiert, dass Änderungen im Antigravity-Review sichtbar waren, aber zunächst nicht zuverlässig in den realen Projektdateien materialisiert erschienen. Es wurden mehrere Wiederherstellungswege diskutiert. Der entscheidende Auftrag verlangte anschließend:

- die Dateien erneut direkt in den Projektpfad zu schreiben,
- sie von der Festplatte neu zu lesen,
- Dateigröße und SHA-256-Hash auszugeben,
- die Tests erneut auszuführen.

Der Vergleich der anschließend hochgeladenen Dateien mit den gemeldeten Hashes war erfolgreich.

Belege:

- HTML-Zeilen 8499–8543: Ein hochgeladener Zwischenstand enthielt die letzte AP3-Korrekturrunde noch nicht.
- HTML-Zeilen 8543 ff.: Diskussion des Review-/Materialisierungsproblems.
- HTML-Zeilen 897–964 sowie 1002–1008: abschließende Hash- und Inhaltsprüfung.

Nicht gefunden wurde eine damalige, generell formulierte Regel, dass jedes künftige Arbeitspaket zwingend ein Hashmanifest erhalten muss. Die Hashanforderung war zunächst eine gezielte Reaktion auf genau diesen Materialisierungsfehler.

**Konsequenz:** Ein Hashmanifest ist heute eine sinnvolle neue Verifikationsregel, aber keine bereits historisch verbindlich beschlossene Dauerregel.

### H-08 – AP4 und Exakt-einmal-Semantik

**Ergebnis: Zielreihenfolge und Abnahmekriterium bestätigt; konkrete Integrationsschnittstelle weiterhin offen.**

Historisch festgelegt sind:

- Finaltexte durchlaufen zuerst die Historie und danach die Injection-Queue.
- Doppelte Finals mit gleicher `session_id` und `segment_id` erzeugen keinen zweiten History-Eintrag.
- `TranscriptHistoryManager.add_entry(...)` liefert bei einem bereits nur noch im Deduplizierungs-Cache bekannten Segment `None`.
- `TextInjectionQueue.enqueue(entry)` nimmt einen vorhandenen `HistoryEntry` entgegen.
- Pro tatsächlich angenommenem Queue-Job protokolliert der Queue-Worker genau einen abschließenden Injection-Attempt.
- AP4 hat das Abnahmekriterium „Final-Events werden exakt einmal verarbeitet“.

Nicht festgelegt sind:

- ob AP4 `on_text`, `on_event` oder eine neue Session-/Controller-Schnittstelle verwenden soll,
- welcher Thread beziehungsweise Event-Loop den Übergang besitzt,
- wie die Entscheidung „neuer History-Eintrag“ gegenüber „bereits verarbeitet“ am Controller atomar ausgewertet wird,
- wie Fehler zwischen `add_entry()` und `enqueue()` behandelt werden,
- wie Sessionwechsel nach Reconnect in der Integrationslogik abgegrenzt werden.

Der Chat endet nach der AP3-Abnahme gerade mit der Aufforderung, für AP4 zunächst `app.py`, Session-/Event-Schnittstellen und relevante Serverdokumente zu prüfen. Eine konkrete AP4-Implementierungsentscheidung wurde noch nicht getroffen.

**Konsequenz:** E-03 bleibt offen. Die Roadmap liefert das Ziel, aber noch keinen vollständigen Integrationsvertrag.

### H-09 – Historischer Verifikationsstand von AP1 und AP2

**Ergebnis: Technische Prüfungen und Abschlussbewertungen bestätigt; Testzahlen sind eine nachvollziehbare Entwicklung, kein Widerspruch.**

AP1:

- begann mit 15 Tests,
- wurde nach mehreren Korrekturrunden zunächst mit 26,
- abschließend mit 29 History-Tests dokumentiert.
- HTML-Zeilen 4678 ff. zeigen, dass die damalige Session die tatsächlichen Dateien und Tests prüfte und dabei weitere Probleme wie nicht geschlossene SQLite-Verbindungen fand.
- Erst nach deren Behebung wurde AP1 endgültig geschlossen.

AP2:

- begann mit 24 Text-Injection-Tests,
- erreichte nach Korrekturen 33,
- wurde nach Lifecycle-, Cleanup- und Concurrency-Korrekturen mit 41 Tests abgeschlossen.
- HTML-Zeilen 7225–7245 bezeichnen AP2 als technisch abgenommen und nennen 29 AP1-, 41 AP2- und 70 Gesamttests.

AP3:

- entwickelte sich von 22 über 24 auf 26 Tests.
- Zusammen mit AP1 und AP2 ergibt das 96.

Die unterschiedlichen Zahlen in alten Roadmap-, Task- und Übergabeversionen sind daher überwiegend echte Zwischenstände. Sie dürfen nicht nebeneinander als gleichzeitiger Endstand gelesen werden.

Für AP1 und AP2 wurde kein mit AP3 vergleichbares Hashverfahren dokumentiert. Die damalige Session berichtet jedoch wiederholt eigene Datei- und Testprüfungen. Offene manuelle Punkte blieben auch nach der technischen Abnahme bestehen:

- Notepad-Smoke-Test,
- Mikrofon-End-to-End-Test,
- Final-Event-/`app.py`-Integration.

**Konsequenz:** AP1 und AP2 dürfen als technisch abgeschlossen bezeichnet werden, solange die genannten manuellen und integrativen Restpunkte klar getrennt bleiben.

### H-10 – Zuordnung der Baseline-Korrekturen

**Ergebnis: Frühere Paketgrenzen teilweise bestätigt; die konkreten Baseline-Risiken wurden erst durch den aktuellen Prüfbericht identifiziert.**

Die historischen Roadmaps ordnen zu:

- AP4:
  - Controller-Integration,
  - Core-zu-UI über Qt-Signale,
  - UI-zu-Core über thread-sichere Befehle,
  - keine blockierenden asyncio-Aufrufe im Qt-Main-Thread,
  - bestehender Reconnect soll funktionsfähig bleiben.
- AP5:
  - automatische Wiederherstellung bei Netzwerk- und Mikrofonproblemen,
  - erneutes Öffnen beziehungsweise Wiederverwenden des Mikrofons,
  - modalfreies Fehlerverhalten.

Die konkreten heutigen Befunde:

- direkter fremdthreadiger Zugriff auf `asyncio.Queue`,
- unzuverlässige Ping-Miss-Zählung,
- kein erneutes `start` und keine Wiederaufnahme des Audio-Streamings nach Reconnect,

wurden im bereitgestellten bisherigen Verlauf nicht untersucht. Die charakteristischen Codebegriffe und Fehlerbeschreibungen kommen dort nicht vor.

Damit sind die Vorschläge der Stellungnahme zur „Baseline-Korrektur“ keine bereits historisch getroffenen Entscheidungen, sondern neue Planungsempfehlungen auf Basis des aktuellen Audits.

Sachlich sinnvoll ist folgende Abgrenzung:

- Der thread-sichere Audio-zu-asyncio-Übergang ist eine Voraussetzung für die belastbare Integration und sollte vor oder innerhalb von AP4 gezielt korrigiert und getestet werden.
- Die Ping-Miss-Logik ist eine kleine eigenständige Core-Korrektur und sollte nicht stillschweigend in AP4 versteckt werden.
- Die vollständige Wiederaufnahme von Session, `start` und Mikrofonbetrieb nach Reconnect gehört funktional weiterhin zu AP5, sofern AP4 nicht bereits minimalen Wiederanlauf benötigt, um seine eigenen Tests stabil zu bestehen.

**Konsequenz:** E-05 benötigt einen ausdrücklichen Paketbeschluss vor der nächsten Codeänderung.

## 5. Gefundene Widersprüche und ihre Auflösung

### 5.1 „Headless-Core real getestet“ versus tatsächlich ausgeführter Test

Alte Dokumente verwenden diese Formulierung zu breit. Belegt ist nur der Connection-Smoke-Test. Der Mikrofon-/Audio-/Final-Pfad bleibt offen.

**Auflösung:** Testarten einzeln benennen und nie unter „Live-Test“ zusammenfassen.

### 5.2 Alte Modulnamen versus tatsächliche Projektstruktur

`core/audio_processor.py` und `core/stt_client.py` sind nicht als frühere Dateien nachweisbar. Sie erscheinen nur in zwei späten Tracker-Versionen.

**Auflösung:** Als unbelegte Tracker-Fehler entfernen, nicht als historische Umbenennung erklären.

### 5.3 „Jeder Finaltext zuerst lokal gesichert“ versus selektive SQLite-Persistenz

Die historische Spezifikation unterscheidet In-Memory-Historie und ausgewählte SQLite-Persistenz. Dadurch ist die Implementierung erklärbar, aber „gesichert“ bleibt sprachlich mehrdeutig.

**Auflösung:** Künftig immer getrennt formulieren:

- „in die In-Memory-Historie aufgenommen“,
- „persistent in SQLite gespeichert“,
- „gegen Prozessabbruch crash-sicher“.

Die gewünschte Crash-Sicherheit muss noch entschieden werden.

### 5.4 „Exakt einmal“ als Ziel versus fehlender Integrationsvertrag

Das Abnahmekriterium existiert, aber Callback, Threadgrenze und Fehlerübergang sind nicht spezifiziert.

**Auflösung:** Vor AP4 einen kleinen, testbaren Controller-Vertrag festlegen.

### 5.5 Reconnect vorhanden versus Diktierbetrieb automatisch wiederhergestellt

Transport-Reconnect ist implementiert. Der frühere Zieltext verlangt außerdem, dass der Benutzerwunsch nach Reconnect erhalten bleibt und eine aktive Diktierung wieder aufgenommen wird. Das ist im aktuellen `app.py` noch nicht umgesetzt.

**Auflösung:** Ist- und Zielverhalten in getrennten Abschnitten dokumentieren.

### 5.6 Unterschiedliche Testzahlen

15/26/29, 24/33/41 und 22/24/26 sind Entwicklungsstufen. Sie sind kein sachlicher Widerspruch, wenn die jeweilige Dokumentversion als Zwischenstand gekennzeichnet wird.

**Auflösung:** In der aktiven Übergabe nur den aktuellen Endstand 29/41/26 = 96 nennen; frühere Zahlen ausschließlich in einer Chronologie.

### 5.7 „AP3 abgenommen“

Die Bezeichnung war innerhalb der damaligen Chat-Session nachvollziehbar, kann aber fälschlich wie eine formale Benutzerfreigabe wirken.

**Auflösung:** Art der Prüfung und Prüfer benennen.

### 5.8 Hashmanifest als angeblich schon verbindliche Regel

Hashes wurden nach einem konkreten Antigravity-Materialisierungsproblem eingesetzt. Eine generelle Zukunftsregel wurde damals nicht ausdrücklich beschlossen.

**Auflösung:** Wenn gewünscht, die Regel jetzt neu und ausdrücklich festlegen.

### 5.9 Falscher Host in einer historischen Fahrplanversion

`Verbindlicher Umsetzungsfahrplan für die nächste Entwicklungsphase.md`, Zeile 11, enthält noch `voice.voice.marcosudau.com`.

**Auflösung:** Diese Datei ist nur historische Referenz. Der aktuelle verbindliche Host ist ausschließlich `stt.voice.marcosudau.com`. Alte Versionen dürfen nicht als aktive Quelle verwendet werden.

## 6. Was durch den Fact-Check endgültig geklärt ist

1. Der Connection-Smoke-Test wurde tatsächlich ausgeführt und erfolgreich gemeldet.
2. Er ist kein Mikrofon- oder Transkriptions-End-to-End-Test.
3. Ein solcher Mikrofon-End-to-End-Test ist weiterhin offen.
4. Die alten Modulnamen sind nicht als reale frühere Dateien belegt.
5. Aufnahme und Reinsertion sind zwei verschiedene Hotkey-Aktionen.
6. Selektive SQLite-Persistenz war Teil des verbindlichen AP1-Entwurfs.
7. AP1-, AP2- und AP3-Testzahlen entwickelten sich über Korrekturrunden bis 29/41/26.
8. AP3 wurde nach einem Materialisierungsproblem anhand von Inhalt, Testbericht, Größen und Hashes erneut geprüft.
9. Die damalige Chat-Session hat die 96 Tests nicht selbst erneut ausgeführt; der aktuelle Prüfbericht hat sie später unabhängig reproduziert.
10. AP4 wurde noch nicht implementiert und seine konkrete Event-/Controller-Schnittstelle wurde noch nicht festgelegt.
11. Die spezifischen Thread-, Ping- und Reconnect-Risiken sind neue Auditbefunde, keine bereits erledigten Altentscheidungen.

## 7. Weiterhin offene Entscheidungen

### E-01 – Crash-Sicherheit

Soll jedes Final unabhängig von Länge und späterem Injection-Ergebnis sofort in SQLite gespeichert werden?

Ohne neue Entscheidung bleibt die historische selektive Semantik maßgeblich. Dann muss die Übergabe ausdrücklich sagen, dass kurze erfolgreiche Finals nur im RAM liegen können.

### E-02 – Fehler-/Resultatschnittstelle der Historie

Soll die reale Historie Lesefehler von „kein Eintrag vorhanden“ unterscheiden? Die aktuelle Reinsertion-Fehlersemantik ist sonst bei intern abgefangenen SQLite-Fehlern nicht vollständig erreichbar.

### E-03 – AP4-Controller-Vertrag

Vor der Implementierung festzulegen:

- Eingangsschnittstelle für Server-Events,
- zuständiger Thread/Event-Loop,
- Deduplizierungsentscheidung,
- Verhalten bei `add_entry() -> None`,
- Verhalten bei History- oder Queue-Fehler,
- Sessiongrenze nach Reconnect,
- genau ein Queue-Auftrag je neuem Final.

### E-04 – Hotkey-Konfiguration

Aufnahme- und Reinsertion-Hotkey benötigen getrennte Win32-kompatible Konfigurationsfelder und Validierung.

### E-05 – Reihenfolge der Baseline-Korrekturen

Thread-Bridge und Ping-Logik sollten als explizite, testbare Korrekturpakete vor oder zu Beginn von AP4 eingeordnet werden. Die vollständige Reconnect-Selbstheilung bleibt AP5.

### E-06 – Repository- und Dokumentationshygiene

Noch separat zu bereinigen:

- relative Testpfade, die SQLite-Dateien im Projekt erzeugen,
- `config_path.db` und `param_path.db`,
- Cache-/Ignore-Regeln,
- veraltete Root-README,
- aktive Übergabe, `task.md` und Roadmap.

Diese Prüfung hat entsprechend der Benutzeranweisung nichts davon verändert.

### E-07 – Reproduzierbarer Übergabestand

Zu entscheiden ist, ob künftig:

- ein separates Hashmanifest,
- ein Git-Commit,
- oder beides

den übergebenen Dateistand eindeutig bezeichnet. Ein Git-Commit wäre die klarste Variante, sofern das Projekt als Repository geführt wird.

## 8. Empfohlene Reihenfolge der nächsten Schritte

1. Die Entscheidungen E-01 bis E-05 ausdrücklich treffen.
2. Eine korrigierte aktive Übergabe erstellen, die Ist, Ziel und offene Tests klar trennt.
3. `task.md`, Roadmap und README anschließend konsistent angleichen.
4. Repository-/Testartefakte in einem kleinen Hygiene-Arbeitspaket bereinigen.
5. Thread-Bridge und Ping-Miss-Logik in abgegrenzten Korrekturpaketen reproduzierbar testen.
6. AP4 mit einem vorher festgelegten Controller-Vertrag implementieren.
7. Danach den manuellen Notepad-Test und einen echten Serverlauf vom Mikrofon bis zum Finaltext durchführen.
8. AP5 für die vollständige modalfreie Reconnect- und Mikrofon-Selbstheilung umsetzen.
9. Den finalen Übergabestand mit Commit oder Hashmanifest eindeutig fixieren.

## 9. Formulierungsvorschlag für den künftigen Kurzstatus

> Implementiert und automatisiert verifiziert sind die drei isolierten Komponenten Transkript-Historie, Text-Injection-Queue und Reinsertion. Ihre 96 Tests laufen erfolgreich, decken jedoch weder den Headless-Audio-/WebSocket-Pfad noch `app.py`, UI, Hotkeys oder End-to-End-Betrieb ab. Historisch erfolgreich ausgeführt wurde ein Health-/WebSocket-Handshake-/Ping-Pong-Smoke-Test gegen `stt.voice.marcosudau.com`. Ein echter Mikrofon-bis-Finaltext-Test ist weiterhin offen. Der vorhandene `STTSession`-Core kann die Transportverbindung neu aufbauen, nimmt den Diktierbetrieb nach einem Verbindungsabbruch aber noch nicht vollständig automatisch wieder auf. AP4 Controller-Integration ist der nächste reguläre Funktionsschritt; zuvor beziehungsweise zu seinem Beginn sind der Controller-Vertrag, die gewünschte Crash-Sicherheit der Finals und die Einordnung der Thread-/Ping-Korrekturen verbindlich festzulegen.

## 10. Abschlussbewertung

Die größte Gefahr der bisherigen Übergabe war nicht ein einzelner falscher Wert, sondern die Vermischung verschiedener Aussagearten:

- tatsächlicher aktueller Code,
- erfolgreich getestete isolierte Komponenten,
- historische Smoke-Tests,
- noch nicht umgesetztes Zielverhalten,
- und spätere Planungsempfehlungen.

Nach Stellungnahme und Fact-Check lässt sich diese Vermischung auflösen. Der Projektstand ist grundsätzlich gut rekonstruierbar und AP1 bis AP3 sind belastbar vorhanden. Für eine wirklich eindeutige neue Übergabe müssen nun vor allem die noch offenen Produktentscheidungen benannt werden, statt sie durch Formulierungen wie „lokal gesichert“, „Reconnect vorhanden“, „exakt einmal“ oder „abgenommen“ scheinbar vorwegzunehmen.
