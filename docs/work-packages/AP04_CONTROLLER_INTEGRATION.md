# AP04 – Controller-Integration von Historie, Textinjektion und Reinsertion

> **Status:** umgesetzt und verifiziert `[ABGESCHLOSSEN]`  
> **Stand:** 25. Juli 2026 (nach unabhängiger Abschlussabnahme)  
> **Zuständig für:** Scope, Komponentenverträge, Integrationsfluss, umgesetzte Integrationsentscheidungen und Abnahmekriterien von AP4  
> **Letzte Verifikation:** 152 automatische Tests am 25. Juli 2026 erfolgreich (46 Controller-Tests, 9 App-Tests, 30 History-Tests, 67 AP2/AP3-Unittests, `py_compile` Exit-Code 0)  
> **Operativer Auftrag:** `docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`

> **Nummerierungsnachtrag vom 2. August 2026:** Historische Verweise dieses
> abgeschlossenen Vertrags auf „AP7“ als allgemeine Härtung bezeichnen nach der
> verbindlichen Neuplanung AP8. AP7 ist nun das Feedback- und Eventsystem.

> **Nachtrag vom 25. Juli 2026:** Die nach AP4 noch offene Folgesemantik ist
> inzwischen festgelegt: AP5 übernimmt stille Transportheilung, Ping/Pong und
> den endgültigen Diktatabbruch bei Sessionverlust. Mikrofon-Hot-Plug,
> Gerätewechsel und Sleep/Wake gehören zu AP8. Maßgeblich ist ADR-002; der
> historische AP4-Abnahmenachweis bleibt unverändert gültig.

## 1. Ziel des Arbeitspakets

AP4 verbindet erstmals die drei bereits isoliert implementierten Komponenten:

1. `TranscriptHistoryManager` aus AP1,
2. `TextInjectionQueue` aus AP2,
3. `TranscriptReinsertionService` aus AP3,

mit dem vorhandenen STT-Core und einem gemeinsamen, UI-neutralen Controller-Lifecycle.

Nach AP4 muss ein finales Serversegment kontrolliert von der STT-Session bis zum serialisierten Einfügeversuch gelangen. Realtime-Zwischentext darf nie in die Injection-Queue gelangen.

## 2. Nicht Bestandteil von AP4

AP4 implementiert nicht:

- PySide6, Tray oder Overlay,
- globale Hotkeys oder Single-Instance-Guard,
- grafische Verlaufsauswahl,
- breite Mikrofon-, Sleep/Wake- oder Reconnect-Härtung aus späteren Paketen,
- Autostart, DPI-Polish oder Langzeit-Stresstests aus AP7,
- einen neuen Serververtrag,
- vorsorgliche Refactorings des funktionierenden Core.

Der AP4-Controller bleibt frei von PySide6. Er muss jedoch Zustände und Befehle so klar anbieten, dass AP6 später eine Qt-Signalbrücke darum legen kann.

---

## 3. Verbindliche Quellen

In absteigender Zuständigkeit:

1. `server-docs-for-client-development/` für Events, Session-Lebenszyklus und Protokoll,
2. `docs/IMPLEMENTATION_ROADMAP.md` für Zielarchitektur und Paketgrenze,
3. vorhandener Code und erfolgreich ausführbare Tests für den realen Iststand,
4. `task.md` für Fortschritt und Restpunkte,
5. `ÜBERGABE.md` für den operativen Einstieg.

Diese Datei konkretisiert AP4, darf aber keinen abweichenden Serververtrag erfinden.

---

## 4. Ausgangslage vor AP4

### Aktueller Laufzeitpfad

```text
AudioCapture
  → app.py::_on_audio_packet_from_thread()
  → asyncio.Queue
  → app.py::_audio_sender()
  → STTSession.send_audio()
  → Server

Serverevent
  → STTSession._apply_event()
  → STTSession.on_text(segment_id, text, is_final)
  → app.py::_on_text()
  → Konsolenausgabe
```

Historie, Injection-Queue und Reinsertion-Service werden in diesem Pfad noch nicht erzeugt oder gestartet.

### Aktuelle STTSession-Eingänge

`STTSession` bietet:

- `on_text(segment_id, text, is_final)` für neue oder geänderte reduzierte Segmente,
- `on_event(event_type, raw_event)` für jedes Roh-Event,
- `on_state_change(state)` für den reduzierten Gesamtzustand,
- `on_transport_change(transport_state)` für Transportwechsel.

Relevante Besonderheiten:

- `on_text` enthält keine `session_id`.
- `on_event` enthält das Roh-Event, wird aber auch bei wiederholten Roh-Events ausgelöst.
- `STTSession.state.session_id` hält die aktuelle Session-ID.
- Ein byte-identisches wiederholtes Finalsegment löst `on_text` derzeit nicht erneut aus, weil nur neue oder geänderte Segmente gemeldet werden.
- Callback-Exceptions werden in `STTSession` protokolliert und beenden die Session nicht.

Der AP4-Eventeingang und dessen Exactly-once-Semantik müssen vor der Implementierung ausdrücklich festgelegt werden.

---

## 5. Komponentenvertrag AP1 – `TranscriptHistoryManager`

### Öffentliche Datenobjekte

`HistoryEntry` enthält mindestens:

- `id`
- `session_id`
- `segment_id`
- `timestamp`
- `text`
- `text_length`
- `attempts`

`InjectionAttempt` dokumentiert einen einzelnen Versuch am vorhandenen Eintrag.

### Öffentliche Schnittstellen

```python
add_entry(session_id, segment_id, text, timestamp=None) -> Optional[HistoryEntry]
record_injection_attempt(entry_id, status, error=None, timestamp=None)
get_memory_entries()
get_persistent_entries(limit=None)
cleanup()
```

### Garantien

- thread-sicherer Zugriff,
- Deduplizierung über `(session_id, segment_id)`,
- SQLite-`UNIQUE`-Schutz für dieselbe Identität,
- defensive tiefe Kopien für öffentliche Leseergebnisse,
- append-only Attempts,
- In-Memory-Fallback bei mehreren SQLite-Fehlern.

### Für AP4 relevante Grenzen

1. `add_entry()` kann bei einem Duplikat einen vorhandenen Eintrag zurückgeben. Der Rückgabewert sagt nicht, ob der Eintrag in diesem Aufruf neu erzeugt wurde.
2. Wurde ein nur im RAM gespeicherter Eintrag bereits verarbeitet und später aus dem RAM rotiert, kann `add_entry()` für das Duplikat `None` liefern.
3. Kurze erfolgreiche Finaltexte werden mit den aktuellen Defaults zunächst nur im RAM gehalten.
4. `get_persistent_entries()` protokolliert SQLite-Fehler und kann `[]` zurückgeben. Der Aufrufer kann dann „leer“ und „Lesefehler“ nicht unterscheiden.
5. Die Deduplizierung verhindert doppelte History-Einträge, beweist allein aber noch nicht, dass nur ein Queue-Job erzeugt wurde.

### Aktuelle Defaults

| Einstellung | Wert |
|---|---:|
| `history.enabled` | `true` |
| `memory.max_entries` | `5` |
| `persistent.enabled` | `true` |
| `persistent.max_entries` | `100` |
| `persistent.retention_days` | `0` |
| `persistent.min_characters` | `1000` |
| `persistent.store_failed_injections` | `true` |
| `persistent.store_all` | `false` |

---

## 6. Komponentenvertrag AP2 – `TextInjectionQueue`

### Öffentliche Schnittstellen

```python
start() -> None
enqueue(entry: HistoryEntry) -> bool
stop(timeout=None) -> None
is_running() -> bool
queue_size() -> int
```

### Lifecycle

```text
NEW → INITIALIZING → RUNNING → STOPPING → STOPPED
```

### Garantien

- genau ein nicht-daemonisierter Worker,
- FIFO-Abarbeitung angenommener Jobs,
- defensive Übernahme der Entry-Daten in einen unveränderlichen Queue-Job,
- Jobs werden nur im Zustand `RUNNING` angenommen,
- Ziel-Foreground-Window wird unmittelbar vor `Ctrl+V` erfasst,
- keine Aktivierung eines früheren Fensters,
- Clipboard-Zugriff über ein Message-only Owner-Window,
- sequenzgeschützte optionale Wiederherstellung,
- genau ein finaler Attempt pro angenommenem Job.

### Ergebnis- und Attempt-Semantik

Der Worker dokumentiert am History-Eintrag:

- `command_sent`, wenn Clipboard-Schreiben und `SendInput` erfolgreich durchlaufen,
- `failed`, wenn der Job technisch scheitert,
- ergänzende Metadaten beziehungsweise Fehlermeldung gemäß bestehender Implementierung.

`SendInput` kann nur die gesendeten Tastenereignisse bestätigen. Es beweist nicht, dass eine Zielanwendung den Text semantisch angenommen hat.

### Für AP4 relevante Grenzen

- `enqueue()` liefert nur Annahme oder Ablehnung; die spätere Ausführung ist asynchron.
- Die Queue muss vor dem ersten Enqueue vollständig `RUNNING` sein.
- Nach `STOPPED` ist kein normaler Neustart desselben Queue-Objekts vorgesehen.
- Ein abgelehnter normaler Finaltext erhält nicht automatisch einen Attempt; AP4 muss die Fehlersemantik für diesen Fall festlegen.
- `final_strategy`, `append_space` und `warn_elevated` stehen in der Konfiguration, sind in AP2 aber noch keine vollständig wirksamen Funktionen.

---

## 7. Komponentenvertrag AP3 – `TranscriptReinsertionService`

### Öffentliche Schnittstellen

```python
reinsert_last() -> ReinsertionResult
reinsert_entry(entry_id: str) -> ReinsertionResult
get_recent_entries(limit=None) -> tuple[HistoryEntry, ...]
```

### Garantien

- Memory-first-Auflösung, SQLite als Fallback,
- Übergabe ausschließlich über `TextInjectionQueue.enqueue()`,
- kein neuer `HistoryEntry` bei Reinsertion,
- weitere Einfügeversuche bleiben am ursprünglichen Eintrag,
- defensive und unveränderliche Recent-Entries-Rückgabe,
- thread-sichere Serialisierung der Serviceoperationen.

### Resultatstatus

| Status | Bedeutung |
|---|---|
| `queued` | Queue hat den Auftrag angenommen |
| `empty_history` | beide lesbaren Quellen enthalten keinen Eintrag |
| `entry_not_found` | angeforderte ID ist bei fehlerfreiem Lesen nicht vorhanden |
| `queue_unavailable` | Queue hat den Auftrag abgelehnt |
| `failed` | History-Lesen oder Enqueue ist mit Fehler gescheitert |

### Attempt-Semantik

- Queue-Ablehnung: der Service dokumentiert best-effort genau einen `skipped`-Attempt.
- Enqueue-Exception: der Service dokumentiert best-effort genau einen `failed`-Attempt.
- Erfolgreiches Enqueue: der Queue-Worker dokumentiert später den finalen Attempt.
- History-Fehler vor Auflösung eines Eintrags: kein Attempt, weil keine sichere Entry-ID vorliegt.

Für AP4 ist vor allem der Lifecycle relevant: Der Service darf erst verwendet werden, wenn History und Queue vollständig initialisiert sind.

---

## 8. Verbindlicher Integrationsfluss

### Normaler Finaltext

```text
1. Finalevent empfangen
2. session_id, segment_id und finalen Text validieren
3. Finalidentität gegen den AP4-Exactly-once-Vertrag prüfen
4. HistoryEntry vor jedem Paste-Versuch anlegen oder eindeutig auflösen
5. Nur einen neu zur Einfügung zugelassenen Finaltext enqueuen
6. Queue-Worker führt Clipboard + SendInput aus
7. Queue-Worker dokumentiert genau einen finalen Attempt
8. Controller veröffentlicht Status, ohne UI-Abhängigkeit
```

### Realtime-Text

```text
Realtimeevent
  → höchstens Status-/Darstellungsupdate
  → niemals History-Persistenz als Finaltext
  → niemals TextInjectionQueue.enqueue()
```

### Reinsertion

```text
Controllerbefehl
  → TranscriptReinsertionService
  → bestehenden HistoryEntry auflösen
  → dieselbe TextInjectionQueue
  → zusätzlicher Attempt am bestehenden Entry
```

### Exactly-once muss präzise gelten

AP4 benötigt getrennte Aussagen für:

1. **History-Ebene:** höchstens ein `HistoryEntry` pro `(session_id, segment_id)`.
2. **Queue-Ebene:** höchstens ein automatischer Queue-Job pro neuem Finalsegment.
3. **Attempt-Ebene:** genau ein finaler Attempt pro angenommenem Queue-Job.
4. **Reinsertion:** absichtlich weitere Queue-Jobs und Attempts am selben Entry.

„Exakt einmal“ darf nicht pauschal verwendet werden, weil Reinsertion ausdrücklich Mehrfachversuche erlaubt und ein Prozessabsturz ohne persistente Outbox keine atomare Exactly-once-Garantie über History und Queue hinweg bietet.

---

## 9. Controller-Verantwortlichkeiten

Der AP4-Controller soll:

- Komponenten in definierter Reihenfolge erzeugen,
- die Injection-Queue kontrolliert starten,
- STTSession-Callbacks anbinden und beim Shutdown nicht mehr annehmen,
- gewünschten Diktierzustand getrennt vom Transportzustand halten,
- Final- und Realtime-Pfade strikt trennen,
- Session- und Segmentidentitäten validieren,
- doppelte automatische Enqueues verhindern,
- Reinsertion-Befehle anbieten,
- UI-neutrale Zustands- und Fehlerresultate veröffentlichen,
- Audio, Session und Queue in definierter Reihenfolge stoppen,
- keine Clipboard- oder SQLite-Interna duplizieren.

### Empfohlene öffentliche Befehlsfläche

Die konkrete Benennung wird in AP4 festgelegt. Semantisch werden mindestens benötigt:

- Controller starten,
- Diktierwunsch aktivieren/deaktivieren oder toggeln,
- letzten Text erneut einfügen,
- bestimmten Eintrag erneut einfügen,
- letzte Einträge abfragen,
- aktuellen Controllerstatus abfragen,
- kontrolliert herunterfahren.

Eine spätere UI darf diese Befehle nur über eine thread-sichere Brücke aufrufen.

---

## 10. Lifecycle und Shutdown

### Startreihenfolge

1. Konfiguration laden und validieren.
2. `TranscriptHistoryManager` erzeugen.
3. `TextInjectionQueue` mit demselben History-Manager erzeugen.
4. Queue starten und `RUNNING` bestätigen.
5. `TranscriptReinsertionService` mit denselben Instanzen erzeugen.
6. Controller-Callbacks an `STTSession` binden.
7. STTSession und Audio-Laufzeit starten.

### Shutdown-Reihenfolge

1. Controller in `closing`/nicht annehmend versetzen.
2. neue Benutzer- und Reinsertion-Befehle abweisen,
3. Audioaufnahme stoppen,
4. Serverstream und STTSession kontrolliert stoppen,
5. ausstehende Core-Tasks beenden,
6. Injection-Queue kontrolliert leeren und stoppen,
7. History-Cleanup abschließen,
8. Event-Loop und späteren Worker-Thread beenden.

AP4 muss testen, was bei einem Queue-Stop-Timeout geschieht. Ein nicht-daemonisierter Worker darf beim Prozessende nicht unbemerkt zurückbleiben.

---

## 11. Für AP4 festgelegte Integrationsentscheidungen

Die folgenden Punkte waren bei Erstellung dieses Paketvertrags offen. Sie sind
für die AP4-Ausführung inzwischen im operativen Auftrag
`docs/work-packages/AP04_CONTROLLER_INTEGRATION_AUSFUEHRUNGSAUFTRAG.md`
festgelegt. Eine technisch notwendige Abweichung muss vor der Implementierung
mit konkreten Codefundstellen als Blocker gemeldet werden.

### E-01 – Crash-Sicherheit jedes Finaltexts

**Entschieden:** Vor jedem automatischen Enqueue muss ein stabiler
`HistoryEntry` vorliegen. Die vorhandene selektive SQLite-Politik bleibt
unverändert; AP4 führt weder `store_all` als neuen Default noch eine persistente
Outbox ein. Ohne HistoryEntry erfolgt kein automatischer Paste-Versuch. Das
verbleibende Crash-Fenster kurzer, nur im RAM gehaltener Finaltexte wird
dokumentiert.

### E-02 – History-Fehler als auswertbares Ergebnis

**Entschieden:** Der normale Finalpfad muss „neu“, „Duplikat“ und
„History nicht verfügbar“ eindeutig unterscheiden. Falls `add_entry()` dafür
nicht genügt, wird eine kleinstmögliche rückwärtskompatible Ergebnis-API
ergänzt. Bei History-Ausfall wird nicht automatisch eingefügt. Die nicht
eindeutige Fehlerabbildung persistenter Leseoperationen bleibt außerhalb des
normalen Finalpfads best-effort und wird als bekannte Grenze dokumentiert.

### E-03 – Finalevent-Eingang und automatischer Enqueue

**Entschieden:** Das rohe `final`-Event aus `on_event` ist die autoritative
Quelle für `sessionId`, `segmentId` und Text. Der Controller dedupliziert
automatische Finalverarbeitung über `(sessionId, segmentId)`. `on_text` bleibt
Darstellungspfad; Timeline-`final_transcript` ist keine zweite
Transkriptquelle. Eine bloße Prüfung `entry is not None` bleibt unzulässig,
weil `add_entry()` auch vorhandene Einträge zurückgeben kann.

### Weitere erforderliche Fehlersemantik – History- oder Queue-Ausfall

Zu definieren:

- Was meldet der Controller, wenn History deaktiviert oder nicht beschreibbar ist?
- Darf ohne History jemals automatisch eingefügt werden?
- Welcher Attempt wird bei Queue-Ablehnung eines normalen Finaltexts dokumentiert?
- Darf ein Finaltext nach späterer Queue-Erholung automatisch erneut enqueued werden?

Diese Semantik ist im Ausführungsauftrag festgelegt: Ohne History kein
automatischer Paste; Queue-Ablehnung erhält best-effort einen
`skipped`-Attempt, eine Enqueue-Exception einen `failed`-Attempt. Doppelte
Serverevents lösen keinen automatischen Retry aus; dafür existiert die bewusste
Reinsertion.

### E-04 – Hotkey-Konfiguration

**Entschieden:** AP4 implementiert keinen Hotkey und koppelt keine öffentliche
Controller-API an `<ctrl>+<shift>+space` oder ein anderes Tastenschema. Der
Controller bietet nur semantische Diktierbefehle. Das Win32-kompatible Schema
bleibt AP6.

### E-05 – Baseline-Korrekturen und Paketgrenze

**Status: entschieden am 25. Juli 2026.**

- Der bestätigte fremdthreadige Direktzugriff auf `asyncio.Queue` wurde vor AP4 in `app.py` beseitigt. AudioCapture plant Pakete jetzt per `loop.call_soon_threadsafe` auf der besitzenden Event-Loop ein. Pakete vor erfolgreichem `start`, nach Stop/Loop-Ende und bei Queue-Vollstand werden definiert verworfen.
- `tests/test_app.py` sichert die Event-Loop-Bindung, Fremdthread-Übergabe, Start-Grenze und Shutdown-/Überlastfälle mit 7 Regressionstests ab.
- Die unzuverlässige Ping-Miss-Erkennung und das fehlende automatische `send_start()` nach Reconnect bleiben ausdrücklich AP5.

AP4 darf die korrigierte Brücke verwenden, soll aber die beiden AP5-Härtungen nicht stillschweigend vorziehen.

### E-06 – Repository-Hygiene

Testdatenbanken im Projektroot, Cache-/Ignore-Regeln und der absolute Logging-Pfad sind als eigenes Hygiene-Thema einzuplanen. Diese Bereinigung darf nicht stillschweigend mit AP4 vermischt werden, sofern sie für die Controller-Integration nicht zwingend erforderlich ist.

### E-07 – Wake-Word-Vertrag des Desktop-Clients

**Status: separate, nicht blockierende Serverevaluierung; keine AP4-Entscheidung.**

Der Server meldete am 25. Juli 2026 für eine Session mit korrekt in Echtzeit übertragenem Audio:

- `wakeWordEnabled: true`,
- `wakeWords: hey_jarvis`,
- `state: wakeword_wait`.

Ein anschließender Diagnoselauf mit gesprochenem „Hey Jarvis“ bestätigte `wakeword_detected`, Aufnahme, Realtime und Finaltext. Dabei wurden 733 von 733 Capture-Paketen über die korrigierte Brückenlogik gesendet, ohne dass die Clientqueue voll lief. Die technische Wake-Word-Funktion ist damit bestätigt.

Der produktive Single-WebSocket-Vertrag unterstützt nur `start`, `stop`, `clear`, `ping` und `metrics`; ein per-Session-`set_parameter` ist dort nicht erlaubt. Änderungen über die administrative Wake-Word-/Konfigurations-API gelten serverweit beziehungsweise für neue Sessions und sind keine normale Desktop-Client-Funktion.

Zwischenzeitlich wurden eine lokale Option `session.mode` und benannte
serverseitige Sessionprofile als Umschalttechnik vorbereitet. Dieser breite
Entwurf wird wegen des dafür ermittelten Serveraufwands nicht weiterverfolgt:
Die Clientoption und ihre Prüfungen wurden entfernt; der Serverentwurf liegt
nur noch als verworfener Beleg unter
`docs/archive/2026-07-25_SERVER_SESSION_PROFILE_SPECIFICATION_VERWORFEN.md`.

Davon getrennt prüft ein Server-Agent ergebnisoffen, ob ein eng begrenzter
Wake-Word-Override nur in der ohnehin beim Sessionaufbau erzeugten
Recorderkopie mit wesentlich kleinerem Aufwand möglich ist. Der Prüfauftrag
steht in
`docs/evaluations/2026-07-25_SERVER_EVALUIERUNG_SESSIONLOKALER_WAKE_WORD_OVERRIDE.md`.
Es ist weiterhin nicht entschieden, wie Direct Hotkey und dauerhafter
Wake-Word-Betrieb künftig zusammenwirken; AP4 darf dafür weder einen
Modusselector noch einen Serveroverride erfinden. Der frühere
`docs/decisions/ADR-001_BETRIEBSMODI_HOTKEY_UND_WAKE_WORD.md` ist ein
zurückgezogener, nicht bindender Entwurf; ein endgültiges ADR existiert noch
nicht.

Unabhängig davon muss AP4 den vorhandenen Protokollvertrag korrekt abbilden:
`wakeword_wait` bleibt ein gültiger Serverzustand, Audio muss darin
kontinuierlich übertragen werden, und `start` darf bei serverweit aktivem Wake
Word nicht als unmittelbarer Übergang nach `listening` interpretiert werden.
Die externe E-07-Evaluierung blockiert die Controller-Integration nicht.

---

## 12. Fehler- und Ergebnis-Matrix

| Situation | Automatischer Paste? | History/Attempt | Controller-Ergebnis |
|---|---:|---|---|
| Realtime-Event | nein | kein Final-Entry | Darstellungsupdate |
| gültiges neues Finalevent | ja, nach History-Aufnahme | Entry, danach Queue-Attempt | angenommen/queued |
| identisches doppeltes Finalevent | nein | vorhandener Entry unverändert | dedupliziert |
| Finalevent ohne stabile Session-/Segment-ID | nein | kein unsicherer Entry | Protokoll-/Validierungsfehler |
| History-Aufnahme schlägt fehl | nein | Fehler dokumentieren, soweit möglich | history_unavailable |
| Queue nicht `RUNNING` | nein | `skipped` best-effort am vorhandenen Entry | queue_unavailable |
| Queue nimmt Job an, Paste scheitert | versucht | genau ein `failed`-Attempt durch Worker | asynchroner Fehlerstatus |
| Reinsertion bei leerer Historie | nein | kein Attempt | `empty_history` |
| Reinsertion bei Queue-Ablehnung | nein | `skipped` best-effort | `queue_unavailable` |
| Callback wirft Exception | nein für diesen Callback | Log; Session läuft weiter | Controllerfehler |

Die empfohlenen Statusnamen sind keine bereits implementierte Controller-API.

---

## 13. Mindesttests für AP4

### Komponentenverdrahtung

- alle AP1–AP3-Komponenten erhalten dieselben Instanzen,
- Queue ist vor erster Nutzung `RUNNING`,
- Reinsertion-Service wird erst nach History und Queue nutzbar,
- kontrollierter Shutdown stoppt jede gestartete Komponente.

### Final-/Realtime-Pfad

- ein neues Finalsegment erzeugt genau einen HistoryEntry,
- ein neues Finalsegment erzeugt genau einen automatischen Queue-Job,
- ein Realtime-Event erzeugt keinen HistoryEntry und keinen Queue-Job,
- identisches doppeltes Finalevent erzeugt keinen zweiten automatischen Queue-Job,
- geändertes oder widersprüchliches Finalevent wird gemäß festgelegtem Vertrag behandelt,
- Sessionwechsel mit gleicher `segment_id` kollidiert nicht.

### Fehlerpfade

- History deaktiviert oder fehlerhaft,
- Queue noch nicht gestartet,
- Queue bereits gestoppt,
- Enqueue-Exception,
- Callback-Exception,
- Shutdown bei wartenden Jobs,
- Shutdown-Timeout des Workers,
- Reconnect vor, während und nach einem Finalevent.

### Reinsertion

- letzter Eintrag wird über denselben Queue-Pfad enqueued,
- ausgewählter Eintrag wird über denselben Queue-Pfad enqueued,
- Reinsertion erzeugt keinen neuen HistoryEntry,
- Reinsertion darf bewusst einen zusätzlichen Attempt erzeugen,
- leere Historie und unbekannte ID werden unverändert durchgereicht.

### Regression

Nach AP4 müssen mindestens erfolgreich laufen:

```powershell
.\venv\Scripts\python.exe -m unittest tests.test_history tests.test_text_injector tests.test_reinsertion
```

Zusätzlich sind neue Controller- und Integrations-Tests sowie danach die gesamte vorhandene Testsuite auszuführen.

---

## 14. Abnahmekriterien

AP4 ist erst abgeschlossen, wenn:

- [x] Eventeingang und Exactly-once-Grenzen schriftlich entschieden sind.
- [x] Final- und Realtime-Pfade getrennt getestet sind.
- [x] Jeder automatische Paste-Versuch einen vorher aufgelösten HistoryEntry besitzt.
- [x] Ein normales doppeltes Finalevent keinen zweiten automatischen Queue-Job erzeugt.
- [x] Reinsertion weiterhin absichtlich zusätzliche Versuche erlaubt.
- [x] Queue-Start, Queue-Stop und Shutdown deterministisch getestet sind.
- [x] Controller und Core keine PySide6-Abhängigkeit enthalten.
- [x] bekannte Abweichungen oder verschobene Risiken dokumentiert sind.
- [x] neue gezielte Tests und die Gesamtsuite (152 Tests) erfolgreich sind.
- [x] `task.md`, Roadmap und `ÜBERGABE.md` synchronisiert sind.
- [x] nicht automatisch mit AP5 begonnen wurde.

---

## 15. Abschluss und Folgegrenze

AP4 wurde gemäß dem operativen Auftrag implementiert, nach drei
AntiGravity-Korrekturrunden unabhängig nachgeprüft und anschließend an den
verbliebenen Lifecycle-Rändern fertiggestellt. Die vollständigen
Ausführungsnachweise liegen unter
`docs/2026-07-25_AP04_ANTIGRAVITY/`.

Das nächste Paket ist AP5. Der vorliegende AP4-Vertrag darf dafür als
Schnittstellenquelle gezielt gelesen, aber nicht als noch offener
Ausführungsauftrag behandelt werden. AP5 muss vor seiner ersten Codeänderung
einen eigenen, klar abgegrenzten Ausführungsauftrag erhalten.
