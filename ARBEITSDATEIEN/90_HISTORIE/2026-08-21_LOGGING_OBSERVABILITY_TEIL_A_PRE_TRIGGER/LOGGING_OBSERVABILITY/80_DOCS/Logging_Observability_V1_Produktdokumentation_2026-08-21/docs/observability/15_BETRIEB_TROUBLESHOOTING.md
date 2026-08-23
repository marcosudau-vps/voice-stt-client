# Betrieb und Troubleshooting

## Kurz und einfach erklärt

Wenn etwas komisch läuft, soll man nicht zuerst eine Datenbank öffnen und SQL schreiben müssen.

Der normale Diagnoseweg lautet:

1. Logfenster öffnen.
2. Session oder Zeitraum eingrenzen.
3. nach Channel, Level oder Typ filtern.
4. interessanten Eintrag anklicken.
5. IDs vergleichen.
6. Health-Zustand prüfen.

Diese Datei ist die praktische Fehlersuchanleitung.

---

## 1. Erste Fragen bei jedem Problem

```text
Ist Observability selbst gesund?
Welche Session ist betroffen?
Welche Generation?
Client oder Server?
Welcher Channel?
Welcher Eventtyp?
Welche IDs verbinden die Einträge?
```

Erst danach lohnt sich die Detailanalyse.

---

## 2. Health-Zeile lesen

Beispiel:

```text
Logging: ok
geschrieben: 739
dedupliziert: 0
verworfen: 0
Queue: 0
```

### `written`

Kumulativ erfolgreich geschriebene Records.

### `deduplicated`

Serverevent-Duplikate, die nicht erneut eingefügt wurden.

### `dropped_*`

Kontrollierte Verluste durch Backpressure/Shutdown.

### `queue_depth`

Aktueller Rückstau.

---

## 3. „Warum sehe ich 289 Zeilen, obwohl 739 geschrieben wurden?“

Weil das zwei verschiedene Größen sind:

```text
739 = kumulativer Worker-/Health-Zähler
289 = aktuell geladene/gefilterte UI-Zeilen
```

Zusätzlich wirken:

- Filter;
- Pagination;
- Retention;
- History-/Live-Modus.

---

## 4. Verbindungsprobleme

Filtere nach:

```text
channel = system
component ≈ stt_session / connection
```

Relevante Clienttypen:

```text
client.websocket.connecting
client.websocket.connected
client.websocket.disconnected
client.session.admitted
client.session.ready
client.reconnect.scheduled
```

Achte besonders auf `generation`: Ein Reconnect kann dieselbe fachliche Situation in einer neuen Verbindungsgeneration fortsetzen.

---

## 5. Eventstream-Probleme

Filter:

```text
component = eventstream
```

Relevante Typen:

```text
client.eventstream.state_changed
client.eventstream.gap
client.eventstream.error
client.eventstream.replay_completed
client.eventstream.protocol_error
```

Bei Replay zusätzlich `event_id`, Cursor und Dedupe-Zähler prüfen.

---

## 6. Trigger-/Command-Ablauf

Filter:

```text
channel = audit
```

Typische Kette:

```text
client.hotkey.pressed
client.command.requested
client.trigger.sent
client.trigger.ack_received
client.command.completed
```

Dann:

- `command_id`;
- `correlation_id`;
- `session_id`;
- `generation`

vergleichen.

Gerade bei der kommenden Triggerarchitektur ist diese Kette eine zentrale Diagnosehilfe.

---

## 7. Settings Apply

Suche:

```text
client.settings.apply_started
client.settings.runtime_apply
client.settings.apply_completed
```

und vergleiche die `correlation_id`.

Eine reine Observability-Änderung soll keinen unnötigen Audio-/Session-Reconnect verursachen.

---

## 8. Serverevent untersuchen

Quelle auf Server eingrenzen.

Dann prüfen:

- Channel;
- `event_id`;
- `server_cursor`;
- `session_id`;
- `segment_id`/`transcription_id`;
- Replay;
- Details/Raw.

Für operative Zustände und Finaltext bleibt `/ws/transcribe` die Primärquelle; `/ws/logs` ist die ergänzende Beobachtungsachse.

---

## 9. Replay untersuchen

Fragen:

1. Ist das Event als Replay markiert?
2. Ist seine `event_id` bereits bekannt?
3. Steigt `deduplicated`?
4. Ist `log.replay_completed` bzw. das lokale Replay-Completed sichtbar?
5. Entstehen fälschlich doppelte persistente Zeilen?
6. Werden alte Impulse fälschlich als aktuelle Bedienwirkung interpretiert?

---

## 10. Es erscheinen keine neuen Records

Mögliche Ursachen:

```text
Observability deaktiviert
Level filtert den Record
Store/Worker failed
Queue/Backpressure
Filter zu eng
falscher Modus/Provider
```

Health zuerst prüfen.

---

## 11. `enqueued` steigt, `written` nicht

Verdacht:

- Workerproblem;
- Storeproblem;
- DB-Lock;
- ungültiger DB-Pfad.

Prüfen:

```text
state
queue_depth
store_errors
worker_errors
```

---

## 12. `dropped_watermark` steigt

Die Queue war stark gefüllt und Low-Priority-Records wurden kontrolliert verworfen.

Das ist zunächst ein Lastsignal, nicht automatisch ein Produktfehler.

Bei dauerhaft hohen Werten Recordquellen untersuchen – nicht reflexartig die Queue unbegrenzt vergrößern.

---

## 13. `dropped_queue_full` steigt

Die Queue war vollständig voll.

Untersuche:

- Recordrate;
- mögliche Logflut;
- extrem häufige Python-Logger;
- Feedback-/Performance-Records;
- Worker-/Store-Durchsatz.

---

## 14. `FAILED_STORE`

Die Observability-Persistenz funktioniert nicht.

Erwartetes Produktverhalten:

> Diktat und Hauptanwendung laufen möglichst weiter.

In diesem Fall ist `client.log` als unabhängige Diagnosequelle besonders wichtig.

---

## 15. JSONL fehlt

Prüfen:

```text
file_sink_enabled
file_sink_dir
sink_errors
Dateirechte/Pfad
```

SQLite kann gleichzeitig vollständig gesund sein.

---

## 16. Filter liefert „zu wenig“

Prüfen:

- History oder Live?
- Replay ausgeblendet?
- Level-Schwelle?
- exakter Typ statt Präfix?
- Session-ID korrekt?
- Pagination vollständig?
- Activation-ID möglicherweise unzuverlässig?
- Freitext vs. strukturierter Filter?

---

## 17. Filter liefert „zu viel“

Freitext durch strukturierte Filter ersetzen.

Statt:

```text
text = trigger
```

besser:

```text
channel = audit
type_prefix = client.trigger
session_id = ...
```

---

## 18. Raw fehlt

Raw ist optional.

Mögliche Gründe:

- Raw-Policy deaktiviert;
- Quellrecord hat keinen Raw-Payload;
- Listenansicht hat Raw noch nicht lazy nachgeladen.

---

## 19. Klassisches Log vs. Observability

Eine `client.log`-Zeile muss nicht 1:1 einen strukturierten Eventtyp besitzen.

Umgekehrt kann ein strukturiertes Event wesentlich mehr IDs und Details tragen als die klassische Meldung.

Beide Systeme ergänzen sich.

---

## 20. Was nicht automatisch ein Logging-Defekt ist

Bekannte fachliche Altprobleme der Triggerarchitektur, etwa:

- falsche Hotkeybedeutung;
- alte Dictation-State-Machine;
- Trigger-Lock;
- Merge-vs-First-Trigger;
- Lifecycle hängt;

sind nicht automatisch Observability-Fehler.

Observability arbeitet korrekt, wenn sie diese Probleme zuverlässig sichtbar macht, ohne selbst die Ursache zu sein.

---

## 21. Empfohlener realer Diagnoseablauf

```text
1. Problem reproduzieren
2. Session-ID notieren
3. History auf Session filtern
4. System + Audit prüfen
5. Serverquelle ergänzen
6. IDs korrelieren
7. Transcription hinzunehmen
8. Performance nur bei Timing-/Lastfrage
9. Details/Raw öffnen
10. Ursache erst danach klassifizieren
```

---

## 22. Wenn die UI selbst verdächtig ist

Zum Gegencheck unterscheiden:

```text
Store enthält Record?
Query liefert Record?
TableModel enthält Record?
UI zeigt Record?
```

So lässt sich ein Datenproblem von einem Darstellungsproblem trennen.

---

## 23. Wenn History und Live unterschiedlich wirken

Das kann normal sein:

- History: neueste zuerst;
- Live: neue Records unten;
- Filter/Cursor unterscheiden sich;
- Live zeigt nur nach dem Tail-Cursor neu persistierte Records.

Wenn tatsächlich ein Record fehlt, mit `record_id`, Store-ID und Query-Cursor untersuchen.
