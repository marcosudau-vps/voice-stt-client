# Persistenz, Sinks und Ausgabeformate

## Kurz und einfach erklärt

Die Anwendung kann Diagnoseinformationen auf mehreren Wegen ausgeben:

- **`client.log`** ist ein klassisches Notizbuch für Menschen.
- **SQLite** ist ein ordentliches Karteikartenarchiv, in dem man sehr gezielt suchen kann.
- **JSONL** ist eine fortlaufende maschinenlesbare Exportdatei.

Für die neue lokale Diagnoseansicht ist SQLite die wichtigste Datenquelle.

---

## 1. Drei Ausgabewelten

```text
klassisches Python-Logging
    → Console
    → client.log

Observability
    → SQLiteLogStore

optional
    → JsonlSink
```

Sie existieren bewusst nebeneinander.

---

## 2. Warum SQLite die lokale Wahrheit ist

Die Diagnoseoberfläche benötigt:

- Filter;
- Sortierung;
- ID-Suche;
- Pagination;
- Retention;
- Dedupe;
- Persistenz über Neustarts.

Eine lineare Textdatei wäre dafür deutlich ungeeigneter.

---

## 3. Writer-Modell

Der `LoggingWorker` besitzt die Schreibverbindung.

Wichtig:

> Die SQLite-Verbindung wird im Worker-Thread erzeugt.

Damit wird vermieden, eine Verbindung in Thread A zu erzeugen und in Thread B zu verwenden.

---

## 4. SQLite-Betriebsmodus

V1 verwendet unter anderem:

```text
WAL
synchronous=NORMAL
busy_timeout=5000
```

WAL erleichtert parallele Leser, während der Worker schreibt.

---

## 5. Reader-Modell

Der `LocalLogProvider` verwendet eigene kurzlebige Leseverbindungen.

Schreibschutz:

```sql
PRAGMA query_only = ON;
```

Die Query-/UI-Seite soll nicht versehentlich Daten verändern.

---

## 6. Vereinfachtes Schema

Kernspalten:

```text
id
record_id
received_at
source_timestamp

producer_kind
producer_id
instance_id
scope

channel
level
type
component

session_id
generation
activation_id
segment_id
transcription_id
command_id
event_id
correlation_id
server_cursor

replayed
message
details_json
raw_json
```

Das exakte DDL bleibt im normativen Contract die maßgebliche Quelle.

---

## 7. Indizes

Gezielte Indizes existieren für häufige Abfrage-/Identitätsfälle, insbesondere sinngemäß:

- Session;
- Received Time;
- Channel + Level;
- Activation;
- Correlation;
- Event-Dedupe.

Nicht jedes Feld bekommt automatisch einen Einzelindex. Jeder Index erhöht auch Schreibkosten.

---

## 8. Replay-Dedupe

Der zentrale partielle Unique-Constraint:

```sql
UNIQUE (producer_id, event_id)
WHERE event_id IS NOT NULL
```

Damit gilt:

```text
gleiches Serverevent bei Replay
→ kein zweiter persistenter Datensatz
→ deduplicated steigt
```

Lokale Records ohne `event_id` werden nicht fälschlich gegeneinander dedupliziert.

---

## 9. Batch Writes

Der Worker schreibt mehrere Records in einer Transaktion.

`write_batch` unterscheidet konzeptionell:

```text
eingefügt
dedupliziert
```

Dadurch sind Health-Zähler aussagekräftig.

---

## 10. Retention

Zwei aktive Grenzen:

```text
retention_days
max_entries
```

Beide wirken.

Cleanup erfolgt blockweise, damit nicht ein riesiger Delete den Store lange monopolisiert.

---

## 11. `max_db_bytes`

`max_db_bytes` ist in V1:

```text
Warn-/Health-Signal
```

nicht:

```text
harte automatische Quota
```

Bei Überschreitung wird Druck sichtbar gemacht, aber nicht automatisch:

- `VACUUM`;
- `auto_vacuum`;
- `incremental_vacuum`;
- `max_entries` heimlich verändert.

---

## 12. Warum kein automatisches VACUUM

Ein automatischer VACUUM-Pfad wäre ein zusätzlicher schwerer I/O-/Lock- und Fehlerpfad.

V1 setzt lieber auf vorhersehbare Retention nach Alter und Eintragszahl.

---

# JSONL

## 13. Was JSONL ist

Eine Datei besteht aus **einem JSON-Objekt pro Zeile**:

```json
{"schemaVersion":1,"recordId":"A","channel":"audit","type":"client.trigger.sent"}
{"schemaVersion":1,"recordId":"B","channel":"system","level":"WARNING"}
```

---

## 14. Warum JSONL statt einer großen JSON-Liste

Klassisches JSON:

```json
[
  {...},
  {...}
]
```

muss beim Anhängen strukturell gültig gehalten werden.

JSONL:

```text
{...}
{...}
{...}
```

kann einfach fortlaufend geschrieben und zeilenweise verarbeitet werden.

---

## 15. V1-Sink-Scope

Der Observability-File-Sink unterstützt in V1 bewusst nur:

```text
JSONL
```

Darum gibt es keine `file_sink_format`-Option mit nur einer sinnvollen Auswahl.

Weitere Formate/Sinks gehören in OBS-150.

---

# Klassisches Logging

## 16. Warum `client.log` bleibt

Das vorhandene Logging wurde nicht ersetzt.

Bei einem Ausfall von Observability:

```text
Worker/Store kaputt
→ client.log kann weiterhin technische Hinweise liefern
```

Die Doppelung kostet Speicher, erhöht aber die Diagnose-Resilienz.

---

## 17. Vergleich

| Eigenschaft | `client.log` | SQLite | JSONL |
|---|---|---|---|
| menschenlesbar | direkt | über UI/Tools | eingeschränkt |
| strukturierte IDs | begrenzt | ja | ja |
| schnelle Filter | Textsuche | ja | extern |
| Pagination | nein | ja | nein |
| Replay-Dedupe | nein | ja | folgt Worker/Recordfluss |
| Retention nach Eintragszahl | nein | ja | sink-/dateibasiert |
| UI-Primärquelle | nein | ja | nein |
| Fallback bei Observability-Workerfehler | ja | nein | nein |
| maschinell streambar | begrenzt | DB | sehr gut |

---

## 18. Schema-Versionierung

Persistente Formate müssen evolvierbar bleiben.

JSONL trägt `schemaVersion` je Record. SQLite besitzt einen Schema-/Migrationsvertrag.

Neue Eventtypen brauchen nicht automatisch eine DB-Migration, solange das Canonical-Schema gleich bleibt.

---

## 19. `details_json` und `raw_json`

Beide enthalten strukturierte Daten.

Die UI lädt Raw für Tabellenlisten bewusst nicht zwingend vollständig. Große Quellpayloads sollen einfache Abfragen nicht unnötig aufblasen.

---

## 20. Inhaltsgrenzen

Store und JSONL teilen die zentralen Normalisierungs-/Redaction-Regeln.

Insbesondere sollen nicht ungeprüft persistiert werden:

- Tokens/Secrets;
- Audio-Rohdaten;
- Transkriptinhalt entgegen der Content-Policy.

Das ist eine gemeinsame Datenpfadregel, keine separate „Datenschutz-Unterarchitektur“.

---

## 21. Wo die Dateien liegen

Der exakte lokale Ablageort hängt von `db_path`, `file_sink_dir` und den Standardpfaden des Clients ab.

Die Standardentscheidung lautet:

- produktive Diagnose-Daten **außerhalb des Repositories**;
- unter Benutzer-/Anwendungsdaten;
- keine Runtime-DB im Git-Workspace.

---

## 22. Zukunft

Spätere Sinks können additiv ergänzt werden:

```text
CanonicalLogRecord
├→ SQLiteLogStore
├→ JsonlSink
└→ weitere Sink-Adapter
```

ohne den Producer- oder Queryvertrag neu zu erfinden.
