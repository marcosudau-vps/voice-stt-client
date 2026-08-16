# AP04 – Ausführungsauftrag Controller-Integration

> **Status:** ausgeführt und abgenommen; historischer operativer AP4-Vertrag  
> **Stand:** 25. Juli 2026  
> **Adressat:** ausführender Implementierungsagent  
> **Review:** am 25. Juli 2026 nach drei Korrekturrunden und unabhängiger Fertigstellung abgenommen  
> **Scope:** ausschließlich AP4; nach Abschluss stoppen

> **Nummerierungsnachtrag vom 2. August 2026:** „AP7-Polish“ in diesem
> historischen Auftrag heißt nach der verbindlichen Neuplanung AP8. AP7 ist nun
> das Feedback- und Eventsystem.

## 1. Auftrag

Implementiere AP4 vollständig: Verbinde den vorhandenen WebSocket-/Audio-Core,
die Transkript-Historie, die Text-Injection-Queue und den Reinsertion-Service in
einem gemeinsamen, UI-neutralen Controller-Lifecycle.

Nach AP4 muss ein gültiges neues `final`-Serverevent:

```text
final
  → stabile (session_id, segment_id)-Identität
  → genau ein aufgelöster HistoryEntry
  → höchstens ein automatischer Queue-Job
  → Clipboard + SendInput durch den vorhandenen Queue-Worker
  → genau ein finaler Attempt für den angenommenen Job
```

durchlaufen.

Realtime-Zwischentext darf niemals als Finaltext gespeichert oder automatisch
eingefügt werden. Eine bewusste Reinsertion darf weiterhin zusätzliche
Queue-Jobs und Attempts am bereits vorhandenen HistoryEntry erzeugen.

## 2. Paketgrenze

### Bestandteil

- UI-neutraler Controller und dessen Ergebnis-/Statusmodell;
- gemeinsamer Lifecycle für `STTSession`, `AudioCapture`,
  `TranscriptHistoryManager`, `TextInjectionQueue` und
  `TranscriptReinsertionService`;
- Integration in den tatsächlich gestarteten Headless-Pfad;
- autoritativer Finalevent-Eingang;
- History-before-enqueue;
- automatische Final-Deduplizierung;
- Reinsertion-Befehle über den bestehenden Service;
- deterministischer Start und Shutdown;
- gezielte Controller- und Integrationstests;
- vollständige Regression;
- Abschlussdokumentation von AP4.

### Ausdrücklich nicht Bestandteil

- PySide6, Tray, Overlay oder Qt-Signale;
- globale Hotkeys oder ein konkretes Tastenschema;
- Single-Instance-Guard;
- E-07, Betriebsmodusselector, Wake-Word-Override oder Admin-Service;
- neue Serverbefehle oder ein neuer Serververtrag;
- AP5-Reconnect-Härtung oder Reparatur der Ping-Miss-Erkennung;
- Mikrofon-Hot-Plug, Sleep/Wake oder Gerätewechsel;
- AP7-Polish, Autostart oder Langzeit-Stresstests;
- allgemeine Refactorings funktionierender Komponenten;
- neue Abhängigkeiten ohne nachgewiesene technische Notwendigkeit.

## 3. Kontextschonende Pflichtlektüre

Die Reihenfolge ist verbindlich und absichtlich von allgemein zu unmittelbar
implementierungsrelevant geordnet.

### 3.1 Vollständig lesen

1. `AGENTS.md`
2. `docs/ARBEITSWEISE_UND_DOKUMENTATIONSORDNUNG.md`
3. `docs/PROJEKTUEBERSICHT.md`
4. `docs/IMPLEMENTATION_ROADMAP.md`
5. `ÜBERGABE.md`
6. `task.md`
7. diese Datei
8. `server-docs-for-client-development/README.md`

### 3.2 Paketvertrag gezielt gegenprüfen

Aus `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md` nur diese Abschnitte
zusätzlich lesen:

- 1. Ziel des Arbeitspakets;
- 2. Nicht Bestandteil von AP4;
- 3. Verbindliche Quellen;
- 4. Ausgangslage vor AP4;
- 8. Verbindlicher Integrationsfluss;
- 9. Controller-Verantwortlichkeiten;
- 10. Lifecycle und Shutdown.

Die Komponenten-, Entscheidungs-, Test- und Abnahmeverträge sind in diesem
Ausführungsauftrag bereits operativ zusammengeführt. Bei einem Widerspruch
nicht beide Varianten vermischen, sondern vor der Codeänderung den Konflikt
melden.

### 3.3 Serververtrag gezielt lesen

Nicht alle Serverdokumente vollständig laden. Mit Überschriften- und
Stichwortsuche genau diese Bereiche lesen:

- `01-session-und-server-scope.md`
  - Kurzfassung;
  - Besitz- und Isolationsmatrix;
  - Session-Lebenszyklus.
- `02-websocket-protokoll.md`
  - Verbindungs-Handshake;
  - Clientbefehle;
  - Segmentvertrag;
  - Verbindungsende und Reconnect.
- `03-server-events-kurzreferenz.md`
  - vollständig; dies ist die kompakte Eventreferenz.
- `04-server-events-katalog-und-chronologie.md`
  - `realtime`;
  - `final`;
  - `error`;
  - Forward-Compatibility.
- `05-client-zustandsmodell.md`
  - empfohlenes State-Schema;
  - Event-Reducer;
  - Realtime-Upsert;
  - Final-Upsert;
  - Reconnect-Automat;
  - Persistenz im Client.
- `07-robustheit-grenzen-und-sicherheit.md`
  - Fehlerstrategie;
  - Race Conditions, die der Client tolerieren muss;
  - Abnahmetest-Checkliste für Textmodell und Fehler.

Für AP4 nicht pauschal lesen:

- Admin-/HTTP-Details aus Kapitel 06;
- Protokollvergleich aus Kapitel 08;
- Betriebsmodus-/Adminplanung aus Kapitel 09;
- `docs/evaluations/`;
- Archive und datierte Übergabeordner.

### 3.4 Implementierungsoberfläche vollständig lesen

- `app.py`
- `core/config.py`
- `core/audio_capture.py`
- `core/stt_session.py`
- `core/history.py`
- `core/text_injector.py`
- `core/reinsertion.py`
- `tests/test_app.py`
- `tests/test_history.py`
- `tests/test_text_injector.py`
- `tests/test_reinsertion.py`
- `config.yaml`

`requirements.txt` nur auf neue Abhängigkeiten prüfen. Es sollen keine neuen
Abhängigkeiten eingeführt werden.

Andere Dateien nur öffnen, wenn eine konkrete Symbolreferenz oder ein
fehlgeschlagener Test sie erforderlich macht.

## 4. Pflicht-Baseline vor Änderungen

Nur die Projektumgebung verwenden:

```powershell
.\venv\Scripts\python.exe --version
.\venv\Scripts\python.exe -m unittest tests.test_app tests.test_history tests.test_text_injector tests.test_reinsertion
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Erwarteter Ausgangsstand:

```text
103 Tests
OK
```

Weicht die Baseline ab, vor jeder Codeänderung Ursache und genaue Fehler
melden. Keine vorhandenen Tests löschen, abschwächen oder überspringen, um eine
grüne Suite zu erzeugen.

## 5. Verbindliche Entscheidungen für AP4

Diese Festlegungen lösen E-01 bis E-04 für dieses Paket. Sie dürfen nur
verlassen werden, wenn der tatsächliche Code ihre technische Unmöglichkeit
belegt. In diesem Fall vor der Implementierung stoppen und den konkreten
Blocker mit Codefundstellen melden.

### E-01 – Bedeutung „vor Paste gesichert“

- Ein Finaltext muss vor jedem automatischen Enqueue als stabiler
  `HistoryEntry` im `TranscriptHistoryManager` vorliegen.
- Die vorhandene selektive SQLite-Politik bleibt unverändert.
- AP4 führt weder `store_all=true` als neuen Default noch eine persistente
  Outbox ein.
- Die bestehende Grenze bleibt dokumentiert: Kurze erfolgreiche Finaltexte
  können nur im RAM liegen und bei Prozessabsturz verloren gehen.
- Ohne stabilen HistoryEntry erfolgt kein automatischer Paste-Versuch.

### E-02 – History-Fehler

- Der Controller muss „Entry vorhanden“, „Duplikat“ und
  „History nicht verfügbar“ unterscheiden können.
- Falls die bestehende Rückgabe von `add_entry()` dafür nicht genügt, ist die
  kleinstmögliche rückwärtskompatible History-Erweiterung einzuführen, zum
  Beispiel ein zusätzliches Ergebnisobjekt oder eine neue Methode.
- Die bestehende öffentliche `add_entry()`-Semantik darf nicht stillschweigend
  gebrochen werden.
- Bei deaktivierter oder fehlgeschlagener History wird nicht automatisch
  eingefügt.
- Persistente Lesefehler außerhalb des normalen Finalpfads bleiben
  best-effort, sofern AP4 sie nicht zuverlässig unterscheiden kann; diese
  Grenze ist als bekannte Abweichung zu dokumentieren und nicht durch einen
  breiten AP1-Refactor zu lösen.

### E-03 – Autoritativer Finalevent-Eingang

- Das rohe Serverevent `type == "final"` ist die autoritative Quelle für die
  automatische History-/Injection-Verarbeitung.
- Nur dort liegen `sessionId`, `segmentId` und `text` als zusammengehöriger
  Serververtrag vor.
- `on_text` bleibt für reduzierte Realtime-/Finaldarstellung zulässig, ist aber
  nicht die Identitätsquelle für den automatischen Enqueue.
- `timeline(event=final_transcript)` ist Diagnostik und keine zweite
  Transkriptquelle.
- Der Controller validiert:
  - `sessionId`: nicht leerer String;
  - `segmentId`: Ganzzahl, kein Boolean, nicht negativ;
  - `text`: nicht leerer String nach fachlich begründeter Validierung.
- Deduplizierungsschlüssel ist `(sessionId, segmentId)`.
- Dieselbe `segmentId` in einer neuen Session ist ein neuer Finaltext.
- Ein identisches doppeltes Finalevent erzeugt keinen zweiten Queue-Job.
- Ein widersprüchlicher zweiter Finaltext mit derselben Identität und anderem
  Text erzeugt ebenfalls keinen zweiten automatischen Queue-Job; er wird als
  Protokollwiderspruch protokolliert und im Controllerstatus gemeldet.
- Ein abgelehnter oder fehlgeschlagener automatischer Queue-Versuch wird nicht
  später durch ein doppeltes Serverevent automatisch wiederholt.
- Bewusste Reinsertion bleibt der vorgesehene manuelle Wiederholungsweg.

### E-04 – Hotkey-Abgrenzung

- AP4 implementiert keinen Hotkey und interpretiert keine Zeichenfolge wie
  `<ctrl>+<shift>+space`.
- Die Controller-API bietet nur semantische Diktierbefehle, ohne Kenntnis einer
  Taste oder eines UI-Frameworks.
- Das spätere Win32-Tastenschema bleibt AP6.

### E-05 bis E-07

- E-05: Die korrigierte Audio-Thread-Brücke wird beibehalten und durch die
  bestehenden Tests geschützt.
- Ping-Miss-Erkennung und die genaue Reconnect-Semantik bleiben AP5.
- Nachtrag vom 25. Juli 2026: AP5 wurde inzwischen verbindlich abgegrenzt.
  Nach ADR-002 heilt sich der Transport, ein unterbrochenes Diktat wird jedoch
  beendet und nicht wiederaufgenommen. Dieser Nachtrag ändert keinen
  AP4-Abnahmenachweis.
- E-06 Repository-Hygiene wird nicht in AP4 hineingezogen.
- E-07 bleibt eine getrennte, nicht blockierende Serverevaluierung. Kein
  Modusselector, Admin-Key oder Wake-Word-Override in AP4.

## 6. Implementierungsvertrag

### 6.1 Controller

Lege eine klar benannte UI-neutrale Controllerkomponente unter `core/` an.
Bevorzugter Name:

```text
core/controller.py
```

Die konkrete Klassennennung darf sich am vorhandenen Stil orientieren. Die
Komponente muss:

- die AP1–AP3-Instanzen konsistent verdrahten;
- dieselbe History-Instanz an Queue und Reinsertion-Service übergeben;
- die Queue vor Callbackannahme starten;
- STTSession-Callbacks anbinden;
- Final- und Realtime-Pfade trennen;
- automatische Finalidentitäten innerhalb des Controller-Lebenszyklus
  deduplizieren;
- semantische Diktierbefehle anbieten;
- Reinsertion-Befehle durchreichen;
- Recent-Entries und Controllerstatus UI-neutral bereitstellen;
- während Shutdown keine neuen Befehle oder Finals annehmen;
- alle selbst gestarteten Komponenten deterministisch stoppen.

Abhängigkeiten sollen für Tests injizierbar sein. Produktionsdefaults dürfen
die realen Komponenten erzeugen, Tests müssen jedoch ohne Mikrofon, echten
WebSocket und echte Win32-Tasteneingaben laufen.

### 6.2 Headless-Integration

Der Controller darf kein unbenutztes Nebenmodul bleiben. `app.py` muss den
neuen Controller im regulären Headless-Startpfad verwenden.

Dabei:

- bestehende Konsolenausgabe für Realtime und Final erhalten;
- korrigierte `call_soon_threadsafe`-Audiobrücke erhalten;
- keinen automatischen realen Paste-Test beim Start hinzufügen;
- keine PySide6-Abhängigkeit einführen;
- keine funktionierende Audio-/WebSocket-Logik ohne Not neu schreiben.

Wenn die kleinste sichere Lösung den bestehenden `RealtimeSTTClient` aus
`app.py` teilweise in den Core-Controller verschiebt, müssen alle sieben
Audio-Bridge-Regressionen angepasst und weiterhin inhaltlich gleichwertig
bestanden werden. Kein Test darf nur wegen einer Verschiebung entfallen.

### 6.3 Startreihenfolge

Mindestens:

```text
Konfiguration
  → History
  → InjectionQueue erstellen
  → InjectionQueue.start()
  → RUNNING bestätigen
  → ReinsertionService
  → Callbacks aktivieren
  → STTSession/Audio-Laufzeit
```

Ein Teilfehler muss bereits gestartete Komponenten wieder kontrolliert
abbauen.

### 6.4 Finalverarbeitung

Der Verarbeitungspfad muss logisch atomar gegen doppelte Callbackannahme sein.
Eine zulässige Sequenz:

```text
raw final empfangen
  → closing prüfen
  → Felder validieren
  → Identität reservieren
  → History-Create-or-Resolve mit eindeutigem Ergebnis
  → nur bei neuem zulässigem Final enqueue
  → Ergebnisstatus veröffentlichen
```

Erforderliche Fälle:

- neu + History erfolgreich + Queue akzeptiert:
  `queued`;
- Duplikat:
  `deduplicated`;
- ungültige Identität:
  `invalid_final`;
- History nicht verfügbar:
  `history_unavailable`, kein Enqueue;
- Queue nicht laufend oder lehnt ab:
  `queue_unavailable`, `skipped`-Attempt best-effort;
- Enqueue wirft:
  `failed`, `failed`-Attempt best-effort;
- angenommener Job scheitert später:
  vorhandener Queue-Worker schreibt genau einen `failed`-Attempt.

Statusnamen dürfen stilistisch angepasst werden, müssen aber eindeutig,
testbar und UI-neutral sein.

### 6.5 Realtime

`realtime` darf:

- Anzeige-/Statuscallbacks aktualisieren;
- den reduzierten STT-Zustand verwenden.

`realtime` darf niemals:

- `HistoryEntry` erzeugen;
- `TextInjectionQueue.enqueue()` aufrufen;
- einen InjectionAttempt erzeugen.

### 6.6 Reinsertion

Controllerbefehle müssen den vorhandenen
`TranscriptReinsertionService` verwenden:

- letzten Text erneut einfügen;
- ausgewählten Eintrag erneut einfügen;
- letzte Einträge abfragen.

Keine Reinsertion darf einen neuen HistoryEntry erzeugen. Der vorhandene
Queue-/Attempt-Vertrag bleibt unverändert.

### 6.7 Shutdown

Mindestens:

```text
closing setzen
  → neue Befehle/Finals abweisen
  → Audio stoppen
  → Serverstream/STTSession stoppen
  → Core-Tasks beenden
  → InjectionQueue leeren/stoppen
  → History cleanup
  → Event-Loop freigeben
```

Ein Queue-Stop-Timeout darf nicht verschluckt werden. Der Controller muss einen
auswertbaren Fehlerstatus beziehungsweise eine Exception liefern. Kein
nicht-daemonisierter Worker darf unbemerkt zurückbleiben.

## 7. Testauftrag

Lege mindestens an:

```text
tests/test_controller.py
```

Weitere kleine Integrationstestdateien sind zulässig, wenn dadurch
Verantwortlichkeiten klarer bleiben.

### 7.1 Verdrahtung und Lifecycle

- Queue startet vor der ersten Callbackannahme.
- Queue und Reinsertion erhalten dieselbe History-Instanz.
- Start ist gegen unbeabsichtigte Doppelinitialisierung geschützt.
- Teilfehler beim Start räumt bereits gestartete Komponenten auf.
- Shutdown stoppt jede gestartete Komponente genau einmal.
- Shutdown ist bei wiederholtem Aufruf sicher.
- Queue-Stop-Timeout wird sichtbar.
- Nach `closing` werden keine neuen Finals oder Benutzerbefehle angenommen.

### 7.2 Final und Deduplizierung

- neues gültiges Final erzeugt genau einen Entry und einen Enqueue;
- identisches doppeltes Final erzeugt keinen zweiten Enqueue;
- widersprüchliches doppeltes Final erzeugt keinen zweiten Enqueue und meldet
  Konflikt;
- gleiche `segmentId` in anderer Session wird separat verarbeitet;
- Final ohne stabile Session-ID wird abgewiesen;
- ungültige Segment-ID wird abgewiesen;
- leerer/ungültiger Finaltext wird abgewiesen;
- Timeline-`final_transcript` erzeugt keinen Enqueue;
- Realtime erzeugt weder Entry noch Enqueue;
- Callback-Exception beendet die Session nicht und wird sichtbar protokolliert.

### 7.3 Fehlerpfade

- History deaktiviert;
- History-Create schlägt fehl;
- vorhandener History-Duplikatfall;
- Queue noch nicht gestartet;
- Queue bereits gestoppt;
- `enqueue()` liefert `False`;
- `enqueue()` wirft Exception;
- Attempt-Protokollierung schlägt zusätzlich fehl;
- Final während Shutdown;
- Sessionwechsel rund um Finalevents.

### 7.4 Reinsertion

- `reinsert_last()` läuft über denselben Queuepfad;
- `reinsert_entry()` läuft über denselben Queuepfad;
- Reinsertion erzeugt keinen neuen HistoryEntry;
- zusätzliche Reinsertion darf zusätzlichen Attempt erzeugen;
- `empty_history`, `entry_not_found`, `queue_unavailable` und `failed` werden
  unverändert beziehungsweise eindeutig weitergegeben.

### 7.5 Audio- und App-Regression

- alle sieben bisherigen Audio-Bridge-Tests bleiben erhalten;
- Audio vor erfolgreichem `start` bleibt verworfen;
- Fremdthread-Übergabe verwendet weiterhin `call_soon_threadsafe`;
- Stop-/Loop-Ende-/Queue-Voll-Grenzen bleiben unverändert;
- `app.py` verwendet im echten Startpfad den Controller.

## 8. Verifikationsbefehle

Nach jeder relevanten Korrektur zuerst gezielt:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_controller -v
.\venv\Scripts\python.exe -m unittest tests.test_app -v
.\venv\Scripts\python.exe -m unittest tests.test_history tests.test_text_injector tests.test_reinsertion
```

Danach vollständig:

```powershell
.\venv\Scripts\python.exe -m unittest discover -s tests -p "test_*.py"
```

Zusätzlich:

```powershell
$ap4CompileTargets = @((Resolve-Path -LiteralPath app.py).Path)
$ap4CompileTargets += (Get-ChildItem -LiteralPath core -Filter *.py -File).FullName
$ap4CompileTargets += (Get-ChildItem -LiteralPath tests -Filter 'test_*.py' -File).FullName
.\venv\Scripts\python.exe -m py_compile @ap4CompileTargets
```

Keine global installierte Python-Version verwenden.

Ein realer Mikrofon-/Paste-Test ist für die automatisierte AP4-Abnahme nicht
erforderlich und darf nicht unangekündigt Tastatureingaben in die fokussierte
Anwendung senden. Ein späterer manueller Smoke-Test erfolgt nur kontrolliert
mit ausdrücklicher Benutzerbeteiligung.

## 9. Dokumentationsabschluss

Nach grüner Gesamtsuite:

1. `docs/work-packages/AP04_CONTROLLER_INTEGRATION.md`
   - Entscheidungen E-01 bis E-04 als umgesetzt markieren;
   - tatsächlich gewählte API und Fehlersemantik dokumentieren;
   - Testzahlen und Abnahmekriterien aktualisieren.
2. `task.md`
   - AP4-Arbeitsschritte und genaue Testzahlen aktualisieren.
3. `docs/IMPLEMENTATION_ROADMAP.md`
   - AP4 nur bei vollständiger Erfüllung auf abgeschlossen setzen.
4. `ÜBERGABE.md`
   - neuen Controller, Startpfad, Tests und bekannte Grenzen dokumentieren.
5. `docs/PROJEKTUEBERSICHT.md`
   - Paketstand und Kurzstatus synchronisieren.
6. `README.md`
   - nur ändern, wenn sich der reguläre Benutzerstart tatsächlich ändert.

E-07 und das Evaluierungsdokument nicht inhaltlich entscheiden oder als
abgeschlossen markieren.

## 10. Abgabeformat des ausführenden Agenten

Die Abschlussmeldung muss enthalten:

1. umgesetzte Architektur in wenigen präzisen Punkten;
2. Liste aller geänderten und neu angelegten Dateien;
3. getroffene E-01-bis-E-04-Umsetzung;
4. gezielte Testergebnisse mit Anzahl und Laufzeit;
5. Ergebnis der vollständigen Testsuite mit Anzahl und Laufzeit;
6. Ergebnis von `py_compile`;
7. ausdrücklich nicht umgesetzte spätere Pakete;
8. verbleibende Risiken oder nicht automatisierbare manuelle Prüfungen.

Keine pauschale Aussage „alles funktioniert“ ohne Befehle und Ergebnisse.

## 11. Getrennter Review- und Korrekturzyklus

Die Umsetzung ist nach der Agentenabgabe noch nicht automatisch abgenommen.
Der prüfende Agent führt anschließend unabhängig aus:

1. Scope- und Dateiprüfung;
2. Quellcodeprüfung gegen diesen Vertrag;
3. Prüfung der Deduplizierungs-, Fehler- und Shutdownpfade;
4. gezielte Tests;
5. vollständige Regression;
6. Dokumentationskonsistenzprüfung.

Bei Abweichungen erhält der ausführende Agent einen eng begrenzten Folgeauftrag:

```text
AP4-Korrekturrunde N

Befund:
<reproduzierbarer Fehler mit Datei/Symbol/Test>

Soll:
<konkretes Vertragsverhalten>

Auftrag:
<kleinstmögliche Korrektur>

Pflichttests:
<gezielte Tests plus Gesamtsuite>

Nicht ändern:
<Scope-Schutz>
```

Dieser Zyklus wird wiederholt, bis:

- alle AP4-Abnahmekriterien nachweislich erfüllt sind;
- alle gezielten und vollständigen Tests bestehen;
- keine bekannte Scope-Verletzung verbleibt;
- Dokumentation und tatsächlicher Codezustand übereinstimmen.

Danach wird AP4 abgenommen und beendet. Nicht mit AP5 oder AP6 fortfahren.
