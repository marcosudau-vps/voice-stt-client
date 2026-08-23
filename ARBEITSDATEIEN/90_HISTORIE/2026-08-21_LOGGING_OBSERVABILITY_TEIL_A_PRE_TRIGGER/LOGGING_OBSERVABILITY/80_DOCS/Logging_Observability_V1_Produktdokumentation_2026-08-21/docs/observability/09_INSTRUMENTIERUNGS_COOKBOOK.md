# Instrumentierungs-Cookbook

## Kurz und einfach erklärt

Diese Datei ist die Rezeptesammlung.

Nicht: „Wie funktioniert das ganze Logging theoretisch?“

Sondern:

> „Ich stehe gerade in einer Funktion und will **diesen konkreten Fall** richtig protokollieren. Was mache ich?“

---

## Rezept 1 – normaler technischer Hinweis

```python
logger.info("WebSocket connected")
```

Wenn IDs sicher bekannt sind:

```python
logger.info(
    "WebSocket connected",
    extra={"session_id": session_id, "generation": generation},
)
```

---

## Rezept 2 – technischer Fehler mit Stacktrace

```python
try:
    ...
except Exception:
    logger.exception("Failed to open audio stream")
```

Nur zusätzlich ein strukturiertes Event erzeugen, wenn der Fehler einen stabilen Fachvertrag besitzt.

---

## Rezept 3 – Benutzeraktion

Hotkey angenommen:

```text
type      = client.hotkey.pressed
channel   = audit
level     = INFO
component = hotkeys
```

Der Record bestätigt nur: **Client hat den Hotkey registriert.**

Er bestätigt nicht: **Server nimmt bereits auf.**

---

## Rezept 4 – Request und Ack korrelieren

Request:

```text
client.trigger.sent
session_id = S1
generation = 4
command_id = C7
```

Ack:

```text
client.trigger.ack_received
session_id = S1
generation = 4
command_id = C7
```

---

## Rezept 5 – Settings Apply über mehrere Schichten

```text
client.settings.apply_started   correlation_id=settings:abc
client.settings.runtime_apply   correlation_id=settings:abc
client.settings.apply_completed correlation_id=settings:abc
```

---

## Rezept 6 – strukturierte Zusatzdaten

Schlecht:

```text
message = "Trigger sent source=manual attempt=2 timeout=4.0"
```

Besser:

```text
message = "Trigger sent"

details = {
  "source": "manual",
  "attempt": 2,
  "timeout_s": 4.0
}
```

---

## Rezept 7 – unbekannte Session-ID

Wenn die Funktion die Session nicht sicher kennt:

```text
session_id = null
```

Nicht die „gerade aktuelle“ Session irgendwo abfragen, nur damit das Feld gefüllt ist.

---

## Rezept 8 – Audio-Hot-Path

Nicht:

```python
def callback(chunk):
    observability.event("client.audio.chunk_received", ...)
```

Besser:

```python
self._audio_packets += 1
self._audio_bytes += len(chunk)
```

und periodisch `client.audio.stream_stats`.

---

## Rezept 9 – Serverevent

Nicht künstlich:

```text
client.server.transcription_completed
```

erfinden, wenn das echte Serverevent bereits:

```text
transcription.completed
```

heißt.

ServerLiveAdapter/Normalizer verwenden und Identität erhalten.

---

## Rezept 10 – Replay

Derselbe `event_id` darf bei Replay nicht als zweiter persistenter Datensatz erscheinen.

```text
event_id = E17
replayed = true
```

Replay ist Kontext, nicht neue fachliche Identität.

---

## Rezept 11 – Performancewert

Bei hochfrequenten Werten aggregieren:

```json
{
  "type": "client.audio.stream_stats",
  "details": {
    "packets_sent": 1350,
    "bytes_sent": 1728000,
    "max_queue_depth": 6
  }
}
```

---

## Rezept 12 – LED-/Soundfehler

```text
client.led.dispatch_failed
client.sound.failed
```

Observability beobachtet den Ausgabefehler. Sie führt nicht selbst einen zweiten Ausgaberversuch aus.

---

## Rezept 13 – andere Persistenzfehler

Beispiel Text-History:

```text
client.history.persist_failed
```

Nicht mit dem Observability-`SQLiteLogStore` verwechseln.

---

## Rezept 14 – Logging selbst ist kaputt

```text
Loggingfehler
→ Health/Counter
→ begrenzter Emergency-Ausgang
→ KEIN normaler rekursiver Observability-Loop
```

---

## Rezept 15 – neuer Eventtyp

```text
1. Katalog durchsuchen
2. prüfen, ob Python-Log reicht
3. Namespace wählen
4. Channel wählen
5. Level wählen
6. IDs definieren
7. Details definieren
8. Hot-Path prüfen
9. Test ergänzen
10. Katalog aktualisieren
```

---

## Rezept 16 – Message oder strukturiertes Feld?

Später filtern/auswerten?

```text
→ strukturiertes Feld / details
```

Nur für Menschen beim Lesen?

```text
→ message
```

---

## Rezept 17 – Transkriptinhalt

Nicht beiläufig ganze Transkripte in technische Fehlermeldungen einbauen.

Transkriptbezogene Inhalte müssen die Content-Policy beachten.

---

## Rezept 18 – keine Doppelwelt bauen

Bevor ein Event aus Runtime-State abgeleitet wird:

> Gibt es bereits ein echtes Ereignis an der Quelle?

Wenn ja, dieses beobachten statt einen zweiten parallelen Lifecycle nur fürs Logging zu rekonstruieren.
