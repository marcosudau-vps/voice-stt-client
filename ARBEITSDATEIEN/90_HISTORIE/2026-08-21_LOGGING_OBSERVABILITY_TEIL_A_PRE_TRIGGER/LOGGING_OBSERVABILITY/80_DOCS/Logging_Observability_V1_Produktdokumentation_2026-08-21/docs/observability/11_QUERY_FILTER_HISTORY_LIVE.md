# Query, Filter, History und Live

## Kurz und einfach erklärt

Stell dir vor, das Logging ist ein sehr großes Karteikartenarchiv.

**History** bedeutet:

> „Suche mir aus dem Archiv die Karten heraus, die zu meiner Frage passen.“

**Live** bedeutet:

> „Ich habe mir die letzte Karte gemerkt. Zeig mir ab jetzt immer nur die Karten, die danach neu dazugekommen sind.“

Die Oberfläche lädt also nicht 200.000 Karten und sortiert sie selbst. Sie sagt der Suchschicht genau, was sie braucht.

Das ist der zentrale Gedanke dieses Kapitels.

---

## 1. Query-Schicht

```text
LogWindow
→ LogQueryController
→ LogQueryService
→ LocalLogProvider
→ SQLite
```

Der `LogQueryService` bildet die stabile Grenze zwischen Benutzeroberfläche und Datenquelle.

---

## 2. Warum die UI nicht direkt SQL verwendet

Direktes SQL im UI-Code würde:

- die Oberfläche an SQLite binden;
- Remote-History später erschweren;
- DB-Details in Qt-Code mischen;
- Testbarkeit verschlechtern.

Darum kennt die UI einen Queryvertrag und keinen Datenbankvertrag.

---

## 3. `QueryFilter`

Der V1-Vertrag unterstützt sinngemäß:

```text
producers/sources
channels
levels
types
type_prefix
components
scopes

session_id
generation
activation_id
segment_id
command_id
correlation_id
transcription_id
event_id

since
until
text

include_replayed
newest_first
```

Die UI muss nicht zwingend jedes Feld gleichzeitig anzeigen; die Query-Schicht kann umfassender sein.

---

## 4. Filterdimensionen verständlich erklärt

### Quelle / Producer

> „Nur vom Client“ oder „nur vom Server“.

### Channel

> „Nur technische Systemmeldungen“, „nur Aktionen“, „nur Transkription“ usw.

### Level

> „Zeig mir nur Warnungen und Fehler.“

### Typ

> „Zeig mir genau `client.trigger.sent`.“

### Typ-Präfix

> „Zeig mir alles unter `client.trigger.*`.“

### Component

> „Zeig mir alles vom `eventstream`.“

### IDs

> „Zeig mir alles, was sicher zu dieser Session/Command/Korrelation gehört.“

### Freitext

> „Ich erinnere mich nur an einen Begriff – suche ihn in lesbaren/klassifizierenden Feldern.“

---

## 5. Freitext

Freitext ist eine schnelle Suchhilfe.

Die gewünschte Semantik umfasst insbesondere:

```text
message
type
component
```

Für belastbare Forensik sollte eine konkrete ID oder ein strukturierter Filter bevorzugt werden.

---

## 6. Exakter Typ vs. Typ-Präfix

Exakt:

```text
client.trigger.sent
```

Präfix:

```text
client.trigger
```

kann treffen:

```text
client.trigger.sent
client.trigger.ack_received
client.trigger.ack_dropped
```

Die geplante UI-Nachbesserung ergänzt dafür eine Auswahl bekannter Typen/Präfixe.

---

## 7. Zeitfilter

Konzeptionell:

```text
since = inklusive Untergrenze
until = exklusive Obergrenze
```

Das verhindert Doppelungen, wenn Zeitfenster direkt aneinander anschließen.

---

# History

## 8. Was History macht

History ist eine **Abfrage gespeicherter Daten**.

Typischer Nutzerablauf:

1. History wählen.
2. Filter setzen.
3. erste Seite laden.
4. Record auswählen.
5. Details ansehen.
6. bei Bedarf „Weitere laden“.

---

## 9. Warum Pagination nötig ist

Falsch:

```text
SELECT alle 200.000 Records
→ Python
→ Qt
→ lokal filtern
```

Richtig:

```text
Filter + begrenzte Seite
→ nur benötigte Records
```

Das hält Speicher, Queryzeit und UI-Latenz begrenzt.

---

## 10. `QueryPage`

Eine Seite enthält konzeptionell:

```text
records
next_cursor
complete
```

### `records`

Die aktuelle Teilmenge.

### `next_cursor`

Position, ab der die nächste Seite fortgesetzt werden kann.

### `complete`

Ob nach den aktuellen Bedingungen noch weitere Records existieren bzw. die Seite vollständig ist.

---

## 11. Cursorbasierte Pagination

Anstatt großer `OFFSET`-Sprünge merkt sich die Query den letzten Schlüssel.

Einfach erklärt:

```text
"Ich war bis Karte Nr. 4711.
Gib mir die nächsten passenden Karten danach."
```

Das ist bei wachsenden Tabellen robuster als eine rein numerische Seitenzahl.

---

## 12. History-Sortierung

History verwendet typischerweise:

```text
newest_first = true
```

Der Benutzer sieht also zunächst die neuesten gespeicherten Treffer.

„Weitere laden“ ergänzt ältere Records.

---

# Live

## 13. Was Live macht

Live ist **keine zweite Datenquelle**.

Der Modus fragt denselben lokalen Store regelmäßig:

> „Was ist seit meinem letzten bekannten Record neu hinzugekommen?“

---

## 14. Live-Tail

V1 verwendet bewusst keinen Memory-Ringbuffer.

Konzeptionell:

```sql
WHERE id > :last
ORDER BY id
LIMIT 500
```

periodisch über einen Qt-Timer.

Ablauf:

```text
1. letzte gesehene Store-ID merken
2. nach größeren IDs fragen
3. nur neue persistierte Records erhalten
4. unten an die Live-Tabelle anhängen
5. Cursor weiterschieben
```

---

## 15. Warum Live die neuesten Records unten hat

Ein laufendes Protokoll liest sich:

```text
alt
↓
neu
↓
noch neuer
```

Darum werden neue Live-Records unten angefügt.

History dagegen startet sinnvollerweise mit den neuesten Treffern oben.

Diese unterschiedliche Leserichtung ist bewusst und soll in der UI künftig noch deutlicher markiert werden.

---

## 16. Warum kein Memory-Ringbuffer

Früher geplant:

```text
Worker
├→ SQLite
└→ Memory Ringbuffer → UI
```

V1:

```text
Worker → SQLite → Provider → UI
```

Vorteile:

- nur eine lokale Wahrheit;
- keine zusätzliche Synchronisation;
- UI sieht nur tatsächlich persistierte Records;
- gleicher Provider für History und Live;
- weniger Komponenten und Locks;
- Remote-Provider später leichter.

---

## 17. Was bei einem kaputten Worker passiert

Mit Store-Tailing:

```text
Worker schreibt nichts mehr
→ Live zeigt keine neuen persistenten Records
```

Das ist ehrlich.

Ein separater Ringbuffer könnte dagegen noch Records anzeigen, die niemals gespeichert wurden.

---

## 18. Warum History und Live nicht gemischt werden

Eine Mischansicht müsste gleichzeitig:

- historische Seiten halten;
- neue Records einsortieren;
- Filterwechsel behandeln;
- Live-/History-Duplikate erkennen;
- Cursor in mehreren Richtungen koordinieren.

Für V1 wurde bewusst entschieden:

```text
History-Modus ODER Live-Modus
```

statt einer komplexen Mischansicht.

---

## 19. Auto-Scroll

Live kann neuen Records folgen.

Wenn der Benutzer hochscrollt oder Auto-Scroll deaktiviert, soll die Ansicht nicht eigenmächtig zurückspringen.

---

## 20. Replay-Filter

`include_replayed` steuert, ob Replaykontext angezeigt wird.

Wichtige Feinheit:

Ein bereits früher persistiertes Serverevent mit derselben `event_id` kann beim Replay durch den Dedupe-Index vollständig unterdrückt werden. Es entsteht dann nicht zwangsläufig eine zweite Zeile mit `replayed=true`.

---

## 21. Kontextfilter

Aus einem ausgewählten Record kann direkt gefiltert werden:

```text
session_id
activation_id
segment_id
type
```

Das ist zuverlässiger als lange IDs manuell zu kopieren.

---

## 22. Activation-Filter

Vor der Trigger-Migration gilt:

```text
activation_id = diagnostischer Hinweis
```

nicht:

```text
activation_id = garantierte fachliche Wahrheit
```

Deshalb muss dieser Filter mit dem bekannten Vorbehalt dokumentiert/angezeigt werden.

---

## 23. Raw-Lazy-Load

Listenabfrage:

```text
kompakte LogRecordView
```

Nach Auswahl:

```text
Detailabruf
→ raw laden
```

So werden große Payloads nicht für jede Tabellenzeile geladen.

---

## 24. Fehlersemantik

Ein Provider-/Queryfehler:

```text
→ UI zeigt Diagnoseproblem
```

nicht:

```text
→ Runtime stoppt
```

---

## 25. Spätere Remote-History

Teil B kann ergänzen:

```text
LogQueryService
├→ LocalLogProvider
└→ RemoteServerLogProvider
```

Genau deshalb wurde die Query-Semantik schon in V1 als eigener Vertrag gebaut.
