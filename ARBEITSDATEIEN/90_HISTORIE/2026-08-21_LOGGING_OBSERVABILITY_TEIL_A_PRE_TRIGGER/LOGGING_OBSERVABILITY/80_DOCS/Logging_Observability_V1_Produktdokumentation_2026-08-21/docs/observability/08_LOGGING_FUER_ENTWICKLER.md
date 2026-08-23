# Logging für Entwickler

## Kurz und einfach erklärt

Nicht jede Information muss auf dieselbe Weise protokolliert werden.

Wenn du nur sagen willst:

> „Hier ist ein technischer Hinweis.“

reicht oft normales Python-Logging.

Wenn du später zuverlässig danach filtern, testen oder mehrere Komponenten verbinden willst, brauchst du ein **strukturiertes Event**.

---

## 1. Entscheidungsbaum

```text
Nur technische Meldung/Exception?
    → normales Python logging

Stabil filterbar oder korrelierbar?
    → strukturiertes Clientevent

Information ist bereits echtes Serverevent?
    → ServerLiveAdapter/Normalizer nutzen
      nicht manuell neu erfinden

Audio-/anderer Hot Path?
    → Zähler/Aggregate statt Einzelrecords
```

---

## 2. Normales Python-Logging

```python
logger.warning("Connection closed: code=%s reason=%s", code, reason)
```

Geeignet für:

- technische Diagnose;
- Exceptions;
- detaillierte Entwicklerhinweise;
- bestehende klassische Pfade.

Der `UnifiedLogHandler` kann daraus zusätzlich einen Canonical Record erzeugen.

---

## 3. IDs mit `extra`

Nur wenn sie wirklich bekannt sind:

```python
logger.info(
    "Session admitted",
    extra={
        "session_id": session_id,
        "generation": generation,
    },
)
```

Keine IDs aus globalem Zustand „auffüllen“.

---

## 4. Strukturierte Client-Observations

Konzeptionelles Beispiel:

```python
observability.event(
    "client.trigger.sent",
    channel="audit",
    level="INFO",
    component="stt_session",
    message="Trigger sent",
    details={"source": "manual"},
    session_id=session_id,
    generation=generation,
    command_id=command_id,
)
```

Im realen Projekt vorhandene Adapter (`ClientEventEmitter`/Ingress) wiederverwenden, keine parallele zweite Logging-API erfinden.

---

## 5. Wann ein `type` sinnvoll ist

Ein strukturierter Typ ist sinnvoll, wenn mindestens eines gilt:

- andere Komponenten sollen danach suchen;
- er ist Teil einer wichtigen Ablaufkette;
- IDs gehören dazu;
- Tests sollen sein Auftreten prüfen;
- die fachliche Bedeutung ist stabil;
- spätere Forensik profitiert davon.

Nicht jeder Debugsatz braucht einen Eventtyp.

---

## 6. Naming

Client:

```text
client.<bereich>.<ereignis>
```

Logging intern:

```text
logging.<ereignis>
```

Serverevents behalten ihren Servernamen.

---

## 7. Channel wählen

- `system` – Technik, Lifecycle, Infrastruktur.
- `audit` – absichtliche Aktionen, Commands, Settings.
- `transcription` – Text-/Transkriptionsfluss.
- `performance` – Zahlen, Zähler, Aggregate.

Faustregel:

> Der Channel beschreibt, **warum man den Record später sucht**, nicht welche Python-Datei ihn erzeugt.

---

## 8. Level wählen

| Level | Bedeutung |
|---|---|
| `DEBUG` | feine technische Details |
| `INFO` | normaler erwarteter Vorgang |
| `WARNING` | unerwartet/degradiert, aber weiterlauffähig |
| `ERROR` | Vorgang fehlgeschlagen |
| `CRITICAL` | schwerer Komponenten-/Anwendungsausfall |

Nicht `WARNING` wählen, nur um einen Record sichtbarer zu machen.

---

## 9. Component

Technischer Ursprung:

```text
eventstream
stt_session
controller
ui.application
```

Nicht den Eventtyp duplizieren.

---

## 10. Message

Kurz und menschenlesbar:

```text
"Trigger acknowledgement dropped"
```

Nicht nur denselben String wie `type` wiederholen.

---

## 11. Details

Strukturierte Zusatzinformation:

```json
{
  "source": "manual",
  "attempt": 2,
  "timeout_s": 4.0
}
```

Spezialdaten gehören eher in `details` als als immer neue globale Canonical-Felder.

---

## 12. Raw

Raw erhält Quellstruktur, ersetzt aber nicht die Kernfelder.

Wenn später häufig nach einem Wert gefiltert wird, sollte er nicht ausschließlich im Raw versteckt sein.

---

## 13. Exceptions

Für technische Exceptions:

```python
logger.exception("Failed to open audio stream")
```

Nur zusätzlich strukturiert loggen, wenn es einen stabilen fachlichen Eventvertrag gibt.

---

## 14. Hot Paths

Nicht:

```python
for audio_chunk in chunks:
    observability.event(...)
```

Sondern:

```text
Zähler erhöhen
→ periodisch aggregierten Record schreiben
```

z. B. `client.audio.stream_stats`.

---

## 15. Inhaltsgrenzen

Keine Tokens, Authorization-Header, Audio-Rohdaten oder ungeprüften großen Payloads absichtlich in `message`, `details` oder `raw` legen. Die zentrale Redaction ist eine zweite Schutzschicht, kein Ersatz für saubere Instrumentierung.

---

## 16. Keine Runtime-Kopplung

Loggingcode darf nicht:

- Controllerzustand verändern;
- Reconnect auslösen;
- Feedback triggern;
- Sessionstate abfragen, nur um Metadaten zu erfinden;
- auf DB-Erfolg warten.

---

## 17. Checkliste für einen neuen Instrumentierungspunkt

1. Reicht Python-Logging?
2. Brauche ich wirklich einen strukturierten Typ?
3. Welcher Channel passt?
4. Welches Level?
5. Welche Component?
6. Welche IDs kenne ich sicher?
7. Was gehört in `details`?
8. Enthält etwas sensible oder riesige Rohdaten?
9. Bin ich in einem Hot Path?
10. Existiert dasselbe Event bereits?
11. Braucht es Tests?
12. Muss der Eventkatalog aktualisiert werden?

---

## 18. Dokumentation mitpflegen

Neue stabile Clienttypen → `05_EVENT_KATALOG_CLIENT.md`.

Neue relevante Servereventverträge → `06_SERVER_EVENTS_UND_LOGSTREAM.md`.

Die Dokumentation soll nicht erst Monate später aus dem Code rekonstruiert werden.
